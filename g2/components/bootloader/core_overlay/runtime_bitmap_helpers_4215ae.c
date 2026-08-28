/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader two-word bitmap helpers. */

typedef __UINT8_TYPE__ open_cfw_bitmap_u8;
typedef __UINT32_TYPE__ open_cfw_bitmap_u32;

#ifndef OPEN_CFW_BOOTLOADER_BITMAP_TABLE
#define OPEN_CFW_BOOTLOADER_BITMAP_TABLE \
    ((volatile open_cfw_bitmap_u32 (*)[2])0x20026E74U)
#endif

extern open_cfw_bitmap_u32 open_cfw_bootloader_popcount_421584(
    open_cfw_bitmap_u32 value);

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BITMAP_HELPER_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BITMAP_HELPER_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_BITMAP_HELPER_ATTR
open_cfw_bitmap_u32 open_cfw_bootloader_bitmap_any_4215ae(
    open_cfw_bitmap_u32 selector)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "movs r2, #0\n"
        "b 2f\n"
        "1:\n"
        "adds r2, r2, #1\n"
        "2:\n"
        "movs r1, r2\n"
        "uxtb r1, r1\n"
        "cmp r1, #2\n"
        "bge 4f\n"
        "ldr.w r1, [pc, #0xc50]\n"
        "movs r3, r0\n"
        "uxtb r3, r3\n"
        "add.w r1, r1, r3, lsl #3\n"
        "movs r3, r2\n"
        "uxtb r3, r3\n"
        "ldr.w r1, [r1, r3, lsl #2]\n"
        "cmp r1, #0\n"
        "beq 1b\n"
        "movs r0, #1\n"
        "b 5f\n"
        "4:\n"
        "movs r0, #0\n"
        "5:\n"
        "bx lr\n");
#else
    open_cfw_bitmap_u8 row = (open_cfw_bitmap_u8)selector;
    open_cfw_bitmap_u8 word;

    for (word = 0U; word < 2U; ++word) {
        if (OPEN_CFW_BOOTLOADER_BITMAP_TABLE[row][word] != 0U) {
            return 1U;
        }
    }
    return 0U;
#endif
}

OPEN_CFW_BITMAP_HELPER_ATTR
open_cfw_bitmap_u32 open_cfw_bootloader_bitmap_test_4215dc(
    open_cfw_bitmap_u32 selector,
    open_cfw_bitmap_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "movs r2, r1\n"
        "uxtb r2, r2\n"
        "lsrs r2, r2, #5\n"
        "ands r1, r1, #0x1f\n"
        "ldr.w r3, [pc, #0xc28]\n"
        "uxtb r0, r0\n"
        "add.w r0, r3, r0, lsl #3\n"
        "uxtb r2, r2\n"
        "ldr.w r0, [r0, r2, lsl #2]\n"
        "lsrs r0, r0, r1\n"
        "ands r0, r0, #1\n"
        "bx lr\n");
#else
    open_cfw_bitmap_u8 narrowed_bit = (open_cfw_bitmap_u8)bit;
    open_cfw_bitmap_u8 word = (open_cfw_bitmap_u8)(narrowed_bit >> 5U);
    open_cfw_bitmap_u8 shift = (open_cfw_bitmap_u8)(bit & 0x1FU);
    return (OPEN_CFW_BOOTLOADER_BITMAP_TABLE[(open_cfw_bitmap_u8)selector][word]
            >> shift) & 1U;
#endif
}

OPEN_CFW_BITMAP_HELPER_ATTR
open_cfw_bitmap_u32 open_cfw_bootloader_bitmap_count_4215fe(
    open_cfw_bitmap_u32 selector)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r4, r5, r6, lr}\n"
        "movs r4, r0\n"
        "movs r6, #0\n"
        "movs r5, #0\n"
        "b 2f\n"
        "1:\n"
        "ldr.w r0, [pc, #0xc04]\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "add.w r0, r0, r1, lsl #3\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "ldr.w r0, [r0, r1, lsl #2]\n"
        "bl open_cfw_bootloader_popcount_421584\n"
        "adds r6, r0, r6\n"
        "adds r5, r5, #1\n"
        "2:\n"
        "movs r0, r5\n"
        "uxtb r0, r0\n"
        "cmp r0, #2\n"
        "blt 1b\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "pop {r4, r5, r6, pc}\n");
#else
    open_cfw_bitmap_u8 row = (open_cfw_bitmap_u8)selector;
    open_cfw_bitmap_u32 count = 0U;
    open_cfw_bitmap_u8 word;

    for (word = 0U; word < 2U; ++word) {
        count += open_cfw_bootloader_popcount_421584(
            OPEN_CFW_BOOTLOADER_BITMAP_TABLE[row][word]);
    }
    return (open_cfw_bitmap_u8)count;
#endif
}
