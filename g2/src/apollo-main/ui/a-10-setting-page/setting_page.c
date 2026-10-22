/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\setting\setting.c
 * Native setting_page_event_handler 0x467d68..0x467e49 and the calibration
 * status getter 0x467f08..0x467f0d; literal pool 0x467f10..0x467fef.
 * The neighbouring Setting_ui_event_handler 0x467e68 lives in
 * app/setting-ui/setting_ui_event_handler_467e68.c. */
#include <stdint.h>
#include <stddef.h>

/* Settings record fields used here (settings_get_config, 0x46b44c). */
#define SETTINGS_HEAD_UP_BASE_ANGLE 0x0cu /* int32 head-up angle offset */
#define SETTINGS_HEAD_UP_HEADING    0x10u /* int32 last measured heading */

#define APP_ID_SETTING 9u
#define LV_EVENT_CLICKED 10u
#define PAGE_EVENT_42 0x42u
#define PAGE_EVENT_43 0x43u
#define PAGE_EVENT_48 0x48u

extern uint8_t audio_uart_calibration_status_2007501c; /* RAM 0x2007501c */
extern uint8_t audio_uart_device_role_get(void);        /* 0x45a568 */
extern uint8_t *audio_settings_get_config_46b44c(void); /* settings_get_config */
extern int32_t semantic_get_heading_degrees(void);      /* 0x4a5d04 */
extern uint32_t audio_hub_parameter_config_4a6e3c(uint32_t type, const int32_t *param); /* HUB_ParameterConfig */
extern void audio_uart_master_display_refresh(uint32_t app, const void *payload,
                                              uint16_t length, uint32_t extra); /* 0x464bb2 */
extern void audio_uart_master_display_stop(uint32_t app, const void *payload,
                                           uint16_t length, uint32_t extra); /* 0x464c36 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "setting"; /* ROM 0x78e67c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c"; /* ROM 0x70f3a4 */
static const char page_fn[] = "setting_page_event_handler"; /* ROM 0x771c78 */
static const char clicked_fmt[] = "LV_EVENT_CLICKED head_up_angle_calibration:%d"; /* ROM 0x738ad4 */
static const char clicked_short[] = "[setting]LV_EVENT_CLICKED head_up_angle_calibration:%d"; /* ROM 0x723540 */

static int32_t config_word(const uint8_t *config, uint32_t offset)
{
    return *(const int32_t *)(const void *)(config + offset);
}

/* Click on the head-up calibration page (master only): record the current
 * heading, push the clamped [-90, 90] head-up angle to the sensor hub and
 * refresh the setting app. The HUB parameter's second word comes from a zero
 * ROM initializer (0x78e69c). */
uint32_t setting_page_event_handler_467d68(uint32_t unused0, uint32_t unused1, uint32_t event, void *data)
{
    (void)unused0;
    (void)unused1;
    (void)data;
    if (event == LV_EVENT_CLICKED) {
        if (audio_uart_device_role_get() != 1u)
            return 1u;
        uint8_t *config = audio_settings_get_config_46b44c();
        *(int32_t *)(void *)(config + SETTINGS_HEAD_UP_HEADING) = semantic_get_heading_degrees();
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, page_fn, 0x2deu, clicked_fmt,
                               config_word(audio_settings_get_config_46b44c(), SETTINGS_HEAD_UP_HEADING));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x0c400000u, clicked_short, clicked_short,
                                      config_word(audio_settings_get_config_46b44c(), SETTINGS_HEAD_UP_HEADING));
        const uint8_t *base = audio_settings_get_config_46b44c();
        const uint8_t *heading = audio_settings_get_config_46b44c();
        int32_t angle = config_word(heading, SETTINGS_HEAD_UP_HEADING) +
                        config_word(base, SETTINGS_HEAD_UP_BASE_ANGLE);
        if (angle > 90)
            angle = 90;
        if (angle < -90)
            angle = -90;
        int32_t param[2] = {0, 0};
        param[0] = angle;
        (void)audio_hub_parameter_config_4a6e3c(1u, param);
        audio_uart_master_display_refresh(APP_ID_SETTING, NULL, 0u, 0u);
        return 1u;
    }
    if (event == PAGE_EVENT_42 || event == PAGE_EVENT_43)
        return 1u;
    if (event == PAGE_EVENT_48 && audio_uart_device_role_get() == 1u)
        audio_uart_master_display_stop(APP_ID_SETTING, NULL, 0u, 0u);
    return 1u;
}

/* Recalibration-in-progress byte (set by setting type 4, cleared on setting
 * exit); the display thread reads it through this name. */
uint8_t onboarding_active_flag_467f08(void)
{
    return audio_uart_calibration_status_2007501c;
}
