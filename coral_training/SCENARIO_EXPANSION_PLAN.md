# Scenario Expansion Plan: From 20 to 40 Training Examples

## Current Status

**Completed Scenarios (20):**
1. quiet_idle - Basic idle state
2. rf_environmental_mapping - RF spectrum environmental analysis
3. rf_unknown_analysis - Unknown signal investigation
4. friendly_conversation - Social interaction
5. creative_problem_solving - Deep creative reasoning
6. multi_sensor_fusion - Multiple sensor integration
7. deep_learning_session - Active learning mode
8. defensive_posture - Security/threat response
9. listening_attentive - Focused audio input
10. executing_task - Task execution mode
11. high_uncertainty_reasoning - Uncertain decision making
12. night_monitoring - Low-activity nighttime state
13. busy_daytime - High-activity daytime state
14. empathetic_interaction - Emotional engagement
15. analytical_mode - Logical analysis mode
16. novel_scene_exploration - Visual novelty processing
17. crowded_rf_spectrum - Dense RF environment
18. proactive_suggestion - Proactive user assistance
19. system_thermal_stress - High computational load
20. quiet_human_nearby - Passive human presence detection

## Gap Analysis

### Coverage Assessment
Current scenarios cover:
- ✓ Basic cognitive states (idle, listening, processing, speaking, reasoning)
- ✓ RF spectrum analysis (environmental, unknown, crowded)
- ✓ Human interaction modes (friendly, empathetic, analytical, proactive)
- ✓ Environmental conditions (day, night, thermal)
- ✓ Sensor fusion basics
- ✓ Security/defensive posture

### Missing Critical Scenarios

#### 1. **Error & Recovery States**
- Sensor failure/degradation
- Network connection loss/restoration
- Conflicting sensor data resolution
- System recovery from crash
- Memory corruption detection

#### 2. **Complex Cognitive States**
- Philosophical reflection (deep existential thought)
- Learning from failure/mistakes
- Metacognition (thinking about thinking)
- Ethical dilemma resolution
- Multi-hypothesis evaluation

#### 3. **Advanced Interaction Patterns**
- User frustration detection & mitigation
- Teaching/educational mode
- Debugging/troubleshooting assistance
- Collaborative problem solving
- Conflict mediation

#### 4. **Multi-Modal Integration**
- Voice synthesis while monitoring environment
- Vision + RF + audio simultaneous processing
- Real-time translation/interpretation
- Media content analysis
- Gesture recognition with audio

#### 5. **Extreme Conditions**
- Sensor overload (too much input)
- Resource exhaustion (memory/CPU near limits)
- Multiple simultaneous threats
- Cascading system failures
- Emergency shutdown preparation

#### 6. **Temporal & Contextual**
- Morning startup/initialization
- Evening wind-down preparation
- Context switching (task interruption)
- Long-term memory consolidation
- Prediction/anticipation mode

## Proposed 20 Additional Scenarios

### Error Handling & Recovery (4 scenarios)
21. **sensor_failure_compensation** - Vision sensor fails, compensating with RF + audio
22. **network_dropout_recovery** - Network disconnected, switching to offline mode
23. **conflicting_sensor_data** - Temperature/humidity sensors give conflicting readings
24. **post_crash_recovery** - System just recovered from crash, rebuilding state

### Advanced Cognitive (4 scenarios)
25. **philosophical_reflection** - Deep existential/philosophical reasoning
26. **learning_from_failure** - Analyzing past mistakes, updating knowledge
27. **metacognitive_analysis** - AI analyzing its own reasoning process
28. **ethical_dilemma** - Weighing competing ethical considerations

### Complex Interaction (4 scenarios)
29. **user_frustration_detected** - User showing signs of frustration, adapting response
30. **teaching_mode** - Explaining complex concepts step-by-step
31. **collaborative_debugging** - Working with user to troubleshoot problem
32. **multi_user_coordination** - Managing input from multiple users simultaneously

### Multi-Modal Fusion (4 scenarios)
33. **voice_synthesis_active** - Speaking while simultaneously monitoring sensors
34. **full_multimodal_reasoning** - Vision + RF + audio + environmental data integration
35. **media_content_analysis** - Analyzing video/audio content (movie, music, etc.)
36. **gesture_voice_fusion** - Processing hand gestures + speech simultaneously

### Extreme Conditions (2 scenarios)
37. **sensor_overload** - Too much sensory input, filtering/prioritizing
38. **multiple_threats** - Several security threats detected simultaneously

### Temporal & Contextual (2 scenarios)
39. **morning_initialization** - System startup, loading memories, planning day
40. **predictive_anticipation** - Anticipating user needs based on patterns

## Feature Distribution Analysis

### Ensuring Full 68-Feature Coverage

**Underutilized Features in Current 20:**
- `sensor_tampering` (only used in defensive scenarios)
- `intrusion_attempts` (only security scenarios)
- `visual_novelty` (only one scenario)
- `gpu_usage` (minimal coverage)
- `formality_level` (limited variation)
- `proactivity` (only one scenario)
- `memory_access_depth` (underutilized)

**New Scenarios Will Exercise:**
- Error/failure states (sensor tampering, anomaly detection)
- Complex multi-modal combinations (all sensors active)
- Extreme value ranges (overload, exhaustion)
- Temporal patterns (startup, shutdown, transitions)
- Learning features (learning_active, memory_access_depth)

## Implementation Plan

### Phase 1: Complete Current 20 Scenarios
- ✓ Monitor until completion (~90 minutes remaining)
- Verify dataset integrity (20 examples × 68 features × 10k particles)

### Phase 2: Update generate_dataset.py
- Add 20 new scenarios to SCENARIOS dictionary
- Update scenario count from 20 → 40
- Preserve existing 20 scenarios
- Test generation on 1-2 new scenarios first

### Phase 3: Generate Additional 20 Scenarios
- Resume generation from example 21/40
- Estimated time: ~4.5 hours (13 min/example average)
- Continue monitoring with /tmp/monitor_progress.sh

### Phase 4: Dataset Review & Model Training
- Verify 40 examples generated successfully
- Analyze feature distribution across all 40 scenarios
- Ensure no feature is consistently zero or one
- Proceed to TensorFlow Lite model training

## Performance Considerations

### Dataset Size
- Current: 20 examples
- Proposed: 40 examples
- Impact on training: +100% data = better generalization
- Estimated training time increase: +50% (not linear due to batching)

### Model Complexity
- 68 input features (unchanged)
- 30,000 output values (unchanged)
- Estimated model size: 3-5 MB (well under 8 MB Edge TPU cache limit)
- Expected Edge TPU mapping: 100% (single subgraph)

### Time Investment
- Current 20 scenarios: ~4.5 hours generation time
- Additional 20 scenarios: ~4.5 hours
- Total: ~9 hours for complete 40-scenario dataset
- **Worth it:** Significantly better model performance and robustness

## Decision Matrix

### Option A: Keep 20 Scenarios
**Pros:**
- Faster to train and deploy
- Covers basic functionality
- Good for MVP/prototype

**Cons:**
- Limited edge case coverage
- Weaker generalization
- Production-ready concerns
- Missing critical failure modes

### Option B: Expand to 40 Scenarios (RECOMMENDED)
**Pros:**
- Comprehensive edge case coverage
- Better generalization and robustness
- Production-ready quality
- Handles failure modes and recovery
- Full 68-feature utilization

**Cons:**
- Additional 4.5 hours generation time
- Slightly longer training time

## Recommendation

**EXPAND TO 40 SCENARIOS** for production-quality Coral TPU model.

The additional 4.5 hours of dataset generation is a worthwhile investment for:
1. Significantly better model robustness
2. Handling real-world edge cases
3. Full utilization of rich 68-feature architecture
4. Production-ready quality
5. Reduced need for retraining later

## Next Steps

1. **Wait for current 20 to complete** (~75 minutes remaining)
2. **Review generated dataset quality**
3. **Update generate_dataset.py with 20 new scenarios**
4. **Resume generation for examples 21-40**
5. **Proceed to model training with full 40-scenario dataset**
