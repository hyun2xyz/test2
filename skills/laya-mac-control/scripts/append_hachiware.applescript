on run argv
    set savedID to item 1 of argv
    set imagePath to item 2 of argv
    set noteTitle to "Laya 하치왕왕 사진 모음"

    tell application "Notes"
        set targetNote to missing value
        if savedID is not "" then
            try
                set targetNote to note id savedID
            end try
        end if
        if targetNote is missing value then
            set targetFolder to folder "Notes" of default account
            set matches to every note of targetFolder whose name is noteTitle
            if (count of matches) > 0 then
                set targetNote to item 1 of matches
            else
                set targetNote to make new note at targetFolder with properties {name:noteTitle, body:"<div>하치와레 사진을 모읍니다.</div>"}
            end if
        end if
        set previousCount to count of attachments of targetNote
        set targetID to id of targetNote
        show targetNote
        activate
        set selectedNotes to selection
        if (count of selectedNotes) is not 1 then error "전용 메모 선택을 확인하지 못했습니다."
        if (id of item 1 of selectedNotes) is not targetID then error "다른 메모가 선택되어 사진 추가를 중단했습니다."
    end tell

    tell application "System Events"
        tell process "Notes"
            set frontmost to true
            set targetWindow to missing value
            repeat with candidateWindow in windows
                set windowSize to size of candidateWindow
                if (item 1 of windowSize) > 400 and (item 2 of windowSize) > 400 then
                    set targetWindow to contents of candidateWindow
                    exit repeat
                end if
            end repeat
            if targetWindow is missing value then error "메모 편집창을 찾지 못했습니다."
            set focused of text area 1 of scroll area 2 of splitter group 1 of targetWindow to true
            key code 126 using {command down}
            key code 125
            click menu button 2 of toolbar 1 of targetWindow
            try
                click menu item "파일 첨부" of menu 1 of menu button 2 of toolbar 1 of targetWindow
            on error
                click menu item "Attach File" of menu 1 of menu button 2 of toolbar 1 of targetWindow
            end try
        end tell
        delay 0.3
        key code 5 using {command down, shift down}
        tell process "Notes"
            repeat 50 times
                if (exists text field 1 of sheet 1 of sheet 1 of targetWindow) then exit repeat
                delay 0.1
            end repeat
            if not (exists text field 1 of sheet 1 of sheet 1 of targetWindow) then error "파일 경로 입력창을 찾지 못했습니다."
            set value of text field 1 of sheet 1 of sheet 1 of targetWindow to imagePath
        end tell
        key code 36
        tell process "Notes"
            repeat 50 times
                if not (exists sheet 1 of sheet 1 of targetWindow) then exit repeat
                delay 0.1
            end repeat
            if (exists sheet 1 of sheet 1 of targetWindow) then error "사진 파일 선택을 확인하지 못했습니다."
        end tell
        key code 36
    end tell

    return targetID & tab & (previousCount as text)
end run
