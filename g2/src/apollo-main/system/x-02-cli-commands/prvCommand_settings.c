/* Product FreeRTOS-Plus-CLI "set" and "get" setting commands (two stock
 * modules), stock directory D:\01_workspace\s200_ap510b_iar_git\kernel\
 * FreeRTOS-Plus-CLI\prvCommand\ (file names not retained). Native:
 *   set: key parsers 0x5837bc..0x583917, handler 0x583918..0x583ce5
 *        (inline "get" 0x583ce8, pool 0x583cf8..0x583df7); the registrar
 *        0x583cec is in a-60-cli-commands/cli_command_register.c.
 *   get: key parser 0x584470..0x5844fd, handler 0x5844fe..0x584701 (pool
 *        0x58470c..0x5847ab); registrar 0x584702 in the same a-60 file.
 * Key names are matched case-insensitively (strncasecmp). */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

enum {
    SET_KEY_NONE = 0,
    SET_KEY_SCREEN = 1,
    SET_KEY_WEARDETECT = 2,
    SET_KEY_AUTOBRIGHTNESS = 3,
    SET_KEY_SETTING = 4,
    SET_KEY_SILENTMODE = 5,
    SET_KEY_TIME_FORMAT = 6,
    SET_KEY_TEMPERATURE_UNIT = 7,
    SET_KEY_DATE_FORMAT = 9,     /* 8 is not produced by the parser */
    SET_KEY_DISTANCE_UNIT = 10,
    SET_KEY_METRIC_UNIT = 11
};

enum { SCREEN_SUB_NONE = 0, SCREEN_SUB_HEIGHT = 1, SCREEN_SUB_MODE = 2, SCREEN_SUB_BRIGHT = 3 };
enum { STATE_NONE = 0, STATE_ENABLE = 1, STATE_DISABLE = 2 };

enum {
    GET_KEY_NONE = 0,
    GET_KEY_TIME_FORMAT = 1,
    GET_KEY_TEMPERATURE_UNIT = 2,
    GET_KEY_DATE_FORMAT = 3,
    GET_KEY_DISTANCE_UNIT = 4,
    GET_KEY_METRIC_UNIT = 5,
    GET_KEY_DOMINANT_HAND = 6,
    GET_KEY_GESTURE_APP = 7
};

#define SCREEN_HEIGHT_MAX 192
#define SCREEN_BRIGHT_MAX 100
#define DISPLAY_SET_BRIGHTNESS_SLOT 5u /* display state table entry +0x14 */
#define GESTURE_SLOTS 3
#define GESTURE_APP_DISABLED 0u
#define GESTURE_APP_MENU 1u

/* Universal-setting unit record (audio_setting_unit_record_get_466010). */
typedef struct {
    uint8_t reserved0;         /* +0x00 */
    uint8_t metric_unit;       /* +0x01 */
    uint8_t date_format;       /* +0x02 */
    uint8_t distance_unit;     /* +0x03 */
    uint8_t temperature_unit;  /* +0x04 */
    uint8_t reserved5[0x13];
    uint32_t time_format;      /* +0x18 */
} g2_setting_unit_record_view_t;
_Static_assert(offsetof(g2_setting_unit_record_view_t, time_format) == 0x18u, "time_format at +0x18");

typedef void (*g2_display_brightness_fn_t)(uint32_t value);

extern int32_t strncasecmp_595f0c(const char *a, const char *b, uint32_t len);
extern int32_t atoi_48d868(const char *text);
extern int32_t iar_strtol_595a2e(const char *s, char **endptr, int32_t base);
extern uint32_t display_driver_set_brightness_46c984(uint32_t value); /* stores the screen Y offset */
extern uint32_t display_device_mode_set_473bc4(uint8_t mode);
extern uint32_t service_settings_auto_brightness(void);              /* 0x46bfe8 */
extern void *audio_als_callback_context_47394c(void);                /* display state table, ROM 0x776a3c */
extern void audio_wear_detect_set_enable_49eb1e(uint32_t requested);
extern uint32_t audio_uart_auto_brightness_configure(uint32_t value); /* settings_configure_auto_brightness 0x46c158 */
extern void SVC_Settings_DumpSettingConfig(void);                    /* 0x46b458 */
extern void SilentMode_SetStatus(uint32_t enabled);                  /* 0x4691bc */
extern uint8_t *audio_setting_unit_record_get_466010(void);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);        /* publish the unit record */
extern uint32_t audio_time_format_mode_46650c(void);                 /* 1 = 12-hour clock */
extern uint8_t svc_universal_setting_get_temperature_unit_466512(void);
extern uint8_t svc_universal_setting_get_date_format_466500(void);
extern uint8_t svc_universal_setting_get_distance_unit_466506(void);
extern uint8_t svc_universal_setting_get_metric_unit_4664fa(void);
extern uint8_t audio_uart_hand_side_get(void);                       /* 0x466518 dominant hand */
extern uint8_t universal_setting_startup_apptype_46651e(uint8_t system_on, uint8_t op_type);

/* set */
static const char s_key_screen[] = "screen";              /* ROM 0x78e294 */
static const char s_key_weardetect[] = "weardetect";      /* ROM 0x78b9cc */
static const char s_key_autobrightness[] = "autobrightness"; /* ROM 0x7881b0 */
static const char s_key_setting[] = "setting";            /* ROM 0x78e29c */
static const char s_key_silentmode[] = "silentmode";      /* ROM 0x78b9d8 */
static const char s_key_time_format[] = "time_format";    /* ROM 0x78b9e4 / 0x78ba08 */
static const char s_key_temperature_unit[] = "temperature_unit"; /* ROM 0x782830 / 0x782844 */
static const char s_key_date_format[] = "date_format";    /* ROM 0x78b9f0 / 0x78ba14 */
static const char s_key_distance_unit[] = "distance_unit"; /* ROM 0x7881c0 / 0x7881e0 */
static const char s_key_metric_unit[] = "metric_unit";    /* ROM 0x78b9fc / 0x78ba20 */
static const char s_key_dominant_hand[] = "dominant_hand"; /* ROM 0x7881f0 */
static const char s_key_gesture_app[] = "gesture_app";    /* ROM 0x78ba2c */
static const char s_sub_height[] = "height";              /* ROM 0x78e2a4 */
static const char s_sub_mode[] = "mode";                  /* ROM 0x78e2ac */
static const char s_sub_bright[] = "bright";              /* ROM 0x78e2b4 */
static const char s_enable[] = "enable";                  /* ROM 0x78e2bc */
static const char s_disable[] = "disable";                /* ROM 0x78e2c4 */
static const char s_get[] = "get";                        /* ROM 0x583ce8 */
static const char s_dump[] = "dump";                      /* ROM 0x78e2cc */
static const char s_set_missing[] = "set: missing parameters\r\n";             /* ROM 0x77013c */
static const char s_set_usage[] = "Usage: set screen height <value>\r\n";     /* ROM 0x758724 */
static const char s_height_missing[] = "set screen height: missing height value\r\n"; /* ROM 0x741de4 */
static const char s_height_range[] = "set screen height: height value must be 0 - 192\r\n"; /* ROM 0x72c1a0 */
static const char s_mode_missing[] = "set screen mode: missing mode value\r\n"; /* ROM 0x74cea4 */
static const char s_mode_usage[] = "Usage: set screen mode <0x71 or 0x72 or 0x73>\r\n"; /* ROM 0x736fd4 */
static const char s_mode_range[] =
    "set screen mode: mode value must be 0x71 or 0x72 or 0x73 or 0x74\r\n"; /* ROM 0x704a78 */
static const char s_bright_missing[] = "set screen bright: missing bright value\r\n"; /* ROM 0x741e10 */
static const char s_bright_usage[] = "Usage: set screen bright <value>\r\n";  /* ROM 0x758748 */
static const char s_bright_value[] = "get screen brightness value: %d\r\n";   /* ROM 0x75876c */
static const char s_bright_range[] = "set screen bright: bright value must be 0 - 100\r\n"; /* ROM 0x72c1d4 */
static const char s_screen_unknown[] = "set screen: unknown sub-command\r\n";  /* ROM 0x758790 */
static const char s_screen_usage[] =
    "Usage: set screen height <value> or set screen mode <value>\r\n";        /* ROM 0x70e0a4 */
static const char s_wear_invalid[] =
    "set weardetect: invalid state, use 'enable' or 'disable'\r\n";           /* ROM 0x717cbc */
static const char s_auto_invalid[] =
    "set autobrightness: invalid state, use 'enable' or 'disable'\r\n";       /* ROM 0x70e0e4 */
static const char s_setting_dump[] = "setting: dump\r\n";                     /* ROM 0x7881d0 */
static const char s_setting_unknown[] = "set setting: unknown sub-command\r\n"; /* ROM 0x7587b4 */
static const char s_setting_usage[] = "Usage: set setting dump\r\n";          /* ROM 0x770158 */
static const char s_silent_invalid[] =
    "set silentmode: invalid state, use 'enable' or 'disable'\r\n";           /* ROM 0x717cf8 */
static const char s_time_range[] = "set time_format: value must be 0 or 1\r\n"; /* ROM 0x74cecc */
static const char s_time_24[] = "Time_format set to:0, 24H\r\n";              /* ROM 0x770174 */
static const char s_time_12[] = "Time_format set to:1, 12H\r\n";              /* ROM 0x770190 */
static const char s_temp_range[] =
    "set temperature_unit: value must be 1(Celsius) or 2(Fahrenheit)\r\n";    /* ROM 0x704abc */
static const char s_temp_c[] = "Temperature_unit set to:1, Celsius\r\n";      /* ROM 0x74cef4 */
static const char s_temp_f[] = "Temperature_unit set to:2, Fahrenheit\r\n";   /* ROM 0x74cf1c */
static const char s_date_range[] = "set date_format: value must be 0, 1 or 2\r\n"; /* ROM 0x741e3c */
static const char s_date_set[] = "Date_format set to:%d\r\n";                 /* ROM 0x77ab1c */
static const char s_distance_range[] = "set distance_unit: value must be 0 or 1\r\n"; /* ROM 0x741e68 */
static const char s_distance_km[] = "Distance_unit set to:0, km\r\n";         /* ROM 0x763f90 */
static const char s_distance_mi[] = "Distance_unit set to:1, mi\r\n";         /* ROM 0x763fb0 */
static const char s_metric_range[] = "set metric_unit: value must be 0 or 1\r\n"; /* ROM 0x74cf44 */
static const char s_metric_metric[] = "Metric_unit set to:0, metric\r\n";     /* ROM 0x763fd0 */
static const char s_metric_imperial[] = "Metric_unit set to:1, imperial\r\n"; /* ROM 0x7587d8 */
static const char s_set_unknown[] = "set: unknown command\r\n";               /* ROM 0x77ab34 */
static const char s_set_supported[] = "Supported commands:\r\n";              /* ROM 0x77ab4c */
static const char *const s_set_help[] = {
    "  set screen height <value>\r\n",              /* ROM 0x763ff0 */
    "  set screen bright <value>\r\n",              /* ROM 0x764010 */
    "  set screen mode <0x71|0x72|0x73|0x74>\r\n",  /* ROM 0x741e94 */
    "  set weardetect <enable|disable>\r\n",        /* ROM 0x7587fc */
    "  set autobrightness <enable|disable>\r\n",    /* ROM 0x74cf6c */
    "  set setting dump\r\n",                       /* ROM 0x77ab64 */
    "  set silentmode <enable|disable>\r\n",        /* ROM 0x758820 */
    "  set time_format <0|1>\r\n",                  /* ROM 0x7701ac */
    "  set temperature_unit <1|2>\r\n",             /* ROM 0x764030 */
    "  set date_format <0|1|2>\r\n",                /* ROM 0x7701c8 */
    "  set distance_unit <0|1>\r\n",                /* ROM 0x7701e4 */
    "  set metric_unit <0|1>\r\n",                  /* ROM 0x770200 */
};

/* get */
static const char s_get_missing[] = "get: missing parameters\r\n";            /* ROM 0x77021c */
static const char s_get_usage[] = "Usage: get <setting_name>\r\n";            /* ROM 0x770238 */
static const char s_get_supported[] = "Supported settings:\r\n";              /* ROM 0x77ab7c */
static const char s_get_list1[] = "  time_format, temperature_unit, date_format\r\n"; /* ROM 0x737004 */
static const char s_get_list2[] = "  distance_unit, metric_unit, dominant_hand, gesture_app\r\n"; /* ROM 0x717d34 */
static const char s_get_time_24[] = "Current time_format:0, 24H\r\n";         /* ROM 0x764050 */
static const char s_get_time_12[] = "Current time_format:1, 12H\r\n";         /* ROM 0x764070 */
static const char s_get_temp_c[] = "Current temperature_unit:1, \xc2\xb0" "C\r\n"; /* ROM 0x758844 */
static const char s_get_temp_f[] = "Current temperature_unit:2, \xc2\xb0" "F\r\n"; /* ROM 0x758868 */
static const char s_get_temp_unknown[] = "Current temperature_unit:%d, Unknown\r\n"; /* ROM 0x74cf94 */
static const char s_get_date[] =
    "Current date_format:%d (0:YYYY/MM/DD, 1:MM/DD/YYYY, 2:DD/MM/YYYY)\r\n";  /* ROM 0x704b00 */
static const char s_get_km[] = "Current distance_unit:0, km\r\n";             /* ROM 0x764090 */
static const char s_get_mi[] = "Current distance_unit:1, mi\r\n";             /* ROM 0x7640b0 */
static const char s_get_metric[] = "Current metric_unit:0, metric\r\n";       /* ROM 0x7640d0 */
static const char s_get_imperial[] = "Current metric_unit:1, imperial\r\n";   /* ROM 0x75888c */
static const char s_get_left[] = "Current dominant_hand:0, left\r\n";         /* ROM 0x7640f0 */
static const char s_get_right[] = "Current dominant_hand:1, right\r\n";       /* ROM 0x7588b0 */
static const char s_gesture_title[] = "=== Gesture App Settings ===\r\n";     /* ROM 0x764110 */
static const char s_gesture_off[] = "Screen OFF gesture apps:\r\n";           /* ROM 0x770254 */
static const char s_gesture_on[] = "Screen ON gesture apps:\r\n";             /* ROM 0x770270 */
static const char s_gesture_app[] = "  [%d] %s: %d\r\n";                      /* ROM 0x788220 */
static const char s_gesture_menu[] = "  [%d] %s: MENU\r\n";                   /* ROM 0x78286c */
static const char s_gesture_disabled[] = "  [%d] %s:disabled\r\n";            /* ROM 0x77ab94 */
/* Gesture source names copied to the stack from ROM 0x78ba38. */
static const char *const s_gesture_names[GESTURE_SLOTS] = {
    "LEFT_LONG_PRESS",  /* ROM 0x788200 */
    "RIGHT_LONG_PRESS", /* ROM 0x782858 */
    "RING_LONG_PRESS",  /* ROM 0x788210 */
};
static const char s_get_unknown[] = "get: unknown setting name\r\n";          /* ROM 0x77028c */
static const char *const s_get_help[] = {
    "  get time_format\r\n",       /* ROM 0x782880 */
    "  get temperature_unit\r\n",  /* ROM 0x7702a8 */
    "  get date_format\r\n",       /* ROM 0x782894 */
    "  get distance_unit\r\n",     /* ROM 0x77abac */
    "  get metric_unit\r\n",       /* ROM 0x7828a8 */
    "  get dominant_hand\r\n",     /* ROM 0x77abc4 */
    "  get gesture_app\r\n",       /* ROM 0x7828bc */
};

uint8_t set_parse_key_5837bc(const char *text);
uint8_t set_parse_screen_sub_583894(const char *text);
uint8_t set_parse_enable_5838e0(const char *text);
int32_t cli_cmd_set_583918(char *write_buffer, size_t write_buffer_len, const char *command_string);
uint8_t get_parse_key_584470(const char *text);
int32_t cli_cmd_get_5844fe(char *write_buffer, size_t write_buffer_len, const char *command_string);

uint8_t set_parse_key_5837bc(const char *text)
{
    if (text == NULL)
        return SET_KEY_NONE;
    if (strncasecmp_595f0c(text, s_key_screen, 6u) == 0)
        return SET_KEY_SCREEN;
    if (strncasecmp_595f0c(text, s_key_weardetect, 10u) == 0)
        return SET_KEY_WEARDETECT;
    if (strncasecmp_595f0c(text, s_key_autobrightness, 14u) == 0)
        return SET_KEY_AUTOBRIGHTNESS;
    if (strncasecmp_595f0c(text, s_key_setting, 7u) == 0)
        return SET_KEY_SETTING;
    if (strncasecmp_595f0c(text, s_key_silentmode, 10u) == 0)
        return SET_KEY_SILENTMODE;
    if (strncasecmp_595f0c(text, s_key_time_format, 11u) == 0)
        return SET_KEY_TIME_FORMAT;
    if (strncasecmp_595f0c(text, s_key_temperature_unit, 16u) == 0)
        return SET_KEY_TEMPERATURE_UNIT;
    if (strncasecmp_595f0c(text, s_key_date_format, 11u) == 0)
        return SET_KEY_DATE_FORMAT;
    if (strncasecmp_595f0c(text, s_key_distance_unit, 13u) == 0)
        return SET_KEY_DISTANCE_UNIT;
    if (strncasecmp_595f0c(text, s_key_metric_unit, 11u) == 0)
        return SET_KEY_METRIC_UNIT;
    return SET_KEY_NONE;
}

uint8_t set_parse_screen_sub_583894(const char *text)
{
    if (text == NULL)
        return SCREEN_SUB_NONE;
    if (strncasecmp_595f0c(text, s_sub_height, 6u) == 0)
        return SCREEN_SUB_HEIGHT;
    if (strncasecmp_595f0c(text, s_sub_mode, 4u) == 0)
        return SCREEN_SUB_MODE;
    if (strncasecmp_595f0c(text, s_sub_bright, 6u) == 0)
        return SCREEN_SUB_BRIGHT;
    return SCREEN_SUB_NONE;
}

uint8_t set_parse_enable_5838e0(const char *text)
{
    if (text == NULL)
        return STATE_NONE;
    if (strncasecmp_595f0c(text, s_enable, 6u) == 0)
        return STATE_ENABLE;
    if (strncasecmp_595f0c(text, s_disable, 7u) == 0)
        return STATE_DISABLE;
    return STATE_NONE;
}

static void set_screen(const char *command_string, const char *sub, int32_t *length)
{
    const char *value_text;
    g2_display_brightness_fn_t set_brightness;
    int32_t value;

    switch (set_parse_screen_sub_583894(sub)) {
    case SCREEN_SUB_HEIGHT:
        value_text = freertos_cli_get_parameter_5848fc(command_string, 3u, length);
        if (value_text == NULL) {
            audio_ble_hci_boot_log_4733ee(s_height_missing);
            audio_ble_hci_boot_log_4733ee(s_set_usage);
            return;
        }
        value = atoi_48d868(value_text);
        if ((uint32_t)value > (uint32_t)SCREEN_HEIGHT_MAX) {
            audio_ble_hci_boot_log_4733ee(s_height_range);
            return;
        }
        (void)display_driver_set_brightness_46c984((uint32_t)value);
        return;
    case SCREEN_SUB_MODE:
        value_text = freertos_cli_get_parameter_5848fc(command_string, 3u, length);
        if (value_text == NULL) {
            audio_ble_hci_boot_log_4733ee(s_mode_missing);
            audio_ble_hci_boot_log_4733ee(s_mode_usage);
            return;
        }
        value = iar_strtol_595a2e(value_text, NULL, 16);
        if ((uint8_t)value == 0x71u || (uint8_t)value == 0x72u || (uint8_t)value == 0x73u ||
            (uint8_t)value == 0x74u) {
            (void)display_device_mode_set_473bc4((uint8_t)value);
            return;
        }
        audio_ble_hci_boot_log_4733ee(s_mode_range);
        return;
    case SCREEN_SUB_BRIGHT:
        value_text = freertos_cli_get_parameter_5848fc(command_string, 3u, length);
        if (value_text == NULL) {
            audio_ble_hci_boot_log_4733ee(s_bright_missing);
            audio_ble_hci_boot_log_4733ee(s_bright_usage);
            return;
        }
        if (strncasecmp_595f0c(value_text, s_get, 3u) == 0) {
            audio_ble_hci_boot_log_4733ee(s_bright_value, service_settings_auto_brightness());
            return;
        }
        value = atoi_48d868(value_text);
        if ((uint32_t)value > (uint32_t)SCREEN_BRIGHT_MAX) {
            audio_ble_hci_boot_log_4733ee(s_bright_range);
            return;
        }
        /* Stock passes r0 = 0 to the table getter; entry 5 sets brightness. */
        set_brightness = ((const g2_display_brightness_fn_t *)audio_als_callback_context_47394c())
            [DISPLAY_SET_BRIGHTNESS_SLOT];
        set_brightness((uint32_t)value);
        return;
    default:
        audio_ble_hci_boot_log_4733ee(s_screen_unknown);
        audio_ble_hci_boot_log_4733ee(s_screen_usage);
        return;
    }
}

int32_t cli_cmd_set_583918(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    g2_setting_unit_record_view_t *record;
    const char *key;
    const char *value_text;
    int32_t value;
    uint8_t state;
    uint32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    key = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (key == NULL) {
        audio_ble_hci_boot_log_4733ee(s_set_missing);
        audio_ble_hci_boot_log_4733ee(s_set_usage);
        return 0;
    }
    value_text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    if (value_text == NULL) {
        audio_ble_hci_boot_log_4733ee(s_set_missing);
        audio_ble_hci_boot_log_4733ee(s_set_usage);
        return 0;
    }
    switch (set_parse_key_5837bc(key)) {
    case SET_KEY_SCREEN:
        set_screen(command_string, value_text, &length);
        break;
    case SET_KEY_WEARDETECT:
        state = set_parse_enable_5838e0(value_text);
        if (state == STATE_ENABLE)
            audio_wear_detect_set_enable_49eb1e(1u);
        else if (state == STATE_DISABLE)
            audio_wear_detect_set_enable_49eb1e(0u);
        else
            audio_ble_hci_boot_log_4733ee(s_wear_invalid);
        break;
    case SET_KEY_AUTOBRIGHTNESS:
        state = set_parse_enable_5838e0(value_text);
        if (state == STATE_ENABLE)
            (void)audio_uart_auto_brightness_configure(1u);
        else if (state == STATE_DISABLE)
            (void)audio_uart_auto_brightness_configure(0u);
        else
            audio_ble_hci_boot_log_4733ee(s_auto_invalid);
        break;
    case SET_KEY_SETTING:
        if (strncasecmp_595f0c(value_text, s_dump, 4u) == 0) {
            SVC_Settings_DumpSettingConfig();
            audio_ble_hci_boot_log_4733ee(s_setting_dump);
        } else {
            audio_ble_hci_boot_log_4733ee(s_setting_unknown);
            audio_ble_hci_boot_log_4733ee(s_setting_usage);
        }
        break;
    case SET_KEY_SILENTMODE:
        state = set_parse_enable_5838e0(value_text);
        if (state == STATE_ENABLE)
            SilentMode_SetStatus(1u);
        else if (state == STATE_DISABLE)
            SilentMode_SetStatus(0u);
        else
            audio_ble_hci_boot_log_4733ee(s_silent_invalid);
        break;
    case SET_KEY_TIME_FORMAT:
        value = atoi_48d868(value_text);
        if (value != 0 && value != 1) {
            audio_ble_hci_boot_log_4733ee(s_time_range);
            break;
        }
        record = (g2_setting_unit_record_view_t *)(void *)audio_setting_unit_record_get_466010();
        record->time_format = (uint32_t)value;
        audio_ble_hci_boot_log_4733ee(value == 0 ? s_time_24 : s_time_12);
        audio_uart_ring_unpair_publish_hand_4661a6();
        break;
    case SET_KEY_TEMPERATURE_UNIT:
        value = atoi_48d868(value_text);
        if (value != 1 && value != 2) {
            audio_ble_hci_boot_log_4733ee(s_temp_range);
            break;
        }
        record = (g2_setting_unit_record_view_t *)(void *)audio_setting_unit_record_get_466010();
        record->temperature_unit = (uint8_t)value;
        audio_ble_hci_boot_log_4733ee(value == 1 ? s_temp_c : s_temp_f);
        audio_uart_ring_unpair_publish_hand_4661a6();
        break;
    case SET_KEY_DATE_FORMAT:
        value = atoi_48d868(value_text);
        if ((uint32_t)value >= 3u) {
            audio_ble_hci_boot_log_4733ee(s_date_range);
            break;
        }
        record = (g2_setting_unit_record_view_t *)(void *)audio_setting_unit_record_get_466010();
        record->date_format = (uint8_t)value;
        audio_ble_hci_boot_log_4733ee(s_date_set, value);
        audio_uart_ring_unpair_publish_hand_4661a6();
        break;
    case SET_KEY_DISTANCE_UNIT:
        value = atoi_48d868(value_text);
        if (value != 0 && value != 1) {
            audio_ble_hci_boot_log_4733ee(s_distance_range);
            break;
        }
        record = (g2_setting_unit_record_view_t *)(void *)audio_setting_unit_record_get_466010();
        record->distance_unit = (uint8_t)value;
        audio_ble_hci_boot_log_4733ee(value == 0 ? s_distance_km : s_distance_mi);
        audio_uart_ring_unpair_publish_hand_4661a6();
        break;
    case SET_KEY_METRIC_UNIT:
        value = atoi_48d868(value_text);
        if (value != 0 && value != 1) {
            audio_ble_hci_boot_log_4733ee(s_metric_range);
            break;
        }
        record = (g2_setting_unit_record_view_t *)(void *)audio_setting_unit_record_get_466010();
        record->metric_unit = (uint8_t)value;
        audio_ble_hci_boot_log_4733ee(value == 0 ? s_metric_metric : s_metric_imperial);
        audio_uart_ring_unpair_publish_hand_4661a6();
        break;
    default:
        audio_ble_hci_boot_log_4733ee(s_set_unknown);
        audio_ble_hci_boot_log_4733ee(s_set_supported);
        for (i = 0u; i < sizeof(s_set_help) / sizeof(s_set_help[0]); i++)
            audio_ble_hci_boot_log_4733ee(s_set_help[i]);
        break;
    }
    return 0;
}

uint8_t get_parse_key_584470(const char *text)
{
    if (text == NULL)
        return GET_KEY_NONE;
    if (strncasecmp_595f0c(text, s_key_time_format, 11u) == 0)
        return GET_KEY_TIME_FORMAT;
    if (strncasecmp_595f0c(text, s_key_temperature_unit, 16u) == 0)
        return GET_KEY_TEMPERATURE_UNIT;
    if (strncasecmp_595f0c(text, s_key_date_format, 11u) == 0)
        return GET_KEY_DATE_FORMAT;
    if (strncasecmp_595f0c(text, s_key_distance_unit, 13u) == 0)
        return GET_KEY_DISTANCE_UNIT;
    if (strncasecmp_595f0c(text, s_key_metric_unit, 11u) == 0)
        return GET_KEY_METRIC_UNIT;
    if (strncasecmp_595f0c(text, s_key_dominant_hand, 13u) == 0)
        return GET_KEY_DOMINANT_HAND;
    if (strncasecmp_595f0c(text, s_key_gesture_app, 11u) == 0)
        return GET_KEY_GESTURE_APP;
    return GET_KEY_NONE;
}

/* One gesture slot per long-press source; 0 disabled, 1 menu, else app. */
static void get_print_gesture_apps(uint8_t system_on, const char *const names[GESTURE_SLOTS])
{
    int32_t i;
    uint8_t app;

    for (i = 0; i < GESTURE_SLOTS; i++) {
        app = universal_setting_startup_apptype_46651e(system_on, (uint8_t)i);
        if (app == GESTURE_APP_DISABLED)
            audio_ble_hci_boot_log_4733ee(s_gesture_disabled, i, names[i]);
        else if (app == GESTURE_APP_MENU)
            audio_ble_hci_boot_log_4733ee(s_gesture_menu, i, names[i]);
        else
            audio_ble_hci_boot_log_4733ee(s_gesture_app, i, names[i], app);
    }
}

int32_t cli_cmd_get_5844fe(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    const char *names[GESTURE_SLOTS];
    const char *key;
    uint8_t unit;
    uint32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    key = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (key == NULL) {
        audio_ble_hci_boot_log_4733ee(s_get_missing);
        audio_ble_hci_boot_log_4733ee(s_get_usage);
        audio_ble_hci_boot_log_4733ee(s_get_supported);
        audio_ble_hci_boot_log_4733ee(s_get_list1);
        audio_ble_hci_boot_log_4733ee(s_get_list2);
        return 0;
    }
    switch (get_parse_key_584470(key)) {
    case GET_KEY_TIME_FORMAT:
        audio_ble_hci_boot_log_4733ee(audio_time_format_mode_46650c() == 0u ? s_get_time_24 : s_get_time_12);
        break;
    case GET_KEY_TEMPERATURE_UNIT:
        unit = svc_universal_setting_get_temperature_unit_466512();
        if (unit == 1u)
            audio_ble_hci_boot_log_4733ee(s_get_temp_c);
        else if (unit == 2u)
            audio_ble_hci_boot_log_4733ee(s_get_temp_f);
        else
            audio_ble_hci_boot_log_4733ee(s_get_temp_unknown, unit);
        break;
    case GET_KEY_DATE_FORMAT:
        audio_ble_hci_boot_log_4733ee(s_get_date, svc_universal_setting_get_date_format_466500());
        break;
    case GET_KEY_DISTANCE_UNIT:
        audio_ble_hci_boot_log_4733ee(svc_universal_setting_get_distance_unit_466506() == 0u ? s_get_km
                                                                                           : s_get_mi);
        break;
    case GET_KEY_METRIC_UNIT:
        audio_ble_hci_boot_log_4733ee(svc_universal_setting_get_metric_unit_4664fa() == 0u
                                          ? s_get_metric
                                          : s_get_imperial);
        break;
    case GET_KEY_DOMINANT_HAND:
        audio_ble_hci_boot_log_4733ee(audio_uart_hand_side_get() == 0u ? s_get_left : s_get_right);
        break;
    case GET_KEY_GESTURE_APP:
        names[0] = s_gesture_names[0];
        names[1] = s_gesture_names[1];
        names[2] = s_gesture_names[2];
        audio_ble_hci_boot_log_4733ee(s_gesture_title);
        audio_ble_hci_boot_log_4733ee(s_gesture_off);
        get_print_gesture_apps(0u, names);
        audio_ble_hci_boot_log_4733ee(s_gesture_on);
        get_print_gesture_apps(1u, names);
        break;
    default:
        audio_ble_hci_boot_log_4733ee(s_get_unknown);
        audio_ble_hci_boot_log_4733ee(s_get_supported);
        for (i = 0u; i < sizeof(s_get_help) / sizeof(s_get_help[0]); i++)
            audio_ble_hci_boot_log_4733ee(s_get_help[i]);
        break;
    }
    return 0;
}
