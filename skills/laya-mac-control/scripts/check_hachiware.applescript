on run argv
    tell application "Notes"
        set targetNote to note id (item 1 of argv)
        set targetName to item 2 of argv
        set matches to every attachment of targetNote whose name is targetName
        set firstMatches to 0
        if (count of attachments of targetNote) > 0 then
            if (name of first attachment of targetNote) is targetName then set firstMatches to 1
        end if
        return ((count of attachments of targetNote) as text) & tab & ((count of matches) as text) & tab & (firstMatches as text)
    end tell
end run
