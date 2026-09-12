/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room power-trim gate helpers authenticated at G2
 * bootloader addresses 0x0042BD8C, 0x0042BDA0 and 0x0042BDBC.
 *
 * The three helpers are tiny leaves inside the retained span
 * 0x0042B9BA..0x0042BDF0 (BL-009), between the hardware-state decoder
 * and the stored-entry composer. Each is entered through the
 * 0x0041D150 dispatch vector (stored Thumb entries 0x0042BD8D,
 * 0x0042BDA1 and 0x0042BDBD at vector indices 8, 9 and 10) and each
 * is instruction-identical to its Apollo main analogue (0x005A1BBC,
 * 0x005A1BCC, 0x005A1BEC; only the literal-pool offsets differ, and
 * the main pools hold the same semantic values). None of the three
 * calls another function.
 *
 * Semantics: the first helper writes the fixed value 6 into bits
 * 29:25 of the 0x4002034C peripheral register and reports success
 * (0). The other two share one compare gate: they read a state word
 * through the retained SRAM pointer cell 0x0042BFCC and compare it
 * against the 0x1F01600D packed-config word (cell 0x0042BFD0). On a
 * match the second publishes bits 9:0 of the LDOREG1 power-trim
 * register (0x40020080, cell 0x0042C020) from the state word at gate
 * offset 0x20 shifted right by 7, and the third publishes bits 5:0
 * of 0x40020088 (cell 0x0042C024) from the state word at gate offset
 * 0x68 shifted right by 2 plus bits 16:15 of the global-control
 * register 0x400201B0 (cell 0x0042C028) from the low two bits of
 * that same word; both report success (0) either way.
 *
 * The four-byte pad at 0x0042BD9C, the SRAM gate-pointer cell, the
 * shared literal pools and the opaque BL-005 caller of the first
 * span function stay retained and are explicitly out of scope here.
 */

typedef __UINT8_TYPE__ open_cfw_hwstate_u8;
typedef __UINT32_TYPE__ open_cfw_hwstate_u32;

#define OPEN_CFW_HWSTATE_FIELD_MASK 0x3E000000u
#define OPEN_CFW_HWSTATE_FIELD_VALUE (6u << 25)
#define OPEN_CFW_HWSTATE_GATE_EXPECT 0x1F01600Du
#define OPEN_CFW_HWSTATE_LDO_MASK 0x3FFu
#define OPEN_CFW_HWSTATE_FIRST_MASK 0x3Fu
#define OPEN_CFW_HWSTATE_SECOND_SHIFT 15u

#if defined(__arm__) || defined(__thumb__)

/* Writes 6 into bits 29:25 of the 0x4002034C register. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hwstate_u32 open_cfw_bootloader_hwstate_field_publish_42bd8c(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x54]\n"
        "movs r1, #6\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0x19, #5\n"
        "str r2, [r0]\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* Guarded LDOREG1 low-ten-bit publish from the gate state word. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hwstate_u32 open_cfw_bootloader_trim_gate_publish_42bda0(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x228]\n"
        "ldr r1, [r0]\n"
        "ldr r2, [pc, #0x228]\n"
        "cmp r1, r2\n"
        "bne .Lopen_cfw_gate_publish_done\n"
        "ldr r1, [pc, #0x274]\n"
        "ldr r0, [r0, #0x20]\n"
        "lsrs r0, r0, #7\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #0, #0xa\n"
        "str r2, [r1]\n"
        ".Lopen_cfw_gate_publish_done:\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

/* Guarded two-register field publish from the gate state word. */
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hwstate_u32 open_cfw_bootloader_trim_gate_fields_set_42bdbc(void)
{
    __asm volatile(
        "ldr r0, [pc, #0x20c]\n"
        "ldr r1, [r0]\n"
        "ldr r2, [pc, #0x20c]\n"
        "cmp r1, r2\n"
        "bne .Lopen_cfw_gate_fields_done\n"
        "ldr r1, [pc, #0x25c]\n"
        "ldr r2, [r0, #0x68]\n"
        "lsrs r2, r2, #2\n"
        "ldr r3, [r1]\n"
        "bfi r3, r2, #0, #6\n"
        "str r3, [r1]\n"
        "ldr r1, [pc, #0x250]\n"
        "ldr r0, [r0, #0x68]\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #0xf, #2\n"
        "str r2, [r1]\n"
        ".Lopen_cfw_gate_fields_done:\n"
        "movs r0, #0\n"
        "bx lr\n"
    );
}

#else

__attribute__((used, noinline, visibility("default")))
open_cfw_hwstate_u32 open_cfw_bootloader_hwstate_field_publish_42bd8c_portable(
    open_cfw_hwstate_u32 *reg)
{
    *reg = (*reg & ~OPEN_CFW_HWSTATE_FIELD_MASK) | OPEN_CFW_HWSTATE_FIELD_VALUE;
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_hwstate_u32 open_cfw_bootloader_trim_gate_publish_42bda0_portable(
    open_cfw_hwstate_u32 gate_word, open_cfw_hwstate_u32 src_word,
    open_cfw_hwstate_u32 *ldo)
{
    if (gate_word == OPEN_CFW_HWSTATE_GATE_EXPECT) {
        open_cfw_hwstate_u32 field = (src_word >> 7) & OPEN_CFW_HWSTATE_LDO_MASK;
        *ldo = (*ldo & ~OPEN_CFW_HWSTATE_LDO_MASK) | field;
    }
    return 0u;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_hwstate_u32 open_cfw_bootloader_trim_gate_fields_set_42bdbc_portable(
    open_cfw_hwstate_u32 gate_word, open_cfw_hwstate_u32 src_word,
    open_cfw_hwstate_u32 *first, open_cfw_hwstate_u32 *second)
{
    if (gate_word == OPEN_CFW_HWSTATE_GATE_EXPECT) {
        *first = (*first & ~OPEN_CFW_HWSTATE_FIRST_MASK) |
            ((src_word >> 2) & OPEN_CFW_HWSTATE_FIRST_MASK);
        *second = (*second & ~(3u << OPEN_CFW_HWSTATE_SECOND_SHIFT)) |
            ((src_word & 3u) << OPEN_CFW_HWSTATE_SECOND_SHIFT);
    }
    return 0u;
}

#endif
