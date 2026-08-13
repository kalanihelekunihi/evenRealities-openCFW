#!/usr/bin/env python3
"""Exercise the production-excluded G2 WSF assert/trace candidates."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "components/shared/cordio"
SOURCE = CANDIDATE / "runtime_cordio_wsf_assert_trace_candidate.c"


class CordioWsfAssertTraceCandidateTests(unittest.TestCase):
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
                    "-o", str(Path(directory) / "assert-trace.o"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

    def test_trace_hook_and_fatal_paths(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdarg.h>
            #include <stdint.h>
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_wsf_assert_trace_candidate.h"

            open_cfw_cordio_wsf_assert_hook_candidate_t
                open_cfw_cordio_wsf_assert_hook_candidate;
            static unsigned structured, backend, internal, resets, prints;
            static char first_print[64];

            uint32_t open_cfw_cordio_wsf_logger_flags_candidate(void) {
                return 7U;
            }
            void open_cfw_cordio_wsf_assert_structured_log_candidate(
                const char *file, uint16_t line
            ) { assert(file == NULL || strcmp(file, "caller.c") == 0); assert(line == 12); structured++; }
            void open_cfw_cordio_wsf_assert_backend_log_candidate(
                uint32_t mask, const char *file, uint16_t line
            ) { assert(mask == 0x04800000U); assert(file == NULL || strcmp(file, "caller.c") == 0); assert(line == 12); backend++; }
            void open_cfw_cordio_wsf_assert_internal_log_candidate(
                const char *expression, const char *function, uint32_t line
            ) { assert(strcmp(expression, "pFile") == 0); assert(strcmp(function, "WsfAssert") == 0); assert(line == 44); internal++; }
            void open_cfw_cordio_wsf_assert_reset_candidate(void) {
                assert(internal == 1 && structured == 1 && backend == 1);
                resets++;
                exit(0);
            }
            void open_cfw_cordio_wsf_trace_vsprintf_candidate(
                char *buffer, const char *format, va_list arguments
            ) { (void)vsprintf(buffer, format, arguments); }
            uint32_t open_cfw_cordio_wsf_trace_debug_printf_candidate(
                const char *format, ...
            ) {
                if (prints++ == 0) (void)snprintf(first_print, sizeof(first_print), "%s", format);
                return (uint32_t)strlen(format);
            }
            static void hook(const char *expression, const char *function, uint32_t line) {
                assert(strcmp(expression, "pFile") == 0);
                assert(strcmp(function, "WsfAssert") == 0);
                assert(line == 44 && structured == 1 && backend == 1);
                exit(0);
            }

            int main(int argc, char **argv) {
                assert(argc == 2);
                if (strcmp(argv[1], "trace") == 0) {
                    open_cfw_cordio_wsf_trace_candidate("value=%u", 7U);
                    assert(prints == 2 && strcmp(first_print, "value=7") == 0);
                    return 0;
                }
                if (strcmp(argv[1], "hook") == 0) {
                    open_cfw_cordio_wsf_assert_hook_candidate = hook;
                    open_cfw_cordio_wsf_assert_candidate(NULL, 12);
                }
                if (strcmp(argv[1], "fatal") == 0) {
                    open_cfw_cordio_wsf_assert_hook_candidate = NULL;
                    open_cfw_cordio_wsf_assert_candidate(NULL, 12);
                }
                return 99;
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
            for mode in ("trace", "hook", "fatal"):
                subprocess.run([str(binary), mode], check=True)


if __name__ == "__main__":
    unittest.main()
