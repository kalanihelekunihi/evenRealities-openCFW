from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_defaults_pair.c"
HEADER = ROOT / "components/shared/nanopb/runtime_nanopb_defaults_pair.h"
HARNESS = ROOT / "tests/fixtures/runtime_nanopb_defaults_pair_host.c"

SOURCE_PIN = (
    6894,
    "fd5f03e33984a341d532f5eab0db952b3a5c11300a33851b53e33beb192eaaf4",
)
HEADER_PIN = (
    867,
    "fd49a5df94ff89c5c0032f72c304f5efd4ec0bf4ecd5908742c6ef0810e51ab9",
)


def pin(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


class NanopbDefaultsPairRuntimeTests(unittest.TestCase):
    def test_source_and_header_are_pinned(self) -> None:
        self.assertEqual(pin(SOURCE), SOURCE_PIN)
        self.assertEqual(pin(HEADER), HEADER_PIN)

    def test_host_semantics_cover_defaults_and_failure_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            executable = Path(raw) / "defaults-pair"
            completed = subprocess.run(
                [
                    "/usr/bin/clang",
                    "-std=c11",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-I",
                    str(ROOT / "components/shared/nanopb"),
                    str(SOURCE),
                    str(HARNESS),
                    "-o",
                    str(executable),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            executed = subprocess.run(
                [str(executable)], check=False, capture_output=True, text=True
            )
            self.assertEqual(executed.returncode, 0, executed.stderr)

    def test_target_selectors_have_exact_relocation_shapes(self) -> None:
        expected = {
            0: (
                "open_cfw_nanopb_field_set_to_default",
                256,
                (
                    "open_cfw_nanopb_field_iter_begin_extension",
                    "open_cfw_nanopb_message_set_to_defaults",
                    "open_cfw_nanopb_field_iter_begin",
                    "open_cfw_nanopb_message_set_to_defaults",
                ),
            ),
            1: (
                "open_cfw_nanopb_message_set_to_defaults",
                158,
                (
                    "open_cfw_nanopb_istream_from_buffer",
                    "open_cfw_nanopb_decode_tag",
                    "open_cfw_nanopb_field_iter_next",
                    "open_cfw_nanopb_field_set_to_default",
                    "open_cfw_nanopb_decode_field",
                    "open_cfw_nanopb_decode_tag",
                ),
            ),
        }
        with tempfile.TemporaryDirectory() as raw:
            temporary = Path(raw)
            for selector, (function, size, symbols) in expected.items():
                with self.subTest(selector=selector):
                    object_path = temporary / f"selector-{selector}.o"
                    completed = subprocess.run(
                        [
                            "/usr/bin/clang",
                            "--target=thumbv7em-none-eabi",
                            "-mthumb",
                            "-O2",
                            "-ffreestanding",
                            "-fno-jump-tables",
                            "-fomit-frame-pointer",
                            "-fno-builtin",
                            "-mno-unaligned-access",
                            "-fno-unwind-tables",
                            "-fno-asynchronous-unwind-tables",
                            "-fropi",
                            "-ffunction-sections",
                            "-fdata-sections",
                            "-Wall",
                            "-Wextra",
                            "-Werror",
                            "-fno-ident",
                            f"-DOPEN_CFW_NANOPB_DEFAULTS_SELECTION={selector}",
                            "-I",
                            str(ROOT / "components/shared/nanopb"),
                            "-c",
                            str(SOURCE),
                            "-o",
                            str(object_path),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    sections = subprocess.run(
                        ["/usr/bin/objdump", "-h", str(object_path)],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                    section_size = next(
                        line.split()[2]
                        for line in sections.splitlines()
                        if f".text.{function}" in line
                    )
                    self.assertEqual(section_size, f"{size:08x}")
                    relocations = subprocess.run(
                        ["/usr/bin/objdump", "-r", str(object_path)],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                    observed = tuple(
                        line.split()[-1]
                        for line in relocations.splitlines()
                        if "R_ARM_THM_CALL" in line
                    )
                    self.assertEqual(observed, symbols)


if __name__ == "__main__":
    unittest.main()
