/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_CACHE_MAINTENANCE_H
#define OPENCFW_CACHE_MAINTENANCE_H
#include <stdint.h>
typedef struct {
    uint32_t address;
    uint32_t length; /* Compared as signed32 by stock; no unit conversion. */
} opencfw_cache_range_t;
/* NULL range selects whole cache; flag uses nonzero low byte. */
uint32_t opencfw_cache_invalidate(const volatile opencfw_cache_range_t *range, uint32_t clean_too);
uint32_t opencfw_cache_clean(const volatile opencfw_cache_range_t *range);
#endif
