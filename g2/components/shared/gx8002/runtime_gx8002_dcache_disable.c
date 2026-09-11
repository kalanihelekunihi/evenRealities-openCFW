/* SPDX-License-Identifier: MIT */
/* Counterpart to gx_dcache_enable (runtime_gx8002_dcache_enable.c), which the
 * pinned Apache-2.0 C-SKY CSI header's csi_dcache_enable() already matches
 * byte for byte. The disable body is the same upstream algorithm --
 * CACHE->CER &= ~CACHE_CER_EN_Msk; CACHE->CIR = CACHE_CIR_INV_ALL_Msk; --
 * wrapped in __DSB()/__ISB() barriers, but the pinned toolchain's C
 * lowering of that single-bit AND-clear picks a different register
 * allocation and instruction (andni, not the stock object's bclri) than the
 * vendor build used. Editing the vendored header is not an option, so the
 * upstream algorithm is pinned as reviewed inline assembly instead of C:
 * every mnemonic, register and immediate below is the disassembled stock
 * body (see docs/research/gx8002-cache-source.md), authenticated
 * byte-for-byte against the pinned SDK's drivers_lib/cache/gx_dcache.o in
 * verify_gx8002_dcache_disable.py. No opaque/binary bytes are embedded;
 * this is assembly source, reviewed and compiled from that source.
 */

void gx_dcache_disable(void)
{
    __asm__ volatile (
        "sync\n\t"
        "sync\n\t"
        "lrw r3, 0xe000f000\n\t"   /* r3 = CACHE_BASE (TCIP_BASE + 0x1000) */
        "ld.w r2, (r3, 0x0)\n\t"   /* r2 = CACHE->CER */
        "bclri r2, 0\n\t"          /* r2 &= ~CACHE_CER_EN_Msk */
        "st.w r2, (r3, 0x0)\n\t"   /* CACHE->CER = r2 */
        "movi r2, 1\n\t"           /* r2 = CACHE_CIR_INV_ALL_Msk */
        "st.w r2, (r3, 0x4)\n\t"   /* CACHE->CIR = r2 */
        "sync\n\t"
        "sync\n\t"
        : : : "r2", "r3"
    );
}
