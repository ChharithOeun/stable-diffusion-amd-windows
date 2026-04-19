"""
download_model.py — Download and cache Stable Diffusion models from HuggingFace Hub.

Usage:
    python scripts/download_model.py --model runwayml/stable-diffusion-v1-5
    python scripts/download_model.py --model stabilityai/stable-diffusion-xl-base-1.0
    python scripts/download_model.py --model runwayml/stable-diffusion-v1-5 --force
"""
import argparse
import sys


PRESET_MODELS = {
    "sd15": "runwayml/stable-diffusion-v1-5",
    "sd21": "stabilityai/stable-diffusion-2-1",
    "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
    "sdxl-refiner": "stabilityai/stable-diffusion-xl-refiner-1.0",
    "dreamshaper": "Lykon/dreamshaper-8",
    "realistic-vision": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
}


def parse_args():
    p = argparse.ArgumentParser(description="Download SD models for DirectML use")
    p.add_argument("--model", required=False, default="runwayml/stable-diffusion-v1-5",
                   help="HuggingFace model ID or preset name")
    p.add_argument("--force", action="store_true",
                   help="Re-download even if cached")
    p.add_argument("--list", action="store_true",
                   help="List available preset models")
    p.add_argument("--fp16", action="store_true", default=True,
                   help="Download fp16 variant (smaller, recommended)")
    return p.parse_args()


def main():
    args = parse_args()

    if args.list:
        print("Available preset models:")
        for alias, model_id in PRESET_MODELS.items():
            print(f"  {alias:<20} -> {model_id}")
        return

    # Resolve preset
    model_id = PRESET_MODELS.get(args.model, args.model)
    print(f"Downloading: {model_id}")

    try:
        from diffusers import DiffusionPipeline
        import torch
    except ImportError:
        print("ERROR: diffusers not installed. Run: pip install diffusers transformers")
        sys.exit(1)

    kwargs = {
        "torch_dtype": torch.float16,
        "use_safetensors": True,
    }

    if args.force:
        kwargs["force_download"] = True

    # Try fp16 variant first, fall back to default
    try:
        print("Attempting fp16 variant...")
        kwargs["variant"] = "fp16"
        pipe = DiffusionPipeline.from_pretrained(model_id, **kwargs)
    except Exception:
        print("fp16 not available, downloading default...")
        kwargs.pop("variant", None)
        pipe = DiffusionPipeline.from_pretrained(model_id, **kwargs)

    print(f"\nModel downloaded successfully: {model_id}")
    print("Cache location: ~/.cache/huggingface/hub")
    print("\nTo generate:")
    print(f'  python scripts/generate.py --model "{model_id}" --prompt "your prompt"')

    del pipe


if __name__ == "__main__":
    main()
