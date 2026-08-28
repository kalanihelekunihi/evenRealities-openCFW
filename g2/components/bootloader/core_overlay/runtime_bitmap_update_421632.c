/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader bitmap update helper. */

typedef __UINT8_TYPE__ open_cfw_bitmap_update_u8;
typedef __UINT32_TYPE__ open_cfw_bitmap_update_u32;

#ifndef OPEN_CFW_BOOTLOADER_BITMAP_UPDATE_TABLE
#define OPEN_CFW_BOOTLOADER_BITMAP_UPDATE_TABLE \
    ((volatile open_cfw_bitmap_update_u32 (*)[2])0x20026E74U)
#endif

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BITMAP_UPDATE_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BITMAP_UPDATE_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_BITMAP_UPDATE_ATTR
open_cfw_bitmap_update_u32 open_cfw_bootloader_bitmap_update_421632(
    open_cfw_bitmap_update_u32 selector,
    open_cfw_bitmap_update_u32 bit,
    open_cfw_bitmap_update_u32 enabled)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r4, r5}\n"
        "movs r3, r0\n"
        "uxtb r3, r3\n"
        "cmp r3, #7\n"
        "bge 1f\n"
        "movs r3, r1\n"
        "uxtb r3, r3\n"
        "cmp r3, #0x39\n"
        "blt 2f\n"
        "1:\n"
        "movs r0, #6\n"
        "b 5f\n"
        "2:\n"
        "movs r3, r1\n"
        "uxtb r3, r3\n"
        "lsrs r3, r3, #5\n"
        "ands r1, r1, #0x1f\n"
        "uxtb r2, r2\n"
        "cmp r2, #0\n"
        "beq 3f\n"
        "ldr.w r2, [pc, #0xbb4]\n"
        "movs r4, r0\n"
        "uxtb r4, r4\n"
        "add.w r4, r2, r4, lsl #3\n"
        "movs r5, r3\n"
        "uxtb r5, r5\n"
        "uxtb r0, r0\n"
        "add.w r0, r2, r0, lsl #3\n"
        "uxtb r3, r3\n"
        "ldr.w r0, [r0, r3, lsl #2]\n"
        "movs r2, #1\n"
        "lsls.w r1, r2, r1\n"
        "orrs r1, r0\n"
        "str.w r1, [r4, r5, lsl #2]\n"
        "b 4f\n"
        "3:\n"
        "ldr.w r2, [pc, #0xb8c]\n"
        "movs r4, r0\n"
        "uxtb r4, r4\n"
        "add.w r4, r2, r4, lsl #3\n"
        "movs r5, r3\n"
        "uxtb r5, r5\n"
        "uxtb r0, r0\n"
        "add.w r0, r2, r0, lsl #3\n"
        "uxtb r3, r3\n"
        "ldr.w r0, [r0, r3, lsl #2]\n"
        "movs r2, #1\n"
        "lsls.w r1, r2, r1\n"
        "bics.w r1, r0, r1\n"
        "str.w r1, [r4, r5, lsl #2]\n"
        "4:\n"
        "movs r0, #0\n"
        "5:\n"
        "pop {r4, r5}\n"
        "bx lr\n");
#else
    open_cfw_bitmap_update_u8 row = (open_cfw_bitmap_update_u8)selector;
    open_cfw_bitmap_update_u8 narrowed_bit = (open_cfw_bitmap_update_u8)bit;
    open_cfw_bitmap_update_u8 word;
    open_cfw_bitmap_update_u32 mask;
    open_cfw_bitmap_update_u32 value;

    if (row >= 7U || narrowed_bit >= 57U) {
        return 6U;
    }
    word = (open_cfw_bitmap_update_u8)(narrowed_bit >> 5U);
    mask = (open_cfw_bitmap_update_u32)1U << (bit & 0x1FU);
    value = OPEN_CFW_BOOTLOADER_BITMAP_UPDATE_TABLE[row][word];
    if ((open_cfw_bitmap_update_u8)enabled != 0U) {
        value |= mask;
    } else {
        value &= ~mask;
    }
    OPEN_CFW_BOOTLOADER_BITMAP_UPDATE_TABLE[row][word] = value;
    return 0U;
#endif
}
