// SPDX-License-Identifier: Apache-2.0
/*
 * GNU-link replacement for the IAR Region$$Table used by __iar_data_init3
 * (runtime/C3-startup/iar_cmain.c walks iar_region_table_base_75d3c8 ..
 * iar_region_table_limit_75d410). Stock rows are zero-init + LZ77 copy rows
 * produced by the IAR linker; under GNU ld we emit the same row ABI
 * (row[0] = handler - &row[0], Thumb bit set; handler gets &row[1] and
 * returns the next row) with one plain copy row for .data and one zero row
 * for .bss. The stock LZ77 row at 0x75d3e0 targets ITCM 0x40; the GNU
 * replacement copies the same 24-byte source-defined helper image there.
 * A further plain copy row loads Ambiq .itcm_text / .ramfunc from their
 * MRAM LMA into ITCM VMA (>= 0x58), matching stock .textrw. Symbols come
 * from g2/src/apollo-main/link/g2-apollo-main.ld.
 * Not stock behaviour (openCFW GNU completion).
 *
 * Fix 43 (RAM-init, 2026-11-01): stock cstartup zero-inits DTCM through
 * 0x20075048 (crash_data.c, ring_persist_backing_storage.c). Under GNU ld the
 * named .data/.dtcm_bss objects do not fill DTCM up to the CSTACK base, so the
 * span [__dtcm_bss_end, _sstack=0x2007d000) was unowned and never cleared:
 * zero in the Renode simulator, random on hardware. Several hand copies read
 * stock DTCM literals (0x200742d4, 0x20073704, 0x20073ff0, 0x20074603..0x200747a0)
 * that fall in this gap and expect a stock-zeroed cell. The extra zero row
 * below clears the gap (and only the gap: the region is unowned, and the live
 * MSP stack sits above 0x2007d000), reproducing stock boot state on hardware.
 */
#include <stdint.h>

/* Stock ITCM 0x40..0x58: countdown at 0x41, no-op at 0x47, word copy at
 * 0x49, no-op at 0x57. Keep this contiguous: calls use the ITCM addresses. */
__attribute__((naked, used, section(".text.g2c_itcm_overlay")))
void g2c_itcm_countdown(uint32_t count)
{
    __asm__ volatile (
        ".global g2c_itcm_overlay_start\n\t"
        "g2c_itcm_overlay_start:\n\t"
        "1: subs r0, #1\n\t"
        "bne 1b\n\t"
        "bx lr\n\t"
        "bx lr\n\t"
        "2: ldr r3, [r0], #4\n\t"
        "str r3, [r1], #4\n\t"
        "subs r2, #1\n\t"
        "bne 2b\n\t"
        "bx lr\n\t"
        "bx lr\n\t"
        ".global g2c_itcm_overlay_end\n\t"
        "g2c_itcm_overlay_end:\n\t"
    );
}

const uint32_t *g2c_copy_init3(const uint32_t *rec);
const uint32_t *g2c_zero_init3(const uint32_t *rec);

const uint32_t *g2c_copy_init3(const uint32_t *rec)
{
    const uint32_t *src = (const uint32_t *)(uintptr_t)rec[0];
    uint32_t *dst = (uint32_t *)(uintptr_t)rec[1];
    uint32_t *end = (uint32_t *)(uintptr_t)rec[2];
    while (dst < end) *dst++ = *src++;
    return rec + 3;
}

const uint32_t *g2c_zero_init3(const uint32_t *rec)
{
    uint32_t *dst = (uint32_t *)(uintptr_t)rec[0];
    uint32_t *end = (uint32_t *)(uintptr_t)rec[1];
    while (dst < end) *dst++ = 0;
    return rec + 2;
}

__asm__(
    "  .section .rodata.g2c_region_table,\"a\"\n"
    "  .p2align 2\n"
    "  .global iar_region_table_base_75d3c8\n"
    "iar_region_table_base_75d3c8:\n"
    "  .word g2c_copy_init3 - .\n"
    "  .word g2c_itcm_overlay_start, 0x40, 0x58\n"
    "  .word g2c_copy_init3 - .\n"
    "  .word __itcm_text_load_start, __itcm_text_start, __itcm_text_end\n"
    "  .word g2c_copy_init3 - .\n"
    "  .word __data_load_start, __data_start, __data_end\n"
    "  .word g2c_zero_init3 - .\n"
    "  .word __bss_start, __bss_end\n"
    "  .word g2c_zero_init3 - .\n"
    "  .word __dtcm_bss_start, __dtcm_bss_end\n" /* Fix 42 */
    "  .word g2c_zero_init3 - .\n"
    "  .word __dtcm_bss_end, _sstack\n" /* Fix 43: zero the unowned DTCM gap */
    "  .global iar_region_table_limit_75d410\n"
    "iar_region_table_limit_75d410:\n"
    "  .text\n");
