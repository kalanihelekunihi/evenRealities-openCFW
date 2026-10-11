/* SPDX-License-Identifier: MIT
 * UART stage-1 rail control at 0x1000046c and block-clear at 0x100004a4.
 * The clock-rate getter at 0x10000ea0 remains a typed lower contract.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, uint32_t enabled);
extern int32_t gx8002_uart_stage1_pmu_clock_rate(uint32_t selector);

void gx8002_uart_stage1_railcfg(void)
{
    volatile uint32_t *const clock =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400000);
    gx8002_uart_stage1_pmu_dispatch(0x17u, 1u);
    clock[0x10 / 4] = 1;
    clock[0x10 / 4] = 0;
    clock[0x20 / 4] = 1;
    const int32_t rate = gx8002_uart_stage1_pmu_clock_rate(0x17u);
    int32_t quotient;
    const int32_t million = 1000000;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(rate), "r"(million) : "cc");
    clock[0x24 / 4] = (uint32_t)(quotient - 1);
    clock[0x28 / 4] = 0;
    clock[0x10 / 4] = 2;
}

void gx8002_uart_stage1_blkclr(void)
{
    volatile uint32_t *const first =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0500000);
    volatile uint32_t *const second =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0600000);
    (void)first[0x40 / 4];
    first[0x30 / 4] = 0;
    first[0x6c / 4] = 0;
    (void)second[0x40 / 4];
    second[0x30 / 4] = 0;
    second[0x6c / 4] = 0;
    gx8002_uart_stage1_pmu_dispatch(0x14u, 0);
    gx8002_uart_stage1_pmu_dispatch(0x15u, 0);
}
