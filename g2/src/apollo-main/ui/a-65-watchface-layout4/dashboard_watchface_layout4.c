/* Dashboard watchface layout 4 (world clocks), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout4.c.
 * Native 0x5bb1cc..0x5bb2c5 and 0x5bb36c..0x5bbcb1 (literal pool
 * 0x5bbcb4..0x5bbd47). The earlier part of the same TU (pickers, time maths,
 * config validation, 0x5bab2c..0x5bb1cb) lives in the neighbouring segment;
 * this file calls it by address.
 *
 * Layout 4 shows up to three clocks, each a pair of analog-hand images (hour
 * hand by hour % 12, minute hand by minute / 5), a "<city> hh:mm" label and a
 * UTC-offset label, plus a BLE-off icon and a battery / ring-battery status row.
 * Ops table ROM 0x7140bc (g2_watchface_ops_kind4): create, deinit, set_x,
 * update_time, -, -, set_battery, -, set_ble, set_ring, set_ring_connected,
 * set_ring_battery.
 *
 * Floating point: the per-clock UTC offset is a float in hours; callees that
 * take it use the hard-float convention (profile g2-apollo-main-3). */
#include <stdint.h>
#include <stddef.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

#define LAYOUT4_MAX_CLOCKS 3u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u

/* Watchface config record handed to create (validated by 0x5bafc4). */
typedef struct {
    uint8_t kind;                  /* +0x00 4 = layout 4 */
    uint8_t reserved_01[3];        /* +0x01 */
    uint8_t align;                 /* +0x04 */
    uint8_t clock_count;           /* +0x05 1..3 */
    uint8_t offset_count;          /* +0x06 must equal clock_count */
    uint8_t reserved_07;           /* +0x07 */
    float tz_hours[LAYOUT4_MAX_CLOCKS]; /* +0x08 UTC offset in hours */
    uint8_t name_count;            /* +0x14 must equal clock_count */
    char names[LAYOUT4_MAX_CLOCKS][32]; /* +0x15 city names */
} g2_layout4_cfg_t;
_Static_assert(offsetof(g2_layout4_cfg_t, tz_hours) == 0x08, "tz_hours at +0x08");
_Static_assert(offsetof(g2_layout4_cfg_t, names) == 0x15, "names at +0x15");

/* One 0x1c-byte record per clock, RAM 0x2007284c. */
typedef struct {
    void *cont;        /* +0x00 slot container */
    void *hour_hand;   /* +0x04 lv_image */
    void *minute_hand; /* +0x08 lv_image */
    void *local_row;   /* +0x0c flex row (first clock at UTC+0 only) */
    void *local_icon;  /* +0x10 lv_image inside local_row */
    void *time_label;  /* +0x14 "<city> hh:mm" */
    void *offset_label;/* +0x18 UTC offset text */
} g2_layout4_clock_t;
_Static_assert(sizeof(g2_layout4_clock_t) == 0x1c, "layout4 clock record");

extern void *g2_layout4_root;                       /* RAM 0x200744a4 */
extern void *g2_layout4_ble_icon;                   /* RAM 0x200744a8 */
extern void *g2_layout4_status_row;                 /* RAM 0x200744ac */
extern void *g2_layout4_battery_icon;               /* RAM 0x200744b0 */
extern void *g2_layout4_ring_icon;                  /* RAM 0x200744b4 */
extern uint8_t g2_layout4_align_setting;            /* RAM 0x20074fae */
extern uint8_t g2_layout4_clock_count;              /* RAM 0x20074faf */
extern g2_layout4_clock_t g2_layout4_clocks[LAYOUT4_MAX_CLOCKS]; /* RAM 0x2007284c */
extern float g2_layout4_tz_hours[LAYOUT4_MAX_CLOCKS];            /* RAM 0x20073fc0 */
extern char g2_layout4_city_names[LAYOUT4_MAX_CLOCKS][32];       /* RAM 0x20072670 */

extern const int32_t g2_layout4_slot_y[LAYOUT4_MAX_CLOCKS]; /* ROM 0x78a7b4 {6, 84, 168} */
extern const uint8_t g2_translate_lang_pair_font[];  /* ROM 0x7547b8 lv_font_t */
extern const uint8_t g2_lv_font_754800[];            /* ROM 0x754800 lv_font_t */
extern const uint8_t g2_layout4_local_icon_76c4a4[]; /* ROM 0x76c4a4 lv_image_dsc_t */
extern const uint8_t g2_layout4_ble_off_icon_769e5c[]; /* ROM 0x769e5c lv_image_dsc_t */
extern const uint8_t g2_layout4_ring_off_icon_770a34[]; /* ROM 0x770a34 lv_image_dsc_t */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* LVGL. */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);    /* lv_obj_is_valid */
extern void *audio_uart_page_43de82(void *parent);                       /* lv_obj_create */
extern void audio_uart_page_delete_event_filter_44d7b8(void *object);    /* lv_obj_delete */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);            /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);            /* lv_obj_remove_flag */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);     /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                /* lv_obj_set_height */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);     /* lv_obj_set_pos */
extern void audio_uart_page_43f66c(void *obj);                           /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);               /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                    /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel); /* bg_opa */
extern void audio_uart_page_44131c(void *obj, uint32_t v, uint32_t sel); /* border_width */
extern void audio_uart_page_44133a(void *obj, uint32_t v, uint32_t sel); /* outline_width */
extern void audio_uart_page_441378(void *obj, uint32_t v, uint32_t sel); /* outline_pad */
extern void audio_uart_page_441386(void *obj, uint32_t v, uint32_t sel); /* shadow_width */
extern void audio_uart_page_44146a(void *obj, uint32_t v, uint32_t sel); /* radius */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t v, uint32_t sel); /* text_opa */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_4411e4(void *obj, uint32_t v, uint32_t sel); /* text_align */
extern void audio_uart_page_441254(void *obj, uint32_t v, uint32_t sel); /* pad_column */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);            /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main_place, uint32_t cross_place,
                                   uint32_t track_place);                /* lv_obj_set_flex_align */
extern void *audio_uart_page_498668(void *parent);                       /* lv_image_create */
extern void audio_uart_page_498680(void *obj, const void *src);          /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                       /* lv_label_create */
extern void audio_uart_page_49942e(void *obj, const char *text);         /* lv_label_set_text */

/* Runtime / services. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern VFP float roundf_577d08(float x);
extern uint8_t UX_GetSystemBLEStatus(void);            /* 0x47d8ce */
extern uint32_t ux_ring_mac_is_set_47d9c4(void);
extern uint8_t ux_ring_connected_47d9cc(void);
extern uint8_t dashboard_ring_battery_level_get_49c5bc(void);
extern uint8_t ui_common_api_fn_00509f8e(void);        /* glasses battery percent */

/* Same TU, neighbouring segment. */
extern void lv_obj_set_style_pad_all_5bab2c(void *obj, uint32_t value, uint32_t selector);
extern void layout4_place_5bab76(void *obj, int32_t y);
extern const void *layout4_glasses_battery_dsc_5baba6(uint8_t level);
extern const void *layout4_ring_battery_dsc_5bac42(uint8_t level);
extern const void *layout4_hour_hand_src_5bac8c(int32_t hour);
extern const void *layout4_minute_hand_src_5bad10(int32_t minute);
extern VFP void layout4_zone_time_5bad98(float tz_hours, int32_t hour, int32_t minute,
                                         int32_t *out_hour, int32_t *out_minute);
extern void layout4_now_hm_5badf4(int32_t *hour, int32_t *minute);
extern void layout4_format_time_5bae52(const char *name, int32_t hour, int32_t minute,
                                       char *buf, uint32_t size);
extern VFP void layout4_format_offset_5baef0(float tz_hours, char *buf, uint32_t size);
extern uint32_t layout4_cfg_valid_5bafc4(const g2_layout4_cfg_t *cfg);

static const char module_tag[] = "dashboard.wf.l4"; /* ROM 0x7859a0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_watchface_layout4.c"; /* ROM 0x6e73e4 */
static const char create_fn[] = "layout4_create"; /* ROM 0x7859c0 */
static const char parent_null[] = "layout4 create: parent NULL"; /* ROM 0x76abec */
static const char parent_null_short[] = "[dashboard.wf.l4]layout4 create: parent NULL"; /* ROM 0x732ec4 */
static const char cfg_invalid[] = "layout4 create: cfg invalid, return -1 to fallback"; /* ROM 0x7287bc */
static const char cfg_invalid_short[] =
    "[dashboard.wf.l4]layout4 create: cfg invalid, return -1 to fallback"; /* ROM 0x701ea4 */
static const char align_msg[] = "layout4 create: align=%u clock_count=%u"; /* ROM 0x748ffc */
static const char align_short[] = "[dashboard.wf.l4]layout4 create: align=%u clock_count=%u"; /* ROM 0x714080 */
static const char battery_msg[] = "layout4_set_battery: lvl=%d"; /* ROM 0x76ac08 */
static const char battery_short[] = "[dashboard.wf.l4]layout4_set_battery: lvl=%d"; /* ROM 0x732ef4 */
static const char created_msg[] = "layout4 created at x=%d (ble=%d)"; /* ROM 0x7534bc */
static const char created_short[] = "[dashboard.wf.l4]layout4 created at x=%d (ble=%d)"; /* ROM 0x7287f0 */

#define L4_LOG(level, line, plain, ...)                                            \
    do {                                                                           \
        if (audio_log_flags() & 2u)                                                \
            audio_log_extended((level), module_tag, source_file, create_fn, (line), \
                               plain, ##__VA_ARGS__);                              \
    } while (0)
#define L4_SHORT(flags, compact, ...)                                              \
    do {                                                                           \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                  \
            (void)compress_log_output((flags), compact, compact, ##__VA_ARGS__);   \
    } while (0)

static uint32_t obj_ok(void *obj)
{
    return obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) != 0u;
}

/* Zero bg/border/outline/shadow/padding/radius on a plain container. */
static void plain_style(void *obj)
{
    audio_uart_page_44129e(obj, 0u, 0u);
    audio_uart_page_44131c(obj, 0u, 0u);
    audio_uart_page_44133a(obj, 0u, 0u);
    audio_uart_page_441386(obj, 0u, 0u);
    lv_obj_set_style_pad_all_5bab2c(obj, 0u, 0u);
    audio_uart_page_44146a(obj, 0u, 0u);
}

/* Shows the BLE-off icon when the phone link is down. */
void layout4_set_ble_icon_5bb1cc(uint32_t connected)
{
    if (g2_layout4_ble_icon != NULL && audio_terminal_ui_object_valid_43e2ea(g2_layout4_ble_icon) == 1u) {
        if (connected != 0u)
            audio_uart_page_43ded4(g2_layout4_ble_icon, LV_OBJ_FLAG_HIDDEN);
        else
            audio_uart_page_43dfa4(g2_layout4_ble_icon, LV_OBJ_FLAG_HIDDEN);
    }
}

/* Converts the reference time to clock idx's zone and redraws its hands and label. */
void layout4_refresh_clock_5bb208(uint32_t idx, int32_t hour, int32_t minute)
{
    int32_t zone_hour;
    int32_t zone_minute;
    char text[64];
    g2_layout4_clock_t *clock;

    if (idx >= LAYOUT4_MAX_CLOCKS || (int32_t)idx >= (int32_t)g2_layout4_clock_count)
        return;
    clock = &g2_layout4_clocks[idx];
    layout4_zone_time_5bad98(g2_layout4_tz_hours[idx], hour, minute, &zone_hour, &zone_minute);
    if (clock->hour_hand != NULL && audio_terminal_ui_object_valid_43e2ea(clock->hour_hand) == 1u)
        audio_uart_page_498680(clock->hour_hand, layout4_hour_hand_src_5bac8c(zone_hour));
    if (clock->minute_hand != NULL && audio_terminal_ui_object_valid_43e2ea(clock->minute_hand) == 1u)
        audio_uart_page_498680(clock->minute_hand, layout4_minute_hand_src_5bad10(zone_minute));
    if (clock->time_label != NULL && audio_terminal_ui_object_valid_43e2ea(clock->time_label) == 1u) {
        aeabi_memset_43c0e4(text, sizeof(text), 0);
        /* The local clock (with its icon) is drawn without a city name. */
        layout4_format_time_5bae52(clock->local_icon != NULL ? NULL : g2_layout4_city_names[idx],
                                   zone_hour, zone_minute, text, sizeof(text));
        audio_uart_page_49942e(clock->time_label, text);
    }
}

int32_t layout4_create_5bb36c(void *parent, int32_t x, const g2_layout4_cfg_t *cfg)
{
    uint32_t ble;
    int32_t now_hour;
    int32_t now_minute;
    char text[16];
    uint8_t level;

    if (parent == NULL) {
        L4_LOG(1u, 0x1ecu, parent_null);
        L4_SHORT(0x04000000u, parent_null_short);
        return -1;
    }
    if (layout4_cfg_valid_5bafc4(cfg) == 0u) {
        L4_LOG(1u, 0x1f2u, cfg_invalid);
        L4_SHORT(0x04000000u, cfg_invalid_short);
        return -1;
    }

    g2_layout4_align_setting = cfg->align;
    g2_layout4_clock_count = cfg->clock_count;
    aeabi_memset_43c0e4(g2_layout4_tz_hours, sizeof(g2_layout4_tz_hours), 0);
    aeabi_memset_43c0e4(g2_layout4_city_names, sizeof(g2_layout4_city_names), 0);
    for (int32_t i = 0; i < (int32_t)g2_layout4_clock_count; i++) {
        g2_layout4_tz_hours[i] = cfg->tz_hours[i];
        audio_settings_copy_text(g2_layout4_city_names[i], cfg->names[i], 31u);
        g2_layout4_city_names[i][31] = '\0';
    }
    L4_LOG(3u, 0x203u, align_msg, (uint32_t)g2_layout4_align_setting, (uint32_t)g2_layout4_clock_count);
    L4_SHORT(0x0c800000u, align_short, (uint32_t)g2_layout4_align_setting,
             (uint32_t)g2_layout4_clock_count);

    ble = UX_GetSystemBLEStatus() != 0u ? 1u : 0u;

    g2_layout4_root = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(g2_layout4_root, 200, 288);
    audio_uart_page_43f09a(g2_layout4_root, x, 0);
    audio_uart_page_44127e(g2_layout4_root, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_layout4_root, 0u, 0u);
    audio_uart_page_44131c(g2_layout4_root, 0u, 0u);
    audio_uart_page_44133a(g2_layout4_root, 0u, 0u);
    audio_uart_page_441378(g2_layout4_root, 0u, 0u);
    audio_uart_page_441386(g2_layout4_root, 0u, 0u);
    lv_obj_set_style_pad_all_5bab2c(g2_layout4_root, 0u, 0u);
    audio_uart_page_44146a(g2_layout4_root, 0u, 0u);
    audio_uart_page_44140e(g2_layout4_root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(g2_layout4_root, 0xffu, 0u);
    audio_uart_page_43dfa4(g2_layout4_root, LV_OBJ_FLAG_SCROLLABLE);

    layout4_now_hm_5badf4(&now_hour, &now_minute);
    aeabi_memset_43c0e4(g2_layout4_clocks, sizeof(g2_layout4_clocks), 0);
    for (int32_t i = 0; i < (int32_t)g2_layout4_clock_count; i++) {
        g2_layout4_clock_t *clock = &g2_layout4_clocks[i];
        int32_t y = g2_layout4_slot_y[i];
        void *obj;
        void *img;
        uint32_t local;

        obj = audio_uart_page_43de82(g2_layout4_root);
        audio_uart_page_43f4c0(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        plain_style(obj);
        audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_SCROLLABLE);
        clock->cont = obj;

        img = audio_uart_page_498668(obj);
        audio_uart_page_43f506(img, 26);
        audio_uart_page_43f568(img, 26);
        audio_uart_page_43f09a(img, 0, 0);
        audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
        clock->hour_hand = img;

        img = audio_uart_page_498668(obj);
        audio_uart_page_43f506(img, 26);
        audio_uart_page_43f568(img, 26);
        audio_uart_page_43f09a(img, 32, 0);
        audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
        clock->minute_hand = img;
        layout4_place_5bab76(obj, y);

        /* The first clock is "local" when its offset rounds to 0 minutes. */
        local = (i == 0 && (int32_t)roundf_577d08(g2_layout4_tz_hours[i] * 60.0f) == 0) ? 1u : 0u;
        if (local != 0u) {
            void *row = audio_uart_page_43de82(g2_layout4_root);
            audio_uart_page_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
            plain_style(row);
            audio_uart_page_44140e(row, audio_uart_page_44104c(0xffffffu), 0u);
            audio_uart_page_44142e(row, 0xffu, 0u);
            audio_uart_page_43dfa4(row, LV_OBJ_FLAG_SCROLLABLE);
            audio_uart_page_48ba78(row, 0u);
            audio_uart_page_48ba92(row, 0u, 2u, 2u);
            audio_uart_page_441254(row, 6u, 0u);
            clock->local_row = row;

            img = audio_uart_page_498668(row);
            audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
            audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
            audio_uart_page_498680(img, g2_layout4_local_icon_76c4a4);
            clock->local_icon = img;

            obj = audio_uart_page_499416(row);
            audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
            audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
            audio_uart_page_44143e(obj, g2_translate_lang_pair_font, 0u);
            audio_uart_page_4411e4(obj, 2u, 0u);
            clock->time_label = obj;
            layout4_place_5bab76(row, y + 32);
        } else {
            obj = audio_uart_page_499416(g2_layout4_root);
            audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
            audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
            audio_uart_page_44143e(obj, g2_translate_lang_pair_font, 0u);
            clock->time_label = obj;
            layout4_place_5bab76(obj, y + 32);
        }

        obj = audio_uart_page_499416(g2_layout4_root);
        audio_uart_page_43f506(obj, LV_SIZE_CONTENT);
        audio_uart_page_43f568(obj, LV_SIZE_CONTENT);
        audio_uart_page_44143e(obj, g2_lv_font_754800, 0u);
        aeabi_memset_43c0e4(text, sizeof(text), 0);
        layout4_format_offset_5baef0(g2_layout4_tz_hours[i], text, sizeof(text));
        audio_uart_page_49942e(obj, text);
        audio_uart_page_44140e(obj, audio_uart_page_44104c(0x555555u), 0u);
        audio_uart_page_44142e(obj, 0xffu, 0u);
        clock->offset_label = obj;
        layout4_place_5bab76(obj, y + 54);

        layout4_refresh_clock_5bb208((uint32_t)i, now_hour, now_minute);
    }

    g2_layout4_ble_icon = audio_uart_page_498668(g2_layout4_root);
    audio_uart_page_43f506(g2_layout4_ble_icon, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_layout4_ble_icon, LV_SIZE_CONTENT);
    audio_uart_page_498680(g2_layout4_ble_icon, g2_layout4_ble_off_icon_769e5c);
    audio_uart_page_43ded4(g2_layout4_ble_icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(g2_layout4_ble_icon, LV_OBJ_FLAG_SCROLLABLE);
    layout4_place_5bab76(g2_layout4_ble_icon, 243);

    g2_layout4_status_row = audio_uart_page_43de82(g2_layout4_root);
    audio_uart_page_43f4c0(g2_layout4_status_row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    plain_style(g2_layout4_status_row);
    audio_uart_page_43dfa4(g2_layout4_status_row, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_48ba78(g2_layout4_status_row, 0u);
    audio_uart_page_48ba92(g2_layout4_status_row, 0u, 2u, 2u);
    audio_uart_page_441254(g2_layout4_status_row, 12u, 0u);

    g2_layout4_battery_icon = audio_uart_page_498668(g2_layout4_status_row);
    audio_uart_page_43ded4(g2_layout4_battery_icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(g2_layout4_battery_icon, LV_OBJ_FLAG_SCROLLABLE);
    level = ui_common_api_fn_00509f8e();
    L4_LOG(4u, 0x2b4u, battery_msg, (uint32_t)level);
    L4_SHORT(0x10400000u, battery_short, (uint32_t)level);
    audio_uart_page_498680(g2_layout4_battery_icon, layout4_glasses_battery_dsc_5baba6(level));

    if (ux_ring_mac_is_set_47d9c4() != 0u) {
        g2_layout4_ring_icon = audio_uart_page_498668(g2_layout4_status_row);
        audio_uart_page_43ded4(g2_layout4_ring_icon, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(g2_layout4_ring_icon, LV_OBJ_FLAG_SCROLLABLE);
        if (ux_ring_connected_47d9cc() == 0u)
            audio_uart_page_498680(g2_layout4_ring_icon, g2_layout4_ring_off_icon_770a34);
        else
            audio_uart_page_498680(g2_layout4_ring_icon,
                                   layout4_ring_battery_dsc_5bac42(dashboard_ring_battery_level_get_49c5bc()));
    }

    /* Bottom-align the status row at y = 286. */
    audio_uart_page_43f66c(g2_layout4_root);
    layout4_place_5bab76(g2_layout4_status_row,
                         286 - audio_uart_lv_obj_height_43fdda(g2_layout4_status_row));
    layout4_set_ble_icon_5bb1cc(ble);

    L4_LOG(3u, 0x2ceu, created_msg, x, ble);
    L4_SHORT(0x0c800000u, created_short, x, ble);
    return 0;
}

void layout4_deinit_5bbaa8(void)
{
    g2_layout4_root = NULL;
    g2_layout4_ble_icon = NULL;
    g2_layout4_status_row = NULL;
    g2_layout4_battery_icon = NULL;
    g2_layout4_ring_icon = NULL;
    aeabi_memset_43c0e4(g2_layout4_clocks, sizeof(g2_layout4_clocks), 0);
    g2_layout4_align_setting = 0u;
    g2_layout4_clock_count = 0u;
    aeabi_memset_43c0e4(g2_layout4_tz_hours, sizeof(g2_layout4_tz_hours), 0);
    aeabi_memset_43c0e4(g2_layout4_city_names, sizeof(g2_layout4_city_names), 0);
}

void layout4_set_x_5bbb00(int32_t x)
{
    if (g2_layout4_root != NULL)
        audio_uart_page_43f09a(g2_layout4_root, x, 0);
}

/* Ops slot +0x0c: the stock body forwards its third argument as the hour and
 * its second as the minute. */
void layout4_update_time_5bbb1c(uint32_t unused, int32_t minute, int32_t hour)
{
    (void)unused;
    for (int32_t i = 0; i < (int32_t)g2_layout4_clock_count; i++)
        layout4_refresh_clock_5bb208((uint32_t)i, hour, minute);
}

void layout4_set_battery_5bbb40(uint8_t level)
{
    if (g2_layout4_battery_icon != NULL && audio_terminal_ui_object_valid_43e2ea(g2_layout4_battery_icon) != 0u)
        audio_uart_page_498680(g2_layout4_battery_icon, layout4_glasses_battery_dsc_5baba6(level));
}

void layout4_set_ble_5bbb84(uint32_t connected)
{
    layout4_set_ble_icon_5bb1cc(connected);
}

/* Creates or deletes the ring-battery icon, then re-anchors the status row. */
void layout4_set_ring_5bbb8c(uint32_t ring_present, uint8_t battery)
{
    if (!obj_ok(g2_layout4_status_row))
        return;
    if (ring_present == 0u) {
        if (obj_ok(g2_layout4_ring_icon))
            audio_uart_page_delete_event_filter_44d7b8(g2_layout4_ring_icon);
        g2_layout4_ring_icon = NULL;
    } else {
        if (obj_ok(g2_layout4_ring_icon))
            return;
        g2_layout4_ring_icon = audio_uart_page_498668(g2_layout4_status_row);
        audio_uart_page_43ded4(g2_layout4_ring_icon, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(g2_layout4_ring_icon, LV_OBJ_FLAG_SCROLLABLE);
        if (ux_ring_connected_47d9cc() == 0u)
            audio_uart_page_498680(g2_layout4_ring_icon, g2_layout4_ring_off_icon_770a34);
        else
            audio_uart_page_498680(g2_layout4_ring_icon, layout4_ring_battery_dsc_5bac42(battery));
    }
    audio_uart_page_43f66c(g2_layout4_root);
    layout4_place_5bab76(g2_layout4_status_row,
                         286 - audio_uart_lv_obj_height_43fdda(g2_layout4_status_row));
}

void layout4_set_ring_connected_5bbc3c(uint32_t connected)
{
    if (!obj_ok(g2_layout4_ring_icon))
        return;
    if (connected == 0u)
        audio_uart_page_498680(g2_layout4_ring_icon, g2_layout4_ring_off_icon_770a34);
    else
        audio_uart_page_498680(g2_layout4_ring_icon,
                               layout4_ring_battery_dsc_5bac42(dashboard_ring_battery_level_get_49c5bc()));
}

void layout4_set_ring_battery_5bbc80(uint8_t level)
{
    if (obj_ok(g2_layout4_ring_icon) && ux_ring_connected_47d9cc() != 0u)
        audio_uart_page_498680(g2_layout4_ring_icon, layout4_ring_battery_dsc_5bac42(level));
}
