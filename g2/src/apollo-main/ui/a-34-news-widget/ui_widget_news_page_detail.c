/* Dashboard news widget: expanded (detail) page, loading/status labels, list
 * scroll helpers and the widget event handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_widget_news_page.c.
 * Native 0x4f1ab8..0x4f2207, 0x4f2210..0x4f225b, 0x4f2264..0x4f227f,
 * 0x4f2288..0x4f230b, 0x4f2318..0x4f23cd, 0x4f23e4..0x4f24c1,
 * 0x4f24cc..0x4f251b, 0x4f2554..0x4f27f5, 0x4f2804..0x4f28d9,
 * 0x4f28f0..0x4f2b93, 0x4f2bbc..0x4f2cd7, 0x4f2cec..0x4f2e91,
 * 0x4f2ec0..0x4f3067, 0x4f3084..0x4f311d, 0x4f3128..0x4f31b1,
 * 0x4f31c8..0x4f324d, 0x4f326c..0x4f335d, 0x4f3440..0x4f3f6d,
 * 0x4f4030..0x4f45d7. "AM"/"PM" at 0x4f225c/0x4f2260 and the literal pools
 * between the functions are data of this TU. The list page, item borders,
 * expand/collapse animations and News_Widget_ext_init (0x4efffc..0x4f1ab7,
 * 0x4f4670..) are reconstructed separately.
 *
 * News cache (RAM 0x20132f74): five 0x1c98-byte records, +0x0000 valid (1),
 * +0x0001 source (0x80), +0x0081 title (0x80), +0x0101 body text,
 * +0x1c90 u64 publish time in milliseconds.
 *
 * Widget event messages (6 bytes, also the event FIFO record): +0 type (0),
 * +1 code, +2 u32 value, little endian, unaligned. Codes: 0x0a click,
 * 0x44 scroll down, 0x45 scroll up (value = speed << 16 | distance),
 * 0x48 double click (back), 0x49 ignored. */
#include <stdint.h>
#include <stddef.h>

#define NEWS_CACHE_COUNT 5
#define NEWS_CACHE_STRIDE 0x1c98u
#define NEWS_OFF_SOURCE 0x0001u
#define NEWS_OFF_TITLE 0x0081u
#define NEWS_OFF_BODY 0x0101u
#define NEWS_OFF_TIME_MS 0x1c90u

#define DASHBOARD_APP 1u
#define NEWS_EVT_CLICK 0x0au
#define NEWS_EVT_SCROLL_DOWN 0x44u
#define NEWS_EVT_SCROLL_UP 0x45u
#define NEWS_EVT_BACK 0x48u
#define NEWS_EVT_IGNORED 0x49u
#define NEWS_EVT_LEN 6u
/* One-byte requests posted to the dashboard application (sync app 1). */
#define DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT 0x0cu
#define DASHBOARD_NEWS_SCROLL_LABEL_RESUME_EVENT 0x0eu

/* notifyAppNewsStatus status codes as used here. */
#define NEWS_STATUS_EXIT 1u
#define NEWS_STATUS_ITEM 2u
#define NEWS_STATUS_EXPAND 3u
#define NEWS_STATUS_COLLAPSE 4u

#define NEWS_DETAIL_LINE 28           /* scroll quantum and row pitch */
#define NEWS_DETAIL_VIEWPORT_H 0xec
#define NEWS_DETAIL_CONTENT_W 0x21a
#define NEWS_LIST_VIEW_H 0x120
#define NEWS_STATUS_TICKS 600

#define LV_SIZE_CONTENT 0x3fffffff
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_TOP_RIGHT 3u
#define LV_ALIGN_CENTER 9u
#define LV_FLEX_FLOW_ROW 0u
#define LV_FLEX_FLOW_COLUMN 1u
#define LV_FLEX_ALIGN_CENTER 2u
#define LV_LABEL_LONG_WRAP 0u
#define LV_LABEL_LONG_DOT 1u
#define LV_ANIM_OFF 0u
#define LV_ANIM_ON 1u

/* lv_anim_t (LVGL 9.3 fork), 0x60 bytes on the stack. */
typedef struct g2_lv_anim g2_lv_anim_t;
struct g2_lv_anim {
    void *var;                                     /* +0x00 */
    void (*exec_cb)(void *, int32_t);              /* +0x04 */
    void *custom_exec_cb;                          /* +0x08 */
    void *start_cb;                                /* +0x0c */
    void (*completed_cb)(g2_lv_anim_t *);          /* +0x10 */
    void *deleted_cb;                              /* +0x14 */
    void *get_value_cb;                            /* +0x18 */
    void *user_data;                               /* +0x1c */
    int32_t (*path_cb)(const g2_lv_anim_t *);      /* +0x20 */
    int32_t start_value;                           /* +0x24 */
    int32_t current_value;                         /* +0x28 */
    int32_t end_value;                             /* +0x2c */
    int32_t duration;                              /* +0x30 */
    int32_t act_time;                              /* +0x34 */
    uint32_t reverse_delay;                        /* +0x38 */
    uint32_t reverse_duration;                     /* +0x3c */
    uint8_t rest[0x20];                            /* +0x40 */
};
_Static_assert(sizeof(g2_lv_anim_t) == 0x60u, "lv_anim_t");

/* am_hal_rtc_time_t word layout filled by the calendar services. */
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

/* lv_font_t head: only line_height is read. */
typedef struct {
    const void *get_glyph_dsc;    /* +0x0 */
    const void *get_glyph_bitmap; /* +0x4 */
    const void *release_glyph;    /* +0x8 */
    int32_t line_height;          /* +0xc */
} g2_lv_font_head_t;

/* generic_animation_create configuration (app\gui\common\generic_animation.c). */
typedef struct {
    const void *const *frames; /* +0x00 */
    uint32_t frame_count;      /* +0x04 */
    uint32_t period_ms;        /* +0x08 */
    uint8_t mode;              /* +0x0c 0 loop */
    uint8_t reserved_0d[3];
    int32_t width;             /* +0x10 */
    int32_t height;            /* +0x14 */
    uint8_t color_a[3];        /* +0x18 */
    uint8_t opa_a;             /* +0x1b */
    uint8_t bg_color[3];       /* +0x1c */
    uint8_t bg_opa;            /* +0x1f */
} g2_generic_animation_config_t;
_Static_assert(sizeof(g2_generic_animation_config_t) == 0x20u, "generic animation config");

/* Dashboard tileview tile (RAM 0x200734bc). */
typedef struct {
    void *tile;  /* +0x00 */
    void *frame; /* +0x04 widget container */
} g2_dashboard_tile_t;

/* RAM state of this TU (names shared with ui/a-33-widget-news-page; the stock
 * variable names from the log strings are given where known). */
extern int32_t g2_dashboard_news_ready_20074e60;    /* RAM 0x20074e60 tile widget built */
extern int32_t g2_news_widget_state_20074e64;       /* RAM 0x20074e64 widget_news_ext_init_flag */
extern int32_t g2_news_expanded_20074e68;           /* RAM 0x20074e68 widget_news_expand_page_flag */
extern void *g2_news_ext_fifo_20074e6c;             /* RAM 0x20074e6c event FIFO */
extern void *g2_news_scroll_container_20074e74;     /* RAM 0x20074e74 widget_news_ext_scroll_container */
extern int32_t g2_news_selected_index_20074e78;     /* RAM 0x20074e78 current_index */
extern int32_t g2_news_item_count_20074e7c;         /* RAM 0x20074e7c */
extern void *g2_news_items_20073d9c[];              /* RAM 0x20073d9c list item objects */
extern void *g2_news_end_item_20074e80;             /* RAM 0x20074e80 end_item */
extern void *g2_news_loading_anim_20074e84;         /* RAM 0x20074e84 generic animation */
extern int32_t g2_news_anim_running_20074e88;       /* RAM 0x20074e88 news_is_animating */
extern int32_t g2_news_update_animating_20074e8c;   /* RAM 0x20074e8c news_widget_is_update_animating */
extern int32_t g2_news_update_timeout_20074e90;     /* RAM 0x20074e90 ticks */
extern int32_t g2_news_expanding_20074e94;          /* RAM 0x20074e94 news_widget_is_switching */
extern int32_t g2_news_status_shown_20074e98;       /* RAM 0x20074e98 end-item status label shown */
extern int32_t g2_news_status_resume_20074e9c;      /* RAM 0x20074e9c ticks */
extern void *g2_news_expand_container_20074ea0;     /* RAM 0x20074ea0 */
extern void *g2_news_detail_20074ea4;               /* RAM 0x20074ea4 detail viewport */
extern void *g2_news_detail_20074ea8;               /* RAM 0x20074ea8 detail content column */
extern void *g2_news_detail_20074eac;               /* RAM 0x20074eac detail scrollbar */
extern int32_t g2_news_detail_20074eb0;             /* RAM 0x20074eb0 detail scroll y (animated) */
extern int32_t g2_news_detail_20074eb4;             /* RAM 0x20074eb4 detail target y */
extern int32_t g2_news_detail_20074eb8;             /* RAM 0x20074eb8 detail content height */
extern int32_t g2_news_detail_20074ebc;             /* RAM 0x20074ebc detail viewport height */
extern int32_t g2_news_detail_20074ec0;             /* RAM 0x20074ec0 widget_news_detail_is_bouncing */
extern int32_t g2_news_detail_scrolling_20074ec4;   /* RAM 0x20074ec4 widget_news_detail_is_scrolling */
extern const void *g2_news_loading_frames_20004330[25]; /* RAM 0x20004330 (.data) spinner frames */
extern uint32_t g2_news_tile_index_2000432c;        /* RAM 0x2000432c (.data) */
extern g2_dashboard_tile_t g2_dashboard_tiles[];    /* RAM 0x200734bc */
extern void *g2_dashboard_focus_frame;              /* RAM 0x20074b9c expanded-page parent */
extern uint8_t g2_dashboard_news_cache_20132f74[0x8ef8]; /* RAM 0x20132f74 */
extern uint32_t audio_uart_ring_primary_head_cell;  /* RAM 0x200746dc: active lv_font_t * */
extern const uint8_t news_icon_76e7c0[];            /* ROM 0x76e7c0 lv_image_dsc_t 24x24 L8 */
extern const uint8_t news_refresh_icon_769d98[];    /* ROM 0x769d98 lv_image_dsc_t 24x24 L8 */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Runtime helpers. */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);  /* 0x439c04 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);   /* memset 0x43c0e4 */
extern uint32_t g2_log_module_length(const char *text);                       /* strlen 0x44a43c */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *fmt, ...); /* 0x44b728 */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t low, uint32_t high, uint32_t dlow,
                                               uint32_t dhigh);
extern void audio_time_epoch_to_calendar_44a100(uint32_t seconds, void *record);
extern void service_time_current_calendar_get(g2_calendar_t *calendar);       /* 0x44a19a */
extern uint8_t svc_universal_setting_get_date_format_466500(void);
extern uint32_t audio_time_format_mode_46650c(void);                          /* 1 = 12 h */
extern uint8_t audio_uart_device_role_get(void);                              /* 0x45a568, 1 master */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);            /* 0x464bb2 */
extern uint32_t audio_uart_page_460084(const char *key);                      /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);   /* localized text */

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                            /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                 /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                 /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);             /* lv_obj_is_valid */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);          /* lv_obj_set_pos */
extern void audio_uart_page_43f142(void *obj, int32_t y);                     /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);          /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                     /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                     /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                                /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                         /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);                     /* lv_obj_get_width */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                    /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                         /* lv_color_hex */
extern uint32_t lv_color_white_441094(void);
extern uint32_t lv_color_black_4410a6(void);
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);       /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);       /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);       /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);       /* pad_right */
extern void audio_uart_page_441246(void *obj, int32_t v, uint32_t sel);       /* pad_row */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);       /* pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);  /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);    /* bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);       /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);  /* text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel);   /* text_font */
extern void audio_uart_page_44144c(void *obj, int32_t v, uint32_t sel);       /* text_line_space */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);       /* radius */
extern void style_prop_2d_441478(void *obj, uint32_t v, uint32_t sel);        /* clip_corner */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);            /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                                /* lv_obj_clean */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);        /* lv_obj_get_child */
extern int32_t audio_uart_lv_child_count_44ddea(void *obj);                   /* lv_obj_get_child_count */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                         /* lv_obj_get_scroll_y */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);                  /* lv_anim_init */
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);          /* lv_anim_start */
extern uint32_t audio_uart_anim_delete_450500(void *var, void (*exec_cb)(void *, int32_t)); /* lv_anim_delete */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern int32_t audio_uart_lv_anim_path_450672(const g2_lv_anim_t *a);         /* lv_anim_path_ease_out */
extern int32_t audio_uart_lv_anim_path_450688(const g2_lv_anim_t *a);         /* lv_anim_path_ease_in_out */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);                 /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_uart_page_498668(void *parent);                            /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);             /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                            /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);     /* lv_label_set_text */
extern void audio_uart_page_layout_499678(void *label, uint32_t mode);        /* lv_label_set_long_mode */

/* UI common byte FIFO (app\gui\common). */
extern void ui_common_api_fn_00509c96(void *fifo);                            /* destroy */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push */
extern void ui_common_api_fn_00509f52(void *fifo);                            /* reset */

/* generic_animation.c. */
extern void *generic_animation_create_463c68(void *parent, const g2_generic_animation_config_t *config);
extern void generic_animation_destroy_463e1c(void *anim, uint8_t delete_image);
extern void generic_animation_start_463ea6(void *anim);
extern void generic_animation_update_463f34(void *anim);

/* Dashboard main screen, data process and page state sync. */
extern void dashboard_focus_frame_shrink_anim_4e92f4(void);
extern int32_t requesetAppUpgradeNewsInfo_4fe0aa(void);
extern int32_t notifyAppNewsStatus_4fe1b4(uint8_t status, uint32_t index);
extern void page_state_sync_dashboard_main_5000cc(uint32_t tile, uint8_t widget);

/* Rest of ui_widget_news_page.c. */
extern void lv_obj_set_style_pad_all_4effa8(void *obj, int32_t v, uint32_t sel); /* TU copy */
extern int32_t News_Widget_init_Reflash_4efffc(void);
extern void widget_news_show_item_border_4f0e18(int32_t index);
extern void widget_news_hide_item_border_4f0e94(int32_t index);
extern void widget_news_scroll_anim_exec_cb_4f0f1c(void *obj, int32_t y);
extern void widget_news_scroll_anim_ready_cb_4f0f26(g2_lv_anim_t *a);
extern void widget_news_scroll_anim_ready_no_border_cb_4f101c(g2_lv_anim_t *a);
extern void widget_news_bounce_at_top_4f11c0(void);
extern void widget_news_start_expand_4f1544(void);
extern void widget_news_start_collapse_4f18ac(void);
extern int32_t News_Widget_ext_init_4f4670(void *parent);

void widget_news_detail_update_scrollbar_4f2210(int32_t scroll_y);
void widget_news_detail_scroll_anim_cb_4f2264(void *obj, int32_t y);
void widget_news_detail_bounce_anim_cb_4f2288(void *obj, int32_t y);
void widget_news_detail_bounce_ready_cb_4f2294(g2_lv_anim_t *a);
void widget_news_detail_bounce_at_top_4f2318(void);
void widget_news_detail_bounce_at_bottom_4f23e4(void);
void widget_news_scroll_ready_cb_4f24cc(g2_lv_anim_t *a);
int32_t widget_news_calculate_scroll_pos_4f2804(int32_t index);
void widget_news_end_item_show_error_4f2acc(void *end_item);
void widget_news_end_item_show_no_updates_4f2b30(void *end_item);

static const char module_tag[] = "dashborad.news.widget"; /* ROM 0x77d624 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_widget_news_page.c"; /* ROM 0x6eae4c */

static const char load_fn[] = "widget_news_detail_load_content"; /* ROM 0x767e90 */
static const char expand_null[] = "Expand container is NULL"; /* ROM 0x774528 */
static const char expand_null_short[] = "[dashborad.news.widget]Expand container is NULL"; /* ROM 0x73b234 */
static const char no_data[] = "Cannot find valid news data for index %d"; /* ROM 0x74687c */
static const char no_data_short[] =
    "[dashborad.news.widget]Cannot find valid news data for index %d"; /* ROM 0x7118e4 */
static const char loading[] = "Loading detail content for data[%d]: %s"; /* ROM 0x7510bc */
static const char loading_short[] =
    "[dashborad.news.widget]Loading detail content for data[%d]: %s"; /* ROM 0x711924 */
static const char viewport_fail[] = "Failed to create detail viewport"; /* ROM 0x75cf48 */
static const char viewport_fail_short[] =
    "[dashborad.news.widget]Failed to create detail viewport"; /* ROM 0x725f08 */
static const char content_fail[] = "Failed to create detail content container"; /* ROM 0x7468a8 */
static const char content_fail_short[] =
    "[dashborad.news.widget]Failed to create detail content container"; /* ROM 0x70841c */
static const char date_fmt[] = "%02d/%02d"; /* ROM 0x78c8cc */
static const char time12_fmt[] = "%02d:%02d %s"; /* ROM 0x789eb0 */
static const char time24_fmt[] = "%02d:%02d"; /* ROM 0x78c8d8 */
static const char am_text[] = "AM"; /* ROM 0x4f225c */
static const char pm_text[] = "PM"; /* ROM 0x4f2260 */
static const char loaded[] = "Detail content loaded: content_height=%d, viewport_height=%d"; /* ROM 0x711964 */
static const char loaded_short[] =
    "[dashborad.news.widget]Detail content loaded: content_height=%d, viewport_height=%d"; /* ROM 0x6eaea0 */
static const char bar_created[] = "Scrollbar created: bar_h=%d, track_h=%d, pad_y=%d"; /* ROM 0x730988 */
static const char bar_created_short[] =
    "[dashborad.news.widget]Scrollbar created: bar_h=%d, track_h=%d, pad_y=%d"; /* ROM 0x6f7960 */

static const char bounce_ready_fn[] = "widget_news_detail_bounce_ready_cb"; /* ROM 0x75cf6c */
static const char bounce_done[] = "Detail bounce completed, restored scroll_y=%d"; /* ROM 0x73b264 */
static const char bounce_done_short[] =
    "[dashborad.news.widget]Detail bounce completed, restored scroll_y=%d"; /* ROM 0x6ff35c */
static const char bounce_top_fn[] = "widget_news_detail_bounce_at_top"; /* ROM 0x75cf90 */
static const char bounce_top[] = "Detail bounce at top started"; /* ROM 0x767eb0 */
static const char bounce_top_short[] = "[dashborad.news.widget]Detail bounce at top started"; /* ROM 0x7309bc */
static const char bounce_bottom_fn[] = "widget_news_detail_bounce_at_bottom"; /* ROM 0x75cfb4 */
static const char bounce_bottom[] = "Detail bounce at bottom started (bottom_y=%d)"; /* ROM 0x73b294 */
static const char bounce_bottom_short[] =
    "[dashborad.news.widget]Detail bounce at bottom started (bottom_y=%d)"; /* ROM 0x6ff3a4 */
static const char scroll_ready_fn[] = "widget_news_scroll_ready_cb"; /* ROM 0x774544 */
static const char scroll_ready[] = "Detail scroll ready."; /* ROM 0x77d654 */
static const char scroll_ready_short[] = "[dashborad.news.widget]Detail scroll ready."; /* ROM 0x7468d4 */

static const char scroll_by_fn[] = "widget_news_detail_scroll_by"; /* ROM 0x767ed0 */
static const char fits[] = "Content fits in viewport, no scroll needed"; /* ROM 0x746900 */
static const char fits_short[] =
    "[dashborad.news.widget]Content fits in viewport, no scroll needed"; /* ROM 0x708460 */
static const char not_valid[] = "Detail content is not valid, ignore scroll"; /* ROM 0x74692c */
static const char not_valid_short[] =
    "[dashborad.news.widget]Detail content is not valid, ignore scroll"; /* ROM 0x7084a4 */
static const char bouncing[] = "Bouncing in progress, ignore same-direction scroll"; /* ROM 0x7309f0 */
static const char bouncing_short[] =
    "[dashborad.news.widget]Bouncing in progress, ignore same-direction scroll"; /* ROM 0x6f79ac */
static const char scroll_anim[] = "Detail scroll anim: from=%d to=%d, speed=%d"; /* ROM 0x746958 */
static const char scroll_anim_short[] =
    "[dashborad.news.widget]Detail scroll anim: from=%d to=%d, speed=%d"; /* ROM 0x7084e8 */

static const char calc_fn[] = "widget_news_calculate_scroll_pos"; /* ROM 0x75cfd8 */
static const char calc_msg[] =
    "Calculated scroll position: target_index=%d, target_y=%d, scroll_pos=%d"; /* ROM 0x6ff3ec */
static const char calc_msg_short[] =
    "[dashborad.news.widget]Calculated scroll position: target_index=%d, target_y=%d, scroll_pos=%d"; /* ROM 0x6def14 */
static const char scroll_to_fn[] = "widget_news_scroll_to_item"; /* ROM 0x774560 */
static const char bad_index[] = "Invalid target index: %d (count=%d)"; /* ROM 0x75cffc */
static const char bad_index_short[] =
    "[dashborad.news.widget]Invalid target index: %d (count=%d)"; /* ROM 0x71b22c */
static const char no_container[] = "Scroll container is NULL"; /* ROM 0x77457c */
static const char no_container_short[] = "[dashborad.news.widget]Scroll container is NULL"; /* ROM 0x73b2c4 */
static const char anim_started[] = "Started scroll animation to item %d, y=%d, time=%ums"; /* ROM 0x725f40 */
static const char anim_started_short[] =
    "[dashborad.news.widget]Started scroll animation to item %d, y=%d, time=%ums"; /* ROM 0x6f79f8 */
static const char no_anim[] = "Scrolled to item %d without animation, y=%d"; /* ROM 0x746984 */
static const char no_anim_short[] =
    "[dashborad.news.widget]Scrolled to item %d without animation, y=%d"; /* ROM 0x70852c */

static const char id_went_wrong[] = "ID_GENERAL_SOMETHING_WENT_WRONG"; /* ROM 0x767ef0 */
static const char id_no_updates[] = "ID_DASHBOARD_NEWS_NO_UPDATES"; /* ROM 0x767f10 */
static const char id_scroll_refresh[] = "ID_DASHBOARD_NEWS_SCROLL_TO_REFRESH_NEWS"; /* ROM 0x7467f8 */

static const char updating_fn[] = "Start_NewsUpdating_Animation"; /* ROM 0x767f30 */
static const char anim_fail[] = "Failed to create loading animation"; /* ROM 0x75d020 */
static const char anim_fail_short[] =
    "[dashborad.news.widget]Failed to create loading animation"; /* ROM 0x71b268 */

static const char reflash_fn[] = "NewsWidget_AutoReflash"; /* ROM 0x77d66c */
static const char ext_init_zero[] = "widget_news_ext_init_flag == 0, return"; /* ROM 0x7510e4 */
static const char ext_init_zero_short[] =
    "[dashborad.news.widget]widget_news_ext_init_flag == 0, return"; /* ROM 0x7119a4 */
static const char reflash_send[] =
    "NewsWidget_AutoReflash: send DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT to dashboard"; /* ROM 0x6f0fd8 */
static const char reflash_send_short[] =
    "[dashborad.news.widget]NewsWidget_AutoReflash: send DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT to dashboard"; /* ROM 0x6d9be4 */

static const char resume_fn[] = "NewsWidget_ScrollLableResume_Handler"; /* ROM 0x75110c */
static const char resume_msg[] = "NewsWidget_ScrollLableResume_Handler"; /* ROM 0x751134 */
static const char resume_msg_short[] =
    "[dashborad.news.widget]NewsWidget_ScrollLableResume_Handler"; /* ROM 0x71b2a4 */
static const char end_item_bad[] = "end_item is not valid"; /* ROM 0x77d684 */
static const char end_item_bad_short[] = "[dashborad.news.widget]end_item is not valid"; /* ROM 0x73b2f4 */

static const char timeout_fn[] = "NewsWidget_UpdateTimeout_Handler"; /* ROM 0x75d044 */
static const char no_sources_fn[] = "NewsWidget_NoSources_Handler"; /* ROM 0x767f50 */
static const char timeout_msg[] = "DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT"; /* ROM 0x75d068 */
static const char timeout_msg_short[] =
    "[dashborad.news.widget]DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT"; /* ROM 0x71b2e0 */

static const char load_content_fn[] = "NewsWidget_LoadContent_Handler"; /* ROM 0x767f70 */
static const char load_content_msg[] = "NewsWidget_LoadContent_Handler"; /* ROM 0x767f90 */
static const char load_content_msg_short[] =
    "[dashborad.news.widget]NewsWidget_LoadContent_Handler"; /* ROM 0x725f78 */
static const char clear_content_fn[] = "NewsWidget_ClearContent_Handler"; /* ROM 0x767fb0 */
static const char clear_content_msg[] =
    "NewsWidget_ClearContent_Handler, clear list list content"; /* ROM 0x71b31c */
static const char clear_content_msg_short[] =
    "[dashborad.news.widget]NewsWidget_ClearContent_Handler, clear list list content"; /* ROM 0x6f1028 */

static const char ext_fn[] = "news_widget_ext_event_handler"; /* ROM 0x767fd0 */
static const char len_zero[] = "len == 0, return"; /* ROM 0x784b08 */
static const char len_zero_short[] = "[dashborad.news.widget]len == 0, return"; /* ROM 0x75115c */
static const char ext_code[] = "news_widget_ext_event_handler: code = %d, value = %u"; /* ROM 0x725fb0 */
static const char ext_code_short[] =
    "[dashborad.news.widget]news_widget_ext_event_handler: code = %d, value = %u"; /* ROM 0x6f7a44 */
static const char ext_down[] = "news_widget_ext_event_handler: SCROLLDOWN_EVENT"; /* ROM 0x73b324 */
static const char ext_down_short[] =
    "[dashborad.news.widget]news_widget_ext_event_handler: SCROLLDOWN_EVENT"; /* ROM 0x6ff434 */
static const char ext_not_init[] = "widget_news_ext_init_flag != 1, return"; /* ROM 0x751184 */
static const char ext_not_init_short[] =
    "[dashborad.news.widget]widget_news_ext_init_flag != 1, return"; /* ROM 0x7119e4 */
static const char ext_no_container[] = "widget_news_ext_scroll_container == NULL, return"; /* ROM 0x730a24 */
static const char ext_no_container_short[] =
    "[dashborad.news.widget]widget_news_ext_scroll_container == NULL, return"; /* ROM 0x6ff47c */
static const char push_down[] =
    "Animation in progress, ignore scroll down event,push event to fifo"; /* ROM 0x708570 */
static const char push_down_short[] =
    "[dashborad.news.widget]Animation in progress, ignore scroll down event,push event to fifo"; /* ROM 0x6e200c */
static const char cur_scroll[] = "NewsWidget_ext_event_handler: current_scroll = %d"; /* ROM 0x730a58 */
static const char cur_scroll_short[] =
    "[dashborad.news.widget]NewsWidget_ext_event_handler: current_scroll = %d"; /* ROM 0x6f7a90 */
static const char to_next[] = "Scrolling to next item (current_index=%d)"; /* ROM 0x7469b0 */
static const char to_next_short[] =
    "[dashborad.news.widget]Scrolling to next item (current_index=%d)"; /* ROM 0x7085b4 */
static const char end_item_ok[] = "NewsWidget_ext_event_handler: end_item is not NULL"; /* ROM 0x730a8c */
static const char end_item_ok_short[] =
    "[dashborad.news.widget]NewsWidget_ext_event_handler: end_item is not NULL"; /* ROM 0x6f7adc */
static const char to_end[] = "Scrolling to show end_item (end_y=%d, current=%d)"; /* ROM 0x730ac0 */
static const char to_end_short[] =
    "[dashborad.news.widget]Scrolling to show end_item (end_y=%d, current=%d)"; /* ROM 0x6f7b28 */
static const char hide_border[] = "NewsWidget_ext_event_handler: hide item border"; /* ROM 0x73b354 */
static const char hide_border_short[] =
    "[dashborad.news.widget]NewsWidget_ext_event_handler: hide item border"; /* ROM 0x6ff4c4 */
static const char no_end_item[] = "No end_item, already at last news item"; /* ROM 0x7511ac */
static const char no_end_item_short[] =
    "[dashborad.news.widget]No end_item, already at last news item"; /* ROM 0x711a24 */
static const char detail_down[] = "Detail page scroll down"; /* ROM 0x77d69c */
static const char detail_down_short[] = "[dashborad.news.widget]Detail page scroll down"; /* ROM 0x73b384 */
static const char ext_up[] = "news_widget_ext_event_handler: SCROLLUP_EVENT"; /* ROM 0x73b3b4 */
static const char ext_up_short[] =
    "[dashborad.news.widget]news_widget_ext_event_handler: SCROLLUP_EVENT"; /* ROM 0x6ff50c */
static const char list_mode[] =
    "NewsWidget_ext_event_handler: widget_news_expand_page_flag == 0 && widget_news_ext_init_flag == 1"; /* ROM 0x6dbeac */
static const char list_mode_short[] =
    "[dashborad.news.widget]NewsWidget_ext_event_handler: widget_news_expand_page_flag == 0 && widget_news_ext_init_flag == 1"; /* ROM 0x69d614 */
static const char push_up[] =
    "Animation in progress, ignore scroll up event,push event to fifo"; /* ROM 0x7085f8 */
static const char push_up_short[] =
    "[dashborad.news.widget]Animation in progress, ignore scroll up event,push event to fifo"; /* ROM 0x6e5b38 */
static const char in_end_area[] =
    "In end_item area (scroll=%d > last_item_scroll=%d), scrolling back to last news item"; /* ROM 0x6e5b90 */
static const char in_end_area_short[] =
    "[dashborad.news.widget]In end_item area (scroll=%d > last_item_scroll=%d), scrolling back to last news item"; /* ROM 0x6d8170 */
static const char to_prev[] = "Scrolling to previous item (current_index=%d)"; /* ROM 0x73b3e4 */
static const char to_prev_short[] =
    "[dashborad.news.widget]Scrolling to previous item (current_index=%d)"; /* ROM 0x6ff554 */
static const char not_top[] = "Not at correct top position (current=%d), scrolling back"; /* ROM 0x71b358 */
static const char not_top_short[] =
    "[dashborad.news.widget]Not at correct top position (current=%d), scrolling back"; /* ROM 0x6f1078 */
static const char at_top[] = "At top (scroll=%d), executing rubber band bounce effect"; /* ROM 0x725fe8 */
static const char at_top_short[] =
    "[dashborad.news.widget]At top (scroll=%d), executing rubber band bounce effect"; /* ROM 0x6f10c8 */
static const char detail_up[] = "Detail page scroll up"; /* ROM 0x77d6b4 */
static const char detail_up_short[] = "[dashborad.news.widget]Detail page scroll up"; /* ROM 0x73b414 */
static const char click_busy[] = "Animation in progress, ignore click event"; /* ROM 0x7469dc */
static const char click_busy_short[] =
    "[dashborad.news.widget]Animation in progress, ignore click event"; /* ROM 0x70863c */
static const char click_list[] = "Click on list page, starting expand animation"; /* ROM 0x73b444 */
static const char click_list_short[] =
    "[dashborad.news.widget]Click on list page, starting expand animation"; /* ROM 0x6ff59c */
static const char click_detail[] = "Click on detail page, drop it..."; /* ROM 0x75d08c */
static const char click_detail_short[] =
    "[dashborad.news.widget]Click on detail page, drop it..."; /* ROM 0x726020 */
static const char collapse[] = "Click on detail page, starting collapse animation"; /* ROM 0x730af4 */
static const char collapse_short[] =
    "[dashborad.news.widget]Click on detail page, starting collapse animation"; /* ROM 0x6f7b74 */

static const char input_fn[] = "NewsWidgetInputEventHandler"; /* ROM 0x774598 */
static const char in_switching[] =
    "NewsInputEventHandler: news_widget_is_switching == 1, ignore clicked event"; /* ROM 0x6f7bc0 */
static const char in_switching_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: news_widget_is_switching == 1, ignore clicked event"; /* ROM 0x6dbf10 */
static const char in_updating[] =
    "NewsInputEventHandler: widget_news_expand_page_flag == 0 && widget_news_ext_init_flag == 1 && news_widget_is_update_animating == 1, send DASHBOARD_NEWS_LOAD_CONTENT_EVENT to dashboard"; /* ROM 0x6d1d54 */
static const char in_updating_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: widget_news_expand_page_flag == 0 && widget_news_ext_init_flag == 1 && news_widget_is_update_animating == 1, send DASHBOARD_NEWS_LOAD_CONTENT_EVENT to dashboard"; /* ROM 0x6d1144 */
static const char in_detail_busy[] =
    "NewsInputEventHandler: widget_news_detail_is_scrolling == 1 || widget_news_detail_is_bouncing == 1, ignore clicked event"; /* ROM 0x69da14 */
static const char in_detail_busy_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: widget_news_detail_is_scrolling == 1 || widget_news_detail_is_bouncing == 1, ignore clicked event"; /* ROM 0x6d4050 */
static const char in_anim_updating[] =
    "NewsInputEventHandler: news_is_animating == 1 && news_widget_is_update_animating == 1, ignore scroll down event"; /* ROM 0x6d7890 */
static const char in_anim_updating_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: news_is_animating == 1 && news_widget_is_update_animating == 1, ignore scroll down event"; /* ROM 0x6d4a98 */
static const char in_animating[] =
    "NewsInputEventHandler: news_is_animating == 1, ignore scroll down event"; /* ROM 0x6ff5e4 */
static const char in_animating_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: news_is_animating == 1, ignore scroll down event"; /* ROM 0x6def74 */
static const char in_down[] = "NewsInputEventHandler: scroll down event"; /* ROM 0x746a08 */
static const char in_down_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: scroll down event"; /* ROM 0x711a64 */
static const char in_up[] = "NewsInputEventHandler: scroll up event"; /* ROM 0x7511d4 */
static const char in_up_short[] =
    "[dashborad.news.widget]NewsInputEventHandler: scroll up event"; /* ROM 0x711aa4 */

/* Loading spinner: 25 frames of 24x24, 50 ms, loop; colours replaced at run time. */
static const g2_generic_animation_config_t news_loading_anim_config = {
    g2_news_loading_frames_20004330, 25u, 50u, 0u, {0u, 0u, 0u}, 24, 24,
    {0u, 0u, 0u}, 0xffu, {0u, 0u, 0u}, 0u,
}; /* ROM 0x767ff0 */

/* Both sinks are tested separately and every argument is evaluated per sink,
 * as in stock. The compressed-log word is level << 26 | argument count << 22. */
#define NEWS_LOG(level, func, line, nargs, text, short_text, ...)                              \
    do {                                                                                       \
        if ((audio_log_flags() & 2u) != 0u)                                                    \
            audio_log_extended((level), module_tag, source_file, (func), (line), (text),       \
                               ##__VA_ARGS__);                                                 \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                  \
            (void)compress_log_output(((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22),   \
                                      (short_text), (short_text), ##__VA_ARGS__);              \
    } while (0)

#define NEWS_TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))
#define NEWS_FONT() audio_uart_ring_primary_head_cell
#define NEWS_LINE_SPACE() (NEWS_DETAIL_LINE - ((const g2_lv_font_head_t *)NEWS_FONT())->line_height)
/* Lowest (most negative) detail y: the overflow rounded up to whole lines. */
#define NEWS_DETAIL_BOTTOM()                                                                   \
    (((g2_news_detail_20074eb8 - g2_news_detail_20074ebc + 27) /   \
      NEWS_DETAIL_LINE) * -NEWS_DETAIL_LINE)

static uint8_t *news_cache_entry(int32_t slot)
{
    return &g2_dashboard_news_cache_20132f74[(uint32_t)slot * NEWS_CACHE_STRIDE];
}

/* Build the expanded page for the index-th valid cache record: a clipped
 * viewport holding a column of {time icon, date/time, source}, title, body,
 * plus a 2 px scrollbar when the column is taller than the viewport. */
void widget_news_detail_load_content_4f1ab8(int32_t index)
{
    if (g2_news_expand_container_20074ea0 == NULL) {
        NEWS_LOG(1u, load_fn, 0x3ccu, 0u, expand_null, expand_null_short);
        return;
    }

    int32_t slot = -1;
    int32_t valid = 0;
    for (int32_t i = 0; i < NEWS_CACHE_COUNT; i++) {
        if (news_cache_entry(i)[0] == 1u) {
            if (valid == index) {
                slot = i;
                break;
            }
            valid++;
        }
    }
    if (slot < 0) {
        NEWS_LOG(1u, load_fn, 0x3ddu, 1u, no_data, no_data_short, index);
        return;
    }
    NEWS_LOG(3u, load_fn, 0x3e1u, 2u, loading, loading_short, slot,
             (const char *)&news_cache_entry(slot)[NEWS_OFF_TITLE]);

    g2_news_detail_20074ea4 = audio_uart_page_43de82(g2_news_expand_container_20074ea0);
    if (g2_news_detail_20074ea4 == NULL) {
        NEWS_LOG(1u, load_fn, 1000u, 0u, viewport_fail, viewport_fail_short);
        return;
    }
    audio_uart_page_43f4c0(g2_news_detail_20074ea4, 0x23c, 0xfc);
    audio_uart_page_43f09a(g2_news_detail_20074ea4, 0, 0x10);
    audio_uart_page_44129e(g2_news_detail_20074ea4, 0u, 0u);
    audio_uart_page_44131c(g2_news_detail_20074ea4, 0, 0u);
    audio_uart_page_44122a(g2_news_detail_20074ea4, 20, 0u);
    audio_uart_page_441238(g2_news_detail_20074ea4, 8, 0u);
    audio_uart_page_44120e(g2_news_detail_20074ea4, 0, 0u);
    audio_uart_page_44121c(g2_news_detail_20074ea4, 16, 0u);
    audio_uart_page_44146a(g2_news_detail_20074ea4, 0, 0u);
    style_prop_2d_441478(g2_news_detail_20074ea4, 1u, 0u);
    audio_uart_page_43dfa4(g2_news_detail_20074ea4, LV_OBJ_FLAG_SCROLLABLE);

    g2_news_detail_20074ea8 = audio_uart_page_43de82(g2_news_detail_20074ea4);
    if (g2_news_detail_20074ea8 == NULL) {
        NEWS_LOG(1u, load_fn, 0x3ffu, 0u, content_fail, content_fail_short);
        return;
    }
    const int32_t width = NEWS_DETAIL_CONTENT_W;
    audio_uart_page_43f506(g2_news_detail_20074ea8, width);
    audio_uart_page_43f568(g2_news_detail_20074ea8, LV_SIZE_CONTENT);
    audio_uart_page_43f09a(g2_news_detail_20074ea8, 0, 0);
    audio_uart_page_44129e(g2_news_detail_20074ea8, 0u, 0u);
    audio_uart_page_44131c(g2_news_detail_20074ea8, 0, 0u);
    audio_uart_page_44122a(g2_news_detail_20074ea8, 0, 0u);
    audio_uart_page_441238(g2_news_detail_20074ea8, 0, 0u);
    audio_uart_page_44120e(g2_news_detail_20074ea8, 2, 0u);
    audio_uart_page_44121c(g2_news_detail_20074ea8, 0, 0u);
    audio_uart_page_44146a(g2_news_detail_20074ea8, 0, 0u);
    audio_uart_page_43dfa4(g2_news_detail_20074ea8, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_48ba78(g2_news_detail_20074ea8, LV_FLEX_FLOW_COLUMN);
    audio_uart_page_441246(g2_news_detail_20074ea8, NEWS_DETAIL_LINE, 0u);

    void *row = audio_uart_page_43de82(g2_news_detail_20074ea8);
    audio_uart_page_43f506(row, width);
    audio_uart_page_43f568(row, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, 0u);
    audio_uart_page_44131c(row, 0, 0u);
    lv_obj_set_style_pad_all_4effa8(row, 0, 0u);
    audio_uart_page_43dfa4(row, LV_OBJ_FLAG_SCROLLABLE);

    void *icon = audio_uart_page_498668(row);
    audio_uart_page_498680(icon, news_icon_76e7c0);
    audio_uart_page_43f4c0(icon, 24, 24);
    audio_uart_page_43f09a(icon, 0, 2);
    audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

    /* Older than today: date (order from the date-format setting), else time. */
    char when[32];
    g2_calendar_t published;
    g2_calendar_t now;
    audio_uart_buffer_zero(when, sizeof when, 0u);
    uint8_t *entry = news_cache_entry(slot);
    const uint32_t *ms = (const uint32_t *)(const void *)&entry[NEWS_OFF_TIME_MS];
    audio_time_epoch_to_calendar_44a100((uint32_t)audio_uart_ring_u64_div_47cc60(ms[0], ms[1], 1000u, 0u),
                                        &published);
    service_time_current_calendar_get(&now);
    if (published.year < now.year ||
        (now.year == published.year && published.month < now.month) ||
        (now.year == published.year && now.month == published.month && published.day < now.day)) {
        if (svc_universal_setting_get_date_format_466500() == 0u ||
            svc_universal_setting_get_date_format_466500() == 1u)
            (void)g2_audio_dump_snprintf(when, sizeof when, date_fmt, published.month, published.day);
        else
            (void)g2_audio_dump_snprintf(when, sizeof when, date_fmt, published.day, published.month);
    } else if (audio_time_format_mode_46650c() == 1u) {
        uint32_t hour = published.hour % 12u;
        if (hour == 0u)
            hour = 12u;
        (void)g2_audio_dump_snprintf(when, sizeof when, time12_fmt, hour, published.minute,
                                     published.hour < 12u ? am_text : pm_text);
    } else {
        (void)g2_audio_dump_snprintf(when, sizeof when, time24_fmt, published.hour, published.minute);
    }

    void *time_label = audio_uart_page_499416(row);
    audio_uart_page_43f506(time_label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(time_label, NEWS_DETAIL_LINE);
    audio_uart_page_43f6b8(time_label, LV_ALIGN_TOP_RIGHT, 0, 0);
    (void)audio_uart_page_49942e(time_label, when);
    audio_uart_page_44140e(time_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(time_label, NEWS_FONT(), 0u);
    audio_uart_page_43f66c(time_label);
    int32_t time_width = audio_uart_lv_obj_width_43fd9e(time_label);

    void *source = audio_uart_page_499416(row);
    audio_uart_page_43f506(source, (width - 0x2c) - time_width);
    audio_uart_page_43f568(source, NEWS_DETAIL_LINE);
    audio_uart_page_43f09a(source, 32, 0);
    audio_uart_page_layout_499678(source, LV_LABEL_LONG_DOT);
    (void)audio_uart_page_49942e(source, (const char *)&news_cache_entry(slot)[NEWS_OFF_SOURCE]);
    audio_uart_page_44140e(source, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(source, NEWS_FONT(), 0u);

    void *title = audio_uart_page_499416(g2_news_detail_20074ea8);
    audio_uart_page_43f506(title, 400);
    audio_uart_page_43f568(title, LV_SIZE_CONTENT);
    audio_uart_page_layout_499678(title, LV_LABEL_LONG_WRAP);
    (void)audio_uart_page_49942e(title, (const char *)&news_cache_entry(slot)[NEWS_OFF_TITLE]);
    audio_uart_page_44140e(title, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(title, NEWS_FONT(), 0u);
    audio_uart_page_44144c(title, NEWS_LINE_SPACE(), 0u);

    if (g2_log_module_length((const char *)&news_cache_entry(slot)[NEWS_OFF_BODY]) != 0u) {
        void *body = audio_uart_page_499416(g2_news_detail_20074ea8);
        audio_uart_page_43f506(body, width);
        audio_uart_page_43f568(body, LV_SIZE_CONTENT);
        audio_uart_page_layout_499678(body, LV_LABEL_LONG_WRAP);
        (void)audio_uart_page_49942e(body, (const char *)&news_cache_entry(slot)[NEWS_OFF_BODY]);
        audio_uart_page_44140e(body, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44143e(body, NEWS_FONT(), 0u);
        audio_uart_page_44144c(body, NEWS_LINE_SPACE(), 0u);
    }

    audio_uart_page_43f66c(g2_news_detail_20074ea8);
    g2_news_detail_20074eb8 = audio_uart_lv_obj_height_43fdda(g2_news_detail_20074ea8);
    g2_news_detail_20074ebc = NEWS_DETAIL_VIEWPORT_H;
    g2_news_detail_20074eb0 = 0;
    g2_news_detail_20074eb4 = 0;
    g2_news_detail_20074ec0 = 0;
    NEWS_LOG(3u, load_fn, 0x47cu, 2u, loaded, loaded_short, g2_news_detail_20074eb8,
             g2_news_detail_20074ebc);

    if (g2_news_detail_20074ebc < g2_news_detail_20074eb8) {
        int32_t track = g2_news_detail_20074ebc;
        int32_t bar_h = (g2_news_detail_20074ebc * track) /
                        g2_news_detail_20074eb8;
        if (bar_h < 16)
            bar_h = 16;
        g2_news_detail_20074eac = audio_uart_page_43de82(g2_news_detail_20074ea4);
        if (g2_news_detail_20074eac != NULL) {
            audio_uart_page_43f4c0(g2_news_detail_20074eac, 2, bar_h);
            audio_uart_page_43f09a(g2_news_detail_20074eac, 0x220, 0);
            audio_uart_page_44127e(g2_news_detail_20074eac, audio_uart_page_44104c(0x555555u), 0u);
            audio_uart_page_44129e(g2_news_detail_20074eac, 0x7fu, 0u);
            audio_uart_page_44131c(g2_news_detail_20074eac, 0, 0u);
            audio_uart_page_44146a(g2_news_detail_20074eac, 1, 0u);
            lv_obj_set_style_pad_all_4effa8(g2_news_detail_20074eac, 0, 0u);
            audio_uart_page_43dfa4(g2_news_detail_20074eac, LV_OBJ_FLAG_SCROLLABLE);
            NEWS_LOG(3u, load_fn, 0x497u, 3u, bar_created, bar_created_short, bar_h, track, 20);
        }
    }
}

/* Place the scrollbar thumb for a (non-positive) content y. */
void widget_news_detail_update_scrollbar_4f2210(int32_t scroll_y)
{
    if (g2_news_detail_20074eac == NULL)
        return;
    int32_t track = g2_news_detail_20074ebc;
    int32_t bar_h = audio_uart_lv_obj_height_43fdda(g2_news_detail_20074eac);
    int32_t range = g2_news_detail_20074eb8 - g2_news_detail_20074ebc;
    int32_t y = 0;
    if (range > 0) {
        y = -(((track - bar_h) * scroll_y) / range);
        if (y < 0)
            y = 0;
        if (track - bar_h < y)
            y = track - bar_h;
    }
    audio_uart_page_43f142(g2_news_detail_20074eac, y);
}

void widget_news_detail_scroll_anim_cb_4f2264(void *obj, int32_t y)
{
    if (obj != NULL) {
        audio_uart_page_43f142(obj, y);
        g2_news_detail_20074eb0 = y;
        widget_news_detail_update_scrollbar_4f2210(y);
    }
}

void widget_news_detail_bounce_anim_cb_4f2288(void *obj, int32_t y)
{
    if (obj != NULL)
        audio_uart_page_43f142(obj, y);
}

void widget_news_detail_bounce_ready_cb_4f2294(g2_lv_anim_t *a)
{
    (void)a;
    g2_news_detail_20074ec0 = 0;
    g2_news_detail_scrolling_20074ec4 = 0;
    if (g2_news_detail_20074ea8 != NULL)
        audio_uart_page_43f142(g2_news_detail_20074ea8, g2_news_detail_20074eb0);
    NEWS_LOG(4u, bounce_ready_fn, 0x4cdu, 1u, bounce_done, bounce_done_short,
             g2_news_detail_20074eb0);
}

/* Rubber band: 32 px out in 150 ms, back in 180 ms (playback). */
void widget_news_detail_bounce_at_top_4f2318(void)
{
    if (g2_news_detail_20074ea8 == NULL)
        return;
    g2_lv_anim_t a;
    g2_news_detail_20074ec0 = 1;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_detail_20074ea8;
    a.exec_cb = widget_news_detail_bounce_anim_cb_4f2288;
    audio_uart_lv_anim_values_4506ce(&a, 0, 32);
    a.duration = 150;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.reverse_duration = 180u;
    a.reverse_delay = 0u;
    g2_news_detail_scrolling_20074ec4 = 1;
    a.completed_cb = widget_news_detail_bounce_ready_cb_4f2294;
    (void)audio_uart_lv_anim_start_450408(&a);
    NEWS_LOG(4u, bounce_top_fn, 0x4e3u, 0u, bounce_top, bounce_top_short);
}

void widget_news_detail_bounce_at_bottom_4f23e4(void)
{
    if (g2_news_detail_20074ea8 == NULL)
        return;
    g2_lv_anim_t a;
    g2_news_detail_20074ec0 = 1;
    int32_t bottom = NEWS_DETAIL_BOTTOM();
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_detail_20074ea8;
    a.exec_cb = widget_news_detail_bounce_anim_cb_4f2288;
    audio_uart_lv_anim_values_4506ce(&a, bottom, bottom - 32);
    a.duration = 150;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.reverse_duration = 180u;
    a.reverse_delay = 0u;
    g2_news_detail_scrolling_20074ec4 = 1;
    a.completed_cb = widget_news_detail_bounce_ready_cb_4f2294;
    (void)audio_uart_lv_anim_start_450408(&a);
    NEWS_LOG(4u, bounce_bottom_fn, 0x4fcu, 1u, bounce_bottom, bounce_bottom_short, bottom);
}

void widget_news_scroll_ready_cb_4f24cc(g2_lv_anim_t *a)
{
    (void)a;
    g2_news_detail_scrolling_20074ec4 = 0;
    NEWS_LOG(4u, scroll_ready_fn, 0x502u, 0u, scroll_ready, scroll_ready_short);
}

/* Scroll the detail column by whole lines; direction > 0 moves the text up
 * (scroll down). Fast swipes (speed > 100) scroll twice the distance. At an
 * end the same-direction swipe bounces instead. */
void widget_news_detail_scroll_by_4f2554(int32_t direction, int32_t speed, int32_t distance)
{
    if (g2_news_detail_20074ea8 == NULL || g2_news_detail_20074ea4 == NULL)
        return;
    if (g2_news_detail_20074ebc >= g2_news_detail_20074eb8) {
        NEWS_LOG(4u, scroll_by_fn, 0x510u, 0u, fits, fits_short);
        return;
    }
    if (audio_terminal_ui_object_valid_43e2ea(g2_news_detail_20074ea8) == 0u) {
        NEWS_LOG(4u, scroll_by_fn, 0x515u, 0u, not_valid, not_valid_short);
        return;
    }

    int32_t bottom = NEWS_DETAIL_BOTTOM();
    if (g2_news_detail_20074ec0 != 0) {
        if ((direction > 0 && g2_news_detail_20074eb4 <= bottom) ||
            (direction < 0 && g2_news_detail_20074eb4 >= 0)) {
            NEWS_LOG(4u, scroll_by_fn, 0x520u, 0u, bouncing, bouncing_short);
            return;
        }
        (void)audio_uart_anim_delete_450500(g2_news_detail_20074ea8,
                                            widget_news_detail_bounce_anim_cb_4f2288);
        g2_news_detail_20074ec0 = 0;
        audio_uart_page_43f142(g2_news_detail_20074ea8, g2_news_detail_20074eb0);
    }

    int32_t target;
    if (direction > 0) {
        if (speed > 100)
            distance <<= 1;
        target = ((g2_news_detail_20074eb4 -
                   ((distance + 27) / NEWS_DETAIL_LINE) * NEWS_DETAIL_LINE) / NEWS_DETAIL_LINE) *
                 NEWS_DETAIL_LINE;
        if (target < bottom)
            target = bottom;
    } else {
        if (speed > 100)
            distance <<= 1;
        target = ((((distance + 27) / NEWS_DETAIL_LINE) * NEWS_DETAIL_LINE +
                   g2_news_detail_20074eb4) / NEWS_DETAIL_LINE) * NEWS_DETAIL_LINE;
        if (target > 0)
            target = 0;
    }

    if (target == g2_news_detail_20074eb4) {
        if (g2_news_detail_20074ec0 == 0) {
            if (direction < 0 && g2_news_detail_20074eb4 >= 0)
                widget_news_detail_bounce_at_top_4f2318();
            else if (direction > 0 && g2_news_detail_20074eb4 <= bottom)
                widget_news_detail_bounce_at_bottom_4f23e4();
        }
        return;
    }

    g2_lv_anim_t a;
    g2_news_detail_20074eb4 = target;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_detail_20074ea8;
    a.exec_cb = widget_news_detail_scroll_anim_cb_4f2264;
    audio_uart_lv_anim_values_4506ce(&a, g2_news_detail_20074eb0, target);
    a.duration = 200;
    a.path_cb = audio_uart_lv_anim_path_450672;
    g2_news_detail_scrolling_20074ec4 = 1;
    a.completed_cb = widget_news_scroll_ready_cb_4f24cc;
    (void)audio_uart_lv_anim_start_450408(&a);
    NEWS_LOG(4u, scroll_by_fn, 0x562u, 3u, scroll_anim, scroll_anim_short,
             g2_news_detail_20074eb0, target, speed);
}

/* List scroll offset that centres item index in the 0x120 px view, but never
 * hides the bottom 30 px of the previous item; item 0 is always at 0. */
int32_t widget_news_calculate_scroll_pos_4f2804(int32_t index)
{
    if (index < 0 || index >= g2_news_item_count_20074e7c)
        return 0;
    void *item = g2_news_items_20073d9c[index];
    if (item == NULL)
        return 0;

    int32_t y = audio_uart_lv_obj_y_43fce0(item);
    int32_t h = audio_uart_lv_obj_height_43fdda(item);
    int32_t pos;
    if (index == 0) {
        pos = 0;
    } else {
        pos = y - (NEWS_LIST_VIEW_H - h) / 2;
        void *prev;
        if (index > 0 && (prev = g2_news_items_20073d9c[index - 1]) != NULL) {
            int32_t prev_y = audio_uart_lv_obj_y_43fce0(prev);
            int32_t min = audio_uart_lv_obj_height_43fdda(prev) + prev_y - 30;
            if (pos < min)
                pos = min;
        }
    }
    if (pos < 0)
        pos = 0;
    NEWS_LOG(4u, calc_fn, 0x599u, 3u, calc_msg, calc_msg_short, index, y, pos);
    return pos;
}

void widget_news_scroll_to_item_4f28f0(int32_t index, uint32_t time_ms)
{
    if (index < 0 || index >= g2_news_item_count_20074e7c) {
        NEWS_LOG(2u, scroll_to_fn, 0x5a5u, 2u, bad_index, bad_index_short, index,
                 g2_news_item_count_20074e7c);
        return;
    }
    if (g2_news_scroll_container_20074e74 == NULL) {
        NEWS_LOG(1u, scroll_to_fn, 0x5aau, 0u, no_container, no_container_short);
        return;
    }

    widget_news_hide_item_border_4f0e94(g2_news_selected_index_20074e78);
    g2_news_selected_index_20074e78 = index;
    int32_t pos = widget_news_calculate_scroll_pos_4f2804(index);
    if (time_ms == 0u) {
        audio_uart_lv_scroll_to_y_44ea04(g2_news_scroll_container_20074e74, pos, LV_ANIM_OFF);
        widget_news_show_item_border_4f0e18(index);
        NEWS_LOG(4u, scroll_to_fn, 0x5cbu, 2u, no_anim, no_anim_short, index, pos);
        return;
    }

    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_scroll_container_20074e74;
    a.exec_cb = widget_news_scroll_anim_exec_cb_4f0f1c;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(g2_news_scroll_container_20074e74),
                                     pos);
    a.duration = (int32_t)time_ms;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = widget_news_scroll_anim_ready_cb_4f0f26;
    g2_news_anim_running_20074e88 = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
    NEWS_LOG(4u, scroll_to_fn, 0x5c6u, 3u, anim_started, anim_started_short, index, pos, time_ms);
}

/* End-of-list status labels. */
void widget_news_end_item_show_error_4f2acc(void *end_item)
{
    if (audio_terminal_ui_object_valid_43e2ea(end_item) != 0u)
        audio_uart_page_44d878(end_item);
    void *label = audio_uart_page_499416(end_item);
    (void)audio_uart_page_49942e(label, NEWS_TR(id_went_wrong));
    audio_uart_page_44143e(label, NEWS_FONT(), 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f6b8(label, LV_ALIGN_CENTER, 0, 0);
}

void widget_news_end_item_show_no_updates_4f2b30(void *end_item)
{
    if (audio_terminal_ui_object_valid_43e2ea(end_item) != 0u)
        audio_uart_page_44d878(end_item);
    void *label = audio_uart_page_499416(end_item);
    (void)audio_uart_page_49942e(label, NEWS_TR(id_no_updates));
    audio_uart_page_44143e(label, NEWS_FONT(), 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f6b8(label, LV_ALIGN_CENTER, 0, 0);
}

/* Replace the end item with a centred loading spinner and arm the 600-tick
 * update timeout. Returns 0, or -1 when the animation cannot be created. */
int32_t Start_NewsUpdating_Animation_4f2bbc(void *parent, void **anim_out)
{
    if (audio_terminal_ui_object_valid_43e2ea(parent) != 0u)
        audio_uart_page_44d878(parent);
    void *box = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(box, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(box, 0u, 0u);
    audio_uart_page_44131c(box, 0, 0u);
    lv_obj_set_style_pad_all_4effa8(box, 0, 0u);
    audio_uart_page_48ba78(box, LV_FLEX_FLOW_ROW);
    audio_uart_page_48ba92(box, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    audio_uart_page_441254(box, 8, 0u);
    audio_uart_page_43f6b8(box, LV_ALIGN_CENTER, 0, 0);

    g2_generic_animation_config_t config;
    uint32_t color;
    (void)aeabi_memcpy4_439c04(&config, &news_loading_anim_config, sizeof config);
    color = lv_color_white_441094();
    (void)audio_queue_copy_bytes(config.color_a, &color, 3u);
    color = lv_color_black_4410a6();
    (void)audio_queue_copy_bytes(config.bg_color, &color, 3u);

    *anim_out = generic_animation_create_463c68(box, &config);
    if (*anim_out == NULL) {
        NEWS_LOG(1u, updating_fn, 0x618u, 0u, anim_fail, anim_fail_short);
        return -1;
    }
    generic_animation_start_463ea6(*anim_out);
    g2_news_update_animating_20074e8c = 1;
    g2_news_update_timeout_20074e90 = NEWS_STATUS_TICKS;
    g2_news_status_shown_20074e98 = 0;
    return 0;
}

static void news_post_dashboard_event(uint8_t event)
{
    uint8_t msg[5];
    audio_uart_buffer_zero(msg, sizeof msg, 0u);
    audio_uart_buffer_zero(msg, sizeof msg, 0u);
    msg[0] = event;
    if (audio_uart_device_role_get() == 1u) {
        (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, sizeof msg, 0u);
        NEWS_LOG(3u, reflash_fn, event == DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT ? 0x63fu : 0x64cu, 0u,
                 reflash_send, reflash_send_short);
    }
}

/* Periodic tick: advance the spinner and count down the update timeout
 * (event 0x0c) or the status-label resume delay (event 0x0e). */
int32_t NewsWidget_AutoReflash_4f2cec(void)
{
    if (g2_news_widget_state_20074e64 == 0) {
        NEWS_LOG(2u, reflash_fn, 0x62eu, 0u, ext_init_zero, ext_init_zero_short);
        return 0;
    }
    if (g2_news_loading_anim_20074e84 != NULL && g2_news_widget_state_20074e64 == 1) {
        if (g2_news_update_animating_20074e8c == 1)
            generic_animation_update_463f34(g2_news_loading_anim_20074e84);
        if (g2_news_update_timeout_20074e90 > 0 && g2_news_update_animating_20074e8c == 1) {
            g2_news_update_timeout_20074e90--;
            if (g2_news_update_timeout_20074e90 == 0)
                news_post_dashboard_event(DASHBOARD_NEWS_UPDATE_TIMEOUT_EVENT);
        }
    } else if (g2_news_widget_state_20074e64 == 1 && g2_news_status_shown_20074e98 == 1 &&
               g2_news_status_resume_20074e9c > 0) {
        g2_news_status_resume_20074e9c--;
        if (g2_news_status_resume_20074e9c == 0)
            news_post_dashboard_event(DASHBOARD_NEWS_SCROLL_LABEL_RESUME_EVENT);
    }
    return 0;
}

/* Status label timed out: show the refresh icon with "scroll to refresh". */
void NewsWidget_ScrollLableResume_Handler_4f2ec0(void)
{
    if (g2_news_widget_state_20074e64 == 1 && g2_news_status_shown_20074e98 == 1 &&
        g2_news_update_animating_20074e8c == 0) {
        NEWS_LOG(3u, resume_fn, 0x659u, 0u, resume_msg, resume_msg_short);
        if (audio_terminal_ui_object_valid_43e2ea(g2_news_end_item_20074e80) == 0u) {
            NEWS_LOG(1u, resume_fn, 0x65du, 0u, end_item_bad, end_item_bad_short);
            return;
        }
        audio_uart_page_44d878(g2_news_end_item_20074e80);
        void *box = audio_uart_page_43de82(g2_news_end_item_20074e80);
        audio_uart_page_43f4c0(box, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        audio_uart_page_44129e(box, 0u, 0u);
        audio_uart_page_44131c(box, 0, 0u);
        lv_obj_set_style_pad_all_4effa8(box, 0, 0u);
        audio_uart_page_48ba78(box, LV_FLEX_FLOW_ROW);
        audio_uart_page_48ba92(box, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
        audio_uart_page_441254(box, 8, 0u);
        audio_uart_page_43f6b8(box, LV_ALIGN_CENTER, 0, 0);

        void *icon = audio_uart_page_498668(box);
        audio_uart_page_498680(icon, news_refresh_icon_769d98);
        audio_uart_page_43f506(icon, 24);
        audio_uart_page_43f568(icon, 24);
        audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

        void *label = audio_uart_page_499416(box);
        (void)audio_uart_page_49942e(label, NEWS_TR(id_scroll_refresh));
        audio_uart_page_44143e(label, NEWS_FONT(), 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
    }
    g2_news_status_shown_20074e98 = 0;
    g2_news_status_resume_20074e9c = 0;
}

/* Update finished without new content: stop the spinner, restore the item
 * border and show the end-item status for 600 ticks. */
void NewsWidget_UpdateTimeout_Handler_4f3084(void)
{
    if (g2_news_loading_anim_20074e84 != NULL && g2_news_widget_state_20074e64 == 1 &&
        g2_news_update_animating_20074e8c == 1) {
        NEWS_LOG(3u, timeout_fn, 0x681u, 0u, timeout_msg, timeout_msg_short);
        generic_animation_destroy_463e1c(g2_news_loading_anim_20074e84, 1u);
        g2_news_loading_anim_20074e84 = NULL;
        g2_news_update_animating_20074e8c = 0;
        g2_news_update_timeout_20074e90 = 0;
        widget_news_show_item_border_4f0e18(g2_news_selected_index_20074e78);
        widget_news_end_item_show_error_4f2acc(g2_news_end_item_20074e80);
        g2_news_status_shown_20074e98 = 1;
        g2_news_status_resume_20074e9c = NEWS_STATUS_TICKS;
    }
}

void NewsWidget_NoSources_Handler_4f3128(void)
{
    if (g2_news_loading_anim_20074e84 != NULL && g2_news_widget_state_20074e64 == 1 &&
        g2_news_update_animating_20074e8c == 1) {
        NEWS_LOG(3u, no_sources_fn, 0x690u, 0u, timeout_msg, timeout_msg_short);
        generic_animation_destroy_463e1c(g2_news_loading_anim_20074e84, 1u);
        g2_news_loading_anim_20074e84 = NULL;
        g2_news_update_animating_20074e8c = 0;
        g2_news_update_timeout_20074e90 = 0;
        widget_news_show_item_border_4f0e18(g2_news_selected_index_20074e78);
        widget_news_end_item_show_no_updates_4f2b30(g2_news_end_item_20074e80);
        g2_news_status_shown_20074e98 = 1;
        g2_news_status_resume_20074e9c = NEWS_STATUS_TICKS;
    }
}

/* New news data: rebuild the expanded list and the dashboard tile. The
 * condition reduces to ext_init_flag == 1; it is kept as written in stock. */
void NewsWidget_LoadContent_Handler_4f31c8(void)
{
    if ((g2_news_widget_state_20074e64 == 1 && g2_news_update_animating_20074e8c == 1) ||
        (g2_news_widget_state_20074e64 == 1 && g2_news_expanded_20074e68 == 1) ||
        g2_news_widget_state_20074e64 == 1) {
        NEWS_LOG(3u, load_content_fn, 0x6a0u, 0u, load_content_msg, load_content_msg_short);
        if (audio_terminal_ui_object_valid_43e2ea(g2_dashboard_focus_frame) != 0u) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            (void)News_Widget_ext_init_4f4670(g2_dashboard_focus_frame);
        }
    }
    if (g2_dashboard_news_ready_20074e60 == 1)
        (void)News_Widget_init_Reflash_4efffc();
}

/* As LoadContent (stock logs the LoadContent message here too), then drop an
 * open detail page. */
void NewsWidget_ClearContent_Handler_4f326c(void)
{
    if ((g2_news_widget_state_20074e64 == 1 && g2_news_update_animating_20074e8c == 1) ||
        (g2_news_widget_state_20074e64 == 1 && g2_news_expanded_20074e68 == 1) ||
        g2_news_widget_state_20074e64 == 1) {
        NEWS_LOG(3u, clear_content_fn, 0x6afu, 0u, load_content_msg, load_content_msg_short);
        if (audio_terminal_ui_object_valid_43e2ea(g2_dashboard_focus_frame) != 0u) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            (void)News_Widget_ext_init_4f4670(g2_dashboard_focus_frame);
        }
    }
    if (g2_dashboard_news_ready_20074e60 == 1)
        (void)News_Widget_init_Reflash_4efffc();
    if (g2_news_widget_state_20074e64 == 1 && g2_news_expanded_20074e68 == 1) {
        NEWS_LOG(3u, clear_content_fn, 0x6bbu, 0u, clear_content_msg, clear_content_msg_short);
        if (audio_terminal_ui_object_valid_43e2ea(g2_news_expand_container_20074ea0) != 0u) {
            audio_uart_page_44d878(g2_news_expand_container_20074ea0);
            g2_news_expanded_20074e68 = 0;
            g2_news_anim_running_20074e88 = 0;
            g2_news_expanding_20074e94 = 0;
        }
    }
}

static void news_ext_scroll_down(const uint8_t *data, uint32_t value)
{
    NEWS_LOG(3u, ext_fn, 0x6dau, 0u, ext_down, ext_down_short);
    if (g2_news_widget_state_20074e64 != 1) {
        NEWS_LOG(2u, ext_fn, 0x6ddu, 0u, ext_not_init, ext_not_init_short);
        return;
    }
    if (g2_news_expanded_20074e68 == 0 ||
        (g2_news_anim_running_20074e88 == 1 && g2_news_expanding_20074e94 == 1)) {
        if (g2_news_scroll_container_20074e74 == NULL) {
            NEWS_LOG(2u, ext_fn, 0x6e5u, 0u, ext_no_container, ext_no_container_short);
        } else if (g2_news_anim_running_20074e88 == 1) {
            NEWS_LOG(4u, ext_fn, 0x6ebu, 0u, push_down, push_down_short);
            (void)ui_common_api_fn_00509ca2(g2_news_ext_fifo_20074e6c, data, NEWS_EVT_LEN);
        } else {
            int32_t scroll = audio_uart_lv_obj_y_44e498(g2_news_scroll_container_20074e74);
            NEWS_LOG(3u, ext_fn, 0x6f2u, 1u, cur_scroll, cur_scroll_short, scroll);
            if (g2_news_selected_index_20074e78 < g2_news_item_count_20074e7c - 1) {
                NEWS_LOG(4u, ext_fn, 0x6f6u, 1u, to_next, to_next_short, g2_news_selected_index_20074e78);
                widget_news_scroll_to_item_4f28f0(g2_news_selected_index_20074e78 + 1, 200u);
                (void)notifyAppNewsStatus_4fe1b4(NEWS_STATUS_ITEM, (uint32_t)g2_news_selected_index_20074e78);
            } else if (g2_news_end_item_20074e80 == NULL) {
                NEWS_LOG(4u, ext_fn, 0x72bu, 0u, no_end_item, no_end_item_short);
            } else {
                NEWS_LOG(3u, ext_fn, 0x6fdu, 0u, end_item_ok, end_item_ok_short);
                int32_t end_y = audio_uart_lv_obj_y_43fce0(g2_news_end_item_20074e80);
                if (scroll + 0xee < end_y) {
                    /* End item not yet visible: scroll it into the centre first. */
                    NEWS_LOG(4u, ext_fn, 0x704u, 2u, to_end, to_end_short, end_y, scroll);
                    widget_news_hide_item_border_4f0e94(g2_news_selected_index_20074e78);
                    int32_t h = audio_uart_lv_obj_height_43fdda(g2_news_end_item_20074e80);
                    g2_lv_anim_t a;
                    g2_news_anim_running_20074e88 = 1;
                    audio_uart_lv_anim_init_4503d6(&a);
                    a.var = g2_news_scroll_container_20074e74;
                    a.exec_cb = widget_news_scroll_anim_exec_cb_4f0f1c;
                    audio_uart_lv_anim_values_4506ce(&a, scroll, end_y - (NEWS_LIST_VIEW_H - h) / 2);
                    a.duration = 200;
                    a.path_cb = audio_uart_lv_anim_path_450688;
                    a.completed_cb = widget_news_scroll_anim_ready_no_border_cb_4f101c;
                    (void)audio_uart_lv_anim_start_450408(&a);
                } else {
                    /* Pulled past the end: request fresh news. */
                    NEWS_LOG(3u, ext_fn, 0x725u, 0u, hide_border, hide_border_short);
                    widget_news_hide_item_border_4f0e94(g2_news_selected_index_20074e78);
                    (void)Start_NewsUpdating_Animation_4f2bbc(g2_news_end_item_20074e80,
                                                             &g2_news_loading_anim_20074e84);
                    (void)requesetAppUpgradeNewsInfo_4fe0aa();
                }
            }
        }
    } else if (g2_news_expanded_20074e68 == 1) {
        NEWS_LOG(4u, ext_fn, 0x730u, 0u, detail_down, detail_down_short);
        widget_news_detail_scroll_by_4f2554(1, (int32_t)(value >> 16), (int32_t)(value & 0xffffu));
    }
}

static void news_ext_scroll_up(const uint8_t *data, uint32_t value)
{
    NEWS_LOG(3u, ext_fn, 0x737u, 0u, ext_up, ext_up_short);
    if (g2_news_widget_state_20074e64 != 1) {
        NEWS_LOG(2u, ext_fn, 0x73au, 0u, ext_not_init, ext_not_init_short);
        return;
    }
    if (g2_news_expanded_20074e68 == 0 ||
        (g2_news_anim_running_20074e88 == 1 && g2_news_expanding_20074e94 == 1)) {
        NEWS_LOG(3u, ext_fn, 0x740u, 0u, list_mode, list_mode_short);
        if (g2_news_scroll_container_20074e74 == NULL) {
            NEWS_LOG(2u, ext_fn, 0x743u, 0u, ext_no_container, ext_no_container_short);
        } else if (g2_news_anim_running_20074e88 == 1) {
            NEWS_LOG(4u, ext_fn, 0x749u, 0u, push_up, push_up_short);
            (void)ui_common_api_fn_00509ca2(g2_news_ext_fifo_20074e6c, data, NEWS_EVT_LEN);
        } else {
            int32_t scroll = audio_uart_lv_obj_y_44e498(g2_news_scroll_container_20074e74);
            int32_t last;
            if (g2_news_end_item_20074e80 != NULL && g2_news_item_count_20074e7c >= 1 &&
                scroll > (last = widget_news_calculate_scroll_pos_4f2804(g2_news_item_count_20074e7c - 1)) + 10) {
                NEWS_LOG(4u, ext_fn, 0x756u, 2u, in_end_area, in_end_area_short, scroll, last);
                widget_news_scroll_to_item_4f28f0(g2_news_item_count_20074e7c - 1, 200u);
            } else if (g2_news_selected_index_20074e78 >= 1) {
                NEWS_LOG(4u, ext_fn, 0x75eu, 1u, to_prev, to_prev_short, g2_news_selected_index_20074e78);
                widget_news_scroll_to_item_4f28f0(g2_news_selected_index_20074e78 - 1, 200u);
                (void)notifyAppNewsStatus_4fe1b4(NEWS_STATUS_ITEM, (uint32_t)g2_news_selected_index_20074e78);
            } else if (scroll < 0x15) {
                NEWS_LOG(4u, ext_fn, 0x76au, 1u, at_top, at_top_short, scroll);
                widget_news_bounce_at_top_4f11c0();
            } else {
                NEWS_LOG(4u, ext_fn, 0x765u, 1u, not_top, not_top_short, scroll);
                audio_uart_lv_scroll_to_y_44ea04(g2_news_scroll_container_20074e74, 0, LV_ANIM_ON);
            }
        }
    } else if (g2_news_expanded_20074e68 == 1) {
        NEWS_LOG(4u, ext_fn, 0x770u, 0u, detail_up, detail_up_short);
        widget_news_detail_scroll_by_4f2554(-1, (int32_t)(value >> 16), (int32_t)(value & 0xffffu));
    }
}

/* Events forwarded from the dashboard application to the expanded widget. */
int32_t news_widget_ext_event_handler_4f3440(const uint8_t *data, uint32_t len)
{
    if (g2_news_widget_state_20074e64 == 0) {
        NEWS_LOG(2u, ext_fn, 0x6c8u, 0u, ext_init_zero, ext_init_zero_short);
        return 0;
    }
    if (len == 0u) {
        NEWS_LOG(2u, ext_fn, 0x6cdu, 0u, len_zero, len_zero_short);
        return 0;
    }
    if (data[0] != 0u)
        return 0;

    uint8_t code = data[1];
    uint32_t value = (uint32_t)data[2] | ((uint32_t)data[3] << 8) | ((uint32_t)data[4] << 16) |
                     ((uint32_t)data[5] << 24);
    NEWS_LOG(3u, ext_fn, 0x6d6u, 2u, ext_code, ext_code_short, code, value);

    if (code == NEWS_EVT_CLICK) {
        if (g2_news_anim_running_20074e88 == 1 || g2_news_update_animating_20074e8c == 1) {
            NEWS_LOG(4u, ext_fn, 0x77au, 0u, click_busy, click_busy_short);
        } else if (g2_news_expanded_20074e68 == 0 && g2_news_widget_state_20074e64 == 1) {
            NEWS_LOG(3u, ext_fn, 0x780u, 0u, click_list, click_list_short);
            widget_news_start_expand_4f1544();
            ui_common_api_fn_00509f52(g2_news_ext_fifo_20074e6c);
            (void)notifyAppNewsStatus_4fe1b4(NEWS_STATUS_EXPAND, (uint32_t)g2_news_selected_index_20074e78);
        } else if (g2_news_expanded_20074e68 == 1 && g2_news_widget_state_20074e64 == 1) {
            NEWS_LOG(3u, ext_fn, 0x78bu, 0u, click_detail, click_detail_short);
        }
    } else if (code == NEWS_EVT_SCROLL_DOWN) {
        news_ext_scroll_down(data, value);
    } else if (code == NEWS_EVT_SCROLL_UP) {
        news_ext_scroll_up(data, value);
    } else if (code == NEWS_EVT_BACK) {
        if (g2_news_widget_state_20074e64 != 1) {
            NEWS_LOG(2u, ext_fn, 0x794u, 0u, ext_not_init, ext_not_init_short);
            return 0;
        }
        if (g2_news_expanded_20074e68 == 0) {
            /* Leave the expanded widget and return to the dashboard tile. */
            if (g2_news_ext_fifo_20074e6c != NULL) {
                ui_common_api_fn_00509c96(g2_news_ext_fifo_20074e6c);
                g2_news_ext_fifo_20074e6c = NULL;
            }
            for (int32_t i = audio_uart_lv_child_count_44ddea(g2_dashboard_focus_frame) - 1; i >= 0; i--) {
                void *child = audio_uart_lv_child_get_44dce2(g2_dashboard_focus_frame, i);
                if (child != NULL)
                    audio_uart_page_delete_event_filter_44d7b8(child);
            }
            g2_news_widget_state_20074e64 = 0;
            if (g2_dashboard_tiles[g2_news_tile_index_2000432c].frame != NULL)
                audio_uart_page_44d878(g2_dashboard_tiles[g2_news_tile_index_2000432c].frame);
            (void)News_Widget_init_Reflash_4efffc();
            dashboard_focus_frame_shrink_anim_4e92f4();
            page_state_sync_dashboard_main_5000cc(g2_news_tile_index_2000432c, 1u);
            (void)notifyAppNewsStatus_4fe1b4(NEWS_STATUS_EXIT, 0u);
        } else if (g2_news_expanded_20074e68 == 1) {
            NEWS_LOG(3u, ext_fn, 0x7b4u, 0u, collapse, collapse_short);
            ui_common_api_fn_00509f52(g2_news_ext_fifo_20074e6c);
            widget_news_start_collapse_4f18ac();
            (void)notifyAppNewsStatus_4fe1b4(NEWS_STATUS_COLLAPSE, (uint32_t)g2_news_selected_index_20074e78);
        }
    }
    return 0;
}

/* Input (display side): filter gestures while animations run, otherwise
 * forward them to the dashboard application as 6-byte widget events. */
int32_t NewsWidgetInputEventHandler_4f4030(uint32_t code, const void *event)
{
    uint8_t msg[NEWS_EVT_LEN];

    if (code == NEWS_EVT_CLICK || code == NEWS_EVT_BACK) {
        const uint32_t line = code == NEWS_EVT_CLICK ? 0x7d5u : 0x7eeu;
        if (g2_news_expanding_20074e94 == 1) {
            NEWS_LOG(4u, input_fn, line, 0u, in_switching, in_switching_short);
            return 0;
        }
        if (g2_news_expanded_20074e68 == 0 && g2_news_widget_state_20074e64 == 1 &&
            g2_news_update_animating_20074e8c == 1) {
            NEWS_LOG(3u, input_fn, line + 5u, 0u, in_updating, in_updating_short);
            return 0;
        }
        if ((g2_news_detail_scrolling_20074ec4 == 1 || g2_news_detail_20074ec0 == 1) &&
            g2_news_expanded_20074e68 == 1 && g2_news_widget_state_20074e64 == 1) {
            NEWS_LOG(4u, input_fn, line + 10u, 0u, in_detail_busy, in_detail_busy_short);
            return 0;
        }
        msg[0] = 0u;
        msg[1] = (uint8_t)code;
        msg[2] = 0u;
        msg[3] = 0u;
        msg[4] = 0u;
        msg[5] = 0u;
        return (int32_t)audio_uart_master_display_refresh(DASHBOARD_APP, msg, NEWS_EVT_LEN, 0u);
    }
    if (code == NEWS_EVT_IGNORED)
        return 0;
    if (code == NEWS_EVT_SCROLL_UP || code == NEWS_EVT_SCROLL_DOWN) {
        const uint32_t line = code == NEWS_EVT_SCROLL_UP ? 0x809u : 0x822u;
        if (g2_news_expanded_20074e68 == 0 && g2_news_widget_state_20074e64 == 1 &&
            g2_news_update_animating_20074e8c == 1) {
            NEWS_LOG(3u, input_fn, line, 0u, in_updating, in_updating_short);
            return 0;
        }
        if (g2_news_anim_running_20074e88 == 1 && g2_news_expanded_20074e68 == 0 &&
            g2_news_widget_state_20074e64 == 1) {
            NEWS_LOG(4u, input_fn, line + 4u, 0u, in_anim_updating, in_anim_updating_short);
            return 0;
        }
        if (g2_news_expanding_20074e94 == 1) {
            NEWS_LOG(4u, input_fn, line + 9u, 0u, in_animating, in_animating_short);
            return 0;
        }
        /* The input side names 0x45 "scroll down" (finger direction); the
         * ext handler names the same code SCROLLUP_EVENT. */
        if (code == NEWS_EVT_SCROLL_UP)
            NEWS_LOG(3u, input_fn, 0x815u, 0u, in_down, in_down_short);
        else
            NEWS_LOG(3u, input_fn, 0x82eu, 0u, in_up, in_up_short);
        /* event +0x10 -> int32_t[2] {distance, speed}, sent as two LE u16. */
        const int32_t *swipe = *(const int32_t *const *)(const void *)((const uint8_t *)event + 0x10u);
        msg[0] = 0u;
        msg[1] = (uint8_t)code;
        msg[2] = (uint8_t)swipe[0];
        msg[3] = (uint8_t)(swipe[0] >> 8);
        msg[4] = (uint8_t)swipe[1];
        msg[5] = (uint8_t)(swipe[1] >> 8);
        return (int32_t)audio_uart_master_display_refresh(DASHBOARD_APP, msg, NEWS_EVT_LEN, 0u);
    }
    return (int32_t)code;
}
