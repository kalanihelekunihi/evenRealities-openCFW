/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_INIT_TABLE_H
#define OPENCFW_BOOT_INIT_TABLE_H

#include <stdint.h>

struct opencfw_boot_init_record {
    uintptr_t callback;
    uint32_t priority;
};

void opencfw_boot_init_table_run(const struct opencfw_boot_init_record *begin,
                                const struct opencfw_boot_init_record *end);
void opencfw_boot_init_table_default(void);
int32_t opencfw_boot_init_priority_compare(
    const struct opencfw_boot_init_record *left,
    const struct opencfw_boot_init_record *right);

#endif
