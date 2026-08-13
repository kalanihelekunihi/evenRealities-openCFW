#!/usr/bin/env python3
"""Guard the recovered, production-excluded G2 Cordio WSF OS/queue source."""

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
ANALYZER = ROOT / "tools/analyze_g2_cordio_wsf_os.py"
CANDIDATE_DIR = ROOT / "components/shared/cordio"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_wsf_os", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(CORPUS.is_dir(), "authenticated Apollo Ghidra corpus unavailable")
class CordioWsfOsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_modules_callers_and_abi_are_closed(self) -> None:
        os_module = self.report["modules"]["wsf_os"]
        queue_module = self.report["modules"]["wsf_queue"]
        self.assertEqual(
            (os_module["start"], os_module["end_exclusive"], os_module["size"]),
            (0x0052B8A4, 0x0052BAB8, 532),
        )
        self.assertEqual(
            (queue_module["start"], queue_module["end_exclusive"], queue_module["size"]),
            (0x00538C24, 0x00538D16, 242),
        )
        self.assertEqual((len(os_module["functions"]), len(queue_module["functions"])), (12, 6))
        by_name = {
            item["name"]: item
            for item in os_module["functions"] + queue_module["functions"]
        }
        self.assertEqual(len(by_name["WsfCsEnter"]["direct_bl_callers"]), 13)
        self.assertEqual(len(by_name["WsfTaskLock"]["direct_bl_callers"]), 28)
        self.assertEqual(
            by_name["wsfOsDispatcher"]["direct_bl_callers"],
            [0x004D0A62],
        )
        self.assertEqual(
            by_name["WsfQueueInsert"]["direct_bl_callers"],
            [0x0052A45E, 0x005353D8],
        )
        self.assertEqual(self.report["modules"]["stored_entry_or_interior_pointers"], 0)
        abi = self.report["abi"]
        self.assertEqual((abi["max_handlers"], abi["task_size"]), (10, 0x40))
        self.assertEqual(abi["task_offsets"]["message_queue"], 0x34)
        self.assertEqual(abi["globals"]["scb_icsr"], 0xE000ED04)

    def test_lineage_candidate_and_matrix_are_qualified(self) -> None:
        lineage = self.report["lineage"]
        self.assertEqual(lineage["selected_release"], "2.5.1")
        self.assertEqual(
            lineage["os_git_blob"],
            "8a466f57d90e402502cdfcfda96e616736487021",
        )
        self.assertEqual(
            lineage["queue_git_blob"],
            "7eab0ae7d02486a9e8af9419cc8f25235a2a1200",
        )
        self.assertEqual(lineage["stock_effective_handler_count"], 10)
        self.assertEqual(lineage["exact_g2_handler_count_definition_site"], "unavailable")
        self.assertEqual(len(lineage["later_ten_handler_corroboration"]), 2)
        candidate = self.report["candidate"]
        self.assertEqual(candidate["production"], "excluded")
        self.assertEqual(candidate["behaviorally_recreated_stock_functions"], 18)
        self.assertEqual(candidate["behaviorally_recreated_stock_bytes"], 774)
        self.assertFalse(candidate["stock_queue_empty_body_bounded"])
        matrix = self.report["stock_abi_matrix"]
        self.assertEqual((matrix["configs"], matrix["comparison_rows"]), (13, 234))
        self.assertEqual(matrix["best_common_config"], "Os_nosibling")
        self.assertEqual(matrix["linked_unresolved_symbols"], 0)
        self.assertEqual(matrix["raw_matches"], 0)

    def test_candidate_host_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdbool.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_wsf_os_candidate.h"

            uint8_t open_cfw_cordio_wsf_cs_nesting_candidate;
            struct open_cfw_cordio_wsf_os_task_candidate open_cfw_cordio_wsf_os_task_candidate;
            void *open_cfw_cordio_wsf_radio_event_group_candidate;

            static unsigned disables, enables, pends, yields, creates, waits;
            static unsigned updates, frees, callbacks, isr_sets, task_sets;
            static int inside, isr_result, hpw_value;
            static uint32_t task_set_result;
            static char trace[8];
            static unsigned trace_len;
            static struct open_cfw_cordio_wsf_msg_header message;
            static struct open_cfw_cordio_wsf_timer timer;
            static bool message_ready, timer_ready;

            void open_cfw_cordio_wsf_interrupt_disable_candidate(void) { disables++; }
            void open_cfw_cordio_wsf_interrupt_enable_candidate(void) { enables++; }
            int open_cfw_cordio_wsf_port_is_inside_interrupt_candidate(void) { return inside; }
            int open_cfw_cordio_wsf_event_group_set_bits_from_isr_candidate(
                void *group, uint32_t bits, int *hpw
            ) { assert(group == (void *)0x1234 && bits == 1); *hpw = hpw_value; isr_sets++; return isr_result; }
            uint32_t open_cfw_cordio_wsf_event_group_set_bits_candidate(
                void *group, uint32_t bits
            ) { assert(group == (void *)0x1234 && bits == 1); task_sets++; return task_set_result; }
            void open_cfw_cordio_wsf_pend_pendsv_candidate(void) { pends++; }
            void open_cfw_cordio_wsf_yield_candidate(void) { yields++; }
            void *open_cfw_cordio_wsf_event_group_create_candidate(void) { creates++; return (void *)0x1234; }
            uint32_t open_cfw_cordio_wsf_event_group_wait_bits_candidate(
                void *group, uint32_t bits, bool clear, bool all, uint32_t ticks
            ) { assert(group == (void *)0x1234 && bits == 1 && clear && !all && ticks == UINT32_MAX); waits++; return 0; }
            void *open_cfw_cordio_wsf_os_message_dequeue_candidate(
                struct open_cfw_cordio_wsf_queue_candidate *queue, uint8_t *handler
            ) { (void)queue; if (!message_ready) return 0; message_ready = false; *handler = 0; return &message; }
            void open_cfw_cordio_wsf_os_message_free_candidate(void *value) { assert(value == &message); frees++; }
            void open_cfw_cordio_wsf_timer_update_ticks_candidate(void) { updates++; }
            struct open_cfw_cordio_wsf_timer *open_cfw_cordio_wsf_timer_service_expired_candidate(uint8_t id) {
                assert(id == 0); if (!timer_ready) return 0; timer_ready = false; return &timer;
            }
            static void handler(uint8_t event, struct open_cfw_cordio_wsf_msg_header *value) {
                callbacks++;
                if (value == &message) { assert(event == 0); trace[trace_len++] = 'M'; }
                else if (value == &timer.msg) { assert(event == 0); trace[trace_len++] = 'T'; }
                else { assert(value == 0 && event == 5); trace[trace_len++] = 'H'; }
            }

            struct node { void *next; unsigned value; };

            int main(void) {
                struct open_cfw_cordio_wsf_queue_candidate queue = {0};
                struct node a = {0,1}, b = {0,2}, c = {0,3};

                open_cfw_cordio_wsf_queue_enqueue_candidate(&queue, &a);
                open_cfw_cordio_wsf_queue_enqueue_candidate(&queue, &b);
                open_cfw_cordio_wsf_queue_insert_candidate(&queue, &c, &a);
                assert(queue.head == &a && queue.tail == &b && a.next == &c && c.next == &b);
                assert(open_cfw_cordio_wsf_queue_count_candidate(&queue) == 3);
                open_cfw_cordio_wsf_queue_remove_candidate(&queue, &c, &a);
                assert(a.next == &b && c.next == &b);
                open_cfw_cordio_wsf_queue_push_candidate(&queue, &c);
                assert(open_cfw_cordio_wsf_queue_dequeue_candidate(&queue) == &c && c.next == &a);
                open_cfw_cordio_wsf_queue_remove_candidate(&queue, &b, &a);
                assert(queue.tail == &a);
                assert(open_cfw_cordio_wsf_queue_dequeue_candidate(&queue) == &a);
                assert(open_cfw_cordio_wsf_queue_empty_candidate(&queue));
                assert(open_cfw_cordio_wsf_cs_nesting_candidate == 0 && disables == enables);

                disables = enables = 0;
                open_cfw_cordio_wsf_queue_insert_candidate(&queue, &a, 0);
                assert(disables == 1 && enables == 1);
                open_cfw_cordio_wsf_cs_nesting_candidate = 0;
                open_cfw_cordio_wsf_cs_exit_candidate();
                assert(open_cfw_cordio_wsf_cs_nesting_candidate == 255 && enables == 1);
                open_cfw_cordio_wsf_cs_nesting_candidate = 0;

                open_cfw_cordio_wsf_radio_event_group_candidate = 0;
                open_cfw_cordio_wsf_set_os_specific_event_candidate();
                assert(isr_sets == 0 && task_sets == 0);
                open_cfw_cordio_wsf_radio_event_group_candidate = (void *)0x1234;
                inside = 1; isr_result = 1; hpw_value = 1;
                open_cfw_cordio_wsf_set_os_specific_event_candidate();
                assert(isr_sets == 1 && pends == 1);
                inside = 0; task_set_result = 1;
                open_cfw_cordio_wsf_set_os_specific_event_candidate();
                assert(task_sets == 1 && yields == 1);

                memset(&open_cfw_cordio_wsf_os_task_candidate, 0xA5, sizeof(open_cfw_cordio_wsf_os_task_candidate));
                open_cfw_cordio_wsf_radio_event_group_candidate = 0;
                open_cfw_cordio_wsf_os_init_candidate();
                assert(creates == 1 && open_cfw_cordio_wsf_radio_event_group_candidate == (void *)0x1234);
                assert(open_cfw_cordio_wsf_os_task_candidate.number_of_handlers == 0);
                assert(open_cfw_cordio_wsf_os_set_next_handler_candidate(handler) == 0);
                assert(open_cfw_cordio_wsf_task_message_queue_candidate(9) == &open_cfw_cordio_wsf_os_task_candidate.message_queue);

                timer.handler_id = 0;
                message_ready = timer_ready = true;
                open_cfw_cordio_wsf_os_task_candidate.task_event_mask = 7;
                open_cfw_cordio_wsf_os_task_candidate.handler_event_masks[0] = 5;
                open_cfw_cordio_wsf_os_dispatcher_candidate();
                assert(callbacks == 3 && frees == 1 && trace_len == 3);
                assert(trace[0] == 'M' && trace[1] == 'T' && trace[2] == 'H');
                assert(updates == 2 && waits == 1);
                assert(open_cfw_cordio_wsf_os_task_candidate.task_event_mask == 0);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "harness.c"
            binary = Path(directory) / "harness"
            source.write_text(harness)
            subprocess.run([
                os.environ.get("CC", "cc"), "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-fno-strict-aliasing", "-I", str(CANDIDATE_DIR),
                str(CANDIDATE_DIR / "runtime_cordio_wsf_os_candidate.c"),
                str(CANDIDATE_DIR / "runtime_cordio_wsf_queue_candidate.c"),
                str(source), "-o", str(binary),
            ], cwd=ROOT, check=True, capture_output=True, text=True)
            subprocess.run([str(binary)], check=True)

    def test_combined_arm_compile_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for name in (
                "runtime_cordio_wsf_queue_candidate.c",
                "runtime_cordio_wsf_timer_candidate.c",
                "runtime_cordio_wsf_os_candidate.c",
            ):
                subprocess.run([
                    "clang", "-target", "arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-I", str(CANDIDATE_DIR), "-c", str(CANDIDATE_DIR / name),
                    "-o", str(Path(directory) / f"{name}.o"),
                ], cwd=ROOT, check=True, capture_output=True, text=True)

    def test_candidate_is_absent_from_production_inputs(self) -> None:
        for needle in ("runtime_cordio_wsf_os_candidate", "runtime_cordio_wsf_queue_candidate"):
            for relative in (
                "components/apollo_main/core_overlay/build_component.py",
                "components/apollo_main/core_overlay/overlay.json",
                "components/apollo_main/ring_gesture/build_component.py",
                "components/apollo_main/ring_gesture/overlay.json",
                "components/bootloader/core_overlay/build_component.py",
                "components/bootloader/core_overlay/overlay.json",
            ):
                self.assertNotIn(needle, (ROOT / relative).read_text())

    def test_cli_json(self) -> None:
        parsed = json.loads(subprocess.run([
            sys.executable, str(ANALYZER), "--ghidra-corpus", str(CORPUS), "--json",
        ], cwd=ROOT, check=True, capture_output=True, text=True).stdout)
        self.assertEqual(parsed["modules"]["wsf_queue"]["functions"][-1]["name"], "WsfQueueCount")


if __name__ == "__main__":
    unittest.main()
