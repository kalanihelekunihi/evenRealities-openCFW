/* SPDX-License-Identifier: MIT */
/* Recovered GX8002 analog LDO register leaf.
 * The NationalChip SDK's drivers_lib/analog/ldo.o identifies the ABI and the
 * sentinel-skip/mask/byte-narrow algorithm below. The pinned toolchain's C
 * lowering of that algorithm picks a different (but equivalent) mask
 * instruction and result register than the stock object, so -- as with
 * gx_dcache_disable (runtime_gx8002_dcache_disable.c) -- the reviewed
 * upstream algorithm is pinned as inline assembly instead of C. Every
 * mnemonic, register and immediate below is the disassembled stock body,
 * authenticated byte-for-byte against the pinned SDK's
 * drivers_lib/analog/ldo.o in verify_gx8002_analog_ldo.py. A voltage code of
 * UINT32_MAX ("no change") leaves the register untouched and is returned
 * unchanged instead of a zero success code, matching the stock leaf.
 */
#include "runtime_gx8002_analog_ldo.h"

int gx_analog_set_ldo_ana_voltage(uint32_t voltage)
{
    register uint32_t result __asm__("r0") = voltage;
    __asm__ volatile (
        "movi r3, 0\n\t"
        "subi r3, 1\n\t"          /* r3 = UINT32_MAX */
        "cmpne r0, r3\n\t"        /* C = (voltage != UINT32_MAX) */
        "bf 1f\n\t"               /* skip the register write when voltage == UINT32_MAX */
        "lrw r2, 0xa0005000\n\t"  /* r2 = LDO analog control block base */
        "ld.w r3, (r2, 0x54)\n\t" /* r3 = previous control byte */
        "andi r3, r3, 240\n\t"    /* r3 &= 0xf0 (keep the upper nibble) */
        "or r0, r3\n\t"           /* r0 = voltage | (previous & 0xf0) */
        "zextb r0, r0\n\t"        /* narrow to the register's byte width */
        "st.w r0, (r2, 0x54)\n\t" /* write back the merged control byte */
        "movi r0, 0\n\t"          /* success */
        "1:\n\t"
        : "+r"(result) : : "r2", "r3"
    );
    return (int)result;
}
