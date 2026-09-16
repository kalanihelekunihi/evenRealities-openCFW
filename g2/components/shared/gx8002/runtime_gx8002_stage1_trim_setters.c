/* SPDX-License-Identifier: MIT */
/* Recovered SPL trim-state writes, package 0x397f4 and 0x3980c.
 * Each compound assignment must retain its own volatile read/write pair. */
#include <stdint.h>
#define TRIM_STATE (*(volatile uint32_t *)(uintptr_t)0xa0010030u)
void open_cfw_gx8002_stage1_397f4(unsigned value)
{
    TRIM_STATE &= ~1u;
    TRIM_STATE |= value & 1u;
}
void open_cfw_gx8002_stage1_3980c(unsigned value)
{
    uint32_t cleared = TRIM_STATE;
    /* GCC emits four-byte ANDNI for this mask. The stock two-byte BCLRI
     * preserves the 24-byte entry envelope. This is source assembly, not
     * extracted firmware bytes; the entire function is execution-checked. */
    __asm__("bclri %0, 1" : "+r" (cleared));
    TRIM_STATE = cleared;
    TRIM_STATE |= (value & 1u) << 1;
}
