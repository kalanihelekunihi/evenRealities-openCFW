/* Dashboard news widget (tile list and expanded list page), first part, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_widget_news_page.c.
 * Native 0x4eff94..0x4f091b (style helpers, News_Widget_init_Reflash),
 * 0x4f091c..0x4f098f, 0x4f0998..0x4f0ca9, 0x4f0cc0..0x4f0dfb, 0x4f0e18..0x4f0e8b,
 * 0x4f0e94..0x4f0f07, 0x4f0f1c..0x4f100f, 0x4f101c..0x4f1271, 0x4f1280..0x4f1381,
 * 0x4f13a0..0x4f1539, 0x4f1544..0x4f1885, 0x4f18ac..0x4f19dd. Literal pools and
 * the per-function "AM"/"PM" literals sit in the gaps (0x4f0990, 0x4f0e8c,
 * 0x4f0f08.., 0x4f1274.., 0x4f1888.., 0x4f19e0..0x4f1ab7). The rest of the TU
 * (detail page 0x4f1ab8, list scrolling, ext event handler 0x4f3440) is
 * reconstructed separately.
 *
 * News cache (RAM 0x20132f74): five 0x1c98-byte records {valid u8, title[0x80],
 * content[0x1c0f], timestamp_ms u64 @0x1c90}. The tile widget is drawn into
 * tile_list[tile][1] of the dashboard tile table (RAM 0x200734bc). */
#include <stdint.h>
#include <stddef.h>

#define NEWS_RECORDS 5
#define NEWS_TILE_MAX 6

#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PART_MAIN 0u
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_TOP_MID 2u
#define LV_ALIGN_TOP_RIGHT 3u
#define LV_ALIGN_CENTER 9u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_LABEL_LONG_WRAP 0u
#define LV_LABEL_LONG_DOT 1u
#define LV_FLEX_FLOW_ROW 0u
#define LV_FLEX_ALIGN_CENTER 2u
#define LV_STYLE_PAD_TOP 16u
#define LV_STYLE_PAD_LEFT 18u
#define COLOR_BLACK 0x000000u
#define COLOR_WHITE 0xffffffu
#define WAIT_FOREVER 0xffffffffu

#define SCREEN_W 0x240
#define SCREEN_H 0x120
#define TILE_H_LIMIT 0xfa

typedef struct {
    uint8_t valid;          /* +0x0000 1 = record present */
    char title[0x80];       /* +0x0001 */
    char content[0x1c0f];   /* +0x0081 */
    uint64_t timestamp_ms;  /* +0x1c90 */
} g2_news_record_t;
_Static_assert(sizeof(g2_news_record_t) == 0x1c98u, "news record");

/* am_hal_rtc_time_t word layout as filled by service_time. */
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
    int32_t (*path_cb)(void *);         /* +0x20 */
    int32_t start_value;                /* +0x24 */
    int32_t current_value;              /* +0x28 */
    int32_t end_value;                  /* +0x2c */
    int32_t duration;                   /* +0x30 */
    int32_t act_time;                   /* +0x34 */
    uint32_t reverse_delay;             /* +0x38 */
    uint32_t reverse_duration;          /* +0x3c */
    uint8_t rest[0x20];                 /* +0x40 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* Minimal lv_font_t head: line_height at +0xc. */
typedef struct {
    void *get_glyph_dsc;    /* +0x0 */
    void *get_glyph_bitmap; /* +0x4 */
    void *release_glyph;    /* +0x8 */
    int32_t line_height;    /* +0xc */
} g2_lv_font_head_t;

extern uint8_t g2_dashboard_news_cache_20132f74[0x8ef8];  /* RAM 0x20132f74 */
extern void *g2_dashboard_mutex_200743a8;                 /* RAM 0x200743a8 osMutexId */
extern uint32_t audio_uart_ring_primary_head_cell;        /* RAM 0x200746dc: active lv_font_t * */
extern void *g2_dashboard_tiles[][2];        /* RAM 0x200734bc tile_list[tile][0..1] */
extern void *g2_dashboard_focus_frame;            /* RAM 0x20074b9c expanded-page parent */
extern int32_t g2_dashboard_news_ready_20074e60;         /* RAM 0x20074e60 */
extern int32_t g2_news_tile_index_2000432c;               /* RAM 0x2000432c (initialised data) */
extern int32_t g2_news_widget_state_20074e64;             /* RAM 0x20074e64 */
extern int32_t g2_news_item_count_20074e7c;               /* RAM 0x20074e7c */
extern void *g2_news_items_20073d9c[];                    /* RAM 0x20073d9c list item objects */
extern int32_t g2_news_selected_index_20074e78;           /* RAM 0x20074e78 */
extern int32_t g2_news_anim_running_20074e88;             /* RAM 0x20074e88 */
extern void *g2_news_ext_fifo_20074e6c;                   /* RAM 0x20074e6c */
extern void *g2_news_list_page_20074e70;                  /* RAM 0x20074e70 */
extern void *g2_news_scroll_container_20074e74;           /* RAM 0x20074e74 */
extern void *g2_news_expand_container_20074ea0;           /* RAM 0x20074ea0 */
extern int32_t g2_news_expanded_20074e68;                 /* RAM 0x20074e68 */
extern int32_t g2_news_expanding_20074e94;                /* RAM 0x20074e94 */
extern int32_t g2_news_expand_x_20074ec8;                 /* RAM 0x20074ec8 */
extern int32_t g2_news_expand_y_20074ecc;                 /* RAM 0x20074ecc */
extern int32_t g2_news_expand_w_20074ed0;                 /* RAM 0x20074ed0 */
extern int32_t g2_news_expand_h_20074ed4;                 /* RAM 0x20074ed4 */
extern int32_t g2_news_expand_index_20074ed8;             /* RAM 0x20074ed8 */
/* Detail page state filled by widget_news_load_detail_content (0x4f1ab8). */
extern uint32_t g2_news_detail_20074ea4;                  /* RAM 0x20074ea4 */
extern uint32_t g2_news_detail_20074ea8;                  /* RAM 0x20074ea8 */
extern uint32_t g2_news_detail_20074eac;                  /* RAM 0x20074eac */
extern uint32_t g2_news_detail_20074eb0;                  /* RAM 0x20074eb0 */
extern uint32_t g2_news_detail_20074eb4;                  /* RAM 0x20074eb4 */
extern uint32_t g2_news_detail_20074eb8;                  /* RAM 0x20074eb8 */
extern uint32_t g2_news_detail_20074ebc;                  /* RAM 0x20074ebc */
extern uint32_t g2_news_detail_20074ec0;                  /* RAM 0x20074ec0 */

extern const uint8_t news_icon_76e7c0[];     /* ROM 0x76e7c0 lv_image_dsc_t */
extern const uint8_t news_refresh_icon_769d98[]; /* ROM 0x769d98 lv_image_dsc_t */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);   /* memset 0x43c0e4 */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t, uint32_t, uint32_t, uint32_t); /* u64 / u64 */
extern void service_time_epoch_to_calendar(uint32_t epoch, g2_calendar_t *out); /* 0x44a100 */
extern void service_time_current_calendar_get(g2_calendar_t *out);              /* 0x44a19a */
extern uint8_t svc_universal_setting_get_date_format_466500(void);  /* 0/1 = month first */
extern uint32_t audio_time_format_mode_46650c(void);            /* 1 = 12-hour clock */
extern void *audio_uart_page_43de82(void *parent);              /* lv_obj_create */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);       /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag); /* lv_obj_remove_flag */
extern void audio_lv_object_position_43f09a(void *obj, int32_t x, int32_t y); /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);       /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);       /* lv_obj_set_y */
extern void audio_lv_object_size_call_43f4c0(void *obj, int32_t w, int32_t h); /* lv_obj_set_size */
extern void audio_lv_width_43f506(void *obj, int32_t w);        /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);       /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                  /* lv_obj_update_layout */
extern void lv_obj_align_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y);
extern int32_t audio_uart_lv_obj_x_43fc70(void *obj);           /* lv_obj_get_x */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);           /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);       /* lv_obj_get_width */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);      /* lv_obj_get_height */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);            /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);  /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);  /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);  /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);  /* style pad_right */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);  /* style pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t c, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel); /* style bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t c, uint32_t sel); /* style border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t v, uint32_t sel); /* style border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);  /* style border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);  /* style outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);  /* style outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);  /* style shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t sel);  /* style shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t sel);  /* style shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);  /* style shadow_spread */
extern void audio_lv_style_color_44140e(void *obj, uint32_t c, uint32_t sel); /* style text_color */
extern void audio_lv_style_alpha_44142e(void *obj, uint32_t v, uint32_t sel); /* style text_opa */
extern void audio_lv_style_font_44143e(void *obj, uint32_t font, uint32_t sel); /* style text_font */
extern void audio_lv_style_spacing_44144c(void *obj, int32_t v, uint32_t sel); /* style text_line_space */
extern void audio_lv_style_a_44145a(void *obj, uint32_t v, uint32_t sel); /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* style radius */
extern uint32_t audio_uart_lv_style_property_44bdea(void *obj, uint32_t part, uint32_t prop); /* lv_obj_get_style_prop */
extern void audio_lv_delete_44d7b8(void *obj);                  /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                  /* lv_obj_clean */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);           /* lv_obj_get_scroll_y */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *anim);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *anim);
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *anim, int32_t start, int32_t end);
extern int32_t audio_uart_lv_anim_path_450688(void *anim);      /* lv_anim_path_ease_in_out */
extern int32_t lv_pct_4515d2(int32_t percent);
extern uint32_t audio_uart_page_460084(const char *key);        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);   /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_lv_image_create_498668(void *parent);        /* lv_image_create */
extern void audio_lv_image_source_498680(void *img, const void *src); /* lv_image_set_src */
extern void *audio_lv_label_create_499416(void *parent);        /* lv_label_create */
extern void audio_lv_label_text_49942e(void *label, const char *text); /* lv_label_set_text */
extern void audio_lv_label_mode_499678(void *label, uint32_t mode); /* lv_label_set_long_mode */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);           /* 0 = events pending */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len); /* fifo get */
extern uint32_t audio_log_flags(void);                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Same TU, reconstructed separately. */
extern void widget_news_detail_load_content_4f1ab8(int32_t index);
extern int32_t news_widget_ext_event_handler_4f3440(const uint8_t *data, uint32_t len);

int32_t lv_obj_get_style_pad_top_4eff94(void *obj, uint32_t part);
int32_t lv_obj_get_style_pad_left_4eff9e(void *obj, uint32_t part);
void lv_obj_set_style_pad_all_4effa8(void *obj, int32_t value, uint32_t selector);
int32_t news_valid_count_4effda(void);
int32_t News_Widget_init_Reflash_4efffc(void);
int32_t Widget_News_init_4f091c(int32_t index);
void *widget_news_create_item_4f0998(void *parent, const g2_news_record_t *news, int32_t y);
void *widget_news_create_refresh_item_4f0cc0(void *parent, int32_t y);
void widget_news_show_item_border_4f0e18(int32_t index);
void widget_news_hide_item_border_4f0e94(int32_t index);
void widget_news_scroll_anim_exec_cb_4f0f1c(void *obj, int32_t y);
void widget_news_scroll_anim_ready_cb_4f0f26(void *anim);
void widget_news_scroll_anim_ready_no_border_cb_4f101c(void *anim);
void widget_news_bounce_ready_cb_4f10ee(void *anim);
void widget_news_bounce_at_top_4f11c0(void);
void widget_news_expand_anim_exec_cb_4f1280(void *obj, int32_t v);
void widget_news_expand_anim_ready_cb_4f12f6(void *anim);
void widget_news_collapse_anim_ready_cb_4f13a0(void *anim);
void widget_news_start_expand_4f1544(void);
void widget_news_start_collapse_4f18ac(void);

static const char module_tag[] = "dashborad.news.widget"; /* ROM 0x77d624 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_widget_news_page.c"; /* ROM 0x6eae4c */
static const char fn_reflash[] = "News_Widget_init_Reflash"; /* ROM 0x77442c */
static const char no_news[] = "No valid news data, create no available news label"; /* ROM 0x7307b4 */
static const char no_news_short[] =
    "[dashborad.news.widget]No valid news data, create no available news label"; /* ROM 0x6f787c */
static const char tile_null_label[] =
    "tile_list[%d][1] is NULL, cannot create label. This may happen if indicator_count is less than %d"; /* ROM 0x6dbe48 */
static const char tile_null_label_short[] =
    "[dashborad.news.widget]tile_list[%d][1] is NULL, cannot create label. This may happen if indicator_count is less than %d"; /* ROM 0x69d214 */
static const char label_failed[] = "Failed to create label"; /* ROM 0x77d63c */
static const char label_failed_short[] = "[dashborad.news.widget]Failed to create label"; /* ROM 0x73b1d4 */
static const char id_no_news_1[] = "ID_DASHBOARD_NEWS_NO_AVAILABLE_NEWS_1"; /* ROM 0x750f7c */
static const char id_no_news_2[] = "ID_DASHBOARD_NEWS_NO_AVAILABLE_NEWS_2"; /* ROM 0x750fa4 */
static const char tile_null_widgets[] =
    "tile_list[%d][1] is NULL, cannot create news widgets. This may happen if indicator_count is less than %d"; /* ROM 0x6d8104 */
static const char tile_null_widgets_short[] =
    "[dashborad.news.widget]tile_list[%d][1] is NULL, cannot create news widgets. This may happen if indicator_count is less than %d"; /* ROM 0x6d5d58 */
static const char fmt_date[] = "%02d/%02d"; /* ROM 0x78c8cc */
static const char fmt_time_12h[] = "%02d:%02d %s"; /* ROM 0x789eb0 */
static const char fmt_time_24h[] = "%02d:%02d"; /* ROM 0x78c8d8 */
static const char str_am[] = "AM"; /* ROM 0x4f0990 (copy at 0x4f0e8c) */
static const char str_pm[] = "PM"; /* ROM 0x4f0994 (copy at 0x4f0e90) */
static const char item_height[] = "item_height: %d"; /* ROM 0x789ec0 */
static const char item_height_short[] = "[dashborad.news.widget]item_height: %d"; /* ROM 0x750fcc */
static const char current_y[] = "current_y: %d"; /* ROM 0x789ed0 */
static const char current_y_short[] = "[dashborad.news.widget]current_y: %d"; /* ROM 0x750ff4 */
static const char fn_init[] = "Widget_News_init"; /* ROM 0x784af4 */
static const char bad_index[] = "NewsWidget_init: Invalid index %d, must be 0-5"; /* ROM 0x73b204 */
static const char bad_index_short[] = "[dashborad.news.widget]NewsWidget_init: Invalid index %d, must be 0-5"; /* ROM 0x6ff314 */
static const char id_scroll_refresh[] = "ID_DASHBOARD_NEWS_SCROLL_TO_REFRESH_NEWS"; /* ROM 0x7467f8 */
static const char fn_show_border[] = "widget_news_show_item_border"; /* ROM 0x767df0 */
static const char show_border[] = "Showing border for item %d"; /* ROM 0x774448 */
static const char show_border_short[] = "[dashborad.news.widget]Showing border for item %d"; /* ROM 0x7307e8 */
static const char fn_hide_border[] = "widget_news_hide_item_border"; /* ROM 0x767e10 */
static const char hide_border[] = "Hiding border for item %d"; /* ROM 0x774464 */
static const char hide_border_short[] = "[dashborad.news.widget]Hiding border for item %d"; /* ROM 0x73081c */
static const char fn_scroll_ready[] = "widget_news_scroll_anim_ready_cb"; /* ROM 0x75ce94 */
static const char scroll_ready[] = "Scroll animation completed, showing border for item %d"; /* ROM 0x725e98 */
static const char scroll_ready_short[] =
    "[dashborad.news.widget]Scroll animation completed, showing border for item %d"; /* ROM 0x6f0f88 */
static const char fifo_pending[] = "fifo is not empty,exec event"; /* ROM 0x767e30 */
static const char fifo_pending_short[] = "[dashborad.news.widget]fifo is not empty,exec event"; /* ROM 0x730850 */
static const char fn_scroll_ready_nb[] = "widget_news_scroll_anim_ready_no_border_cb"; /* ROM 0x746824 */
static const char scroll_ready_nb[] = "Scroll animation completed (no border)"; /* ROM 0x75101c */
static const char scroll_ready_nb_short[] =
    "[dashborad.news.widget]Scroll animation completed (no border)"; /* ROM 0x711824 */
static const char fn_bounce_ready[] = "widget_news_bounce_ready_cb"; /* ROM 0x774480 */
static const char bounce_ready[] = "Bounce animation completed"; /* ROM 0x77449c */
static const char bounce_ready_short[] = "[dashborad.news.widget]Bounce animation completed"; /* ROM 0x730884 */
static const char fn_bounce[] = "widget_news_bounce_at_top"; /* ROM 0x7744b8 */
static const char bounce[] = "Executing bounce effect at top"; /* ROM 0x767e50 */
static const char bounce_short[] = "[dashborad.news.widget]Executing bounce effect at top"; /* ROM 0x725ed0 */
static const char fn_expand_ready[] = "widget_news_expand_anim_ready_cb"; /* ROM 0x75ceb8 */
static const char expand_ready[] = "Expand animation completed"; /* ROM 0x7744d4 */
static const char expand_ready_short[] = "[dashborad.news.widget]Expand animation completed"; /* ROM 0x7308b8 */
static const char fn_collapse_ready[] = "widget_news_collapse_anim_ready_cb"; /* ROM 0x75cedc */
static const char collapse_ready[] = "Collapse animation completed"; /* ROM 0x767e70 */
static const char collapse_ready_short[] = "[dashborad.news.widget]Collapse animation completed"; /* ROM 0x7308ec */
static const char restored[] = "List page restored, selected index=%d"; /* ROM 0x751044 */
static const char restored_short[] = "[dashborad.news.widget]List page restored, selected index=%d"; /* ROM 0x711864 */
static const char fn_expand[] = "widget_news_start_expand"; /* ROM 0x7744f0 */
static const char expand_not_ready[] = "Cannot expand: scroll_container or items not ready"; /* ROM 0x730920 */
static const char expand_not_ready_short[] =
    "[dashborad.news.widget]Cannot expand: scroll_container or items not ready"; /* ROM 0x6f78c8 */
static const char expand_bad_index[] = "Cannot expand: invalid scroll index %d"; /* ROM 0x75106c */
static const char expand_bad_index_short[] =
    "[dashborad.news.widget]Cannot expand: invalid scroll index %d"; /* ROM 0x7118a4 */
static const char expand_null_item[] = "Cannot expand: selected item is NULL"; /* ROM 0x751094 */
static const char expand_null_item_short[] =
    "[dashborad.news.widget]Cannot expand: selected item is NULL"; /* ROM 0x71b178 */
static const char expand_from[] = "Expand from: x=%d, y=%d, w=%d, h=%d, item_index=%d"; /* ROM 0x730954 */
static const char expand_from_short[] =
    "[dashborad.news.widget]Expand from: x=%d, y=%d, w=%d, h=%d, item_index=%d"; /* ROM 0x6f7914 */
static const char expand_create_failed[] = "Failed to create expand container"; /* ROM 0x75cf00 */
static const char expand_create_failed_short[] =
    "[dashborad.news.widget]Failed to create expand container"; /* ROM 0x71b1b4 */
static const char fn_collapse[] = "widget_news_start_collapse"; /* ROM 0x77450c */
static const char collapse_null[] = "Cannot collapse: expand container is NULL"; /* ROM 0x746850 */
static const char collapse_null_short[] =
    "[dashborad.news.widget]Cannot collapse: expand container is NULL"; /* ROM 0x7083d8 */
static const char collapse_to[] = "Collapse to: x=%d, y=%d, w=%d, h=%d"; /* ROM 0x75cf24 */
static const char collapse_to_short[] = "[dashborad.news.widget]Collapse to: x=%d, y=%d, w=%d, h=%d"; /* ROM 0x71b1f0 */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. */
#define NEWS_LOG(level, fn, line, cflags, msg, msg_short, ...)                                      \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

#define NEWS ((const g2_news_record_t *)(const void *)g2_dashboard_news_cache_20132f74)
#define FONT() (audio_uart_ring_primary_head_cell)
#define FONT_LINE_HEIGHT() (((const g2_lv_font_head_t *)(uintptr_t)audio_uart_ring_primary_head_cell)->line_height)

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* IAR out-of-line copies of the lv_obj_style.h inlines used in this TU. */
int32_t lv_obj_get_style_pad_top_4eff94(void *obj, uint32_t part)
{
    return (int32_t)audio_uart_lv_style_property_44bdea(obj, part, LV_STYLE_PAD_TOP);
}

int32_t lv_obj_get_style_pad_left_4eff9e(void *obj, uint32_t part)
{
    return (int32_t)audio_uart_lv_style_property_44bdea(obj, part, LV_STYLE_PAD_LEFT);
}

void lv_obj_set_style_pad_all_4effa8(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* Caller holds the dashboard mutex. */
int32_t news_valid_count_4effda(void)
{
    int32_t count = 0;
    for (int32_t i = 0; i < NEWS_RECORDS; i++) {
        if (NEWS[i].valid == 1u)
            count++;
    }
    return count;
}

/* "MM/DD" (or "DD/MM") for news older than today, else "hh:mm" / "hh:mm AM". */
static void format_news_time(char *buf, const g2_news_record_t *news)
{
    g2_calendar_t when;
    g2_calendar_t now;
    audio_uart_buffer_zero(buf, 0x20u, 0u);
    uint32_t epoch = (uint32_t)audio_uart_ring_u64_div_47cc60((uint32_t)news->timestamp_ms,
                                                              (uint32_t)(news->timestamp_ms >> 32), 1000u, 0u);
    service_time_epoch_to_calendar(epoch, &when);
    service_time_current_calendar_get(&now);
    if (when.year < now.year || (now.year == when.year && when.month < now.month) ||
        (now.year == when.year && now.month == when.month && when.day < now.day)) {
        if (svc_universal_setting_get_date_format_466500() == 0u || svc_universal_setting_get_date_format_466500() == 1u)
            (void)g2_audio_dump_snprintf(buf, 0x20u, fmt_date, when.month, when.day);
        else
            (void)g2_audio_dump_snprintf(buf, 0x20u, fmt_date, when.day, when.month);
    } else if (audio_time_format_mode_46650c() == 1u) {
        uint32_t hour = when.hour % 12u;
        if (hour == 0u)
            hour = 12u;
        (void)g2_audio_dump_snprintf(buf, 0x20u, fmt_time_12h, hour, when.minute,
                                     when.hour < 12u ? str_am : str_pm);
    } else {
        (void)g2_audio_dump_snprintf(buf, 0x20u, fmt_time_24h, when.hour, when.minute);
    }
}

static void *news_icon(void *parent, int32_t x, int32_t y)
{
    void *icon = audio_lv_image_create_498668(parent);
    audio_lv_image_source_498680(icon, news_icon_76e7c0);
    audio_lv_width_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_uart_page_43f0e0(icon, x);
    audio_uart_page_43f142(icon, y);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
    return icon;
}

/* Time label right-aligned on the item row; returns its laid-out width. */
static int32_t time_label(void *item, const char *text)
{
    void *label = audio_lv_label_create_499416(item);
    audio_lv_width_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, 0x1c);
    audio_uart_page_43f142(label, 0);
    lv_obj_align_43f6b8(label, LV_ALIGN_TOP_RIGHT, 0, 0);
    audio_lv_label_text_49942e(label, text);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    audio_uart_page_43f66c(label);
    return audio_uart_lv_obj_width_43fd9e(label);
}

static void title_label(void *item, int32_t width, const char *text)
{
    void *label = audio_lv_label_create_499416(item);
    audio_lv_width_43f506(label, width);
    audio_uart_page_43f568(label, 0x1c);
    audio_uart_page_43f0e0(label, 0x20);
    audio_uart_page_43f142(label, 0);
    audio_lv_label_mode_499678(label, LV_LABEL_LONG_DOT);
    audio_lv_label_text_49942e(label, text);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
}

static void *content_label(void *item, int32_t width, const char *text)
{
    void *label = audio_lv_label_create_499416(item);
    audio_lv_width_43f506(label, width);
    audio_uart_page_43f0e0(label, 0);
    audio_uart_page_43f142(label, 0x20);
    audio_lv_label_text_49942e(label, text);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    audio_lv_style_spacing_44144c(label, 0x1c - FONT_LINE_HEIGHT(), LV_PART_MAIN);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    return label;
}

/* Transparent 315x256 container at (20,16) on the tile with every box style
 * cleared. */
static void *tile_container(void *tile)
{
    void *box = audio_uart_page_43de82(tile);
    audio_lv_object_position_43f09a(box, 0x14, 0x10);
    audio_lv_width_43f506(box, 0x13b);
    audio_uart_page_43f568(box, 0x100);
    audio_uart_page_44127e(box, audio_lv_color_44104c(COLOR_BLACK), LV_PART_MAIN);
    audio_uart_page_44129e(box, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(box, 0, LV_PART_MAIN);
    audio_uart_page_44133a(box, 0, LV_PART_MAIN);
    audio_uart_page_441378(box, 0, LV_PART_MAIN);
    audio_uart_page_441386(box, 0, LV_PART_MAIN);
    audio_uart_page_4413b0(box, 0, LV_PART_MAIN);
    audio_uart_page_441394(box, 0, LV_PART_MAIN);
    audio_uart_page_4413a2(box, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_4effa8(box, 0, LV_PART_MAIN);
    audio_uart_page_44120e(box, 0, LV_PART_MAIN);
    audio_uart_page_44121c(box, 0, LV_PART_MAIN);
    audio_uart_page_44122a(box, 0, LV_PART_MAIN);
    audio_uart_page_441238(box, 0, LV_PART_MAIN);
    audio_uart_page_44146a(box, 0, LV_PART_MAIN);
    audio_uart_page_4412ec(box, audio_lv_color_44104c(COLOR_BLACK), LV_PART_MAIN);
    audio_lv_style_color_44140e(box, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_alpha_44142e(box, 0xffu, LV_PART_MAIN);
    return box;
}

/* Centred flex row {icon, gap 8} used by the placeholder items. */
static void *icon_row(void *parent)
{
    void *row = audio_uart_page_43de82(parent);
    audio_lv_object_size_call_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(row, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_4effa8(row, 0, LV_PART_MAIN);
    audio_uart_page_48ba78(row, LV_FLEX_FLOW_ROW);
    audio_uart_page_48ba92(row, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    audio_uart_page_441254(row, 8, LV_PART_MAIN);
    return row;
}

static void icon_row_image(void *row, const void *src)
{
    void *icon = audio_lv_image_create_498668(row);
    audio_lv_image_source_498680(icon, src);
    audio_lv_width_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
}

/* Draws the news tile: the valid news stacked top-down until 250 px are used,
 * or a "no available news" placeholder. Returns 0, -1 on a missing tile or
 * label; the populated path returns osMutexRelease's status (no explicit
 * return in stock). */
int32_t News_Widget_init_Reflash_4efffc(void)
{
    if (g2_dashboard_news_ready_20074e60 == 0 || g2_news_tile_index_2000432c < 0)
        return 0;
    if (g2_dashboard_tiles[g2_news_tile_index_2000432c][1] != NULL)
        audio_uart_page_44d878(g2_dashboard_tiles[g2_news_tile_index_2000432c][1]);

    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    int32_t valid = news_valid_count_4effda();
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);

    if (valid == 0) {
        NEWS_LOG(4u, fn_reflash, 0xb5u, 0x10000000u, no_news, no_news_short);
        if (g2_dashboard_tiles[g2_news_tile_index_2000432c][1] == NULL) {
            NEWS_LOG(1u, fn_reflash, 0xb9u, 0x04800000u, tile_null_label, tile_null_label_short,
                     g2_news_tile_index_2000432c, g2_news_tile_index_2000432c + 1);
            return -1;
        }
        void *box = tile_container(g2_dashboard_tiles[g2_news_tile_index_2000432c][1]);
        void *row = icon_row(box);
        lv_obj_align_43f6b8(row, LV_ALIGN_TOP_MID, 0, 100);
        icon_row_image(row, news_icon_76e7c0);
        void *label = audio_lv_label_create_499416(row);
        if (label == NULL) {
            NEWS_LOG(1u, fn_reflash, 0xeau, 0x04000000u, label_failed, label_failed_short);
            return -1;
        }
        audio_lv_label_text_49942e(label, localized(id_no_news_1));
        audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
        audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
        label = audio_lv_label_create_499416(box);
        if (label == NULL) {
            NEWS_LOG(1u, fn_reflash, 0xf3u, 0x04000000u, label_failed, label_failed_short);
            return -1;
        }
        audio_lv_label_text_49942e(label, localized(id_no_news_2));
        audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
        audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
        audio_lv_style_a_44145a(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
        lv_obj_align_43f6b8(label, LV_ALIGN_TOP_MID, 0, 0x82);
        return 0;
    }

    if (g2_dashboard_tiles[g2_news_tile_index_2000432c][1] == NULL) {
        NEWS_LOG(1u, fn_reflash, 0x101u, 0x04800000u, tile_null_widgets, tile_null_widgets_short,
                 g2_news_tile_index_2000432c, g2_news_tile_index_2000432c + 1);
        return -1;
    }
    void *box = tile_container(g2_dashboard_tiles[g2_news_tile_index_2000432c][1]);
    audio_lv_object_clear_flag_43dfa4(box, LV_OBJ_FLAG_SCROLLABLE);

    int32_t y = 0;
    int32_t shown = 0;
    char text[0x20];
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    for (int32_t i = 0; i < NEWS_RECORDS; i++) {
        if (NEWS[i].valid != 1u)
            continue;
        void *item = audio_uart_page_43de82(box);
        audio_lv_width_43f506(item, 0x13b);
        audio_uart_page_43f568(item, LV_SIZE_CONTENT);
        audio_uart_page_43f0e0(item, 0);
        audio_uart_page_43f142(item, y);
        audio_uart_page_44129e(item, 0u, LV_PART_MAIN);
        audio_uart_page_44131c(item, 0, LV_PART_MAIN);
        lv_obj_set_style_pad_all_4effa8(item, 0, LV_PART_MAIN);
        audio_uart_page_44146a(item, 0, LV_PART_MAIN);
        audio_lv_object_clear_flag_43dfa4(item, LV_OBJ_FLAG_SCROLLABLE);
        (void)news_icon(item, 0, 2);
        format_news_time(text, &NEWS[i]);
        int32_t time_w = time_label(item, text);
        title_label(item, 0x10f - time_w, NEWS[i].title);
        if (y + 0x20 < TILE_H_LIMIT) {
            void *body = content_label(item, 0x13b, NEWS[i].content);
            audio_uart_page_43f66c(body);
            if (audio_uart_lv_obj_height_43fdda(body) < 0x55) {
                audio_uart_page_43f568(body, LV_SIZE_CONTENT);
                audio_lv_label_mode_499678(body, LV_LABEL_LONG_WRAP);
            } else {
                audio_uart_page_43f568(body, 0x54);
                audio_lv_label_mode_499678(body, LV_LABEL_LONG_DOT);
            }
        }
        audio_uart_page_43f66c(item);
        int32_t h = audio_uart_lv_obj_height_43fdda(item);
        NEWS_LOG(3u, fn_reflash, 0x199u, 0x0c400000u, item_height, item_height_short, h);
        y = h + y + 0x19;
        NEWS_LOG(3u, fn_reflash, 0x19du, 0x0c400000u, current_y, current_y_short, y);
        shown++;
        if (y > TILE_H_LIMIT)
            break;
    }
    (void)shown;
    return osMutexRelease(g2_dashboard_mutex_200743a8);
}

int32_t Widget_News_init_4f091c(int32_t index)
{
    g2_news_tile_index_2000432c = index;
    g2_dashboard_news_ready_20074e60 = 1;
    if ((uint32_t)g2_news_tile_index_2000432c < NEWS_TILE_MAX) {
        (void)News_Widget_init_Reflash_4efffc();
        g2_news_widget_state_20074e64 = 0;
        return 0;
    }
    NEWS_LOG(1u, fn_init, 0x1b0u, 0x04400000u, bad_index, bad_index_short, g2_news_tile_index_2000432c);
    return -1;
}

/* One rounded list item on the expanded page (white 2 px border, hidden until
 * selected via border_opa). */
void *widget_news_create_item_4f0998(void *parent, const g2_news_record_t *news, int32_t y)
{
    char text[0x20];
    if (parent == NULL || news == NULL)
        return NULL;
    void *item = audio_uart_page_43de82(parent);
    audio_lv_width_43f506(item, lv_pct_4515d2(100));
    audio_uart_page_43f568(item, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(item, 0);
    audio_uart_page_43f142(item, y);
    audio_uart_page_44129e(item, 0u, LV_PART_MAIN);
    audio_uart_page_44120e(item, 6, LV_PART_MAIN);
    audio_uart_page_44121c(item, 6, LV_PART_MAIN);
    audio_uart_page_44122a(item, 0xc, LV_PART_MAIN);
    audio_uart_page_441238(item, 0xc, LV_PART_MAIN);
    audio_uart_page_44146a(item, 6, LV_PART_MAIN);
    audio_uart_page_44131c(item, 2, LV_PART_MAIN);
    audio_uart_page_4412ec(item, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_uart_page_44130c(item, 0u, LV_PART_MAIN);
    audio_lv_object_clear_flag_43dfa4(item, LV_OBJ_FLAG_SCROLLABLE);
    (void)news_icon(item, 0, 2);
    format_news_time(text, news);
    int32_t time_w = time_label(item, text);
    title_label(item, 0x1fe - time_w, news->title);
    void *body = content_label(item, 0x216, news->content);
    audio_lv_label_mode_499678(body, LV_LABEL_LONG_WRAP);
    audio_uart_page_43f66c(item);
    return item;
}

/* "Scroll to refresh" footer item: icon + localized hint centred in 80 px. */
void *widget_news_create_refresh_item_4f0cc0(void *parent, int32_t y)
{
    if (parent == NULL)
        return NULL;
    void *item = audio_uart_page_43de82(parent);
    audio_lv_width_43f506(item, lv_pct_4515d2(100));
    audio_uart_page_43f568(item, 0x50);
    audio_uart_page_43f0e0(item, 0);
    audio_uart_page_43f142(item, y);
    audio_uart_page_44129e(item, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(item, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_4effa8(item, 0, LV_PART_MAIN);
    audio_uart_page_44146a(item, 6, LV_PART_MAIN);
    audio_lv_object_clear_flag_43dfa4(item, LV_OBJ_FLAG_SCROLLABLE);
    void *row = icon_row(item);
    lv_obj_align_43f6b8(row, LV_ALIGN_CENTER, 0, 0);
    icon_row_image(row, news_refresh_icon_769d98);
    void *label = audio_lv_label_create_499416(row);
    audio_lv_label_text_49942e(label, localized(id_scroll_refresh));
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    return item;
}

void widget_news_show_item_border_4f0e18(int32_t index)
{
    if (index >= 0 && index < g2_news_item_count_20074e7c && g2_news_items_20073d9c[index] != NULL) {
        audio_uart_page_44130c(g2_news_items_20073d9c[index], 0xffu, LV_PART_MAIN);
        NEWS_LOG(4u, fn_show_border, 0x276u, 0x10400000u, show_border, show_border_short, index);
    }
}

void widget_news_hide_item_border_4f0e94(int32_t index)
{
    if (index >= 0 && index < g2_news_item_count_20074e7c && g2_news_items_20073d9c[index] != NULL) {
        audio_uart_page_44130c(g2_news_items_20073d9c[index], 0u, LV_PART_MAIN);
        NEWS_LOG(4u, fn_hide_border, 0x281u, 0x10400000u, hide_border, hide_border_short, index);
    }
}

void widget_news_scroll_anim_exec_cb_4f0f1c(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

/* Replays one queued 6-byte input event deferred while an animation ran. */
static void replay_pending_event(const char *fn, uint32_t line)
{
    uint8_t event[10];
    if (g2_news_ext_fifo_20074e6c == NULL || ui_common_api_fn_00509dfa(g2_news_ext_fifo_20074e6c) != 0)
        return;
    NEWS_LOG(4u, fn, line, 0x10000000u, fifo_pending, fifo_pending_short);
    audio_uart_buffer_zero(event, sizeof event, 0u);
    audio_uart_buffer_zero(event, sizeof event, 0u);
    (void)ui_common_api_fn_00509e14(g2_news_ext_fifo_20074e6c, event, 6u);
    (void)news_widget_ext_event_handler_4f3440(event, 6u);
}

void widget_news_scroll_anim_ready_cb_4f0f26(void *anim)
{
    (void)anim;
    NEWS_LOG(4u, fn_scroll_ready, 0x294u, 0x10400000u, scroll_ready, scroll_ready_short,
             g2_news_selected_index_20074e78);
    widget_news_show_item_border_4f0e18(g2_news_selected_index_20074e78);
    g2_news_anim_running_20074e88 = 0;
    replay_pending_event(fn_scroll_ready, 0x298u);
}

void widget_news_scroll_anim_ready_no_border_cb_4f101c(void *anim)
{
    (void)anim;
    NEWS_LOG(4u, fn_scroll_ready_nb, 0x2a5u, 0x10000000u, scroll_ready_nb, scroll_ready_nb_short);
    g2_news_anim_running_20074e88 = 0;
    replay_pending_event(fn_scroll_ready_nb, 0x2a8u);
}

void widget_news_bounce_ready_cb_4f10ee(void *anim)
{
    (void)anim;
    NEWS_LOG(4u, fn_bounce_ready, 0x2b5u, 0x10000000u, bounce_ready, bounce_ready_short);
    g2_news_anim_running_20074e88 = 0;
    replay_pending_event(fn_bounce_ready, 0x2b8u);
}

/* Nudges the list 32 px down and back (200 ms each way) at the top edge. */
void widget_news_bounce_at_top_4f11c0(void)
{
    g2_lv_anim_t a;
    if (g2_news_scroll_container_20074e74 == NULL)
        return;
    NEWS_LOG(4u, fn_bounce, 0x2c8u, 0x10000000u, bounce, bounce_short);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_scroll_container_20074e74;
    a.exec_cb = audio_uart_page_43f142; /* lv_obj_set_y */
    audio_uart_lv_anim_values_4506ce(&a, 0, 0x20);
    a.duration = 200;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.reverse_duration = 200u;
    a.reverse_delay = 0u;
    a.completed_cb = widget_news_bounce_ready_cb_4f10ee;
    g2_news_anim_running_20074e88 = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* v runs 0..1000: the box moves from the item origin to (0,0) and grows to
 * full screen (576x288). */
void widget_news_expand_anim_exec_cb_4f1280(void *obj, int32_t v)
{
    if (obj == NULL)
        return;
    int32_t x0 = g2_news_expand_x_20074ec8;
    int32_t y0 = g2_news_expand_y_20074ecc;
    int32_t w0 = g2_news_expand_w_20074ed0;
    int32_t h0 = g2_news_expand_h_20074ed4;
    audio_lv_object_position_43f09a(obj, (v * g2_news_expand_x_20074ec8) / -1000 + x0,
                                    (v * g2_news_expand_y_20074ecc) / -1000 + y0);
    audio_lv_object_size_call_43f4c0(obj, (v * (SCREEN_W - g2_news_expand_w_20074ed0)) / 1000 + w0,
                                     (v * (SCREEN_H - g2_news_expand_h_20074ed4)) / 1000 + h0);
}

void widget_news_expand_anim_ready_cb_4f12f6(void *anim)
{
    (void)anim;
    NEWS_LOG(3u, fn_expand_ready, 0x312u, 0x0c000000u, expand_ready, expand_ready_short);
    if (g2_news_expand_container_20074ea0 != NULL) {
        audio_lv_object_position_43f09a(g2_news_expand_container_20074ea0, 0, 0);
        audio_lv_object_size_call_43f4c0(g2_news_expand_container_20074ea0, SCREEN_W, SCREEN_H);
    }
    g2_news_expanded_20074e68 = 1;
    g2_news_expanding_20074e94 = 0;
    g2_news_anim_running_20074e88 = 0;
    widget_news_detail_load_content_4f1ab8(g2_news_expand_index_20074ed8);
}

void widget_news_collapse_anim_ready_cb_4f13a0(void *anim)
{
    (void)anim;
    NEWS_LOG(3u, fn_collapse_ready, 0x326u, 0x0c000000u, collapse_ready, collapse_ready_short);
    if (g2_news_expand_container_20074ea0 != NULL) {
        audio_lv_delete_44d7b8(g2_news_expand_container_20074ea0);
        g2_news_expand_container_20074ea0 = NULL;
    }
    g2_news_detail_20074ea4 = 0u;
    g2_news_detail_20074ea8 = 0u;
    g2_news_detail_20074eac = 0u;
    g2_news_detail_20074eb0 = 0u;
    g2_news_detail_20074eb4 = 0u;
    g2_news_detail_20074eb8 = 0u;
    g2_news_detail_20074ebc = 0u;
    g2_news_detail_20074ec0 = 0u;
    if (g2_news_scroll_container_20074e74 != NULL)
        audio_lv_object_clear_flag_43dfa4(g2_news_scroll_container_20074e74, LV_OBJ_FLAG_HIDDEN);
    g2_news_expanded_20074e68 = 0;
    g2_news_anim_running_20074e88 = 0;
    g2_news_expanding_20074e94 = 0;
    NEWS_LOG(3u, fn_collapse_ready, 0x33fu, 0x0c400000u, restored, restored_short,
             g2_news_selected_index_20074e78);
    replay_pending_event(fn_collapse_ready, 0x342u);
}

/* Hides the list and grows a bordered box from the selected item's screen
 * rectangle to full screen over 300 ms (exec 0x4f1280, ready 0x4f12f6). */
void widget_news_start_expand_4f1544(void)
{
    g2_lv_anim_t a;
    if (g2_news_scroll_container_20074e74 == NULL || g2_news_item_count_20074e7c == 0) {
        NEWS_LOG(2u, fn_expand, 0x34fu, 0x08000000u, expand_not_ready, expand_not_ready_short);
        return;
    }
    if (g2_news_selected_index_20074e78 < 0 || g2_news_selected_index_20074e78 >= g2_news_item_count_20074e7c) {
        NEWS_LOG(2u, fn_expand, 0x353u, 0x08400000u, expand_bad_index, expand_bad_index_short,
                 g2_news_selected_index_20074e78);
        return;
    }
    void *item = g2_news_items_20073d9c[g2_news_selected_index_20074e78];
    if (item == NULL) {
        NEWS_LOG(2u, fn_expand, 0x359u, 0x08000000u, expand_null_item, expand_null_item_short);
        return;
    }
    int32_t scroll_y = audio_uart_lv_obj_y_44e498(g2_news_scroll_container_20074e74);
    int32_t item_y = audio_uart_lv_obj_y_43fce0(item);
    int32_t item_x = audio_uart_lv_obj_x_43fc70(item);
    int32_t list_x = audio_uart_lv_obj_x_43fc70(g2_news_scroll_container_20074e74);
    int32_t list_y = audio_uart_lv_obj_y_43fce0(g2_news_scroll_container_20074e74);
    int32_t page_x = audio_uart_lv_obj_x_43fc70(g2_news_list_page_20074e70);
    int32_t page_y = audio_uart_lv_obj_y_43fce0(g2_news_list_page_20074e70);
    int32_t pad_left = lv_obj_get_style_pad_left_4eff9e(g2_news_scroll_container_20074e74, LV_PART_MAIN);
    int32_t pad_top = lv_obj_get_style_pad_top_4eff94(g2_news_scroll_container_20074e74, LV_PART_MAIN);
    g2_news_expand_x_20074ec8 = item_x + pad_left + list_x + page_x;
    g2_news_expand_y_20074ecc = item_y + pad_top + list_y + page_y - scroll_y;
    g2_news_expand_w_20074ed0 = audio_uart_lv_obj_width_43fd9e(item);
    g2_news_expand_h_20074ed4 = audio_uart_lv_obj_height_43fdda(item);
    g2_news_expand_index_20074ed8 = g2_news_selected_index_20074e78;
    NEWS_LOG(3u, fn_expand, 0x377u, 0x0d400000u, expand_from, expand_from_short, g2_news_expand_x_20074ec8,
             g2_news_expand_y_20074ecc, g2_news_expand_w_20074ed0, g2_news_expand_h_20074ed4,
             g2_news_expand_index_20074ed8);
    if (g2_news_scroll_container_20074e74 != NULL)
        audio_lv_object_flag_43ded4(g2_news_scroll_container_20074e74, LV_OBJ_FLAG_HIDDEN);

    g2_news_expand_container_20074ea0 = audio_uart_page_43de82(g2_dashboard_focus_frame);
    if (g2_news_expand_container_20074ea0 == NULL) {
        NEWS_LOG(1u, fn_expand, 0x381u, 0x04000000u, expand_create_failed, expand_create_failed_short);
        if (g2_news_scroll_container_20074e74 != NULL)
            audio_lv_object_clear_flag_43dfa4(g2_news_scroll_container_20074e74, LV_OBJ_FLAG_HIDDEN);
        return;
    }
    audio_lv_object_position_43f09a(g2_news_expand_container_20074ea0, g2_news_expand_x_20074ec8,
                                    g2_news_expand_y_20074ecc);
    audio_lv_object_size_call_43f4c0(g2_news_expand_container_20074ea0, g2_news_expand_w_20074ed0,
                                     g2_news_expand_h_20074ed4);
    audio_uart_page_44129e(g2_news_expand_container_20074ea0, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(g2_news_expand_container_20074ea0, 2, LV_PART_MAIN);
    audio_uart_page_4412ec(g2_news_expand_container_20074ea0, audio_lv_color_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_uart_page_44146a(g2_news_expand_container_20074ea0, 6, LV_PART_MAIN);
    lv_obj_set_style_pad_all_4effa8(g2_news_expand_container_20074ea0, 0, LV_PART_MAIN);
    audio_lv_object_clear_flag_43dfa4(g2_news_expand_container_20074ea0, LV_OBJ_FLAG_SCROLLABLE);
    g2_news_anim_running_20074e88 = 1;
    g2_news_expanding_20074e94 = 1;
    g2_news_detail_20074ec0 = 0u;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_expand_container_20074ea0;
    a.exec_cb = widget_news_expand_anim_exec_cb_4f1280;
    audio_uart_lv_anim_values_4506ce(&a, 0, 1000);
    a.duration = 300;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = widget_news_expand_anim_ready_cb_4f12f6;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Clears the detail page and shrinks the box back onto the list item. */
void widget_news_start_collapse_4f18ac(void)
{
    g2_lv_anim_t a;
    if (g2_news_expand_container_20074ea0 == NULL) {
        NEWS_LOG(2u, fn_collapse, 0x3aau, 0x08000000u, collapse_null, collapse_null_short);
        return;
    }
    NEWS_LOG(3u, fn_collapse, 0x3afu, 0x0d000000u, collapse_to, collapse_to_short, g2_news_expand_x_20074ec8,
             g2_news_expand_y_20074ecc, g2_news_expand_w_20074ed0, g2_news_expand_h_20074ed4);
    audio_uart_page_44d878(g2_news_expand_container_20074ea0);
    g2_news_detail_20074ea4 = 0u;
    g2_news_detail_20074ea8 = 0u;
    g2_news_detail_20074eac = 0u;
    g2_news_anim_running_20074e88 = 1;
    g2_news_expanding_20074e94 = 1;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_news_expand_container_20074ea0;
    a.exec_cb = widget_news_expand_anim_exec_cb_4f1280;
    audio_uart_lv_anim_values_4506ce(&a, 1000, 0);
    a.duration = 300;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = widget_news_collapse_anim_ready_cb_4f13a0;
    (void)audio_uart_lv_anim_start_450408(&a);
}
