"""Import the shared humanizer from the repository's hyphenated script directory."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_source = Path(__file__).resolve().parents[1] / "peta-sunyi" / "humanize_narration.py"
_spec = spec_from_file_location("_peta_sunyi_humanizer_impl", _source)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load Peta Sunyi humanizer at {_source}")
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)
collect_targets = _module.collect_targets
apply_rewrites = _module.apply_rewrites
