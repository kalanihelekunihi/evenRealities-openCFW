/* SPDX-License-Identifier: MIT
 * Candidate reconstruction of image-A XIP 0x10206204..0x1020647f.
 * Pinned NationalChip driver/spi.h supplies spi_device/message/transfer
 * offsets; the stock native body supplies register operations and branches.
 * Hardware timing and runtime equality still require bounded execution.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t module,
                                                 uint32_t enabled);

static volatile uint8_t *spi_address(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static uint32_t spi_word(volatile uint8_t *base, uint32_t offset)
{
    return *(volatile uint32_t *)(void *)(base + offset);
}

static void spi_set_word(volatile uint8_t *base, uint32_t offset,
                         uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_spi_quick_transfer_10206204(uint32_t *device,
                                                void *raw_message)
{
    volatile uint8_t *const master = spi_address(device[0]);
    volatile uint8_t *const state = spi_address(spi_word(master, 0x18u));
    volatile uint8_t *const message = raw_message;
    int32_t result = 0;
    spi_set_word(message, 0x18u, 0u); /* spi_message.actual_length */
    spi_set_word(message, 8u, (uint32_t)(uintptr_t)device);
    if (spi_word(state, 0x10u) == 0u) {
        spi_set_word(state, 0x10u, (uint32_t)(uintptr_t)message);
        gx8002_resident_platform_gate_25080(14u, 1u);
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa030008c) = 2u;
        volatile uint8_t *link = spi_address(spi_word(message, 0u));
        while (link != message) {
            volatile uint8_t *const transfer = link - 24u;
            volatile uint8_t *const active_message =
                spi_address(spi_word(state, 0x10u));
            volatile uint8_t *const active_device =
                spi_address(spi_word(active_message, 8u));
            volatile uint8_t *const config =
                spi_address(spi_word(active_device, 0x0cu));
            uint32_t buffer = spi_word(transfer, 0u); /* tx_buf */
            if (buffer == 0u) buffer = spi_word(transfer, 4u); /* rx_buf */
            const uint32_t length = spi_word(transfer, 8u);
            spi_set_word(state, 0x14u, (uint32_t)(uintptr_t)transfer);
            spi_set_word(state, 0x18u, buffer);
            spi_set_word(state, 0x1cu, length);
            uint32_t bits = transfer[13u];
            if (bits == 0u) {
                transfer[13u] = 8u;
                state[0x28u] = 1u;
            } else {
                uint32_t rounded = (bits + 7u) & ~7u;
                if (rounded == 24u) rounded = 32u;
                state[0x28u] = (uint8_t)(rounded >> 3u);
            }
            bits = transfer[13u];
            const uint32_t tx_buffer = spi_word(transfer, 0u);
            const uint32_t control = spi_word(config, 4u);
            volatile uint8_t *const registers =
                spi_address(spi_word(state, 4u));
            spi_set_word(registers, 8u, 0u);
            spi_set_word(registers, 0xf0u, spi_word(config, 12u));
            spi_set_word(registers, 0u, (bits - 1u) | control |
                         (tx_buffer != 0u ? 0x400u : 0x800u));
            uint32_t sample = spi_word(config, 8u);
            sample = ((sample & 0xffffu) < 2u) ? 2u : sample & 0x7fffu;
            spi_set_word(registers, 0x14u, sample);
            spi_set_word(registers, 4u, 0u);
            spi_set_word(registers, 0x4cu, 0u);
            const uint32_t width = state[0x28u];
            const uint32_t words = length / width;
            const uint32_t fifo_mask = spi_word(state, 0x0cu) * 2u - 1u;
            if (length != words * width || buffer != width * (buffer / width)) {
                result = -22;
                break;
            }
            spi_set_word(state, 0x20u, 0u);
            spi_set_word(registers, 8u, 0u);
            spi_set_word(registers, 0x10u, 1u);
            spi_set_word(registers, 0x4cu, 0u);
            uint32_t remaining = words;
            if (tx_buffer == 0u) {
                while (remaining != 0u) {
                    spi_set_word(registers, 8u, 0u);
                    const uint32_t capacity = spi_word(state, 0x0cu);
                    const uint32_t chunk =
                        remaining < capacity ? remaining : capacity;
                    spi_set_word(registers, 4u, chunk - 1u);
                    spi_set_word(registers, 8u, 1u);
                    spi_set_word(registers, 0x60u, 0u);
                    uint32_t pending = chunk;
                    while (pending != 0u) {
                        const uint32_t ready = fifo_mask &
                            spi_word(registers, 0x24u);
                        for (uint32_t index = 0; index < ready; ++index) {
                            volatile uint8_t *const cursor = spi_address(buffer);
                            if (width == 1u) {
                                cursor[0u] = (uint8_t)
                                    spi_word(registers, 0x60u);
                                buffer += 1u;
                            } else if (width == 2u) {
                                *(volatile uint16_t *)(void *)cursor =
                                    (uint16_t)spi_word(registers, 0x60u);
                                buffer += 2u;
                            } else if (width == 4u) {
                                spi_set_word(cursor, 0u,
                                             spi_word(registers, 0x60u));
                                buffer += 4u;
                            }
                        }
                        pending -= ready;
                    }
                    remaining -= chunk;
                }
            } else {
                spi_set_word(registers, 8u, 1u);
                while (remaining != 0u) {
                    uint32_t chunk = spi_word(state, 8u) -
                        (fifo_mask & spi_word(registers, 0x20u));
                    if (chunk > remaining) chunk = remaining;
                    spi_set_word(registers, 4u, chunk - 1u);
                    for (uint32_t index = 0; index < chunk; ++index) {
                        const volatile uint8_t *const cursor =
                            spi_address(buffer + index * width);
                        if (width == 1u)
                            spi_set_word(registers, 0x60u, cursor[0u]);
                        else if (width == 2u)
                            spi_set_word(registers, 0x60u,
                                *(volatile const uint16_t *)(const void *)cursor);
                        else if (width == 4u)
                            spi_set_word(registers, 0x60u,
                                *(volatile const uint32_t *)(const void *)cursor);
                    }
                    buffer += chunk * width;
                    remaining -= chunk;
                }
                while ((spi_word(registers, 0x28u) & 4u) == 0u) { }
                while ((spi_word(registers, 0x28u) & 1u) != 0u) { }
            }
            link = spi_address(spi_word(link, 0u));
            spi_set_word(registers, 8u, 0u);
        }
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa030008c) = 3u;
        gx8002_resident_platform_gate_25080(14u, 0u);
    }
    spi_set_word(state, 0x10u, 0u);
    spi_set_word(state, 0x14u, 0u);
    return result;
}
