import importlib.util
import pathlib
import re
import tempfile
import unittest

MODULE_PATH = pathlib.Path("scripts/peta-sunyi/render_long_horror.py")
SPEC = importlib.util.spec_from_file_location("peta_sunyi_renderer", MODULE_PATH)
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)

class SubtitleRegressionTests(unittest.TestCase):
    def read_caption_words(self, ass_path):
        words = []
        for line in pathlib.Path(ass_path).read_text(encoding="utf-8").splitlines():
            if not line.startswith("Dialogue:"):
                continue
            match = re.search(r"\\rDefault\}(.*)$", line)
            self.assertIsNotNone(match)
            caption = match.group(1).replace(r"\N", " ")
            words.extend(caption.split())
        return words

    def test_long_vtt_cue_is_split_at_six_words_without_loss(self):
        source = "Ini adalah kalimat panjang yang harus terbagi menjadi beberapa bagian tanpa kehilangan satu kata pun."
        with tempfile.TemporaryDirectory() as temp:
            vtt = pathlib.Path(temp) / "sample.vtt"
            ass = pathlib.Path(temp) / "sample.ass"
            vtt.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:08.000\n" + source + "\n", encoding="utf-8")
            RENDERER.subtitles(vtt, ass, "NARATOR", source, 8.0)
            caption_lines = self.read_caption_words(ass)
            self.assertEqual(RENDERER.normalized_words(" ".join(caption_lines)), RENDERER.normalized_words(source))
            for line in pathlib.Path(ass).read_text(encoding="utf-8").splitlines():
                if line.startswith("Dialogue:"):
                    caption = re.search(r"\\rDefault\}(.*)$", line).group(1).replace(r"\N", " ")
                    self.assertLessEqual(len(caption.split()), 6)

    def test_incomplete_vtt_falls_back_to_complete_script(self):
        source = "Semua kata dari naskah harus tetap muncul pada subtitle akhir."
        with tempfile.TemporaryDirectory() as temp:
            vtt = pathlib.Path(temp) / "incomplete.vtt"
            ass = pathlib.Path(temp) / "fallback.ass"
            vtt.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nSemua kata dari naskah\n", encoding="utf-8")
            RENDERER.subtitles(vtt, ass, "NARATOR", source, 5.0)
            caption_lines = self.read_caption_words(ass)
            self.assertEqual(RENDERER.normalized_words(" ".join(caption_lines)), RENDERER.normalized_words(source))

if __name__ == "__main__":
    unittest.main()
