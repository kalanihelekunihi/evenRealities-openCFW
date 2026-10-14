/* SPDX-License-Identifier: MIT
 * Main 0x4c0758: route MSPI serial clock through CLKGEN peripheral field.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);
extern void audio_delay_us_selected(uint32_t);

uint32_t g2_main_mspi_clock_route_4c0758(uint32_t module,
                                           uint32_t enable,
                                           uint32_t set_divider,
                                           uint32_t divider)
{
    const uint32_t previous_mask = g2_main_critical_save_473940();
    volatile uint32_t *const clock_reg =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40004110);
    const uint32_t shift = module * 5u;
    const uint32_t gate = shift < 32u ? UINT32_C(1) << shift : 0u;
    if ((uint8_t)enable == 0u) {
        *clock_reg &= ~gate;
    } else {
        if ((uint8_t)set_divider != 0u) {
            const uint32_t mask = shift < 32u ? 0x1eu << shift : 0u;
            const uint32_t value = shift < 32u ?
                (((uint32_t)(uint8_t)divider << 1) << shift) : 0u;
            *clock_reg = (*clock_reg & ~mask) | value;
        }
        *clock_reg |= gate;
        audio_delay_us_selected(10u);
    }
    __asm__ volatile("msr primask, %0" :: "r"(previous_mask) : "memory");
    return previous_mask;
}
