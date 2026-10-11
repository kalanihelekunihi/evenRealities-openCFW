/* SPDX-License-Identifier: MIT
 * Native XIP 0x10203278..0x1020335d. UART IRQ status branches, callback
 * slots, register reads/writes and byte transfer loops follow direct
 * C-SKY disassembly. Product channel state and callback registration remain
 * runtime-owned inputs; callbacks are never fabricated.
 */
#include <stdint.h>

typedef void (*gx8002_uart_rx_callback)(uint32_t port, uint32_t level,
                                          uint32_t context);
typedef void (*gx8002_uart_tx_callback)(uint32_t port, uint32_t room,
                                          uint32_t context);
typedef void (*gx8002_uart_done_callback)(uint32_t port, uint32_t context);

static uint32_t channel_load(volatile const uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void channel_store(volatile uint8_t *base, uint32_t offset,
                          uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_uart_isr_10203278(uint32_t irq, void *raw_channel)
{
    (void)irq;
    volatile uint8_t *const channel = raw_channel;
    volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
        channel_load(channel, 4u);
    uint32_t status = channel_load(registers, 8u);
    if ((status & 4u) != 0u) {
        uint32_t level = channel_load(registers, 0x84u);
        if (channel_load(channel, 0x40u) == 1u) {
            gx8002_uart_rx_callback callback =
                (gx8002_uart_rx_callback)(uintptr_t)
                channel_load(channel, 0x50u);
            callback(channel_load(channel, 0u), level,
                     channel_load(channel, 0x54u));
        } else if (channel_load(channel, 0x2cu) == 0u &&
                   channel_load(channel, 0x40u) == 2u) {
            uint32_t available = level;
            uint32_t remaining = channel_load(channel, 0x64u);
            if (available > remaining) available = remaining;
            uint8_t *cursor = (uint8_t *)(uintptr_t)
                channel_load(channel, 0x60u);
            for (uint32_t index = 0; index < available; ++index)
                cursor[index] = (uint8_t)channel_load(registers, 0u);
            channel_store(channel, 0x60u,
                          channel_load(channel, 0x60u) + available);
            remaining -= available;
            channel_store(channel, 0x64u, remaining);
            if (remaining == 0u) {
                channel_store(registers, 4u,
                              channel_load(registers, 4u) & ~UINT32_C(1));
                gx8002_uart_done_callback callback =
                    (gx8002_uart_done_callback)(uintptr_t)
                    channel_load(channel, 0x58u);
                callback(channel_load(channel, 0u),
                         channel_load(channel, 0x5cu));
            }
        }
    }
    if ((status & 2u) != 0u) {
        uint32_t encoded = (channel_load(registers, 0xf4u) & 0x7fffffu) >> 16;
        uint32_t room = encoded * 16u - channel_load(registers, 0x80u);
        if (channel_load(channel, 0x44u) == 1u) {
            gx8002_uart_tx_callback callback =
                (gx8002_uart_tx_callback)(uintptr_t)
                channel_load(channel, 0x48u);
            callback(channel_load(channel, 0u), room,
                     channel_load(channel, 0x4cu));
        } else if (channel_load(channel, 0x2cu) == 0u &&
                   channel_load(channel, 0x44u) == 2u) {
            uint32_t remaining = channel_load(channel, 0x78u);
            if (room > remaining) room = remaining;
            const uint8_t *cursor = (const uint8_t *)(uintptr_t)
                channel_load(channel, 0x74u);
            for (uint32_t index = 0; index < room; ++index)
                channel_store(registers, 0u, cursor[index]);
            channel_store(channel, 0x74u,
                          channel_load(channel, 0x74u) + room);
            remaining -= room;
            channel_store(channel, 0x78u, remaining);
            if (remaining == 0u) {
                while ((channel_load(registers, 0x14u) & 0x40u) == 0u) { }
                channel_store(registers, 4u,
                              channel_load(registers, 4u) & ~UINT32_C(2));
                gx8002_uart_done_callback callback =
                    (gx8002_uart_done_callback)(uintptr_t)
                    channel_load(channel, 0x6cu);
                callback(channel_load(channel, 0u),
                         channel_load(channel, 0x70u));
            }
        }
    }
    return 0u;
}
