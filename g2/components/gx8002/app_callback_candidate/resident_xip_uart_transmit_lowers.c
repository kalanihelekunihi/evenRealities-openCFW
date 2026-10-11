/* SPDX-License-Identifier: MIT
 * Direct-native image-A XIP 0x10203604, 0x10203630, 0x10203664,
 * 0x10203720. The 0x20026a94 UART channel identity is stock literal;
 * product-state initialization and hardware execution remain unqualified.
 */
#include <stdint.h>

struct g2_codec_uart_prefix;
extern void g2_codec_dw_uart_putc(
    const struct g2_codec_uart_prefix *, uint32_t);
extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t);
extern int32_t gx8002_xip_uart_transmit_dma_entry_10203108(
    volatile uint8_t *, const void *, uint32_t);

static volatile uint8_t *channel_at(uint32_t port)
{
    return (volatile uint8_t *)(uintptr_t)
        (UINT32_C(0x20026a94) + port * 0x80u);
}
static uint32_t word_at(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void set_word(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_uart_write_10203604(
    uint32_t port, const void *raw_bytes, uint32_t raw_length)
{
    const uint8_t *bytes = raw_bytes;
    int32_t length = (int32_t)raw_length;
    for (int32_t index = 0; index < length; ++index)
        g2_codec_dw_uart_putc(
            (const struct g2_codec_uart_prefix *)channel_at(port),
            bytes[index]);
    return length > 0 ? length : 0;
}

int32_t gx8002_xip_uart_transmit_start_10203630(
    uint32_t port, uint32_t (*callback)(uint32_t, uint32_t),
    uint32_t context)
{
    volatile uint8_t *channel = channel_at(port);
    if (!callback) return -1;
    set_word(channel, 0x44u, 1u);
    set_word(channel, 0x48u, (uint32_t)(uintptr_t)callback);
    set_word(channel, 0x4cu, context);
    uint32_t saved = g2_codec_critical_save();
    volatile uint8_t *registers =
        (volatile uint8_t *)(uintptr_t)word_at(channel, 4u);
    set_word(registers, 4u, word_at(registers, 4u) | 2u);
    g2_codec_critical_restore(saved);
    return 0;
}

int32_t gx8002_xip_uart_transmit_stop_10203664(uint32_t port)
{
    volatile uint8_t *channel = channel_at(port);
    set_word(channel, 0x48u, 0u);
    set_word(channel, 0x4cu, 0u);
    uint32_t saved = g2_codec_critical_save();
    volatile uint8_t *registers =
        (volatile uint8_t *)(uintptr_t)word_at(channel, 4u);
    set_word(registers, 4u, word_at(registers, 4u) & ~UINT32_C(2));
    g2_codec_critical_restore(saved);
    return 0;
}

int32_t gx8002_xip_uart_transmit_buffer_10203720(
    uint32_t port, const void *bytes, uint32_t length,
    uint32_t (*callback)(uint32_t), uint32_t context)
{
    if (!bytes || !callback) return -1;
    volatile uint8_t *channel = channel_at(port);
    set_word(channel, 0x6cu, (uint32_t)(uintptr_t)callback);
    set_word(channel, 0x44u, 2u);
    set_word(channel, 0x74u, (uint32_t)(uintptr_t)bytes);
    set_word(channel, 0x78u, length);
    set_word(channel, 0x70u, context);
    set_word(channel, 0x7cu, UINT32_MAX);
    if (word_at(channel, 0x2cu) == 0u) {
        uint32_t saved = g2_codec_critical_save();
        volatile uint8_t *registers =
            (volatile uint8_t *)(uintptr_t)word_at(channel, 4u);
        set_word(registers, 4u, word_at(registers, 4u) | 2u);
        g2_codec_critical_restore(saved);
        return 0;
    }
    volatile uint8_t *registers =
        (volatile uint8_t *)(uintptr_t)word_at(channel, 4u);
    set_word(registers, 0xa8u, 1u);
    return gx8002_xip_uart_transmit_dma_entry_10203108(
        channel, bytes, length);
}
