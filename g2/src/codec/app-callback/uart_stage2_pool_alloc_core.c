/* SPDX-License-Identifier: MIT
 * Seeded pool block allocation at stock 0x100070ac. The raw 20-byte
 * bucket layout and boundary-pointer updates are transcribed from its
 * retained pseudocode and native branch structure. Runtime equality is
 * still unqualified; this is a complete C candidate, not a stub.
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

void *gx8002_uart_stage2_pool_alloc_lower_70ac(void *control,
                                                 uint32_t bytes)
{
    uint32_t *pool = (uint32_t *)control;
    uint32_t requested = (bytes + 15u) & ~UINT32_C(15);
    if (pool[0] - pool[2] < requested) return 0;
    uint32_t index = bucket_index(requested);
    if (index > 1042u) return 0;
    uintptr_t base = (uintptr_t)pool;
    uint32_t *block = 0;
    for (; index <= 1042u; ++index) {
        uintptr_t head = base + 24u + index * 20u;
        uintptr_t current = (uintptr_t)*at(head + 4u);
        while (current != head) {
            if (*at(current) >= requested) {
                block = at(current);
                break;
            }
            current = (uintptr_t)*at(current + 4u);
        }
        if (block != 0) break;
    }
    if (block == 0) return 0;
    uintptr_t address = (uintptr_t)block;
    uint32_t original = block[0];
    uint32_t remainder = original - requested;
    uintptr_t previous = (uintptr_t)*at(address + original + 12u);
    uintptr_t next = (uintptr_t)block[1];
    *at(previous + 4u) = (uint32_t)next;
    *at(next + *at(next) + 12u) = (uint32_t)previous;
    block[1] = 0;
    --pool[index * 5u + 10u];

    if (!(remainder < 16401u && remainder < requested + 16u)) {
        uintptr_t split = address + requested + 8u;
        uint32_t free_size = remainder - 16u;
        block[0] = requested;
        *at(split) = requested;
        *at(split + 8u) = free_size;
        *at(split + remainder) = free_size;
        pool[2] += 16u;
        uint32_t free_index = bucket_index(free_size);
        uintptr_t head = base + 24u + free_index * 20u;
        uintptr_t current = (uintptr_t)*at(head + 4u);
        while (current != head && *at(current) < free_size)
            current = (uintptr_t)*at(current + 4u);
        uintptr_t previous_free = (uintptr_t)*at(current + *at(current) + 12u);
        uintptr_t free_block = split + 8u;
        *at(previous_free + 4u) = (uint32_t)free_block;
        *at(split + remainder + 4u) = (uint32_t)previous_free;
        *at(split + 12u) = (uint32_t)current;
        *at(current + *at(current) + 12u) = (uint32_t)free_block;
        ++pool[free_index * 5u + 10u];
    }
    uint32_t used = pool[2] + block[0];
    pool[1] += block[0];
    pool[2] = used;
    if (pool[3] < used) pool[3] = used;
    return (void *)(address + 8u);
}
