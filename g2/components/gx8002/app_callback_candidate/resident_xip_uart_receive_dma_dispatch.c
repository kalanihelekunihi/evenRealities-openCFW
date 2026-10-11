/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10203780..0x102037d9 and 0x10207ee0..0x10207f07.
 * A receive DMA callback drives the already sourced body parser.
 */
#include <stdint.h>

extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t state);
extern volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(uint32_t);
extern uint32_t gx8002_xip_uart_receive_dma_10203190(
    void *channel, uint32_t address, uint32_t length);
extern int32_t gx8002_xip_uart_body_probe_10207cec(
    uint32_t, uint8_t *, volatile uint32_t *, uint32_t *);

static uint32_t gx8002_rx_dma_load(const volatile uint8_t *base,
                                   uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void gx8002_rx_dma_store(volatile uint8_t *base, uint32_t offset,
                                uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_uart_receive_buffer_10203780(
    uint32_t port, uint32_t address, uint32_t length,
    uint32_t (*callback)(uint32_t), uint32_t context)
{
    volatile uint8_t *const channel = (volatile uint8_t *)(uintptr_t)
        (UINT32_C(0x20026a94) + (port << 7u));
    if (address == 0u || callback == (void *)0) return UINT32_MAX;
    gx8002_rx_dma_store(channel, 0x58u, (uint32_t)(uintptr_t)callback);
    gx8002_rx_dma_store(channel, 0x40u, 2u);
    gx8002_rx_dma_store(channel, 0x60u, address);
    gx8002_rx_dma_store(channel, 0x64u, length);
    gx8002_rx_dma_store(channel, 0x5cu, context);
    gx8002_rx_dma_store(channel, 0x68u, UINT32_MAX);
    if (gx8002_rx_dma_load(channel, 0x2cu) == 0u) {
        uint32_t saved = g2_codec_critical_save();
        volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
            gx8002_rx_dma_load(channel, 4u);
        gx8002_rx_dma_store(registers, 4u,
            gx8002_rx_dma_load(registers, 4u) | 1u);
        g2_codec_critical_restore(saved);
        return 0u;
    }
    volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
        gx8002_rx_dma_load(channel, 4u);
    gx8002_rx_dma_store(registers, 0xa8u, 1u);
    return gx8002_xip_uart_receive_dma_10203190(
        (void *)channel, address, length);
}

uint32_t gx8002_xip_uart_receive_body_done_10207ee0(uint32_t port)
{
    volatile uint32_t *const channel =
        gx8002_xip_uart_channel_lookup_10207ac0(port & 0xffu);
    if (channel == (void *)0) return UINT32_MAX;
    (void)gx8002_xip_uart_body_probe_10207cec(
        port, (uint8_t *)(void *)(channel + 7u), (void *)0, (void *)0);
    return 0u;
}
