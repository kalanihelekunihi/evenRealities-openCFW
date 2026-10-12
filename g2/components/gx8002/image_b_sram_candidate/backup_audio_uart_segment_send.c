/* SPDX-License-Identifier: MIT
 * Image-B 0x1000ab7c: send a queued UART payload segment, switching from
 * polled TX to the native DMA completion path for aligned long remainders.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941,
 * 0x1000ab7c..0x1000aca9. SRAM base and both callback entries are literal
 * native operands; their final source relocation is a separate layout gate.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_poll_write_buffer_10004614(
    uint32_t port, const uint8_t *source, int32_t count);
extern int32_t gx8002_image_b_uart_tx_irq_enable_10004650(
    uint32_t port, uint32_t callback, uint32_t context);
extern int32_t gx8002_image_b_uart_tx_irq_disable_10004684(uint32_t port);
extern int32_t gx8002_image_b_uart_dma_send_10004740(
    uint32_t port, const uint8_t *source, uint32_t length,
    uint32_t callback, uint32_t context);
extern int32_t gx8002_image_b_audio_uart_tx_complete_1000afc4(
    uint32_t channel, uint32_t available);
extern int32_t gx8002_image_b_audio_uart_dma_complete_1000acbc(
    uint32_t channel, uint32_t context);

static uint32_t load32(volatile const uint8_t *address)
{
    return *(volatile const uint32_t *)(volatile const void *)address;
}

static void store32(volatile uint8_t *address, uint32_t value)
{
    *(volatile uint32_t *)(volatile void *)address = value;
}

int32_t gx8002_image_b_audio_uart_segment_send_1000ab7c(
    uint32_t channel, const uint8_t *packet, uint32_t *available)
{
    const uintptr_t shared_base = UINT32_C(0x2002cc20);
    volatile uint8_t *cursor_state = (volatile uint8_t *)(shared_base + channel * 4u);
    uint32_t sent = load32(cursor_state + 0x2f8u);
    uint32_t length;
    if (sent == 0u) {
        /* Native reads packet+0x18 unconditionally on this branch. */
        length = *(const uint32_t *)(const void *)(packet + 0x18u);
        store32(cursor_state + 0x300u, length);
        if (length == 0u) goto segment_complete;
    } else {
        length = load32(cursor_state + 0x300u);
        if (sent == length) goto segment_complete;
    }
    if (packet == 0 || available == 0 || *available == 0u) {
        (void)gx8002_image_b_uart_tx_irq_enable_10004650(
            channel, (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_tx_complete_1000afc4, 0u);
        return -1;
    }
    uint32_t count = length - sent;
    if (*available < count) count = *available;
    uint32_t data_address = *(const uint32_t *)(const void *)(packet + 0x10u);
    (void)gx8002_image_b_uart_poll_write_buffer_10004614(
        channel, (const uint8_t *)(uintptr_t)(data_address + sent), (int32_t)count);
    sent = load32(cursor_state + 0x2f8u) + count;
    length = load32(cursor_state + 0x300u);
    if (sent == length) {
        store32(cursor_state + 0x2f8u, 0u);
        *available -= count;
        return 1;
    }
    store32(cursor_state + 0x2f8u, sent);
    *available -= count;
    if (sent == 0u) return 1;
    uint32_t remaining = length - sent;
    if (((data_address + sent) & 15u) != 0u) {
        if (sent < 16u || remaining < 33u) return 0;
    }
    uint32_t dma_count = remaining & ~UINT32_C(15);
    (void)gx8002_image_b_uart_tx_irq_disable_10004684(channel);
    (void)gx8002_image_b_uart_dma_send_10004740(
        channel, (const uint8_t *)(uintptr_t)(data_address + sent), dma_count,
        (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_dma_complete_1000acbc, 0u);
    store32(cursor_state + 0x2f8u, load32(cursor_state + 0x2f8u) + dma_count);
    *available = 0u;
    return 0;

segment_complete:
    store32(cursor_state + 0x2f8u, 0u);
    uint32_t selected = channel & 0xffu;
    if (selected > 1u) return -1;
    volatile uint8_t *state = (volatile uint8_t *)(selected == 0u ?
        shared_base : UINT32_C(0x2002cd9c));
    store32(state + 0x174u, state[0x43u] == 0u ? 3u : 2u);
    (void)gx8002_image_b_uart_tx_irq_enable_10004650(
        channel, (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_tx_complete_1000afc4, 0u);
    return 1;
}
