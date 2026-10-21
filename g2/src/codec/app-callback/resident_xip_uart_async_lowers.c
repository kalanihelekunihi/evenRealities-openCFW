/* SPDX-License-Identifier: MIT
 * Direct-native image-A XIP UART async descendants 0x1020321c/34,
 * 0x1020368c/e8, 0x10203704, 0x10207ac0, 0x10207770,
 * 0x10207c74/9c. Native callback and runtime SRAM identities are retained.
 */
#include <stdint.h>

extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t state);
extern uint32_t gx8002_xip_dma_abort_10203b40(uint32_t channel);
extern uint32_t gx8002_xip_uart_initialize_10203530(uint32_t, uint32_t);
extern uint32_t gx8002_xip_uart_receive_callback_10208098(uint32_t,
                                                          uint32_t);

static volatile uint8_t *gx8002_uart_register_channel(uint32_t port)
{
    return (volatile uint8_t *)(uintptr_t)
        (UINT32_C(0x20026a94) + (port << 7u));
}

static uint32_t gx8002_uart_load(const volatile uint8_t *base,
                                 uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void gx8002_uart_store(volatile uint8_t *base, uint32_t offset,
                              uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(uint32_t port)
{
    if (port == 0u)
        return (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e050);
    if (port == 1u)
        return (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e1cc);
    return (void *)0;
}

uint32_t gx8002_xip_uart_transmit_abort_dma_1020321c(
    volatile uint8_t *channel)
{
    int32_t dma = (int32_t)gx8002_uart_load(channel, 0x7cu);
    if (dma >= 0) {
        (void)gx8002_xip_dma_abort_10203b40((uint32_t)dma);
        gx8002_uart_store(channel, 0x7cu, UINT32_MAX);
    }
    return 0u;
}

uint32_t gx8002_xip_uart_receive_abort_dma_10203234(
    volatile uint8_t *channel)
{
    int32_t dma = (int32_t)gx8002_uart_load(channel, 0x68u);
    if (dma >= 0) {
        (void)gx8002_xip_dma_abort_10203b40((uint32_t)dma);
        gx8002_uart_store(channel, 0x68u, UINT32_MAX);
    }
    return 0u;
}

uint32_t gx8002_xip_uart_transmit_abort_102036e8(uint32_t port)
{
    volatile uint8_t *const channel = gx8002_uart_register_channel(port);
    if (gx8002_uart_load(channel, 0x2cu) != 0u)
        (void)gx8002_xip_uart_transmit_abort_dma_1020321c(channel);
    return 0u;
}

uint32_t gx8002_xip_uart_receive_abort_10203704(uint32_t port)
{
    volatile uint8_t *const channel = gx8002_uart_register_channel(port);
    if (gx8002_uart_load(channel, 0x2cu) != 0u)
        (void)gx8002_xip_uart_receive_abort_dma_10203234(channel);
    return 0u;
}

uint32_t gx8002_xip_uart_receive_start_1020368c(
    uint32_t port, uint32_t (*callback)(uint32_t, uint32_t), uint32_t context)
{
    volatile uint8_t *const channel = gx8002_uart_register_channel(port);
    if (callback == (void *)0) return UINT32_MAX;
    gx8002_uart_store(channel, 0x40u, 1u);
    gx8002_uart_store(channel, 0x50u, (uint32_t)(uintptr_t)callback);
    gx8002_uart_store(channel, 0x54u, context);
    uint32_t saved = g2_codec_critical_save();
    volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
        gx8002_uart_load(channel, 4u);
    gx8002_uart_store(registers, 4u,
                      gx8002_uart_load(registers, 4u) | 1u);
    g2_codec_critical_restore(saved);
    return 0u;
}

uint32_t gx8002_xip_uart_receive_stop_102036c0(uint32_t port)
{
    volatile uint8_t *const channel = gx8002_uart_register_channel(port);
    gx8002_uart_store(channel, 0x50u, 0u);
    gx8002_uart_store(channel, 0x54u, 0u);
    uint32_t saved = g2_codec_critical_save();
    volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
        gx8002_uart_load(channel, 4u);
    gx8002_uart_store(registers, 4u,
                      gx8002_uart_load(registers, 4u) & ~UINT32_C(1));
    g2_codec_critical_restore(saved);
    return 0u;
}

uint32_t gx8002_xip_power_lock_create_10207770(void *raw_slot)
{
    volatile uint32_t *const flags =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfc0);
    volatile uint32_t *const slot = raw_slot;
    for (uint32_t index = 0u; index < 32u; ++index) {
        uint32_t bit = UINT32_C(1) << index;
        if ((*flags & bit) == 0u) {
            *slot = index + 1u;
            *flags = *flags | bit;
            return *slot;
        }
    }
    return UINT32_MAX;
}

uint32_t gx8002_xip_uart_message_suspend_10207c74(void)
{
    for (uint32_t port = 0u; port < 2u; ++port) {
        volatile uint32_t *const channel =
            gx8002_xip_uart_channel_lookup_10207ac0(port);
        if (channel != (void *)0) {
            (void)gx8002_xip_uart_transmit_abort_102036e8(channel[2]);
            (void)gx8002_xip_uart_receive_abort_10203704(channel[2]);
        }
    }
    return 0u;
}

uint32_t gx8002_xip_uart_message_resume_10207c9c(void)
{
    for (uint32_t port = 0u; port < 2u; ++port) {
        volatile uint32_t *const channel =
            gx8002_xip_uart_channel_lookup_10207ac0(port);
        if (channel == (void *)0 || channel[3] != 1u) continue;
        (void)gx8002_xip_uart_transmit_abort_102036e8(channel[2]);
        (void)gx8002_xip_uart_receive_abort_10203704(channel[2]);
        if (gx8002_xip_uart_initialize_10203530(channel[2], channel[4]) != 0u)
            return UINT32_MAX;
        (void)gx8002_xip_uart_receive_start_1020368c(
            channel[2], gx8002_xip_uart_receive_callback_10208098, 0u);
    }
    return 0u;
}
