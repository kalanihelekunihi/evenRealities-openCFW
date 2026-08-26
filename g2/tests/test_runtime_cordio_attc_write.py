#!/usr/bin/env python3
"""Exercise the production-routed G2 Cordio ATT client write unit."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_attc_write.c"


class CordioAttcWriteSourceTests(unittest.TestCase):
    def test_host_response_command_prepare_and_execute_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_attc_write.h"

            static int fail_allocate;
            static uint16_t allocated_length;
            static uint8_t *allocation;
            static int sends;
            static uint8_t sent_connection;
            static uint16_t sent_handle;
            static uint8_t sent_message;
            static uint8_t sent_continuing;
            static union open_cfw_cordio_attc_packet_parameter *sent_packet;

            void *open_cfw_cordio_att_message_allocate(uint16_t length) {
                allocated_length = length;
                if (fail_allocate) return NULL;
                allocation = calloc(1, length);
                return allocation;
            }

            void open_cfw_cordio_attc_send_message(
                uint8_t connection_id, uint16_t handle, uint8_t message_id,
                union open_cfw_cordio_attc_packet_parameter *packet,
                uint8_t continuing
            ) {
                sends++;
                sent_connection = connection_id;
                sent_handle = handle;
                sent_message = message_id;
                sent_packet = packet;
                sent_continuing = continuing;
            }

            static void reset(void) {
                free(allocation);
                allocation = NULL;
                allocated_length = 0;
                sends = 0;
                fail_allocate = 0;
            }

            int main(void) {
                struct open_cfw_cordio_attc_connection_control_block ccb;
                struct open_cfw_cordio_att_event event;
                uint8_t response[12] = {0};
                uint8_t value[3] = {0xAA, 0xBB, 0xCC};
                uint8_t *bytes;

                memset(&ccb, 0, sizeof(ccb));
                memset(&event, 0, sizeof(event));
                ccb.outstanding_request.header.status = 1;
                ccb.outstanding_parameters.prepare.length = 0;
                event.value = response;
                event.value_length = 9;
                open_cfw_cordio_attc_process_prepare_write_response(
                    &ccb, 9, response, &event
                );
                assert(ccb.outstanding_request.header.status == 0);
                assert(event.value == response + 4);
                assert(event.value_length == 5);

                ccb.outstanding_request.header.status = 1;
                ccb.outstanding_parameters.prepare.length = 2;
                event.value = response;
                event.value_length = 6;
                open_cfw_cordio_attc_process_prepare_write_response(
                    &ccb, 6, response, &event
                );
                assert(ccb.outstanding_request.header.status == 1);

                open_cfw_cordio_attc_write_command(2, 0x1234, 3, value);
                assert(allocated_length == 14 && sends == 1);
                assert(sent_connection == 2 && sent_handle == 0x1234);
                assert(sent_message == 10 && sent_continuing == 0);
                assert(sent_packet->length == 6);
                bytes = (uint8_t *)sent_packet;
                assert(bytes[8] == 0x52 && bytes[9] == 0x34 && bytes[10] == 0x12);
                assert(memcmp(bytes + 11, value, 3) == 0);
                reset();

                open_cfw_cordio_attc_prepare_write_request(
                    3, 0x5678, 0x0123, 3, value, 0, 0
                );
                assert(sends == 1 && sent_message == 11);
                assert(sent_connection == 3 && sent_handle == 0x5678);
                assert(sent_continuing == 0);
                bytes = (uint8_t *)sent_packet;
                assert(bytes[8] == 0x16 && bytes[9] == 0x78 && bytes[10] == 0x56);
                assert(sent_packet->prepare->length == 3);
                assert(sent_packet->prepare->offset == 0x0123);
                assert(sent_packet->prepare->value == bytes + 13);
                assert(memcmp(bytes + 13, value, 3) == 0);
                reset();

                open_cfw_cordio_attc_prepare_write_request(
                    1, 0x1111, 7, 3, value, 1, 1
                );
                assert(sends == 1 && sent_continuing == 1);
                assert(sent_packet->prepare->value == value);
                assert(sent_packet->prepare->length == 3);
                assert(sent_packet->prepare->offset == 7);
                reset();

                open_cfw_cordio_attc_execute_write_request(2, 1);
                assert(allocated_length == 10 && sends == 1);
                assert(sent_connection == 2 && sent_handle == 0);
                assert(sent_message == 12 && sent_continuing == 0);
                assert(sent_packet->length == 2);
                bytes = (uint8_t *)sent_packet;
                assert(bytes[8] == 0x18 && bytes[9] == 1);
                reset();

                fail_allocate = 1;
                open_cfw_cordio_attc_write_command(1, 2, 3, value);
                open_cfw_cordio_attc_prepare_write_request(
                    1, 2, 0, 3, value, 0, 0
                );
                open_cfw_cordio_attc_execute_write_request(1, 1);
                assert(sends == 0);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            harness_path = temp / "harness.c"
            executable = temp / "attc-write-test"
            harness_path.write_text(harness)
            subprocess.run(
                [
                    "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE_DIR), str(SOURCE), str(harness_path),
                    "-o", str(executable),
                ],
                check=True,
            )
            subprocess.run([str(executable)], check=True)

    def test_complete_and_isolated_cortex_m55_builds(self) -> None:
        selectors = [
            "PREP_ALLOC", "PROCESS_PREP_RSP", "COMMAND",
            "PREPARE_REQUEST", "EXECUTE_REQUEST",
        ]
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            subprocess.run(
                [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE_DIR), "-c", str(SOURCE),
                    "-o", str(temp / "all.o"),
                ],
                check=True,
            )
            for selector in selectors:
                subprocess.run(
                    [
                        "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                        "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                        "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                        "-I", str(SOURCE_DIR),
                        f"-DOPEN_CFW_ATTC_WRITE_{selector}_ONLY=1",
                        "-c", str(SOURCE),
                        "-o", str(temp / f"{selector}.o"),
                    ],
                    check=True,
                )

    def test_source_has_no_placeholder_or_host_dependency(self) -> None:
        source = SOURCE.read_text()
        self.assertNotIn("TODO", source)
        self.assertNotIn("abort(", source)
        self.assertNotIn("stdio.h", source)
        self.assertNotIn("stdlib.h", source)


if __name__ == "__main__":
    unittest.main()
