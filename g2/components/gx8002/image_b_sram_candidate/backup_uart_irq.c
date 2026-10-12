/* SPDX-License-Identifier: MIT
 * UART IRQ service at image-B 0x10004250..0x10004339, decoded from
 * binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * IRQ/data-register and callback order are retained; physical interleavings
 * require device qualification.
 */
#include <stdint.h>

typedef void (*uart_callback)(uint32_t, uint32_t, uint32_t);

static void callback_word(uint32_t address, uint32_t first,
                          uint32_t second, uint32_t third)
{
    ((uart_callback)(uintptr_t)address)(first, second, third);
}

int32_t gx8002_image_b_uart_irq_10004250(int32_t line, void *argument)
{
    (void)line;
    volatile uint32_t *record = (volatile uint32_t *)argument;
    volatile uint32_t *uart = (volatile uint32_t *)(uintptr_t)record[1];
    uint32_t status = uart[2];
    if ((status & 4u) != 0u) {
        uint32_t available = uart[0x84u / 4u];
        if (record[0x40u / 4u] == 1u) {
            callback_word(record[0x50u / 4u], record[0],
                          available, record[0x54u / 4u]);
        } else if (record[0x2cu / 4u] == 0u &&
                   record[0x40u / 4u] == 2u) {
            uint32_t count = record[0x64u / 4u];
            if (available < count) count = available;
            uint8_t *destination = (uint8_t *)(uintptr_t)
                record[0x60u / 4u];
            for (uint32_t i = 0u; i < count; ++i)
                destination[i] = (uint8_t)uart[0];
            record[0x60u / 4u] += count;
            record[0x64u / 4u] -= count;
            if (record[0x64u / 4u] == 0u) {
                uart[1] &= ~1u;
                callback_word(record[0x58u / 4u], record[0],
                              record[0x5cu / 4u], (uint32_t)(uintptr_t)uart);
            }
        }
    }
    if ((status & 2u) != 0u) {
        uint32_t available =
            ((uart[0xf4u / 4u] >> 16) & 0xffu) * 16u - uart[0x80u / 4u];
        if (record[0x44u / 4u] == 1u) {
            callback_word(record[0x48u / 4u], record[0],
                          available, record[0x4cu / 4u]);
        } else if (record[0x2cu / 4u] == 0u &&
                   record[0x44u / 4u] == 2u) {
            uint32_t count = record[0x78u / 4u];
            if (available < count) count = available;
            const uint8_t *source = (const uint8_t *)(uintptr_t)
                record[0x74u / 4u];
            for (uint32_t i = 0u; i < count; ++i) uart[0] = source[i];
            record[0x74u / 4u] += count;
            record[0x78u / 4u] -= count;
            if (record[0x78u / 4u] == 0u) {
                while ((uart[0x14u / 4u] & 64u) == 0u) { }
                uart[1] &= ~2u;
                callback_word(record[0x6cu / 4u], record[0],
                              record[0x70u / 4u], (uint32_t)(uintptr_t)uart);
            }
        }
    }
    return 0;
}
