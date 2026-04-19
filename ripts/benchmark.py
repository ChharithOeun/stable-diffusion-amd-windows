"""
benchmark.py — Benchmark Stable Diffusion performance on AMD DirectML.

Runs a quick generation test and reports steps/sec across resolutions.
"""
import sys
import time


BENCHMARK_CONFIGS = [
    {"name": "SD 1.5 — 512x512 (20 steps)", "width": 512, "height": 512, "steps": 20,
     "model": "runwayml/stable-diffusion-v1-5", "sdxl": False},
    {"name": "SD 1.5 — 768x512 (20 steps)", "width": 768, "height": 512, "steps": 20,
     "model": "runwayml/stable-diffusion-v1-5", "sdxl": False},
]

PROMPT = "benchmark test image, simple landscape"


def run_benchmark(config, device):
    import torch
    from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

    print(f"\n  Loading: {config['model']}")
    pipe = StableDiffusionPipeline.from_pretrained(
        config["model"],
        torch_dtype=torch.float16,
        safety_checker=None,
        feature_extractor=None,
    )
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to(device)
    pipe.enable_attention_slicing()

    gen = torch.Generator(device="cpu").manual_seed(42)

    # Warmup
    print("  Warmup run...")
    pipe(prompt=PROMPT, num_inference_steps=5, width=512, height=512, generator=gen)

    # Timed run
    print(f"  Timed run: {config['steps']} steps @ {config['width']}x{config['height']}")
    gen.manual_seed(42)
    t0 = time.time()
    pipe(
        prompt=PROMPT,
        num_inference_steps=config["steps"],
        width=config["width"],
        height=config["height"],
        generator=gen,
    )
    elapsed = time.time() - t0
    its = config["steps"] / elapsed

    del pipe
    return elapsed, its


def main():
    print("=== Stable Diffusion AMD DirectML Benchmark ===\n")

    try:
        import torch_directml
    except ImportError:
        print("ERROR: torch_directml not installed. Run: pip install torch-directml")
        sys.exit(1)

    device = torch_directml.device()
    try:
        adapter = torch_directml.device_name(0)
        print(f"Adapter : {adapter}")
    except Exception:
        adapter = "Unknown"

    print(f"Device  : {device}")
    print()

    results = []
    for cfg in BENCHMARK_CONFIGS:
        print(f"[{cfg['name']}]")
        try:
            elapsed, its = run_benchmark(cfg, device)
            results.append((cfg["name"], elapsed, its))
            print(f"  Result : {elapsed:.1f}s total | {its:.2f} it/s")
        except Exception as e:
            print(f"  FAILED : {e}")
            results.append((cfg["name"], None, None))

    print("\n=== Summary ===")
    print(f"{'Config':<40} {'Time':>8} {'it/s':>8}")
    print("-" * 60)
    for name, elapsed, its in results:
        if elapsed is not None:
            print(f"{name:<40} {elapsed:>7.1f}s {its:>7.2f}")
        else:
            print(f"{name:<40} {'FAILED':>8} {'—':>8}")

    print(f"\nAdapter: {adapter}")
    print("Benchmark complete.")


if __name__ == "__main__":
    main()
