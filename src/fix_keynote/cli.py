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

        # --- Étape 3 : Copier toutes les images trouvées (méthode résiliente) ---
        images_list = []
        # On va chercher toutes les images peu importe le dossier interne (Data, Index, Media, etc.)
        allowed_extensions = {".png", ".jpg", ".jpeg", ".tiff", ".gif"}
        
        for file_path in work_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                # Éviter de recopier ce qui est déjà dans extracted_images
                if "extracted_images" not in file_path.parts:
                    dest_file = images_dir / file_path.name
                    # S'assurer de ne pas écraser si noms identiques dans dossiers différents
                    if dest_file.exists():
                        dest_file = images_dir / f"{file_path.parent.name}_{file_path.name}"
                    
                    shutil.copy(file_path, dest_file)
                    images_list.append(dest_file.name)
        
        # Trier la liste pour conserver un ordre pseudo-chronologique
        images_list.sort()

        # --- Étape 4 : Déterminer le nombre de slides ---
        num_slides = len(slides_text)
        
        # Essayer preview.pdf (ancien format) ou QuickLook/Preview.pdf (nouveau format)
        for pdf_path in [work_dir / "preview.pdf", work_dir / "QuickLook" / "Preview.pdf"]:
            if pdf_path.exists():
                try:
                    reader = PdfReader(pdf_path)
                    num_slides = max(num_slides, len(reader.pages))
                except Exception:
                    pass

        # Si on ne trouve ni texte ni PDF de preview, on crée au moins une slide par image extraite
        if num_slides == 0 and images_list:
            num_slides = len(images_list)

        # Si le fichier est totalement illisible sans aucune info, on crée au moins 1 slide
        if num_slides == 0:
            print(f"❌ Impossible d'extraire des données (texte, images ou PDF de prévisualisation) depuis le fichier '{filename}'. Le fichier est trop corrompu ou dans un format illisible.")
            return

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