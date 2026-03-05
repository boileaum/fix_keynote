import zipfile
import xml.etree.ElementTree as ET
import shutil
import subprocess
import sys
from pathlib import Path
from PyPDF2 import PdfReader

def main():
    # --- Configuration ---
    # Arguments : un fichier .key ou aucun (traite tous les .key du dossier)
    if len(sys.argv) > 1:
        key_files = [Path(sys.argv[1])]
    else:
        folder = Path.home() / "Desktop" / "fix_keynote"
        if not folder.exists():
            print(f"Le dossier {folder} n'existe pas.")
            return
        key_files = list(folder.glob("*.key"))

    for key_file in key_files:
        filename = key_file.stem
        work_dir = key_file.parent / f"{filename}_rebuild"
        work_dir.mkdir(parents=True, exist_ok=True)
        images_dir = work_dir / "extracted_images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # --- Étape 1 : Extraire le .key ---
        with zipfile.ZipFile(key_file, "r") as zip_ref:
            zip_ref.extractall(work_dir)

        # --- Étape 2 : Extraire texte et notes depuis index.apxl ---
        index_file = work_dir / "index.apxl"
        slides_text = []
        slides_notes = []
        if index_file.exists():
            tree = ET.parse(index_file)
            root = tree.getroot()
            # Texte
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

        # --- Étape 3 : Copier toutes les images ---
        data_dir = work_dir / "Data"
        images_list = []
        if data_dir.exists():
            for f in sorted(data_dir.iterdir()):
                if f.is_file():
                    shutil.copy(f, images_dir / f.name)
                    images_list.append(f.name)  # liste d’images triée par ordre dans Data

        # --- Étape 4 : Lire le PDF preview.pdf pour l’ordre ---
        pdf_file = work_dir / "preview.pdf"
        num_slides = len(slides_text)
        if pdf_file.exists():
            try:
                reader = PdfReader(pdf_file)
                num_slides = len(reader.pages)
            except:
                pass  # garder le nombre de slides extrait du XML

        slide_order = list(range(1, num_slides + 1))

        # Préparer les notes pour AppleScript (en formatant correctement les échappements)
        safe_notes = []
        for i in range(num_slides):
            n = slides_notes[i] if i < len(slides_notes) else ""
            # AppleScript utilise \r pour les retours à la ligne
            safe_n = n.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\r")
            safe_notes.append(f'"{safe_n}"')
        applescript_notes = "{" + ", ".join(safe_notes) + "}"

        # --- Étape 5 : Générer AppleScript ---
        # On associe images automatiquement par position
        template_path = Path(__file__).parent / "rebuild_template.applescript"
        with open(template_path, "r", encoding="utf-8") as tpl_file:
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

        # --- Étape 6 : Exécuter AppleScript ---
        subprocess.run(["osascript", str(applescript_file)])
        print(f"Présentation recréée : {work_dir}/{filename}_reconstructed_sain.key")

if __name__ == "__main__":
    main()