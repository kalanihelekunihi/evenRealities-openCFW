/* SPDX-License-Identifier: MIT
 * Image-B receive packet state machine 0x1000ad60..0x1000af77.
 * Stock binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Native initialized callback table 0x2002cf30 and ring 0x2002d770 are
 * literal SRAM contracts pending complete source-owned initialization/scatter.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_rx_irq_enable_100046ac(
    uint32_t port, uint32_t callback, uint32_t context);
extern int32_t gx8002_image_b_uart_rx_irq_disable_100046e0(uint32_t port);
extern int32_t gx8002_image_b_uart_dma_receive_100047a4(
    uint32_t port, uint8_t *destination, uint32_t length,
    uint32_t callback, uint32_t context);
extern uint32_t gx8002_image_b_audio_ring_write_10015b64(
    volatile int32_t *ring, const uint8_t *source);
extern int32_t gx8002_image_b_audio_uart_rx_irq_1000b198(
    uint32_t port, uint32_t available);
extern int32_t gx8002_image_b_audio_uart_rx_dma_complete_1000af94(
    uint32_t port, uint32_t context);
/* 0xaf94 calls this body with r2=0; native ad a6 still loads word [0]. */
extern uint32_t gx8002_image_b_native_word_at_zero_1000ada6(void);

static uint32_t load32(volatile const uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(volatile const void *)(base + offset);
}
static uint16_t load16(volatile const uint8_t *base, uint32_t offset)
{
    return *(volatile const uint16_t *)(volatile const void *)(base + offset);
}
static void store32(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(volatile void *)(base + offset) = value;
}

int32_t gx8002_image_b_audio_uart_receive_packet_1000ad60(
    uint32_t channel, volatile uint8_t *packet,
    uint8_t **input, uint32_t *available)
{
    uint32_t selected = channel & 0xffu;
    volatile uint8_t *shared = (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002cc20);
    volatile uint8_t *state = selected == 0u ? shared :
        selected == 1u ? (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002cd9c) : 0;
    volatile uint8_t *cursor = shared + channel * 4u;
    uint32_t expected = (uint32_t)load16(packet, 8u) -
        (packet[7u] != 0u ? 4u : 0u);
    uint32_t progress = load32(cursor, 0x308u);
    uint8_t *source = input != 0 ? *input :
        (uint8_t *)(uintptr_t)gx8002_image_b_native_word_at_zero_1000ada6();
    if (progress == expected) goto packet_complete;

    if (progress == 0u) {
        volatile uint8_t *table = (volatile uint8_t *)(uintptr_t)
            UINT32_C(0x2002cf30);
        uint32_t key = load16(packet, 4u);
        uint32_t index;
        for (index = 0u; index < 16u; ++index) {
            if (load32(table + index * 28u, 4u) == key) break;
        }
        if (index == 16u) goto registration_failure;
        volatile uint8_t *record = table + index * 28u;
        uint32_t capacity = load32(record, 12u);
        if (capacity < expected) goto registration_failure;
        uint32_t used = load32(record, 16u);
        if (capacity < (uint32_t)load16(packet, 8u) + used) {
            store32(record, 16u, 0u);
            used = 0u;
        }
        uint32_t destination = load32(record, 8u);
        if (destination == 0u) goto registration_failure;
        store32(packet, 16u, destination + used);
        store32(record, 16u, used + expected);
    }
    if (source == 0 || available == 0 || *available == 0u) {
        (void)gx8002_image_b_uart_rx_irq_enable_100046ac(
            load32(state, 8u),
            (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_rx_irq_1000b198, 0u);
        return -1;
    }
    uint32_t count = expected - progress;
    if (count > *available) count = *available;
    if (count != 0u) {
        uint8_t *destination = (uint8_t *)(uintptr_t)load32(packet, 16u);
        for (uint32_t index = 0u; index < count; ++index)
            destination[progress + index] = source[index];
        progress += count;
        store32(cursor, 0x308u, progress);
        *available -= count;
        if (progress == expected) {
            *input = source + count;
            store32(cursor, 0x308u, 0u);
            if (packet[7u] != 0u) {
                store32(state, 0x170u, 3u);
                return 0;
            }
            return 1;
        }
    }
    uint32_t remaining = expected - progress;
    if (remaining <= 32u) return 0;
    uint32_t destination = load32(packet, 16u) + progress;
    uint32_t next_boundary = (destination & ~UINT32_C(15)) + 16u;
    if (next_boundary >= destination) return 0;
    uint32_t dma_length = remaining & ~UINT32_C(15);
    (void)gx8002_image_b_uart_rx_irq_disable_100046e0(channel);
    (void)gx8002_image_b_uart_dma_receive_100047a4(
        channel, (uint8_t *)(uintptr_t)destination, dma_length,
        (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_rx_dma_complete_1000af94,
        0u);
    *available = 0u;
    store32(cursor, 0x308u, load32(cursor, 0x308u) + dma_length);
    *input = (uint8_t *)(uintptr_t)UINT32_C(0x2002d0f0);
    return 0;

packet_complete:
    store32(cursor, 0x308u, 0u);
    (void)gx8002_image_b_uart_rx_irq_enable_100046ac(
        load32(state, 8u),
        (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_rx_irq_1000b198, 0u);
    if (packet[7u] != 0u) {
        store32(state, 0x170u, 3u);
        return 0;
    }
    store32(state, 0x170u, 0u);
    state[0x30u] = (uint8_t)channel;
    store32(state, 0x34u, (uint32_t)load16(state, 0x24u) -
        (state[0x23u] != 0u ? 4u : 0u));
    (void)gx8002_image_b_audio_ring_write_10015b64(
        (volatile int32_t *)(uintptr_t)UINT32_C(0x2002d770),
        (const uint8_t *)(state + 0x1cu));
    store32(state, 0x1cu, 0u);
    store32(state, 0x34u, 0u);
    return 0;

registration_failure:
    store32(packet, 16u, 0u);
    store32(packet, 24u, 0u);
    return -1;
}
