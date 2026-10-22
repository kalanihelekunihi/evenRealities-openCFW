/* Onboarding stock demo page (tile widget and expanded page), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_stock_page.c
 * (log tag "onboarding.stock"). Native 0x50ca56..0x50cb27, 0x50cb28..0x50cb2f,
 * 0x50cb30..0x50d359, 0x50d35a..0x50d531, 0x50d532..0x50d541, 0x50d578..0x50d867,
 * 0x50d894..0x50daa1, 0x50dab8..0x50db1b, 0x50db34..0x50dc4b, 0x50dcbc..0x50e44d
 * (inline pool 0x50dddc), 0x50e468..0x50e489, 0x50e48a..0x50e515,
 * 0x50e534..0x50e719, 0x50e728..0x50e7dd, 0x50e7f0..0x50e85b and
 * 0x50e870..0x50e8db; literal pools 0x50cc8c (inline ""), 0x50d544..0x50d577,
 * 0x50d868..0x50d893, 0x50daa4..0x50dab7, 0x50db1c..0x50db33,
 * 0x50dc4c..0x50dcbb, 0x50e450..0x50e467, 0x50e518..0x50e533,
 * 0x50e71c..0x50e727, 0x50e7e0..0x50e7ef, 0x50e85c..0x50e86f and
 * 0x50e8dc..0x50e98f. 0x50ca24 is the LVGL header inline
 * lv_obj_set_style_pad_all emitted in this TU (upstream, not hand-written).
 *
 * Clone of the dashboard stock page (ui_stock_page.c) for the onboarding
 * feature tiles: up to nine 0x380-byte records at RAM 0x201280a0 (count
 * 0x2012a020) only gate which rows are shown; the rows always display the
 * fixed demo quotes DOW JONES 172.49 / 0.33%, QQQ 257.65 / 0.12% and
 * VOO 98.37 / 0.80% with their prerendered chart images. The tile widget is a
 * 315x254 frame in onboarding_tile_list[tile][1]; the expanded page is a
 * 539x254 frame holding three 288-px containers of three rows each. A double
 * tap at tutorial process 2 substep 6 closes the expanded page and advances
 * the tutorial to substep 7. */
#include <stdint.h>
#include <stddef.h>

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_LABEL_LONG_MODE_DOTS 1u
#define LV_TEXT_ALIGN_RIGHT 3u
#define WAIT_FOREVER 0xffffffffu

#define STOCK_MAX 9u
#define STOCK_ROWS 3
#define STOCK_CONTAINERS 3
#define CONTAINER_W 0x21b
#define CONTAINER_H 0x120
#define FRAME_H 0xfe
#define WIDGET_W 0x13b
#define MAX_TILES 6u
#define COLOR_SEPARATOR 0x222222u /* ROM 0x50daa4 / 0x50e918 */
#define COLOR_WHITE 0xffffffu

enum {
    ONB_STOCK_MSG_INPUT = 0u,
    ONB_STOCK_MSG_DATA = 1u,
};

enum {
    ONB_KEY_SCROLL_UP = 0x44,   /* 'D' */
    ONB_KEY_SCROLL_DOWN = 0x45, /* 'E' */
    ONB_KEY_REBUILD = 0x47,
    ONB_KEY_DOUBLE_TAP = 0x48,  /* 'H' */
};

/* One stock as pushed by the phone (layout of the dashboard record with a
 * shorter chart point array). */
typedef struct {
    uint8_t bytes[0x380];
} g2_onboarding_stock_record_t;
_Static_assert(sizeof(g2_onboarding_stock_record_t) == 0x380, "onboarding stock record");

typedef struct {
    void *icon;   /* lv_image */
    void *name;   /* lv_label */
    void *symbol; /* lv_label */
    void *chart;  /* lv_image */
    void *price;  /* lv_label, right aligned */
    void *change; /* lv_label, right aligned */
} g2_onboarding_stock_row_t;

typedef struct {
    void *root;                                /* +0x00 */
    g2_onboarding_stock_row_t row[STOCK_ROWS]; /* +0x04 */
    void *separator[2];                        /* +0x4c */
    int32_t position_y;                        /* +0x54 */
    uint32_t array_index;                      /* +0x58 */
    uint8_t data_loaded;                       /* +0x5c */
    uint8_t reserved_5d[3];
} g2_onboarding_stock_container_t;
_Static_assert(sizeof(g2_onboarding_stock_container_t) == 0x60, "onboarding stock container");

/* RAM 0x2006fd8c. */
typedef struct {
    g2_onboarding_stock_container_t container[STOCK_CONTAINERS]; /* +0x000 */
    uint32_t stock_count;                                        /* +0x120 */
    uint8_t is_animating;                                        /* +0x124 mgr.is_animating */
    uint8_t reserved_125[3];
    void *frame;                                                 /* +0x128 */
} g2_onboarding_stock_scroll_t;
_Static_assert(sizeof(g2_onboarding_stock_scroll_t) == 0x12c, "onboarding stock scroll");

typedef struct {
    uint8_t key;
    uint8_t process_id;
    uint8_t substep;
    uint8_t reserved;
    uint32_t value;
} g2_onboarding_key_msg_t;
_Static_assert(sizeof(g2_onboarding_key_msg_t) == 8u, "key sync record");

typedef struct {
    uint8_t process_id; /* +0 */
    uint8_t substep;    /* +1 */
    uint8_t status;     /* +2 */
} g2_onboarding_process_head_t;

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                       /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                       /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);            /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                       /* lv_obj_set_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);    /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);      /* bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);         /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);    /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel);    /* text_align */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);              /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                                  /* lv_obj_clean */
extern void *audio_lv_child_44dce2(void *obj, int32_t index);                   /* lv_obj_get_child */
extern uint32_t audio_uart_lv_child_count_44ddea(void *obj);                    /* lv_obj_get_child_count */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                   /* lv_obj_set_scrollbar_mode */
extern void *audio_uart_page_498668(void *parent);                              /* lv_image_create */
extern void audio_uart_page_498680(void *obj, const void *src);                 /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *obj, const char *text);                /* lv_label_set_text */
extern void audio_uart_page_layout_499678(void *obj, uint32_t mode);            /* lv_label_set_long_mode */
extern uint32_t audio_uart_page_460084(const char *key);                        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);     /* localized text */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
/* lv_obj_set_style_pad_all inline copy at 0x50ca24 (upstream lv_obj_style.h). */
extern void ui_onboarding_stock_sub_0050CA24(void *obj, int32_t value, uint32_t selector);

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */

extern void *ui_common_api_fn_00509c1c(void);                                        /* fifo create */
extern void ui_common_api_fn_00509c96(void *fifo);                                   /* fifo destroy */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push */

extern int32_t ui_onboarding_main_sub_004A979C(const uint8_t *raw, int32_t offset,
                                               g2_onboarding_key_msg_t *out);
extern void ui_onboarding_main_sub_004A9DE8(void);
extern void ui_onboarding_main_sub_004A9EDC(void);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* RAM state. */
extern g2_onboarding_stock_record_t g2_onboarding_stock_data_201280a0[STOCK_MAX]; /* RAM 0x201280a0 */
extern uint16_t g2_onboarding_stock_count_2012a020;          /* RAM 0x2012a020 */
extern uint8_t g2_onboarding_stock_scratch_2012a024[0x380];  /* RAM 0x2012a024 */
extern uint8_t g2_onboarding_stock_scratch_2012a3a4[0x388];  /* RAM 0x2012a3a4 */
extern g2_onboarding_stock_scroll_t g2_onboarding_stock_scroll_2006fd8c; /* RAM 0x2006fd8c */
extern int32_t g2_onboarding_stock_ext_widget_init_flag_20074dbc; /* RAM 0x20074dbc */
extern int32_t g2_onboarding_stock_is_animating_20074dc0;    /* RAM 0x20074dc0 */
extern void *g2_onboarding_stock_ext_fifo_20074dc4;          /* RAM 0x20074dc4 */
extern int32_t g2_onboarding_stock_state_20074dc8;           /* RAM 0x20074dc8 */
extern int32_t g2_onboarding_stock_container_index_20074dcc; /* RAM 0x20074dcc */
extern void *g2_onboarding_stock_widget_frame_20074dd0;      /* RAM 0x20074dd0 */
extern void *g2_onboarding_stock_expanded_frame_20074dd4;    /* RAM 0x20074dd4 */
extern void *g2_onboarding_stock_widget_objs_20074dd8[4];    /* RAM 0x20074dd8..0x20074de7 */
extern void *g2_onboarding_stock_expanded_objs_20074de8[4];  /* RAM 0x20074de8..0x20074df7 */
extern uint8_t g2_onboarding_stock_state_20073d88[0x14];     /* RAM 0x20073d88 */
extern int32_t g2_onboarding_stock_slots_200740d4[3];        /* RAM 0x200740d4 */
extern uint32_t g2_onboarding_stock_tile_index_200042bc;     /* RAM 0x200042bc (.data) */
extern void *g2_onboarding_main_obj_20074ce8;                /* RAM 0x20074ce8 feature page container */
extern void *g2_onboarding_tile_list[MAX_TILES][2];          /* RAM 0x200734ec onboarding_tile_list */
extern void *g2_onboarding_mutex;                            /* RAM 0x20074830 */
extern g2_onboarding_process_head_t g2_onboarding_process;   /* RAM 0x200f4800 */
extern const void *audio_uart_ring_primary_head_cell;        /* RAM 0x200746dc: active lv_font_t * */
extern const uint8_t g2_stock_icon_trend_1[];                /* ROM 0x7725c4 lv_image_dsc_t 24x24 */
extern const uint8_t g2_onboarding_stock_chart_dow[];        /* ROM 0x76ebe8 lv_image_dsc_t */
extern const uint8_t g2_onboarding_stock_chart_qqq[];        /* ROM 0x76ec04 lv_image_dsc_t */
extern const uint8_t g2_onboarding_stock_chart_voo[];        /* ROM 0x76ec20 lv_image_dsc_t */

static const char module_tag[] = "onboarding.stock"; /* ROM 0x78498c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\ui_onboarding_stock_page.c"; /* ROM 0x6eab58 */
static const char empty_text[] = ""; /* inline 0x50cc8c / 0x50e71c */

static const char key_dow[] = "ID_ONBOARDING_STOCK_DOW_JONES"; /* ROM 0x767890 */
static const char key_dow_detail_1[] = "ID_ONBOARDING_STOCK_DOW_DETAIL_1"; /* ROM 0x75c93c */
static const char key_dow_detail_2[] = "ID_ONBOARDING_STOCK_DOW_DETAIL_2"; /* ROM 0x75c888 */
static const char key_qqq[] = "ID_ONBOARDING_STOCK_QQQ"; /* ROM 0x77d45c */
static const char key_qqq_detail[] = "ID_ONBOARDING_STOCK_INV_QQQ_TRU"; /* ROM 0x7678b0 */
static const char key_voo[] = "ID_ONBOARDING_STOCK_VOO"; /* ROM 0x77d474 */
static const char key_voo_detail[] = "ID_ONBOARDING_STOCK_VAN_ETF"; /* ROM 0x7741fc */
static const char price_dow[] = "172.49"; /* ROM 0x78ed64 */
static const char change_dow[] = "0.33%"; /* ROM 0x78ed6c */
static const char price_qqq[] = "257.65"; /* ROM 0x78ed74 */
static const char change_qqq[] = "0.12%"; /* ROM 0x78ed7c */
static const char price_voo[] = "98.37"; /* ROM 0x78ed84 */
static const char change_voo[] = "0.80%"; /* ROM 0x78ed8c */

static const char peek_fn[] = "onboarding_stock_page_peek_data_at"; /* ROM 0x75c840 */
static const char peek_null[] = "onboarding_stock_page_peek_data_at: stock_data is NULL"; /* ROM 0x7257d0 */
static const char peek_null_short[] =
    "[onboarding.stock]onboarding_stock_page_peek_data_at: stock_data is NULL"; /* ROM 0x6f74a0 */
static const char peek_range[] = "onboarding_stock_page_peek_data_at: Index %d out of range (count: %d)"; /* ROM 0x6fece4 */
static const char peek_range_short[] =
    "[onboarding.stock]onboarding_stock_page_peek_data_at: Index %d out of range (count: %d)"; /* ROM 0x6e5928 */
static const char create_fn[] = "onboarding_stock_scroll_create_container"; /* ROM 0x746170 */
static const char create_null[] = "onboarding_stock_scroll_create_container:NULL"; /* ROM 0x73aab4 */
static const char create_null_short[] = "[onboarding.stock]onboarding_stock_scroll_create_container:NULL"; /* ROM 0x7111e4 */
static const char load_fn[] = "onboarding_stock_scroll_load_stock_data"; /* ROM 0x750af4 */
static const char load_null[] = "container is NULL"; /* ROM 0x7849a0 */
static const char load_null_short[] = "[onboarding.stock]container is NULL"; /* ROM 0x75c864 */
static const char ext_fn[] = "onboarding_stock_ext_event_handler"; /* ROM 0x75c8ac */
static const char ext_off[] = "onboarding_stock_ext_widget_init_flag == 0, return"; /* ROM 0x730168 */
static const char ext_off_short[] = "[onboarding.stock]onboarding_stock_ext_widget_init_flag == 0, return"; /* ROM 0x6fed2c */
static const char ext_bad[] = "Invalid parameters"; /* ROM 0x7849b4 */
static const char ext_bad_short[] = "[onboarding.stock]Invalid parameters"; /* ROM 0x750b1c */
static const char ext_busy[] =
    "stock_Animation in progress (onboarding_stock_is_animating=%d, mgr.is_animating=%d), handling event code=%d"; /* ROM 0x6d7f54 */
static const char ext_busy_short[] =
    "[onboarding.stock]stock_Animation in progress (onboarding_stock_is_animating=%d, mgr.is_animating=%d), handling event code=%d"; /* ROM 0x6d5cd8 */
static const char ext_ignored[] = "stock Scroll event ignored during animation, code = %d"; /* ROM 0x725808 */
static const char ext_ignored_short[] = "[onboarding.stock]stock Scroll event ignored during animation, code = %d"; /* ROM 0x6f74ec */
static const char ext_queued[] = "stock Non-scroll event queued to fifo, code = %d"; /* ROM 0x73019c */
static const char ext_queued_short[] = "[onboarding.stock]stock Non-scroll event queued to fifo, code = %d"; /* ROM 0x707dbc */
static const char ext_data[] = "onboarding_stock_ext_event_handler: Stock data update event received"; /* ROM 0x6fed74 */
static const char ext_data_short[] =
    "[onboarding.stock]onboarding_stock_ext_event_handler: Stock data update event received"; /* ROM 0x6e5980 */
static const char init_fn[] = "onboarding_stock_ext_Widget_init"; /* ROM 0x75c8d0 */
static const char init_null[] = "parent_obj is NULL"; /* ROM 0x7849c8 */
static const char init_null_short[] = "[onboarding.stock]parent_obj is NULL"; /* ROM 0x750b44 */
static const char init_fifo_failed[] = "onboarding_stock_ext_fifo create failed"; /* ROM 0x750b6c */
static const char init_fifo_failed_short[] = "[onboarding.stock]onboarding_stock_ext_fifo create failed"; /* ROM 0x71ac50 */
static const char init_frame_failed[] = "Failed to create container frame"; /* ROM 0x75c8f4 */
static const char init_frame_failed_short[] = "[onboarding.stock]Failed to create container frame"; /* ROM 0x7301d0 */
static const char init_ok[] = "Stock extension widget initialized with %d stocks"; /* ROM 0x730204 */
static const char init_ok_short[] = "[onboarding.stock]Stock extension widget initialized with %d stocks"; /* ROM 0x707e00 */
static const char reflash_fn[] = "Onboarding_Stock_Page_Reflash"; /* ROM 0x7678d0 */
static const char reflash_null[] = "onboarding_Stock_Page_Reflash data is NULL"; /* ROM 0x74619c */
static const char reflash_null_short[] = "[onboarding.stock]onboarding_Stock_Page_Reflash data is NULL"; /* ROM 0x711224 */
static const char reflash_index[] = "Invalid onboarding_stock_tilelist_index: %d"; /* ROM 0x7461c8 */
static const char reflash_index_short[] = "[onboarding.stock]Invalid onboarding_stock_tilelist_index: %d"; /* ROM 0x711264 */
static const char main_fn[] = "Onboarding_StockWidget_MainPage_init"; /* ROM 0x750b94 */
static const char main_index[] = "Invalid index %d, must be 0-5"; /* ROM 0x7678f0 */
static const char main_index_short[] = "[onboarding.stock]Invalid index %d, must be 0-5"; /* ROM 0x73aae4 */
static const char main_tile_null[] = "onboarding_tile_list[%d][1] is NULL"; /* ROM 0x75c918 */
static const char main_tile_null_short[] = "[onboarding.stock]onboarding_tile_list[%d][1] is NULL"; /* ROM 0x725840 */
static const char main_frame_failed[] = "stock Failed to create container frame"; /* ROM 0x750bbc */
static const char main_frame_failed_short[] = "[onboarding.stock]stock Failed to create container frame"; /* ROM 0x71ac8c */
static const char sep_fn[] = "onboarding_update_separator_lines_visibility"; /* ROM 0x73ab14 */
static const char sep_null[] = "onboarding_update_separator_lines_visibility: container is NULL"; /* ROM 0x7112a4 */
static const char sep_null_short[] =
    "[onboarding.stock]onboarding_update_separator_lines_visibility: container is NULL"; /* ROM 0x6eabac */
static const char expanded_fn[] = "onboarding_stock_switch_to_expanded_container"; /* ROM 0x73ab44 */
static const char expanded_null[] =
    "onboarding_stock_switch_to_expanded_container: Expanded container frame pointer is NULL"; /* ROM 0x6e59d8 */
static const char expanded_null_short[] =
    "[onboarding.stock]onboarding_stock_switch_to_expanded_container: Expanded container frame pointer is NULL"; /* ROM 0x6d7fc0 */
static const char widget_fn[] = "onboarding_stock_switch_to_widget_container"; /* ROM 0x7461f4 */
static const char widget_null[] =
    "onboarding_stock_switch_to_widget_container: Widget container frame pointer is NULL"; /* ROM 0x6eac00 */
static const char widget_null_short[] =
    "[onboarding.stock]onboarding_stock_switch_to_widget_container: Widget container frame pointer is NULL"; /* ROM 0x6d9b7c */

/* Demo rows: name key, detail key (widget / expanded page), price, change. */
typedef struct {
    const char *name_key;
    const char *widget_detail_key;
    const char *page_detail_key;
    const char *price;
    const char *change;
    const uint8_t *chart;
} demo_row_t;

static const demo_row_t demo_rows[STOCK_ROWS] = {
    {key_dow, key_dow_detail_1, key_dow_detail_2, price_dow, change_dow, g2_onboarding_stock_chart_dow},
    {key_qqq, key_qqq_detail, key_qqq_detail, price_qqq, change_qqq, g2_onboarding_stock_chart_qqq},
    {key_voo, key_voo_detail, key_voo_detail, price_voo, change_voo, g2_onboarding_stock_chart_voo},
};

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

static void log0(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 0), msg_short, msg_short);
}

static void log1(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 1), msg_short, msg_short, a);
}

static void log2(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a, uint32_t b)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a, b);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 2), msg_short, msg_short, a, b);
}

static void log3(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a, uint32_t b, uint32_t c)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a, b, c);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 3), msg_short, msg_short, a, b, c);
}

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

uint32_t ui_onboarding_stock_sub_0050CA56(g2_onboarding_stock_record_t *out, uint16_t index);
uint16_t ui_onboarding_stock_sub_0050CB28(void);
void ui_onboarding_stock_sub_0050CB30(g2_onboarding_stock_container_t *c, void *parent, int32_t position_y,
                                      uint32_t array_index);
void ui_onboarding_stock_sub_0050D35A(g2_onboarding_stock_container_t *c, int32_t index);
void ui_onboarding_stock_sub_0050D532(void);
int32_t ui_onboarding_stock_sub_0050D578(const uint8_t *data, uint32_t len);
int32_t ui_onboarding_stock_sub_0050D894(void *parent);
void ui_onboarding_stock_sub_0050DAB8(void);
int32_t ui_onboarding_stock_sub_0050DB34(const uint8_t *data, uint32_t len);
int32_t ui_onboarding_stock_sub_0050DCBC(uint32_t tile_index);
int32_t ui_onboarding_stock_sub_0050E468(int32_t index);
void ui_onboarding_stock_sub_0050E48A(g2_onboarding_stock_container_t *c, int32_t index);
void ui_onboarding_stock_sub_0050E534(void);
void ui_onboarding_stock_sub_0050E728(void);
void ui_onboarding_stock_sub_0050E7F0(void);
void ui_onboarding_stock_sub_0050E870(void);

/* onboarding_stock_page_peek_data_at: copies record index into out.
 * Returns 1, or 0 for NULL out / index >= count. */
uint32_t ui_onboarding_stock_sub_0050CA56(g2_onboarding_stock_record_t *out, uint16_t index)
{
    if (out == NULL) {
        log0(1u, peek_fn, 0xbbu, peek_null, peek_null_short);
        return 0u;
    }
    if (index >= g2_onboarding_stock_count_2012a020) {
        log2(2u, peek_fn, 0xc0u, peek_range, peek_range_short, index, g2_onboarding_stock_count_2012a020);
        return 0u;
    }
    (void)audio_queue_copy_bytes(out, &g2_onboarding_stock_data_201280a0[index], sizeof(*out));
    return 1u;
}

/* onboarding_stock_page_get_count. */
uint16_t ui_onboarding_stock_sub_0050CB28(void)
{
    return g2_onboarding_stock_count_2012a020;
}

static void *create_image(void *parent, int32_t w, int32_t h, int32_t x, int32_t y)
{
    void *img = audio_uart_page_498668(parent);

    audio_uart_page_43f506(img, w);
    audio_uart_page_43f568(img, h);
    audio_uart_page_43f0e0(img, x);
    audio_uart_page_43f142(img, y);
    audio_uart_page_44129e(img, 0u, 0u);
    audio_uart_page_44131c(img, 0, 0u);
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    return img;
}

static void *create_label(void *parent, int32_t w, int32_t h, int32_t x, int32_t y)
{
    void *label = audio_uart_page_499416(parent);

    audio_uart_page_43f506(label, w);
    audio_uart_page_43f568(label, h);
    audio_uart_page_43f0e0(label, x);
    audio_uart_page_43f142(label, y);
    return label;
}

static void *create_separator(void *parent, int32_t w, int32_t y)
{
    void *line = audio_uart_page_43de82(parent);

    audio_uart_page_43f506(line, w);
    audio_uart_page_43f568(line, 1);
    audio_uart_page_43f0e0(line, 0);
    audio_uart_page_43f142(line, y);
    audio_uart_page_44127e(line, audio_uart_page_44104c(COLOR_SEPARATOR), 0u);
    audio_uart_page_44129e(line, 0xffu, 0u);
    audio_uart_page_44131c(line, 0, 0u);
    ui_onboarding_stock_sub_0050CA24(line, 0, 0u);
    return line;
}

/* onboarding_stock_scroll_create_container: one 539x288 container of three
 * empty rows (stock code fully unrolled; rows are 0x60 apart, the icon of
 * row 0 sits one pixel higher). */
void ui_onboarding_stock_sub_0050CB30(g2_onboarding_stock_container_t *c, void *parent, int32_t position_y,
                                      uint32_t array_index)
{
    static const int32_t icon_y[STOCK_ROWS] = {2, 99, 0xc3};
    int32_t r;

    if (c == NULL || parent == NULL) {
        log0(1u, create_fn, 0xffu, create_null, create_null_short);
        return;
    }
    c->array_index = array_index;
    c->position_y = position_y;
    c->root = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(c->root, CONTAINER_W);
    audio_uart_page_43f568(c->root, CONTAINER_H);
    audio_uart_page_43f0e0(c->root, 0);
    audio_uart_page_43f142(c->root, position_y);
    audio_uart_page_44129e(c->root, 0u, 0u);
    audio_uart_page_44131c(c->root, 0, 0u);
    ui_onboarding_stock_sub_0050CA24(c->root, 0, 0u);

    for (r = 0; r < STOCK_ROWS; r++) {
        g2_onboarding_stock_row_t *row = &c->row[r];
        int32_t y = r * 0x60;

        row->icon = create_image(c->root, 0x18, 0x18, 0, icon_y[r]);

        row->name = create_label(c->root, 0xdc, 0x1c, 0x20, y);
        audio_uart_page_44143e(row->name, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(row->name, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_44129e(row->name, 0u, 0u);
        audio_uart_page_44131c(row->name, 0, 0u);
        audio_uart_page_layout_499678(row->name, LV_LABEL_LONG_MODE_DOTS);
        audio_uart_page_49942e(row->name, empty_text);

        row->symbol = create_label(c->root, 0xfc, 0x1c, 0, y + 0x22);
        audio_uart_page_44143e(row->symbol, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44129e(row->symbol, 0u, 0u);
        audio_uart_page_44131c(row->symbol, 0, 0u);
        audio_uart_page_44140e(row->symbol, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_layout_499678(row->symbol, LV_LABEL_LONG_MODE_DOTS);
        audio_uart_page_49942e(row->symbol, empty_text);

        row->chart = create_image(c->root, 0x84, 0x3e, 0x10c, y);

        row->price = create_label(c->root, 0x84, 0x1c, 0x197, y);
        audio_uart_page_44145a(row->price, LV_TEXT_ALIGN_RIGHT, 0u);
        audio_uart_page_44143e(row->price, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(row->price, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_44129e(row->price, 0u, 0u);
        audio_uart_page_44131c(row->price, 0, 0u);
        audio_uart_page_49942e(row->price, empty_text);

        row->change = create_label(c->root, 0x5d, 0x1c, 0x1be, y + 0x22);
        audio_uart_page_44145a(row->change, LV_TEXT_ALIGN_RIGHT, 0u);
        audio_uart_page_44143e(row->change, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(row->change, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_44129e(row->change, 0u, 0u);
        audio_uart_page_44131c(row->change, 0, 0u);
        audio_uart_page_49942e(row->change, empty_text);
    }
    c->separator[0] = create_separator(c->root, 0x218, 0x4f);
    c->separator[1] = create_separator(c->root, 0x218, 0xaf);
    c->data_loaded = 0u;
}

/* onboarding_stock_scroll_load_stock_data: rows 3*index .. 3*index+2 that
 * have a record get the fixed demo quote of their row. */
void ui_onboarding_stock_sub_0050D35A(g2_onboarding_stock_container_t *c, int32_t index)
{
    g2_onboarding_stock_record_t rec[STOCK_ROWS];
    int32_t r;

    if (c == NULL) {
        log0(1u, load_fn, 0x21au, load_null, load_null_short);
        return;
    }
    for (r = 0; r < STOCK_ROWS; r++) {
        g2_onboarding_stock_row_t *row = &c->row[r];
        const demo_row_t *demo = &demo_rows[r];
        int32_t si = index * 3 + r;

        if (si >= (int32_t)ui_onboarding_stock_sub_0050CB28() ||
            ui_onboarding_stock_sub_0050CA56(&rec[r], (uint16_t)si) == 0u)
            continue;
        audio_uart_page_498680(row->icon, g2_stock_icon_trend_1);
        audio_uart_page_49942e(row->name, localized(demo->name_key));
        audio_uart_page_49942e(row->symbol, localized(demo->page_detail_key));
        audio_uart_page_49942e(row->price, demo->price);
        audio_uart_page_49942e(row->change, demo->change);
        audio_uart_page_498680(row->chart, demo->chart);
    }
    ui_onboarding_stock_sub_0050E48A(c, index);
    c->data_loaded = 1u;
}

/* onboarding_stock_scroll_sync_count. */
void ui_onboarding_stock_sub_0050D532(void)
{
    g2_onboarding_stock_scroll_2006fd8c.stock_count = ui_onboarding_stock_sub_0050CB28();
}

/* onboarding_stock_ext_event_handler: byte 0 selects an input record (0,
 * key record in bytes 1..7) or a data update notice (1). While an animation
 * runs, scroll keys are dropped and other keys are queued. Returns 0, or -1
 * for bad parameters / an undecodable record. */
int32_t ui_onboarding_stock_sub_0050D578(const uint8_t *data, uint32_t len)
{
    g2_onboarding_key_msg_t msg;
    int32_t i;

    if (g2_onboarding_stock_ext_widget_init_flag_20074dbc == 0) {
        log0(2u, ext_fn, 0x461u, ext_off, ext_off_short);
        return 0;
    }
    if (data == NULL || len == 0u) {
        log0(1u, ext_fn, 0x466u, ext_bad, ext_bad_short);
        return -1;
    }
    if (data[0] == ONB_STOCK_MSG_INPUT) {
        if (ui_onboarding_main_sub_004A979C(data, 1, &msg) != 0)
            return -1;
        if (g2_onboarding_stock_is_animating_20074dc0 != 0 ||
            g2_onboarding_stock_scroll_2006fd8c.is_animating != 0u) {
            log3(3u, ext_fn, 0x479u, ext_busy, ext_busy_short, (uint32_t)g2_onboarding_stock_is_animating_20074dc0,
                 g2_onboarding_stock_scroll_2006fd8c.is_animating, msg.key);
            if (msg.key == ONB_KEY_SCROLL_UP || msg.key == ONB_KEY_SCROLL_DOWN) {
                log1(3u, ext_fn, 0x47eu, ext_ignored, ext_ignored_short, msg.key);
                return 0;
            }
            if (g2_onboarding_stock_ext_fifo_20074dc4 != NULL) {
                (void)ui_common_api_fn_00509ca2(g2_onboarding_stock_ext_fifo_20074dc4, data + 1, 7u);
                log1(3u, ext_fn, 0x485u, ext_queued, ext_queued_short, msg.key);
            }
            return 0;
        }
        if (msg.process_id == 2u && msg.substep == 6u && msg.key == ONB_KEY_DOUBLE_TAP) {
            (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
            g2_onboarding_process.substep = 7u;
            (void)osMutexRelease(g2_onboarding_mutex);
            ui_onboarding_main_sub_004A9EDC();
            i = (int32_t)audio_uart_lv_child_count_44ddea(g2_onboarding_main_obj_20074ce8);
            while (--i >= 0) {
                void *child = audio_lv_child_44dce2(g2_onboarding_main_obj_20074ce8, i);

                if (child != NULL)
                    audio_uart_page_delete_event_filter_44d7b8(child);
            }
            if (g2_onboarding_stock_ext_fifo_20074dc4 != NULL) {
                ui_common_api_fn_00509c96(g2_onboarding_stock_ext_fifo_20074dc4);
                g2_onboarding_stock_ext_fifo_20074dc4 = NULL;
            }
            g2_onboarding_stock_ext_widget_init_flag_20074dbc = 0;
            g2_onboarding_stock_is_animating_20074dc0 = 0;
            ui_onboarding_main_sub_004A9DE8();
        }
    } else if (data[0] == ONB_STOCK_MSG_DATA) {
        log0(3u, ext_fn, 0x50fu, ext_data, ext_data_short);
    }
    return 0;
}

/* onboarding_stock_ext_Widget_init: builds the expanded page in parent
 * scrolled to the current container index. Returns 0, or -1 on failure. */
int32_t ui_onboarding_stock_sub_0050D894(void *parent)
{
    g2_onboarding_stock_scroll_t *m = &g2_onboarding_stock_scroll_2006fd8c;
    void *frame;
    int32_t base;

    if (parent == NULL) {
        log0(1u, init_fn, 0x522u, init_null, init_null_short);
        return -1;
    }
    if (g2_onboarding_stock_ext_fifo_20074dc4 != NULL) {
        ui_common_api_fn_00509c96(g2_onboarding_stock_ext_fifo_20074dc4);
        g2_onboarding_stock_ext_fifo_20074dc4 = NULL;
    }
    g2_onboarding_stock_ext_fifo_20074dc4 = ui_common_api_fn_00509c1c();
    if (g2_onboarding_stock_ext_fifo_20074dc4 == NULL) {
        log0(1u, init_fn, 0x52du, init_fifo_failed, init_fifo_failed_short);
        return -1;
    }
    g2_onboarding_stock_expanded_frame_20074dd4 = audio_uart_page_43de82(parent);
    if (g2_onboarding_stock_expanded_frame_20074dd4 == NULL) {
        log0(1u, init_fn, 0x534u, init_frame_failed, init_frame_failed_short);
        return -1;
    }
    frame = g2_onboarding_stock_expanded_frame_20074dd4;
    m->frame = frame;
    audio_uart_page_43f09a(frame, 0x14, 0x11);
    audio_uart_page_43f4c0(frame, CONTAINER_W, FRAME_H);
    audio_uart_page_44129e(frame, 0u, 0u);
    audio_uart_page_44129e(frame, 0u, 0u);
    audio_uart_page_44131c(frame, 0, 0u);
    ui_onboarding_stock_sub_0050CA24(frame, 0, 0u);
    audio_uart_page_44e368(frame, LV_SCROLLBAR_MODE_OFF);
    base = -CONTAINER_H * g2_onboarding_stock_container_index_20074dcc; /* ROM 0x50dc50 = -288 */
    ui_onboarding_stock_sub_0050CB30(&m->container[0], frame, base, 0u);
    ui_onboarding_stock_sub_0050CB30(&m->container[1], frame, base + CONTAINER_H, 1u);
    ui_onboarding_stock_sub_0050CB30(&m->container[2], frame, base + 2 * CONTAINER_H, 2u);
    m->is_animating = 0u;
    ui_onboarding_stock_sub_0050D532();
    ui_onboarding_stock_sub_0050D35A(&m->container[0], 0);
    g2_onboarding_stock_ext_widget_init_flag_20074dbc = 1;
    ui_onboarding_stock_sub_0050E7F0();
    log1(3u, init_fn, 0x579u, init_ok, init_ok_short, ui_onboarding_stock_sub_0050CB28());
    return 0;
}

/* Closes the expanded page: clears its state, deletes the feature page
 * children and rebuilds the stock tile widget. */
void ui_onboarding_stock_sub_0050DAB8(void)
{
    int32_t i;

    if (g2_onboarding_main_obj_20074ce8 == NULL)
        return;
    ui_onboarding_stock_sub_0050E534();
    i = (int32_t)audio_uart_lv_child_count_44ddea(g2_onboarding_main_obj_20074ce8);
    while (--i >= 0) {
        void *child = audio_lv_child_44dce2(g2_onboarding_main_obj_20074ce8, i);

        if (child != NULL)
            audio_uart_page_delete_event_filter_44d7b8(child);
    }
    ui_onboarding_stock_sub_0050E728();
    ui_onboarding_stock_sub_0050E870();
    if (g2_onboarding_stock_tile_index_200042bc < MAX_TILES) {
        if (g2_onboarding_tile_list[g2_onboarding_stock_tile_index_200042bc][1] != NULL)
            audio_uart_page_44d878(g2_onboarding_tile_list[g2_onboarding_stock_tile_index_200042bc][1]);
        (void)ui_onboarding_stock_sub_0050DCBC(g2_onboarding_stock_tile_index_200042bc);
    }
}

/* Onboarding_Stock_Page_Reflash: rebuilds the tile widget and, when the
 * expanded page is open, the expanded page (deferred as a queued 0x47 key
 * while an animation runs). The data bytes are not read. */
int32_t ui_onboarding_stock_sub_0050DB34(const uint8_t *data, uint32_t len)
{
    uint8_t rebuild[5];

    (void)len;
    if (data == NULL) {
        log0(1u, reflash_fn, 0x60au, reflash_null, reflash_null_short);
        return -1;
    }
    if (g2_onboarding_stock_tile_index_200042bc < MAX_TILES) {
        if (g2_onboarding_tile_list[g2_onboarding_stock_tile_index_200042bc][1] != NULL)
            audio_uart_page_44d878(g2_onboarding_tile_list[g2_onboarding_stock_tile_index_200042bc][1]);
        (void)ui_onboarding_stock_sub_0050DCBC(g2_onboarding_stock_tile_index_200042bc);
    } else {
        log1(2u, reflash_fn, 0x61du, reflash_index, reflash_index_short, g2_onboarding_stock_tile_index_200042bc);
    }
    if (g2_onboarding_stock_ext_widget_init_flag_20074dbc == 1 && g2_onboarding_stock_ext_fifo_20074dc4 != NULL &&
        g2_onboarding_main_obj_20074ce8 != NULL) {
        if (g2_onboarding_stock_is_animating_20074dc0 == 0) {
            audio_uart_page_44d878(g2_onboarding_main_obj_20074ce8);
            (void)ui_onboarding_stock_sub_0050D894(g2_onboarding_main_obj_20074ce8);
        } else {
            rebuild[0] = ONB_KEY_REBUILD;
            rebuild[1] = 0u;
            rebuild[2] = 0u;
            rebuild[3] = 0u;
            rebuild[4] = 0u;
            (void)ui_common_api_fn_00509ca2(g2_onboarding_stock_ext_fifo_20074dc4, rebuild, sizeof(rebuild));
        }
    }
    return 0;
}

/* Onboarding_StockWidget_MainPage_init: draws the 315x254 tile widget of
 * the current container (up to three demo rows plus separators) into
 * onboarding_tile_list[tile][1]. Returns 0, or -1 on failure. */
int32_t ui_onboarding_stock_sub_0050DCBC(uint32_t tile_index)
{
    static const int32_t icon_y[STOCK_ROWS] = {3, 99, 0xc3};
    void *frame;
    void *sep0;
    void *sep1;
    int32_t ci;
    int32_t n;
    int32_t r;

    g2_onboarding_stock_tile_index_200042bc = tile_index;
    if (g2_onboarding_stock_tile_index_200042bc >= MAX_TILES) {
        log1(1u, main_fn, 0x673u, main_index, main_index_short, g2_onboarding_stock_tile_index_200042bc);
        return -1;
    }
    if (g2_onboarding_tile_list[g2_onboarding_stock_tile_index_200042bc][1] == NULL) {
        log1(1u, main_fn, 0x679u, main_tile_null, main_tile_null_short, g2_onboarding_stock_tile_index_200042bc);
        return -1;
    }
    g2_onboarding_stock_widget_frame_20074dd0 =
        audio_uart_page_43de82(g2_onboarding_tile_list[g2_onboarding_stock_tile_index_200042bc][1]);
    if (g2_onboarding_stock_widget_frame_20074dd0 == NULL) {
        log0(1u, main_fn, 0x681u, main_frame_failed, main_frame_failed_short);
        return -1;
    }
    frame = g2_onboarding_stock_widget_frame_20074dd0;
    audio_uart_page_43f09a(frame, 0x14, 0x10);
    audio_uart_page_43f4c0(frame, WIDGET_W, FRAME_H);
    audio_uart_page_44129e(frame, 0u, 0u);
    audio_uart_page_44131c(frame, 0, 0u);
    ui_onboarding_stock_sub_0050CA24(frame, 0, 0u);
    audio_uart_page_44e368(frame, LV_SCROLLBAR_MODE_OFF);

    ci = g2_onboarding_stock_container_index_20074dcc;
    for (r = 0; r < STOCK_ROWS; r++) {
        const demo_row_t *demo = &demo_rows[r];
        int32_t y = r * 0x60;
        void *icon;
        void *label;

        if (ci * 3 + r >= (int32_t)g2_onboarding_stock_count_2012a020)
            continue;
        icon = audio_uart_page_498668(frame);
        audio_uart_page_43f506(icon, 0x18);
        audio_uart_page_43f568(icon, 0x18);
        audio_uart_page_43f0e0(icon, 0);
        audio_uart_page_43f142(icon, icon_y[r]);
        audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
        audio_uart_page_498680(icon, g2_stock_icon_trend_1);

        label = create_label(frame, 0x9c, 0x1c, 0x20, y);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_49942e(label, localized(demo->name_key));

        label = create_label(frame, 0x7e, 0x1c, 0xbd, y);
        audio_uart_page_44145a(label, LV_TEXT_ALIGN_RIGHT, 0u);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_49942e(label, demo->price);

        label = create_label(frame, 0xf0, 0x1c, 0, y + 0x22);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_49942e(label, localized(demo->widget_detail_key));

        label = create_label(frame, 0x50, 0x1c, 0xeb, y + 0x22);
        audio_uart_page_44145a(label, LV_TEXT_ALIGN_RIGHT, 0u);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_49942e(label, demo->change);
    }
    n = ui_onboarding_stock_sub_0050E468(ci);
    sep0 = create_separator(frame, 0x138, 0x4f);
    sep1 = create_separator(frame, 0x138, 0xaf);
    if (n < 2)
        audio_uart_page_43ded4(sep0, LV_OBJ_FLAG_HIDDEN);
    if (n < 3)
        audio_uart_page_43ded4(sep1, LV_OBJ_FLAG_HIDDEN);
    return 0;
}

/* onboarding_calculate_stocks_in_container: rows (0..3) shown by container index. */
int32_t ui_onboarding_stock_sub_0050E468(int32_t index)
{
    int32_t count = ui_onboarding_stock_sub_0050CB28();
    int32_t i = index * 3;
    int32_t end = i + 3;
    int32_t n = 0;

    for (; i < end && i < count; i++)
        n++;
    return n;
}

/* onboarding_update_separator_lines_visibility. */
void ui_onboarding_stock_sub_0050E48A(g2_onboarding_stock_container_t *c, int32_t index)
{
    int32_t n;

    if (c == NULL) {
        log0(1u, sep_fn, 0x86au, sep_null, sep_null_short);
        return;
    }
    n = ui_onboarding_stock_sub_0050E468(index);
    if (c->separator[0] != NULL) {
        if (n < 2)
            audio_uart_page_43ded4(c->separator[0], LV_OBJ_FLAG_HIDDEN);
        else
            audio_uart_page_43dfa4(c->separator[0], LV_OBJ_FLAG_HIDDEN);
    }
    if (c->separator[1] != NULL) {
        if (n < 3)
            audio_uart_page_43ded4(c->separator[1], LV_OBJ_FLAG_HIDDEN);
        else
            audio_uart_page_43dfa4(c->separator[1], LV_OBJ_FLAG_HIDDEN);
    }
}

/* onboarding_stock_ext_page_cleanup: detaches every row object (image
 * sources NULL, label texts "") and forgets the expanded page. */
void ui_onboarding_stock_sub_0050E534(void)
{
    g2_onboarding_stock_scroll_t *m = &g2_onboarding_stock_scroll_2006fd8c;
    int32_t i;
    int32_t r;

    for (i = 0; i < STOCK_CONTAINERS; i++) {
        g2_onboarding_stock_container_t *c = &m->container[i];

        for (r = 0; r < STOCK_ROWS; r++) {
            g2_onboarding_stock_row_t *row = &c->row[r];

            if (row->icon != NULL) {
                audio_uart_page_498680(row->icon, NULL);
                row->icon = NULL;
            }
            if (row->name != NULL) {
                audio_uart_page_49942e(row->name, empty_text);
                row->name = NULL;
            }
            if (row->symbol != NULL) {
                audio_uart_page_49942e(row->symbol, empty_text);
                row->symbol = NULL;
            }
            if (row->chart != NULL) {
                audio_uart_page_498680(row->chart, NULL);
                row->chart = NULL;
            }
            if (row->price != NULL) {
                audio_uart_page_49942e(row->price, empty_text);
                row->price = NULL;
            }
            if (row->change != NULL) {
                audio_uart_page_49942e(row->change, empty_text);
                row->change = NULL;
            }
        }
        if (c->separator[0] != NULL)
            c->separator[0] = NULL;
        if (c->separator[1] != NULL)
            c->separator[1] = NULL;
        if (c->root != NULL)
            c->root = NULL;
        c->data_loaded = 0u;
        c->position_y = 0;
        c->array_index = 0u;
    }
    if (m->frame != NULL)
        m->frame = NULL;
    if (g2_onboarding_stock_expanded_frame_20074dd4 != NULL)
        g2_onboarding_stock_expanded_frame_20074dd4 = NULL;
    for (i = 0; i < 4; i++)
        g2_onboarding_stock_expanded_objs_20074de8[i] = NULL;
    m->is_animating = 0u;
    m->stock_count = 0u;
    g2_onboarding_stock_state_20074dc8 = 0;
    (void)aeabi_memset_43c0e4(g2_onboarding_stock_state_20073d88, sizeof(g2_onboarding_stock_state_20073d88), 0);
    g2_onboarding_stock_ext_widget_init_flag_20074dbc = 0;
}

/* onboarding_stock_page_reset_state. */
void ui_onboarding_stock_sub_0050E728(void)
{
    g2_onboarding_stock_scroll_t *m = &g2_onboarding_stock_scroll_2006fd8c;
    int32_t i;

    for (i = 0; i < STOCK_CONTAINERS; i++) {
        m->container[i].data_loaded = 0u;
        m->container[i].position_y = 0;
        m->container[i].array_index = 0u;
    }
    m->is_animating = 0u;
    m->stock_count = 0u;
    g2_onboarding_stock_state_20074dc8 = 0;
    (void)aeabi_memset_43c0e4(g2_onboarding_stock_state_20073d88, sizeof(g2_onboarding_stock_state_20073d88), 0);
    g2_onboarding_stock_is_animating_20074dc0 = 0;
    for (i = 0; i < 3; i++)
        g2_onboarding_stock_slots_200740d4[i] = 0;
    g2_onboarding_stock_ext_widget_init_flag_20074dbc = 0;
    (void)aeabi_memset_43c0e4(g2_onboarding_stock_scratch_2012a024, sizeof(g2_onboarding_stock_scratch_2012a024), 0);
    (void)aeabi_memset_43c0e4(g2_onboarding_stock_scratch_2012a3a4, sizeof(g2_onboarding_stock_scratch_2012a3a4), 0);
    if (g2_onboarding_stock_widget_frame_20074dd0 != NULL)
        g2_onboarding_stock_widget_frame_20074dd0 = NULL;
    for (i = 0; i < 4; i++)
        g2_onboarding_stock_widget_objs_20074dd8[i] = NULL;
    if (g2_onboarding_stock_ext_fifo_20074dc4 != NULL) {
        ui_common_api_fn_00509c96(g2_onboarding_stock_ext_fifo_20074dc4);
        g2_onboarding_stock_ext_fifo_20074dc4 = NULL;
    }
}

/* onboarding_stock_switch_to_expanded_container: forgets the tile widget. */
void ui_onboarding_stock_sub_0050E7F0(void)
{
    int32_t i;

    if (g2_onboarding_stock_widget_frame_20074dd0 != NULL)
        g2_onboarding_stock_widget_frame_20074dd0 = NULL;
    for (i = 0; i < 4; i++)
        g2_onboarding_stock_widget_objs_20074dd8[i] = NULL;
    if (g2_onboarding_stock_expanded_frame_20074dd4 == NULL)
        log0(2u, expanded_fn, 0x978u, expanded_null, expanded_null_short);
}

/* onboarding_stock_switch_to_widget_container: forgets the expanded page. */
void ui_onboarding_stock_sub_0050E870(void)
{
    int32_t i;

    if (g2_onboarding_stock_expanded_frame_20074dd4 != NULL)
        g2_onboarding_stock_expanded_frame_20074dd4 = NULL;
    for (i = 0; i < 4; i++)
        g2_onboarding_stock_expanded_objs_20074de8[i] = NULL;
    if (g2_onboarding_stock_widget_frame_20074dd0 == NULL)
        log0(2u, widget_fn, 0x994u, widget_null, widget_null_short);
}
