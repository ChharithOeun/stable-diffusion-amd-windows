"""
generate.py — Stable Diffusion image generation via AMD DirectML on Windows.

Usage:
    python scripts/generate.py --prompt "a sunset over mountains"
    python scripts/generate.py --sdxl --prompt "cyberpunk city" --width 1024 --height 1024
    python scripts/generate.py --help
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="Stable Diffusion on AMD GPU via DirectML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--prompt", required=True, help="Generation prompt")
    p.add_argument("--negative", default="low quality, blurry, bad anatomy, ugly, watermark",
                   help="Negative prompt")
    p.add_argument("--model", default="runwayml/stable-diffusion-v1-5",
                   help="Model ID (HuggingFace Hub) or local path")
    p.add_argument("--steps", type=int, default=30, help="Inference steps")
    p.add_argument("--guidance", type=float, default=7.5, help="Guidance scale (CFG)")
    p.add_argument("--width", type=int, default=512, help="Image width")
    p.add_argument("--height", type=int, default=512, help="Image height")
    p.add_argument("--seed", type=int, default=-1, help="Random seed (-1 = random)")
    p.add_argument("--output", default="output.png", help="Output file path")
    p.add_argument("--output-dir", default="outputs", help="Output directory")
    p.add_argument("--scheduler", default="euler",
                   choices=["euler", "euler_a", "ddim", "dpm++", "pndm", "lms"],
                   help="Noise scheduler")
    p.add_argument("--batch", type=int, default=1, help="Number of images to generate")
    p.add_argument("--attention-slicing", action="store_true",
                   help="Enable attention slicing (reduces VRAM usage)")
    p.add_argument("--vae-tiling", action="store_true",
                   help="Enable VAE tiling (reduces VRAM for hi-res)")
    p.add_argument("--cpu-offload", action="store_true",
                   help="Enable sequential CPU offload (very low VRAM)")
    p.add_argument("--sdxl", action="store_true", help="Use SDXL pipeline")
    p.add_argument("--refiner", action="store_true",
                   help="Run SDXL refiner (requires --sdxl)")
    p.add_argument("--no-safety-checker", action="store_true",
                   help="Disable NSFW safety checker")
    p.add_argument("--config", default=None, help="Load settings from JSON config file")
    p.add_argument("--mode", default="txt2img",
                   choices=["txt2img", "img2img", "inpaint"],
                   help="Generation mode")
    p.add_argument("--init-image", default=None, help="Input image (img2img / inpaint)")
    p.add_argument("--mask", default=None, help="Mask image (inpaint mode)")
    p.add_argument("--strength", type=float, default=0.75,
                   help="Denoising strength for img2img (0.0–1.0)")
    return p


def load_config(args, config_path):
    """Merge JSON config with CLI args (CLI takes precedence)."""
    with open(config_path) as f:
        cfg = json.load(f)
    for key, val in cfg.items():
        attr = key.replace("-", "_")
        if hasattr(args, attr) and getattr(args, attr) is None:
            setattr(args, attr, val)
    return args


def get_scheduler(name, config):
    """Return scheduler instance by name."""
    from diffusers import (
        EulerDiscreteScheduler,
        EulerAncestralDiscreteScheduler,
        DDIMScheduler,
        DPMSolverMultistepScheduler,
        PNDMScheduler,
        LMSDiscreteScheduler,
    )
    schedulers = {
        "euler": EulerDiscreteScheduler,
        "euler_a": EulerAncestralDiscreteScheduler,
        "ddim": DDIMScheduler,
        "dpm++": DPMSolverMultistepScheduler,
        "pndm": PNDMScheduler,
        "lms": LMSDiscreteScheduler,
    }
    cls = schedulers.get(name, EulerDiscreteScheduler)
    return cls.from_config(config)


def load_pipeline(args, device):
    """Load the appropriate diffusers pipeline."""
    from diffusers import (
        StableDiffusionPipeline,
        StableDiffusionXLPipeline,
        StableDiffusionImg2ImgPipeline,
        StableDiffusionInpaintPipeline,
    )
    import torch

    dtype = torch.float16
    model_path = args.model

    print(f"Loading model: {model_path}")
    print(f"Mode: {args.mode} | SDXL: {args.sdxl}")

    if args.sdxl:
        pipe = StableDiffusionXLPipeline.from_pretrained(
            model_path,
            torch_dtype=dtype,
            use_safetensors=True,
            variant="fp16",
        )
    elif args.mode == "img2img":
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_path,
            torch_dtype=dtype,
        )
    elif args.mode == "inpaint":
        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            model_path,
            torch_dtype=dtype,
        )
    else:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=dtype,
        )

    # Safety checker
    if args.no_safety_checker and hasattr(pipe, "safety_checker"):
        pipe.safety_checker = None
        pipe.feature_extractor = None

    # Scheduler
    pipe.scheduler = get_scheduler(args.scheduler, pipe.scheduler.config)

    # VRAM optimizations
    if args.cpu_offload:
        print("Enabling sequential CPU offload...")
        pipe.enable_sequential_cpu_offload()
    else:
        pipe = pipe.to(device)

    if args.attention_slicing:
        print("Enabling attention slicing...")
        pipe.enable_attention_slicing()

    if args.vae_tiling:
        print("Enabling VAE tiling...")
        pipe.enable_vae_tiling()

    return pipe


def generate(args, pipe, device, seed):
    """Run generation and return images."""
    import torch
    from PIL import Image

    generator = torch.Generator(device="cpu")
    if seed >= 0:
        generator.manual_seed(seed)
    else:
        generator.seed()

    actual_seed = generator.initial_seed()
    print(f"Seed: {actual_seed}")

    kwargs = dict(
        prompt=args.prompt,
        negative_prompt=args.negative,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        num_images_per_prompt=args.batch,
        generator=generator,
    )

    if args.mode == "txt2img" and not args.sdxl:
        kwargs["width"] = args.width
        kwargs["height"] = args.height
    elif args.sdxl:
        kwargs["width"] = args.width
        kwargs["height"] = args.height

    if args.mode == "img2img":
        init_img = Image.open(args.init_image).convert("RGB")
        init_img = init_img.resize((args.width, args.height))
        kwargs["image"] = init_img
        kwargs["strength"] = args.strength
        del kwargs["guidance_scale"]
        kwargs["guidance_scale"] = args.guidance

    if args.mode == "inpaint":
        init_img = Image.open(args.init_image).convert("RGB")
        mask_img = Image.open(args.mask).convert("RGB")
        init_img = init_img.resize((args.width, args.height))
        mask_img = mask_img.resize((args.width, args.height))
        kwargs["image"] = init_img
        kwargs["mask_image"] = mask_img
        kwargs["strength"] = args.strength

    t0 = time.time()
    result = pipe(**kwargs)
    elapsed = time.time() - t0

    its = args.steps / elapsed
    print(f"Generated in {elapsed:.1f}s ({its:.2f} it/s)")

    return result.images, actual_seed


def main():
    parser = parse_args()
    args = parser.parse_args()

    # Load config file if specified
    if args.config:
        args = load_config(args, args.config)

    # Imports
    try:
        import torch_directml
    except ImportError:
        print("ERROR: torch_directml not installed.")
        print("  Run: pip install torch-directml")
        sys.exit(1)

    # Device
    device = torch_directml.device()
    print(f"Using device: {device}")
    try:
        adapter = torch_directml.device_name(0)
        print(f"Adapter: {adapter}")
    except Exception:
        pass

    # Output directory
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load pipeline
    pipe = load_pipeline(args, device)

    # Generate
    print(f"\nGenerating: {args.prompt[:80]}...")
    images, seed = generate(args, pipe, device, args.seed)

    # Save
    for i, img in enumerate(images):
        if len(images) == 1:
            out_path = out_dir / args.output
        else:
            stem = Path(args.output).stem
            ext = Path(args.output).suffix
            out_path = out_dir / f"{stem}_{i:03d}{ext}"
        img.save(out_path)
        print(f"Saved: {out_path}")

    print(f"\nDone. {len(images)} image(s) generated.")


if __name__ == "__main__":
    main()
