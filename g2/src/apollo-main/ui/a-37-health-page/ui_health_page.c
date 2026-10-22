/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\health\ui_health_page.c
 * (log tag "health.page"), first part. Native 0x4FB1C0..0x4FC1B6 with literal
 * pools 0x4FB700..0x4FB75F, 0x4FBA30..0x4FBA33, 0x4FBC8C..0x4FBC93 (inline "%d"/"-"),
 * 0x4FBE08..0x4FBE0F, 0x4FC1B8..0x4FC1DB, 0x4FC330..0x4FC35F, 0x4FC580..0x4FC5FB
 * (the pools after 0x4FC1DC are shared with the expanded page that follows).
 *
 * Dashboard health tile (widget 5) and the paging/animation glue of the
 * expanded health page. The tile shows the productivity score, steps and
 * calories progress bars (312 px wide, filled in 3 px steps) and three small
 * metrics (a duration value, heart rate, a percentage), read under
 * health_lock_storage from the health record at RAM 0x200f41b4. The expanded
 * page is a two-page vertical scroll container (256 px per page) with page
 * dots; input events that arrive while the scroll animation runs are queued
 * in health_ext_fifo and replayed from the animation-ready callback.
 *
 * Uses single-precision VFP (vcvt.u32.f32 / vdiv.f32): build with profile
 * g2-apollo-main-3. No float crosses a call boundary. */
#include <stddef.h>
#include <stdint.h>

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stock 0x60-byte frame. */
typedef struct {
    void *var;                          /* +0x00 */
    void (*exec_cb)(void *, int32_t);   /* +0x04 */
    void *custom_exec_cb;               /* +0x08 */
    void *start_cb;                     /* +0x0c */
    void (*completed_cb)(void *);       /* +0x10 */
    void *deleted_cb;                   /* +0x14 */
    void *get_value_cb;                 /* +0x18 */
    void *user_data;                    /* +0x1c */
    int32_t (*path_cb)(const void *);   /* +0x20 */
    int32_t start_value;                /* +0x24 */
    int32_t current_value;              /* +0x28 */
    int32_t end_value;                  /* +0x2c */
    int32_t duration;                   /* +0x30 */
    uint8_t rest[0x2c];                 /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* One health metric (0x18 bytes); value is a float, goal 0 means default. */
typedef struct {
    uint8_t head[8];     /* +0x00 */
    uint32_t goal;       /* +0x08 */
    float value;         /* +0x0c */
    uint8_t tail[8];     /* +0x10 */
} g2_health_metric_t;
_Static_assert(sizeof(g2_health_metric_t) == 0x18, "metric record");

/* Health record (RAM 0x200f41b4, 0x5d0 bytes; cleared by 0x5598ae). */
typedef struct {
    g2_health_metric_t metric[8]; /* +0x00 */
    uint8_t ring_state;           /* +0xc0 1 / 3 select the status icon */
    uint8_t rest[0x5d0 - 0xc1];
} g2_health_data_t;
_Static_assert(sizeof(g2_health_data_t) == 0x5d0, "health record");

#define HEALTH_M_STEPS        0 /* goal default 10000 */
#define HEALTH_M_CALORIES     1 /* goal default 2000 */
#define HEALTH_M_DURATION     2 /* shown as hours/minutes on the expanded page */
#define HEALTH_M_HEART_RATE   3 /* "ID_DASHBOARD_HEALTH_BPM" */
#define HEALTH_M_PERCENT      4 /* "%d%%", capped at "100%" */
#define HEALTH_M_PRODUCTIVITY 7 /* "ID_DASHBOARD_HEALTH_PRODUCTIVITY_SCORE" */

/* One tile of the dashboard tileview (RAM 0x200734bc, 6 entries). */
typedef struct {
    void *tile;  /* +0x00 */
    void *frame; /* +0x04 */
} g2_dashboard_tile_t;

#define HEALTH_PAGE_COUNT       2u
#define HEALTH_PAGE_PITCH_SHIFT 8   /* 256 px per page */
#define HEALTH_SCROLL_MS        250
#define HEALTH_SCROLL_MIN_MS    10  /* already there: short no-op animation */
#define HEALTH_BAR_W            312 /* 0x138 */
#define HEALTH_WIDGET_TYPE      5u

#define HEALTH_EVT_TAP          0x0au /* close expanded page */
#define HEALTH_EVT_NEXT         0x44u
#define HEALTH_EVT_PREV         0x45u
#define HEALTH_EVT_46           0x46u
#define HEALTH_EVT_REFRESH      0x47u /* queued by Health_Page_Reflash */
#define HEALTH_EVT_DOUBLE_TAP   0x48u /* close expanded page */
#define HEALTH_EVT_FADEOUT      0x49u

#define LV_OBJ_FLAG_SCROLLABLE  0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_SIZE_CONTENT         0x3fffffff
#define LV_ALIGN_TOP_LEFT       1u
#define LV_ALIGN_TOP_RIGHT      3u
#define LV_ALIGN_OUT_BOTTOM_LEFT 13u
#define LV_ALIGN_OUT_RIGHT_TOP  19u
#define LV_SCROLLBAR_MODE_OFF   0u
#define LV_ANIM_OFF             0u

/* RAM state. */
extern g2_health_data_t g2_health_data;               /* RAM 0x200f41b4 */
extern g2_dashboard_tile_t g2_dashboard_tiles[6];     /* RAM 0x200734bc */
extern void *g2_dashboard_focus_frame;                /* RAM 0x20074b9c expanded-page parent */
extern void *g2_health_page_dots[HEALTH_PAGE_COUNT];  /* RAM 0x20074198 */
extern int32_t g2_health_widget_init_flag;            /* RAM 0x20074c0c widget_health_init_flag */
extern void *g2_health_ext_fifo;                      /* RAM 0x20074c10 health_ext_fifo */
extern int32_t g2_health_is_animating;                /* RAM 0x20074c14 health_is_animating */
extern uint32_t g2_health_tile_index;                 /* RAM 0x20074c18 */
extern int32_t g2_health_ext_widget_init_flag;        /* RAM 0x20074c1c health_ext_widget_init_flag */
extern uint32_t g2_health_page_index;                 /* RAM 0x20074c20 */
extern void *g2_health_tile_root;                     /* RAM 0x20074c24 */
extern void *g2_health_ring_icon;                     /* RAM 0x20074c28 */
extern void *g2_health_score_title;                   /* RAM 0x20074c2c */
extern void *g2_health_score_value;                   /* RAM 0x20074c30 */
extern void *g2_health_steps_icon;                    /* RAM 0x20074c34 */
extern void *g2_health_steps_label;                   /* RAM 0x20074c38 */
extern void *g2_health_steps_bar;                     /* RAM 0x20074c3c */
extern void *g2_health_steps_mask;                    /* RAM 0x20074c40 */
extern void *g2_health_calories_icon;                 /* RAM 0x20074c44 */
extern void *g2_health_calories_label;                /* RAM 0x20074c48 */
extern void *g2_health_calories_bar;                  /* RAM 0x20074c4c */
extern void *g2_health_calories_mask;                 /* RAM 0x20074c50 */
extern void *g2_health_duration_icon;                 /* RAM 0x20074c54 */
extern void *g2_health_duration_label;                /* RAM 0x20074c58 */
extern void *g2_health_heart_icon;                    /* RAM 0x20074c5c */
extern void *g2_health_heart_label;                   /* RAM 0x20074c60 */
extern void *g2_health_percent_icon;                  /* RAM 0x20074c64 */
extern void *g2_health_percent_label;                 /* RAM 0x20074c68 */
extern void *g2_health_scroll_container;              /* RAM 0x20074c6c health_scroll_container */
extern void *audio_uart_ring_primary_head_cell;       /* RAM 0x200746dc: active lv_font_t * */

/* lv_image_dsc_t assets (ROM). */
extern const uint8_t g2_health_img_ring_state1[];     /* ROM 0x7725c4, 24x24 */
extern const uint8_t g2_health_img_ring_state3[];     /* ROM 0x7725a8, 24x24 */
extern const uint8_t g2_health_img_ring_other[];      /* ROM 0x77258c, 24x24 */
extern const uint8_t g2_health_img_steps[];           /* ROM 0x7747ac, 24x24 */
extern const uint8_t g2_health_img_bar[];             /* ROM 0x76bd50, 312x8 */
extern const uint8_t g2_health_img_calories[];        /* ROM 0x769fac, 24x24 */
extern const uint8_t g2_health_img_duration[];        /* ROM 0x771dc8, 24x24 */
extern const uint8_t g2_health_img_heart[];           /* ROM 0x76bddc, 24x24 */
extern const uint8_t g2_health_img_percent[];         /* ROM 0x771e54, 24x24 */

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
extern void audio_uart_page_43f506(void *obj, int32_t w);                     /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                     /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                                /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                                /* lv_obj_align_to */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                         /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);       /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);       /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);       /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);       /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);  /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);    /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);  /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);       /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);       /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);       /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);       /* shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t sel);       /* shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t sel);       /* shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);       /* shadow_spread */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);  /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);    /* text_opa */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);       /* radius */
extern void audio_lv_delete_44d7b8(void *obj);                                /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                                /* lv_obj_clean */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);        /* lv_obj_get_child */
extern int32_t audio_uart_lv_child_count_44ddea(void *obj);                   /* lv_obj_get_child_count */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                 /* lv_obj_set_scrollbar_mode */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                         /* lv_obj_get_scroll_y */
extern void audio_terminal_display_status_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);                  /* lv_anim_init */
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);          /* lv_anim_start */
extern int32_t audio_uart_lv_anim_path_450672(const void *a);                 /* lv_anim_path_ease_out */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_page_498668(void *parent);                            /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);             /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                            /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);     /* lv_label_set_text */

/* Dashboard / health modules. */
extern void Dashboard_Fadeout_Anim_Start_4e8a90(void);
extern void dashboard_focus_frame_shrink_anim_4e92f4(void);
extern void health_ext_widget_page_create_4fc644(void *parent);
extern uint32_t health_lock_storage(void);    /* 0x4ffc32, 1 locked */
extern void health_unlock_storage(void);      /* 0x4ffc90 */
extern int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile_index, uint8_t widget);
extern int32_t page_state_sync_health_expanded_50029c(uint32_t page);
extern int32_t health_data_reset_5598ae(void); /* clears g2_health_data */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push */
extern void ui_common_api_fn_00509c96(void *fifo);                                    /* destroy */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);                                 /* 0 has data */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len);       /* pop */

void lv_obj_set_style_pad_all_4fb1c0(void *obj, int32_t value, uint32_t selector);
void health_update_page_indicator_4fb1fa(uint32_t page_index);
void scroll_container_anim_ready_cb_4fb360(void *anim);
void health_scroll_anim_exec_cb_4fb55a(void *obj, int32_t y);
void health_scroll_container_anim_start_4fb568(void *obj, int32_t target_y, int32_t duration);
void HealthWidget_MainPage_init_4fb760(uint32_t tile_index);

static const char tag[] = "health.page"; /* ROM 0x78c830 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\health\\ui_health_page.c"; /* ROM 0x707b9c */
static const char fn_indicator[] = "health_update_page_indicator"; /* ROM 0x7674b0 */
static const char m_bad_page[] = "health_update_page_indicator: invalid page_index %d"; /* ROM 0x72fd8c */
static const char t_bad_page[] =
    "[health.page]health_update_page_indicator: invalid page_index %d"; /* ROM 0x707be0 */
static const char fn_switch[] = "health_switch_to_page"; /* ROM 0x77d2c4 */
static const char m_no_container[] = "health_scroll_container == NULL, return"; /* ROM 0x750824 */
static const char t_no_container[] =
    "[health.page]health_scroll_container == NULL, return"; /* ROM 0x725418 */
static const char m_bad_target[] = "health_switch_to_page: invalid target_page_index %d"; /* ROM 0x72fdc0 */
static const char t_bad_target[] =
    "[health.page]health_switch_to_page: invalid target_page_index %d"; /* ROM 0x707c24 */
static const char fn_anim_ready[] = "scroll_container_anim_ready_cb"; /* ROM 0x7674d0 */
static const char m_unknown_evt[] = "HealthWidget_event_handler: unknown event type: %d"; /* ROM 0x72fdf4 */
static const char t_unknown_evt[] =
    "[health.page]HealthWidget_event_handler: unknown event type: %d"; /* ROM 0x711024 */
static const char fn_reflash[] = "Health_Page_Reflash"; /* ROM 0x784810 */
static const char m_not_init[] = "widget_health_init_flag == 0, return"; /* ROM 0x75084c */
static const char t_not_init[] = "[health.page]widget_health_init_flag == 0, return"; /* ROM 0x72fe28 */
static const char m_queued[] =
    "health_ext_fifo is not empty, push event to fifo,code = %d"; /* ROM 0x71a980 */
static const char t_queued[] =
    "[health.page]health_ext_fifo is not empty, push event to fifo,code = %d"; /* ROM 0x6feaec */
static const char key_score[] = "ID_DASHBOARD_HEALTH_PRODUCTIVITY_SCORE"; /* ROM 0x750874 */
static const char key_steps[] = "ID_DASHBOARD_HEALTH_STEPS";       /* ROM 0x773f78 */
static const char key_calories[] = "ID_DASHBOARD_HEALTH_CALORIES"; /* ROM 0x7674f0 */
static const char key_bpm[] = "ID_DASHBOARD_HEALTH_BPM";           /* ROM 0x77d2dc */
static const char f_int[] = "%d";          /* ROM 0x4fbc8c / 0x4fc1b8 (inline copies) */
static const char f_dash[] = "-";          /* ROM 0x4fbc90 / 0x4fc1bc */
static const char f_name_int[] = "%s %d";  /* ROM 0x78ecbc */
static const char f_name_dash[] = "%s -";  /* ROM 0x78ecc4 */
static const char f_int_unit[] = "%d%s";   /* ROM 0x78eccc */
static const char f_dash_unit[] = "-%s";   /* ROM 0x4fc330 */
static const char f_full_pct[] = "100%%";  /* ROM 0x78ecd4 */
static const char f_int_pct[] = "%d%%";    /* ROM 0x78ecdc */
static const char f_dash_pct[] = "-%%";    /* ROM 0x4fc338 */

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

static const char *health_text(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* Progress bar fill in pixels: ratio * 312 + 1, rounded down to 3 px, max 312. */
static int32_t health_bar_fill(uint32_t value, uint32_t goal)
{
    float ratio = 0.0f;   /* ROM 0x4fbe08 */
    int32_t fill;

    if (value != 0u)
        ratio = (value < goal) ? (float)value / (float)goal : 1.0f;
    fill = ((int32_t)(ratio * 312.0f + 1.0f) / 3) * 3;   /* 312.0f: ROM 0x4fbe0c */
    if (fill > HEALTH_BAR_W)
        fill = HEALTH_BAR_W;
    return fill;
}

/* IAR out-of-line copy of the LVGL 9.3 lv_obj_style.h inline. */
void lv_obj_set_style_pad_all_4fb1c0(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* Native 0x4fb1f2..0x4fb1f9 (not in the symbol inventory); called by the dashboard reset. */
void health_page_reset_4fb1f2(void)
{
    (void)health_data_reset_5598ae();
}

void health_update_page_indicator_4fb1fa(uint32_t page_index)
{
    uint32_t i;

    if (page_index >= HEALTH_PAGE_COUNT) {
        HP_LOG1(2u, 0xa3u, fn_indicator, m_bad_page, t_bad_page, page_index);
        return;
    }
    for (i = 0; (int32_t)i < (int32_t)HEALTH_PAGE_COUNT; i++) {
        if (g2_health_page_dots[i] == NULL)
            continue;
        if (i == page_index)
            audio_uart_page_44127e(g2_health_page_dots[i], audio_uart_page_44104c(0xffffffu), 0u);
        else
            audio_uart_page_44127e(g2_health_page_dots[i], audio_uart_page_44104c(0x444444u), 0u);
    }
}

void health_switch_to_page_4fb290(uint32_t target_page_index)
{
    if (g2_health_scroll_container == NULL) {
        HP_LOG0(2u, 0xbau, fn_switch, m_no_container, t_no_container);
        return;
    }
    if (target_page_index >= HEALTH_PAGE_COUNT) {
        HP_LOG1(2u, 0xbfu, fn_switch, m_bad_target, t_bad_target, target_page_index);
        return;
    }
    if (target_page_index != g2_health_page_index && g2_health_is_animating == 0) {
        g2_health_page_index = target_page_index;
        health_update_page_indicator_4fb1fa(g2_health_page_index);
        (void)page_state_sync_health_expanded_50029c(g2_health_page_index + 1u);
        health_scroll_container_anim_start_4fb568(
            g2_health_scroll_container, (int32_t)(target_page_index << HEALTH_PAGE_PITCH_SHIFT),
            HEALTH_SCROLL_MS);
    }
}

static void health_close_expanded_page(void)
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

/* lv_anim completed_cb of the page scroll: clears the busy flag and replays
 * one event that was queued while the animation ran. */
void scroll_container_anim_ready_cb_4fb360(void *anim)
{
    uint8_t evt[10];

    (void)anim;
    g2_health_is_animating = 0;
    if (g2_health_ext_fifo == NULL || ui_common_api_fn_00509dfa(g2_health_ext_fifo) != 0 ||
        g2_health_ext_widget_init_flag != 1)
        return;
    aeabi_memset_43c0e4(evt, sizeof evt, 0);
    aeabi_memset_43c0e4(evt, sizeof evt, 0);
    (void)ui_common_api_fn_00509e14(g2_health_ext_fifo, evt, 5u);
    switch (evt[0]) {
    case HEALTH_EVT_TAP:
        health_close_expanded_page();
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
    case HEALTH_EVT_REFRESH:
        if (g2_health_ext_widget_init_flag == 1 && g2_health_ext_fifo != NULL &&
            g2_health_is_animating == 0 && g2_dashboard_focus_frame != NULL) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            health_ext_widget_page_create_4fc644(g2_dashboard_focus_frame);
        }
        break;
    case HEALTH_EVT_DOUBLE_TAP:
        health_close_expanded_page();
        break;
    case HEALTH_EVT_FADEOUT:
        Dashboard_Fadeout_Anim_Start_4e8a90();
        g2_health_ext_widget_init_flag = 0;
        g2_health_is_animating = 0;
        break;
    default:
        HP_LOG1(2u, 0x146u, fn_anim_ready, m_unknown_evt, t_unknown_evt, (uint32_t)evt[0]);
        break;
    }
}

/* lv_anim exec_cb: y is the scroll position of the container. */
void health_scroll_anim_exec_cb_4fb55a(void *obj, int32_t y)
{
    if (obj != NULL)
        audio_terminal_display_status_44ea04(obj, y, LV_ANIM_OFF);
}

void health_scroll_container_anim_start_4fb568(void *obj, int32_t target_y, int32_t duration)
{
    g2_lv_anim_t a;
    int32_t cur;

    if (obj == NULL)
        return;
    audio_uart_page_43f66c(g2_health_scroll_container);
    cur = audio_uart_lv_obj_y_44e498(obj);
    if (target_y == cur)
        duration = HEALTH_SCROLL_MIN_MS;
    if (duration < 1) {
        audio_terminal_display_status_44ea04(obj, target_y, LV_ANIM_OFF);
        return;
    }
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, cur, target_y);
    a.duration = duration;
    a.exec_cb = health_scroll_anim_exec_cb_4fb55a;
    a.completed_cb = scroll_container_anim_ready_cb_4fb360;
    a.path_cb = audio_uart_lv_anim_path_450672;
    g2_health_is_animating = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Rebuilds the tile; refreshes the expanded page now, or queues the refresh
 * while its scroll animation runs. The dashboard passes the payload, which
 * stock does not read. */
int32_t Health_Page_Reflash_4fb5e8(const uint8_t *data, uint32_t len)
{
    uint8_t evt[5];

    (void)data;
    (void)len;
    if (g2_health_widget_init_flag == 0) {
        HP_LOG0(2u, 0x233u, fn_reflash, m_not_init, t_not_init);
        return 0;
    }
    if (g2_dashboard_tiles[g2_health_tile_index].frame != NULL)
        audio_uart_page_44d878(g2_dashboard_tiles[g2_health_tile_index].frame);
    HealthWidget_MainPage_init_4fb760(g2_health_tile_index);
    if (g2_health_ext_widget_init_flag == 1 && g2_health_ext_fifo != NULL &&
        g2_dashboard_focus_frame != NULL) {
        if (g2_health_is_animating == 0) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            health_ext_widget_page_create_4fc644(g2_dashboard_focus_frame);
        } else {
            evt[0] = HEALTH_EVT_REFRESH;
            evt[1] = 0;
            evt[2] = 0;
            evt[3] = 0;
            evt[4] = 0;
            (void)ui_common_api_fn_00509ca2(g2_health_ext_fifo, evt, 5u);
            HP_LOG1(3u, 0x248u, fn_reflash, m_queued, t_queued, (uint32_t)evt[0]);
        }
    }
    return 0;
}

/* 24x24 icon with SCROLLABLE cleared and ADV_HITTEST set. */
static void *health_icon(void *parent, const void *src_img)
{
    void *img = audio_uart_page_498668(parent);

    audio_uart_page_498680(img, src_img);
    audio_uart_page_43f506(img, 24);
    audio_uart_page_43f568(img, 24);
    return img;
}

static void health_icon_flags(void *img)
{
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
}

/* Black mask over the unfilled right part of a progress bar image. */
static void *health_bar_mask(void *parent, void *bar, int32_t fill)
{
    void *mask = audio_uart_page_43de82(parent);

    audio_uart_page_43f506(mask, HEALTH_BAR_W - fill);
    audio_uart_page_43f568(mask, 8);
    audio_uart_page_43f6d6(mask, bar, LV_ALIGN_TOP_LEFT, fill, 0);
    audio_uart_page_44127e(mask, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(mask, 0xbeu, 0u);
    lv_obj_set_style_pad_all_4fb1c0(mask, 0, 0u);
    audio_uart_page_44131c(mask, 0, 0u);
    audio_uart_page_44146a(mask, 0, 0u);
    audio_uart_page_43dfa4(mask, LV_OBJ_FLAG_SCROLLABLE);
    return mask;
}

void HealthWidget_MainPage_init_4fb760(uint32_t tile_index)
{
    char text[32];
    uint32_t score, steps, steps_goal, calories, calories_goal;
    int32_t fill;

    g2_health_widget_init_flag = 1;
    g2_health_tile_index = tile_index;
    aeabi_memset_43c0e4(text, sizeof text, 0);

    g2_health_tile_root = audio_uart_page_43de82(g2_dashboard_tiles[g2_health_tile_index].frame);
    audio_uart_page_43f09a(g2_health_tile_root, 20, 16);
    audio_uart_page_43f506(g2_health_tile_root, 315);
    audio_uart_page_43f568(g2_health_tile_root, 256);
    audio_uart_page_44127e(g2_health_tile_root, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_health_tile_root, 0u, 0u);
    audio_uart_page_44131c(g2_health_tile_root, 0, 0u);
    audio_uart_page_44133a(g2_health_tile_root, 0, 0u);
    audio_uart_page_441378(g2_health_tile_root, 0, 0u);
    audio_uart_page_441386(g2_health_tile_root, 0, 0u);
    audio_uart_page_4413b0(g2_health_tile_root, 0, 0u);
    audio_uart_page_441394(g2_health_tile_root, 0, 0u);
    audio_uart_page_4413a2(g2_health_tile_root, 0, 0u);
    lv_obj_set_style_pad_all_4fb1c0(g2_health_tile_root, 0, 0u);
    audio_uart_page_44120e(g2_health_tile_root, 0, 0u);
    audio_uart_page_44121c(g2_health_tile_root, 0, 0u);
    audio_uart_page_44122a(g2_health_tile_root, 0, 0u);
    audio_uart_page_441238(g2_health_tile_root, 0, 0u);
    audio_uart_page_44146a(g2_health_tile_root, 0, 0u);
    audio_uart_page_4412ec(g2_health_tile_root, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44140e(g2_health_tile_root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(g2_health_tile_root, 0xffu, 0u);
    audio_uart_page_43dfa4(g2_health_tile_root, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e368(g2_health_tile_root, LV_SCROLLBAR_MODE_OFF);

    /* Ring status icon + productivity score. */
    g2_health_ring_icon = audio_uart_page_498668(g2_health_tile_root);
    (void)health_lock_storage();
    if (g2_health_data.ring_state == 1u)
        audio_uart_page_498680(g2_health_ring_icon, g2_health_img_ring_state1);
    else if (g2_health_data.ring_state == 3u)
        audio_uart_page_498680(g2_health_ring_icon, g2_health_img_ring_state3);
    else
        audio_uart_page_498680(g2_health_ring_icon, g2_health_img_ring_other);
    health_unlock_storage();
    audio_uart_page_43f506(g2_health_ring_icon, 24);
    audio_uart_page_43f568(g2_health_ring_icon, 24);
    audio_uart_page_43f0e0(g2_health_ring_icon, 0);
    audio_uart_page_43f142(g2_health_ring_icon, 2);
    health_icon_flags(g2_health_ring_icon);

    g2_health_score_title = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_score_title, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_health_score_title, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_score_title, g2_health_ring_icon, LV_ALIGN_OUT_RIGHT_TOP, 8, -2);
    (void)audio_uart_page_49942e(g2_health_score_title, health_text(key_score));
    audio_uart_page_44140e(g2_health_score_title, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_health_score_title, audio_uart_ring_primary_head_cell, 0u);

    (void)health_lock_storage();
    score = (uint32_t)g2_health_data.metric[HEALTH_M_PRODUCTIVITY].value;
    health_unlock_storage();
    if (score == 0u)
        (void)audio_ble_format_to_buffer(text, f_dash);
    else
        (void)audio_ble_format_to_buffer(text, f_int, score);
    g2_health_score_value = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_score_value, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_health_score_value, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(g2_health_score_value, LV_ALIGN_TOP_RIGHT, 0, 0);
    (void)audio_uart_page_49942e(g2_health_score_value, text);
    audio_uart_page_44140e(g2_health_score_value, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_health_score_value, audio_uart_ring_primary_head_cell, 0u);

    /* Steps. */
    (void)health_lock_storage();
    steps = (uint32_t)g2_health_data.metric[HEALTH_M_STEPS].value;
    steps_goal = g2_health_data.metric[HEALTH_M_STEPS].goal;
    if (steps_goal == 0u)
        steps_goal = 10000u;
    health_unlock_storage();
    g2_health_steps_icon = health_icon(g2_health_tile_root, g2_health_img_steps);
    audio_uart_page_43f0e0(g2_health_steps_icon, 0);
    audio_uart_page_43f142(g2_health_steps_icon, 55);
    health_icon_flags(g2_health_steps_icon);
    g2_health_steps_label = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_steps_label, 315);
    audio_uart_page_43f568(g2_health_steps_label, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_steps_label, g2_health_steps_icon, LV_ALIGN_OUT_RIGHT_TOP, 8, -2);
    audio_uart_page_44140e(g2_health_steps_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_health_steps_label, audio_uart_ring_primary_head_cell, 0u);
    if (steps == 0u)
        (void)audio_ble_format_to_buffer(text, f_name_dash, health_text(key_steps));
    else
        (void)audio_ble_format_to_buffer(text, f_name_int, health_text(key_steps), steps);
    (void)audio_uart_page_49942e(g2_health_steps_label, text);
    g2_health_steps_bar = audio_uart_page_498668(g2_health_tile_root);
    audio_uart_page_498680(g2_health_steps_bar, g2_health_img_bar);
    audio_uart_page_43f506(g2_health_steps_bar, HEALTH_BAR_W);
    audio_uart_page_43f568(g2_health_steps_bar, 8);
    audio_uart_page_43f6d6(g2_health_steps_bar, g2_health_steps_icon, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 10);
    health_icon_flags(g2_health_steps_bar);
    fill = health_bar_fill(steps, steps_goal);
    g2_health_steps_mask = health_bar_mask(g2_health_tile_root, g2_health_steps_bar, fill);

    /* Calories. */
    (void)health_lock_storage();
    calories = (uint32_t)g2_health_data.metric[HEALTH_M_CALORIES].value;
    calories_goal = g2_health_data.metric[HEALTH_M_CALORIES].goal;
    if (calories_goal == 0u)
        calories_goal = 2000u;
    health_unlock_storage();
    g2_health_calories_icon = health_icon(g2_health_tile_root, g2_health_img_calories);
    audio_uart_page_43f0e0(g2_health_calories_icon, 0);
    audio_uart_page_43f142(g2_health_calories_icon, 117);
    health_icon_flags(g2_health_calories_icon);
    g2_health_calories_label = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_calories_label, 315);
    audio_uart_page_43f568(g2_health_calories_label, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_calories_label, g2_health_calories_icon, LV_ALIGN_OUT_RIGHT_TOP,
                           8, -2);
    audio_uart_page_44140e(g2_health_calories_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_health_calories_label, audio_uart_ring_primary_head_cell, 0u);
    if (calories == 0u)
        (void)audio_ble_format_to_buffer(text, f_name_dash, health_text(key_calories));
    else
        (void)audio_ble_format_to_buffer(text, f_name_int, health_text(key_calories), calories);
    (void)audio_uart_page_49942e(g2_health_calories_label, text);
    g2_health_calories_bar = audio_uart_page_498668(g2_health_tile_root);
    audio_uart_page_498680(g2_health_calories_bar, g2_health_img_bar);
    audio_uart_page_43f506(g2_health_calories_bar, HEALTH_BAR_W);
    audio_uart_page_43f568(g2_health_calories_bar, 8);
    audio_uart_page_43f6d6(g2_health_calories_bar, g2_health_calories_icon, LV_ALIGN_OUT_BOTTOM_LEFT,
                           0, 10);
    health_icon_flags(g2_health_calories_bar);
    fill = health_bar_fill(calories, calories_goal);
    g2_health_calories_mask = health_bar_mask(g2_health_tile_root, g2_health_calories_bar, fill);

    /* Bottom row: duration, heart rate, percentage. */
    g2_health_duration_icon = health_icon(g2_health_tile_root, g2_health_img_duration);
    audio_uart_page_43f0e0(g2_health_duration_icon, 0);
    audio_uart_page_43f142(g2_health_duration_icon, 188);
    health_icon_flags(g2_health_duration_icon);
    g2_health_duration_label = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_duration_label, 130);
    audio_uart_page_43f568(g2_health_duration_label, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_duration_label, g2_health_duration_icon,
                           LV_ALIGN_OUT_BOTTOM_LEFT, 0, 6);
    (void)health_lock_storage();
    if (g2_health_data.metric[HEALTH_M_DURATION].value <= 0.0f)
        (void)audio_ble_format_to_buffer(text, f_dash);
    else
        (void)audio_ble_format_to_buffer(text, f_int,
                                         (uint32_t)g2_health_data.metric[HEALTH_M_DURATION].value);
    (void)audio_uart_page_49942e(g2_health_duration_label, text);
    health_unlock_storage();
    audio_uart_page_44143e(g2_health_duration_label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44140e(g2_health_duration_label, audio_uart_page_44104c(0xffffffu), 0u);

    g2_health_heart_icon = health_icon(g2_health_tile_root, g2_health_img_heart);
    audio_uart_page_43f6d6(g2_health_heart_icon, g2_health_duration_icon, LV_ALIGN_OUT_RIGHT_TOP,
                           107, 0);
    health_icon_flags(g2_health_heart_icon);
    g2_health_heart_label = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_heart_label, 123);
    audio_uart_page_43f568(g2_health_heart_label, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_heart_label, g2_health_heart_icon, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 6);
    (void)health_lock_storage();
    if (g2_health_data.metric[HEALTH_M_HEART_RATE].value <= 0.0f)
        (void)audio_ble_format_to_buffer(text, f_dash_unit, health_text(key_bpm));
    else
        (void)audio_ble_format_to_buffer(text, f_int_unit,
                                         (uint32_t)g2_health_data.metric[HEALTH_M_HEART_RATE].value,
                                         health_text(key_bpm));
    (void)audio_uart_page_49942e(g2_health_heart_label, text);
    health_unlock_storage();
    audio_uart_page_44140e(g2_health_heart_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_health_heart_label, audio_uart_ring_primary_head_cell, 0u);

    g2_health_percent_icon = health_icon(g2_health_tile_root, g2_health_img_percent);
    audio_uart_page_43f6d6(g2_health_percent_icon, g2_health_heart_icon, LV_ALIGN_OUT_RIGHT_TOP,
                           107, 0);
    health_icon_flags(g2_health_percent_icon);
    g2_health_percent_label = audio_uart_page_499416(g2_health_tile_root);
    audio_uart_page_43f506(g2_health_percent_label, 53);
    audio_uart_page_43f568(g2_health_percent_label, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(g2_health_percent_label, g2_health_percent_icon, LV_ALIGN_OUT_BOTTOM_LEFT,
                           0, 6);
    (void)health_lock_storage();
    if (g2_health_data.metric[HEALTH_M_PERCENT].value < 100.0f) {   /* ROM 0x4fc334 */
        if (g2_health_data.metric[HEALTH_M_PERCENT].value <= 0.0f)
            (void)audio_ble_format_to_buffer(text, f_dash_pct);
        else
            (void)audio_ble_format_to_buffer(text, f_int_pct,
                                             (uint32_t)g2_health_data.metric[HEALTH_M_PERCENT].value);
    } else {
        (void)audio_ble_format_to_buffer(text, f_full_pct);
    }
    (void)audio_uart_page_49942e(g2_health_percent_label, text);
    health_unlock_storage();
    audio_uart_page_44140e(g2_health_percent_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_health_percent_label, audio_uart_ring_primary_head_cell, 0u);
}
