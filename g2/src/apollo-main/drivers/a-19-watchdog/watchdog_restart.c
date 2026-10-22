/* MCU watchdog restart hook, native 0x4b29f8..0x4b2a01 (stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\wdt\watchdog.c by placement next
 * to the watchdog start helper 0x4b29d8).
 *
 * Called from am_freertos_sleep 0x46d836, am_freertos_wakeup 0x46d856 and
 * vApplicationIdleHook 0x46d898, so the watchdog is fed around every tickless
 * sleep. The callee 0x52a3da is AmbiqSuite am_hal_wdt_restart: for instance 0
 * it writes key 0xB2 to WDT->RSTRT (0x40024004) and returns 0, otherwise 1. */
#include <stdint.h>

#define AM_HAL_WDT_MCU 0u

extern uint32_t am_hal_wdt_restart_52a3da(uint32_t timer);

void watchdog_restart_4b29f8(void)
{
    (void)am_hal_wdt_restart_52a3da(AM_HAL_WDT_MCU);
}
