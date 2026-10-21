/* SPDX-License-Identifier: MIT
 * UART boot stage-1 PMU bit accessors at 0x10000374..0x100003ba.
 * Native setters perform two writes to 0xa0010030, so both are retained.
 */
#include <stdint.h>

static volatile uint32_t *const pmu_bits =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010030);

void gx8002_uart_stage1_pmu_set_bit0(uint32_t value)
{
    uint32_t current = *pmu_bits;
    *pmu_bits = current & ~UINT32_C(1);
    current = *pmu_bits;
    *pmu_bits = current | (value & 1u);
}

void gx8002_uart_stage1_pmu_set_bit1(uint32_t value)
{
    uint32_t current = *pmu_bits;
    *pmu_bits = current & ~UINT32_C(2);
    current = *pmu_bits;
    *pmu_bits = current | ((value << 1) & 2u);
}

uint32_t gx8002_uart_stage1_pmu_get_bit0(void)
{
    return *pmu_bits & 1u;
}

uint32_t gx8002_uart_stage1_pmu_get_bit1(void)
{
    return (*pmu_bits >> 1) & 1u;
}
