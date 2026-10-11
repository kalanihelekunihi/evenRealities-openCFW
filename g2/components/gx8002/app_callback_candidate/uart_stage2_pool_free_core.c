/* SPDX-License-Identifier: MIT
 * Seeded free/coalesce body at stock 0x10007240. It unlinks adjacent
 * free blocks, updates the control overhead, and reinserts the merged
 * block into the stock 1,043-bucket sorted list.
 */
#include <stdint.h>

static uint32_t *at(uintptr_t address)
{
    return (uint32_t *)address;
}

static uint32_t bucket_index(uint32_t size)
{
    if (size <= 16384u) return size >> 4;
    if ((int32_t)size < 0) return 1042u;
    uint32_t bit = size;
    uint32_t shift = 31u;
    do {
        bit <<= 1;
        --shift;
    } while ((int32_t)bit >= 0);
    return 1011u + shift;
}

static void unlink_free(uintptr_t base, uintptr_t block, uint32_t size)
{
    uintptr_t previous = (uintptr_t)*at(block + size + 12u);
    uintptr_t next = (uintptr_t)*at(block + 4u);
    *at(previous + 4u) = (uint32_t)next;
    *at(next + *at(next) + 12u) = (uint32_t)previous;
    --*at(base + 40u + bucket_index(size) * 20u);
}

void gx8002_uart_stage2_pool_free_core_7240(void *control,
                                              void *allocation)
{
    if (allocation == 0) return;
    uintptr_t base = (uintptr_t)control;
    uintptr_t block = (uintptr_t)allocation - 8u;
    uint32_t size = *at(block);
    *at(base + 4u) -= size;
    *at(base + 8u) -= size;

    uintptr_t following = block + size + 16u;
    if (following < (uintptr_t)*at(base + 20u) &&
        *at(following + 4u) != 0u) {
        uint32_t adjacent = *at(following);
        unlink_free(base, following, adjacent);
        size += 16u + adjacent;
        *at(base + 8u) -= 16u;
    }
    if ((uintptr_t)*at(base + 16u) < block) {
        uint32_t previous_size = *at(block - 8u);
        uintptr_t preceding = block - 16u - previous_size;
        if (*at(preceding + 4u) != 0u) {
            unlink_free(base, preceding, previous_size);
            size += 16u + previous_size;
            *at(base + 8u) -= 16u;
            block = preceding;
        }
    }
    *at(block) = size;
    *at(block + size + 8u) = size;
    uint32_t index = bucket_index(size);
    uintptr_t head = base + 24u + index * 20u;
    uintptr_t current = (uintptr_t)*at(head + 4u);
    while (current != head && *at(current) < size)
        current = (uintptr_t)*at(current + 4u);
    uintptr_t previous = (uintptr_t)*at(current + *at(current) + 12u);
    *at(previous + 4u) = (uint32_t)block;
    *at(block + size + 12u) = (uint32_t)previous;
    *at(block + 4u) = (uint32_t)current;
    *at(current + *at(current) + 12u) = (uint32_t)block;
    ++*at(base + 40u + index * 20u);
}
