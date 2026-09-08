/* SPDX-License-Identifier: MIT */
/* Recovered watchdog configuration. Clock gate and IRQ registration remain
 * external recovery dependencies; reset timeout is unused by stock. */
#include <stdint.h>
#include <stddef.h>
typedef int (*open_cfw_irq_handler)(int, void *);
extern open_cfw_irq_handler open_cfw_gx8002_watchdog_handler;
extern void open_cfw_gx8002_platform_gate(unsigned int, unsigned int);
extern void open_cfw_gx8002_request_irq(int, open_cfw_irq_handler, void *);
extern int open_cfw_gx8002_printf(const char *, ...);

int open_cfw_gx8002_watchdog_interrupt(int irq, void *private_data)
{
    int result = 0;
    if (open_cfw_gx8002_watchdog_handler)
        result = open_cfw_gx8002_watchdog_handler(irq, private_data);
    (void)*(volatile uint32_t *)(uintptr_t)0xA0700014U;
    return result;
}

void open_cfw_gx8002_watchdog_initialize(uint16_t reset_ms, uint16_t level_ms,
                                       open_cfw_irq_handler handler, void *private_data)
{
    (void)reset_ms;
    if (level_ms < 1000) {
        (void)open_cfw_gx8002_printf("level timout invalid\n");
        return;
    }
    open_cfw_gx8002_platform_gate(24, 1);
    unsigned seconds = level_ms / 1000U;
    unsigned setting;
    for (setting = 0; setting < 16; ++setting) {
        uint32_t raw = UINT32_C(1) << (setting + 16);
        /* level_ms is uint16_t, so seconds <= 65. Selection stops by
         * setting 10 (2^26 / 1000000 == 67), before bit 31 is reached.
         * Signed and unsigned division therefore agree for every input. */
        if (raw / 1000000U >= seconds)
            break;
    }
    if (setting == 16) setting = 15;
    volatile uint32_t *watchdog = (volatile uint32_t *)(uintptr_t)0xA0700000U;
    watchdog[1] = setting | (setting << 4);
    watchdog[3] = 118;
    open_cfw_gx8002_watchdog_handler = handler;
    open_cfw_gx8002_request_irq(11, open_cfw_gx8002_watchdog_interrupt, private_data);
    watchdog[0] = watchdog[0] | 1U;
}
