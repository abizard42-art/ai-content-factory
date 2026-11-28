import pathlib
import tempfile
import unittest
from PIL import Image
from scripts.peta_sunyi.animated_overlays import create_overlay

class AnimatedOverlayTests(unittest.TestCase):
    def test_motion_overlay_has_multiple_frames_and_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "motion.gif"
            create_overlay(target, 2.0, motion="flashlight", seed=4)
            with Image.open(target) as gif:
                self.assertGreater(gif.n_frames, 1)
                self.assertEqual(gif.size, (960, 540))
                gif.seek(0)
                alpha = gif.convert("RGBA").getchannel("A")
                self.assertLess(alpha.getextrema()[0], 255)

    def test_timeline_graphic_is_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "timeline.gif"
            create_overlay(target, 2.0, graphic={
                "type": "timeline",
                "heading": "UJI TIMELINE",
                "items": [{"label": "2012"}, {"label": "2022"}, {"label": "2025"}]
            })
            with Image.open(target) as gif:
                self.assertGreater(gif.n_frames, 1)
                self.assertEqual(gif.size, (960, 540))

if __name__ == "__main__":
    unittest.main()
