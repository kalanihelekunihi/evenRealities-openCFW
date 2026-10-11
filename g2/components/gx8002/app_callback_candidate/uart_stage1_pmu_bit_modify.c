/* SPDX-License-Identifier: MIT
 * Stage-1 PMU bit modify at 0x10000840. The second descriptor word's low
 * byte is written into the selected bit field at 0xa001008c.
 */
#include <stdint.h>

void gx8002_uart_stage1_pmu_bit_modify(const uint32_t *descriptor)
{
    const uint32_t bit = descriptor[0] & 31u;
    const uint32_t value = (uint8_t)descriptor[1];
    volatile uint32_t *const register_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);
    const uint32_t old = *register_word;
    *register_word = (old & ~(UINT32_C(1) << bit)) | (value << bit);
}
