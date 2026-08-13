import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_conversate_controller.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_conversate_controller", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ConversateControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = MODULE.analyze()

    def test_complete_surface(self):
        surface = self.report["surface"]
        self.assertEqual((surface["linked_functions"], surface["restored_functions"]), (12, 3))
        self.assertEqual((surface["body_bytes"], surface["physical_bytes"], surface["noncode_bytes"]), (2250, 2628, 378))
        self.assertEqual((surface["direct_body_calls"], surface["internal_direct_body_calls"], surface["external_direct_body_calls"]), (152, 13, 139))
        self.assertEqual((surface["indirect_body_calls"], surface["strict_interior_ingress"]), (0, 0))
        self.assertEqual((surface["stored_aligned_function_entry_pointers"], surface["unaligned_exact_entry_byte_windows"]), (3, 1))

    def test_provider_boundary(self):
        providers = self.report["provider_boundary"]
        self.assertEqual(sum(providers[key] for key in (
            "easylogger_calls", "iar_dlib_calls", "cmsis_freertos_calls",
            "lvgl_calls", "nanopb_calls", "source_owned_eabi_calls",
            "cmbacktrace_calls", "first_party_calls",
        )), 139)
        self.assertEqual(providers["cmbacktrace_selected_compatibility_commit"], "73714489f9d8af130aacb515586b397b604a5768")
        self.assertIsNone(providers["cmbacktrace_exact_historical_commit"])
        self.assertFalse(providers["new_version_discriminator"])

    def test_no_embedded_dependency_or_production_claim(self):
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
