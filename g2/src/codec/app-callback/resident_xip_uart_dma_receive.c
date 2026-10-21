/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102030e4, 0x10203190, 0x10203a4c, 0x10203b64.
 * This is the receive DMA/IRQ callback path with the stock 12-word transfer
 * descriptor and real imported transfer implementation at 0x10203b78.
 */
#include <stdint.h>

struct g2_codec_uart_prefix;
extern uint32_t g2_codec_dw_uart_dma_burst(
    const struct g2_codec_uart_prefix *, int32_t direction);
extern void gx8002_resident_cache_invalidate_25608(void *, int32_t);
extern void gx8002_resident_cache_clean_invalidate_256c0(void *, int32_t);
extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t state);
extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_xip_dma_release_10203b38(uint32_t channel);
extern int32_t gx8002_xip_dma_transfer_10203b78(
    uint32_t source, uint32_t target, uint32_t length,
    uint32_t channel, const uint32_t *descriptor);

static uint32_t gx8002_rx_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void gx8002_rx_set_word(volatile uint8_t *base, uint32_t offset,
                               uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_dma_select_10203a4c(void)
{
    uint32_t saved = g2_codec_critical_save();
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e93c);
    uint32_t count = gx8002_rx_word(state, 4u);
    for (uint32_t channel = 0u; channel < count; ++channel) {
        if (state[0x370u + channel] != 0u) continue;
        state[0x370u + channel] = 1u;
        gx8002_resident_platform_gate_25080(25u, 1u);
        g2_codec_critical_restore(saved);
        return (int32_t)channel;
    }
    g2_codec_critical_restore(saved);
    return -1;
}

void gx8002_xip_dma_callback_10203b64(uint32_t channel,
                                       void (*callback)(void *),
                                       void *context)
{
    volatile uint8_t *const table =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20027320);
    gx8002_rx_set_word(table, channel * 4u,
                       (uint32_t)(uintptr_t)callback);
    gx8002_rx_set_word(table, channel * 4u + 8u,
                       (uint32_t)(uintptr_t)context);
}

void gx8002_xip_uart_receive_complete_102030e4(void *raw_channel)
{
    volatile uint8_t *const channel = raw_channel;
    gx8002_xip_dma_release_10203b38(gx8002_rx_word(channel, 0x68u));
    gx8002_rx_set_word(channel, 0x68u, UINT32_MAX);
    gx8002_resident_cache_clean_invalidate_256c0(
        (void *)(uintptr_t)gx8002_rx_word(channel, 0x60u),
        (int32_t)gx8002_rx_word(channel, 0x64u));
    uint32_t raw_callback = gx8002_rx_word(channel, 0x58u) & ~UINT32_C(1);
    void (*callback)(uint32_t, uint32_t) =
        (void (*)(uint32_t, uint32_t))(uintptr_t)raw_callback;
    callback(gx8002_rx_word(channel, 0u),
             gx8002_rx_word(channel, 0x5cu));
}

uint32_t gx8002_xip_uart_receive_dma_10203190(
    void *raw_channel, uint32_t address, uint32_t length)
{
    volatile uint8_t *const channel = raw_channel;
    const uint32_t registers = gx8002_rx_word(channel, 4u);
    gx8002_resident_cache_invalidate_25608(
        (void *)(uintptr_t)gx8002_rx_word(channel, 0x60u),
        (int32_t)gx8002_rx_word(channel, 0x64u));
    int32_t selected = gx8002_xip_dma_select_10203a4c();
    if (selected < 0) return UINT32_MAX;
    gx8002_rx_set_word(channel, 0x68u, (uint32_t)selected);
    const uint32_t burst_one = g2_codec_dw_uart_dma_burst(
        (const struct g2_codec_uart_prefix *)raw_channel, 0);
    const uint32_t port = gx8002_rx_word(channel, 0u);
    if (port != 0u && port != 1u) return UINT32_MAX;
    const uint32_t burst_two = g2_codec_dw_uart_dma_burst(
        (const struct g2_codec_uart_prefix *)raw_channel, 0);
    uint32_t descriptor[12] = {
        0u, burst_one, 1u, port == 0u ? 6u : 4u,
        1u, 0u, burst_two, 0u, 0u, 0u, 0u, 2u
    };
    gx8002_xip_dma_callback_10203b64(
        (uint32_t)selected, gx8002_xip_uart_receive_complete_102030e4,
        raw_channel);
    (void)gx8002_xip_dma_transfer_10203b78(
        address, registers, length, (uint32_t)selected, descriptor);
    return 0u;
}
