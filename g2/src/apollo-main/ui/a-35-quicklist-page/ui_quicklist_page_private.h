/* Private declarations shared by the a-35 QuickList page units, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c.
 *
 * RAM layout (2.2.6.10):
 *   0x2012a72c  g2_quicklist_ui_data   0x2e50 bytes, UI copy of the list (40 rows of 296 bytes)
 *   0x201303cc  completed-UID cache    40 x 16 bytes + u16 count (0x288 bytes)
 *   0x20130654  temp completed cache   same layout, merged into the completed cache
 *   0x2006e370  row object table       40 x 16 bytes, word 0 = lv_obj_t * of the row
 */
#ifndef G2_UI_QUICKLIST_PAGE_PRIVATE_H
#define G2_UI_QUICKLIST_PAGE_PRIVATE_H

#include <stdint.h>
#include <stddef.h>

#define QL_MAX_ITEMS 40u
#define QL_SCREEN_W 0x240
#define QL_SCREEN_H 0x120

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_ANIM_OFF 0u

/* Values of g2_quicklist_border_state_2007503f. */
enum {
    QL_BORDER_FULL = 0u,    /* focus border spans the whole widget */
    QL_BORDER_ITEM = 2u,    /* border shrunk to the focused row */
    QL_BORDER_MOVING = 4u,  /* focus move animation running */
};

/* Data request event types (quicklist_send_data_request_event). */
enum {
    QL_REQUEST_UP = 1u,
    QL_REQUEST_DOWN = 2u,
};

/* One QuickList row as copied into the UI table (296 bytes). */
typedef struct {
    uint8_t data[0x10c];   /* +0x000 title, flags, text */
    uint32_t uid;          /* +0x10c */
    uint8_t rest[0x18];    /* +0x110 */
} g2_quicklist_ui_item_t;
_Static_assert(sizeof(g2_quicklist_ui_item_t) == 296u, "quicklist UI row");

typedef struct {
    uint16_t count;                                   /* +0x0000 */
    uint8_t reserved_0002[6];
    g2_quicklist_ui_item_t items[QL_MAX_ITEMS];       /* +0x0008 */
    uint16_t pending_fade_count;                      /* +0x2e48 */
    uint8_t reserved_2e4a[3];
    uint8_t last_request_event;                       /* +0x2e4d */
    uint8_t pending_fade_type;                        /* +0x2e4e */
    uint8_t reserved_2e4f;
} g2_quicklist_ui_data_t;
_Static_assert(offsetof(g2_quicklist_ui_data_t, pending_fade_count) == 0x2e48u, "pending count");
_Static_assert(offsetof(g2_quicklist_ui_data_t, last_request_event) == 0x2e4du, "request event");
_Static_assert(sizeof(g2_quicklist_ui_data_t) == 0x2e50u, "quicklist UI data");

/* Completed-UID cache entry; the 64-bit word is forwarded to the app as is. */
typedef struct {
    uint32_t uid;          /* +0x0 */
    uint32_t reserved;     /* +0x4 */
    uint64_t stamp;        /* +0x8 */
} g2_quicklist_uid_entry_t;
_Static_assert(sizeof(g2_quicklist_uid_entry_t) == 16u, "uid entry");

typedef struct {
    g2_quicklist_uid_entry_t entries[QL_MAX_ITEMS];   /* +0x000 */
    uint16_t count;                                   /* +0x280 */
    uint8_t reserved_282[6];
} g2_quicklist_uid_cache_t;
_Static_assert(offsetof(g2_quicklist_uid_cache_t, count) == 0x280u, "uid cache count");
_Static_assert(sizeof(g2_quicklist_uid_cache_t) == 0x288u, "uid cache");

typedef struct {
    void *obj;             /* +0x0 row container */
    uint8_t rest[12];
} g2_quicklist_row_t;
_Static_assert(sizeof(g2_quicklist_row_t) == 16u, "row object entry");

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

typedef void (*g2_lv_anim_ready_cb_t)(void *anim);

/* Page state. */
extern g2_quicklist_ui_data_t g2_quicklist_ui_data_2012a72c;     /* RAM 0x2012a72c */
extern g2_quicklist_uid_cache_t g2_quicklist_completed_201303cc; /* RAM 0x201303cc */
extern g2_quicklist_uid_cache_t g2_quicklist_temp_cache_20130654;/* RAM 0x20130654 */
extern g2_quicklist_row_t g2_quicklist_rows_2006e370[QL_MAX_ITEMS]; /* RAM 0x2006e370 */
extern int32_t g2_quicklist_focus_index_200042c0;               /* RAM 0x200042c0 (initialised data) */
extern void *g2_quicklist_container_20074e00;                   /* RAM 0x20074e00 scroll container */
extern void *g2_quicklist_loading_20074e08;                     /* RAM 0x20074e08 loading row */
extern void *g2_quicklist_event_fifo_20074e14;                  /* RAM 0x20074e14 */
extern int32_t g2_quicklist_page_active_20074e1c;               /* RAM 0x20074e1c 1 = ext page shown */
extern int32_t g2_quicklist_anim_state_20074e20;                /* RAM 0x20074e20 1 scroll anim, 2 rebuild */
extern int32_t g2_quicklist_org_scroll_y_20074e24;              /* RAM 0x20074e24 */
extern uint64_t g2_quicklist_loading_tick_200741a0;             /* RAM 0x200741a0 */
extern uint64_t g2_quicklist_request_tick_200741a8;             /* RAM 0x200741a8 */
extern uint8_t g2_quicklist_border_state_2007503f;              /* RAM 0x2007503f */
extern uint8_t g2_quicklist_loading_shown_20075040;             /* RAM 0x20075040 */
extern void *g2_dashboard_focus_frame;                          /* RAM 0x20074b9c expanded-page parent */

/* Same TU, reconstructed here or separately. */
void lv_obj_set_style_pad_all_4f5068(void *obj, int32_t value, uint32_t selector);
void quicklist_page_reset_4f509a(uint8_t full);
uint8_t quicklist_is_leap_year_4f517c(uint32_t year);
uint8_t quicklist_date_relation_4f51aa(const void *now, const void *when);
uint8_t quicklist_format_timestamp_4f5366(int64_t seconds, uint8_t mode, char *out, int32_t out_len);
void quicklist_send_data_request_event_4f5fd0(uint8_t event_type);
uint8_t quicklist_need_data_request_4f61a0(uint8_t event_type);
uint8_t quicklist_can_send_data_request_4f61f4(void);
void quicklist_request_data_with_debounce_4f6282(uint8_t event_type);
int32_t quicklist_add_completed_uid_to_temp_cache_4f658c(uint32_t uid, uint64_t stamp);
int32_t quicklist_remove_completed_uid_from_temp_cache_4f6664(uint32_t uid);
int32_t quicklist_merge_temp_cache_to_completed_items_4f6770(void);
int32_t QuicklistInputEventHandler_4f6880(int32_t code, const void *e);
void scroll_container_anim_ready_cb_4f6a10(void *anim);
void quicklist_scroll_anim_exec_cb_4f6d50(void *obj, int32_t y);
int32_t quicklist_scroll_clamp_target_y_4f6d84(void *obj, int32_t target_y);
void quicklist_scroll_content_with_anim_ready_cb_4f6e6c(void *obj, int32_t target_y, int32_t time_ms,
                                                        g2_lv_anim_ready_cb_t ready_cb);
void quicklist_scroll_content_with_anim_4f6f9c(void *obj, int32_t target_y, int32_t time_ms);
void quicklist_get_item_geometry_4f6fc4(int32_t index, int32_t *x, int32_t *y, int32_t *w, int32_t *h);
void quicklist_ensure_item_visible_4f70a4(int32_t index);
void quicklist_show_loading_as_item_4f7180(uint8_t from_bottom);
void quicklist_loading_opa_exec_cb_4f73f8(void *obj, int32_t opa);
void quicklist_hide_loading_with_fade_ready_cb_to_new_item_4f7408(void *anim);
void quicklist_hide_loading_with_fade_ready_cb_4f7480(void *anim);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. Each unit defines module_tag/source_file. */
#define QL_LOG(level, fn, line, cflags, msg, msg_short, ...)                                        \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

#endif /* G2_UI_QUICKLIST_PAGE_PRIVATE_H */
