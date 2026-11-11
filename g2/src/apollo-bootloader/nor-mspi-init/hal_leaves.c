/* SPDX-License-Identifier: MIT
 * Out-of-line CMSIS NVIC_EnableIRQ / NVIC_SetPriority as the IAR build emits
 * them (4-bit priority field). The MSPI leaves that lived here are upstream
 * am_hal_mspi.c.
 */
#include <stdint.h>
void opencfw_bl_interrupt_enable(uint32_t number) {
    int32_t irq = (int16_t)number;
    if (irq >= 0)
        *(volatile uint32_t *)(uintptr_t)
            (0xe000e100u + ((uint32_t)irq >> 5) * 4u) =
            1u << (number & 31u);
}
void opencfw_bl_interrupt_priority(uint32_t number, uint32_t priority) {
    int32_t irq = (int16_t)number;
    uintptr_t address = irq < 0 ?
        0xe000ed14u + ((uint32_t)irq & 15u) :
        0xe000e400u + (uint32_t)irq;
    *(volatile uint8_t *)address = (uint8_t)(priority << 4);
}
