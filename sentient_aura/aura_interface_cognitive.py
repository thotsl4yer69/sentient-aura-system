#!/usr/bin/env python3
"""
Sentient Aura - COGNITIVE INTERFACE (Production-Ready)
=====================================================

Fully integrated visualization combining:
- Cognitive Engine (40 personality states)
- Particle Physics Engine (10,000 particles @ 60 FPS)
- Sensor Visualizer (WiFi, Bluetooth, Audio)
- Text Input for communication

This is the SENTIENT interface that replaces the old simple orb.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import numpy as np
import math
import time
from typing import List, Tuple, Dict, Optional
import threading
import queue
import logging

from . import config
from .cognitive_engine import CognitiveEngine, COGNITIVE_PROFILES
from .particle_physics import ParticlePhysicsEngine
from .sensor_visualizer import SensorVisualizer

# Import all constants from config
from .config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, FULLSCREEN,
    COLOR_IDLE, COLOR_LISTENING, COLOR_PROCESSING,
    COLOR_SPEAKING, COLOR_EXECUTING, COLOR_THREAT, COLOR_ERROR,
    COLOR_BACKGROUND,
    STATE_IDLE, STATE_LISTENING, STATE_PROCESSING,
    STATE_SPEAKING, STATE_EXECUTING, STATE_THREAT, STATE_ERROR,
    SHOW_FPS
)

logger = logging.getLogger("aura_interface_cognitive")


class TextInputBox:
    """Enhanced text input box for user communication."""

    def __init__(self, x: int, y: int, w: int, h: int, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (100, 200, 255)  # Cyan
        self.color_active = (0, 255, 255)      # Bright cyan
        self.color = self.color_inactive
        self.text = ''
        self.font = font
        self.txt_surface = self.font.render('', True, self.color)
        self.active = False

        # Message history
        self.history = []
        self.max_history = 100

    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events. Returns command string on Enter."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                command = self.text.strip()
                if command:
                    self.history.append(command)
                    if len(self.history) > self.max_history:
                        self.history = self.history[-self.max_history:]
                    self.text = ''
                    self.txt_surface = self.font.render('', True, self.color)
                    return command
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Add character (with length limit)
                if len(self.text) < 200:
                    self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, self.color)

        return None

    def draw(self, screen: pygame.Surface):
        """Render the input box."""
        # Draw background
        bg_alpha = 180 if self.active else 120
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, bg_alpha), (0, 0, self.rect.width, self.rect.height), border_radius=10)
        screen.blit(bg_surface, (self.rect.x, self.rect.y))

        # Draw text
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2
        screen.blit(self.txt_surface, (text_x, text_y))

        # Draw border
        border_width = 3 if self.active else 2
        pygame.draw.rect(screen, self.color, self.rect, border_width, border_radius=10)

        # Draw cursor if active
        if self.active and int(time.time() * 2) % 2 == 0:
            cursor_x = text_x + self.txt_surface.get_width() + 2
            cursor_y = text_y
            pygame.draw.line(screen, self.color,
                           (cursor_x, cursor_y),
                           (cursor_x, cursor_y + self.txt_surface.get_height()), 2)


class CognitiveAuraInterface:
    """
    Main COGNITIVE visual interface integrating all visualization components.

    This replaces the old AuraOrb with a fully sentient particle system.
    """

    def __init__(self, num_particles: int = 10000):
        logger.info("Initializing Cognitive Aura Interface...")

        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Create window
        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        pygame.display.set_caption("Sentient Core - Cognitive Aura")

        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 18)

        # Core visualization components
        self.num_particles = num_particles
        self.cognitive_engine = CognitiveEngine()
        self.physics_engine = ParticlePhysicsEngine(num_particles=num_particles)
        self.sensor_visualizer = SensorVisualizer(num_particles=num_particles)

        # Initialize humanoid silhouette
        self.physics_engine.reset_positions("humanoid")

        # State management
        self.current_state = STATE_IDLE
        self.personality_state = "idle_standing"
        self.status_text = "Hello! I'm here to help you."
        self.transcription = ""

        # Sensor data (updated externally)
        self.sensor_data = {
            'wifi_networks': [],
            'bluetooth_devices': [],
            'audio_amplitude': 0.0,
            'gps_movement': np.array([0.0, 0.0, 0.0])
        }

        # Communication
        self.command_queue = queue.Queue()
        self.state_queue = queue.Queue()

        # Text input
        input_y = WINDOW_HEIGHT - 80
        input_w = WINDOW_WIDTH - 100
        self.input_box = TextInputBox(50, input_y, input_w, 50, self.font_small)

        # Conversation history
        self.conversation_history = []
        self.max_conversation_lines = 10

        # Rendering optimization
        self.particle_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        # Threading
        self.running = False
        self.thread = None

        # Performance
        self.clock = pygame.time.Clock()
        self.fps = FPS

        # 3D projection parameters
        self.camera_pos = np.array([0.0, 1.0, 3.0])  # Camera position
        self.screen_center = np.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2])
        self.fov_scale = 600  # Field of view scaling

        logger.info(f"✓ Cognitive Aura Interface initialized ({num_particles} particles)")

    def project_3d_to_2d(self, positions_3d: np.ndarray) -> np.ndarray:
        """
        Project 3D particle positions to 2D screen coordinates.

        Uses perspective projection for depth.

        Args:
            positions_3d: Particle positions (N, 3) in 3D space

        Returns:
            Screen coordinates (N, 2) and depths (N,)
        """
        # Translate particles relative to camera
        relative = positions_3d - self.camera_pos

        # Perspective divide (z must be > 0)
        z = relative[:, 2]
        z = np.maximum(z, 0.1)  # Prevent divide by zero

        # Project to 2D
        screen_x = (relative[:, 0] / z) * self.fov_scale + self.screen_center[0]
        screen_y = (-relative[:, 1] / z) * self.fov_scale + self.screen_center[1]  # Flip Y

        screen_coords = np.column_stack([screen_x, screen_y])

        return screen_coords, z

    def set_state(self, state: str, status_text: str = "", personality: Optional[str] = None):
        """
        Update visual state and personality.

        Args:
            state: System state (idle, listening, processing, etc.)
            status_text: Optional status message
            personality: Optional personality state name
        """
        self.current_state = state
        if status_text:
            self.status_text = status_text

        # Map system state to personality state if not explicitly provided
        if personality:
            self.personality_state = personality
        else:
            # Default personality mapping
            state_personality_map = {
                STATE_IDLE: "idle_standing",
                STATE_LISTENING: "listening_intently",
                STATE_PROCESSING: "analyzing_data",
                STATE_SPEAKING: "engaged_conversation",
                STATE_EXECUTING: "autonomous_operation",
                STATE_THREAT: "threat_detected",
                STATE_ERROR: "error_state"
            }
            self.personality_state = state_personality_map.get(state, "idle_standing")

        # Update cognitive engine
        self.cognitive_engine.update_state(self.personality_state, transition_time=1.0)

        logger.info(f"State changed: {state} -> {self.personality_state}")

    def set_transcription(self, text: str):
        """Set current transcription/response text."""
        self.transcription = text
        if text and self.current_state == STATE_SPEAKING:
            self.add_to_conversation("AURA", text)

    def add_to_conversation(self, speaker: str, text: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            'speaker': speaker,
            'text': text,
            'time': time.time()
        })
        if len(self.conversation_history) > self.max_conversation_lines:
            self.conversation_history = self.conversation_history[-self.max_conversation_lines:]

    def update_sensor_data(self, sensor_data: Dict):
        """Update sensor data for visualization."""
        self.sensor_data.update(sensor_data)

    def update(self, dt: float):
        """
        Update all visualization components.

        Args:
            dt: Delta time in seconds
        """
        # Update cognitive engine
        self.cognitive_engine.update(dt)

        # Get current cognitive profile
        profile = self.cognitive_engine.get_current_profile()

        # Update particle physics with cognitive parameters
        breath_factor = self.cognitive_engine.get_breathing_factor()

        self.physics_engine.update(
            dt=dt,
            cohesion=profile.cohesion,
            separation=profile.separation,
            alignment=profile.alignment,
            wander=profile.wander,
            breath_factor=breath_factor,
            speed_multiplier=profile.particle_speed,
            damping=0.98
        )

        # Process state updates from queue
        try:
            while True:
                state_update = self.state_queue.get_nowait()
                if 'state' in state_update:
                    self.set_state(
                        state_update['state'],
                        state_update.get('text', ''),
                        state_update.get('personality')
                    )
                if 'transcription' in state_update:
                    self.set_transcription(state_update['transcription'])
                if 'sensor_data' in state_update:
                    self.update_sensor_data(state_update['sensor_data'])
        except queue.Empty:
            pass

    def draw(self):
        """Render all visual elements."""
        # Clear screen
        self.screen.fill(COLOR_BACKGROUND)

        # Get current cognitive profile for color
        profile = self.cognitive_engine.get_current_profile()

        # Get particle positions from physics engine
        positions_3d = self.physics_engine.positions

        # Apply sensor influences to get colors
        sensor_influences, base_colors = self.sensor_visualizer.combine_sensor_influences(
            positions_3d, self.sensor_data, dt=1/60
        )

        # Apply cognitive color shift
        final_colors = self.sensor_visualizer.apply_cognitive_color_shift(
            base_colors,
            profile.color_shift,
            profile.glow_intensity
        )

        # Project 3D to 2D
        screen_coords, depths = self.project_3d_to_2d(positions_3d)

        # Clear particle surface
        self.particle_surface.fill((0, 0, 0, 0))

        # Draw particles (back to front for depth)
        depth_order = np.argsort(depths)[::-1]  # Furthest first

        for i in depth_order[::10]:  # Draw every 10th particle for performance
            x, y = screen_coords[i]

            # Skip off-screen particles
            if not (0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT):
                continue

            # Calculate particle size based on depth
            size = max(1, int(self.fov_scale / (depths[i] * 2)))
            size = min(size, 8)  # Cap max size

            # Get particle color
            color = tuple(final_colors[i])

            # Draw with glow
            if size > 2:
                # Draw glow
                glow_color = (*color, int(profile.glow_intensity * 50))
                pygame.draw.circle(self.particle_surface, glow_color,
                                 (int(x), int(y)), size + 2)

            # Draw core
            pygame.draw.circle(self.particle_surface, color,
                             (int(x), int(y)), size)

        # Blit particles to screen
        self.screen.blit(self.particle_surface, (0, 0))

        # Draw conversation history panel
        self.draw_conversation_history()

        # Draw status text
        status_surface = self.font_large.render(self.status_text, True, (255, 255, 255))
        status_rect = status_surface.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(status_surface, status_rect)

        # Draw transcription
        if self.transcription and self.current_state in [STATE_SPEAKING, STATE_PROCESSING]:
            self.draw_transcription()

        # Draw personality state indicator
        personality_text = f"Personality: {self.personality_state.replace('_', ' ').title()}"
        personality_surface = self.font_small.render(personality_text, True, (150, 150, 150))
        self.screen.blit(personality_surface, (WINDOW_WIDTH - 300, 20))

        # Draw text input
        input_label = self.font_small.render("Type your message:", True, (150, 200, 255))
        self.screen.blit(input_label, (self.input_box.rect.x, self.input_box.rect.y - 25))
        self.input_box.draw(self.screen)

        # Draw FPS counter
        if SHOW_FPS:
            fps_text = f"FPS: {int(self.clock.get_fps())} | Particles: {self.num_particles}"
            fps_surface = self.font_small.render(fps_text, True, (100, 100, 100))
            self.screen.blit(fps_surface, (10, 10))

        # Update display
        pygame.display.flip()

    def draw_conversation_history(self):
        """Draw conversation history panel."""
        if not self.conversation_history:
            return

        panel_width = 400
        panel_height = WINDOW_HEIGHT - 200
        panel_x = 20
        panel_y = 120

        # Semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (20, 30, 40, 200),
                        (0, 0, panel_width, panel_height), border_radius=15)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Title
        title = self.font_medium.render("Conversation", True, (100, 200, 255))
        self.screen.blit(title, (panel_x + 20, panel_y + 15))

        # Draw messages
        y_offset = panel_y + 60
        line_height = 70

        for msg in self.conversation_history[-6:]:
            speaker_color = (0, 255, 100) if msg['speaker'] == "AURA" else (255, 200, 100)

            # Speaker label
            speaker_text = self.font_small.render(f"{msg['speaker']}:", True, speaker_color)
            self.screen.blit(speaker_text, (panel_x + 20, y_offset))

            # Message text (word wrapped)
            words = msg['text'].split()
            lines = []
            current_line = []
            max_width = panel_width - 40

            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font_small.size(test_line)[0] < max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            # Draw lines
            for i, line in enumerate(lines[:2]):
                text_surface = self.font_small.render(line, True, (220, 220, 220))
                self.screen.blit(text_surface, (panel_x + 20, y_offset + 25 + i * 20))

            y_offset += line_height

            if y_offset > panel_y + panel_height - 80:
                break

    def draw_transcription(self):
        """Draw current transcription text."""
        words = self.transcription.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font_medium.size(test_line)[0] < WINDOW_WIDTH - 100:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        y_offset = WINDOW_HEIGHT - 180
        for line in lines[-3:]:
            trans_surface = self.font_medium.render(line, True, (200, 200, 200))
            trans_rect = trans_surface.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(trans_surface, trans_rect)
            y_offset += 35

    def run(self):
        """Main GUI loop."""
        self.running = True
        logger.info("Cognitive Aura Interface running...")

        while self.running:
            # Handle events
            for event in pygame.event.get():
                # Handle text input
                command = self.input_box.handle_event(event)
                if command:
                    logger.info(f"User command: {command}")
                    self.command_queue.put(command)
                    self.add_to_conversation("YOU", command)

                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Update
            dt = self.clock.tick(self.fps) / 1000.0
            self.update(dt)

            # Draw
            self.draw()

        logger.info("Cognitive Aura Interface stopped")
        pygame.quit()

    def start(self):
        """Start GUI in separate thread."""
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        logger.info("Cognitive Aura Interface thread started")

    def stop(self):
        """Stop the GUI."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("\n" + "=" * 70)
    print("COGNITIVE AURA INTERFACE TEST")
    print("=" * 70)
    print("\nPress ESC to quit")
    print("Type in the text box and press ENTER to send messages")
    print("\n" + "=" * 70 + "\n")

    aura = CognitiveAuraInterface(num_particles=5000)  # Reduce for testing

    # Simulate state changes
    import time as t
    def demo_states():
        t.sleep(2)
        aura.state_queue.put({
            'state': STATE_LISTENING,
            'text': 'Listening...',
            'personality': 'listening_intently'
        })
        t.sleep(3)
        aura.state_queue.put({
            'state': STATE_PROCESSING,
            'text': 'Analyzing...',
            'personality': 'analyzing_data'
        })
        t.sleep(3)
        aura.state_queue.put({
            'state': STATE_SPEAKING,
            'text': 'Speaking...',
            'transcription': 'Hello! I am your Sentient Core. All systems are fully integrated and operational.',
            'personality': 'engaged_conversation'
        })
        t.sleep(4)
        aura.state_queue.put({
            'state': STATE_IDLE,
            'text': 'Ready',
            'personality': 'awaiting_command'
        })

    # Run demo in background
    demo_thread = threading.Thread(target=demo_states, daemon=True)
    demo_thread.start()

    # Run GUI (blocking)
    aura.run()
