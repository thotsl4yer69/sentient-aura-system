# Compiling Models for Coral Edge TPU using Google Colab

## ARM64 Limitation

The Edge TPU compiler is **NOT available on ARM64 systems** (Raspberry Pi) as of version 2.1. Google has essentially abandoned the Coral project with no updates since 2021.

This guide shows how to compile your TensorFlow Lite model for Edge TPU using Google Colab (free, web-based).

## Prerequisites

1. Trained TensorFlow Lite model (.tflite file) from `train_model.py`
2. Google account for Colab access
3. SCP/SFTP access to transfer files

## Step 1: Prepare Your Model

On Raspberry Pi, after training completes:

```bash
cd ~/Sentient-Core-v4/coral_training/models
ls -lh latest.tflite  # Verify model exists
```

## Step 2: Open Google Colab

1. Go to https://colab.research.google.com/
2. Create new notebook: **File → New notebook**
3. Change runtime to GPU (optional but faster): **Runtime → Change runtime type → GPU**

## Step 3: Install Edge TPU Compiler

In the first Colab cell:

```python
# Install Edge TPU Compiler
!curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
!echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
!sudo apt-get update
!sudo apt-get install -y edgetpu-compiler
```

Run the cell (Shift+Enter). This installs the compiler on Colab's x86_64 Linux system.

## Step 4: Upload Your Model

In the second cell:

```python
from google.colab import files
import os

# Upload your .tflite file
print("Upload your TensorFlow Lite model (.tflite file)")
uploaded = files.upload()

# Get the filename
model_name = list(uploaded.keys())[0]
print(f"Uploaded: {model_name}")
```

Run the cell and select your `latest.tflite` file when prompted.

## Step 5: Compile for Edge TPU

In the third cell:

```python
# Compile for Edge TPU with best practices
# Use --min_runtime_version to ensure compatibility with Raspberry Pi runtime
!edgetpu_compiler {model_name} --min_runtime_version 13

# List output files
!ls -lh *.tflite

# Check compilation log for detailed operation mapping
!cat *.log
```

This creates a file named `<model_name>_edgetpu.tflite`.

The compiler will show statistics like:
- Edge TPU Compiler version
- Input/output tensors
- Number of operations mapped to Edge TPU
- **Target: 100% Edge TPU operations for best performance**

## Step 6: Download Compiled Model

In the fourth cell:

```python
# Download the compiled Edge TPU model
import glob

edgetpu_models = glob.glob("*_edgetpu.tflite")
for model in edgetpu_models:
    print(f"Downloading: {model}")
    files.download(model)
```

## Step 7: Transfer to Raspberry Pi

On your local machine (or use WinSCP/FileZilla):

```bash
# Replace with your Pi's IP address
scp *_edgetpu.tflite mz1312@<raspberry-pi-ip>:~/Sentient-Core-v4/coral_training/models/
```

Or on Raspberry Pi directly:

```bash
cd ~/Sentient-Core-v4/coral_training/models
# Move downloaded file from ~/Downloads/ or wherever you saved it
```

## Step 8: Verify Model Compatibility

**CRITICAL**: Check the compiler output for Edge TPU compatibility.

Example of **GOOD** compilation (100% Edge TPU):
```
Edge TPU Compiler version 16.0.384591198
Input model: visualization_model.tflite
Input size: 124.56KB
Output model: visualization_model_edgetpu.tflite
Output size: 125.32KB
On-chip memory used for caching model parameters: 124.00KB
On-chip memory remaining for caching model parameters: 7.75MB
Off-chip memory used for streaming uncached model parameters: 0.00B
Number of Edge TPU subgraphs: 1
Total number of operations: 8
Operation log: visualization_model_edgetpu.log

Model compiled successfully in 847 ms.
```

Example of **BAD** compilation (partial CPU execution):
```
WARNING: Operator not supported by Edge TPU: RESHAPE
Number of Edge TPU subgraphs: 2  ← BAD: Multiple subgraphs means CPU fallback
...
Operations mapped to Edge TPU: 6
Operations run on CPU: 2  ← BAD: Causes 10x+ slowdown
```

If you see CPU operations:
1. Review the operation log file
2. Check model architecture against [supported operations](https://gweb-coral-full.uc.r.appspot.com/docs/edgetpu/models-intro/#supported-operations)
3. Modify model architecture to use only supported operations

## Step 9: Install Edge TPU Runtime on Raspberry Pi

Back on Raspberry Pi:

```bash
# Install Edge TPU runtime libraries (NOT the compiler)
sudo apt-get install -y python3-pycoral libedgetpu1-std

# Verify installation
python3 -c "from pycoral.utils import edgetpu; print(edgetpu.list_edge_tpus())"
```

This should list available Edge TPU devices (USB or PCIe).

## Alternative: Automated Colab Notebook

Create a single-cell Colab notebook with this complete script:

```python
# Complete Edge TPU Compilation Workflow
import os
from google.colab import files
import glob

# 1. Install compiler
print("Installing Edge TPU Compiler...")
!curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - > /dev/null 2>&1
!echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list > /dev/null 2>&1
!sudo apt-get update > /dev/null 2>&1
!sudo apt-get install -y edgetpu-compiler > /dev/null 2>&1
print("✓ Compiler installed")

# 2. Upload model
print("\n📤 Upload your .tflite model:")
uploaded = files.upload()
model_name = list(uploaded.keys())[0]
print(f"✓ Uploaded: {model_name}")

# 3. Compile
print(f"\n🔧 Compiling {model_name} for Edge TPU...")
!edgetpu_compiler {model_name}

# 4. Check results
edgetpu_models = glob.glob("*_edgetpu.tflite")
if edgetpu_models:
    print(f"\n✓ Compilation complete: {edgetpu_models[0]}")
    print("\n📊 Model Statistics:")
    !ls -lh *.tflite

    # 5. Download
    print(f"\n📥 Downloading compiled model...")
    for model in edgetpu_models:
        files.download(model)
    print("✓ Done! Transfer to Raspberry Pi.")
else:
    print("❌ Compilation failed - check output above")
```

Save this notebook for future use.

## Troubleshooting

**"edgetpu_compiler: command not found"**
- Colab session might have reset. Re-run installation cell.

**"Model has unsupported operations"**
- Review train_model.py architecture
- Only use [supported operations](https://gweb-coral-full.uc.r.appspot.com/docs/edgetpu/models-intro/#supported-operations)
- Our Dense/FullyConnected layers ARE supported

**"Multiple Edge TPU subgraphs detected"**
- Model contains unsupported operations causing CPU fallback
- This causes 10x+ performance degradation
- Must redesign model architecture

**"Edge TPU not found" on Raspberry Pi**
- Ensure Coral USB/PCIe accelerator is connected
- Check `lsusb` for USB devices or `lspci` for PCIe
- Install runtime: `sudo apt-get install python3-pycoral libedgetpu1-std`

## Edge TPU Best Practices

### Model Size & Caching

- **Edge TPU SRAM**: ~8 MB for parameter caching
- **Per-layer caching**: Layers either fully fit in cache OR load from external memory (no partial caching)
- **Target model size**: <6 MB for single-segment optimal performance
- **Segmentation formula**: If model >6 MB: `num_segments = [Model size in MB] / 6` (round up)

### Optimization Tips

1. **Keep layers small**: Design architecture so individual layers fit in 8 MB cache
2. **INT8 quantization**: Required for Edge TPU (our train_model.py does this)
3. **Single subgraph**: Target 100% Edge TPU mapping (1 subgraph)
4. **Fully Connected layers**: Dense/FullyConnected operations are well-supported
5. **Avoid unsupported ops**: Check [operation compatibility](https://gweb-coral-full.uc.r.appspot.com/docs/edgetpu/models-intro/#supported-operations)

### Compiler Flags

```bash
edgetpu_compiler model.tflite \
  --min_runtime_version 13  # Ensure Pi compatibility
  --out_dir ./              # Output directory
  --show_operations         # Verbose operation mapping (optional)
```

### Expected Model Statistics

**Our Model (estimated)**:
- Input: 68 features (float32) → INT8 quantized
- Output: 30,000 values (10,000 particles × 3D coordinates)
- Estimated size: ~3-5 MB (well under 8 MB cache limit)
- Expected: Single Edge TPU subgraph, 100% mapping

## Performance Expectations

- **100% Edge TPU**: 60+ FPS for real-time particle generation
- **Partial CPU fallback**: <10 FPS (unusable for real-time visualization)
- **CPU only**: <1 FPS (completely unusable)

**Target: 100% Edge TPU compatibility with <5 MB model size**

## Next Steps

After successful compilation:
1. Transfer `*_edgetpu.tflite` to Raspberry Pi
2. Test inference: `python3 coral_training/test_inference.py`
3. Deploy to daemon: `python3 coral_daemon.py`
4. Monitor performance and FPS

## References

- [Coral Edge TPU Models](https://gweb-coral-full.uc.r.appspot.com/docs/edgetpu/models-intro/)
- [Edge TPU Compiler](https://gweb-coral-full.uc.r.appspot.com/docs/edgetpu/compiler/)
- [PyCoral API](https://gweb-coral-full.uc.r.appspot.com/docs/reference/py/)
