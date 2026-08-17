-- Export a .pptx to .pdf using the real Microsoft PowerPoint app, so slide
-- animations, builds, and layout render exactly as in the presentation.
-- Usage:  osascript export_pptx_to_pdf.applescript <in.pptx> <out.pdf>
-- Prints "OK <path>" on success, or an error string (which the pipeline shows).
on run argv
    set inPath to item 1 of argv
    set outPath to item 2 of argv
    tell application "Microsoft PowerPoint"
        activate
        open (POSIX file inPath)
        set theDoc to active presentation
        save theDoc in (POSIX file outPath) as save as PDF
        close theDoc saving no
    end tell
    set p to POSIX path of (POSIX file outPath)
    try
        do shell script "test -f " & quoted form of p
        return "OK " & p
    on error
        error "save reported success but no file at " & p
    end try
end run
