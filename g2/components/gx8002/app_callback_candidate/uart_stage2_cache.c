/* SPDX-License-Identifier: MIT
 * UART stage-2 cache/interrupt control at 0x10003174, 0x10003194,
 * and 0x100031b4. Volatile reads and sync instructions retain native order.
 */
#include <stdint.h>

void gx8002_uart_stage2_cache_init_3174(void)
{
    volatile uint32_t *const cache =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xb0000000);
    cache[0] = 0;
    cache[0] = cache[0] | 1u;
    while ((cache[1] & 3u) != 2u) { }
}

void gx8002_uart_stage2_interrupt_tail_3194(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    __asm__ volatile("sync\nsync" ::: "memory");
    control[1] = 1;
    control[0] = 21;
    __asm__ volatile("sync\nsync" ::: "memory");
}

void gx8002_uart_stage2_dcache_disable_31b4(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    __asm__ volatile("sync\nsync" ::: "memory");
    control[0] &= ~UINT32_C(1);
    control[1] = 1;
    __asm__ volatile("sync\nsync" ::: "memory");
}
