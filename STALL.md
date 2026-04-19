# Installation Guide

## Requirements

- Windows 10 (21H2 or newer) or Windows 11
- Python 3.10, 3.11, or 3.12
- AMD GPU with DirectX 12 support (most RX 400 series and newer)
- AMD Adrenalin drivers 23.x or newer
- ~10GB disk space for SD 1.5 model, ~14GB for SDXL

## Step-by-Step

### 1. Install Python

Download from [python.org](https://www.python.org/downloads/). During install:
- Check **"Add Python to PATH"**
- Check **"Install pip"**

Verify:
```bat
python --version
pip --version
```

### 2. Clone this repo

```bat
git clone https://github.com/ChharithOeun/stable-diffusion-amd-windows.git
cd stable-diffusion-amd-windows
```

### 3. Create virtual environment (recommended)

```bat
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies

```bat
pip install -r requirements.txt
```

This takes 5–10 minutes on first install (downloading PyTorch + dependencies).

### 5. Verify GPU

```bat
python scripts\verify_gpu.py
```

You should see `GPU acceleration: READY`.

### 6. Download a model

```bat
python scripts\download_model.py --model runwayml/stable-diffusion-v1-5
```

First download is ~5GB and may take 10–30 minutes depending on your connection.

### 7. Generate your first image

```bat
python scripts\generate.py --prompt "a beautiful sunset over the ocean"
```

Output saved to `outputs/output.png`.

---

## Updating

```bat
git pull
pip install -r requirements.txt --upgrade
```

## Uninstalling

Delete the repo folder. Model cache is stored separately at:
- `C:\Users\<you>\.cache\huggingface\hub`

Delete that folder to remove downloaded models.
