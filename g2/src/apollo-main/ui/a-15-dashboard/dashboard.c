/* Dashboard data glue, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard.c.
 * Native 0x49c070..0x49c0db and 0x49c146..0x49cd0f; literal pool 0x49cb14..0x49ce13.
 * dashboard_reset_auto_close_timeout 0x49c0dc is app/dashboard-auto/dashboard_auto_close_reset_49c0dc.c.
 *
 * Covers the three LVGL style getters IAR emitted out of line in this TU, the
 * dashboard mutex and data reset, the notification/battery callbacks the
 * dashboard registers (pointer table at 0x49ea94), the stock and calendar data
 * clears, and the grey-out ("darken") / resume passes over tile indicators and
 * widget trees used while the dashboard is not focused. */
#include <stdint.h>
#include <stddef.h>

/* LVGL 9.3 style property ids (src/misc/lv_style.h). */
#define LV_STYLE_BG_COLOR 28u
#define LV_STYLE_BORDER_COLOR 49u
#define LV_STYLE_TEXT_COLOR 88u

/* lv_color_format_t values tested on image sources. */
#define LV_CF_L8 6u
#define LV_CF_I1 7u
#define LV_CF_I8 10u

#define DASHBOARD_GREY 0x333333u
#define DASHBOARD_WHITE 0xffffffu

/* lv_image_header_t: word 0 = magic:8 | cf:8 | flags:16. */
typedef struct {
    uint32_t magic_cf_flags; /* +0x0 */
    uint32_t w_h;            /* +0x4 */
    uint32_t stride;         /* +0x8 */
} g2_lv_image_header_t;
_Static_assert(sizeof(g2_lv_image_header_t) == 12u, "lv_image_header_t");

/* Message handed to dashboard_send_to_app_serialize (0x4ff09c, protocols\
 * dashboard_service\dashboard_data_process.c). data_type 1 = notification
 * status, whose first payload word is the unread count. */
typedef struct {
    uint32_t package_id;     /* +0x00 */
    uint8_t flag;            /* +0x04 */
    uint8_t data_type;       /* +0x05 */
    uint8_t reserved_06[2];
    uint32_t payload[18];    /* +0x08 */
} g2_dashboard_app_msg_t;
_Static_assert(sizeof(g2_dashboard_app_msg_t) == 0x50u, "dashboard app message");

extern void *g2_dashboard_mutex;                          /* RAM 0x200743a8 */
extern uint8_t g2_dashboard_state[];                      /* RAM 0x200e3e80, 0xa0 bytes */
extern uint32_t g2_dashboard_package_id;                  /* RAM 0x200005b8 (initialised data) */
extern uint8_t g2_dashboard_stock_data_a[0x428];          /* RAM 0x200e4f20 */
extern uint8_t g2_dashboard_stock_data_b[0x430];          /* RAM 0x200e5348 */
extern uint8_t g2_dashboard_stock_data_c[0x428];          /* RAM 0x20378974 */
extern uint8_t g2_dashboard_calendar_events[4 + 0x1080];  /* RAM 0x2011df34, +0 u16 count */
extern uint8_t g2_dashboard_calendar_data_a[0x1080];      /* RAM 0x200e5778 */
extern uint8_t g2_dashboard_calendar_data_b[0x1088];      /* RAM 0x200e67f8 */
extern void *g2_dashboard_tile_indicators[];              /* RAM 0x20073c50 */
extern int32_t g2_dashboard_tile_indicator_count;         /* RAM 0x2000423c */
extern const uint8_t audio_uart_image_class_756108[];     /* ROM 0x756108 lv_image_class */

/* One-byte "update data" frames for the dashboard app (ROM 0x78f6d5..0x78f6d7, all 1). */
static const uint8_t update_msg_count = 1u;     /* ROM 0x78f6d5 */
static const uint8_t update_battery_level = 1u; /* ROM 0x78f6d6 */
static const uint8_t update_battery_charge = 1u; /* ROM 0x78f6d7 */

extern void *osMutexNew(const void *attr);                  /* 0x44971c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                 /* 0x44981c */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern uint32_t audio_uart_lv_style_property_44bdea(void *object, uint32_t selector, uint32_t property); /* lv_obj_get_style_prop */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);       /* lv_color_hex */
extern uint32_t audio_uart_page_441068(uint32_t red, uint32_t green, uint32_t blue); /* lv_color_make */
extern uint32_t audio_uart_page_rgb_equal_44102e(uint32_t first, uint32_t second); /* lv_color_eq */
extern void audio_uart_page_44127e(void *object, uint32_t color, uint32_t selector); /* set_style_bg_color */
extern void audio_uart_page_44129e(void *object, uint32_t opa, uint32_t selector);   /* set_style_bg_opa */
extern void audio_uart_page_4412ec(void *object, uint32_t color, uint32_t selector); /* set_style_border_color */
extern void audio_uart_page_44140e(void *object, uint32_t color, uint32_t selector); /* set_style_text_color */
extern void audio_uart_page_4413ce(void *object, uint32_t opa, uint32_t selector);   /* set_style_image_opa */
extern void lv_obj_set_style_image_recolor_4413de(void *object, uint32_t color, uint32_t selector);
extern void lv_obj_set_style_image_recolor_opa_4413fe(void *object, uint32_t opa, uint32_t selector);
extern uint32_t lv_obj_check_type_43e2bc(const void *object, const void *class_p); /* lv_obj_has_class */
extern const void *lv_image_get_src_498b50(void *image);
extern uint32_t audio_uart_lv_image_header_488f6a(const void *source, void *header); /* lv_image_decoder_get_info */
extern uint32_t audio_uart_lv_child_count_44ddea(void *object);
extern void *audio_uart_lv_child_get_44dce2(void *object, int32_t index);
extern void dashboard_main_screen_reset_4e7712(void);      /* ui_DashBaord_Main_Screen.c */
extern void stock_page_reset_4e9e06(void);                 /* ui_stock_page.c */
extern void stock_page_clear_4e9fde(void);                 /* ui_stock_page.c */
extern void calendar_page_reset_4ed80a(void);              /* ui_calendar_page.c */
extern void news_page_reset_4f4f3c(void);
extern void quicklist_page_reset_4f509a(uint8_t full);     /* ui_quicklist_page.c */
extern void health_page_reset_4fb1f2(void);                /* ui_health_page.c */
extern int32_t dashboard_send_to_app_serialize_4ff09c(const g2_dashboard_app_msg_t *msg);
extern uint32_t audio_settings_unread_message_count(void); /* 0x4974d4 SVC_ANCC_GetNotifCount */
extern uint8_t ring_battery_level_get(void);               /* 0x4ff98a */
extern uint8_t audio_uart_device_role_get(void);           /* 0x45a568, 1 = master */
extern uint32_t audio_uart_service_mode(void);             /* 0x45a570 */
extern uint32_t audio_log_wake_allowed(void);              /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len, uint32_t flags); /* 0x464bb2 */
extern uint32_t audio_log_flags(void);                     /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "dashboard"; /* ROM 0x78a6b8 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard.c"; /* ROM 0x701624 */
static const char send_fn[] = "dashboard_send_notification_status_to_app"; /* ROM 0x73d3fc */
static const char send_msg[] = "dashboard send notification to app, unread_count=%d"; /* ROM 0x7281a4 */
static const char send_msg_short[] = "[dashboard]dashboard send notification to app, unread_count=%d"; /* ROM 0x70a5e4 */
static const char send_failed[] = "send failed, ret=%d"; /* ROM 0x77eb2c */
static const char send_failed_short[] = "[dashboard]send failed, ret=%d"; /* ROM 0x75ee30 */
static const char send_ok[] = "send success, package_id=%d, unread_count=%d"; /* ROM 0x732954 */
static const char send_ok_short[] = "[dashboard]send success, package_id=%d, unread_count=%d"; /* ROM 0x71d2d0 */
static const char initial_fn[] = "dashboard_send_initial_notification_status_to_app"; /* ROM 0x7281d8 */
static const char initial_msg[] = "dashboard send initial notification to app, startup unread_count=%d"; /* ROM 0x701668 */
static const char initial_msg_short[] = "[dashboard]dashboard send initial notification to app, startup unread_count=%d"; /* ROM 0x6ec758 */
static const char msg_count_fn[] = "dashboard_msg_count_callback"; /* ROM 0x75ee50 */
static const char msg_count_null[] = "dashboard_msg_count_callback: data is NULL"; /* ROM 0x73d428 */
static const char msg_count_null_short[] = "[dashboard]dashboard_msg_count_callback: data is NULL"; /* ROM 0x71d308 */
static const char msg_count_msg[] = "dashboard_msg_count_callback: eventType=%d, msg_count=%d"; /* ROM 0x713900 */
static const char msg_count_msg_short[] = "[dashboard]dashboard_msg_count_callback: eventType=%d, msg_count=%d"; /* ROM 0x7016ac */
static const char update_ret[] = "dashboard_update_data_screen_on: ret = %d\n"; /* ROM 0x73d454 */
static const char update_ret_short[] = "[dashboard]dashboard_update_data_screen_on: ret = %d\n"; /* ROM 0x71d340 */
static const char battery_fn[] = "dashboard_battery_callback"; /* ROM 0x76a8a4 */
static const char battery_null[] = "dashboard_battery_callback: data is NULL"; /* ROM 0x73d480 */
static const char battery_null_short[] = "[dashboard]dashboard_battery_callback: data is NULL"; /* ROM 0x72820c */
static const char battery_msg[] = "dashboard_battery_callback: eventType=%d, data=%d"; /* ROM 0x728240 */
static const char battery_msg_short[] = "[dashboard]dashboard_battery_callback: eventType=%d, data=%d"; /* ROM 0x70a624 */
static const char battery_unknown[] = "Unknown battery event type: %d"; /* ROM 0x75ee70 */
static const char battery_unknown_short[] = "[dashboard]Unknown battery event type: %d"; /* ROM 0x73d4ac */
static const char ring_fn[] = "dashboard_ring_battery_callback"; /* ROM 0x75ee90 */
static const char ring_msg[] = "dashboard_ring_battery_callback: eventType=%d, data=%d"; /* ROM 0x71d378 */
static const char ring_msg_short[] = "[dashboard]dashboard_ring_battery_callback: eventType=%d, data=%d"; /* ROM 0x7016f0 */
static const char stock_fn[] = "dashboard_clear_stock_ui_data"; /* ROM 0x75eeb0 */
static const char stock_begin[] = "dashboard_clear_stock_ui_data: Clearing stock UI data"; /* ROM 0x71d3b0 */
static const char stock_begin_short[] = "[dashboard]dashboard_clear_stock_ui_data: Clearing stock UI data"; /* ROM 0x701734 */
static const char stock_done[] = "dashboard_clear_stock_ui_data: Stock UI data cleared successfully"; /* ROM 0x701778 */
static const char stock_done_short[] = "[dashboard]dashboard_clear_stock_ui_data: Stock UI data cleared successfully"; /* ROM 0x6ec7a8 */
static const char calendar_fn[] = "dashboard_clear_calendar_ui_data"; /* ROM 0x7530a8 */
static const char calendar_begin[] = "dashboard_clear_calendar_ui_data: Clearing calendar UI data"; /* ROM 0x71393c */
static const char calendar_begin_short[] = "[dashboard]dashboard_clear_calendar_ui_data: Clearing calendar UI data"; /* ROM 0x6f971c */
static const char calendar_done[] = "dashboard_clear_calendar_ui_data: Calendar UI data cleared successfully"; /* ROM 0x6f9764 */
static const char calendar_done_short[] = "[dashboard]dashboard_clear_calendar_ui_data: Calendar UI data cleared successfully"; /* ROM 0x6e6fa0 */
static const char darken_tiles_fn[] = "darken_tile_indicators"; /* ROM 0x775fd4 */
static const char darken_tile_msg[] = "Darkened tile_indicator[%d]"; /* ROM 0x76a8c0 */
static const char darken_tile_msg_short[] = "[dashboard]Darkened tile_indicator[%d]"; /* ROM 0x748b4c */
static const char resume_tiles_fn[] = "resume_tile_indicators"; /* ROM 0x775fec */
static const char resume_tile_msg[] = "Resumed tile_indicator[%d]"; /* ROM 0x76a8dc */
static const char resume_tile_msg_short[] = "[dashboard]Resumed tile_indicator[%d]"; /* ROM 0x748b74 */
static const char darken_fn[] = "darken_widget_colors_recursive"; /* ROM 0x75eed0 */
static const char indexed_dark[] = "Applied recolor to indexed image (cf=%d)"; /* ROM 0x73d4d8 */
static const char indexed_dark_short[] = "[dashboard]Applied recolor to indexed image (cf=%d)"; /* ROM 0x728274 */
static const char l8_dark[] = "Applied opacity to L8 image (cf=%d)"; /* ROM 0x7530cc */
static const char l8_dark_short[] = "[dashboard]Applied opacity to L8 image (cf=%d)"; /* ROM 0x732984 */
static const char no_info[] = "Failed to get image info, skipping recolor"; /* ROM 0x73d504 */
static const char no_info_short[] = "[dashboard]Failed to get image info, skipping recolor"; /* ROM 0x71d3e8 */
static const char resume_fn[] = "resume_widget_colors_recursive"; /* ROM 0x75eef0 */
static const char indexed_resume[] = "Applied white recolor to indexed image (cf=%d)"; /* ROM 0x7329b4 */
static const char indexed_resume_short[] = "[dashboard]Applied white recolor to indexed image (cf=%d)"; /* ROM 0x713978 */
static const char l8_resume[] = "Restored opacity for L8 image (cf=%d)"; /* ROM 0x748b9c */
static const char l8_resume_short[] = "[dashboard]Restored opacity for L8 image (cf=%d)"; /* ROM 0x7282a8 */

static void log0(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, msg_short, msg_short);
}

static void log1(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x00400000u, msg_short, msg_short, a);
}

static void log2(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a, uint32_t b)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a, b);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x00800000u, msg_short, msg_short, a, b);
}

static uint32_t image_cf(const g2_lv_image_header_t *header)
{
    return (header->magic_cf_flags >> 8) & 0xffu;
}

/* LVGL lv_obj_style_gen.h static inline getters kept out of line in this TU;
 * the lv_color_t result comes back in r0. */
uint32_t lv_obj_get_style_bg_color_49c070(void *obj, uint32_t part)
{
    return audio_uart_lv_style_property_44bdea(obj, part, LV_STYLE_BG_COLOR);
}

uint32_t lv_obj_get_style_border_color_49c07e(void *obj, uint32_t part)
{
    return audio_uart_lv_style_property_44bdea(obj, part, LV_STYLE_BORDER_COLOR);
}

uint32_t lv_obj_get_style_text_color_49c08c(void *obj, uint32_t part)
{
    return audio_uart_lv_style_property_44bdea(obj, part, LV_STYLE_TEXT_COLOR);
}

void dashboard_mutex_init_49c09a(void)
{
    if (g2_dashboard_mutex == NULL)
        g2_dashboard_mutex = osMutexNew(NULL);
}

/* Clear the dashboard state block and reset every dashboard page's cached data. */
void dashboard_data_reset_49c0b0(void)
{
    audio_uart_buffer_zero(g2_dashboard_state, 0xa0u, 0u);
    dashboard_main_screen_reset_4e7712();
    stock_page_reset_4e9e06();
    calendar_page_reset_4ed80a();
    news_page_reset_4f4f3c();
    quicklist_page_reset_4f509a(1u);
    health_page_reset_4fb1f2();
}

void dashboard_send_notification_status_to_app_49c146(uint32_t unread_count)
{
    log1(4u, send_fn, 138u, send_msg, send_msg_short, unread_count);
    g2_dashboard_app_msg_t msg;
    audio_uart_lv_memzero_48949c(&msg, sizeof(msg));
    msg.package_id = g2_dashboard_package_id;
    g2_dashboard_package_id++;
    msg.flag = 0u;
    msg.data_type = 1u;
    msg.payload[0] = unread_count;
    int32_t ret = dashboard_send_to_app_serialize_4ff09c(&msg);
    if (ret != 0)
        log1(3u, send_fn, 152u, send_failed, send_failed_short, (uint32_t)ret);
    else
        log2(4u, send_fn, 155u, send_ok, send_ok_short, msg.package_id, unread_count);
}

void dashboard_send_initial_notification_status_to_app_49c25a(void)
{
    uint32_t unread_count = audio_settings_unread_message_count();
    log1(4u, initial_fn, 167u, initial_msg, initial_msg_short, unread_count);
    dashboard_send_notification_status_to_app_49c146(unread_count);
}

/* ANCC message-count callback: forward the count to the app and, when the
 * dashboard is in front, refresh it. */
void dashboard_msg_count_callback_49c2b0(uint32_t event_type, const uint8_t *data)
{
    if (data == NULL) {
        log0(1u, msg_count_fn, 181u, msg_count_null, msg_count_null_short);
        return;
    }
    uint8_t count = data[0];
    log2(4u, msg_count_fn, 186u, msg_count_msg, msg_count_msg_short, event_type, count);
    if ((uint8_t)audio_uart_service_mode() == 1u && audio_log_wake_allowed() == 1u &&
        audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
        dashboard_send_notification_status_to_app_49c146(count);
        uint8_t frame = update_msg_count;
        uint32_t ret = audio_uart_master_display_refresh(1u, &frame, 1u, 0u);
        log1(4u, msg_count_fn, 196u, update_ret, update_ret_short, ret);
    }
}

/* Glasses battery callback: event 0 level, event 1 charge state; refresh the
 * dashboard on the master when it is in front. */
void dashboard_battery_callback_49c3d8(uint32_t event_type, const uint32_t *data)
{
    if (data == NULL) {
        log0(1u, battery_fn, 208u, battery_null, battery_null_short);
        return;
    }
    uint32_t value = *data;
    log2(4u, battery_fn, 213u, battery_msg, battery_msg_short, event_type, value);
    if (event_type == 0u) {
        if (audio_uart_device_role_get() == 1u && audio_log_wake_allowed() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
            uint8_t frame = update_battery_level;
            uint32_t ret = audio_uart_master_display_refresh(1u, &frame, 1u, 0u);
            log1(4u, battery_fn, 221u, update_ret, update_ret_short, ret);
        }
    } else if (event_type == 1u) {
        if (audio_uart_device_role_get() == 1u && audio_log_wake_allowed() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
            uint8_t frame = update_battery_charge;
            uint32_t ret = audio_uart_master_display_refresh(1u, &frame, 1u, 0u);
            log1(4u, battery_fn, 230u, update_ret, update_ret_short, ret);
        }
    } else {
        log1(2u, battery_fn, 235u, battery_unknown, battery_unknown_short, event_type);
    }
}

uint8_t dashboard_ring_battery_level_get_49c5bc(void)
{
    return ring_battery_level_get();
}

/* Ring battery callback: on event 0 push {0x13, 4, level} to the dashboard app. */
void dashboard_ring_battery_callback_49c5c4(uint32_t event_type, const uint8_t *data)
{
    log2(3u, ring_fn, 251u, ring_msg, ring_msg_short, event_type, data[0]);
    if (event_type == 0u && audio_log_wake_allowed() == 1u &&
        audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
        uint8_t frame[3];
        audio_uart_buffer_zero(frame, sizeof(frame), 0u);
        audio_uart_buffer_zero(frame, sizeof(frame), 0u);
        frame[0] = 0x13u;
        frame[1] = 4u;
        frame[2] = data[0];
        (void)audio_uart_master_display_refresh(1u, frame, sizeof(frame), 0u);
    }
}

void dashboard_clear_stock_ui_data_49c668(void)
{
    log0(4u, stock_fn, 269u, stock_begin, stock_begin_short);
    stock_page_clear_4e9fde();
    audio_uart_buffer_zero(g2_dashboard_stock_data_a, sizeof(g2_dashboard_stock_data_a), 0u);
    audio_uart_buffer_zero(g2_dashboard_stock_data_b, sizeof(g2_dashboard_stock_data_b), 0u);
    audio_uart_buffer_zero(g2_dashboard_stock_data_c, sizeof(g2_dashboard_stock_data_c), 0u);
    log0(4u, stock_fn, 281u, stock_done, stock_done_short);
}

void dashboard_clear_calendar_ui_data_49c728(void)
{
    log0(4u, calendar_fn, 289u, calendar_begin, calendar_begin_short);
    (void)osMutexAcquire(g2_dashboard_mutex, UINT32_MAX);
    *(uint16_t *)(void *)g2_dashboard_calendar_events = 0u;
    audio_uart_buffer_zero(g2_dashboard_calendar_events + 4, 0x1080u, 0u);
    audio_uart_buffer_zero(g2_dashboard_calendar_data_a, sizeof(g2_dashboard_calendar_data_a), 0u);
    audio_uart_buffer_zero(g2_dashboard_calendar_data_b, sizeof(g2_dashboard_calendar_data_b), 0u);
    (void)osMutexRelease(g2_dashboard_mutex);
    log0(4u, calendar_fn, 305u, calendar_done, calendar_done_short);
}

/* White tile indicators -> grey, opaque. */
void darken_tile_indicators_49c7fe(void)
{
    for (int32_t i = 0; i < g2_dashboard_tile_indicator_count; i++) {
        if (g2_dashboard_tile_indicators[i] == NULL)
            continue;
        void *tile = g2_dashboard_tile_indicators[i];
        uint32_t white = audio_uart_page_44104c(DASHBOARD_WHITE);
        if (audio_uart_page_rgb_equal_44102e(lv_obj_get_style_bg_color_49c070(tile, 0u), white) == 0u)
            continue;
        audio_uart_page_44127e(tile, audio_uart_page_44104c(DASHBOARD_GREY), 0u);
        audio_uart_page_44129e(tile, 0xffu, 0u);
        log1(4u, darken_tiles_fn, 341u, darken_tile_msg, darken_tile_msg_short, (uint32_t)i);
    }
}

/* Grey tile indicators -> white, opaque. */
void resume_tile_indicators_49c89e(void)
{
    for (int32_t i = 0; i < g2_dashboard_tile_indicator_count; i++) {
        if (g2_dashboard_tile_indicators[i] == NULL)
            continue;
        void *tile = g2_dashboard_tile_indicators[i];
        uint32_t grey = audio_uart_page_44104c(DASHBOARD_GREY);
        if (audio_uart_page_rgb_equal_44102e(lv_obj_get_style_bg_color_49c070(tile, 0u), grey) == 0u)
            continue;
        audio_uart_page_44127e(tile, audio_uart_page_44104c(DASHBOARD_WHITE), 0u);
        audio_uart_page_44129e(tile, 0xffu, 0u);
        log1(4u, resume_tiles_fn, 356u, resume_tile_msg, resume_tile_msg_short, (uint32_t)i);
    }
}

/* Grey out a widget tree: border grey, white text grey, indexed images recoloured
 * grey at full opacity, L8 images at opacity 0x40. The border colour is read
 * first and discarded. */
void darken_widget_colors_recursive_49c93e(void *obj)
{
    if (obj == NULL)
        return;
    (void)lv_obj_get_style_border_color_49c07e(obj, 0u);
    audio_uart_page_4412ec(obj, audio_uart_page_44104c(DASHBOARD_GREY), 0u);
    uint32_t text = lv_obj_get_style_text_color_49c08c(obj, 0u);
    if (audio_uart_page_rgb_equal_44102e(text, audio_uart_page_44104c(DASHBOARD_WHITE)) != 0u)
        audio_uart_page_44140e(obj, audio_uart_page_44104c(DASHBOARD_GREY), 0u);
    if (lv_obj_check_type_43e2bc(obj, audio_uart_image_class_756108) != 0u) {
        const void *src = lv_image_get_src_498b50(obj);
        if (src != NULL) {
            g2_lv_image_header_t header;
            if (audio_uart_lv_image_header_488f6a(src, &header) == 1u) {
                if (image_cf(&header) >= LV_CF_I1 && image_cf(&header) <= LV_CF_I8) {
                    lv_obj_set_style_image_recolor_4413de(obj, audio_uart_page_441068(0x33u, 0x33u, 0x33u), 0u);
                    lv_obj_set_style_image_recolor_opa_4413fe(obj, 0xffu, 0u);
                    log1(4u, darken_fn, 397u, indexed_dark, indexed_dark_short, image_cf(&header));
                } else if (image_cf(&header) == LV_CF_L8) {
                    audio_uart_page_4413ce(obj, 0x40u, 0u);
                    log1(4u, darken_fn, 401u, l8_dark, l8_dark_short, image_cf(&header));
                }
            } else {
                log0(2u, darken_fn, 406u, no_info, no_info_short);
            }
        }
    }
    uint32_t count = audio_uart_lv_child_count_44ddea(obj);
    for (uint32_t i = 0u; i < count; i++) {
        void *child = audio_uart_lv_child_get_44dce2(obj, (int32_t)i);
        if (child != NULL)
            darken_widget_colors_recursive_49c93e(child);
    }
}

/* Inverse of the darken pass: border white, grey text white, indexed images
 * recoloured white, L8 images back to full opacity. */
void resume_widget_colors_recursive_49cb50(void *obj)
{
    if (obj == NULL)
        return;
    audio_uart_page_4412ec(obj, audio_uart_page_44104c(DASHBOARD_WHITE), 0u);
    uint32_t text = lv_obj_get_style_text_color_49c08c(obj, 0u);
    if (audio_uart_page_rgb_equal_44102e(text, audio_uart_page_44104c(DASHBOARD_GREY)) != 0u)
        audio_uart_page_44140e(obj, audio_uart_page_44104c(DASHBOARD_WHITE), 0u);
    if (lv_obj_check_type_43e2bc(obj, audio_uart_image_class_756108) != 0u) {
        const void *src = lv_image_get_src_498b50(obj);
        if (src != NULL) {
            g2_lv_image_header_t header;
            if (audio_uart_lv_image_header_488f6a(src, &header) == 1u) {
                if (image_cf(&header) >= LV_CF_I1 && image_cf(&header) <= LV_CF_I8) {
                    lv_obj_set_style_image_recolor_4413de(obj, audio_uart_page_441068(0xffu, 0xffu, 0xffu), 0u);
                    lv_obj_set_style_image_recolor_opa_4413fe(obj, 0xffu, 0u);
                    log1(4u, resume_fn, 452u, indexed_resume, indexed_resume_short, image_cf(&header));
                } else if (image_cf(&header) == LV_CF_L8) {
                    audio_uart_page_4413ce(obj, 0xffu, 0u);
                    log1(4u, resume_fn, 456u, l8_resume, l8_resume_short, image_cf(&header));
                }
            } else {
                log0(2u, resume_fn, 461u, no_info, no_info_short);
            }
        }
    }
    uint32_t count = audio_uart_lv_child_count_44ddea(obj);
    for (uint32_t i = 0u; i < count; i++) {
        void *child = audio_uart_lv_child_get_44dce2(obj, (int32_t)i);
        if (child != NULL)
            resume_widget_colors_recursive_49cb50(child);
    }
}
