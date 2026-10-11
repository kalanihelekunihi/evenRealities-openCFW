/* SPDX-License-Identifier: MIT */
#ifndef GX8002_RESIDENT_PLATFORM_GATE_H
#define GX8002_RESIDENT_PLATFORM_GATE_H
#include "resident_product_data.h"

struct gx8002_module_info {
    const struct gx8002_module_entry *entry;
    volatile uint32_t *base;
    volatile uint32_t *status;
    volatile uint32_t *field18;
    volatile uint32_t *disable;
    volatile uint32_t *enable;
};
_Static_assert(sizeof(struct gx8002_module_info) == 24,
               "native module info ABI");
int32_t gx8002_resident_module_get_info_24a44(
    uint32_t module, struct gx8002_module_info *info);
#endif
