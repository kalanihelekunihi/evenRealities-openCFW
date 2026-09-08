/* SPDX-License-Identifier: MIT */
/* Recovered watchdog service register write. */
#include <stdint.h>
void open_cfw_gx8002_watchdog_ping(void)
{
    *(volatile uint32_t *)(uintptr_t)0xA070000CU = 118;
}
