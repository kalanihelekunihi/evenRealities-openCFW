from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/foundation/touch_scb"

HARNESS = r'''#include "touch_scb_fifo.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

enum { CONFIG=0x000, RX_FIFO_CTRL=0x304, REG_BYTES=0x340 };
static _Alignas(4) uint8_t regs[REG_BYTES];
static volatile uint32_t *r32(uintptr_t base,unsigned off) {
    return (volatile uint32_t *)(base+off);
}
static void setup(uint32_t config,uint32_t control) {
    unsigned i;for(i=0;i<REG_BYTES;i++)regs[i]=0;
    *r32((uintptr_t)regs,CONFIG)=config;
    *r32((uintptr_t)regs,RX_FIFO_CTRL)=control;
}
int main(void) {
    uintptr_t base=(uintptr_t)regs;
    setup(0,0xa5c312e7u);
    assert(touch_scb_fifo_set_rx_level(base,0)==TOUCH_SCB_FIFO_OK);
    assert(*r32(base,RX_FIFO_CTRL)==0xa5c31200u);
    assert(touch_scb_fifo_set_rx_level(base,15)==TOUCH_SCB_FIFO_OK);
    assert(*r32(base,RX_FIFO_CTRL)==0xa5c3120fu);
    printf("depth16 low-byte field update and upper-bit preserve ok\n");

    setup(0x4000u,0xdeadbeefu);
    assert(touch_scb_fifo_set_rx_level(base,7)==TOUCH_SCB_FIFO_OK);
    assert(*r32(base,RX_FIFO_CTRL)==0xdeadbe07u);
    setup(0x8000u,0x01020304u);
    assert(touch_scb_fifo_set_rx_level(base,7)==TOUCH_SCB_FIFO_OK);
    assert(*r32(base,RX_FIFO_CTRL)==0x01020307u);
    printf("depth8 field update ok\n");

    setup(0,0x12345678u);
    assert(touch_scb_fifo_set_rx_level(base,16)==TOUCH_SCB_FIFO_INVALID_LEVEL);
    assert(*r32(base,RX_FIFO_CTRL)==0x12345678u);
    setup(0x4000u,0x87654321u);
    assert(touch_scb_fifo_set_rx_level(base,8)==TOUCH_SCB_FIFO_INVALID_LEVEL);
    assert(*r32(base,RX_FIFO_CTRL)==0x87654321u);
    assert(touch_scb_fifo_set_rx_level(base,0x101u)==TOUCH_SCB_FIFO_INVALID_LEVEL);
    assert(touch_scb_fifo_set_rx_level(base,UINT32_MAX)==TOUCH_SCB_FIFO_INVALID_LEVEL);
    assert(*r32(base,RX_FIFO_CTRL)==0x87654321u);
    printf("invalid levels leave register unchanged ok\n");

    assert(touch_scb_fifo_set_rx_level(0,0)==TOUCH_SCB_FIFO_INVALID_ARGUMENT);
    assert(touch_scb_fifo_set_rx_level(base+1,0)==TOUCH_SCB_FIFO_INVALID_ARGUMENT);
    assert(touch_scb_fifo_set_rx_level(UINTPTR_MAX & ~(uintptr_t)3u,0)==TOUCH_SCB_FIFO_INVALID_ARGUMENT);
    printf("invalid and overflowing bases rejected ok\n");
    return 0;
}
'''


@unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
class TouchScbFifoTests(unittest.TestCase):
    def test_simulated_rx_fifo_control(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-fifo-") as temp:
            td = Path(temp)
            harness = td / "harness.c"
            binary = td / "harness"
            harness.write_text(HARNESS)
            build = subprocess.run(
                ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-I", str(COMPONENT), str(COMPONENT / "touch_scb_fifo.c"),
                 str(harness), "-o", str(binary)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            for expected in (
                "depth16 low-byte field update and upper-bit preserve ok",
                "depth8 field update ok",
                "invalid levels leave register unchanged ok",
                "invalid and overflowing bases rejected ok",
            ):
                self.assertIn(expected, run.stdout)

    def test_armv6m_freestanding_compile(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-fifo-arm-") as temp:
            obj = Path(temp) / "touch_scb_fifo.o"
            result = subprocess.run(
                ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                 "-ffreestanding", "-fno-builtin", "-std=c11", "-Wall", "-Wextra",
                 "-Werror", "-I", str(COMPONENT), "-c",
                 str(COMPONENT / "touch_scb_fifo.c"), "-o", str(obj)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
