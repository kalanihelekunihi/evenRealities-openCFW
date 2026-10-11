/* SPDX-License-Identifier: MIT
 * Image-B 0x1000a080 audio channel preparation from pinned native branches.
 * The children are separately selected C bodies; runtime SRAM/MMIO is an
 * independent placement and hardware qualification contract.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_channel_address_1000a05c(uint32_t channel);
extern uint32_t gx8002_image_b_audio_channel_extent_1000a034(uint32_t channel);
extern uint32_t gx8002_image_b_audio_runtime_pointer_1000324c(void);
extern uint32_t gx8002_image_b_audio_sample_bytes_10009f5c(void);
extern int32_t gx8002_image_b_set_logfbank_enable_10005ab4(
    uint32_t module_enable, uint32_t hmt_enable);
extern uint32_t gx8002_image_b_dual_buffer_100054cc(
    uint32_t channel, uint32_t left, uint32_t right, uint32_t bytes,
    uint32_t frame_count, uint32_t endian, uint32_t source);
extern uint32_t gx8002_image_b_pcm_path_1000568c(
    uint32_t channel, uint32_t address, uint32_t bytes,
    uint32_t frames, uint32_t word_mode, uint32_t output_mode);
extern uint32_t gx8002_image_b_audio_capture_setup_100055e0(
    uint32_t buffer, uint32_t bytes, uint32_t frame_quantum,
    uint32_t first_mode, uint32_t second_mode);
extern uint32_t gx8002_image_b_i2s_input_10005794(
    uint32_t pcm_length, uint32_t data_format, uint32_t clock_mode,
    uint32_t fsync_mode, uint32_t bclk_mode,
    uint32_t left_source, uint32_t right_source);
extern int32_t gx8002_image_b_audio_i2s_output_mode_100058ac(uint32_t value);

#define FIELD(offset) state[(offset) / 4u]

void gx8002_image_b_audio_channel_prepare_at_1000a080(
    volatile uint32_t *state, uint32_t flags, uint32_t channel,
    uint32_t address, uint32_t extent)
{
    const volatile uint8_t *bytes = (const volatile uint8_t *)state;
    if (channel == 1u) {
        uint32_t interleaved = (bytes[5] >> 3) & 1u;
        uint32_t bytes_per_buffer =
            ((flags & 9u) == 0u && interleaved != 0u)
                ? (extent >> 8) << 7 : extent & ~UINT32_C(127);
        uint32_t base = address & ~UINT32_C(7);
        if ((flags & 8u) == 0u) {
            FIELD(0x7c) = base;
            FIELD(0x80) = interleaved != 0u ? base + bytes_per_buffer : 0u;
            FIELD(0x84) = bytes_per_buffer;
            FIELD(0x8c) = 0u;
            FIELD(0x88) = 0x100u;
        } else {
            FIELD(0xe0) = extent;
            FIELD(0x84) = bytes_per_buffer;
            FIELD(0x7c) = base;
            FIELD(0xdc) = base;
            FIELD(0xe4) = extent >> 3;
            (void)gx8002_image_b_set_logfbank_enable_10005ab4(1u, 1u);
            (void)gx8002_image_b_pcm_path_1000568c(
                1u, FIELD(0xdc), FIELD(0xe0), FIELD(0xe4),
                FIELD(0xe8), FIELD(0xec));
            FIELD(0x88) = 0x400u;
        }
        (void)gx8002_image_b_dual_buffer_100054cc(
            1u, FIELD(0x7c), FIELD(0x80), FIELD(0x84),
            FIELD(0x88), FIELD(0x8c), FIELD(0x90));
        return;
    }

    if (channel == 2u) {
        uint32_t interleaved = (bytes[0x21] >> 3) & 1u;
        uint32_t chosen_extent =
            ((flags & 1u) == 0u && interleaved != 0u)
                ? (extent >> 8) << 7 : extent & ~UINT32_C(127);
        uint32_t base = address & ~UINT32_C(7);
        int32_t sample_bytes =
            (int32_t)gx8002_image_b_audio_sample_bytes_10009f5c();
        if (sample_bytes < 0) sample_bytes += 63;
        uint32_t rounded = (uint32_t)sample_bytes & ~UINT32_C(63);
        FIELD(0x9c) = chosen_extent;
        FIELD(0x94) = base;
        FIELD(0xa4) = 0u;
        FIELD(0x98) = interleaved != 0u ? chosen_extent + base : 0u;
        FIELD(0xa0) = rounded;
        (void)gx8002_image_b_dual_buffer_100054cc(
            2u, FIELD(0x94), FIELD(0x98), FIELD(0x9c),
            FIELD(0xa0), FIELD(0xa4), FIELD(0xa8));
        return;
    }

    if (channel == 4u) {
        FIELD(0xac) = address & ~UINT32_C(7);
        FIELD(0xb0) = extent;
        FIELD(0xb4) = 1u;
        (void)gx8002_image_b_set_logfbank_enable_10005ab4(1u, 1u);
        (void)gx8002_image_b_audio_capture_setup_100055e0(
            FIELD(0xac), FIELD(0xb0), FIELD(0xb4),
            FIELD(0xb8), FIELD(0xbc));
        return;
    }

    if (channel == 8u) {
        (void)gx8002_image_b_i2s_input_10005794(
            FIELD(0xc0), FIELD(0xc4), FIELD(0xc8), FIELD(0xcc),
            FIELD(0xd0), FIELD(0xd4), FIELD(0xd8));
        (void)gx8002_image_b_audio_i2s_output_mode_100058ac(0u);
    }
}

void gx8002_image_b_audio_channel_prepare_1000a080(
    uint32_t flags, uint32_t channel)
{
    uint32_t address = gx8002_image_b_audio_channel_address_1000a05c(channel);
    uint32_t extent = gx8002_image_b_audio_channel_extent_1000a034(channel);
    volatile uint32_t *state = (volatile uint32_t *)(uintptr_t)
        gx8002_image_b_audio_runtime_pointer_1000324c();
    gx8002_image_b_audio_channel_prepare_at_1000a080(
        state, flags, channel, address, extent);
}
