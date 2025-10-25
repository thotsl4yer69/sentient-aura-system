#!/usr/bin/env python3
"""
Sentient Aura - Visual Interface
Beautiful Pygame GUI showing the AI's consciousness state
"""

import sys
import os
# Fix import path FIRST
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import math
import random
import time
from typing import List, Tuple, Optional
import threading
import queue
import logging

from . import config
from .cognitive_engine import CognitiveEngine, COGNITIVE_PROFILES
from .particle_physics import ParticlePhysicsEngine
from .sensor_visualizer import SensorVisualizer

# Import all constants from config
from .config import (
    # Window settings
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, FULLSCREEN,
    # Orb settings
    ORB_RADIUS, ORB_CENTER_X, ORB_CENTER_Y,
    # Colors
    COLOR_IDLE, COLOR_LISTENING, COLOR_PROCESSING,
    COLOR_SPEAKING, COLOR_EXECUTING, COLOR_THREAT, COLOR_ERROR,
    COLOR_BACKGROUND,
    # Pulse speeds
    PULSE_SPEED_IDLE, PULSE_SPEED_LISTENING, PULSE_SPEED_PROCESSING,
    PULSE_SPEED_SPEAKING, PULSE_SPEED_THREAT,
    # Particles
    PARTICLES_ENABLED, PARTICLE_COUNT_PROCESSING, PARTICLE_COUNT_EXECUTING,
    # States
    STATE_IDLE, STATE_LISTENING, STATE_PROCESSING,
    STATE_SPEAKING, STATE_EXECUTING, STATE_THREAT, STATE_ERROR,
    # Sensors
    SENSOR_ICONS, SENSOR_DISPLAY_DURATION, SENSOR_ICON_SIZE,
    # Debug
    SHOW_FPS
)

logger = logging.getLogger("aura_interface")

# Cognitive state to visual state mapping
STATE_TO_COGNITIVE = {
    STATE_IDLE: "idle_standing",
    STATE_LISTENING: "listening_intently",
    STATE_PROCESSING: "analyzing_data",
    STATE_SPEAKING: "presenting_information",
    STATE_EXECUTING: "autonomous_operation",
    STATE_THREAT: "threat_detected",
    STATE_ERROR: "error_state"
}


class Particle:
    """Animated particle for visual effects."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        self.lifetime = random.uniform(0.5, 2.0)
        self.age = 0
        self.size = random.uniform(2, 5)
        self.alpha = 255  # Initialize alpha to full opacity

    def update(self, dt: float):
        """Update particle position and age."""
        self.x += self.vx
        self.y += self.vy
        self.age += dt

        # Fade out as it ages
        self.alpha = max(0, 255 * (1 - self.age / self.lifetime))

    def is_alive(self) -> bool:
        """Check if particle should still be rendered."""
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface):
        """Render the particle."""
        if self.is_alive():
            alpha = int(self.alpha)
            color = (*self.color, alpha)
            # Draw as a small circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


class AuraOrb:
    """The central consciousness orb."""

    def __init__(self, x: int, y: int, radius: int):
        self.x = x
        self.y = y
        self.radius = radius
        self.base_radius = radius

        # Visual state
        self.color = COLOR_IDLE
        self.target_color = COLOR_IDLE
        self.pulse_speed = PULSE_SPEED_IDLE
        self.pulse_phase = 0

        # Animation
        self.particles = []
        self.time = 0

        # Smooth color transitions
        self.color_transition_speed = 0.1

    def set_color(self, color: Tuple[int, int, int], pulse_speed: float):
        """Set target color and pulse speed."""
        self.target_color = color
        self.pulse_speed = pulse_speed

    def update(self, dt: float):
        """Update orb animation."""
        self.time += dt

        # Smooth color transition
        self.color = tuple(
            int(self.color[i] + (self.target_color[i] - self.color[i]) * self.color_transition_speed)
            for i in range(3)
        )

        # Pulse animation
        self.pulse_phase += self.pulse_speed * dt * 2 * math.pi
        pulse_factor = (math.sin(self.pulse_phase) + 1) / 2
        self.radius = int(self.base_radius + pulse_factor * 20)

        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

    def add_particles(self, count: int):
        """Add particles around the orb."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.radius * 0.8, self.radius * 1.2)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            self.particles.append(Particle(x, y, self.color))

    def draw(self, surface: pygame.Surface):
        """Render the orb with a friendly face."""
        # Draw glow layers (multiple circles with decreasing alpha)
        for i in range(5):
            glow_radius = self.radius + (i * 15)
            alpha = max(0, 100 - i * 20)
            glow_color = (*self.color, alpha)

            # Create temporary surface for alpha blending
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha // 2),
                             (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))

        # Draw main orb
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

        # Draw friendly face
        self._draw_face(surface)

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

    def _draw_face(self, surface: pygame.Surface):
        """Draw a friendly face on the orb."""
        # Eye settings
        eye_spacing = int(self.radius * 0.4)
        eye_y_offset = int(self.radius * 0.15)
        eye_radius = int(self.radius * 0.15)

        # Pupil animation based on pulse
        blink_factor = abs(math.sin(self.pulse_phase * 2))
        eye_open_amount = 0.7 + 0.3 * blink_factor

        # Draw left eye
        left_eye_x = self.x - eye_spacing
        left_eye_y = self.y - eye_y_offset

        # Eye white
        pygame.draw.circle(surface, (255, 255, 255),
                         (left_eye_x, left_eye_y), eye_radius)

        # Pupil (slightly offset for expression)
        pupil_offset_x = int(math.sin(self.time * 0.5) * 3)
        pupil_offset_y = int(math.cos(self.time * 0.3) * 2)
        pupil_radius = int(eye_radius * 0.5 * eye_open_amount)
        pygame.draw.circle(surface, (20, 20, 40),
                         (left_eye_x + pupil_offset_x, left_eye_y + pupil_offset_y),
                         pupil_radius)

        # Draw right eye
        right_eye_x = self.x + eye_spacing
        right_eye_y = self.y - eye_y_offset

        pygame.draw.circle(surface, (255, 255, 255),
                         (right_eye_x, right_eye_y), eye_radius)
        pygame.draw.circle(surface, (20, 20, 40),
                         (right_eye_x + pupil_offset_x, right_eye_y + pupil_offset_y),
                         pupil_radius)

        # Draw mouth (smile curve)
        mouth_y = self.y + int(self.radius * 0.4)
        mouth_width = int(self.radius * 0.6)

        # Smile that animates with pulse
        smile_amount = 0.5 + 0.5 * (math.sin(self.pulse_phase) + 1) / 2

        # Draw smile arc
        mouth_rect = pygame.Rect(
            self.x - mouth_width // 2,
            mouth_y - int(mouth_width * 0.3 * smile_amount),
            mouth_width,
            int(mouth_width * 0.6 * smile_amount)
        )
        pygame.draw.arc(surface, (255, 255, 255), mouth_rect, 0, math.pi, 4)


class SensorIcon:
    """Icon representing a hardware sensor."""

    def __init__(self, name: str, icon: str, x: int, y: int):
        self.name = name
        self.icon = icon
        self.x = x
        self.y = y
        self.online = False
        self.active = False  # Currently detecting something
        self.size = SENSOR_ICON_SIZE

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Render the sensor icon."""
        # Determine color based on status
        if self.active:
            color = (255, 255, 0)  # Yellow when actively detecting
        elif self.online:
            color = (100, 200, 255)  # Blue when online
        else:
            color = (50, 50, 50)  # Gray when offline

        # Draw icon background circle
        pygame.draw.circle(surface, color, (self.x, self.y), self.size // 2)

        # Draw icon text (emoji)
        text_surface = font.render(self.icon, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        surface.blit(text_surface, text_rect)

        # Draw label
        label_font = pygame.font.SysFont('Arial', 14)
        label_surface = label_font.render(self.name.upper(), True, color)
        label_rect = label_surface.get_rect(center=(self.x, self.y + self.size))
        surface.blit(label_surface, label_rect)


class TextInputBox:
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (200, 200, 200)
        self.text = ''
        self.font = font
        self.txt_surface = self.font.render('', True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = (255, 255, 255) if self.active else (200, 200, 200)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    command = self.text
                    self.text = ''
                    return command
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2 if self.active else 1)


class AuraInterface:
    """Main visual interface for Sentient Aura."""

    def __init__(self):
        logger.info("Initializing Aura Interface...")

        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Create window
        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        pygame.display.set_caption("Sentient Aura")

        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 16)
        self.font_emoji = pygame.font.SysFont('Segoe UI Emoji', 48)

        # ===  COGNITIVE VISUALIZATION ENGINES ===
        self.cognitive_engine = CognitiveEngine()
        self.particle_physics = ParticlePhysicsEngine(num_particles=10000)
        self.sensor_visualizer = SensorVisualizer(num_particles=10000)

        # Initialize humanoid distribution
        self.particle_physics.reset_positions("humanoid")

        # Legacy orb (kept for fallback)
        self.orb = AuraOrb(ORB_CENTER_X, ORB_CENTER_Y, ORB_RADIUS)
        self.use_particle_mode = True  # Enable new particle visualization

        # Create sensor icons
        self.create_sensor_icons()

        # State
        self.current_state = STATE_IDLE
        self.status_text = "Hello! I'm here to help you."
        self.transcription = ""
        self.show_sensors = False
        self.sensor_show_time = 0
        self.show_arduino_peripherals = False
        self.arduino_peripherals = {}

        # Sensor data for visualization
        self.wifi_data = []
        self.bluetooth_data = []
        self.audio_data = {"amplitude": 0.0}

        # Conversation history for human-like interaction
        self.conversation_history = []
        self.max_conversation_lines = 10

        # Communication queues
        self.command_queue = queue.Queue()
        self.state_queue = queue.Queue()

        self.input_box = TextInputBox(50, WINDOW_HEIGHT - 50, WINDOW_WIDTH - 100, 32, self.font_small)

        # Threading
        self.running = False
        self.thread = None

        # Performance
        self.clock = pygame.time.Clock()
        self.fps = FPS

        logger.info("✓ Aura Interface initialized with Cognitive Visualization Engines")
        logger.info(f"  - Cognitive Engine: {len(COGNITIVE_PROFILES)} personality states")
        logger.info(f"  - Particle Physics: {self.particle_physics.num_particles} particles")
        logger.info(f"  - Sensor Visualizer: WiFi/BT/Audio enabled")

    def create_sensor_icons(self):
        """Create sensor status icons arranged in a circle."""
        self.sensor_icons = {}
        sensors = list(SENSOR_ICONS.items())
        count = len(sensors)

        # Arrange icons in a circle around the orb
        circle_radius = ORB_RADIUS + 150
        for i, (sensor_name, icon_emoji) in enumerate(sensors):
            angle = (2 * math.pi * i / count) - (math.pi / 2)  # Start at top
            x = ORB_CENTER_X + int(circle_radius * math.cos(angle))
            y = ORB_CENTER_Y + int(circle_radius * math.sin(angle))

            self.sensor_icons[sensor_name] = SensorIcon(sensor_name, icon_emoji, x, y)

    def set_state(self, state: str, status_text: str = ""):
        """Update visual state."""
        self.current_state = state
        if status_text:
            self.status_text = status_text

        # Update cognitive engine with mapped state
        cognitive_state = STATE_TO_COGNITIVE.get(state, "idle_standing")
        self.cognitive_engine.update_state(cognitive_state, transition_time=0.5)

        # Legacy orb update (fallback)
        if state == STATE_IDLE or state == STATE_LISTENING:
            self.orb.set_color(COLOR_LISTENING, PULSE_SPEED_LISTENING)
        elif state == STATE_PROCESSING:
            self.orb.set_color(COLOR_PROCESSING, PULSE_SPEED_PROCESSING)
            if PARTICLES_ENABLED:
                self.orb.add_particles(PARTICLE_COUNT_PROCESSING)
        elif state == STATE_SPEAKING:
            self.orb.set_color(COLOR_SPEAKING, PULSE_SPEED_SPEAKING)
        elif state == STATE_EXECUTING:
            self.orb.set_color(COLOR_EXECUTING, PULSE_SPEED_IDLE)
            if PARTICLES_ENABLED:
                self.orb.add_particles(PARTICLE_COUNT_EXECUTING)
        elif state == STATE_THREAT:
            self.orb.set_color(COLOR_THREAT, PULSE_SPEED_THREAT)
        elif state == STATE_ERROR:
            self.orb.set_color(COLOR_ERROR, PULSE_SPEED_PROCESSING)

        logger.debug(f"State changed: {state} -> cognitive: {cognitive_state}")

    def set_transcription(self, text: str):
        """Set the current transcription text."""
        self.transcription = text

        # Add to conversation history if it's a response
        if text and self.current_state == STATE_SPEAKING:
            self.add_to_conversation("AI", text)

    def add_to_conversation(self, speaker: str, text: str):
        """Add a message to conversation history."""
        import time as t
        self.conversation_history.append({
            'speaker': speaker,
            'text': text,
            'time': t.time()
        })

        # Keep only last N messages
        if len(self.conversation_history) > self.max_conversation_lines:
            self.conversation_history = self.conversation_history[-self.max_conversation_lines:]

    def update_sensor_status(self, sensor_statuses: dict):
        """Update sensor online/offline status."""
        logger.info(f"Updating sensor statuses: {sensor_statuses}")
        for sensor_name, online in sensor_statuses.items():
            if sensor_name in self.sensor_icons:
                self.sensor_icons[sensor_name].online = online

    def show_sensor_display(self):
        """Show the sensor status display."""
        self.show_sensors = True
        self.sensor_show_time = time.time()

    def update(self, dt: float):
        """Update all visual elements."""
        # Update cognitive engine
        self.cognitive_engine.update(dt)
        profile = self.cognitive_engine.get_current_profile()
        breath_factor = self.cognitive_engine.get_breathing_factor()

        # Update particle physics using cognitive profile
        self.particle_physics.update(
            dt=dt,
            cohesion=profile.cohesion,
            separation=profile.separation,
            alignment=profile.alignment,
            wander=profile.wander,
            breath_factor=breath_factor,
            speed_multiplier=profile.particle_speed
        )

        # Update legacy orb (fallback)
        self.orb.update(dt)

        # Check if we should hide sensor display
        if self.show_sensors and (time.time() - self.sensor_show_time > SENSOR_DISPLAY_DURATION):
            self.show_sensors = False

        # Process state updates from queue
        try:
            while True:
                state_update = self.state_queue.get_nowait()
                if 'state' in state_update:
                    self.set_state(state_update['state'], state_update.get('text', ''))
                if 'transcription' in state_update:
                    self.set_transcription(state_update['transcription'])
                if 'sensors' in state_update:
                    self.update_sensor_status(state_update['sensors'])
                if 'show_sensors' in state_update:
                    self.show_sensor_display()
                if 'arduino_peripherals' in state_update:
                    self.arduino_peripherals = state_update['arduino_peripherals']
                # NEW: Sensor data updates for visualization
                if 'wifi_data' in state_update:
                    self.wifi_data = state_update['wifi_data']
                    self.cognitive_engine.update_sensor_data('wifi_networks', self.wifi_data)
                if 'bluetooth_data' in state_update:
                    self.bluetooth_data = state_update['bluetooth_data']
                    self.cognitive_engine.update_sensor_data('bluetooth_devices', self.bluetooth_data)
                if 'audio_data' in state_update:
                    self.audio_data = state_update['audio_data']
                    self.cognitive_engine.update_sensor_data('audio_amplitude',
                        self.audio_data.get('amplitude', 0.0))
        except queue.Empty:
            pass

    def draw_arduino_peripherals(self):
        """Draw the Arduino peripherals panel."""
        panel_rect = pygame.Rect(50, 150, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 250)
        pygame.draw.rect(self.screen, (20, 30, 40, 230), panel_rect, border_radius=15)

        title_surface = self.font_medium.render("Arduino Peripherals", True, (255, 255, 255))
        self.screen.blit(title_surface, (panel_rect.x + 20, panel_rect.y + 20))

        y_offset = panel_rect.y + 70
        for name, props in self.arduino_peripherals.items():
            name_surface = self.font_small.render(f"{name} ({props['type']} on pin {props['pin']})", True, (200, 200, 200))
            self.screen.blit(name_surface, (panel_rect.x + 20, y_offset))

            if props['type'] == 'led':
                button_rect = pygame.Rect(panel_rect.x + 300, y_offset, 100, 30)
                pygame.draw.rect(self.screen, (0, 100, 200), button_rect, border_radius=5)
                button_text = "ON" if props.get('value') == "1" else "OFF"
                text_surface = self.font_small.render(button_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (button_rect.x + 35, button_rect.y + 5))
                # Add a click handler for this button in the run loop

            elif props['type'] == 'sensor':
                value_surface = self.font_small.render(str(props.get('value', 'N/A')), True, (255, 255, 255))
                self.screen.blit(value_surface, (panel_rect.x + 300, y_offset))

            y_offset += 40

    def send_arduino_command(self, name, command, value=None):
        """Send a command to the Arduino daemon."""
        action = {
            "target_daemon": "arduino",
            "action": command,
            "parameters": {"name": name, "value": value}
        }
        self.command_queue.put(action)

    def draw_particle_humanoid(self):
        """Draw the 10,000 particle humanoid visualization."""
        # Get positions from particle physics (in normalized 3D space [-1, 1])
        positions_3d = self.particle_physics.get_positions_for_distribution("humanoid")

        # Get current cognitive profile for visual effects
        profile = self.cognitive_engine.get_current_profile()
        breath_factor = self.cognitive_engine.get_breathing_factor()

        # Apply sensor visualizer colors and effects
        particle_colors = self.sensor_visualizer.apply_sensor_colors(
            positions_3d,
            wifi_data=self.wifi_data,
            bluetooth_data=self.bluetooth_data,
            audio_amplitude=self.audio_data.get('amplitude', 0.0),
            base_color=profile.color_shift
        )

        # Project 3D positions to 2D screen coordinates
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        scale = 300 * (1.0 + breath_factor * 0.2)  # Breathing effect

        for i, pos_3d in enumerate(positions_3d):
            # Simple orthographic projection (ignore Z for now)
            x = int(center_x + pos_3d[0] * scale)
            y = int(center_y + pos_3d[1] * scale)

            # Skip particles outside screen bounds
            if not (0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT):
                continue

            # Get particle color with glow
            color = particle_colors[i]
            alpha = int(255 * profile.glow_intensity)

            # Draw particle as small circle
            particle_size = max(1, int(2 * profile.glow_intensity))
            pygame.draw.circle(self.screen, color[:3], (x, y), particle_size)

    def draw_conversation_history(self):
        """Draw conversation history panel."""
        if not self.conversation_history:
            return

        # Panel on the left side
        panel_width = 350
        panel_height = WINDOW_HEIGHT - 100
        panel_x = 20
        panel_y = 50

        # Semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (20, 30, 40, 200),
                        (0, 0, panel_width, panel_height), border_radius=15)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Title
        title = self.font_medium.render("Conversation", True, (100, 200, 255))
        self.screen.blit(title, (panel_x + 20, panel_y + 10))

        # Draw conversation messages
        y_offset = panel_y + 50
        line_height = 60

        for msg in self.conversation_history[-6:]:  # Show last 6 messages
            speaker_color = (100, 200, 255) if msg['speaker'] == "AI" else (255, 200, 100)

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

            # Draw lines (max 2 lines per message)
            for i, line in enumerate(lines[:2]):
                text_surface = self.font_small.render(line, True, (220, 220, 220))
                self.screen.blit(text_surface, (panel_x + 20, y_offset + 20 + i * 18))

            y_offset += line_height

            if y_offset > panel_y + panel_height - 70:
                break

    def draw(self):
        """Render all visual elements."""
        # Clear screen
        self.screen.fill(COLOR_BACKGROUND)

        # Draw conversation history panel
        self.draw_conversation_history()

        # Draw visualization based on mode
        if self.use_particle_mode:
            # NEW: Particle-based humanoid silhouette with cognitive engine
            self.draw_particle_humanoid()
        else:
            # Legacy orb with friendly face (fallback)
            self.orb.draw(self.screen)

        # Draw status text (more friendly)
        status_surface = self.font_large.render(self.status_text, True, (255, 255, 255))
        status_rect = status_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(status_surface, status_rect)

        # Draw transcription (if speaking or processing)
        if self.transcription and self.current_state in [STATE_SPEAKING, STATE_PROCESSING]:
            # Word wrap transcription
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

            # Draw lines
            y_offset = WINDOW_HEIGHT - 200
            for line in lines[-3:]:  # Show last 3 lines
                trans_surface = self.font_medium.render(line, True, (200, 200, 200))
                trans_rect = trans_surface.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(trans_surface, trans_rect)
                y_offset += 30

        # Draw sensor icons (if requested)
        if self.show_sensors:
            for icon in self.sensor_icons.values():
                icon.draw(self.screen, self.font_emoji)

        if self.show_arduino_peripherals:
            self.draw_arduino_peripherals()

        # Draw text input box with better label
        input_label = self.font_small.render("Type your message:", True, (150, 150, 150))
        self.screen.blit(input_label, (self.input_box.rect.x, self.input_box.rect.y - 20))
        self.input_box.draw(self.screen)

        # Draw FPS counter (if enabled)
        if SHOW_FPS:
            fps_text = f"FPS: {int(self.clock.get_fps())}"
            fps_surface = self.font_small.render(fps_text, True, (100, 100, 100))
            self.screen.blit(fps_surface, (10, 10))

        # Update display
        pygame.display.flip()

    def run(self):
        """Main GUI loop."""
        self.running = True
        logger.info("Aura Interface running...")

        while self.running:
            # Handle events
            for event in pygame.event.get():
                command = self.input_box.handle_event(event)
                if command:
                    self.command_queue.put(command)

                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_arduino_peripherals:
                        y_offset = 150 + 70
                        for name, props in self.arduino_peripherals.items():
                            if props['type'] == 'led':
                                button_rect = pygame.Rect(50 + 300, y_offset, 100, 30)
                                if button_rect.collidepoint(event.pos):
                                    new_value = 1 if props.get('value') == "0" else 0
                                    self.send_arduino_command(name, "write", new_value)
                            y_offset += 40

                    if self.show_sensors:
                        for sensor_name, icon in self.sensor_icons.items():
                            if icon.name == 'arduino' and pygame.Rect(icon.x - icon.size // 2, icon.y - icon.size // 2, icon.size, icon.size).collidepoint(event.pos):
                                self.show_arduino_peripherals = not self.show_arduino_peripherals
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_s:
                        # Toggle sensor display
                        if not self.show_sensors:
                            self.show_sensor_display()

            # Update
            dt = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            self.update(dt)

            # Draw
            self.draw()

        logger.info("Aura Interface stopped")
        pygame.quit()

    def start(self):
        """Start GUI in a separate thread."""
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        logger.info("Aura Interface thread started")

    def stop(self):
        """Stop the GUI."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("Starting Aura Interface...")
    print("Press ESC to quit, S to toggle sensor display")

    aura = AuraInterface()

    # Simulate state changes for demo
    import time as t
    def demo_states():
        t.sleep(2)
        aura.state_queue.put({'state': STATE_LISTENING, 'text': 'Listening...'})
        t.sleep(2)
        aura.state_queue.put({'state': STATE_PROCESSING, 'text': 'Thinking...'})
        t.sleep(2)
        aura.state_queue.put({
            'state': STATE_SPEAKING,
            'text': 'Speaking...',
            'transcription': 'Hello! I am your sentient core. All systems are operational and ready.'
        })
        t.sleep(3)
        aura.state_queue.put({'state': STATE_EXECUTING, 'text': 'Executing: RF Scan'})
        t.sleep(2)
        aura.state_queue.put({'state': STATE_LISTENING, 'text': 'Listening...'})

    # Run demo in background
    import threading
    demo_thread = threading.Thread(target=demo_states, daemon=True)
    demo_thread.start()

    # Run GUI (blocking)
    aura.run()
