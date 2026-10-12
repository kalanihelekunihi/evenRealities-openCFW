/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102091bc..0x1020923a. App task poll,
 * I2S request lock/unlock, and signed timeout countdown.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_notification_poll_102097c8(void);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern uint32_t g2_codec_channel_timer_start(uint32_t);
extern uint32_t gx8002_xip_start_i2s_10208ff0(void);
extern void gx8002_xip_stop_i2s_1020913c(void);
extern void g2_codec_construct_request(void);
extern uint32_t gx8002_xip_power_unlock_102077d4(int32_t);
extern int32_t gx8002_xip_tws_command_10207808(uint32_t);

static volatile uint32_t *const request =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e92c);
static volatile uint8_t *const mode =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e930);
static volatile uint32_t *const application =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e8c4);

uint32_t gx8002_xip_i2s_request_tick_102091bc(void)
{
    (void)gx8002_xip_notification_poll_102097c8();
    if (*request == 1u) {
        (void)gx8002_xip_tws_publish_10206c24(
            "processing i2s status request, mode_state = %d\n", *mode);
        if (*mode == 1u) {
            (void)g2_codec_channel_timer_start(application[2]);
            (void)gx8002_xip_tws_publish_10206c24(
                "====  I2S output requested, lock ====\n");
            (void)gx8002_xip_start_i2s_10208ff0();
            g2_codec_construct_request();
            *request = 0u;
        } else if (*mode == 0u) {
            (void)gx8002_xip_stop_i2s_1020913c();
            g2_codec_construct_request();
            *request = 0u;
            (void)gx8002_xip_power_unlock_102077d4(
                (int32_t)application[2]);
            (void)gx8002_xip_tws_publish_10206c24(
                "====  I2S output requested, unlock ====\n");
            (void)gx8002_xip_tws_command_10207808(13u);
        }
    }
    int32_t remaining = (int32_t)application[3];
    if (remaining > 0) {
        remaining = (int32_t)((uint32_t)remaining - 10u);
        application[3] = (uint32_t)remaining;
        if (remaining <= 0 && application[5] == 0u) {
            (void)gx8002_xip_tws_publish_10206c24(
                "[YW_APP]UART wakeup timeout, unlock\n");
            (void)gx8002_xip_power_unlock_102077d4(
                (int32_t)application[2]);
            application[3] = 0u;
        }
    }
    return 0u;
}
