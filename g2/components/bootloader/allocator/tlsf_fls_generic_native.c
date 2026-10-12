/* SPDX-License-Identifier: BSD-3-Clause
 * Stock 0x4169a4..0x4169e2 uses the TLSF v3.1 generic highest-set-bit
 * algorithm. The selected Clang build takes TLSF's compiler-builtin branch,
 * so this explicit source body owns the stock generic branch separately.
 */
#include <stdint.h>

int opencfw_boot_tlsf_fls_generic(uint32_t word)
{
    int bit = 32;
    if (word == 0u) --bit;
    if ((word & UINT32_C(0xffff0000)) == 0u) { word <<= 16; bit -= 16; }
    if ((word & UINT32_C(0xff000000)) == 0u) { word <<= 8; bit -= 8; }
    if ((word & UINT32_C(0xf0000000)) == 0u) { word <<= 4; bit -= 4; }
    if ((word & UINT32_C(0xc0000000)) == 0u) { word <<= 2; bit -= 2; }
    if ((word & UINT32_C(0x80000000)) == 0u) { word <<= 1; bit -= 1; }
    return bit;
}

/* Stock 0x4169f2..0x4169fc is the pinned generic TLSF branch's fls
 * wrapper. Keep it explicit because target Clang selects another branch. */
int opencfw_boot_tlsf_fls_native(uint32_t word)
{
    return opencfw_boot_tlsf_fls_generic(word) - 1;
}

/* Stock 0x4169e2..0x4169f2 is the distinct ffs wrapper. */
int opencfw_boot_tlsf_ffs_native(uint32_t word)
{
    return opencfw_boot_tlsf_fls_generic(word & (0u - word)) - 1;
}
