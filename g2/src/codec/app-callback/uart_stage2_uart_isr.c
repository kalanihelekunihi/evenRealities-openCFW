/* SPDX-License-Identifier: MIT
 * Stage-2 UART interrupt service at stock 0x10002aa8. Descriptor field
 * offsets and UART register reads/writes come from the native body.
 * Callback data is retained as target function pointers, not fabricated.
 */
#include <stdint.h>

typedef void (*gx8002_uart_stage2_irq_callback)(uint32_t, uint32_t);

static void invoke(volatile uint32_t *descriptor, uint32_t callback_offset,
                   uint32_t argument_offset)
{
    uint32_t address = descriptor[callback_offset / 4u];
    uint32_t argument = descriptor[argument_offset / 4u];
    gx8002_uart_stage2_irq_callback callback =
        (gx8002_uart_stage2_irq_callback)(uintptr_t)address;
    callback(descriptor[0], argument);
}

uint32_t gx8002_uart_stage2_irq_handler_2aa8(
    uint32_t irq, volatile uint32_t *descriptor)
{
    (void)irq;
    volatile uint32_t *uart = (volatile uint32_t *)(uintptr_t)descriptor[1];
    uint32_t status = uart[8u / 4u];
    if ((status & 4u) != 0u) {
        uint32_t mode = descriptor[0x40u / 4u];
        uint32_t available = uart[0x84u / 4u];
        if (mode == 1u) {
            invoke(descriptor, 0x50u, 0x54u);
        } else if (descriptor[0x2cu / 4u] == 0u && mode == 2u) {
            uint32_t remaining = descriptor[0x64u / 4u];
            uint32_t count = remaining < available ? remaining : available;
            uint8_t *buffer = (uint8_t *)(uintptr_t)descriptor[0x60u / 4u];
            if ((int32_t)count > 0) {
                for (uint32_t i = 0; i < count; ++i)
                    buffer[i] = (uint8_t)uart[0];
            }
            descriptor[0x60u / 4u] = (uint32_t)(uintptr_t)(buffer + count);
            descriptor[0x64u / 4u] = remaining - count;
            if (remaining == count) {
                uart[1] = uart[1] & ~UINT32_C(1);
                invoke(descriptor, 0x58u, 0x5cu);
            }
        }
    }
    if ((status & 2u) == 0u) return 0;
    uint32_t mode = descriptor[0x44u / 4u];
    uint32_t available =
        (((uart[0xf4u / 4u] >> 16) & 0xffu) << 4) - uart[0x80u / 4u];
    if (mode == 1u) {
        invoke(descriptor, 0x48u, 0x4cu);
        return 0;
    }
    if (descriptor[0x2cu / 4u] != 0u || mode != 2u) return 0;
    uint32_t remaining = descriptor[0x78u / 4u];
    uint32_t count = remaining < available ? remaining : available;
    const uint8_t *buffer =
        (const uint8_t *)(uintptr_t)descriptor[0x74u / 4u];
    if ((int32_t)count > 0) {
        for (uint32_t i = 0; i < count; ++i)
            uart[0] = buffer[i];
    }
    descriptor[0x74u / 4u] = (uint32_t)(uintptr_t)(buffer + count);
    descriptor[0x78u / 4u] = remaining - count;
    if (remaining == count) {
        while ((uart[0x14u / 4u] & 64u) == 0u) { }
        uart[1] = uart[1] & ~UINT32_C(2);
        invoke(descriptor, 0x6cu, 0x70u);
    }
    return 0;
}
