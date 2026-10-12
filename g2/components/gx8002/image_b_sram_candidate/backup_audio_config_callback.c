/* SPDX-License-Identifier: MIT
 * Image-B config callback 0x1000a2a0..0x1000a3fa. Branch and call order
 * follow the native C-SKY CFG; all child providers are separate C units.
 */
#include <stdint.h>

extern void gx8002_image_b_audio_gain_log_10003254(void);
extern uint32_t gx8002_image_b_audio_runtime_pointer_1000324c(void);
extern uint32_t gx8002_image_b_channel_polarity_100058bc(uint32_t, uint32_t);
extern uint32_t gx8002_image_b_audio_triplet_10005a5c(uint32_t, uint32_t,
                                                        uint32_t, uint32_t);
extern void gx8002_image_b_audio_pcm_control_10005978(uint32_t, uint32_t,
                                                       uint32_t, uint32_t);
extern uint32_t gx8002_image_b_channel_gain_10005920(uint32_t, uint32_t);
extern int32_t gx8002_image_b_audio_i2s_clock_1000588c(uint32_t);
extern void gx8002_image_b_input_route_100053e0(uint32_t, uint32_t,
                                                 uint32_t, uint32_t,
                                                 uint32_t, uint32_t);
extern uint32_t gx8002_image_b_channel_sources_10005490(uint32_t, uint32_t,
                                                          uint32_t);
extern int32_t gx8002_image_b_audio_i2s_input_mode_1000589c(uint32_t);
extern uint32_t gx8002_image_b_pdm_input_10005394(uint32_t);
extern int32_t gx8002_image_b_sadc_input_1000532c(uint32_t);
extern uint32_t gx8002_image_b_channel_rate_10005840(uint32_t);
extern void gx8002_image_b_audio_channel_prepare_1000a080(uint32_t, uint32_t);

static uint32_t word(const volatile uint8_t *state, uint32_t offset)
{
    return *(const volatile uint32_t *)(const volatile void *)(state + offset);
}
static uint32_t half(const volatile uint8_t *state, uint32_t offset)
{
    return *(const volatile uint16_t *)(const volatile void *)(state + offset);
}

int32_t gx8002_image_b_audio_configure_1000a2a0(void)
{
    gx8002_image_b_audio_gain_log_10003254();
    const volatile uint8_t *state = (const volatile uint8_t *)(uintptr_t)
        gx8002_image_b_audio_runtime_pointer_1000324c();
    uint32_t flags = word(state, 0u);
    if ((flags & 1u) != 0u) {
        (void)gx8002_image_b_channel_polarity_100058bc(
            1u, (state[5] >> 2) & 1u);
        (void)gx8002_image_b_audio_triplet_10005a5c(
            1u, word(state, 0x14u), word(state, 0x18u), word(state, 0x1cu));
        gx8002_image_b_audio_pcm_control_10005978(
            1u, word(state, 8u), word(state, 0xcu), word(state, 0x10u));
        (void)gx8002_image_b_sadc_input_1000532c(word(state, 0x5cu));
        (void)gx8002_image_b_channel_rate_10005840(state[4] & 63u);
        (void)gx8002_image_b_channel_gain_10005920(
            1u, (half(state, 4u) >> 6) & 15u);
    }
    if ((flags & 2u) != 0u) {
        (void)gx8002_image_b_channel_polarity_100058bc(
            2u, (state[0x21u] >> 2) & 1u);
        (void)gx8002_image_b_audio_triplet_10005a5c(
            2u, word(state, 0x30u), word(state, 0x34u), word(state, 0x38u));
        gx8002_image_b_audio_pcm_control_10005978(
            2u, word(state, 0x24u), word(state, 0x28u), word(state, 0x2cu));
        (void)gx8002_image_b_channel_gain_10005920(
            2u, (half(state, 0x20u) >> 6) & 15u);
        (void)gx8002_image_b_pdm_input_10005394(word(state, 0x60u));
        (void)gx8002_image_b_channel_sources_10005490(2u, 0u, 1u);
    }
    if ((flags & 4u) != 0u) {
        (void)gx8002_image_b_channel_polarity_100058bc(
            4u, (state[0x3du] >> 2) & 1u);
        (void)gx8002_image_b_audio_triplet_10005a5c(
            4u, word(state, 0x4cu), word(state, 0x50u), word(state, 0x54u));
        gx8002_image_b_audio_pcm_control_10005978(
            4u, word(state, 0x40u), word(state, 0x44u), word(state, 0x48u));
        (void)gx8002_image_b_channel_gain_10005920(
            4u, (half(state, 0x3cu) >> 6) & 15u);
        (void)gx8002_image_b_audio_i2s_clock_1000588c(4u);
        gx8002_image_b_input_route_100053e0(
            word(state, 0x64u), word(state, 0x68u), word(state, 0x6cu),
            word(state, 0x70u), word(state, 0x74u), word(state, 0x78u));
        (void)gx8002_image_b_channel_sources_10005490(4u, 1u, 0u);
        (void)gx8002_image_b_audio_i2s_input_mode_1000589c(0u);
    }
    uint32_t channels = state[0x58u];
    if ((channels & 1u) != 0u)
        gx8002_image_b_audio_channel_prepare_1000a080(flags, 1u);
    if ((channels & 2u) != 0u)
        gx8002_image_b_audio_channel_prepare_1000a080(flags, 2u);
    if ((channels & 4u) != 0u)
        gx8002_image_b_audio_channel_prepare_1000a080(flags, 4u);
    if ((channels & 8u) != 0u)
        gx8002_image_b_audio_channel_prepare_1000a080(flags, 8u);
    return 0;
}
