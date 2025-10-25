#!/usr/bin/env python3
"""
Quick Test Script for Cognitive Integration
============================================

Tests the complete integrated system:
1. Cognitive Engine
2. Particle Physics
3. Sensor Visualizer
4. Pygame Interface with Text Input

Run this to verify everything works before full integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import time
import numpy as np
from sentient_aura.aura_interface_cognitive import CognitiveAuraInterface, STATE_PROCESSING, STATE_SPEAKING, STATE_IDLE

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("\n" + "=" * 70)
print("SENTIENT CORE v4 - COGNITIVE INTEGRATION TEST")
print("=" * 70)
print("\nThis test will:")
print("  1. Initialize cognitive aura interface (10,000 particles)")
print("  2. Demonstrate personality state transitions")
print("  3. Simulate sensor data (WiFi, Bluetooth, Audio)")
print("  4. Show text input functionality")
print("\nControls:")
print("  - Type in the text box and press ENTER to send messages")
print("  - Watch particles change behavior with each personality state")
print("  - Press ESC to quit")
print("\n" + "=" * 70 + "\n")

input("Press ENTER to start the test...")

# Create interface with reduced particles for testing
aura = CognitiveAuraInterface(num_particles=5000)

# Simulate state changes and sensor data
def demo_sequence():
    """Run through demo scenarios."""
    time.sleep(2)

    # 1. IDLE STATE
    print("\n[DEMO] Setting to IDLE state (idle_standing personality)")
    aura.state_queue.put({
        'state': STATE_IDLE,
        'text': 'System initialized. Ready for commands.',
        'personality': 'idle_standing'
    })
    time.sleep(3)

    # 2. GREETING
    print("\n[DEMO] Greeting human (greeting_human personality)")
    aura.state_queue.put({
        'state': STATE_SPEAKING,
        'text': 'Greeting...',
        'transcription': 'Hello! I am your Sentient Core. All cognitive systems are online.',
        'personality': 'greeting_human'
    })
    time.sleep(4)

    # 3. LISTENING with WiFi sensor data
    print("\n[DEMO] Listening + WiFi visualization (blue particles)")
    aura.state_queue.put({
        'state': STATE_IDLE,
        'text': 'Listening...',
        'personality': 'listening_intently',
        'sensor_data': {
            'wifi_networks': [
                {'ssid': 'HomeNetwork', 'bssid': 'AA:BB:CC:DD:EE:FF', 'signal': -45},
                {'ssid': 'NeighborWiFi', 'bssid': '11:22:33:44:55:66', 'signal': -65},
                {'ssid': 'Office5G', 'bssid': 'AA:11:BB:22:CC:33', 'signal': -55}
            ],
            'bluetooth_devices': [],
            'audio_amplitude': 0.0,
            'gps_movement': np.array([0.0, 0.0, 0.0])
        }
    })
    time.sleep(4)

    # 4. ANALYZING DATA
    print("\n[DEMO] Analyzing data (analyzing_data personality - fast particles)")
    aura.state_queue.put({
        'state': STATE_PROCESSING,
        'text': 'Processing sensor data...',
        'personality': 'analyzing_data'
    })
    time.sleep(4)

    # 5. BLUETOOTH DETECTION
    print("\n[DEMO] Bluetooth detected (purple particles)")
    aura.state_queue.put({
        'state': STATE_PROCESSING,
        'text': 'Scanning Bluetooth...',
        'personality': 'scanning_environment',
        'sensor_data': {
            'wifi_networks': [],
            'bluetooth_devices': [
                {'mac': '00:11:22:33:44:55', 'name': 'Phone', 'rssi': -40},
                {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'Headphones', 'rssi': -55}
            ],
            'audio_amplitude': 0.0,
            'gps_movement': np.array([0.0, 0.0, 0.0])
        }
    })
    time.sleep(4)

    # 6. AUDIO RESPONSE
    print("\n[DEMO] Audio detected (green pulsing particles)")
    for i in range(20):
        amplitude = abs(np.sin(i * 0.5)) * 0.8  # Pulsing audio
        aura.state_queue.put({
            'sensor_data': {
                'wifi_networks': [],
                'bluetooth_devices': [],
                'audio_amplitude': amplitude,
                'gps_movement': np.array([0.0, 0.0, 0.0])
            }
        })
        time.sleep(0.2)

    # 7. EXCITED DISCOVERY
    print("\n[DEMO] Excited discovery (chaotic, expansive motion)")
    aura.state_queue.put({
        'state': STATE_PROCESSING,
        'text': 'New pattern discovered!',
        'personality': 'excited_discovery'
    })
    time.sleep(4)

    # 8. THINKING PAUSE
    print("\n[DEMO] Contemplating (slow, contemplative motion)")
    aura.state_queue.put({
        'state': STATE_PROCESSING,
        'text': 'Analyzing implications...',
        'personality': 'thinking_pause'
    })
    time.sleep(4)

    # 9. FINAL RESPONSE
    print("\n[DEMO] Final response (engaged conversation)")
    aura.state_queue.put({
        'state': STATE_SPEAKING,
        'text': 'Responding...',
        'transcription': 'Analysis complete. I have detected 3 WiFi networks, 2 Bluetooth devices, and ambient audio. All systems functioning optimally.',
        'personality': 'engaged_conversation'
    })
    time.sleep(5)

    # 10. RETURN TO IDLE
    print("\n[DEMO] Returning to idle (awaiting command)")
    aura.state_queue.put({
        'state': STATE_IDLE,
        'text': 'Ready for next command.',
        'personality': 'awaiting_command'
    })

    print("\n[DEMO] Demo sequence complete!")
    print("[DEMO] Try typing messages in the text input box!")
    print("[DEMO] Watch how particles respond to different personality states")
    print("[DEMO] Press ESC to exit\n")

# Monitor user commands
def monitor_commands():
    """Monitor and echo user commands."""
    while aura.running:
        try:
            command = aura.command_queue.get(timeout=0.5)
            print(f"\n[USER COMMAND] {command}")

            # Echo response
            aura.state_queue.put({
                'state': STATE_SPEAKING,
                'transcription': f"I received: '{command}'. This is a test echo.",
                'personality': 'engaged_conversation'
            })

            time.sleep(2)

            # Return to idle
            aura.state_queue.put({
                'state': STATE_IDLE,
                'text': 'Ready',
                'personality': 'awaiting_command'
            })

        except:
            pass

# Run demo and command monitor in background
import threading
demo_thread = threading.Thread(target=demo_sequence, daemon=True)
command_thread = threading.Thread(target=monitor_commands, daemon=True)

demo_thread.start()
command_thread.start()

# Run GUI (blocking)
print("\n[TEST] Starting cognitive aura interface...")
print("[TEST] Window should appear shortly...\n")

try:
    aura.run()
except KeyboardInterrupt:
    print("\n\n[TEST] Interrupted by user")
except Exception as e:
    print(f"\n\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nIf you saw:")
print("  ✓ 5000 particles in humanoid shape")
print("  ✓ Particles changing motion with each personality state")
print("  ✓ Blue particles for WiFi, purple for Bluetooth, green for audio")
print("  ✓ Text input box responding to your messages")
print("  ✓ Conversation history showing messages")
print("\nThen INTEGRATION IS SUCCESSFUL! 🎉")
print("\nNext step: Integrate into main SentientCore system")
print("See INTEGRATION_GUIDE.md for instructions")
print("\n" + "=" * 70 + "\n")
