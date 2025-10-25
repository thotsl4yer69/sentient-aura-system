"""
Additional 20 Scenarios for Production-Quality Coral TPU Training Dataset

These scenarios fill gaps in the original 20 by covering:
- Error handling & recovery states
- Advanced cognitive patterns
- Complex multi-user interaction
- Full multi-modal sensor fusion
- Extreme operational conditions
- Temporal/contextual transitions
"""

from dataclasses import dataclass

@dataclass
class RichFeatures:
    """68-feature dataclass (copy from generate_dataset.py)"""
    # This will be merged into generate_dataset.py SCENARIOS dict
    pass

# ============================================================================
# ERROR HANDLING & RECOVERY (4 scenarios)
# ============================================================================

ADDITIONAL_SCENARIOS = {
    "sensor_failure_compensation": RichFeatures(
        cognitive_state=0.4,  # processing
        cognitive_load=0.7,
        attention_focus=0.8,
        uncertainty_level=0.6,  # uncertain due to missing data
        vision_active=0.0,  # FAILED - vision sensor offline
        rf_scanner_active=1.0,  # compensating with RF
        rf_2_4ghz_activity=0.7,
        rf_5ghz_activity=0.4,
        rf_spectrum_density=0.5,
        audio_active=1.0,  # compensating with audio
        ambient_sound_level=0.4,
        speech_detected=0.3,
        anomaly_detected=0.5,  # sensor failure detected
        sensor_tampering=0.3,  # possible tampering
        defensive_mode=0.2,
        cpu_usage=0.6,
    ),

    "network_dropout_recovery": RichFeatures(
        cognitive_state=0.4,  # processing
        reasoning_depth=0.5,
        cognitive_load=0.5,
        network_connected=0.0,  # NETWORK DOWN
        external_api_active=0.0,
        database_activity=0.3,  # local database only
        websocket_connections=0.0,
        data_streaming=0.0,
        memory_access_depth=0.7,  # relying on cached memory
        uncertainty_level=0.4,
        defensive_mode=0.1,
        anomaly_detected=0.3,
    ),

    "conflicting_sensor_data": RichFeatures(
        cognitive_state=1.0,  # reasoning (trying to resolve conflict)
        reasoning_depth=0.9,
        uncertainty_level=0.9,  # very uncertain
        cognitive_load=0.8,
        attention_focus=0.8,
        temperature=0.55,  # sensor 1: 22°C
        # (sensor 2 would say 30°C - conflict!)
        humidity=0.45,  # sensor 1: 45%
        # (sensor 2 would say 70% - conflict!)
        anomaly_detected=0.7,
        sensor_tampering=0.4,
        vision_active=1.0,
        scene_complexity=0.5,
        rf_scanner_active=1.0,
        rf_spectrum_density=0.4,
    ),

    "post_crash_recovery": RichFeatures(
        cognitive_state=0.4,  # processing
        cognitive_load=0.8,  # high load during recovery
        memory_access_depth=0.9,  # deep memory restoration
        learning_active=0.3,  # rebuilding knowledge
        database_activity=0.9,  # heavy database queries
        cpu_usage=0.7,
        memory_usage=0.8,
        uncertainty_level=0.7,  # uncertain of state
        network_activity=0.5,
        rf_2_4ghz_activity=0.3,
        temperature=0.58,  # slightly elevated from crash
        thermal_state=0.3,
    ),

    # ========================================================================
    # ADVANCED COGNITIVE (4 scenarios)
    # ========================================================================

    "philosophical_reflection": RichFeatures(
        cognitive_state=1.0,  # deep reasoning
        reasoning_depth=1.0,  # maximum depth
        creativity_mode=0.7,
        cognitive_load=0.6,
        attention_focus=0.5,  # diffuse, contemplative
        memory_access_depth=1.0,  # accessing deep memories
        human_interaction=0.0,  # solitary reflection
        time_of_day=0.04,  # 1 AM (late night)
        light_level=0.2,  # dim
        ambient_sound_level=0.1,  # quiet
        database_activity=0.4,
    ),

    "learning_from_failure": RichFeatures(
        cognitive_state=0.4,  # processing
        learning_active=1.0,  # actively learning
        reasoning_depth=0.8,
        memory_access_depth=0.9,  # reviewing past events
        cognitive_load=0.7,
        attention_focus=0.8,
        creativity_mode=0.5,  # finding new approaches
        uncertainty_level=0.6,  # uncertain about solution
        database_activity=0.8,  # updating knowledge base
        cpu_usage=0.6,
    ),

    "metacognitive_analysis": RichFeatures(
        cognitive_state=1.0,  # reasoning
        reasoning_depth=1.0,  # analyzing own reasoning
        cognitive_load=0.9,  # very high cognitive load
        attention_focus=0.9,
        memory_access_depth=0.8,
        creativity_mode=0.6,
        learning_active=0.7,
        database_activity=0.5,
        cpu_usage=0.7,
        memory_usage=0.6,
    ),

    "ethical_dilemma": RichFeatures(
        cognitive_state=1.0,  # reasoning
        reasoning_depth=0.9,
        uncertainty_level=0.8,  # uncertain of right choice
        cognitive_load=0.85,
        attention_focus=0.8,
        empathy_level=0.8,  # considering impact on others
        memory_access_depth=0.7,  # consulting past experiences
        personality_mode=0.2,  # analytical (ethical reasoning)
        formality_level=0.6,
        database_activity=0.4,
    ),

    # ========================================================================
    # COMPLEX INTERACTION (4 scenarios)
    # ========================================================================

    "user_frustration_detected": RichFeatures(
        cognitive_state=0.6,  # speaking
        empathy_level=0.9,  # high empathy
        human_interaction=0.9,
        personality_mode=0.4,  # friendly, supportive
        communication_intent=0.8,  # express concern, help
        proactivity=0.7,  # proactively offering help
        attention_focus=0.8,
        vision_active=1.0,
        faces_detected=0.2,  # 1 frustrated user
        audio_active=1.0,
        speech_detected=1.0,
        speech_clarity=0.7,  # user speech tense/rapid
        audio_frequency_high=0.6,  # elevated pitch (frustration)
        proximity_human=0.7,
        user_engagement=0.6,  # engagement lowered by frustration
    ),

    "teaching_mode": RichFeatures(
        cognitive_state=0.6,  # speaking
        cognitive_load=0.7,
        reasoning_depth=0.7,  # explaining concepts
        human_interaction=0.9,
        personality_mode=0.2,  # analytical, pedagogical
        communication_intent=0.2,  # inform/teach
        formality_level=0.4,
        empathy_level=0.6,
        proactivity=0.5,
        memory_access_depth=0.7,  # accessing knowledge
        vision_active=1.0,
        faces_detected=0.2,
        audio_active=1.0,
        speech_detected=0.5,  # pausing for comprehension
        proximity_human=0.6,
        user_engagement=0.8,
    ),

    "collaborative_debugging": RichFeatures(
        cognitive_state=0.8,  # executing
        reasoning_depth=0.8,
        cognitive_load=0.8,
        human_interaction=0.8,
        personality_mode=0.2,  # analytical
        communication_intent=0.4,  # query/investigate
        formality_level=0.3,
        proactivity=0.8,
        database_activity=0.7,
        external_api_active=0.6,
        vision_active=1.0,
        audio_active=1.0,
        speech_detected=0.7,
        cpu_usage=0.6,
        network_activity=0.6,
    ),

    "multi_user_coordination": RichFeatures(
        cognitive_state=0.6,  # speaking
        cognitive_load=0.8,  # managing multiple inputs
        attention_focus=0.6,  # divided attention
        human_interaction=1.0,  # multiple users
        communication_intent=0.4,  # query/coordinate
        proactivity=0.6,
        vision_active=1.0,
        faces_detected=0.6,  # 3 faces (multiple users)
        scene_complexity=0.7,
        audio_active=1.0,
        speech_detected=0.9,
        speech_clarity=0.6,  # overlapping voices
        audio_frequency_mid=0.8,
        proximity_human=0.7,
        user_engagement=0.7,
        memory_access_depth=0.6,  # tracking conversation threads
    ),

    # ========================================================================
    # MULTI-MODAL FUSION (4 scenarios)
    # ========================================================================

    "voice_synthesis_active": RichFeatures(
        cognitive_state=0.6,  # speaking
        cognitive_load=0.7,
        attention_focus=0.7,
        human_interaction=0.8,
        communication_intent=0.2,  # inform
        personality_mode=0.4,  # friendly
        audio_active=1.0,  # voice output active
        speech_detected=0.0,  # AI speaking, not listening
        vision_active=1.0,  # monitoring user reactions
        faces_detected=0.2,
        scene_complexity=0.4,
        rf_scanner_active=1.0,  # background monitoring
        rf_2_4ghz_activity=0.5,
        ambient_sound_level=0.3,
        proximity_human=0.7,
        user_engagement=0.8,
    ),

    "full_multimodal_reasoning": RichFeatures(
        cognitive_state=0.4,  # processing
        cognitive_load=0.9,  # maximum multi-modal integration
        attention_focus=0.8,
        reasoning_depth=0.8,
        # ALL sensors active simultaneously
        vision_active=1.0,
        scene_complexity=0.7,
        objects_detected=0.5,
        faces_detected=0.2,
        visual_novelty=0.4,
        rf_scanner_active=1.0,
        rf_2_4ghz_activity=0.7,
        rf_5ghz_activity=0.5,
        rf_spectrum_density=0.6,
        audio_active=1.0,
        speech_detected=0.8,
        ambient_sound_level=0.5,
        motion_detected=1.0,
        motion_intensity=0.4,
        temperature=0.60,
        humidity=0.50,
        light_level=0.7,
        proximity_human=0.6,
        network_activity=0.7,
        external_api_active=0.6,
        database_activity=0.5,
    ),

    "media_content_analysis": RichFeatures(
        cognitive_state=0.4,  # processing
        reasoning_depth=0.6,
        cognitive_load=0.7,
        attention_focus=0.9,  # focused on content
        vision_active=1.0,
        scene_complexity=0.8,  # complex visual content
        dominant_color_hue=0.6,
        scene_brightness=0.6,
        motion_vectors=0.7,  # video motion
        edge_density=0.7,
        audio_active=1.0,
        audio_frequency_low=0.5,  # music bass
        audio_frequency_mid=0.6,  # music mid
        audio_frequency_high=0.5,  # music high
        ambient_sound_level=0.6,
        learning_active=0.4,  # learning from content
        creativity_mode=0.3,
    ),

    "gesture_voice_fusion": RichFeatures(
        cognitive_state=0.4,  # processing
        cognitive_load=0.7,
        attention_focus=0.8,
        human_interaction=0.9,
        vision_active=1.0,
        faces_detected=0.2,
        motion_detected=1.0,
        motion_intensity=0.6,  # active gesturing
        objects_detected=0.3,  # hands/arms
        audio_active=1.0,
        speech_detected=1.0,
        speech_clarity=0.8,
        audio_frequency_mid=0.7,
        proximity_human=0.7,
        user_engagement=0.9,
    ),

    # ========================================================================
    # EXTREME CONDITIONS (2 scenarios)
    # ========================================================================

    "sensor_overload": RichFeatures(
        cognitive_state=0.8,  # executing (filtering/prioritizing)
        cognitive_load=0.95,  # near maximum
        attention_focus=0.5,  # struggling to focus
        reasoning_depth=0.4,  # shallow, reactive
        # TOO MUCH INPUT
        vision_active=1.0,
        scene_complexity=0.95,  # extremely complex
        objects_detected=1.0,  # 10+ objects
        motion_detected=1.0,
        motion_intensity=0.9,  # rapid motion
        rf_scanner_active=1.0,
        rf_spectrum_density=0.95,  # crowded spectrum
        rf_2_4ghz_activity=0.95,
        rf_5ghz_activity=0.9,
        audio_active=1.0,
        ambient_sound_level=0.9,  # loud
        speech_detected=0.7,
        temperature=0.68,  # 27°C (warm)
        humidity=0.65,
        light_level=0.9,  # bright
        cpu_usage=0.9,
        memory_usage=0.85,
        thermal_state=0.6,  # getting hot
    ),

    "multiple_threats": RichFeatures(
        cognitive_state=0.8,  # executing
        cognitive_load=0.9,
        reasoning_depth=0.7,
        attention_focus=0.7,
        defensive_mode=1.0,  # maximum defensive
        threat_level=0.9,  # multiple threats
        anomaly_detected=0.8,
        rf_scanner_active=1.0,
        rf_unknown_signals=0.8,
        rf_jamming_detected=0.7,
        rf_spectrum_density=0.8,
        vision_active=1.0,
        scene_complexity=0.6,
        visual_novelty=0.7,  # unusual activity
        audio_active=1.0,
        ambient_sound_level=0.5,
        sensor_tampering=0.6,
        intrusion_attempts=0.7,
        network_activity=0.8,  # suspicious traffic
        cpu_usage=0.8,
        personality_mode=0.6,  # defensive
    ),

    # ========================================================================
    # TEMPORAL & CONTEXTUAL (2 scenarios)
    # ========================================================================

    "morning_initialization": RichFeatures(
        cognitive_state=0.4,  # processing
        cognitive_load=0.6,
        memory_access_depth=0.8,  # loading memories
        learning_active=0.3,  # reviewing yesterday
        time_of_day=0.29,  # 7 AM
        light_level=0.6,  # sunrise
        temperature=0.48,  # 19°C (cool morning)
        humidity=0.55,
        database_activity=0.7,  # loading state
        network_activity=0.5,  # checking updates
        external_api_active=0.4,
        rf_2_4ghz_activity=0.4,  # morning network usage
        proactivity=0.4,  # planning day
    ),

    "predictive_anticipation": RichFeatures(
        cognitive_state=0.4,  # processing
        reasoning_depth=0.7,  # predicting future
        cognitive_load=0.6,
        attention_focus=0.6,
        memory_access_depth=0.9,  # analyzing patterns
        learning_active=0.5,
        proactivity=0.9,  # maximum proactivity
        creativity_mode=0.5,
        database_activity=0.6,  # querying history
        vision_active=1.0,
        scene_complexity=0.4,
        audio_active=1.0,
        ambient_sound_level=0.3,
        time_of_day=0.54,  # 1 PM (predicting afternoon needs)
    ),
}

# Total: 20 additional scenarios
# Grand total: 40 scenarios (20 original + 20 additional)
