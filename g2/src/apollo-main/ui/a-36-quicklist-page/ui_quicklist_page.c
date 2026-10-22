/* QuickList dashboard widget page: border/focus animations, loading row, completion toggling,
 * main-tile preview, expanded ("ext") page item list and the ext event handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c (log tag "quicklist.page").
 * Native 0x4f74f8..0x4f9aef (rows of segment a-36 plus the unlisted 0x4f78cc
 * quicklist_border_fade_in_ready_cb); literal pools 0x4f7ae0..0x4f7ae3, 0x4f7c04..0x4f7c0f,
 * 0x4f7c90..0x4f7caf, 0x4f7f04..0x4f7f17, 0x4f8090..0x4f809f, 0x4f81d4..0x4f81ef,
 * 0x4f8294..0x4f8297, 0x4f8320..0x4f8347, 0x4f84b8..0x4f84cb, 0x4f8610..0x4f8643,
 * 0x4f8870..0x4f8877, 0x4f88a4..0x4f891b, 0x4f8fbc..0x4f8ffb, 0x4f92e0..0x4f92ef,
 * 0x4f9344..0x4f9367, 0x4f9468..0x4f9483 and the shared pools from 0x4f9af0 on.
 *
 * The expanded page (built by Quicklist_ext_WidgetPage_Create 0x4fac74) is a scrolling list
 * container (RAM 0x20074e00) of up to 40 item rows, each {row container, check icon, title
 * label, optional time label}, a white focus border (0x20074e04) drawn over the focused row
 * and a hidden "loading" row (0x20074e08) shown while more items are requested. The border
 * state machine (0x2007503f): 0 full screen, 1 shrinking to an item, 2 on an item, 3 expanding
 * to full screen (then the page closes), 4 moving between items. Input arriving while an
 * animation runs (busy flag 0x20074e20) is queued as 5-byte records in the ext fifo and replayed
 * by scroll_container_anim_ready_cb (0x4f6a10). Event codes: 0x0a click (toggle completion),
 * 0x44/0x45 next/previous item, 0x46 ignored, 0x47 rebuild page (queued reflash), 0x48 double
 * click (expand and close), 0x49 dashboard fade-out. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define QL_MAX_ITEMS 40
#define QL_TITLE_LEN 0xc9
#define QL_TIME_TEXT_LEN 0x40

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_CLICKABLE 0x02u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u /* LVGL 9.3 bit 16 */
#define LV_PART_MAIN 0u
#define LV_PART_SCROLLBAR 0x10000u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_ALIGN_TOP_LEFT 1u
#define LV_ALIGN_TOP_MID 2u
#define LV_ALIGN_CENTER 9u
#define LV_ALIGN_OUT_BOTTOM_LEFT 13u
#define LV_ALIGN_OUT_BOTTOM_MID 14u
#define LV_ALIGN_OUT_RIGHT_TOP 19u
#define LV_ALIGN_OUT_RIGHT_MID 20u
#define LV_LABEL_LONG_WRAP 0u
#define LV_LABEL_LONG_DOT 1u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_OPA_TRANSP 0u
#define LV_OPA_COVER 0xffu
#define QL_COMPLETED_OPA 0x30u
#define QL_SCROLLBAR_FOCUS_OPA 0x20u

#define QL_BORDER_FULL 0u
#define QL_BORDER_SHRINKING 1u
#define QL_BORDER_ON_ITEM 2u
#define QL_BORDER_EXPANDING 3u
#define QL_BORDER_MOVING 4u

#define QL_FOCUS_PAST_END (-1)
#define QL_FOCUS_BEFORE_START (-2)

#define QL_MSG_INPUT 0u
#define QL_MSG_DASHBOARD 1u
#define QL_MSG_REFLASH 5u

#define QL_EVT_CLICK 0x0au
#define QL_EVT_NEXT 0x44u
#define QL_EVT_PREV 0x45u
#define QL_EVT_IGNORED 0x46u
#define QL_EVT_REBUILD 0x47u
#define QL_EVT_DOUBLE_CLICK 0x48u
#define QL_EVT_FADEOUT 0x49u

#define QL_REQUEST_DIR_PREV 1u
#define QL_REQUEST_DIR_NEXT 2u
#define QL_REQUEST_DEBOUNCE_MS 2000u

#define QL_ADD_UP 2u   /* quicklist_prepare_fade_animation_for_new_item operation codes */
#define QL_ADD_DOWN 3u

/* One quicklist record (0x128 bytes; filled by audio_quicklist_copy_record_4f55e0). */
typedef struct {
    char title[QL_TITLE_LEN];         /* +0x000 */
    char time_text[QL_TIME_TEXT_LEN]; /* +0x0c9 formatted by quicklist_format_timestamp_4f5366 */
    uint8_t reserved_109[3];
    uint32_t uid;                     /* +0x10c */
    uint32_t field_110;               /* +0x110 */
    uint32_t reserved_114;
    int64_t timestamp;                /* +0x118 shown when > 0 */
    uint8_t time_kind;                /* +0x120 */
    uint8_t completed;                /* +0x121 */
    uint8_t reserved_122[6];
} g2_quicklist_item_t;
_Static_assert(offsetof(g2_quicklist_item_t, uid) == 0x10c, "item uid");
_Static_assert(offsetof(g2_quicklist_item_t, timestamp) == 0x118, "item timestamp");
_Static_assert(offsetof(g2_quicklist_item_t, completed) == 0x121, "item completed");
_Static_assert(sizeof(g2_quicklist_item_t) == 0x128, "item record");

/* RAM 0x2012a72c, guarded by quicklist_lock_storage. */
typedef struct {
    uint16_t count;                            /* +0x0000 */
    uint8_t reserved_2[6];
    g2_quicklist_item_t item[QL_MAX_ITEMS];    /* +0x0008 */
    uint16_t reflash_value;                    /* +0x2e48 latched from a REFLASH record */
    uint8_t reserved_2e4a[4];
    uint8_t reflash_kind;                      /* +0x2e4e */
} g2_quicklist_storage_t;
_Static_assert(offsetof(g2_quicklist_storage_t, reflash_value) == 0x2e48, "storage reflash");
_Static_assert(offsetof(g2_quicklist_storage_t, reflash_kind) == 0x2e4e, "storage reflash kind");

/* RAM 0x201303cc: completed UIDs awaiting upload; count at +0x280. */
typedef struct {
    uint8_t entries[0x280];
    uint16_t count; /* +0x280 */
} g2_quicklist_completed_t;
_Static_assert(offsetof(g2_quicklist_completed_t, count) == 0x280, "completed count");

/* Widgets of one row of the expanded page (RAM 0x2006e370, 40 entries). */
typedef struct {
    void *container; /* +0x0 */
    void *icon;      /* +0x4 check box image */
    void *title;     /* +0x8 */
    void *time;      /* +0xc */
} g2_quicklist_row_t;
_Static_assert(sizeof(g2_quicklist_row_t) == 0x10, "row widgets");

typedef struct {
    void *tile;
    void *frame;
} g2_dashboard_tile_t;

/* generic_animation config / handle (ui/a-10-generic-animation). */
typedef struct {
    const void *const *frames; /* +0x00 */
    uint32_t frame_count;      /* +0x04 */
    uint32_t period_ms;        /* +0x08 */
    uint8_t mode;              /* +0x0c */
    uint8_t reserved_0d[3];
    int32_t width;             /* +0x10 */
    int32_t height;            /* +0x14 */
    uint8_t color_a[3];        /* +0x18 */
    uint8_t opa_a;             /* +0x1b */
    uint8_t bg_color[3];       /* +0x1c */
    uint8_t bg_opa;            /* +0x1f */
} g2_generic_animation_config_t;
_Static_assert(sizeof(g2_generic_animation_config_t) == 0x20, "animation config");

typedef struct {
    void *image;               /* +0x00 */
    uint8_t reserved_04[0x14];
    uint8_t running;           /* +0x18 */
} g2_generic_animation_t;

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stack frame. */
typedef void (*g2_lv_anim_exec_cb_t)(void *var, int32_t value);
typedef void (*g2_lv_anim_completed_cb_t)(void *anim);
typedef struct {
    void *var;                              /* +0x00 */
    g2_lv_anim_exec_cb_t exec_cb;           /* +0x04 */
    void *custom_exec_cb;                   /* +0x08 */
    void *start_cb;                         /* +0x0c */
    g2_lv_anim_completed_cb_t completed_cb; /* +0x10 */
    void *deleted_cb;                       /* +0x14 */
    void *get_value_cb;                     /* +0x18 */
    void *user_data;                        /* +0x1c */
    int32_t (*path_cb)(const void *);       /* +0x20 */
    int32_t start_value;                    /* +0x24 */
    int32_t current_value;                  /* +0x28 */
    int32_t end_value;                      /* +0x2c */
    int32_t duration;                       /* +0x30 */
    uint8_t rest[0x2c];                     /* +0x34 */
} g2_lv_anim_t;
_Static_assert(offsetof(g2_lv_anim_t, duration) == 0x30, "lv_anim_t duration");
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

typedef struct {
    uint8_t b[8];
} g2_quicklist_request_msg_t;

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag);    /* lv_obj_has_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);               /* lv_obj_is_valid */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                       /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                       /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);            /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                       /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                                  /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                                  /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                           /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                      /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern uint32_t lv_color_white_441094(void);
extern uint32_t lv_color_black_4410a6(void);
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);         /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);         /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);         /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);         /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);    /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);      /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);    /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);         /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);         /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);         /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);         /* shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t sel);         /* shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t sel);         /* shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);         /* shadow_spread */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);    /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);      /* text_opa */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel);    /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);         /* radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);              /* lv_obj_delete */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                   /* lv_obj_set_scrollbar_mode */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                           /* lv_obj_get_scroll_y */
extern void audio_terminal_display_status_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);                    /* lv_anim_init */
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);            /* lv_anim_start */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_page_498668(void *parent);                              /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);               /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);              /* lv_label_set_text */
extern void *audio_uart_page_layout_499678(void *label, uint32_t mode);         /* lv_label_set_long_mode */

/* Localisation, memory, RTOS, transport. */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);     /* localized text */
extern uint32_t audio_uart_page_460084(const char *key);                        /* i18n index of key */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern uint32_t osKernelGetTickCount(void);                                     /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                                /* 0x45a568 */
extern uint32_t audio_log_wake_allowed(void);                                   /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern void audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                              uint32_t flags);                  /* 0x464bb2 */
extern uint32_t audio_uart_ring_rtc_refresh(void); /* service_time_rtc_refresh 0x44a1ea: epoch s */
extern uint32_t audio_quicklist_refresh_lock_4ffac8(void);   /* quicklist_lock_storage */
extern void audio_quicklist_refresh_unlock_4ffb26(void);     /* quicklist_unlock_storage */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push, 0 ok */

/* Generic frame animation (ui/a-10-generic-animation). */
extern g2_generic_animation_t *generic_animation_create_463c68(void *parent,
                                                               const g2_generic_animation_config_t *config);
extern void generic_animation_destroy_463e1c(g2_generic_animation_t *anim, uint8_t delete_image);
extern void generic_animation_start_463ea6(g2_generic_animation_t *anim);
extern void generic_animation_stop_463eee(g2_generic_animation_t *anim);
extern void generic_animation_update_463f34(g2_generic_animation_t *anim);

/* Rest of ui_quicklist_page.c and its helpers. */
extern uint8_t lv_obj_get_style_bg_opa_4f5050(void *obj, uint32_t part);
extern uint8_t lv_obj_get_style_opa_4f505c(void *obj, uint32_t part);
extern void lv_obj_set_style_pad_all_4f5068(void *obj, int32_t v, uint32_t sel);
extern int32_t quicklist_text_line_count_4f50d6(const char *text, const void *font, int32_t max_width,
                                                int32_t letter_space, int32_t line_space,
                                                int32_t max_lines, int32_t *out_height);
extern uint8_t quicklist_format_timestamp_4f5366(int64_t seconds, uint8_t mode, char *out, int32_t out_len);
extern void audio_quicklist_refresh_pending_4f5596(void);
extern uint8_t quicklist_need_data_request_4f61a0(uint8_t direction);
extern void quicklist_request_data_with_debounce_4f6282(uint8_t direction);
extern uint32_t audio_quicklist_aux_update_4f6328(void); /* quicklist_send_completed_uids: 0 ok, -2 BT down */
extern int32_t quicklist_add_completed_uid_to_temp_cache_4f658c(uint32_t uid, uint64_t stamp);
extern int32_t quicklist_remove_completed_uid_from_temp_cache_4f6664(uint32_t uid);
extern int32_t quicklist_merge_temp_cache_to_completed_items_4f6770(void);
extern void scroll_container_anim_ready_cb_4f6a10(void *anim);
extern int32_t quicklist_scroll_clamp_target_y_4f6d84(void *obj, int32_t y);
extern void quicklist_scroll_content_with_anim_ready_cb_4f6e6c(void *obj, int32_t y, int32_t time_ms,
                                                      g2_lv_anim_completed_cb_t ready_cb);
extern void quicklist_get_item_geometry_4f6fc4(int32_t index, int32_t *x, int32_t *y, int32_t *w,
                                                  int32_t *h);
extern void quicklist_show_loading_as_item_4f7180(uint8_t at_bottom);
extern void quicklist_loading_opa_exec_cb_4f73f8(void *obj, int32_t opa);
extern void quicklist_hide_loading_with_fade_ready_cb_to_new_item_4f7408(void *anim);
extern void quicklist_hide_loading_with_fade_ready_cb_4f7480(void *anim);
extern int32_t Quicklist_ext_WidgetPage_Create_4fac74(void *parent);
extern void quicklist_ext_widget_deinit_4faf20(void);
extern void quicklist_page_clean_4fb1a4(void *obj, uint8_t stop_loading);
extern void Dashboard_Fadeout_Anim_Start_4e8a90(void);
extern void dashboard_main_screen_data_event_4e8970(const uint8_t *data, uint32_t len);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Globals. */
extern uint32_t g2_quicklist_word_20074df8;          /* RAM 0x20074df8 widget_quicklist_init_flag */
extern void *g2_quicklist_container_20074e00;               /* RAM 0x20074e00 */
extern void *g2_quicklist_border;                       /* RAM 0x20074e04 */
extern void *g2_quicklist_loading_20074e08;                 /* RAM 0x20074e08 */
extern void *g2_quicklist_loading_label;                /* RAM 0x20074e0c */
extern g2_generic_animation_t *g2_quicklist_loading_anim; /* RAM 0x20074e10 */
extern void *g2_quicklist_event_fifo_20074e14;                     /* RAM 0x20074e14 quicklist_ext_fifo */
extern int32_t g2_quicklist_tile_index;                 /* RAM 0x20074e18 dashboard tile index */
extern int32_t g2_quicklist_page_active_20074e1c;       /* RAM 0x20074e1c */
extern int32_t g2_quicklist_anim_state_20074e20;        /* RAM 0x20074e20 0 idle, 1 animating, 2 rebuilding */
extern int32_t g2_quicklist_org_scroll_y_20074e24;              /* RAM 0x20074e24 */
extern uint8_t g2_quicklist_border_state_2007503f;               /* RAM 0x2007503f */
extern uint8_t g2_quicklist_loading_shown_20075040;             /* RAM 0x20075040 */
extern int32_t g2_quicklist_focus_index_200042c0;                 /* RAM 0x200042c0 */
extern uint64_t g2_quicklist_loading_tick_200741a0;         /* RAM 0x200741a0 */
extern g2_quicklist_row_t g2_quicklist_rows_2006e370[QL_MAX_ITEMS]; /* RAM 0x2006e370 */
extern g2_quicklist_storage_t g2_quicklist_ui_data_2012a72c;     /* RAM 0x2012a72c */
extern g2_quicklist_completed_t g2_quicklist_completed_201303cc; /* RAM 0x201303cc */
extern g2_dashboard_tile_t g2_dashboard_tiles[6];       /* RAM 0x200734bc */
extern void *g2_dashboard_focus_frame;                  /* RAM 0x20074b9c */
extern const void *audio_uart_ring_primary_head_cell;   /* RAM 0x200746dc: active lv_font_t * */

extern const uint8_t g2_img_quicklist_checked[];        /* ROM 0x772928 lv_image_dsc_t 24x24 */
extern const uint8_t g2_img_quicklist_unchecked[];      /* ROM 0x772944 lv_image_dsc_t 24x24 */
extern const uint8_t g2_img_quicklist_empty[];          /* ROM 0x7708ac lv_image_dsc_t 24x24 */
/* {frames = RAM 0x200042c4, 25 frames, 50 ms, loop, 24x24, colour fields 0xff000000/0}. */
extern const g2_generic_animation_config_t g2_quicklist_loading_anim_config; /* ROM 0x767bf0 */
/* Sync-interface "request quicklist data" message {0x05, 0x01, 0, 0, 0, 0} (6 bytes sent). */
extern const g2_quicklist_request_msg_t g2_quicklist_request_msg; /* ROM 0x78ed9c */

static const char ql_tag[] = "quicklist.page"; /* ROM 0x789e40 */
static const char ql_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c"; /* ROM 0x6f7538 */

static const char id_default_1[] = "ID_DASHBOARD_QUICKLIST_DEFAULT_1"; /* ROM 0x75caec */
static const char id_default_2[] = "ID_DASHBOARD_QUICKLIST_DEFAULT_2"; /* ROM 0x75cb10 */
static const char id_loading[] = "ID_DASHBOARD_QUICKLIST_LOADING";     /* ROM 0x767b10 */

static const char fn_expand_ready[] = "quicklist_border_expand_ready_cb"; /* ROM 0x75c9f0 */
static const char m_expand_done[] = "Border expand animation completed"; /* ROM 0x75ca14 */
static const char m_expand_done_s[] = "[quicklist.page]Border expand animation completed"; /* ROM 0x73033c */

static const char fn_move_ready[] = "quicklist_border_move_ready_cb"; /* ROM 0x767a10 */
static const char m_moved[] = "Border moved to item %d after scroll, starting fade in"; /* ROM 0x725ae0 */
static const char m_moved_s[] = "[quicklist.page]Border moved to item %d after scroll, starting fade in"; /* ROM 0x6fefb4 */

static const char fn_fade_in_ready[] = "quicklist_border_fade_in_ready_cb"; /* ROM 0x75ca38 */
static const char m_fade_in_done[] = "Border fade in completed"; /* ROM 0x774288 */
static const char m_fade_in_done_s[] = "[quicklist.page]Border fade in completed"; /* ROM 0x746380 */

static const char fn_fade_out_move[] = "quicklist_border_fade_out_move_ready_cb"; /* ROM 0x750d24 */
static const char m_height_limit[] = "Item exceeds height limit, adjusted scroll to: %d"; /* ROM 0x730370 */
static const char m_height_limit_s[] = "[quicklist.page]Item exceeds height limit, adjusted scroll to: %d"; /* ROM 0x707f10 */
static const char m_scroll_visible[] = "Scroll to make item %d visible: scroll from %d to %d"; /* ROM 0x725b18 */
static const char m_scroll_visible_s[] = "[quicklist.page]Scroll to make item %d visible: scroll from %d to %d"; /* ROM 0x6feffc */

static const char fn_shrink[] = "quicklist_border_shrink_to_item"; /* ROM 0x767a30 */
static const char m_shrink_bad[] = "Invalid item index %d for shrink"; /* ROM 0x75ca5c */
static const char m_shrink_bad_s[] = "[quicklist.page]Invalid item index %d for shrink"; /* ROM 0x7303a4 */

static const char fn_expand[] = "quicklist_border_expand_to_full"; /* ROM 0x767a50 */
static const char m_expanding[] = "Expanding border to full size"; /* ROM 0x767a70 */
static const char m_expanding_s[] = "[quicklist.page]Expanding border to full size"; /* ROM 0x73ad84 */

static const char fn_toggle[] = "quicklist_toggle_item_completion"; /* ROM 0x75ca80 */
static const char m_toggle_bad[] = "Invalid item index %d for toggle completion"; /* ROM 0x7463ac */
static const char m_toggle_bad_s[] = "[quicklist.page]Invalid item index %d for toggle completion"; /* ROM 0x71adf4 */
static const char m_widgets_null[] = "Item %d widgets are NULL"; /* ROM 0x7742a4 */
static const char m_widgets_null_s[] = "[quicklist.page]Item %d widgets are NULL"; /* ROM 0x7463d8 */
static const char m_completed[] = "Item %d marked as completed (UID: %u), added to temp cache"; /* ROM 0x71ae30 */
static const char m_completed_s[] = "[quicklist.page]Item %d marked as completed (UID: %u), added to temp cache"; /* ROM 0x6f761c */
static const char m_incomplete[] = "Item %d marked as incomplete (UID: %u), removed from temp cache"; /* ROM 0x711464 */
static const char m_incomplete_s[] = "[quicklist.page]Item %d marked as incomplete (UID: %u), removed from temp cache"; /* ROM 0x6f0c68 */

static const char fn_new_fade_ready[] = "quicklist_fade_in_anim_ready_cb"; /* ROM 0x767a90 */
static const char m_new_fade_done[] = "New item fade-in animation completed"; /* ROM 0x750d4c */
static const char m_new_fade_done_s[] = "[quicklist.page]New item fade-in animation completed"; /* ROM 0x725b50 */

static const char fn_offset[] = "quicklist_offset_all_items_down"; /* ROM 0x767ab0 */
static const char m_offset[] = "Offsetting all items down by %d pixels"; /* ROM 0x750d74 */
static const char m_offset_s[] = "[quicklist.page]Offsetting all items down by %d pixels"; /* ROM 0x725b88 */

static const char fn_focus_fade[] = "quicklist_animate_focus_items_fade_in"; /* ROM 0x750d9c */
static const char m_focus_bad[] = "Invalid target item index %d, skipping fade-in animation"; /* ROM 0x71ae6c */
static const char m_focus_bad_s[] = "[quicklist.page]Invalid target item index %d, skipping fade-in animation"; /* ROM 0x6f7668 */

static const char fn_prepare[] = "quicklist_prepare_fade_animation_for_new_item"; /* ROM 0x73adb4 */
static const char m_prepare[] =
    "Set new item %d opacity to 0 for fade animation (operation=%d, is_last=%d, added_count=%d)"; /* ROM 0x6e1e40 */
static const char m_prepare_s[] =
    "[quicklist.page]Set new item %d opacity to 0 for fade animation (operation=%d, is_last=%d, added_count=%d)"; /* ROM 0x6d802c */
static const char m_prepare_bad[] =
    "Invalid target_item_index %d for fade animation (operation=%d, added_count=%d)"; /* ROM 0x6f0cb8 */
static const char m_prepare_bad_s[] =
    "[quicklist.page]Invalid target_item_index %d for fade animation (operation=%d, added_count=%d)"; /* ROM 0x6dee54 */

static const char fn_loading_init[] = "quicklist_init_loading_animation"; /* ROM 0x75caa4 */
static const char m_loading_fail[] = "Failed to create loading animation"; /* ROM 0x75cac8 */
static const char m_loading_fail_s[] = "[quicklist.page]Failed to create loading animation"; /* ROM 0x7303d8 */

static const char fn_exit[] = "quicklist_process_completed_items_on_exit"; /* ROM 0x746404 */
static const char m_exit[] = "Processing %d completed items on exit (merged %d from temp cache)"; /* ROM 0x707f54 */
static const char m_exit_s[] = "[quicklist.page]Processing %d completed items on exit (merged %d from temp cache)"; /* ROM 0x6eac54 */
static const char m_sent[] = "Successfully sent %d completed UIDs via Bluetooth"; /* ROM 0x73040c */
static const char m_sent_s[] = "[quicklist.page]Successfully sent %d completed UIDs via Bluetooth"; /* ROM 0x707f98 */
static const char m_bt_down[] = "Bluetooth not connected, keeping %d completed items for later"; /* ROM 0x7114a4 */
static const char m_bt_down_s[] = "[quicklist.page]Bluetooth not connected, keeping %d completed items for later"; /* ROM 0x6f0d08 */
static const char m_send_fail[] = "Failed to send completed UIDs, result: %d"; /* ROM 0x746430 */
static const char m_send_fail_s[] = "[quicklist.page]Failed to send completed UIDs, result: %d"; /* ROM 0x71aea8 */

static const char fn_remove[] = "quicklist_remove_completed_items_from_ui"; /* ROM 0x74645c */
static const char m_removed_one[] = "Removed completed item from UI: UID=%u, title='%.20s'"; /* ROM 0x725bc0 */
static const char m_removed_one_s[] = "[quicklist.page]Removed completed item from UI: UID=%u, title='%.20s'"; /* ROM 0x6ff044 */
static const char m_removed[] = "Removed %d completed items from UI, remaining: %d"; /* ROM 0x730440 */
static const char m_removed_s[] = "[quicklist.page]Removed %d completed items from UI, remaining: %d"; /* ROM 0x707fdc */

static const char fn_reflash[] = "Quicklist_Page_Reflash"; /* ROM 0x77d4d4 */
static const char m_widget_off[] = "widget_quicklist_init_flag == 0, return"; /* ROM 0x750dc4 */
static const char m_widget_off_s[] = "[quicklist.page]widget_quicklist_init_flag == 0, return"; /* ROM 0x725bf8 */
static const char m_fifo_push[] = "quicklist_ext_fifo is not empty, push event to fifo,code = %d"; /* ROM 0x7114e4 */
static const char m_fifo_push_s[] = "[quicklist.page]quicklist_ext_fifo is not empty, push event to fifo,code = %d"; /* ROM 0x6f0d58 */

static const char fn_main_init[] = "QuicklistWidget_MainPage_init"; /* ROM 0x767ad0 */
static const char m_displayed[] = "Displayed %d quicklist items"; /* ROM 0x767af0 */
static const char m_displayed_s[] = "[quicklist.page]Displayed %d quicklist items"; /* ROM 0x73ade4 */

static const char fn_ext_event[] = "quicklist_ext_event_handler"; /* ROM 0x7742c0 */
static const char m_ext_off[] = "quicklist_ext_widget_init_flag == 0, return"; /* ROM 0x746488 */
static const char m_ext_off_s[] = "[quicklist.page]quicklist_ext_widget_init_flag == 0, return"; /* ROM 0x71aee4 */
static const char m_len0[] = "len == 0, return"; /* ROM 0x784a2c */
static const char m_len0_s[] = "[quicklist.page]len == 0, return"; /* ROM 0x75cb34 */
static const char m_no_focus[] = "No focused item to toggle, border_state: %d, focus_item: %d"; /* ROM 0x71ad7c */
static const char m_no_focus_s[] = "[quicklist.page]No focused item to toggle, border_state: %d, focus_item: %d"; /* ROM 0x6f75d0 */
static const char m_unknown[] = "QuicklistWidget_event_handler: unknown event type: %d"; /* ROM 0x7259c8 */
static const char m_unknown_s[] = "[quicklist.page]QuicklistWidget_event_handler: unknown event type: %d"; /* ROM 0x6fee94 */

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

#define QL_LOG0(level, fn, line, msg, msg_s)                                                  \
    do {                                                                                      \
        if (audio_log_flags() & 2u)                                                           \
            audio_log_extended((level), ql_tag, ql_file, (fn), (line), (msg));                \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                             \
            (void)compress_log_output(LOG_FLAGS((level), 0), (msg_s), (msg_s));               \
    } while (0)

#define QL_LOG(level, fn, line, msg, msg_s, nargs, ...)                                       \
    do {                                                                                      \
        if (audio_log_flags() & 2u)                                                           \
            audio_log_extended((level), ql_tag, ql_file, (fn), (line), (msg), __VA_ARGS__);   \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                             \
            (void)compress_log_output(LOG_FLAGS((level), (nargs)), (msg_s), (msg_s),          \
                                      __VA_ARGS__);                                           \
    } while (0)

/* lv_obj_set_style_opa passed straight to lv_anim as exec_cb (stock 0x441489). */
#define QL_EXEC_SET_OPA ((g2_lv_anim_exec_cb_t)(uintptr_t)&audio_uart_display_audio_reset_441488)

void quicklist_loading_fade_4f74f8(uint8_t opa, int32_t duration, g2_lv_anim_completed_cb_t ready_cb);
void quicklist_loading_request_data_4f7590(void);
void quicklist_border_opa_exec_cb_4f7624(void *obj, int32_t opa);
void quicklist_border_fade_to_4f7634(uint8_t opa, int32_t duration, g2_lv_anim_completed_cb_t ready_cb);
void quicklist_scrollbar_opa_exec_cb_4f76a4(void *obj, int32_t opa);
void quicklist_scrollbar_fade_to_4f76b6(uint8_t opa, int32_t duration);
void quicklist_border_expand_ready_cb_4f770c(void *anim);
void quicklist_border_full_fade_out_ready_cb_4f7760(void *anim);
void quicklist_border_move_ready_cb_4f7794(void *anim);
void quicklist_hide_loading_finish_4f7860(void *anim);
void quicklist_border_fade_in_ready_cb_4f78cc(void *anim);
void quicklist_border_fade_out_move_ready_cb_4f7944(void *anim);
void quicklist_border_fade_out_edge_ready_cb_4f7aa2(void *anim);
void quicklist_border_shrink_to_item_4f7ae4(int32_t index);
void quicklist_border_expand_to_full_4f7b84(void);
void quicklist_focus_move_to_4f7c10(int32_t index);
void quicklist_toggle_item_completion_4f7cb0(int32_t index);
void quicklist_fade_in_anim_ready_cb_4f7eb0(void *anim);
void quicklist_offset_all_items_down_4f7f18(int32_t dy);
void quicklist_animate_focus_items_fade_in_4f7fa8(void);
void quicklist_prepare_fade_animation_for_new_item_4f80a0(uint8_t is_last, uint8_t operation,
                                                          int32_t added_count);
void quicklist_init_loading_animation_4f81f0(void);
void quicklist_loading_anim_destroy_4f8298(void);
void quicklist_loading_anim_start_4f82d0(void);
void quicklist_loading_anim_stop_4f82e4(void);
void quicklist_loading_anim_update_4f82f8(void);
void quicklist_process_completed_items_on_exit_4f8348(void);
void quicklist_remove_completed_items_from_ui_4f84cc(void);
int32_t Quicklist_Page_Reflash_4f8644(const uint8_t *data, uint32_t len);
int32_t quicklist_widget_tick_4f8878(void);
int32_t QuicklistWidget_MainPage_init_4f891c(int32_t tile_index);
int32_t quicklist_ext_event_handler_4f8ffc(const uint8_t *data, uint32_t len);
void quicklist_delete_item_objects_4f92f0(void);
void quicklist_create_loading_item_4f9368(void);
void quicklist_create_items_4f9484(void);

/* Fade the loading row's opacity to opa (stops the spinner first). */
void quicklist_loading_fade_4f74f8(uint8_t opa, int32_t duration, g2_lv_anim_completed_cb_t ready_cb)
{
    g2_lv_anim_t a;

    if (g2_quicklist_loading_20074e08 == NULL ||
        audio_terminal_ui_object_valid_43e2ea(g2_quicklist_loading_20074e08) == 0u ||
        audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) != 0u)
        return;
    g2_quicklist_anim_state_20074e20 = 1;
    g2_quicklist_loading_shown_20075040 = 0u;
    quicklist_loading_anim_stop_4f82e4();
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_quicklist_loading_20074e08;
    audio_uart_lv_anim_values_4506ce(&a, lv_obj_get_style_opa_4f505c(g2_quicklist_loading_20074e08, LV_PART_MAIN),
                                     opa);
    a.duration = duration;
    a.exec_cb = quicklist_loading_opa_exec_cb_4f73f8;
    if (ready_cb != NULL)
        a.completed_cb = ready_cb;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* While the loading row is visible, ask the phone for more items at most every 2 s. */
void quicklist_loading_request_data_4f7590(void)
{
    uint32_t now;
    g2_quicklist_request_msg_t msg;

    if (g2_quicklist_loading_20074e08 == NULL || g2_quicklist_loading_shown_20075040 == 0u ||
        audio_terminal_ui_object_valid_43e2ea(g2_quicklist_loading_20074e08) == 0u ||
        audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) != 0u)
        return;
    now = osKernelGetTickCount();
    if (g2_quicklist_loading_tick_200741a0 + QL_REQUEST_DEBOUNCE_MS < (uint64_t)now) {
        g2_quicklist_loading_tick_200741a0 = osKernelGetTickCount();
        if (audio_uart_device_role_get() == 1u && audio_log_wake_allowed() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
            msg = g2_quicklist_request_msg;
            audio_uart_master_display_refresh(1u, &msg, 6u, 0u);
        }
    }
}

void quicklist_border_opa_exec_cb_4f7624(void *obj, int32_t opa)
{
    if (obj != NULL)
        audio_uart_display_audio_reset_441488(obj, (uint8_t)opa, LV_PART_MAIN);
}

/* Fade the focus border's opacity to opa. */
void quicklist_border_fade_to_4f7634(uint8_t opa, int32_t duration, g2_lv_anim_completed_cb_t ready_cb)
{
    g2_lv_anim_t a;

    if (g2_quicklist_border == NULL || audio_terminal_ui_object_valid_43e2ea(g2_quicklist_border) == 0u)
        return;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_quicklist_border;
    audio_uart_lv_anim_values_4506ce(&a, lv_obj_get_style_opa_4f505c(g2_quicklist_border, LV_PART_MAIN), opa);
    a.duration = duration;
    a.exec_cb = quicklist_border_opa_exec_cb_4f7624;
    if (ready_cb != NULL)
        a.completed_cb = ready_cb;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void quicklist_scrollbar_opa_exec_cb_4f76a4(void *obj, int32_t opa)
{
    if (obj != NULL)
        audio_uart_page_44129e(obj, (uint8_t)opa, LV_PART_SCROLLBAR);
}

/* Fade the list container's scrollbar (bg_opa of LV_PART_SCROLLBAR) to opa. */
void quicklist_scrollbar_fade_to_4f76b6(uint8_t opa, int32_t duration)
{
    g2_lv_anim_t a;
    uint8_t from;

    if (g2_quicklist_container_20074e00 == NULL)
        return;
    from = lv_obj_get_style_bg_opa_4f5050(g2_quicklist_container_20074e00, LV_PART_SCROLLBAR);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_quicklist_container_20074e00;
    audio_uart_lv_anim_values_4506ce(&a, from, opa);
    a.duration = duration;
    a.exec_cb = quicklist_scrollbar_opa_exec_cb_4f76a4;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void quicklist_border_expand_ready_cb_4f770c(void *anim)
{
    (void)anim;
    g2_quicklist_border_state_2007503f = QL_BORDER_FULL;
    QL_LOG0(4u, fn_expand_ready, 0x94eu, m_expand_done, m_expand_done_s);
    quicklist_ext_widget_deinit_4faf20();
}

/* Border faded out for expand: resize it to the full 576x288 screen and fade it back in. */
void quicklist_border_full_fade_out_ready_cb_4f7760(void *anim)
{
    (void)anim;
    audio_uart_page_43f09a(g2_quicklist_border, 0, 0);
    audio_uart_page_43f4c0(g2_quicklist_border, 0x240, 0x120);
    quicklist_border_fade_to_4f7634(LV_OPA_COVER, 100, quicklist_border_expand_ready_cb_4f770c);
}

/* Border faded out: move it over the focused item (12 px left inset, 8 px top inset in the
 * scrolled list) and fade it back in. */
void quicklist_border_move_ready_cb_4f7794(void *anim)
{
    int32_t focus = g2_quicklist_focus_index_200042c0;
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;

    (void)anim;
    if (g2_quicklist_loading_20074e08 != NULL) {
        audio_uart_page_43ded4(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN);
        audio_uart_page_43f142(g2_quicklist_loading_20074e08, 0);
        audio_uart_display_audio_reset_441488(g2_quicklist_loading_20074e08, LV_OPA_COVER, LV_PART_MAIN);
    }
    audio_uart_page_43f66c(g2_quicklist_container_20074e00);
    quicklist_get_item_geometry_4f6fc4(focus, &x, &y, &w, &h);
    y -= audio_uart_lv_obj_y_44e498(g2_quicklist_container_20074e00);
    audio_uart_page_43f09a(g2_quicklist_border, x + 12, y + 8);
    audio_uart_page_43f4c0(g2_quicklist_border, w, h);
    quicklist_border_fade_to_4f7634(LV_OPA_COVER, 100, quicklist_border_fade_in_ready_cb_4f78cc);
    QL_LOG(4u, fn_move_ready, 0x983u, m_moved, m_moved_s, 1, focus);
}

/* Completion of the scroll that brings the focused item into view (also reached after the
 * loading row / new-item fade): resolve the past-end and before-start focus markers, then move
 * the border. */
void quicklist_hide_loading_finish_4f7860(void *anim)
{
    if (g2_quicklist_focus_index_200042c0 == QL_FOCUS_PAST_END) {
        g2_quicklist_focus_index_200042c0 = (int32_t)g2_quicklist_ui_data_2012a72c.count - 1;
        quicklist_border_move_ready_cb_4f7794(anim);
    } else if (g2_quicklist_focus_index_200042c0 == QL_FOCUS_BEFORE_START) {
        g2_quicklist_focus_index_200042c0 = 0;
        quicklist_offset_all_items_down_4f7f18(-g2_quicklist_org_scroll_y_20074e24);
        audio_terminal_display_status_44ea04(g2_quicklist_container_20074e00, 0, 0u);
        quicklist_border_move_ready_cb_4f7794(anim);
    } else {
        quicklist_border_move_ready_cb_4f7794(anim);
    }
    g2_quicklist_org_scroll_y_20074e24 = 0;
}

/* Not in the function inventory (gap 0x4f78be..0x4f7944); completion of the border fade-in. */
void quicklist_border_fade_in_ready_cb_4f78cc(void *anim)
{
    g2_quicklist_border_state_2007503f = QL_BORDER_ON_ITEM;
    g2_quicklist_anim_state_20074e20 = 0;
    QL_LOG0(4u, fn_fade_in_ready, 0x9a1u, m_fade_in_done, m_fade_in_done_s);
    scroll_container_anim_ready_cb_4f6a10(anim);
}

/* Border faded out before moving: scroll the list so the new focus item is fully visible
 * (keeping its bottom within 272 px), or move the border directly when it already is. */
void quicklist_border_fade_out_move_ready_cb_4f7944(void *anim)
{
    int32_t focus = g2_quicklist_focus_index_200042c0;
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    int32_t view_h;
    int32_t scroll_y;
    int32_t target;
    int32_t clamped;
    bool need_scroll;

    if (g2_quicklist_container_20074e00 == NULL) {
        g2_quicklist_anim_state_20074e20 = 0;
        return;
    }
    quicklist_get_item_geometry_4f6fc4(focus, &x, &y, &w, &h);
    view_h = audio_uart_lv_obj_height_43fdda(g2_quicklist_container_20074e00);
    scroll_y = audio_uart_lv_obj_y_44e498(g2_quicklist_container_20074e00);
    target = scroll_y;
    need_scroll = false;
    if (y - scroll_y < 0) {
        target = y;
        need_scroll = true;
    } else if (view_h < h + (y - scroll_y)) {
        target = h + y - view_h;
        need_scroll = true;
    }
    if (h + y - scroll_y > 0x110) {
        target = h + y - 0x110;
        need_scroll = true;
        QL_LOG(4u, fn_fade_out_move, 0x9d0u, m_height_limit, m_height_limit_s, 1, target);
    }
    if (need_scroll) {
        clamped = quicklist_scroll_clamp_target_y_4f6d84(g2_quicklist_container_20074e00, target);
        quicklist_scroll_content_with_anim_ready_cb_4f6e6c(g2_quicklist_container_20074e00, clamped, 100,
                                                  quicklist_hide_loading_finish_4f7860);
        QL_LOG(4u, fn_fade_out_move, 0x9d9u, m_scroll_visible, m_scroll_visible_s, 3, focus, scroll_y,
               clamped);
    } else {
        quicklist_border_move_ready_cb_4f7794(anim);
    }
}

/* Border faded out while stepping past either end of the list: show the loading row there. */
void quicklist_border_fade_out_edge_ready_cb_4f7aa2(void *anim)
{
    (void)anim;
    if (g2_quicklist_container_20074e00 == NULL) {
        g2_quicklist_anim_state_20074e20 = 0;
    } else if (g2_quicklist_focus_index_200042c0 == QL_FOCUS_PAST_END) {
        quicklist_show_loading_as_item_4f7180(1u);
    } else if (g2_quicklist_focus_index_200042c0 == QL_FOCUS_BEFORE_START) {
        quicklist_show_loading_as_item_4f7180(0u);
    }
}

void quicklist_border_shrink_to_item_4f7ae4(int32_t index)
{
    if (g2_quicklist_border == NULL || g2_quicklist_anim_state_20074e20 != 0)
        return;
    if (index < 0 || index >= (int32_t)g2_quicklist_ui_data_2012a72c.count) {
        QL_LOG(2u, fn_shrink, 0xa0au, m_shrink_bad, m_shrink_bad_s, 1, index);
        return;
    }
    g2_quicklist_border_state_2007503f = QL_BORDER_SHRINKING;
    g2_quicklist_anim_state_20074e20 = 1;
    g2_quicklist_focus_index_200042c0 = index;
    quicklist_border_fade_to_4f7634(LV_OPA_TRANSP, 100, quicklist_border_move_ready_cb_4f7794);
    quicklist_scrollbar_fade_to_4f76b6(QL_SCROLLBAR_FOCUS_OPA, 250);
}

void quicklist_border_expand_to_full_4f7b84(void)
{
    if (g2_quicklist_border == NULL || g2_quicklist_anim_state_20074e20 != 0)
        return;
    g2_quicklist_border_state_2007503f = QL_BORDER_EXPANDING;
    g2_quicklist_anim_state_20074e20 = 1;
    QL_LOG0(4u, fn_expand, 0xa4eu, m_expanding, m_expanding_s);
    quicklist_border_fade_to_4f7634(LV_OPA_TRANSP, 100, quicklist_border_full_fade_out_ready_cb_4f7760);
    quicklist_scrollbar_fade_to_4f76b6(LV_OPA_TRANSP, 250);
}

/* Move the border from the focused item to index (-1 past the end, -2 before the start). */
void quicklist_focus_move_to_4f7c10(int32_t index)
{
    if (g2_quicklist_border == NULL || g2_quicklist_anim_state_20074e20 != 0 ||
        g2_quicklist_border_state_2007503f != QL_BORDER_ON_ITEM)
        return;
    g2_quicklist_anim_state_20074e20 = 1;
    g2_quicklist_border_state_2007503f = QL_BORDER_MOVING;
    if (index >= (int32_t)g2_quicklist_ui_data_2012a72c.count) {
        g2_quicklist_focus_index_200042c0 = QL_FOCUS_PAST_END;
        quicklist_border_fade_to_4f7634(LV_OPA_TRANSP, 100, quicklist_border_fade_out_edge_ready_cb_4f7aa2);
    } else if (index < 0) {
        g2_quicklist_focus_index_200042c0 = QL_FOCUS_BEFORE_START;
        quicklist_border_fade_to_4f7634(LV_OPA_TRANSP, 100, quicklist_border_fade_out_edge_ready_cb_4f7aa2);
    } else {
        g2_quicklist_focus_index_200042c0 = index;
        quicklist_border_fade_to_4f7634(LV_OPA_TRANSP, 100, quicklist_border_fade_out_move_ready_cb_4f7944);
    }
}

void quicklist_toggle_item_completion_4f7cb0(int32_t index)
{
    g2_quicklist_item_t *item;
    uint32_t uid;
    uint8_t completed;

    if (index < 0 || index >= (int32_t)g2_quicklist_ui_data_2012a72c.count) {
        QL_LOG(2u, fn_toggle, 0xac1u, m_toggle_bad, m_toggle_bad_s, 1, index);
        return;
    }
    if (g2_quicklist_rows_2006e370[index].container == NULL || g2_quicklist_rows_2006e370[index].icon == NULL) {
        QL_LOG(2u, fn_toggle, 0xac7u, m_widgets_null, m_widgets_null_s, 1, index);
        return;
    }
    item = &g2_quicklist_ui_data_2012a72c.item[index];
    completed = (uint8_t)(item->completed == 0u);
    (void)audio_quicklist_refresh_lock_4ffac8();
    item->completed = completed;
    audio_quicklist_refresh_unlock_4ffb26();
    if (completed != 0u) {
        audio_uart_page_498680(g2_quicklist_rows_2006e370[index].icon, g2_img_quicklist_checked);
        audio_uart_display_audio_reset_441488(g2_quicklist_rows_2006e370[index].container, QL_COMPLETED_OPA,
                                              LV_PART_MAIN);
        uid = item->uid;
        (void)quicklist_add_completed_uid_to_temp_cache_4f658c(uid, audio_uart_ring_rtc_refresh());
        QL_LOG(4u, fn_toggle, 0xadeu, m_completed, m_completed_s, 2, index, uid);
    } else {
        audio_uart_page_498680(g2_quicklist_rows_2006e370[index].icon, g2_img_quicklist_unchecked);
        audio_uart_display_audio_reset_441488(g2_quicklist_rows_2006e370[index].container, LV_OPA_COVER,
                                              LV_PART_MAIN);
        uid = item->uid;
        (void)quicklist_remove_completed_uid_from_temp_cache_4f6664(uid);
        QL_LOG(4u, fn_toggle, 0xae8u, m_incomplete, m_incomplete_s, 2, index, uid);
    }
}

void quicklist_fade_in_anim_ready_cb_4f7eb0(void *anim)
{
    g2_quicklist_anim_state_20074e20 = 0;
    QL_LOG0(4u, fn_new_fade_ready, 0xaf4u, m_new_fade_done, m_new_fade_done_s);
    quicklist_hide_loading_finish_4f7860(anim);
}

void quicklist_offset_all_items_down_4f7f18(int32_t dy)
{
    int32_t i;

    if (dy == 0 || g2_quicklist_container_20074e00 == NULL)
        return;
    QL_LOG(4u, fn_offset, 0xb03u, m_offset, m_offset_s, 1, dy);
    for (i = 0; i < (int32_t)g2_quicklist_ui_data_2012a72c.count && i < QL_MAX_ITEMS; i++) {
        if (g2_quicklist_rows_2006e370[i].container != NULL)
            audio_uart_page_43f142(g2_quicklist_rows_2006e370[i].container,
                                   dy + audio_uart_lv_obj_y_43fce0(g2_quicklist_rows_2006e370[i].container));
    }
}

/* Fade the newly focused row in from opacity 0 (100 ms). */
void quicklist_animate_focus_items_fade_in_4f7fa8(void)
{
    g2_lv_anim_t a;
    void *row;

    if (g2_quicklist_container_20074e00 == NULL || g2_quicklist_focus_index_200042c0 < 0)
        return;
    g2_quicklist_anim_state_20074e20 = 1;
    if (g2_quicklist_focus_index_200042c0 < 0 || g2_quicklist_focus_index_200042c0 >= (int32_t)g2_quicklist_ui_data_2012a72c.count ||
        g2_quicklist_focus_index_200042c0 >= QL_MAX_ITEMS ||
        g2_quicklist_rows_2006e370[g2_quicklist_focus_index_200042c0].container == NULL) {
        QL_LOG(2u, fn_focus_fade, 0xb27u, m_focus_bad, m_focus_bad_s, 1, g2_quicklist_focus_index_200042c0);
        g2_quicklist_anim_state_20074e20 = 0;
        scroll_container_anim_ready_cb_4f6a10(NULL);
        return;
    }
    row = g2_quicklist_rows_2006e370[g2_quicklist_focus_index_200042c0].container;
    audio_uart_display_audio_reset_441488(row, LV_OPA_TRANSP, LV_PART_MAIN);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = row;
    audio_uart_lv_anim_values_4506ce(&a, LV_OPA_TRANSP, LV_OPA_COVER);
    a.duration = 100;
    a.exec_cb = QL_EXEC_SET_OPA;
    a.completed_cb = quicklist_fade_in_anim_ready_cb_4f7eb0;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* After an add-up (2) or add-down (3) update, hide the row that will be faded in and fade the
 * loading row out (its ready callback starts the row fade). */
void quicklist_prepare_fade_animation_for_new_item_4f80a0(uint8_t is_last, uint8_t operation,
                                                          int32_t added_count)
{
    int32_t target = -1;

    if (operation == QL_ADD_UP) {
        if (is_last != 0u)
            target = added_count - 1;
        else
            target = 0;
    } else if (operation == QL_ADD_DOWN) {
        if (is_last != 0u) {
            target = (int32_t)g2_quicklist_ui_data_2012a72c.count - 1;
        } else {
            target = (int32_t)g2_quicklist_ui_data_2012a72c.count - added_count;
            if (target < 0)
                target = 0;
        }
    }
    if (target >= 0 && target < (int32_t)g2_quicklist_ui_data_2012a72c.count &&
        g2_quicklist_rows_2006e370[target].container != NULL) {
        audio_uart_display_audio_reset_441488(g2_quicklist_rows_2006e370[target].container, LV_OPA_TRANSP,
                                              LV_PART_MAIN);
        QL_LOG(4u, fn_prepare, 0xb9eu, m_prepare, m_prepare_s, 4, target, operation, is_last,
               added_count);
    } else {
        QL_LOG(2u, fn_prepare, 0xba1u, m_prepare_bad, m_prepare_bad_s, 3, target, operation,
               added_count);
    }
    quicklist_loading_fade_4f74f8(LV_OPA_TRANSP, 100,
                                     quicklist_hide_loading_with_fade_ready_cb_to_new_item_4f7408);
}

/* Spinner on the loading row: white foreground, black background, at (0, 2). */
void quicklist_init_loading_animation_4f81f0(void)
{
    g2_generic_animation_config_t cfg;
    uint32_t color;

    quicklist_loading_anim_destroy_4f8298();
    (void)aeabi_memcpy4_439c04(&cfg, &g2_quicklist_loading_anim_config, sizeof cfg);
    color = lv_color_white_441094();
    (void)audio_queue_copy_bytes(cfg.color_a, &color, 3u);
    color = lv_color_black_4410a6();
    (void)audio_queue_copy_bytes(cfg.bg_color, &color, 3u);
    g2_quicklist_loading_anim = generic_animation_create_463c68(g2_quicklist_loading_20074e08, &cfg);
    if (g2_quicklist_loading_anim == NULL) {
        QL_LOG0(1u, fn_loading_init, 0xbcau, m_loading_fail, m_loading_fail_s);
        return;
    }
    audio_uart_page_43f09a(g2_quicklist_loading_anim->image, 0, 2);
}

void quicklist_loading_anim_destroy_4f8298(void)
{
    if (g2_quicklist_loading_anim == NULL)
        return;
    if (g2_quicklist_loading_anim->image != NULL &&
        audio_terminal_ui_object_valid_43e2ea(g2_quicklist_loading_anim->image) != 0u)
        generic_animation_destroy_463e1c(g2_quicklist_loading_anim, 1u);
    else
        generic_animation_destroy_463e1c(g2_quicklist_loading_anim, 0u);
    g2_quicklist_loading_anim = NULL;
}

void quicklist_loading_anim_start_4f82d0(void)
{
    if (g2_quicklist_loading_anim != NULL)
        generic_animation_start_463ea6(g2_quicklist_loading_anim);
}

void quicklist_loading_anim_stop_4f82e4(void)
{
    if (g2_quicklist_loading_anim != NULL)
        generic_animation_stop_463eee(g2_quicklist_loading_anim);
}

void quicklist_loading_anim_update_4f82f8(void)
{
    if (g2_quicklist_loading_anim != NULL &&
        audio_terminal_ui_object_valid_43e2ea(g2_quicklist_loading_anim->image) != 0u &&
        g2_quicklist_loading_anim->running == 1u)
        generic_animation_update_463f34(g2_quicklist_loading_anim);
}

/* On page exit: merge the temp cache, upload the completed UIDs and, when that succeeded or
 * Bluetooth is down, drop completed items from the list. */
void quicklist_process_completed_items_on_exit_4f8348(void)
{
    int32_t merged = quicklist_merge_temp_cache_to_completed_items_4f6770();
    int32_t result;

    if (g2_quicklist_completed_201303cc.count == 0u)
        return;
    QL_LOG(4u, fn_exit, 0xc0du, m_exit, m_exit_s, 2, g2_quicklist_completed_201303cc.count, merged);
    result = (int32_t)audio_quicklist_aux_update_4f6328();
    if (result == 0) {
        QL_LOG(4u, fn_exit, 0xc13u, m_sent, m_sent_s, 1, g2_quicklist_completed_201303cc.count);
        quicklist_remove_completed_items_from_ui_4f84cc();
    } else if (result == -2) {
        QL_LOG(4u, fn_exit, 0xc18u, m_bt_down, m_bt_down_s, 1, g2_quicklist_completed_201303cc.count);
        quicklist_remove_completed_items_from_ui_4f84cc();
    } else {
        QL_LOG(1u, fn_exit, 0xc1eu, m_send_fail, m_send_fail_s, 1, result);
    }
}

/* Compact the record array in place, dropping completed records. */
void quicklist_remove_completed_items_from_ui_4f84cc(void)
{
    int32_t removed = 0;
    int32_t kept = 0;
    int32_t i;
    g2_quicklist_storage_t *s = &g2_quicklist_ui_data_2012a72c;

    (void)audio_quicklist_refresh_lock_4ffac8();
    for (i = 0; i < (int32_t)s->count; i++) {
        if (s->item[i].completed == 0u) {
            if (kept != i)
                (void)audio_queue_copy_bytes(&s->item[kept], &s->item[i], sizeof s->item[0]);
            kept++;
        } else {
            removed++;
            QL_LOG(4u, fn_remove, 0xc3du, m_removed_one, m_removed_one_s, 2, s->item[i].uid,
                   s->item[i].title);
        }
    }
    for (i = kept; i < (int32_t)s->count; i++)
        (void)aeabi_memset_43c0e4(&s->item[i], sizeof s->item[0], 0);
    s->count = (uint16_t)kept;
    if (removed >= 1)
        QL_LOG(4u, fn_remove, 0xc4bu, m_removed, m_removed_s, 2, removed, s->count);
    audio_quicklist_refresh_unlock_4ffb26();
}

/* REFLASH record from the phone. NULL/empty rebuilds the main-tile preview. data[0] == 0
 * latches {data[1], u16 data[2..3]} and rebuilds the expanded page (or queues a 0x47 record
 * while an animation runs); data[0] == 1 fades the loading row out (or queues). */
int32_t Quicklist_Page_Reflash_4f8644(const uint8_t *data, uint32_t len)
{
    uint8_t rec[5];
    g2_quicklist_storage_t *s = &g2_quicklist_ui_data_2012a72c;

    if (g2_quicklist_word_20074df8 == 0u) {
        QL_LOG0(2u, fn_reflash, 0xc55u, m_widget_off, m_widget_off_s);
        return 0;
    }
    if (data == NULL || len == 0u) {
        if (g2_dashboard_tiles[g2_quicklist_tile_index].frame != NULL)
            quicklist_page_clean_4fb1a4(g2_dashboard_tiles[g2_quicklist_tile_index].frame, 0u);
        (void)QuicklistWidget_MainPage_init_4f891c(g2_quicklist_tile_index);
        return 0;
    }
    if (data[0] == 0u) {
        s->reflash_kind = data[1];
        s->reflash_value = (uint16_t)(data[2] | ((uint32_t)data[3] << 8));
        if (g2_quicklist_page_active_20074e1c == 1 && g2_quicklist_event_fifo_20074e14 != NULL &&
            g2_dashboard_focus_frame != NULL) {
            if (g2_quicklist_anim_state_20074e20 == 0) {
                g2_quicklist_anim_state_20074e20 = 2;
                if (s->count == 0u || g2_quicklist_border_state_2007503f == QL_BORDER_FULL)
                    quicklist_page_clean_4fb1a4(g2_dashboard_focus_frame, 1u);
                (void)Quicklist_ext_WidgetPage_Create_4fac74(g2_dashboard_focus_frame);
                if (g2_quicklist_anim_state_20074e20 == 2)
                    g2_quicklist_anim_state_20074e20 = 0;
            } else {
                (void)aeabi_memset_43c0e4(rec, sizeof rec, 0);
                rec[0] = QL_EVT_REBUILD;
                rec[1] = 0u;
                rec[2] = s->reflash_kind;
                rec[3] = (uint8_t)s->reflash_value;
                rec[4] = (uint8_t)(s->reflash_value >> 8);
                (void)ui_common_api_fn_00509ca2(g2_quicklist_event_fifo_20074e14, rec, 5u);
                QL_LOG(3u, fn_reflash, 0xc7eu, m_fifo_push, m_fifo_push_s, 1, rec[0]);
            }
        } else {
            if (g2_dashboard_tiles[g2_quicklist_tile_index].frame != NULL)
                quicklist_page_clean_4fb1a4(g2_dashboard_tiles[g2_quicklist_tile_index].frame, 0u);
            audio_quicklist_refresh_pending_4f5596();
            (void)QuicklistWidget_MainPage_init_4f891c(g2_quicklist_tile_index);
        }
        s->reflash_kind = 0u;
        s->reflash_value = 0u;
    } else if (data[0] == 1u) {
        if (g2_quicklist_anim_state_20074e20 != 0) {
            rec[0] = QL_EVT_REBUILD;
            rec[1] = 1u;
            rec[2] = 0u;
            rec[3] = 0u;
            rec[4] = 0u;
            (void)ui_common_api_fn_00509ca2(g2_quicklist_event_fifo_20074e14, rec, 5u);
        } else if (g2_quicklist_page_active_20074e1c == 1 && g2_quicklist_event_fifo_20074e14 != NULL &&
                   g2_dashboard_focus_frame != NULL) {
            quicklist_loading_fade_4f74f8(LV_OPA_TRANSP, 100, quicklist_hide_loading_with_fade_ready_cb_4f7480);
        }
    }
    return 0;
}

/* Periodic tick while the expanded page is open. */
int32_t quicklist_widget_tick_4f8878(void)
{
    if (g2_quicklist_page_active_20074e1c == 1 && g2_quicklist_event_fifo_20074e14 != NULL &&
        g2_dashboard_focus_frame != NULL) {
        quicklist_loading_request_data_4f7590();
        quicklist_loading_anim_update_4f82f8();
    }
    return 0;
}

/* Apply the zeroed "plain container" style used for the preview containers. */
static void quicklist_plain_style(void *obj)
{
    audio_uart_page_44127e(obj, audio_uart_page_44104c(0x000000u), LV_PART_MAIN);
    audio_uart_page_44129e(obj, LV_OPA_TRANSP, LV_PART_MAIN);
    audio_uart_page_44131c(obj, 0, LV_PART_MAIN);
    audio_uart_page_44133a(obj, 0, LV_PART_MAIN);
    audio_uart_page_441378(obj, 0, LV_PART_MAIN);
    audio_uart_page_441386(obj, 0, LV_PART_MAIN);
    audio_uart_page_4413b0(obj, 0, LV_PART_MAIN);
}

static void quicklist_plain_style_tail(void *obj)
{
    lv_obj_set_style_pad_all_4f5068(obj, 0, LV_PART_MAIN);
    audio_uart_page_44146a(obj, 0, LV_PART_MAIN);
    audio_uart_page_4412ec(obj, audio_uart_page_44104c(0x000000u), LV_PART_MAIN);
    audio_uart_page_44140e(obj, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_44142e(obj, LV_OPA_COVER, LV_PART_MAIN);
    audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
}

/* Centred icon + "ID_DASHBOARD_QUICKLIST_DEFAULT_1" line and a DEFAULT_2 hint below. */
static void quicklist_build_empty_hint(void *parent, int32_t hint_width)
{
    void *outer;
    void *row;
    void *icon;
    void *label;
    void *hint;

    outer = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(outer, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(outer, LV_ALIGN_CENTER, 0, 0);
    quicklist_plain_style(outer);
    quicklist_plain_style_tail(outer);

    row = audio_uart_page_43de82(outer);
    audio_uart_page_43f4c0(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(row, LV_ALIGN_TOP_MID, 0, 0);
    quicklist_plain_style(row);
    quicklist_plain_style_tail(row);

    icon = audio_uart_page_498668(row);
    audio_uart_page_498680(icon, g2_img_quicklist_empty);
    audio_uart_page_43f506(icon, 24);
    audio_uart_page_43f568(icon, 24);
    audio_uart_page_43f6b8(icon, LV_ALIGN_TOP_LEFT, 0, 2);
    audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

    label = audio_uart_page_499416(row);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(id_default_1, audio_uart_page_460084(id_default_1)));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
    audio_uart_page_43f6d6(label, icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);

    hint = audio_uart_page_499416(outer);
    audio_uart_page_43f506(hint, hint_width);
    audio_uart_page_43f568(hint, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(hint, row, LV_ALIGN_OUT_BOTTOM_MID, 0, 4);
    audio_uart_page_44140e(hint, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_49942e(hint, audio_uart_page_45fffe(id_default_2, audio_uart_page_460084(id_default_2)));
    audio_uart_page_44143e(hint, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
    audio_uart_page_44145a(hint, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
}

static void quicklist_preview_icon(void *parent, const g2_quicklist_item_t *item, int32_t y)
{
    void *icon = audio_uart_page_498668(parent);

    if (item->completed == 0u)
        audio_uart_page_498680(icon, g2_img_quicklist_unchecked);
    else
        audio_uart_page_498680(icon, g2_img_quicklist_checked);
    audio_uart_page_43f506(icon, 24);
    audio_uart_page_43f568(icon, 24);
    audio_uart_page_43f0e0(icon, 0);
    audio_uart_page_43f142(icon, y + 2);
}

/* Main dashboard tile: a 315x256 container at (20, 16) listing as many items as fit (title of
 * up to two wrapped lines, optional 28-px time line, 20-px gap); a partially fitting item is
 * cut to one dotted line when at least 28 px remain. Empty lists show the default hint. */
int32_t QuicklistWidget_MainPage_init_4f891c(int32_t tile_index)
{
    g2_quicklist_storage_t *s = &g2_quicklist_ui_data_2012a72c;
    g2_quicklist_item_t *item;
    void *box;
    void *label;
    uint16_t i;
    int32_t y;
    int32_t shown;
    int32_t avail;
    int32_t title_h;
    int32_t needed;

    g2_quicklist_tile_index = tile_index;
    box = audio_uart_page_43de82(g2_dashboard_tiles[g2_quicklist_tile_index].frame);
    audio_uart_page_43f09a(box, 20, 16);
    audio_uart_page_43f506(box, 0x13b);
    audio_uart_page_43f568(box, 0x100);
    quicklist_plain_style(box);
    audio_uart_page_441394(box, 0, LV_PART_MAIN);
    audio_uart_page_4413a2(box, 0, LV_PART_MAIN);
    quicklist_plain_style_tail(box);
    g2_quicklist_word_20074df8 = 1u;

    if (s->count == 0u) {
        quicklist_build_empty_hint(box, 0x13b);
        return 0;
    }

    y = 0;
    shown = 0;
    avail = 0x100;
    for (i = 0u; i < s->count; i++) {
        item = &s->item[i];
        title_h = 0;
        (void)audio_quicklist_refresh_lock_4ffac8();
        (void)quicklist_text_line_count_4f50d6(item->title, audio_uart_ring_primary_head_cell, 0x11b, 0, 0,
                                               2, &title_h);
        audio_quicklist_refresh_unlock_4ffb26();
        needed = title_h;
        if (item->time_text[0] != '\0')
            needed += 28;
        needed += 20;
        if (avail < needed + y) {
            if (avail - y < 28)
                break;
            quicklist_preview_icon(box, item, y);
            if (avail - y < needed) {
                label = audio_uart_page_499416(box);
                audio_uart_page_43f506(label, 0x11b);
                audio_uart_page_43f568(label, 28);
                audio_uart_page_43f0e0(label, 32);
                audio_uart_page_43f142(label, y);
                (void)audio_uart_page_layout_499678(label, LV_LABEL_LONG_DOT);
                (void)audio_quicklist_refresh_lock_4ffac8();
                audio_uart_page_49942e(label, item->title);
                audio_quicklist_refresh_unlock_4ffb26();
                audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
                audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
                break;
            }
        }
        quicklist_preview_icon(box, item, y);
        label = audio_uart_page_499416(box);
        audio_uart_page_43f506(label, 0x11b);
        audio_uart_page_43f568(label, title_h);
        audio_uart_page_43f0e0(label, 32);
        audio_uart_page_43f142(label, y);
        (void)audio_quicklist_refresh_lock_4ffac8();
        audio_uart_page_49942e(label, item->title);
        audio_quicklist_refresh_unlock_4ffb26();
        audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
        (void)audio_uart_page_layout_499678(label, LV_LABEL_LONG_DOT);
        y += title_h;
        if (item->timestamp > 0) {
            label = audio_uart_page_499416(box);
            audio_uart_page_43f506(label, 0x11b);
            audio_uart_page_43f568(label, 28);
            audio_uart_page_43f0e0(label, 32);
            audio_uart_page_43f142(label, y);
            (void)audio_uart_page_layout_499678(label, LV_LABEL_LONG_DOT);
            (void)audio_quicklist_refresh_lock_4ffac8();
            (void)quicklist_format_timestamp_4f5366(item->timestamp, item->time_kind, item->time_text,
                                              QL_TIME_TEXT_LEN);
            audio_uart_page_49942e(label, item->time_text);
            audio_quicklist_refresh_unlock_4ffb26();
            audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
            audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
            y += 28;
        } else {
            item->time_text[0] = '\0';
        }
        y += 20;
        shown++;
    }
    QL_LOG(4u, fn_main_init, 0xd7du, m_displayed, m_displayed_s, 1, shown);
    return 0;
}

/* Expanded page input. data[0]: 0 input record {0, code, ...}, 1 dashboard data, 5 reflash. */
int32_t quicklist_ext_event_handler_4f8ffc(const uint8_t *data, uint32_t len)
{
    uint8_t code;

    if (g2_quicklist_page_active_20074e1c == 0) {
        QL_LOG0(2u, fn_ext_event, 0xd86u, m_ext_off, m_ext_off_s);
        return 0;
    }
    if (len == 0u) {
        QL_LOG0(2u, fn_ext_event, 0xd8au, m_len0, m_len0_s);
        return 0;
    }
    if (data[0] == QL_MSG_DASHBOARD) {
        dashboard_main_screen_data_event_4e8970(data + 1, len - 1u);
        return 0;
    }
    if (data[0] == QL_MSG_REFLASH) {
        (void)Quicklist_Page_Reflash_4f8644(data + 1, len - 1u);
        return 0;
    }
    if (data[0] != QL_MSG_INPUT)
        return 0;

    code = data[1];
    if (g2_quicklist_anim_state_20074e20 != 0) {
        (void)ui_common_api_fn_00509ca2(g2_quicklist_event_fifo_20074e14, data + 1, 5u);
        return 0;
    }
    switch (code) {
    case QL_EVT_CLICK:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL) {
            if (g2_quicklist_ui_data_2012a72c.count != 0u)
                quicklist_border_shrink_to_item_4f7ae4(g2_quicklist_focus_index_200042c0 < 0 ? 0 : g2_quicklist_focus_index_200042c0);
        } else if (g2_quicklist_border_state_2007503f == QL_BORDER_ON_ITEM && g2_quicklist_focus_index_200042c0 >= 0) {
            quicklist_toggle_item_completion_4f7cb0(g2_quicklist_focus_index_200042c0);
        } else {
            QL_LOG(4u, fn_ext_event, 0xe18u, m_no_focus, m_no_focus_s, 2, g2_quicklist_border_state_2007503f,
                   g2_quicklist_focus_index_200042c0);
        }
        break;
    case QL_EVT_NEXT:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL) {
            if (g2_quicklist_ui_data_2012a72c.count != 0u)
                quicklist_border_shrink_to_item_4f7ae4(g2_quicklist_focus_index_200042c0 < 0 ? 0 : g2_quicklist_focus_index_200042c0);
        } else if (g2_quicklist_border_state_2007503f == QL_BORDER_ON_ITEM && g2_quicklist_focus_index_200042c0 >= 0) {
            if (quicklist_need_data_request_4f61a0(QL_REQUEST_DIR_NEXT) != 0u)
                quicklist_request_data_with_debounce_4f6282(QL_REQUEST_DIR_NEXT);
            quicklist_focus_move_to_4f7c10(g2_quicklist_focus_index_200042c0 + 1);
        }
        break;
    case QL_EVT_PREV:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL) {
            if (g2_quicklist_ui_data_2012a72c.count != 0u)
                quicklist_border_shrink_to_item_4f7ae4(g2_quicklist_focus_index_200042c0 < 0 ? 0 : g2_quicklist_focus_index_200042c0);
        } else if (g2_quicklist_border_state_2007503f == QL_BORDER_ON_ITEM && g2_quicklist_focus_index_200042c0 >= 0) {
            if (quicklist_need_data_request_4f61a0(QL_REQUEST_DIR_PREV) != 0u)
                quicklist_request_data_with_debounce_4f6282(QL_REQUEST_DIR_PREV);
            quicklist_focus_move_to_4f7c10(g2_quicklist_focus_index_200042c0 - 1);
        }
        break;
    case QL_EVT_IGNORED:
        break;
    case QL_EVT_DOUBLE_CLICK:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_ON_ITEM)
            quicklist_border_expand_to_full_4f7b84();
        else if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL)
            quicklist_ext_widget_deinit_4faf20();
        break;
    case QL_EVT_FADEOUT:
        Dashboard_Fadeout_Anim_Start_4e8a90();
        g2_quicklist_page_active_20074e1c = 0;
        g2_quicklist_anim_state_20074e20 = 0;
        break;
    default:
        QL_LOG(2u, fn_ext_event, 0xe2du, m_unknown, m_unknown_s, 1, code);
        break;
    }
    return 0;
}

void quicklist_delete_item_objects_4f92f0(void)
{
    int32_t i;
    int32_t j;
    void **w;

    for (i = 0; i < (int32_t)g2_quicklist_ui_data_2012a72c.count; i++) {
        w = &g2_quicklist_rows_2006e370[i].container;
        for (j = 0; j < 4; j++) {
            if (w[j] != NULL && audio_terminal_ui_object_valid_43e2ea(w[j]) != 0u) {
                audio_uart_page_delete_event_filter_44d7b8(w[j]);
                w[j] = NULL;
            }
        }
    }
}

/* Hidden 546-px loading row at the top of the list: spinner plus "ID_DASHBOARD_QUICKLIST_LOADING". */
void quicklist_create_loading_item_4f9368(void)
{
    if (g2_quicklist_container_20074e00 == NULL)
        return;
    g2_quicklist_loading_20074e08 = audio_uart_page_43de82(g2_quicklist_container_20074e00);
    audio_uart_page_43f4c0(g2_quicklist_loading_20074e08, 0x222, LV_SIZE_CONTENT);
    audio_uart_page_43f09a(g2_quicklist_loading_20074e08, 0, 0);
    audio_uart_page_44127e(g2_quicklist_loading_20074e08, audio_uart_page_44104c(0x000000u), LV_PART_MAIN);
    audio_uart_page_44129e(g2_quicklist_loading_20074e08, LV_OPA_TRANSP, LV_PART_MAIN);
    audio_uart_page_44146a(g2_quicklist_loading_20074e08, 6, LV_PART_MAIN);
    lv_obj_set_style_pad_all_4f5068(g2_quicklist_loading_20074e08, 8, LV_PART_MAIN);
    audio_uart_page_44e368(g2_quicklist_loading_20074e08, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_4412ec(g2_quicklist_loading_20074e08, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_44131c(g2_quicklist_loading_20074e08, 0, LV_PART_MAIN);
    audio_uart_page_43dfa4(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43ded4(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN);
    quicklist_init_loading_animation_4f81f0();

    g2_quicklist_loading_label = audio_uart_page_499416(g2_quicklist_loading_20074e08);
    audio_uart_page_43f506(g2_quicklist_loading_label, 0x240);
    audio_uart_page_43f568(g2_quicklist_loading_label, LV_SIZE_CONTENT);
    audio_uart_page_49942e(g2_quicklist_loading_label,
                           audio_uart_page_45fffe(id_loading, audio_uart_page_460084(id_loading)));
    audio_uart_page_44140e(g2_quicklist_loading_label, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
    audio_uart_page_44143e(g2_quicklist_loading_label, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
    audio_uart_page_43f0e0(g2_quicklist_loading_label, 32);
    audio_uart_page_43f142(g2_quicklist_loading_label, 0);
}

/* Expanded page rows: 546-px row containers stacked 4 px apart (pad 8/8/8/5, radius 6), check
 * icon, wrapped title (501 px) and an optional dotted time line; completed rows at opa 0x30.
 * Empty lists show the default hint (546-px wide). Ends by creating the loading row. */
void quicklist_create_items_4f9484(void)
{
    g2_quicklist_storage_t *s = &g2_quicklist_ui_data_2012a72c;
    g2_quicklist_row_t *row;
    g2_quicklist_item_t *item;
    uint16_t i;

    if (g2_quicklist_container_20074e00 == NULL ||
        audio_terminal_ui_object_valid_43e2ea(g2_quicklist_container_20074e00) == 0u)
        return;
    if (s->count == 0u) {
        quicklist_build_empty_hint(g2_quicklist_container_20074e00, 0x222);
        return;
    }
    for (i = 0u; i < s->count; i++) {
        row = &g2_quicklist_rows_2006e370[i];
        item = &s->item[i];
        row->container = audio_uart_page_43de82(g2_quicklist_container_20074e00);
        audio_uart_page_43f506(row->container, 0x222);
        audio_uart_page_43f568(row->container, LV_SIZE_CONTENT);
        if (i == 0u)
            audio_uart_page_43f6b8(g2_quicklist_rows_2006e370[0].container, LV_ALIGN_TOP_LEFT, 0, 0);
        else
            audio_uart_page_43f6d6(row->container, g2_quicklist_rows_2006e370[i - 1u].container,
                                   LV_ALIGN_OUT_BOTTOM_LEFT, 0, 4);
        audio_uart_display_audio_reset_441488(row->container, LV_OPA_COVER, LV_PART_MAIN);
        audio_uart_page_44127e(row->container, audio_uart_page_44104c(0x000000u), LV_PART_MAIN);
        audio_uart_page_44129e(row->container, LV_OPA_TRANSP, LV_PART_MAIN);
        audio_uart_page_44146a(row->container, 6, LV_PART_MAIN);
        audio_uart_page_4412ec(row->container, audio_uart_page_44104c(0x000000u), LV_PART_MAIN);
        audio_uart_page_44131c(row->container, 0, LV_PART_MAIN);
        audio_uart_page_44120e(row->container, 8, LV_PART_MAIN);
        audio_uart_page_44121c(row->container, 8, LV_PART_MAIN);
        audio_uart_page_44122a(row->container, 8, LV_PART_MAIN);
        audio_uart_page_441238(row->container, 5, LV_PART_MAIN);
        audio_uart_page_44e368(row->container, LV_SCROLLBAR_MODE_OFF);
        audio_uart_page_43dfa4(row->container, LV_OBJ_FLAG_SCROLLABLE);

        row->icon = audio_uart_page_498668(row->container);
        if (item->completed == 0u) {
            audio_uart_page_498680(row->icon, g2_img_quicklist_unchecked);
            audio_uart_display_audio_reset_441488(row->container, LV_OPA_COVER, LV_PART_MAIN);
        } else {
            audio_uart_page_498680(row->icon, g2_img_quicklist_checked);
            audio_uart_display_audio_reset_441488(row->container, QL_COMPLETED_OPA, LV_PART_MAIN);
        }
        audio_uart_page_43f506(row->icon, 24);
        audio_uart_page_43f568(row->icon, 24);
        audio_uart_page_43f6b8(row->icon, LV_ALIGN_TOP_LEFT, 0, 2);

        row->title = audio_uart_page_499416(row->container);
        audio_uart_page_43f506(row->title, 0x1f5);
        audio_uart_page_43f568(row->title, LV_SIZE_CONTENT);
        audio_uart_page_43f6d6(row->title, row->icon, LV_ALIGN_OUT_RIGHT_TOP, 8, -2);
        (void)audio_uart_page_layout_499678(row->title, LV_LABEL_LONG_WRAP);
        audio_uart_page_44140e(row->title, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
        audio_uart_page_44143e(row->title, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
        (void)audio_quicklist_refresh_lock_4ffac8();
        audio_uart_page_49942e(row->title, item->title);
        audio_quicklist_refresh_unlock_4ffb26();

        if (item->timestamp > 0) {
            row->time = audio_uart_page_499416(row->container);
            audio_uart_page_43f506(row->time, 0x1f5);
            audio_uart_page_43f568(row->time, 28);
            audio_uart_page_43f6d6(row->time, row->title, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 0);
            (void)audio_uart_page_layout_499678(row->time, LV_LABEL_LONG_DOT);
            (void)audio_quicklist_refresh_lock_4ffac8();
            (void)quicklist_format_timestamp_4f5366(item->timestamp, item->time_kind, item->time_text,
                                              QL_TIME_TEXT_LEN);
            audio_uart_page_49942e(row->time, item->time_text);
            audio_quicklist_refresh_unlock_4ffb26();
            audio_uart_page_44140e(row->time, audio_uart_page_44104c(0xffffffu), LV_PART_MAIN);
            audio_uart_page_44143e(row->time, audio_uart_ring_primary_head_cell, LV_PART_MAIN);
        } else {
            item->time_text[0] = '\0';
        }
    }
    quicklist_create_loading_item_4f9368();
}
