from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_task_get_info.c"
HEADER = SOURCE.with_suffix(".h")
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
FUNCTION = "open_cfw_freertos_task_get_info"
START = 0x00455728
END = 0x004557A8
BASE = 0x00438000
STOCK_SHA256 = "53d97f8c2e506f69df7908f9b3d2c644fd4f21b456f5961311f1ce34d975f626"


class FreeRTOSTaskGetInfoTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        harness = r'''
#include <assert.h>
#include <string.h>
struct open_cfw_freertos_task_get_info_tcb;
extern struct open_cfw_freertos_task_get_info_tcb *open_cfw_test_current;
#define OPEN_CFW_FREERTOS_TASK_GET_INFO_CURRENT_TCB_LOAD() open_cfw_test_current
#include "runtime_freertos_task_get_info.h"

struct open_cfw_freertos_task_get_info_tcb *open_cfw_test_current;
static unsigned suspends, resumes, state_calls, stack_calls;
enum open_cfw_freertos_task_get_info_state open_cfw_freertos_task_get_state(
    const struct open_cfw_freertos_task_get_info_tcb *task) {
    assert(task != 0); state_calls++; return OPEN_CFW_FREERTOS_TASK_GET_INFO_READY;
}
void open_cfw_freertos_task_suspend_all(void) { suspends++; }
open_cfw_freertos_task_get_info_u32 open_cfw_freertos_task_resume_all(void) {
    resumes++; return 1;
}
open_cfw_freertos_task_get_info_u16 open_cfw_freertos_task_check_free_stack_space(
    const open_cfw_freertos_task_get_info_u8 *stack) {
    assert(stack != 0); stack_calls++; return 77;
}

#include "runtime_freertos_task_get_info.c"

int main(void) {
    struct open_cfw_freertos_task_get_info_tcb current = {0}, other = {0};
    struct open_cfw_freertos_task_get_info_status out;
    unsigned char stack[8];
    open_cfw_test_current = &current;
    current.priority = 9; current.stack = stack; current.tcb_number = 12;
    current.base_priority = 4; memcpy(current.name, "current", 8);
    memset(&out, 0xA5, sizeof(out));
    open_cfw_freertos_task_get_info(0, &out, 1,
        OPEN_CFW_FREERTOS_TASK_GET_INFO_INVALID);
    assert(out.handle == &current && out.name == current.name);
    assert(out.current_priority == 9 && out.task_number == 12);
    assert(out.base_priority == 4 && out.run_time_counter == 0);
    assert(out.stack_base == stack && out.stack_high_water_mark == 77);
    assert(out.current_state == OPEN_CFW_FREERTOS_TASK_GET_INFO_READY);
    assert(state_calls == 1 && stack_calls == 1);

    memset(&out, 0, sizeof(out));
    open_cfw_freertos_task_get_info(&current, &out, 0,
        OPEN_CFW_FREERTOS_TASK_GET_INFO_SUSPENDED);
    assert(out.current_state == OPEN_CFW_FREERTOS_TASK_GET_INFO_RUNNING);
    assert(out.stack_high_water_mark == 0 && suspends == 0 && resumes == 0);

    other.event_list_item.container = &other;
    open_cfw_freertos_task_get_info(&other, &out, 0,
        OPEN_CFW_FREERTOS_TASK_GET_INFO_SUSPENDED);
    assert(out.current_state == OPEN_CFW_FREERTOS_TASK_GET_INFO_BLOCKED);
    assert(suspends == 1 && resumes == 1);
    other.event_list_item.container = 0;
    open_cfw_freertos_task_get_info(&other, &out, 0,
        OPEN_CFW_FREERTOS_TASK_GET_INFO_SUSPENDED);
    assert(out.current_state == OPEN_CFW_FREERTOS_TASK_GET_INFO_SUSPENDED);
    assert(suspends == 2 && resumes == 2);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness_path = root / "harness.c"
            binary = root / "task-get-info"
            harness_path.write_text(harness, encoding="utf-8")
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE.parent), str(harness_path), "-o", str(binary),
                ],
                check=True, capture_output=True, text=True,
            )
            subprocess.run([str(binary)], check=True)

    def test_stock_span_is_pinned(self) -> None:
        image = OFFICIAL.read_bytes()[32:]
        body = image[START - BASE:END - BASE]
        self.assertEqual(len(body), 128)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)

    def test_production_routing_is_exact(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = [x for x in config["relocated_leaves"] if x["function"] == FUNCTION]
        patches = [x for x in config["patch_sites"] if x.get("target_function") == FUNCTION]
        self.assertEqual(len(leaves), 1)
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]["runtime_address"], START)
        self.assertEqual(patches[0]["expected_size"], END - START)
        self.assertEqual(patches[0]["expected_sha256"], STOCK_SHA256)
        self.assertEqual(patches[0]["branch"], "b_w")

    def test_source_is_pinned_by_overlay(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaf = next(x for x in config["relocated_leaves"] if x["function"] == FUNCTION)
        for path in (SOURCE, HEADER):
            self.assertTrue(path.read_bytes())
        self.assertEqual(leaf["source"]["size"], SOURCE.stat().st_size)
        self.assertEqual(leaf["source"]["sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
