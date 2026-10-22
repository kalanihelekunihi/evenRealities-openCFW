/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\health\ui_health_page.c
 * (log tag "health.page"), second part: the expanded (two-page) health widget.
 * Native 0x4FC1DC..0x4FC32D, 0x4FC360..0x4FC57F, 0x4FC644..0x4FD785,
 * 0x4FD7B0..0x4FD835, 0x4FD840..0x4FD86F; literal pools 0x4FC330..0x4FC35F,
 * 0x4FC580..0x4FC643, 0x4FC904, 0x4FCBB0..0x4FCBB7, 0x4FCD8C..0x4FCD93,
 * 0x4FCFD4..0x4FCFD7, 0x4FD1EC..0x4FD1EF, 0x4FD450..0x4FD45B, 0x4FD5B0..0x4FD5CF,
 * 0x4FD6B8..0x4FD6C3, 0x4FD786..0x4FD7AF, 0x4FD836..0x4FD83F, 0x4FD870..0x4FD93B.
 * The first part (tile, paging, scroll animation, Health_Page_Reflash,
 * 0x4FB1C0..0x4FC1B6) is ui/a-37-health-page/ui_health_page.c.
 *
 * Expanded page layout (parent = dashboard focus frame, RAM 0x20074b9c):
 * a 576x256 vertical scroll container holding two 536x256 pages at y 0/256.
 * Page 0: productivity score, steps and calories progress bars (536 px, filled
 * in 3 px steps), sleep score + duration, heart rate + average, blood oxygen
 * + average. Page 1: up to five typed insight lines, or "gathering insights".
 * A separate right-aligned column holds the two 4x4 page dots.
 *
 * The health record metric slots follow the health data manager type table
 * (0x559854: 2 STEPS, 3 CALORIES, 4 SLEEP, 5 HEART_RATE, 6 BLOOD_OXYGEN,
 * 7 TEMPERATURE, 8 HRV, 9 PRODUCTIVITY; slot = type - 2).
 *
 * Uses single-precision VFP (vcvt.u32.f32, vdiv.f32, vmla.f32, vcmp.f32):
 * build with profile g2-apollo-main-3. No float crosses a call boundary. */
#include <stddef.h>
#include <stdint.h>

/* One health metric (0x18 bytes); same layout as ui_health_page.c. */
typedef struct {
    uint8_t head[8];     /* +0x00 */
    uint32_t goal;       /* +0x08 0 = default goal */
    float value;         /* +0x0c */
    float average;       /* +0x10 heart rate / blood oxygen average */
    uint32_t seconds;    /* +0x14 sleep duration */
} g2_health_metric_t;
_Static_assert(sizeof(g2_health_metric_t) == 0x18, "metric record");

/* One insight line (0x101 bytes): metric type, then NUL-terminated text. */
typedef struct {
    uint8_t type;        /* +0x000 */
    char text[0x100];    /* +0x001 */
} g2_health_insight_t;
_Static_assert(sizeof(g2_health_insight_t) == 0x101, "insight record");

#define HEALTH_INSIGHT_MAX 5u

/* Health record (RAM 0x200f41b4, 0x5d0 bytes). */
typedef struct {
    g2_health_metric_t metric[8];                     /* +0x000 */
    uint8_t ring_state;                               /* +0x0c0 1 / 3 select the status icon */
    uint8_t pad_c1[3];
    uint32_t insight_count;                           /* +0x0c4 */
    g2_health_insight_t insight[HEALTH_INSIGHT_MAX];  /* +0x0c8 */
    uint8_t pad_5cd[3];
} g2_health_data_t;
_Static_assert(sizeof(g2_health_data_t) == 0x5d0, "health record");
_Static_assert(offsetof(g2_health_data_t, insight) == 0xc8, "insights at +0xc8");

#define HEALTH_M_STEPS        0 /* goal default 10000 */
#define HEALTH_M_CALORIES     1 /* goal default 2000 */
#define HEALTH_M_SLEEP        2 /* value = score, seconds = duration */
#define HEALTH_M_HEART_RATE   3
#define HEALTH_M_BLOOD_OXYGEN 4 /* percent, capped at 100 */
#define HEALTH_M_PRODUCTIVITY 7

/* Insight types (health data manager numbering). */
#define HEALTH_T_STEPS        2u
#define HEALTH_T_CALORIES     3u
#define HEALTH_T_SLEEP        4u
#define HEALTH_T_HEART_RATE   5u
#define HEALTH_T_BLOOD_OXYGEN 6u
#define HEALTH_T_TEMPERATURE  7u
#define HEALTH_T_HRV          8u

/* Icon/label pair of one insight line (RAM 0x20073800 table). */
typedef struct {
    void *icon;  /* +0x00 */
    void *label; /* +0x04 */
} g2_health_insight_objs_t;

#define HEALTH_PAGE_COUNT       2u
#define HEALTH_PAGE_W           536 /* 0x218, also the bar width */
#define HEALTH_PAGE_H           256
#define HEALTH_WIDGET_TYPE      5u

#define HEALTH_EVT_TAP          0x0au
#define HEALTH_EVT_NEXT         0x44u
#define HEALTH_EVT_PREV         0x45u
#define HEALTH_EVT_46           0x46u
#define HEALTH_EVT_DOUBLE_TAP   0x48u
#define HEALTH_EVT_FADEOUT      0x49u

#define LV_OBJ_FLAG_CLICKABLE   0x02u
#define LV_OBJ_FLAG_SCROLLABLE  0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_SIZE_CONTENT         0x3fffffff
#define LV_ALIGN_TOP_LEFT       1u
#define LV_ALIGN_TOP_RIGHT      3u
#define LV_ALIGN_RIGHT_MID      8u
#define LV_ALIGN_CENTER         9u
#define LV_ALIGN_OUT_BOTTOM_LEFT 13u
#define LV_ALIGN_OUT_LEFT_TOP   16u
#define LV_ALIGN_OUT_RIGHT_TOP  19u
#define LV_DIR_VER              0x0cu
#define LV_SCROLLBAR_MODE_OFF   0u
#define LV_TEXT_ALIGN_CENTER    2u
#define LV_ANIM_OFF             0u

/* Input event handed to HealthInputEventHandler; +0x10 points at two words
 * (scroll offset, speed) for the 0x44/0x45 scroll events. */
typedef struct {
    uint8_t hdr[0x10];       /* +0x00 */
    const int32_t *value;    /* +0x10 */
} g2_health_input_event_t;

/* RAM state. */
extern g2_health_data_t g2_health_data;                  /* RAM 0x200f41b4 */
extern void *g2_dashboard_focus_frame;                   /* RAM 0x20074b9c expanded-page parent */
extern void *g2_health_page_dots[HEALTH_PAGE_COUNT];     /* RAM 0x20074198 */
extern void *g2_health_ext_pages[HEALTH_PAGE_COUNT];     /* RAM 0x20074190 */
extern g2_health_insight_objs_t g2_health_insight_objs[HEALTH_INSIGHT_MAX]; /* RAM 0x20073800 */
extern int32_t g2_health_widget_init_flag;               /* RAM 0x20074c0c widget_health_init_flag */
extern void *g2_health_ext_fifo;                         /* RAM 0x20074c10 health_ext_fifo */
extern int32_t g2_health_is_animating;                   /* RAM 0x20074c14 health_is_animating */
extern uint32_t g2_health_tile_index;                    /* RAM 0x20074c18 */
extern int32_t g2_health_ext_widget_init_flag;           /* RAM 0x20074c1c health_ext_widget_init_flag */
extern uint32_t g2_health_page_index;                    /* RAM 0x20074c20 */
extern void *g2_health_scroll_container;                 /* RAM 0x20074c6c health_scroll_container */
extern void *g2_health_ext_ring_icon;                    /* RAM 0x20074c70 */
extern void *g2_health_ext_score_title;                  /* RAM 0x20074c74 */
extern void *g2_health_ext_score_value;                  /* RAM 0x20074c78 */
extern void *g2_health_ext_steps_icon;                   /* RAM 0x20074c7c */
extern void *g2_health_ext_steps_label;                  /* RAM 0x20074c80 */
extern void *g2_health_ext_steps_goal;                   /* RAM 0x20074c84 */
extern void *g2_health_ext_steps_bar;                    /* RAM 0x20074c88 */
extern void *g2_health_ext_steps_mask;                   /* RAM 0x20074c8c */
extern void *g2_health_ext_calories_icon;                /* RAM 0x20074c90 */
extern void *g2_health_ext_calories_label;               /* RAM 0x20074c94 */
extern void *g2_health_ext_calories_goal;                /* RAM 0x20074c98 */
extern void *g2_health_ext_calories_bar;                 /* RAM 0x20074c9c */
extern void *g2_health_ext_calories_mask;                /* RAM 0x20074ca0 */
extern void *g2_health_ext_sleep_icon;                   /* RAM 0x20074ca4 */
extern void *g2_health_ext_sleep_value;                  /* RAM 0x20074ca8 */
extern void *g2_health_ext_sleep_duration;               /* RAM 0x20074cac */
extern void *g2_health_ext_heart_icon;                   /* RAM 0x20074cb0 */
extern void *g2_health_ext_heart_value;                  /* RAM 0x20074cb4 */
extern void *g2_health_ext_heart_average;                /* RAM 0x20074cb8 */
extern void *g2_health_ext_oxygen_icon;                  /* RAM 0x20074cbc */
extern void *g2_health_ext_oxygen_value;                 /* RAM 0x20074cc0 */
extern void *g2_health_ext_oxygen_average;               /* RAM 0x20074cc4 */
extern void *g2_health_ext_insight_placeholder;          /* RAM 0x20074cc8 */
extern void *g2_health_ext_indicator;                    /* RAM 0x20074ccc page-dot column */
extern void *audio_uart_ring_primary_head_cell;          /* RAM 0x200746dc: active lv_font_t * */

/* lv_image_dsc_t assets (ROM). */
extern const uint8_t g2_health_img_ring_state1[];        /* ROM 0x7725c4, 24x24 */
extern const uint8_t g2_health_img_ring_state3[];        /* ROM 0x7725a8, 24x24 */
extern const uint8_t g2_health_img_ring_other[];         /* ROM 0x77258c, 24x24 */
extern const uint8_t g2_health_img_steps[];              /* ROM 0x7747ac, 24x24 */
extern const uint8_t g2_health_img_bar_wide[];           /* ROM 0x76bd34, 536x8 */
extern const uint8_t g2_health_img_calories[];           /* ROM 0x769fac, 24x24 */
extern const uint8_t g2_health_img_duration[];           /* ROM 0x771dc8, 24x24 (sleep) */
extern const uint8_t g2_health_img_heart[];              /* ROM 0x76bddc, 24x24 (also HRV insight) */
extern const uint8_t g2_health_img_percent[];            /* ROM 0x771e54, 24x24 (blood oxygen) */
extern const uint8_t g2_health_img_insight_heart_rate[]; /* ROM 0x76a888, 24x24 */
extern const uint8_t g2_health_img_insight_temperature[]; /* ROM 0x769e78, 24x24 */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* libc-like, i18n. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern uint32_t audio_uart_page_460084(const char *key);                       /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);    /* localized text */

/* LVGL 9.3 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                            /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                 /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                 /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);          /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                     /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                     /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);          /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                     /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                     /* lv_obj_set_height */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                                /* lv_obj_align_to */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                         /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);  /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);    /* bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);       /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);  /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel);  /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);       /* radius */
extern void audio_lv_delete_44d7b8(void *obj);                                /* lv_obj_delete */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);        /* lv_obj_get_child */
extern int32_t audio_uart_lv_child_count_44ddea(void *obj);                   /* lv_obj_get_child_count */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                 /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);                  /* lv_obj_set_scroll_dir */
extern void audio_terminal_display_status_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void *audio_uart_page_498668(void *parent);                            /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);             /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                            /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);     /* lv_label_set_text */

/* UI FIFO (ui_common_api), sync interface. */
extern void *ui_common_api_fn_00509c1c(void);                                         /* create */
extern void ui_common_api_fn_00509c96(void *fifo);                                    /* destroy */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push */
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                 uint32_t flags); /* 0x464bb2 */

/* Dashboard / health modules. */
extern void dashboard_status_data_apply_4e8970(const uint8_t *data, uint32_t len);
extern void Dashboard_Fadeout_Anim_Start_4e8a90(void);
extern void dashboard_focus_frame_shrink_anim_4e92f4(void);
extern void lv_obj_set_style_pad_all_4fb1c0(void *obj, int32_t value, uint32_t selector);
extern void health_update_page_indicator_4fb1fa(uint32_t page_index);
extern void health_switch_to_page_4fb290(uint32_t target_page_index);
extern int32_t Health_Page_Reflash_4fb5e8(const uint8_t *data, uint32_t len);
extern uint32_t health_lock_storage(void);    /* 0x4ffc32, 1 locked */
extern void health_unlock_storage(void);      /* 0x4ffc90 */
extern int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile_index, uint8_t widget);
extern int32_t page_state_sync_health_expanded_50029c(uint32_t page);

int32_t HealthInputEventHandler_4fc1dc(uint32_t code, const g2_health_input_event_t *event);
int32_t health_ext_event_handler_4fc360(const uint8_t *data, uint32_t len);
int32_t health_ext_widget_page_create_4fc644(void *parent);
int32_t Health_ext_Widget_init_4fd7b0(void *parent);
int32_t health_ext_widget_state_reset_4fd840(void);

static const char tag[] = "health.page"; /* ROM 0x78c830 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\health\\ui_health_page.c"; /* ROM 0x707b9c */
static const char fn_input[] = "HealthInputEventHandler"; /* ROM 0x77d2f4 */
static const char m_animating[] = "health_is_animating == 1, return"; /* ROM 0x75c408 */
static const char t_animating[] = "[health.page]health_is_animating == 1, return"; /* ROM 0x73a814 */
static const char fn_ext_handler[] = "health_ext_event_handler"; /* ROM 0x773f94 */
static const char m_ext_not_init[] = "health_ext_widget_init_flag == 0, return"; /* ROM 0x745eb0 */
static const char t_ext_not_init[] =
    "[health.page]health_ext_widget_init_flag == 0, return"; /* ROM 0x725450 */
static const char m_len_zero[] = "len == 0, return"; /* ROM 0x784824 */
static const char t_len_zero[] = "[health.page]len == 0, return"; /* ROM 0x767510 */
static const char m_unknown_evt[] = "HealthWidget_event_handler: unknown event type: %d"; /* ROM 0x72fdf4 */
static const char t_unknown_evt[] =
    "[health.page]HealthWidget_event_handler: unknown event type: %d"; /* ROM 0x711024 */
static const char fn_init[] = "Health_ext_Widget_init"; /* ROM 0x77d33c */
static const char m_fifo_failed[] = "health_ext_fifo create failed"; /* ROM 0x767530 */
static const char t_fifo_failed[] = "[health.page]health_ext_fifo create failed"; /* ROM 0x745edc */
static const char key_score[] = "ID_DASHBOARD_HEALTH_PRODUCTIVITY_SCORE"; /* ROM 0x750874 */
static const char key_steps[] = "ID_DASHBOARD_HEALTH_STEPS";       /* ROM 0x773f78 */
static const char key_calories[] = "ID_DASHBOARD_HEALTH_CALORIES"; /* ROM 0x7674f0 */
static const char key_min[] = "ID_DASHBOARD_HEALTH_MIN";           /* ROM 0x77d30c */
static const char key_hour[] = "ID_DASHBOARD_HEALTH_HOUR";         /* ROM 0x773fb0 */
static const char key_bpm[] = "ID_DASHBOARD_HEALTH_BPM";           /* ROM 0x77d2dc */
static const char key_avg[] = "ID_DASHBOARD_HEALTH_AVG";           /* ROM 0x77d324 */
static const char key_gathering[] = "ID_DASHBOARD_HEALTH_GATHERING_INSIGHTS"; /* ROM 0x75089c */
static const char f_int[] = "%d";              /* ROM 0x4fcbb0 (inline) */
static const char f_dash[] = "-";              /* ROM 0x4fcbb4 (inline) */
static const char f_int_2[] = "%d";            /* ROM 0x4fcfd4 (inline) */
static const char f_dash_2[] = "-";            /* ROM 0x4fd1ec (inline) */
static const char f_name_int[] = "%s %d";      /* ROM 0x78ecbc */
static const char f_name_dash[] = "%s -";      /* ROM 0x78ecc4 */
static const char f_dur_none[] = "-%s -%s";    /* ROM 0x78ece4 */
static const char f_dur_zero[] = "0%s 0%s";    /* ROM 0x78ecec */
static const char f_dur[] = "%d%s %d%s";       /* ROM 0x78c83c */
static const char f_dash_unit[] = "-%s";       /* ROM 0x4fd450 (inline) */
static const char f_int_unit[] = "%d%s";       /* ROM 0x78eccc */
static const char f_avg_int_unit[] = "%s %d%s";  /* ROM 0x78ecf4 */
static const char f_avg_dash_unit[] = "%s -%s";  /* ROM 0x78ecfc */
static const char f_full_pct[] = "100%%";      /* ROM 0x78ecd4 */
static const char f_int_pct[] = "%d%%";        /* ROM 0x78ecdc */
static const char f_dash_pct[] = "-%%";        /* ROM 0x4fd5c8 (inline) */
static const char f_avg_full_pct[] = "%s 100%%"; /* ROM 0x78c848 */
static const char f_avg_int_pct[] = "%s %d%%";   /* ROM 0x78ed04 */
static const char f_avg_dash_pct[] = "%s -%%";   /* ROM 0x78ed0c */

#define HP_LOG0(lvl, line, fn, m, t)                                                     \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((lvl), tag, src, (fn), (line), (m));                      \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output((uint32_t)(lvl) << 26, (t), (t));                  \
    } while (0)
#define HP_LOG1(lvl, line, fn, m, t, a)                                                  \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((lvl), tag, src, (fn), (line), (m), (a));                 \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output(((uint32_t)(lvl) << 26) | 0x00400000u, (t), (t), (a)); \
    } while (0)

#define FONT() (audio_uart_ring_primary_head_cell)
#define WHITE() (audio_uart_page_44104c(0xffffffu))

static const char *health_text(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* Forwards a dashboard input event to the UI application as a 6-byte type-0
 * frame {0, code, a lo, a hi, b lo, b hi}; other codes are returned as is. */
int32_t HealthInputEventHandler_4fc1dc(uint32_t code, const g2_health_input_event_t *event)
{
    uint8_t frame[6];
    const int32_t *v;

    if (g2_health_is_animating == 1) {
        HP_LOG0(3u, 0x397u, fn_input, m_animating, t_animating);
        return 0;
    }
    if (code == HEALTH_EVT_TAP || code == HEALTH_EVT_DOUBLE_TAP || code == HEALTH_EVT_FADEOUT) {
        frame[0] = 0;
        frame[1] = (uint8_t)code;
        frame[2] = 0;
        frame[3] = 0;
        frame[4] = 0;
        frame[5] = 0;
        return audio_uart_master_display_refresh(1u, frame, 6u, 0u);
    }
    if (code == HEALTH_EVT_PREV || code == HEALTH_EVT_NEXT) {
        v = event->value;
        frame[0] = 0;
        frame[1] = (uint8_t)code;
        frame[2] = (uint8_t)v[0];
        frame[3] = (uint8_t)(v[0] >> 8);
        frame[4] = (uint8_t)v[1];
        frame[5] = (uint8_t)(v[1] >> 8);
        return audio_uart_master_display_refresh(1u, frame, 6u, 0u);
    }
    return (int32_t)code;
}

static void health_ext_close(void)
{
    int32_t i;
    void *child;

    for (i = audio_uart_lv_child_count_44ddea(g2_dashboard_focus_frame) - 1; i >= 0; i--) {
        child = audio_uart_lv_child_get_44dce2(g2_dashboard_focus_frame, i);
        if (child != NULL)
            audio_lv_delete_44d7b8(child);
    }
    if (g2_health_ext_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_health_ext_fifo);
        g2_health_ext_fifo = NULL;
    }
    g2_health_ext_widget_init_flag = 0;
    g2_health_is_animating = 0;
    dashboard_focus_frame_shrink_anim_4e92f4();
    (void)page_state_sync_dashboard_main_5000cc(g2_health_tile_index, HEALTH_WIDGET_TYPE);
}

/* UI-side frames: [0] type. 0 = input {0, code, value u32 LE} (queued in the
 * FIFO while the page scroll runs), 1 = dashboard status data, 6 = health
 * data refresh. */
int32_t health_ext_event_handler_4fc360(const uint8_t *data, uint32_t len)
{
    uint8_t code;
    uint32_t value;

    if (g2_health_ext_widget_init_flag == 0) {
        HP_LOG0(2u, 0x3cfu, fn_ext_handler, m_ext_not_init, t_ext_not_init);
        return 0;
    }
    if (len == 0u) {
        HP_LOG0(2u, 0x3d3u, fn_ext_handler, m_len_zero, t_len_zero);
        return 0;
    }
    switch (data[0]) {
    case 0:
        code = data[1];
        value = (uint32_t)data[2] | ((uint32_t)data[3] << 8) | ((uint32_t)data[4] << 16) |
                ((uint32_t)data[5] << 24);
        (void)(value >> 16); /* speed, decoded but unused */
        if (g2_health_is_animating != 0) {
            (void)ui_common_api_fn_00509ca2(g2_health_ext_fifo, data + 1, 5u);
            return 0;
        }
        switch (code) {
        case HEALTH_EVT_TAP:
            health_ext_close();
            break;
        case HEALTH_EVT_NEXT:
            if ((int32_t)g2_health_page_index + 1 < (int32_t)HEALTH_PAGE_COUNT)
                health_switch_to_page_4fb290(g2_health_page_index + 1u);
            break;
        case HEALTH_EVT_PREV:
            if ((int32_t)g2_health_page_index - 1 >= 0)
                health_switch_to_page_4fb290(g2_health_page_index - 1u);
            break;
        case HEALTH_EVT_46:
            break;
        case HEALTH_EVT_DOUBLE_TAP:
            health_ext_close();
            break;
        case HEALTH_EVT_FADEOUT:
            Dashboard_Fadeout_Anim_Start_4e8a90();
            g2_health_ext_widget_init_flag = 0;
            g2_health_is_animating = 0;
            break;
        default:
            HP_LOG1(2u, 0x42eu, fn_ext_handler, m_unknown_evt, t_unknown_evt, (uint32_t)code);
            break;
        }
        break;
    case 1:
        dashboard_status_data_apply_4e8970(data + 1, len - 1u);
        break;
    case 6:
        (void)Health_Page_Reflash_4fb5e8(data + 1, len - 1u);
        break;
    default:
        break;
    }
    return 0;
}

/* Transparent, unpadded, borderless container used for pages and masks. */
static void health_flat_style(void *obj, uint32_t opa)
{
    audio_uart_page_44127e(obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(obj, opa, 0u);
    lv_obj_set_style_pad_all_4fb1c0(obj, 0, 0u);
    audio_uart_page_44131c(obj, 0, 0u);
    audio_uart_page_44146a(obj, 0, 0u);
}

static void health_icon_flags(void *img)
{
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
}

/* 24x24 icon at (0, y) of the first page. */
static void *health_row_icon(void *page, const void *img_src, int32_t y)
{
    void *img = audio_uart_page_498668(page);

    audio_uart_page_498680(img, img_src);
    audio_uart_page_43f506(img, 24);
    audio_uart_page_43f568(img, 24);
    audio_uart_page_43f0e0(img, 0);
    audio_uart_page_43f142(img, y);
    health_icon_flags(img);
    return img;
}

/* Label placed right of an icon (8 px gap, 2 px up). */
static void *health_row_label(void *page, void *icon, int32_t w)
{
    void *label = audio_uart_page_499416(page);

    audio_uart_page_43f506(label, w);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(label, icon, LV_ALIGN_OUT_RIGHT_TOP, 8, -2);
    return label;
}

/* Goal text ("%d") right-aligned at y, dark grey. */
static void *health_goal_label(void *page, int32_t y, char *text, const char *fmt, uint32_t goal)
{
    void *label = audio_uart_page_499416(page);

    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(label, LV_ALIGN_TOP_RIGHT, 0, y);
    (void)audio_ble_format_to_buffer(text, fmt, goal);
    (void)audio_uart_page_49942e(label, text);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0u);
    audio_uart_page_44143e(label, FONT(), 0u);
    return label;
}

static void *health_bar(void *page, void *icon)
{
    void *bar = audio_uart_page_498668(page);

    audio_uart_page_498680(bar, g2_health_img_bar_wide);
    audio_uart_page_43f506(bar, HEALTH_PAGE_W);
    audio_uart_page_43f568(bar, 8);
    audio_uart_page_43f6d6(bar, icon, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 10);
    health_icon_flags(bar);
    return bar;
}

/* Fill in pixels: ratio * 536 + 1, rounded down to 3 px, max 536. */
static int32_t health_bar_fill(uint32_t value, uint32_t goal)
{
    float ratio;
    int32_t fill;

    if (value == 0u)
        ratio = 0.0f;   /* ROM 0x4fcd8c */
    else if (value < goal)
        ratio = (float)value / (float)goal;
    else
        ratio = 1.0f;
    fill = ((int32_t)(ratio * 536.0f + 1.0f) / 3) * 3;   /* 536.0f: ROM 0x4fcd90 */
    if (fill > HEALTH_PAGE_W)
        fill = HEALTH_PAGE_W;
    return fill;
}

/* Black 190-opacity mask over the unfilled right part of a bar. */
static void *health_bar_mask(void *page, void *bar, int32_t fill)
{
    void *mask = audio_uart_page_43de82(page);

    audio_uart_page_43f506(mask, HEALTH_PAGE_W - fill);
    audio_uart_page_43f568(mask, 8);
    audio_uart_page_43f6d6(mask, bar, LV_ALIGN_TOP_LEFT, fill, 0);
    health_flat_style(mask, 0xbeu);
    audio_uart_page_43dfa4(mask, LV_OBJ_FLAG_SCROLLABLE);
    return mask;
}

static void health_white_text(void *label)
{
    audio_uart_page_44140e(label, WHITE(), 0u);
    audio_uart_page_44143e(label, FONT(), 0u);
}

static const void *health_insight_icon(uint8_t type)
{
    switch (type) {
    case HEALTH_T_STEPS:
    case HEALTH_T_CALORIES:
        return g2_health_img_steps;
    case HEALTH_T_SLEEP:
        return g2_health_img_duration;
    case HEALTH_T_HEART_RATE:
        return g2_health_img_insight_heart_rate;
    case HEALTH_T_BLOOD_OXYGEN:
        return g2_health_img_percent;
    case HEALTH_T_TEMPERATURE:
        return g2_health_img_insight_temperature;
    case HEALTH_T_HRV:
        return g2_health_img_heart;
    default:
        return NULL;
    }
}

/* Builds the expanded health page under `parent` and scrolls it to the
 * current page without animation. */
int32_t health_ext_widget_page_create_4fc644(void *parent)
{
    char text[64];
    int32_t i, rows, fill;
    uint32_t score, value, goal, seconds, count, n;
    uint8_t type;
    const void *icon;
    void *page;
    const char *min_txt, *hour_txt, *unit_txt, *avg_txt;

    aeabi_memset_43c0e4(text, sizeof text, 0);

    g2_health_scroll_container = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(g2_health_scroll_container, 0x240, HEALTH_PAGE_H);
    audio_uart_page_43f09a(g2_health_scroll_container, 0, 16);
    audio_uart_page_43ded4(g2_health_scroll_container, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e3ca(g2_health_scroll_container, LV_DIR_VER);
    audio_uart_page_44e368(g2_health_scroll_container, LV_SCROLLBAR_MODE_OFF);
    lv_obj_set_style_pad_all_4fb1c0(g2_health_scroll_container, 0, 0u);
    audio_uart_page_44131c(g2_health_scroll_container, 0, 0u);
    audio_uart_page_44127e(g2_health_scroll_container, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_health_scroll_container, 0u, 0u);

    for (i = 0; i < (int32_t)HEALTH_PAGE_COUNT; i++) {
        g2_health_ext_pages[i] = audio_uart_page_43de82(g2_health_scroll_container);
        audio_uart_page_43f4c0(g2_health_ext_pages[i], HEALTH_PAGE_W, HEALTH_PAGE_H);
        audio_uart_page_43f09a(g2_health_ext_pages[i], 20, i << 8);
        audio_uart_page_43dfa4(g2_health_ext_pages[i], LV_OBJ_FLAG_SCROLLABLE);
        audio_uart_page_44e368(g2_health_ext_pages[i], LV_SCROLLBAR_MODE_OFF);
        audio_uart_page_44127e(g2_health_ext_pages[i], audio_uart_page_44104c(0x000000u), 0u);
        audio_uart_page_44129e(g2_health_ext_pages[i], 0u, 0u);
        lv_obj_set_style_pad_all_4fb1c0(g2_health_ext_pages[i], 0, 0u);
        audio_uart_page_44131c(g2_health_ext_pages[i], 0, 0u);
        audio_uart_page_44146a(g2_health_ext_pages[i], 0, 0u);
    }
    page = g2_health_ext_pages[0];

    /* Ring status icon + productivity score. */
    g2_health_ext_ring_icon = audio_uart_page_498668(page);
    (void)health_lock_storage();
    if (g2_health_data.ring_state == 1u)
        audio_uart_page_498680(g2_health_ext_ring_icon, g2_health_img_ring_state1);
    else if (g2_health_data.ring_state == 3u)
        audio_uart_page_498680(g2_health_ext_ring_icon, g2_health_img_ring_state3);
    else
        audio_uart_page_498680(g2_health_ext_ring_icon, g2_health_img_ring_other);
    health_unlock_storage();
    audio_uart_page_43f506(g2_health_ext_ring_icon, 24);
    audio_uart_page_43f568(g2_health_ext_ring_icon, 24);
    audio_uart_page_43f0e0(g2_health_ext_ring_icon, 0);
    audio_uart_page_43f142(g2_health_ext_ring_icon, 2);
    health_icon_flags(g2_health_ext_ring_icon);

    g2_health_ext_score_title = health_row_label(page, g2_health_ext_ring_icon, LV_SIZE_CONTENT);
    (void)audio_uart_page_49942e(g2_health_ext_score_title, health_text(key_score));
    health_white_text(g2_health_ext_score_title);

    (void)health_lock_storage();
    score = (uint32_t)g2_health_data.metric[HEALTH_M_PRODUCTIVITY].value;
    health_unlock_storage();
    if (score == 0u)
        (void)audio_ble_format_to_buffer(text, f_dash);
    else
        (void)audio_ble_format_to_buffer(text, f_int, score);
    g2_health_ext_score_value = audio_uart_page_499416(page);
    audio_uart_page_43f506(g2_health_ext_score_value, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_health_ext_score_value, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(g2_health_ext_score_value, LV_ALIGN_TOP_RIGHT, 0, 0);
    (void)audio_uart_page_49942e(g2_health_ext_score_value, text);
    health_white_text(g2_health_ext_score_value);

    /* Steps. */
    (void)health_lock_storage();
    value = (uint32_t)g2_health_data.metric[HEALTH_M_STEPS].value;
    goal = g2_health_data.metric[HEALTH_M_STEPS].goal;
    if (goal == 0u)
        goal = 10000u;
    health_unlock_storage();
    g2_health_ext_steps_icon = health_row_icon(page, g2_health_img_steps, 0x37);
    g2_health_ext_steps_label = health_row_label(page, g2_health_ext_steps_icon, 0x240);
    health_white_text(g2_health_ext_steps_label);
    if (value == 0u)
        (void)audio_ble_format_to_buffer(text, f_name_dash, health_text(key_steps));
    else
        (void)audio_ble_format_to_buffer(text, f_name_int, health_text(key_steps), value);
    (void)audio_uart_page_49942e(g2_health_ext_steps_label, text);
    g2_health_ext_steps_goal = health_goal_label(page, 0x35, text, f_int, goal);
    g2_health_ext_steps_bar = health_bar(page, g2_health_ext_steps_icon);
    fill = health_bar_fill(value, goal);
    g2_health_ext_steps_mask = health_bar_mask(page, g2_health_ext_steps_bar, fill);

    /* Calories. */
    (void)health_lock_storage();
    value = (uint32_t)g2_health_data.metric[HEALTH_M_CALORIES].value;
    goal = g2_health_data.metric[HEALTH_M_CALORIES].goal;
    if (goal == 0u)
        goal = 2000u;
    health_unlock_storage();
    g2_health_ext_calories_icon = health_row_icon(page, g2_health_img_calories, 0x75);
    g2_health_ext_calories_label = health_row_label(page, g2_health_ext_calories_icon, 0x240);
    health_white_text(g2_health_ext_calories_label);
    if (value == 0u)
        (void)audio_ble_format_to_buffer(text, f_name_dash, health_text(key_calories));
    else
        (void)audio_ble_format_to_buffer(text, f_name_int, health_text(key_calories), value);
    (void)audio_uart_page_49942e(g2_health_ext_calories_label, text);
    g2_health_ext_calories_goal = health_goal_label(page, 0x73, text, f_int_2, goal);
    g2_health_ext_calories_bar = health_bar(page, g2_health_ext_calories_icon);
    fill = health_bar_fill(value, goal);
    g2_health_ext_calories_mask = health_bar_mask(page, g2_health_ext_calories_bar, fill);

    /* Sleep score and duration. */
    g2_health_ext_sleep_icon = health_row_icon(page, g2_health_img_duration, 0xbf);
    g2_health_ext_sleep_value = health_row_label(page, g2_health_ext_sleep_icon, 0xa3);
    (void)health_lock_storage();
    if (g2_health_data.metric[HEALTH_M_SLEEP].value <= 0.0f)
        (void)audio_ble_format_to_buffer(text, f_dash_2);
    else
        (void)audio_ble_format_to_buffer(text, f_int_2,
                                         (uint32_t)g2_health_data.metric[HEALTH_M_SLEEP].value);
    (void)audio_uart_page_49942e(g2_health_ext_sleep_value, text);
    health_unlock_storage();
    health_white_text(g2_health_ext_sleep_value);

    g2_health_ext_sleep_duration = audio_uart_page_499416(page);
    audio_uart_page_43f506(g2_health_ext_sleep_duration, 0xa3);
    audio_uart_page_43f568(g2_health_ext_sleep_duration, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_ext_sleep_duration, g2_health_ext_sleep_value,
                           LV_ALIGN_OUT_BOTTOM_LEFT, 0, 4);
    (void)health_lock_storage();
    seconds = g2_health_data.metric[HEALTH_M_SLEEP].seconds;
    min_txt = health_text(key_min);
    hour_txt = health_text(key_hour);
    if (seconds == 0u)
        (void)audio_ble_format_to_buffer(text, f_dur_none, hour_txt, min_txt);
    else if (seconds < 60u)
        (void)audio_ble_format_to_buffer(text, f_dur_zero, hour_txt, min_txt);
    else
        (void)audio_ble_format_to_buffer(text, f_dur, seconds / 3600u, hour_txt,
                                         (seconds % 3600u) / 60u, min_txt);
    (void)audio_uart_page_49942e(g2_health_ext_sleep_duration, text);
    health_unlock_storage();
    audio_uart_page_44143e(g2_health_ext_sleep_duration, FONT(), 0u);
    audio_uart_page_44140e(g2_health_ext_sleep_duration, WHITE(), 0u);

    /* Heart rate and average. */
    g2_health_ext_heart_icon = audio_uart_page_498668(page);
    audio_uart_page_498680(g2_health_ext_heart_icon, g2_health_img_heart);
    audio_uart_page_43f506(g2_health_ext_heart_icon, 24);
    audio_uart_page_43f568(g2_health_ext_heart_icon, 24);
    audio_uart_page_43f6d6(g2_health_ext_heart_icon, g2_health_ext_sleep_icon, LV_ALIGN_OUT_RIGHT_TOP,
                           0xb2, 0);
    health_icon_flags(g2_health_ext_heart_icon);
    g2_health_ext_heart_value = health_row_label(page, g2_health_ext_heart_icon, 0xab);
    (void)health_lock_storage();
    unit_txt = health_text(key_bpm);
    if (g2_health_data.metric[HEALTH_M_HEART_RATE].value <= 0.0f)
        (void)audio_ble_format_to_buffer(text, f_dash_unit, unit_txt);
    else
        (void)audio_ble_format_to_buffer(text, f_int_unit,
                                         (uint32_t)g2_health_data.metric[HEALTH_M_HEART_RATE].value,
                                         unit_txt);
    (void)audio_uart_page_49942e(g2_health_ext_heart_value, text);
    health_unlock_storage();
    health_white_text(g2_health_ext_heart_value);

    g2_health_ext_heart_average = audio_uart_page_499416(page);
    audio_uart_page_43f506(g2_health_ext_heart_average, 0xab);
    audio_uart_page_43f568(g2_health_ext_heart_average, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_ext_heart_average, g2_health_ext_heart_value,
                           LV_ALIGN_OUT_BOTTOM_LEFT, 0, 4);
    (void)health_lock_storage();
    unit_txt = health_text(key_bpm);
    avg_txt = health_text(key_avg);
    if (g2_health_data.metric[HEALTH_M_HEART_RATE].average <= 0.0f)
        (void)audio_ble_format_to_buffer(text, f_avg_dash_unit, avg_txt, unit_txt);
    else
        (void)audio_ble_format_to_buffer(text, f_avg_int_unit, avg_txt,
                                         (uint32_t)g2_health_data.metric[HEALTH_M_HEART_RATE].average,
                                         unit_txt);
    (void)audio_uart_page_49942e(g2_health_ext_heart_average, text);
    health_unlock_storage();
    health_white_text(g2_health_ext_heart_average);

    /* Blood oxygen and average (percent, 100.0f: ROM 0x4fd5b4). */
    g2_health_ext_oxygen_icon = audio_uart_page_498668(page);
    audio_uart_page_498680(g2_health_ext_oxygen_icon, g2_health_img_percent);
    audio_uart_page_43f506(g2_health_ext_oxygen_icon, 24);
    audio_uart_page_43f568(g2_health_ext_oxygen_icon, 24);
    audio_uart_page_43f6d6(g2_health_ext_oxygen_icon, g2_health_ext_heart_icon, LV_ALIGN_OUT_RIGHT_TOP,
                           0xb2, 0);
    health_icon_flags(g2_health_ext_oxygen_icon);
    g2_health_ext_oxygen_value = health_row_label(page, g2_health_ext_oxygen_icon, 100);
    (void)health_lock_storage();
    if (g2_health_data.metric[HEALTH_M_BLOOD_OXYGEN].value < 100.0f) {
        if (g2_health_data.metric[HEALTH_M_BLOOD_OXYGEN].value <= 0.0f)
            (void)audio_ble_format_to_buffer(text, f_dash_pct);
        else
            (void)audio_ble_format_to_buffer(
                text, f_int_pct, (uint32_t)g2_health_data.metric[HEALTH_M_BLOOD_OXYGEN].value);
    } else {
        (void)audio_ble_format_to_buffer(text, f_full_pct);
    }
    (void)audio_uart_page_49942e(g2_health_ext_oxygen_value, text);
    health_unlock_storage();
    health_white_text(g2_health_ext_oxygen_value);

    g2_health_ext_oxygen_average = audio_uart_page_499416(page);
    audio_uart_page_43f506(g2_health_ext_oxygen_average, 0x6e);
    audio_uart_page_43f568(g2_health_ext_oxygen_average, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_ext_oxygen_average, g2_health_ext_oxygen_value,
                           LV_ALIGN_OUT_BOTTOM_LEFT, 0, 4);
    (void)health_lock_storage();
    avg_txt = health_text(key_avg);
    if (g2_health_data.metric[HEALTH_M_BLOOD_OXYGEN].average < 100.0f) {
        if (g2_health_data.metric[HEALTH_M_BLOOD_OXYGEN].average <= 0.0f)
            (void)audio_ble_format_to_buffer(text, f_avg_dash_pct, avg_txt);
        else
            (void)audio_ble_format_to_buffer(
                text, f_avg_int_pct, avg_txt,
                (uint32_t)g2_health_data.metric[HEALTH_M_BLOOD_OXYGEN].average);
    } else {
        (void)audio_ble_format_to_buffer(text, f_avg_full_pct, avg_txt);
    }
    (void)audio_uart_page_49942e(g2_health_ext_oxygen_average, text);
    health_unlock_storage();
    health_white_text(g2_health_ext_oxygen_average);

    /* Page 1: insights. */
    (void)health_lock_storage();
    count = g2_health_data.insight_count;
    health_unlock_storage();
    if (count == 0u) {
        g2_health_ext_insight_placeholder = audio_uart_page_499416(g2_health_ext_pages[1]);
        audio_uart_page_43f506(g2_health_ext_insight_placeholder, HEALTH_PAGE_W);
        audio_uart_page_43f568(g2_health_ext_insight_placeholder, LV_SIZE_CONTENT);
        audio_uart_page_43f6b8(g2_health_ext_insight_placeholder, LV_ALIGN_CENTER, 0, 0);
        (void)audio_uart_page_49942e(g2_health_ext_insight_placeholder, health_text(key_gathering));
        health_white_text(g2_health_ext_insight_placeholder);
        audio_uart_page_44145a(g2_health_ext_insight_placeholder, LV_TEXT_ALIGN_CENTER, 0u);
    } else {
        rows = 0;
        for (n = 0; n < count; n++) {
            (void)health_lock_storage();
            type = g2_health_data.insight[n].type;
            health_unlock_storage();
            icon = health_insight_icon(type);
            if (icon == NULL)
                continue;
            g2_health_insight_objs[rows].label = audio_uart_page_499416(g2_health_ext_pages[1]);
            audio_uart_page_43f506(g2_health_insight_objs[rows].label, 0x1f8);
            audio_uart_page_43f568(g2_health_insight_objs[rows].label, LV_SIZE_CONTENT);
            if (rows == 0)
                audio_uart_page_43f6b8(g2_health_insight_objs[0].label, LV_ALIGN_TOP_LEFT, 0x20, 0);
            else
                audio_uart_page_43f6d6(g2_health_insight_objs[rows].label,
                                       g2_health_insight_objs[rows - 1].label,
                                       LV_ALIGN_OUT_BOTTOM_LEFT, 0, 0x18);
            health_white_text(g2_health_insight_objs[rows].label);
            (void)health_lock_storage();
            (void)audio_uart_page_49942e(g2_health_insight_objs[rows].label,
                                         g2_health_data.insight[n].text);
            health_unlock_storage();
            g2_health_insight_objs[rows].icon = audio_uart_page_498668(g2_health_ext_pages[1]);
            audio_uart_page_498680(g2_health_insight_objs[rows].icon, icon);
            audio_uart_page_43f506(g2_health_insight_objs[rows].icon, 24);
            audio_uart_page_43f568(g2_health_insight_objs[rows].icon, 24);
            audio_uart_page_43f6d6(g2_health_insight_objs[rows].icon,
                                   g2_health_insight_objs[rows].label, LV_ALIGN_OUT_LEFT_TOP, -8, 2);
            health_icon_flags(g2_health_insight_objs[rows].icon);
            rows++;
        }
    }

    /* Page dots column. */
    g2_health_ext_indicator = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(g2_health_ext_indicator, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_health_ext_indicator, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(g2_health_ext_indicator, LV_ALIGN_RIGHT_MID, -8, 0);
    audio_uart_page_44127e(g2_health_ext_indicator, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_health_ext_indicator, 0xffu, 0u);
    audio_uart_page_44131c(g2_health_ext_indicator, 0, 0u);
    audio_uart_page_44146a(g2_health_ext_indicator, 0, 0u);
    lv_obj_set_style_pad_all_4fb1c0(g2_health_ext_indicator, 0, 0u);
    audio_uart_page_44e368(g2_health_ext_indicator, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_43ded4(g2_health_ext_indicator, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(g2_health_ext_indicator, LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE);
    for (i = 0; i < (int32_t)HEALTH_PAGE_COUNT; i++) {
        g2_health_page_dots[i] = audio_uart_page_43de82(g2_health_ext_indicator);
        audio_uart_page_43f506(g2_health_page_dots[i], 4);
        audio_uart_page_43f568(g2_health_page_dots[i], 4);
        if (i == 0)
            audio_uart_page_43f6b8(g2_health_page_dots[0], LV_ALIGN_TOP_LEFT, 0, 0);
        else
            audio_uart_page_43f6d6(g2_health_page_dots[i], g2_health_page_dots[i - 1],
                                   LV_ALIGN_OUT_BOTTOM_LEFT, 0, 8);
        audio_uart_page_44127e(g2_health_page_dots[i], WHITE(), 0u);
        audio_uart_page_44129e(g2_health_page_dots[i], 0xffu, 0u);
        audio_uart_page_44131c(g2_health_page_dots[i], 0, 0u);
        audio_uart_page_44146a(g2_health_page_dots[i], 0, 0u);
        lv_obj_set_style_pad_all_4fb1c0(g2_health_page_dots[i], 0, 0u);
        audio_uart_page_43dfa4(g2_health_page_dots[i], LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE);
    }
    health_update_page_indicator_4fb1fa(g2_health_page_index);
    audio_terminal_display_status_44ea04(g2_health_scroll_container,
                                         (int32_t)(g2_health_page_index << 8), LV_ANIM_OFF);
    return 0;
}

int32_t Health_ext_Widget_init_4fd7b0(void *parent)
{
    if (g2_health_ext_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_health_ext_fifo);
        g2_health_ext_fifo = NULL;
    }
    g2_health_ext_fifo = ui_common_api_fn_00509c1c();
    if (g2_health_ext_fifo == NULL) {
        HP_LOG0(1u, 0x65fu, fn_init, m_fifo_failed, t_fifo_failed);
        return -1;
    }
    g2_health_is_animating = 0;
    g2_health_page_index = 0u;
    (void)health_ext_widget_page_create_4fc644(parent);
    g2_health_ext_widget_init_flag = 1;
    (void)page_state_sync_health_expanded_50029c(g2_health_page_index + 1u);
    return 0;
}

int32_t health_ext_widget_state_reset_4fd840(void)
{
    if (g2_health_ext_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_health_ext_fifo);
        g2_health_ext_fifo = NULL;
    }
    g2_health_ext_widget_init_flag = 0;
    g2_health_is_animating = 0;
    g2_health_page_index = 0u;
    g2_health_widget_init_flag = 0;
    return 0;
}
