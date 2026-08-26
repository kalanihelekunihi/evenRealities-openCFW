#!/usr/bin/env python3
"""Exercise the production-routed G2 Cordio ATT CCC implementation."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_ccc.c"


class CordioAttsCccSourceTests(unittest.TestCase):
    def test_host_behavior_and_g2_validation(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_atts_ccc.h"

            struct open_cfw_cordio_atts_ccc_control_block
                open_cfw_cordio_atts_ccc_control_block;
            open_cfw_cordio_atts_ccc_main_callback_t
                open_cfw_cordio_atts_ccc_atts_main_callback;
            static unsigned allocations, frees, callbacks;
            static uint8_t security_level = 2;
            static struct open_cfw_cordio_atts_ccc_event last_event;

            void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t n) {
                allocations++;
                return calloc(1, n);
            }
            void open_cfw_cordio_wsf_buffer_free_candidate(void *p) {
                frees++;
                free(p);
            }
            uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t id) {
                (void)id;
                return security_level;
            }
            static void callback(struct open_cfw_cordio_atts_ccc_event *event) {
                callbacks++;
                last_event = *event;
            }

            int main(void) {
                struct open_cfw_cordio_atts_ccc_setting settings[2] = {
                    {0x13, 2, 0, 0}, {0x25, 1, 2, 0}
                };
                uint16_t initial[2] = {2, 0};
                uint8_t value[2] = {0};

                memset(&open_cfw_cordio_atts_ccc_control_block, 0,
                    sizeof(open_cfw_cordio_atts_ccc_control_block));
                open_cfw_cordio_atts_ccc_register(2, settings, callback);
                assert(open_cfw_cordio_atts_ccc_atts_main_callback
                    == open_cfw_cordio_atts_ccc_main_callback);
                assert(open_cfw_cordio_atts_ccc_table_length() == 2);

                open_cfw_cordio_atts_ccc_initialize_table(1, initial);
                assert(allocations == 1 && callbacks == 1);
                assert(last_event.header.parameter == 1);
                assert(last_event.header.event == 0x14);
                assert(last_event.index == 0 && last_event.handle == 0);
                assert(last_event.value == 2);
                assert(open_cfw_cordio_atts_ccc_get(1, 0) == 2);

                assert(open_cfw_cordio_atts_ccc_main_callback(
                    1, 5, 0x13, value) == 0);
                assert(value[0] == 2 && value[1] == 0);
                value[0] = 1;
                assert(open_cfw_cordio_atts_ccc_write_value(
                    1, 0x13, value) == 0x80);
                value[0] = 0;
                assert(open_cfw_cordio_atts_ccc_write_value(
                    1, 0x13, value) == 0);
                assert(callbacks == 2 && last_event.handle == 0x13);
                assert(open_cfw_cordio_atts_ccc_read_value(
                    1, 0x9999, value) == 0x0A);

                open_cfw_cordio_atts_ccc_set(1, 1, 1);
                security_level = 1;
                assert(open_cfw_cordio_atts_ccc_enabled(1, 1) == 0);
                security_level = 2;
                assert(open_cfw_cordio_atts_ccc_enabled(1, 1) == 1);

                /* G2 validation prevents table[-1] and out-of-range free. */
                assert(open_cfw_cordio_atts_ccc_allocate_table(0) == 0);
                assert(open_cfw_cordio_atts_ccc_get_table(0) == 0);
                open_cfw_cordio_atts_ccc_initialize_table(0, initial);
                assert(open_cfw_cordio_atts_ccc_read_value(0, 0x13, value)
                    == 0x11);
                open_cfw_cordio_atts_ccc_clear_table(0);
                open_cfw_cordio_atts_ccc_clear_table(4);
                assert(allocations == 1 && frees == 0);
                open_cfw_cordio_atts_ccc_clear_table(1);
                assert(frees == 1 && open_cfw_cordio_atts_ccc_get(1, 0) == 0);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "harness.c"
            binary = Path(directory) / "harness"
            src.write_text(harness)
            subprocess.run([
                "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE_DIR), str(src), str(SOURCE), "-o", str(binary),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(binary)], check=True)

    def test_isolated_arm_leaves(self) -> None:
        selectors = (
            "CALLBACK", "ALLOCATE", "GET_TABLE", "FREE", "READ", "WRITE",
            "MAIN", "REGISTER", "INITIALIZE", "CLEAR", "GET", "SET",
            "ENABLED", "LENGTH",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_CCC_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_CCC_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
