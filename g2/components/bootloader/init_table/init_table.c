/* SPDX-License-Identifier: MIT
 * Bounded source reconstruction of locked-image initializer runner 0x41f9f8.
 * The sorter is reconstructed in qsort.c and has independent stock tests.
 */
#include "init_table.h"

extern void opencfw_boot_init_sort(
    void *base, uint32_t count, uint32_t record_size,
    int32_t (*compare)(const struct opencfw_boot_init_record *,
                       const struct opencfw_boot_init_record *));

#define INIT_SCRATCH ((volatile struct opencfw_boot_init_record *)0x20022e00u)

int32_t opencfw_boot_init_priority_compare(
    const struct opencfw_boot_init_record *left,
    const struct opencfw_boot_init_record *right)
{
    /* Stock returns the low 32 bits of left.priority - right.priority. */
    return (int32_t)(left->priority - right->priority);
}

void opencfw_boot_init_table_run(const struct opencfw_boot_init_record *begin,
                                const struct opencfw_boot_init_record *end)
{
    uint32_t count = (uint32_t)(((uintptr_t)end - (uintptr_t)begin) >> 3);
    if (count >= 257u)
        count = 256u;

    for (uint32_t i = 0; i < count; ++i) {
        INIT_SCRATCH[i].callback = begin[i].callback;
        INIT_SCRATCH[i].priority = begin[i].priority;
    }

    opencfw_boot_init_sort((void *)INIT_SCRATCH, count, 8u,
                           opencfw_boot_init_priority_compare);

    for (uint32_t i = 0; i < count; ++i) {
        uintptr_t target = INIT_SCRATCH[i].callback;
        if (target != 0u)
            ((void (*)(void))target)();
    }
}

/* Fixed-table entry consumed by the locked-image startup path. */
void opencfw_boot_init_table_default(void)
{
    opencfw_boot_init_table_run(
        (const struct opencfw_boot_init_record *)(uintptr_t)0x433440u,
        (const struct opencfw_boot_init_record *)(uintptr_t)0x433460u);
}
