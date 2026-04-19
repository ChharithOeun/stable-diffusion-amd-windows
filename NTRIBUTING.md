# Contributing

Contributions welcome! Bug reports, hardware testing results, and PRs all help.

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-fix`
3. Make your changes
4. Test on AMD hardware if possible
5. Submit a pull request

## What's most needed

- **Hardware test results** — benchmarks on GPUs not yet in the table
- **Bug fixes** — especially VRAM edge cases
- **Model compatibility** — tested with community models (CivitAI etc.)
- **Scheduler improvements** — new schedulers for better quality/speed

## Reporting bugs

Use the [Bug Report](https://github.com/ChharithOeun/stable-diffusion-amd-windows/issues/new?template=bug_report.md) template. Always include:

- GPU model and VRAM
- AMD driver version
- Python version
- Full error traceback
- Exact command that failed

## Code style

- Standard Python (PEP 8 loosely)
- Type hints where practical
- Docstrings on public functions
