/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10208d98..0x10208e3d: sample audio range and
 * GPIO suspend/resume/event callbacks. The application state at
 * 0x2002e8c4 remains a genuine separately initialized runtime record.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_audio_out_push_frame_10205488(
    uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern uint32_t gx8002_xip_gpio_disable_trigger_10206074(uint32_t);
extern uint32_t gx8002_xip_gpio_enable_trigger_10205fb4(
    uint32_t, uint32_t, uint32_t, uint32_t);
extern int32_t gx8002_xip_padmux_set_102065dc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_gpio_set_direction_10205f24(
    uint32_t, uint32_t);
extern uint32_t g2_codec_channel_timer_start(uint32_t);
uint32_t gx8002_xip_app_gpio_event_10208e20(void);

static volatile uint32_t *const application =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e8c4);

uint32_t gx8002_xip_audio_range_callback_10208d98(
    uint32_t first, uint32_t last)
{
    uint32_t frame[2] = {
        last + 1u,
        (last - first) + 1u + last
    };
    if (frame[1] >= application[0]) {
        frame[0] = 0u;
        frame[1] = last - first;
    }
    return gx8002_xip_audio_out_push_frame_10205488(
        application[1], (uint32_t)(uintptr_t)frame);
}

uint32_t gx8002_xip_app_gpio_suspend_10208dcc(const char *message)
{
    (void)gx8002_xip_tws_publish_10206c24("[YW_APP]%s\n", message);
    (void)gx8002_xip_gpio_disable_trigger_10206074(6u);
    (void)gx8002_xip_padmux_set_102065dc(6u, 0u);
    return 0u;
}

uint32_t gx8002_xip_app_gpio_resume_10208dec(const char *message)
{
    (void)gx8002_xip_tws_publish_10206c24("%s\n", message);
    (void)gx8002_xip_padmux_set_102065dc(6u, 1u);
    (void)gx8002_xip_gpio_set_direction_10205f24(6u, 0u);
    (void)gx8002_xip_gpio_enable_trigger_10205fb4(
        6u, 1u, (uint32_t)(uintptr_t)&gx8002_xip_app_gpio_event_10208e20,
        0u);
    return 0u;
}

uint32_t gx8002_xip_app_gpio_event_10208e20(void)
{
    (void)gx8002_xip_tws_publish_10206c24(
        "[YW_APP]%s %d !\n", "gpio_callback", 124);
    (void)g2_codec_channel_timer_start(application[2]);
    application[3] = 2000u;
    return 0u;
}
