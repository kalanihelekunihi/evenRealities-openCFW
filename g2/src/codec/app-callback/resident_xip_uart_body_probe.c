/* SPDX-License-Identifier: MIT
 * Candidate reduction of native image-A XIP 0x10207cec..0x10207ecb.
 * The sixteen 28-byte handler records and payload/CRC trailer states
 * follow direct native and pinned UART record layouts. DMA completion
 * timing and runtime equality remain separately unqualified.
 */
#include <stdint.h>

extern volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(
    uint32_t port);
extern uint32_t gx8002_xip_uart_receive_callback_10208098(uint32_t,
                                                           uint32_t);
extern uint32_t gx8002_xip_uart_receive_start_1020368c(
    uint32_t, uint32_t (*)(uint32_t, uint32_t), uint32_t);
extern uint32_t gx8002_xip_uart_receive_stop_102036c0(uint32_t);
extern uint32_t gx8002_xip_uart_receive_buffer_10203780(
    uint32_t port, uint32_t address, uint32_t length,
    uint32_t (*callback)(uint32_t), uint32_t context);
extern uint32_t gx8002_xip_uart_receive_body_done_10207ee0(uint32_t);
extern uint32_t g2_codec_queue_enqueue(void *queue, const void *item);

static uint32_t uart_body_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void uart_body_set_word(volatile uint8_t *base, uint32_t offset,
                               uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_uart_body_probe_10207cec(
    uint32_t port, uint8_t *header, volatile uint32_t *cursor_slot,
    uint32_t *remaining)
{
    volatile uint8_t *const channel = (volatile uint8_t *)
        gx8002_xip_uart_channel_lookup_10207ac0(port & 0xffu);
    volatile uint8_t *const runtime =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e050);
    volatile uint32_t *const progress =
        (volatile uint32_t *)(void *)(runtime + 0x308u + port * 4u);
    const uint16_t raw_length =
        (uint16_t)((uint16_t)header[8u] |
                   ((uint16_t)header[9u] << 8u));
    const uint32_t body_length =
        (uint32_t)raw_length - (header[7u] != 0u ? 4u : 0u);

    if (body_length == *progress) {
        *progress = 0u;
        (void)gx8002_xip_uart_receive_start_1020368c(
            uart_body_word(channel, 8u),
            gx8002_xip_uart_receive_callback_10208098, 0u);
        if (header[7u] == 0u) {
            uart_body_set_word(channel, 0x170u, 0u);
            channel[0x30u] = (uint8_t)port;
            uart_body_set_word(channel, 0x34u, body_length);
            (void)g2_codec_queue_enqueue(
                (void *)(uintptr_t)UINT32_C(0x2002ecc4), header);
            uart_body_set_word(channel, 0x1cu, 0u);
            uart_body_set_word(channel, 0x34u, 0u);
            return 0;
        }
        uart_body_set_word(channel, 0x170u, 3u);
        return 0;
    }

    if (*progress == 0u) {
        volatile uint8_t *const handlers = runtime + 0x310u;
        uint16_t command = (uint16_t)((uint16_t)header[4u] |
                            ((uint16_t)header[5u] << 8u));
        for (uint32_t index = 0u; index < 16u; ++index) {
            volatile uint8_t *const handler = handlers + index * 28u;
            if (uart_body_word(handler, 4u) != command) continue;
            if (body_length <= uart_body_word(handler, 0x0cu)) {
                uint32_t used = uart_body_word(handler, 0x10u);
                if (uart_body_word(handler, 0x0cu) <
                    (uint32_t)raw_length + used) {
                    used = 0u;
                    uart_body_set_word(handler, 0x10u, 0u);
                }
                uint32_t storage = uart_body_word(handler, 8u);
                if (storage != 0u) {
                    uart_body_set_word((volatile uint8_t *)header, 0x10u,
                                       storage + used);
                    uart_body_set_word(handler, 0x10u,
                                       used + body_length);
                    goto copy_body;
                }
            }
            break;
        }
        uart_body_set_word((volatile uint8_t *)header, 0x10u, 0u);
        uart_body_set_word((volatile uint8_t *)header, 0x18u, 0u);
    } else {
copy_body:
        if (cursor_slot != (void *)0 && remaining != (void *)0 &&
            *cursor_slot != 0u && *remaining != 0u) {
            uint32_t take = body_length - *progress;
            if (take > *remaining) take = *remaining;
            uint8_t *const source = (uint8_t *)(uintptr_t)*cursor_slot;
            uint8_t *const destination = (uint8_t *)(uintptr_t)
                (uart_body_word((volatile uint8_t *)header, 0x10u) + *progress);
            for (uint32_t index = 0u; index < take; ++index)
                destination[index] = source[index];
            *progress += take;
            *remaining -= take;
            if (*progress != body_length) {
                if (body_length - *progress < 0x21u) return 0;
                const uint32_t output =
                    uart_body_word((volatile uint8_t *)header, 0x10u) +
                    *progress;
                const uint32_t start =
                    uart_body_word((volatile uint8_t *)header, 0x10u);
                if (output <= (start & ~UINT32_C(15)) + 0x10u)
                    return 0;
                uint32_t dma_bytes =
                    (body_length - *progress) & ~UINT32_C(15);
                (void)gx8002_xip_uart_receive_stop_102036c0(port);
                (void)gx8002_xip_uart_receive_buffer_10203780(
                    port, output, dma_bytes,
                    gx8002_xip_uart_receive_body_done_10207ee0, 0u);
                *remaining = 0u;
                *progress += dma_bytes;
                *cursor_slot = UINT32_C(0x2002e520);
                return 0;
            }
            *cursor_slot += take;
            *progress = 0u;
            if (header[7u] == 0u) return 1;
            uart_body_set_word(channel, 0x170u, 3u);
            return 0;
        }
        (void)gx8002_xip_uart_receive_start_1020368c(
            uart_body_word(channel, 8u),
            gx8002_xip_uart_receive_callback_10208098, 0u);
    }
    return -1;
}
