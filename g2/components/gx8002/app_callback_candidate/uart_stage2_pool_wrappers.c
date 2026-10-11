/* SPDX-License-Identifier: MIT
 * Package-pool wrappers at stock 0x100060b0, 0x10006134, 0x10006154,
 * 0x10006168. The first and third retain actual allocator/free lowers.
 */
#include <stdint.h>

extern void *gx8002_uart_stage2_pool_alloc_lower_70ac(
    void *pool, uint32_t bytes);
extern void gx8002_uart_stage2_pool_free_lower_60e8(void *allocation);

void *gx8002_uart_stage2_pool_search_60b0(uint32_t bytes)
{
    volatile const uint32_t *count =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x200099c8);
    volatile const uint32_t *descriptors =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2000a19c);
    uint32_t n = *count;
    if ((int32_t)n <= 0) return 0;
    for (uint32_t i = 0; i < n; ++i) {
        void *pool = (void *)(uintptr_t)descriptors[i * 3u];
        void *result = gx8002_uart_stage2_pool_alloc_lower_70ac(pool, bytes);
        if (result != 0) return result;
    }
    return 0;
}

void *gx8002_uart_stage2_pool_malloc_6134(uint32_t bytes)
{
    void *raw = gx8002_uart_stage2_pool_search_60b0(bytes + 36u);
    if (raw == 0) return 0;
    uintptr_t aligned = ((uintptr_t)raw + 35u) & ~(uintptr_t)31u;
    *(uint32_t *)(aligned - 4u) = (uint32_t)(uintptr_t)raw;
    return (void *)aligned;
}

void gx8002_uart_stage2_pool_free_6154(void *aligned)
{
    if (aligned == 0) return;
    void *raw = (void *)(uintptr_t)*(const uint32_t *)
        ((uintptr_t)aligned - 4u);
    if (raw != 0) gx8002_uart_stage2_pool_free_lower_60e8(raw);
}

void gx8002_uart_stage2_pool_free_wrapper_6168(void *allocation)
{
    gx8002_uart_stage2_pool_free_6154(allocation);
}
