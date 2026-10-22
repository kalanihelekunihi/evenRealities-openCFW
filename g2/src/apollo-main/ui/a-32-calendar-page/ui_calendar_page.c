/* Dashboard calendar widget page (first part), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_calendar_page.c.
 * Native 0x4ed7d8..0x4eda73, 0x4edac4..0x4eeaa5 and 0x4eeadc..0x4eebdb;
 * literal pools 0x4eda74..0x4edac3, 0x4ee6f8..0x4ee70b, 0x4eeaa8..0x4eeadb and
 * 0x4eef38..0x4eef7b (the last shared with the expanded page at 0x4eef7c).
 *
 * Covers the calendar data reset, the expanded page's 28 px snap scrolling
 * (lv_anim on the content object plus a proportional scrollbar), the page
 * refresh entry, the non-expanded widget (up to three events of title /
 * optional location / time, or a disconnected / no-event / default
 * placeholder) and the forwarding of UI events to the dashboard app. */
#include <stdint.h>
#include <stddef.h>

#define CALENDAR_TILE_COUNT 6u
#define CALENDAR_EVENTS_MAX 8u
#define CALENDAR_WIDGET_EVENTS 3u
#define DASHBOARD_APP 1u
#define WAIT_FOREVER 0xffffffffu

/* Expanded page viewport and scroll snapping. */
#define EXT_VIEW_H 256
#define SCROLL_STEP 28
#define SCROLL_FAST_SPEED 100
#define SCROLL_ANIM_MS 200

/* Non-expanded widget frame (inside the 352x288 tile). */
#define FRAME_X 20
#define FRAME_Y 16
#define FRAME_W 315
#define FRAME_H 256
#define ICON_SIZE 24
#define LABEL_H 28
#define TITLE_W 280
#define LOCATION_W 283
#define TIME_W 287

/* LVGL 9.3 constants. */
#define LV_OBJ_FLAG_SCROLLABLE 0x00010u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_LABEL_LONG_DOT 1u
#define LV_ALIGN_CENTER 9u
#define LV_FLEX_FLOW_ROW 0u
#define LV_FLEX_FLOW_COLUMN 1u
#define LV_FLEX_ALIGN_CENTER 2u
#define LV_OPA_TRANSP 0u
#define LV_OPA_COVER 0xffu
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_EVENT_CLICKED 10u

#define CAL_BLACK 0x000000u
#define CAL_WHITE 0xffffffu

/* UI-side event codes forwarded to the dashboard app (custom LVGL codes). */
#define CAL_EVENT_0x44 0x44u /* carries an lv_point_t */
#define CAL_EVENT_0x45 0x45u /* carries an lv_point_t */
#define CAL_EVENT_0x48 0x48u
#define CAL_EVENT_0x49 0x49u

/* Schedule record (see app/a-16-dashboard/dashboard_async_update_data.c). */
typedef struct {
    char title[0xb0];     /* +0x000 */
    char location[0x11b]; /* +0x0b0 optional */
    char time[0x41];      /* +0x1cb */
    uint32_t stamp;       /* +0x20c */
} g2_schedule_record_t;
_Static_assert(sizeof(g2_schedule_record_t) == 0x210u, "schedule record");

/* Calendar UI copy (RAM 0x2011df34, cleared as 0x1088 bytes). */
typedef struct {
    uint16_t count;                              /* +0x0000 */
    uint8_t reserved_0002[2];
    g2_schedule_record_t event[CALENDAR_EVENTS_MAX]; /* +0x0004 */
    uint32_t authority;                          /* +0x1084 1 = calendar access granted */
} g2_schedule_ui_t;
_Static_assert(sizeof(g2_schedule_ui_t) == 0x1088u, "calendar UI data");

/* Widgets of one event on the non-expanded page (RAM 0x20074b24 + 0x18 * n). */
typedef struct {
    void *title_icon;     /* +0x00 */
    void *title_label;    /* +0x04 */
    void *location_icon;  /* +0x08 */
    void *location_label; /* +0x0c */
    void *time_icon;      /* +0x10 */
    void *time_label;     /* +0x14 */
} g2_calendar_event_widgets_t;
_Static_assert(sizeof(g2_calendar_event_widgets_t) == 0x18u, "event widgets");

typedef struct {
    void *tile;  /* +0x00 */
    void *frame; /* +0x04 */
} g2_dashboard_tile_t;

/* lv_anim_t (LVGL 9.3 fork) as laid out on the 0x60-byte stack frame. */
typedef struct {
    void *var;                        /* +0x00 */
    void (*exec_cb)(void *, int32_t); /* +0x04 */
    void *custom_exec_cb;             /* +0x08 */
    void *start_cb;                   /* +0x0c */
    void (*completed_cb)(void *);     /* +0x10 */
    void *deleted_cb;                 /* +0x14 */
    void *get_value_cb;               /* +0x18 */
    void *user_data;                  /* +0x1c */
    int32_t (*path_cb)(void *);       /* +0x20 */
    int32_t start_value;              /* +0x24 */
    int32_t current_value;            /* +0x28 */
    int32_t end_value;                /* +0x2c */
    int32_t duration;                 /* +0x30 */
    uint8_t rest[0x2c];               /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60u, "stock anim frame is 96 bytes");

typedef struct {
    int32_t x;
    int32_t y;
} g2_lv_point_t;

/* lv_event_t prefix; lv_event_get_param() is inlined as e->param. */
typedef struct {
    void *current_target; /* +0x00 */
    void *original_target; /* +0x04 */
    uint32_t code;        /* +0x08 */
    void *user_data;      /* +0x0c */
    void *param;          /* +0x10 */
} g2_lv_event_t;

extern g2_schedule_ui_t g2_dashboard_schedule_ui_2011df34;          /* RAM 0x2011df34 */
extern void *g2_dashboard_mutex_200743a8;                           /* RAM 0x200743a8 osMutexId */
extern g2_dashboard_tile_t g2_dashboard_tiles[CALENDAR_TILE_COUNT]; /* RAM 0x200734bc */
extern void *g2_dashboard_focus_frame;                              /* RAM 0x20074b9c, expanded-page parent */
extern void *audio_uart_ring_primary_head_cell;                     /* RAM 0x200746dc: active lv_font_t * */
extern uint32_t g2_calendar_widget_init_flag_20074b1c;  /* RAM 0x20074b1c widget_calendar_init_flag */
extern uint32_t g2_calendar_scroll_anim_running_20074b20; /* RAM 0x20074b20 */
extern g2_calendar_event_widgets_t g2_calendar_event_widgets_20074b24[CALENDAR_WIDGET_EVENTS]; /* RAM 0x20074b24 */
extern void *g2_calendar_ext_content_20074b70;          /* RAM 0x20074b70 scrolled object */
extern void *g2_calendar_ext_scrollbar_20074b74;        /* RAM 0x20074b74 */
extern int32_t g2_calendar_ext_content_height_20074b78; /* RAM 0x20074b78 */
extern int32_t g2_calendar_ext_scroll_y_20074b7c;       /* RAM 0x20074b7c current (animated) y */
extern int32_t g2_calendar_ext_target_y_20074b80;       /* RAM 0x20074b80 */
extern uint32_t g2_calendar_state_20074b84;             /* RAM 0x20074b84, cleared on init */
extern uint32_t g2_calendar_tilelist_index_20074b8c;    /* RAM 0x20074b8c */
extern uint32_t g2_calendar_ext_active_20074b90;        /* RAM 0x20074b90 expanded page shown */
extern const uint8_t g2_calendar_icon_img_769f58[];     /* ROM 0x769f58 lv_image_dsc_t */
extern const uint8_t g2_calendar_location_img_769f3c[]; /* ROM 0x769f3c lv_image_dsc_t */
extern const uint8_t g2_calendar_time_img_769f74[];     /* ROM 0x769f74 lv_image_dsc_t */

extern void calendar_ext_page_create_4eef7c(void *parent);

extern void aeabi_memset_43c0e4(void *dst, uint32_t len, uint32_t value);
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                     /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                       /* 0x44981c */
extern uint32_t g2_log_module_length(const char *text);                           /* 0x44a43c strlen */
extern void *audio_uart_page_43de82(void *parent);                                /* lv_obj_create */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);                /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag);          /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);                 /* lv_obj_is_valid */
extern void audio_lv_object_position_43f09a(void *obj, int32_t x, int32_t y);     /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                         /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                         /* lv_obj_set_y */
extern void audio_lv_object_size_call_43f4c0(void *obj, int32_t w, int32_t h);    /* lv_obj_set_size */
extern void audio_lv_width_43f506(void *obj, int32_t width);                      /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);                    /* lv_obj_set_height */
extern void lv_obj_align_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y);  /* lv_obj_align */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                        /* lv_obj_get_height */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);                              /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t selector);      /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t selector);      /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t selector);      /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t selector);      /* pad_right */
extern void audio_uart_page_441246(void *obj, int32_t v, uint32_t selector);      /* pad_row */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t selector);      /* pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t selector); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t selector);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t selector); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t selector);      /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t selector);      /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t selector);      /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t selector);      /* shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t selector);      /* shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t selector);      /* shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t selector);      /* shadow_spread */
extern void audio_lv_style_color_44140e(void *obj, uint32_t color, uint32_t selector); /* text_color */
extern void audio_lv_style_alpha_44142e(void *obj, uint32_t opa, uint32_t selector);   /* text_opa */
extern void audio_lv_style_font_44143e(void *obj, const void *font, uint32_t selector); /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t selector);  /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t radius, uint32_t selector);  /* radius */
extern void audio_uart_page_44d878(void *obj);                                     /* lv_obj_clean */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                      /* scrollbar_mode */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *anim);                    /* lv_anim_init */
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *anim);            /* lv_anim_start */
extern uint32_t audio_uart_anim_delete_450500(void *var, void (*exec_cb)(void *, int32_t)); /* lv_anim_delete */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);                         /* anim path */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *anim, int32_t start, int32_t end); /* lv_anim_set_values */
extern uint32_t audio_uart_page_460084(const char *key);                           /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);        /* localized text */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);                 /* 0x464bb2 */
extern uint32_t UX_GetSystemBLEStatus(void);                                       /* 0x47d8ce */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);                      /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_lv_image_create_498668(void *parent);                           /* lv_image_create */
extern void audio_lv_image_source_498680(void *obj, const void *src);              /* lv_image_set_src */
extern void *audio_lv_label_create_499416(void *parent);                           /* lv_label_create */
extern void audio_lv_label_text_49942e(void *obj, const char *text);               /* lv_label_set_text */
extern void audio_lv_label_mode_499678(void *obj, uint32_t mode);                  /* lv_label_set_long_mode */
extern uint32_t audio_log_flags(void);                                             /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...);                                               /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);    /* 0x43ce9e */

void calendar_obj_set_style_pad_all_4ed7d8(void *obj, int32_t value, uint32_t selector);
void calendar_page_reset_4ed80a(void);
void calendar_ext_scroll_anim_completed_4ed81c(void *anim);
void calendar_ext_update_scrollbar_4ed824(int32_t scroll_y);
void calendar_ext_scroll_anim_exec_4ed868(void *obj, int32_t y);
void calendar_ext_scroll_by_4ed882(int32_t direction, int32_t speed, int32_t distance);
int32_t Calendar_Page_Reflash_4ed9b6(const void *data);
int32_t CalendarWidget_MainPage_init_4edac4(uint32_t tile_index);
void calendar_forward_ui_event_4eeadc(uint32_t code, const g2_lv_event_t *event);

static const char cal_module_tag[] = "dashborad.calendar"; /* ROM 0x7846f8 (sic) */
static const char cal_source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_calendar_page.c"; /* ROM 0x6ea7bc */
static const char fn_scroll_by[] = "calendar_ext_scroll_by"; /* ROM 0x77d114 */
static const char scroll_msg[] = "calendar_ext_scroll_by: from=%d to=%d, speed=%d, offset=%d"; /* ROM 0x71a6b0 */
static const char scroll_msg_short[] =
    "[dashborad.calendar]calendar_ext_scroll_by: from=%d to=%d, speed=%d, offset=%d"; /* ROM 0x6f0948 */
static const char fn_reflash[] = "Calendar_Page_Reflash"; /* ROM 0x77d12c */
static const char reflash_uninit[] = "widget_calendar_init_flag == 0, return"; /* ROM 0x7505cc */
static const char reflash_uninit_short[] = "[dashborad.calendar]widget_calendar_init_flag == 0, return"; /* ROM 0x71a6ec */
static const char key_disconnected_1[] = "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_1"; /* ROM 0x73a604 */
static const char key_disconnected_2[] = "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_2"; /* ROM 0x73a634 */
static const char key_no_event_1[] = "ID_DASHBOARD_CALENDAR_NO_EVENT_1"; /* ROM 0x75c210 */
static const char key_default_1[] = "ID_DASHBOARD_CALENDAR_DEFAULT_1"; /* ROM 0x7672f0 */
static const char key_default_2[] = "ID_DASHBOARD_CALENDAR_DEFAULT_2"; /* ROM 0x767310 */

#define CAL_LOG(level, code, line, fn, msg, ...)                                                     \
    do {                                                                                             \
        if (audio_log_flags() & 2u)                                                                  \
            audio_log_extended((level), cal_module_tag, cal_source_file, (fn), (line), msg,          \
                               ##__VA_ARGS__);                                                       \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                                    \
            (void)compress_log_output((code), msg##_short, msg##_short, ##__VA_ARGS__);              \
    } while (0)

/* Out-of-line lv_obj_set_style_pad_all (this TU's copy). */
void calendar_obj_set_style_pad_all_4ed7d8(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

void calendar_page_reset_4ed80a(void)
{
    aeabi_memset_43c0e4(&g2_dashboard_schedule_ui_2011df34, sizeof g2_dashboard_schedule_ui_2011df34, 0u);
}

void calendar_ext_scroll_anim_completed_4ed81c(void *anim)
{
    (void)anim;
    g2_calendar_scroll_anim_running_20074b20 = 0u;
}

/* Scrollbar thumb follows the content offset proportionally. */
void calendar_ext_update_scrollbar_4ed824(int32_t scroll_y)
{
    if (g2_calendar_ext_scrollbar_20074b74 == NULL)
        return;
    const int32_t range = g2_calendar_ext_content_height_20074b78 - EXT_VIEW_H;
    if (range < 1)
        return;

    const int32_t thumb_h = audio_uart_lv_obj_height_43fdda(g2_calendar_ext_scrollbar_20074b74);
    int32_t y = -(((EXT_VIEW_H - thumb_h) * scroll_y) / range);
    if (y < 0)
        y = 0;
    if (EXT_VIEW_H - thumb_h < y)
        y = EXT_VIEW_H - thumb_h;
    audio_uart_page_43f142(g2_calendar_ext_scrollbar_20074b74, y);
}

void calendar_ext_scroll_anim_exec_4ed868(void *obj, int32_t y)
{
    if (obj == NULL)
        return;
    audio_uart_page_43f142(obj, y);
    g2_calendar_ext_scroll_y_20074b7c = y;
    calendar_ext_update_scrollbar_4ed824(y);
}

/* Scroll the expanded page by `distance` pixels rounded up to whole 28 px
 * rows (doubled above speed 100); direction >= 1 scrolls down. */
void calendar_ext_scroll_by_4ed882(int32_t direction, int32_t speed, int32_t distance)
{
    if (g2_calendar_ext_content_20074b70 == NULL || g2_calendar_ext_content_height_20074b78 <= EXT_VIEW_H)
        return;

    const int32_t min_y =
        ((g2_calendar_ext_content_height_20074b78 - EXT_VIEW_H + SCROLL_STEP - 1) / SCROLL_STEP) * -SCROLL_STEP;
    const int32_t target = g2_calendar_ext_target_y_20074b80;
    int32_t new_y;

    if (direction >= 1) {
        if (speed > SCROLL_FAST_SPEED)
            distance <<= 1;
        new_y = ((target - ((distance + SCROLL_STEP - 1) / SCROLL_STEP) * SCROLL_STEP) / SCROLL_STEP) * SCROLL_STEP;
        if (new_y < min_y)
            new_y = min_y;
    } else {
        if (speed > SCROLL_FAST_SPEED)
            distance <<= 1;
        new_y = ((((distance + SCROLL_STEP - 1) / SCROLL_STEP) * SCROLL_STEP + target) / SCROLL_STEP) * SCROLL_STEP;
        if (new_y > 0)
            new_y = 0;
    }
    if (new_y == g2_calendar_ext_target_y_20074b80)
        return;
    g2_calendar_ext_target_y_20074b80 = new_y;

    g2_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = g2_calendar_ext_content_20074b70;
    anim.exec_cb = calendar_ext_scroll_anim_exec_4ed868;
    audio_uart_lv_anim_values_4506ce(&anim, g2_calendar_ext_scroll_y_20074b7c, new_y);
    anim.duration = SCROLL_ANIM_MS;
    anim.path_cb = audio_uart_lv_anim_path_450672;
    anim.completed_cb = calendar_ext_scroll_anim_completed_4ed81c;
    g2_calendar_scroll_anim_running_20074b20 = 1u;
    (void)audio_uart_lv_anim_start_450408(&anim);
    CAL_LOG(4u, 0x11000000u, 0xe7u, fn_scroll_by, scroll_msg, g2_calendar_ext_scroll_y_20074b7c, new_y, speed,
            distance);
}

int32_t Calendar_Page_Reflash_4ed9b6(const void *data)
{
    (void)data;
    if (g2_calendar_widget_init_flag_20074b1c == 0u) {
        CAL_LOG(2u, 0x08000000u, 0x104u, fn_reflash, reflash_uninit);
        return 0;
    }

    if (g2_dashboard_tiles[g2_calendar_tilelist_index_20074b8c].frame != NULL)
        audio_uart_page_44d878(g2_dashboard_tiles[g2_calendar_tilelist_index_20074b8c].frame);
    (void)CalendarWidget_MainPage_init_4edac4(g2_calendar_tilelist_index_20074b8c);

    if (g2_calendar_ext_active_20074b90 == 1u && g2_dashboard_focus_frame != NULL) {
        /* Stock condition is literally "!= NULL || lv_obj_is_valid()". */
        if (g2_calendar_ext_content_20074b70 != NULL ||
            audio_terminal_ui_object_valid_43e2ea(g2_calendar_ext_content_20074b70) != 0u)
            (void)audio_uart_anim_delete_450500(g2_calendar_ext_content_20074b70, calendar_ext_scroll_anim_exec_4ed868);
        g2_calendar_scroll_anim_running_20074b20 = 0u;
        g2_calendar_ext_scroll_y_20074b7c = 0;
        g2_calendar_ext_target_y_20074b80 = 0;
        audio_uart_page_44d878(g2_dashboard_focus_frame);
        calendar_ext_page_create_4eef7c(g2_dashboard_focus_frame);
    }
    return 0;
}

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* Transparent, borderless, padding-free frame shared by both layouts. */
static void *create_frame(void *parent)
{
    void *frame = audio_uart_page_43de82(parent);
    audio_lv_object_position_43f09a(frame, FRAME_X, FRAME_Y);
    audio_lv_width_43f506(frame, FRAME_W);
    audio_uart_page_43f568(frame, FRAME_H);
    audio_uart_page_44127e(frame, audio_lv_color_44104c(CAL_BLACK), 0u);
    audio_uart_page_44129e(frame, LV_OPA_TRANSP, 0u);
    audio_uart_page_44131c(frame, 0, 0u);
    audio_uart_page_44133a(frame, 0, 0u);
    audio_uart_page_441378(frame, 0, 0u);
    audio_uart_page_441386(frame, 0, 0u);
    audio_uart_page_4413b0(frame, 0, 0u);
    audio_uart_page_441394(frame, 0, 0u);
    audio_uart_page_4413a2(frame, 0, 0u);
    calendar_obj_set_style_pad_all_4ed7d8(frame, 0, 0u);
    audio_uart_page_44120e(frame, 0, 0u);
    audio_uart_page_44121c(frame, 0, 0u);
    audio_uart_page_44122a(frame, 0, 0u);
    audio_uart_page_441238(frame, 0, 0u);
    audio_uart_page_44146a(frame, 0, 0u);
    audio_uart_page_4412ec(frame, audio_lv_color_44104c(CAL_BLACK), 0u);
    audio_lv_style_color_44140e(frame, audio_lv_color_44104c(CAL_WHITE), 0u);
    audio_lv_style_alpha_44142e(frame, LV_OPA_COVER, 0u);
    return frame;
}

/* Content-sized transparent flex box, items centred. */
static void *create_flex_box(void *parent, uint32_t flow)
{
    void *box = audio_uart_page_43de82(parent);
    audio_lv_object_size_call_43f4c0(box, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(box, LV_OPA_TRANSP, 0u);
    audio_uart_page_44131c(box, 0, 0u);
    calendar_obj_set_style_pad_all_4ed7d8(box, 0, 0u);
    audio_uart_page_48ba78(box, flow);
    audio_uart_page_48ba92(box, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    return box;
}

/* Placeholder row [calendar icon][line1] inside `column`, optional line2 below. */
static void create_placeholder(void *column, const char *key1, const char *key2)
{
    void *row = create_flex_box(column, LV_FLEX_FLOW_ROW);
    audio_uart_page_441254(row, 8, 0u);

    void *icon = audio_lv_image_create_498668(row);
    audio_lv_image_source_498680(icon, g2_calendar_icon_img_769f58);
    audio_lv_width_43f506(icon, ICON_SIZE);
    audio_uart_page_43f568(icon, ICON_SIZE);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

    void *label = audio_lv_label_create_499416(row);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(CAL_WHITE), 0u);
    audio_lv_label_text_49942e(label, localized(key1));
    audio_lv_style_font_44143e(label, audio_uart_ring_primary_head_cell, 0u);

    if (key2 == NULL)
        return;
    label = audio_lv_label_create_499416(column);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(CAL_WHITE), 0u);
    audio_lv_label_text_49942e(label, localized(key2));
    audio_lv_style_font_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44145a(label, LV_TEXT_ALIGN_CENTER, 0u);
}

static void *create_icon(void *frame, const void *src, int32_t y)
{
    void *icon = audio_lv_image_create_498668(frame);
    audio_lv_image_source_498680(icon, src);
    audio_lv_width_43f506(icon, ICON_SIZE);
    audio_uart_page_43f568(icon, ICON_SIZE);
    audio_uart_page_43f0e0(icon, 0);
    audio_uart_page_43f142(icon, y);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
    return icon;
}

/* Label with dots overflow; the text is read under the dashboard mutex.
 * Callers set colour and font afterwards (order varies in the stock code). */
static void *create_text(void *frame, int32_t width, int32_t x, int32_t y, const char *text)
{
    void *label = audio_lv_label_create_499416(frame);
    audio_lv_width_43f506(label, width);
    audio_uart_page_43f568(label, LABEL_H);
    audio_uart_page_43f0e0(label, x);
    audio_uart_page_43f142(label, y);
    audio_lv_label_mode_499678(label, LV_LABEL_LONG_DOT);
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    audio_lv_label_text_49942e(label, text);
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    return label;
}

static void color_then_font(void *label)
{
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(CAL_WHITE), 0u);
    audio_lv_style_font_44143e(label, audio_uart_ring_primary_head_cell, 0u);
}

static void font_then_color(void *label)
{
    audio_lv_style_font_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(CAL_WHITE), 0u);
}

static int32_t has_location(const g2_schedule_record_t *event)
{
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    const int32_t length = (int32_t)g2_log_module_length(event->location);
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    return length >= 1;
}

/* Events 2 and 3: title at y+0x32, then location / time rows 0x20 apart.
 * Returns the y the next event is placed from. */
static int32_t create_following_event(void *frame, uint32_t index, int32_t y)
{
    g2_calendar_event_widgets_t *const w = &g2_calendar_event_widgets_20074b24[index];
    const g2_schedule_record_t *const event = &g2_dashboard_schedule_ui_2011df34.event[index];

    w->title_icon = create_icon(frame, g2_calendar_icon_img_769f58, y + 0x34);
    w->title_label = create_text(frame, TITLE_W, 32, y + 0x32, event->title);
    color_then_font(w->title_label);
    if (!has_location(event)) {
        w->time_icon = create_icon(frame, g2_calendar_time_img_769f74, y + 0x54);
        w->time_label = create_text(frame, TIME_W, 28, y + 0x52, event->time);
        color_then_font(w->time_label);
        return y + 0x54;
    }
    w->location_icon = create_icon(frame, g2_calendar_location_img_769f3c, y + 0x54);
    w->location_label = create_text(frame, LOCATION_W, 32, y + 0x52, event->location);
    color_then_font(w->location_label);
    w->time_icon = create_icon(frame, g2_calendar_time_img_769f74, y + 0x74);
    w->time_label = create_text(frame, TIME_W, 28, y + 0x72, event->time);
    color_then_font(w->time_label);
    return y + 0x74;
}

/* Builds the non-expanded calendar widget inside dashboard tile tile_index. */
int32_t CalendarWidget_MainPage_init_4edac4(uint32_t tile_index)
{
    g2_schedule_ui_t *const data = &g2_dashboard_schedule_ui_2011df34;

    g2_calendar_tilelist_index_20074b8c = tile_index;
    g2_calendar_state_20074b84 = 0u;
    g2_calendar_widget_init_flag_20074b1c = 1u;

    if (data->count == 0u) {
        void *const frame = create_frame(g2_dashboard_tiles[g2_calendar_tilelist_index_20074b8c].frame);
        void *const column = create_flex_box(frame, LV_FLEX_FLOW_COLUMN);
        audio_uart_page_441246(column, 8, 0u);
        lv_obj_align_43f6b8(column, LV_ALIGN_CENTER, 0, 0);
        if (UX_GetSystemBLEStatus() == 0u)
            create_placeholder(column, key_disconnected_1, key_disconnected_2);
        else if (data->authority == 1u)
            create_placeholder(column, key_no_event_1, NULL);
        else
            create_placeholder(column, key_default_1, key_default_2);
        return 0;
    }

    void *const frame = create_frame(g2_dashboard_tiles[g2_calendar_tilelist_index_20074b8c].frame);
    audio_lv_object_clear_flag_43dfa4(frame, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e368(frame, LV_SCROLLBAR_MODE_OFF);

    /* First event: title at y 0, location / time rows 0x1c apart. */
    g2_calendar_event_widgets_t *const w = &g2_calendar_event_widgets_20074b24[0];
    w->title_icon = create_icon(frame, g2_calendar_icon_img_769f58, 2);
    w->title_label = create_text(frame, TITLE_W, 32, 0, data->event[0].title);
    color_then_font(w->title_label);

    int32_t y;
    if (!has_location(&data->event[0])) {
        w->time_icon = create_icon(frame, g2_calendar_time_img_769f74, 0x22);
        w->time_label = create_text(frame, TIME_W, 32, 0x20, data->event[0].time);
        font_then_color(w->time_label);
        y = 0x20;
    } else {
        w->location_icon = create_icon(frame, g2_calendar_location_img_769f3c, 0x22);
        w->location_label = create_text(frame, LOCATION_W, 32, 0x20, data->event[0].location);
        color_then_font(w->location_label);
        w->time_icon = create_icon(frame, g2_calendar_time_img_769f74, 0x3e);
        w->time_label = create_text(frame, TIME_W, 32, 0x3c, data->event[0].time);
        font_then_color(w->time_label);
        y = 0x3e;
    }

    if (data->count == 1u)
        return 0;
    y = create_following_event(frame, 1u, y);
    if (data->count == 2u)
        return 0;
    (void)create_following_event(frame, 2u, y);
    return 0;
}

/* Sends {0, code, x lo, x hi, y lo, y hi} to the dashboard app; codes 0x44 and
 * 0x45 carry the lv_point_t event parameter, the others zeros. */
void calendar_forward_ui_event_4eeadc(uint32_t code, const g2_lv_event_t *event)
{
    uint8_t msg[6];

    if (code == LV_EVENT_CLICKED || code == CAL_EVENT_0x48 || code == CAL_EVENT_0x49) {
        msg[0] = 0u;
        msg[1] = (uint8_t)code;
        msg[2] = 0u;
        msg[3] = 0u;
        msg[4] = 0u;
        msg[5] = 0u;
        (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, sizeof msg, 0u);
    } else if (code == CAL_EVENT_0x45 || code == CAL_EVENT_0x44) {
        const g2_lv_point_t *const point = (const g2_lv_point_t *)event->param;
        msg[0] = 0u;
        msg[1] = (uint8_t)code;
        msg[2] = (uint8_t)point->x;
        msg[3] = (uint8_t)(point->x >> 8);
        msg[4] = (uint8_t)point->y;
        msg[5] = (uint8_t)(point->y >> 8);
        (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, sizeof msg, 0u);
    }
}
