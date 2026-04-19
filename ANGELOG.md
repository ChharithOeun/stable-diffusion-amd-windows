# Changelog

All notable changes will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Features

- Initial release: SD 1.5, SD 2.x, SDXL support via DirectML
- `generate.py` — txt2img, img2img, inpaint modes
- `benchmark.py` — performance benchmarking across resolutions
- `download_model.py` — HuggingFace model downloader with presets
- `verify_gpu.py` — DirectML device verification
- VRAM optimization flags: attention slicing, VAE tiling, CPU offload
- Scheduler selection: Euler, Euler A, DDIM, DPM++, PNDM, LMS
- JSON config file support
- Batch generation support
- SDXL refiner pipeline support
