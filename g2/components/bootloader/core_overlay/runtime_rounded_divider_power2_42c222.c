/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room realizations of the rounded-divider and power-of-two
 * helpers authenticated at G2 bootloader addresses 0x0042C222 and 0x0042C256.
 */

typedef __UINT32_TYPE__ open_cfw_divider_u32;
typedef __UINT8_TYPE__ open_cfw_divider_u8;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_divider_u32 open_cfw_bootloader_rounded_divider_42c222(
    open_cfw_divider_u32 numerator __attribute__((unused)),
    open_cfw_divider_u32 exponent __attribute__((unused)),
    open_cfw_divider_u32 multiplier_a __attribute__((unused)),
    open_cfw_divider_u32 multiplier_b __attribute__((unused)),
    open_cfw_divider_u32 multiplier_c __attribute__((unused)))
{
    __asm volatile(
        "push {r4, r5, r6}\n"
        "movs r4, r0\n"
        "ldr r5, [sp, #12]\n"
        "movs r6, #1\n"
        "subs r0, r1, #1\n"
        "lsls r6, r0\n"
        "lsls r2, r2, #1\n"
        "adds r2, r2, #1\n"
        "mul r2, r2, r6\n"
        "muls r3, r5, r3\n"
        "adds r3, r3, #1\n"
        "muls r2, r3, r2\n"
        "udiv r0, r4, r2\n"
        "udiv r1, r4, r2\n"
        "mls r4, r2, r1, r4\n"
        "lsrs r2, r2, #1\n"
        "cmp r2, r4\n"
        "bhs.n .Lrounded_done\n"
        "adds r0, r0, #1\n"
        "b.n .Lrounded_done\n"
        ".Lrounded_done:\n"
        "pop {r4, r5, r6}\n"
        "bx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_divider_u8 open_cfw_bootloader_is_power_of_two_42c256(
    open_cfw_divider_u32 value __attribute__((unused)))
{
    __asm volatile(
        "cmp r0, #0\n"
        "beq.n .Lpower2_false\n"
        "subs r1, r0, #1\n"
        "tst r0, r1\n"
        "bne.n .Lpower2_false\n"
        "movs r0, #1\n"
        "b.n .Lpower2_done\n"
        ".Lpower2_false:\n"
        "movs r0, #0\n"
        ".Lpower2_done:\n"
        "uxtb r0, r0\n"
        "bx lr\n"
    );
}

#else

__attribute__((used, noinline, visibility("default")))
open_cfw_divider_u32 open_cfw_bootloader_rounded_divider_42c222(
    open_cfw_divider_u32 numerator, open_cfw_divider_u32 exponent,
    open_cfw_divider_u32 multiplier_a, open_cfw_divider_u32 multiplier_b,
    open_cfw_divider_u32 multiplier_c)
{
    open_cfw_divider_u32 denominator =
        ((multiplier_a * 2U) + 1U) * (1U << (exponent - 1U));
    denominator *= (multiplier_c * multiplier_b) + 1U;
    return (numerator / denominator) +
        ((numerator % denominator) > (denominator >> 1U) ? 1U : 0U);
}

__attribute__((used, noinline, visibility("default")))
open_cfw_divider_u8 open_cfw_bootloader_is_power_of_two_42c256(
    open_cfw_divider_u32 value)
{
    return (open_cfw_divider_u8)
        ((value != 0U) && ((value & (value - 1U)) == 0U));
}

#endif
