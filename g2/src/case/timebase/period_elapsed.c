/* SPDX-License-Identifier: MIT
 * Stock 0x08005e18..0x08005e28: application HAL_TIM_PeriodElapsedCallback
 * (CubeMX main.c form), reached from HAL_TIM_IRQHandler 0x08005c90 on the
 * update event. TIM17 (0x40014800) is the HAL timebase, so only it ticks.
 */
#include <stdint.h>

extern void case_boot_clock_accumulate_tick(void); /* 0x08004edc HAL_IncTick */

/* Stock 0x08005E18 (case_run_if_token) */
void case_run_if_token(const uint32_t *htim)
{
    /* htim word 0 is the TIM_TypeDef instance pointer. */
    if (htim[0] == 0x40014800u)
        case_boot_clock_accumulate_tick();
}
