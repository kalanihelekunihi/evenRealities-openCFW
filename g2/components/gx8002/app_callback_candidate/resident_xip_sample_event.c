/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10208f04..0x10208fd6. Audio event dispatch,
 * channel state, first-frame ranges, and their original call order.
 * Context and buffer validity are runtime preconditions of the native body.
 */
#include <stdint.h>
#include "resident_sample_product_data.h"

extern uint32_t gx8002_xip_tws_context_10206ec8(
    uint32_t, void **, void *);
extern uint32_t gx8002_xip_vad_notify_1020979c(uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void g2_codec_event_91_helper(uint32_t);
extern uint32_t gx8002_xip_mic_buffer_10208e80(
    const uint8_t *, uint32_t, uint32_t, uint32_t *, uint32_t *);
extern uint32_t gx8002_xip_audio_out_push_frame_10205488(
    uint32_t, uint32_t);

static volatile uint32_t *const application =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e8c4);
static volatile uint8_t *const shared_channel =
    (volatile uint8_t *)(void *)&gx8002_sample_registration_26d30;

uint32_t gx8002_xip_sample_event_10208f04(const uint32_t *event)
{
    void *audio_context;
    uint32_t context_stride;
    (void)gx8002_xip_tws_context_10206ec8(
        event[1], &audio_context, &context_stride);
    uint32_t status = ((const uint8_t *)audio_context)[12] & 7u;
    if (status != *(volatile uint32_t *)(void *)shared_channel) {
        (void)gx8002_xip_vad_notify_1020979c(status);
        *(volatile uint32_t *)(void *)shared_channel = status;
    }
    if (event[0] == 100u) {
        (void)gx8002_xip_tws_publish_10206c24("wake up hey even\n");
        g2_codec_event_91_helper(event[0]);
    }
    if (event[0] == 101u) {
        (void)gx8002_xip_tws_publish_10206c24("wake up hi even\n");
        g2_codec_event_91_helper(event[0]);
    }
    if (event[0] == 91u && application[5] != 0u &&
        shared_channel[4] != 0u) {
        (void)gx8002_xip_tws_publish_10206c24(
            "=====    S:%d, first:%d  =====\n", event[1], 1u);
        const uint8_t *const mic_context =
            *(const uint8_t *const *)(const void *)audio_context;
        uint32_t first_address = 0u;
        uint32_t first_span = 0u;
        uint32_t second_address = 0u;
        uint32_t second_span = 0u;
        (void)gx8002_xip_mic_buffer_10208e80(
            mic_context, 0u, event[1], &first_address, &first_span);
        (void)gx8002_xip_mic_buffer_10208e80(
            mic_context, 1u, event[1], &second_address, &second_span);
        uint32_t range[2];
        range[0] = first_address - application[6];
        range[1] = range[0] + first_span - 1u;
        (void)gx8002_xip_tws_publish_10206c24(
            "=====   first push_frame S:%d, E:%d  =====\n",
            range[0], range[1]);
        (void)gx8002_xip_audio_out_push_frame_10205488(
            application[1], (uint32_t)(uintptr_t)range);
        shared_channel[4] = 0u;
    }
    return 0u;
}
