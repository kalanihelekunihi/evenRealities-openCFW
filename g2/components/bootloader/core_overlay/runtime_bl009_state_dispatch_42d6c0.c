/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room state-flag dispatcher authenticated at G2
 * bootloader address 0x0042D6C0.
 *
 * The dispatcher lives inside the retained span
 * 0x0042D5C2..0x0042D84C (BL-009), between the trim-state leaves
 * (ending 0x0042D6C0) and the shared literal pool (starting
 * 0x0042D79E). It takes no arguments, returns 0, issues no calls,
 * and publishes three retained SRAM state-flag bytes from one
 * peripheral mode register and two SRAM state words:
 *
 * - flag byte one is set iff the low byte of the 0x4002000C trim-block
 *   state register reads 0x21 while the state word reads 2;
 * - flag byte two is set iff (mode 0x21, state 2 or 3) or
 *   (mode 0x22, state 0);
 * - flag byte three is set iff (mode 0x22, state 1) or (mode 0x23,
 *   state 0, and the guarded status predicate is clear). The
 *   predicate reads the status word, masks it with 0x3FE00000,
 *   and requires a zero low halfword plus either a masked match of
 *   0x31800000 with bits 20:16 at or above 0x14, or bits 29:25 at
 *   or above 0x19.
 *
 * The body is byte-identical to its Apollo main analogue at
 * 0x005A08E4, which corroborates the reconstruction. The literal
 * cells it reads (SRAM flag/state addresses, the register address,
 * and the field mask) stay outside this leaf: the peripheral
 * address and mask are routed as in-place data beside this file,
 * while the unattributed SRAM-address cells stay retained per the
 * pool rule, and the portable model below takes every address-fed
 * value as a parameter.
 */

typedef __UINT8_TYPE__ open_cfw_dispatch_u8;
typedef __UINT32_TYPE__ open_cfw_dispatch_u32;

#define OPEN_CFW_DISPATCH_MODE_ONE 0x21u
#define OPEN_CFW_DISPATCH_MODE_TWO 0x22u
#define OPEN_CFW_DISPATCH_MODE_THREE 0x23u
#define OPEN_CFW_DISPATCH_FIELD_MASK 0x3FE00000u
#define OPEN_CFW_DISPATCH_FIELD_MATCH 0x31800000u
#define OPEN_CFW_DISPATCH_MID_FLOOR 0x14u
#define OPEN_CFW_DISPATCH_HIGH_FLOOR 0x19u

#if defined(__arm__) || defined(__thumb__)

/* Publishes the three state-flag bytes; always returns 0. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_dispatch_u32 open_cfw_bootloader_state_flag_dispatch_42d6c0(void)
{
    __asm volatile(
        "movs r0, #0\n"
        "ldr r2, [pc, #0x170]\n"
        "ldr r1, [r2]\n"
        "and.w r1, r1, #0xff\n"
        "cmp r1, #0x21\n"
        "bne .Lopen_cfw_dispatch_first_else\n"
        "ldr r1, [pc, #0x168]\n"
        "ldr r1, [r1]\n"
        "cmp r1, #2\n"
        "bne .Lopen_cfw_dispatch_first_else\n"
        "movs r1, #1\n"
        "ldr r3, [pc, #0x134]\n"
        "strb r1, [r3]\n"
        "b .Lopen_cfw_dispatch_first_done\n"
        ".Lopen_cfw_dispatch_first_else:\n"
        "movs r1, #0\n"
        "ldr r3, [pc, #0x12c]\n"
        "strb r1, [r3]\n"
        ".Lopen_cfw_dispatch_first_done:\n"
        "ldr r1, [r2]\n"
        "and.w r1, r1, #0xff\n"
        "cmp r1, #0x21\n"
        "bne .Lopen_cfw_dispatch_second_next\n"
        "ldr r1, [pc, #0x148]\n"
        "ldr r1, [r1]\n"
        "cmp r1, #2\n"
        "beq .Lopen_cfw_dispatch_second_set\n"
        ".Lopen_cfw_dispatch_second_next:\n"
        "ldr r1, [r2]\n"
        "and.w r1, r1, #0xff\n"
        "cmp r1, #0x21\n"
        "bne .Lopen_cfw_dispatch_second_alt\n"
        "ldr r1, [pc, #0x134]\n"
        "ldr r1, [r1]\n"
        "cmp r1, #3\n"
        "beq .Lopen_cfw_dispatch_second_set\n"
        ".Lopen_cfw_dispatch_second_alt:\n"
        "ldr r1, [r2]\n"
        "and.w r1, r1, #0xff\n"
        "cmp r1, #0x22\n"
        "bne .Lopen_cfw_dispatch_second_else\n"
        "ldr r1, [pc, #0x124]\n"
        "ldr r1, [r1]\n"
        "cmp r1, #0\n"
        "bne .Lopen_cfw_dispatch_second_else\n"
        ".Lopen_cfw_dispatch_second_set:\n"
        "movs r1, #1\n"
        "ldr r3, [pc, #0x8c]\n"
        "strb r1, [r3]\n"
        "b .Lopen_cfw_dispatch_second_done\n"
        ".Lopen_cfw_dispatch_second_else:\n"
        "movs r1, #0\n"
        "ldr r3, [pc, #0x84]\n"
        "strb r1, [r3]\n"
        ".Lopen_cfw_dispatch_second_done:\n"
        "ldr r1, [r2]\n"
        "and.w r1, r1, #0xff\n"
        "cmp r1, #0x22\n"
        "bne .Lopen_cfw_dispatch_third_next\n"
        "ldr r1, [pc, #0x104]\n"
        "ldr r1, [r1]\n"
        "cmp r1, #1\n"
        "beq .Lopen_cfw_dispatch_third_set\n"
        ".Lopen_cfw_dispatch_third_next:\n"
        "ldr r1, [r2]\n"
        "and.w r1, r1, #0xff\n"
        "cmp r1, #0x23\n"
        "bne .Lopen_cfw_dispatch_third_else\n"
        "ldr r1, [pc, #0xf0]\n"
        "ldr r1, [r1]\n"
        "cmp r1, #0\n"
        "bne .Lopen_cfw_dispatch_third_else\n"
        "ldr r2, [pc, #0xec]\n"
        "ldr r3, [r2, #0x44]\n"
        "ldr r1, [pc, #0xec]\n"
        "ands r3, r1\n"
        "cmp.w r3, #0x31800000\n"
        "bne .Lopen_cfw_dispatch_guard_high\n"
        "ldr r1, [r2, #0x44]\n"
        "ubfx r1, r1, #16, #5\n"
        "cmp r1, #0x14\n"
        "blt .Lopen_cfw_dispatch_guard_high\n"
        "ldr r1, [r2, #0x44]\n"
        "lsls r1, r1, #16\n"
        "beq .Lopen_cfw_dispatch_guard_set\n"
        ".Lopen_cfw_dispatch_guard_high:\n"
        "ldr r1, [r2, #0x44]\n"
        "ubfx r1, r1, #25, #5\n"
        "cmp r1, #0x19\n"
        "blt .Lopen_cfw_dispatch_guard_one\n"
        "ldr r1, [r2, #0x44]\n"
        "lsls r1, r1, #16\n"
        "beq .Lopen_cfw_dispatch_guard_zero\n"
        ".Lopen_cfw_dispatch_guard_one:\n"
        "movs r1, #1\n"
        "b .Lopen_cfw_dispatch_guard_flip\n"
        ".Lopen_cfw_dispatch_guard_zero:\n"
        "movs r1, #0\n"
        ".Lopen_cfw_dispatch_guard_flip:\n"
        "eors.w r1, r1, #1\n"
        "b .Lopen_cfw_dispatch_guard_join\n"
        ".Lopen_cfw_dispatch_guard_set:\n"
        "movs r1, #1\n"
        ".Lopen_cfw_dispatch_guard_join:\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "bne .Lopen_cfw_dispatch_third_else\n"
        ".Lopen_cfw_dispatch_third_set:\n"
        "movs r1, #1\n"
        "ldr r2, [pc, #0xb0]\n"
        "strb r1, [r2]\n"
        "b .Lopen_cfw_dispatch_third_done\n"
        ".Lopen_cfw_dispatch_third_else:\n"
        "movs r1, #0\n"
        "ldr r2, [pc, #0xa8]\n"
        "strb r1, [r2]\n"
        ".Lopen_cfw_dispatch_third_done:\n"
        "bx lr\n"
    );
}

#else

__attribute__((used, noinline, visibility("default")))
open_cfw_dispatch_u32 open_cfw_bootloader_state_flag_dispatch_42d6c0_portable(
    open_cfw_dispatch_u32 mode_reg, open_cfw_dispatch_u32 state,
    open_cfw_dispatch_u32 status, open_cfw_dispatch_u8 *first,
    open_cfw_dispatch_u8 *second, open_cfw_dispatch_u8 *third)
{
    open_cfw_dispatch_u32 mode = mode_reg & 0xFFu;
    open_cfw_dispatch_u32 set_third;

    *first = (open_cfw_dispatch_u8)(
        (mode == OPEN_CFW_DISPATCH_MODE_ONE && state == 2u) ? 1u : 0u);

    *second = (open_cfw_dispatch_u8)(
        ((mode == OPEN_CFW_DISPATCH_MODE_ONE && state == 2u) ||
         (mode == OPEN_CFW_DISPATCH_MODE_ONE && state == 3u) ||
         (mode == OPEN_CFW_DISPATCH_MODE_TWO && state == 0u))
            ? 1u
            : 0u);

    if (mode == OPEN_CFW_DISPATCH_MODE_TWO && state == 1u) {
        set_third = 1u;
    } else if (mode == OPEN_CFW_DISPATCH_MODE_THREE && state == 0u) {
        open_cfw_dispatch_u32 masked = status & OPEN_CFW_DISPATCH_FIELD_MASK;
        open_cfw_dispatch_u32 mid = (status >> 16) & 0x1Fu;
        open_cfw_dispatch_u32 high = (status >> 25) & 0x1Fu;
        open_cfw_dispatch_u32 low_clear = ((status & 0xFFFFu) == 0u) ? 1u : 0u;
        open_cfw_dispatch_u32 mid_hit =
            (masked == OPEN_CFW_DISPATCH_FIELD_MATCH &&
             mid >= OPEN_CFW_DISPATCH_MID_FLOOR && low_clear != 0u)
                ? 1u
                : 0u;
        open_cfw_dispatch_u32 high_hit =
            (high >= OPEN_CFW_DISPATCH_HIGH_FLOOR && low_clear != 0u) ? 1u
                                                                      : 0u;
        set_third = (mid_hit == 0u && high_hit == 0u) ? 1u : 0u;
    } else {
        set_third = 0u;
    }
    *third = (open_cfw_dispatch_u8)set_third;
    return 0u;
}

#endif
