import zipfile
import xml.etree.ElementTree as ET
import shutil
import subprocess
import sys
import os
from pathlib import Path
from PyPDF2 import PdfReader


def show_popup(message, is_error=False):
    """Helper to display a native macOS popup (useful when running as App)"""
    title = "FixKeynote Error" if is_error else "FixKeynote"
    # Ensure double quotes are escaped for AppleScript
    safe_msg = message.replace('"', '\\"')
    apple_script = f'display alert "{title}" message "{safe_msg}"'
    subprocess.run(["osascript", "-e", apple_script])
    print(message)


def main():
    # --- Configuration ---
    # Arguments: a .key file or none (processes all .key files in the folder)
    if len(sys.argv) > 1:
        key_files = [Path(arg) for arg in sys.argv[1:] if arg.lower().endswith(".key")]
        if not key_files:
            show_popup("No .key files found to process.", is_error=True)
            return
    else:
        folder = Path.home() / "Desktop" / "fix_keynote"
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            show_popup(
                f"Le dossier '{folder.name}' a été créé sur votre Bureau.\n\n"
                "Veuillez y glisser vos fichiers .key corrompus, puis relancer l'application FixKeynote."
            )
            return
        
        key_files = list(folder.glob("*.key"))
        if not key_files:
            show_popup(
                f"Aucun fichier .key trouvé dans le dossier '{folder.name}'.\n\n"
                "Veuillez y glisser vos fichiers .key corrompus, puis relancer l'application."
            )
            return

    for key_file in key_files:
        filename = key_file.stem
        work_dir = key_file.parent / f"{filename}_rebuild"
        work_dir.mkdir(parents=True, exist_ok=True)
        images_dir = work_dir / "extracted_images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # --- Step 1: Extract the .key file ---
        with zipfile.ZipFile(key_file, "r") as zip_ref:
            zip_ref.extractall(work_dir)

        # --- Step 2: Extract text and notes from index.apxl ---
        index_file = work_dir / "index.apxl"
        slides_text = []
        slides_notes = []
        if index_file.exists():
            tree = ET.parse(index_file)
            root = tree.getroot()
            # Text
            for sf in root.iter("sf"):
                if sf.text:
                    slides_text.append(sf.text.strip())
            # Notes
            for note in root.iter("notes"):
                slides_notes.append(note.text.strip() if note.text else "")

        text_output = work_dir / "extracted_text.txt"
        with open(text_output, "w", encoding="utf-8") as f:
            for t in slides_text:
                f.write(t + "\n")

        # --- Step 3: Copy all found images (resilient method) ---
        images_list = []
        # Search for all images regardless of internal folder (Data, Index, Media, etc.)
        allowed_extensions = {".png", ".jpg", ".jpeg", ".tiff", ".gif"}

        for file_path in work_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                # Avoid copying what is already in extracted_images
                if "extracted_images" not in file_path.parts:
                    dest_file = images_dir / file_path.name
                    # Make sure not to overwrite if identical names exist in different folders
                    if dest_file.exists():
                        dest_file = (
                            images_dir / f"{file_path.parent.name}_{file_path.name}"
                        )

                    shutil.copy(file_path, dest_file)
                    images_list.append(dest_file.name)

        # Sort list to maintain pseudo-chronological order
        images_list.sort()

        # --- Step 4: Determine the number of slides ---
        num_slides = len(slides_text)

        # Try preview.pdf (old format) or QuickLook/Preview.pdf (new format)
        for pdf_path in [
            work_dir / "preview.pdf",
            work_dir / "QuickLook" / "Preview.pdf",
        ]:
            if pdf_path.exists():
                try:
                    reader = PdfReader(pdf_path)
                    num_slides = max(num_slides, len(reader.pages))
                except Exception:
                    pass

        # If no text or preview PDF is found, create at least one slide per extracted image
        if num_slides == 0 and images_list:
            num_slides = len(images_list)

        # If the file is completely unreadable with no info, create at least 1 slide
        if num_slides == 0:
            show_popup(
                f"❌ Cannot extract data (text, images, or preview PDF) from file '{filename}'. The file is too corrupted or in an unreadable format.",
                is_error=True,
            )
            return

        slide_order = list(range(1, num_slides + 1))

        # Prepare notes for AppleScript (properly formatting escapes)
        safe_notes = []
        for i in range(num_slides):
            n = slides_notes[i] if i < len(slides_notes) else ""
            # AppleScript uses \r for newlines
            safe_n = n.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\r")
            safe_notes.append(f'"{safe_n}"')
        applescript_notes = "{" + ", ".join(safe_notes) + "}"

        # --- Step 5: Generate AppleScript ---
        # Automatically associate images by position
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # Running in a PyInstaller bundle
            template_path = Path(sys._MEIPASS) / "rebuild_template.applescript"
        elif "RESOURCEPATH" in os.environ:
            # Running in a py2app bundle
            template_path = (
                Path(os.environ["RESOURCEPATH"]) / "rebuild_template.applescript"
            )
        else:
            # Running natively (CLI)
            template_path = Path(__file__).parent / "rebuild_template.applescript"

        with open(template_path, "r", encoding="utf-8", errors="replace") as tpl_file:
            template_content = tpl_file.read()

        applescript_code = (
            template_content.replace("_WORK_DIR_", str(work_dir))
            .replace("_APPLESCRIPT_NOTES_", applescript_notes)
            .replace("_SLIDE_ORDER_", ",".join(str(x) for x in slide_order))
            .replace("_FILENAME_", filename)
        )

        applescript_file = work_dir / "rebuild.scpt"
        with open(applescript_file, "w", encoding="utf-8") as f:
            f.write(applescript_code)

        # --- Step 6: Execute AppleScript ---
        subprocess.run(["osascript", str(applescript_file)])
        
        reconstructed_file = work_dir / f"{filename}_reconstructed.key"
        # Reveal the reconstructed file in Finder
        if reconstructed_file.exists():
            subprocess.run(["open", "-R", str(reconstructed_file)])
        else:
            # Fallback to opening the folder if the specific file wasn't found for some reason
            subprocess.run(["open", str(work_dir)])
            
        show_popup(f"Presentation recreated: {reconstructed_file}")


if __name__ == "__main__":
    main()
