/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room power-trim state helpers authenticated at G2
 * bootloader addresses 0x0042D5C2, 0x0042D5F8, 0x0042D61E, 0x0042D63A,
 * 0x0042D692 and 0x0042D6A6.
 *
 * Each helper is a tiny leaf inside the retained span
 * 0x0042D5C2..0x0042D84C (BL-009), between the byte-event state
 * dispatcher (ends 0x0042D5C2) and the stream-mode selection primitive
 * (starts 0x0042D84C). All six bodies are byte-identical to their
 * Apollo main analogues (0x005A07E6, 0x005A081C, 0x005A0842,
 * 0x005A085E, 0x005A08B6, 0x005A08CA), which corroborates the
 * reconstruction. None of the six calls another function; the
 * retained 0x0042D5CC neighbour (which calls opaque BL-005 code) is
 * explicitly out of scope here, as is the 0x0042D6C0 dispatcher.
 *
 * The helpers publish single state-flag bytes in retained SRAM and
 * program fields of the power-trim register block (0x40020080 is the
 * LDOREG1 register identified by the SPOTmgr transition closure;
 * 0x400201B0 is the global-control register; 0x400211A0..0x400211BC
 * is a six-word peripheral register block programmed with fixed
 * calibration constants). The literal pool they read lives at
 * 0x0042D79E..0x0042D848; the peripheral-address cells it holds are
 * routed as in-place data beside this file, while the unattributed
 * SRAM-address cells stay retained.
 */

typedef __UINT8_TYPE__ open_cfw_trim_u8;
typedef __UINT32_TYPE__ open_cfw_trim_u32;

#define OPEN_CFW_TRIM_LEVEL_FLOOR 8u
#define OPEN_CFW_TRIM_LEVEL_BIAS 7u
#define OPEN_CFW_TRIM_FIELD_MASK 0x3FFu
#define OPEN_CFW_TRIM_BLOCK_HIGH_16 16u

#if defined(__arm__) || defined(__thumb__)

/* Sets the retained state-flag byte and reports success (0). */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_state_flag_raise_42d5c2(void)
{
    __asm volatile(
        "movs r0, #1\n"
        "ldr r1, [pc, #0x1f4]\n"
        "strb r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* When the gate flag is set, publishes the level word (minus a fixed
 * bias once it clears the floor, else zero) into the low ten bits of
 * the trim register. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_field_publish_42d5f8(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x1a4]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_trim_publish_done\n"
        "ldr r0, [pc, #0x210]\n"
        "ldr r1, [r0]\n"
        "cmp r1, #8\n"
        "blo .Lopen_cfw_trim_publish_floor\n"
        "ldr r0, [r0]\n"
        "subs r0, r0, #7\n"
        "b .Lopen_cfw_trim_publish_store\n"
        ".Lopen_cfw_trim_publish_floor:\n"
        "movs r0, #0\n"
        ".Lopen_cfw_trim_publish_store:\n"
        "ldr r1, [pc, #0x1cc]\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #0, #0xa\n"
        "str r2, [r1]\n"
        ".Lopen_cfw_trim_publish_done:\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* Writes one fixed field into each of two trim registers. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_fields_set_42d61e(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x1c8]\n"
        "movs r1, #1\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #6\n"
        "str r2, [r0]\n"
        "ldr r0, [pc, #0x1d0]\n"
        "movs r1, #2\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0xf, #2\n"
        "str r2, [r0]\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* Programs the six-word trim register block with fixed calibration
 * constants and clears the low status bits of the head register. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_block_program_42d63a(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x1dc]\n"
        "ldr r1, [r0]\n"
        "bics.w r1, r1, #0x1f00\n"
        "str r1, [r0]\n"
        "mov.w r1, #0x3e8\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0x10, #0x10\n"
        "str r2, [r0]\n"
        "ldr r1, [pc, #0x1c8]\n"
        "ldr r2, [r1]\n"
        "movs r2, #0\n"
        "str r2, [r1]\n"
        "ldr r1, [pc, #0x1c4]\n"
        "ldr r2, [r1]\n"
        "mov.w r2, #0x320\n"
        "str r2, [r1]\n"
        "ldr r1, [pc, #0x1c0]\n"
        "ldr r2, [r1]\n"
        "mov.w r2, #0x1c2\n"
        "str r2, [r1]\n"
        "ldr r1, [pc, #0x1b8]\n"
        "ldr r2, [r1]\n"
        "mov.w r2, #0x258\n"
        "str r2, [r1]\n"
        "ldr r1, [pc, #0x1b4]\n"
        "ldr r2, [r1]\n"
        "movs r2, #0xfa\n"
        "str r2, [r1]\n"
        "ldr r1, [r0]\n"
        "bics.w r1, r1, #2\n"
        "str r1, [r0]\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #1\n"
        "lsls r1, r1, #1\n"
        "str r1, [r0]\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* Sets the low two status bits of the head trim register and raises
 * the retained state-flag byte. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_bits_raise_42d692(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x184]\n"
        "ldr r1, [r0]\n"
        "orrs.w r1, r1, #3\n"
        "str r1, [r0]\n"
        "movs r0, #1\n"
        "ldr r1, [pc, #0x190]\n"
        "strb r0, [r1]\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* When the retained state-flag byte is set, clears the low two status
 * bits of the head trim register and lowers the flag byte. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_bits_clear_42d6a6(void)
{
    __asm volatile(
        "ldr r1, [pc, #0x188]\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_trim_clear_done\n"
        "ldr r0, [pc, #0x168]\n"
        "ldr r2, [r0]\n"
        "lsrs r2, r2, #2\n"
        "lsls r2, r2, #2\n"
        "str r2, [r0]\n"
        "movs r0, #0\n"
        "strb r0, [r1]\n"
        ".Lopen_cfw_trim_clear_done:\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

#else

__attribute__((used, noinline, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_state_flag_raise_42d5c2_portable(
    open_cfw_trim_u8 *flag)
{
    *flag = 1u;
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_field_publish_42d5f8_portable(
    const open_cfw_trim_u8 *gate, const open_cfw_trim_u32 *level,
    open_cfw_trim_u32 *trim)
{
    if (*gate != 0u) {
        open_cfw_trim_u32 raw = *level;
        open_cfw_trim_u32 field =
            (raw >= OPEN_CFW_TRIM_LEVEL_FLOOR)
                ? (raw - OPEN_CFW_TRIM_LEVEL_BIAS)
                : 0u;
        *trim = (*trim & ~OPEN_CFW_TRIM_FIELD_MASK) |
            (field & OPEN_CFW_TRIM_FIELD_MASK);
    }
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_fields_set_42d61e_portable(
    open_cfw_trim_u32 *first, open_cfw_trim_u32 *second)
{
    *first = (*first & ~0x3Fu) | 1u;
    *second = (*second & ~(3u << 15)) | (2u << 15);
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_block_program_42d63a_portable(
    open_cfw_trim_u32 *head, open_cfw_trim_u32 *word_a,
    open_cfw_trim_u32 *word_b, open_cfw_trim_u32 *word_c,
    open_cfw_trim_u32 *word_d, open_cfw_trim_u32 *word_e)
{
    *head &= ~0x1F00u;
    *head = (*head & 0x0000FFFFu) |
        ((open_cfw_trim_u32)0x3E8u << OPEN_CFW_TRIM_BLOCK_HIGH_16);
    *word_a = 0u;
    *word_b = 0x320u;
    *word_c = 0x1C2u;
    *word_d = 0x258u;
    *word_e = 0xFAu;
    *head &= ~2u;
    *head &= ~1u;
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_bits_raise_42d692_portable(
    open_cfw_trim_u32 *head, open_cfw_trim_u8 *flag)
{
    *head |= 3u;
    *flag = 1u;
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_trim_u32 open_cfw_bootloader_trim_bits_clear_42d6a6_portable(
    open_cfw_trim_u8 *flag, open_cfw_trim_u32 *head)
{
    if (*flag != 0u) {
        *head &= ~3u;
        *flag = 0u;
    }
    return 0u;
}

#endif
