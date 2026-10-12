/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020979c and 0x102097c8 notification service.
 * Both literal pools resolve state to 0x2002e8f0; the VAD format is
 * exact stock XIP data at 0x1020b8f4.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void g2_codec_event_prepare(void);
extern uint32_t g2_codec_event_dispatch(uint32_t, uint32_t, uint32_t);
extern uint32_t g2_codec_timestamp(void);
extern uint32_t g2_codec_gpio_set_level(uint32_t, uint32_t);

uint32_t gx8002_xip_vad_notify_1020979c(uint32_t argument)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e8f0);
    if (*(volatile uint16_t *)(void *)(state + 0x34u) != 0u) {
        (void)gx8002_xip_tws_publish_10206c24("notify vad status\n");
        g2_codec_event_prepare();
        (void)g2_codec_event_dispatch(1u, 13u, argument);
    }
    return 0u;
}

uint32_t gx8002_xip_notification_poll_102097c8(void)
{
    volatile uint32_t *const stamp =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e910);
    uint32_t previous = *stamp;
    if (previous != 0u &&
        (uint32_t)(g2_codec_timestamp() - *stamp) > 60u) {
        (void)g2_codec_gpio_set_level(2u, 1u);
        *stamp = 0u;
    }
    return 0u;
}
