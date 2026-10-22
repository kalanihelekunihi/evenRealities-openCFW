/* Dashboard stock widget data store and expanded ("ext") stock page, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_stock_page.c.
 * Native 0x4e9dd4..0x4ea00b, 0x4ea00c..0x4ea7e1, 0x4ea800..0x4eacef, 0x4ead10..0x4eb493,
 * 0x4eb4a4..0x4eb73f, 0x4eb7b8..0x4ebdd1 and 0x4ebdfc..0x4ebf1b; literal pools
 * 0x4ea7e4..0x4ea7ff, 0x4eac50..0x4eac5f, 0x4eacb8..0x4eacbf, 0x4eacf0..0x4ead0f,
 * 0x4eb31c..0x4eb33b, 0x4eb494..0x4eb4a3, 0x4eb740..0x4eb7b7, 0x4ebdd4..0x4ebdfb and
 * 0x4ebf1c..0x4ebf1f (shared with 0x4ebf20.. ). The inline "" at 0x4ea254 is the
 * placeholder label text.
 *
 * Up to 9 stock records (0x428 bytes each) are pushed by
 * dashboard_async_update_data. The expanded page is a 539x254 vertically
 * scrolling frame holding three 288-px containers of three rows each
 * (trend icon, name, symbol, 132x62 chart, price, change %); one vertical
 * swipe scrolls one container with a 250 ms animation. Input arriving while the
 * animation runs is queued in a 5-byte-entry fifo and replayed from the
 * animation-ready callback. Event codes: 0x0a click, 0x44/0x45 scroll,
 * 0x47 rebuild page, 0x48 double click, 0x49 ignored.
 *
 * Floating point: stock_scroll_load_stock_data passes the float record fields
 * as doubles in d0/d1 and floats in s0..s2 (hard-float), so this unit needs the
 * double-precision profile. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u /* LVGL 9.3 bit 16 */
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_COORD_MAX 0x1fffffff
#define LV_DIR_VER 0x0cu
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_LABEL_LONG_MODE_DOTS 1u
#define LV_TEXT_ALIGN_LEFT 1u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_TEXT_ALIGN_RIGHT 3u

#define STOCK_MAX 9u
#define STOCK_ROWS 3u
#define STOCK_CONTAINERS 3u
#define CONTAINER_W 0x21b
#define CONTAINER_H 0x120
#define FRAME_H 0xfe
#define MAX_SCROLL_Y 0x240
#define SCROLL_ANIM_MS 250
#define MAX_TILES 6u

enum {
    STOCK_EVT_CLICK = 0x0a,
    STOCK_EVT_SCROLL_UP = 0x44,
    STOCK_EVT_SCROLL_DOWN = 0x45,
    STOCK_EVT_REBUILD = 0x47,
    STOCK_EVT_DOUBLE_CLICK = 0x48,
    STOCK_EVT_IGNORED = 0x49,
};

enum { /* stock_ext_event_handler message types (byte 0) */
    STOCK_MSG_INPUT = 0u,
    STOCK_MSG_DASHBOARD = 1u,
    STOCK_MSG_REFLASH = 4u,
};

#define PAGE_STATE_WIDGET_DASHBOARD 2u

/* One stock as pushed by the phone app (RAM 0x201308dc, 9 entries). */
typedef struct {
    char name[0x80];         /* +0x000 */
    char symbol[0x88];       /* +0x080 */
    float change_percent;    /* +0x108 */
    float price;             /* +0x10c */
    float chart_high;        /* +0x110 */
    float chart_low;         /* +0x114 */
    uint8_t reserved_118[0x1c];
    int32_t trend;           /* +0x134 1 / 2 / other select the row icon */
    uint32_t point_count;    /* +0x138 */
    float chart_reference;   /* +0x13c */
    float points[186];       /* +0x140 */
} g2_stock_record_t;
_Static_assert(sizeof(g2_stock_record_t) == 0x428, "stock record");

typedef struct {
    void *icon;   /* lv_image */
    void *name;   /* lv_label */
    void *symbol; /* lv_label */
    void *chart;  /* lv_image */
    void *price;  /* lv_label, right aligned */
    void *change; /* lv_label, right aligned */
} g2_stock_row_t;

typedef struct {
    void *root;                     /* +0x00 */
    g2_stock_row_t row[STOCK_ROWS]; /* +0x04 */
    void *separator[2];             /* +0x4c */
    int32_t position_y;             /* +0x54 */
    uint32_t array_index;           /* +0x58 */
    uint8_t data_loaded;            /* +0x5c */
    uint8_t reserved_5d[3];
} g2_stock_container_t;
_Static_assert(sizeof(g2_stock_container_t) == 0x60, "stock container");

/* RAM 0x20132e48. */
typedef struct {
    g2_stock_container_t container[STOCK_CONTAINERS]; /* +0x000 */
    uint32_t stock_count;                             /* +0x120 */
    uint8_t is_animating;                             /* +0x124 */
} g2_stock_scroll_t;

typedef struct {
    void *tile;
    void *frame;
} g2_dashboard_tile_t;

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

typedef struct {
    int32_t x;
    int32_t y;
} g2_lv_point_t;

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);            /* lv_obj_set_size */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);         /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);         /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);         /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);         /* pad_right */
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
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);                    /* lv_obj_set_scroll_dir */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                           /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);                   /* lv_obj_get_scroll_bottom */
extern void audio_terminal_display_status_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);                    /* lv_anim_init */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);            /* lv_anim_start */
extern int32_t audio_uart_lv_anim_path_450672(const void *a);                   /* lv_anim_path_ease_out */
extern void audio_uart_page_event_calculate_489546(g2_lv_point_t *size, const char *text, const void *font,
                                                   int32_t letter_space, int32_t line_space, int32_t max_width,
                                                   uint32_t flag);              /* lv_text_get_size */
extern void *audio_uart_page_498668(void *parent);                              /* lv_image_create */
extern void audio_uart_page_498680(void *obj, const void *src);                 /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *obj, const char *text);                /* lv_label_set_text */
extern void audio_uart_page_layout_499678(void *obj, uint32_t mode);            /* lv_label_set_long_mode */
extern uint32_t audio_uart_page_460084(const char *key);                        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);     /* localized text */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

/* Stock page helpers outside this segment, dashboard and sync services. */
extern uint32_t stock_get_container_index_4ebf20(void);
extern void Stock_Page_Reflash_4ebf5c(const uint8_t *data, uint32_t len);
extern int32_t StockWidget_MainPage_init_4ec2dc(uint32_t tile_index);
extern VFP int32_t stock_format_price_4ecee8(char *buf, uint32_t len, double price);
extern VFP int32_t stock_format_change_percent_4ecf3c(char *buf, uint32_t len, double price,
                                                      double change_percent);
extern void update_separator_lines_visibility_4ed058(g2_stock_container_t *container, uint32_t index);
extern uint8_t stock_page_dots_visible_4ed0ec(void); /* byte at RAM 0x20075042 */
extern void stock_create_page_dots_4ed12c(void *parent);
extern void stock_update_page_dots_4ed37c(void);
extern void stock_ext_page_cleanup_4ed440(void);
extern void stock_switch_to_expanded_container_4ed52e(void);
extern void dashboard_main_screen_data_event_4e8970(const uint8_t *data, uint32_t len);
extern void dashboard_focus_frame_shrink_anim_4e92f4(void);
extern VFP uint8_t stock_chart_render_4ff4c0(uint32_t index, const float *points, uint32_t count, float high,
                                             float low, float reference);
extern int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile_index, uint8_t widget);
extern int32_t page_state_sync_stock_expanded_50012e(uint32_t page);
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                 uint32_t flags); /* RequestDisplayReflash 0x464bb2 */
extern void *ui_common_api_fn_00509c1c(void);                                        /* fifo create */
extern void ui_common_api_fn_00509c96(void *fifo);                                   /* fifo destroy */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push, 0 ok */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);                                /* 1 empty */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len);      /* pop */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern g2_stock_record_t g2_stock_data[STOCK_MAX];        /* RAM 0x201308dc */
extern uint16_t g2_stock_count;                           /* RAM 0x20132e44 */
extern g2_stock_scroll_t g2_stock_scroll;                 /* RAM 0x20132e48 */
extern uint32_t g2_stock_ext_page_flag;                   /* RAM 0x20074e30 */
extern void *g2_stock_ext_fifo;                           /* RAM 0x20074e34 */
extern int32_t g2_stock_container_index;                  /* RAM 0x20074e38 */
extern void *g2_stock_ext_container_frame;                /* RAM 0x20074e40 */
extern void *g2_stock_no_data_icon;                       /* RAM 0x20074e50 */
extern void *g2_stock_no_data_title;                      /* RAM 0x20074e54 */
extern void *g2_stock_no_data_hint;                       /* RAM 0x20074e58 */
extern uint8_t g2_stock_chart_images[STOCK_MAX][0x14];    /* RAM 0x200e7880, image descriptors */
extern void *g2_dashboard_focus_frame;                    /* RAM 0x20074b9c */
extern uint32_t g2_dashboard_current_tile;                /* RAM 0x20004328 */
extern g2_dashboard_tile_t g2_dashboard_tiles[MAX_TILES]; /* RAM 0x200734bc */
extern const void *audio_uart_ring_primary_head_cell;     /* RAM 0x200746dc: active lv_font_t * */
extern const uint8_t g2_stock_icon_trend_1[];             /* ROM 0x7725c4 lv_image_dsc_t 24x24 */
extern const uint8_t g2_stock_icon_trend_2[];             /* ROM 0x7725a8 lv_image_dsc_t 24x24 */
extern const uint8_t g2_stock_icon_trend_flat[];          /* ROM 0x77258c lv_image_dsc_t 24x24 */
extern const uint8_t g2_stock_icon_no_data[];             /* ROM 0x772570 lv_image_dsc_t 24x24 */

static const char module_tag[] = "dashboard.stock"; /* ROM 0x789e80 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_stock_page.c"; /* ROM 0x6f0e98 */
static const char empty_text[] = ""; /* inline 0x4ea254 */

static const char push_fn[] = "stock_page_push_data"; /* ROM 0x77d51c */
static const char push_msg[] = "stock_data = %p, stock_num = %u, stock_total = %u"; /* ROM 0x730578 */
static const char push_msg_short[] = "[dashboard.stock]stock_data = %p, stock_num = %u, stock_total = %u"; /* ROM 0x708174 */
static const char peek_fn[] = "stock_page_peek_data_at"; /* ROM 0x77d534 */
static const char peek_index[] = "index = %d"; /* ROM 0x78c8c0 */
static const char peek_index_short[] = "[dashboard.stock]index = %d"; /* ROM 0x77434c */
static const char peek_null[] = "stock_data is NULL"; /* ROM 0x784a40 */
static const char peek_null_short[] = "[dashboard.stock]stock_data is NULL"; /* ROM 0x75cc0c */
static const char peek_range[] = "Index %d out of range (count: %d)"; /* ROM 0x75cc30 */
static const char peek_range_short[] = "[dashboard.stock]Index %d out of range (count: %d)"; /* ROM 0x7305ac */
static const char create_fn[] = "stock_scroll_create_container"; /* ROM 0x767c10 */
static const char create_null[] = "stock_scroll NULL"; /* ROM 0x784a54 */
static const char create_null_short[] = "[dashboard.stock]stock_scroll NULL"; /* ROM 0x75cc54 */
static const char create_msg[] = "Creating container with array_index=%d, position_y=%d"; /* ROM 0x725cd8 */
static const char create_msg_short[] =
    "[dashboard.stock]Creating container with array_index=%d, position_y=%d"; /* ROM 0x6ff1f4 */
static const char load_fn[] = "stock_scroll_load_stock_data"; /* ROM 0x767c30 */
static const char load_null[] = "stock_scroll container is NULL"; /* ROM 0x767c50 */
static const char load_null_short[] = "[dashboard.stock]stock_scroll container is NULL"; /* ROM 0x73af04 */
static const char load_msg[] = "Loading stocks for container %d, stock indices: %d, %d, %d"; /* ROM 0x71af98 */
static const char load_msg_short[] =
    "[dashboard.stock]Loading stocks for container %d, stock indices: %d, %d, %d"; /* ROM 0x6f774c */
static const char scroll_fn[] = "stock_scroll_handle_vertical_scroll"; /* ROM 0x75cc78 */
static const char scroll_dir[] = "stock scroll direction = %d, is_animating = %d"; /* ROM 0x73af34 */
static const char scroll_dir_short[] = "[dashboard.stock]stock scroll direction = %d, is_animating = %d"; /* ROM 0x711664 */
static const char scroll_busy[] = "stock is animating, return"; /* ROM 0x774368 */
static const char scroll_busy_short[] = "[dashboard.stock]stock is animating, return"; /* ROM 0x746614 */
static const char scroll_no_frame[] = "g_stock_ext_container_frame is NULL"; /* ROM 0x75cc9c */
static const char scroll_no_frame_short[] = "[dashboard.stock]g_stock_ext_container_frame is NULL"; /* ROM 0x725d10 */
static const char scroll_no_down[] = "Cannot scroll down"; /* ROM 0x784a68 */
static const char scroll_no_down_short[] = "[dashboard.stock]Cannot scroll down"; /* ROM 0x75ccc0 */
static const char scroll_no_up[] = "Cannot scroll up"; /* ROM 0x784a7c */
static const char scroll_no_up_short[] = "[dashboard.stock]Cannot scroll up"; /* ROM 0x75cce4 */
static const char scroll_from_to[] = "Scrolling from %d to %d"; /* ROM 0x77d54c */
static const char scroll_from_to_short[] = "[dashboard.stock]Scrolling from %d to %d"; /* ROM 0x746640 */
static const char ready_fn[] = "stock_container_switch_anim_ready_cb"; /* ROM 0x750e64 */
static const char ready_queued[] = "stock Processing queued event from fifo, code:%d"; /* ROM 0x7305e0 */
static const char ready_queued_short[] = "[dashboard.stock]stock Processing queued event from fifo, code:%d"; /* ROM 0x7081b8 */
static const char ready_scroll[] = "stock scroll up event"; /* ROM 0x77d564 */
static const char ready_scroll_short[] = "[dashboard.stock]stock scroll up event"; /* ROM 0x750e8c */
static const char ready_click[] = "stock single/double click event"; /* ROM 0x767c70 */
static const char ready_click_short[] = "[dashboard.stock]stock single/double click event"; /* ROM 0x730614 */
static const char move_fn[] = "stock_container_move_with_anim"; /* ROM 0x767c90 */
static const char move_null[] = "stock anim container is NULL"; /* ROM 0x767cb0 */
static const char move_null_short[] = "[dashboard.stock]stock anim container is NULL"; /* ROM 0x73af64 */
static const char move_same[] =
    "stock scroll content with anim, target_y == current_scroll_y, animation time:%d"; /* ROM 0x6f0ee8 */
static const char move_same_short[] =
    "[dashboard.stock]stock scroll content with anim, target_y == current_scroll_y, animation time:%d"; /* ROM 0x6dbd80 */
static const char move_msg[] = "stock scroll content with anim, scrolling from %d to %d with %dms animation"; /* ROM 0x6f7798 */
static const char move_msg_short[] =
    "[dashboard.stock]stock scroll content with anim, scrolling from %d to %d with %dms animation"; /* ROM 0x6deeb4 */
static const char input_fn[] = "StockInputEventHandler"; /* ROM 0x77d57c */
static const char input_busy[] = "stock is_animating, return"; /* ROM 0x774384 */
static const char input_busy_short[] = "[dashboard.stock]stock is_animating, return"; /* ROM 0x74666c */
static const char ext_fn[] = "stock_ext_event_handler"; /* ROM 0x77d594 */
static const char ext_off[] = "stock ext page flag is 0, return"; /* ROM 0x75cd08 */
static const char ext_off_short[] = "[dashboard.stock]stock ext page flag is 0, return"; /* ROM 0x730648 */
static const char ext_bad[] = "stock raw_data is null or len == 0, return"; /* ROM 0x746698 */
static const char ext_bad_short[] = "[dashboard.stock]stock raw_data is null or len == 0, return"; /* ROM 0x71afd4 */
static const char ext_event[] = "stock is_animating, handling event code=%d"; /* ROM 0x7466c4 */
static const char ext_event_short[] = "[dashboard.stock]stock is_animating, handling event code=%d"; /* ROM 0x71b010 */
static const char ext_queued[] = "stock don't allowed input event, queued to fifo, code = %d"; /* ROM 0x71b04c */
static const char ext_queued_short[] =
    "[dashboard.stock]stock don't allowed input event, queued to fifo, code = %d"; /* ROM 0x6f77e4 */
static const char ext_click[] = "stock single_click or double_click event, Current container index is %d"; /* ROM 0x6ff23c */
static const char ext_click_short[] =
    "[dashboard.stock]stock single_click or double_click event, Current container index is %d"; /* ROM 0x6e1ef8 */
static const char page_fn[] = "stock_ext_WidgetPage_Create"; /* ROM 0x7743a0 */
static const char page_null[] = "parent_obj is NULL"; /* ROM 0x784a90 */
static const char page_null_short[] = "[dashboard.stock]parent_obj is NULL"; /* ROM 0x75cd2c */
static const char page_clamp[] =
    "Container index %d exceeds max valid index %d (stock count: %d), adjusting to %d"; /* ROM 0x6eadf8 */
static const char page_clamp_short[] =
    "[dashboard.stock]Container index %d exceeds max valid index %d (stock count: %d), adjusting to %d"; /* ROM 0x6dbde4 */
static const char page_reset[] = "No stock data, resetting container index from %d to 0"; /* ROM 0x725d48 */
static const char page_reset_short[] =
    "[dashboard.stock]No stock data, resetting container index from %d to 0"; /* ROM 0x6ff284 */
static const char page_frame_failed[] = "Failed to create container frame"; /* ROM 0x75cd50 */
static const char page_frame_failed_short[] = "[dashboard.stock]Failed to create container frame"; /* ROM 0x73067c */
static const char page_init_index[] = "Initializing with container index %d"; /* ROM 0x750eb4 */
static const char page_init_index_short[] = "[dashboard.stock]Initializing with container index %d"; /* ROM 0x725d80 */
static const char page_scrolled[] = "Scrolled to position %d for container index %d"; /* ROM 0x73af94 */
static const char page_scrolled_short[] = "[dashboard.stock]Scrolled to position %d for container index %d"; /* ROM 0x7116a4 */
static const char page_loaded[] = "Loaded data for containers: 0->0, 1->1, 2->2"; /* ROM 0x73afc4 */
static const char page_loaded_short[] = "[dashboard.stock]Loaded data for containers: 0->0, 1->1, 2->2"; /* ROM 0x7116e4 */
static const char page_no_data[] = "No data available, showing new no data display"; /* ROM 0x73aff4 */
static const char page_no_data_short[] =
    "[dashboard.stock]No data available, showing new no data display"; /* ROM 0x711724 */
static const char key_default_1[] = "ID_DASHBOARD_STOCKS_DEFAULT_1"; /* ROM 0x767cd0 */
static const char key_default_2[] = "ID_DASHBOARD_STOCKS_DEFAULT_2"; /* ROM 0x767cf0 */
static const char page_created[] = "Stock extension widget page created with %d stocks"; /* ROM 0x7306b0 */
static const char page_created_short[] = "[dashboard.stock]Stock extension widget page created with %d stocks"; /* ROM 0x7081fc */
static const char init_fn[] = "stock_ext_Widget_init"; /* ROM 0x77d5ac */
static const char init_fifo_failed[] = "stock_ext_fifo create failed"; /* ROM 0x767d10 */
static const char init_fifo_failed_short[] = "[dashboard.stock]stock_ext_fifo create failed"; /* ROM 0x73b024 */
static const char init_ok[] = "Stock extension widget initialized successfully"; /* ROM 0x73b054 */
static const char init_ok_short[] = "[dashboard.stock]Stock extension widget initialized successfully"; /* ROM 0x708240 */

void stock_container_move_with_anim_4eb1c0(void *obj, int32_t target_y, int32_t time_ms);
int32_t stock_ext_WidgetPage_Create_4eb7b8(void *parent);

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

static void log4(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a, uint32_t b, uint32_t c, uint32_t d)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a, b, c, d);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 4), msg_short, msg_short, a, b, c, d);
}

/* lv_obj_set_style_pad_all, instantiated in this TU. */
void stock_obj_set_style_pad_all_4e9dd4(void *obj, int32_t v, uint32_t sel)
{
    audio_uart_page_44122a(obj, v, sel);
    audio_uart_page_441238(obj, v, sel);
    audio_uart_page_44120e(obj, v, sel);
    audio_uart_page_44121c(obj, v, sel);
}

void stock_page_reset_4e9e06(void)
{
    (void)aeabi_memset_43c0e4(g2_stock_data, sizeof(g2_stock_data), 0);
    g2_stock_count = 0u;
    if (stock_get_container_index_4ebf20() != 0u)
        g2_stock_container_index = 0;
}

/* Copies one record into slot stock_num and sets the visible count to
 * stock_total. Returns 1 on success, 0 for NULL data or slot >= 9. */
uint32_t stock_page_push_data_4e9e32(const uint8_t *stock, uint32_t stock_num, uint32_t stock_total)
{
    log3(4u, push_fn, 0x7du, push_msg, push_msg_short, (uint32_t)(uintptr_t)stock, stock_num, stock_total);
    if (stock == NULL || stock_num >= STOCK_MAX)
        return 0u;
    (void)audio_queue_copy_bytes(&g2_stock_data[stock_num], stock, sizeof(g2_stock_record_t));
    g2_stock_count = (uint16_t)stock_total;
    return 1u;
}

uint32_t stock_page_peek_data_at_4e9eb8(g2_stock_record_t *out, uint16_t index)
{
    log1(4u, peek_fn, 0x92u, peek_index, peek_index_short, index);
    if (out == NULL) {
        log0(1u, peek_fn, 0x95u, peek_null, peek_null_short);
        return 0u;
    }
    if (index >= g2_stock_count) {
        log2(2u, peek_fn, 0x9au, peek_range, peek_range_short, index, g2_stock_count);
        return 0u;
    }
    (void)audio_queue_copy_bytes(out, &g2_stock_data[index], sizeof(g2_stock_record_t));
    return 1u;
}

uint16_t stock_page_get_count_4e9fd6(void)
{
    return g2_stock_count;
}

void stock_page_clear_4e9fde(void)
{
    g2_stock_count = 0u;
    (void)aeabi_memset_43c0e4(g2_stock_data, sizeof(g2_stock_data), 0);
    if (stock_get_container_index_4ebf20() != 0u)
        g2_stock_container_index = 0;
}

static void *create_label(void *parent, int32_t w, int32_t h, int32_t x, int32_t y)
{
    void *label = audio_uart_page_499416(parent);

    audio_uart_page_43f4c0(label, w, h);
    audio_uart_page_43f09a(label, x, y);
    return label;
}

static void *create_plain_image(void *parent, int32_t w, int32_t h, int32_t x, int32_t y)
{
    void *img = audio_uart_page_498668(parent);

    audio_uart_page_43f4c0(img, w, h);
    audio_uart_page_43f09a(img, x, y);
    audio_uart_page_44129e(img, 0u, 0u);
    audio_uart_page_44131c(img, 0, 0u);
    audio_uart_page_43ded4(img, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(img, LV_OBJ_FLAG_SCROLLABLE);
    return img;
}

/* Builds one 539x288 container of three stock rows at position_y inside the
 * scrolling frame (stock code is fully unrolled; rows are 0x60 apart). */
void stock_scroll_create_container_4ea00c(g2_stock_container_t *c, void *parent, int32_t position_y,
                                          uint32_t array_index)
{
    uint32_t r;

    if (c == NULL || parent == NULL) {
        log0(1u, create_fn, 0xc2u, create_null, create_null_short);
        return;
    }
    c->array_index = array_index;
    c->position_y = position_y;
    log2(4u, create_fn, 0xcau, create_msg, create_msg_short, array_index, (uint32_t)position_y);

    c->root = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(c->root, CONTAINER_W, CONTAINER_H);
    audio_uart_page_43f09a(c->root, 0, position_y);
    audio_uart_page_44129e(c->root, 0u, 0u);
    audio_uart_page_44131c(c->root, 0, 0u);
    stock_obj_set_style_pad_all_4e9dd4(c->root, 0, 0u);

    for (r = 0; r < STOCK_ROWS; r++) {
        g2_stock_row_t *row = &c->row[r];
        int32_t y = (int32_t)(r * 0x60u);

        row->icon = create_plain_image(c->root, 0x18, 0x18, 0, y + 3);

        row->name = create_label(c->root, LV_SIZE_CONTENT, 0x1e, 0x20, y);
        audio_uart_page_44143e(row->name, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(row->name, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44129e(row->name, 0u, 0u);
        audio_uart_page_44131c(row->name, 0, 0u);
        audio_uart_page_49942e(row->name, empty_text);

        row->symbol = create_label(c->root, LV_SIZE_CONTENT, 0x1c, 0, y + 0x22);
        audio_uart_page_44143e(row->symbol, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44129e(row->symbol, 0u, 0u);
        audio_uart_page_44131c(row->symbol, 0, 0u);
        audio_uart_page_44140e(row->symbol, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_49942e(row->symbol, empty_text);

        row->chart = create_plain_image(c->root, 0x84, 0x3e, 0x102, y);

        row->price = audio_uart_page_499416(c->root);
        audio_uart_page_43f4c0(row->price, 0x84, 0x1e);
        if (stock_page_dots_visible_4ed0ec() == 0u)
            audio_uart_page_43f09a(row->price, 0x197, y);
        else
            audio_uart_page_43f09a(row->price, 0x18d, y);
        audio_uart_page_44145a(row->price, LV_TEXT_ALIGN_RIGHT, 0u);
        audio_uart_page_44143e(row->price, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(row->price, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44129e(row->price, 0u, 0u);
        audio_uart_page_44131c(row->price, 0, 0u);
        audio_uart_page_49942e(row->price, empty_text);

        row->change = audio_uart_page_499416(c->root);
        audio_uart_page_43f4c0(row->change, 0x5d, 0x1c);
        if (stock_page_dots_visible_4ed0ec() == 0u)
            audio_uart_page_43f09a(row->change, 0x1be, y + 0x22);
        else
            audio_uart_page_43f09a(row->change, 0x1b4, y + 0x22);
        audio_uart_page_44145a(row->change, LV_TEXT_ALIGN_RIGHT, 0u);
        audio_uart_page_44143e(row->change, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(row->change, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44129e(row->change, 0u, 0u);
        audio_uart_page_44131c(row->change, 0, 0u);
        audio_uart_page_49942e(row->change, empty_text);
    }

    for (r = 0; r < 2u; r++) {
        c->separator[r] = audio_uart_page_43de82(c->root);
        audio_uart_page_43f4c0(c->separator[r], 0x218, 1);
        audio_uart_page_43f09a(c->separator[r], 0, r == 0u ? 0x4f : 0xaf);
        audio_uart_page_44127e(c->separator[r], audio_uart_page_44104c(0x222222u), 0u);
        audio_uart_page_44129e(c->separator[r], 0xffu, 0u);
        audio_uart_page_44131c(c->separator[r], 0, 0u);
        stock_obj_set_style_pad_all_4e9dd4(c->separator[r], 0, 0u);
    }
    c->data_loaded = 0u;
}

/* Fills the three rows of a container with stocks 3*index .. 3*index+2. */
void stock_scroll_load_stock_data_4ea800(g2_stock_container_t *c, uint32_t index)
{
    g2_stock_record_t rec;
    char price_text[0x20];
    char change_text[0x20];
    uint32_t r;

    if (c == NULL) {
        log0(1u, load_fn, 0x1c6u, load_null, load_null_short);
        return;
    }
    log4(4u, load_fn, 0x1d0u, load_msg, load_msg_short, index, index * 3u, index * 3u + 1u, index * 3u + 2u);

    for (r = 0; r < STOCK_ROWS; r++) {
        g2_stock_row_t *row = &c->row[r];
        uint32_t si = index * 3u + r;

        if ((int32_t)si >= (int32_t)stock_page_get_count_4e9fd6() ||
            stock_page_peek_data_at_4e9eb8(&rec, (uint16_t)si) == 0u)
            continue;
        if (rec.trend == 1)
            audio_uart_page_498680(row->icon, g2_stock_icon_trend_1);
        else if (rec.trend == 2)
            audio_uart_page_498680(row->icon, g2_stock_icon_trend_2);
        else
            audio_uart_page_498680(row->icon, g2_stock_icon_trend_flat);
        audio_uart_page_43f4c0(row->name, 0xe4, 0x1e);
        audio_uart_page_layout_499678(row->name, LV_LABEL_LONG_MODE_DOTS);
        audio_uart_page_49942e(row->name, rec.name);
        audio_uart_page_43f4c0(row->symbol, 0xf0, 0x1c);
        audio_uart_page_layout_499678(row->symbol, LV_LABEL_LONG_MODE_DOTS);
        audio_uart_page_49942e(row->symbol, rec.symbol);
        (void)stock_format_price_4ecee8(price_text, sizeof(price_text), (double)rec.price);
        audio_uart_page_49942e(row->price, price_text);
        (void)stock_format_change_percent_4ecf3c(change_text, sizeof(change_text), (double)rec.price,
                                                 (double)rec.change_percent);
        audio_uart_page_49942e(row->change, change_text);
        if (stock_chart_render_4ff4c0(si, rec.points, rec.point_count, rec.chart_high, rec.chart_low,
                                      rec.chart_reference) != 0u)
            audio_uart_page_498680(row->chart, g2_stock_chart_images[si]);
    }
    update_separator_lines_visibility_4ed058(c, index);
    c->data_loaded = 1u;
}

void stock_scroll_sync_count_4eac40(void)
{
    g2_stock_scroll.stock_count = stock_page_get_count_4e9fd6();
}

uint32_t stock_scroll_can_scroll_down_4eac60(void)
{
    uint32_t pages;

    if (stock_page_get_count_4e9fd6() == 0u)
        return 0u;
    if (g2_stock_ext_container_frame == NULL)
        return 0u;
    pages = (stock_page_get_count_4e9fd6() + 2u) / 3u;
    if (pages < 2u || (int32_t)(pages - 1u) <= g2_stock_container_index)
        return 0u;
    return audio_uart_lv_scroll_bottom_44e4bc(g2_stock_ext_container_frame) >= 1 ? 1u : 0u;
}

uint32_t stock_scroll_can_scroll_up_4eacc0(void)
{
    if (g2_stock_ext_container_frame == NULL)
        return 0u;
    if (g2_stock_container_index < 1)
        return 0u;
    return audio_uart_lv_obj_y_44e498(g2_stock_ext_container_frame) >= 1 ? 1u : 0u;
}

/* direction 1 scrolls to the next container (event 0x44), anything else to
 * the previous one (0x45 passes -1). */
void stock_scroll_handle_vertical_scroll_4ead10(int32_t direction)
{
    int32_t current;
    int32_t target;
    int32_t bottom;

    log2(4u, scroll_fn, 0x2a0u, scroll_dir, scroll_dir_short, (uint32_t)direction, g2_stock_scroll.is_animating);
    if (g2_stock_scroll.is_animating != 0u) {
        log0(2u, scroll_fn, 0x2a3u, scroll_busy, scroll_busy_short);
        return;
    }
    if (g2_stock_ext_container_frame == NULL) {
        log0(1u, scroll_fn, 0x2a8u, scroll_no_frame, scroll_no_frame_short);
        return;
    }
    current = audio_uart_lv_obj_y_44e498(g2_stock_ext_container_frame);
    if (direction == 1) {
        if (stock_scroll_can_scroll_down_4eac60() == 0u) {
            log0(4u, scroll_fn, 0x2b3u, scroll_no_down, scroll_no_down_short);
            return;
        }
        target = current + CONTAINER_H;
    } else {
        if (stock_scroll_can_scroll_up_4eacc0() == 0u) {
            log0(4u, scroll_fn, 0x2bau, scroll_no_up, scroll_no_up_short);
            return;
        }
        target = current - CONTAINER_H;
    }
    if (target < 0)
        target = 0;
    else if (target > MAX_SCROLL_Y)
        target = MAX_SCROLL_Y;
    bottom = audio_uart_lv_scroll_bottom_44e4bc(g2_stock_ext_container_frame);
    if (bottom + current < target)
        target = bottom + current;
    log2(4u, scroll_fn, 0x2cbu, scroll_from_to, scroll_from_to_short, (uint32_t)current, (uint32_t)target);
    stock_container_move_with_anim_4eb1c0(g2_stock_ext_container_frame, target, SCROLL_ANIM_MS);

    if (direction == 1)
        g2_stock_container_index++;
    else
        g2_stock_container_index--;
    if (g2_stock_container_index < 0)
        g2_stock_container_index = 0;
    else if (g2_stock_container_index > 2)
        g2_stock_container_index = 2;
}

/* Deletes the expanded page, shrinks the focus frame and rebuilds the
 * dashboard stock tile (single/double click closes the page). */
static void close_expanded_page(bool shrink_first)
{
    int32_t i = (int32_t)audio_uart_lv_child_count_44ddea(g2_dashboard_focus_frame);

    while (--i >= 0) {
        void *child = audio_lv_child_44dce2(g2_dashboard_focus_frame, i);

        if (child != NULL)
            audio_uart_page_delete_event_filter_44d7b8(child);
    }
    stock_ext_page_cleanup_4ed440();
    if (shrink_first) {
        dashboard_focus_frame_shrink_anim_4e92f4();
        (void)page_state_sync_dashboard_main_5000cc(g2_dashboard_current_tile, PAGE_STATE_WIDGET_DASHBOARD);
    } else {
        (void)page_state_sync_dashboard_main_5000cc(g2_dashboard_current_tile, PAGE_STATE_WIDGET_DASHBOARD);
        dashboard_focus_frame_shrink_anim_4e92f4();
    }
    if (g2_dashboard_current_tile < MAX_TILES) {
        if (g2_dashboard_tiles[g2_dashboard_current_tile].frame != NULL)
            audio_uart_page_44d878(g2_dashboard_tiles[g2_dashboard_current_tile].frame);
        StockWidget_MainPage_init_4ec2dc(g2_dashboard_current_tile);
    }
}

/* lv_anim completed_cb of stock_container_move_with_anim: updates the page
 * dots and replays one queued input event. */
void stock_container_switch_anim_ready_cb_4eaf76(void *anim)
{
    uint8_t event[10];

    (void)anim;
    g2_stock_scroll.is_animating = 0u;
    stock_update_page_dots_4ed37c();
    (void)page_state_sync_stock_expanded_50012e(stock_get_container_index_4ebf20() + 1u);
    if (g2_stock_ext_fifo == NULL || ui_common_api_fn_00509dfa(g2_stock_ext_fifo) != 0 ||
        g2_stock_ext_page_flag != 1u)
        return;

    (void)aeabi_memset_43c0e4(event, sizeof(event), 0);
    (void)aeabi_memset_43c0e4(event, sizeof(event), 0);
    (void)ui_common_api_fn_00509e14(g2_stock_ext_fifo, event, 5u);
    log1(3u, ready_fn, 0x2f3u, ready_queued, ready_queued_short, event[0]);

    switch (event[0]) {
    case STOCK_EVT_SCROLL_UP:
        log0(3u, ready_fn, 0x2f8u, ready_scroll, ready_scroll_short);
        stock_scroll_handle_vertical_scroll_4ead10(1);
        break;
    case STOCK_EVT_SCROLL_DOWN:
        log0(3u, ready_fn, 0x2fcu, ready_scroll, ready_scroll_short);
        stock_scroll_handle_vertical_scroll_4ead10(-1);
        break;
    case STOCK_EVT_REBUILD:
        if (g2_stock_ext_page_flag == 1u && g2_stock_ext_fifo != NULL && g2_dashboard_focus_frame != NULL &&
            g2_stock_scroll.is_animating == 0u) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            (void)stock_ext_WidgetPage_Create_4eb7b8(g2_dashboard_focus_frame);
        }
        break;
    case STOCK_EVT_CLICK:
    case STOCK_EVT_DOUBLE_CLICK:
        log0(3u, ready_fn, 0x301u, ready_click, ready_click_short);
        close_expanded_page(true);
        break;
    default:
        break;
    }
}

/* lv_anim exec_cb: scroll the frame to the animated y. */
void stock_scroll_anim_exec_cb_4eb1b2(void *obj, int32_t y)
{
    if (obj != NULL)
        audio_terminal_display_status_44ea04(obj, y, 0u);
}

void stock_container_move_with_anim_4eb1c0(void *obj, int32_t target_y, int32_t time_ms)
{
    g2_lv_anim_t a;
    int32_t current;

    if (obj == NULL) {
        log0(1u, move_fn, 0x33fu, move_null, move_null_short);
        return;
    }
    g2_stock_scroll.is_animating = 0u;
    current = audio_uart_lv_obj_y_44e498(obj);
    if (target_y == current) {
        time_ms = 10;
        log1(4u, move_fn, 0x347u, move_same, move_same_short, 10u);
    }
    log3(4u, move_fn, 0x34bu, move_msg, move_msg_short, (uint32_t)current, (uint32_t)target_y, (uint32_t)time_ms);
    if (time_ms == 0) {
        audio_terminal_display_status_44ea04(obj, target_y, 0u);
        return;
    }
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, current, target_y);
    a.exec_cb = stock_scroll_anim_exec_cb_4eb1b2;
    a.completed_cb = stock_container_switch_anim_ready_cb_4eaf76;
    a.path_cb = audio_uart_lv_anim_path_450672;
    g2_stock_scroll.is_animating = 1u;
    a.duration = time_ms;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Forwards input to the phone (RequestDisplayReflash, app 1) as
 * {0, code, x lo, x hi, y lo, y hi}. Returns the send result, 0 while a scroll
 * animation runs, or the code itself for 0x49 / unknown codes. */
int32_t StockInputEventHandler_4eb33c(int32_t code, const void *event)
{
    uint8_t msg[6];

    if (code == STOCK_EVT_CLICK || code == STOCK_EVT_DOUBLE_CLICK) {
        if (g2_stock_scroll.is_animating != 0u) {
            if (code == STOCK_EVT_CLICK)
                log0(4u, input_fn, 0x362u, input_busy, input_busy_short);
            return 0;
        }
        msg[0] = 0u;
        msg[1] = (uint8_t)code;
        msg[2] = 0u;
        msg[3] = 0u;
        msg[4] = 0u;
        msg[5] = 0u;
        return audio_uart_master_display_refresh(1u, msg, sizeof(msg), 0u);
    }
    if (code == STOCK_EVT_IGNORED)
        return code;
    if (code == STOCK_EVT_SCROLL_DOWN || code == STOCK_EVT_SCROLL_UP) {
        const g2_lv_point_t *pt;

        if (g2_stock_scroll.is_animating != 0u)
            return 0;
        pt = *(const g2_lv_point_t *const *)(const void *)((const uint8_t *)event + 0x10u);
        msg[0] = 0u;
        msg[1] = (uint8_t)code;
        msg[2] = (uint8_t)pt->x;
        msg[3] = (uint8_t)(pt->x >> 8);
        msg[4] = (uint8_t)pt->y;
        msg[5] = (uint8_t)(pt->y >> 8);
        return audio_uart_master_display_refresh(1u, msg, sizeof(msg), 0u);
    }
    return code;
}

/* Data from the sync app: byte 0 selects input event (0), dashboard data (1)
 * or stock page refresh (4). Returns 0, or -1 for NULL/empty data. */
int32_t stock_ext_event_handler_4eb4a4(const uint8_t *data, uint32_t len)
{
    uint8_t code;

    if (g2_stock_ext_page_flag == 0u) {
        log0(4u, ext_fn, 0x3abu, ext_off, ext_off_short);
        return 0;
    }
    if (data == NULL || len == 0u) {
        log0(1u, ext_fn, 0x3b0u, ext_bad, ext_bad_short);
        return -1;
    }
    switch (data[0]) {
    case STOCK_MSG_INPUT:
        break;
    case STOCK_MSG_DASHBOARD:
        dashboard_main_screen_data_event_4e8970(data + 1, len - 1u);
        return 0;
    case STOCK_MSG_REFLASH:
        Stock_Page_Reflash_4ebf5c(data + 1, len - 1u);
        return 0;
    default:
        return 0;
    }

    code = data[1];
    log1(4u, ext_fn, 0x3bau, ext_event, ext_event_short, code);
    if (g2_stock_scroll.is_animating != 0u) {
        if (g2_stock_ext_fifo != NULL) {
            (void)ui_common_api_fn_00509ca2(g2_stock_ext_fifo, data + 1, 5u);
            log1(4u, ext_fn, 0x3c0u, ext_queued, ext_queued_short, code);
        }
        return 0;
    }
    switch (code) {
    case STOCK_EVT_SCROLL_UP:
        stock_scroll_handle_vertical_scroll_4ead10(1);
        break;
    case STOCK_EVT_SCROLL_DOWN:
        stock_scroll_handle_vertical_scroll_4ead10(-1);
        break;
    case STOCK_EVT_REBUILD:
        if (g2_stock_ext_page_flag == 1u && g2_stock_ext_fifo != NULL && g2_dashboard_focus_frame != NULL) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            (void)stock_ext_WidgetPage_Create_4eb7b8(g2_dashboard_focus_frame);
        }
        break;
    case STOCK_EVT_CLICK:
    case STOCK_EVT_DOUBLE_CLICK:
        log1(3u, ext_fn, 0x3cfu, ext_click, ext_click_short, stock_get_container_index_4ebf20());
        close_expanded_page(false);
        break;
    default:
        break;
    }
    return 0;
}

/* Builds the expanded stock page inside parent: the scrolling frame, page
 * dots, three containers, then either the stock rows or a centred
 * icon + two-line "no stocks" hint. Returns 0, or -1 on failure. */
int32_t stock_ext_WidgetPage_Create_4eb7b8(void *parent)
{
    g2_stock_container_t *c0 = &g2_stock_scroll.container[0];
    g2_stock_container_t *c1 = &g2_stock_scroll.container[1];
    g2_stock_container_t *c2 = &g2_stock_scroll.container[2];
    uint16_t count;
    int32_t i;

    if (parent == NULL) {
        log0(1u, page_fn, 0x40fu, page_null, page_null_short);
        return -1;
    }
    count = stock_page_get_count_4e9fd6();
    if (count == 0u) {
        if (stock_get_container_index_4ebf20() != 0u) {
            log1(4u, page_fn, 0x420u, page_reset, page_reset_short, stock_get_container_index_4ebf20());
            g2_stock_container_index = 0;
        }
    } else {
        uint16_t max_index = (uint16_t)(((int32_t)count - 1) / 3);

        if ((int32_t)max_index < (int32_t)stock_get_container_index_4ebf20()) {
            log4(2u, page_fn, 0x41au, page_clamp, page_clamp_short, stock_get_container_index_4ebf20(), max_index,
                 count, max_index);
            g2_stock_container_index = max_index;
        }
    }

    g2_stock_ext_container_frame = audio_uart_page_43de82(parent);
    if (g2_stock_ext_container_frame == NULL) {
        log0(1u, page_fn, 0x429u, page_frame_failed, page_frame_failed_short);
        return -1;
    }
    audio_uart_page_43f09a(g2_stock_ext_container_frame, 0x14, 0x11);
    audio_uart_page_43f4c0(g2_stock_ext_container_frame, CONTAINER_W, FRAME_H);
    audio_uart_page_44e3ca(g2_stock_ext_container_frame, LV_DIR_VER);
    audio_uart_page_44e368(g2_stock_ext_container_frame, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44129e(g2_stock_ext_container_frame, 0u, 0u);
    audio_uart_page_44131c(g2_stock_ext_container_frame, 0, 0u);
    stock_obj_set_style_pad_all_4e9dd4(g2_stock_ext_container_frame, 0, 0u);
    stock_create_page_dots_4ed12c(parent);
    stock_scroll_create_container_4ea00c(c0, g2_stock_ext_container_frame, 0, 0u);
    stock_scroll_create_container_4ea00c(c1, g2_stock_ext_container_frame, CONTAINER_H, 1u);
    stock_scroll_create_container_4ea00c(c2, g2_stock_ext_container_frame, 2 * CONTAINER_H, 2u);
    log1(4u, page_fn, 0x441u, page_init_index, page_init_index_short, (uint32_t)g2_stock_container_index);
    stock_scroll_sync_count_4eac40();

    if (stock_page_get_count_4e9fd6() == 0u) {
        const char *title;
        const char *hint;
        g2_lv_point_t title_size;
        g2_lv_point_t hint_size;
        int32_t gap = 8;
        int32_t line_h;
        int32_t top;
        int32_t left;

        log0(4u, page_fn, 0x465u, page_no_data, page_no_data_short);
        for (i = 0; i < (int32_t)STOCK_CONTAINERS; i++) {
            if (g2_stock_scroll.container[i].root != NULL)
                audio_uart_page_43ded4(g2_stock_scroll.container[i].root, LV_OBJ_FLAG_HIDDEN);
        }
        title = audio_uart_page_45fffe(key_default_1, audio_uart_page_460084(key_default_1));
        hint = audio_uart_page_45fffe(key_default_2, audio_uart_page_460084(key_default_2));
        audio_uart_page_event_calculate_489546(&title_size, title, audio_uart_ring_primary_head_cell, 0, 0,
                                               LV_COORD_MAX, 0u);
        line_h = title_size.y < 0x19 ? 0x18 : title_size.y;
        audio_uart_page_event_calculate_489546(&hint_size, hint, audio_uart_ring_primary_head_cell, 0, 0,
                                               CONTAINER_W, 0u);
        if (hint_size.x > CONTAINER_W)
            hint_size.x = CONTAINER_W;
        top = (FRAME_H - (hint_size.y + line_h + 4)) / 2;
        left = (CONTAINER_W - (title_size.x + gap + 0x18)) / 2;

        g2_stock_no_data_icon = audio_uart_page_498668(g2_stock_ext_container_frame);
        audio_uart_page_43f4c0(g2_stock_no_data_icon, 0x18, 0x18);
        audio_uart_page_43f09a(g2_stock_no_data_icon, left, (line_h - 0x18) / 2 + top);
        audio_uart_page_498680(g2_stock_no_data_icon, g2_stock_icon_no_data);

        g2_stock_no_data_title = audio_uart_page_499416(g2_stock_ext_container_frame);
        audio_uart_page_43f4c0(g2_stock_no_data_title, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        audio_uart_page_43f09a(g2_stock_no_data_title, gap + left + 0x18, (line_h - title_size.y) / 2 + top);
        audio_uart_page_44145a(g2_stock_no_data_title, LV_TEXT_ALIGN_LEFT, 0u);
        audio_uart_page_44143e(g2_stock_no_data_title, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(g2_stock_no_data_title, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_49942e(g2_stock_no_data_title, title);

        g2_stock_no_data_hint = audio_uart_page_499416(g2_stock_ext_container_frame);
        audio_uart_page_43f4c0(g2_stock_no_data_hint, hint_size.x, LV_SIZE_CONTENT);
        audio_uart_page_43f09a(g2_stock_no_data_hint, (CONTAINER_W - hint_size.x) / 2, line_h + top + 4);
        audio_uart_page_44145a(g2_stock_no_data_hint, LV_TEXT_ALIGN_CENTER, 0u);
        audio_uart_page_44143e(g2_stock_no_data_hint, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(g2_stock_no_data_hint, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_49942e(g2_stock_no_data_hint, hint);
    } else {
        stock_scroll_load_stock_data_4ea800(c0, 0u);
        if (stock_page_get_count_4e9fd6() > 3u)
            stock_scroll_load_stock_data_4ea800(c1, 1u);
        if (stock_page_get_count_4e9fd6() > 6u)
            stock_scroll_load_stock_data_4ea800(c2, 2u);
        update_separator_lines_visibility_4ed058(c0, 0u);
        update_separator_lines_visibility_4ed058(c1, 1u);
        update_separator_lines_visibility_4ed058(c2, 2u);
        if (g2_stock_container_index > 0) {
            int32_t y = g2_stock_container_index * CONTAINER_H;

            audio_terminal_display_status_44ea04(g2_stock_ext_container_frame, y, 0u);
            log2(4u, page_fn, 0x45du, page_scrolled, page_scrolled_short, (uint32_t)y,
                 (uint32_t)g2_stock_container_index);
        }
        log0(4u, page_fn, 0x460u, page_loaded, page_loaded_short);
    }
    stock_switch_to_expanded_container_4ed52e();
    log1(3u, page_fn, 0x4b8u, page_created, page_created_short, stock_page_get_count_4e9fd6());
    return 0;
}

/* Opens the expanded stock page: (re)creates the input fifo, marks the page
 * active and builds it. Returns 0, or -1 on failure. */
int32_t stock_ext_Widget_init_4ebdfc(void *parent)
{
    if (parent == NULL) {
        log0(1u, init_fn, 0x4c3u, page_null, page_null_short);
        return -1;
    }
    if (g2_stock_ext_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_stock_ext_fifo);
        g2_stock_ext_fifo = NULL;
    }
    g2_stock_ext_fifo = ui_common_api_fn_00509c1c();
    if (g2_stock_ext_fifo == NULL) {
        log0(1u, init_fn, 0x4cfu, init_fifo_failed, init_fifo_failed_short);
        return -1;
    }
    g2_stock_ext_page_flag = 1u;
    g2_stock_scroll.is_animating = 0u;
    (void)stock_ext_WidgetPage_Create_4eb7b8(parent);
    (void)page_state_sync_stock_expanded_50012e(stock_get_container_index_4ebf20() + 1u);
    log0(3u, init_fn, 0x4d9u, init_ok, init_ok_short);
    return 0;
}
