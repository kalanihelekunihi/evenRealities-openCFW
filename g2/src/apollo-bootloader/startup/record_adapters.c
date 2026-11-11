/* SPDX-License-Identifier: MIT
 * Init-record adapters called by the C descriptor sequence in record_dispatch.c.
 * Stock passes R9 as the static base, which only matters for odd
 * (position-relative) record addresses; every record here is absolute. */
#include <stdint.h>
#include "initialize.h"

extern uint32_t *opencfw_boot_expand_locked_data_record(uint32_t *record, uint32_t static_base);

__attribute__((section(".boot_expand_adapter"), used))
uint32_t *opencfw_boot_expand_adapter(uint32_t *record)
{
    return opencfw_boot_expand_locked_data_record(record, 0u);
}

__attribute__((section(".boot_zero_adapter"), used))
uint32_t *opencfw_boot_zero_adapter(uint32_t *table)
{
    return opencfw_boot_zero_table(table, 0u);
}
