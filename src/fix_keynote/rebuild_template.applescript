set workDir to "_WORK_DIR_"
set textFilePath to (POSIX file (workDir & "/extracted_text.txt"))
set outFilePath to (POSIX file (workDir & "/_FILENAME__reconstructed.key"))
set slideTexts to {}
try
    set slideTexts to paragraphs of (read textFilePath as Çclass utf8È)
end try

set imageFolder to workDir & "/extracted_images/"
set imageFiles to paragraphs of (do shell script "ls " & quoted form of imageFolder)
set allNotes to _APPLESCRIPT_NOTES_

tell application "Keynote"
    activate
    set themeName to "Basic White"
    try
        set newDoc to make new document with properties {document theme:theme themeName}
    on error
        -- If "Basic White" fails (e.g. non-english system), try fallback generic name or none
        try
            set newDoc to make new document with properties {document theme:theme "Blanc basique"}
        on error
            set newDoc to make new document
        end try
    end try
    set imgIndex to 1

    repeat with i in {_SLIDE_ORDER_}
        set slideText to ""
        try
            if (count of slideTexts) ³ i then
                set slideText to item i of slideTexts
            end if
        end try

        set newSlide to make new slide at end of slides of newDoc
        
        if slideText is not "" then
            try
                tell newSlide
                    set the object text of default body item to slideText
                end tell
            end try
        end if

        -- Add note if it exists
        try
            set noteText to item i of allNotes
            if noteText is not "" then set presenter notes of newSlide to noteText
        end try

        -- Add available images
        set imagesAdded to 0
        repeat while imgIndex ² count of imageFiles
            set imgName to item imgIndex of imageFiles
            set imgPathStr to imageFolder & imgName
            
            try
                -- Direct file object creation via StandardAdditions, reliable way to build paths into Keynote
                set theFile to POSIX file imgPathStr as alias
                
                tell newSlide
                    make new image with properties {file:theFile}
                end tell
                set imagesAdded to imagesAdded + 1
            on error errMsg
                -- Ignore silent failures on specific images
            end try
            
            set imgIndex to imgIndex + 1
            if imagesAdded ³ 1 then exit repeat -- One image successfully added per slide
        end repeat
    end repeat

    -- Remove the default blank slide that Keynote creates initially
    try
        if (count of slides of newDoc) > (count of {_SLIDE_ORDER_}) then
            delete slide 1 of newDoc
        end if
    end try

    save newDoc in outFilePath
end tell
