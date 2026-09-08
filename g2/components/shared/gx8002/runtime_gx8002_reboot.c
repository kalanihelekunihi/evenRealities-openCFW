/* SPDX-License-Identifier: MIT */
/* Recovered watchdog-triggered reboot. The final wait is the stock reset
 * wait, not a substitute for unrecovered functionality. Platform gate call
 * at runtime 0x10025080 remains a separately tracked dependency. */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(unsigned int, unsigned int);
__attribute__((noreturn)) void open_cfw_gx8002_reboot(void)
{
    open_cfw_gx8002_platform_gate(24, 1);
    *(volatile uint32_t *)(uintptr_t)0xA001002CU = 1;
    volatile uint32_t *watchdog = (volatile uint32_t *)(uintptr_t)0xA0700000U;
    watchdog[0] = 0;
    watchdog[1] = 0;
    watchdog[3] = 118;
    watchdog[0] = 1;
    for (;;) {}
}

int open_cfw_gx8002_watchdog_callback(int irq, void *private_data)
{
    (void)irq;
    (void)private_data;
    open_cfw_gx8002_reboot();
}
