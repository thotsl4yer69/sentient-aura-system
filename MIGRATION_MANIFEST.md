# Sentient Cortana - Migration Manifest

**Date:** 2025-10-26
**Purpose:** Complete file list for migration to new system

---

## 🔥 ESSENTIAL FILES - Copy These to New System

### Core Intelligence Modules (NEW - Required)

```
/home/mz1312/Sentient-Core-v4/sentient_aura/intelligence/__init__.py
/home/mz1312/Sentient-Core-v4/sentient_aura/intelligence/cross_modal_attention.py
/home/mz1312/Sentient-Core-v4/sentient_aura/intelligence/hybrid_emotion_model.py
/home/mz1312/Sentient-Core-v4/sentient_aura/intelligence/hierarchical_memory.py
/home/mz1312/Sentient-Core-v4/sentient_aura/intelligence/sentient_cortana.py
```

### Visualization Modules (NEW - Required)

```
/home/mz1312/Sentient-Core-v4/sentient_aura/visualization/__init__.py
/home/mz1312/Sentient-Core-v4/sentient_aura/visualization/morphing_controller.py
```

### Coral TPU Integration (Required)

```
/home/mz1312/Sentient-Core-v4/coral_pixel_engine.py
/home/mz1312/Sentient-Core-v4/coral_training_notebook.ipynb
```

### Essential Documentation (Required)

```
/home/mz1312/Sentient-Core-v4/SENTIENT_CORTANA_COMPLETE.md
/home/mz1312/Sentient-Core-v4/IMPLEMENTATION_SUMMARY.md
/home/mz1312/Sentient-Core-v4/QUICK_START_SENTIENT_CORTANA.md
/home/mz1312/Sentient-Core-v4/RESEARCH_VALIDATED_ARCHITECTURE.md
/home/mz1312/Sentient-Core-v4/FINAL_CORAL_TRAINING_PLAN.md
/home/mz1312/Sentient-Core-v4/CORTANA_VISUALIZATION_SPEC.md
/home/mz1312/Sentient-Core-v4/MULTI_ACCELERATOR_ARCHITECTURE.md
/home/mz1312/Sentient-Core-v4/README.md
```

---

## 📋 EXISTING PROJECT FILES - Keep These

### Main System Files

```
/home/mz1312/Sentient-Core-v4/launch_system.sh
/home/mz1312/Sentient-Core-v4/requirements.txt
/home/mz1312/Sentient-Core-v4/setup.py
```

### Sentient Aura Core Modules

```
/home/mz1312/Sentient-Core-v4/sentient_aura/__init__.py
/home/mz1312/Sentient-Core-v4/sentient_aura/core/
/home/mz1312/Sentient-Core-v4/sentient_aura/daemons/
/home/mz1312/Sentient-Core-v4/sentient_aura/visualization/particle_system.py
/home/mz1312/Sentient-Core-v4/sentient_aura/hardware/
/home/mz1312/Sentient-Core-v4/sentient_aura/utils/
```

### Configuration Files

```
/home/mz1312/Sentient-Core-v4/config/
/home/mz1312/Sentient-Core-v4/.env
```

### Web Interface (if applicable)

```
/home/mz1312/Sentient-Core-v4/web/
/home/mz1312/Sentient-Core-v4/static/
/home/mz1312/Sentient-Core-v4/templates/
```

---

## 📊 REFERENCE DOCUMENTATION - Optional but Recommended

```
/home/mz1312/Sentient-Core-v4/MANIFEST_NEW_FILES.md
/home/mz1312/Sentient-Core-v4/REVIEW_PACKAGE.md
/home/mz1312/Sentient-Core-v4/MIGRATION_MANIFEST.md
/home/mz1312/Sentient-Core-v4/HARDWARE_REQUIREMENTS.md
/home/mz1312/Sentient-Core-v4/HOW_TO_USE.md
/home/mz1312/Sentient-Core-v4/QUICKSTART.md
```

---

## 🗑️ DO NOT COPY - Archived/Superseded

```
/home/mz1312/Sentient-Core-v4/docs/archive_2025-10-26/
```

These are old files kept for reference only. They are superseded by the new implementation.

---

## 📦 Directory Structure for New System

```
Sentient-Core-v4/
│
├── sentient_aura/
│   ├── __init__.py
│   ├── intelligence/                    ✅ NEW
│   │   ├── __init__.py
│   │   ├── cross_modal_attention.py
│   │   ├── hybrid_emotion_model.py
│   │   ├── hierarchical_memory.py
│   │   └── sentient_cortana.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── morphing_controller.py      ✅ NEW
│   │   └── particle_system.py          (existing)
│   ├── core/                            (existing modules)
│   ├── daemons/                         (existing modules)
│   ├── hardware/                        (existing modules)
│   └── utils/                           (existing modules)
│
├── coral_pixel_engine.py               ✅ Required
├── coral_training_notebook.ipynb       ✅ Required
│
├── launch_system.sh
├── requirements.txt
├── setup.py
├── README.md
│
├── config/
├── web/
├── static/
├── templates/
│
└── [Documentation files]
```

---

## 🚀 Migration Steps

### Step 1: Create Directory Structure

```bash
# On new system
mkdir -p Sentient-Core-v4/sentient_aura/intelligence
mkdir -p Sentient-Core-v4/sentient_aura/visualization
mkdir -p Sentient-Core-v4/sentient_aura/core
mkdir -p Sentient-Core-v4/sentient_aura/daemons
mkdir -p Sentient-Core-v4/sentient_aura/hardware
mkdir -p Sentient-Core-v4/sentient_aura/utils
mkdir -p Sentient-Core-v4/config
```

### Step 2: Copy Core Intelligence Files (NEW)

```bash
# From this manifest - PRIORITY 1
scp /home/mz1312/Sentient-Core-v4/sentient_aura/intelligence/*.py new-system:~/Sentient-Core-v4/sentient_aura/intelligence/
scp /home/mz1312/Sentient-Core-v4/sentient_aura/visualization/morphing_controller.py new-system:~/Sentient-Core-v4/sentient_aura/visualization/
scp /home/mz1312/Sentient-Core-v4/sentient_aura/visualization/__init__.py new-system:~/Sentient-Core-v4/sentient_aura/visualization/
```

### Step 3: Copy Coral TPU Files

```bash
scp /home/mz1312/Sentient-Core-v4/coral_pixel_engine.py new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/coral_training_notebook.ipynb new-system:~/Sentient-Core-v4/
```

### Step 4: Copy Documentation

```bash
scp /home/mz1312/Sentient-Core-v4/SENTIENT_CORTANA_COMPLETE.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/IMPLEMENTATION_SUMMARY.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/QUICK_START_SENTIENT_CORTANA.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/RESEARCH_VALIDATED_ARCHITECTURE.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/FINAL_CORAL_TRAINING_PLAN.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/CORTANA_VISUALIZATION_SPEC.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/MULTI_ACCELERATOR_ARCHITECTURE.md new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/README.md new-system:~/Sentient-Core-v4/
```

### Step 5: Copy Existing System Files

```bash
# Copy existing sentient_aura modules
scp -r /home/mz1312/Sentient-Core-v4/sentient_aura/core new-system:~/Sentient-Core-v4/sentient_aura/
scp -r /home/mz1312/Sentient-Core-v4/sentient_aura/daemons new-system:~/Sentient-Core-v4/sentient_aura/
scp -r /home/mz1312/Sentient-Core-v4/sentient_aura/hardware new-system:~/Sentient-Core-v4/sentient_aura/
scp -r /home/mz1312/Sentient-Core-v4/sentient_aura/utils new-system:~/Sentient-Core-v4/sentient_aura/

# Copy system files
scp /home/mz1312/Sentient-Core-v4/launch_system.sh new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/requirements.txt new-system:~/Sentient-Core-v4/
scp /home/mz1312/Sentient-Core-v4/setup.py new-system:~/Sentient-Core-v4/

# Copy config
scp -r /home/mz1312/Sentient-Core-v4/config new-system:~/Sentient-Core-v4/
```

### Step 6: On New System

```bash
# Install dependencies
cd ~/Sentient-Core-v4
pip install -r requirements.txt

# Set Python path
export PYTHONPATH=/path/to/Sentient-Core-v4:$PYTHONPATH

# Test installation
python3 sentient_aura/intelligence/sentient_cortana.py
```

---

## ✅ Verification Checklist

After migration, verify these files exist:

### Critical Files (Must Have)
- [ ] `sentient_aura/intelligence/sentient_cortana.py`
- [ ] `sentient_aura/intelligence/hybrid_emotion_model.py`
- [ ] `sentient_aura/intelligence/hierarchical_memory.py`
- [ ] `sentient_aura/intelligence/cross_modal_attention.py`
- [ ] `sentient_aura/visualization/morphing_controller.py`
- [ ] `coral_pixel_engine.py`
- [ ] `SENTIENT_CORTANA_COMPLETE.md`

### Test After Migration
```bash
export PYTHONPATH=/path/to/Sentient-Core-v4
python3 sentient_aura/intelligence/sentient_cortana.py
```

Expected output: "SENTIENT CORTANA INTELLIGENCE SYSTEM" test with passing results

---

## 📝 Notes

1. **Do NOT copy `docs/archive_2025-10-26/`** - These are superseded files
2. **Update paths** - Adjust PYTHONPATH for new system location
3. **Dependencies** - Run `pip install -r requirements.txt` on new system
4. **Coral TPU** - If migrating to system without Coral, set `use_coral_tpu=False`
5. **Config files** - Review and update config files for new system paths

---

**Total Files to Copy:** ~25 essential files + existing project structure
**Total Size:** ~150 KB (new modules) + existing project files
**Migration Time:** ~5-10 minutes

---

*Ready for migration to new system!*
