/* ALS driver open/close and timer state machine, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\sensor\als\als.c.
 * Native DRV_ALSOpen 0x4ae10a..0x4ae218, DRV_ALSClose 0x4ae218..0x4ae282,
 * DRV_ALSTimerHandlerStart 0x4ae2b6..0x4ae3b2, DRV_ALSTimerHandlerAdjust
 * 0x4ae3c8..0x4ae4c6, DRV_ALSTimerHandlerPolling 0x4ae4f8..0x4ae6c4 and
 * DRV_ALSTimerHandler 0x4ae6d0..0x4ae732; literal pools 0x4ae3b4..0x4ae3c4,
 * 0x4ae4c8..0x4ae4f4, 0x4ae734..0x4ae738, 0x4ae810..0x4ae818,
 * 0x4ae8d4..0x4ae8e0, 0x4ae94c..0x4aea08.
 *
 * Open powers and configures the sensor, then arms the sensor-hub timer for
 * 110 ms. Each expiry runs DRV_ALSTimerHandler, which dispatches on the status
 * at 0x200741c4:
 *   START   (1): first reading; target from it; publish it with notify_app
 *                unless a manual-brightness lock is active; go to POLLING.
 *   ADJUST  (2): every 200 ms step the current brightness toward the target
 *                (5% up, 2% up in the darkest bands, 2% down); POLLING when
 *                reached, publishing the final level with notify_app.
 *   POLLING (3): every 1000 ms read, filter by the 5-sample peak, update the
 *                target; while a manual brightness timestamp (settings word
 *                +4) is set, stay locked until 43200 s have passed or the
 *                peak window spreads by more than 300; otherwise switch to
 *                ADJUST when target != current. */
#include <stdint.h>
#include "g2_als.h"
#include "als_log.h"

#define OPEN_FIRST_READ_MS 110u
#define ADJUST_PERIOD_MS 200u
#define POLLING_PERIOD_MS 1000u
#define ADJUST_STEP_UP 5u
#define ADJUST_STEP_SLOW 2u
#define MANUAL_LOCK_SECONDS 43201u /* compared with <, i.e. 12 h */
#define SETTINGS_MANUAL_TIME 4u

extern int32_t hub_timer_start(uint32_t ms); /* 0x4a6988 */
extern int32_t hub_timer_stop(void);         /* 0x4a6998 */
extern uint8_t *audio_settings_get_config_46b44c(void); /* settings_get_config */
extern uint32_t display_driver_uled_type0_context_46bfe8(void); /* brightness setting byte */
extern uint32_t audio_log_context(void); /* service_time_current_epoch_get 0x44a1c6 */

static const char open_function[] = "DRV_ALSOpen"; /* ROM 0x789fa4 */
static const char already_opened[] = "ALS already opened"; /* ROM 0x77d8bc */
static const char already_opened_short[] = "[sensor_als]ALS already opened"; /* ROM 0x75d4f0 */
static const char open_error[] = "ALS open error"; /* ROM 0x784b90 */
static const char open_error_short[] = "[sensor_als]ALS open error"; /* ROM 0x7689b0 */
static const char close_function[] = "DRV_ALSClose"; /* ROM 0x784ba0 */
static const char already_closed[] = "ALS already closed"; /* ROM 0x77d8d0 */
static const char already_closed_short[] = "[sensor_als]ALS already closed"; /* ROM 0x75d510 */
static const char start_function[] = "DRV_ALSTimerHandlerStart"; /* ROM 0x7689cc */
static const char start_error[] = "ALS start read data error"; /* ROM 0x7689e8 */
static const char start_error_short[] = "[sensor_als]ALS start read data error"; /* ROM 0x746e14 */
static const char start_ok[] =
    "ALS start read data success, als value:%d, target:%d, scale_q10:%d"; /* ROM 0x6ff864 */
static const char start_ok_short[] =
    "[sensor_als]ALS start read data success, als value:%d, target:%d, scale_q10:%d"; /* ROM 0x6eaf48 */
static const char adjust_function[] = "DRV_ALSTimerHandlerAdjust"; /* ROM 0x768a04 */
static const char adjust_manual[] =
    "mannual brightness time is not 0, switch to polling status"; /* ROM 0x711d1c */
static const char adjust_manual_short[] =
    "[sensor_als]mannual brightness time is not 0, switch to polling status"; /* ROM 0x6f7d3c */
static const char adjust_done[] = "als brightness adjust success"; /* ROM 0x75d530 */
static const char adjust_done_short[] = "[sensor_als]als brightness adjust success"; /* ROM 0x73b824 */
static const char polling_function[] = "DRV_ALSTimerHandlerPolling"; /* ROM 0x768a20 */
static const char polling[] =
    "ALS polling, als_value:%d, peak_value:%d, target:%d, current:%d, scale_q10:%d"; /* ROM 0x6eaf98 */
static const char polling_short[] =
    "[sensor_als]ALS polling, als_value:%d, peak_value:%d, target:%d, current:%d, scale_q10:%d"; /* ROM 0x6df154 */
static const char unlocked[] = "als value is too different or 2 hours passed, unlock"; /* ROM 0x71b698 */
static const char unlocked_short[] =
    "[sensor_als]als value is too different or 2 hours passed, unlock"; /* ROM 0x6ff8a8 */
static const char locked[] = "als birghtness is locked"; /* ROM 0x768a3c */
static const char locked_short[] = "[sensor_als]als birghtness is locked"; /* ROM 0x746e3c */
static const char to_adjust[] = "switch to adjust status, %d -> %d"; /* ROM 0x751584 */
static const char to_adjust_short[] = "[sensor_als]switch to adjust status, %d -> %d"; /* ROM 0x730df4 */
static const char handler_function[] = "DRV_ALSTimerHandler"; /* ROM 0x77d8e4 */
static const char status_error[] = "ALS process status error"; /* ROM 0x768a58 */
static const char status_error_short[] = "[sensor_als]ALS process status error"; /* ROM 0x746e64 */

/* Settings word +4: epoch of the last manual brightness change, 0 if none. */
static uint32_t *manual_brightness_time(void)
{
    return (uint32_t *)(void *)(audio_settings_get_config_46b44c() + SETTINGS_MANUAL_TIME);
}

int32_t als_function_28(void)
{
    if (audio_als_manual_ready == 1u) {
        ALS_LOG(2u, open_function, 0x1b6u, 0x08000000u, already_opened, already_opened_short);
        return -1;
    }
    if (als_function_25() != 0) {
        ALS_LOG(1u, open_function, 0x1bcu, 0x04000000u, open_error, open_error_short);
        return -1;
    }
    audio_als_manual_ready = 1u;
    g2_als_process_status = G2_ALS_STATUS_START;
    audio_als_default_previous = 0u;
    audio_als_active_previous = 0u;
    audio_als_curve_index = 0u;
    audio_als_curve_nominal = display_driver_uled_type0_context_46bfe8();
    audio_als_curve_adjusted = 0u;
    audio_als_manual_level = display_driver_uled_type0_context_46bfe8();
    audio_als_manual_level_copy = audio_als_manual_level;
    audio_als_manual_pending = 0u;
    als_function_22();
    audio_als_manual_recalculate_4adcd8();
    als_function_06();
    (void)hub_timer_start(OPEN_FIRST_READ_MS);
    return 0;
}

int32_t als_function_29(void)
{
    if (audio_als_manual_ready == 0u) {
        ALS_LOG(2u, close_function, 0x1d4u, 0x08000000u, already_closed, already_closed_short);
        return -1;
    }
    audio_als_manual_ready = 0u;
    g2_als_process_status = G2_ALS_STATUS_CLOSED;
    als_function_26();
    (void)hub_timer_stop();
    return 0;
}

void als_function_31(void)
{
    g2_als_process_status = G2_ALS_STATUS_POLLING;
    (void)hub_timer_start(POLLING_PERIOD_MS);
    uint32_t lux = als_function_27();
    audio_als_default_previous = lux;
    if (lux == 0u) {
        ALS_LOG(2u, start_function, 0x1fbu, 0x08000000u, start_error, start_error_short);
        return;
    }
    als_function_04(lux);
    als_function_05(lux);
    audio_als_active_previous = lux;
    als_function_11(audio_als_active_previous);
    ALS_LOG(3u, start_function, 0x205u, 0x0cc00000u, start_ok, start_ok_short,
            lux, audio_als_curve_adjusted, audio_als_scale_active);
    if (*manual_brightness_time() == 0u)
        als_function_23(audio_als_curve_adjusted, 1u);
}

void als_function_32(void)
{
    if (*manual_brightness_time() != 0u) {
        g2_als_process_status = G2_ALS_STATUS_POLLING;
        (void)hub_timer_start(POLLING_PERIOD_MS);
        ALS_LOG(3u, adjust_function, 0x210u, 0x0c000000u, adjust_manual, adjust_manual_short);
        return;
    }
    uint32_t current = display_driver_uled_type0_context_46bfe8();
    uint32_t step = ADJUST_STEP_UP;
    audio_als_manual_level = current;
    if (audio_als_curve_adjusted == current) {
        g2_als_process_status = G2_ALS_STATUS_POLLING;
        (void)hub_timer_start(POLLING_PERIOD_MS);
        ALS_LOG(3u, adjust_function, 0x21bu, 0x0c000000u, adjust_done, adjust_done_short);
        als_function_23(current, 1u);
        return;
    }
    uint32_t next;
    if (current < audio_als_curve_adjusted) {
        if (als_function_24())
            step = ADJUST_STEP_SLOW;
        next = als_function_30(audio_als_curve_adjusted, current, step);
    } else {
        next = als_function_30(audio_als_curve_adjusted, current, ADJUST_STEP_SLOW);
    }
    als_function_23(next, 0u);
}

void als_function_33(void)
{
    uint32_t lux = als_function_27();
    audio_als_default_previous = lux;
    als_function_04(lux);
    als_function_05(lux);
    audio_als_active_previous = als_function_10();
    als_function_11(audio_als_active_previous);
    uint32_t current = display_driver_uled_type0_context_46bfe8();
    audio_als_manual_level = current;
    ALS_LOG(3u, polling_function, 0x23fu, 0x0d400000u, polling, polling_short,
            lux, audio_als_active_previous, audio_als_curve_adjusted, current,
            audio_als_scale_active);
    if (*manual_brightness_time() != 0u) {
        uint32_t now = audio_log_context();
        if (als_function_12() != 1 && now - *manual_brightness_time() < MANUAL_LOCK_SECONDS) {
            ALS_LOG(3u, polling_function, 0x249u, 0x0c000000u, locked, locked_short);
            return;
        }
        *manual_brightness_time() = 0u;
        ALS_LOG(3u, polling_function, 0x247u, 0x0c000000u, unlocked, unlocked_short);
    }
    if (audio_als_curve_adjusted != current) {
        g2_als_process_status = G2_ALS_STATUS_ADJUST;
        (void)hub_timer_start(ADJUST_PERIOD_MS);
        ALS_LOG(3u, polling_function, 0x254u, 0x0c800000u, to_adjust, to_adjust_short,
                current, audio_als_curve_adjusted);
    }
}

/* Sensor-hub timer expiry. */
void als_function_34(void)
{
    switch (g2_als_process_status) {
    case G2_ALS_STATUS_START:
        als_function_31();
        return;
    case G2_ALS_STATUS_ADJUST:
        als_function_32();
        return;
    case G2_ALS_STATUS_POLLING:
        als_function_33();
        return;
    default:
        ALS_LOG(2u, handler_function, 0x264u, 0x08000000u, status_error, status_error_short);
        return;
    }
}
