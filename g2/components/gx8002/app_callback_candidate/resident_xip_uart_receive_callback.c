/* SPDX-License-Identifier: MIT
 * Candidate C reduction of native image-A XIP 0x10208098..0x10208297.
 * The 14-byte sync/header, CRC, body and trailer states and exact SRAM
 * addresses follow direct C-SKY branches and pinned UART/queue APIs.
 * Body parsing at 0x10207cec remains a genuine typed source contract.
 */
#include <stdint.h>

extern volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(
    uint32_t port);
extern int32_t gx8002_xip_uart_read_102035d8(
    uint32_t port, uint8_t *destination, int32_t count);
extern uint32_t crc32(uint32_t initial, const unsigned char *bytes,
                      unsigned int length);
extern int32_t gx8002_xip_uart_body_probe_10207cec(
    uint32_t port, uint8_t *header, volatile uint32_t *cursor_slot,
    uint32_t *remaining);
extern uint32_t g2_codec_queue_enqueue(void *queue, const void *item);

static uint32_t uart_rx_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void uart_rx_set_word(volatile uint8_t *base, uint32_t offset,
                             uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_uart_receive_callback_10208098(uint32_t port,
                                                     uint32_t available)
{
    const uint32_t slot = port & 0xffu;
    volatile uint8_t *const channel = (volatile uint8_t *)
        gx8002_xip_uart_channel_lookup_10207ac0(slot);
    if (channel == (void *)0) return UINT32_MAX;
    uint8_t *const buffer =
        (uint8_t *)(uintptr_t)UINT32_C(0x2002e520);
    volatile uint32_t *const cursor_slot =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e5d8);
    volatile uint32_t *const header_progress =
        (volatile uint32_t *)(uintptr_t)
            (UINT32_C(0x20026c74) + port * 4u);
    volatile uint32_t *const trailer_progress =
        (volatile uint32_t *)(uintptr_t)
            (UINT32_C(0x2002e5dc) + port * 4u);
    *cursor_slot = (uint32_t)(uintptr_t)buffer;
    uint32_t remaining = (uint32_t)gx8002_xip_uart_read_102035d8(
        port, buffer, (int32_t)available);
    if (remaining == 0u) return 0u;

    uint8_t *const header = (uint8_t *)(void *)(channel + 0x1cu);
    while (remaining != 0u) {
        uint8_t *cursor = (uint8_t *)(uintptr_t)*cursor_slot;
        const uint32_t state = uart_rx_word(channel, 0x170u);
        if (state == 0u) {
            if (uart_rx_word(channel, 0u) !=
                uart_rx_word(channel, 0x1cu)) {
                uint32_t consumed = 0u;
                while (consumed < remaining) {
                    uint32_t rolling =
                        (uart_rx_word(channel, 0x1cu) >> 8u) |
                        ((uint32_t)cursor[consumed] << 24u);
                    uart_rx_set_word(channel, 0x1cu, rolling);
                    ++consumed;
                    if (rolling == uart_rx_word(channel, 0u)) break;
                }
                cursor += consumed;
                remaining -= consumed;
                *cursor_slot = (uint32_t)(uintptr_t)cursor;
                if (uart_rx_word(channel, 0u) !=
                    uart_rx_word(channel, 0x1cu)) {
                    if (remaining == 0u) *cursor_slot = (uint32_t)(uintptr_t)buffer;
                    continue;
                }
            }
            uart_rx_set_word(channel, 0x170u, 1u);
            continue;
        } else if (state == 1u) {
            uint32_t progress = *header_progress;
            uint32_t consumed = 0u;
            while (consumed < remaining && progress + consumed < 14u) {
                header[progress + consumed] = cursor[consumed];
                ++consumed;
            }
            progress += consumed;
            *header_progress = progress;
            remaining -= consumed;
            if (remaining != 0u)
                *cursor_slot = (uint32_t)(uintptr_t)(cursor + consumed);
            if (progress != 14u) continue;
            *header_progress = 4u;
            const uint32_t expected =
                (uint32_t)header[10u] |
                ((uint32_t)header[11u] << 8u) |
                ((uint32_t)header[12u] << 16u) |
                ((uint32_t)header[13u] << 24u);
            if (crc32(0u, header, 10u) != expected) {
                header[0u] = header[1u] = header[2u] = header[3u] = 0u;
                uart_rx_set_word(channel, 0x170u, 0u);
                continue;
            }
            const uint16_t payload_length =
                (uint16_t)((uint16_t)channel[0x24u] |
                           ((uint16_t)channel[0x25u] << 8u));
            if (payload_length != 0u) {
                uart_rx_set_word(channel, 0x170u, 2u);
                continue;
            }
            uart_rx_set_word(channel, 0x170u, 0u);
            channel[0x30u] = (uint8_t)slot;
            uart_rx_set_word(channel, 0x34u, 0u);
        } else if (state == 2u) {
            int32_t result = gx8002_xip_uart_body_probe_10207cec(
                port, header, cursor_slot, &remaining);
            if (result == -1) {
                uart_rx_set_word(channel, 0x170u, 0u);
                continue;
            }
            if (result != 1) continue;
            uart_rx_set_word(channel, 0x170u, 0u);
            channel[0x30u] = (uint8_t)slot;
            const uint16_t payload_length =
                (uint16_t)((uint16_t)channel[0x24u] |
                           ((uint16_t)channel[0x25u] << 8u));
            uart_rx_set_word(channel, 0x34u,
                (uint32_t)payload_length - (channel[0x23u] != 0u ? 4u : 0u));
        } else if (state == 3u) {
            uint32_t progress = *trailer_progress;
            uint32_t take = 4u - progress;
            if (take > remaining) take = remaining;
            uint32_t trailer = uart_rx_word(channel, 4u);
            for (uint32_t index = 0u; index < take; ++index)
                trailer = (trailer >> 8u) | ((uint32_t)cursor[index] << 24u);
            uart_rx_set_word(channel, 4u, trailer);
            cursor += take;
            *cursor_slot = (uint32_t)(uintptr_t)cursor;
            remaining -= take;
            progress += take;
            *trailer_progress = progress;
            if (progress != 4u) continue;
            uart_rx_set_word(channel, 0x38u, trailer);
            uart_rx_set_word(channel, 4u, 0u);
            *trailer_progress = 0u;
            uart_rx_set_word(channel, 0x170u, 0u);
            channel[0x30u] = (uint8_t)slot;
            const uint16_t payload_length =
                (uint16_t)((uint16_t)channel[0x24u] |
                           ((uint16_t)channel[0x25u] << 8u));
            uart_rx_set_word(channel, 0x34u,
                (uint32_t)payload_length - (channel[0x23u] != 0u ? 4u : 0u));
        } else {
            remaining = 0u;
            continue;
        }
        (void)g2_codec_queue_enqueue(
            (void *)(uintptr_t)UINT32_C(0x2002ecc4), header);
        uart_rx_set_word(channel, 0x1cu, 0u);
        uart_rx_set_word(channel, 0x34u, 0u);
    }
    return 0u;
}
