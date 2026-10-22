/* Dashboard calendar extension widget (expanded page) and expiry service, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_calendar_page.c.
 * Native 0x4eebdc..0x4eef37, 0x4eef7c..0x4ef987, 0x4ef9a4..0x4efa4f,
 * 0x4efa78..0x4efc95, 0x4efcb8..0x4efeab, 0x4efeb0..0x4efee7; literal pools
 * 0x4eef38..0x4eef7b, 0x4ef988..0x4ef9a3, 0x4efa50..0x4efa77, 0x4efc98..0x4efcb7,
 * 0x4efeec..0x4eff93. The first half of this TU (0x4ed7d8..0x4eebdb: pad_all
 * copy, scroll animation, Calendar_Page_Reflash, tile page) is reconstructed
 * separately.
 *
 * Calendar UI data (RAM 0x2011df34, 0x1088 bytes) is a u16 event count at +0
 * followed by up to eight 0x210-byte records: title +0x000 (0xb0), location
 * +0x0b0 (0x11b), time text +0x1cb (0x40), end timestamp +0x20c (u32 epoch).
 * Each displayed event owns six LVGL objects (icon/label pairs for title,
 * location or time, time) in the table at RAM 0x2011efbc. */
#include <stdint.h>
#include <stddef.h>

#define CAL_EVENT_MAX 8
#define CAL_EVENT_SIZE 0x210u
#define CAL_UI_SIZE 0x1088u

#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PART_MAIN 0u
#define LV_PART_SCROLLBAR 0x10000u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_TOP_MID 2u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_LABEL_LONG_DOT 1u
#define LV_FLEX_FLOW_ROW 0u
#define LV_FLEX_FLOW_COLUMN 1u
#define LV_FLEX_ALIGN_CENTER 2u
#define LV_DIR_VER 0xcu
#define LV_SCROLLBAR_MODE_AUTO 3u
#define COLOR_WHITE 0xffffffu
#define COLOR_SCROLLBAR 0x555555u
#define WAIT_FOREVER 0xffffffffu

/* Input event ids delivered in type-0 frames. */
#define KEY_SINGLE_TAP 0x0au
#define KEY_SCROLL_DOWN 0x44u
#define KEY_SCROLL_UP 0x45u
#define KEY_46 0x46u
#define KEY_REFRESH 0x47u
#define KEY_DOUBLE_TAP 0x48u

typedef struct {
    char title[0xb0];       /* +0x000 */
    char location[0x11b];   /* +0x0b0 */
    char time_text[0x40];   /* +0x1cb */
    uint8_t pad_20b;        /* +0x20b */
    uint32_t end_timestamp; /* +0x20c */
} g2_calendar_event_t;
_Static_assert(sizeof(g2_calendar_event_t) == CAL_EVENT_SIZE, "calendar record");

typedef struct {
    uint16_t count;                              /* +0x0000 */
    uint16_t pad_02;                             /* +0x0002 */
    g2_calendar_event_t events[CAL_EVENT_MAX];   /* +0x0004 */
    uint8_t tail[4];                             /* +0x1084 */
} g2_calendar_ui_t;
_Static_assert(sizeof(g2_calendar_ui_t) == CAL_UI_SIZE, "calendar UI copy");

/* Per-event object row (0x18 bytes). Without a location only [0..3] are used:
 * [2]/[3] hold the time icon/label. */
typedef struct {
    void *title_icon;   /* +0x00 */
    void *title_label;  /* +0x04 */
    void *line2_icon;   /* +0x08 location or time */
    void *line2_label;  /* +0x0c */
    void *time_icon;    /* +0x10 */
    void *time_label;   /* +0x14 */
} g2_calendar_item_objs_t;
_Static_assert(sizeof(g2_calendar_item_objs_t) == 0x18u, "calendar item row");

/* lv_anim_t is only touched through lv_anim_delete here. */

extern uint8_t g2_dashboard_schedule_ui_2011df34[];         /* RAM 0x2011df34, g2_calendar_ui_t */
extern volatile uint32_t g2_dashboard_schedule_authority_2011efb8; /* RAM 0x2011efb8 */
extern void *g2_dashboard_mutex_200743a8;                  /* RAM 0x200743a8 osMutexId */
extern uint32_t audio_uart_ring_primary_head_cell;         /* RAM 0x200746dc: active lv_font_t * */
extern uint32_t g2_calendar_ext_active_20074b90;        /* RAM 0x20074b90 */
extern void *g2_calendar_ext_content_20074b70;             /* RAM 0x20074b70 scrolling column */
extern uint32_t g2_calendar_scroll_anim_running_20074b20;     /* RAM 0x20074b20 */
extern void *g2_dashboard_focus_frame;             /* RAM 0x20074b9c expanded-page parent */
extern void *g2_calendar_ext_fifo_20074b88;                /* RAM 0x20074b88 */
extern uint32_t g2_calendar_tilelist_index_20074b8c;          /* RAM 0x20074b8c */
extern int32_t g2_calendar_ext_scroll_y_20074b7c;        /* RAM 0x20074b7c */
extern int32_t g2_calendar_ext_target_y_20074b80;     /* RAM 0x20074b80 */
extern void *g2_calendar_ext_root_20074b6c;                /* RAM 0x20074b6c */
extern void *g2_calendar_ext_scrollbar_20074b74;           /* RAM 0x20074b74 */
extern int32_t g2_calendar_ext_content_height_20074b78;         /* RAM 0x20074b78 */
extern g2_calendar_item_objs_t g2_calendar_ext_items_2011efbc[CAL_EVENT_MAX]; /* RAM 0x2011efbc */
extern uint32_t g2_calendar_state_20074b84;          /* RAM 0x20074b84 */
extern uint32_t g2_calendar_widget_init_flag_20074b1c;     /* RAM 0x20074b1c */
extern uint8_t g2_calendar_expire_scratch_2011f0ac[CAL_UI_SIZE]; /* RAM 0x2011f0ac */

extern const uint8_t g2_calendar_icon_img_769f58[];   /* ROM 0x769f58 lv_image_dsc_t */
extern const uint8_t g2_calendar_time_img_769f74[];     /* ROM 0x769f74 lv_image_dsc_t */
extern const uint8_t g2_calendar_location_img_769f3c[]; /* ROM 0x769f3c lv_image_dsc_t */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);   /* memset 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t g2_log_module_length(const char *text);         /* strlen 0x44a43c */
extern void *audio_uart_page_43de82(void *parent);              /* lv_obj_create */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);       /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag); /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);        /* lv_obj_is_valid */
extern void audio_lv_object_position_43f09a(void *obj, int32_t x, int32_t y); /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);       /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);       /* lv_obj_set_y */
extern void audio_lv_object_size_call_43f4c0(void *obj, int32_t w, int32_t h); /* lv_obj_set_size */
extern void audio_lv_width_43f506(void *obj, int32_t w);        /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);       /* lv_obj_set_height */
extern void lv_obj_align_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y);
extern uint32_t audio_lv_color_44104c(uint32_t rgb);            /* lv_color_hex */
extern void audio_uart_page_441246(void *obj, int32_t v, uint32_t sel);  /* style pad_row */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);  /* style pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t c, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel); /* style bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);  /* style border_width */
extern void audio_lv_style_color_44140e(void *obj, uint32_t c, uint32_t sel); /* style text_color */
extern void audio_lv_style_font_44143e(void *obj, uint32_t font, uint32_t sel); /* style text_font */
extern void audio_lv_style_a_44145a(void *obj, uint32_t v, uint32_t sel); /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* style radius */
extern void style_prop_2d_441478(void *obj, uint32_t v, uint32_t sel);   /* style clip_corner */
extern void audio_lv_delete_44d7b8(void *obj);                  /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                  /* lv_obj_clean */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);   /* lv_obj_get_child */
extern int32_t audio_uart_lv_child_count_44ddea(void *obj);     /* lv_obj_get_child_count */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);   /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);    /* lv_obj_set_scroll_dir */
extern uint32_t audio_uart_anim_delete_450500(void *var, void (*exec_cb)(void *, int32_t)); /* lv_anim_delete */
extern uint32_t audio_uart_page_460084(const char *key);        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);   /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_lv_image_create_498668(void *parent);        /* lv_image_create */
extern void audio_lv_image_source_498680(void *img, const void *src); /* lv_image_set_src */
extern void *audio_lv_label_create_499416(void *parent);        /* lv_label_create */
extern void audio_lv_label_text_49942e(void *label, const char *text); /* lv_label_set_text */
extern void audio_lv_label_mode_499678(void *label, uint32_t mode); /* lv_label_set_long_mode */
extern uint32_t UX_GetSystemBLEStatus(void);                    /* 0x47d8ce */
extern uint32_t service_time_rtc_refresh(void);                 /* 0x44a1ea, epoch seconds */
extern uint32_t audio_uart_service_mode(void);                  /* 0x45a570, 1 = master */
extern void audio_uart_master_display_refresh(uint32_t app, const void *payload,
                                              uint16_t length, uint32_t extra); /* 0x464bb2 */
extern void *ui_common_api_fn_00509c1c(void);                   /* fifo create */
extern void ui_common_api_fn_00509c96(void *fifo);              /* fifo destroy */
extern uint32_t audio_log_flags(void);                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Same TU, reconstructed separately. */
extern void calendar_obj_set_style_pad_all_4ed7d8(void *obj, int32_t v, uint32_t sel);
extern void calendar_ext_scroll_anim_exec_4ed868(void *obj, int32_t y);
extern void calendar_ext_scroll_by_4ed882(int32_t direction, uint32_t speed, uint32_t offset);
extern void Calendar_Page_Reflash_4ed9b6(const uint8_t *data, uint32_t len);
/* ui_DashBaord_Main_Screen.c */
extern void dashboard_status_data_apply_4e8970(const uint8_t *data, uint32_t len);
extern void dashboard_focus_frame_shrink_anim_4e92f4(void);
/* page_state_sync.c */
extern void page_state_sync_dashboard_main_5000cc(uint32_t tile, uint8_t widget);
extern void page_state_sync_calendar_expanded_500180(uint32_t page);

int32_t calendar_extWidget_ReflashEvent_handler_4eebdc(const uint8_t *data, uint32_t len);
void calendar_ext_page_create_4eef7c(void *parent);
int32_t Calendar_ext_Widget_init_4ef9a4(void *parent);
void Calendar_expire_check_4efa78(void);
void Calendar_expire_update_4efcb8(uint32_t mask_value);
void calendar_widget_deinit_4efeb0(void);

static const char module_tag[] = "dashborad.calendar"; /* ROM 0x7846f8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_calendar_page.c"; /* ROM 0x6ea7bc */
static const char fn_handler[] = "calendar_extWidget_ReflashEvent_handler"; /* ROM 0x7505f4 */
static const char not_init[] = "calendar_ext_widget_init_flag == 0, return"; /* ROM 0x745ccc */
static const char not_init_short[] = "[dashborad.calendar]calendar_ext_widget_init_flag == 0, return"; /* ROM 0x710be4 */
static const char len_zero[] = "len == 0, return"; /* ROM 0x78470c */
static const char len_zero_short[] = "[dashborad.calendar]len == 0, return"; /* ROM 0x75061c */
static const char no_content[] = "calendar_content == NULL, return"; /* ROM 0x75c234 */
static const char no_content_short[] = "[dashborad.calendar]calendar_content == NULL, return"; /* ROM 0x7250d0 */
static const char unknown_event[] = "CalendarWidget_event_handler: unknown event type: %d"; /* ROM 0x725108 */
static const char unknown_event_short[] =
    "[dashborad.calendar]CalendarWidget_event_handler: unknown event type: %d"; /* ROM 0x6f702c */
static const char id_ble_1[] = "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_1"; /* ROM 0x73a604 */
static const char id_ble_2[] = "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_2"; /* ROM 0x73a634 */
static const char id_no_event_1[] = "ID_DASHBOARD_CALENDAR_NO_EVENT_1"; /* ROM 0x75c210 */
static const char id_default_1[] = "ID_DASHBOARD_CALENDAR_DEFAULT_1"; /* ROM 0x7672f0 */
static const char id_default_2[] = "ID_DASHBOARD_CALENDAR_DEFAULT_2"; /* ROM 0x767310 */
static const char fn_init[] = "Calendar_ext_Widget_init"; /* ROM 0x773d80 */
static const char fifo_failed[] = "calendar_ext_fifo create failed"; /* ROM 0x767330 */
static const char fifo_failed_short[] = "[dashborad.calendar]calendar_ext_fifo create failed"; /* ROM 0x72fab4 */
static const char fn_check[] = "Calendar_expire_check"; /* ROM 0x77d144 */
static const char check_begin[] = "Calendar_expire_check: check calendar expire"; /* ROM 0x73a664 */
static const char check_begin_short[] =
    "[dashborad.calendar]Calendar_expire_check: check calendar expire"; /* ROM 0x707938 */
static const char check_now[] = "current_timestamp = %d"; /* ROM 0x77d15c */
static const char check_now_short[] = "[dashborad.calendar]current_timestamp = %d"; /* ROM 0x745cf8 */
static const char check_expired[] =
    "Calendar_expire_check: calendar %d is expired, current_timestamp = %d, end_timestamp = %d"; /* ROM 0x6e1cd0 */
static const char check_expired_short[] =
    "[dashborad.calendar]Calendar_expire_check: calendar %d is expired, current_timestamp = %d, end_timestamp = %d"; /* ROM 0x6d7820 */
static const char check_mask[] = "Calendar_expire_check: calendar expire mask = %d"; /* ROM 0x72fae8 */
static const char check_mask_short[] =
    "[dashborad.calendar]Calendar_expire_check: calendar expire mask = %d"; /* ROM 0x6fe81c */
static const char check_send[] = "Calendar_expire_check: send calendar expire event to dashboard"; /* ROM 0x710c24 */
static const char check_send_short[] =
    "[dashborad.calendar]Calendar_expire_check: send calendar expire event to dashboard"; /* ROM 0x6ea810 */
static const char fn_update[] = "Calendar_expire_update"; /* ROM 0x77d174 */
static const char widget_not_init[] = "widget_calendar_init_flag == 0, return"; /* ROM 0x7505cc */
static const char widget_not_init_short[] =
    "[dashborad.calendar]widget_calendar_init_flag == 0, return"; /* ROM 0x71a6ec */
static const char update_value[] = "Calendar_expire_update: mask_value = %d"; /* ROM 0x750644 */
static const char update_value_short[] = "[dashborad.calendar]Calendar_expire_update: mask_value = %d"; /* ROM 0x71a728 */
static const char update_mask[] = "Calendar_expire_update: calendar expire mask = %d"; /* ROM 0x72fb1c */
static const char update_mask_short[] =
    "[dashborad.calendar]Calendar_expire_update: calendar expire mask = %d"; /* ROM 0x6fe864 */
static const char update_send[] = "Calendar_expire_update: send calendar expire event to dashboard"; /* ROM 0x710c64 */
static const char update_send_short[] =
    "[dashborad.calendar]Calendar_expire_update: send calendar expire event to dashboard"; /* ROM 0x6ea864 */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. */
#define CAL_LOG(level, fn, line, cflags, msg, msg_short, ...)                                       \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

#define CAL_UI ((g2_calendar_ui_t *)(void *)g2_dashboard_schedule_ui_2011df34)
#define FONT() (audio_uart_ring_primary_head_cell)

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* Leave the expanded calendar page and return to the dashboard main page. */
static void calendar_ext_exit(void)
{
    if (g2_calendar_ext_content_20074b70 != NULL ||
        audio_terminal_ui_object_valid_43e2ea(g2_calendar_ext_content_20074b70) != 0u)
        (void)audio_uart_anim_delete_450500(g2_calendar_ext_content_20074b70,
                                            calendar_ext_scroll_anim_exec_4ed868);
    g2_calendar_scroll_anim_running_20074b20 = 0;
    for (int32_t i = audio_uart_lv_child_count_44ddea(g2_dashboard_focus_frame) - 1; i >= 0; i--) {
        void *child = audio_uart_lv_child_get_44dce2(g2_dashboard_focus_frame, i);
        if (child != NULL)
            audio_lv_delete_44d7b8(child);
    }
    if (g2_calendar_ext_fifo_20074b88 != NULL) {
        ui_common_api_fn_00509c96(g2_calendar_ext_fifo_20074b88);
        g2_calendar_ext_fifo_20074b88 = NULL;
    }
    g2_calendar_ext_active_20074b90 = 0;
    dashboard_focus_frame_shrink_anim_4e92f4();
    page_state_sync_dashboard_main_5000cc(g2_calendar_tilelist_index_20074b8c, 3u);
}

/* Frames: [0] type. Type 0 = input event {0, key, value u32 LE}; type 1 =
 * dashboard main data; type 2 = calendar page data; type 3 ignored. */
int32_t calendar_extWidget_ReflashEvent_handler_4eebdc(const uint8_t *data, uint32_t len)
{
    if (g2_calendar_ext_active_20074b90 == 0) {
        CAL_LOG(2u, fn_handler, 0x34au, 0x08000000u, not_init, not_init_short);
        return 0;
    }
    if (len == 0u) {
        CAL_LOG(2u, fn_handler, 0x34eu, 0x08000000u, len_zero, len_zero_short);
        return 0;
    }
    switch (data[0]) {
    case 0: {
        uint8_t key = data[1];
        uint32_t value = (uint32_t)data[2] | ((uint32_t)data[3] << 8) | ((uint32_t)data[4] << 16) |
                         ((uint32_t)data[5] << 24);
        if (key == KEY_SINGLE_TAP) {
            calendar_ext_exit();
        } else if (key == KEY_SCROLL_DOWN || key == KEY_SCROLL_UP) {
            if (g2_calendar_ext_content_20074b70 == NULL ||
                audio_terminal_ui_object_valid_43e2ea(g2_calendar_ext_content_20074b70) == 0u) {
                CAL_LOG(2u, fn_handler, 0x35bu, 0x08000000u, no_content, no_content_short);
                return 0;
            }
            calendar_ext_scroll_by_4ed882(key == KEY_SCROLL_DOWN ? 1 : -1, value >> 16, value & 0xffffu);
        } else if (key == KEY_46) {
            /* ignored */
        } else if (key == KEY_REFRESH) {
            if (g2_calendar_ext_content_20074b70 == NULL ||
                audio_terminal_ui_object_valid_43e2ea(g2_calendar_ext_content_20074b70) == 0u) {
                CAL_LOG(2u, fn_handler, 0x3a0u, 0x08000000u, no_content, no_content_short);
                return 0;
            }
            (void)audio_uart_anim_delete_450500(g2_calendar_ext_content_20074b70,
                                                calendar_ext_scroll_anim_exec_4ed868);
            g2_calendar_scroll_anim_running_20074b20 = 0;
            g2_calendar_ext_scroll_y_20074b7c = 0;
            g2_calendar_ext_target_y_20074b80 = 0;
            if (g2_calendar_ext_active_20074b90 == 1 && g2_dashboard_focus_frame != NULL) {
                audio_uart_page_44d878(g2_dashboard_focus_frame);
                calendar_ext_page_create_4eef7c(g2_dashboard_focus_frame);
            }
        } else if (key == KEY_DOUBLE_TAP) {
            calendar_ext_exit();
        } else {
            CAL_LOG(2u, fn_handler, 0x3b0u, 0x08400000u, unknown_event, unknown_event_short, key);
        }
        break;
    }
    case 2:
        Calendar_Page_Reflash_4ed9b6(data + 1, len - 1u);
        break;
    case 1:
        dashboard_status_data_apply_4e8970(data + 1, len - 1u);
        break;
    case 3:
    default:
        break;
    }
    return 0;
}

/* Label in a flex row/column with the white text style and active font. */
static void *status_icon_row(void *parent)
{
    void *row = audio_uart_page_43de82(parent);
    audio_lv_object_size_call_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(row, 0, LV_PART_MAIN);
    calendar_obj_set_style_pad_all_4ed7d8(row, 0, LV_PART_MAIN);
    audio_uart_page_48ba78(row, LV_FLEX_FLOW_ROW);
    audio_uart_page_48ba92(row, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    audio_uart_page_441254(row, 8, LV_PART_MAIN);
    void *icon = audio_lv_image_create_498668(row);
    audio_lv_image_source_498680(icon, g2_calendar_icon_img_769f58);
    audio_lv_width_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
    return row;
}

/* Two-line placeholder (icon + line 1, then centred line 2) under `column`. */
static void status_two_lines(void *column, const char *key1, const char *key2)
{
    void *row = status_icon_row(column);
    void *label = audio_lv_label_create_499416(row);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_label_text_49942e(label, localized(key1));
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    label = audio_lv_label_create_499416(column);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_label_text_49942e(label, localized(key2));
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    audio_lv_style_a_44145a(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
}

static void *item_icon(void *parent, const void *src, int32_t y)
{
    void *icon = audio_lv_image_create_498668(parent);
    audio_lv_image_source_498680(icon, src);
    audio_lv_width_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_uart_page_43f0e0(icon, 0x14);
    audio_uart_page_43f142(icon, y);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
    return icon;
}

static void *item_label(void *parent, int32_t y)
{
    void *label = audio_lv_label_create_499416(parent);
    audio_lv_width_43f506(label, 0x1fb);
    audio_uart_page_43f568(label, 0x1c);
    audio_uart_page_43f0e0(label, 0x34);
    audio_uart_page_43f142(label, y);
    audio_lv_label_mode_499678(label, LV_LABEL_LONG_DOT);
    return label;
}

/* Builds the expanded calendar page under `parent`: either a placeholder
 * (BLE disconnected / no events / default) or the scrolling event list with a
 * proportional scrollbar when the content is taller than 256 px. */
void calendar_ext_page_create_4eef7c(void *parent)
{
    if (CAL_UI->count == 0u) {
        void *box = audio_uart_page_43de82(parent);
        audio_lv_object_size_call_43f4c0(box, 0x21b, 0x100);
        audio_lv_object_position_43f09a(box, 0x14, 0x10);
        audio_uart_page_44e3ca(box, LV_DIR_VER);
        audio_uart_page_44e368(box, LV_SCROLLBAR_MODE_AUTO);
        calendar_obj_set_style_pad_all_4ed7d8(box, 0, LV_PART_MAIN);
        audio_uart_page_44131c(box, 0, LV_PART_MAIN);
        audio_uart_page_44129e(box, 0u, LV_PART_MAIN);
        audio_uart_page_44127e(box, audio_lv_color_44104c(COLOR_WHITE), LV_PART_SCROLLBAR);
        audio_uart_page_44129e(box, 200u, LV_PART_SCROLLBAR);

        void *column = audio_uart_page_43de82(box);
        audio_lv_object_size_call_43f4c0(column, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        audio_uart_page_44129e(column, 0u, LV_PART_MAIN);
        audio_uart_page_44131c(column, 0, LV_PART_MAIN);
        calendar_obj_set_style_pad_all_4ed7d8(column, 0, LV_PART_MAIN);
        audio_uart_page_48ba78(column, LV_FLEX_FLOW_COLUMN);
        audio_uart_page_48ba92(column, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
        audio_uart_page_441246(column, 8, LV_PART_MAIN);
        lv_obj_align_43f6b8(column, LV_ALIGN_TOP_MID, 0, 0x62);

        if (UX_GetSystemBLEStatus() == 0u) {
            status_two_lines(column, id_ble_1, id_ble_2);
        } else if (g2_dashboard_schedule_authority_2011efb8 == 1u) {
            void *row = status_icon_row(column);
            void *label = audio_lv_label_create_499416(row);
            audio_lv_label_text_49942e(label, localized(id_no_event_1));
            audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
            audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
        } else {
            status_two_lines(column, id_default_1, id_default_2);
        }
        g2_calendar_ext_root_20074b6c = NULL;
        g2_calendar_ext_content_20074b70 = NULL;
        g2_calendar_ext_scrollbar_20074b74 = NULL;
        g2_calendar_ext_content_height_20074b78 = 0;
        g2_calendar_ext_scroll_y_20074b7c = 0;
        g2_calendar_ext_target_y_20074b80 = 0;
        return;
    }

    g2_calendar_ext_root_20074b6c = audio_uart_page_43de82(parent);
    audio_lv_object_size_call_43f4c0(g2_calendar_ext_root_20074b6c, 0x240, 0x100);
    audio_lv_object_position_43f09a(g2_calendar_ext_root_20074b6c, 0, 0x10);
    calendar_obj_set_style_pad_all_4ed7d8(g2_calendar_ext_root_20074b6c, 0, LV_PART_MAIN);
    audio_uart_page_44131c(g2_calendar_ext_root_20074b6c, 0, LV_PART_MAIN);
    audio_uart_page_44129e(g2_calendar_ext_root_20074b6c, 0u, LV_PART_MAIN);
    audio_uart_page_44146a(g2_calendar_ext_root_20074b6c, 0, LV_PART_MAIN);
    style_prop_2d_441478(g2_calendar_ext_root_20074b6c, 1u, LV_PART_MAIN);
    audio_lv_object_clear_flag_43dfa4(g2_calendar_ext_root_20074b6c, LV_OBJ_FLAG_SCROLLABLE);

    g2_calendar_ext_content_20074b70 = audio_uart_page_43de82(g2_calendar_ext_root_20074b6c);
    audio_lv_width_43f506(g2_calendar_ext_content_20074b70, 0x240);
    audio_lv_object_position_43f09a(g2_calendar_ext_content_20074b70, 0, 0);
    calendar_obj_set_style_pad_all_4ed7d8(g2_calendar_ext_content_20074b70, 0, LV_PART_MAIN);
    audio_uart_page_44131c(g2_calendar_ext_content_20074b70, 0, LV_PART_MAIN);
    audio_uart_page_44129e(g2_calendar_ext_content_20074b70, 0u, LV_PART_MAIN);
    audio_uart_page_44146a(g2_calendar_ext_content_20074b70, 0, LV_PART_MAIN);
    audio_lv_object_clear_flag_43dfa4(g2_calendar_ext_content_20074b70, LV_OBJ_FLAG_SCROLLABLE);
    g2_calendar_ext_scroll_y_20074b7c = 0;
    g2_calendar_ext_target_y_20074b80 = 0;

    int32_t y = 0;
    for (int32_t i = 0; i < (int32_t)CAL_UI->count; i++) {
        g2_calendar_item_objs_t *objs = &g2_calendar_ext_items_2011efbc[i];
        g2_calendar_event_t *ev = &CAL_UI->events[i];
        objs->title_icon = item_icon(g2_calendar_ext_content_20074b70, g2_calendar_icon_img_769f58, y + 2);
        objs->title_label = item_label(g2_calendar_ext_content_20074b70, y);
        audio_lv_label_text_49942e(objs->title_label, ev->title);
        audio_lv_style_color_44140e(objs->title_label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
        audio_lv_style_font_44143e(objs->title_label, FONT(), LV_PART_MAIN);

        (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
        int32_t location_len = (int32_t)g2_log_module_length(ev->location);
        (void)osMutexRelease(g2_dashboard_mutex_200743a8);

        if (location_len < 1) {
            objs->line2_icon = item_icon(g2_calendar_ext_content_20074b70, g2_calendar_time_img_769f74, y + 0x22);
            objs->line2_label = item_label(g2_calendar_ext_content_20074b70, y + 0x20);
            audio_lv_label_text_49942e(objs->line2_label, ev->time_text);
            audio_lv_style_font_44143e(objs->line2_label, FONT(), LV_PART_MAIN);
            audio_lv_style_color_44140e(objs->line2_label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
            y += 0x54;
        } else {
            objs->line2_icon = item_icon(g2_calendar_ext_content_20074b70, g2_calendar_location_img_769f3c, y + 0x22);
            objs->line2_label = item_label(g2_calendar_ext_content_20074b70, y + 0x20);
            audio_lv_label_text_49942e(objs->line2_label, ev->location);
            audio_lv_style_color_44140e(objs->line2_label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
            audio_lv_style_font_44143e(objs->line2_label, FONT(), LV_PART_MAIN);
            objs->time_icon = item_icon(g2_calendar_ext_content_20074b70, g2_calendar_time_img_769f74, y + 0x3e);
            objs->time_label = item_label(g2_calendar_ext_content_20074b70, y + 0x3c);
            audio_lv_label_text_49942e(objs->time_label, ev->time_text);
            audio_lv_style_font_44143e(objs->time_label, FONT(), LV_PART_MAIN);
            audio_lv_style_color_44140e(objs->time_label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
            y += 0x70;
        }
    }
    audio_uart_page_43f568(g2_calendar_ext_content_20074b70, y);
    g2_calendar_ext_content_height_20074b78 = y;
    g2_calendar_ext_scrollbar_20074b74 = NULL;
    if (g2_calendar_ext_content_height_20074b78 > 0x100) {
        int32_t thumb = 0x10000 / g2_calendar_ext_content_height_20074b78;
        if (thumb < 0x14)
            thumb = 0x14;
        g2_calendar_ext_scrollbar_20074b74 = audio_uart_page_43de82(g2_calendar_ext_root_20074b6c);
        if (g2_calendar_ext_scrollbar_20074b74 != NULL) {
            void *bar = g2_calendar_ext_scrollbar_20074b74;
            audio_lv_object_size_call_43f4c0(bar, 2, thumb);
            audio_lv_object_position_43f09a(bar, 0x234, 0);
            audio_uart_page_44127e(bar, audio_lv_color_44104c(COLOR_SCROLLBAR), LV_PART_MAIN);
            audio_uart_page_44129e(bar, 0x7fu, LV_PART_MAIN);
            audio_uart_page_44131c(bar, 0, LV_PART_MAIN);
            audio_uart_page_44146a(bar, 1, LV_PART_MAIN);
            calendar_obj_set_style_pad_all_4ed7d8(bar, 0, LV_PART_MAIN);
            audio_lv_object_clear_flag_43dfa4(bar, LV_OBJ_FLAG_SCROLLABLE);
        }
    }
}

int32_t Calendar_ext_Widget_init_4ef9a4(void *parent)
{
    if (g2_calendar_ext_fifo_20074b88 != NULL) {
        ui_common_api_fn_00509c96(g2_calendar_ext_fifo_20074b88);
        g2_calendar_ext_fifo_20074b88 = NULL;
    }
    g2_calendar_ext_fifo_20074b88 = ui_common_api_fn_00509c1c();
    if (g2_calendar_ext_fifo_20074b88 == NULL) {
        CAL_LOG(1u, fn_init, 0x4e8u, 0x04000000u, fifo_failed, fifo_failed_short);
        return -1;
    }
    g2_calendar_scroll_anim_running_20074b20 = 0;
    g2_calendar_ext_scroll_y_20074b7c = 0;
    g2_calendar_ext_target_y_20074b80 = 0;
    g2_calendar_ext_content_20074b70 = NULL;
    g2_calendar_ext_scrollbar_20074b74 = NULL;
    g2_calendar_ext_content_height_20074b78 = 0;
    calendar_ext_page_create_4eef7c(parent);
    g2_calendar_ext_active_20074b90 = 1;
    page_state_sync_calendar_expanded_500180(0u);
    return 0;
}

/* Called once per dashboard tick; every 3601st call reports events whose end
 * time is more than 15 minutes past as a bit mask {10, mask LE32} to the app. */
void Calendar_expire_check_4efa78(void)
{
    if (g2_calendar_state_20074b84++ <= 3600u)
        return;
    g2_calendar_state_20074b84 = 0u;
    CAL_LOG(4u, fn_check, 0x4fdu, 0x10000000u, check_begin, check_begin_short);
    if (CAL_UI->count == 0u)
        return;

    uint32_t mask = 0u;
    for (int32_t i = 0; i < (int32_t)CAL_UI->count; i++) {
        uint32_t now = service_time_rtc_refresh();
        CAL_LOG(4u, fn_check, 0x509u, 0x10400000u, check_now, check_now_short, now);
        if (CAL_UI->events[i].end_timestamp < now && now - CAL_UI->events[i].end_timestamp > 900u) {
            CAL_LOG(4u, fn_check, 0x50bu, 0x10c00000u, check_expired, check_expired_short, i, now,
                    CAL_UI->events[i].end_timestamp);
            mask |= 1u << (uint32_t)i;
        }
    }
    uint8_t mode = (uint8_t)audio_uart_service_mode();
    if (mask == 0u || mode != 1u)
        return;
    CAL_LOG(4u, fn_check, 0x512u, 0x10400000u, check_mask, check_mask_short, mask);
    uint8_t msg[5];
    audio_uart_buffer_zero(msg, sizeof msg, 0u);
    msg[0] = 10u;
    msg[1] = (uint8_t)mask;
    msg[2] = (uint8_t)((int32_t)mask >> 8);
    msg[3] = (uint8_t)((int32_t)mask >> 16);
    msg[4] = (uint8_t)((int32_t)mask >> 24);
    audio_uart_master_display_refresh(1u, msg, 5u, 0u);
    CAL_LOG(4u, fn_check, 0x51au, 0x10000000u, check_send, check_send_short);
}

/* Removes the events selected by mask_value bits 0..7 and compacts the rest
 * (records with an empty title are dropped), then pings the dashboard {2}. */
void Calendar_expire_update_4efcb8(uint32_t mask_value)
{
    if (g2_calendar_widget_init_flag_20074b1c == 0) {
        CAL_LOG(2u, fn_update, 0x522u, 0x08000000u, widget_not_init, widget_not_init_short);
        return;
    }
    if (CAL_UI->count == 0u)
        return;
    CAL_LOG(4u, fn_update, 0x528u, 0x10400000u, update_value, update_value_short, mask_value);

    g2_calendar_ui_t *scratch = (g2_calendar_ui_t *)(void *)g2_calendar_expire_scratch_2011f0ac;
    audio_uart_buffer_zero(scratch, CAL_UI_SIZE, 0u);
    (void)audio_queue_copy_bytes(scratch, CAL_UI, CAL_UI_SIZE);
    for (int32_t i = 0; i < CAL_EVENT_MAX; i++) {
        if (((uint8_t)mask_value & (1u << (uint32_t)i)) != 0u)
            audio_uart_buffer_zero(&scratch->events[i], CAL_EVENT_SIZE, 0u);
    }

    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    int32_t kept = 0;
    for (int32_t i = 0; i < CAL_EVENT_MAX; i++) {
        if (g2_log_module_length(scratch->events[i].title) != 0u) {
            (void)audio_queue_copy_bytes(&CAL_UI->events[kept], &scratch->events[i], CAL_EVENT_SIZE);
            kept++;
        }
    }
    CAL_UI->count = (uint16_t)kept;
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);

    if ((uint8_t)audio_uart_service_mode() != 1u)
        return;
    CAL_LOG(3u, fn_update, 0x543u, 0x0c400000u, update_mask, update_mask_short, (uint8_t)mask_value);
    uint8_t msg[5];
    audio_uart_buffer_zero(msg, sizeof msg, 0u);
    msg[0] = 2u;
    audio_uart_master_display_refresh(1u, msg, 1u, 0u);
    CAL_LOG(4u, fn_update, 0x547u, 0x10000000u, update_send, update_send_short);
}

void calendar_widget_deinit_4efeb0(void)
{
    g2_calendar_ext_active_20074b90 = 0;
    g2_calendar_scroll_anim_running_20074b20 = 0;
    g2_calendar_ext_scroll_y_20074b7c = 0;
    g2_calendar_ext_target_y_20074b80 = 0;
    g2_calendar_ext_content_20074b70 = NULL;
    g2_calendar_ext_scrollbar_20074b74 = NULL;
    g2_calendar_ext_content_height_20074b78 = 0;
    g2_calendar_state_20074b84 = 0u;
    g2_calendar_widget_init_flag_20074b1c = 0;
}
