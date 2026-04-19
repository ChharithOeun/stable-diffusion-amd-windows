@echo off
REM stable-diffusion-amd-windows — Quick Start
REM AMD GPU via DirectML on Windows

echo ============================================
echo  Stable Diffusion — AMD DirectML Windows
echo ============================================
echo.

REM Activate venv if present
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import torch_directml" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Installation failed. Check your Python and pip versions.
        pause
        exit /b 1
    )
)

REM Verify GPU
echo.
echo Verifying GPU...
python scripts\verify_gpu.py
if errorlevel 1 (
    echo.
    echo WARNING: GPU verification failed. Check driver version.
    echo Continuing anyway...
)

REM Default generation
echo.
echo Running sample generation...
python scripts\generate.py ^
    --prompt "a mountain landscape at sunset, photorealistic, 8k" ^
    --steps 25 ^
    --width 512 ^
    --height 512 ^
    --attention-slicing ^
    --output sample_output.png

if errorlevel 0 (
    echo.
    echo Done! Output saved to: outputs\sample_output.png
) else (
    echo.
    echo Generation failed. Check the error above.
)

pause
