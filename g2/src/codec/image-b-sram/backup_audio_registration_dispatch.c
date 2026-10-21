/* SPDX-License-Identifier: MIT
 * Image-B 0x1000b4c8..0x1000b53e. A 32-byte ring record is CRC-checked
 * when byte 7 equals one, then dispatched by 16x28 registration key/type.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_ring_read_10009fbc(
    volatile int32_t *ring, uint8_t *destination);
extern uint32_t gx8002_image_b_crc32_1000c5c4(
    uint32_t initial, const unsigned char *bytes, uint32_t length);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

typedef int32_t (*registered_callback)(uint8_t *record, uint32_t context);

int32_t gx8002_image_b_audio_registration_dispatch_at_1000b4c8(
    volatile int32_t *ring, volatile uint8_t *table)
{
    uint8_t record[32];
    if (gx8002_image_b_audio_ring_read_10009fbc(ring, record) == 0u)
        return -1;

    if (record[7] == 1u) {
        uint32_t address = *(uint32_t *)(void *)(record + 0x10u);
        uint32_t length = *(uint32_t *)(void *)(record + 0x18u);
        uint32_t expected = *(uint32_t *)(void *)(record + 0x1cu);
        uint32_t actual = gx8002_image_b_crc32_1000c5c4(
            0u, (const unsigned char *)(uintptr_t)address, length);
        if (actual != expected) {
            (void)gx8002_image_b_heap_log_10009934("Crc Error %d\n", length);
            return -1;
        }
    }

    uint16_t key = *(uint16_t *)(void *)(record + 4u);
    uint8_t type = record[0x14u];
    for (uint32_t index = 0u; index < 16u; ++index) {
        volatile uint8_t *slot = table + index * 28u;
        uint32_t registered_key =
            *(volatile uint32_t *)(volatile void *)(slot + 4u);
        if (registered_key == (uint32_t)key && slot[0] == type) {
            uint32_t function =
                *(volatile uint32_t *)(volatile void *)(slot + 0x14u);
            uint32_t context =
                *(volatile uint32_t *)(volatile void *)(slot + 0x18u);
            return ((registered_callback)(uintptr_t)function)(record, context);
        }
    }
    return -1;
}

int32_t gx8002_image_b_audio_registration_dispatch_1000b4c8(void)
{
    return gx8002_image_b_audio_registration_dispatch_at_1000b4c8(
        (volatile int32_t *)(uintptr_t)UINT32_C(0x2002d770),
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002cf30));
}
