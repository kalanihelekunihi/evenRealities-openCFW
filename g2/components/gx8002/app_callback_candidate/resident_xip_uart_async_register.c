/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102082ac..0x1020832f. Direct C-SKY listing
 * establishes sixteen 28-byte callback records at 0x2002e360, the
 * duplicate-ID purge, field copy order, and -1 capacity return.
 * SRAM state allocation/initial values remain startup/layout obligations.
 */
#include <stdint.h>

static uint32_t uart_record_word(const volatile uint8_t *record,
                                 uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(record + offset);
}

static void uart_record_set_word(volatile uint8_t *record, uint32_t offset,
                                 uint32_t value)
{
    *(volatile uint32_t *)(void *)(record + offset) = value;
}

int32_t gx8002_xip_uart_async_register_102082ac(
    const uint8_t *registration)
{
    volatile uint8_t *const records =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e360);
    const uint32_t identity =
        *(const uint32_t *)(const void *)(registration + 4u);
    for (uint32_t index = 0u; index < 16u; ++index) {
        volatile uint8_t *const record = records + index * 28u;
        if (uart_record_word(record, 4u) != identity) continue;
        uart_record_set_word(record, 4u, 0u);
        record[0u] = 0xffu;
        uart_record_set_word(record, 8u, 0u);
        uart_record_set_word(record, 12u, 0u);
        uart_record_set_word(record, 16u, 0u);
        uart_record_set_word(record, 24u, 0u);
        uart_record_set_word(record, 20u, 0u);
    }
    for (uint32_t index = 0u; index < 16u; ++index) {
        volatile uint8_t *const record = records + index * 28u;
        if (uart_record_word(record, 4u) != 0u) continue;
        uart_record_set_word(record, 4u, identity);
        record[0u] = registration[0u];
        uart_record_set_word(record, 8u,
            *(const uint32_t *)(const void *)(registration + 8u));
        uart_record_set_word(record, 12u,
            *(const uint32_t *)(const void *)(registration + 12u));
        uart_record_set_word(record, 16u,
            *(const uint32_t *)(const void *)(registration + 16u));
        uart_record_set_word(record, 24u,
            *(const uint32_t *)(const void *)(registration + 24u));
        uart_record_set_word(record, 20u,
            *(const uint32_t *)(const void *)(registration + 20u));
        return 0;
    }
    return -1;
}
