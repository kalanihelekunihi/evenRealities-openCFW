/* SPDX-License-Identifier: MIT
 * Main 0x470368: bounded MX25U status polling. The status query, scheduler
 * state, scheduler delay and microsecond delay remain named lower contracts.
 */
#include <stdint.h>

extern uint32_t g2_norflash_status_busy_4702d8(void);
extern void g2_norflash_delay_us_491102(uint32_t microseconds);
extern uint32_t g2_norflash_scheduler_state_44906c(void);
extern void g2_norflash_scheduler_delay_449376(uint32_t ticks);

uint32_t g2_norflash_wait_status_470368(uint32_t timeout_ticks)
{
    for (uint32_t attempt = 0; attempt < 200u; ++attempt) {
        if (g2_norflash_status_busy_4702d8() == 0u) return 0u;
        g2_norflash_delay_us_491102(5u);
    }
    for (uint32_t attempt = 0; attempt < timeout_ticks; ++attempt) {
        if (g2_norflash_scheduler_state_44906c() == 2u)
            g2_norflash_scheduler_delay_449376(1u);
        else
            g2_norflash_delay_us_491102(1000u);
        if (g2_norflash_status_busy_4702d8() == 0u) return 0u;
    }
    return 1u;
}
