on run argv
    set noteID to item 1 of argv
    set targetName to item 2 of argv
    set previousCount to (item 3 of argv) as integer

    tell application "Notes"
        tell note id noteID
            set matchingAttachments to every attachment whose name is targetName
            if (count of attachments) is not previousCount + 2 then error "첨부 개수가 바뀌어 중복 제거를 중단했습니다."
            if (count of matchingAttachments) is not 2 then error "중복 사진을 확인하지 못했습니다."
            if (name of first attachment) is not targetName then error "첫 첨부가 새 사진이 아닙니다."
            if (name of attachment 2) is not targetName then error "두 번째 첨부가 중복 사진이 아닙니다."
            delete attachment 2
            return (count of attachments) as text
        end tell
    end tell
end run
