/* Dashboard main screen (tileview of widget tiles), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c
 * (log tag "dashborad.ui"). Native 0x4e772c..0x4e7fd5, 0x4e8000..0x4e80d9,
 * 0x4e80e8..0x4e8131, 0x4e814c..0x4e8329 (0x4e82e4..0x4e82eb pool),
 * 0x4e832a..0x4e835b, 0x4e8370..0x4e83b1, 0x4e83c8..0x4e8429,
 * 0x4e84b0..0x4e895b, 0x4e8a90..0x4e8bb3, 0x4e8bcc..0x4e8da5,
 * 0x4e8dec..0x4e922f, 0x4e923c..0x4e926f, 0x4e9280..0x4e92e5; literal pools
 * 0x4e7fd8..0x4e7fff, 0x4e80dc..0x4e80e7, 0x4e8134..0x4e814b,
 * 0x4e835c..0x4e836f, 0x4e83b4..0x4e83c7, 0x4e842c..0x4e84af,
 * 0x4e895c..0x4e896f, 0x4e8a60..0x4e8a8f, 0x4e8bb4..0x4e8bcb,
 * 0x4e8da8..0x4e8deb, 0x4e9230..0x4e923b, 0x4e9270..0x4e927f.
 * The settings/weather apply handler 0x4e8970 is in
 * ui_dashboard_main_screen_weather.c (single-precision FPU).
 *
 * Tiles are 0x130 (304) px tall and scroll vertically; one tile per widget
 * type: 0 news, 1 stock, 2 calendar, 3 health, 4 quicklist (type table RAM
 * 0x20004224). A tap expands the current widget into its "ext" page by
 * animating the ext container width 0x160 -> 0x240; while expanded, input and
 * reflash events go to that widget's ext handlers. Input that arrives during an
 * animation is queued in a ui_common byte FIFO (5-byte records {code, u32
 * value}) and replayed by the animation-completed callbacks. Peer side input
 * is mirrored as 6-byte records {0, code, x lo, x hi, y lo, y hi} on sync
 * app 1. LVGL 9.3 fork: 0x441488 LV_STYLE_OPA, 0x44127e bg_color, 0x44129e
 * bg_opa; lv_anim_t completed_cb +0x10, path_cb +0x20, duration +0x30. */
#include <stdint.h>
#include <stddef.h>

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stock stack frame. */
typedef struct {
    void *var;                          /* +0x00 */
    void (*exec_cb)(void *, int32_t);   /* +0x04 */
    void *custom_exec_cb;               /* +0x08 */
    void *start_cb;                     /* +0x0c */
    void (*completed_cb)(void *);       /* +0x10 */
    void *deleted_cb;                   /* +0x14 */
    void *get_value_cb;                 /* +0x18 */
    void *user_data;                    /* +0x1c */
    int32_t (*path_cb)(void *);         /* +0x20 */
    int32_t start_value;                /* +0x24 */
    int32_t current_value;              /* +0x28 */
    int32_t end_value;                  /* +0x2c */
    int32_t duration;                   /* +0x30 */
    uint8_t rest[0x2c];                 /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* Ext page geometry (RAM 0x2000420c, initialised data). */
typedef struct {
    int32_t watchface_base;   /* +0x00 */
    int32_t word04;           /* +0x04 */
    uint8_t align;            /* +0x08 lv_align_t of the ext container */
    uint8_t pad09[7];
    int32_t watchface_scale;  /* +0x10 per-pixel factor while resizing */
    int32_t enabled;          /* +0x14 0: tap does not expand */
} g2_dashboard_ext_cfg_t;
_Static_assert(sizeof(g2_dashboard_ext_cfg_t) == 0x18u, "ext cfg");

enum {
    DASH_WIDGET_NEWS = 0u,
    DASH_WIDGET_STOCK = 1u,
    DASH_WIDGET_CALENDAR = 2u,
    DASH_WIDGET_HEALTH = 3u,
    DASH_WIDGET_QUICKLIST = 4u,
    DASH_WIDGET_COUNT = 5u,
};

/* Input codes of Dashboard_InputEventWarp. */
enum {
    DASH_KEY_TAP = 0x0au,
    DASH_KEY_SCROLL_DOWN = 0x44u,
    DASH_KEY_SCROLL_UP = 0x45u,
    DASH_KEY_JUMP = 0x46u,
    DASH_KEY_DOUBLE_TAP = 0x48u,
    DASH_KEY_49 = 0x49u,
    DASH_KEY_SCROLL_RELEASE = 0x4au,
};

#define DASH_TILE_HEIGHT 0x130
#define DASH_EXT_WIDTH_FOLDED 0x160
#define DASH_EXT_WIDTH_EXPANDED 0x240
#define DASH_SYNC_APP 1u
#define LV_OBJ_FLAG_HIDDEN 1u

extern void *g2_dashboard_tile_indicators[];                 /* RAM 0x20073c50 */
extern int32_t g2_dashboard_tile_indicator_count;            /* RAM 0x2000423c tile count */
extern g2_dashboard_ext_cfg_t g2_dashboard_ext_cfg_2000420c; /* RAM 0x2000420c */
extern uint8_t g2_dashboard_widget_types_20004224[DASH_WIDGET_COUNT]; /* RAM 0x20004224 */
extern int32_t g2_dashboard_scroll_ms_2000422c;              /* RAM 0x2000422c tile scroll time */
extern int32_t g2_dashboard_bounce_px_20004230;              /* RAM 0x20004230 */
extern int32_t g2_dashboard_bounce_ms_20004234;              /* RAM 0x20004234 */
extern int32_t g2_dashboard_word_20004238;                   /* RAM 0x20004238 reset to 200 */
extern volatile uint32_t audio_dashboard_auto_close_current_200743d0; /* RAM 0x200743d0 countdown */
extern volatile uint32_t audio_dashboard_auto_close_default_200743d4; /* RAM 0x200743d4 */
extern void *volatile g2_dashboard_root_200743b8;            /* RAM 0x200743b8 dashboard screen */
extern uint32_t g2_dashboard_layout_saved_20074b94;          /* RAM 0x20074b94 */
extern void *g2_dashboard_input_fifo_20074b98;               /* RAM 0x20074b98 queued input */
extern void *g2_dashboard_ext_container_20074b9c;            /* RAM 0x20074b9c */
extern volatile uint32_t g2_dashboard_auto_close_hold_20074ba0; /* RAM 0x20074ba0 ext page open */
extern void *g2_dashboard_obj_20074ba4;                      /* RAM 0x20074ba4 hidden on fade-out */
extern void *g2_dashboard_tileview_20074ba8;                 /* RAM 0x20074ba8 */
extern int32_t g2_dashboard_tile_index_20074bac;             /* RAM 0x20074bac current tile */
extern uint32_t g2_dashboard_ext_index_20074bb0;             /* RAM 0x20074bb0 expanded tile */
extern int32_t g2_dashboard_saved_tile_index_20074bb4;       /* RAM 0x20074bb4 */
extern uint32_t g2_dashboard_word_20074bb8;                  /* RAM 0x20074bb8 */
extern int32_t g2_dashboard_bounce_origin_y_20074bbc;        /* RAM 0x20074bbc */
extern uint32_t g2_dashboard_animating_20074bc0;             /* RAM 0x20074bc0 */
extern uint32_t g2_dashboard_word_20074bc4;                  /* RAM 0x20074bc4 */
extern uint32_t g2_dashboard_word_20074bc8;                  /* RAM 0x20074bc8 */
extern int32_t g2_dashboard_scroll_accum_20074bcc;           /* RAM 0x20074bcc */
extern void *g2_dashboard_tile_col0_20074bd0[6];             /* RAM 0x20074bd0 */
extern void *g2_dashboard_tile_col1_20074be8[6];             /* RAM 0x20074be8 */
extern void *g2_dashboard_tile_pairs_200734bc[12];           /* RAM 0x200734bc */
extern uint32_t g2_dashboard_news_ready_20074e60;            /* RAM 0x20074e60 */
extern uint8_t g2_dashboard_saved_layout_20120134[0x80];     /* RAM 0x20120134 */

/* Widget pages (stock app\gui\dashboard\...). */
extern int32_t NewsWidgetInputEventHandler_4f4030(int32_t code, const void *e);
extern int32_t StockInputEventHandler_4eb33c(int32_t code, const void *e);
extern int32_t calendar_input_event_handler_4eeadc(int32_t code, const void *e);
extern int32_t HealthInputEventHandler_4fc1dc(int32_t code, const void *e);
extern int32_t QuicklistInputEventHandler_4f6880(int32_t code, const void *e);
extern void News_Widget_ext_init_4f4670(void *parent);
extern void stock_ext_Widget_init_4ebdfc(void *parent);
extern void Calendar_ext_Widget_init_4ef9a4(void *parent);
extern void Health_ext_Widget_init_4fd7b0(void *parent);
extern void Quicklist_ext_Widget_init_4faf9c(void *parent);
extern void news_widget_ext_event_handler_4f3440(const uint8_t *data, uint32_t len);
extern void stock_ext_event_handler_4eb4a4(const uint8_t *data, uint32_t len);
extern void calendar_extWidget_ReflashEvent_handler_4eebdc(const uint8_t *data, uint32_t len);
extern void health_ext_event_handler_4fc360(const uint8_t *data, uint32_t len);
extern void quicklist_ext_event_handler_4f8ffc(const uint8_t *data, uint32_t len);
extern void Calendar_Page_Reflash_4ed9b6(const uint8_t *data, uint32_t len);
extern void Stock_Page_Reflash_4ebf5c(const uint8_t *data, uint32_t len);
extern void Quicklist_Page_Reflash_4f8644(const uint8_t *data, uint32_t len);
extern void Health_Page_Reflash_4fb5e8(const uint8_t *data, uint32_t len);
extern void Calendar_expire_update_4efcb8(uint8_t mask);
extern void News_Widget_init_Reflash_4efffc(void);
extern void NewsWidget_AutoReflash_4f2cec(uint32_t arg0, uint32_t arg1);
extern void quicklist_widget_tick_4f8878(uint32_t arg0, uint32_t arg1);
extern void NewsWidget_UpdateTimeout_Handler_4f3084(void);
extern void NewsWidget_NoSources_Handler_4f3128(void);
extern void NewsWidget_ScrollLableResume_Handler_4f2ec0(void);
extern void NewsWidget_LoadContent_Handler_4f31c8(void);
extern void NewsWidget_ClearContent_Handler_4f326c(void);
extern void calendar_widget_deinit_4efeb0(void);
extern void stock_widget_deinit_4ed6c4(void);
extern void quicklist_widget_deinit_4fb08c(void);
extern void news_widget_deinit_4f4ed8(void);
extern void health_widget_deinit_4fd840(void);

extern void dashboard_watchface_manager_deinit(void);                  /* 0x50060e */
extern void dashboard_watchface_manager_call_08(int32_t value);        /* 0x50062c */
extern void dashboard_watchface_manager_call_0c(uint8_t hour, uint8_t minute,
                                                uint8_t h24);           /* 0x500646 */
extern void dashboard_watchface_manager_call_20(uint8_t connected);    /* 0x500712 */
extern void dashboard_watchface_manager_call_24(uint8_t connected, uint8_t battery); /* 0x50077a */
extern void dashboard_watchface_manager_call_28(uint8_t charging);     /* 0x500796 */
extern void dashboard_watchface_manager_call_2c(uint8_t value);        /* 0x5007b0 */
extern void dashboard_watchface_manager_call_30(void);                 /* 0x50072c */
extern void dashboard_status_data_apply_4e8970(const uint8_t *data, uint32_t len);
extern uint8_t dashboard_ring_battery_level_get_49c5bc(void);
extern uint8_t dashboard_tile_widget_type_4ffeb4(uint32_t tile);
extern int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile, uint8_t widget_type);
extern const uint8_t *dashboard_layout_get_current_558142(void);               /* 0x80-byte layout */

extern void audio_uart_master_display_refresh(uint32_t app, const void *payload,
                                              uint16_t length, uint32_t extra); /* 0x464bb2 */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t context);
extern uint8_t audio_uart_device_role_get(void);                       /* 0x45a568 */
extern int32_t iar_abs_509694(int32_t v);
extern int32_t ui_common_api_fn_00509dfa(void *fifo);       /* 1 empty, 0 has data */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len); /* pop */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push */
extern void ui_common_api_fn_00509f52(void *fifo);          /* reset */
extern void ui_common_api_fn_00509c96(void *fifo);          /* destroy */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_log_flags(void);                                  /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                     /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* LVGL 9.3 fork. */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);    /* lv_obj_is_valid */
extern void audio_lv_width_43f506(void *obj, int32_t width);            /* lv_obj_set_width */
extern void audio_uart_page_43f142(void *obj, int32_t y);               /* lv_obj_set_y */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                          /* lv_obj_align_to */
extern void audio_uart_page_43f66c(void *obj);                          /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                   /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                   /* lv_obj_get_scroll_y */
extern void *audio_uart_lv_obj_parent_44dca2(void *obj);                /* lv_obj_get_parent */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim);
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);      /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag); /* lv_obj_remove_flag */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);                    /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_lv_style_opa_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern int32_t audio_uart_lv_anim_path_45065a(void *anim);              /* ease_in */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);              /* ease_out */
extern int32_t audio_uart_lv_anim_path_450688(void *anim);              /* ease_in_out */

/* Defined in this file. */
void update_tile_indicators_4e772c(int32_t tile);
void scroll_anim_ready_cb_4e7802(void *anim);
void scroll_anim_exec_cb_4e78a0(void *obj, int32_t y);
void bounce_transform_anim_exec_cb_4e78aa(void *obj, int32_t y);
void bounce_restore_anim_ready_cb_4e7902(void *anim);
void page_fade_in_anim_exec_cb_4e79a8(void *obj, int32_t opa);
void page_fade_in_anim_ready_cb_4e79b4(void *anim);
void page_fade_out_anim_exec_cb_4e7a04(void *obj, int32_t opa);
void page_fade_out_anim_ready_cb_4e7a10(void *anim);
void bounce_transform_anim_ready_cb_4e7a74(void *anim);
void execute_bounce_effect_4e7b16(int32_t direction);
void tileview_scroll_anim_start_4e7cc0(void *obj, int32_t target_y, int32_t duration);
void virtual_scroll_tileview_4e7d20(int32_t direction);
void jump_to_tile_absolute_4e7dfa(int32_t target);
void ui_Screen1_Deinit_4e8000(void);
int32_t dashboard_ext_input_dispatch_4e80e8(int32_t code, const void *e);
int32_t dashboard_main_screen_event_4e814c(int32_t code, const void *e);
void ext_expand_anim_exec_cb_4e82a6(void *obj, int32_t width);
void ext_collapse_anim_exec_cb_4e82ec(void *obj, int32_t width);
void ext_expand_anim_ready_cb_4e832a(void *anim);
void ext_collapse_anim_ready_cb_4e8370(void *anim);
void dashboard_ext_widget_init_4e83c8(uint32_t index);
void tileview_ext_event_handler_4e84b0(const uint8_t *data, uint32_t len);
void Dashboard_Fadeout_Anim_Start_4e8a90(void);
void Dashboard_InputEventWarp_4e8bcc(uint8_t code, uint32_t value);
int32_t Dashboard_ReflashEventHandler_4e8dec(const uint8_t *data, uint32_t len);
int32_t dashboard_main_screen_tick_4e923c(uint32_t arg0, uint32_t arg1);
void dashboard_tile_pairs_export_4e9280(void);

static const char module_tag[] = "dashborad.ui"; /* ROM 0x789d20 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_DashBaord_Main_Screen.c"; /* ROM 0x6e1d2c */

static const char indicators_fn[] = "update_tile_indicators"; /* ROM 0x77d18c */
static const char sync_failed[] =
    "Failed to sync dashboard main page state: tile_index=%d, widget_type=%d"; /* ROM 0x6fe8ac */
static const char sync_failed_short[] =
    "[dashborad.ui]Failed to sync dashboard main page state: tile_index=%d, widget_type=%d"; /* ROM 0x6e56c0 */
static const char scroll_ready_fn[] = "scroll_anim_ready_cb"; /* ROM 0x77d1a4 */
static const char scroll_ready[] = "scroll_anim_ready_cb: scroll animation completed"; /* ROM 0x72fb50 */
static const char scroll_ready_short[] =
    "[dashborad.ui]scroll_anim_ready_cb: scroll animation completed"; /* ROM 0x710ca4 */
static const char bounce_exec_fn[] = "bounce_transform_anim_exec_cb"; /* ROM 0x767390 */
static const char bounce_exec[] = "bounce_transform_anim_exec_cb value = %d"; /* ROM 0x745d24 */
static const char bounce_exec_short[] =
    "[dashborad.ui]bounce_transform_anim_exec_cb value = %d"; /* ROM 0x725178 */
static const char restore_ready_fn[] = "bounce_restore_anim_ready_cb"; /* ROM 0x7673b0 */
static const char restore_ready[] =
    "bounce_restore_anim_ready_cb: bounce animation fully completed"; /* ROM 0x710ce4 */
static const char restore_ready_short[] =
    "[dashborad.ui]bounce_restore_anim_ready_cb: bounce animation fully completed"; /* ROM 0x6f0998 */
static const char fade_in_fn[] = "page_fade_in_anim_ready_cb"; /* ROM 0x773df0 */
static const char fade_in[] = "page_fade_in_anim_ready_cb: page fade-in animation completed"; /* ROM 0x710d24 */
static const char fade_in_short[] =
    "[dashborad.ui]page_fade_in_anim_ready_cb: page fade-in animation completed"; /* ROM 0x6f7078 */
static const char fade_out_fn[] = "page_fade_out_anim_ready_cb"; /* ROM 0x773e0c */
static const char fade_out[] =
    "page_fade_out_anim_ready_cb: page fade-out animation completed - screen is now dark"; /* ROM 0x6ea90c */
static const char fade_out_short[] =
    "[dashborad.ui]page_fade_out_anim_ready_cb: page fade-out animation completed - screen is now dark"; /* ROM 0x6dbcb8 */
static const char transform_ready_fn[] = "bounce_transform_anim_ready_cb"; /* ROM 0x7673d0 */
static const char transform_ready[] =
    "bounce_transform_anim_ready_cb, bouncing back to original position"; /* ROM 0x7079c0 */
static const char transform_ready_short[] =
    "[dashborad.ui]bounce_transform_anim_ready_cb, bouncing back to original position"; /* ROM 0x6ea960 */
static const char bounce_fn[] = "execute_bounce_effect"; /* ROM 0x77d1bc */
static const char bottom_bounce[] = "Bottom bounce: moving tileview from %d to %d"; /* ROM 0x73a6c4 */
static const char bottom_bounce_short[] =
    "[dashborad.ui]Bottom bounce: moving tileview from %d to %d"; /* ROM 0x71a764 */
static const char top_bounce[] = "Top bounce: moving tileview from %d to %d"; /* ROM 0x745d50 */
static const char top_bounce_short[] =
    "[dashborad.ui]Top bounce: moving tileview from %d to %d"; /* ROM 0x7251b0 */
static const char bounce_start[] =
    "execute_bounce_effect: direction=%d, original_y=%d, target_y=%d"; /* ROM 0x710d64 */
static const char bounce_start_short[] =
    "[dashborad.ui]execute_bounce_effect: direction=%d, original_y=%d, target_y=%d"; /* ROM 0x6f09e8 */
static const char virtual_fn[] = "virtual_scroll_tileview"; /* ROM 0x77d1d4 */
static const char virtual_busy[] =
    "virtual_scroll_tileview: animation in progress (state=%d), ignoring request"; /* ROM 0x6f70c4 */
static const char virtual_busy_short[] =
    "[dashborad.ui]virtual_scroll_tileview: animation in progress (state=%d), ignoring request"; /* ROM 0x6e1d88 */
static const char jump_fn[] = "jump_to_tile_absolute"; /* ROM 0x77d1ec */
static const char jump_busy[] =
    "jump_to_tile_absolute: animation in progress (state=%d), ignoring request"; /* ROM 0x6f7110 */
static const char jump_busy_short[] =
    "[dashborad.ui]jump_to_tile_absolute: animation in progress (state=%d), ignoring request"; /* ROM 0x6e5718 */
static const char jump_invalid[] = "jump_to_tile_absolute: invalid target index %d, must be 0-2"; /* ROM 0x71a7a0 */
static const char jump_invalid_short[] =
    "[dashborad.ui]jump_to_tile_absolute: invalid target index %d, must be 0-2"; /* ROM 0x6f715c */
static const char jump_same[] = "jump_to_tile_absolute: already at target index %d"; /* ROM 0x72fb84 */
static const char jump_same_short[] =
    "[dashborad.ui]jump_to_tile_absolute: already at target index %d"; /* ROM 0x710da4 */
static const char jump_go[] = "jump_to_tile_absolute: jumping from tile %d to tile %d"; /* ROM 0x7251e8 */
static const char jump_go_short[] =
    "[dashborad.ui]jump_to_tile_absolute: jumping from tile %d to tile %d"; /* ROM 0x6fe8f4 */
static const char jump_started[] =
    "jump_to_tile_absolute: animation started, target_y=%d, duration=%dms"; /* ROM 0x6fe93c */
static const char jump_started_short[] =
    "[dashborad.ui]jump_to_tile_absolute: animation started, target_y=%d, duration=%dms"; /* ROM 0x6ea9b4 */
static const char deinit_fn[] = "ui_Screen1_Deinit"; /* ROM 0x7847c0 */
static const char deinit_save[] = "Dashboard deinit: saving current tile index = %d"; /* ROM 0x72fbb8 */
static const char deinit_save_short[] =
    "[dashborad.ui]Dashboard deinit: saving current tile index = %d"; /* ROM 0x710de4 */
static const char ext_fn[] = "tileview_ext_event_handler"; /* ROM 0x773e28 */
static const char ext_bad_args[] = "tileview ext event handler len = %d, raw_data = %p"; /* ROM 0x72fbec */
static const char ext_bad_args_short[] =
    "[dashborad.ui]tileview ext event handler len = %d, raw_data = %p"; /* ROM 0x707a04 */
static const char news_timeout[] = "receive DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT"; /* ROM 0x745d7c */
static const char news_timeout_short[] =
    "[dashborad.ui]receive DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT"; /* ROM 0x71a7dc */
static const char news_no_sources[] = "receive DASHBOARD_NEWS_NO_SOURCES_EVENT"; /* ROM 0x7506bc */
static const char news_no_sources_short[] =
    "[dashborad.ui]receive DASHBOARD_NEWS_NO_SOURCES_EVENT"; /* ROM 0x725220 */
static const char news_resume[] = "receive DASHBOARD_NEWS_SCROLL_LABLE_RESUME_EVENT"; /* ROM 0x72fc20 */
static const char news_resume_short[] =
    "[dashborad.ui]receive DASHBOARD_NEWS_SCROLL_LABLE_RESUME_EVENT"; /* ROM 0x710e24 */
static const char news_load[] = "receive DASHBOARD_NEWS_LOAD_CONTENT_EVENT"; /* ROM 0x745da8 */
static const char news_load_short[] =
    "[dashborad.ui]receive DASHBOARD_NEWS_LOAD_CONTENT_EVENT"; /* ROM 0x725258 */
static const char news_clear[] =
    "receive DASHBOARD_NEWS_UI_CLEAR_DATA_EVENT,clear list list content"; /* ROM 0x707a48 */
static const char news_clear_short[] =
    "[dashborad.ui]receive DASHBOARD_NEWS_UI_CLEAR_DATA_EVENT,clear list list content"; /* ROM 0x6eaa08 */
static const char timeout_exit[] = "dashboard timeout exit event"; /* ROM 0x7673f0 */
static const char timeout_exit_short[] = "[dashborad.ui]dashboard timeout exit event"; /* ROM 0x745dd4 */
static const char ble_change[] = "dashboard ble connect status change event"; /* ROM 0x745e00 */
static const char ble_change_short[] =
    "[dashborad.ui]dashboard ble connect status change event"; /* ROM 0x725290 */
static const char ble_data[] = "dashboard ble connect status change event _data = %d"; /* ROM 0x7252c8 */
static const char ble_data_short[] =
    "[dashborad.ui]dashboard ble connect status change event _data = %d"; /* ROM 0x707a8c */
static const char calendar_expire[] = "dashboard calendar expire update event"; /* ROM 0x7506e4 */
static const char calendar_expire_short[] =
    "[dashborad.ui]dashboard calendar expire update event"; /* ROM 0x725300 */
static const char calendar_mask[] = "dashboard calendar expire update event _data_mask = %d"; /* ROM 0x725338 */
static const char calendar_mask_short[] =
    "[dashborad.ui]dashboard calendar expire update event _data_mask = %d"; /* ROM 0x6fe984 */
static const char time_update[] = "update time display,hour = %d,min = %d,h24 = %d"; /* ROM 0x73a6f4 */
static const char time_update_short[] =
    "[dashborad.ui]update time display,hour = %d,min = %d,h24 = %d"; /* ROM 0x710e64 */
static const char fadeout_fn[] = "Dashboard_Fadeout_Anim_Start"; /* ROM 0x767410 */
static const char fadeout_start[] =
    "Starting page fade-out animation (double click detected)"; /* ROM 0x71a818 */
static const char fadeout_start_short[] =
    "[dashborad.ui]Starting page fade-out animation (double click detected)"; /* ROM 0x6fe9cc */
static const char fadeout_started[] =
    "Dashboard screen fade-out animation started (100ms) - screen will go dark"; /* ROM 0x6f71a8 */
static const char fadeout_started_short[] =
    "[dashborad.ui]Dashboard screen fade-out animation started (100ms) - screen will go dark"; /* ROM 0x6e5770 */
static const char warp_fn[] = "Dashboard_InputEventWarp"; /* ROM 0x773e44 */
static const char scroll_release[] =
    ">>> SCROLLRELEASE_EVENT: ext_enable=%d, accumulated=%d, is_animating=%d"; /* ROM 0x6fea14 */
static const char scroll_release_short[] =
    "[dashborad.ui]>>> SCROLLRELEASE_EVENT: ext_enable=%d, accumulated=%d, is_animating=%d"; /* ROM 0x6e57c8 */
static const char warp_unknown[] = "unknown Dashboard_InputEventWarp code = %d"; /* ROM 0x745e2c */
static const char warp_unknown_short[] =
    "[dashborad.ui]unknown Dashboard_InputEventWarp code = %d"; /* ROM 0x71a854 */
static const char reflash_fn[] = "Dashboard_ReflashEventHandler"; /* ROM 0x767430 */
static const char reflash_load[] =
    "receive DASHBOARD_NEWS_LOAD_CONTENT_EVENT,widget page refresh"; /* ROM 0x710ea4 */
static const char reflash_load_short[] =
    "[dashborad.ui]receive DASHBOARD_NEWS_LOAD_CONTENT_EVENT,widget page refresh"; /* ROM 0x6f71f4 */
static const char ring_change[] = "ring status change: sub=%d data=%d"; /* ROM 0x75c27c */
static const char ring_change_short[] = "[dashborad.ui]ring status change: sub=%d data=%d"; /* ROM 0x72fc54 */
static const char ring_unknown[] = "unknown ring sub_event=%d"; /* ROM 0x773e60 */
static const char ring_unknown_short[] = "[dashborad.ui]unknown ring sub_event=%d"; /* ROM 0x75070c */

#define DASH_LOG(level, func, line, cflags, text, short_text, ...)                              \
    do {                                                                                        \
        if ((audio_log_flags() & 2u) != 0u)                                                     \
            audio_log_extended((level), module_tag, source_file, (func), (line), (text),        \
                               ##__VA_ARGS__);                                                  \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                   \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);     \
    } while (0)

/* Highlight the indicator of the current tile (white, opaque; others
 * 0x222222 at opa 150) and tell the peer which widget is now shown. */
void update_tile_indicators_4e772c(int32_t tile)
{
    for (int32_t i = 0; i < g2_dashboard_tile_indicator_count; i++) {
        void *ind = g2_dashboard_tile_indicators[i];
        if (ind == NULL)
            continue;
        if (i == tile) {
            audio_uart_page_44127e(ind, audio_lv_color_44104c(0xffffffu), 0u);
            audio_uart_page_44129e(g2_dashboard_tile_indicators[i], 0xffu, 0u);
        } else {
            audio_uart_page_44127e(ind, audio_lv_color_44104c(0x222222u), 0u);
            audio_uart_page_44129e(g2_dashboard_tile_indicators[i], 0x96u, 0u);
        }
    }
    if (g2_dashboard_tile_indicator_count > 0) {
        uint8_t type = dashboard_tile_widget_type_4ffeb4((uint32_t)tile);
        if (page_state_sync_dashboard_main_5000cc((uint32_t)tile, type) != 0)
            DASH_LOG(2u, indicators_fn, 0x153u, 0x08800000u, sync_failed, sync_failed_short,
                     tile, type);
    }
}

/* Replay one queued 5-byte input record, if any. */
static void replay_queued_input(void)
{
    uint8_t rec[10];

    if (g2_dashboard_input_fifo_20074b98 != NULL &&
        ui_common_api_fn_00509dfa(g2_dashboard_input_fifo_20074b98) == 0) {
        aeabi_memset_43c0e4(rec, sizeof rec, 0);
        (void)ui_common_api_fn_00509e14(g2_dashboard_input_fifo_20074b98, rec, 5u);
        Dashboard_InputEventWarp_4e8bcc(rec[0], (uint32_t)rec[1] | (uint32_t)rec[2] << 8 |
                                                    (uint32_t)rec[3] << 16 |
                                                    (uint32_t)rec[4] << 24);
    }
}

void scroll_anim_ready_cb_4e7802(void *anim)
{
    (void)anim;
    DASH_LOG(4u, scroll_ready_fn, 0x17fu, 0x10000000u, scroll_ready, scroll_ready_short);
    g2_dashboard_animating_20074bc0 = 0u;
    replay_queued_input();
}

void scroll_anim_exec_cb_4e78a0(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

void bounce_transform_anim_exec_cb_4e78aa(void *obj, int32_t y)
{
    DASH_LOG(4u, bounce_exec_fn, 0x197u, 0x10400000u, bounce_exec, bounce_exec_short, y);
    audio_uart_page_43f142(obj, y);
}

void bounce_restore_anim_ready_cb_4e7902(void *anim)
{
    (void)anim;
    DASH_LOG(4u, restore_ready_fn, 0x1a2u, 0x10000000u, restore_ready, restore_ready_short);
    g2_dashboard_animating_20074bc0 = 0u;
    g2_dashboard_scroll_accum_20074bcc = 0;
    replay_queued_input();
}

void page_fade_in_anim_exec_cb_4e79a8(void *obj, int32_t opa)
{
    audio_lv_style_opa_441488(obj, (uint8_t)opa, 0u);
}

void page_fade_in_anim_ready_cb_4e79b4(void *anim)
{
    (void)anim;
    g2_dashboard_animating_20074bc0 = 0u;
    DASH_LOG(4u, fade_in_fn, 0x1beu, 0x10000000u, fade_in, fade_in_short);
}

void page_fade_out_anim_exec_cb_4e7a04(void *obj, int32_t opa)
{
    audio_lv_style_opa_441488(obj, (uint8_t)opa, 0u);
}

/* The screen is dark: the master side closes the dashboard app. */
void page_fade_out_anim_ready_cb_4e7a10(void *anim)
{
    (void)anim;
    g2_dashboard_animating_20074bc0 = 0u;
    DASH_LOG(4u, fade_out_fn, 0x1ceu, 0x10000000u, fade_out, fade_out_short);
    if (audio_uart_device_role_get() == 1u)
        audio_system_alert_close_464c36(1u, 0u, 0u, 0u);
}

/* Second half of the bounce: ease back to the saved y. */
void bounce_transform_anim_ready_cb_4e7a74(void *anim)
{
    g2_lv_anim_t a;

    (void)anim;
    DASH_LOG(4u, transform_ready_fn, 0x1d8u, 0x10000000u, transform_ready,
             transform_ready_short);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_dashboard_tileview_20074ba8;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_43fce0(g2_dashboard_tileview_20074ba8),
                                     g2_dashboard_bounce_origin_y_20074bbc);
    a.duration = g2_dashboard_bounce_ms_20004234;
    a.exec_cb = bounce_transform_anim_exec_cb_4e78aa;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = bounce_restore_anim_ready_cb_4e7902;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Overscroll feedback at the first/last tile: move the tileview by the
 * bounce distance and back. */
void execute_bounce_effect_4e7b16(int32_t direction)
{
    g2_lv_anim_t a;
    int32_t target;

    if (g2_dashboard_tileview_20074ba8 == NULL)
        return;
    audio_uart_page_43f66c(g2_dashboard_tileview_20074ba8);
    g2_dashboard_bounce_origin_y_20074bbc = audio_uart_lv_obj_y_43fce0(g2_dashboard_tileview_20074ba8);
    if (direction == 1 && g2_dashboard_tile_indicator_count - 1 <= g2_dashboard_tile_index_20074bac) {
        target = g2_dashboard_bounce_origin_y_20074bbc - g2_dashboard_bounce_px_20004230;
        DASH_LOG(4u, bounce_fn, 499u, 0x10800000u, bottom_bounce, bottom_bounce_short,
                 g2_dashboard_bounce_origin_y_20074bbc, target);
    } else if (direction == -1 && g2_dashboard_tile_index_20074bac <= 0) {
        target = g2_dashboard_bounce_px_20004230 + g2_dashboard_bounce_origin_y_20074bbc;
        DASH_LOG(4u, bounce_fn, 0x1f7u, 0x10800000u, top_bounce, top_bounce_short,
                 g2_dashboard_bounce_origin_y_20074bbc, target);
    } else {
        return;
    }
    DASH_LOG(4u, bounce_fn, 0x1fdu, 0x10c00000u, bounce_start, bounce_start_short, direction,
             g2_dashboard_bounce_origin_y_20074bbc, target);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_dashboard_tileview_20074ba8;
    audio_uart_lv_anim_values_4506ce(&a, g2_dashboard_bounce_origin_y_20074bbc, target);
    a.duration = g2_dashboard_bounce_ms_20004234;
    a.exec_cb = bounce_transform_anim_exec_cb_4e78aa;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = bounce_transform_anim_ready_cb_4e7a74;
    g2_dashboard_animating_20074bc0 = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Animate the tileview scroll position from its current value to target_y. */
void tileview_scroll_anim_start_4e7cc0(void *obj, int32_t target_y, int32_t duration)
{
    g2_lv_anim_t a;

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(obj), target_y);
    a.exec_cb = scroll_anim_exec_cb_4e78a0;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = scroll_anim_ready_cb_4e7802;
    g2_dashboard_animating_20074bc0 = 1u;
    a.duration = duration;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Scroll one tile down (1) or up (-1); bounce at the ends. */
void virtual_scroll_tileview_4e7d20(int32_t direction)
{
    void *tv = g2_dashboard_tileview_20074ba8;

    if (tv == NULL || audio_terminal_ui_object_valid_43e2ea(tv) == 0u)
        return;
    if (g2_dashboard_animating_20074bc0 != 0u) {
        DASH_LOG(4u, virtual_fn, 0x224u, 0x10400000u, virtual_busy, virtual_busy_short,
                 g2_dashboard_animating_20074bc0);
        return;
    }
    int32_t y = audio_uart_lv_obj_y_44e498(tv);
    if (direction == 1 && g2_dashboard_tile_index_20074bac < g2_dashboard_tile_indicator_count - 1) {
        g2_dashboard_tile_index_20074bac++;
        tileview_scroll_anim_start_4e7cc0(g2_dashboard_tileview_20074ba8, y + DASH_TILE_HEIGHT,
                                          g2_dashboard_scroll_ms_2000422c);
        update_tile_indicators_4e772c(g2_dashboard_tile_index_20074bac);
    } else if (direction == -1 && g2_dashboard_tile_index_20074bac > 0) {
        g2_dashboard_tile_index_20074bac--;
        tileview_scroll_anim_start_4e7cc0(g2_dashboard_tileview_20074ba8, y - DASH_TILE_HEIGHT,
                                          g2_dashboard_scroll_ms_2000422c);
        update_tile_indicators_4e772c(g2_dashboard_tile_index_20074bac);
    } else {
        execute_bounce_effect_4e7b16(direction);
    }
}

/* Scroll straight to a tile; 50 ms extra per additional tile crossed. */
void jump_to_tile_absolute_4e7dfa(int32_t target)
{
    if (g2_dashboard_tileview_20074ba8 == NULL)
        return;
    if (g2_dashboard_animating_20074bc0 != 0u) {
        DASH_LOG(3u, jump_fn, 0x253u, 0x0c400000u, jump_busy, jump_busy_short,
                 g2_dashboard_animating_20074bc0);
        return;
    }
    if (target < 0 || g2_dashboard_tile_indicator_count - 1 < target) {
        DASH_LOG(2u, jump_fn, 0x259u, 0x08400000u, jump_invalid, jump_invalid_short, target);
        return;
    }
    if (target == g2_dashboard_tile_index_20074bac) {
        DASH_LOG(3u, jump_fn, 0x25fu, 0x0c400000u, jump_same, jump_same_short, target);
        return;
    }
    DASH_LOG(4u, jump_fn, 0x263u, 0x10800000u, jump_go, jump_go_short,
             g2_dashboard_tile_index_20074bac, target);
    int32_t target_y = target * DASH_TILE_HEIGHT;
    int32_t duration = (iar_abs_509694(target - g2_dashboard_tile_index_20074bac) - 1) * 50 +
                       g2_dashboard_scroll_ms_2000422c;
    g2_dashboard_tile_index_20074bac = target;
    g2_dashboard_animating_20074bc0 = 1u;
    tileview_scroll_anim_start_4e7cc0(g2_dashboard_tileview_20074ba8, target_y, duration);
    update_tile_indicators_4e772c(g2_dashboard_tile_index_20074bac);
    DASH_LOG(4u, jump_fn, 0x279u, 0x10800000u, jump_started, jump_started_short, target_y,
             duration);
}

/* Screen teardown: remember the tile and the layout, reset the screen state
 * and the watch face, and deinit every widget page. */
void ui_Screen1_Deinit_4e8000(void)
{
    g2_dashboard_saved_tile_index_20074bb4 = g2_dashboard_tile_index_20074bac;
    DASH_LOG(3u, deinit_fn, 0x35bu, 0x0c400000u, deinit_save, deinit_save_short,
             g2_dashboard_saved_tile_index_20074bb4);
    const uint8_t *layout = dashboard_layout_get_current_558142();
    if (layout != NULL) {
        audio_queue_copy_bytes(g2_dashboard_saved_layout_20120134, layout, 0x80u);
        g2_dashboard_layout_saved_20074b94 = 1u;
    }
    g2_dashboard_tile_index_20074bac = 0;
    g2_dashboard_word_20074bb8 = 0u;
    g2_dashboard_animating_20074bc0 = 0u;
    g2_dashboard_auto_close_hold_20074ba0 = 0u;
    dashboard_watchface_manager_deinit();
    g2_dashboard_scroll_accum_20074bcc = 0;
    g2_dashboard_word_20074bc4 = 0u;
    g2_dashboard_word_20074bc8 = 0u;
    g2_dashboard_word_20004238 = 200;
    if (g2_dashboard_input_fifo_20074b98 != NULL) {
        ui_common_api_fn_00509c96(g2_dashboard_input_fifo_20074b98);
        g2_dashboard_input_fifo_20074b98 = NULL;
    }
    calendar_widget_deinit_4efeb0();
    stock_widget_deinit_4ed6c4();
    quicklist_widget_deinit_4fb08c();
    news_widget_deinit_4f4ed8();
    health_widget_deinit_4fd840();
}

/* Forward an LVGL input event to the expanded widget's input handler. */
int32_t dashboard_ext_input_dispatch_4e80e8(int32_t code, const void *e)
{
    if (g2_dashboard_ext_index_20074bb0 >= DASH_WIDGET_COUNT)
        return 0;
    switch (g2_dashboard_widget_types_20004224[g2_dashboard_ext_index_20074bb0]) {
    case DASH_WIDGET_NEWS:
        (void)NewsWidgetInputEventHandler_4f4030(code, e);
        break;
    case DASH_WIDGET_STOCK:
        (void)StockInputEventHandler_4eb33c(code, e);
        break;
    case DASH_WIDGET_CALENDAR:
        (void)calendar_input_event_handler_4eeadc(code, e);
        break;
    case DASH_WIDGET_HEALTH:
        (void)HealthInputEventHandler_4fc1dc(code, e);
        break;
    case DASH_WIDGET_QUICKLIST:
        (void)QuicklistInputEventHandler_4f6880(code, e);
        break;
    default:
        break;
    }
    return 0;
}

static void send_key(uint8_t code, const int32_t *point)
{
    uint8_t msg[6];

    msg[0] = 0u;
    msg[1] = code;
    if (point != NULL) {
        msg[2] = (uint8_t)point[0];
        msg[3] = (uint8_t)(point[0] >> 8);
        msg[4] = (uint8_t)point[1];
        msg[5] = (uint8_t)(point[1] >> 8);
    } else {
        msg[2] = 0u;
        msg[3] = 0u;
        msg[4] = 0u;
        msg[5] = 0u;
    }
    audio_uart_master_display_refresh(DASH_SYNC_APP, msg, 6u, 0u);
}

/* Main screen input event: mirror the key to the peer (which answers through
 * the reflash handler), or hand it to the expanded widget. Ignored while an
 * animation runs. */
int32_t dashboard_main_screen_event_4e814c(int32_t code, const void *e)
{
    if (g2_dashboard_auto_close_hold_20074ba0 != 0u) {
        if (g2_dashboard_animating_20074bc0 != 0u)
            return 0;
        (void)dashboard_ext_input_dispatch_4e80e8(code, e);
        return 0;
    }
    if (g2_dashboard_animating_20074bc0 != 0u)
        return 0;
    switch (code) {
    case DASH_KEY_SCROLL_DOWN:
    case DASH_KEY_SCROLL_UP:
        /* lv_event_t +0x10: int32_t point[2] */
        send_key((uint8_t)code, *(const int32_t *const *)(const void *)((const uint8_t *)e + 0x10));
        break;
    case DASH_KEY_SCROLL_RELEASE:
    case DASH_KEY_TAP:
    case DASH_KEY_DOUBLE_TAP:
    case DASH_KEY_49:
        send_key((uint8_t)code, NULL);
        break;
    default:
        break;
    }
    return 0;
}

/* Ext container width animation (expand); the watch face follows the width. */
void ext_expand_anim_exec_cb_4e82a6(void *obj, int32_t width)
{
    audio_lv_width_43f506(obj, width);
    dashboard_watchface_manager_call_08((width - DASH_EXT_WIDTH_FOLDED) *
                                            g2_dashboard_ext_cfg_2000420c.watchface_scale +
                                        g2_dashboard_ext_cfg_2000420c.watchface_base);
    audio_uart_page_43f6d6(obj, audio_uart_lv_obj_parent_44dca2(obj),
                           g2_dashboard_ext_cfg_2000420c.align, 0, 0);
}

/* Same body as the expand callback; used by the collapse animation. */
void ext_collapse_anim_exec_cb_4e82ec(void *obj, int32_t width)
{
    audio_lv_width_43f506(obj, width);
    dashboard_watchface_manager_call_08((width - DASH_EXT_WIDTH_FOLDED) *
                                            g2_dashboard_ext_cfg_2000420c.watchface_scale +
                                        g2_dashboard_ext_cfg_2000420c.watchface_base);
    audio_uart_page_43f6d6(obj, audio_uart_lv_obj_parent_44dca2(obj),
                           g2_dashboard_ext_cfg_2000420c.align, 0, 0);
}

void ext_expand_anim_ready_cb_4e832a(void *anim)
{
    (void)anim;
    g2_dashboard_animating_20074bc0 = 0u;
    g2_dashboard_auto_close_hold_20074ba0 = 1u;
    dashboard_ext_widget_init_4e83c8(g2_dashboard_ext_index_20074bb0);
    if (g2_dashboard_input_fifo_20074b98 != NULL &&
        ui_common_api_fn_00509dfa(g2_dashboard_input_fifo_20074b98) == 0)
        ui_common_api_fn_00509f52(g2_dashboard_input_fifo_20074b98);
}

void ext_collapse_anim_ready_cb_4e8370(void *anim)
{
    (void)anim;
    g2_dashboard_animating_20074bc0 = 0u;
    g2_dashboard_auto_close_hold_20074ba0 = 0u;
    audio_dashboard_auto_close_current_200743d0 = audio_dashboard_auto_close_default_200743d4;
    audio_lv_object_flag_43ded4(g2_dashboard_ext_container_20074b9c, LV_OBJ_FLAG_HIDDEN);
    if (g2_dashboard_input_fifo_20074b98 != NULL &&
        ui_common_api_fn_00509dfa(g2_dashboard_input_fifo_20074b98) == 0)
        ui_common_api_fn_00509f52(g2_dashboard_input_fifo_20074b98);
}

/* Build the expanded page of the widget on the given tile. */
void dashboard_ext_widget_init_4e83c8(uint32_t index)
{
    if (index >= DASH_WIDGET_COUNT)
        return;
    switch (g2_dashboard_widget_types_20004224[index]) {
    case DASH_WIDGET_NEWS:
        News_Widget_ext_init_4f4670(g2_dashboard_ext_container_20074b9c);
        break;
    case DASH_WIDGET_STOCK:
        stock_ext_Widget_init_4ebdfc(g2_dashboard_ext_container_20074b9c);
        break;
    case DASH_WIDGET_CALENDAR:
        Calendar_ext_Widget_init_4ef9a4(g2_dashboard_ext_container_20074b9c);
        break;
    case DASH_WIDGET_HEALTH:
        Health_ext_Widget_init_4fd7b0(g2_dashboard_ext_container_20074b9c);
        break;
    case DASH_WIDGET_QUICKLIST:
        Quicklist_ext_Widget_init_4faf9c(g2_dashboard_ext_container_20074b9c);
        break;
    default:
        break;
    }
}

/* Event code 7: {7, hour, minute[, x, h24]}; the h24 byte is data[3] when the
 * record has at least 4 bytes, otherwise data[1]. */
static void time_display_event(const uint8_t *data, uint32_t len, const char *func,
                               uint32_t line)
{
    uint8_t h24 = len < 4u ? data[1] : data[3];
    DASH_LOG(3u, func, line, 0x0cc00000u, time_update, time_update_short, data[1], data[2], h24);
    dashboard_watchface_manager_call_0c(data[1], data[2], h24);
}

/* Reflash events while the ext page is open. Type 0 records go to the
 * expanded widget's ext handler; the rest update shared dashboard data. */
void tileview_ext_event_handler_4e84b0(const uint8_t *data, uint32_t len)
{
    if (len == 0u || data == NULL) {
        DASH_LOG(1u, ext_fn, 0x455u, 0x04800000u, ext_bad_args, ext_bad_args_short, len, data);
        return;
    }
    switch (data[0]) {
    case 0u:
        if (g2_dashboard_ext_index_20074bb0 >= DASH_WIDGET_COUNT)
            return;
        switch (g2_dashboard_widget_types_20004224[g2_dashboard_ext_index_20074bb0]) {
        case DASH_WIDGET_NEWS:
            news_widget_ext_event_handler_4f3440(data, len);
            break;
        case DASH_WIDGET_STOCK:
            stock_ext_event_handler_4eb4a4(data, len);
            break;
        case DASH_WIDGET_CALENDAR:
            calendar_extWidget_ReflashEvent_handler_4eebdc(data, len);
            break;
        case DASH_WIDGET_HEALTH:
            health_ext_event_handler_4fc360(data, len);
            break;
        case DASH_WIDGET_QUICKLIST:
            quicklist_ext_event_handler_4f8ffc(data, len);
            break;
        default:
            break;
        }
        return;
    case 1u:
        dashboard_status_data_apply_4e8970(data + 1, len - 1u);
        return;
    case 2u:
        Calendar_Page_Reflash_4ed9b6(data + 1, len - 1u);
        return;
    case 3u:
        return;
    case 4u:
        Stock_Page_Reflash_4ebf5c(data + 1, len - 1u);
        return;
    case 5u:
        Quicklist_Page_Reflash_4f8644(data + 1, len - 1u);
        return;
    case 6u:
        Health_Page_Reflash_4fb5e8(data + 1, len - 1u);
        dashboard_watchface_manager_call_30();
        return;
    case 7u:
        time_display_event(data, len, ext_fn, 0x4c0u);
        return;
    case 8u:
        DASH_LOG(3u, ext_fn, 0x4abu, 0x0c000000u, timeout_exit, timeout_exit_short);
        Dashboard_Fadeout_Anim_Start_4e8a90();
        return;
    case 9u: {
        DASH_LOG(4u, ext_fn, 0x4b0u, 0x10000000u, ble_change, ble_change_short);
        uint8_t v = data[1];
        DASH_LOG(3u, ext_fn, 0x4b2u, 0x0c400000u, ble_data, ble_data_short, v);
        dashboard_watchface_manager_call_20(v);
        return;
    }
    case 10u: {
        DASH_LOG(4u, ext_fn, 0x4b7u, 0x10000000u, calendar_expire, calendar_expire_short);
        uint8_t v = data[1];
        DASH_LOG(3u, ext_fn, 0x4b9u, 0x0c400000u, calendar_mask, calendar_mask_short, v);
        Calendar_expire_update_4efcb8(v);
        return;
    }
    case 0x0cu:
        DASH_LOG(3u, ext_fn, 0x472u, 0x0c000000u, news_timeout, news_timeout_short);
        NewsWidget_UpdateTimeout_Handler_4f3084();
        return;
    case 0x0du:
        DASH_LOG(3u, ext_fn, 0x477u, 0x0c000000u, news_no_sources, news_no_sources_short);
        NewsWidget_NoSources_Handler_4f3128();
        return;
    case 0x0eu:
        DASH_LOG(3u, ext_fn, 0x47cu, 0x0c000000u, news_resume, news_resume_short);
        NewsWidget_ScrollLableResume_Handler_4f2ec0();
        return;
    case 0x0fu:
        DASH_LOG(3u, ext_fn, 0x481u, 0x0c000000u, news_load, news_load_short);
        NewsWidget_LoadContent_Handler_4f31c8();
        return;
    case 0x12u:
        DASH_LOG(3u, ext_fn, 0x486u, 0x0c000000u, news_clear, news_clear_short);
        NewsWidget_ClearContent_Handler_4f326c();
        return;
    default:
        return;
    }
}

/* Fade the dashboard (or the open ext page) out over 250 ms; the completed
 * callback closes the app. */
void Dashboard_Fadeout_Anim_Start_4e8a90(void)
{
    g2_lv_anim_t a;

    DASH_LOG(4u, fadeout_fn, 0x505u, 0x10000000u, fadeout_start, fadeout_start_short);
    audio_uart_lv_anim_init_4503d6(&a);
    if (g2_dashboard_auto_close_hold_20074ba0 == 1u) {
        audio_lv_object_flag_43ded4(g2_dashboard_obj_20074ba4, LV_OBJ_FLAG_HIDDEN);
        audio_lv_object_flag_43ded4(g2_dashboard_tileview_20074ba8, LV_OBJ_FLAG_HIDDEN);
        if (audio_terminal_ui_object_valid_43e2ea(g2_dashboard_ext_container_20074b9c) == 1u)
            a.var = g2_dashboard_ext_container_20074b9c;
        else
            a.var = g2_dashboard_root_200743b8;
    } else {
        a.var = g2_dashboard_root_200743b8;
    }
    audio_uart_lv_anim_values_4506ce(&a, 0xff, 0);
    a.duration = 250;
    a.exec_cb = page_fade_out_anim_exec_cb_4e7a04;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = page_fade_out_anim_ready_cb_4e7a10;
    g2_dashboard_animating_20074bc0 = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
    DASH_LOG(4u, fadeout_fn, 0x52bu, 0x10000000u, fadeout_started, fadeout_started_short);
}

/* Apply one input record (from the peer echo or the replay FIFO). */
void Dashboard_InputEventWarp_4e8bcc(uint8_t code, uint32_t value)
{
    g2_lv_anim_t a;

    switch (code) {
    case DASH_KEY_TAP:
        if (g2_dashboard_auto_close_hold_20074ba0 != 0u || g2_dashboard_animating_20074bc0 != 0u)
            return;
        if (g2_dashboard_ext_cfg_2000420c.enabled == 0 || g2_dashboard_ext_container_20074b9c == NULL)
            return;
        audio_lv_object_clear_flag_43dfa4(g2_dashboard_ext_container_20074b9c, LV_OBJ_FLAG_HIDDEN);
        audio_uart_lv_anim_init_4503d6(&a);
        a.var = g2_dashboard_ext_container_20074b9c;
        audio_uart_lv_anim_values_4506ce(&a, DASH_EXT_WIDTH_FOLDED, DASH_EXT_WIDTH_EXPANDED);
        a.duration = 250;
        a.exec_cb = ext_expand_anim_exec_cb_4e82a6;
        a.path_cb = audio_uart_lv_anim_path_450672;
        a.completed_cb = ext_expand_anim_ready_cb_4e832a;
        g2_dashboard_animating_20074bc0 = 1u;
        g2_dashboard_ext_index_20074bb0 = (uint32_t)g2_dashboard_tile_index_20074bac;
        (void)audio_uart_lv_anim_start_450408(&a);
        return;
    case DASH_KEY_SCROLL_DOWN:
        if (g2_dashboard_auto_close_hold_20074ba0 == 0u)
            virtual_scroll_tileview_4e7d20(1);
        return;
    case DASH_KEY_SCROLL_UP:
        if (g2_dashboard_auto_close_hold_20074ba0 == 0u)
            virtual_scroll_tileview_4e7d20(-1);
        return;
    case DASH_KEY_JUMP:
        if (g2_dashboard_auto_close_hold_20074ba0 == 0u)
            jump_to_tile_absolute_4e7dfa((int32_t)value);
        return;
    case DASH_KEY_DOUBLE_TAP:
    case DASH_KEY_49:
        if (g2_dashboard_auto_close_hold_20074ba0 == 0u && g2_dashboard_animating_20074bc0 == 0u)
            Dashboard_Fadeout_Anim_Start_4e8a90();
        return;
    case DASH_KEY_SCROLL_RELEASE:
        DASH_LOG(3u, warp_fn, 0x559u, 0x0cc00000u, scroll_release, scroll_release_short,
                 g2_dashboard_auto_close_hold_20074ba0, g2_dashboard_scroll_accum_20074bcc,
                 g2_dashboard_animating_20074bc0);
        return;
    default:
        DASH_LOG(2u, warp_fn, 0x590u, 0x08400000u, warp_unknown, warp_unknown_short, code);
        return;
    }
}

/* Dashboard app reflash events (sync records from the peer). */
int32_t Dashboard_ReflashEventHandler_4e8dec(const uint8_t *data, uint32_t len)
{
    if (g2_dashboard_auto_close_hold_20074ba0 == 1u) {
        tileview_ext_event_handler_4e84b0(data, len);
        return 0;
    }
    switch (data[0]) {
    case 0u:
        if (g2_dashboard_animating_20074bc0 != 0u) {
            (void)ui_common_api_fn_00509ca2(g2_dashboard_input_fifo_20074b98, data + 1, 5u);
            return 0;
        }
        Dashboard_InputEventWarp_4e8bcc(data[1], (uint32_t)data[2] | (uint32_t)data[3] << 8 |
                                                     (uint32_t)data[4] << 16 |
                                                     (uint32_t)data[5] << 24);
        break;
    case 1u:
        dashboard_status_data_apply_4e8970(data + 1, len - 1u);
        break;
    case 2u:
        Calendar_Page_Reflash_4ed9b6(data + 1, len - 1u);
        break;
    case 3u:
        break;
    case 4u:
        Stock_Page_Reflash_4ebf5c(data + 1, len - 1u);
        break;
    case 5u:
        Quicklist_Page_Reflash_4f8644(data + 1, len - 1u);
        break;
    case 6u:
        Health_Page_Reflash_4fb5e8(data + 1, len - 1u);
        dashboard_watchface_manager_call_30();
        break;
    case 7u:
        time_display_event(data, len, reflash_fn, 0x5d9u);
        break;
    case 8u:
        DASH_LOG(3u, reflash_fn, 0x5deu, 0x0c000000u, timeout_exit, timeout_exit_short);
        Dashboard_Fadeout_Anim_Start_4e8a90();
        break;
    case 9u: {
        DASH_LOG(4u, reflash_fn, 0x5e3u, 0x10000000u, ble_change, ble_change_short);
        uint8_t v = data[1];
        DASH_LOG(3u, reflash_fn, 0x5e5u, 0x0c400000u, ble_data, ble_data_short, v);
        dashboard_watchface_manager_call_20(v);
        break;
    }
    case 10u: {
        DASH_LOG(4u, reflash_fn, 0x5eau, 0x10000000u, calendar_expire, calendar_expire_short);
        uint8_t v = data[1];
        DASH_LOG(3u, reflash_fn, 0x5ecu, 0x0c400000u, calendar_mask, calendar_mask_short, v);
        Calendar_expire_update_4efcb8(v);
        break;
    }
    case 0x0fu:
        DASH_LOG(3u, reflash_fn, 0x59fu, 0x0c000000u, reflash_load, reflash_load_short);
        if (g2_dashboard_news_ready_20074e60 == 1u)
            News_Widget_init_Reflash_4efffc();
        break;
    case 0x12u:
        DASH_LOG(3u, reflash_fn, 0x5a7u, 0x0c000000u, news_clear, news_clear_short);
        if (g2_dashboard_news_ready_20074e60 == 1u)
            News_Widget_init_Reflash_4efffc();
        break;
    case 0x13u: {
        /* Ring status: {0x13, sub, data}; sub 0 disconnected, 1 connected,
         * 2/3 charging off/on, 4 value update. */
        uint8_t sub = data[1];
        uint8_t v = data[2];
        DASH_LOG(3u, reflash_fn, 0x5feu, 0x0c800000u, ring_change, ring_change_short, sub, v);
        switch (sub) {
        case 0u:
            dashboard_watchface_manager_call_24(0u, 0u);
            break;
        case 1u:
            dashboard_watchface_manager_call_24(1u, dashboard_ring_battery_level_get_49c5bc());
            break;
        case 2u:
            dashboard_watchface_manager_call_28(0u);
            break;
        case 3u:
            dashboard_watchface_manager_call_28(1u);
            break;
        case 4u:
            dashboard_watchface_manager_call_2c(v);
            break;
        default:
            DASH_LOG(2u, reflash_fn, 0x611u, 0x08400000u, ring_unknown, ring_unknown_short, sub);
            break;
        }
        break;
    }
    default:
        break;
    }
    return 0;
}

/* Periodic tick, only for the expanded news and quicklist pages; the
 * arguments are passed through unchanged. */
int32_t dashboard_main_screen_tick_4e923c(uint32_t arg0, uint32_t arg1)
{
    if (g2_dashboard_auto_close_hold_20074ba0 == 1u &&
        g2_dashboard_ext_index_20074bb0 < DASH_WIDGET_COUNT) {
        uint8_t type = g2_dashboard_widget_types_20004224[g2_dashboard_ext_index_20074bb0];
        if (type == DASH_WIDGET_NEWS)
            NewsWidget_AutoReflash_4f2cec(arg0, arg1);
        else if (type == DASH_WIDGET_QUICKLIST)
            quicklist_widget_tick_4f8878(arg0, arg1);
    }
    return 0;
}

/* Interleave the two tile-object columns into one 12-entry table. */
void dashboard_tile_pairs_export_4e9280(void)
{
    for (uint32_t i = 0u; i < 6u; i++) {
        g2_dashboard_tile_pairs_200734bc[2u * i] = g2_dashboard_tile_col0_20074bd0[i];
        g2_dashboard_tile_pairs_200734bc[2u * i + 1u] = g2_dashboard_tile_col1_20074be8[i];
    }
}
