#!/usr/bin/env python3
"""Exercise the production-routed G2 Cordio ATT client read unit."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_attc_read.c"


class CordioAttcReadSourceTests(unittest.TestCase):
    def test_host_response_and_all_request_behaviors(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_attc_read.h"

            static uint8_t *allocation;
            static uint16_t allocated_length;
            static int sends;
            static uint8_t sent_connection, sent_message, sent_continuing;
            static uint16_t sent_handle;
            static union open_cfw_cordio_attc_packet_parameter *sent_packet;

            void *open_cfw_cordio_att_message_allocate(uint16_t length) {
                allocated_length = length;
                allocation = calloc(1, length);
                return allocation;
            }
            void open_cfw_cordio_attc_send_message(
                uint8_t connection_id, uint16_t handle, uint8_t message_id,
                union open_cfw_cordio_attc_packet_parameter *packet,
                uint8_t continuing
            ) {
                sends++;
                sent_connection = connection_id; sent_handle = handle;
                sent_message = message_id; sent_packet = packet;
                sent_continuing = continuing;
            }
            static void reset(void) {
                free(allocation); allocation = NULL; allocated_length = 0;
                sends = 0;
            }

            int main(void) {
                struct open_cfw_cordio_attc_connection_control_block ccb;
                struct open_cfw_cordio_attc_main_control_block main_cb;
                struct open_cfw_cordio_att_event event;
                uint8_t packet[32] = {0};
                uint8_t value[3] = {0xA1, 0xB2, 0xC3};
                uint16_t handles[2] = {0x1234, 0x5678};
                uint8_t *bytes;
                memset(&ccb, 0, sizeof(ccb));
                memset(&main_cb, 0, sizeof(main_cb));
                memset(&event, 0, sizeof(event));

                ccb.outstanding_request.header.status = 1;
                ccb.outstanding_parameters.handles.start_handle = 1;
                ccb.outstanding_parameters.handles.end_handle = 9;
                packet[9] = 1; packet[11] = 3;
                packet[13] = 5; packet[15] = 9;
                open_cfw_cordio_attc_process_find_by_type_response(
                    &ccb, 9, packet, &event
                );
                assert(event.header.status == 0);
                assert(ccb.outstanding_request.header.status == 0);

                memset(packet, 0, sizeof(packet));
                event.header.status = 0;
                ccb.outstanding_request.header.status = 1;
                ccb.outstanding_parameters.handles.start_handle = 1;
                ccb.outstanding_parameters.handles.end_handle = 20;
                packet[9] = 4; packet[11] = 7;
                open_cfw_cordio_attc_process_find_by_type_response(
                    &ccb, 5, packet, &event
                );
                assert(ccb.outstanding_parameters.handles.start_handle == 8);
                assert(ccb.outstanding_request.handle == 8);

                event.header.status = 0;
                open_cfw_cordio_attc_process_find_by_type_response(
                    &ccb, 3, packet, &event
                );
                assert(event.header.status == 0x13);

                ccb.main = &main_cb; ccb.slot = 2;
                main_cb.bearer[2].mtu = 23;
                ccb.outstanding_request.header.status = 1;
                ccb.outstanding_parameters.offset.offset = 5;
                event.value_length = 7;
                open_cfw_cordio_attc_process_read_long_response(
                    &ccb, 23, packet, &event
                );
                assert(ccb.outstanding_parameters.offset.offset == 12);
                open_cfw_cordio_attc_process_read_long_response(
                    &ccb, 22, packet, &event
                );
                assert(ccb.outstanding_request.header.status == 0);

                open_cfw_cordio_attc_find_by_type_value_request(
                    2, 1, 9, 0x2800, 3, value, 1
                );
                bytes = (uint8_t *)sent_packet;
                assert(allocated_length == 18 && sends == 1);
                assert(sent_packet->handles.length == 10);
                assert(sent_packet->handles.start_handle == 1);
                assert(sent_packet->handles.end_handle == 9);
                assert(bytes[8] == 0x06 && bytes[13] == 0x00 && bytes[14] == 0x28);
                assert(memcmp(bytes + 15, value, 3) == 0);
                assert(sent_connection == 2 && sent_handle == 1);
                assert(sent_message == 3 && sent_continuing == 1);
                reset();

                open_cfw_cordio_attc_read_by_type_request(
                    3, 2, 8, 3, value, 0
                );
                bytes = (uint8_t *)sent_packet;
                assert(allocated_length == 16 && sent_packet->handles.length == 8);
                assert(bytes[8] == 0x08 && memcmp(bytes + 13, value, 3) == 0);
                assert(sent_message == 4 && sent_handle == 2);
                reset();

                open_cfw_cordio_attc_read_long_request(1, 0x1234, 7, 1);
                bytes = (uint8_t *)sent_packet;
                assert(allocated_length == 13 && sent_packet->offset.length == 5);
                assert(sent_packet->offset.offset == 7);
                assert(bytes[8] == 0x0C && bytes[9] == 0x34 && bytes[10] == 0x12);
                assert(sent_message == 6 && sent_continuing == 1);
                reset();

                open_cfw_cordio_attc_read_multiple_request(2, 2, handles);
                bytes = (uint8_t *)sent_packet;
                assert(allocated_length == 13 && sent_packet->length == 5);
                assert(bytes[8] == 0x0E && bytes[9] == 0x34 && bytes[12] == 0x56);
                assert(sent_message == 7 && sent_handle == 0x1234);
                reset();
                open_cfw_cordio_attc_read_multiple_request(2, 0, handles);
                assert(sends == 0);

                open_cfw_cordio_attc_read_by_group_type_request(
                    2, 1, 0xFFFF, 3, value, 1
                );
                bytes = (uint8_t *)sent_packet;
                assert(bytes[8] == 0x10 && memcmp(bytes + 13, value, 3) == 0);
                assert(sent_message == 8 && sent_continuing == 1);
                reset();
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            harness_path = temp / "harness.c"
            executable = temp / "attc-read-test"
            harness_path.write_text(harness)
            subprocess.run([
                "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE_DIR), str(SOURCE), str(harness_path),
                "-o", str(executable),
            ], check=True)
            subprocess.run([str(executable)], check=True)

    def test_complete_and_isolated_cortex_m55_builds(self) -> None:
        selectors = [
            "FIND_TYPE_RESPONSE", "LONG_RESPONSE", "FIND_TYPE_REQUEST",
            "TYPE_REQUEST", "LONG_REQUEST", "MULTIPLE_REQUEST",
            "GROUP_TYPE_REQUEST",
        ]
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            for selector in [None, *selectors]:
                command = [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE_DIR),
                ]
                if selector is not None:
                    command.append(f"-DOPEN_CFW_ATTC_READ_{selector}_ONLY=1")
                command.extend([
                    "-c", str(SOURCE),
                    "-o", str(temp / f"{selector or 'all'}.o"),
                ])
                subprocess.run(command, check=True)

    def test_source_has_no_placeholder_or_host_dependency(self) -> None:
        source = SOURCE.read_text()
        self.assertNotIn("TODO", source)
        self.assertNotIn("abort(", source)
        self.assertNotIn("stdio.h", source)
        self.assertNotIn("stdlib.h", source)


if __name__ == "__main__":
    unittest.main()
