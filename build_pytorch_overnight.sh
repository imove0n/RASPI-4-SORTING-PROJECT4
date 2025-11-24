#!/bin/bash
# Build PyTorch from source - Run this overnight (6-12 hours)
# Usage: bash build_pytorch_overnight.sh

echo "=========================================="
echo "PyTorch Overnight Build Script"
echo "This will take 6-12 hours"
echo "=========================================="
echo ""

# Create build directory
cd ~
mkdir -p pytorch-build
cd pytorch-build

# Clone PyTorch
echo "[1/6] Cloning PyTorch repository..."
git clone --recursive --branch v2.0.0 https://github.com/pytorch/pytorch.git
cd pytorch

# Install build dependencies
echo "[2/6] Installing build dependencies..."
sudo apt-get install -y libopenblas-dev libblas-dev m4 cmake cython3 \
    python3-dev python3-yaml python3-setuptools python3-wheel \
    python3-numpy python3-cffi python3-future

# Install Python dependencies
echo "[3/6] Installing Python dependencies..."
pip3 install pyyaml typing_extensions --break-system-packages

# Set build options (CPU only, no CUDA)
echo "[4/6] Setting build configuration..."
export USE_CUDA=0
export USE_CUDNN=0
export USE_MKLDNN=0
export USE_DISTRIBUTED=0
export MAX_JOBS=2
export BUILD_TEST=0

# Build and install
echo "[5/6] Building PyTorch (this takes 6-12 hours)..."
echo "Started at: $(date)"
python3 setup.py install --user

# Test installation
echo "[6/6] Testing PyTorch installation..."
python3 -c "import torch; print('PyTorch version:', torch.__version__); print('SUCCESS!')"

echo ""
echo "=========================================="
echo "Build completed at: $(date)"
echo "=========================================="
echo ""
echo "Now install ultralytics:"
echo "pip3 install ultralytics --break-system-packages"
