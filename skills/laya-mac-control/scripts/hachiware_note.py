"""Place one new Hachiware Pinterest image at the top of an Apple Note."""

import ctypes
import datetime
import fcntl
import hashlib
import json
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


TITLE = "Laya 하치왕왕 사진 모음"
# Pinterest Ideas search results change over time. These pins were visually checked
# to contain Hachiware; only use them while they still appear in a live result page.
PINTEREST_TOPICS = (
    ("https://jp.pinterest.com/ideas/-/899990466928/", (
        "1548181177296304", "21392166973299314", "7318418139447558",
        "8585055532518148", "224476362673742062", "847310117415432103",
    )),
    ("https://jp.pinterest.com/ideas/-/948075266825/", (
        "224476362673742062", "371617406777387688", "667306869818592673",
        "790733647131578694", "16536723627222258", "17381148556279219",
        "25684660372588865", "977844137858532817", "42291683992921594",
        "764767580511925806", "590323463716015564", "464504149095083145",
    )),
    ("https://jp.pinterest.com/ideas/-/961250704881/", (
        "991917886684853422", "7036943161485557", "22095854414297872",
        "949063321461314949", "732538695684979764", "977492294111418093",
        "879961214757341770", "936748791254139816", "1075234479806764284",
        "13510867625511491", "878624208538252397", "565412928239621751",
        "936748791261478937", "138345019798314373", "3659243439843402",
        "8162843069130835", "616289530301582011",
    )),
    ("https://jp.pinterest.com/ideas/-/941347485649/", (
        "56787645304065914", "21110691999588152", "7036943161485557",
        "8162843069130835", "4011087179547450", "23292123067289661",
        "244742560994019078", "20969954511513615", "3870349674870246",
        "914862418647523", "174021973096224040", "3870349674870197",
        "12314598977486119", "21603273207138243", "3659243439843402",
    )),
)
STATE_DIR = Path.home() / "Library" / "Application Support" / "Laya"
IMAGE_DIR = Path.home() / "Pictures" / "Laya" / "Hachiware"
SCRIPT = Path(__file__).with_name("append_hachiware.applescript")
CHECK_SCRIPT = Path(__file__).with_name("check_hachiware.applescript")
DEDUPE_SCRIPT = Path(__file__).with_name("dedupe_hachiware.applescript")
SHOW_SCRIPT = Path(__file__).with_name("show_hachiware.applescript")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"


def _pinterest_candidates(used):
    seen = set(used)
    for topic_url, approved_pin_ids in PINTEREST_TOPICS:
        request = urllib.request.Request(topic_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=20) as response:
            if urllib.parse.urlparse(response.geturl()).hostname != "jp.pinterest.com":
                raise RuntimeError("핀터레스트 검색 페이지로 연결되지 않았습니다.")
            page = response.read(4 * 1024 * 1024 + 1).decode("utf-8")
        if len(page) > 4 * 1024 * 1024:
            raise RuntimeError("핀터레스트 검색 페이지가 너무 큽니다.")
        match = re.search(r'<script id="__PWS_INITIAL_PROPS__"[^>]*>(.*?)</script>', page, re.DOTALL)
        if not match:
            raise RuntimeError("핀터레스트 검색 결과를 읽지 못했습니다.")
        pins = json.loads(match.group(1)).get("initialReduxState", {}).get("pins", {})
        for pin_id in approved_pin_ids:
            pin = pins.get(pin_id, {})
            image = pin.get("images", {}).get("736x", {})
            image_url = image.get("url", "")
            parsed = urllib.parse.urlparse(image_url)
            if (parsed.scheme != "https" or parsed.hostname != "i.pinimg.com" or
                    not re.fullmatch(r"/736x/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.jpe?g", parsed.path)):
                continue
            if image_url in seen:
                continue
            seen.add(image_url)
            yield {
                "url": image_url,
                "handle": "pinterest-" + pin_id,
                "source": "https://jp.pinterest.com/pin/" + pin_id + "/",
                "kind": "pinterest",
            }


def _ensure_accessibility():
    accessibility = ctypes.CDLL("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")
    accessibility.AXIsProcessTrusted.restype = ctypes.c_bool
    if not accessibility.AXIsProcessTrusted():
        raise RuntimeError(
            "터미널에 손쉬운 사용 권한이 없습니다. 시스템 설정 > 개인정보 보호 및 보안 > "
            "손쉬운 사용에서 터미널(또는 현재 사용하는 터미널 앱)을 켠 뒤 다시 실행해 주세요."
        )


def _download(url, handle):
    extension = Path(urllib.parse.urlparse(url).path).suffix.lower()
    safe_handle = re.sub(r"[^a-zA-Z0-9_-]", "-", str(handle))[:40]
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    destination = IMAGE_DIR / f"{timestamp}-{safe_handle}-{digest}{extension}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response, destination.open("wb") as output:
            content_type = response.headers.get_content_type()
            if content_type not in ("image/jpeg", "image/png"):
                raise RuntimeError("이미지 형식이 JPEG 또는 PNG가 아닙니다.")
            total = 0
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > 15 * 1024 * 1024:
                    raise RuntimeError("이미지가 15MB를 초과합니다.")
                output.write(chunk)
        if not total:
            raise RuntimeError("빈 이미지가 내려왔습니다.")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return destination


def _append_to_notes(image_path, note_id):
    try:
        completed = subprocess.run(
            ["osascript", str(SCRIPT), note_id or "", str(image_path)],
            capture_output=True, text=True, timeout=90, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("메모 앱 응답 시간이 초과되었습니다. macOS 자동화 권한을 확인해 주세요.") from exc
    if completed.returncode:
        error = completed.stderr.strip()
        if "-25211" in error:
            raise RuntimeError(
                "터미널의 손쉬운 사용 권한이 꺼져 메모에 사진을 넣지 못했습니다. "
                "시스템 설정 > 개인정보 보호 및 보안 > 손쉬운 사용에서 터미널을 켜 주세요."
            )
        raise RuntimeError(error or "메모에 사진을 추가하지 못했습니다.")
    parts = completed.stdout.strip().split("\t")
    if len(parts) != 2 or not parts[0].startswith("x-coredata://") or not parts[1].isdigit():
        raise RuntimeError("메모 앱에서 예상하지 못한 결과가 왔습니다.")
    return parts[0], int(parts[1])


def _wait_for_single_attachment(note_id, filename, previous_count):
    stable = 0
    duplicate_stable = 0
    deduped = False
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        completed = subprocess.run(
            ["osascript", str(CHECK_SCRIPT), note_id, filename],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip() or "메모 첨부 확인에 실패했습니다.")
        parts = completed.stdout.strip().split("\t")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise RuntimeError("메모 첨부 확인 결과가 올바르지 않습니다.")
        total, matches, first_matches = map(int, parts)
        if total == previous_count + 1 and matches == 1 and first_matches == 1:
            stable += 1
            duplicate_stable = 0
            if stable >= 4:
                return
        else:
            stable = 0
            if total == previous_count + 2 and matches == 2 and not deduped:
                duplicate_stable += 1
                if duplicate_stable >= 4:
                    _remove_duplicate(note_id, filename, previous_count)
                    deduped = True
                    duplicate_stable = 0
            else:
                duplicate_stable = 0
        time.sleep(1)
    raise RuntimeError("메모 앱에서 사진 한 장만 추가됐는지 확인하지 못했습니다.")


def _remove_duplicate(note_id, filename, previous_count):
    completed = subprocess.run(
        ["osascript", str(DEDUPE_SCRIPT), note_id, filename, str(previous_count)],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "메모의 중복 사진을 제거하지 못했습니다.")


def _show_note(note_id):
    completed = subprocess.run(
        ["osascript", str(SHOW_SCRIPT), note_id],
        capture_output=True, text=True, timeout=30, check=False,
    )
    return completed.returncode == 0


def append_hachiware_photo():
    _ensure_accessibility()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_path = STATE_DIR / "hachiware-note.json"
    with (STATE_DIR / "hachiware-note.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        used = set(state.get("used_images", []))
        selection = None
        image_path = None
        for candidate in _pinterest_candidates(used):
            try:
                image_path = _download(candidate["url"], candidate["handle"])
            except (urllib.error.URLError, RuntimeError):
                continue
            selection = candidate
            break
        if selection is None:
            raise RuntimeError("핀터레스트 검색 결과에서 새로운 하치와레 사진을 내려받지 못했습니다.")
        url = selection["url"]
        note_id, previous_count = _append_to_notes(image_path, state.get("note_id", ""))
        _wait_for_single_attachment(note_id, image_path.name, previous_count)

        state["note_id"] = note_id
        state["used_images"] = state.get("used_images", []) + [url]
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=STATE_DIR, delete=False) as output:
            json.dump(state, output, ensure_ascii=False, indent=2)
            temp_path = Path(output.name)
        temp_path.replace(state_path)
        opened = _show_note(note_id)
        return {
            "note": TITLE,
            "photos_added": len(state["used_images"]),
            "saved_image": str(image_path),
            "source": selection["source"],
            "image_type": selection["kind"],
            "opened": opened,
        }
