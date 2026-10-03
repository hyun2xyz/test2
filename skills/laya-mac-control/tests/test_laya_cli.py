import importlib.machinery
import importlib.util
import json
import pathlib
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "laya"
sys.path.insert(0, str(SCRIPT.parent))
import hachiware_note
loader = importlib.machinery.SourceFileLoader("laya_cli", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
laya_cli = importlib.util.module_from_spec(spec)
loader.exec_module(laya_cli)


class LayaCliTests(unittest.TestCase):
    def test_requested_actions_route(self):
        examples = (
            ("메모 켜줘", "launch_app", {"app": "Notes"}),
            ("배터리 상태 알려줘", "battery", {}),
            ("맥 정보 알려줘", "system_info", {}),
            ("볼륨 30으로 설정해", "volume_set", {"level": 30}),
            ("클립보드에 Hello World 복사해줘", "clipboard_set", {"text": "Hello World"}),
            ("파일 Report.PDF 찾아줘", "file_search", {"name": "Report.PDF"}),
            ("스크린샷 찍어줘", "screenshot", {}),
            ("하치왕왕 보여줘", "hachiware_note_append", {}),
            ("Laya 하치왕왕 보여줘", "hachiware_note_append", {}),
            ("밤이 깊었네", "youtube_play", {"url": laya_cli.NIGHT_SONG_URL}),
            ("Laya 밤이 깊었네", "youtube_play", {"url": laya_cli.NIGHT_SONG_URL}),
        )
        for prompt, action, params in examples:
            with self.subTest(prompt=prompt):
                self.assertEqual(laya_cli.route(prompt), {"action": action, "params": params})

    def test_unsupported_requests_do_not_execute(self):
        for prompt in ("메모에 글 적어줘", "크롬 종료해", "볼륨 120으로 설정해", "앱 켜줘"):
            with self.subTest(prompt=prompt):
                with self.assertRaises(ValueError):
                    laya_cli.route(prompt)

    def test_clipboard_text_is_preserved_and_not_echoed(self):
        action = laya_cli.route("클립보드에 Hello   World 복사해줘")
        self.assertEqual(action["params"]["text"], "Hello   World")
        result = laya_cli.execute(action, dry_run=True)
        self.assertEqual(result["params"], {"text_length": 13})

    @patch.object(laya_cli, "command")
    def test_dry_run_has_no_side_effect(self, command):
        result = laya_cli.execute(laya_cli.route("메모 켜줘"), dry_run=True)
        command.assert_not_called()
        self.assertEqual(result["status"], "dry-run")

    @patch.object(laya_cli.platform, "system", return_value="Darwin")
    @patch.object(laya_cli, "command")
    def test_launch_uses_exact_app(self, command, _system):
        result = laya_cli.execute(laya_cli.route("메모 켜줘"))
        command.assert_called_once_with("open", "-a", "Notes")
        self.assertEqual(result["status"], "launch-requested")

    @patch.object(laya_cli.platform, "system", return_value="Darwin")
    @patch.object(laya_cli, "command")
    def test_night_song_opens_full_url(self, command, _system):
        result = laya_cli.execute(laya_cli.route("Laya 밤이 깊었네"))
        self.assertTrue(laya_cli.NIGHT_SONG_URL.endswith("&t=0s"))
        command.assert_called_once_with("open", laya_cli.NIGHT_SONG_URL)
        self.assertEqual(result["status"], "open-requested")


class HachiwareSelectionTests(unittest.TestCase):
    def test_search_uses_only_approved_unused_pinterest_image(self):
        image_url = "https://i.pinimg.com/736x/83/fb/32/83fb32a034b36a27c2c620260e853397.jpg"
        page = {"initialReduxState": {"pins": {
            "1548181177296304": {"images": {"736x": {"url": image_url}}},
            "unrelated": {"images": {"736x": {"url": "https://elsewhere.test/not-hachiware.jpg"}}},
        }}}
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = "https://jp.pinterest.com/ideas/-/899990466928/"
        response.read.return_value = (
            '<script id="__PWS_INITIAL_PROPS__" type="application/json">'
            + json.dumps(page) + "</script>"
        ).encode()
        with patch.object(hachiware_note, "PINTEREST_TOPICS", ((response.geturl(),
                ("unrelated", "1548181177296304")),)), \
                patch.object(hachiware_note.urllib.request, "urlopen", return_value=response):
            selected = list(hachiware_note._pinterest_candidates(set()))
            used = list(hachiware_note._pinterest_candidates({image_url}))
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["url"], image_url)
        self.assertEqual(selected[0]["source"], "https://jp.pinterest.com/pin/1548181177296304/")
        self.assertEqual(used, [])

    def test_missing_accessibility_stops_before_download(self):
        accessibility = Mock()
        accessibility.AXIsProcessTrusted.return_value = False
        with patch.object(hachiware_note.ctypes, "CDLL", return_value=accessibility), \
                patch.object(hachiware_note, "_download") as download:
            with self.assertRaisesRegex(RuntimeError, "손쉬운 사용 권한"):
                hachiware_note.append_hachiware_photo()
        download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
