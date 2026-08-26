#!/usr/bin/env python3
"""Exercise the production-routed G2 Cordio ATT server write processors."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_write.c"


class CordioAttsWriteSourceTests(unittest.TestCase):
    def test_host_write_prepare_execute_and_continue_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_atts_write.h"

            struct open_cfw_cordio_wsf_queue_candidate
                open_cfw_cordio_atts_prepared_write_queues[4];
            static struct open_cfw_cordio_att_configuration configuration = {
                0, 23, 30, 3
            };
            struct open_cfw_cordio_att_configuration
                *open_cfw_cordio_att_configuration = &configuration;
            open_cfw_cordio_atts_ccc_write_callback_t
                open_cfw_cordio_atts_write_ccc_callback;

            static struct open_cfw_cordio_atts_attribute attributes[2];
            static struct open_cfw_cordio_atts_group group;
            static struct open_cfw_cordio_att_main_control_block main_cb;
            static unsigned allocations, frees, sends, errors, clears;
            static uint8_t permission_error, callback_error;
            static uint8_t last_opcode, last_reason, last_slot;
            static uint16_t last_handle, last_send_length;
            static uint8_t last_packet[64];

            static uint8_t write_callback(
                uint8_t connection_id, uint16_t handle, uint8_t opcode,
                uint16_t offset, uint16_t length, uint8_t *value,
                struct open_cfw_cordio_atts_attribute *attribute
            ) {
                (void)attribute;
                assert(connection_id == 2);
                assert(handle == 0x22);
                assert(offset == 0);
                assert(length == 2);
                assert(value[0] == 0xA1 && value[1] == 0xB2);
                last_opcode = opcode;
                return callback_error;
            }

            struct open_cfw_cordio_atts_attribute *
            open_cfw_cordio_atts_find_by_handle(
                uint16_t handle, struct open_cfw_cordio_atts_group **out
            ) {
                *out = &group;
                if (handle == 0x11) return &attributes[0];
                if (handle == 0x22) return &attributes[1];
                return 0;
            }
            uint8_t open_cfw_cordio_atts_permissions(
                uint8_t connection_id, uint8_t permit, uint16_t handle,
                uint8_t permissions
            ) {
                assert(connection_id == 2);
                assert(permit == 0x10 && permissions == 0x10);
                assert(handle == 0x11 || handle == 0x22);
                return permission_error;
            }
            void open_cfw_cordio_atts_error_response(
                struct open_cfw_cordio_att_main_control_block *main,
                uint8_t slot, uint8_t opcode, uint16_t handle, uint8_t reason
            ) {
                assert(main == &main_cb);
                errors++;
                last_slot = slot;
                last_opcode = opcode;
                last_handle = handle;
                last_reason = reason;
            }
            void *open_cfw_cordio_att_message_allocate(uint16_t length) {
                assert(length <= sizeof(last_packet));
                memset(last_packet, 0, sizeof(last_packet));
                return last_packet;
            }
            void open_cfw_cordio_att_l2c_data_request(
                struct open_cfw_cordio_att_main_control_block *main,
                uint8_t slot, uint16_t length, uint8_t *packet
            ) {
                assert(main == &main_cb && packet == last_packet);
                sends++;
                last_slot = slot;
                last_send_length = length;
            }
            struct open_cfw_cordio_att_main_control_block *
            open_cfw_cordio_att_control_block_by_connection_id(uint8_t id) {
                return id == 2 ? &main_cb : 0;
            }
            void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t n) {
                allocations++;
                return calloc(1, n);
            }
            void open_cfw_cordio_wsf_buffer_free_candidate(void *p) {
                frees++;
                free(p);
            }
            void open_cfw_cordio_wsf_queue_enqueue_candidate(
                struct open_cfw_cordio_wsf_queue_candidate *queue, void *item
            ) {
                struct open_cfw_cordio_atts_prepared_write *prepared = item;
                prepared->next = 0;
                if (queue->tail) {
                    ((struct open_cfw_cordio_atts_prepared_write *)
                        queue->tail)->next = prepared;
                } else {
                    queue->head = prepared;
                }
                queue->tail = prepared;
            }
            void *open_cfw_cordio_wsf_queue_dequeue_candidate(
                struct open_cfw_cordio_wsf_queue_candidate *queue
            ) {
                struct open_cfw_cordio_atts_prepared_write *prepared =
                    queue->head;
                if (prepared) {
                    queue->head = prepared->next;
                    if (!queue->head) queue->tail = 0;
                    prepared->next = 0;
                }
                return prepared;
            }
            uint16_t open_cfw_cordio_wsf_queue_count_candidate(
                struct open_cfw_cordio_wsf_queue_candidate *queue
            ) {
                uint16_t count = 0;
                struct open_cfw_cordio_atts_prepared_write *prepared =
                    queue->head;
                while (prepared) { count++; prepared = prepared->next; }
                return count;
            }
            void open_cfw_cordio_atts_clear_prepared_writes(
                struct open_cfw_cordio_atts_connection_control_block *ccb
            ) {
                void *prepared;
                struct open_cfw_cordio_wsf_queue_candidate *queue =
                    &open_cfw_cordio_atts_prepared_write_queues[
                        ccb->connection_id];
                clears++;
                while ((prepared =
                    open_cfw_cordio_wsf_queue_dequeue_candidate(queue))) {
                    open_cfw_cordio_wsf_buffer_free_candidate(prepared);
                }
            }

            static void build_write(uint8_t *packet, uint8_t opcode,
                                    uint16_t handle, uint8_t a, uint8_t b) {
                memset(packet, 0, 32);
                packet[8] = opcode;
                packet[9] = (uint8_t)handle;
                packet[10] = (uint8_t)(handle >> 8);
                packet[11] = a;
                packet[12] = b;
            }
            static void build_prepare(uint8_t *packet, uint16_t handle,
                                      uint16_t offset, uint8_t a, uint8_t b) {
                memset(packet, 0, 32);
                packet[8] = 0x16;
                packet[9] = (uint8_t)handle;
                packet[10] = (uint8_t)(handle >> 8);
                packet[11] = (uint8_t)offset;
                packet[12] = (uint8_t)(offset >> 8);
                packet[13] = a;
                packet[14] = b;
            }

            int main(void) {
                struct open_cfw_cordio_atts_connection_control_block ccb;
                uint8_t value0[8] = {0}, value1[8] = {0};
                uint16_t length0 = 0, length1 = 0;
                uint8_t packet[32];

                memset(&ccb, 0, sizeof(ccb));
                memset(&main_cb, 0, sizeof(main_cb));
                memset(&group, 0, sizeof(group));
                ccb.main = &main_cb;
                ccb.connection_id = 2;
                ccb.slot = 1;
                main_cb.connection_id = 2;
                attributes[0].value = value0;
                attributes[0].length = &length0;
                attributes[0].maximum_length = 4;
                attributes[0].settings = 0x08 | 0x10;
                attributes[0].permissions = 0x10;
                attributes[1].value = value1;
                attributes[1].length = &length1;
                attributes[1].maximum_length = 2;
                attributes[1].settings = 0x02;
                attributes[1].permissions = 0x10;
                group.write_callback = write_callback;

                /* Ordinary variable write and response. */
                build_write(packet, 0x12, 0x11, 0x41, 0x42);
                open_cfw_cordio_atts_process_write(&ccb, 5, packet);
                assert(value0[0] == 0x41 && value0[1] == 0x42);
                assert(length0 == 2 && sends == 1 && last_send_length == 1);
                assert(last_packet[8] == 0x13 && last_slot == 1);

                /* Commands never receive an ATT error response. */
                build_write(packet, 0x52, 0x9999, 1, 2);
                open_cfw_cordio_atts_process_write(&ccb, 5, packet);
                assert(errors == 0);

                /* A callback can defer a request on its bearer. */
                callback_error = 0x7A;
                build_write(packet, 0x12, 0x22, 0xA1, 0xB2);
                open_cfw_cordio_atts_process_write(&ccb, 5, packet);
                assert(last_opcode == 0x12 && errors == 0);
                assert(main_cb.bearer[1].control == 0x08);
                callback_error = 0;

                /* Prepare echoes handle, offset, and value and queues data. */
                build_prepare(packet, 0x11, 1, 0x77, 0x88);
                open_cfw_cordio_atts_process_prepare_write_request(
                    &ccb, 7, packet
                );
                assert(allocations == 1);
                assert(open_cfw_cordio_wsf_queue_count_candidate(
                    &open_cfw_cordio_atts_prepared_write_queues[2]) == 1);
                assert(last_packet[8] == 0x17 && last_packet[9] == 0x11);
                assert(last_packet[11] == 1 && last_packet[13] == 0x77);
                assert(last_send_length == 7);

                /* Execute validates the whole queue, commits, frees, responds. */
                memset(packet, 0, sizeof(packet));
                packet[8] = 0x18;
                packet[9] = 1;
                open_cfw_cordio_atts_process_execute_write_request(
                    &ccb, 2, packet
                );
                assert(value0[1] == 0x77 && value0[2] == 0x88);
                assert(length0 == 3 && frees == 1);
                assert(last_packet[8] == 0x19 && last_send_length == 1);

                /* Invalid offset is rejected before any queued write commits. */
                build_prepare(packet, 0x11, 7, 0x55, 0x66);
                open_cfw_cordio_atts_process_prepare_write_request(
                    &ccb, 7, packet
                );
                memset(packet, 0, sizeof(packet));
                packet[9] = 1;
                open_cfw_cordio_atts_process_execute_write_request(
                    &ccb, 2, packet
                );
                assert(last_opcode == 0x18 && last_reason == 0x07);
                assert(clears == 1 && frees == 2);

                /* Cancel clears and succeeds; unknown flag returns invalid PDU. */
                build_prepare(packet, 0x11, 0, 0x31, 0x32);
                open_cfw_cordio_atts_process_prepare_write_request(
                    &ccb, 7, packet
                );
                memset(packet, 0, sizeof(packet));
                packet[9] = 0;
                open_cfw_cordio_atts_process_execute_write_request(
                    &ccb, 2, packet
                );
                assert(clears == 2 && frees == 3 && last_packet[8] == 0x19);
                packet[9] = 2;
                open_cfw_cordio_atts_process_execute_write_request(
                    &ccb, 2, packet
                );
                assert(last_reason == 0x04 && last_handle == 0);

                /* Source-only continuation still has complete behavior. */
                main_cb.bearer[0].control = 0x08;
                open_cfw_cordio_atts_continue_write_request(2, 0x11, 0);
                assert(main_cb.bearer[0].control == 0);
                assert(last_packet[8] == 0x13 && last_slot == 0);
                main_cb.bearer[0].control = 0x08;
                open_cfw_cordio_atts_continue_write_request(2, 0x11, 0x0E);
                assert(main_cb.bearer[0].control == 0);
                assert(last_opcode == 0x12 && last_reason == 0x0E);
                open_cfw_cordio_atts_continue_write_request(0, 0x11, 0);
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
            "EXECUTE", "PROCESS", "PREPARE", "EXECUTE_REQUEST", "CONTINUE",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_WRITE_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_WRITE_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
