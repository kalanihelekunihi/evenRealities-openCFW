/* SPDX-License-Identifier: BSD-3-Clause */
/* Source-equivalent adapter for AmbiqSuite 5.1.0 sched_hiprio. */

extern void open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_mspi_cq_pause_423fb8(void);
extern void open_cfw_bootloader_mspi_program_dma_42403e(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_sched_hiprio_4240aa(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r6, r0\n"
        "movs r7, r1\n"
        "movs r5, #0\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "ldr.w r4, [r6, #0x840]\n"
        "ldr.w r0, [r6, #0x840]\n"
        "adds r7, r7, r0\n"
        "str.w r7, [r6, #0x840]\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "cmp r4, #0\n"
        "bne 2f\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_mspi_cq_pause_423fb8\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "movs r0, #0\n"
        "str r0, [r6, #0x24]\n"
        "ldr.w r0, [pc, #0xaf8]\n"
        "ldr r1, [r6, #4]\n"
        "adds.w r1, r0, r1, lsl #12\n"
        "movs r2, #0x40\n"
        "str.w r2, [r1, #0x208]\n"
        "ldr r1, [r6, #4]\n"
        "adds.w r1, r0, r1, lsl #12\n"
        "ldr r2, [r6, #4]\n"
        "adds.w r0, r0, r2, lsl #12\n"
        "ldr.w r0, [r0, #0x200]\n"
        "orrs r0, r0, #0x40\n"
        "str.w r0, [r1, #0x200]\n"
        "movs r0, #1\n"
        "strb.w r0, [r6, #0x83c]\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_mspi_program_dma_42403e\n"
        "movs r5, r0\n"
        "cmp r5, #0\n"
        "beq 2f\n"
        "movs r0, r5\n"
        "b 3f\n"
        "2:\n"
        "movs r0, r5\n"
        "3:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n");
}
