/* Dashboard watchface layout3 (hour/minute images with a digital clock,
 * weather and date labels and the glasses/ring battery row), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout3.c
 * (log tag "dashboard.wf.l3"). Native 0x5b9cec..0x5baa1d; literal pools
 * 0x5ba068..0x5ba07b, 0x5ba7a8, 0x5ba828..0x5ba83b, 0x5ba890..0x5ba89f,
 * 0x5ba904..0x5ba92f, 0x5ba9d8..0x5ba9e3, 0x5baa20..0x5baa43, 0x5baa78..0x5bab23.
 *
 * The functions from 0x5ba07c on fill the layout3 ops table (ROM 0x714008):
 * +0x00 create, +0x04 deinit, +0x08 set_x, +0x0c time, +0x10 date,
 * +0x14 weather, +0x18 glasses battery, +0x24 ring paired, +0x28 ring
 * connected. Slots +0x20 (0x5bab24) and +0x2c (0x5baa44) are stock functions
 * the inventory does not list (they sit inside the literal pool range).
 *
 * The Fahrenheit conversion is done in double precision and +0x14 is a
 * hard-float entry: profile g2-apollo-main-20. */
#include <stdint.h>
#include <stddef.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

#define LV_SIZE_CONTENT         0x3fffffff
#define LV_OBJ_FLAG_HIDDEN      0x1u
#define LV_OBJ_FLAG_SCROLLABLE  0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_TOP_LEFT       1u
#define LV_ALIGN_TOP_MID        2u
#define LV_ALIGN_TOP_RIGHT      3u
#define LV_FLEX_FLOW_ROW        0u
#define LV_FLEX_ALIGN_START     0u
#define LV_FLEX_ALIGN_CENTER    2u

/* am_hal_rtc_time_t word layout filled by service_time. */
typedef struct {
    uint32_t read_error; /* +0 */
    uint32_t weekday;    /* +4 */
    uint32_t century;    /* +8 */
    uint32_t year;       /* +12 */
    uint32_t month;      /* +16 */
    uint32_t day;        /* +20 */
    uint32_t hour;       /* +24 */
    uint32_t minute;     /* +28 */
    uint32_t second;     /* +32 */
    uint32_t hundredths; /* +36 */
} g2_calendar_t;

/* Layout3 state. */
extern void *g2_layout3_root;                    /* RAM 0x20074478 */
extern void *g2_layout3_hands;                   /* RAM 0x2007447c hour/minute image group */
extern void *g2_layout3_hour_img;                /* RAM 0x20074480 */
extern void *g2_layout3_minute_img;              /* RAM 0x20074484 */
extern void *g2_layout3_time_label;              /* RAM 0x20074488 */
extern void *g2_layout3_ble_off_img;             /* RAM 0x2007448c */
extern void *g2_layout3_weather_label;           /* RAM 0x20074490 */
extern void *g2_layout3_date_label;              /* RAM 0x20074494 */
extern void *g2_layout3_status_row;              /* RAM 0x20074498 */
extern void *g2_layout3_glasses_battery_img;     /* RAM 0x2007449c */
extern void *g2_layout3_ring_battery_img;        /* RAM 0x200744a0 */
extern uint8_t g2_layout3_align_setting;         /* RAM 0x20074fab cfg[4] */
extern uint8_t g2_layout3_date_enabled;          /* RAM 0x20074fac cfg[5] */
extern uint8_t g2_layout3_temperature_enabled;   /* RAM 0x20074fad cfg[6] */

/* Shared dashboard state. */
extern uint8_t g2_dashboard_state[];             /* RAM 0x200e3e80, 0xa0 bytes */
extern volatile uint32_t g2_dashboard_last_hour_200743bc;    /* RAM 0x200743bc */
extern volatile uint32_t g2_dashboard_last_minute_200743c0;  /* RAM 0x200743c0 */
extern volatile uint32_t g2_dashboard_last_month_200743c4;   /* RAM 0x200743c4 */
extern volatile uint32_t g2_dashboard_last_day_200743c8;     /* RAM 0x200743c8 */
extern volatile uint32_t g2_dashboard_last_weekday_200743cc; /* RAM 0x200743cc */
extern const char *g2_dashboard_weekday_keys_20004240[7];    /* RAM .data 0x20004240 i18n keys */

#define DS_TEMPERATURE  0x24u /* float, Celsius */
#define DS_WEATHER_TEXT 0x38u /* NUL-terminated */

/* ROM assets. */
extern const uint8_t g2_translate_lang_pair_font[]; /* ROM 0x7547b8 lv_font_t */
extern const uint8_t g2_wf_glasses_batt_0[];    /* ROM 0x76bae8, 31x10 */
extern const uint8_t g2_wf_glasses_batt_20[];   /* ROM 0x76bb20, 31x10 */
extern const uint8_t g2_wf_glasses_batt_40[];   /* ROM 0x76bb3c, 31x10 */
extern const uint8_t g2_wf_glasses_batt_60[];   /* ROM 0x76bb58, 31x10 */
extern const uint8_t g2_wf_glasses_batt_80[];   /* ROM 0x76bb74, 31x10 */
extern const uint8_t g2_wf_glasses_batt_100[];  /* ROM 0x76bb04, 31x10 */
extern const uint8_t g2_wf_ring_batt_0[];       /* ROM 0x7708e4, 30x10 */
extern const uint8_t g2_wf_ring_batt_20[];      /* ROM 0x77091c, 30x10 */
extern const uint8_t g2_wf_ring_batt_40[];      /* ROM 0x770938, 30x10 */
extern const uint8_t g2_wf_ring_batt_60[];      /* ROM 0x770954, 30x10 */
extern const uint8_t g2_wf_ring_batt_80[];      /* ROM 0x770970, 30x10 */
extern const uint8_t g2_wf_ring_batt_100[];     /* ROM 0x770900, 30x10 */
extern const uint8_t g2_layout4_ring_off_icon_770a34[]; /* ROM 0x770a34, 29x10 ring disconnected */
extern const uint8_t g2_layout4_ble_off_icon_769e5c[]; /* ROM 0x769e5c, 24x24 BLE disconnected */
/* 26x26 hour images, one per hour 1..12. */
extern const uint8_t g2_wf_hour_1[];   /* ROM 0x76ee88 */
extern const uint8_t g2_wf_hour_2[];   /* ROM 0x76eef8 */
extern const uint8_t g2_wf_hour_3[];   /* ROM 0x76ef14 */
extern const uint8_t g2_wf_hour_4[];   /* ROM 0x76ef30 */
extern const uint8_t g2_wf_hour_5[];   /* ROM 0x76ef4c */
extern const uint8_t g2_wf_hour_6[];   /* ROM 0x76ef68 */
extern const uint8_t g2_wf_hour_7[];   /* ROM 0x76ef84 */
extern const uint8_t g2_wf_hour_8[];   /* ROM 0x76efa0 */
extern const uint8_t g2_wf_hour_9[];   /* ROM 0x76efbc */
extern const uint8_t g2_wf_hour_10[];  /* ROM 0x76eea4 */
extern const uint8_t g2_wf_hour_11[];  /* ROM 0x76eec0 */
extern const uint8_t g2_wf_hour_12[];  /* ROM 0x76eedc */
/* 26x26 minute images, one per 5-minute step (1 = :05 .. 12 = :00). */
extern const uint8_t g2_wf_minute_1[];   /* ROM 0x76efd8 */
extern const uint8_t g2_wf_minute_2[];   /* ROM 0x76f048 */
extern const uint8_t g2_wf_minute_3[];   /* ROM 0x76f064 */
extern const uint8_t g2_wf_minute_4[];   /* ROM 0x76f080 */
extern const uint8_t g2_wf_minute_5[];   /* ROM 0x76f09c */
extern const uint8_t g2_wf_minute_6[];   /* ROM 0x76f0b8 */
extern const uint8_t g2_wf_minute_7[];   /* ROM 0x76f0d4 */
extern const uint8_t g2_wf_minute_8[];   /* ROM 0x76f0f0 */
extern const uint8_t g2_wf_minute_9[];   /* ROM 0x76f10c */
extern const uint8_t g2_wf_minute_10[];  /* ROM 0x76eff4 */
extern const uint8_t g2_wf_minute_11[];  /* ROM 0x76f010 */
extern const uint8_t g2_wf_minute_12[];  /* ROM 0x76f02c */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* libc-like, i18n, services. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern uint32_t audio_uart_page_460084(const char *key);                       /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);    /* localized text */
extern void service_time_current_calendar_get(g2_calendar_t *out);             /* 0x44a19a */
extern uint32_t audio_time_format_mode_46650c(void);                           /* 1 = 12-hour clock */
extern uint8_t svc_universal_setting_get_temperature_unit_466512(void);        /* 1 = Celsius as stored */
extern uint32_t UX_GetSystemBLEStatus(void);                                   /* 0x47d8ce */
extern uint32_t ux_ring_mac_is_set_47d9c4(void);
extern uint8_t ux_ring_connected_47d9cc(void);
extern uint8_t dashboard_ring_battery_level_get_49c5bc(void);
extern uint8_t ui_common_api_fn_00509f8e(void);                                /* glasses battery percent */

/* LVGL 9.3 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                            /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                 /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                 /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);          /* lv_obj_is_valid */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);          /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                     /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                     /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);          /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                     /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                     /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                                /* lv_obj_update_layout */
extern void audio_uart_page_43f6ac(void *obj, uint32_t align);                /* lv_obj_set_align */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                    /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                         /* lv_color_hex */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);       /* pad_column */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);       /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);       /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);       /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);       /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);  /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);    /* bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);       /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);       /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);       /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);       /* shadow_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);  /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);    /* text_opa */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);       /* radius */
extern void audio_lv_delete_44d7b8(void *obj);                                /* lv_obj_delete */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);                 /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_uart_page_498668(void *parent);                            /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);             /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                            /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);     /* lv_label_set_text */

static const char tag[] = "dashboard.wf.l3";                                         /* ROM 0x785990 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_watchface_layout3.c"; /* ROM 0x6e7390 */
static const char fn_create[] = "layout3_create";                                    /* ROM 0x785980 */
static const char m_parent_null[] = "layout3 create: parent NULL";                   /* ROM 0x76ab98 */
static const char t_parent_null[] = "[dashboard.wf.l3]layout3 create: parent NULL";  /* ROM 0x732e34 */
static const char m_create_cfg[] = "layout3 create: align=%u date_en=%u temperature_en=%u"; /* ROM 0x71dab0 */
static const char t_create_cfg[] =
    "[dashboard.wf.l3]layout3 create: align=%u date_en=%u temperature_en=%u";        /* ROM 0x6f9be4 */
static const char m_battery[] = "layout3_set_battery: lvl=%d";                       /* ROM 0x76abb4 */
static const char t_battery[] = "[dashboard.wf.l3]layout3_set_battery: lvl=%d";      /* ROM 0x732e64 */
static const char m_created[] = "layout3 created at x=%d (ble=%d)";                  /* ROM 0x753498 */
static const char t_created[] = "[dashboard.wf.l3]layout3 created at x=%d (ble=%d)"; /* ROM 0x728754 */
static const char s_dash[] = "-";                                                    /* ROM 0x5ba068 */
static const char s_time_fmt[] = "%02d:%02d";                                        /* ROM 0x78a784 */
static const char s_date_fmt[] = "%s %d";                                            /* ROM 0x78d344 */
static const char s_weather_c_fmt[] = "%s %d\xe2\x84\x83";                           /* ROM 0x78a790 "%s %d℃" */
static const char s_weather_f_fmt[] = "%s %d\xe2\x84\x89";                           /* ROM 0x78a79c "%s %d℉" */

#define L3_LOG_PREFIX(lvl, line, msg, ...)                                                 \
    do {                                                                                   \
        if (audio_log_flags() & 2u)                                                        \
            audio_log_extended((lvl), tag, src, fn_create, (line), (msg), ##__VA_ARGS__);  \
    } while (0)
#define L3_LOG_COMPRESSED(code, text, ...)                                                 \
    do {                                                                                   \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                          \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__);              \
    } while (0)

/* Layout geometry: the date label sits at y=226 when the weather line is
 * shown and drops to 246 otherwise; the battery row is bottom-aligned at 286. */
#define L3_Y_DATE_WITH_WEATHER 226
#define L3_Y_WEATHER           246
#define L3_ROW_BOTTOM          286

void lv_obj_set_style_pad_all_5b9cec(void *obj, int32_t value, uint32_t selector);
uint8_t layout3_align_from_setting_5b9d1e(uint8_t setting);
void layout3_place_5b9d36(void *obj, int32_t y);
const void *layout3_ring_battery_dsc_5b9d66(uint8_t level);
const void *layout3_glasses_battery_dsc_5b9db0(uint8_t level);
const void *layout3_hour_image_5b9dfa(int32_t hour);
const void *layout3_minute_image_5b9e7e(int32_t minute);
void layout3_format_time_5b9f06(int32_t hour, int32_t minute, char *buf, uint32_t size);
void layout3_format_weather_5b9f58(char *buf, uint32_t size);
void layout3_apply_ble_5b9fd6(uint32_t connected);
int32_t layout3_create_5ba07c(void *parent, int32_t x, const uint8_t *cfg);
void layout3_deinit_5ba728(void);
void layout3_set_x_5ba792(int32_t x);
void layout3_set_time_5ba7ac(int32_t hour, int32_t minute, uint32_t h24);
void layout3_set_date_5ba83c(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format);
VFP void layout3_set_weather_5ba8a0(uint16_t icon, uint32_t valid, uint32_t unit, float temperature);
void layout3_set_battery_5ba8d8(uint8_t level);
void layout3_set_ring_paired_5ba930(uint32_t paired, uint8_t battery);
void layout3_set_ring_connected_5ba9e4(uint32_t connected);

static uint32_t obj_valid(void *obj)
{
    return audio_terminal_ui_object_valid_43e2ea(obj);
}

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

void lv_obj_set_style_pad_all_5b9cec(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

uint8_t layout3_align_from_setting_5b9d1e(uint8_t setting)
{
    if (setting == 1u)
        return LV_ALIGN_TOP_MID;
    if (setting == 2u)
        return LV_ALIGN_TOP_RIGHT;
    return LV_ALIGN_TOP_LEFT;
}

void layout3_place_5b9d36(void *obj, int32_t y)
{
    if (obj != NULL) {
        audio_uart_page_43f6ac(obj, layout3_align_from_setting_5b9d1e(g2_layout3_align_setting));
        audio_uart_page_43f0e0(obj, 0);
        audio_uart_page_43f142(obj, y);
    }
}

const void *layout3_ring_battery_dsc_5b9d66(uint8_t level)
{
    if (level == 0u)
        return g2_wf_ring_batt_0;
    if (level < 21u)
        return g2_wf_ring_batt_20;
    if (level < 41u)
        return g2_wf_ring_batt_40;
    if (level < 61u)
        return g2_wf_ring_batt_60;
    if (level < 81u)
        return g2_wf_ring_batt_80;
    return g2_wf_ring_batt_100;
}

const void *layout3_glasses_battery_dsc_5b9db0(uint8_t level)
{
    if (level == 0u)
        return g2_wf_glasses_batt_0;
    if (level < 21u)
        return g2_wf_glasses_batt_20;
    if (level < 41u)
        return g2_wf_glasses_batt_40;
    if (level < 61u)
        return g2_wf_glasses_batt_60;
    if (level < 81u)
        return g2_wf_glasses_batt_80;
    return g2_wf_glasses_batt_100;
}

const void *layout3_hour_image_5b9dfa(int32_t hour)
{
    int32_t h = hour % 12;

    if (h < 0)
        h += 12;
    if (h == 0)
        h = 12;
    switch (h) {
    case 1:
        return g2_wf_hour_1;
    case 2:
        return g2_wf_hour_2;
    case 3:
        return g2_wf_hour_3;
    case 4:
        return g2_wf_hour_4;
    case 5:
        return g2_wf_hour_5;
    case 6:
        return g2_wf_hour_6;
    case 7:
        return g2_wf_hour_7;
    case 8:
        return g2_wf_hour_8;
    case 9:
        return g2_wf_hour_9;
    case 10:
        return g2_wf_hour_10;
    case 11:
        return g2_wf_hour_11;
    default:
        return g2_wf_hour_12;
    }
}

const void *layout3_minute_image_5b9e7e(int32_t minute)
{
    int32_t step;

    if (minute < 0)
        minute = 0;
    if (minute >= 60)
        minute = 59;
    step = minute / 5;
    if (step == 0)
        step = 12;
    switch (step) {
    case 1:
        return g2_wf_minute_1;
    case 2:
        return g2_wf_minute_2;
    case 3:
        return g2_wf_minute_3;
    case 4:
        return g2_wf_minute_4;
    case 5:
        return g2_wf_minute_5;
    case 6:
        return g2_wf_minute_6;
    case 7:
        return g2_wf_minute_7;
    case 8:
        return g2_wf_minute_8;
    case 9:
        return g2_wf_minute_9;
    case 10:
        return g2_wf_minute_10;
    case 11:
        return g2_wf_minute_11;
    default:
        return g2_wf_minute_12;
    }
}

void layout3_format_time_5b9f06(int32_t hour, int32_t minute, char *buf, uint32_t size)
{
    if (buf == NULL || size == 0u)
        return;
    buf[0] = '\0';
    if (audio_time_format_mode_46650c() == 1u) {
        hour %= 12;
        if (hour == 0)
            hour = 12;
    }
    if (minute < 0)
        minute = 0;
    if (minute >= 60)
        minute = 59;
    (void)g2_audio_dump_snprintf(buf, size, s_time_fmt, hour, minute);
}

/* "<weather text> <temperature>" or "-" when the dashboard has no weather text. */
void layout3_format_weather_5b9f58(char *buf, uint32_t size)
{
    uint8_t *const st = g2_dashboard_state;
    const char *text = (const char *)&st[DS_WEATHER_TEXT];
    float temperature;

    if (buf == NULL || size == 0u)
        return;
    buf[0] = '\0';
    if (text[0] == '\0') {
        (void)g2_audio_dump_snprintf(buf, size, s_dash);
        return;
    }
    temperature = *(const float *)(const void *)&st[DS_TEMPERATURE];
    if (svc_universal_setting_get_temperature_unit_466512() == 1u)
        (void)g2_audio_dump_snprintf(buf, size, s_weather_c_fmt, text, (int32_t)temperature);
    else
        (void)g2_audio_dump_snprintf(buf, size, s_weather_f_fmt, text,
                                     (int32_t)((double)temperature * 1.8 + 32.0));
}

/* BLE up: hide the BLE-off icon, show the weather line when enabled and move
 * the date above it. BLE down: show the icon, hide the weather line. */
void layout3_apply_ble_5b9fd6(uint32_t connected)
{
    uint32_t show_weather = (g2_layout3_temperature_enabled != 0u && connected != 0u) ? 1u : 0u;

    if (g2_layout3_ble_off_img != NULL && obj_valid(g2_layout3_ble_off_img) == 1u) {
        if (connected != 0u)
            audio_uart_page_43ded4(g2_layout3_ble_off_img, LV_OBJ_FLAG_HIDDEN);
        else
            audio_uart_page_43dfa4(g2_layout3_ble_off_img, LV_OBJ_FLAG_HIDDEN);
    }
    if (g2_layout3_weather_label != NULL && obj_valid(g2_layout3_weather_label) == 1u) {
        if (show_weather != 0u)
            audio_uart_page_43dfa4(g2_layout3_weather_label, LV_OBJ_FLAG_HIDDEN);
        else
            audio_uart_page_43ded4(g2_layout3_weather_label, LV_OBJ_FLAG_HIDDEN);
    }
    if (g2_layout3_date_label != NULL && obj_valid(g2_layout3_date_label) == 1u)
        layout3_place_5b9d36(g2_layout3_date_label,
                             show_weather != 0u ? L3_Y_DATE_WITH_WEATHER : L3_Y_WEATHER);
}

/* cfg is the layout's watchface block: [0] kind (3), [4] align, [5] date
 * enabled, [6] temperature enabled. */
int32_t layout3_create_5ba07c(void *parent, int32_t x, const uint8_t *cfg)
{
    char time_text[8];
    char date_text[16];
    char weather_text[64];
    g2_calendar_t now;
    void *root, *hands, *obj, *row, *img;
    const void *font;
    uint32_t ble;
    uint8_t level;

    if (parent == NULL) {
        L3_LOG_PREFIX(1u, 348u, m_parent_null);
        L3_LOG_COMPRESSED(0x04000000u, t_parent_null);
        return -1;
    }

    if (cfg != NULL && cfg[0] == 3u) {
        g2_layout3_align_setting = cfg[4];
        g2_layout3_date_enabled = cfg[5];
        g2_layout3_temperature_enabled = cfg[6];
    } else {
        g2_layout3_align_setting = 1u;
        g2_layout3_date_enabled = 1u;
        g2_layout3_temperature_enabled = 1u;
    }
    L3_LOG_PREFIX(3u, 363u, m_create_cfg, g2_layout3_align_setting, g2_layout3_date_enabled,
                  g2_layout3_temperature_enabled);
    L3_LOG_COMPRESSED(0x0cc00000u, t_create_cfg, g2_layout3_align_setting, g2_layout3_date_enabled,
                      g2_layout3_temperature_enabled);

    ble = UX_GetSystemBLEStatus() != 0u ? 1u : 0u;

    root = audio_uart_page_43de82(parent);
    g2_layout3_root = root;
    audio_uart_page_43f4c0(root, 200, 288);
    audio_uart_page_43f09a(root, x, 0);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0, 0u);
    audio_uart_page_44133a(root, 0, 0u);
    audio_uart_page_441378(root, 0, 0u);
    audio_uart_page_441386(root, 0, 0u);
    lv_obj_set_style_pad_all_5b9cec(root, 0, 0u);
    audio_uart_page_44146a(root, 0, 0u);
    audio_uart_page_44140e(root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(root, 0xffu, 0u);
    audio_uart_page_43dfa4(root, LV_OBJ_FLAG_SCROLLABLE);

    service_time_current_calendar_get(&now);

    /* Hour and minute images side by side (x 0 and 32). */
    hands = audio_uart_page_43de82(root);
    g2_layout3_hands = hands;
    audio_uart_page_43f4c0(hands, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(hands, 0u, 0u);
    audio_uart_page_44131c(hands, 0, 0u);
    audio_uart_page_44133a(hands, 0, 0u);
    audio_uart_page_441386(hands, 0, 0u);
    lv_obj_set_style_pad_all_5b9cec(hands, 0, 0u);
    audio_uart_page_44146a(hands, 0, 0u);
    audio_uart_page_43dfa4(hands, LV_OBJ_FLAG_SCROLLABLE);

    img = audio_uart_page_498668(hands);
    g2_layout3_hour_img = img;
    audio_uart_page_43f506(img, 26);
    audio_uart_page_43f568(img, 26);
    audio_uart_page_43f09a(img, 0, 0);
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_498680(img, layout3_hour_image_5b9dfa((int32_t)now.hour));

    img = audio_uart_page_498668(hands);
    g2_layout3_minute_img = img;
    audio_uart_page_43f506(img, 26);
    audio_uart_page_43f568(img, 26);
    audio_uart_page_43f09a(img, 32, 0);
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_498680(img, layout3_minute_image_5b9e7e((int32_t)now.minute));
    layout3_place_5b9d36(hands, 6);

    /* Digital clock. */
    obj = audio_uart_page_499416(root);
    g2_layout3_time_label = obj;
    audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
    audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
    font = g2_translate_lang_pair_font;
    audio_uart_page_44143e(obj, font, 0u);
    (void)aeabi_memset_43c0e4(time_text, sizeof(time_text), 0);
    layout3_format_time_5b9f06((int32_t)now.hour, (int32_t)now.minute, time_text, sizeof(time_text));
    (void)audio_uart_page_49942e(obj, time_text);
    layout3_place_5b9d36(obj, 40);
    g2_dashboard_last_hour_200743bc = now.hour;
    g2_dashboard_last_minute_200743c0 = now.minute;

    img = audio_uart_page_498668(root);
    g2_layout3_ble_off_img = img;
    audio_uart_page_43f506(img, LV_SIZE_CONTENT);
    audio_uart_page_43f568(img, LV_SIZE_CONTENT);
    audio_uart_page_498680(img, g2_layout4_ble_off_icon_769e5c);
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    layout3_place_5b9d36(img, 64);

    if (g2_layout3_date_enabled != 0u) {
        obj = audio_uart_page_499416(root);
        g2_layout3_date_label = obj;
        audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
        audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
        audio_uart_page_44143e(obj, font, 0u);
        (void)aeabi_memset_43c0e4(date_text, sizeof(date_text), 0);
        (void)audio_ble_format_to_buffer(date_text, s_date_fmt,
                                         localized(g2_dashboard_weekday_keys_20004240[now.weekday]),
                                         now.day);
        (void)audio_uart_page_49942e(obj, date_text);
        audio_uart_page_44140e(obj, audio_uart_page_44104c(0x555555u), 0u);
        audio_uart_page_44142e(obj, 0xffu, 0u);
        layout3_place_5b9d36(obj, L3_Y_DATE_WITH_WEATHER);
    }
    g2_dashboard_last_month_200743c4 = now.month;
    g2_dashboard_last_day_200743c8 = now.day;
    g2_dashboard_last_weekday_200743cc = now.weekday;

    if (g2_layout3_temperature_enabled != 0u) {
        obj = audio_uart_page_499416(root);
        g2_layout3_weather_label = obj;
        audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
        audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
        audio_uart_page_44143e(obj, font, 0u);
        (void)aeabi_memset_43c0e4(weather_text, sizeof(weather_text), 0);
        layout3_format_weather_5b9f58(weather_text, sizeof(weather_text));
        (void)audio_uart_page_49942e(obj, weather_text);
        audio_uart_page_44140e(obj, audio_uart_page_44104c(0x555555u), 0u);
        audio_uart_page_44142e(obj, 0xffu, 0u);
        layout3_place_5b9d36(obj, L3_Y_WEATHER);
    }

    /* Battery row. */
    row = audio_uart_page_43de82(root);
    g2_layout3_status_row = row;
    audio_uart_page_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, 0u);
    audio_uart_page_44131c(row, 0, 0u);
    audio_uart_page_44133a(row, 0, 0u);
    audio_uart_page_441386(row, 0, 0u);
    lv_obj_set_style_pad_all_5b9cec(row, 0, 0u);
    audio_uart_page_44146a(row, 0, 0u);
    audio_uart_page_43dfa4(row, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_48ba78(row, LV_FLEX_FLOW_ROW);
    audio_uart_page_48ba92(row, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    audio_uart_page_441254(row, 12, 0u);

    img = audio_uart_page_498668(row);
    g2_layout3_glasses_battery_img = img;
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    level = ui_common_api_fn_00509f8e();
    L3_LOG_PREFIX(4u, 506u, m_battery, (uint32_t)level);
    L3_LOG_COMPRESSED(0x10400000u, t_battery, (uint32_t)level);
    audio_uart_page_498680(img, layout3_glasses_battery_dsc_5b9db0(level));

    if (ux_ring_mac_is_set_47d9c4() != 0u) {
        img = audio_uart_page_498668(row);
        g2_layout3_ring_battery_img = img;
        audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
        if (ux_ring_connected_47d9cc() != 0u)
            audio_uart_page_498680(img, layout3_ring_battery_dsc_5b9d66(
                                            dashboard_ring_battery_level_get_49c5bc()));
        else
            audio_uart_page_498680(img, g2_layout4_ring_off_icon_770a34);
    }
    audio_uart_page_43f66c(root);
    layout3_place_5b9d36(row, L3_ROW_BOTTOM - audio_uart_lv_obj_height_43fdda(row));

    layout3_apply_ble_5b9fd6(ble);

    L3_LOG_PREFIX(3u, 532u, m_created, x, ble);
    L3_LOG_COMPRESSED(0x0c800000u, t_created, x, ble);
    return 0;
}

void layout3_deinit_5ba728(void)
{
    g2_layout3_root = NULL;
    g2_layout3_hands = NULL;
    g2_layout3_hour_img = NULL;
    g2_layout3_minute_img = NULL;
    g2_layout3_time_label = NULL;
    g2_layout3_ble_off_img = NULL;
    g2_layout3_date_label = NULL;
    g2_layout3_weather_label = NULL;
    g2_layout3_status_row = NULL;
    g2_layout3_glasses_battery_img = NULL;
    g2_layout3_ring_battery_img = NULL;
    g2_layout3_align_setting = 0u;
    g2_layout3_date_enabled = 0u;
    g2_layout3_temperature_enabled = 0u;
}

void layout3_set_x_5ba792(int32_t x)
{
    if (g2_layout3_root != NULL)
        audio_uart_page_43f09a(g2_layout3_root, x, 0);
}

void layout3_set_time_5ba7ac(int32_t hour, int32_t minute, uint32_t h24)
{
    char text[8];

    (void)h24;
    if (g2_layout3_time_label != NULL && obj_valid(g2_layout3_time_label) == 1u) {
        (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
        layout3_format_time_5b9f06(hour, minute, text, sizeof(text));
        (void)audio_uart_page_49942e(g2_layout3_time_label, text);
    }
    if (g2_layout3_hour_img != NULL && obj_valid(g2_layout3_hour_img) == 1u)
        audio_uart_page_498680(g2_layout3_hour_img, layout3_hour_image_5b9dfa(hour));
    if (g2_layout3_minute_img != NULL && obj_valid(g2_layout3_minute_img) == 1u)
        audio_uart_page_498680(g2_layout3_minute_img, layout3_minute_image_5b9e7e(minute));
}

void layout3_set_date_5ba83c(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format)
{
    char text[16];

    (void)month;
    (void)date_format;
    if (g2_layout3_date_label == NULL || obj_valid(g2_layout3_date_label) == 0u)
        return;
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    (void)audio_ble_format_to_buffer(text, s_date_fmt,
                                     localized(g2_dashboard_weekday_keys_20004240[weekday]), day);
    (void)audio_uart_page_49942e(g2_layout3_date_label, text);
}

/* Re-reads the dashboard state; the arguments are unused. */
VFP void layout3_set_weather_5ba8a0(uint16_t icon, uint32_t valid, uint32_t unit, float temperature)
{
    char text[64];

    (void)icon;
    (void)valid;
    (void)unit;
    (void)temperature;
    if (g2_layout3_weather_label == NULL || obj_valid(g2_layout3_weather_label) == 0u)
        return;
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    layout3_format_weather_5b9f58(text, sizeof(text));
    (void)audio_uart_page_49942e(g2_layout3_weather_label, text);
}

void layout3_set_battery_5ba8d8(uint8_t level)
{
    if (g2_layout3_glasses_battery_img == NULL || obj_valid(g2_layout3_glasses_battery_img) == 0u)
        return;
    audio_uart_page_498680(g2_layout3_glasses_battery_img, layout3_glasses_battery_dsc_5b9db0(level));
}

void layout3_set_ring_paired_5ba930(uint32_t paired, uint8_t battery)
{
    void *img;

    if (g2_layout3_status_row == NULL || obj_valid(g2_layout3_status_row) == 0u)
        return;
    if (paired != 0u) {
        if (g2_layout3_ring_battery_img != NULL && obj_valid(g2_layout3_ring_battery_img) != 0u)
            return;
        img = audio_uart_page_498668(g2_layout3_status_row);
        g2_layout3_ring_battery_img = img;
        audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
        if (ux_ring_connected_47d9cc() != 0u)
            audio_uart_page_498680(img, layout3_ring_battery_dsc_5b9d66(battery));
        else
            audio_uart_page_498680(img, g2_layout4_ring_off_icon_770a34);
    } else {
        if (g2_layout3_ring_battery_img != NULL && obj_valid(g2_layout3_ring_battery_img) != 0u)
            audio_lv_delete_44d7b8(g2_layout3_ring_battery_img);
        g2_layout3_ring_battery_img = NULL;
    }
    audio_uart_page_43f66c(g2_layout3_root);
    layout3_place_5b9d36(g2_layout3_status_row,
                         L3_ROW_BOTTOM - audio_uart_lv_obj_height_43fdda(g2_layout3_status_row));
}

void layout3_set_ring_connected_5ba9e4(uint32_t connected)
{
    if (g2_layout3_ring_battery_img == NULL || obj_valid(g2_layout3_ring_battery_img) == 0u)
        return;
    if (connected != 0u)
        audio_uart_page_498680(g2_layout3_ring_battery_img,
                               layout3_ring_battery_dsc_5b9d66(dashboard_ring_battery_level_get_49c5bc()));
    else
        audio_uart_page_498680(g2_layout3_ring_battery_img, g2_layout4_ring_off_icon_770a34);
}
