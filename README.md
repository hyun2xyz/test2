# Laya Mac Control — Codex Skill

이 저장소의 [`laya-mac-control`](skills/laya-mac-control/SKILL.md)은 **Codex 스킬**과 작은 macOS 터미널 명령입니다. 터미널에서 `laya 메모 켜줘`처럼 입력하거나 Codex에서 `$laya-mac-control 메모 켜줘`로 호출할 수 있습니다. 별도 Mac 앱을 설치하지 않습니다.

## Codex에 설치

Codex에서 다음처럼 요청하세요.

> `https://github.com/hyun2xyz/test2/tree/main/skills/laya-mac-control` 스킬을 설치해줘.

또는 Codex의 `skill-installer`를 사용할 수 있습니다.

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo hyun2xyz/test2 --path skills/laya-mac-control
```

터미널 명령도 설치하려면, 설치된 스킬의 스크립트를 `PATH`에 연결하세요.

```bash
mkdir -p ~/.local/bin
ln -s ~/.codex/skills/laya-mac-control/scripts/laya ~/.local/bin/laya
ln -s ~/.codex/skills/laya-mac-control/scripts/laya ~/.local/bin/Laya
```

`~/.local/bin`이 `PATH`에 없다면 셸 설정에 추가한 뒤 새 터미널을 여세요. 설치 후 `laya --help`와 `laya 메모 켜줘 --dry-run --json`으로 확인할 수 있습니다. 새 Codex 작업에서는 `$laya-mac-control 포토부스 켜줘`처럼 호출합니다.

## 동작 범위

로컬 `laya` 명령은 Photo Booth, 메모, Chrome, Safari, Finder, 캘린더 실행과 배터리 상태, macOS 정보, 볼륨, 클립보드, 스크린샷, Spotlight 파일 검색을 지원합니다. `--dry-run --json`으로 실행 전 해석 결과를 확인할 수 있습니다. 지원하지 않는 요청은 임의 명령으로 바꾸지 않고 오류를 냅니다.

`Laya 하치왕왕 보여줘` 또는 `laya 하치왕왕 보여줘`는 [핀터레스트의 하치와레 검색 결과](https://jp.pinterest.com/ideas/-/899990466928/)에서 확인한 핀 중 사용하지 않은 이미지 한 장을 내려받아 Mac 메모의 **Laya 하치왕왕 사진 모음** 제목 바로 아래에 추가합니다. 다시 실행할 때마다 다른 이미지 한 장이 기존 사진 위에 쌓입니다. 이전에 추가한 사진은 그대로 둡니다. 사진 파일은 `~/Pictures/Laya/Hachiware`에 보관합니다. 터미널에서 실행하려면 시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용에서 터미널을 켜야 하며, 메모 자동화 권한도 필요합니다.

`Laya 밤이 깊었네`는 [지정한 유튜브 영상](https://www.youtube.com/watch?v=Nc76PTAngtk&list=RDNc76PTAngtk&start_radio=1&t=0s)을 기본 브라우저에서 처음부터 엽니다. 재생목록 설정은 유지합니다. 브라우저의 자동 재생 설정에 따라 재생 버튼을 눌러야 할 수 있습니다.

이 명령은 macOS 기본 도구를 사용하는 규칙 기반 실행 보조 파일이며 Laya-MLX 모델은 포함하지 않습니다. 결과의 `engine: fast-path-rule`은 모델 추론을 뜻하지 않습니다. [MIT 라이선스](skills/laya-mac-control/LICENSE)는 스킬 폴더에만 적용됩니다.

## 다른 사람들이 만든 재미있는 Laya 활용

[재미있는 Laya 스킬·데모 모음](docs/fun-laya-skills.md)에 게임, 브라우저 에이전트, Mac 화면보호기 등을 짧게 정리했습니다. 실제 Codex 스킬과 데모 프로젝트를 구분했고, 외부 코드는 복사하거나 설치하지 않았습니다.
