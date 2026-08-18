from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "package_zephyr_bundle.py"
SPEC = importlib.util.spec_from_file_location("package_zephyr_bundle", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class ZephyrBundleMemoryTests(unittest.TestCase):
    @staticmethod
    def memory_map(end: int) -> str:
        return (
            f"  0x{package.RAM_START:016x} _image_ram_start = .\n"
            f"  0x{end:016x} _image_ram_end = .\n"
        )

    def test_accepts_ram_extent_with_required_headroom(self) -> None:
        end = package.RAM_START + package.RAM_BYTES - \
            package.MINIMUM_RAM_HEADROOM
        memory = package.linked_ram_usage(self.memory_map(end))
        self.assertEqual(memory["used_bytes"],
                         package.RAM_BYTES - package.MINIMUM_RAM_HEADROOM)
        self.assertEqual(memory["headroom_bytes"],
                         package.MINIMUM_RAM_HEADROOM)

    def test_rejects_ram_extent_below_headroom_gate(self) -> None:
        end = package.RAM_START + package.RAM_BYTES - \
            package.MINIMUM_RAM_HEADROOM + 1
        with self.assertRaisesRegex(ValueError, "below the required"):
            package.linked_ram_usage(self.memory_map(end))

    def test_rejects_missing_duplicate_and_out_of_range_symbols(self) -> None:
        with self.assertRaisesRegex(ValueError, "not unique"):
            package.linked_ram_usage("")
        valid = self.memory_map(package.RAM_START + 1)
        with self.assertRaisesRegex(ValueError, "not unique"):
            package.linked_ram_usage(valid + valid.splitlines()[0] + "\n")
        invalid_origin = valid.replace(
            f"0x{package.RAM_START:016x}",
            f"0x{package.RAM_START + 4:016x}", 1)
        with self.assertRaisesRegex(ValueError, "is invalid"):
            package.linked_ram_usage(invalid_origin)


if __name__ == "__main__":
    unittest.main()
