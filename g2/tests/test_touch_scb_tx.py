from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/foundation/touch_scb"

HARNESS = r'''#include "touch_scb_tx.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

enum { CONFIG=0x000, CTRL=0x200, STATUS=0x208, FIFO_WR=0x240, REG_BYTES=0x300 };
static _Alignas(4) uint8_t regs[REG_BYTES];
static volatile uint32_t *r32(uintptr_t base, unsigned off) {
    return (volatile uint32_t *)(base+off);
}
static void setup(uint32_t config,uint32_t ctrl,uint32_t status,uint32_t fifo) {
    unsigned i; for(i=0;i<REG_BYTES;i++) regs[i]=0;
    *r32((uintptr_t)regs,CONFIG)=config;
    *r32((uintptr_t)regs,CTRL)=ctrl;
    *r32((uintptr_t)regs,STATUS)=status;
    *r32((uintptr_t)regs,FIFO_WR)=fifo;
}
int main(void) {
    const uintptr_t base=(uintptr_t)regs;
    uint32_t actual=0xdeadbeefu;
    uint8_t bytes[8]={0x91,0x82,0x73,0x64,0xa5,0xb6,0xc7,0xd8};

    setup(0,0,0xffff000cu,0xeeeeeeeeu); /* depth 16, used 12 => 4 free */
    actual=touch_scb_mmio_write_array(base,bytes,7);
    assert(actual==4 && *r32(base,FIFO_WR)==0x00000064u);
    printf("depth16 byte writes clamp and truncate ok\n");

    {
        _Alignas(2) uint16_t halfwords[5]={0x1234,0x5678,0x9abc,0xdef0,0x8888};
        setup(0,0x08u,14u,0xeeeeeeeeu); /* depth 16, two free */
        actual=touch_scb_mmio_write_array(base,halfwords,5);
        assert(actual==2 && *r32(base,FIFO_WR)==0x00005678u);
    }
    printf("halfword writes clamp and truncate ok\n");

    setup(0x4000u,0x10u,6u,0xeeeeeeeeu); /* depth 8, two free */
    { _Alignas(2) uint16_t halfwords[3]={0x1111,0x2282,0x3373};
      actual=touch_scb_mmio_write_array(base,halfwords,5);
      assert(actual==2 && *r32(base,FIFO_WR)==0x00002282u); }
    printf("depth8 and alternate halfword-width bit ok\n");

    setup(0,0,16u,0x13579bdfu); /* full depth-16 FIFO */
    actual=touch_scb_mmio_write_array(base,bytes,8);
    assert(actual==0 && *r32(base,FIFO_WR)==0x13579bdfu);
    printf("full FIFO raw zero-count behavior ok\n");

    setup(0,0,17u,0xeeeeeeeeu); /* malformed used > depth */
    actual=touch_scb_mmio_write_array(base,bytes,2);
    assert(actual==2 && *r32(base,FIFO_WR)==0x00000082u); /* raw u32 underflow */
    printf("raw underflow behavior bounded by request ok\n");

    setup(0,0,17u,0x2468ace0u); actual=0xdeadbeefu;
    assert(touch_scb_mmio_write_array_checked(base,bytes,sizeof(bytes),2,&actual)==TOUCH_SCB_TX_INVALID_FIFO_STATUS);
    assert(actual==0xdeadbeefu && *r32(base,FIFO_WR)==0x2468ace0u);
    printf("checked malformed status rejects before write ok\n");

    setup(0,0x08u,15u,0x2468ace0u); actual=0xdeadbeefu;
    {
        _Alignas(2) uint16_t halfwords[2]={0x1111,0x2222};
        assert(touch_scb_mmio_write_array_checked(base,halfwords,1,1,&actual)==TOUCH_SCB_TX_INSUFFICIENT_CAPACITY);
        assert(actual==0xdeadbeefu && *r32(base,FIFO_WR)==0x2468ace0u);
        assert(touch_scb_mmio_write_array_checked(base,halfwords,4,1,&actual)==TOUCH_SCB_TX_OK);
        assert(actual==1 && *r32(base,FIFO_WR)==0x00001111u);
    }
    printf("checked halfword capacity and success ok\n");

    setup(0,0x08u,0u,0x2468ace0u); actual=0xdeadbeefu;
    assert(touch_scb_mmio_write_array_checked(base,bytes+1,sizeof(bytes)-1,1,&actual)==TOUCH_SCB_TX_INVALID_ALIGNMENT);
    assert(actual==0xdeadbeefu && *r32(base,FIFO_WR)==0x2468ace0u);
    printf("checked alignment rejects before write ok\n");

    setup(0,0,16u,0x2468ace0u); actual=0xdeadbeefu;
    assert(touch_scb_mmio_write_array_checked(base,bytes,sizeof(bytes),9,&actual)==TOUCH_SCB_TX_OK);
    assert(actual==0 && *r32(base,FIFO_WR)==0x2468ace0u);
    printf("checked full FIFO zero transfer ok\n");

    assert(touch_scb_mmio_write_array_checked(0,bytes,sizeof(bytes),1,&actual)==TOUCH_SCB_TX_INVALID_ARGUMENT);
    assert(touch_scb_mmio_write_array_checked(base+1,bytes,sizeof(bytes),1,&actual)==TOUCH_SCB_TX_INVALID_ARGUMENT);
    assert(touch_scb_mmio_write_array_checked(UINTPTR_MAX & ~(uintptr_t)3u,bytes,sizeof(bytes),1,&actual)==TOUCH_SCB_TX_INVALID_ARGUMENT);
    assert(touch_scb_mmio_write_array_checked(base,bytes,sizeof(bytes),1,0)==TOUCH_SCB_TX_INVALID_ARGUMENT);
    printf("checked invalid arguments ok\n");
    return 0;
}
'''


@unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
class TouchScbTxTests(unittest.TestCase):
    def test_simulated_tx_register_block(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-tx-") as temp:
            td = Path(temp)
            harness = td / "harness.c"
            binary = td / "harness"
            harness.write_text(HARNESS)
            build = subprocess.run(
                ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-I", str(COMPONENT), str(COMPONENT / "touch_scb_tx.c"),
                 str(harness), "-o", str(binary)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            for expected in (
                "depth16 byte writes clamp and truncate ok",
                "halfword writes clamp and truncate ok",
                "depth8 and alternate halfword-width bit ok",
                "full FIFO raw zero-count behavior ok",
                "raw underflow behavior bounded by request ok",
                "checked malformed status rejects before write ok",
                "checked halfword capacity and success ok",
                "checked alignment rejects before write ok",
                "checked full FIFO zero transfer ok",
                "checked invalid arguments ok",
            ):
                self.assertIn(expected, run.stdout)

    def test_armv6m_freestanding_compile(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-tx-arm-") as temp:
            obj = Path(temp) / "touch_scb_tx.o"
            result = subprocess.run(
                ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                 "-ffreestanding", "-fno-builtin", "-std=c11", "-Wall", "-Wextra",
                 "-Werror", "-I", str(COMPONENT), "-c",
                 str(COMPONENT / "touch_scb_tx.c"), "-o", str(obj)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
