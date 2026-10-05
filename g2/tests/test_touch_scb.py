from __future__ import annotations

import shutil
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/foundation/touch_scb"
SOURCE = COMPONENT / "touch_scb.c"
HEADER_DIR = COMPONENT
ORIGINAL_RESULTS = ROOT / "analysis/shortcut-batch-2026-10-05/touch-upstream/results.json"
EXPANDED_RESULTS = COMPONENT / "validation/results.json"


HARNESS = r'''#include "touch_scb.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

typedef struct { uint32_t status; unsigned status_calls; unsigned transfer_calls;
                 uint32_t last_count; void *last_scb; void *last_dst; } fixture_t;
static uint32_t status_cb(void *opaque, void *scb) {
    fixture_t *f = (fixture_t *)opaque; ++f->status_calls; f->last_scb = scb;
    return f->status;
}
static void transfer_cb(void *opaque, void *scb, void *dst, uint32_t count) {
    fixture_t *f = (fixture_t *)opaque; ++f->transfer_calls; f->last_scb = scb;
    f->last_dst = dst; f->last_count = count;
}
static void reset(fixture_t *f, uint32_t status) {
    f->status=status;f->status_calls=0;f->transfer_calls=0;f->last_count=0;
    f->last_scb=0;f->last_dst=0;
}
int main(void) {
    fixture_t f = {0};
    touch_scb_io_t io = {&f, status_cb, transfer_cb};
    uint32_t actual=0xdeadbeefu;
    uint32_t scb_word=0;
    void *scb=&scb_word;
    uint8_t dst[8]={0};
    const uint32_t status[]={0u,0u,3u,3u,0x12340003u,0xffffffffu,3u,2u};
    const uint32_t requested[]={0u,5u,2u,9u,9u,0x300u,3u,0xffffffffu};
    const uint32_t expected[]={0u,0u,2u,3u,3u,511u,3u,2u};
    unsigned i;

    for(i=0;i<8;i++) {
        reset(&f,status[i]);
        actual=touch_scb_read_array(&io,scb,dst,requested[i]);
        assert(actual==expected[i]);
        assert(f.status_calls==1 && f.transfer_calls==1);
        assert(f.last_scb==scb && f.last_dst==dst);
        assert(f.last_count==expected[i]);
        printf("ORIGINAL %u %08x %u %u\n",i,status[i],requested[i],actual);
    }

    reset(&f,0x12340003u);
    assert(touch_scb_read_array_checked(&io,scb,dst,
        sizeof(dst),1,9,&actual)==TOUCH_SCB_OK);
    assert(actual==3 && f.status_calls==1 && f.transfer_calls==1 && f.last_count==3);
    printf("ADAPTER width1 ok\n");

    reset(&f,3u); actual=99;
    assert(touch_scb_read_array_checked(&io,scb,dst,
        sizeof(dst),2,9,&actual)==TOUCH_SCB_OK);
    assert(actual==3 && f.transfer_calls==1 && f.last_count==3);
    printf("ADAPTER width2 ok\n");

    reset(&f,3u); actual=99;
    assert(touch_scb_read_array_checked(&io,scb,dst,
        5,2,9,&actual)==TOUCH_SCB_INSUFFICIENT_CAPACITY);
    assert(f.status_calls==1 && f.transfer_calls==0 && actual==99);
    printf("ADAPTER capacity error\n");

    reset(&f,3u); actual=99;
    assert(touch_scb_read_array_checked(&io,scb,dst,
        sizeof(dst),4,9,&actual)==TOUCH_SCB_INVALID_WIDTH);
    assert(f.status_calls==0 && f.transfer_calls==0 && actual==99);
    printf("ADAPTER width error\n");

    reset(&f,3u); actual=99;
    assert(touch_scb_read_array_checked(0,scb,dst,
        sizeof(dst),2,9,&actual)==TOUCH_SCB_INVALID_ARGUMENT);
    assert(f.status_calls==0 && f.transfer_calls==0 && actual==99);
    printf("ADAPTER argument error\n");

    reset(&f,0u); actual=99;
    assert(touch_scb_read_array_checked(&io,scb,dst,0,1,9,&actual)==TOUCH_SCB_OK);
    assert(actual==0 && f.status_calls==1 && f.transfer_calls==1 && f.last_count==0);
    printf("ADAPTER zero-capacity empty success\n");

    reset(&f,1u); actual=99;
    { touch_scb_io_t missing_status={&f,0,transfer_cb};
      assert(touch_scb_read_array_checked(&missing_status,scb,dst,sizeof(dst),1,1,&actual)==TOUCH_SCB_INVALID_ARGUMENT); }
    assert(f.status_calls==0 && f.transfer_calls==0 && actual==99);
    printf("ADAPTER missing status callback\n");

    reset(&f,1u); actual=99;
    { touch_scb_io_t missing_transfer={&f,status_cb,0};
      assert(touch_scb_read_array_checked(&missing_transfer,scb,dst,sizeof(dst),1,1,&actual)==TOUCH_SCB_INVALID_ARGUMENT); }
    assert(f.status_calls==0 && f.transfer_calls==0 && actual==99);
    printf("ADAPTER missing transfer callback\n");
    return 0;
}
'''


@unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
class TouchScbTests(unittest.TestCase):
    def test_host_behavior_matches_original_and_heldout_cases_and_adapter_edges(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-") as temp:
            td = Path(temp)
            harness = td / "harness.c"
            binary = td / "harness"
            harness.write_text(HARNESS)
            built = subprocess.run(
                ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-I", str(HEADER_DIR), str(SOURCE), str(harness), "-o", str(binary)],
                capture_output=True, text=True,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("ORIGINAL 0 00000000 0 0", run.stdout)
            self.assertIn("ORIGINAL 5 ffffffff 768 511", run.stdout)
            self.assertIn("ADAPTER capacity error", run.stdout)
            self.assertIn("ADAPTER width error", run.stdout)
            self.assertIn("ADAPTER argument error", run.stdout)
            self.assertIn("ADAPTER zero-capacity empty success", run.stdout)
            self.assertIn("ADAPTER missing status callback", run.stdout)
            self.assertIn("ADAPTER missing transfer callback", run.stdout)
            prior = json.loads(ORIGINAL_RESULTS.read_text())
            result = json.loads(EXPANDED_RESULTS.read_text())
            self.assertEqual(prior["case_count"], 6)
            self.assertEqual(result["case_count"], 8)
            self.assertEqual(result["cases"][:6], prior["cases"])
            actual_lines = [line.split() for line in run.stdout.splitlines()
                            if line.startswith("ORIGINAL ")]
            self.assertEqual(len(actual_lines), result["case_count"])
            for line, case in zip(actual_lines, result["cases"]):
                self.assertEqual(int(line[1]), case["index"])
                self.assertEqual(int(line[2], 16), int(case["status"], 16))
                self.assertEqual(int(line[3]), case["requested"])
                self.assertEqual(int(line[4]), case["return_value"])

    def test_armv6m_freestanding_object_compiles(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-arm-") as temp:
            obj = Path(temp) / "touch_scb.o"
            result = subprocess.run(
                ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                 "-ffreestanding", "-fno-builtin", "-std=c11", "-Wall", "-Wextra",
                 "-Werror", "-I", str(HEADER_DIR), "-c", str(SOURCE), "-o", str(obj)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(obj.is_file())
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
