# Pic2Pix
A script to process pictures/drawings of people to turn them into sprites usable in 2d game engines like GameMaker

## Table of Contents
- [Examples](#examples)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)

## Examples

### Photo to Sprite Conversion
A basic demo of what you can expect this script to do: Please note that the script expects the part to be extracted to be in the middle of the image. It samples the edges to determine the range of pixels to be filtered out, so if the edge corners are covered by the parts to be extracted, you'll have issues.

| Input | Output |
|-------|--------|
| ![Capture](https://github.com/user-attachments/assets/f42106d4-6e55-43ad-862d-7c9b2c042f8d) | ![Sprited](https://github.com/user-attachments/assets/d283df28-e98f-4853-8a27-423b38e56d84) |

The background doesnt have to be a perfect green screen. so long as it is distinct from the target, and is somewhat uniformly colored, it will be filtered out. The target shouldnt be similar in color to the background; if it is, you'll see parts of the target parts filtered out

Try turning yourself into a sprite!

The default color palette in the code is fantasy24 on Lospec

### Pencil Drawing Processing
For pencil drawings and doodles, anything with just a single color, rename your image so it has "pencil" in the name

| Input | Output |
|-------|--------|
| ![pencil](https://github.com/user-attachments/assets/753184c0-213a-484b-8861-07df3b8e1393) | ![transparency_test1](https://github.com/user-attachments/assets/a2960f1f-469b-41dd-bac9-1d35b7fd29fc) |

Yes, I have the artistic ability of a drunk walrus. Hopefully, you're much better.

### Animation Processing

| Input | Output |
|-------|--------|
| <img src="https://github.com/user-attachments/assets/905ed294-1a87-406e-88a8-d329a1781305" width="300"> | <img src="https://github.com/user-attachments/assets/7fdc947f-f968-43aa-ae2f-0b85fa891124" width="300"> |

## Installation

### 1. Install uv
First, install the `uv` package manager:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or visit [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for more options.

### 2. Install the tool
Clone this repository and install the tool:

```bash
git clone https://github.com/BobDev94/Pic2Pix.git
cd Pic2Pix
uv tool install --from . pic2pix
```

## Usage

The tool provides several commands for different image processing tasks:

```bash
# Process a single image file
pic2pix file image.png

# Process all images in a folder with an optional custom tolerance
pic2pix folder ./frames --tolerance 32

# Split a spritesheet into individual sprites
pic2pix spritesheet sheet.png --rows 4 --columns 6

# Create animated GIF from images in a folder
pic2pix gif ./frames --fps 12
pic2pix gif ./frames --duration 80
```

### Options
- `--tolerance 0-255`: Transparency tolerance for background removal (default: 40)
- `--fps 0.1-240`: Frames per second for GIF creation (default: 12)
- `--duration 1-20000`: Frame duration in milliseconds for GIF creation

## Testing

Run the test suite to verify everything is working correctly:

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with verbose output
uv run pytest -v
```
