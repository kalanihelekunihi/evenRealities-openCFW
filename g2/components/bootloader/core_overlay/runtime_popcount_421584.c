/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader 32-bit population count. */

typedef __UINT32_TYPE__ open_cfw_popcount_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
open_cfw_popcount_u32 open_cfw_bootloader_popcount_421584(
    open_cfw_popcount_u32 value)
{
    __asm__ volatile(
        "movs r1, r0\n"
        "lsrs r1, r1, #1\n"
        "bics.w r1, r1, #0xaaaaaaaa\n"
        "subs r0, r0, r1\n"
        "bics.w r1, r0, #0xcccccccc\n"
        "lsrs r0, r0, #2\n"
        "bics.w r0, r0, #0xcccccccc\n"
        "adds r0, r0, r1\n"
        "adds.w r0, r0, r0, lsr #4\n"
        "bics.w r0, r0, #0xf0f0f0f0\n"
        "movs.w r1, #0x01010101\n"
        "muls r0, r1, r0\n"
        "lsrs r0, r0, #24\n"
        "uxtb r0, r0\n"
        "bx lr\n");
}
#else
__attribute__((used, noinline))
open_cfw_popcount_u32 open_cfw_bootloader_popcount_421584(
    open_cfw_popcount_u32 value)
{
    value = value - ((value >> 1U) & 0x55555555U);
    value = (value & 0x33333333U) + ((value >> 2U) & 0x33333333U);
    value = (value + (value >> 4U)) & 0x0F0F0F0FU;
    return (value * 0x01010101U) >> 24U;
}
#endif
