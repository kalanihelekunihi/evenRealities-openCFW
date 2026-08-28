/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance clock-divider service. */

typedef __UINT32_TYPE__ open_cfw_hwcd_u32;
typedef __UINT64_TYPE__ open_cfw_hwcd_u64;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_u64_divmod_42287c(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_clock_divider_422e28(void)
{
    __asm__ volatile(
        "push.w {r4, r5, r6, r7, r8, lr}\n"
        "movs r5, r0\n"
        "mov r12, r1\n"
        "mov r8, r2\n"
        "ldr.w r7, [pc, #0x60c]\n"
        "adds.w r0, r7, r5, lsl #12\n"
        "ldr r0, [r0, #0x30]\n"
        "lsrs r0, r0, #4\n"
        "ands r0, r0, #7\n"
        "cmp r0, #1\n"
        "beq 2f\n"
        "blo 7f\n"
        "cmp r0, #3\n"
        "beq 4f\n"
        "blo 3f\n"
        "cmp r0, #5\n"
        "beq 1f\n"
        "blo 5f\n"
        "cmp r0, #6\n"
        "bne 7f\n"
        "ldr.w r6, [pc, #0x9d8]\n"
        "6:\n"
        "lsls.w r12, r12, #4\n"
        "udiv r4, r6, r12\n"
        "movs r0, r6\n"
        "movs r1, #0\n"
        "lsls r1, r1, #6\n"
        "orr.w r1, r1, r0, lsr #26\n"
        "lsls r0, r0, #6\n"
        "mov r2, r12\n"
        "movs r3, #0\n"
        "bl open_cfw_bootloader_u64_divmod_42287c\n"
        "movs r2, r4\n"
        "movs r3, #0\n"
        "lsls r3, r3, #6\n"
        "orr.w r3, r3, r2, lsr #26\n"
        "lsls r2, r2, #6\n"
        "subs r0, r0, r2\n"
        "sbcs r1, r3\n"
        "cmp r4, #0\n"
        "bne 8f\n"
        "movs r0, #0\n"
        "str.w r0, [r8]\n"
        "ldr.w r0, [pc, #0x9a4]\n"
        "b 9f\n"
        "1:\n"
        "ldr.w r6, [pc, #0x9a0]\n"
        "b 6b\n"
        "2:\n"
        "ldr.w r6, [pc, #0x9a0]\n"
        "b 6b\n"
        "3:\n"
        "ldr.w r6, [pc, #0x99c]\n"
        "b 6b\n"
        "4:\n"
        "ldr.w r6, [pc, #0x99c]\n"
        "b 6b\n"
        "5:\n"
        "ldr.w r6, [pc, #0x848]\n"
        "b 6b\n"
        "7:\n"
        "movs r0, #0\n"
        "str.w r0, [r8]\n"
        "ldr.w r0, [pc, #0x98c]\n"
        "b 9f\n"
        "8:\n"
        "adds.w r1, r7, r5, lsl #12\n"
        "str r4, [r1, #0x24]\n"
        "adds.w r7, r7, r5, lsl #12\n"
        "str r0, [r7, #0x28]\n"
        "lsrs r0, r0, #2\n"
        "adds.w r0, r0, r4, lsl #4\n"
        "udiv r0, r6, r0\n"
        "str.w r0, [r8]\n"
        "movs r0, #0\n"
        "9:\n"
        "pop.w {r4, r5, r6, r7, r8, pc}\n");
}
#else
extern open_cfw_hwcd_u32 open_cfw_hwcd_host_registers[4][32];

open_cfw_hwcd_u32 open_cfw_bootloader_hw_clock_divider_422e28(
    open_cfw_hwcd_u32 index,
    open_cfw_hwcd_u32 requested,
    open_cfw_hwcd_u32 *actual)
{
    static const open_cfw_hwcd_u32 references[7] = {
        0U, 24000000U, 12000000U, 6000000U,
        3000000U, 48000000U, 49152000U
    };
    open_cfw_hwcd_u32 mode = (open_cfw_hwcd_host_registers[index][12] >> 4) & 7U;
    open_cfw_hwcd_u32 reference;
    open_cfw_hwcd_u32 divisor;
    open_cfw_hwcd_u32 integer;
    open_cfw_hwcd_u32 fraction;
    open_cfw_hwcd_u64 quotient;
    if (mode == 0U || mode == 7U) {
        *actual = 0U;
        return 0x08000002U;
    }
    reference = references[mode];
    divisor = requested << 4;
    if (divisor == 0U) {
        *actual = 0U;
        return 0x08000003U;
    }
    integer = reference / divisor;
    quotient = ((open_cfw_hwcd_u64)reference << 6) / divisor;
    fraction = (open_cfw_hwcd_u32)(quotient - ((open_cfw_hwcd_u64)integer << 6));
    if (integer == 0U) {
        *actual = 0U;
        return 0x08000003U;
    }
    open_cfw_hwcd_host_registers[index][9] = integer;
    open_cfw_hwcd_host_registers[index][10] = fraction;
    divisor = (fraction >> 2) + (integer << 4);
    *actual = reference / divisor;
    return 0U;
}
#endif
