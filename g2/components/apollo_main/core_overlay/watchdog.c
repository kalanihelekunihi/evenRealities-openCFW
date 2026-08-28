/* SPDX-License-Identifier: MIT */
/*
 * Clean-room reconstruction of the G2 watchdog policy wrapper.
 *
 * The hardware-facing enable operation remains in the retained nPMx driver.
 * This module recreates the complete first-party watchdog.c decision layer:
 * selector zero enables the provider only for product configuration value 1.
 */

#include <stdint.h>

#ifndef OPEN_CFW_WATCHDOG_SELECTOR
const uint8_t *open_cfw_retained_watchdog_selector(uint32_t selector);
#define OPEN_CFW_WATCHDOG_SELECTOR(selector) \
    open_cfw_retained_watchdog_selector((selector))
#endif

#ifndef OPEN_CFW_WATCHDOG_ENABLE_PROVIDER
void open_cfw_retained_watchdog_enable_provider(void);
#define OPEN_CFW_WATCHDOG_ENABLE_PROVIDER() \
    open_cfw_retained_watchdog_enable_provider()
#endif

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_WATCHDOG_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_WATCHDOG_NOINLINE
#endif

#if !defined(OPEN_CFW_WATCHDOG_INIT_ONLY)
OPEN_CFW_WATCHDOG_NOINLINE void open_cfw_watchdog_enable(void)
{
    const uint8_t *const product_selector = OPEN_CFW_WATCHDOG_SELECTOR(0u);

    if (*product_selector == 1u) {
        OPEN_CFW_WATCHDOG_ENABLE_PROVIDER();
    }
}
#else
void open_cfw_watchdog_enable(void);
#endif

#if !defined(OPEN_CFW_WATCHDOG_ENABLE_ONLY)
void open_cfw_watchdog_init(void)
{
    open_cfw_watchdog_enable();
}
#endif
