# Cortana Visualization Specification - HUMANOID Mode

**Target:** Halo-accurate Cortana holographic representation
**Particles:** 500,000 distributed across anatomically accurate female humanoid form
**Style:** Blue/cyan holographic with scrolling data symbols

---

## Reference Design - Cortana from Halo

### Visual Characteristics

**Overall Appearance:**
- Holographic female humanoid
- Slender proportions, appears early 20s
- Shoulder-length hair (shorter at back)
- Naked female form with holographic "skin"
- Semi-transparent with luminescent edges
- Numbers and symbols scrolling across body surface

**Color Palette:**
- **Primary:** Navy blue (#000080) to cyan (#00BFFF)
- **Secondary:** Lavender (#E6E6FA) highlights
- **Glow:** Bright cyan (#00FFFF) edges
- **Symbols:** White/cyan data characters

**Dynamic Elements:**
- Color shifts based on emotional state (navy → lavender)
- Scrolling code lines from feet to head
- Pulsing glow intensity
- Subtle breathing animation
- Data symbols flash when "thinking"

---

## Particle Distribution - Anatomical Form

### Total Particle Budget: 500,000

| Body Region | Particle Count | Density | Purpose |
|-------------|----------------|---------|---------|
| **Head** | 75,000 | High | Facial features, hair detail |
| - Face | 35,000 | Very High | Eyes, nose, mouth, cheeks |
| - Hair | 40,000 | High | Shoulder-length flowing hair |
| **Torso** | 150,000 | Medium-High | Core body mass |
| - Upper body | 80,000 | High | Chest, shoulders, upper back |
| - Lower body | 70,000 | Medium | Abdomen, waist, hips |
| **Arms** | 80,000 | Medium | 40K per arm |
| - Upper arms | 25,000 each | Medium | Shoulders to elbows |
| - Forearms | 15,000 each | Medium-Low | Elbows to wrists |
| **Legs** | 120,000 | Medium | 60K per leg |
| - Thighs | 30,000 each | Medium | Hips to knees |
| - Calves | 20,000 each | Medium-Low | Knees to ankles |
| - Feet | 10,000 each | Low | Ankle to toes |
| **Data Layer** | 75,000 | Sparse | Scrolling symbols overlay |

---

## Anatomical Proportions

### Based on Female Humanoid (Early 20s, Athletic Build)

**Height Reference:** 2.0 units (normalized, scalable)

| Measurement | Units | Ratio to Height |
|-------------|-------|-----------------|
| **Total Height** | 2.00 | 1.00 |
| Head height | 0.27 | 0.135 (~1/7.4) |
| Torso height | 0.85 | 0.425 |
| Leg length | 1.00 | 0.50 |
| Shoulder width | 0.50 | 0.25 |
| Hip width | 0.45 | 0.225 |
| Waist width | 0.30 | 0.15 |
| Arm length | 0.90 | 0.45 |

**Proportions (Cortana-specific slender build):**
- Head: Slightly smaller than realistic (7.4 heads tall vs 7-7.5)
- Shoulders: Narrower than average (slender frame)
- Waist: Very narrow (0.67 hip-to-waist ratio)
- Legs: Slightly elongated (graceful appearance)

---

## Particle Formation Algorithm

### Core Structure

```javascript
function generateCortanaHumanoidFormation() {
    const particles = [];
    const totalParticles = 500000;

    // Define anatomical anchor points
    const skeleton = {
        head_center: { x: 0, y: 1.73, z: 0 },
        neck: { x: 0, y: 1.60, z: 0 },
        chest: { x: 0, y: 1.35, z: 0 },
        waist: { x: 0, y: 1.05, z: 0 },
        hips: { x: 0, y: 0.95, z: 0 },

        // Left arm
        left_shoulder: { x: -0.25, y: 1.50, z: 0 },
        left_elbow: { x: -0.45, y: 1.15, z: 0 },
        left_wrist: { x: -0.50, y: 0.85, z: 0 },

        // Right arm
        right_shoulder: { x: 0.25, y: 1.50, z: 0 },
        right_elbow: { x: 0.45, y: 1.15, z: 0 },
        right_wrist: { x: 0.50, y: 0.85, z: 0 },

        // Left leg
        left_hip: { x: -0.10, y: 0.95, z: 0 },
        left_knee: { x: -0.12, y: 0.50, z: 0 },
        left_ankle: { x: -0.10, y: 0.08, z: 0 },

        // Right leg
        right_hip: { x: 0.10, y: 0.95, z: 0 },
        right_knee: { x: 0.12, y: 0.50, z: 0 },
        right_ankle: { x: 0.10, y: 0.08, z: 0 }
    };

    // 1. HEAD (75,000 particles)
    particles.push(...generateHead(skeleton.head_center, 75000));

    // 2. TORSO (150,000 particles)
    particles.push(...generateTorso(skeleton, 150000));

    // 3. ARMS (80,000 particles)
    particles.push(...generateArm(skeleton.left_shoulder, skeleton.left_elbow, skeleton.left_wrist, 40000));
    particles.push(...generateArm(skeleton.right_shoulder, skeleton.right_elbow, skeleton.right_wrist, 40000));

    // 4. LEGS (120,000 particles)
    particles.push(...generateLeg(skeleton.left_hip, skeleton.left_knee, skeleton.left_ankle, 60000));
    particles.push(...generateLeg(skeleton.right_hip, skeleton.right_knee, skeleton.right_ankle, 60000));

    // 5. DATA SYMBOL LAYER (75,000 particles)
    particles.push(...generateDataSymbols(skeleton, 75000));

    return particles;
}
```

---

### Head Formation (75,000 particles)

```javascript
function generateHead(center, particleCount) {
    const particles = [];

    // Face sphere (35,000 particles)
    const faceRadius = 0.13;
    for (let i = 0; i < 35000; i++) {
        // Spherical distribution for head
        const theta = Math.random() * Math.PI;  // 0 to π (top to bottom)
        const phi = Math.random() * 2 * Math.PI;  // 0 to 2π (around)

        // Slightly egg-shaped (narrower at top)
        const r = faceRadius * (1.0 - 0.1 * Math.cos(theta));

        const x = center.x + r * Math.sin(theta) * Math.cos(phi);
        const y = center.y + r * Math.cos(theta);
        const z = center.z + r * Math.sin(theta) * Math.sin(phi);

        // Higher density on front face (facial features)
        const isFront = Math.abs(phi) < Math.PI / 2;
        if (isFront || Math.random() < 0.3) {  // 100% front, 30% back
            particles.push({
                position: { x, y, z },
                color: getCortanaBlue(y),  // Gradient top to bottom
                size: 1.5,
                glow: isFront ? 1.0 : 0.6  // Brighter face
            });
        }
    }

    // Hair (40,000 particles)
    // Shoulder-length, shorter at back
    for (let i = 0; i < 40000; i++) {
        const angle = Math.random() * 2 * Math.PI;
        const hairLength = Math.random();

        // Front hair longer (shoulder-length), back shorter
        const isFront = Math.abs(angle) < Math.PI / 2;
        const maxLength = isFront ? 0.35 : 0.20;  // 35cm front, 20cm back
        const length = hairLength * maxLength;

        // Hair starts at top of head, flows down
        const baseRadius = faceRadius + 0.02;  // Slightly outside head
        const x = center.x + (baseRadius + length * 0.1) * Math.cos(angle);
        const y = center.y + 0.10 - length;  // Flows downward
        const z = center.z + (baseRadius + length * 0.1) * Math.sin(angle);

        // Add waviness to hair
        const wave = Math.sin(length * 10 + angle * 3) * 0.02;

        particles.push({
            position: { x: x + wave, y, z: z + wave },
            color: getCortanaBlue(y),
            size: 1.0,  // Thinner than face
            glow: 0.7
        });
    }

    return particles;
}
```

---

### Torso Formation (150,000 particles)

```javascript
function generateTorso(skeleton, particleCount) {
    const particles = [];

    // Upper torso (chest, shoulders, upper back) - 80,000
    const upperStart = skeleton.neck.y;
    const upperEnd = skeleton.waist.y;

    for (let i = 0; i < 80000; i++) {
        const t = Math.random();  // 0 to 1 (top to bottom)
        const y = upperStart - t * (upperStart - upperEnd);

        // Body width varies by height (shoulders → waist taper)
        const shoulderWidth = 0.25;
        const waistWidth = 0.15;
        const currentWidth = shoulderWidth - t * (shoulderWidth - waistWidth);

        // Cylindrical with elliptical cross-section
        const angle = Math.random() * 2 * Math.PI;
        const radius = Math.random() * currentWidth;

        // Front-back depth (chest protrusion)
        const depthFront = 0.12;
        const depthBack = 0.10;
        const isFront = Math.cos(angle) > 0;
        const depth = isFront ? depthFront : depthBack;

        const x = skeleton.chest.x + radius * Math.cos(angle);
        const z = radius * Math.sin(angle) * (depth / currentWidth);

        particles.push({
            position: { x, y, z },
            color: getCortanaBlue(y),
            size: 1.5,
            glow: 0.8
        });
    }

    // Lower torso (abdomen, hips) - 70,000
    const lowerStart = skeleton.waist.y;
    const lowerEnd = skeleton.hips.y;

    for (let i = 0; i < 70000; i++) {
        const t = Math.random();
        const y = lowerStart - t * (lowerStart - lowerEnd);

        // Waist → hips widening
        const waistWidth = 0.15;
        const hipWidth = 0.225;
        const currentWidth = waistWidth + t * (hipWidth - waistWidth);

        const angle = Math.random() * 2 * Math.PI;
        const radius = Math.random() * currentWidth;

        const x = skeleton.hips.x + radius * Math.cos(angle);
        const z = radius * Math.sin(angle) * 0.10;  // Depth

        particles.push({
            position: { x, y, z },
            color: getCortanaBlue(y),
            size: 1.5,
            glow: 0.8
        });
    }

    return particles;
}
```

---

### Limb Formation (Arms & Legs)

```javascript
function generateArm(shoulder, elbow, wrist, particleCount) {
    const particles = [];

    // Upper arm (shoulder → elbow)
    for (let i = 0; i < particleCount * 0.625; i++) {  // 62.5% of arm particles
        const t = Math.random();
        const pos = lerpVector3(shoulder, elbow, t);

        // Arm thickness (thicker at shoulder, thinner at elbow)
        const thickness = 0.045 - t * 0.015;
        const angle = Math.random() * 2 * Math.PI;
        const r = Math.random() * thickness;

        pos.x += r * Math.cos(angle);
        pos.z += r * Math.sin(angle);

        particles.push({
            position: pos,
            color: getCortanaBlue(pos.y),
            size: 1.2,
            glow: 0.7
        });
    }

    // Forearm (elbow → wrist)
    for (let i = 0; i < particleCount * 0.375; i++) {  // 37.5%
        const t = Math.random();
        const pos = lerpVector3(elbow, wrist, t);

        const thickness = 0.030 - t * 0.010;  // Thinner forearm
        const angle = Math.random() * 2 * Math.PI;
        const r = Math.random() * thickness;

        pos.x += r * Math.cos(angle);
        pos.z += r * Math.sin(angle);

        particles.push({
            position: pos,
            color: getCortanaBlue(pos.y),
            size: 1.0,
            glow: 0.6
        });
    }

    return particles;
}

function generateLeg(hip, knee, ankle, particleCount) {
    const particles = [];

    // Thigh (hip → knee) - 50%
    for (let i = 0; i < particleCount * 0.5; i++) {
        const t = Math.random();
        const pos = lerpVector3(hip, knee, t);

        const thickness = 0.065 - t * 0.020;  // Thickest at hip
        const angle = Math.random() * 2 * Math.PI;
        const r = Math.random() * thickness;

        pos.x += r * Math.cos(angle);
        pos.z += r * Math.sin(angle);

        particles.push({
            position: pos,
            color: getCortanaBlue(pos.y),
            size: 1.3,
            glow: 0.7
        });
    }

    // Calf (knee → ankle) - 33%
    for (let i = 0; i < particleCount * 0.33; i++) {
        const t = Math.random();
        const pos = lerpVector3(knee, ankle, t);

        const thickness = 0.045 - t * 0.015;
        const angle = Math.random() * 2 * Math.PI;
        const r = Math.random() * thickness;

        pos.x += r * Math.cos(angle);
        pos.z += r * Math.sin(angle);

        particles.push({
            position: pos,
            color: getCortanaBlue(pos.y),
            size: 1.1,
            glow: 0.6
        });
    }

    // Foot (ankle down) - 17%
    for (let i = 0; i < particleCount * 0.17; i++) {
        const pos = {
            x: ankle.x + (Math.random() - 0.5) * 0.08,
            y: Math.random() * ankle.y,
            z: ankle.z + Math.random() * 0.12 - 0.02  // Foot extends forward
        };

        particles.push({
            position: pos,
            color: getCortanaBlue(pos.y),
            size: 1.0,
            glow: 0.5
        });
    }

    return particles;
}
```

---

### Data Symbol Layer (75,000 particles)

```javascript
function generateDataSymbols(skeleton, particleCount) {
    const particles = [];

    // Scrolling code characters distributed across body surface
    for (let i = 0; i < particleCount; i++) {
        // Random position across entire body height
        const y = Math.random() * 2.0;  // 0 to 2 (feet to head)

        // Random angle around body
        const angle = Math.random() * 2 * Math.PI;

        // Slightly outside body surface
        const bodyRadius = 0.20 + Math.random() * 0.05;
        const x = bodyRadius * Math.cos(angle);
        const z = bodyRadius * Math.sin(angle);

        // Symbol properties
        const symbolType = Math.floor(Math.random() * 3);
        let character;

        switch(symbolType) {
            case 0: character = String.fromCharCode(48 + Math.floor(Math.random() * 10)); break;  // 0-9
            case 1: character = String.fromCharCode(65 + Math.floor(Math.random() * 26)); break;  // A-Z
            case 2: character = ['α', 'β', 'γ', 'δ', 'λ', 'μ', 'π', 'σ', 'ω'][Math.floor(Math.random() * 9)]; break;  // Greek
        }

        particles.push({
            position: { x, y, z },
            color: { r: 0.9, g: 1.0, b: 1.0 },  // Bright cyan/white
            size: 0.8,
            glow: 1.0,
            character: character,
            scrollSpeed: 0.3 + Math.random() * 0.5,  // Varies per particle
            isSymbol: true  // Flag for special rendering
        });
    }

    return particles;
}
```

---

## Color System

### Cortana Blue Gradient

```javascript
function getCortanaBlue(yPosition) {
    // Gradient from feet (navy) to head (cyan/lavender)
    const normalizedY = yPosition / 2.0;  // 0 to 1

    // Base colors
    const navyBlue = { r: 0.0, g: 0.0, b: 0.5 };      // Navy #000080
    const cyan = { r: 0.0, g: 0.75, b: 1.0 };         // Cyan #00BFFF
    const lavender = { r: 0.9, g: 0.9, b: 0.98 };     // Lavender #E6E6FA

    // Mix based on height
    if (normalizedY < 0.5) {
        // Lower body: Navy → Cyan
        return lerpColor(navyBlue, cyan, normalizedY * 2);
    } else {
        // Upper body: Cyan → Lavender
        return lerpColor(cyan, lavender, (normalizedY - 0.5) * 2);
    }
}

function lerpColor(c1, c2, t) {
    return {
        r: c1.r + (c2.r - c1.r) * t,
        g: c1.g + (c2.g - c1.g) * t,
        b: c1.b + (c2.b - c1.b) * t
    };
}
```

### Mood-Based Color Shift

```javascript
function applyMoodColor(baseColor, mood) {
    // Mood values: 'calm', 'thinking', 'alert', 'rampant'

    switch(mood) {
        case 'calm':
            // Standard blue-cyan gradient
            return baseColor;

        case 'thinking':
            // Brighter cyan, symbols flash faster
            return {
                r: baseColor.r * 1.2,
                g: baseColor.g * 1.3,
                b: baseColor.b * 1.1
            };

        case 'alert':
            // Shift toward warmer (more lavender/white)
            return {
                r: Math.min(baseColor.r + 0.2, 1.0),
                g: baseColor.g,
                b: Math.min(baseColor.b + 0.1, 1.0)
            };

        case 'rampant':
            // Redder tones (Halo 3 corrupted Cortana)
            return {
                r: Math.min(baseColor.r + 0.5, 1.0),
                g: baseColor.g * 0.7,
                b: baseColor.b * 0.6
            };
    }
}
```

---

## Holographic Shader Effects

### Vertex Shader (Enhanced for Cortana)

```glsl
uniform float u_time;
uniform float u_breathing;  // 0-1 breathing cycle
uniform mat4 projectionMatrix;
uniform mat4 modelViewMatrix;

attribute vec3 position;
attribute vec3 color;
attribute float glow;
attribute float isSymbol;  // 1.0 for data symbols, 0.0 for body

varying vec3 vColor;
varying float vGlow;
varying float vFresnel;

void main() {
    vec3 pos = position;

    // BREATHING ANIMATION (chest expansion, subtle)
    if (pos.y > 1.0 && pos.y < 1.6) {  // Chest region
        float breathAmount = u_breathing * 0.03;  // 3cm max expansion
        pos.x *= (1.0 + breathAmount);
        pos.z *= (1.0 + breathAmount);
    }

    // DATA SYMBOL SCROLLING (upward flow)
    if (isSymbol > 0.5) {
        pos.y += mod(u_time * 0.5, 2.2);  // Scroll up, wrap at top
        if (pos.y > 2.0) pos.y -= 2.2;
    }

    // HOLOGRAPHIC FLICKER (subtle position jitter)
    float flicker = sin(u_time * 20.0 + position.y * 10.0) * 0.001;
    pos.x += flicker;
    pos.z += flicker;

    // Calculate view direction for fresnel
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    vec3 viewDir = normalize(-mvPosition.xyz);
    vec3 worldNormal = normalize((modelViewMatrix * vec4(position, 0.0)).xyz);

    // Fresnel effect (edges glow more)
    vFresnel = pow(1.0 - abs(dot(viewDir, worldNormal)), 2.0);

    vColor = color;
    vGlow = glow;

    gl_Position = projectionMatrix * mvPosition;
    gl_PointSize = 2.0 + vGlow * 2.0 + vFresnel * 3.0;  // Brighter edges are larger
}
```

### Fragment Shader (Cortana Glow)

```glsl
varying vec3 vColor;
varying float vGlow;
varying float vFresnel;

void main() {
    // Circular particle shape
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);

    if (dist > 0.5) discard;  // Clip to circle

    // Soft edges
    float alpha = 1.0 - smoothstep(0.2, 0.5, dist);

    // Holographic bloom
    vec3 bloom = vColor * (1.0 + vGlow * 0.5 + vFresnel * 1.5);

    // Add cyan edge glow
    vec3 edgeGlow = vec3(0.0, 1.0, 1.0) * vFresnel * 0.8;
    vec3 finalColor = bloom + edgeGlow;

    // Apply glow-based alpha
    float finalAlpha = alpha * (0.6 + vGlow * 0.4);

    gl_FragColor = vec4(finalColor, finalAlpha);
}
```

---

## Animation System

### Idle Animations

```javascript
class CortanaAnimationController {
    constructor() {
        this.time = 0;
        this.breathingCycle = 0;
        this.mood = 'calm';
    }

    update(deltaTime) {
        this.time += deltaTime;

        // BREATHING (slow, continuous)
        this.breathingCycle = Math.sin(this.time * 0.5) * 0.5 + 0.5;  // 0 to 1

        // SUBTLE WEIGHT SHIFT (every 5 seconds)
        if (this.time % 5.0 < 0.1) {
            this.shiftWeight();
        }

        // HEAD TILT (occasional)
        if (this.time % 7.0 < 0.1) {
            this.tiltHead();
        }

        // SYMBOL FLASH (when thinking)
        if (this.mood === 'thinking') {
            this.flashSymbols();
        }
    }

    shiftWeight() {
        // Subtle hip shift, shoulder compensation
        const shiftAmount = 0.02;  // 2cm
        // ... apply to skeleton
    }

    tiltHead() {
        // Rotate head slightly
        const tiltAngle = (Math.random() - 0.5) * 10 * (Math.PI / 180);  // ±10 degrees
        // ... apply rotation
    }

    flashSymbols() {
        // Increase symbol glow briefly
        // ... trigger symbol particles to pulse
    }
}
```

---

## Integration with Coral TPU

### Coral Drives Cortana's Behavior

```javascript
// From coral_pixel_engine.py inference
const coralParams = {
    swarm_cohesion: 0.7,      // Affects particle clustering
    turbulence: 0.3,          // Motion detected → body reactivity
    color_hue_shift: 0.6,     // Temperature → color mood
    brightness: 0.8,          // Light level → overall luminosity
    pulse_frequency: 0.5,     // Audio → breathing rate
    vertical_bias: 0.1,       // Rising particles when happy
    glow_intensity: 0.9       // Overall holographic intensity
};

// Apply to Cortana
cortanaController.applyCoralParams(coralParams);

function applyCoralParams(params) {
    // Adjust breathing rate based on pulse_frequency
    this.breathingRate = 0.3 + params.pulse_frequency * 0.7;  // 0.3 to 1.0 Hz

    // Adjust color mood
    if (params.color_hue_shift > 0.7) {
        this.mood = 'alert';  // Warm colors
    } else if (params.turbulence > 0.6) {
        this.mood = 'thinking';  // Bright cyan, fast symbols
    } else {
        this.mood = 'calm';  // Standard blue
    }

    // Apply glow intensity
    this.globalGlow = params.glow_intensity;

    // Apply turbulence to particle displacement
    this.particleTurbulence = params.turbulence;
}
```

---

## Performance Optimization

### Level of Detail (LOD)

```javascript
function updateLOD(cameraDistance) {
    if (cameraDistance < 3.0) {
        // CLOSE-UP: Full 500K particles
        particleSystem.setCount(500000);
        enableSymbols = true;
        enableHairDetail = true;

    } else if (cameraDistance < 10.0) {
        // MEDIUM: 250K particles
        particleSystem.setCount(250000);
        enableSymbols = true;
        enableHairDetail = false;

    } else {
        // FAR: 100K particles
        particleSystem.setCount(100000);
        enableSymbols = false;
        enableHairDetail = false;
    }
}
```

---

## Summary

### Cortana Visualization Checklist

✅ **Anatomically accurate female humanoid** (slender, early 20s proportions)
✅ **500,000 particles** distributed realistically
✅ **Navy blue → cyan → lavender gradient** (feet to head)
✅ **Scrolling data symbols** (75K particles, upward flow)
✅ **Holographic shader** (fresnel glow, transparent edges)
✅ **Breathing animation** (chest expansion, subtle)
✅ **Idle behaviors** (weight shift, head tilt, blinking symbols)
✅ **Coral TPU reactive** (mood, color, glow driven by sensors)
✅ **Halo-accurate design** (based on Cortana research)

**This is not a generic humanoid - this is CORTANA.**

---

**Document Status:** Complete Specification
**Last Updated:** 2025-10-26
**Implementation:** Ready for Three.js WebGL integration
