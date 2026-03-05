set workDir to "_WORK_DIR_"
set textFilePath to (POSIX file (workDir & "/extracted_text.txt"))
set slideTexts to {}
try
    set slideTexts to paragraphs of (read textFilePath as «class utf8»)
end try

set imageFolder to workDir & "/extracted_images/"
set imageFiles to paragraphs of (do shell script "ls " & quoted form of imageFolder)
set allNotes to _APPLESCRIPT_NOTES_

tell application "Keynote"
    activate
    set themeName to "Blanc basique"
    try
        set newDoc to make new document with properties {document theme:theme themeName}
    on error
        -- Si "Blanc basique" ne marche pas, essaye de prendre le premier thème dispo
        set newDoc to make new document
    end try
    set imgIndex to 1

    repeat with i in {_SLIDE_ORDER_}
        set slideText to item i of slideTexts
        set newSlide to make new slide at end of slides of newDoc with properties {slide layout:"Title & Bullets"}
        tell newSlide
            set the object text of default body item to slideText
        end tell

        -- Ajouter note si elle existe
        try
            set noteText to item i of allNotes
            if noteText is not "" then set presenter notes of newSlide to noteText
        end try

        -- Ajouter toutes les images disponibles
        repeat while imgIndex ≤ count of imageFiles
            set imgName to item imgIndex of imageFiles
            set imgPath to (POSIX file (imageFolder & imgName))
            tell newSlide
                make new image with properties {file:imgPath}
            end tell
            set imgIndex to imgIndex + 1
            exit repeat -- une image par slide pour éviter surcharge
        end repeat
    end repeat

    set savePath to (POSIX file (workDir & "/_FILENAME__reconstructed_sain.key"))
    save newDoc in savePath
end tell
