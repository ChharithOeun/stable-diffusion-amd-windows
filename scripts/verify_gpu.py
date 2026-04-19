"""
verify_gpu.py — Check DirectML device availability for Stable Diffusion.
"""
import sys


def check_directml():
    print("=== DirectML GPU Verification ===\n")

    # Check torch_directml
    try:
        import torch_directml
        print(f"torch-directml version : {torch_directml.__version__}")
    except ImportError:
        print("ERROR: torch_directml not installed.")
        print("  Run: pip install torch-directml")
        return False

    # Device
    try:
        dml = torch_directml.device()
        print(f"DirectML device        : {dml}")
    except Exception as e:
        print(f"ERROR getting DirectML device: {e}")
        return False

    # Adapter name
    try:
        name = torch_directml.device_name(0)
        print(f"Adapter                : {name}")
    except Exception:
        print("Adapter                : (unknown)")

    # Tensor test
    try:
        import torch
        t = torch.randn(4, 4).to(dml)
        result = (t @ t).sum().item()
        print(f"Tensor matmul test     : OK (result={result:.4f})")
    except Exception as e:
        print(f"ERROR: Tensor test failed: {e}")
        return False

    # diffusers check
    try:
        import diffusers
        print(f"diffusers version      : {diffusers.__version__}")
    except ImportError:
        print("WARNING: diffusers not installed. Run: pip install diffusers")

    # transformers check
    try:
        import transformers
        print(f"transformers version   : {transformers.__version__}")
    except ImportError:
        print("WARNING: transformers not installed. Run: pip install transformers")

    print("\nStatus: GPU acceleration READY for Stable Diffusion")
    return True


if __name__ == "__main__":
    ok = check_directml()
    sys.exit(0 if ok else 1)
