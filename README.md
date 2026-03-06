# FixKeynote

FixKeynote is a tool intended to help recover corrupted Apple Keynote (`.key`) files.
It works by extracting text, presenter notes, and images from the corrupted archive and
then using AppleScript to create a new presentation with the recovered data.

## How to Use FixKeynote

There are two main ways to use this tool: as a standalone macOS application or a command-line tool.

### 1. Using the macOS App (`FixKeynote.app`)

If you have the compiled Application bundle:

*   **Batch processing (Default behavior):**
    Drop your corrupted `.key` files into a folder named `fix_keynote` on your Desktop (`~/Desktop/fix_keynote/`). Then, simply double-click on `FixKeynote.app`. The application will automatically detect all `.key` files in that folder, extract their data, and reconstruct them next to the original files.
*   **Targeting specific files via Terminal:**
    You can process a specific corrupted Keynote file by dragging the executable inside the App into a terminal, followed by the file itself:
    1. Open `Terminal`.
    2. Right-click `FixKeynote.app` > **Show Package Contents**.
    3. Navigate to `Contents/MacOS/` and drag the `FixKeynote` binary into the terminal.
    4. Drag and drop your corrupted `.key` file into the terminal (make sure there is a space before the file path).
    5. Press `Enter`.

### 2. Using the Command Line (CLI)

If you are running the script directly via Python or `uv`:

```bash
# Run on a specific file
uv run python src/fix_keynote/cli.py /path/to/corrupted_presentation.key

# Or process everything in ~/Desktop/fix_keynote/
uv run python src/fix_keynote/cli.py
```

## How to Build the macOS App

To build a standalone macOS application bundle (`.app`) so you can easily move it or place it in your Applications folder, we use **PyInstaller**.

### Prerequisites
Make sure you have `uv` installed, then install the required dependencies:
```bash
uv pip install pyinstaller
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
