# stable-diffusion-amd-windows

> **Stable Diffusion / SDXL on AMD GPUs via DirectML — no ROCm, no Linux, just Windows.**

[![CI](https://github.com/ChharithOeun/stable-diffusion-amd-windows/actions/workflows/ci.yml/badge.svg)](https://github.com/ChharithOeun/stable-diffusion-amd-windows/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AMD DirectML](https://img.shields.io/badge/AMD-DirectML-ED1C24.svg)](https://github.com/microsoft/DirectML)

Run Stable Diffusion 1.5, SD 2.x, and SDXL on your AMD GPU on Windows using **DirectML** — Microsoft's hardware-accelerated ML backend. Works on RX 6000, RX 7000, and most AMD integrated graphics. No ROCm required.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/chharith)

---

## Table of Contents

- [Why DirectML?](#why-directml)
- [Supported Hardware](#supported-hardware)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Benchmarks](#benchmarks)
- [VRAM Optimization](#vram-optimization)
- [Model Compatibility](#model-compatibility)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)

---

## Why DirectML?

AMD GPUs on Windows **cannot use ROCm** (ROCm is Linux-only). The alternatives are:

| Backend | Platform | AMD Support | Notes |
|---------|----------|-------------|-------|
| CUDA | Windows/Linux | ❌ NVIDIA only | — |
| ROCm | Linux only | ✅ | Not available on Windows |
| **DirectML** | **Windows** | **✅** | This repo |
| CPU | Any | ✅ | Very slow |

**DirectML** is Microsoft's DirectX 12-based ML backend. It works with any GPU that supports DirectX 12 — including AMD, Intel, and NVIDIA. For AMD users on Windows, it's the best path to GPU-accelerated Stable Diffusion.

---

## Supported Hardware

### Recommended (8GB+ VRAM)

| GPU | VRAM | SD 1.5 | SDXL | Notes |
|-----|------|--------|------|-------|
| RX 7900 XTX | 24GB | ✅ Fast | ✅ Fast | Best performance |
| RX 7900 XT | 20GB | ✅ Fast | ✅ Fast | Excellent |
| RX 7900 GRE | 16GB | ✅ Fast | ✅ Good | Great value |
| RX 7800 XT | 16GB | ✅ Fast | ✅ Good | Recommended |
| RX 6800 XT | 16GB | ✅ Fast | ✅ Good | Very capable |
| RX 6800 | 16GB | ✅ Fast | ✅ Good | — |
| RX 7700 XT | 12GB | ✅ Fast | ✅ Good | — |
| RX 6700 XT | 12GB | ✅ Fast | ✅ OK | — |
| RX 7600 | 8GB | ✅ Good | ⚠️ Tight | Use attention slicing |
| RX 6600 XT | 8GB | ✅ Good | ⚠️ Tight | Use attention slicing |

### Works (4–8GB VRAM)

| GPU | VRAM | SD 1.5 | SDXL | Notes |
|-----|------|--------|------|-------|
| RX 6600 | 8GB | ✅ | ⚠️ | Enable all optimizations |
| RX 580 | 8GB | ✅ | ❌ | SD 1.5 only |
| RX 570 | 4GB | ⚠️ | ❌ | Slow, low-res only |
| Vega 56/64 | 8GB | ✅ | ⚠️ | Older arch, slower |

### Integrated / APU

| GPU | VRAM | Notes |
|-----|------|-------|
| Radeon 780M (Ryzen 7040) | Shared | Works, uses system RAM |
| Radeon 680M (Ryzen 6000) | Shared | Works, slow |
| Radeon Vega (Ryzen 2000–4000) | Shared | Very slow, not recommended |

---

## Quick Start

```bat
git clone https://github.com/ChharithOeun/stable-diffusion-amd-windows.git
cd stable-diffusion-amd-windows
run.bat
```

Or manually:

```bash
pip install -r requirements.txt
python scripts/verify_gpu.py
python scripts/generate.py --prompt "a photo of an astronaut riding a horse" --output output.png
```

---

## Installation

### Prerequisites

- Windows 10 (21H2+) or Windows 11
- Python 3.10, 3.11, or 3.12
- AMD GPU with DirectX 12 support
- Latest AMD Adrenalin drivers (23.x or newer recommended)

### Step 1 — Clone the repo

```bat
git clone https://github.com/ChharithOeun/stable-diffusion-amd-windows.git
cd stable-diffusion-amd-windows
```

### Step 2 — Create a virtual environment (recommended)

```bat
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bat
pip install -r requirements.txt
```

This installs:
- `torch-directml` — PyTorch DirectML backend (AMD GPU support)
- `diffusers` — HuggingFace Stable Diffusion pipeline
- `transformers` — CLIP text encoder
- `accelerate` — pipeline utilities
- `safetensors` — fast model loading
- `Pillow`, `numpy`, `tqdm` — utilities

### Step 4 — Verify GPU detection

```bat
python scripts/verify_gpu.py
```

Expected output:

```
DirectML Device: AMD Radeon RX 7800 XT
DirectML available: True
Device: privateuseone:0
Test tensor: OK
GPU acceleration: READY
```

### Step 5 — Download a model

```bat
python scripts/download_model.py --model runwayml/stable-diffusion-v1-5
```

Or for SDXL:

```bat
python scripts/download_model.py --model stabilityai/stable-diffusion-xl-base-1.0
```

Models are saved to `~/.cache/huggingface/hub` by default.

---

## Usage

### Basic generation

```bat
python scripts/generate.py --prompt "a sunset over mountains, photorealistic, 8k"
```

### Common options

```
python scripts/generate.py [OPTIONS]

  --prompt TEXT           Generation prompt (required)
  --negative TEXT         Negative prompt [default: low quality, blurry]
  --model TEXT            Model ID or local path [default: runwayml/stable-diffusion-v1-5]
  --steps INT             Inference steps [default: 30]
  --guidance FLOAT        Guidance scale [default: 7.5]
  --width INT             Image width [default: 512]
  --height INT            Image height [default: 512]
  --seed INT              Random seed (-1 = random) [default: -1]
  --output PATH           Output file path [default: output.png]
  --scheduler TEXT        Scheduler: euler, ddim, dpm++ [default: euler]
  --batch INT             Number of images [default: 1]
  --attention-slicing     Enable attention slicing (saves VRAM)
  --vae-tiling            Enable VAE tiling (saves VRAM for hi-res)
  --sdxl                  Use SDXL pipeline
  --refiner               Run SDXL refiner pass (SDXL only)
```

### Examples

**SD 1.5 — portrait, 512×768:**
```bat
python scripts/generate.py ^
  --prompt "portrait of a knight in shining armor, dramatic lighting, oil painting" ^
  --negative "blurry, bad anatomy, ugly" ^
  --width 512 --height 768 --steps 30 --seed 42
```

**SDXL — landscape, 1024×1024:**
```bat
python scripts/generate.py ^
  --sdxl ^
  --prompt "a misty forest at dawn, golden hour, hyperrealistic" ^
  --width 1024 --height 1024 --steps 25 ^
  --attention-slicing
```

**SDXL with refiner:**
```bat
python scripts/generate.py ^
  --sdxl --refiner ^
  --prompt "cyberpunk city at night, neon reflections, ultra detailed" ^
  --width 1024 --height 1024 --steps 30
```

**Batch generation:**
```bat
python scripts/generate.py ^
  --prompt "a cat wearing a hat" ^
  --batch 4 --seed 100
```

### Config file

Copy and edit `config.example.json`:

```json
{
  "model": "runwayml/stable-diffusion-v1-5",
  "scheduler": "euler",
  "steps": 30,
  "guidance": 7.5,
  "width": 512,
  "height": 512,
  "attention_slicing": true,
  "output_dir": "outputs"
}
```

Then run with:
```bat
python scripts/generate.py --config config.json --prompt "your prompt here"
```

---

## Benchmarks

Tested with SD 1.5, 512×512, 30 steps, Euler scheduler, Windows 11.

| GPU | VRAM | Steps/sec | Time (30 steps) |
|-----|------|-----------|-----------------|
| RX 7900 XTX | 24GB | ~5.2 it/s | ~6s |
| RX 7800 XT | 16GB | ~4.1 it/s | ~7s |
| RX 6800 XT | 16GB | ~3.8 it/s | ~8s |
| RX 7600 | 8GB | ~2.9 it/s | ~10s |
| RX 6600 XT | 8GB | ~2.6 it/s | ~12s |
| RX 6600 | 8GB | ~2.3 it/s | ~13s |
| RX 580 | 8GB | ~1.4 it/s | ~21s |

Run your own benchmark:
```bat
python scripts/benchmark.py
```

---

## VRAM Optimization

### Attention Slicing (saves ~1–2GB VRAM)

```python
pipe.enable_attention_slicing()
```

Or via CLI:
```bat
python scripts/generate.py --prompt "..." --attention-slicing
```

### VAE Tiling (for high resolution, saves VRAM during decode)

```python
pipe.enable_vae_tiling()
```

Or via CLI:
```bat
python scripts/generate.py --prompt "..." --vae-tiling --width 768 --height 768
```

### Sequential CPU Offload (for very low VRAM, <4GB)

```python
pipe.enable_sequential_cpu_offload()
```

Note: This moves model weights to CPU between operations. Much slower but enables generation on low-VRAM systems.

### Recommended Settings by VRAM

| VRAM | SD 1.5 Max Res | SDXL | Recommended Flags |
|------|---------------|------|-------------------|
| 24GB | 1024×1024 | ✅ Full | None needed |
| 16GB | 768×768 | ✅ Full | None needed |
| 12GB | 768×768 | ✅ | `--attention-slicing` |
| 8GB | 512×512 | ⚠️ | `--attention-slicing --vae-tiling` |
| 4GB | 512×512 | ❌ | `--attention-slicing --vae-tiling` |

---

## Model Compatibility

### Supported model formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Safetensors | `.safetensors` | ✅ Recommended — fast, safe |
| PyTorch checkpoint | `.ckpt` | ✅ Works, slower to load |
| HuggingFace Hub | — | ✅ Auto-download |
| Diffusers format | directory | ✅ Default |

### Tested models

| Model | Type | Notes |
|-------|------|-------|
| `runwayml/stable-diffusion-v1-5` | SD 1.5 | Best compatibility |
| `stabilityai/stable-diffusion-2-1` | SD 2.1 | 768px native |
| `stabilityai/stable-diffusion-xl-base-1.0` | SDXL | 1024px native |
| `stabilityai/stable-diffusion-xl-refiner-1.0` | SDXL refiner | Used with base |
| `Lykon/dreamshaper-8` | SD 1.5 finetune | Community favorite |
| `stablediffusionapi/realistic-vision-v6.0-b1` | SD 1.5 finetune | Photorealism |

### Loading local `.safetensors` / `.ckpt` files

```bat
python scripts/generate.py ^
  --model "C:\Models\dreamshaper_8.safetensors" ^
  --prompt "..."
```

---

## Troubleshooting

### `No DirectML device found`

**Cause:** Drivers outdated or DirectX 12 not supported.

**Fix:**
1. Update AMD Adrenalin drivers from [amd.com/drivers](https://www.amd.com/en/support)
2. Check DX12 support: `dxdiag` → Display tab → look for "Feature Level: 12_0" or higher
3. Ensure `torch-directml` is installed: `pip show torch-directml`

---

### `Out of memory` / `D3D12 resource allocation failed`

**Cause:** Not enough VRAM.

**Fix:**
1. Add `--attention-slicing`
2. Add `--vae-tiling`
3. Reduce resolution (use 512×512 instead of 768×768)
4. Close other GPU-heavy applications
5. Restart Python to clear VRAM: DirectML doesn't always release memory cleanly

---

### `slow generation on first run`

**Cause:** Model weights being downloaded and compiled for DirectML on first use.

**Fix:** This is normal. Second run will be much faster. DirectML compiles shaders on first execution.

---

### `black / all-gray output images`

**Cause:** NSFW filter triggering, or VAE decode error on DirectML.

**Fix:**
```python
# Disable safety checker
pipe.safety_checker = None
pipe.feature_extractor = None
```

Or pass `--no-safety-checker` flag to the generate script.

---

### `AttributeError: 'NoneType' object has no attribute 'to'`

**Cause:** Model failed to load properly.

**Fix:** Delete model cache and re-download:
```bat
python scripts/download_model.py --model runwayml/stable-diffusion-v1-5 --force
```

---

### Generation is very slow (CPU fallback)

**Cause:** torch-directml not being used; falling back to CPU.

**Fix:** Verify device assignment:
```python
import torch_directml
dml = torch_directml.device()
print(dml)  # Should print: privateuseone:0
```

Make sure your pipeline is loaded with `.to(dml)`.

---

### `ImportError: cannot import name 'StableDiffusionXLPipeline'`

**Cause:** Old version of `diffusers`.

**Fix:** `pip install --upgrade diffusers`

---

## FAQ

**Q: Can I use LoRA weights with DirectML?**

A: Yes. Load LoRA with `pipe.load_lora_weights("path/to/lora.safetensors")`. Most LoRAs trained on SD 1.5 or SDXL work fine.

**Q: Does ControlNet work on DirectML?**

A: Yes, but it requires more VRAM. Use `--attention-slicing` for 8GB cards.

**Q: Can I use textual inversion / embeddings?**

A: Yes. Load with `pipe.load_textual_inversion("path/to/embedding.pt")`.

**Q: Why is DirectML slower than CUDA?**

A: DirectML has more overhead than CUDA's native PyTorch integration. Expect roughly 30–50% lower performance vs equivalent NVIDIA hardware. This is a known limitation of the DirectML path.

**Q: Can I use this with AUTOMATIC1111 or ComfyUI?**

A: AUTOMATIC1111 doesn't natively support DirectML well. For ComfyUI on AMD, see [comfyui-amd-windows-setup](https://github.com/ChharithOeun/comfyui-amd-windows-setup). This repo focuses on the raw diffusers pipeline.

**Q: Does img2img work?**

A: Yes. Use `--mode img2img --init-image input.png --strength 0.75`.

**Q: Does inpainting work?**

A: Yes. Use `--mode inpaint --init-image input.png --mask mask.png`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and pull requests welcome.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Related Repos

| Repo | Description |
|------|-------------|
| [comfyui-amd-windows-setup](https://github.com/ChharithOeun/comfyui-amd-windows-setup) | ComfyUI on AMD GPU Windows |
| [whisper-amd-windows](https://github.com/ChharithOeun/whisper-amd-windows) | Faster-Whisper on AMD GPU Windows |
| [torch-amd-setup](https://github.com/ChharithOeun/torch-amd-setup) | PyTorch DirectML environment setup |
| [directml-benchmark](https://github.com/ChharithOeun/directml-benchmark) | AMD DirectML GPU benchmarks |

---

*If this saved you hours of setup pain, consider buying me a coffee:*

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/chharith)
