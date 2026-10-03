on run argv
    tell application "Notes"
        show note id (item 1 of argv)
        activate
    end tell
end run
