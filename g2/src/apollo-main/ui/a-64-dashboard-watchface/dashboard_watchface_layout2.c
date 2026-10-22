/* Dashboard watchface layout2 (digital clock, date, glasses/ring battery row
 * and up to three complication slots), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout2.c
 * (log tag "dashboard.wf.l2"). Native 0x5b8dd0..0x5b9c59; literal pools
 * 0x5b99c4, 0x5b9a30, 0x5b9a48..0x5b9a67, 0x5b9afc, 0x5b9b9c, 0x5b9bbc,
 * 0x5b9c40..0x5b9c4b, 0x5b9c5c..0x5b9ceb.
 * 0x5b8e1a (layout2_place_5b8e1a) and 0x5b8f18 (layout2_slot_create_5b8f18)
 * are in ui/u-09/watchface_layout_slots.c.
 *
 * The functions from 0x5b90e8 on fill the layout2 ops table (ROM 0x713fcc):
 * +0x00 create, +0x04 deinit, +0x08 set_x, +0x0c time, +0x10 date,
 * +0x14 weather, +0x18 glasses battery, +0x1c unread count, +0x20 BLE state,
 * +0x24 ring paired, +0x28 ring connected, +0x2c ring battery, +0x30 health
 * refresh, +0x34/+0x38 kind-2/kind-3 slot refresh.
 *
 * +0x14 takes the temperature in s0 (hard-float ABI): profile g2-apollo-main-3. */
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
#define LV_ALIGN_OUT_RIGHT_MID  20u
#define LV_FLEX_FLOW_ROW        0u
#define LV_FLEX_ALIGN_START     0u
#define LV_FLEX_ALIGN_CENTER    2u

/* One 12-byte record per complication slot (same as ui/u-09). */
typedef struct {
    void *icon;     /* +0x0 lv_image */
    void *label;    /* +0x4 lv_label */
    uint8_t kind;   /* +0x8 complication kind (0 = none) */
    uint8_t active; /* +0x9 */
    uint8_t pad[2];
} g2_layout2_slot_t;
_Static_assert(sizeof(g2_layout2_slot_t) == 12, "layout2 slot record");

typedef void (*g2_layout2_slot_cb_t)(g2_layout2_slot_t *slot, const void *arg);

/* Argument record built on the stack by layout2_set_weather_5b9860. */
typedef struct {
    uint16_t icon;      /* +0x0 weather icon code */
    uint8_t pad[2];
    float temperature;  /* +0x4 */
    uint32_t valid;     /* +0x8 */
    uint32_t unit;      /* +0xc */
} g2_layout2_weather_arg_t;
_Static_assert(sizeof(g2_layout2_weather_arg_t) == 16, "weather arg record");

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

typedef struct {
    uint8_t type;      /* +0x00 */
    uint8_t pad1[3];
    uint32_t goal;     /* +0x04 */
    float value;       /* +0x08 */
    float avg_value;   /* +0x0c */
    uint32_t duration; /* +0x10 */
    uint8_t trend;     /* +0x14 */
    uint8_t pad15[3];
} g2_wf_health_metric_t;
_Static_assert(sizeof(g2_wf_health_metric_t) == 0x18u, "health metric record");

typedef struct {
    uint32_t head;                    /* +0x00 */
    g2_wf_health_metric_t metric[8];  /* +0x04 */
} g2_wf_health_data_t;

/* Layout2 state. */
extern g2_layout2_slot_t g2_layout2_slots[3];          /* RAM 0x200005e8 */
extern void *g2_layout2_slot_conts[3];                 /* RAM 0x20073fb4 */
extern void *g2_layout2_parent;                        /* RAM 0x2007445c root container */
extern void *g2_layout2_time_label;                    /* RAM 0x20074460 */
extern void *g2_layout2_date_label;                    /* RAM 0x20074464 */
extern void *g2_layout2_status_row;                    /* RAM 0x20074468 */
extern void *g2_layout2_glasses_battery_img;           /* RAM 0x2007446c */
extern void *g2_layout2_ring_battery_img;              /* RAM 0x20074470 */
extern void *g2_layout2_ble_off_img;                   /* RAM 0x20074474 */
extern uint8_t g2_layout2_clock_style;                 /* RAM 0x20074fa7 cfg[5] */
extern uint8_t g2_layout2_date_enabled;                /* RAM 0x20074fa8 cfg[6] */
extern uint8_t g2_layout2_align_setting;               /* RAM 0x20074fa9 cfg[4] */
extern uint8_t g2_layout2_slot_count;                  /* RAM 0x20074faa cfg[7] */

/* Shared dashboard state. */
extern g2_wf_health_data_t g2_health_data;             /* RAM 0x200f41b4 */
extern volatile uint32_t g2_dashboard_last_hour_200743bc;    /* RAM 0x200743bc */
extern volatile uint32_t g2_dashboard_last_minute_200743c0;  /* RAM 0x200743c0 */
extern volatile uint32_t g2_dashboard_last_month_200743c4;   /* RAM 0x200743c4 */
extern volatile uint32_t g2_dashboard_last_day_200743c8;     /* RAM 0x200743c8 */
extern volatile uint32_t g2_dashboard_last_weekday_200743cc; /* RAM 0x200743cc */
extern const char *g2_dashboard_weekday_keys_20004240[7];    /* RAM .data 0x20004240 i18n keys */
extern const void *audio_uart_ring_primary_head_cell;        /* RAM 0x200746dc: active lv_font_t * */

/* ROM assets. */
extern const uint8_t g2_font_754794[];          /* ROM 0x754794 lv_font_t, default clock */
extern const uint8_t g2_font_7547dc[];          /* ROM 0x7547dc lv_font_t, clock style 1 */
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

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* libc-like, i18n, services. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern uint32_t audio_uart_page_460084(const char *key);                       /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);    /* localized text */
extern void service_time_current_calendar_get(g2_calendar_t *out);             /* 0x44a19a */
extern uint32_t UX_GetSystemBLEStatus(void);                                   /* 0x47d8ce */
extern uint32_t ux_ring_mac_is_set_47d9c4(void);
extern uint8_t ux_ring_connected_47d9cc(void);
extern uint8_t dashboard_ring_battery_level_get_49c5bc(void);
extern uint8_t ui_common_api_fn_00509f8e(void);                                /* glasses battery percent */
extern uint32_t health_lock_storage(void);                                     /* 0x4ffc32 */
extern void health_unlock_storage(void);                                       /* 0x4ffc90 */

/* LVGL 9.3 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                            /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                 /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                 /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);          /* lv_obj_is_valid */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);          /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);          /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                     /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                     /* lv_obj_set_height */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                                /* lv_obj_align_to */
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

/* Same-module helpers (ui/u-09 and the complication TU at 0x5b89f0). */
extern void layout2_place_5b8e1a(void *obj, int32_t y);
extern void layout2_slot_create_5b8f18(uint32_t slot, uint8_t kind);
extern void layout2_slot_icon_refresh_5b8d20(g2_layout2_slot_t *slot);
extern void layout2_slot_text_5b8bc8(uint8_t kind, char *buf, uint32_t size);
extern int32_t watchface_health_metric_index_5b8a6a(uint8_t kind);
extern VFP void watchface_health_value_format_5b8a9c(float value, uint8_t kind, uint32_t duration,
                                                     char *buf, uint32_t size);

static const char tag[] = "dashboard.wf.l2";                                         /* ROM 0x785970 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_watchface_layout2.c"; /* ROM 0x6e733c */
static const char fn_create[] = "layout2_create";                                    /* ROM 0x785960 */
static const char m_parent_null[] = "layout2 create: parent NULL";                   /* ROM 0x76ab60 */
static const char t_parent_null[] = "[dashboard.wf.l2]layout2 create: parent NULL";  /* ROM 0x732dd4 */
static const char m_create_cfg[] =
    "layout2 create: align=%u clock=%u date_en=%u list_count=%u";                    /* ROM 0x713f90 */
static const char t_create_cfg[] =
    "[dashboard.wf.l2]layout2 create: align=%u clock=%u date_en=%u list_count=%u";   /* ROM 0x6f2dac */
static const char m_battery[] = "layout2_set_battery: lvl=%d";                       /* ROM 0x76ab7c */
static const char t_battery[] = "[dashboard.wf.l2]layout2_set_battery: lvl=%d";      /* ROM 0x732e04 */
static const char m_created[] = "layout2 created at x=%d";                           /* ROM 0x7766ac */
static const char t_created[] = "[dashboard.wf.l2]layout2 created at x=%d";          /* ROM 0x73dadc */
static const char s_time_fmt[] = "%02d:%02d";                                        /* ROM 0x78a778 */
static const char s_date_fmt[] = "%s %d";                                            /* ROM 0x78d33c */
static const char s_int_fmt[] = "%d";                                                /* ROM 0x5b9c5c */

#define L2_LOG_PREFIX(lvl, line, msg, ...)                                                 \
    do {                                                                                   \
        if (audio_log_flags() & 2u)                                                        \
            audio_log_extended((lvl), tag, src, fn_create, (line), (msg), ##__VA_ARGS__);  \
    } while (0)
#define L2_LOG_COMPRESSED(code, text, ...)                                                 \
    do {                                                                                   \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                          \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__);              \
    } while (0)

void lv_obj_set_style_pad_all_5b8dd0(uint32_t obj, uint32_t value, uint32_t selector);
uint8_t layout2_align_from_setting_5b8e02(uint8_t setting);
int32_t layout2_slot_y_5b8e4a(int32_t row);
int32_t layout2_slot_row_5b8e5e(uint32_t slot, int32_t count);
const void *layout2_clock_font_5b8e72(uint8_t style);
const void *layout2_glasses_battery_dsc_5b8e84(uint8_t level);
const void *layout2_ring_battery_dsc_5b8ece(uint8_t level);
void layout2_slots_foreach_kind_5b90ae(uint8_t kind, g2_layout2_slot_cb_t cb, const void *arg);
int32_t layout2_create_5b90e8(void *parent, int32_t x, const uint8_t *cfg);
void layout2_deinit_5b96b4(void);
void layout2_set_x_5b9748(int32_t x);
void layout2_set_time_5b9760(uint32_t hour, uint32_t minute, uint32_t h24);
void layout2_set_date_5b97a0(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format);
void layout2_slot_refresh_cb_5b97fa(g2_layout2_slot_t *slot, const void *arg);
VFP void layout2_set_weather_5b9860(uint16_t icon, uint32_t valid, uint32_t unit, float temperature);
void layout2_set_battery_5b987e(uint8_t level);
void layout2_set_ring_paired_5b98aa(uint32_t paired, uint8_t battery);
void layout2_set_ring_connected_5b9954(uint32_t connected);
void layout2_set_ring_battery_5b9990(uint8_t level);
void layout2_slot_count_cb_5b99cc(g2_layout2_slot_t *slot, const void *arg);
void layout2_set_unread_count_5b9a38(uint32_t count);
void layout2_set_ble_connected_5b9a68(uint32_t connected);
void layout2_slot_health_refresh_5b9b04(g2_layout2_slot_t *slot);
void layout2_refresh_health_5b9ba0(void);
void layout2_slot_text_refresh_cb_5b9bc0(g2_layout2_slot_t *slot, const void *arg);
void layout2_refresh_kind2_5b9c32(void);
void layout2_refresh_kind3_5b9c4c(void);

static uint32_t obj_valid(void *obj)
{
    return audio_terminal_ui_object_valid_43e2ea(obj);
}

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

void lv_obj_set_style_pad_all_5b8dd0(uint32_t obj, uint32_t value, uint32_t selector)
{
    void *o = (void *)(uintptr_t)obj;

    audio_uart_page_44122a(o, (int32_t)value, selector);
    audio_uart_page_441238(o, (int32_t)value, selector);
    audio_uart_page_44120e(o, (int32_t)value, selector);
    audio_uart_page_44121c(o, (int32_t)value, selector);
}

/* Alignment setting -> lv_align_t: 1 top-mid, 2 top-right, else top-left. */
uint8_t layout2_align_from_setting_5b8e02(uint8_t setting)
{
    if (setting == 1u)
        return LV_ALIGN_TOP_MID;
    if (setting == 2u)
        return LV_ALIGN_TOP_RIGHT;
    return LV_ALIGN_TOP_LEFT;
}

int32_t layout2_slot_y_5b8e4a(int32_t row)
{
    if (row < 0)
        row = 0;
    if (row >= 3)
        row = 2;
    return row * 28 + 206;
}

/* Slots are bottom-aligned: with fewer than three, the first starts lower. */
int32_t layout2_slot_row_5b8e5e(uint32_t slot, int32_t count)
{
    if (count < 1)
        count = 1;
    if (count >= 4)
        count = 3;
    return (int32_t)slot + (3 - count);
}

const void *layout2_clock_font_5b8e72(uint8_t style)
{
    if (style == 1u)
        return g2_font_7547dc;
    return g2_font_754794;
}

const void *layout2_glasses_battery_dsc_5b8e84(uint8_t level)
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

const void *layout2_ring_battery_dsc_5b8ece(uint8_t level)
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

void layout2_slots_foreach_kind_5b90ae(uint8_t kind, g2_layout2_slot_cb_t cb, const void *arg)
{
    int32_t i;

    if (cb == NULL)
        return;
    for (i = 0; i < 3; i++) {
        if (g2_layout2_slots[i].kind == kind)
            cb(&g2_layout2_slots[i], arg);
    }
}

/* cfg is the layout's watchface block: [0] kind (2), [4] align, [5] clock
 * style, [6] date enabled, [7] slot count (max 3), [8..10] slot kinds. */
int32_t layout2_create_5b90e8(void *parent, int32_t x, const uint8_t *cfg)
{
    char time_text[8];
    char date_text[16];
    uint8_t kinds[3];
    g2_calendar_t now;
    void *root, *obj, *row, *img;
    uint8_t level;
    int32_t i;

    if (parent == NULL) {
        L2_LOG_PREFIX(1u, 313u, m_parent_null);
        L2_LOG_COMPRESSED(0x04000000u, t_parent_null);
        return -1;
    }

    (void)aeabi_memset_43c0e4(kinds, sizeof(kinds), 0);
    if (cfg != NULL && cfg[0] == 2u) {
        g2_layout2_clock_style = cfg[5];
        g2_layout2_date_enabled = cfg[6];
        g2_layout2_align_setting = cfg[4];
        g2_layout2_slot_count = cfg[7];
        if (g2_layout2_slot_count >= 4u)
            g2_layout2_slot_count = 3u;
        for (i = 0; i < (int32_t)g2_layout2_slot_count; i++)
            kinds[i] = cfg[8 + i];
    } else {
        g2_layout2_clock_style = 0u;
        g2_layout2_date_enabled = 1u;
        g2_layout2_align_setting = 1u;
        g2_layout2_slot_count = 0u;
    }
    L2_LOG_PREFIX(3u, 340u, m_create_cfg, g2_layout2_align_setting, g2_layout2_clock_style,
                  g2_layout2_date_enabled, g2_layout2_slot_count);
    L2_LOG_COMPRESSED(0x0d000000u, t_create_cfg, g2_layout2_align_setting, g2_layout2_clock_style,
                      g2_layout2_date_enabled, g2_layout2_slot_count);

    root = audio_uart_page_43de82(parent);
    g2_layout2_parent = root;
    audio_uart_page_43f4c0(root, 200, 288);
    audio_uart_page_43f09a(root, x, 0);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0, 0u);
    audio_uart_page_44133a(root, 0, 0u);
    audio_uart_page_441378(root, 0, 0u);
    audio_uart_page_441386(root, 0, 0u);
    lv_obj_set_style_pad_all_5b8dd0((uint32_t)(uintptr_t)root, 0u, 0u);
    audio_uart_page_44146a(root, 0, 0u);
    audio_uart_page_44140e(root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(root, 0xffu, 0u);
    audio_uart_page_43dfa4(root, LV_OBJ_FLAG_SCROLLABLE);

    service_time_current_calendar_get(&now);

    /* Clock label. */
    obj = audio_uart_page_499416(root);
    g2_layout2_time_label = obj;
    audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
    audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
    audio_uart_page_44143e(obj, layout2_clock_font_5b8e72(g2_layout2_clock_style), 0u);
    (void)aeabi_memset_43c0e4(time_text, sizeof(time_text), 0);
    (void)audio_ble_format_to_buffer(time_text, s_time_fmt, now.hour, now.minute);
    (void)audio_uart_page_49942e(obj, time_text);
    layout2_place_5b8e1a(obj, 6);
    g2_dashboard_last_hour_200743bc = now.hour;
    g2_dashboard_last_minute_200743c0 = now.minute;

    /* Optional date label: "<weekday> <day>". */
    if (g2_layout2_date_enabled != 0u) {
        obj = audio_uart_page_499416(root);
        g2_layout2_date_label = obj;
        audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
        audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
        audio_uart_page_44143e(obj, audio_uart_ring_primary_head_cell, 0u);
        (void)aeabi_memset_43c0e4(date_text, sizeof(date_text), 0);
        (void)audio_ble_format_to_buffer(date_text, s_date_fmt,
                                         localized(g2_dashboard_weekday_keys_20004240[now.weekday]),
                                         now.day);
        (void)audio_uart_page_49942e(obj, date_text);
        layout2_place_5b8e1a(obj, 42);
    }
    g2_dashboard_last_month_200743c4 = now.month;
    g2_dashboard_last_day_200743c8 = now.day;
    g2_dashboard_last_weekday_200743cc = now.weekday;

    /* Battery row: glasses battery, then the ring battery when a ring is paired. */
    row = audio_uart_page_43de82(root);
    g2_layout2_status_row = row;
    audio_uart_page_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, 0u);
    audio_uart_page_44131c(row, 0, 0u);
    audio_uart_page_44133a(row, 0, 0u);
    audio_uart_page_441386(row, 0, 0u);
    lv_obj_set_style_pad_all_5b8dd0((uint32_t)(uintptr_t)row, 0u, 0u);
    audio_uart_page_44146a(row, 0, 0u);
    audio_uart_page_44140e(row, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(row, 0xffu, 0u);
    audio_uart_page_43dfa4(row, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_48ba78(row, LV_FLEX_FLOW_ROW);
    audio_uart_page_48ba92(row, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    audio_uart_page_441254(row, 12, 0u);

    img = audio_uart_page_498668(row);
    g2_layout2_glasses_battery_img = img;
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    level = ui_common_api_fn_00509f8e();
    L2_LOG_PREFIX(4u, 423u, m_battery, (uint32_t)level);
    L2_LOG_COMPRESSED(0x10400000u, t_battery, (uint32_t)level);
    audio_uart_page_498680(img, layout2_glasses_battery_dsc_5b8e84(level));

    if (ux_ring_mac_is_set_47d9c4() != 0u) {
        img = audio_uart_page_498668(row);
        g2_layout2_ring_battery_img = img;
        audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
        if (ux_ring_connected_47d9cc() != 0u)
            audio_uart_page_498680(img, layout2_ring_battery_dsc_5b8ece(
                                            dashboard_ring_battery_level_get_49c5bc()));
        else
            audio_uart_page_498680(img, g2_layout4_ring_off_icon_770a34);
    }
    layout2_place_5b8e1a(row, g2_layout2_date_enabled != 0u ? 72 : 42);

    for (i = 0; i < (int32_t)g2_layout2_slot_count; i++)
        layout2_slot_create_5b8f18((uint32_t)i, kinds[i]);

    /* BLE-disconnected icon takes the place of the slots while BLE is down. */
    img = audio_uart_page_498668(root);
    g2_layout2_ble_off_img = img;
    audio_uart_page_43f506(img, LV_SIZE_CONTENT);
    audio_uart_page_43f568(img, LV_SIZE_CONTENT);
    audio_uart_page_498680(img, g2_layout4_ble_off_icon_769e5c);
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    layout2_place_5b8e1a(img, layout2_slot_y_5b8e4a(2));

    if (UX_GetSystemBLEStatus() == 0u) {
        for (i = 0; i < 3; i++) {
            if (g2_layout2_slot_conts[i] != NULL && obj_valid(g2_layout2_slot_conts[i]) == 1u)
                audio_uart_page_43ded4(g2_layout2_slot_conts[i], LV_OBJ_FLAG_HIDDEN);
        }
        audio_uart_page_43dfa4(g2_layout2_ble_off_img, LV_OBJ_FLAG_HIDDEN);
    } else {
        for (i = 0; i < 3; i++) {
            if (g2_layout2_slot_conts[i] != NULL && obj_valid(g2_layout2_slot_conts[i]) == 1u)
                audio_uart_page_43dfa4(g2_layout2_slot_conts[i], LV_OBJ_FLAG_HIDDEN);
        }
        audio_uart_page_43ded4(g2_layout2_ble_off_img, LV_OBJ_FLAG_HIDDEN);
    }

    L2_LOG_PREFIX(3u, 483u, m_created, x);
    L2_LOG_COMPRESSED(0x0c400000u, t_created, x);
    return 0;
}

void layout2_deinit_5b96b4(void)
{
    int32_t i;

    g2_layout2_parent = NULL;
    g2_layout2_time_label = NULL;
    g2_layout2_date_label = NULL;
    g2_layout2_status_row = NULL;
    g2_layout2_glasses_battery_img = NULL;
    g2_layout2_ring_battery_img = NULL;
    g2_layout2_ble_off_img = NULL;
    for (i = 0; i < 3; i++) {
        g2_layout2_slot_conts[i] = NULL;
        g2_layout2_slots[i].icon = NULL;
        g2_layout2_slots[i].label = NULL;
        g2_layout2_slots[i].kind = 0u;
    }
    g2_layout2_clock_style = 0u;
    g2_layout2_date_enabled = 0u;
    g2_layout2_align_setting = 0u;
    g2_layout2_slot_count = 0u;
}

void layout2_set_x_5b9748(int32_t x)
{
    if (g2_layout2_parent != NULL)
        audio_uart_page_43f09a(g2_layout2_parent, x, 0);
}

/* The 12/24-hour flag is ignored: layout2 always prints the hour as given. */
void layout2_set_time_5b9760(uint32_t hour, uint32_t minute, uint32_t h24)
{
    char text[8];

    (void)h24;
    if (g2_layout2_time_label == NULL || obj_valid(g2_layout2_time_label) == 0u)
        return;
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    (void)audio_ble_format_to_buffer(text, s_time_fmt, hour, minute);
    (void)audio_uart_page_49942e(g2_layout2_time_label, text);
}

void layout2_set_date_5b97a0(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format)
{
    char text[16];

    (void)month;
    (void)date_format;
    if (g2_layout2_date_label == NULL || obj_valid(g2_layout2_date_label) == 0u)
        return;
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    (void)audio_ble_format_to_buffer(text, s_date_fmt,
                                     localized(g2_dashboard_weekday_keys_20004240[weekday]), day);
    (void)audio_uart_page_49942e(g2_layout2_date_label, text);
}

void layout2_slot_refresh_cb_5b97fa(g2_layout2_slot_t *slot, const void *arg)
{
    char text[16];

    (void)arg;
    if (slot == NULL || slot->icon == NULL || slot->label == NULL)
        return;
    if (obj_valid(slot->icon) == 0u || obj_valid(slot->label) == 0u)
        return;
    layout2_slot_icon_refresh_5b8d20(slot);
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    layout2_slot_text_5b8bc8(slot->kind, text, sizeof(text));
    (void)audio_uart_page_49942e(slot->label, text);
    audio_uart_page_43f6d6(slot->label, slot->icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
}

/* Weather slots (kind 1) re-read the dashboard state; the record is passed
 * through unused. */
VFP void layout2_set_weather_5b9860(uint16_t icon, uint32_t valid, uint32_t unit, float temperature)
{
    g2_layout2_weather_arg_t arg;

    arg.icon = icon;
    arg.temperature = temperature;
    arg.valid = valid;
    arg.unit = unit;
    layout2_slots_foreach_kind_5b90ae(1u, layout2_slot_refresh_cb_5b97fa, &arg);
}

void layout2_set_battery_5b987e(uint8_t level)
{
    if (g2_layout2_glasses_battery_img == NULL || obj_valid(g2_layout2_glasses_battery_img) == 0u)
        return;
    audio_uart_page_498680(g2_layout2_glasses_battery_img, layout2_glasses_battery_dsc_5b8e84(level));
}

/* Creates or deletes the ring battery image, then re-places the row. */
void layout2_set_ring_paired_5b98aa(uint32_t paired, uint8_t battery)
{
    void *img;

    if (g2_layout2_status_row == NULL || obj_valid(g2_layout2_status_row) == 0u)
        return;
    if (paired != 0u) {
        if (g2_layout2_ring_battery_img != NULL && obj_valid(g2_layout2_ring_battery_img) != 0u)
            return;
        img = audio_uart_page_498668(g2_layout2_status_row);
        g2_layout2_ring_battery_img = img;
        audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
        if (ux_ring_connected_47d9cc() != 0u)
            audio_uart_page_498680(img, layout2_ring_battery_dsc_5b8ece(battery));
        else
            audio_uart_page_498680(img, g2_layout4_ring_off_icon_770a34);
    } else {
        if (g2_layout2_ring_battery_img != NULL && obj_valid(g2_layout2_ring_battery_img) != 0u)
            audio_lv_delete_44d7b8(g2_layout2_ring_battery_img);
        g2_layout2_ring_battery_img = NULL;
    }
    layout2_place_5b8e1a(g2_layout2_status_row, g2_layout2_date_enabled != 0u ? 72 : 42);
}

void layout2_set_ring_connected_5b9954(uint32_t connected)
{
    if (g2_layout2_ring_battery_img == NULL || obj_valid(g2_layout2_ring_battery_img) == 0u)
        return;
    if (connected != 0u)
        audio_uart_page_498680(g2_layout2_ring_battery_img,
                               layout2_ring_battery_dsc_5b8ece(dashboard_ring_battery_level_get_49c5bc()));
    else
        audio_uart_page_498680(g2_layout2_ring_battery_img, g2_layout4_ring_off_icon_770a34);
}

void layout2_set_ring_battery_5b9990(uint8_t level)
{
    if (g2_layout2_ring_battery_img == NULL || obj_valid(g2_layout2_ring_battery_img) == 0u)
        return;
    if (ux_ring_connected_47d9cc() == 0u)
        return;
    audio_uart_page_498680(g2_layout2_ring_battery_img, layout2_ring_battery_dsc_5b8ece(level));
}

void layout2_slot_count_cb_5b99cc(g2_layout2_slot_t *slot, const void *arg)
{
    char text[16];
    int32_t count;

    if (slot == NULL || slot->label == NULL || obj_valid(slot->label) == 0u)
        return;
    count = *(const int32_t *)arg;
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    (void)audio_ble_format_to_buffer(text, s_int_fmt, count);
    (void)audio_uart_page_49942e(slot->label, text);
    if (slot->icon != NULL && obj_valid(slot->icon) == 1u)
        audio_uart_page_43f6d6(slot->label, slot->icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
}

void layout2_set_unread_count_5b9a38(uint32_t count)
{
    layout2_slots_foreach_kind_5b90ae(4u, layout2_slot_count_cb_5b99cc, &count);
}

void layout2_set_ble_connected_5b9a68(uint32_t connected)
{
    int32_t i;

    if (connected != 0u) {
        for (i = 0; i < 3; i++) {
            if (g2_layout2_slot_conts[i] != NULL && obj_valid(g2_layout2_slot_conts[i]) == 1u)
                audio_uart_page_43dfa4(g2_layout2_slot_conts[i], LV_OBJ_FLAG_HIDDEN);
        }
        if (g2_layout2_ble_off_img != NULL && obj_valid(g2_layout2_ble_off_img) == 1u)
            audio_uart_page_43ded4(g2_layout2_ble_off_img, LV_OBJ_FLAG_HIDDEN);
    } else {
        for (i = 0; i < 3; i++) {
            if (g2_layout2_slot_conts[i] != NULL && obj_valid(g2_layout2_slot_conts[i]) == 1u)
                audio_uart_page_43ded4(g2_layout2_slot_conts[i], LV_OBJ_FLAG_HIDDEN);
        }
        if (g2_layout2_ble_off_img != NULL && obj_valid(g2_layout2_ble_off_img) == 1u)
            audio_uart_page_43dfa4(g2_layout2_ble_off_img, LV_OBJ_FLAG_HIDDEN);
    }
}

void layout2_slot_health_refresh_5b9b04(g2_layout2_slot_t *slot)
{
    char text[16];
    int32_t index;
    float value;
    uint32_t duration;

    if (slot == NULL || slot->label == NULL || obj_valid(slot->label) == 0u)
        return;
    index = watchface_health_metric_index_5b8a6a(slot->kind);
    if (index < 0)
        return;
    (void)health_lock_storage();
    value = g2_health_data.metric[index].value;
    duration = g2_health_data.metric[index].duration;
    health_unlock_storage();
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    watchface_health_value_format_5b8a9c(value, slot->kind, duration, text, sizeof(text));
    (void)audio_uart_page_49942e(slot->label, text);
    if (slot->icon != NULL && obj_valid(slot->icon) == 1u)
        audio_uart_page_43f6d6(slot->label, slot->icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
}

void layout2_refresh_health_5b9ba0(void)
{
    int32_t i;

    for (i = 0; i < 3; i++)
        layout2_slot_health_refresh_5b9b04(&g2_layout2_slots[i]);
}

void layout2_slot_text_refresh_cb_5b9bc0(g2_layout2_slot_t *slot, const void *arg)
{
    char text[32];

    (void)arg;
    if (slot == NULL)
        return;
    if (slot->icon != NULL && obj_valid(slot->icon) == 1u)
        layout2_slot_icon_refresh_5b8d20(slot);
    if (slot->label == NULL || obj_valid(slot->label) != 1u)
        return;
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    layout2_slot_text_5b8bc8(slot->kind, text, sizeof(text));
    (void)audio_uart_page_49942e(slot->label, text);
    if (slot->icon != NULL && obj_valid(slot->icon) == 1u)
        audio_uart_page_43f6d6(slot->label, slot->icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
}

void layout2_refresh_kind2_5b9c32(void)
{
    layout2_slots_foreach_kind_5b90ae(2u, layout2_slot_text_refresh_cb_5b9bc0, NULL);
}

void layout2_refresh_kind3_5b9c4c(void)
{
    layout2_slots_foreach_kind_5b90ae(3u, layout2_slot_text_refresh_cb_5b9bc0, NULL);
}
