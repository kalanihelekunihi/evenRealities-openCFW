/* Onboarding news page, first half of the TU, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_news_page.c
 * (log tag "onboarding.news"). Native 0x50a07e..0x50a08f, 0x50a094..0x50aaef,
 * 0x50aafc..0x50ac17, 0x50ac5c..0x50af47, 0x50afa4..0x50b03b,
 * 0x50b054..0x50b14b, 0x50b168..0x50b1b7, 0x50b1bc..0x50b427,
 * 0x50b438..0x50b5d3, 0x50b5f4..0x50b717, 0x50b744..0x50ba59,
 * 0x50ba64..0x50bd19; the literal pools between them (0x50aaf0.., 0x50ac18..,
 * 0x50af48.., 0x50af94.., 0x50b03c.., 0x50b14c.., 0x50b1b8.., 0x50b428..,
 * 0x50b5d4.., 0x50b718.., 0x50ba5c..) are data of this TU. 0x509fdc is the
 * IAR out-of-line copy of LVGL's lv_obj_set_style_pad_all (upstream) and
 * 0x50a010 (FPU) is onboarding_news_scroll_time.c. The scroll second half
 * (0x50bd1c..) is ui/a-42-onboarding-news-scroll.
 *
 * Two views share the file. The tile widget (Onboarding_NewsWidget_init /
 * _Reflash) draws a fixed sample news card into onboarding_tile_list[idx][1].
 * The expanded page (onboarding_news_ext_Widget_init) is a carousel of four
 * 576x288 containers at y = -288, 0, 288, 576 (RAM 0x20071048) fed from a
 * news FIFO of 0xc88-byte records (RAM 0x20120340); the current record is
 * peeked into RAM 0x20061110. Key events are mirrored to the peer as 8-byte
 * sync records {0, key, process_id, substep, a lo, a hi, b lo, b hi} of
 * application 0x10 and come back through the ext event handler. Stock
 * function names are taken from the log records; the seven entry points
 * that other files already call keep their existing names (stock names in
 * the comments). */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "g2_ui_common_api.h"

#define NEWS_CONTAINERS 4
#define NEWS_TILE_COUNT 6
#define NEWS_POS_PREV (-288)  /* ROM 0x50c864 */
#define NEWS_POS_CUR 0
#define NEWS_POS_NEXT 288
#define NEWS_POS_NEXT2 576
#define NEWS_SCROLL_ANIM_MS 250
#define NEWS_SWITCH_ANIM_MS 400
#define ONB_APP_ID 0x10u
#define WAIT_FOREVER 0xffffffffu

#define KEY_CLICK 0x0au
#define KEY_SCROLL_DOWN 0x44u
#define KEY_SCROLL_UP 0x45u
#define KEY_46 0x46u
#define KEY_DOUBLE_CLICK 0x48u
#define KEY_49 0x49u

#define LV_PCT_100 0x20000064     /* LV_PCT(100) */
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PART_MAIN 0u
#define LV_PART_SCROLLBAR 0x10000u
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_CLICKABLE 0x2u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_TOP_MID 2u
#define LV_ALIGN_TOP_RIGHT 3u
#define LV_ALIGN_OUT_BOTTOM_LEFT 13u
#define LV_ALIGN_OUT_BOTTOM_MID 14u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_TEXT_ALIGN_RIGHT 3u
#define LV_LABEL_LONG_WRAP 0u
#define LV_LABEL_LONG_DOT 1u
#define LV_DIR_VER 0xcu
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_SCROLLBAR_MODE_ON 1u
#define LV_FLEX_FLOW_ROW 0u
#define LV_FLEX_ALIGN_CENTER 2u
#define COLOR_BLACK 0x000000u
#define COLOR_WHITE 0xffffffu

/* One carousel container (same layout as in ui/a-42-onboarding-news-scroll). */
typedef struct {
    void *root;               /* +0x00 576x288 container, moved by y */
    void *content_scroll;     /* +0x04 vertically scrolling content */
    void *icon;               /* +0x08 */
    void *source_label;       /* +0x0c */
    void *time_label;         /* +0x10 */
    void *title_label;        /* +0x14 */
    void *content_label;      /* +0x18 */
    uint32_t news_id;         /* +0x1c id of the loaded record */
    int32_t position_y;       /* +0x20 -288 / 0 / 288 / 576 */
    uint8_t scrollable;       /* +0x24 content taller than the viewport */
    uint8_t at_top;           /* +0x25 */
    uint8_t at_bottom;        /* +0x26 */
    uint8_t flag_27;          /* +0x27 shown (read) */
    uint8_t flag_28;          /* +0x28 */
    uint8_t data_loaded;      /* +0x29 */
    uint8_t reserved_2a[2];
    int32_t read_count;       /* +0x2c */
} g2_onboarding_news_container_t;
_Static_assert(sizeof(g2_onboarding_news_container_t) == 0x30, "news container");

/* RAM 0x20071048. */
typedef struct {
    g2_onboarding_news_container_t container[NEWS_CONTAINERS]; /* +0x00 */
    int32_t news_count;       /* +0xc0 */
    uint8_t is_switching;     /* +0xc4 */
    uint8_t reserved_c5[3];
    void *page_obj;           /* +0xc8 */
} g2_onboarding_news_scroll_t;
_Static_assert(sizeof(g2_onboarding_news_scroll_t) == 0xcc, "news page state is cleared as 0xcc bytes");

/* RAM 0x20073c80: target slots applied when the switch animation completes. */
typedef struct {
    int32_t direction;                 /* +0x00 1 next, -1 previous */
    int32_t target_y[NEWS_CONTAINERS]; /* +0x04 */
    uint8_t pending;                   /* +0x14 */
} g2_onboarding_news_pending_t;
_Static_assert(sizeof(g2_onboarding_news_pending_t) == 0x18, "pending switch record");

/* News record as queued by the app (0xc88 bytes). */
typedef struct {
    uint32_t id;              /* +0x000 */
    char source[0x40];        /* +0x004 */
    char title[0x80];         /* +0x044 */
    char content[0xbbc];      /* +0x0c4 */
    uint64_t timestamp_ms;    /* +0xc80 */
} g2_onboarding_news_record_t;
_Static_assert(sizeof(g2_onboarding_news_record_t) == 0xc88u, "news record");

/* RAM 0x20120340: ring of news records. */
typedef struct {
    uint16_t tail;            /* +0x00 write index (not used in this half) */
    uint16_t head;            /* +0x02 read index */
    uint16_t count;           /* +0x04 */
    uint16_t reserved_06;
    uint16_t capacity;        /* +0x08 */
    uint8_t reserved_0a[6];
    g2_onboarding_news_record_t records[]; /* +0x10 */
} g2_onboarding_news_fifo_t;

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

typedef struct {
    uint8_t process_id;  /* +0 */
    uint8_t substep;     /* +1 */
    uint8_t status;      /* +2 */
    uint8_t reserved;    /* +3 */
    uint32_t step_tick;  /* +4 */
} g2_onboarding_process_t;

typedef struct {
    uint8_t key;
    uint8_t process_id;
    uint8_t substep;
    uint8_t reserved;
    uint32_t value;
} g2_onboarding_key_msg_t;
_Static_assert(sizeof(g2_onboarding_key_msg_t) == 8u, "key sync record");

/* RAM state. 0x20071048 / 0x20074db8 / 0x20074db4 keep the names given in
 * ui_onboarding_main_page.c (which calls them "stock"; they belong to this
 * news page). */
extern g2_onboarding_news_scroll_t g2_onboarding_stock_page_20071048;  /* RAM 0x20071048 */
extern int32_t g2_onboarding_stock_flag_20074db8;      /* RAM 0x20074db8 ext page initialised */
extern void *g2_onboarding_stock_obj_20074db4;         /* RAM 0x20074db4 "no news" placeholder */
extern g2_ui_fifo_t *g2_onboarding_news_ext_fifo_20074db0; /* RAM 0x20074db0 queued key records */
extern void *g2_onboarding_mutex;                      /* RAM 0x20074830 osMutexId_t */
extern void *g2_onboarding_main_obj_20074ce8;          /* RAM 0x20074ce8 feature page container */
extern void *g2_onboarding_tile_list[NEWS_TILE_COUNT][2]; /* RAM 0x200734ec {tile, frame} */
extern g2_onboarding_process_t g2_onboarding_process;  /* RAM 0x200f4800 */
extern g2_onboarding_news_record_t g2_onboarding_news_record_20061110; /* RAM 0x20061110 peeked record */
extern int32_t g2_onboarding_news_animating_20074d94;  /* RAM 0x20074d94 */
extern uint8_t g2_onboarding_news_anim_kind_2007503e;  /* RAM 0x2007503e */
extern void *g2_onboarding_news_anim_obj_20074d8c;     /* RAM 0x20074d8c */
extern g2_onboarding_news_pending_t g2_onboarding_news_pending_20073c80; /* RAM 0x20073c80 */
extern g2_onboarding_news_fifo_t g2_onboarding_news_fifo_20120340;      /* RAM 0x20120340 */
extern int32_t g2_onboarding_news_shown_20074d90;      /* RAM 0x20074d90 tile widget requested */
extern int32_t g2_onboarding_news_tile_index_200042b8; /* RAM 0x200042b8 (.data) */
extern uint8_t g2_onboarding_news_state_200715c8[0xa8]; /* RAM 0x200715c8 */
extern g2_onboarding_news_record_t g2_onboarding_news_reflash_record_20061d98; /* RAM 0x20061d98 */
extern void *g2_onboarding_news_widget_20074d98;       /* RAM 0x20074d98 tile card container */
extern void *g2_onboarding_news_icon_20074d9c;         /* RAM 0x20074d9c */
extern void *g2_onboarding_news_title_20074da0;        /* RAM 0x20074da0 */
extern void *g2_onboarding_news_content1_20074da4;     /* RAM 0x20074da4 */
extern void *g2_onboarding_news_content2_20074da8;     /* RAM 0x20074da8 */
extern void *g2_onboarding_news_time_20074dac;         /* RAM 0x20074dac */
extern uint32_t audio_uart_ring_primary_head_cell;     /* RAM 0x200746dc: active lv_font_t * */
extern const uint8_t news_icon_76e7c0[];               /* ROM 0x76e7c0 lv_image_dsc_t */

/* Logging, RTOS, libc, time. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);  /* memset 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t, uint32_t, uint32_t, uint32_t); /* u64 / u64 */
extern void service_time_epoch_to_calendar(uint32_t epoch, g2_calendar_t *out); /* 0x44a100 */
extern void service_time_current_calendar_get(g2_calendar_t *out);              /* 0x44a19a */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags); /* 0x464bb2 app data sync */
extern uint32_t audio_uart_page_460084(const char *key);        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */

/* LVGL 9.3 fork (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                       /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);           /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);           /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flags);
extern uint32_t audio_terminal_ui_object_valid_43e2ea(const void *obj);  /* lv_obj_is_valid */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);     /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);     /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                           /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x, int32_t y); /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);               /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                    /* lv_color_hex */
extern void audio_uart_page_441164(void *obj, int32_t v, uint32_t sel);  /* style width */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);  /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);  /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);  /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);  /* style pad_right */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);  /* style pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t c, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel); /* style bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t c, uint32_t sel); /* style border_color */
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
extern void audio_lv_style_a_44145a(void *obj, uint32_t v, uint32_t sel); /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* style radius */
extern void audio_lv_delete_44d7b8(void *obj);                           /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                           /* lv_obj_clean */
extern void *audio_uart_lv_obj_parent_44dca2(void *obj);                 /* lv_obj_get_parent */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);   /* lv_obj_get_child */
extern uint32_t audio_uart_lv_child_count_44ddea(void *obj);             /* lv_obj_get_child_count */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);            /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);             /* lv_obj_set_scroll_dir */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                    /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *obj);               /* lv_obj_get_scroll_top */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);            /* lv_obj_get_scroll_bottom */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern uint32_t audio_uart_anim_delete_450500(void *var, void (*exec_cb)(void *, int32_t)); /* lv_anim_delete */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);            /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_lv_image_create_498668(void *parent);                 /* lv_image_create */
extern void audio_lv_image_source_498680(void *img, const void *src);    /* lv_image_set_src */
extern void *audio_lv_label_create_499416(void *parent);                 /* lv_label_create */
extern void audio_lv_label_text_49942e(void *label, const char *text);   /* lv_label_set_text */
extern void audio_lv_label_mode_499678(void *label, uint32_t mode);      /* lv_label_set_long_mode */

/* Onboarding main page (ui/a-18-onboarding-main-page). */
extern void ui_onboarding_main_sub_004A93B0(const uint8_t *data, uint32_t len); /* weather/battery update */
extern void ui_onboarding_main_sub_004A96DC(uint8_t mode);       /* fade the page out */
extern int32_t ui_onboarding_main_sub_004A979C(const uint8_t *raw, int32_t offset,
                                               g2_onboarding_key_msg_t *out);
extern void ui_onboarding_main_sub_004A9DE8(void);               /* collapse feature page */
extern void ui_onboarding_main_sub_004A9EDC(void);               /* Onboarding_ProcessStart */

/* Same TU: IAR copy of the LVGL inline (upstream lv_obj_style.h). */
extern void lv_obj_set_style_pad_all_509fdc(void *obj, int32_t value, uint32_t selector);
/* Same TU: onboarding_news_scroll_time.c. */
extern int32_t onboarding_news_scroll_calc_anim_time_50a010(int32_t speed, int32_t distance);
/* Same TU, second half: ui/a-42-onboarding-news-scroll. */
extern void onboarding_news_scroll_switch_to_prev_news_50bd1c(void);
extern void onboarding_news_scroll_anim_exec_cb_50c150(void *obj, int32_t y);
extern void onboarding_news_scroll_content_with_anim_50c1c0(void *obj, int32_t target_y, int32_t time_ms);
extern void onboarding_news_scroll_discard_read_news_from_fifo_50c288(void);
extern uint32_t onboarding_news_scroll_load_next_available_news_50c314(g2_onboarding_news_container_t *c,
                                                                        int32_t base_index);
extern void onboarding_news_scroll_sync_count_50c3c0(void);
extern int32_t onboarding_news_scroll_clamp_target_y_50c3f4(void *scroll_obj, int32_t target_y);
extern g2_onboarding_news_container_t *onboarding_news_find_container_at_50c476(int32_t position_y);
extern void onboarding_news_container_reset_50c4ac(g2_onboarding_news_container_t *c);
extern uint32_t onboarding_news_scroll_can_scroll_down_50c528(void);
extern void onboarding_news_scroll_reset_content_position_50c6e2(g2_onboarding_news_container_t *c);
extern void onboarding_news_container_anim_exec_cb_50c768(void *var, int32_t delta_y);
extern void onboarding_news_container_move_with_anim_50c7a8(int32_t direction, int32_t time_ms);
extern void onboarding_news_scroll_preload_containers_50c868(void);
extern int32_t onboarding_news_scroll_find_next_unloaded_50c8cc(void);

void onboarding_news_data_reset_50a07e(void);
int32_t onboarding_news_page_refresh_50a094(void);
int32_t onboarding_news_page_show_50a47e(uint32_t index);
int32_t onboarding_news_key_handler_50a4ee(uint32_t key, void *data);
void onboarding_news_ext_input_event_warpper_50a670(uint8_t key, uint32_t value);
void onboarding_news_page_close_50a9c2(void);
int32_t onboarding_news_ext_event_handler_50aafc(const uint8_t *data, uint32_t len);
int32_t onboarding_news_page_create_50ac5c(void *parent);
uint8_t onboarding_news_page_fifo_pop_50afa4(g2_onboarding_news_fifo_t *fifo, g2_onboarding_news_record_t *out);
uint8_t onboarding_news_page_fifo_peek_at_50b054(g2_onboarding_news_fifo_t *fifo, g2_onboarding_news_record_t *out,
                                                 uint16_t index);
bool onboarding_news_page_fifo_is_empty_50b168(const g2_onboarding_news_fifo_t *fifo);
uint16_t onboarding_news_page_fifo_count_50b180(const g2_onboarding_news_fifo_t *fifo);
uint8_t onboarding_news_fifo_pop_50b18c(g2_onboarding_news_record_t *out);
uint8_t onboarding_news_fifo_peek_50b19a(g2_onboarding_news_record_t *out, uint16_t index);
uint16_t onboarding_news_fifo_count_50b1ac(void);
void onboarding_news_container_create_50b1bc(g2_onboarding_news_container_t *c, void *parent, int32_t y);
void onboarding_news_scroll_load_news_data_50b438(g2_onboarding_news_container_t *c, int32_t index);
void onboarding_news_scroll_update_content_state_50b5f4(g2_onboarding_news_container_t *c);
void onboarding_news_scroll_handle_vertical_scroll_50b744(int32_t direction, int32_t speed, int32_t distance);
void onboarding_news_scroll_switch_to_next_news_50ba64(void);

static const char module_tag[] = "onboarding.news"; /* ROM 0x789df0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\ui_onboarding_news_page.c"; /* ROM 0x6eab04 */
static const char fn_reflash[] = "Onboarding_NewsWidget_init_Reflash"; /* ROM 0x75c690 */
static const char tile_null[] =
    "onboarding_tile_list[%d][1] is NULL, cannot create news widgets. This may happen if indicator_count is less than %d"; /* ROM 0x6a534c */
static const char tile_null_short[] =
    "[onboarding.news]onboarding_tile_list[%d][1] is NULL, cannot create news widgets. This may happen if indicator_count is less than %d"; /* ROM 0x6d4988 */
static const char id_title[] = "ID_ONBOARDING_NEWS_TITLE"; /* ROM 0x7741a8 */
static const char sample_time[] = "12:41"; /* ROM 0x78ed5c */
static const char id_content_1[] = "ID_ONBOARDING_NEWS_CONTENT_1"; /* ROM 0x767790 */
static const char id_content_2[] = "ID_ONBOARDING_NEWS_CONTENT_2"; /* ROM 0x7677b0 */
static const char fn_init[] = "Onboarding_NewsWidget_init"; /* ROM 0x7741c4 */
static const char bad_index[] = "Invalid index %d, must be 0-5"; /* ROM 0x7677d0 */
static const char bad_index_short[] = "[onboarding.news]Invalid index %d, must be 0-5"; /* ROM 0x73a904 */
static const char fn_wrapper[] = "onboarding_news_ext_input_event_warpper"; /* ROM 0x7509dc */
static const char not_init[] = "onboarding_news_ext_widget_init_flag == 0, return"; /* ROM 0x72ff94 */
static const char not_init_short[] = "[onboarding.news]onboarding_news_ext_widget_init_flag == 0, return"; /* ROM 0x707cac */
static const char fn_ext_event[] = "onboarding_news_ext_event_handler"; /* ROM 0x75c6b4 */
static const char len_zero[] = "len == 0, return"; /* ROM 0x784964 */
static const char len_zero_short[] = "[onboarding.news]len == 0, return"; /* ROM 0x75c6d8 */
static const char fn_ext_init[] = "onboarding_news_ext_Widget_init"; /* ROM 0x7677f0 */
static const char fifo_failed[] = "onboarding_news_ext_Widget_init: Failed to create event FIFO"; /* ROM 0x711124 */
static const char fifo_failed_short[] =
    "[onboarding.news]onboarding_news_ext_Widget_init: Failed to create event FIFO"; /* ROM 0x6f0b28 */
static const char id_default_1[] = "ID_ONBOARDING_NEWS_DEFAULT_1"; /* ROM 0x767810 */
static const char id_default_2[] = "ID_ONBOARDING_NEWS_DEFAULT_2"; /* ROM 0x767830 */
static const char fn_pop[] = "onboarding_news_page_fifo_pop"; /* ROM 0x767850 */
static const char fn_peek[] = "onboarding_news_page_fifo_peek_at"; /* ROM 0x75c720 */
static const char bad_params[] = "invalid parameters"; /* ROM 0x784978 */
static const char bad_params_short[] = "[onboarding.news]invalid parameters"; /* ROM 0x75c6fc */
static const char out_of_range[] = "index %d out of range (count=%d)"; /* ROM 0x75c744 */
static const char out_of_range_short[] = "[onboarding.news]index %d out of range (count=%d)"; /* ROM 0x72ffc8 */
static const char fn_load[] = "onboarding_news_scroll_load_news_data"; /* ROM 0x750a04 */
static const char load_failed[] = "Failed to load news data at FIFO index %d"; /* ROM 0x746010 */
static const char load_failed_short[] = "[onboarding.news]Failed to load news data at FIFO index %d"; /* ROM 0x71aae8 */
static const char fmt_date[] = "%02d/%02d"; /* ROM 0x78c884 */
static const char fmt_time[] = "%02d:%02d"; /* ROM 0x78c890 */
static const char fn_state[] = "onboarding_news_scroll_update_content_state"; /* ROM 0x74603c */
static const char content_invalid[] = "content_scroll object is invalid, skipping update"; /* ROM 0x72fffc */
static const char content_invalid_short[] =
    "[onboarding.news]content_scroll object is invalid, skipping update"; /* ROM 0x707cf0 */
static const char parent_invalid[] = "parent object is invalid, skipping layout update"; /* ROM 0x730030 */
static const char parent_invalid_short[] =
    "[onboarding.news]parent object is invalid, skipping layout update"; /* ROM 0x707d34 */
static const char fn_vertical[] = "onboarding_news_scroll_handle_vertical_scroll"; /* ROM 0x73a934 */
static const char anim_busy[] = "Animation in progress, ignoring scroll"; /* ROM 0x750a2c */
static const char anim_busy_short[] = "[onboarding.news]Animation in progress, ignoring scroll"; /* ROM 0x725648 */
static const char no_child[] = "ext_tileview has no child"; /* ROM 0x7741e0 */
static const char no_child_short[] = "[onboarding.news]ext_tileview has no child"; /* ROM 0x746068 */
static const char no_container[] = "No container at position 0 found"; /* ROM 0x75c768 */
static const char no_container_short[] = "[onboarding.news]No container at position 0 found"; /* ROM 0x730064 */
static const char down_invalid[] = "content_scroll is invalid in DOWN direction"; /* ROM 0x746094 */
static const char down_invalid_short[] = "[onboarding.news]content_scroll is invalid in DOWN direction"; /* ROM 0x711164 */
static const char up_invalid[] = "content_scroll is invalid in UP direction"; /* ROM 0x7460c0 */
static const char up_invalid_short[] = "[onboarding.news]content_scroll is invalid in UP direction"; /* ROM 0x71ab24 */
static const char scrolling_up[] = "Scrolling content up from %d to %d with %dms animation"; /* ROM 0x725680 */
static const char scrolling_up_short[] =
    "[onboarding.news]Scrolling content up from %d to %d with %dms animation"; /* ROM 0x6febc4 */
static const char fn_next[] = "onboarding_news_scroll_switch_to_next_news"; /* ROM 0x7460ec */
static const char preload_288[] = "Failed to pre-load news from FIFO index %d to 288 position"; /* ROM 0x71ab60 */
static const char preload_288_short[] =
    "[onboarding.news]Failed to pre-load news from FIFO index %d to 288 position"; /* ROM 0x6f7408 */
static const char preload_576[] = "Failed to pre-load news from FIFO index %d to 576 position"; /* ROM 0x71ab9c */
static const char preload_576_short[] =
    "[onboarding.news]Failed to pre-load news from FIFO index %d to 576 position"; /* ROM 0x6f7454 */
static const char load_576[] = "Failed to load news from FIFO index %d to 576 position"; /* ROM 0x7256b8 */
static const char load_576_short[] =
    "[onboarding.news]Failed to load news from FIFO index %d to 576 position"; /* ROM 0x6fec0c */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. */
#define NEWS_LOG(level, fn, line, cflags, msg, msg_short, ...)                                      \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

#define PAGE (&g2_onboarding_stock_page_20071048)
#define FONT() (audio_uart_ring_primary_head_cell)

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* Stop the content and container animations and clear the animation state
 * (inlined three times in the stock). */
static void news_stop_animations(void)
{
    for (int32_t i = 0; i < NEWS_CONTAINERS; i++) {
        void *scroll = PAGE->container[i].content_scroll;
        if (scroll != NULL && audio_terminal_ui_object_valid_43e2ea(scroll) != 0u)
            (void)audio_uart_anim_delete_450500(scroll, onboarding_news_scroll_anim_exec_cb_50c150);
    }
    (void)audio_uart_anim_delete_450500(PAGE, onboarding_news_container_anim_exec_cb_50c768);
    g2_onboarding_news_anim_obj_20074d8c = NULL;
    g2_onboarding_news_anim_kind_2007503e = 0u;
    g2_onboarding_news_animating_20074d94 = 0;
}

/* Free the key FIFO, delete the page children and forget the containers,
 * then redraw the tile card (inlined twice in the stock). */
static void news_destroy_ext_page(void)
{
    if (g2_onboarding_news_ext_fifo_20074db0 != NULL) {
        ui_common_api_fn_00509c96(g2_onboarding_news_ext_fifo_20074db0);
        g2_onboarding_news_ext_fifo_20074db0 = NULL;
    }
    for (int32_t i = (int32_t)audio_uart_lv_child_count_44ddea(g2_onboarding_main_obj_20074ce8) - 1; i >= 0; i--) {
        void *child = audio_uart_lv_child_get_44dce2(g2_onboarding_main_obj_20074ce8, i);
        if (child != NULL)
            audio_lv_delete_44d7b8(child);
    }
    for (int32_t i = 0; i < NEWS_CONTAINERS; i++) {
        g2_onboarding_news_container_t *c = &PAGE->container[i];
        c->root = NULL;
        c->content_scroll = NULL;
        c->icon = NULL;
        c->source_label = NULL;
        c->time_label = NULL;
        c->title_label = NULL;
        c->content_label = NULL;
        c->data_loaded = 0u;
    }
    g2_onboarding_stock_flag_20074db8 = 0;
    void *frame = g2_onboarding_tile_list[g2_onboarding_news_tile_index_200042b8][1];
    if (frame != NULL)
        audio_uart_page_44d878(frame);
    (void)onboarding_news_page_refresh_50a094();
}

static void *news_label(void *parent, int32_t w, int32_t h, int32_t x, int32_t y, const char *text)
{
    void *label = audio_lv_label_create_499416(parent);
    audio_uart_page_43f506(label, w);
    audio_uart_page_43f568(label, h);
    audio_uart_page_43f0e0(label, x);
    audio_uart_page_43f142(label, y);
    audio_lv_label_mode_499678(label, LV_LABEL_LONG_DOT);
    audio_lv_label_text_49942e(label, text);
    audio_lv_style_color_44140e(label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    return label;
}

/* Clears 0xa8 bytes of page state at RAM 0x200715c8. */
void onboarding_news_data_reset_50a07e(void)
{
    audio_uart_buffer_zero(g2_onboarding_news_state_200715c8, sizeof g2_onboarding_news_state_200715c8, 0u);
}

/* Onboarding_NewsWidget_init_Reflash: draw the sample news card into the
 * selected tile frame. The success path returns whatever the last style call
 * left in r0 in the stock; 0 here. */
int32_t onboarding_news_page_refresh_50a094(void)
{
    int32_t idx = g2_onboarding_news_tile_index_200042b8;
    if (g2_onboarding_news_shown_20074d90 == 0 || idx < 0)
        return 0;
    if (g2_onboarding_tile_list[idx][1] != NULL)
        audio_uart_page_44d878(g2_onboarding_tile_list[idx][1]);
    if (g2_onboarding_tile_list[g2_onboarding_news_tile_index_200042b8][1] == NULL) {
        idx = g2_onboarding_news_tile_index_200042b8;
        NEWS_LOG(1u, fn_reflash, 0xd5u, 0x04800000u, tile_null, tile_null_short, idx, idx + 1);
        return -1;
    }

    audio_uart_buffer_zero(&g2_onboarding_news_reflash_record_20061d98, sizeof(g2_onboarding_news_record_t), 0u);
    void *card = audio_uart_page_43de82(g2_onboarding_tile_list[g2_onboarding_news_tile_index_200042b8][1]);
    g2_onboarding_news_widget_20074d98 = card;
    audio_uart_page_43f09a(card, 0x14, 0x10);
    audio_uart_page_43f506(card, 0x13b);
    audio_uart_page_43f568(card, 0x100);
    audio_uart_page_44127e(card, audio_uart_page_44104c(COLOR_BLACK), LV_PART_MAIN);
    audio_uart_page_44129e(card, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(card, 0, LV_PART_MAIN);
    audio_uart_page_44133a(card, 0, LV_PART_MAIN);
    audio_uart_page_441378(card, 0, LV_PART_MAIN);
    audio_uart_page_441386(card, 0, LV_PART_MAIN);
    audio_uart_page_4413b0(card, 0, LV_PART_MAIN);
    audio_uart_page_441394(card, 0, LV_PART_MAIN);
    audio_uart_page_4413a2(card, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_509fdc(card, 0, LV_PART_MAIN);
    audio_uart_page_44120e(card, 0, LV_PART_MAIN);
    audio_uart_page_44121c(card, 0, LV_PART_MAIN);
    audio_uart_page_44122a(card, 0, LV_PART_MAIN);
    audio_uart_page_441238(card, 0, LV_PART_MAIN);
    audio_uart_page_44146a(card, 0, LV_PART_MAIN);
    audio_uart_page_4412ec(card, audio_uart_page_44104c(COLOR_BLACK), LV_PART_MAIN);
    audio_lv_style_color_44140e(card, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_alpha_44142e(card, 0xffu, LV_PART_MAIN);
    audio_uart_page_43dfa4(card, LV_OBJ_FLAG_SCROLLABLE);

    void *icon = audio_lv_image_create_498668(card);
    g2_onboarding_news_icon_20074d9c = icon;
    audio_lv_image_source_498680(icon, news_icon_76e7c0);
    audio_uart_page_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_uart_page_43f0e0(icon, 0);
    audio_uart_page_43f142(icon, 2);
    audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

    g2_onboarding_news_title_20074da0 = news_label(card, 0xda, 0x1c, 0x20, 0, localized(id_title));
    g2_onboarding_news_time_20074dac = news_label(card, 0x3c, 0x1c, 0xfa, 0, sample_time);
    g2_onboarding_news_content1_20074da4 =
        news_label(card, 0x13b, LV_SIZE_CONTENT, 0, 0x38, localized(id_content_1));

    void *content2 = audio_lv_label_create_499416(card);
    g2_onboarding_news_content2_20074da8 = content2;
    audio_uart_page_43f506(content2, 0x13b);
    audio_uart_page_43f568(content2, 0x96);
    audio_uart_page_43f0e0(content2, 0);
    audio_uart_page_43f6d6(content2, g2_onboarding_news_content1_20074da4, LV_ALIGN_OUT_BOTTOM_MID, 0, 0x1c);
    audio_lv_label_mode_499678(content2, LV_LABEL_LONG_DOT);
    audio_lv_label_text_49942e(content2, localized(id_content_2));
    audio_lv_style_color_44140e(content2, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(content2, FONT(), LV_PART_MAIN);
    return 0;
}

/* Onboarding_NewsWidget_init. */
int32_t onboarding_news_page_show_50a47e(uint32_t index)
{
    g2_onboarding_news_tile_index_200042b8 = (int32_t)index;
    g2_onboarding_news_shown_20074d90 = 1;
    if ((uint32_t)g2_onboarding_news_tile_index_200042b8 < NEWS_TILE_COUNT) {
        (void)onboarding_news_page_refresh_50a094();
        return 0;
    }
    NEWS_LOG(1u, fn_init, 300u, 0x04400000u, bad_index, bad_index_short, g2_onboarding_news_tile_index_200042b8);
    return -1;
}

/* Mirror a key to the peer. Returns the sync result, 0 while an animation
 * runs, or the key itself when it is not handled. */
int32_t onboarding_news_key_handler_50a4ee(uint32_t key, void *data)
{
    uint8_t rec[8];
    if (key != KEY_CLICK && key != KEY_DOUBLE_CLICK && key != KEY_49 && key != KEY_SCROLL_UP &&
        key != KEY_SCROLL_DOWN)
        return (int32_t)key;
    if (g2_onboarding_news_animating_20074d94 == 1)
        return 0;
    rec[0] = 0u;
    rec[1] = (uint8_t)key;
    rec[2] = g2_onboarding_process.process_id;
    rec[3] = g2_onboarding_process.substep;
    if (key == KEY_SCROLL_UP || key == KEY_SCROLL_DOWN) {
        /* lv_event_t param (+0x10): two words, low 16 bits of each sent. */
        const int32_t *arg = *(int32_t *const *)(void *)((uint8_t *)data + 0x10u);
        rec[4] = (uint8_t)arg[0];
        rec[5] = (uint8_t)(arg[0] >> 8);
        rec[6] = (uint8_t)arg[1];
        rec[7] = (uint8_t)(arg[1] >> 8);
    } else {
        rec[4] = 0u;
        rec[5] = 0u;
        rec[6] = 0u;
        rec[7] = 0u;
    }
    return (int32_t)audio_uart_master_display_refresh(ONB_APP_ID, rec, 8u, 0u);
}

/* onboarding_news_ext_input_event_warpper (sic): apply a mirrored key on the
 * expanded page. value = speed << 16 | distance for the scroll keys. */
void onboarding_news_ext_input_event_warpper_50a670(uint8_t key, uint32_t value)
{
    if (g2_onboarding_stock_flag_20074db8 == 0) {
        NEWS_LOG(2u, fn_wrapper, 0x18cu, 0x08000000u, not_init, not_init_short);
        return;
    }
    int32_t speed = (int32_t)value >> 16;
    int32_t distance = (int32_t)(value & 0xffffu);
    switch (key) {
    case KEY_CLICK:
    case KEY_DOUBLE_CLICK:
        news_stop_animations();
        news_destroy_ext_page();
        ui_onboarding_main_sub_004A9DE8();
        break;
    case KEY_SCROLL_DOWN:
        onboarding_news_scroll_handle_vertical_scroll_50b744(1, speed, distance);
        break;
    case KEY_SCROLL_UP:
        onboarding_news_scroll_handle_vertical_scroll_50b744(-1, speed, distance);
        break;
    case KEY_46:
        break;
    case KEY_49:
        news_stop_animations();
        ui_onboarding_main_sub_004A96DC(1u);
        g2_onboarding_stock_flag_20074db8 = 0;
        break;
    default:
        break;
    }
}

/* Close the expanded page without animation (called when the main page
 * closes the feature page). */
void onboarding_news_page_close_50a9c2(void)
{
    if (g2_onboarding_main_obj_20074ce8 == NULL)
        return;
    news_stop_animations();
    news_destroy_ext_page();
}

/* onboarding_news_ext_event_handler: records from the peer. Type 0 is a key
 * sync record (only the tutorial's double click at process 2 / substep 6 is
 * acted on), 1 a weather/battery update, 3 a tile refresh. Always 0. */
int32_t onboarding_news_ext_event_handler_50aafc(const uint8_t *data, uint32_t len)
{
    g2_onboarding_key_msg_t msg;
    if (g2_onboarding_stock_flag_20074db8 == 0) {
        NEWS_LOG(2u, fn_ext_event, 0x26fu, 0x08000000u, not_init, not_init_short);
        return 0;
    }
    if (len == 0u) {
        NEWS_LOG(2u, fn_ext_event, 0x274u, 0x08000000u, len_zero, len_zero_short);
        return 0;
    }
    switch (data[0]) {
    case 0u:
        if (ui_onboarding_main_sub_004A979C(data, 1, &msg) == 0 && msg.process_id == 2u && msg.substep == 6u &&
            msg.key == KEY_DOUBLE_CLICK) {
            (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
            g2_onboarding_process.substep = 7u;
            (void)osMutexRelease(g2_onboarding_mutex);
            ui_onboarding_main_sub_004A9EDC();
            onboarding_news_ext_input_event_warpper_50a670(msg.key, msg.value);
        }
        break;
    case 1u:
        ui_onboarding_main_sub_004A93B0(data + 1, len - 1u);
        break;
    case 3u:
        (void)onboarding_news_page_refresh_50a094();
        break;
    default:
        break;
    }
    return 0;
}

/* onboarding_news_ext_Widget_init: build the expanded news page. */
int32_t onboarding_news_page_create_50ac5c(void *parent)
{
    int32_t positions[NEWS_CONTAINERS] = { NEWS_POS_PREV, NEWS_POS_CUR, NEWS_POS_NEXT, NEWS_POS_NEXT2 }; /* ROM 0x789e00 */

    if (g2_onboarding_news_ext_fifo_20074db0 != NULL) {
        ui_common_api_fn_00509c96(g2_onboarding_news_ext_fifo_20074db0);
        g2_onboarding_news_ext_fifo_20074db0 = NULL;
    }
    if (g2_onboarding_news_ext_fifo_20074db0 == NULL) {
        g2_onboarding_news_ext_fifo_20074db0 = ui_common_api_fn_00509c1c();
        if (g2_onboarding_news_ext_fifo_20074db0 == NULL) {
            NEWS_LOG(1u, fn_ext_init, 0x2e6u, 0x04000000u, fifo_failed, fifo_failed_short);
            return -1;
        }
    }

    (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
    uint16_t count = onboarding_news_fifo_count_50b1ac();
    (void)osMutexRelease(g2_onboarding_mutex);

    audio_uart_buffer_zero(PAGE, sizeof(g2_onboarding_news_scroll_t), 0u);
    PAGE->page_obj = parent;
    PAGE->news_count = count;
    PAGE->is_switching = 0u;
    audio_uart_buffer_zero(&g2_onboarding_news_pending_20073c80, sizeof(g2_onboarding_news_pending_t), 0u);
    g2_onboarding_news_pending_20073c80.pending = 0u;

    for (int32_t i = 0; i < NEWS_CONTAINERS; i++) {
        onboarding_news_container_create_50b1bc(&PAGE->container[i], parent, positions[i]);
        PAGE->container[i].position_y = positions[i];
    }
    if (count != 0u) {
        for (int32_t i = 0; i < 3 && i < (int32_t)count; i++)
            onboarding_news_scroll_load_news_data_50b438(&PAGE->container[i + 1], i);
    }
    onboarding_news_container_reset_50c4ac(&PAGE->container[0]);
    for (int32_t i = 0; i < NEWS_CONTAINERS; i++)
        onboarding_news_scroll_update_content_state_50b5f4(&PAGE->container[i]);
    audio_uart_page_44e368(PAGE->container[1].content_scroll, LV_SCROLLBAR_MODE_ON);

    /* "No news" placeholder covering the page. */
    void *empty = audio_uart_page_43de82(parent);
    g2_onboarding_stock_obj_20074db4 = empty;
    audio_uart_page_43f4c0(empty, LV_PCT_100, LV_PCT_100);
    audio_uart_page_44129e(empty, 0xffu, LV_PART_MAIN);
    audio_uart_page_44127e(empty, audio_uart_page_44104c(COLOR_BLACK), LV_PART_MAIN);
    audio_uart_page_44131c(empty, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_509fdc(empty, 0, LV_PART_MAIN);

    void *row = audio_uart_page_43de82(empty);
    audio_uart_page_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(row, 0u, LV_PART_MAIN);
    audio_uart_page_44131c(row, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_all_509fdc(row, 0, LV_PART_MAIN);
    audio_uart_page_48ba78(row, LV_FLEX_FLOW_ROW);
    audio_uart_page_48ba92(row, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    audio_uart_page_441254(row, 8, LV_PART_MAIN);
    audio_uart_page_43f6b8(row, LV_ALIGN_TOP_MID, 0, 0x74);

    void *icon = audio_lv_image_create_498668(row);
    audio_lv_image_source_498680(icon, news_icon_76e7c0);
    audio_uart_page_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

    void *label = audio_lv_label_create_499416(row);
    audio_lv_label_text_49942e(label, localized(id_default_1));
    audio_lv_style_color_44140e(label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);

    label = audio_lv_label_create_499416(empty);
    audio_lv_label_text_49942e(label, localized(id_default_2));
    audio_lv_style_color_44140e(label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(label, FONT(), LV_PART_MAIN);
    audio_lv_style_a_44145a(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    audio_uart_page_43f6b8(label, LV_ALIGN_TOP_MID, 0, 0x92);

    if (count == 0u)
        audio_uart_page_43dfa4(empty, LV_OBJ_FLAG_HIDDEN);
    else
        audio_uart_page_43ded4(empty, LV_OBJ_FLAG_HIDDEN);
    g2_onboarding_news_animating_20074d94 = 0;
    g2_onboarding_stock_flag_20074db8 = 1;
    return 0;
}

/* onboarding_news_page_fifo_pop: 1 when a record was copied out. */
uint8_t onboarding_news_page_fifo_pop_50afa4(g2_onboarding_news_fifo_t *fifo, g2_onboarding_news_record_t *out)
{
    if (fifo == NULL || out == NULL) {
        NEWS_LOG(2u, fn_pop, 0x3bcu, 0x08000000u, bad_params, bad_params_short);
        return 0u;
    }
    if (onboarding_news_page_fifo_is_empty_50b168(fifo))
        return 0u;
    (void)audio_queue_copy_bytes(out, &fifo->records[fifo->head], sizeof(g2_onboarding_news_record_t));
    fifo->head = (uint16_t)((uint32_t)(fifo->head + 1u) % fifo->capacity);
    fifo->count--;
    return 1u;
}

/* onboarding_news_page_fifo_peek_at: copy record head + index. */
uint8_t onboarding_news_page_fifo_peek_at_50b054(g2_onboarding_news_fifo_t *fifo, g2_onboarding_news_record_t *out,
                                                 uint16_t index)
{
    if (fifo == NULL || out == NULL) {
        NEWS_LOG(2u, fn_peek, 0x3e5u, 0x08000000u, bad_params, bad_params_short);
        return 0u;
    }
    if (onboarding_news_page_fifo_is_empty_50b168(fifo))
        return 0u;
    if (index >= fifo->count) {
        NEWS_LOG(2u, fn_peek, 0x3efu, 0x08800000u, out_of_range, out_of_range_short, (uint32_t)index,
                 (uint32_t)fifo->count);
        return 0u;
    }
    uint16_t slot = (uint16_t)((uint32_t)(index + fifo->head) % fifo->capacity);
    (void)audio_queue_copy_bytes(out, &fifo->records[slot], sizeof(g2_onboarding_news_record_t));
    return 1u;
}

bool onboarding_news_page_fifo_is_empty_50b168(const g2_onboarding_news_fifo_t *fifo)
{
    if (fifo == NULL)
        return true;
    return fifo->count == 0u;
}

uint16_t onboarding_news_page_fifo_count_50b180(const g2_onboarding_news_fifo_t *fifo)
{
    if (fifo == NULL)
        return 0u;
    return fifo->count;
}

uint8_t onboarding_news_fifo_pop_50b18c(g2_onboarding_news_record_t *out)
{
    return onboarding_news_page_fifo_pop_50afa4(&g2_onboarding_news_fifo_20120340, out);
}

uint8_t onboarding_news_fifo_peek_50b19a(g2_onboarding_news_record_t *out, uint16_t index)
{
    return onboarding_news_page_fifo_peek_at_50b054(&g2_onboarding_news_fifo_20120340, out, index);
}

uint16_t onboarding_news_fifo_count_50b1ac(void)
{
    return onboarding_news_page_fifo_count_50b180(&g2_onboarding_news_fifo_20120340);
}

/* Build one 576x288 carousel container at page y. */
void onboarding_news_container_create_50b1bc(g2_onboarding_news_container_t *c, void *parent, int32_t y)
{
    if (c == NULL || parent == NULL)
        return;
    c->root = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(c->root, 0x240, 0x120);
    audio_uart_page_43f09a(c->root, 0, y);
    audio_uart_page_44127e(c->root, audio_uart_page_44104c(COLOR_BLACK), LV_PART_MAIN);
    audio_uart_page_44129e(c->root, 0u, LV_PART_MAIN);
    lv_obj_set_style_pad_all_509fdc(c->root, 0, LV_PART_MAIN);
    audio_uart_page_44131c(c->root, 0, LV_PART_MAIN);
    audio_uart_page_43dfa4(c->root, LV_OBJ_FLAG_CLICKABLE);

    c->content_scroll = audio_uart_page_43de82(c->root);
    audio_uart_page_43f4c0(c->content_scroll, 0x240, 0x120);
    audio_uart_page_43f09a(c->content_scroll, 0, 0);
    audio_uart_page_44129e(c->content_scroll, 0u, LV_PART_MAIN);
    lv_obj_set_style_pad_all_509fdc(c->content_scroll, 0, LV_PART_MAIN);
    audio_uart_page_44131c(c->content_scroll, 0, LV_PART_MAIN);
    audio_uart_page_44e3ca(c->content_scroll, LV_DIR_VER);
    audio_uart_page_44e368(c->content_scroll, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44127e(c->content_scroll, audio_uart_page_44104c(COLOR_WHITE), LV_PART_SCROLLBAR);
    audio_uart_page_44129e(c->content_scroll, 0xb4u, LV_PART_SCROLLBAR);
    audio_uart_page_441164(c->content_scroll, 4, LV_PART_SCROLLBAR);

    c->icon = audio_lv_image_create_498668(c->content_scroll);
    audio_lv_image_source_498680(c->icon, news_icon_76e7c0);
    audio_uart_page_43f4c0(c->icon, 0x18, 0x18);
    audio_uart_page_43f09a(c->icon, 0x14, 0x10);
    audio_uart_page_43ded4(c->icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(c->icon, LV_OBJ_FLAG_SCROLLABLE);

    c->source_label = audio_lv_label_create_499416(c->content_scroll);
    audio_uart_page_43f4c0(c->source_label, 0x1b8, 0x1c);
    audio_uart_page_43f09a(c->source_label, 0x34, 0x10);
    audio_lv_label_mode_499678(c->source_label, LV_LABEL_LONG_DOT);
    audio_lv_style_color_44140e(c->source_label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(c->source_label, FONT(), LV_PART_MAIN);

    c->time_label = audio_lv_label_create_499416(c->content_scroll);
    audio_uart_page_43f4c0(c->time_label, LV_SIZE_CONTENT, 0x1c);
    audio_uart_page_43f6d6(c->time_label, c->content_scroll, LV_ALIGN_TOP_RIGHT, -16, 16);
    audio_lv_label_mode_499678(c->time_label, LV_LABEL_LONG_DOT);
    audio_lv_style_color_44140e(c->time_label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(c->time_label, FONT(), LV_PART_MAIN);
    audio_lv_style_a_44145a(c->time_label, LV_TEXT_ALIGN_RIGHT, LV_PART_MAIN);

    c->title_label = audio_lv_label_create_499416(c->content_scroll);
    audio_uart_page_43f4c0(c->title_label, 0x168, LV_SIZE_CONTENT);
    audio_uart_page_43f09a(c->title_label, 0x14, 0x38);
    audio_lv_style_color_44140e(c->title_label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(c->title_label, FONT(), LV_PART_MAIN);
    audio_lv_label_mode_499678(c->title_label, LV_LABEL_LONG_WRAP);

    c->content_label = audio_lv_label_create_499416(c->content_scroll);
    audio_uart_page_43f4c0(c->content_label, 0x21b, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(c->content_label, c->title_label, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 0x1c);
    audio_lv_style_color_44140e(c->content_label, audio_uart_page_44104c(COLOR_WHITE), LV_PART_MAIN);
    audio_lv_style_font_44143e(c->content_label, FONT(), LV_PART_MAIN);
    audio_lv_label_mode_499678(c->content_label, LV_LABEL_LONG_WRAP);

    c->news_id = 0u;
    c->position_y = y;
    c->scrollable = 0u;
    c->at_top = 1u;
    c->at_bottom = 1u;
    c->flag_27 = 0u;
    c->flag_28 = 0u;
    c->data_loaded = 0u;
    c->read_count = 0;
}

/* onboarding_news_scroll_load_news_data: peek FIFO record `index` into the
 * container. The time label shows MM/DD for news from an earlier day and
 * HH:MM for today's. */
void onboarding_news_scroll_load_news_data_50b438(g2_onboarding_news_container_t *c, int32_t index)
{
    char when[0x20];
    g2_calendar_t news_time;
    g2_calendar_t now;

    if (c == NULL || index < 0 || index >= PAGE->news_count)
        return;
    (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
    uint8_t ok = onboarding_news_fifo_peek_50b19a(&g2_onboarding_news_record_20061110, (uint16_t)index);
    (void)osMutexRelease(g2_onboarding_mutex);
    if (ok == 0u) {
        NEWS_LOG(1u, fn_load, 0x532u, 0x04400000u, load_failed, load_failed_short, index);
        return;
    }

    const g2_onboarding_news_record_t *rec = &g2_onboarding_news_record_20061110;
    c->news_id = rec->id;
    c->flag_27 = 0u;
    c->flag_28 = 0u;
    c->data_loaded = 1u;
    c->read_count = 0;
    audio_lv_label_text_49942e(c->source_label, rec->source);
    audio_uart_buffer_zero(when, sizeof when, 0u);
    uint32_t epoch = (uint32_t)audio_uart_ring_u64_div_47cc60((uint32_t)rec->timestamp_ms,
                                                               (uint32_t)(rec->timestamp_ms >> 32), 1000u, 0u);
    service_time_epoch_to_calendar(epoch, &news_time);
    service_time_current_calendar_get(&now);
    if (news_time.year < now.year || (now.year == news_time.year && news_time.month < now.month) ||
        (now.year == news_time.year && now.month == news_time.month && news_time.day < now.day))
        (void)g2_audio_dump_snprintf(when, sizeof when, fmt_date, news_time.month, news_time.day);
    else
        (void)g2_audio_dump_snprintf(when, sizeof when, fmt_time, news_time.hour, news_time.minute);
    audio_lv_label_text_49942e(c->time_label, when);
    audio_uart_page_43f6d6(c->time_label, c->content_scroll, LV_ALIGN_TOP_RIGHT, -16, 16);
    audio_lv_label_text_49942e(c->title_label, rec->title);
    audio_lv_label_text_49942e(c->content_label, rec->content);
    audio_uart_page_43f66c(c->title_label);
    audio_uart_page_43f6d6(c->content_label, c->title_label, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 0xc);
    audio_uart_lv_scroll_to_y_44ea04(c->content_scroll, 0, 0u);
    audio_uart_page_43f66c(c->content_scroll);
    onboarding_news_scroll_update_content_state_50b5f4(c);
}

/* onboarding_news_scroll_update_content_state: recompute scrollable /
 * at_top / at_bottom (3 px tolerance) after a layout change. */
void onboarding_news_scroll_update_content_state_50b5f4(g2_onboarding_news_container_t *c)
{
    if (c == NULL || c->content_scroll == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(c->content_scroll) == 0u) {
        NEWS_LOG(2u, fn_state, 0x570u, 0x08000000u, content_invalid, content_invalid_short);
        c->content_scroll = NULL;
        return;
    }
    void *parent = audio_uart_lv_obj_parent_44dca2(c->content_scroll);
    if (parent != NULL && audio_terminal_ui_object_valid_43e2ea(parent) == 0u) {
        NEWS_LOG(2u, fn_state, 0x579u, 0x08000000u, parent_invalid, parent_invalid_short);
        return;
    }
    audio_uart_page_43f66c(c->content_scroll);
    int32_t top = audio_uart_lv_scroll_top_44e4aa(c->content_scroll);
    int32_t bottom = audio_uart_lv_scroll_bottom_44e4bc(c->content_scroll);
    int32_t height = audio_uart_lv_obj_height_43fdda(c->content_scroll);
    c->scrollable = height < bottom + top + height;
    if (c->scrollable == 0u) {
        audio_uart_page_44e368(c->content_scroll, LV_SCROLLBAR_MODE_OFF);
        c->at_top = 1u;
        c->at_bottom = 1u;
    } else {
        c->at_top = audio_uart_lv_obj_y_44e498(c->content_scroll) < 3;
        c->at_bottom = bottom < 3;
    }
}

/* Scroll step: double for distance 50..100, triple above 100. */
static int32_t scroll_step(int32_t speed, int32_t distance)
{
    if (speed == 0)
        speed = 1;
    if (distance > 100)
        speed *= 3;
    else if (distance > 49)
        speed <<= 1;
    return speed;
}

/* onboarding_news_scroll_handle_vertical_scroll: direction 1 down, -1 up.
 * Scrolls the current item's content, or switches item at the content end. */
void onboarding_news_scroll_handle_vertical_scroll_50b744(int32_t direction, int32_t speed, int32_t distance)
{
    if (g2_onboarding_news_animating_20074d94 != 0) {
        NEWS_LOG(2u, fn_vertical, 0x5bdu, 0x08000000u, anim_busy, anim_busy_short);
        return;
    }
    if (audio_uart_lv_child_count_44ddea(g2_onboarding_main_obj_20074ce8) == 0u) {
        NEWS_LOG(2u, fn_vertical, 0x5c3u, 0x08000000u, no_child, no_child_short);
        return;
    }
    (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
    uint16_t count = onboarding_news_fifo_count_50b1ac();
    (void)osMutexRelease(g2_onboarding_mutex);
    if (count != 0u && audio_uart_lv_obj_has_flag_43e0e0(g2_onboarding_stock_obj_20074db4, LV_OBJ_FLAG_HIDDEN) == 0u)
        audio_uart_page_43ded4(g2_onboarding_stock_obj_20074db4, LV_OBJ_FLAG_HIDDEN);
    onboarding_news_scroll_preload_containers_50c868();

    g2_onboarding_news_container_t *cur = NULL;
    for (int32_t i = 0; i < NEWS_CONTAINERS; i++) {
        if (PAGE->container[i].position_y == NEWS_POS_CUR) {
            cur = &PAGE->container[i];
            break;
        }
    }
    if (cur == NULL) {
        NEWS_LOG(1u, fn_vertical, 0x5e5u, 0x04000000u, no_container, no_container_short);
        return;
    }
    onboarding_news_scroll_update_content_state_50b5f4(cur);

    if (direction >= 1) {
        if (cur->scrollable == 0u || cur->at_bottom != 0u) {
            onboarding_news_scroll_switch_to_next_news_50ba64();
            return;
        }
        if (audio_terminal_ui_object_valid_43e2ea(cur->content_scroll) == 0u) {
            NEWS_LOG(2u, fn_vertical, 0x5f6u, 0x08000000u, down_invalid, down_invalid_short);
            return;
        }
        audio_uart_page_43f66c(cur->content_scroll);
        int32_t y = audio_uart_lv_obj_y_44e498(cur->content_scroll);
        speed = scroll_step(speed, distance);
        int32_t target = onboarding_news_scroll_clamp_target_y_50c3f4(cur->content_scroll, speed + y);
        (void)onboarding_news_scroll_calc_anim_time_50a010(speed, distance); /* result unused */
        onboarding_news_scroll_content_with_anim_50c1c0(cur->content_scroll, target, NEWS_SCROLL_ANIM_MS);
    } else {
        if (cur->scrollable == 0u || cur->at_top != 0u) {
            onboarding_news_scroll_switch_to_prev_news_50bd1c();
            return;
        }
        if (audio_terminal_ui_object_valid_43e2ea(cur->content_scroll) == 0u) {
            NEWS_LOG(2u, fn_vertical, 0x61au, 0x08000000u, up_invalid, up_invalid_short);
            return;
        }
        audio_uart_page_43f66c(cur->content_scroll);
        int32_t y = audio_uart_lv_obj_y_44e498(cur->content_scroll);
        speed = scroll_step(speed, distance);
        int32_t target = onboarding_news_scroll_clamp_target_y_50c3f4(cur->content_scroll, y - speed);
        (void)onboarding_news_scroll_calc_anim_time_50a010(speed, distance); /* result unused */
        onboarding_news_scroll_content_with_anim_50c1c0(cur->content_scroll, target, NEWS_SCROLL_ANIM_MS);
        NEWS_LOG(3u, fn_vertical, 0x634u, 0x0cc00000u, scrolling_up, scrolling_up_short, y, target,
                 NEWS_SCROLL_ANIM_MS);
    }
}

/* onboarding_news_scroll_switch_to_next_news: when there is a next item,
 * preload 288/576, then rotate every container up one slot (the one leaving
 * at -288 wraps to 576, is cleared, its read record discarded from the FIFO
 * and refilled) and start the 400 ms container animation. Otherwise replay
 * one queued key record. */
void onboarding_news_scroll_switch_to_next_news_50ba64(void)
{
    onboarding_news_scroll_sync_count_50c3c0();
    if (onboarding_news_scroll_can_scroll_down_50c528() == 0u) {
        if (g2_onboarding_stock_flag_20074db8 == 1 && g2_onboarding_news_ext_fifo_20074db0 != NULL &&
            ui_common_api_fn_00509dfa(g2_onboarding_news_ext_fifo_20074db0) == 0) {
            uint8_t raw[10];
            g2_onboarding_key_msg_t msg;
            audio_uart_buffer_zero(raw, sizeof raw, 0u);
            audio_uart_buffer_zero(raw, sizeof raw, 0u);
            (void)ui_common_api_fn_00509e14(g2_onboarding_news_ext_fifo_20074db0, raw, 7u);
            if (ui_onboarding_main_sub_004A979C(raw, 0, &msg) == 0)
                onboarding_news_ext_input_event_warpper_50a670(msg.key, msg.value);
        }
        return;
    }

    g2_onboarding_news_container_t *c = onboarding_news_find_container_at_50c476(NEWS_POS_NEXT);
    int32_t idx;
    if (c != NULL && c->data_loaded == 0u && (idx = onboarding_news_scroll_find_next_unloaded_50c8cc()) >= 0 &&
        onboarding_news_scroll_load_next_available_news_50c314(c, idx) == 0u)
        NEWS_LOG(2u, fn_next, 0x6beu, 0x08400000u, preload_288, preload_288_short, idx);
    c = onboarding_news_find_container_at_50c476(NEWS_POS_NEXT2);
    if (c != NULL && c->data_loaded == 0u && (idx = onboarding_news_scroll_find_next_unloaded_50c8cc()) >= 0 &&
        onboarding_news_scroll_load_next_available_news_50c314(c, idx) == 0u)
        NEWS_LOG(2u, fn_next, 0x6cdu, 0x08400000u, preload_576, preload_576_short, idx);

    PAGE->is_switching = 1u;
    g2_onboarding_news_pending_t *p = &g2_onboarding_news_pending_20073c80;
    p->direction = 1;
    p->pending = 1u;
    for (int32_t i = 0; i < NEWS_CONTAINERS; i++) {
        g2_onboarding_news_container_t *slot = &PAGE->container[i];
        int32_t y = slot->position_y;
        if (y == NEWS_POS_CUR) {
            if (slot->data_loaded != 0u) {
                slot->flag_27 = 1u;
                onboarding_news_scroll_reset_content_position_50c6e2(slot);
            }
            p->target_y[i] = NEWS_POS_PREV;
        } else if (y == NEWS_POS_NEXT) {
            onboarding_news_scroll_reset_content_position_50c6e2(slot);
            p->target_y[i] = NEWS_POS_CUR;
        } else if (y == NEWS_POS_NEXT2) {
            p->target_y[i] = NEWS_POS_NEXT;
        } else if (y == NEWS_POS_PREV) {
            bool discard = false;
            if (slot->data_loaded != 0u && slot->flag_27 != 0u)
                discard = true;
            onboarding_news_container_reset_50c4ac(slot);
            p->target_y[i] = NEWS_POS_NEXT2;
            if (discard) {
                onboarding_news_scroll_discard_read_news_from_fifo_50c288();
                onboarding_news_scroll_sync_count_50c3c0();
            }
            idx = onboarding_news_scroll_find_next_unloaded_50c8cc();
            if (idx >= 0 && onboarding_news_scroll_load_next_available_news_50c314(slot, idx) == 0u)
                NEWS_LOG(2u, fn_next, 0x715u, 0x08400000u, load_576, load_576_short, idx);
        }
    }
    onboarding_news_container_move_with_anim_50c7a8(1, NEWS_SWITCH_ANIM_MS);
}
