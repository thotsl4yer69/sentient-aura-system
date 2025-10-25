#!/usr/bin/env python3
"""
Sentient Core - Vision Daemon
Manages camera input, motion detection, and visual perception.
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple, List

from daemon_base import BaseDaemon
from world_state import WorldState
from sentient_aura.config import (
    CAMERA_RESOLUTION,
    CAMERA_FPS,
    CAMERA_DEVICE_ID,
    VISION_UPDATE_RATE,
    MOTION_THRESHOLD,
    MOTION_MIN_AREA,
    MOTION_BLUR_SIZE,
    ENABLE_FRAME_SAVING,
    DATA_DIR
)


class VisionDaemon(BaseDaemon):
    """
    Vision processing daemon.
    
    Responsibilities:
    - Capture frames from camera
    - Detect motion
    - Prepare frames for AI inference
    - Update vision state in WorldState
    """
    
    def __init__(self, world_state: WorldState):
        super().__init__("visiond", world_state, VISION_UPDATE_RATE)
        
        self.camera = None
        self.previous_frame = None
        self.frame_count = 0
        self.motion_event_count = 0
    
    def initialize(self) -> bool:
        """Initialize the camera."""
        try:
            self.logger.info(f"Opening camera device {CAMERA_DEVICE_ID}")
            self.camera = cv2.VideoCapture(CAMERA_DEVICE_ID)
            
            if not self.camera.isOpened():
                self.logger.error("Failed to open camera")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
            self.camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            
            # Verify settings
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(
                f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps} FPS"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            return False
    
    def detect_motion(self, frame: np.ndarray) -> Tuple[bool, List]:
        """
        Detect motion in the current frame.
        
        Args:
            frame: Current BGR frame
            
        Returns:
            (motion_detected, contours)
        """
        # Convert to grayscale and blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (MOTION_BLUR_SIZE, MOTION_BLUR_SIZE), 0)
        
        # Initialize previous frame if needed
        if self.previous_frame is None:
            self.previous_frame = gray
            return False, []
        
        # Compute absolute difference
        frame_delta = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_delta, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate to fill holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh.copy(), 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter by area
        motion_contours = [c for c in contours if cv2.contourArea(c) > MOTION_MIN_AREA]
        
        # Update previous frame
        self.previous_frame = gray
        
        return len(motion_contours) > 0, motion_contours
    
    def update(self) -> None:
        """Capture and process a frame."""
        ret, frame = self.camera.read()
        
        if not ret:
            self.logger.warning("Failed to capture frame")
            return
        
        self.frame_count += 1
        current_time = time.time()
        
        # Detect motion
        motion_detected, contours = self.detect_motion(frame)
        
        # Prepare data for WorldState
        vision_data = {
            "rgb_frame": frame,
            "frame_timestamp": current_time,
            "frame_count": self.frame_count,
            "motion_detected": motion_detected,
            "motion_contours": contours,
            "detected_objects": []  # Will be populated by AI engine
        }
        
        # Update WorldState
        self.world_state.update("vision", vision_data)
        
        # Handle motion events
        if motion_detected:
            self.motion_event_count += 1
            
            # Calculate motion metrics
            total_area = sum(cv2.contourArea(c) for c in contours)
            
            self.logger.info(
                f"Motion detected! Event #{self.motion_event_count}, "
                f"{len(contours)} objects, area: {total_area:.0f}px"
            )
            
            # Add to history
            self.world_state.add_to_history("motion_events", {
                "event_id": self.motion_event_count,
                "contour_count": len(contours),
                "total_area": total_area
            })
            
            # Create alert
            self.world_state.add_alert(
                "motion",
                f"Motion detected: {len(contours)} moving object(s)",
                "info"
            )
            
            # Save frame if enabled
            if ENABLE_FRAME_SAVING:
                filename = DATA_DIR / f"motion_{self.motion_event_count}.jpg"
                cv2.imwrite(str(filename), frame)
                self.logger.debug(f"Frame saved: {filename}")
    
    def cleanup(self) -> None:
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.logger.info("Camera released")

