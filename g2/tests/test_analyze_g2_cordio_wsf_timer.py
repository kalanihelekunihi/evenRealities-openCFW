#!/usr/bin/env python3
"""Guard the recovered, production-excluded G2 Cordio WSF timer source."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_cordio_wsf_timer.py"
AMBIQ_VERIFIER = ROOT / "tools" / "verify_ambiqsuite_cordio_wsf_timer_archive.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))
CANDIDATE_DIR = ROOT / "components" / "shared" / "cordio"
AMBIQ_ARCHIVE_ROOT = Path("/var/tmp/ambiqsuite-wsf.ydLxMc")


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_wsf_timer", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(CORPUS.is_dir(), "authenticated Apollo Ghidra corpus unavailable")
class CordioWsfTimerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_module_functions_callers_and_abi_are_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(
            (module["start"], module["end_exclusive"], module["size"]),
            (0x0052A3FC, 0x0052A614, 536),
        )
        by_name = {item["name"]: item for item in module["functions"]}
        self.assertEqual(by_name["WsfTimerInit"]["direct_bl_callers"], [0x004B7F6A])
        self.assertEqual(by_name["WsfTimerNextExpiration"]["direct_bl_callers"], [0x0052A59A])
        self.assertEqual(by_name["WsfTimerServiceExpired"]["direct_bl_callers"], [0x0052BA32])
        self.assertEqual(by_name["WsfTimerUpdateTicks"]["direct_bl_callers"], [0x0052B9D4, 0x0052BA96])
        self.assertEqual(sum(
            len(item["direct_bl_callers"]) for item in module["functions"]
        ), 53)
        self.assertEqual(
            (module["callback_pointer_cell"], module["callback_thumb_entry"]),
            (0x0052A61C, 0x0052A469),
        )
        self.assertEqual(
            by_name["WsfTimerInit"]["direct_bl_callees"],
            [
                {"callsite": 0x0052A494, "target": 0x0047E6DC},
                {"callsite": 0x0052A4A0, "target": 0x005FA0A4},
                {"callsite": 0x0052A4AE, "target": 0x00454EFE},
            ],
        )
        self.assertEqual(
            self.report["abi"]["timer_offsets"],
            {"next": 0, "ticks": 4, "msg": 8, "handler_id": 12, "is_started": 13},
        )
        self.assertEqual(self.report["abi"]["globals"]["queue"], 0x200741B0)

    def test_lineage_is_split_and_candidate_is_production_routed(self) -> None:
        lineage = self.report["lineage"]
        self.assertEqual(
            lineage["packetcraft_r19_02"]["commit"],
            "86372d84ef0386d8834ed036e613c8f2ded1ff16",
        )
        self.assertEqual(
            lineage["packetcraft_r20_05_to_r20_05c"]["git_blob"],
            "df2c9dd1e94b26e2e989f01dcc82a1cf418b58d2",
        )
        self.assertEqual(lineage["ambiqsuite"]["selected_release"], "2.5.1")
        self.assertEqual(
            lineage["ambiqsuite"]["source_sha256"],
            "4d6641c8de197367a6c1561738b389afd164321b879264cd795796c80ab55dd7",
        )
        self.assertEqual(
            lineage["ambiqsuite"]["header_sha256"],
            "ae23e7b3bc17243d30aa300c58c73cb15ef1da070d90418b69cfb5da6862322b",
        )
        self.assertEqual(lineage["ambiqsuite"]["mapped_functions"], 11)
        self.assertEqual(self.report["strings"]["update_name"], "WsfTimerUpdateTicks")
        self.assertEqual(self.report["candidate"]["production"], "routed")
        self.assertEqual(len(self.report["candidate"]["functions"]), 11)
        self.assertEqual(
            self.report["candidate"]["behaviorally_recreated_stock_function_bytes"],
            536,
        )
        self.assertEqual(
            tuple(
                self.report["candidate"][key]
                for key in (
                    "compiled_text_bytes",
                    "alignment_bytes",
                    "strict_relocations",
                    "guarded_redirects",
                    "retained_literal_table_bytes",
                )
            ),
            (632, 14, 29, 11, 36),
        )
        self.assertEqual(self.report["compiler_matrix"]["rows"], 8)
        self.assertEqual(self.report["compiler_matrix"]["raw_matches"], 0)
        self.assertEqual(
            self.report["compiler_matrix"]["exact_size_rows"],
            [{
                "release": "r19.02",
                "config": "Os_noinline",
                "function": "WsfTimerNextExpiration",
                "bytes": 40,
            }],
        )
        current = self.report["current11_matrix"]
        self.assertEqual((current["configs"], current["function_rows"]), (13, 143))
        self.assertEqual(current["exact_size_functions"], 8)
        self.assertEqual(current["raw_matches"], 0)
        self.assertEqual(current["strict_normalized_matches"], 0)
        self.assertEqual(current["linked_unresolved_symbols"], 0)
        self.assertEqual(
            current["remaining_best_size_gaps"],
            {
                "WsfTimerInit": 4,
                "WsfTimerServiceExpired": 2,
                "WsfTimerUpdateTicks": 12,
            },
        )
        limitations = " ".join(self.report["limitations"])
        self.assertIn("versioned AmbiqSuite 2.5.1 archive", limitations)
        self.assertIn("minor local text/config drift", limitations)
        self.assertIn("opposite", limitations)

    def test_candidate_host_behavior(self) -> None:
        harness = textwrap.dedent(
            r"""
            #include <assert.h>
            #include <stdbool.h>
            #include <stdint.h>
            #include "runtime_cordio_wsf_timer_candidate.h"

            struct open_cfw_cordio_wsf_queue_candidate
                open_cfw_cordio_wsf_timer_queue_candidate;
            void *open_cfw_cordio_wsf_freertos_timer_candidate;
            uint32_t open_cfw_cordio_wsf_last_tick_candidate;
            static unsigned locks, unlocks, removes, inserts, readies;
            static unsigned creates, commands, command_failures, fatals;
            static uint32_t now_tick, command, value, reserved, wait_ticks;
            static uint8_t ready_handler;
            static uint8_t ready_event;
            static int command_result = 1;
            static void *create_result = (void *)0x1234;

            void open_cfw_cordio_wsf_task_lock_candidate(void) { locks++; }
            void open_cfw_cordio_wsf_task_unlock_candidate(void) { unlocks++; }
            void open_cfw_cordio_wsf_queue_remove_candidate(
                struct open_cfw_cordio_wsf_queue_candidate *queue,
                void *element,
                void *previous_element
            ) {
                struct open_cfw_cordio_wsf_timer *timer = element;
                struct open_cfw_cordio_wsf_timer *previous = previous_element;
                if (previous == 0) {
                    assert(queue->head == timer);
                    queue->head = timer->next;
                } else {
                    assert(previous->next == timer);
                    previous->next = timer->next;
                }
                if (queue->tail == timer) queue->tail = previous;
                timer->next = 0;
                removes++;
            }
            void open_cfw_cordio_wsf_queue_insert_candidate(
                struct open_cfw_cordio_wsf_queue_candidate *queue,
                void *element,
                void *previous_element
            ) {
                struct open_cfw_cordio_wsf_timer *timer = element;
                struct open_cfw_cordio_wsf_timer *previous = previous_element;
                if (previous == 0) {
                    timer->next = queue->head;
                    queue->head = timer;
                } else {
                    timer->next = previous->next;
                    previous->next = timer;
                }
                if (timer->next == 0) queue->tail = timer;
                if (queue->tail == 0) queue->tail = timer;
                inserts++;
            }
            void open_cfw_cordio_wsf_task_set_ready_candidate(
                uint8_t handler_id, uint8_t event_mask
            ) {
                readies++;
                ready_handler = handler_id;
                ready_event = event_mask;
            }
            uint32_t open_cfw_cordio_wsf_tick_counter_get_candidate(void) { return now_tick; }
            void *open_cfw_cordio_wsf_timer_create_candidate(
                const char *name, uint32_t period_ticks, bool auto_reload,
                void *timer_id, void (*callback)(void *timer)
            ) {
                assert(name[0] == 'W' && name[4] == 'T');
                assert(period_ticks == 10 && !auto_reload && timer_id == 0);
                assert(callback == open_cfw_cordio_wsf_timer_callback_candidate);
                creates++;
                return create_result;
            }
            int open_cfw_cordio_wsf_timer_command_candidate(
                void *timer, uint32_t command_value, uint32_t timer_value,
                uint32_t reserved_value, uint32_t wait_value
            ) {
                assert(timer == open_cfw_cordio_wsf_freertos_timer_candidate);
                commands++;
                command = command_value;
                value = timer_value;
                reserved = reserved_value;
                wait_ticks = wait_value;
                return command_result;
            }
            void open_cfw_cordio_wsf_timer_command_failure_candidate(void) {
                command_failures++;
            }
            void open_cfw_cordio_wsf_timer_fatal_candidate(void) { fatals++; }

            int main(void) {
                bool running = true;
                struct open_cfw_cordio_wsf_timer first = {0};
                struct open_cfw_cordio_wsf_timer second = {0};

                open_cfw_cordio_wsf_timer_queue_candidate.head = &first;
                open_cfw_cordio_wsf_timer_queue_candidate.tail = &first;
                now_tick = 77;
                open_cfw_cordio_wsf_timer_init_candidate();
                assert(open_cfw_cordio_wsf_timer_queue_candidate.head == 0);
                assert(open_cfw_cordio_wsf_timer_queue_candidate.tail == 0);
                assert(open_cfw_cordio_wsf_freertos_timer_candidate == create_result);
                assert(open_cfw_cordio_wsf_last_tick_candidate == 77 && creates == 1);

                open_cfw_cordio_wsf_timer_queue_candidate.head = &second;
                open_cfw_cordio_wsf_timer_queue_candidate.tail = &second;
                now_tick = 88;
                open_cfw_cordio_wsf_timer_init_candidate();
                assert(open_cfw_cordio_wsf_timer_queue_candidate.head == 0);
                assert(open_cfw_cordio_wsf_timer_queue_candidate.tail == 0);
                assert(creates == 1 && open_cfw_cordio_wsf_last_tick_candidate == 77);

                open_cfw_cordio_wsf_timer_callback_candidate((void *)0x5678);
                assert(readies == 1 && ready_handler == 0 && ready_event == 2);

                assert(open_cfw_cordio_wsf_timer_next_expiration_candidate(&running) == 0);
                assert(!running && locks == 1 && unlocks == 1);

                first.handler_id = 3;
                second.handler_id = 5;
                open_cfw_cordio_wsf_timer_start_sec_candidate(&first, 2);
                open_cfw_cordio_wsf_timer_start_ms_candidate(&second, 500);
                assert(first.ticks == 200 && second.ticks == 50);
                assert(open_cfw_cordio_wsf_timer_queue_candidate.head == &second);
                assert(open_cfw_cordio_wsf_timer_queue_candidate.tail == &first);
                assert(first.is_started == 1 && second.is_started == 1 && inserts == 2);

                open_cfw_cordio_wsf_timer_start_ms_candidate(&first, 100);
                assert(removes == 1 && inserts == 3 && first.ticks == 10);
                assert(open_cfw_cordio_wsf_timer_queue_candidate.head == &first);
                open_cfw_cordio_wsf_timer_stop_candidate(&first);
                assert(first.is_started == 0 && removes == 2);
                assert(open_cfw_cordio_wsf_timer_queue_candidate.head == &second);

                open_cfw_cordio_wsf_timer_start_sec_candidate(&first, 1);
                open_cfw_cordio_wsf_timer_update_candidate(60);
                assert(second.ticks == 0 && first.ticks == 40);
                assert(readies == 2 && ready_handler == 5 && ready_event == 2);
                assert(open_cfw_cordio_wsf_timer_next_expiration_candidate(&running) == 0);
                assert(running);
                assert(open_cfw_cordio_wsf_timer_service_expired_candidate(9) == &second);
                assert(second.is_started == 0 && removes == 3);
                assert(open_cfw_cordio_wsf_timer_service_expired_candidate(9) == 0);

                first.ticks = 7;
                open_cfw_cordio_wsf_last_tick_candidate = 100;
                now_tick = 135;
                open_cfw_cordio_wsf_timer_update_ticks_candidate();
                assert(first.ticks == 4);
                assert(open_cfw_cordio_wsf_last_tick_candidate == 135);
                assert(commands == 1 && command == 4 && value == 40);
                assert(reserved == 0 && wait_ticks == 100);

                command_result = 0;
                open_cfw_cordio_wsf_timer_update_ticks_candidate();
                assert(commands == 2 && command_failures == 1 && fatals == 1);

                open_cfw_cordio_wsf_freertos_timer_candidate = 0;
                create_result = 0;
                open_cfw_cordio_wsf_last_tick_candidate = 135;
                now_tick = 999;
                open_cfw_cordio_wsf_timer_init_candidate();
                assert(creates == 2 && fatals == 2);
                assert(open_cfw_cordio_wsf_last_tick_candidate == 135);
                return 0;
            }
            """
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "harness.c"
            binary = Path(directory) / "harness"
            source.write_text(harness, encoding="utf-8")
            subprocess.run(
                [
                    os.environ.get("CC", "cc"),
                    "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-I", str(CANDIDATE_DIR),
                    str(CANDIDATE_DIR / "runtime_cordio_wsf_timer_candidate.c"),
                    str(source), "-o", str(binary),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            subprocess.run([str(binary)], check=True)

    def test_candidate_is_present_in_apollo_production_inputs(self) -> None:
        needle = "runtime_cordio_wsf_timer_candidate"
        self.assertIn(
            needle,
            (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn(
            "cordio_wsf_timer_01_source_replacement",
            (ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text(
                encoding="utf-8"
            ),
        )

    @unittest.skipUnless(
        (AMBIQ_ARCHIVE_ROOT / "AmbiqSuite-R2.4.2.zip").is_file()
        and (AMBIQ_ARCHIVE_ROOT / "AmbiqSuite-R2.5.1-s3.zip").is_file(),
        "authenticated AmbiqSuite comparison archives unavailable",
    )
    def test_official_ambiq_archives_and_discriminator(self) -> None:
        spec = importlib.util.spec_from_file_location("verify_ambiq_wsf", AMBIQ_VERIFIER)
        assert spec is not None and spec.loader is not None
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        older = verifier.verify(
            AMBIQ_ARCHIVE_ROOT / "AmbiqSuite-R2.4.2.zip",
            "2.4.2",
        )
        selected = verifier.verify(
            AMBIQ_ARCHIVE_ROOT / "AmbiqSuite-R2.5.1-s3.zip",
            "2.5.1",
        )
        self.assertFalse(older["saved_tick_init"])
        self.assertEqual(older["mapped_function_spans"], 0)
        self.assertTrue(selected["saved_tick_init"])
        self.assertEqual(selected["mapped_function_spans"], 11)
        self.assertFalse(selected["source_redistributed"])

    def test_cli_json(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--ghidra-corpus", str(CORPUS), "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        ).stdout)
        self.assertEqual(parsed["module"]["functions"][-1]["name"], "WsfTimerUpdateTicks")


if __name__ == "__main__":
    unittest.main()
