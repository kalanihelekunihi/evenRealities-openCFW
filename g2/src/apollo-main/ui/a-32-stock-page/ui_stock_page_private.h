/* Shared declarations for the a-32 reconstruction of
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_stock_page.c
 * (ui_stock_page.c and ui_stock_page_fp.c in this directory). */
#ifndef G2_A32_UI_STOCK_PAGE_PRIVATE_H
#define G2_A32_UI_STOCK_PAGE_PRIVATE_H

#include <stdint.h>
#include <stddef.h>

#define STOCK_TILE_COUNT 6u      /* dashboard tiles, "Invalid index %d, must be 0-5" */
#define STOCK_MAX 9u             /* stock records kept for the UI */
#define STOCKS_PER_CONTAINER 3   /* stocks shown per non-expanded page */
#define STOCK_PAGE_DOTS_MAX 3u

/* LVGL 9.3 constants used by this page. */
#define LV_OBJ_FLAG_HIDDEN 0x00001u
#define LV_OBJ_FLAG_CLICKABLE 0x00002u
#define LV_OBJ_FLAG_SCROLLABLE 0x00010u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_TEXT_ALIGN_LEFT 1u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_TEXT_ALIGN_RIGHT 3u
#define LV_LABEL_LONG_DOT 1u
#define LV_OPA_COVER 0xffu
#define LV_COORD_MAX 0x1fffffff
#define LV_SIZE_CONTENT 0x3fffffff

#define STOCK_WHITE 0xffffffu
#define STOCK_GREY 0x222222u /* ROM 0x4ed6c0 */

/* One stock as kept for the UI (0x428 bytes, filled by dashboard_async_update_data). */
typedef struct {
    char code[0x40];          /* +0x000 ticker, first row left */
    char name[0x40];          /* +0x040 */
    char company[0x80];       /* +0x080 second row left */
    /* +0x100: copy of the 0x40-byte numeric block of the phone package
     * (parsed package +0xf30); only the fields read here are named. */
    uint8_t values_100[8];    /* +0x100 */
    float change_percent;     /* +0x108 price_change_percent */
    float current_price;      /* +0x10c current_price */
    uint8_t values_110[0x24]; /* +0x110 day_high, day_low, open_price, ... */
    int32_t changing_trend;   /* +0x134 1 / 2 / other select the trend icon */
    uint8_t values_138[8];    /* +0x138 */
    uint8_t points[0x2e8];    /* +0x140 chart points used by the expanded page */
} g2_stock_record_t;
_Static_assert(sizeof(g2_stock_record_t) == 0x428u, "stock record");
_Static_assert(offsetof(g2_stock_record_t, changing_trend) == 0x134u, "trend offset");

/* Stock UI copy (RAM 0x201308dc): nine records then the u16 stock count. */
typedef struct {
    g2_stock_record_t stock[STOCK_MAX]; /* +0x0000 */
    uint16_t stock_num;                 /* +0x2568 (RAM 0x20132e44) */
} g2_stock_page_data_t;
_Static_assert(offsetof(g2_stock_page_data_t, stock_num) == 0x2568u, "stock count at 0x20132e44");

/* Expanded ("ext") stock page state (RAM 0x20132e48). Only the fields this
 * segment touches are named; update_separator_lines_visibility takes a
 * pointer of the same shape (separator lines at +0x4c / +0x50). */
typedef struct {
    uint8_t reserved_000[0x4c];
    void *separator_line1;    /* +0x04c */
    void *separator_line2;    /* +0x050 */
    uint8_t reserved_054[0xd0];
    uint8_t ext_busy;         /* +0x124 non-zero: queue refreshes through stock_ext_fifo */
    uint8_t reserved_125[3];
} g2_stock_ext_page_t;
_Static_assert(offsetof(g2_stock_ext_page_t, ext_busy) == 0x124u, "ext busy flag");

/* Dashboard tileview tile (RAM 0x200734bc, see a-31 ui_dashboard_main_screen.c). */
typedef struct {
    void *tile;  /* +0x00 */
    void *frame; /* +0x04 tile_list[i][1], parent of the widget page */
} g2_dashboard_tile_t;

extern g2_stock_page_data_t g2_stock_page_data_201308dc;   /* RAM 0x201308dc */
extern g2_stock_ext_page_t g2_stock_ext_page_20132e48;     /* RAM 0x20132e48 */
extern g2_dashboard_tile_t g2_dashboard_tiles[STOCK_TILE_COUNT]; /* RAM 0x200734bc */
extern void *g2_dashboard_focus_frame;                     /* RAM 0x20074b9c, expanded-page parent */
extern uint32_t g2_stock_tilelist_index_20004328;          /* RAM 0x20004328 (.data) */
extern uint32_t g2_stock_widget_init_flag_20074e2c;        /* RAM 0x20074e2c widget_stock_init_flag */
extern uint32_t g2_stock_ext_active_20074e30;              /* RAM 0x20074e30 expanded page shown */
extern void *g2_stock_ext_fifo_20074e34;                   /* RAM 0x20074e34 stock_ext_fifo */
extern int32_t g2_stock_container_index_20074e38;          /* RAM 0x20074e38 */
extern void *g2_stock_container_frame_20074e3c;            /* RAM 0x20074e3c non-expanded frame */
extern void *g2_stock_ext_container_frame_20074e40;        /* RAM 0x20074e40 expanded frame */
extern void *g2_stock_no_data_icon_20074e44;               /* RAM 0x20074e44 */
extern void *g2_stock_no_data_label1_20074e48;             /* RAM 0x20074e48 */
extern void *g2_stock_no_data_label2_20074e4c;             /* RAM 0x20074e4c */
extern int32_t g2_stock_page_dots_count_20074e5c;          /* RAM 0x20074e5c */
extern void *g2_stock_page_dots_200740e0[STOCK_PAGE_DOTS_MAX]; /* RAM 0x200740e0 */
extern uint8_t g2_stock_page_dots_visible_20075042;        /* RAM 0x20075042 */
extern void *audio_uart_ring_primary_head_cell;            /* RAM 0x200746dc: active lv_font_t * */

/* Functions of this TU. */
int32_t stock_get_container_index_4ebf20(void);
int32_t Stock_Page_Reflash_4ebf5c(const void *data);
int32_t StockWidget_MainPage_init_4ec2dc(uint32_t tile_index);
int32_t is_stock_format_buffer_valid_4ece5c(char *buffer, size_t buffer_size);
int32_t stock_format_placeholder_4ecec4(char *buffer, size_t buffer_size);
__attribute__((pcs("aapcs-vfp"))) int32_t stock_format_price_4ecee8(char *buffer, size_t buffer_size,
                                                                    double price);
__attribute__((pcs("aapcs-vfp"))) int32_t stock_format_change_percent_4ecf3c(char *buffer, size_t buffer_size,
                                                                             double price, double change_percent);
int32_t calculate_stocks_in_container_4ecfc8(int32_t container_index);
void update_separator_lines_visibility_4ed058(g2_stock_ext_page_t *container, int32_t container_index);
uint8_t stock_page_dots_visible_4ed0ec(void);
void stock_create_page_dots_4ed12c(void *parent);
void stock_update_page_dots_4ed37c(void);
void stock_ext_page_cleanup_4ed440(void);
void stock_switch_to_expanded_container_4ed52e(void);
void stock_page_reset_state_4ed6c4(void);

/* Same-file helpers implemented in other segments. */
extern void stock_obj_set_style_pad_all_4e9dd4(void *obj, int32_t value, uint32_t selector);
extern uint16_t stock_page_get_count_4e9fd6(void);
extern int32_t stock_ext_WidgetPage_Create_4eb7b8(void *parent);

/* LVGL 9.3 (stock build) and product helpers. */
extern void *audio_uart_page_43de82(void *parent);                                    /* lv_obj_create */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);                    /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag);              /* lv_obj_remove_flag */
extern void audio_lv_object_position_43f09a(void *obj, int32_t x, int32_t y);         /* lv_obj_set_pos */
extern void audio_lv_object_size_call_43f4c0(void *obj, int32_t w, int32_t h);        /* lv_obj_set_size */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);                                  /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t selector);     /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t selector);       /* bg_opa */
extern void audio_uart_page_44130c(void *obj, uint32_t opa, uint32_t selector);       /* border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t width, uint32_t selector);      /* border_width */
extern void audio_lv_style_color_44140e(void *obj, uint32_t color, uint32_t selector); /* text_color */
extern void audio_lv_style_font_44143e(void *obj, const void *font, uint32_t selector); /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t selector);     /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t radius, uint32_t selector);     /* radius */
extern void audio_uart_page_44d878(void *obj);                                        /* lv_obj_clean */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                         /* scrollbar_mode */
extern void *audio_lv_image_create_498668(void *parent);                              /* lv_image_create */
extern void audio_lv_image_source_498680(void *obj, const void *src);                 /* lv_image_set_src */
extern void *audio_lv_label_create_499416(void *parent);                              /* lv_label_create */
extern void audio_lv_label_text_49942e(void *obj, const char *text);                  /* lv_label_set_text */
extern void audio_lv_label_mode_499678(void *obj, uint32_t mode);                     /* lv_label_set_long_mode */
extern uint32_t audio_uart_page_460084(const char *key);                              /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);           /* localized text */
extern void audio_uart_text_measure_489546(void *size_out, const char *text, const void *font,
                                           int32_t letter_space, int32_t line_space, int32_t max_width,
                                           uint32_t flags);                           /* lv_text_get_size */
extern void ui_common_api_fn_00509c96(void *fifo);                                    /* fifo destroy */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* fifo push */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len);      /* 0x44b5a0 strncpy */
extern int32_t g2_audio_dump_snprintf(char *buf, uint32_t size, const char *fmt, ...); /* 0x44b728 */
extern uint32_t audio_log_flags(void);                                                /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...);                                                  /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);       /* 0x43ce9e */

/* Two-sink log pattern of the stock firmware: the extended logger gets the
 * plain text, the compressed logger the "[module]"-prefixed text twice. */
#define STOCK_LOG(level, code, line, fn, msg, ...)                                                  \
    do {                                                                                            \
        if (audio_log_flags() & 2u)                                                                 \
            audio_log_extended((level), stock_module_tag, stock_source_file, (fn), (line), msg,     \
                               ##__VA_ARGS__);                                                      \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                                   \
            (void)compress_log_output((code), msg##_short, msg##_short, ##__VA_ARGS__);             \
    } while (0)

#endif
