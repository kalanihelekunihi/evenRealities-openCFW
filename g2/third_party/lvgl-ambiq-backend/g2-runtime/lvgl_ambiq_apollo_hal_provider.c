/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_apollo_hal_provider.h"

/*
 * Exact AmbiqSuite ABI adapters for the already source-qualified G2 Apollo510
 * cache and peripheral-power implementations.  This file owns no MMIO policy;
 * the isolated provider audit links and authenticates every implementation
 * object below these five calls.
 */
uint32_t open_cfw_cache_dcache_clean(const am_hal_cachectrl_range_t *range);
uint32_t open_cfw_cache_dcache_invalidate(
    const am_hal_cachectrl_range_t *range,
    uint32_t clean
);
uint32_t open_cfw_pwrctrl_periph_enable(uint32_t peripheral);
uint32_t open_cfw_pwrctrl_periph_disable(uint32_t peripheral);
uint32_t open_cfw_pwrctrl_periph_enabled(uint32_t peripheral, uint8_t *enabled);

_Static_assert(sizeof(am_hal_cachectrl_range_t) == 8U,
               "Apollo510 cache range ABI changed");
_Static_assert(sizeof(am_hal_pwrctrl_periph_e) == 1U,
               "Apollo510 peripheral enum requires short-enum ABI");
_Static_assert(sizeof(bool) == 1U, "Apollo510 bool ABI changed");

uint32_t am_hal_cachectrl_dcache_clean(am_hal_cachectrl_range_t *range)
{
    return open_cfw_cache_dcache_clean(range);
}

uint32_t am_hal_cachectrl_dcache_invalidate(
    am_hal_cachectrl_range_t *range,
    bool clean
)
{
    return open_cfw_cache_dcache_invalidate(range, clean ? 1U : 0U);
}

uint32_t am_hal_pwrctrl_periph_enable(am_hal_pwrctrl_periph_e peripheral)
{
    return open_cfw_pwrctrl_periph_enable((uint32_t)peripheral);
}

uint32_t am_hal_pwrctrl_periph_disable(am_hal_pwrctrl_periph_e peripheral)
{
    return open_cfw_pwrctrl_periph_disable((uint32_t)peripheral);
}

uint32_t am_hal_pwrctrl_periph_enabled(
    am_hal_pwrctrl_periph_e peripheral,
    bool *enabled
)
{
    return open_cfw_pwrctrl_periph_enabled(
        (uint32_t)peripheral,
        (uint8_t *)enabled
    );
}
