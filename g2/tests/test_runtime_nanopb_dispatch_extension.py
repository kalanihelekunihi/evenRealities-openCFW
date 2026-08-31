from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_dispatch_extension.c"
HEADER = ROOT / "components/shared/nanopb/runtime_nanopb_dispatch_extension.h"
HARNESS = ROOT / "tests/fixtures/runtime_nanopb_dispatch_extension_host.c"
SOURCE_PIN = (4_499, "610c8d8e64f87f67aeb9bd175800f3b43661a2bbe9f8d557aa76cc5b9e11ee67")
HEADER_PIN = (1_560, "f6918d0d89b223e9ad33601de800931a73a0c9ad5ac66177ea83c435441c2ec8")


def pin(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


class NanopbDispatchExtensionRuntimeTests(unittest.TestCase):
    def test_source_and_header_are_pinned(self) -> None:
        self.assertEqual(pin(SOURCE), SOURCE_PIN)
        self.assertEqual(pin(HEADER), HEADER_PIN)

    def test_host_semantics_cover_dispatch_extension_and_failures(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            executable = Path(raw) / "dispatch-extension"
            completed = subprocess.run(
                [
                    "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                    "-Werror", "-I", str(ROOT / "components/shared/nanopb"),
                    str(SOURCE), str(HARNESS), "-o", str(executable),
                ],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            executed = subprocess.run(
                [str(executable)], check=False, capture_output=True, text=True
            )
            self.assertEqual(executed.returncode, 0, executed.stderr)

    def test_target_selectors_have_expected_relocation_shapes(self) -> None:
        expected = {
            0: ("open_cfw_nanopb_decode_field", (
                "open_cfw_nanopb_decode_callback_field",
                "open_cfw_nanopb_decode_static_field",
                "open_cfw_nanopb_decode_pointer_field",
            )),
            1: ("open_cfw_nanopb_default_extension_decoder", (
                "open_cfw_nanopb_field_iter_begin_extension",
                "open_cfw_nanopb_decode_field",
            )),
            2: ("open_cfw_nanopb_decode_extension", (
                "open_cfw_nanopb_default_extension_decoder",
            )),
        }
        with tempfile.TemporaryDirectory() as raw:
            temporary = Path(raw)
            for selector, (function, symbols) in expected.items():
                with self.subTest(selector=selector):
                    object_path = temporary / f"selector-{selector}.o"
                    completed = subprocess.run(
                        [
                            "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                            "-mthumb", "-O2", "-ffreestanding",
                            "-fno-jump-tables", "-fomit-frame-pointer",
                            "-fno-builtin", "-mno-unaligned-access",
                            "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                            "-fropi", "-ffunction-sections", "-fdata-sections",
                            "-Wall", "-Wextra", "-Werror", "-fno-ident",
                            f"-DOPEN_CFW_NANOPB_DISPATCH_SELECTION={selector}",
                            "-I", str(ROOT / "components/shared/nanopb"),
                            "-c", str(SOURCE), "-o", str(object_path),
                        ],
                        check=False, capture_output=True, text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    relocations = subprocess.run(
                        ["/usr/bin/objdump", "-r", str(object_path)],
                        check=True, capture_output=True, text=True,
                    ).stdout
                    section = f"RELOCATION RECORDS FOR [.__text.{function}]"
                    if section not in relocations:
                        section = f"RELOCATION RECORDS FOR [.text.{function}]"
                    block = relocations.split(section, 1)[1].split("\n\n", 1)[0]
                    observed = tuple(
                        line.split()[-1]
                        for line in block.splitlines()
                        if "R_ARM_THM_CALL" in line or "R_ARM_THM_JUMP24" in line
                    )
                    self.assertEqual(observed, symbols)


if __name__ == "__main__":
    unittest.main()
