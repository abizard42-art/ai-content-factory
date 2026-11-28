import copy
import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "peta-sunyi" / "humanize_narration.py"
SPEC = importlib.util.spec_from_file_location("peta_sunyi_humanize_narration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
collect_targets = MODULE.collect_targets
apply_rewrites = MODULE.apply_rewrites

class HumanizerShapeTests(unittest.TestCase):
    def test_episode_only_changes_scene_text(self):
        source = {"episode_id":"test","visual_style":"cinematic_2d","scenes":[
            {"scene":1,"text":"Narasi lama.","title":"JUDUL","shot":"01","kind":"ai"},
            {"scene":2,"text":"Narasi kedua.","title":"PETA","shot":"MAP","kind":"graphic"}]}
        original = copy.deepcopy(source)
        targets, mode = collect_targets(source)
        rewritten = {x["id"]:f"Versi baru {x['id']}." for x in targets}
        result = apply_rewrites(source, targets, rewritten, mode)
        self.assertEqual(result["scenes"][0]["text"],"Versi baru scene:1.")
        self.assertEqual(result["scenes"][1]["text"],"Versi baru scene:2.")
        self.assertEqual(result["visual_style"],original["visual_style"])
        self.assertEqual(result["scenes"][0]["title"],original["scenes"][0]["title"])
        self.assertEqual(result["scenes"][0]["shot"],original["scenes"][0]["shot"])

    def test_package_includes_script_and_storyboard_narration(self):
        package={"script":"Naskah penuh.","storyboard":[{"scene":1,"narration":"Narasi scene.","visual_prompt":"Jangan ubah."}],"research":{"source_urls":["https://example.org"]}}
        targets,mode=collect_targets(package)
        result=apply_rewrites(package,targets,{"script":"Naskah baru.","storyboard:1":"Narasi baru."},mode)
        self.assertEqual(result["script"],"Naskah baru.")
        self.assertEqual(result["storyboard"][0]["narration"],"Narasi baru.")
        self.assertEqual(result["storyboard"][0]["visual_prompt"],"Jangan ubah.")
        self.assertEqual(result["research"]["source_urls"],["https://example.org"])

    def test_rejects_missing_ids(self):
        targets,mode=collect_targets({"scenes":[{"scene":1,"text":"Narasi."}]})
        with self.assertRaises(ValueError):
            apply_rewrites({"scenes":[{"scene":1,"text":"Narasi."}]},targets,{},mode)

if __name__=="__main__":
    unittest.main()
