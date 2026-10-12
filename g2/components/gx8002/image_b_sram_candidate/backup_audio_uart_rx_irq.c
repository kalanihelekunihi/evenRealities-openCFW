/* SPDX-License-Identifier: MIT
 * Image-B UART receive interrupt parser 0x1000b198..0x1000b415.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Uses native shared SRAM scratch 0x2002d0f0, per-port header progress at
 * 0x20016f64, and ring 0x2002d770. Their final source initializer/scatter
 * remains a separate obligation.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_poll_read_100045d8(
    uint32_t port, uint8_t *destination, int32_t count);
extern int32_t gx8002_image_b_audio_uart_receive_packet_1000ad60(
    uint32_t channel, volatile uint8_t *packet,
    uint8_t **input, uint32_t *available);
extern uint32_t gx8002_image_b_audio_ring_write_10015b64(
    volatile int32_t *ring, const uint8_t *source);
extern uint32_t gx8002_image_b_crc32_1000c5c4(
    uint32_t seed, const unsigned char *data, unsigned int length);

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

static void enqueue_packet(uint32_t channel, volatile uint8_t *state,
                           volatile int32_t *ring)
{
    store32(state, 0x170u, 0u);
    state[0x30u] = (uint8_t)channel;
    store32(state, 0x34u, (uint32_t)load16(state, 0x24u) -
        (state[0x23u] != 0u ? 4u : 0u));
    (void)gx8002_image_b_audio_ring_write_10015b64(
        ring, (const uint8_t *)(state + 0x1cu));
    store32(state, 0x1cu, 0u);
    store32(state, 0x34u, 0u);
}

int32_t gx8002_image_b_audio_uart_rx_irq_1000b198(
    uint32_t channel, uint32_t requested)
{
    uint32_t selected = channel & 0xffu;
    uintptr_t state_address;
    if (selected == 0u) state_address = UINT32_C(0x2002cc20);
    else if (selected == 1u) state_address = UINT32_C(0x2002cd9c);
    else return -1;
    volatile uint8_t *state = (volatile uint8_t *)state_address;
    volatile uint8_t *shared = (volatile uint8_t *)(uintptr_t)
        UINT32_C(0x2002cc20);
    uint8_t *scratch = (uint8_t *)(uintptr_t)UINT32_C(0x2002d0f0);
    store32(shared, 0x588u, (uint32_t)(uintptr_t)scratch);
    int32_t read = gx8002_image_b_uart_poll_read_100045d8(
        channel, scratch, (int32_t)requested);
    if (read == 0) return 0;
    uint32_t remaining = (uint32_t)read;
    volatile uint8_t *cursor = shared + channel * 4u;
    volatile uint32_t *header_progress =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20016f64);
    volatile int32_t *ring =
        (volatile int32_t *)(uintptr_t)UINT32_C(0x2002d770);
    volatile uint8_t *packet = state + 0x1cu;
    for (;;) {
        uint32_t stage = load32(state, 0x170u);
        if (stage == 0u) {
            uint32_t sync = load32(state, 0u);
            uint32_t rolling = load32(state, 0x1cu);
            if (sync == rolling) {
                store32(state, 0x170u, 1u);
            } else {
                uint8_t *input = (uint8_t *)(uintptr_t)load32(shared, 0x588u);
                while (remaining != 0u) {
                    uint8_t value = *input++;
                    rolling = (rolling >> 8) | ((uint32_t)value << 24);
                    store32(state, 0x1cu, rolling);
                    --remaining;
                    if (rolling == sync) {
                        store32(shared, 0x588u, (uint32_t)(uintptr_t)input);
                        store32(state, 0x170u, 1u);
                        break;
                    }
                }
                if (rolling != sync) {
                    store32(shared, 0x588u, (uint32_t)(uintptr_t)scratch);
                    return 0;
                }
            }
        } else if (stage == 1u) {
            uint32_t progress = header_progress[channel];
            if (progress < 14u) {
                uint32_t count = 14u - progress;
                if (count > remaining) count = remaining;
                uint8_t *input = (uint8_t *)(uintptr_t)load32(shared, 0x588u);
                for (uint32_t i = 0u; i < count; ++i)
                    packet[progress + i] = input[i];
                progress += count;
                header_progress[channel] = progress;
                remaining -= count;
                if (remaining != 0u)
                    store32(shared, 0x588u, (uint32_t)(uintptr_t)(input + count));
            }
            if (progress == 14u) {
                header_progress[channel] = 4u;
                uint32_t expected_crc = ((uint32_t)load16(packet, 12u) << 16) |
                    load16(packet, 10u);
                uint32_t actual_crc = gx8002_image_b_crc32_1000c5c4(
                    0u, (const unsigned char *)packet, 10u);
                if (actual_crc != expected_crc) {
                    store32(packet, 0u, 0u);
                    store32(state, 0x170u, 0u);
                } else if (load16(packet, 8u) != 0u) {
                    store32(state, 0x170u, 2u);
                } else {
                    store32(state, 0x170u, 0u);
                    state[0x30u] = (uint8_t)channel;
                    store32(state, 0x34u, 0u);
                    (void)gx8002_image_b_audio_ring_write_10015b64(
                        ring, (const uint8_t *)(state + 0x1cu));
                    store32(state, 0x1cu, 0u);
                    store32(state, 0x34u, 0u);
                }
            }
        } else if (stage == 2u) {
            uint8_t **input = (uint8_t **)(uintptr_t)
                (UINT32_C(0x2002cc20) + 0x588u);
            int32_t result = gx8002_image_b_audio_uart_receive_packet_1000ad60(
                channel, packet, input, &remaining);
            if (result == 1) enqueue_packet(channel, state, ring);
            else if (result == -1) store32(state, 0x170u, 0u);
        } else if (stage == 3u) {
            uint32_t progress = load32(cursor, 0x58cu);
            uint32_t count = 4u - progress;
            if (count > remaining) count = remaining;
            uint8_t *input = (uint8_t *)(uintptr_t)load32(shared, 0x588u);
            for (uint32_t i = 0u; i < count; ++i) {
                uint32_t crc = load32(state, 4u);
                crc = (crc >> 8) | ((uint32_t)input[i] << 24);
                store32(state, 4u, crc);
            }
            remaining -= count;
            progress += count;
            store32(shared, 0x588u, (uint32_t)(uintptr_t)(input + count));
            if (progress == 4u) {
                store32(state, 0x38u, load32(state, 4u));
                store32(state, 4u, 0u);
                store32(cursor, 0x58cu, 0u);
                enqueue_packet(channel, state, ring);
            } else {
                store32(cursor, 0x58cu, progress);
            }
        } else {
            return 0;
        }
        if (remaining == 0u) return 0;
    }
}
