/* SPDX-License-Identifier: MIT
 * Direct native body 0x100045ec. The register address 0xa001008c
 * is built by movih/bseti plus a 0x0c displacement in stock code.
 */
#include <stdint.h>

void gx8002_uart_stage2_apply_table_entry_45ec(const void *descriptor)
{
    const uint32_t bit = *(const uint32_t *)descriptor & 31u;
    const uint32_t value = *((const uint8_t *)descriptor + 4u);
    volatile uint32_t *const register_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);
    const uint32_t old = *register_word;
    *register_word = (old & ~(UINT32_C(1) << bit)) | (value << bit);
}
