/* SPDX-License-Identifier: MIT
 * Image-B native UART audio TX completion state machine at
 * 0x1000afc4..0x1000b189, verified against the original CK804 disassembly.
 * The six callback records at 0x2002d148 and two channel records are native
 * shared-RAM operands; final source-owned SRAM placement is still open.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_audio_uart_segment_send_1000ab7c(
    uint32_t channel, const uint8_t *packet, uint32_t *available);
extern int32_t gx8002_image_b_uart_poll_write_buffer_10004614(
    uint32_t port, const uint8_t *source, int32_t count);
extern uint32_t gx8002_image_b_crc32_1000c5c4(
    uint32_t seed, const unsigned char *data, unsigned int length);
extern uint32_t gx8002_image_b_audio_resource_unmark_1000a8c4(int32_t resource);
extern int32_t gx8002_image_b_audio_uart_tx_start_1000ab10(uint32_t channel);

typedef void (*audio_finished_fn)(uint8_t *packet, uint32_t context);

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

int32_t gx8002_image_b_audio_uart_tx_complete_1000afc4(
    uint32_t channel, uint32_t available)
{
    uint32_t selected = channel & 0xffu;
    uintptr_t state_address;
    if (selected == 0u) state_address = UINT32_C(0x2002cc20);
    else if (selected == 1u) state_address = UINT32_C(0x2002cd9c);
    else return -1;
    volatile uint8_t *state = (volatile uint8_t *)state_address;
    volatile uint8_t *shared = (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002cc20);
    volatile uint8_t *cursor = shared + channel * 4u;
    uint8_t *packet = (uint8_t *)(state_address + 0x3cu);
    for (;;) {
        uint32_t stage = load32(state, 0x174u);
        if (stage == 1u) {
            int32_t result = gx8002_image_b_audio_uart_segment_send_1000ab7c(
                channel, packet, &available);
            if (result == 1) {
                store32(state, 0x174u, state[0x43u] == 0u ? 3u : 2u);
            }
        } else if (stage == 0u) {
            uint32_t progress = load32(cursor, 0x510u);
            uint32_t count = 14u - progress;
            if (count > available) count = available;
            (void)gx8002_image_b_uart_poll_write_buffer_10004614(
                channel, packet + progress, (int32_t)count);
            uint32_t next = load32(cursor, 0x510u) + count;
            available -= count;
            if (next == 14u) {
                store32(cursor, 0x510u, 0u);
            } else {
                store32(cursor, 0x510u, next);
                if (next != 0u) goto availability_check;
            }
            store32(state, 0x174u, load16(state, 0x44u) == 0u ? 3u : 1u);
        } else if (stage == 2u) {
            uint32_t progress = load32(cursor, 0x518u);
            if (progress == 0u) {
                uint32_t crc = gx8002_image_b_crc32_1000c5c4(
                    0u, (const unsigned char *)(uintptr_t)load32(state, 0x4cu),
                    load32(state, 0x54u));
                store32(cursor, 0x520u, crc);
                progress = load32(cursor, 0x518u);
            }
            uint32_t count = 4u - progress;
            if (count > available) count = available;
            (void)gx8002_image_b_uart_poll_write_buffer_10004614(
                channel,
                (const uint8_t *)(uintptr_t)(UINT32_C(0x2002cc20) + 0x520u +
                    channel * 4u + progress), (int32_t)count);
            uint32_t next = load32(cursor, 0x518u) + count;
            available -= count;
            if (next == 4u) {
                store32(cursor, 0x518u, 0u);
                store32(state, 0x174u, 3u);
            } else {
                store32(cursor, 0x518u, next);
                if (next == 0u) store32(state, 0x174u, 3u);
            }
        } else if (stage == 3u) {
            uint8_t kind = packet[0x14u];
            if (kind == 0u || kind == 1u) {
                volatile uint8_t *owner = (volatile uint8_t *)(uintptr_t)
                    (kind == 0u ? UINT32_C(0x2002cc20) : UINT32_C(0x2002cd9c));
                (void)gx8002_image_b_audio_resource_unmark_1000a8c4(
                    (int32_t)load32(owner, 0x178u));
                uint16_t key = load16((volatile uint8_t *)packet, 4u);
                volatile uint8_t *table = (volatile uint8_t *)(uintptr_t)
                    UINT32_C(0x2002d148);
                for (uint32_t index = 0u; index < 6u; ++index) {
                    volatile uint8_t *record = table + index * 16u;
                    if (load32(record, 4u) == (uint32_t)key &&
                        load32(record, 0u) == (uint32_t)kind) {
                        audio_finished_fn callback = (audio_finished_fn)(uintptr_t)
                            load32(record, 8u);
                        callback(packet, load32(record, 12u));
                        break;
                    }
                }
            }
            if (gx8002_image_b_audio_uart_tx_start_1000ab10(selected) == -1)
                return 0;
        }
availability_check:
        if (available == 0u) return 0;
    }
}
