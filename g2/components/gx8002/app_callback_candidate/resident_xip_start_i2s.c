/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10208ff0..0x1020910e. Full startup call order,
 * three stack descriptors, app-state changes, and exact stock logs.
 * Hardware and product-buffer addresses remain real runtime contracts.
 */
#include <stdint.h>
#include "resident_sample_product_data.h"

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern int32_t gx8002_xip_padmux_set_102065dc(uint32_t, uint32_t);
extern uint32_t gx8002_resident_clock_module_source_24be0(
    uint32_t, uint32_t);
extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t);
extern uint32_t gx8002_xip_audio_out_init_10205530(uint32_t);
extern uint32_t gx8002_xip_audio_out_alloc_playback_1020537c(uint32_t);
extern uint32_t gx8002_xip_audio_out_free_102053b0(uint32_t);
extern uint32_t gx8002_xip_audio_out_exit_10205574(void);
extern uint32_t gx8002_xip_audio_out_config_cb_10205450(uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_out_set_db_102054c0(uint32_t, int32_t);
extern uint32_t gx8002_xip_audio_out_set_channel_102054f8(
    uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_out_config_buffer_102053e4(
    uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_out_config_pcm_10205418(
    uint32_t, uint32_t);
extern uint32_t gx8002_xip_mic_buffer_size_10206e78(void);
extern uint32_t gx8002_xip_mic_buffer_addr_10206e6c(void);
extern uint32_t gx8002_xip_audio_range_callback_10208d98(uint32_t, uint32_t);

static volatile uint32_t *const application =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e8c4);
static volatile uint8_t *const shared_channel =
    (volatile uint8_t *)(void *)&gx8002_sample_registration_26d30;

struct gx8002_pcm_request {
    uint32_t sampling_rate;
    uint8_t channels;
    uint8_t bits;
    uint8_t reserve_6;
    uint8_t reserve_7;
    uint32_t master_clock;
};
_Static_assert(sizeof(struct gx8002_pcm_request) == 12u,
               "stock PCM request stack extent");

uint32_t gx8002_xip_start_i2s_10208ff0(void)
{
    (void)gx8002_xip_tws_publish_10206c24(
        "[YW_APP]:%s, %d\n", "start_i2s", 277);
    if (application[5] != 0u) return UINT32_MAX;
    application[5] = 1u;
    shared_channel[4] = 1u;
    if (application[1] != UINT32_MAX) {
        (void)gx8002_xip_tws_publish_10206c24(
            "[YW_APP]:%s, %d, handle = %d\n",
            "start_i2s", 290, (int32_t)application[1]);
        (void)gx8002_xip_audio_out_free_102053b0(application[1]);
        (void)gx8002_xip_audio_out_exit_10205574();
        application[1] = UINT32_MAX;
    }
    (void)gx8002_xip_padmux_set_102065dc(7u, 3u);
    (void)gx8002_xip_padmux_set_102065dc(8u, 3u);
    (void)gx8002_xip_padmux_set_102065dc(9u, 3u);
    (void)gx8002_xip_padmux_set_102065dc(10u, 3u);
    (void)gx8002_resident_clock_module_source_24be0(8u, 5u);
    (void)gx8002_xip_audio_out_init_10205530(0u);

    struct gx8002_pcm_request pcm = {
        .sampling_rate = 16000u,
        .channels = 2u,
        .bits = 16u,
        .reserve_6 = 0u,
        .reserve_7 = 0u,
        .master_clock = gx8002_resident_clock_frequency_25210(11u)
    };
    application[1] = gx8002_xip_audio_out_alloc_playback_1020537c(0u);
    uint32_t callbacks[2] = {
        (uint32_t)(uintptr_t)&gx8002_xip_audio_range_callback_10208d98,
        0u
    };
    (void)gx8002_xip_audio_out_config_cb_10205450(
        application[1], (uint32_t)(uintptr_t)callbacks);
    (void)gx8002_xip_audio_out_set_db_102054c0(application[1], 0);

    application[0] =
        (uint32_t)((int32_t)gx8002_xip_mic_buffer_size_10206e78() / 2);
    (void)gx8002_xip_audio_out_set_channel_102054f8(application[1], 0u);
    application[6] = gx8002_xip_mic_buffer_addr_10206e6c();
    application[7] = gx8002_xip_mic_buffer_addr_10206e6c() + application[0];
    uint32_t buffer[3] = {application[6], application[7], application[0]};
    (void)gx8002_xip_audio_out_config_buffer_102053e4(
        application[1], (uint32_t)(uintptr_t)buffer);
    (void)gx8002_xip_audio_out_config_pcm_10205418(
        application[1], (uint32_t)(uintptr_t)&pcm);

    (void)gx8002_xip_tws_publish_10206c24(
        "\tMCLK:%dHz\n", gx8002_resident_clock_frequency_25210(11u));
    (void)gx8002_xip_tws_publish_10206c24("\tLRCLK:%dHz\n", pcm.sampling_rate);
    (void)gx8002_xip_tws_publish_10206c24("\tbits:%d\n", pcm.bits);
    (void)gx8002_xip_tws_publish_10206c24(
        "\t%s Init OK\n", "I2S out Master");
    return 0u;
}
