/* SPDX-License-Identifier: MIT
 * Main 0x539944 queue uninitialization and 0x4800e4 IRQ-state read.
 * IRQ enable at 0x48009e remains an explicit downstream provider gate.
 */
#include <stdint.h>

extern uint32_t g2_main_queue_disable_539a10(uint32_t);
extern uint64_t g2_main_irq_enable_48009e(void);

uint32_t g2_main_irq_enabled_4800e4(uint8_t *enabled)
{
    const uint32_t control =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    *enabled = (uint8_t)(((control >> 31) & 1u) ^ 1u);
    return 0u;
}

uint64_t g2_main_queue_uninit_539944(uint32_t queue,
                                      uint32_t unused,
                                      uint32_t third, uint32_t high)
{
    (void)unused;
    (void)third;
    if (queue == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)queue & UINT32_C(0x01ffffff)) !=
         UINT32_C(0x01504c30))
        return ((uint64_t)high << 32) | 2u;

    high &= UINT32_C(0xffffff00);
    if ((*(const volatile uint32_t *)(uintptr_t)queue &
         UINT32_C(0x02000000)) != 0u)
        (void)g2_main_queue_disable_539a10(queue);
    (void)g2_main_irq_enabled_4800e4((uint8_t *)&high);
    if ((high & 0xffu) != 0u)
        (void)g2_main_irq_enable_48009e();
    *(volatile uint32_t *)(uintptr_t)queue &= UINT32_C(0xfeffffff);
    return (uint64_t)high << 32;
}
