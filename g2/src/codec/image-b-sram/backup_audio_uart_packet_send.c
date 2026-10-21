/* SPDX-License-Identifier: MIT
 * Image-B 0x1000b54c: prepare a 16-byte audio UART packet, CRC it, queue
 * through the native ring writer, then start TX only if inactive.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_ring_next_empty_1000a018(
    const volatile int32_t *ring);
extern uint32_t gx8002_image_b_audio_ring_write_10015b64(
    volatile int32_t *ring, const uint8_t *source);
extern uint32_t gx8002_image_b_crc32_1000c5c4(
    uint32_t initial, const unsigned char *bytes, uint32_t length);
extern void gx8002_image_b_dcache_clean_range_10004e74(uint32_t, int32_t);
extern int32_t gx8002_image_b_audio_uart_tx_start_1000ab10(uint32_t);

static uint32_t read_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(const volatile uint32_t *)(const volatile void *)(base + offset);
}
static uint16_t read_half(const volatile uint8_t *base, uint32_t offset)
{
    return *(const volatile uint16_t *)(const volatile void *)(base + offset);
}
static void write_word(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(volatile void *)(base + offset) = value;
}
static void write_half(volatile uint8_t *base, uint32_t offset, uint16_t value)
{
    *(volatile uint16_t *)(volatile void *)(base + offset) = value;
}

int32_t gx8002_image_b_audio_uart_packet_send_1000b54c(uint8_t *packet)
{
    uint8_t channel = packet[0x14u];
    uintptr_t base;
    if (channel == 0u) base = UINT32_C(0x2002cc20);
    else if (channel == 1u) base = UINT32_C(0x2002cd9c);
    else return -1;
    volatile uint8_t *state = (volatile uint8_t *)base;
    if (read_word(state, 0xcu) == 0u) return -1;
    if (read_word(packet, 0x18u) != 0u && read_word(packet, 0x10u) == 0u)
        return -1;
    volatile int32_t *ring = (volatile int32_t *)(base + 0x15cu);
    if (gx8002_image_b_audio_ring_next_empty_1000a018(ring) != 0u)
        return -1;

    uint16_t packet_length = read_half(packet, 0x18u);
    write_half(packet, 8u,
               (uint16_t)(packet_length + (packet[7] != 0u ? 4u : 0u)));
    if (read_word(packet, 0u) == 0u)
        write_word(packet, 0u, read_word(state, 0u));
    if ((read_half(packet, 4u) & 0xff00u) != 0x0200u) {
        uint8_t sequence = state[0x14u];
        state[0x14u] = (uint8_t)(sequence + 1u);
        packet[6] = sequence;
    }
    uint32_t crc = gx8002_image_b_crc32_1000c5c4(0u, packet, 10u);
    write_half(packet, 0xau, (uint16_t)crc);
    write_half(packet, 0xcu, (uint16_t)(crc >> 16));
    gx8002_image_b_dcache_clean_range_10004e74((uint32_t)(uintptr_t)packet, 16);
    if (gx8002_image_b_audio_ring_write_10015b64(ring, packet) == 0u)
        return -1;
    if (read_word(state, 0x18u) == 0u)
        (void)gx8002_image_b_audio_uart_tx_start_1000ab10(state[8u]);
    return 0;
}
