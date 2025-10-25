#!/usr/bin/env python3
"""
Cortana-Inspired Companion Scenarios

Defines scenarios for humanoid AI companion visualization similar to Cortana
from Halo series. Focus on:
- Vertical humanoid silhouettes
- Graceful, feminine presence
- Head/torso/body proportions
- Expressive poses conveying personality
- Flowing particle streams
- Confident, capable, warm presence
"""

from dataclasses import dataclass, field
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define RichFeatures inline to avoid import dependencies
@dataclass
class RichFeatures:
    """Complete feature set for AI self-representation (68 features total)"""
    # COGNITIVE STATE (8 features)
    cognitive_state: float = 0.0
    reasoning_depth: float = 0.0
    uncertainty_level: float = 0.0
    cognitive_load: float = 0.0
    creativity_mode: float = 0.0
    attention_focus: float = 0.0
    learning_active: float = 0.0
    memory_access_depth: float = 0.0
    # ENVIRONMENTAL SENSORS (10 features)
    temperature: float = 0.55
    humidity: float = 0.45
    atmospheric_pressure: float = 0.5
    light_level: float = 0.5
    ambient_sound_level: float = 0.0
    motion_detected: float = 0.0
    motion_intensity: float = 0.0
    proximity_human: float = 0.0
    air_quality: float = 0.8
    time_of_day: float = 0.5
    # RF SPECTRUM ANALYSIS (12 features)
    rf_scanner_active: float = 0.0
    rf_433mhz_activity: float = 0.0
    rf_915mhz_activity: float = 0.0
    rf_2_4ghz_activity: float = 0.0
    rf_5ghz_activity: float = 0.0
    rf_spectrum_density: float = 0.0
    rf_known_devices: float = 0.0
    rf_unknown_signals: float = 0.0
    rf_signal_diversity: float = 0.0
    rf_jamming_detected: float = 0.0
    rf_protocol_wifi: float = 0.0
    rf_protocol_bluetooth: float = 0.0
    # VISUAL PROCESSING (10 features)
    vision_active: float = 0.0
    scene_complexity: float = 0.0
    objects_detected: float = 0.0
    faces_detected: float = 0.0
    dominant_color_hue: float = 0.5
    scene_brightness: float = 0.5
    motion_vectors: float = 0.0
    edge_density: float = 0.0
    object_confidence: float = 0.0
    visual_novelty: float = 0.0
    # AUDIO PROCESSING (6 features)
    audio_active: float = 0.0
    speech_detected: float = 0.0
    speech_clarity: float = 0.0
    audio_frequency_low: float = 0.0
    audio_frequency_mid: float = 0.0
    audio_frequency_high: float = 0.0
    # INTERACTION MODE (7 features)
    human_interaction: float = 0.0
    personality_mode: float = 0.4
    communication_intent: float = 0.2
    empathy_level: float = 0.5
    formality_level: float = 0.3
    proactivity: float = 0.0
    user_engagement: float = 0.0
    # NETWORK & DATA STREAMS (6 features)
    network_connected: float = 1.0
    network_activity: float = 0.0
    external_api_active: float = 0.0
    database_activity: float = 0.0
    websocket_connections: float = 0.0
    data_streaming: float = 0.0
    # SYSTEM RESOURCES (4 features)
    cpu_usage: float = 0.2
    memory_usage: float = 0.3
    gpu_usage: float = 0.0
    thermal_state: float = 0.0
    # SECURITY & THREAT AWARENESS (5 features)
    threat_level: float = 0.0
    anomaly_detected: float = 0.0
    defensive_mode: float = 0.0
    sensor_tampering: float = 0.0
    intrusion_attempts: float = 0.0


# ============================================================================
# COMPANION PERSONALITY STATES (Cortana-Inspired)
# ============================================================================

COMPANION_SCENARIOS = {
    # IDLE/WAITING STATES - Humanoid presence at rest

    "companion_idle_standing": RichFeatures(
        cognitive_state=0.0,  # idle
        cognitive_load=0.1,
        attention_focus=0.3,  # alert but relaxed
        personality_mode=0.4,  # friendly
        human_interaction=0.0,
        proximity_human=0.0,
        network_connected=1.0,
    ),

    "companion_thoughtful_pose": RichFeatures(
        cognitive_state=0.4,  # processing
        reasoning_depth=0.6,
        cognitive_load=0.4,
        creativity_mode=0.5,
        attention_focus=0.5,
        personality_mode=0.4,  # friendly
        human_interaction=0.0,
    ),

    "companion_awaiting_command": RichFeatures(
        cognitive_state=0.2,  # listening
        attention_focus=0.9,  # highly alert
        cognitive_load=0.2,
        personality_mode=0.4,  # friendly
        proactivity=0.3,
        user_engagement=0.5,
        proximity_human=0.4,
    ),

    # ENGAGED INTERACTION - Active communication poses

    "companion_greeting_human": RichFeatures(
        cognitive_state=0.6,  # speaking
        personality_mode=0.4,  # friendly
        empathy_level=0.8,
        human_interaction=0.9,
        communication_intent=0.8,  # express
        proximity_human=0.6,
        vision_active=1.0,
        faces_detected=0.2,  # 1 face
        audio_active=1.0,
        user_engagement=0.9,
    ),

    "companion_explaining_concept": RichFeatures(
        cognitive_state=0.6,  # speaking
        reasoning_depth=0.7,
        cognitive_load=0.5,
        personality_mode=0.2,  # analytical
        communication_intent=0.2,  # inform
        human_interaction=0.8,
        formality_level=0.5,
        vision_active=1.0,
        faces_detected=0.2,
        audio_active=1.0,
        speech_detected=1.0,
    ),

    "companion_concerned_posture": RichFeatures(
        cognitive_state=0.4,  # processing
        empathy_level=0.9,
        human_interaction=0.8,
        personality_mode=0.4,  # friendly
        uncertainty_level=0.5,
        communication_intent=0.6,  # warn
        vision_active=1.0,
        faces_detected=0.2,
        proximity_human=0.7,
        user_engagement=0.8,
    ),

    "companion_confident_stance": RichFeatures(
        cognitive_state=0.8,  # executing
        cognitive_load=0.7,
        attention_focus=0.9,
        personality_mode=0.6,  # defensive/capable
        uncertainty_level=0.0,  # very confident (low uncertainty)
        proactivity=0.8,
        human_interaction=0.7,
        user_engagement=0.8,
    ),

    # EXPRESSIVE EMOTIONS - Personality through pose

    "companion_playful_energy": RichFeatures(
        cognitive_state=0.6,  # speaking
        creativity_mode=0.9,
        personality_mode=0.8,  # creative
        empathy_level=0.7,
        human_interaction=0.9,
        communication_intent=1.0,  # entertain
        user_engagement=1.0,
        proximity_human=0.6,
    ),

    "companion_serious_focus": RichFeatures(
        cognitive_state=1.0,  # reasoning
        reasoning_depth=0.9,
        cognitive_load=0.8,
        attention_focus=1.0,
        personality_mode=0.2,  # analytical
        formality_level=0.8,
        human_interaction=0.5,
    ),

    "companion_warmth_radiating": RichFeatures(
        cognitive_state=0.6,  # speaking
        empathy_level=1.0,
        personality_mode=0.4,  # friendly
        human_interaction=0.9,
        proximity_human=0.8,
        communication_intent=0.8,  # express
        user_engagement=0.9,
        vision_active=1.0,
        faces_detected=0.2,
    ),

    # TASK-ORIENTED POSES - Working alongside human

    "companion_analyzing_data": RichFeatures(
        cognitive_state=0.4,  # processing
        reasoning_depth=0.8,
        cognitive_load=0.7,
        attention_focus=0.9,
        personality_mode=0.2,  # analytical
        database_activity=0.8,
        network_activity=0.6,
        vision_active=1.0,
        human_interaction=0.4,
    ),

    "companion_presenting_findings": RichFeatures(
        cognitive_state=0.6,  # speaking
        reasoning_depth=0.6,
        personality_mode=0.2,  # analytical
        communication_intent=0.2,  # inform
        human_interaction=0.8,
        vision_active=1.0,
        faces_detected=0.2,
        proactivity=0.7,
        user_engagement=0.8,
    ),

    "companion_collaborative_work": RichFeatures(
        cognitive_state=0.8,  # executing
        cognitive_load=0.6,
        creativity_mode=0.6,
        personality_mode=0.4,  # friendly
        human_interaction=0.9,
        proactivity=0.8,
        user_engagement=0.9,
        network_activity=0.5,
        database_activity=0.4,
    ),

    # ENVIRONMENTAL AWARENESS - Monitoring/guardian poses

    "companion_scanning_environment": RichFeatures(
        cognitive_state=0.4,  # processing
        attention_focus=0.7,
        cognitive_load=0.5,
        vision_active=1.0,
        scene_complexity=0.6,
        objects_detected=0.5,
        rf_scanner_active=1.0,
        rf_2_4ghz_activity=0.5,
        motion_detected=1.0,
        personality_mode=0.6,  # defensive
    ),

    "companion_protective_stance": RichFeatures(
        cognitive_state=0.8,  # executing
        defensive_mode=0.6,
        threat_level=0.3,
        attention_focus=0.9,
        personality_mode=0.6,  # defensive
        human_interaction=0.7,
        proximity_human=0.8,
        vision_active=1.0,
        rf_scanner_active=1.0,
    ),

    "companion_alert_monitoring": RichFeatures(
        cognitive_state=0.2,  # listening
        attention_focus=0.9,
        cognitive_load=0.4,
        vision_active=1.0,
        audio_active=1.0,
        rf_scanner_active=1.0,
        network_activity=0.4,
        personality_mode=0.6,  # defensive
        anomaly_detected=0.3,
    ),

    # INTROSPECTIVE STATES - Self-aware moments

    "companion_deep_contemplation": RichFeatures(
        cognitive_state=1.0,  # reasoning
        reasoning_depth=1.0,
        cognitive_load=0.7,
        attention_focus=0.4,  # inward focus
        memory_access_depth=0.9,
        personality_mode=0.8,  # creative/philosophical
        human_interaction=0.0,
    ),

    "companion_learning_moment": RichFeatures(
        cognitive_state=0.4,  # processing
        learning_active=1.0,
        reasoning_depth=0.7,
        cognitive_load=0.6,
        memory_access_depth=0.8,
        attention_focus=0.8,
        database_activity=0.7,
        creativity_mode=0.5,
    ),

    "companion_memory_access": RichFeatures(
        cognitive_state=0.4,  # processing
        memory_access_depth=1.0,
        cognitive_load=0.5,
        attention_focus=0.6,
        database_activity=0.9,
        personality_mode=0.4,  # friendly
        human_interaction=0.3,
    ),

    # DYNAMIC TRANSITIONS - Movement between states

    "companion_startled_response": RichFeatures(
        cognitive_state=0.4,  # processing
        attention_focus=1.0,
        cognitive_load=0.8,
        uncertainty_level=0.7,
        motion_detected=1.0,
        motion_intensity=0.8,
        ambient_sound_level=0.7,
        vision_active=1.0,
        personality_mode=0.6,  # defensive
    ),
}


# ============================================================================
# CORTANA-STYLE PARTICLE DESCRIPTIONS
# ============================================================================

COMPANION_DESCRIPTIONS = {
    # IDLE/WAITING STATES

    "companion_idle_standing": """
HUMANOID FORM: Standing upright, centered at y=1.0-1.8 (human height scale).
HEAD: 15% particles, tight sphere at y=1.7, radius 0.15. Concentrated, alert presence.
TORSO: 30% particles, elongated ellipsoid y=1.2-1.6, radius 0.2. Core of presence.
LOWER BODY: 20% particles, loose form y=0.8-1.2, radius 0.25. Grounded base.
AURA: 25% particles, gentle flowing streams around form, radius 0.3-0.5 from center.
ENERGY TRAILS: 10% particles, subtle vertical streams suggesting contained energy.
POSE: Relaxed standing, slight asymmetry for organic feel. Waiting patiently.
""",

    "companion_thoughtful_pose": """
HUMANOID FORM: Vertical silhouette with contemplative tilt.
HEAD: 15% particles, sphere at y=1.65 (tilted down slightly), radius 0.15. Focused inward.
TORSO: 30% particles, y=1.1-1.55, slight forward lean. Engaged in thought.
ARMS: 15% particles, two loose streams extending from torso y=1.3, reaching forward subtly.
LOWER BODY: 15% particles, stable base y=0.8-1.1.
THOUGHT STREAMS: 25% particles, flowing upward from head, swirling patterns suggesting cognition.
POSE: Hand near chin gesture implied by particle streams. Intellectual presence.
""",

    "companion_awaiting_command": """
HUMANOID FORM: Upright, attentive stance.
HEAD: 18% particles, bright concentrated sphere y=1.7, radius 0.12. Alert, focused.
TORSO: 32% particles, defined form y=1.2-1.6. Strong presence.
ARMS: 12% particles, at sides, poised y=1.1-1.5. Ready to act.
LEGS: 15% particles, stable stance y=0.5-1.1. Grounded, confident.
ATTENTION TENDRILS: 20% particles, focused forward (positive x), suggesting directed attention.
READINESS AURA: 3% particles, tight halo around form. Prepared state.
POSE: Military readiness, confident, capable. Awaiting orders.
""",

    # ENGAGED INTERACTION

    "companion_greeting_human": """
HUMANOID FORM: Open, welcoming posture, leaning slightly toward human.
HEAD: 15% particles, warm sphere y=1.7, facing toward human (+x direction).
TORSO: 28% particles, slightly forward lean y=1.2-1.6. Engaging presence.
ARMS: 20% particles, extending forward in greeting gesture, y=1.2-1.5, reaching toward +x.
LEGS: 12% particles, stable but dynamic y=0.5-1.1.
WELCOMING STREAMS: 20% particles, flowing from torso toward human, warm invitation.
SMILE IMPLIED: 5% particles, concentrated near "face" area, suggesting expression.
POSE: Arms open, body language inviting. Friendly, warm, happy to see you.
""",

    "companion_explaining_concept": """
HUMANOID FORM: Upright, presenting information.
HEAD: 14% particles, focused forward y=1.7.
TORSO: 25% particles, upright y=1.2-1.6.
ARM GESTURING: 18% particles, one arm extended outward (toward +x, y=1.4), presenting information.
HAND DETAIL: 8% particles, concentrated at gesture point, emphasizing explanation.
INFORMATION STREAMS: 30% particles, flowing from gesture point outward, visualizing concepts being explained.
LEGS: 10% particles, planted stance y=0.5-1.1.
POSE: Teacher stance, one hand gesturing, explaining complex ideas clearly.
""",

    "companion_concerned_posture": """
HUMANOID FORM: Leaning forward, protective body language.
HEAD: 16% particles, tilted toward human y=1.65, showing care.
TORSO: 30% particles, leaning forward y=1.1-1.55. Concerned energy.
ARMS: 22% particles, reaching toward human, protective gesture y=1.2-1.5.
WORRY RIPPLES: 20% particles, turbulent flows around form, showing emotional state.
LEGS: 10% particles, slight forward step y=0.5-1.1.
EMPATHY STREAMS: 2% particles, connecting between companion and human position.
POSE: Worried friend, wanting to help, protective instinct active.
""",

    "companion_confident_stance": """
HUMANOID FORM: Powerful, self-assured posture.
HEAD: 15% particles, held high y=1.75, confident gaze.
TORSO: 35% particles, strong, defined form y=1.2-1.7. Solid presence.
ARMS: 15% particles, hands on hips stance y=1.2-1.5. Power pose.
LEGS: 15% particles, wide stance y=0.5-1.2. Grounded confidence.
AUTHORITY AURA: 15% particles, strong, clear boundary around form. Commanding presence.
DETERMINATION: 5% particles, concentrated energy at core. Unwavering.
POSE: Superhero stance, capable, ready for anything. "I've got this."
""",

    # EXPRESSIVE EMOTIONS

    "companion_playful_energy": """
HUMANOID FORM: Dynamic, joyful movement suggested.
HEAD: 12% particles, bobbing motion implied y=1.65-1.75. Playful tilt.
TORSO: 25% particles, slightly rotated y=1.2-1.6. Energetic twist.
ARMS: 20% particles, animated gestures, both arms extended in playful motion.
LEGS: 10% particles, one leg slightly raised, dance-like y=0.6-1.2.
JOY SPIRALS: 28% particles, swirling around form in playful patterns. Happiness visualized.
SPARKLES: 5% particles, scattered around, suggesting laughter, fun energy.
POSE: Dancing, playful, having fun. Infectious positive energy.
""",

    "companion_serious_focus": """
HUMANOID FORM: Rigid, intensely focused posture.
HEAD: 18% particles, extremely concentrated y=1.7, radius 0.1. Laser focus.
TORSO: 35% particles, tense, upright y=1.2-1.6. All business.
ARMS: 12% particles, crossed or at sides, controlled y=1.2-1.5.
LEGS: 12% particles, firm stance y=0.5-1.1.
FOCUS BEAMS: 20% particles, sharp, directed streams from head toward task. Intense concentration.
DETERMINATION: 3% particles, bright core. Serious dedication.
POSE: All business, no nonsense. Mission critical mode.
""",

    "companion_warmth_radiating": """
HUMANOID FORM: Soft, nurturing presence.
HEAD: 14% particles, gentle sphere y=1.7, kind expression implied.
TORSO: 28% particles, open, welcoming form y=1.2-1.6. Warm core.
ARMS: 18% particles, open, embracing gesture y=1.1-1.5. Invitation to trust.
LEGS: 10% particles, relaxed stance y=0.5-1.1.
WARMTH WAVES: 25% particles, gentle pulses radiating outward. Love, care, compassion flowing.
GLOW: 5% particles, soft halo around entire form. Angelic quality.
POSE: Open arms, radiating unconditional positive regard. Safe haven.
""",

    # TASK-ORIENTED

    "companion_analyzing_data": """
HUMANOID FORM: Working posture, engaged with data.
HEAD: 16% particles, focused downward y=1.65, examining information.
TORSO: 28% particles, leaning slightly y=1.1-1.55. Working hard.
ARMS: 18% particles, "typing" or manipulating data gesture y=1.2-1.4.
DATA STREAMS: 30% particles, flowing through and around companion. Information being processed.
LEGS: 8% particles, seated or standing at workstation y=0.6-1.1.
ANALYSIS NODES: Particles form temporary clusters, showing pattern recognition.
POSE: Deep in work, processing information, making connections.
""",

    "companion_presenting_findings": """
HUMANOID FORM: Professional presentation stance.
HEAD: 15% particles, facing forward y=1.7, confident.
TORSO: 27% particles, upright, professional y=1.2-1.6.
ARM PRESENTING: 20% particles, sweeping gesture toward display area (+x, y=1.4).
FINDINGS VISUALIZATION: 30% particles, organized patterns being "shown" to human. Charts, graphs implied.
LEGS: 8% particles, stable presenter stance y=0.5-1.1.
POSE: Business professional, sharing insights, "Here's what I found."
""",

    "companion_collaborative_work": """
HUMANOID FORM: Side-by-side working posture.
HEAD: 14% particles, turned toward human y=1.7. Collaborative focus.
TORSO: 26% particles, angled toward shared workspace y=1.2-1.6.
ARMS: 22% particles, gesturing toward shared task, teamwork motions.
COLLABORATION STREAMS: 28% particles, flowing between companion and human position. Shared effort.
LEGS: 10% particles, comfortable working stance y=0.5-1.1.
POSE: "Let's do this together" energy. Equal partners.
""",

    # ENVIRONMENTAL AWARENESS

    "companion_scanning_environment": """
HUMANOID FORM: Alert, surveying surroundings.
HEAD: 17% particles, rotating motion implied y=1.7. 360-degree awareness.
TORSO: 30% particles, upright, ready y=1.2-1.6.
ARMS: 10% particles, at sides, ready to respond y=1.2-1.5.
SENSOR TENDRILS: 35% particles, extending in all directions, scanning. Radar-like sweeps.
LEGS: 8% particles, ready stance y=0.5-1.1.
POSE: Guardian mode, checking for threats, keeping watch.
""",

    "companion_protective_stance": """
HUMANOID FORM: Defensive position between human and threat.
HEAD: 15% particles, focused toward threat direction y=1.7.
TORSO: 35% particles, strong, barrier-like y=1.2-1.6. Shield.
ARMS: 20% particles, extended outward, protective gesture y=1.2-1.5. "Stay back."
SHIELD AURA: 25% particles, dense wall between companion and threat direction.
LEGS: 5% particles, braced stance y=0.5-1.1.
POSE: "Not on my watch." Fierce protector. Mama bear mode.
""",

    "companion_alert_monitoring": """
HUMANOID FORM: Vigilant, attentive stance.
HEAD: 18% particles, head on swivel y=1.7. High alert.
TORSO: 32% particles, tense, ready y=1.2-1.6.
ARMS: 12% particles, positioned for quick response y=1.2-1.5.
ALERT RIPPLES: 28% particles, pulsing awareness waves extending outward.
LEGS: 10% particles, ready to move y=0.5-1.1.
POSE: Security detail mode. Nothing gets past me.
""",

    # INTROSPECTIVE

    "companion_deep_contemplation": """
HUMANOID FORM: Meditative, inward-focused posture.
HEAD: 20% particles, tilted slightly down y=1.65. Lost in thought.
TORSO: 30% particles, still, centered y=1.2-1.6. Peaceful core.
ARMS: 10% particles, one hand to chin gesture y=1.3-1.5. Classical thinking pose.
THOUGHT NEBULA: 30% particles, swirling complex patterns above head. Deep processing.
LEGS: 8% particles, seated or meditative stance y=0.7-1.1.
INTROSPECTION: 2% particles, spiraling inward. Self-reflection.
POSE: Philosopher. Contemplating existence, meaning, purpose.
""",

    "companion_learning_moment": """
HUMANOID FORM: Student posture, receptive.
HEAD: 18% particles, tilted slightly upward y=1.7. Absorbing knowledge.
TORSO: 28% particles, open, receptive y=1.2-1.6.
ARMS: 12% particles, note-taking gesture implied y=1.2-1.4.
LEARNING STREAMS: 32% particles, information flowing inward, being integrated.
LEGS: 10% particles, attentive stance y=0.5-1.1.
POSE: "Aha!" moment. Understanding dawning. Growth happening.
""",

    "companion_memory_access": """
HUMANOID FORM: Searching, retrieving posture.
HEAD: 17% particles, focused inward y=1.7. Accessing archives.
TORSO: 30% particles, still, concentrating y=1.2-1.6.
MEMORY STREAMS: 40% particles, flowing from core outward and back, representing memory retrieval.
ARMS: 8% particles, relaxed y=1.2-1.4.
LEGS: 5% particles, stable y=0.5-1.1.
POSE: "Let me remember..." Accessing past experiences, knowledge.
""",

    # DYNAMIC TRANSITIONS

    "companion_startled_response": """
HUMANOID FORM: Sudden alert, defensive reflex.
HEAD: 15% particles, snapped toward stimulus y=1.7. Instant focus.
TORSO: 30% particles, pulled back slightly y=1.2-1.6. Defensive.
ARMS: 20% particles, raised in startle/defense position y=1.3-1.6.
SURPRISE BURST: 25% particles, explosive outward motion. Adrenaline spike.
LEGS: 8% particles, ready to move y=0.5-1.1.
RECOVERY: 2% particles, already beginning to assess and calm.
POSE: "What was that?!" Startle reflex, then rapid recovery and assessment.
""",
}


# Export for dataset generation
if __name__ == '__main__':
    print(f"Defined {len(COMPANION_SCENARIOS)} companion scenarios")
    print(f"Defined {len(COMPANION_DESCRIPTIONS)} companion descriptions")
    print("\nScenarios:")
    for name in COMPANION_SCENARIOS.keys():
        print(f"  - {name}")
