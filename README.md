# FixKeynote

FixKeynote is a tool intended to help recover corrupted Apple Keynote (`.key`) files.
It works by extracting text, presenter notes, and images from the corrupted archive and
then using AppleScript to create a new presentation with the recovered data.

## How to Use FixKeynote

There are two main ways to use this tool: as a standalone macOS application or a command-line tool.

### 1. Using the macOS App (`FixKeynote.app`)

If you have the compiled Application bundle:

    Drop your corrupted `.key` files into a folder named `fix_keynote` on your Desktop (`~/Desktop/fix_keynote/`). Then, simply double-click on `FixKeynote.app`. The application will automatically detect all `.key` files in that folder, extract their data, and reconstruct them next to the original files.

### 2. Using the Command Line (CLI)

If you are running the script directly via Python or `uv`:

```bash
# Run on a specific file
uvx fix_keynote /path/to/corrupted_presentation.key

# Or process everything in ~/Desktop/fix_keynote/
uvx fix_keynote /path/to/corrupted_presentation.key
```

## How to Build the macOS App

To build a standalone macOS application bundle (`.app`) so you can easily move it or place it in your Applications folder, we use **PyInstaller**.

### Prerequisites

Make sure you have `uv` installed, then install the required build dependencies:
```bash
uv sync --group build
```

### Build Command

You can easily build the `FixKeynote.app` bundle and copy it to your Desktop using the included Makefile. Run the following command at the root of the project:
```bash
make build
```

### Output

Once the process is complete, your compiled application will be automatically copied to your Desktop (`~/Desktop/FixKeynote.app`).

You can clean the build artifacts later by running:
```bash
make clean
```
