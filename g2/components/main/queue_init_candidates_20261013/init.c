/* SPDX-License-Identifier: MIT
 * Main 0x5398e0 queue initialization and 0x480058 IRQ reset.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);
extern void audio_delay_us_selected(uint32_t);

uint64_t g2_main_irq_disable_480058(void)
{
    const uint32_t saved = g2_main_critical_save_473940();
    if ((*(const volatile uint32_t *)(uintptr_t)UINT32_C(0x4002000c) &
         0xffu) > 0x21u) {
        volatile uint32_t *const advanced =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0x400201b0);
        *advanced &= UINT32_C(0xffdfffff);
        audio_delay_us_selected(1u);
    }
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    *control &= UINT32_C(0x7fffffff);
    *control &= UINT32_C(0xbfffffff);
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    audio_delay_us_selected(5u);
    return (uint64_t)saved << 32;
}

uint32_t g2_main_queue_init_5398e0(uint32_t instance,
                                     volatile uint32_t *output)
{
    if (instance != 0u) return 5u;
    if (output == 0) return 6u;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200740f4);
    if ((*state & UINT32_C(0x01000000)) != 0u) return 7u;
    *state |= UINT32_C(0x01000000);
    *state = (*state & UINT32_C(0xff000000)) | UINT32_C(0x00504c30);
    state[1] = 0u;
    (void)g2_main_irq_disable_480058();
    *output = UINT32_C(0x200740f4);
    return 0u;
}
