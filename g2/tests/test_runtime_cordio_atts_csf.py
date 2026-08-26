#!/usr/bin/env python3
"""Exercise the production-routed G2 Cordio ATTS CSF source."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_csf.c"


class CordioAttsCsfSourceTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_atts_csf.h"

            struct open_cfw_cordio_atts_csf_control_block
                open_cfw_cordio_atts_csf_control_block;
            static unsigned pending, callbacks;
            static uint8_t callback_conn, callback_state, callback_csf;

            void open_cfw_cordio_atts_check_pending_database_hash_read_response(void) {
                pending++;
            }
            static void callback(uint8_t conn, uint8_t state, uint8_t *csf) {
                callbacks++; callback_conn = conn; callback_state = state;
                callback_csf = *csf;
            }

            int main(void) {
                uint8_t packet[16] = {0};
                uint8_t value, output = 0;
                memset(&open_cfw_cordio_atts_csf_control_block, 0,
                    sizeof(open_cfw_cordio_atts_csf_control_block));
                open_cfw_cordio_atts_csf_register(callback);

                open_cfw_cordio_atts_csf_control_block.records[0].change_aware_state = 2;
                open_cfw_cordio_atts_csf_set_hash_update_status(1);
                assert(open_cfw_cordio_atts_csf_get_hash_update_status() == 1);
                assert(open_cfw_cordio_atts_csf_control_block.records[0].change_aware_state == 1);
                open_cfw_cordio_atts_csf_set_hash_update_status(0);
                assert(pending == 1);

                value = 1;
                open_cfw_cordio_atts_csf_connection_open(1, 3, &value);
                assert(!open_cfw_cordio_atts_csf_is_client_change_aware(1, 0x20));
                assert(open_cfw_cordio_atts_csf_is_client_change_aware(1, 0x12));
                assert(open_cfw_cordio_atts_csf_act_client_state(0, 0x40, packet) == 0x12);
                open_cfw_cordio_atts_csf_control_block.records[0].change_aware_state = 3;
                assert(open_cfw_cordio_atts_csf_act_client_state(0, 0x0A, packet) == 0x12);
                assert(open_cfw_cordio_atts_csf_control_block.records[0].change_aware_state == 1);
                assert(open_cfw_cordio_atts_csf_act_client_state(0, 0x0A, packet) == 0);
                assert(callbacks == 1 && callback_conn == 1 && callback_state == 0);

                open_cfw_cordio_atts_csf_control_block.is_hash_updating = 1;
                open_cfw_cordio_atts_csf_control_block.records[0].change_aware_state = 3;
                packet[13] = 0x2A; packet[14] = 0x2B;
                assert(open_cfw_cordio_atts_csf_act_client_state(0, 0x08, packet) == 0);
                assert(open_cfw_cordio_atts_csf_control_block.records[0].change_aware_state == 2);

                value = 6;
                assert(open_cfw_cordio_atts_csf_write_features(1, 0, 2, &value) == 0x0D);
                assert(open_cfw_cordio_atts_csf_write_features(1, 0, 1, &value) == 0);
                assert(callbacks == 2 && callback_csf == 7);
                value = 0;
                assert(open_cfw_cordio_atts_csf_write_features(1, 0, 1, &value) == 0x13);
                open_cfw_cordio_atts_csf_get_features(1, &output, 1);
                assert(output == 7);

                open_cfw_cordio_atts_csf_control_block.records[1].change_aware_state = 2;
                open_cfw_cordio_atts_csf_control_block.records[2].change_aware_state = 3;
                open_cfw_cordio_atts_csf_set_clients_change_awareness_state(0, 0);
                assert(open_cfw_cordio_atts_csf_control_block.records[1].change_aware_state == 1);
                assert(open_cfw_cordio_atts_csf_control_block.records[2].change_aware_state == 0);
                assert(open_cfw_cordio_atts_csf_get_change_aware_state(3) == 0);
                open_cfw_cordio_atts_csf_connection_open(2, 3, 0);
                assert(open_cfw_cordio_atts_csf_get_change_aware_state(2) == 0);

                /* G2's vendor augmentation rejects DM_CONN_ID_NONE without
                 * indexing before the three-record table. */
                output = 0xA5;
                assert(!open_cfw_cordio_atts_csf_is_client_change_aware(0, 0x12));
                open_cfw_cordio_atts_csf_connection_open(0, 3, &value);
                assert(open_cfw_cordio_atts_csf_write_features(0, 0, 1, 0)
                    == 0x0E);
                open_cfw_cordio_atts_csf_get_features(0, &output, 1);
                assert(output == 0xA5);
                assert(open_cfw_cordio_atts_csf_get_change_aware_state(0) == 3);
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
            "SET_HASH", "GET_HASH", "IS_AWARE", "ACT_STATE", "SET_STATE",
            "CONN_OPEN", "REGISTER", "WRITE", "GET_FEATURES", "GET_STATE",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_CSF_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_CSF_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
