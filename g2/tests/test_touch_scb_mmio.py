from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/foundation/touch_scb"


HARNESS = r'''#include "touch_scb_mmio.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { CTRL=0x300, STATUS=0x308, FIFO=0x340, REG_BYTES=0x400 };
static _Alignas(4) uint8_t registers[REG_BYTES];
static volatile uint32_t *reg32(uintptr_t base, unsigned offset) {
    return (volatile uint32_t *)(base + offset);
}
static void reset(uint32_t ctrl, uint32_t status, uint32_t fifo) {
    memset(registers,0,sizeof(registers));
    *reg32((uintptr_t)registers,CTRL)=ctrl;
    *reg32((uintptr_t)registers,STATUS)=status;
    *reg32((uintptr_t)registers,FIFO)=fifo;
}
int main(void) {
    const uintptr_t base=(uintptr_t)registers;
    uint8_t guarded[8];
    uint8_t *dst=guarded+1;
    uint32_t actual=0xdeadbeefu;
    touch_scb_io_t io;

    memset(guarded,0xcc,sizeof(guarded));
    reset(0u,0xabcd0003u,0x123456abu);
    assert(touch_scb_mmio_bind(&io)==TOUCH_SCB_OK);
    assert(touch_scb_read_array(&io,(void *)base,dst,5)==3);
    assert(dst[0]==0xabu && dst[1]==0xabu && dst[2]==0xabu);
    assert(guarded[0]==0xcc && guarded[4]==0xcc);
    printf("byte mode low-byte truncation and guards ok\n");

    reset(0x08u,0x00000002u,0x123456abu);
    {
        _Alignas(2) uint16_t halfwords[4]={0xeeee,0xeeee,0xeeee,0xeeee};
        actual=touch_scb_mmio_read_array(base,halfwords,3);
        assert(actual==2 && halfwords[0]==0x56abu && halfwords[1]==0x56abu);
        assert(halfwords[2]==0xeeee && halfwords[3]==0xeeee);
    }
    printf("halfword mode low-half truncation and guard ok\n");

    reset(0x10u,0x00000001u,0x0000cdefu);
    {
        _Alignas(2) uint16_t halfword[2]={0xeeee,0xeeee};
        assert(touch_scb_mmio_read_array(base,halfword,10)==1);
        assert(halfword[0]==0xcdefu && halfword[1]==0xeeee);
    }
    printf("alternate halfword control bit and count clamp ok\n");

    reset(0u,0u,0x123456abu);
    memset(guarded,0xcc,sizeof(guarded));
    assert(touch_scb_mmio_read_array(base,dst,9)==0);
    assert(guarded[0]==0xcc && guarded[1]==0xcc && guarded[7]==0xcc);
    printf("zero available preserves destination ok\n");

    reset(0x08u,2u,0x123456abu); actual=0xdeadbeefu;
    {
        _Alignas(2) uint16_t halfwords[4]={0xeeee,0xeeee,0xeeee,0xeeee};
        assert(touch_scb_mmio_read_array_checked(base,halfwords,3,9,&actual)==TOUCH_SCB_INSUFFICIENT_CAPACITY);
        assert(actual==0xdeadbeefu && halfwords[0]==0xeeee && halfwords[1]==0xeeee);
    }
    printf("checked capacity failure leaves destination and output unchanged\n");

    reset(0x08u,1u,0x123456abu);
    assert(touch_scb_mmio_read_array_checked(base,dst,8,1,&actual)==TOUCH_SCB_INVALID_ARGUMENT);
    assert(actual==0xdeadbeefu && dst[0]==0xcc);
    printf("checked halfword alignment failure ok\n");

    reset(0u,0u,0x123456abu);
    assert(touch_scb_mmio_read_array_checked(base,dst,0,10,&actual)==TOUCH_SCB_OK);
    assert(actual==0 && dst[0]==0xcc);
    printf("checked zero-capacity no-data case ok\n");

    assert(touch_scb_mmio_read_array_checked(0,dst,8,1,&actual)==TOUCH_SCB_INVALID_ARGUMENT);
    assert(touch_scb_mmio_read_array_checked(base+1,dst,8,1,&actual)==TOUCH_SCB_INVALID_ARGUMENT);
    assert(touch_scb_mmio_read_array_checked(UINTPTR_MAX & ~(uintptr_t)3u,dst,8,1,&actual)==TOUCH_SCB_INVALID_ARGUMENT);
    assert(touch_scb_mmio_bind(0)==TOUCH_SCB_INVALID_ARGUMENT);
    printf("invalid base and bind arguments ok\n");
    return 0;
}
'''


@unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
class TouchScbMmioTests(unittest.TestCase):
    def test_simulated_register_block_and_guards(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-mmio-") as temp:
            td = Path(temp)
            harness = td / "harness.c"
            binary = td / "harness"
            harness.write_text(HARNESS)
            build = subprocess.run(
                ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-I", str(COMPONENT), str(COMPONENT / "touch_scb.c"),
                 str(COMPONENT / "touch_scb_mmio.c"), str(harness), "-o", str(binary)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            for expected in (
                "byte mode low-byte truncation and guards ok",
                "halfword mode low-half truncation and guard ok",
                "alternate halfword control bit and count clamp ok",
                "zero available preserves destination ok",
                "checked capacity failure leaves destination and output unchanged",
                "checked halfword alignment failure ok",
                "checked zero-capacity no-data case ok",
                "invalid base and bind arguments ok",
            ):
                self.assertIn(expected, run.stdout)

    def test_armv6m_freestanding_objects_compile(self):
        with tempfile.TemporaryDirectory(prefix="touch-scb-mmio-arm-") as temp:
            for source in ("touch_scb.c", "touch_scb_mmio.c"):
                obj = Path(temp) / f"{source}.o"
                result = subprocess.run(
                    ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                     "-ffreestanding", "-fno-builtin", "-std=c11", "-Wall", "-Wextra",
                     "-Werror", "-I", str(COMPONENT), "-c", str(COMPONENT / source),
                     "-o", str(obj)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
