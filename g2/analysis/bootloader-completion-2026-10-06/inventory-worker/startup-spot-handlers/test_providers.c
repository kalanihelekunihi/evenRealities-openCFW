/* SPDX-License-Identifier: BSD-3-Clause
 * Deterministic stand-ins for only 421548 (INFO reads) and timer-init 41cc04.
 */
#include <stdint.h>

volatile uint32_t startup_test_status[3];
volatile uint32_t startup_test_words[3][20];
volatile uint32_t startup_test_calls;
volatile uint32_t startup_test_call_log[12];
volatile uint32_t startup_test_commits;

int spot_info_read(uint32_t selector, uint32_t offset, uint32_t count,
                   uint32_t *destination)
{
    uint32_t n = startup_test_calls++;
    uint32_t *log = (uint32_t *)(uintptr_t)startup_test_call_log;
    log[n * 4U + 0U] = selector;
    log[n * 4U + 1U] = offset;
    log[n * 4U + 2U] = count;
    log[n * 4U + 3U] = (uint32_t)(uintptr_t)destination;
    for (uint32_t i = 0; i < count; ++i) destination[i] = startup_test_words[n][i];
    return (int)startup_test_status[n];
}

void spot_timer_init(void)
{
    volatile uint32_t *a = (volatile uint32_t *)(uintptr_t)0x400083e0U;
    uint32_t value = *a;
    *a = value & ~1U;
    *a = 0x110U;
    *(volatile uint32_t *)(uintptr_t)0x400083f0U = 0x100U;
    *(volatile uint32_t *)(uintptr_t)0x400083e8U = 0xffffffffU;
    *(volatile uint32_t *)(uintptr_t)0x400083ecU = 0xffffffffU;
    *(volatile uint32_t *)(uintptr_t)0x40008068U = 0xc0000000U;
    *(volatile uint32_t *)(uintptr_t)0x40008060U |= 0x40000000U;
    startup_test_commits++;
}
