import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/peta-sunyi/generate_i2v.py"
spec = importlib.util.spec_from_file_location("generate_i2v", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FakeQuota:
    def __init__(self, remaining=1000, overquota_used=0):
        self.base = 2400
        self.remaining = remaining
        self.overquota_used = overquota_used
        self.resets_at = None


class PetaSunyiI2VGuardrailTests(unittest.TestCase):
    def base_config(self):
        return {
            "episode_id": "test-episode",
            "motion_generation": {
                "scenes": [
                    {"shot": "01A", "image_asset": "peta-sunyi-01A.jpg",
                     "output": "scene-01.mp4", "prompt": "Slowly turn the flashlight toward the door.",
                     "estimated_gpu_seconds": 60}
                ]
            }
        }

    def test_output_dimensions_follow_episode_format(self):
        self.assertEqual(module.output_dimensions({"motion_generation": {"output_format": "9:16"}}), (1080, 1920))
        self.assertEqual(module.output_dimensions({"motion_generation": {"output_format": "16:9"}}), (1920, 1080))

    def test_rejects_unknown_output_format(self):
        with self.assertRaises(ValueError):
            module.output_dimensions({"motion_generation": {"output_format": "4:3"}})

    def test_valid_plan(self):
        jobs = module.validate_plan(self.base_config())
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["shot"], "01A")

    def test_rejects_more_than_three_clips(self):
        config = self.base_config()
        config["motion_generation"]["scenes"] *= 4
        with self.assertRaises(ValueError):
            module.validate_plan(config)

    def test_rejects_path_traversal(self):
        config = self.base_config()
        config["motion_generation"]["scenes"][0]["image_asset"] = "../secret.png"
        with self.assertRaises(ValueError):
            module.validate_plan(config)

    def test_rejects_estimate_over_run_cap(self):
        config = self.base_config()
        config["motion_generation"]["scenes"][0]["estimated_gpu_seconds"] = 241
        with self.assertRaises(ValueError):
            module.validate_plan(config)

    def test_quota_reserve_is_enforced(self):
        module.assert_quota_safe(FakeQuota(remaining=300), 180, 60)
        with self.assertRaises(RuntimeError):
            module.assert_quota_safe(FakeQuota(remaining=239), 180, 60)

    def test_daily_internal_cap_is_enforced(self):
        module.assert_daily_budget_available(
            {"used_seconds": 120, "reserved_seconds": 0, "jobs": []}, 120
        )
        with self.assertRaises(RuntimeError):
            module.assert_daily_budget_available(
                {"used_seconds": 180, "reserved_seconds": 0, "jobs": []}, 61
            )

    def test_paid_overquota_usage_fails_closed(self):
        with self.assertRaises(RuntimeError):
            module.assert_quota_safe(FakeQuota(remaining=1000, overquota_used=1), 60, 60)


if __name__ == "__main__":
    unittest.main()
