/* SPDX-License-Identifier: MIT
 * Native image-A XIP UART message send path 0x10207b38, 0x10207c50,
 * 0x10207f08. Callback/state table literals are authenticated at
 * 0x10207c44..4c and 0x10208090..94. Remaining UART/CRC children are
 * genuine typed imports, with hardware equality still unqualified.
 */
#include <stdint.h>

extern volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(uint32_t);
extern int32_t gx8002_xip_uart_write_10203604(
    uint32_t, const void *, uint32_t);
extern int32_t gx8002_xip_uart_transmit_start_10203630(
    uint32_t, uint32_t (*)(uint32_t, uint32_t), uint32_t);
extern int32_t gx8002_xip_uart_transmit_stop_10203664(uint32_t);
extern int32_t gx8002_xip_uart_transmit_buffer_10203720(
    uint32_t, const void *, uint32_t, uint32_t (*)(uint32_t), uint32_t);
extern uint32_t gx8002_xip_power_unlock_102077d4(int32_t);
extern int32_t gx8002_xip_uart_message_start_10207adc(uint32_t);
extern uint32_t gx8002_xip_crc32_102098a8(uint32_t, const void *, uint32_t);

uint32_t gx8002_xip_uart_send_callback_10207f08(uint32_t, uint32_t);
uint32_t gx8002_xip_uart_body_done_10207c50(uint32_t);

static uint32_t rx_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void tx_word(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_uart_message_body_10207b38(
    uint32_t port, volatile uint8_t *message, uint32_t *remaining)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e050);
    uint32_t slot = port * 4u;
    uint32_t cursor = rx_word(state, slot + 0x2f8u);
    if (cursor == 0) tx_word(state, slot + 0x300u, rx_word(message, 0x18u));
    uint32_t size = rx_word(state, slot + 0x300u);
    if (cursor == size) {
        tx_word(state, slot + 0x2f8u, 0);
        volatile uint8_t *channel =
            (volatile uint8_t *)gx8002_xip_uart_channel_lookup_10207ac0(port & 0xffu);
        if (!channel) return UINT32_MAX;
        tx_word(channel, 0x174u, 2u - (channel[0x43u] != 0u));
        (void)gx8002_xip_uart_transmit_start_10203630(
            port, gx8002_xip_uart_send_callback_10207f08, 0);
        return 1u;
    }
    if (!message || !remaining || !*remaining) {
        (void)gx8002_xip_uart_transmit_start_10203630(
            port, gx8002_xip_uart_send_callback_10207f08, 0);
        return UINT32_MAX;
    }
    uint32_t length = size - cursor < *remaining ? size - cursor : *remaining;
    uint32_t data = rx_word(message, 0x10u);
    (void)gx8002_xip_uart_write_10203604(
        port, (const void *)(uintptr_t)(data + cursor), length);
    cursor += length;
    if (cursor == size) cursor = 0;
    tx_word(state, slot + 0x2f8u, cursor);
    *remaining -= length;
    if (cursor == 0) return 1u;
    if (((data + cursor) & 0xfu) != 0u &&
        (cursor < 0x10u || size - cursor < 0x21u)) return 0u;
    uint32_t aligned = (size - cursor) & ~UINT32_C(0xf);
    (void)gx8002_xip_uart_transmit_stop_10203664(port);
    (void)gx8002_xip_uart_transmit_buffer_10203720(
        port, (const void *)(uintptr_t)(data + cursor), aligned,
        gx8002_xip_uart_body_done_10207c50, 0);
    tx_word(state, slot + 0x2f8u, cursor + aligned);
    *remaining = 0;
    return 0u;
}

uint32_t gx8002_xip_uart_body_done_10207c50(uint32_t port)
{
    volatile uint8_t *channel =
        (volatile uint8_t *)gx8002_xip_uart_channel_lookup_10207ac0(port & 0xffu);
    if (!channel) return UINT32_MAX;
    (void)gx8002_xip_uart_message_body_10207b38(port, channel + 0x3cu, 0);
    return 0;
}

uint32_t gx8002_xip_uart_send_callback_10207f08(
    uint32_t port, uint32_t byte_budget)
{
    volatile uint8_t *channel =
        (volatile uint8_t *)gx8002_xip_uart_channel_lookup_10207ac0(port & 0xffu);
    if (!channel) return UINT32_MAX;
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e050);
    volatile uint8_t *const callback_table =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e578);
    uint32_t slot = port * 4u;
    uint32_t remaining = byte_budget;
    do {
        uint32_t phase = rx_word(channel, 0x174u);
        if (phase == 1u) {
            uint32_t result = gx8002_xip_uart_message_body_10207b38(
                port, channel + 0x3cu, &remaining);
            if (result == 1u)
                tx_word(channel, 0x174u, 2u - (channel[0x43u] != 0u));
        } else if (phase == 0u) {
            uint32_t offset = rx_word(state, slot + 0x510u);
            uint32_t count = 14u - offset < remaining ?
                14u - offset : remaining;
            (void)gx8002_xip_uart_write_10203604(
                port, (const void *)(channel + 0x3cu + offset), count);
            offset += count;
            if (offset == 14u) offset = 0;
            remaining -= count;
            tx_word(state, slot + 0x510u, offset);
            if (offset == 0u)
                tx_word(channel, 0x174u,
                        *(volatile const uint16_t *)(const void *)(channel + 0x44u)
                        ? 1u : 3u);
        } else if (phase == 2u) {
            uint32_t offset = rx_word(state, slot + 0x518u);
            if (offset == 0u)
                tx_word(state, slot + 0x520u,
                    gx8002_xip_crc32_102098a8(
                        0, (const void *)(uintptr_t)rx_word(channel, 0x4cu),
                        rx_word(channel, 0x54u)));
            uint32_t count = 4u - offset < remaining ?
                4u - offset : remaining;
            (void)gx8002_xip_uart_write_10203604(
                port, (const void *)(state + 0x520u + slot + offset), count);
            offset += count;
            if (offset == 4u) offset = 0;
            remaining -= count;
            tx_word(state, slot + 0x518u, offset);
            if (offset == 0u) tx_word(channel, 0x174u, 3u);
        } else if (phase == 3u) {
            volatile uint8_t *peer =
                (volatile uint8_t *)gx8002_xip_uart_channel_lookup_10207ac0(channel[0x50u]);
            if (peer) {
                (void)gx8002_xip_power_unlock_102077d4((int32_t)rx_word(peer, 0x178u));
                for (uint32_t i = 0; i < 6u; ++i) {
                    volatile uint8_t *row = callback_table + 16u * i;
                    if (rx_word(row, 4u) ==
                            *(volatile const uint16_t *)(const void *)(channel + 0x40u) &&
                        rx_word(row, 0u) == channel[0x50u]) {
                        uint32_t raw_callback = rx_word(row, 8u) & ~UINT32_C(1);
                        void (*callback)(volatile uint8_t *, uint32_t) =
                            (void (*)(volatile uint8_t *, uint32_t))(uintptr_t)raw_callback;
                        callback(channel + 0x3cu, rx_word(row, 12u));
                        break;
                    }
                }
            }
            if (gx8002_xip_uart_message_start_10207adc(port & 0xffu) == -1)
                break;
        }
    } while (remaining != 0u);
    return 0;
}
