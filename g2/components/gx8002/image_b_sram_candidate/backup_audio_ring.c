/* SPDX-License-Identifier: MIT
 * Image-B audio ring 0x10009fbc..0x1000a05c and pointer 0x1000324c.
 * Native MVCV returns equality as 0/1; the retained decompiler's bitwise
 * complement expression for 0x1000a00c/0x1000a018 is inaccurate.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_state_word_50_10009e18(void);
extern uint32_t gx8002_image_b_audio_state_word_54_10009e24(void);
extern uint32_t gx8002_image_b_audio_state_word_70_10009e30(void);
extern uint32_t gx8002_image_b_audio_state_word_74_10009e3c(void);
extern uint32_t gx8002_image_b_audio_word_08_10009f9c(void);

uint32_t gx8002_image_b_audio_runtime_pointer_1000324c(void)
{
    return UINT32_C(0x200167d0);
}

uint32_t gx8002_image_b_audio_ring_read_10009fbc(
    volatile int32_t *ring, uint8_t *destination)
{
    int32_t read_index = ring[1];
    if (read_index == ring[0]) return 0u;
    int32_t count = ring[4];
    if (count > 0) {
        int32_t i = 0;
        do {
            int32_t current =
                (int32_t)((uint32_t)read_index + (uint32_t)i);
            int32_t capacity = ring[3];
            int32_t offset = current - (current / capacity) * capacity;
            const uint8_t *source =
                (const uint8_t *)(uintptr_t)(uint32_t)ring[2];
            destination[i] = source[offset];
            ++i;
            count = ring[4];
            read_index = ring[1];
        } while (i < count);
    }
    int32_t next = (int32_t)((uint32_t)read_index + (uint32_t)count);
    int32_t capacity = ring[3];
    ring[1] = next - (next / capacity) * capacity;
    return 1u;
}

/* Native 0x10015b64, the write-side companion to the selected ring reader.
 * A full ring returns zero without touching input; signed capacity division
 * and the byte-at-a-time source advance follow the C-SKY instructions. */
uint32_t gx8002_image_b_audio_ring_write_at_10015b64(
    volatile int32_t *ring, uint8_t *destination, const uint8_t *source)
{
    int32_t write_index = ring[0];
    int32_t count = ring[4];
    int32_t capacity = ring[3];
    int32_t next = (int32_t)((uint32_t)write_index + (uint32_t)count);
    next -= (next / capacity) * capacity;
    if (next == ring[1]) return 0u;
    for (int32_t index = 0; index < count; ++index) {
        write_index = ring[0];
        capacity = ring[3];
        int32_t offset = (int32_t)((uint32_t)write_index + (uint32_t)index);
        offset -= (offset / capacity) * capacity;
        destination[offset] = source[index];
    }
    write_index = ring[0];
    count = ring[4];
    capacity = ring[3];
    next = (int32_t)((uint32_t)write_index + (uint32_t)count);
    ring[0] = next - (next / capacity) * capacity;
    return 1u;
}

uint32_t gx8002_image_b_audio_ring_write_10015b64(
    volatile int32_t *ring, const uint8_t *source)
{
    return gx8002_image_b_audio_ring_write_at_10015b64(
        ring, (uint8_t *)(uintptr_t)(uint32_t)ring[2], source);
}

uint32_t gx8002_image_b_audio_ring_empty_1000a00c(
    const volatile int32_t *ring)
{
    return ring[1] == ring[0];
}

uint32_t gx8002_image_b_audio_ring_next_empty_1000a018(
    const volatile int32_t *ring)
{
    int32_t next = (int32_t)((uint32_t)ring[0] + (uint32_t)ring[4]);
    int32_t capacity = ring[3];
    return next - (next / capacity) * capacity == ring[1];
}

uint32_t gx8002_image_b_audio_channel_extent_1000a034(uint32_t channel)
{
    if (channel == 2u)
        return (gx8002_image_b_audio_state_word_54_10009e24() /
                gx8002_image_b_audio_word_08_10009f9c()) * 2u;
    if (channel == 4u)
        return gx8002_image_b_audio_state_word_74_10009e3c();
    return 0u;
}

uint32_t gx8002_image_b_audio_channel_address_1000a05c(uint32_t channel)
{
    (void)gx8002_image_b_audio_runtime_pointer_1000324c();
    if (channel == 4u)
        return gx8002_image_b_audio_state_word_70_10009e30();
    if (channel == 1u || channel == 2u)
        return gx8002_image_b_audio_state_word_50_10009e18();
    return 0u;
}
