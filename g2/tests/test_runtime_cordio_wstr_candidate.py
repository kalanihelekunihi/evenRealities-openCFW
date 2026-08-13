#!/usr/bin/env python3
"""Exercise the production-excluded G2 Cordio WSF string helpers."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "components/shared/cordio"
SOURCE = CANDIDATE / "runtime_cordio_wstr_candidate.c"


class CordioWstrCandidateTests(unittest.TestCase):
    def test_arm_compile_gate(self) -> None:
        clang = subprocess.run(
            ["sh", "-c", "command -v clang"],
            check=False,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not clang:
            self.skipTest("clang unavailable")
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [
                    clang,
                    "-target", "arm-none-eabi",
                    "-mcpu=cortex-m4",
                    "-mthumb",
                    "-ffreestanding",
                    "-std=c11",
                    "-Wall", "-Wextra", "-Werror",
                    f"-I{CANDIDATE}",
                    "-c", str(SOURCE),
                    "-o", str(Path(directory) / "wstr.o"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

    def test_reverse_copy_and_in_place_reverse(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_wstr_candidate.h"

            int main(void) {
                const uint8_t source[] = {1, 2, 3, 4, 5};
                uint8_t destination[] = {9, 9, 9, 9, 9};
                uint8_t even[] = {1, 2, 3, 4};
                uint8_t one[] = {7};

                open_cfw_cordio_wstr_reverse_copy_candidate(
                    destination, source, sizeof(source)
                );
                assert(memcmp(destination, (uint8_t[]){5, 4, 3, 2, 1}, 5) == 0);
                open_cfw_cordio_wstr_reverse_candidate(even, sizeof(even));
                assert(memcmp(even, (uint8_t[]){4, 3, 2, 1}, 4) == 0);
                open_cfw_cordio_wstr_reverse_candidate(one, sizeof(one));
                assert(one[0] == 7);
                open_cfw_cordio_wstr_reverse_copy_candidate(destination, source, 0);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "harness.c"
            binary = Path(directory) / "harness"
            source.write_text(harness)
            subprocess.run(
                [
                    "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    f"-I{CANDIDATE}", str(source), str(SOURCE), "-o", str(binary),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
