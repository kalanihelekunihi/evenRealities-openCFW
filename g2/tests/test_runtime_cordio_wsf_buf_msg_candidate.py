#!/usr/bin/env python3
"""Exercise the production-excluded G2 WSF buffer and message candidates."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "components/shared/cordio"


class CordioWsfBufferMessageCandidateTests(unittest.TestCase):
    def test_arm_abi_compile_gate(self) -> None:
        clang = subprocess.run(
            ["sh", "-c", "command -v clang"],
            check=False,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not clang:
            self.skipTest("clang unavailable")
        with tempfile.TemporaryDirectory() as directory:
            for source in (
                "runtime_cordio_wsf_buf_candidate.c",
                "runtime_cordio_wsf_msg_candidate.c",
                "runtime_cordio_wsf_queue_candidate.c",
            ):
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
                        "-c", str(CANDIDATE / source),
                        "-o", str(Path(directory) / f"{source}.o"),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )

    def test_host_buffer_and_message_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stddef.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_wsf_buf_candidate.h"
            #include "runtime_cordio_wsf_msg_candidate.h"

            struct open_cfw_cordio_wsf_buffer_block_candidate
                *open_cfw_cordio_wsf_buffer_memory_candidate;
            uint16_t open_cfw_cordio_wsf_buffer_memory_length_candidate;
            uint8_t open_cfw_cordio_wsf_buffer_pool_count_candidate;

            static unsigned enters, exits, failures, ready_calls;
            static uint16_t failed_length;
            static uint8_t ready_handler, ready_event;
            static struct open_cfw_cordio_wsf_queue_candidate task_queue;

            void open_cfw_cordio_wsf_cs_enter_candidate(void) { enters++; }
            void open_cfw_cordio_wsf_cs_exit_candidate(void) { exits++; }
            void open_cfw_cordio_wsf_buffer_allocation_failure_candidate(
                uint16_t length
            ) { failures++; failed_length = length; }
            struct open_cfw_cordio_wsf_queue_candidate *
            open_cfw_cordio_wsf_task_message_queue_candidate(uint8_t id) {
                assert(id == 7); return &task_queue;
            }
            void open_cfw_cordio_wsf_task_set_ready_candidate(
                uint8_t handler, uint8_t event
            ) {
                ready_calls++; ready_handler = handler; ready_event = event;
            }

            int main(void) {
                union {
                    max_align_t alignment;
                    uint8_t bytes[512];
                } storage;
                const struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate
                    descriptors[] = {{16, 2, 0}, {32, 1, 0}};
                struct open_cfw_cordio_wsf_buffer_pool_candidate *pools;
                void *a, *b, *c, *message;
                uint8_t handler = 0;
                const uint16_t expected = (uint16_t)(
                    2 * sizeof(struct open_cfw_cordio_wsf_buffer_pool_candidate)
                    + 2 * OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT
                    + 2 * OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT
                );

                memset(&storage, 0xA5, sizeof(storage));
                assert(open_cfw_cordio_wsf_buffer_init_candidate(
                    sizeof(storage.bytes), storage.bytes, 2, descriptors
                ) == expected);
                pools = (struct open_cfw_cordio_wsf_buffer_pool_candidate *)
                    storage.bytes;
                assert(pools[0].descriptor.length
                    == OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT);
                assert(pools[0].descriptor.count == 2);
                assert(pools[1].descriptor.length
                    == 2 * OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT);

                a = open_cfw_cordio_wsf_buffer_allocate_candidate(1);
                b = open_cfw_cordio_wsf_buffer_allocate_candidate(16);
                c = open_cfw_cordio_wsf_buffer_allocate_candidate(16);
                assert(a == pools[0].start);
                assert(b != a && c == pools[1].start);
                assert(enters == 4 && exits == 4);
                assert(((struct open_cfw_cordio_wsf_buffer_block_candidate *)a)
                    ->free_marker == 0);

                open_cfw_cordio_wsf_buffer_free_candidate(a);
                assert(pools[0].free == a);
                assert(((struct open_cfw_cordio_wsf_buffer_block_candidate *)a)
                    ->free_marker == OPEN_CFW_CORDIO_WSF_BUFFER_FREE_MARKER);
                assert(enters == 5 && exits == 5);

                assert(open_cfw_cordio_wsf_buffer_allocate_candidate(1000) == 0);
                assert(failures == 1 && failed_length == 1000);

                open_cfw_cordio_wsf_buffer_free_candidate(b);
                open_cfw_cordio_wsf_buffer_free_candidate(c);
                message = open_cfw_cordio_wsf_message_data_allocate_candidate(4, 3);
                assert(message != 0);
                open_cfw_cordio_wsf_message_send_candidate(7, message);
                assert(ready_calls == 1 && ready_handler == 7 && ready_event == 1);
                assert(open_cfw_cordio_wsf_message_peek_candidate(
                    &task_queue, &handler
                ) == message && handler == 7);
                handler = 0;
                assert(open_cfw_cordio_wsf_os_message_dequeue_candidate(
                    &task_queue, &handler
                ) == message && handler == 7);
                assert(task_queue.head == 0 && task_queue.tail == 0);
                open_cfw_cordio_wsf_os_message_free_candidate(message);

                assert(open_cfw_cordio_wsf_buffer_init_candidate(
                    1, storage.bytes, 2, descriptors
                ) == 0);
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
                    f"-I{CANDIDATE}",
                    str(source),
                    str(CANDIDATE / "runtime_cordio_wsf_buf_candidate.c"),
                    str(CANDIDATE / "runtime_cordio_wsf_msg_candidate.c"),
                    str(CANDIDATE / "runtime_cordio_wsf_queue_candidate.c"),
                    "-o", str(binary),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
