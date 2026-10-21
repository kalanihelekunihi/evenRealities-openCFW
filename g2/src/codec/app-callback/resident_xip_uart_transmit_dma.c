/* SPDX-License-Identifier: MIT
 * Direct-native image-A XIP 0x102030c4 transmit completion and
 * 0x10203108 DMA entry. Descriptor words follow retained native stack
 * stores and pinned NationalChip UART/DMA layout. Port must be 0 or 1,
 * as initialized by the selected UART channel setup; other-port native
 * descriptor word 8 has no supported initialized value.
 */
#include <stdint.h>

struct g2_codec_uart_prefix;
extern uint32_t g2_codec_dw_uart_dma_burst(
    const struct g2_codec_uart_prefix *, int32_t);
extern void g2_codec_header_sync(void *, uint32_t);
extern int32_t gx8002_xip_dma_select_10203a4c(void);
extern void gx8002_xip_dma_callback_10203b64(
    uint32_t, void (*)(void *), void *);
extern int32_t gx8002_xip_dma_transfer_10203b78(
    uint32_t, uint32_t, uint32_t, uint32_t, const uint32_t *);
extern void gx8002_xip_dma_release_10203b38(uint32_t);
extern void gx8002_xip_uart_flush_10203598(uint32_t);

static uint32_t native_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void native_store(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

void gx8002_xip_uart_transmit_complete_102030c4(void *raw_channel)
{
    volatile uint8_t *channel = raw_channel;
    gx8002_xip_dma_release_10203b38(native_word(channel, 0x7cu));
    native_store(channel, 0x7cu, UINT32_MAX);
    uint32_t port = native_word(channel, 0u);
    gx8002_xip_uart_flush_10203598(port);
    uint32_t raw_callback = native_word(channel, 0x6cu) & ~UINT32_C(1);
    void (*callback)(uint32_t, uint32_t) =
        (void (*)(uint32_t, uint32_t))(uintptr_t)raw_callback;
    callback(port, native_word(channel, 0x70u));
}

int32_t gx8002_xip_uart_transmit_dma_entry_10203108(
    volatile uint8_t *channel, const void *bytes, uint32_t length)
{
    uint32_t registers = native_word(channel, 4u);
    g2_codec_header_sync((void *)bytes, length);
    int32_t selected = gx8002_xip_dma_select_10203a4c();
    if (selected < 0) return -1;
    native_store(channel, 0x7cu, (uint32_t)selected);
    uint32_t burst_one = g2_codec_dw_uart_dma_burst(
        (const struct g2_codec_uart_prefix *)channel, 1);
    uint32_t burst_two = g2_codec_dw_uart_dma_burst(
        (const struct g2_codec_uart_prefix *)channel, 1);
    uint32_t port = native_word(channel, 0u);
    if (port > 1u) return -1;
    uint32_t descriptor[12] = {
        0u, burst_one, 0u, 0u, 0u, 0u,
        burst_two, 1u, port == 0u ? 7u : 5u, 1u, 0u, 1u
    };
    gx8002_xip_dma_callback_10203b64(
        (uint32_t)selected,
        gx8002_xip_uart_transmit_complete_102030c4, (void *)channel);
    (void)gx8002_xip_dma_transfer_10203b78(
        registers, (uint32_t)(uintptr_t)bytes, length,
        (uint32_t)selected, descriptor);
    return 0;
}
