/* SPDX-License-Identifier: MIT
 * Seeded pool-range free dispatch at stock 0x100060e8. Eight 12-byte
 * descriptors share the pool list whose count is at 0x200099c8.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_pool_free_core_7240(
    void *pool, void *allocation);

void gx8002_uart_stage2_pool_free_lower_60e8(void *allocation)
{
    volatile const uint32_t *count =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x200099c8);
    volatile const uint32_t *descriptors =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2000a19c);
    uint32_t n = *count;
    if ((int32_t)n <= 0) return;
    uint32_t address = (uint32_t)(uintptr_t)allocation;
    for (uint32_t i = 0; i < n; ++i) {
        uint32_t start = descriptors[i * 3u + 1u];
        uint32_t bytes = descriptors[i * 3u + 2u];
        if (address >= start && address <= start + bytes) {
            void *pool = (void *)(uintptr_t)descriptors[i * 3u];
            gx8002_uart_stage2_pool_free_core_7240(pool, allocation);
            return;
        }
    }
}
