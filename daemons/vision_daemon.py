#!/usr/bin/env python3
"""
Sentient Core - Vision Daemon
Handles camera input and basic computer vision.
CRITICAL UPDATE: Implements frame throttling to prevent WorldState overload.
"""

import logging
import time
import cv2
import numpy as np
from daemon_base import BaseDaemon

class VisionDaemon(BaseDaemon):
    def __init__(self, world_state):
        super().__init__("vision", world_state)
        self.camera = cv2.VideoCapture(0)
        self.last_full_frame_update = time.time()
        self.full_frame_interval = 5.0 # Update full frame every 5 seconds by default
        self.motion_detected = False
        self.frame_counter = 0

    def _run_loop(self):
        while self._running:
            ret, frame = self.camera.read()
            if not ret:
                self.logger.error("Failed to read frame from camera.")
                time.sleep(1)
                continue
            
            self.frame_counter += 1
            
            # 1. Motion Detection (Placeholder for actual CV logic)
            # For this example, we'll simulate motion detection
            self.motion_detected = self.frame_counter % 100 == 0 # Simulate motion every 100 frames

            # 2. Frame Throttling Logic
            current_time = time.time()
            update_full_frame = False

            if self.motion_detected:
                # Always update on a critical event
                update_full_frame = True
            elif current_time - self.last_full_frame_update > self.full_frame_interval:
                # Update periodically even if no event
                update_full_frame = True

            vision_data = {
                "timestamp": current_time,
                "motion_detected": self.motion_detected,
                "objects_detected": 0, # Placeholder
                "frame_available": update_full_frame
            }

            if update_full_frame:
                # Only store the full frame in WorldState when necessary
                vision_data["rgb_frame"] = frame
                self.last_full_frame_update = current_time
                self.logger.info("WorldState updated with full frame (event or interval)."
            else:
                # Store a low-res thumbnail or just metadata to save memory
                # In a real app, you might store a compressed JPEG thumbnail
                vision_data["rgb_frame"] = None 
                self.logger.debug("WorldState updated with metadata only (throttled).")

            self.world_state.update("vision", vision_data)

            # Process the frame (e.g., run object detection)
            # ... (CV processing logic here) ...

            time.sleep(1 / 30) # 30 FPS loop

    def conserve_power(self):
        """Reduces frame rate to conserve power."""
        self.full_frame_interval = 30.0 # Reduce full frame updates to every 30 seconds
        self.logger.warning("Vision Daemon set to low-power mode.")

    def __del__(self):
        self.camera.release()