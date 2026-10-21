/* SPDX-License-Identifier: MIT
 * Main 0x48009e: IRQ controller enable sequence.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);
extern void audio_delay_us_selected(uint32_t);

uint64_t g2_main_irq_enable_48009e(void)
{
    const uint32_t saved = g2_main_critical_save_473940();
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    *control |= UINT32_C(0x80000000);
    *control |= UINT32_C(0x40000000);
    if ((*(const volatile uint32_t *)(uintptr_t)UINT32_C(0x4002000c) &
         0xffu) > 0x21u) {
        audio_delay_us_selected(1u);
        volatile uint32_t *const advanced =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0x400201b0);
        *advanced |= UINT32_C(0x00200000);
    }
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    return (uint64_t)saved << 32;
}
