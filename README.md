# Aasishi – ASCII Video & Image Studio

ascii is a desktop application built with Python that transforms webcam feeds, images, and video files into real-time ASCII art. It provides customizable character styles, colors, visual effects, and density controls through an interactive PyQt6 interface.it is personal and you have not to use ai and give your original photo/video .it is made to save user identity 

## Features

- **Live Webcam:** Convert webcam footage into ASCII art in real time.
- **Image Processing:** Open and transform images into ASCII artwork.
- **Video Processing:** Play video files with ASCII rendering.
- **Customizable Density:** Adjust character density from 40 to 300.
- **Multiple Character Sets:** Choose Binary, Standard, Detailed, or Blocks.
- **Color Presets:** Matrix Green, Cyberpunk Green, Retro Amber, Cyan, White, and Original Colors.
- **Visual Effects:**
  - None
  - Invert Colors
  - Neon Edge Detection (Canny)
  - Glitch Noise
- **Zoom Control:** Adjust the viewport from 0.2x to 5.0x.
- **Interactive Interface:** Collapsible sidebar and media viewport.
- **Media Controls:** Start and stop media feeds.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| PyQt6 | Desktop graphical interface |
| OpenCV | Image processing and video capture |
| NumPy | Image matrix operations |
| Pillow | ASCII character rendering and image drawing |

## Requirements

### Hardware

- Dual-core 2 GHz processor or better
- 4 GB RAM minimum (8 GB recommended)
- Webcam for live webcam functionality
- 1280 × 720 display recommended

### Software

- Windows 10/11, macOS, or Linux
- Python 3.9–3.12

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Tirthika/ASCII-ART.git
```

### 2. Open the project directory

```bash
cd ASCII-ART
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install PyQt6 opencv-python numpy Pillow
```

### 6. Run the application

```bash
python new.py
```

## How to Use

1. Launch the application.
2. Select a media source from the sidebar:
   - Live Webcam
   - Open Photo
   - Open Video
3. Adjust the ASCII density.
4. Select your preferred character set.
5. Choose a color preset.
6. Apply visual effects if desired.
7. Adjust the zoom level.
8. Use the Stop Feed option to stop the current media source.

## Supported Formats

**Images:**
- PNG
- JPG / JPEG
- BMP
- WEBP

**Videos:**
- MP4
- AVI
- MOV
- MKV

Video and audio playback compatibility may depend on the installed OpenCV and Qt multimedia backends.

## Project Structure

```text
ASCII-ART/
│
├── new.py
├── README.md
├── LICENSE
└── venv/
```

## Version Information

**Current Version:** 1.0.1

**Development Status:** Active development

The project is being improved with additional rendering capabilities, performance optimizations, and export features.

## Roadmap

Planned improvements include:

- Export ASCII artwork as PNG.
- Export rendered ASCII videos.
- Improve frame-processing performance.
- Add custom font selection.
- Improve audio-video synchronization.
- Improve stability at higher resolutions.
- Add custom character sets.
- Introduce additional visual effects and export formats.

## Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork this repository.
2. Create a new branch for your changes.
3. Implement your improvements.
4. Test your changes.
5. Submit a Pull Request.

For major changes, open an issue first to discuss your proposal.

## Bug Reports

If you encounter a bug or have a feature suggestion, please open an issue:

https://github.com/Tirthika/ASCII-ART/issues

## Source Code

Main application source:

https://github.com/Tirthika/ASCII-ART/blob/main/new.py

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Tirthika/ASCII-ART/blob/main/LICENSE) file for details.

## Author

Developed by [Tirthika](https://github.com/Tirthika).

---

**Aasishi – Turning ordinary media into ASCII art.**
