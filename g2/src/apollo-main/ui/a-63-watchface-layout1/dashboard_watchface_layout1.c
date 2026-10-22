/* Dashboard watchface layout1, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout1.c
 * (log tag "dashboard.wf.l1"). Native 0x5b7934..0x5b82e3, 0x5b82e4..0x5b849f,
 * 0x5b8594..0x5b86d1, 0x5b86d2..0x5b8729 (literal pools 0x5b8494..0x5b84a8,
 * 0x5b8564.., 0x5b85c0.., 0x5b8718.., 0x5b87cc..0x5b89e4).
 *
 * Layout1 ops table, ROM 0x713f54 (see dashboard_watchface_manager.c):
 *   +0x00 layout1_create_5b7b60      +0x04 layout1_deinit_5b824c
 *   +0x08 layout1_set_x_5b82cc       +0x0c layout1_update_time_5b82e4
 *   +0x10 layout1_update_date_5b8402 +0x14 layout1_update_weather_5b856c (VFP unit)
 *   +0x18 layout1_set_glasses_battery_5b8594 +0x1c layout1_update_value_5b871c
 *   +0x20 0x5b8880 (outside this unit)        +0x24 layout1_ring_presence_5b85d4
 *   +0x28 layout1_ring_connection_5b8666      +0x2c layout1_ring_battery_5b86a0
 *   +0x30 0x5b87bc (a-64)                     +0x34 0x5b8844
 * Battery icons: six lv_image_dsc_t per device for 0 / 1-20 / 21-40 / 41-60 /
 * 61-80 / 81-100 percent. */
#include <stdint.h>
#include <stddef.h>
#include "dashboard_watchface_layout1.h"

#define LV_SIZE_CONTENT 0x3fffffffu
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_TOP_RIGHT 3u
#define LV_ALIGN_OUT_LEFT_MID 17u
#define LV_ALIGN_OUT_RIGHT_MID 20u

/* am_hal_rtc_time_t word layout as filled by service_time. */
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
_Static_assert(sizeof(g2_calendar_t) == 40u, "am_hal_rtc_time_t");

/* Layout config passed by the watchface manager (layout + 8). */
typedef struct {
    uint8_t valid;       /* +0 1 = fields below are set */
    uint8_t pad[3];
    uint8_t clock_style; /* +4 0 = stacked digits, 1 = "HH:MM" */
    uint8_t left_kind;   /* +5 */
    uint8_t right_kind;  /* +6 */
} g2_wf_layout1_cfg_t;

/* RAM 0x20074434..0x2007445b: layout1 objects. */
extern void *g2_layout1_root;               /* RAM 0x20074434 */
extern void *g2_layout1_hour_label;         /* RAM 0x20074438 */
extern void *g2_layout1_minute_label;       /* RAM 0x2007443c */
extern void *g2_layout1_colon_label;        /* RAM 0x20074440 */
extern void *g2_layout1_date_label;         /* RAM 0x20074444 */
extern void *g2_layout1_status_row;         /* RAM 0x20074448 */
extern void *g2_layout1_glasses_battery_img; /* RAM 0x2007444c */
extern void *g2_layout1_ring_battery_img;   /* RAM 0x20074450 */
extern void *g2_layout1_ble_off_cont;       /* RAM 0x20074454 */
extern void *g2_layout1_ble_off_img;        /* RAM 0x20074458 */
extern uint8_t g2_layout1_clock_style;      /* RAM 0x20074fa6 */
extern const char *g2_dashboard_weekday_keys_20004240[7]; /* RAM 0x20004240, i18n keys by weekday */
extern volatile uint32_t g2_dashboard_last_hour_200743bc;    /* RAM 0x200743bc */
extern volatile uint32_t g2_dashboard_last_minute_200743c0;  /* RAM 0x200743c0 */
extern volatile uint32_t g2_dashboard_last_month_200743c4;   /* RAM 0x200743c4 */
extern volatile uint32_t g2_dashboard_last_day_200743c8;     /* RAM 0x200743c8 */
extern volatile uint32_t g2_dashboard_last_weekday_200743cc; /* RAM 0x200743cc */

/* ROM lv_font_t / lv_image_dsc_t. */
extern const uint8_t g2_translate_lang_pair_font[];    /* ROM 0x7547b8 lv_font_t (date, slots) */
extern const uint8_t g2_onboarding_time_font_754824[]; /* ROM 0x754824 lv_font_t (stacked digits) */
extern const uint8_t g2_font_7547dc[];     /* ROM 0x7547dc lv_font_t ("HH:MM") */
extern const uint8_t g2_wf_glasses_batt_0[];   /* ROM 0x76bae8 */
extern const uint8_t g2_wf_glasses_batt_100[]; /* ROM 0x76bb04 */
extern const uint8_t g2_wf_glasses_batt_20[];  /* ROM 0x76bb20 */
extern const uint8_t g2_wf_glasses_batt_40[];  /* ROM 0x76bb3c */
extern const uint8_t g2_wf_glasses_batt_60[];  /* ROM 0x76bb58 */
extern const uint8_t g2_wf_glasses_batt_80[];  /* ROM 0x76bb74 */
extern const uint8_t g2_wf_ring_batt_0[];      /* ROM 0x7708e4 */
extern const uint8_t g2_wf_ring_batt_100[];    /* ROM 0x770900 */
extern const uint8_t g2_wf_ring_batt_20[];     /* ROM 0x77091c */
extern const uint8_t g2_wf_ring_batt_40[];     /* ROM 0x770938 */
extern const uint8_t g2_wf_ring_batt_60[];     /* ROM 0x770954 */
extern const uint8_t g2_wf_ring_batt_80[];     /* ROM 0x770970 */
extern const uint8_t g2_layout4_ring_off_icon_770a34[];   /* ROM 0x770a34 */
extern const uint8_t g2_layout4_ble_off_icon_769e5c[];             /* ROM 0x769e5c */

extern void service_time_current_calendar_get(g2_calendar_t *out); /* 0x44a19a */
extern uint8_t ui_common_api_fn_00509f8e(void);           /* glasses battery level */
extern uint32_t ux_ring_mac_is_set_47d9c4(void);
extern uint8_t ux_ring_connected_47d9cc(void);
extern uint8_t dashboard_ring_battery_level_get_49c5bc(void);
extern uint8_t UX_GetSystemBLEStatus(void);                /* 0x47d8ce */
extern void layout2_slot_icon_refresh_5b8d20(g2_wf_slot_t *slot);
extern void layout2_slot_text_5b8bc8(uint8_t kind, char *buf, uint32_t size);
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...);              /* sprintf 0x4b4728 */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...);   /* 0x44b728 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* LVGL 9. */
extern void *audio_uart_page_43de82(void *parent);                        /* lv_obj_create */
extern void audio_uart_page_43ded4(void *object, uint32_t flags);         /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);         /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);      /* lv_obj_is_valid */
extern void audio_uart_page_delete_event_filter_44d7b8(void *object);     /* lv_obj_delete */
extern void audio_uart_page_43f09a(void *object, int32_t x, int32_t y);   /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *object, int32_t x);              /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *object, int32_t y);              /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *object, uint32_t w, uint32_t h); /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *object, uint32_t w);             /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *object, uint32_t h);             /* lv_obj_set_height */
extern void audio_uart_page_43f6ac(void *object, uint32_t align);         /* lv_obj_set_align */
extern void audio_uart_page_43f6d6(void *object, void *base, uint32_t align, int32_t x,
                                   int32_t y);                            /* lv_obj_align_to */
extern void audio_uart_page_48ba78(void *object, uint32_t flow);          /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *object, uint32_t main_place, uint32_t cross_place,
                                   uint32_t track_place);                 /* lv_obj_set_flex_align */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                     /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);   /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);   /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);   /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);   /* style pad_right */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);   /* style pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel);  /* style bg_opa */
extern void audio_uart_page_44131c(void *obj, uint32_t v, uint32_t sel);  /* style border_width */
extern void audio_uart_page_44133a(void *obj, uint32_t v, uint32_t sel);  /* style outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);   /* style outline_pad */
extern void audio_uart_page_441386(void *obj, uint32_t v, uint32_t sel);  /* style shadow_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* style text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t v, uint32_t sel);  /* style text_opa */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* style text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);   /* style radius */
extern void *audio_uart_page_498668(void *parent);                        /* lv_image_create */
extern void audio_uart_page_498680(void *object, const void *source);     /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                        /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern uint32_t audio_uart_page_460084(const char *key);                  /* i18n index lookup */
extern const char *audio_uart_page_45fffe(const char *fallback, uint32_t index); /* i18n text */

static const char module[] = "dashboard.wf.l1"; /* ROM 0x785940 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_watchface_layout1.c"; /* ROM 0x6e72e8 */
static const char pick_fn[] = "layout1_pick_g_battery_dsc"; /* ROM 0x76ab28 */
static const char pick_msg[] = "layout1_pick_g_battery_dsc: level=%d"; /* ROM 0x748fac */
static const char pick_c[] = "[dashboard.wf.l1]layout1_pick_g_battery_dsc: level=%d"; /* ROM 0x71da78 */
static const char create_fn[] = "layout1_create"; /* ROM 0x785950 */
static const char no_parent[] = "layout1 create: parent NULL"; /* ROM 0x76ab44 */
static const char no_parent_c[] = "[dashboard.wf.l1]layout1 create: parent NULL"; /* ROM 0x732da4 */
static const char create_cfg[] = "layout1 create: clock=%u left=%d right=%d"; /* ROM 0x73da84 */
static const char create_cfg_c[] = "[dashboard.wf.l1]layout1 create: clock=%u left=%d right=%d"; /* ROM 0x713f18 */
static const char created[] = "layout1 created at x=%d"; /* ROM 0x776694 */
static const char created_c[] = "[dashboard.wf.l1]layout1 created at x=%d"; /* ROM 0x73dab0 */
static const char date_fmt[] = "%s %d";      /* ROM 0x78d314 */
static const char digits_fmt[] = "%1d %1d";  /* ROM 0x78d31c */
static const char two_digit_fmt[] = "%02d";  /* ROM 0x78d324 */
static const char colon[] = ":";             /* ROM 0x5b82c8 */
static const char value_fmt[] = "%d";        /* ROM 0x5b8988 */

/* lv_obj_set_style_pad_all: left, right, top, bottom. */
void layout1_style_pad_all_5b7934(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

const void *layout1_pick_g_battery_dsc_5b7966(uint8_t level)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, pick_fn, 0x9fu, pick_msg, level);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, pick_c, pick_c, level);
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

const void *layout1_pick_ring_battery_dsc_5b7a02(uint8_t level)
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

/* Left slot: icon at the bottom-left, label to its right; right slot: label
 * at the bottom-right, icon to its left. */
void layout1_slot_layout_5b7a4c(g2_wf_slot_t *slot)
{
    if (slot == NULL || slot->icon == NULL || slot->label == NULL)
        return;
    if (slot->side != 0u) {
        audio_uart_page_43f0e0(slot->icon, 0);
        audio_uart_page_43f142(slot->icon, 0x106);
        audio_uart_page_43f6d6(slot->label, slot->icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
    } else {
        audio_uart_page_43f6ac(slot->label, LV_ALIGN_TOP_RIGHT);
        audio_uart_page_43f0e0(slot->label, 0);
        audio_uart_page_43f142(slot->label, 0x109);
        audio_uart_page_43f6d6(slot->icon, slot->label, LV_ALIGN_OUT_LEFT_MID, -8, 0);
    }
}

void layout1_slot_create_5b7aba(g2_wf_slot_t *slot, void *parent, uint8_t kind, uint8_t side)
{
    char text[16];

    if (slot == NULL || parent == NULL)
        return;
    slot->kind = kind;
    slot->side = side;
    slot->icon = NULL;
    slot->label = NULL;
    if (kind == 0u)
        return;
    slot->icon = audio_uart_page_498668(parent);
    audio_uart_page_43f506(slot->icon, 24u);
    audio_uart_page_43f568(slot->icon, 24u);
    audio_uart_page_43ded4(slot->icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(slot->icon, LV_OBJ_FLAG_SCROLLABLE);
    layout2_slot_icon_refresh_5b8d20(slot);
    slot->label = audio_uart_page_499416(parent);
    audio_uart_page_43f506(slot->label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(slot->label, LV_SIZE_CONTENT);
    audio_uart_page_44143e(slot->label, g2_translate_lang_pair_font, 0u);
    aeabi_memset_43c0e4(text, sizeof(text), 0);
    layout2_slot_text_5b8bc8(kind, text, sizeof(text));
    audio_uart_page_49942e(slot->label, text);
    layout1_slot_layout_5b7a4c(slot);
}

static void *icon_create(void *parent)
{
    void *const icon = audio_uart_page_498668(parent);

    audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
    return icon;
}

static void *content_label(void *parent)
{
    void *const label = audio_uart_page_499416(parent);

    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    return label;
}

static void set_hidden(void *obj, int hidden)
{
    if (obj == NULL)
        return;
    if (hidden)
        audio_uart_page_43ded4(obj, LV_OBJ_FLAG_HIDDEN);
    else
        audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_HIDDEN);
}

/* ops +0x00: build layout1 at x inside parent. 0 ok, -1 without parent. */
int32_t layout1_create_5b7b60(void *parent, int32_t x, const g2_wf_layout1_cfg_t *cfg)
{
    uint8_t left, right;
    g2_calendar_t now;
    char date[32], hour[10], minute[10];

    if (parent == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, create_fn, 0xfdu, no_parent);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, no_parent_c, no_parent_c);
        return -1;
    }
    if (cfg != NULL && cfg->valid == 1u) {
        g2_layout1_clock_style = cfg->clock_style;
        left = cfg->left_kind;
        right = cfg->right_kind;
    } else {
        g2_layout1_clock_style = 0u;
        left = 1u;
        right = 4u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, create_fn, 0x10fu, create_cfg, g2_layout1_clock_style, left, right);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0cc00000u, create_cfg_c, create_cfg_c, g2_layout1_clock_style, left, right);

    g2_layout1_root = audio_uart_page_43de82(parent);
    void *const root = g2_layout1_root;
    audio_uart_page_43f4c0(root, 200u, 0x120u);
    audio_uart_page_43f09a(root, x, 0);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44133a(root, 0u, 0u);
    audio_uart_page_441378(root, 0, 0u);
    audio_uart_page_441386(root, 0u, 0u);
    layout1_style_pad_all_5b7934(root, 0, 0u);
    audio_uart_page_44146a(root, 0, 0u);
    audio_uart_page_44140e(root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(root, 0xffu, 0u);
    audio_uart_page_43dfa4(root, LV_OBJ_FLAG_SCROLLABLE);

    /* Date line "<weekday> <day>". */
    service_time_current_calendar_get(&now);
    g2_layout1_date_label = content_label(root);
    audio_uart_page_43f0e0(g2_layout1_date_label, 0);
    audio_uart_page_43f142(g2_layout1_date_label, 1);
    aeabi_memset_43c0e4(date, sizeof(date), 0);
    audio_ble_format_to_buffer(date, date_fmt,
                               audio_uart_page_45fffe(g2_dashboard_weekday_keys_20004240[now.weekday],
                                                      audio_uart_page_460084(g2_dashboard_weekday_keys_20004240[now.weekday])),
                               now.day);
    audio_uart_page_49942e(g2_layout1_date_label, date);
    g2_dashboard_last_month_200743c4 = now.month;
    g2_dashboard_last_day_200743c8 = now.day;
    g2_dashboard_last_weekday_200743cc = now.weekday;
    audio_uart_page_44143e(g2_layout1_date_label, g2_translate_lang_pair_font, 0u);

    /* Top-right status row: glasses battery, then ring battery when paired. */
    g2_layout1_status_row = audio_uart_page_43de82(root);
    void *const row = g2_layout1_status_row;
    audio_uart_page_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, 0u);
    audio_uart_page_44131c(row, 0u, 0u);
    audio_uart_page_44133a(row, 0u, 0u);
    audio_uart_page_441386(row, 0u, 0u);
    layout1_style_pad_all_5b7934(row, 0, 0u);
    audio_uart_page_44146a(row, 0, 0u);
    audio_uart_page_43dfa4(row, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f6ac(row, LV_ALIGN_TOP_RIGHT);
    audio_uart_page_43f0e0(row, 0);
    audio_uart_page_43f142(row, 5);
    audio_uart_page_48ba78(row, 0u);
    audio_uart_page_48ba92(row, 0u, 2u, 2u);
    audio_uart_page_441254(row, 12, 0u);
    g2_layout1_glasses_battery_img = icon_create(row);
    audio_uart_page_498680(g2_layout1_glasses_battery_img,
                           layout1_pick_g_battery_dsc_5b7966(ui_common_api_fn_00509f8e()));
    if (ux_ring_mac_is_set_47d9c4() != 0u) {
        g2_layout1_ring_battery_img = icon_create(row);
        if (ux_ring_connected_47d9cc() == 0u)
            audio_uart_page_498680(g2_layout1_ring_battery_img, g2_layout4_ring_off_icon_770a34);
        else
            audio_uart_page_498680(g2_layout1_ring_battery_img,
                                   layout1_pick_ring_battery_dsc_5b7a02(dashboard_ring_battery_level_get_49c5bc()));
    }

    /* Clock. */
    g2_layout1_hour_label = content_label(root);
    g2_layout1_minute_label = content_label(root);
    aeabi_memset_43c0e4(hour, sizeof(hour), 0);
    aeabi_memset_43c0e4(minute, sizeof(minute), 0);
    if (g2_layout1_clock_style == 0u) {
        audio_uart_page_43f0e0(g2_layout1_hour_label, 0x2a);
        audio_uart_page_43f142(g2_layout1_hour_label, 0x46);
        audio_ble_format_to_buffer(hour, digits_fmt, now.hour / 10u, now.hour % 10u);
        audio_uart_page_49942e(g2_layout1_hour_label, hour);
        audio_uart_page_44143e(g2_layout1_hour_label, g2_onboarding_time_font_754824, 0u);
        audio_uart_page_43f0e0(g2_layout1_minute_label, 0x2a);
        audio_uart_page_43f142(g2_layout1_minute_label, 0x9c);
        audio_ble_format_to_buffer(minute, digits_fmt, now.minute / 10u, now.minute % 10u);
        audio_uart_page_49942e(g2_layout1_minute_label, minute);
        audio_uart_page_44143e(g2_layout1_minute_label, g2_onboarding_time_font_754824, 0u);
    } else {
        audio_uart_page_43f0e0(g2_layout1_hour_label, 0x2c);
        audio_uart_page_43f142(g2_layout1_hour_label, 0x74);
        audio_ble_format_to_buffer(hour, two_digit_fmt, now.hour);
        audio_uart_page_49942e(g2_layout1_hour_label, hour);
        audio_uart_page_44143e(g2_layout1_hour_label, g2_font_7547dc, 0u);
        g2_layout1_colon_label = content_label(root);
        audio_uart_page_49942e(g2_layout1_colon_label, colon);
        audio_uart_page_44143e(g2_layout1_colon_label, g2_font_7547dc, 0u);
        audio_uart_page_43f6d6(g2_layout1_colon_label, g2_layout1_hour_label, LV_ALIGN_OUT_RIGHT_MID, 6, 0);
        audio_ble_format_to_buffer(minute, two_digit_fmt, now.minute);
        audio_uart_page_49942e(g2_layout1_minute_label, minute);
        audio_uart_page_44143e(g2_layout1_minute_label, g2_font_7547dc, 0u);
        audio_uart_page_43f6d6(g2_layout1_minute_label, g2_layout1_colon_label, LV_ALIGN_OUT_RIGHT_MID, 6, 0);
    }
    g2_dashboard_last_hour_200743bc = now.hour;
    g2_dashboard_last_minute_200743c0 = now.minute;

    /* Complication slots and the "phone disconnected" badge in their place. */
    layout1_slot_create_5b7aba(&g2_layout1_slot_a, root, left, 1u);
    layout1_slot_create_5b7aba(&g2_layout1_slot_b, root, right, 0u);
    g2_layout1_ble_off_cont = audio_uart_page_43de82(root);
    void *const badge = g2_layout1_ble_off_cont;
    audio_uart_page_43f506(badge, 0x82u);
    audio_uart_page_43f568(badge, 0x18u);
    audio_uart_page_43f0e0(badge, 0);
    audio_uart_page_43f142(badge, 0x106);
    audio_uart_page_44127e(badge, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(badge, 0xffu, 0u);
    audio_uart_page_44131c(badge, 0u, 0u);
    layout1_style_pad_all_5b7934(badge, 0, 0u);
    audio_uart_page_43dfa4(badge, LV_OBJ_FLAG_SCROLLABLE);
    g2_layout1_ble_off_img = audio_uart_page_498668(badge);
    audio_uart_page_43f506(g2_layout1_ble_off_img, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_layout1_ble_off_img, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(g2_layout1_ble_off_img, 0);
    audio_uart_page_43f142(g2_layout1_ble_off_img, 0);
    audio_uart_page_498680(g2_layout1_ble_off_img, g2_layout4_ble_off_icon_769e5c);
    audio_uart_page_43ded4(g2_layout1_ble_off_img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(g2_layout1_ble_off_img, LV_OBJ_FLAG_SCROLLABLE);

    if (UX_GetSystemBLEStatus() == 0u) {
        set_hidden(g2_layout1_slot_a.icon, 1);
        set_hidden(g2_layout1_slot_a.label, 1);
        audio_uart_page_43dfa4(badge, LV_OBJ_FLAG_HIDDEN);
        set_hidden(g2_layout1_slot_b.icon, 1);
        set_hidden(g2_layout1_slot_b.label, 1);
    } else {
        audio_uart_page_43ded4(badge, LV_OBJ_FLAG_HIDDEN);
        set_hidden(g2_layout1_slot_a.icon, 0);
        set_hidden(g2_layout1_slot_a.label, 0);
        set_hidden(g2_layout1_slot_b.icon, 0);
        set_hidden(g2_layout1_slot_b.label, 0);
    }

    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, create_fn, 0x1cdu, created, x);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, created_c, created_c, x);
    return 0;
}

/* ops +0x04: forget the objects (the manager deletes the parent). */
void layout1_deinit_5b824c(void)
{
    g2_layout1_root = NULL;
    g2_layout1_hour_label = NULL;
    g2_layout1_minute_label = NULL;
    g2_layout1_colon_label = NULL;
    g2_layout1_date_label = NULL;
    g2_layout1_status_row = NULL;
    g2_layout1_glasses_battery_img = NULL;
    g2_layout1_ring_battery_img = NULL;
    g2_layout1_ble_off_cont = NULL;
    g2_layout1_ble_off_img = NULL;
    g2_layout1_slot_a.icon = NULL;
    g2_layout1_slot_a.label = NULL;
    g2_layout1_slot_a.kind = 0u;
    g2_layout1_slot_b.icon = NULL;
    g2_layout1_slot_b.label = NULL;
    g2_layout1_slot_b.kind = 0u;
    g2_layout1_clock_style = 0u;
}

/* ops +0x08 */
void layout1_set_x_5b82cc(int32_t x)
{
    if (g2_layout1_root != NULL)
        audio_uart_page_43f09a(g2_layout1_root, x, 0);
}

static int valid(void *obj)
{
    return obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) == 1u;
}

/* ops +0x0c */
void layout1_update_time_5b82e4(int32_t hour, int32_t minute, uint32_t h24)
{
    char h[10], m[10];
    (void)h24;

    aeabi_memset_43c0e4(h, sizeof(h), 0);
    aeabi_memset_43c0e4(m, sizeof(m), 0);
    if (g2_layout1_clock_style == 0u) {
        audio_ble_format_to_buffer(h, digits_fmt, hour / 10, hour % 10);
        audio_ble_format_to_buffer(m, digits_fmt, minute / 10, minute % 10);
    } else {
        audio_ble_format_to_buffer(h, two_digit_fmt, hour);
        audio_ble_format_to_buffer(m, two_digit_fmt, minute);
    }
    if (valid(g2_layout1_hour_label))
        audio_uart_page_49942e(g2_layout1_hour_label, h);
    if (valid(g2_layout1_minute_label))
        audio_uart_page_49942e(g2_layout1_minute_label, m);
    if (g2_layout1_clock_style == 1u) {
        if (valid(g2_layout1_colon_label) && valid(g2_layout1_hour_label))
            audio_uart_page_43f6d6(g2_layout1_colon_label, g2_layout1_hour_label, LV_ALIGN_OUT_RIGHT_MID, 6, 0);
        if (valid(g2_layout1_minute_label) && valid(g2_layout1_colon_label))
            audio_uart_page_43f6d6(g2_layout1_minute_label, g2_layout1_colon_label, LV_ALIGN_OUT_RIGHT_MID, 6, 0);
    }
}

/* ops +0x10 */
void layout1_update_date_5b8402(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format)
{
    char text[32];
    (void)month;
    (void)date_format;

    if (g2_layout1_date_label == NULL || audio_terminal_ui_object_valid_43e2ea(g2_layout1_date_label) == 0u)
        return;
    aeabi_memset_43c0e4(text, sizeof(text), 0);
    audio_ble_format_to_buffer(text, date_fmt,
                               audio_uart_page_45fffe(g2_dashboard_weekday_keys_20004240[weekday],
                                                      audio_uart_page_460084(g2_dashboard_weekday_keys_20004240[weekday])),
                               day);
    audio_uart_page_49942e(g2_layout1_date_label, text);
}

/* Apply fn(slot, arg) to every slot showing complication `kind`. */
void layout1_slots_for_kind_5b845c(uint8_t kind, g2_wf_slot_fn_t fn, const void *arg)
{
    if (g2_layout1_slot_a.kind == kind && fn != NULL)
        fn(&g2_layout1_slot_a, arg);
    if (g2_layout1_slot_b.kind == kind && fn != NULL)
        fn(&g2_layout1_slot_b, arg);
}

/* ops +0x18 */
void layout1_set_glasses_battery_5b8594(uint8_t level)
{
    if (g2_layout1_glasses_battery_img != NULL &&
        audio_terminal_ui_object_valid_43e2ea(g2_layout1_glasses_battery_img) != 0u)
        audio_uart_page_498680(g2_layout1_glasses_battery_img, layout1_pick_g_battery_dsc_5b7966(level));
}

/* ops +0x24: ring paired / unpaired; creates or deletes the ring icon. */
void layout1_ring_presence_5b85d4(uint32_t paired, uint8_t level)
{
    if (g2_layout1_status_row == NULL || audio_terminal_ui_object_valid_43e2ea(g2_layout1_status_row) == 0u)
        return;
    if (paired == 0u) {
        if (g2_layout1_ring_battery_img != NULL &&
            audio_terminal_ui_object_valid_43e2ea(g2_layout1_ring_battery_img) != 0u)
            audio_uart_page_delete_event_filter_44d7b8(g2_layout1_ring_battery_img);
        g2_layout1_ring_battery_img = NULL;
        return;
    }
    if (g2_layout1_ring_battery_img != NULL &&
        audio_terminal_ui_object_valid_43e2ea(g2_layout1_ring_battery_img) != 0u)
        return;
    g2_layout1_ring_battery_img = icon_create(g2_layout1_status_row);
    if (ux_ring_connected_47d9cc() == 0u)
        audio_uart_page_498680(g2_layout1_ring_battery_img, g2_layout4_ring_off_icon_770a34);
    else
        audio_uart_page_498680(g2_layout1_ring_battery_img, layout1_pick_ring_battery_dsc_5b7a02(level));
}

/* ops +0x28 */
void layout1_ring_connection_5b8666(uint32_t connected)
{
    if (g2_layout1_ring_battery_img == NULL ||
        audio_terminal_ui_object_valid_43e2ea(g2_layout1_ring_battery_img) == 0u)
        return;
    if (connected == 0u)
        audio_uart_page_498680(g2_layout1_ring_battery_img, g2_layout4_ring_off_icon_770a34);
    else
        audio_uart_page_498680(g2_layout1_ring_battery_img,
                               layout1_pick_ring_battery_dsc_5b7a02(dashboard_ring_battery_level_get_49c5bc()));
}

/* ops +0x2c */
void layout1_ring_battery_5b86a0(uint8_t level)
{
    if (g2_layout1_ring_battery_img != NULL &&
        audio_terminal_ui_object_valid_43e2ea(g2_layout1_ring_battery_img) != 0u &&
        ux_ring_connected_47d9cc() != 0u)
        audio_uart_page_498680(g2_layout1_ring_battery_img, layout1_pick_ring_battery_dsc_5b7a02(level));
}

/* Slot refresh for complication kind 4: plain integer value. */
void layout1_slot_value_refresh_5b86d2(g2_wf_slot_t *slot, const void *arg)
{
    char text[16];

    if (slot == NULL || slot->label == NULL || audio_terminal_ui_object_valid_43e2ea(slot->label) == 0u)
        return;
    const uint32_t value = *(const uint32_t *)arg;
    aeabi_memset_43c0e4(text, sizeof(text), 0);
    g2_audio_dump_snprintf(text, sizeof(text), value_fmt, value);
    audio_uart_page_49942e(slot->label, text);
    layout1_slot_layout_5b7a4c(slot);
}

/* ops +0x1c */
void layout1_update_value_5b871c(uint32_t value)
{
    layout1_slots_for_kind_5b845c(4u, layout1_slot_value_refresh_5b86d2, &value);
}
