/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_clkgen_ctrl_candidate.h"

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_retained_delay_us_41d1c0(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r7, r2\n"
        "movs r5, r3\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "uxtb r6, r6\n"
        "cmp r6, #0\n"
        "beq 3f\n"
        "uxtb r7, r7\n"
        "cmp r7, #0\n"
        "beq 2f\n"
        "ldr.w r1, [pc, #0x7e8]\n"
        "ldr r0, [r1]\n"
        "movs r2, #0x1e\n"
        "movs r3, #5\n"
        "mul r3, r3, r4\n"
        "lsls r2, r3\n"
        "bics r0, r2\n"
        "uxtb r5, r5\n"
        "lsls r5, r5, #1\n"
        "movs r2, #5\n"
        "mul r2, r2, r4\n"
        "lsls r5, r2\n"
        "orrs r5, r0\n"
        "str r5, [r1]\n"
        "2:\n"
        "ldr.w r1, [pc, #0x7c8]\n"
        "ldr r2, [r1]\n"
        "movs r3, #1\n"
        "movs r0, #5\n"
        "muls r4, r0, r4\n"
        "lsls.w r4, r3, r4\n"
        "orrs r4, r2\n"
        "str r4, [r1]\n"
        "movs r0, #10\n"
        "bl open_cfw_bootloader_retained_delay_us_41d1c0\n"
        "b 4f\n"
        "3:\n"
        "ldr.w r1, [pc, #0x7ac]\n"
        "ldr r2, [r1]\n"
        "movs r3, #1\n"
        "movs r0, #5\n"
        "muls r4, r0, r4\n"
        "lsls.w r4, r3, r4\n"
        "bics.w r4, r2, r4\n"
        "str r4, [r1]\n"
        "4:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "pop {r0, r4, r5, r6, r7, pc}\n");
}
#else
void open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(
    uint32_t module, uint32_t enable, uint32_t configure, uint32_t clock_select,
    const open_cfw_mspi_clkgen_ports *ports)
{
    const uint32_t token = ports->critical_save(ports->context);
    const uint32_t shift = module * 5U;
    uint32_t value = ports->read_reg(ports->context, 0x40004110U);
    if ((uint8_t)enable != 0U) {
        if ((uint8_t)configure != 0U) {
            value &= ~(0x1EU << shift);
            value |= (((uint32_t)(uint8_t)clock_select << 1U) << shift);
            ports->write_reg(ports->context, 0x40004110U, value);
        }
        value |= 1U << shift;
        ports->write_reg(ports->context, 0x40004110U, value);
        ports->delay_us(ports->context, 10U);
    } else {
        value &= ~(1U << shift);
        ports->write_reg(ports->context, 0x40004110U, value);
    }
    ports->critical_restore(ports->context, token);
}
#endif
