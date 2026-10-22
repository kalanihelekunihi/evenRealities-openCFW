/* Dashboard main screen build, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c.
 * Native 0x4e92f4..0x4e934d (focus frame shrink animation) and 0x4e93e4..0x4e9ce7
 * (ui_Screen1_screen_init); literal pool 0x4e9ce8..0x4e9dd3 (plus one word at 0x4e9388).
 *
 * The screen is a 576x288 root, a transparent content layer that the watchface
 * manager fills, one 4x4 tile indicator dot per dashboard widget (LEFT_MID column,
 * first dot white, the rest 0x222222 at opa 150), and an optional vertical
 * tileview with one 352x288 tile per widget. Each tile gets a white 1 px frame
 * (radius 6). A second, hidden 352x288 "focus frame" sits on top of the root;
 * expanded widget pages (stock, quicklist, ...) are built inside it and it is
 * shrunk back from 576 to 352 px when such a page closes.
 *
 * Layout record (dashboard_layout_get_current, RAM 0x200e7934):
 *   +0 u8 version, +1 u8 widget count, +2.. u8 widget type per tile
 *   (0 news, 1 stock, 2 calendar, 3 health, 4 quicklist). */
#include <stdint.h>
#include <stddef.h>

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_CLICKABLE 0x02u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_ALIGN_TOP_LEFT 1u
#define LV_ALIGN_LEFT_MID 7u
#define LV_DIR_VER 0x0cu
#define LV_SCROLLBAR_MODE_OFF 0u

#define SCREEN_W 0x240
#define SCREEN_H 0x120
#define TILE_W 0x160
#define TILE_H 0x120
#define TILEVIEW_H 0x130
#define TILE_PITCH 0x130
#define MAX_TILES 6u

enum {
    WIDGET_NEWS = 0u,
    WIDGET_STOCK = 1u,
    WIDGET_CALENDAR = 2u,
    WIDGET_HEALTH = 3u,
    WIDGET_QUICKLIST = 4u,
};

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stack frame. */
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

/* Watchface placement config (RAM 0x2000420c). */
typedef struct {
    uint32_t manager_arg;     /* +0x00 handed to dashboard_watchface_manager_init */
    int32_t tileview_x;       /* +0x04 */
    uint8_t frame_align;      /* +0x08 lv_align_t of the focus frame */
    uint8_t reserved_09[3];
    int32_t indicator_x;      /* +0x0c */
    int32_t width_scale;      /* +0x10 used by the shrink animation exec callback */
    uint32_t tileview_enable; /* +0x14 */
} g2_dashboard_watchface_cfg_t;
_Static_assert(sizeof(g2_dashboard_watchface_cfg_t) == 0x18, "watchface cfg");

typedef struct {
    uint8_t version;
    uint8_t widget_count;
    uint8_t widget_type[];
} g2_dashboard_layout_t;

/* One tile of the dashboard tileview (RAM 0x200734bc, 6 entries). */
typedef struct {
    void *tile;  /* +0x00 lv_tileview tile */
    void *frame; /* +0x04 1 px frame drawn inside the tile */
} g2_dashboard_tile_t;

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);            /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                       /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                                  /* lv_obj_update_layout */
extern void audio_uart_page_43f6ac(void *obj, uint32_t align);                  /* lv_obj_set_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                                  /* lv_obj_align_to */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);         /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);         /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);         /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);         /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);    /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);      /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);    /* border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t opa, uint32_t sel);      /* border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);         /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);         /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);         /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);         /* shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t sel);         /* shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t sel);         /* shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);         /* shadow_spread */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);    /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);      /* text_opa */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);         /* radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                   /* lv_obj_set_scrollbar_mode */
extern void audio_terminal_display_status_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);                    /* lv_anim_init */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);            /* lv_anim_start */
extern int32_t audio_uart_lv_anim_path_45065a(const void *a);                   /* lv_anim_path_linear */
extern int32_t audio_uart_lv_anim_path_450672(const void *a);                   /* lv_anim_path_ease_out */
extern void *lv_tileview_create_50fef8(void *parent);
extern void *lv_tileview_add_tile_50ff0e(void *tileview, uint8_t col, uint8_t row, uint32_t dir);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

/* Dashboard helpers in this TU / neighbouring dashboard units. */
extern void dashboard_obj_set_style_pad_all_4e75b0(void *obj, int32_t v, uint32_t sel); /* static pad_all copy */
extern void dashboard_apply_layout_4e75e2(const g2_dashboard_layout_t *layout);
extern void update_tile_indicators_4e772c(uint32_t tile_index);
extern void dashboard_tiles_load_4e9280(void);
extern void dashboard_focus_frame_width_exec_cb_4e82ec(void *obj, int32_t width);
extern void dashboard_focus_frame_shrink_ready_cb_4e8370(void *anim);
extern void page_fade_in_anim_exec_cb_4e79a8(void *obj, int32_t opa);
extern void page_fade_in_anim_ready_cb_4e79b4(void *anim);
extern void dashboard_ext_apply_layout_pb_to_runtime_502174(void);
extern const g2_dashboard_layout_t *dashboard_layout_get_current_558142(void);
extern int32_t dashboard_layout_equal_558314(const g2_dashboard_layout_t *a, const void *b);
extern int32_t dashboard_watchface_manager_init(void *parent, uint32_t arg); /* 0x5004b2 */
extern uint32_t audio_uart_service_mode(void);                               /* 0x45a570 */
extern uint8_t dashboard_widget_page_type_4ffeb4(uint32_t tile_index);
extern int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile_index, uint8_t widget);
extern void Widget_News_init_4f091c(uint32_t tile_index);
extern int32_t StockWidget_MainPage_init_4ec2dc(uint32_t tile_index);
extern int32_t CalendarWidget_MainPage_init_4edac4(uint32_t tile_index);
extern void HealthWidget_MainPage_init_4fb760(uint32_t tile_index);
extern void QuicklistWidget_MainPage_init_4f891c(uint32_t tile_index);
extern void *ui_common_api_fn_00509c1c(void);                       /* fifo create */
extern int32_t ui_common_api_fn_00509f7a(int32_t *x, int32_t *y);   /* page offset */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern void *g2_dashboard_input_fifo;                            /* RAM 0x20074b98 */
extern void *g2_dashboard_focus_frame;                           /* RAM 0x20074b9c */
extern volatile uint32_t g2_dashboard_auto_close_hold_20074ba0;  /* RAM 0x20074ba0 */
extern void *g2_dashboard_content;                               /* RAM 0x20074ba4 */
extern void *g2_dashboard_tileview;                              /* RAM 0x20074ba8 */
extern uint32_t g2_dashboard_tile_index;                         /* RAM 0x20074bac */
extern int32_t g2_dashboard_last_saved_tile;                     /* RAM 0x20074bb4 */
extern uint32_t g2_dashboard_anim_running;                       /* RAM 0x20074bc0 */
extern uint32_t g2_dashboard_layout_saved_valid;                 /* RAM 0x20074b94 */
extern uint8_t g2_dashboard_layout_saved[];                      /* RAM 0x20120134 */
extern void *volatile g2_dashboard_root_200743b8;                /* RAM 0x200743b8 dashboard screen object */
extern g2_dashboard_watchface_cfg_t g2_dashboard_watchface_cfg;  /* RAM 0x2000420c */
extern int32_t g2_dashboard_tile_indicator_count;                /* RAM 0x2000423c */
extern void *g2_dashboard_tile_indicators[];                     /* RAM 0x20073c50, 6 entries */
extern g2_dashboard_tile_t g2_dashboard_tiles[MAX_TILES];        /* RAM 0x200734bc */
extern const int32_t g2_dashboard_indicator_size;                /* ROM 0x78f4fc = 4 */
extern const int32_t g2_dashboard_indicator_pitch;               /* ROM 0x78f500 = 16 */

static const char module_tag[] = "dashborad.ui"; /* ROM 0x789d20 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_DashBaord_Main_Screen.c"; /* ROM 0x6e1d2c */
static const char init_fn[] = "ui_Screen1_screen_init"; /* ROM 0x77d204 */
static const char layout_changed[] = "dashboard layout changed, reset last_saved_tile_index=%d -> 0"; /* ROM 0x710ee4 */
static const char layout_changed_short[] =
    "[dashborad.ui]dashboard layout changed, reset last_saved_tile_index=%d -> 0"; /* ROM 0x6f7240 */
static const char watchface_failed[] = "dashboard_watchface_manager_init failed"; /* ROM 0x750734 */
static const char watchface_failed_short[] = "[dashborad.ui]dashboard_watchface_manager_init failed"; /* ROM 0x725370 */
static const char skip_indicators[] = "Dashboard init: widget_count=%d, skip tile_indicators creation"; /* ROM 0x710f24 */
static const char skip_indicators_short[] =
    "[dashborad.ui]Dashboard init: widget_count=%d, skip tile_indicators creation"; /* ROM 0x6f0a38 */
static const char unknown_widget[] = "unknown widget type %d at tile %d"; /* ROM 0x75c2a0 */
static const char unknown_widget_short[] = "[dashborad.ui]unknown widget type %d at tile %d"; /* ROM 0x73a724 */
static const char restored_tile[] = "Dashboard init: restored to saved tile index = %d (y=%d)"; /* ROM 0x71a890 */
static const char restored_tile_short[] =
    "[dashborad.ui]Dashboard init: restored to saved tile index = %d (y=%d)"; /* ROM 0x6fea5c */
static const char start_tile0[] =
    "Dashboard init: starting from tile 0 (last_saved=%d, indicator_count=%d)"; /* ROM 0x6f728c */
static const char start_tile0_short[] =
    "[dashborad.ui]Dashboard init: starting from tile 0 (last_saved=%d, indicator_count=%d)"; /* ROM 0x6e5820 */
static const char sync_failed[] =
    "Failed to sync dashboard main page state: tile_index=%d, widget_type=%d"; /* ROM 0x6fe8ac */
static const char sync_failed_short[] =
    "[dashborad.ui]Failed to sync dashboard main page state: tile_index=%d, widget_type=%d"; /* ROM 0x6e56c0 */
static const char fade_started[] = "Dashboard screen fade-in animation started (100ms)"; /* ROM 0x72fc88 */
static const char fade_started_short[] =
    "[dashborad.ui]Dashboard screen fade-in animation started (100ms)"; /* ROM 0x707ad0 */

static void log0(uint8_t level, uint32_t line, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, init_fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, msg_short, msg_short);
}

static void log1(uint8_t level, uint32_t line, const char *msg, const char *msg_short, uint32_t a)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, init_fn, line, msg, a);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x00400000u, msg_short, msg_short, a);
}

static void log2(uint8_t level, uint32_t line, const char *msg, const char *msg_short, uint32_t a,
                 uint32_t b)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, init_fn, line, msg, a, b);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x00800000u, msg_short, msg_short, a, b);
}

/* Shrink the focus frame from full screen width back to one tile (250 ms,
 * ease-out); called when an expanded widget page closes. */
void dashboard_focus_frame_shrink_anim_4e92f4(void)
{
    g2_lv_anim_t a;

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_dashboard_focus_frame;
    audio_uart_lv_anim_values_4506ce(&a, SCREEN_W, TILE_W);
    a.duration = 250;
    a.exec_cb = dashboard_focus_frame_width_exec_cb_4e82ec;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = dashboard_focus_frame_shrink_ready_cb_4e8370;
    g2_dashboard_anim_running = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* ui_Screen1_screen_init. */
void dashboard_main_screen_4e93e4(void *parent)
{
    void *root;
    void *content;
    const g2_dashboard_layout_t *layout;
    g2_lv_anim_t a;
    int32_t x;
    int32_t y;
    int32_t i;

    if (g2_dashboard_input_fifo == NULL)
        g2_dashboard_input_fifo = ui_common_api_fn_00509c1c();
    g2_dashboard_anim_running = 0u;

    root = audio_uart_page_43de82(parent);
    g2_dashboard_root_200743b8 = root;
    audio_uart_page_43dfa4(g2_dashboard_root_200743b8, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f506(g2_dashboard_root_200743b8, SCREEN_W);
    audio_uart_page_43f568(g2_dashboard_root_200743b8, SCREEN_H);
    audio_uart_page_43f09a(g2_dashboard_root_200743b8, 0, 0);
    audio_uart_page_43dfa4(g2_dashboard_root_200743b8, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44127e(g2_dashboard_root_200743b8, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_dashboard_root_200743b8, 0xffu, 0u);
    audio_uart_page_44140e(g2_dashboard_root_200743b8, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(g2_dashboard_root_200743b8, 0xffu, 0u);
    audio_uart_page_4412ec(g2_dashboard_root_200743b8, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44131c(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_44133a(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_441378(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_441386(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_4413b0(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_441394(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_4413a2(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_44146a(g2_dashboard_root_200743b8, 0, 0u);
    dashboard_obj_set_style_pad_all_4e75b0(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_44120e(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_44121c(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_44122a(g2_dashboard_root_200743b8, 0, 0u);
    audio_uart_page_441238(g2_dashboard_root_200743b8, 0, 0u);

    content = audio_uart_page_43de82(g2_dashboard_root_200743b8);
    g2_dashboard_content = content;
    audio_uart_page_43dfa4(g2_dashboard_content, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f506(g2_dashboard_content, SCREEN_W);
    audio_uart_page_43f568(g2_dashboard_content, SCREEN_H);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_dashboard_content, x, y);
    audio_uart_page_44127e(g2_dashboard_content, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_dashboard_content, 0u, 0u);
    audio_uart_page_44131c(g2_dashboard_content, 0, 0u);
    audio_uart_page_44133a(g2_dashboard_content, 0, 0u);
    audio_uart_page_441378(g2_dashboard_content, 0, 0u);
    audio_uart_page_441386(g2_dashboard_content, 0, 0u);
    audio_uart_page_4413b0(g2_dashboard_content, 0, 0u);
    audio_uart_page_441394(g2_dashboard_content, 0, 0u);
    audio_uart_page_4413a2(g2_dashboard_content, 0, 0u);
    dashboard_obj_set_style_pad_all_4e75b0(g2_dashboard_content, 0, 0u);
    audio_uart_page_44120e(g2_dashboard_content, 0, 0u);
    audio_uart_page_44121c(g2_dashboard_content, 0, 0u);
    audio_uart_page_44122a(g2_dashboard_content, 0, 0u);
    audio_uart_page_441238(g2_dashboard_content, 0, 0u);
    audio_uart_page_44146a(g2_dashboard_content, 0, 0u);
    audio_uart_page_4412ec(g2_dashboard_content, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44140e(g2_dashboard_content, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(g2_dashboard_content, 0xffu, 0u);

    dashboard_ext_apply_layout_pb_to_runtime_502174();
    layout = dashboard_layout_get_current_558142();
    dashboard_apply_layout_4e75e2(layout);
    if (g2_dashboard_layout_saved_valid != 0u &&
        dashboard_layout_equal_558314(layout, g2_dashboard_layout_saved) == 0) {
        log1(3u, 0x6bfu, layout_changed, layout_changed_short, (uint32_t)g2_dashboard_last_saved_tile);
        g2_dashboard_last_saved_tile = 0;
    }
    if (g2_dashboard_last_saved_tile >= (int32_t)layout->widget_count)
        g2_dashboard_last_saved_tile = 0;

    if (dashboard_watchface_manager_init(g2_dashboard_content, g2_dashboard_watchface_cfg.manager_arg) != 0)
        log0(1u, 0x6ccu, watchface_failed, watchface_failed_short);

    /* Tile indicator dots. */
    g2_dashboard_tile_indicator_count = layout->widget_count;
    (void)aeabi_memset_43c0e4(g2_dashboard_tile_indicators, MAX_TILES * sizeof(void *), 0);
    if (g2_dashboard_tile_indicator_count >= 2) {
        for (i = 0; i < g2_dashboard_tile_indicator_count; i++) {
            int32_t dot_y;

            g2_dashboard_tile_indicators[i] = audio_uart_page_43de82(g2_dashboard_content);
            audio_uart_page_43f4c0(g2_dashboard_tile_indicators[i], g2_dashboard_indicator_size,
                                   g2_dashboard_indicator_size);
            audio_uart_page_44131c(g2_dashboard_tile_indicators[i], 0, 0u);
            audio_uart_page_44146a(g2_dashboard_tile_indicators[i], 0, 0u);
            audio_uart_page_44130c(g2_dashboard_tile_indicators[i], 0u, 0u);
            dot_y = (g2_dashboard_indicator_pitch * (i * 2 - g2_dashboard_tile_indicator_count + 1)) / 2;
            audio_uart_page_43f6ac(g2_dashboard_tile_indicators[i], LV_ALIGN_LEFT_MID);
            audio_uart_page_43f09a(g2_dashboard_tile_indicators[i], g2_dashboard_watchface_cfg.indicator_x, dot_y);
            if (i == 0) {
                audio_uart_page_44127e(g2_dashboard_tile_indicators[0], audio_uart_page_44104c(0xffffffu), 0u);
                audio_uart_page_44129e(g2_dashboard_tile_indicators[0], 0xffu, 0u);
            } else {
                audio_uart_page_44127e(g2_dashboard_tile_indicators[i], audio_uart_page_44104c(0x222222u), 0u);
                audio_uart_page_44129e(g2_dashboard_tile_indicators[i], 150u, 0u);
            }
            audio_uart_page_43dfa4(g2_dashboard_tile_indicators[i], LV_OBJ_FLAG_CLICKABLE);
        }
    } else {
        log1(3u, 0x70au, skip_indicators, skip_indicators_short, (uint32_t)g2_dashboard_tile_indicator_count);
    }

    g2_dashboard_auto_close_hold_20074ba0 = 0u;
    g2_dashboard_tileview = NULL;
    g2_dashboard_focus_frame = NULL;
    if (g2_dashboard_watchface_cfg.tileview_enable != 0u) {
        int32_t tile;

        g2_dashboard_tileview = lv_tileview_create_50fef8(g2_dashboard_root_200743b8);
        audio_uart_page_44127e(g2_dashboard_tileview, audio_uart_page_44104c(0x000000u), 0u);
        audio_uart_page_43f4c0(g2_dashboard_tileview, TILE_W, TILEVIEW_H);
        (void)ui_common_api_fn_00509f7a(&x, &y);
        audio_uart_page_43f09a(g2_dashboard_tileview, g2_dashboard_watchface_cfg.tileview_x, y);
        audio_uart_page_44e368(g2_dashboard_tileview, LV_SCROLLBAR_MODE_OFF);
        audio_uart_page_44131c(g2_dashboard_tileview, 0, 0u);
        audio_uart_page_44146a(g2_dashboard_tileview, 0, 0u);
        dashboard_obj_set_style_pad_all_4e75b0(g2_dashboard_tileview, 0, 0u);
        audio_uart_page_43f66c(g2_dashboard_tileview);
        dashboard_tiles_load_4e9280();

        for (tile = 0; tile < g2_dashboard_tile_indicator_count; tile++) {
            g2_dashboard_tile_t *t = &g2_dashboard_tiles[tile];

            t->tile = lv_tileview_add_tile_50ff0e(g2_dashboard_tileview, 0u, (uint8_t)tile, LV_DIR_VER);
            dashboard_obj_set_style_pad_all_4e75b0(t->tile, 0, 0u);
            t->frame = audio_uart_page_43de82(t->tile);
            audio_uart_page_43f4c0(t->frame, TILE_W, TILE_H);
            audio_uart_page_43f6d6(t->frame, t->tile, LV_ALIGN_TOP_LEFT, 0, 0);
            audio_uart_page_44129e(t->frame, 0u, 0u);
            audio_uart_page_44131c(t->frame, 1, 0u);
            audio_uart_page_4412ec(t->frame, audio_uart_page_44104c(0xffffffu), 0u);
            audio_uart_page_44146a(t->frame, 6, 0u);
            audio_uart_page_44130c(t->frame, 0xffu, 0u);
            dashboard_obj_set_style_pad_all_4e75b0(t->frame, 0, 0u);
            audio_uart_page_43dfa4(t->frame, LV_OBJ_FLAG_CLICKABLE);
        }
        audio_uart_page_43f66c(g2_dashboard_tileview);

        for (tile = 0; tile < g2_dashboard_tile_indicator_count; tile++) {
            uint8_t type = layout->widget_type[tile];

            if (type == WIDGET_NEWS) {
                Widget_News_init_4f091c((uint32_t)tile);
            } else if (type == WIDGET_CALENDAR) {
                CalendarWidget_MainPage_init_4edac4((uint32_t)tile);
            } else if (type < WIDGET_CALENDAR) {
                StockWidget_MainPage_init_4ec2dc((uint32_t)tile);
            } else if (type == WIDGET_QUICKLIST) {
                QuicklistWidget_MainPage_init_4f891c((uint32_t)tile);
            } else if (type < WIDGET_QUICKLIST) {
                HealthWidget_MainPage_init_4fb760((uint32_t)tile);
            } else {
                log2(2u, 0x74au, unknown_widget, unknown_widget_short, layout->widget_type[tile],
                     (uint32_t)tile);
            }
        }

        /* Hidden focus frame that hosts expanded widget pages. */
        g2_dashboard_focus_frame = lv_tileview_create_50fef8(g2_dashboard_root_200743b8);
        audio_uart_page_44127e(g2_dashboard_focus_frame, audio_uart_page_44104c(0x000000u), 0u);
        audio_uart_page_43f4c0(g2_dashboard_focus_frame, TILE_W, TILE_H);
        audio_uart_page_44146a(g2_dashboard_focus_frame, 6, 0u);
        dashboard_obj_set_style_pad_all_4e75b0(g2_dashboard_focus_frame, 0, 0u);
        audio_uart_page_43f6d6(g2_dashboard_focus_frame, g2_dashboard_root_200743b8,
                               g2_dashboard_watchface_cfg.frame_align, 0, 0);
        audio_uart_page_44e368(g2_dashboard_focus_frame, LV_SCROLLBAR_MODE_OFF);
        audio_uart_page_4412ec(g2_dashboard_focus_frame, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44131c(g2_dashboard_focus_frame, 1, 0u);
        audio_uart_page_44129e(g2_dashboard_focus_frame, 0xffu, 0u);
        audio_uart_page_43ded4(g2_dashboard_focus_frame, LV_OBJ_FLAG_HIDDEN);
        audio_uart_page_43f66c(g2_dashboard_focus_frame);
    }

    if (g2_dashboard_tileview != NULL && g2_dashboard_last_saved_tile >= 1 &&
        g2_dashboard_last_saved_tile < g2_dashboard_tile_indicator_count) {
        int32_t scroll_y = g2_dashboard_last_saved_tile * TILE_PITCH;

        audio_terminal_display_status_44ea04(g2_dashboard_tileview, scroll_y, 0u);
        g2_dashboard_tile_index = (uint32_t)g2_dashboard_last_saved_tile;
        update_tile_indicators_4e772c(g2_dashboard_tile_index);
        log2(3u, 0x76fu, restored_tile, restored_tile_short, (uint32_t)g2_dashboard_last_saved_tile,
             (uint32_t)scroll_y);
    } else {
        g2_dashboard_tile_index = 0u;
        log2(3u, 0x773u, start_tile0, start_tile0_short, (uint32_t)g2_dashboard_last_saved_tile,
             (uint32_t)g2_dashboard_tile_indicator_count);
        if (audio_uart_service_mode() == 1u) {
            uint8_t widget = dashboard_widget_page_type_4ffeb4(g2_dashboard_tile_index);

            if (page_state_sync_dashboard_main_5000cc(g2_dashboard_tile_index, widget) != 0)
                log2(2u, 0x779u, sync_failed, sync_failed_short, g2_dashboard_tile_index, widget);
        }
    }

    /* Fade the whole screen in. */
    audio_uart_display_audio_reset_441488(g2_dashboard_root_200743b8, 0u, 0u);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_dashboard_root_200743b8;
    audio_uart_lv_anim_values_4506ce(&a, 0, 0xff);
    a.duration = 250;
    a.exec_cb = page_fade_in_anim_exec_cb_4e79a8;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = page_fade_in_anim_ready_cb_4e79b4;
    g2_dashboard_anim_running = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
    log0(4u, 0x791u, fade_started, fade_started_short);
}
