---
name: laya-mac-control
description: Use the local `laya` terminal command for basic macOS actions, a specific YouTube song, and the dedicated Hachiware photo collection in Apple Notes. Handles Korean requests such as `laya 메모 켜줘`, `Laya 밤이 깊었네`, `laya 하치왕왕 보여줘`, battery status, volume, clipboard, screenshot, and file search. Do not use for unrelated Laya desktop software.
---

# Laya Mac Control

This is a **Codex skill** with a small terminal command at `scripts/laya`. It translates a supported Korean request into one macOS built-in action. It does not call an LLM or install a desktop app.

## Use from Codex

1. Confirm this is macOS. Locate `laya` on `PATH`; if unavailable, run `python3 scripts/laya` from this skill directory. Do not assume an unrelated `laya` command has this skill's behavior; inspect `laya --help` when the target is unclear.
2. Pass the user's requested phrase as command arguments. Use `--dry-run --json` first for a state-changing or ambiguous action, inspect `action` and `params`, then execute the same request. The command also accepts the legacy form `laya run '메모 켜줘'`.
3. Inspect command output. For app launch, a successful `open -a` reports that launch was requested; verify the app window with an available native app tool before claiming it opened.

## Supported requests

| Terminal example | Action |
| --- | --- |
| `laya 메모 켜줘` | Open Notes. Also supports Photo Booth, Chrome, Safari, Finder, Calendar. |
| `laya 배터리 상태 알려줘` | Read battery status. |
| `laya 맥 정보 알려줘` | Read macOS version and architecture. |
| `laya 볼륨 알려줘` / `laya 볼륨 30으로 설정해` | Read or set output volume. |
| `laya 클립보드 보여줘` / `laya 클립보드에 안녕 복사해줘` | Read or set clipboard text. |
| `laya 스크린샷 찍어줘` | Save a PNG in the current directory. |
| `laya 파일 보고서 찾아줘` | Search Spotlight by filename (first 20 matches). |
| `Laya 하치왕왕 보여줘` or `laya 하치왕왕 보여줘` | Search public Hachiware results on Pinterest, download one new image, and insert it at the top of the dedicated Apple Note. |
| `Laya 밤이 깊었네` or `laya 밤이 깊었네` | Open the requested YouTube video in the default browser from the beginning, preserving its radio playlist link. |

The song command opens `https://www.youtube.com/watch?v=Nc76PTAngtk&list=RDNc76PTAngtk&start_radio=1&t=0s`. The explicit zero timestamp avoids the 5:12 start time in the original link. The CLI reports that opening the URL was requested; browser autoplay settings may still require a click to start playback.

When the user says “Laya 하치왕왕 보여줘” to Codex, run `laya 하치왕왕 보여줘`. Both capitalizations work in Terminal when both aliases are installed. The first run creates the note **Laya 하치왕왕 사진 모음** in the default account's Notes folder; later runs insert one new image directly below the title, above all older images, in that same note. The command reads current public [Pinterest Hachiware Ideas results](https://jp.pinterest.com/ideas/-/899990466928/) and selects an unused pin whose image was checked to contain Hachiware. It downloads the image from Pinterest's image host and returns the pin URL as `source`. Earlier images from other sites remain in the note. Images are saved in `~/Pictures/Laya/Hachiware`, with selection state in `~/Library/Application Support/Laya/hachiware-note.json`. The command needs internet access, macOS Automation permission for Notes, and Accessibility permission for the terminal app to control the Notes interface. If macOS reports `-25211`, direct the user to System Settings → Privacy & Security → Accessibility and have them enable Terminal (or their terminal app). `photos_added` counts successful runs recorded by this skill.

Use macOS built-in commands directly for another clearly requested basic operation when the local command has no route; do not present that as a `laya` command. Ask for missing paths or content when needed. Opening Notes does not authorize writing a note; opening Chrome does not authorize browsing. Do not invent support for unsupported phrases.

The `engine: fast-path-rule` result means deterministic routing, not Laya-MLX inference. Never report model inference for these actions. Treat clipboard output and screenshots as potentially private; show their contents only when requested. A macOS permission or Codex sandbox denial is a real limit to report, not something to work around.

Requires macOS and Python 3. The scripts have no third-party dependencies.
