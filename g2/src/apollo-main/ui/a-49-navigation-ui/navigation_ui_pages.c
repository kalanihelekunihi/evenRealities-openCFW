/* Navigation UI, part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c
 * (log tag "navigation.ui"). Native 0x548484..0x548549, 0x5485c4..0x548b39,
 * 0x548b98..0x548f23, 0x548f80..0x549595, 0x5495a8..0x5496cf,
 * 0x549708..0x549977 and 0x549994..0x549b6b; literal pools 0x548550..0x5485c3,
 * 0x548b3c..0x548b97, 0x548f24..0x548f7f, 0x549598..0x5495a7,
 * 0x5496d0..0x549707, 0x549978..0x549993 and 0x549b6c..0x549c23.
 * The rest of the TU (container A/B show/hide animations 0x547ad2 / 0x547dcc,
 * fade callbacks 0x547abc / 0x5482c4, page dispatcher 0x549c24, scroll and
 * style helpers 0x54c3ec..0x54db30) is reconstructed separately.
 *
 * The page root (RAM 0x20074718) hosts either the location list (title label
 * "ID_NAVIGATE_SELECT", a 552x200 vertically scrolling container and up to 20
 * 40 px rows with a 24x24 type icon and the location name) or the 2-option
 * travel mode list (Walking / Cycling). Inputs are forwarded to the master
 * side as 6-byte sync records (app 8). Navigation info and the mini / max map
 * bitmaps arrive through navigation_data_handler.c and are copied into the UI
 * record (RAM 0x202c0d70) under the navigation mutex. */
#include <stdint.h>
#include <stddef.h>

#define WAIT_FOREVER 0xffffffffu

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_DIR_VER 0x0cu
#define LV_ALIGN_LEFT_MID 7u
#define LV_ALIGN_OUT_RIGHT_MID 20u
#define LV_LABEL_LONG_MODE_DOTS 1u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_OPA_TRANSP 0u
#define LV_OPA_COVER 255u

#define NAV_MAX_LOCATIONS 20
#define NAV_ITEM_H 40
#define NAV_LIST_W 552               /* 0x228 */
#define NAV_MODE_W 500
#define NAV_MODE_COUNT 2
#define NAV_MINI_MAP_SIZE 18000u     /* 0x4650 */
#define NAV_MAX_MAP_SIZE 60000u      /* 0xea60 */
#define NAV_GREY 0x444444u           /* ROM 0x548f70 */

/* Page events handled by NavigationInputEventHandler. */
enum {
    NAV_EVT_CLICK = 0x0a,
    NAV_EVT_IMU_COMPASS = 0x41,
    NAV_EVT_SCROLL_UP = 0x44,
    NAV_EVT_SCROLL_DOWN = 0x45,
    NAV_EVT_DOUBLE_CLICK = 0x48,
    NAV_EVT_SYSTEM_EXIT_NOTIFY = 0x4f,
    NAV_EVT_IMU_COMPASS_RESET = 0x50, /* logged as "IMU compass Event." too */
};

/* navigation_ui_state values (RAM byte 0x20074fed). */
enum {
    NAVIGATION_LOCATION_LIST_SELECT_PAGE = 2,
    NAVIGATION_MODE_SELECT_PAGE = 9,
};

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
    uint8_t rest[0x2c];                 /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* lv_font_t prefix: only line_height is read here. */
typedef struct {
    void *get_glyph_dsc;      /* +0x00 */
    void *get_glyph_bitmap;   /* +0x04 */
    void *release_glyph;      /* +0x08 */
    int32_t line_height;      /* +0x0c */
} g2_lv_font_prefix_t;

/* Location list pushed by the phone (RAM 0x20376c38). */
typedef struct {
    uint32_t count;                               /* +0x000 */
    uint8_t header_04[2];                         /* +0x004 */
    char name[NAV_MAX_LOCATIONS][0x40];           /* +0x006 */
    uint8_t reserved_506[2];                      /* +0x506 */
    uint32_t icon_type[NAV_MAX_LOCATIONS];        /* +0x508 1 / 2 / other */
    uint8_t reserved_558[4];                      /* +0x558 (stock clears 0x55c bytes) */
} g2_navigation_location_list_t;
_Static_assert(sizeof(g2_navigation_location_list_t) == 0x55c, "location list");
_Static_assert(offsetof(g2_navigation_location_list_t, name) == 0x006, "location name");
_Static_assert(offsetof(g2_navigation_location_list_t, icon_type) == 0x508, "location icon type");

/* Navigation info record (field names from the data handler log format at
 * ROM 0x6d6650). Staged at RAM 0x2037bdd0, copied to the head of the UI
 * record. */
typedef struct {
    uint8_t valid;                 /* +0x000 */
    uint8_t reserved_01[3];
    uint32_t field_04;             /* +0x004 not logged */
    char distance[0x40];           /* +0x008 */
    char road_name[0x40];          /* +0x048 */
    char spend_time[0x40];         /* +0x088 */
    char remain_distance[0x40];    /* +0x0c8 */
    char eta_time[0x40];           /* +0x108 */
    char speed[0x40];              /* +0x148 */
    uint32_t navigate_work_method; /* +0x188 */
} g2_navigation_info_t;
_Static_assert(sizeof(g2_navigation_info_t) == 0x18c, "navigation info record");

/* UI navigation record (RAM 0x202c0d70, 0x13258 bytes, ROM 0x54687c). */
typedef struct {
    g2_navigation_info_t info;                 /* +0x0000 */
    uint8_t mini_map_ready;                    /* +0x018c */
    uint8_t reserved_18d[3];
    uint32_t mini_map_size;                    /* +0x0190 */
    uint32_t mini_map_compress_mode;           /* +0x0194 0 raw, 1 rle, 2 lz4 */
    uint8_t reserved_198[4];
    uint8_t mini_map_data[NAV_MINI_MAP_SIZE];  /* +0x019c */
    uint8_t reserved_47ec;                     /* +0x47ec */
    uint8_t max_map_ready;                     /* +0x47ed */
    uint8_t reserved_47ee[2];
    uint32_t max_map_size;                     /* +0x47f0 */
    uint32_t max_map_compress_mode;            /* +0x47f4 */
    uint8_t max_map_data[NAV_MAX_MAP_SIZE];    /* +0x47f8 */
} g2_navigation_ui_data_t;
_Static_assert(offsetof(g2_navigation_ui_data_t, mini_map_ready) == 0x18c, "mini map flag");
_Static_assert(offsetof(g2_navigation_ui_data_t, mini_map_data) == 0x19c, "mini map data");
_Static_assert(offsetof(g2_navigation_ui_data_t, max_map_ready) == 0x47ed, "max map flag");
_Static_assert(offsetof(g2_navigation_ui_data_t, max_map_data) == 0x47f8, "max map data");
_Static_assert(sizeof(g2_navigation_ui_data_t) == 0x13258, "navigation ui record");

/* RAM state. */
extern void *g2_navigation_mutex;                                   /* RAM 0x2007471c */
extern void *g2_navigation_page_root_20074718;                      /* RAM 0x20074718 */
extern const g2_lv_font_prefix_t *audio_uart_ring_primary_head_cell; /* RAM 0x200746dc: active lv_font_t * */
extern g2_navigation_location_list_t g2_navigation_location_list_20376c38; /* RAM 0x20376c38 */
extern void *g2_navigation_location_container_2007479c;             /* RAM 0x2007479c scrolling viewport */
extern void *g2_navigation_location_content_200747a0;               /* RAM 0x200747a0 */
extern void *g2_navigation_location_items_20072c68[NAV_MAX_LOCATIONS]; /* RAM 0x20072c68 */
extern int32_t g2_navigation_location_selected_200747a4;            /* RAM 0x200747a4 */
extern int32_t g2_navigation_location_scroll_offset_200747a8;       /* RAM 0x200747a8, in items */
extern void *g2_navigation_mode_container_200747ac;                 /* RAM 0x200747ac */
extern void *g2_navigation_mode_content_200747b0;                   /* RAM 0x200747b0 */
extern void *g2_navigation_mode_items_20074160[NAV_MODE_COUNT];     /* RAM 0x20074160 */
extern int32_t g2_navigation_mode_selected_200747b4;                /* RAM 0x200747b4 */
extern int32_t g2_navigation_mode_scroll_offset_200747b8;           /* RAM 0x200747b8 */
extern void *g2_navigation_container_a_200747c0;                    /* RAM 0x200747c0 */
extern void *g2_navigation_container_b_200747c4;                    /* RAM 0x200747c4 */
extern const char *g2_navigation_mode_names_20002d00[NAV_MODE_COUNT]; /* RAM .data 0x20002d00: i18n keys */
extern uint8_t g2_navigation_ui_state_20074fed;                     /* RAM 0x20074fed */
extern uint8_t g2_navigation_location_animating_20074fe8;           /* RAM 0x20074fe8 */
extern uint8_t g2_navigation_mode_animating_20074fe9;               /* RAM 0x20074fe9 */
extern g2_navigation_info_t g2_navigation_info_staging_2037bdd0;    /* RAM 0x2037bdd0 */
extern g2_navigation_ui_data_t g2_navigation_ui_data_202c0d70;      /* RAM 0x202c0d70 */
extern uint8_t g2_navigation_mini_map_decode_2032dc74[NAV_MINI_MAP_SIZE]; /* RAM 0x2032dc74 */
extern uint8_t g2_navigation_max_map_decode_202f3a44[NAV_MAX_MAP_SIZE];   /* RAM 0x202f3a44 */

/* Location type icons, 24x24 lv_image_dsc_t in ROM. */
extern const uint8_t g2_navigation_icon_type1_76e654[]; /* ROM 0x76e654 */
extern const uint8_t g2_navigation_icon_type2_76e670[]; /* ROM 0x76e670 */
extern const uint8_t g2_navigation_icon_other_76e68c[]; /* ROM 0x76e68c */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* RTOS, libc. */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t g2_log_module_length(const char *text);                       /* 0x44a43c strlen */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */

/* Sync to the master side. */
extern uint32_t audio_uart_service_mode(void); /* 0x45a570, 1 = master */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags); /* 0x464bb2 */

/* i18n. */
extern uint32_t audio_uart_page_460084(const char *key);                   /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                         /* lv_obj_create */
extern void audio_uart_page_44d878(void *obj);                             /* lv_obj_clean */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);              /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);              /* lv_obj_remove_flag */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                  /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                  /* lv_obj_set_y */
extern void audio_uart_page_43f506(void *obj, int32_t w);                  /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                  /* lv_obj_set_height */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);       /* lv_obj_set_size */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                             /* lv_obj_align_to */
extern void lv_obj_center_4409fa(void *obj); /* lv_obj_align(obj, CENTER, 0, 0) */
extern void audio_uart_page_43f66c(void *obj);                             /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);                  /* lv_obj_get_width */
extern void audio_uart_page_invalidate_440656(void *obj);                  /* lv_obj_invalidate */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);              /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);               /* lv_obj_set_scroll_dir */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern uint32_t audio_uart_page_44104c(uint32_t hex);                      /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);    /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);    /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);    /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);    /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel); /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);    /* border_width */
extern void audio_uart_page_441180(void *obj, int32_t v, uint32_t sel);    /* max_width */
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t sel); /* image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);    /* radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void *audio_uart_page_499416(void *parent);                         /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);         /* lv_label_set_text */
extern void audio_uart_page_layout_499678(void *label, uint32_t mode);     /* lv_label_set_long_mode */
extern void *audio_uart_page_498668(void *parent);                         /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);          /* lv_image_set_src */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);
extern uint32_t audio_uart_lv_style_unlink_450500(void *var, void *exec_cb); /* lv_anim_delete */
extern int32_t audio_uart_lv_anim_path_450688(void *anim);                 /* lv_anim_path_ease_in_out */

/* Decompressors shared with the EvenHub image path. */
extern uint32_t evenhub_lz4_decompress_4e0c0c(const void *src, uint32_t src_len, void *dst,
                                              uint32_t dst_cap); /* 0 on failure */
extern uint32_t evenhub_rle_decompress_4e0c34(const void *src, uint32_t src_len, void *dst,
                                              uint32_t dst_cap); /* {count, byte} pairs */

/* Rest of navigation_ui.c. */
extern void lv_obj_set_style_pad_all_545594(void *obj, int32_t v, uint32_t sel);
extern void navigation_container_opa_anim_exec_cb_547abc(void *obj, int32_t opa);
extern void navigation_show_container_B_with_animation_547ad2(void);
extern void navigation_hide_container_B_with_animation_547dcc(void);
extern void navigation_container_A_fade_in_complete_cb_5482c4(void *anim);
extern int32_t navigation_location_item_y_54c3ec(int32_t index, int32_t count); /* index * 40 */
extern int32_t navigation_calculate_scroll_position_for_item_54cc00(int32_t item_index);
extern void navigation_update_location_item_styles_54d9a4(void);
extern int32_t navigation_mode_item_y_54dad8(int32_t index, int32_t count); /* (index + (5 - count) / 2) * 40 */
extern void navigation_update_mode_item_styles_54db30(void);

static const char module_tag[] = "navigation.ui"; /* ROM 0x787ab0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_ui.c"; /* ROM 0x6fb6e4 */
static const char title_key[] = "ID_NAVIGATE_SELECT"; /* ROM 0x7813cc */
static const char layout_top_aligned[] = "top-aligned"; /* ROM 0x78b5e8 */
static const char layout_normal[] = "normal"; /* ROM 0x78dd54 */

static const char fade_out_fn[] = "navigation_container_B_fade_out_complete_cb"; /* ROM 0x740550 */
static const char fade_out_msg[] = "Container B fade out complete, showing container A"; /* ROM 0x72b0f8 */
static const char fade_out_short[] =
    "[navigation.ui]Container B fade out complete, showing container A"; /* ROM 0x703fd8 */

static const char loc_fn[] = "navigation_ui_create_location_list_page"; /* ROM 0x74b7fc */
static const char loc_creating[] = "Creating navigation location list page with %d locations"; /* ROM 0x7166b4 */
static const char loc_creating_short[] =
    "[navigation.ui]Creating navigation location list page with %d locations"; /* ROM 0x6fb7bc */
static const char loc_height[] =
    "Navigation content height set to: %d pixels (items: %d, layout: %s)"; /* ROM 0x70401c */
static const char loc_height_short[] =
    "[navigation.ui]Navigation content height set to: %d pixels (items: %d, layout: %s)"; /* ROM 0x6e8cd4 */
static const char loc_item[] = "Created navigation location item %d: %s"; /* ROM 0x74b824 */
static const char loc_item_short[] = "[navigation.ui]Created navigation location item %d: %s"; /* ROM 0x720600 */
static const char loc_initial[] = "Initial navigation selected_index: %d, scroll position: %d"; /* ROM 0x7166f0 */
static const char loc_initial_short[] =
    "[navigation.ui]Initial navigation selected_index: %d, scroll position: %d"; /* ROM 0x6f4780 */
static const char loc_done[] =
    "Navigation location list page initialization complete with %d locations"; /* ROM 0x6fb804 */
static const char loc_done_short[] =
    "[navigation.ui]Navigation location list page initialization complete with %d locations"; /* ROM 0x6e4488 */

static const char mode_fn[] = "navigation_ui_create_mode_list_page"; /* ROM 0x756e88 */
static const char mode_creating[] = "Creating mode select page with 2 options: Walking, Cycling"; /* ROM 0x71672c */
static const char mode_creating_short[] =
    "[navigation.ui]Creating mode select page with 2 options: Walking, Cycling"; /* ROM 0x6f47cc */
static const char mode_height[] =
    "Mode content height set to: %d pixels (items: 2, layout: centered)"; /* ROM 0x704060 */
static const char mode_height_short[] =
    "[navigation.ui]Mode content height set to: %d pixels (items: 2, layout: centered)"; /* ROM 0x6e8d28 */
static const char mode_item[] = "Created mode option %d: %s"; /* ROM 0x76e750 */
static const char mode_item_short[] = "[navigation.ui]Created mode option %d: %s"; /* ROM 0x74057c */
static const char mode_done[] = "Mode select page initialization complete"; /* ROM 0x7405a8 */
static const char mode_done_short[] = "[navigation.ui]Mode select page initialization complete"; /* ROM 0x720638 */

static const char input_fn[] = "NavigationInputEventHandler"; /* ROM 0x76e76c */
static const char input_sent[] = "navigation_data_handler send input event to UI: ret = %d\n"; /* ROM 0x716768 */
static const char input_sent_short[] =
    "[navigation.ui]navigation_data_handler send input event to UI: ret = %d\n"; /* ROM 0x6f4818 */
static const char input_loc_busy[] =
    "navigation_ui_state is NAVIGATION_LOCATION_LIST_SELECT_PAGE and navigation_is_animating is 1, "
    "do not send scroll up event"; /* ROM 0x69ba14 */
static const char input_loc_busy_short[] =
    "[navigation.ui]navigation_ui_state is NAVIGATION_LOCATION_LIST_SELECT_PAGE and "
    "navigation_is_animating is 1, do not send scroll up event"; /* ROM 0x6d4428 */
static const char input_mode_busy[] =
    "navigation_ui_state is NAVIGATION_MODE_SELECT_PAGE and navigation_is_animating is 1, "
    "do not send scroll up event"; /* ROM 0x6a15a4 */
static const char input_mode_busy_short[] =
    "[navigation.ui]navigation_ui_state is NAVIGATION_MODE_SELECT_PAGE and navigation_is_animating "
    "is 1, do not send scroll up event"; /* ROM 0x6d5758 */
static const char input_compass[] = "IMU compass Event."; /* ROM 0x7813e0 */
static const char input_compass_short[] = "[navigation.ui]IMU compass Event."; /* ROM 0x756eac */
static const char input_exit[] = "PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x74b84c */
static const char input_exit_short[] = "[navigation.ui]PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x72b12c */
static const char input_exit_sent[] = "systemClose application send exit command to UI: ret = %d\n"; /* ROM 0x7167a4 */
static const char input_exit_sent_short[] =
    "[navigation.ui]systemClose application send exit command to UI: ret = %d\n"; /* ROM 0x6f4864 */

static const char mini_fn[] = "store_mini_map_data"; /* ROM 0x7813f4 */
static const char mini_start[] = "rle_decompress mini map data"; /* ROM 0x7626d0 */
static const char mini_start_short[] = "[navigation.ui]rle_decompress mini map data"; /* ROM 0x7405d4 */
static const char mini_size[] = "mini_map_size = %d"; /* ROM 0x781408 */
static const char mini_size_short[] = "[navigation.ui]mini_map_size = %d"; /* ROM 0x756ed0 */
static const char mini_raw[] =
    "mini map compress mode is 0, no compress, copy raw data to decode buffer"; /* ROM 0x6f48b0 */
static const char mini_raw_short[] =
    "[navigation.ui]mini map compress mode is 0, no compress, copy raw data to decode buffer"; /* ROM 0x6e44e0 */
static const char mini_rle[] = "rle decompress mini map data len = %d"; /* ROM 0x74b874 */
static const char mini_rle_short[] = "[navigation.ui]rle decompress mini map data len = %d"; /* ROM 0x720670 */
static const char mini_lz4[] = "lz4 decompress mini map data len = %u"; /* ROM 0x74b89c */
static const char mini_lz4_short[] = "[navigation.ui]lz4 decompress mini map data len = %u"; /* ROM 0x7206a8 */
static const char mini_bad[] = "unsupported mini map compress mode = %d"; /* ROM 0x74b8c4 */
static const char mini_bad_short[] = "[navigation.ui]unsupported mini map compress mode = %d"; /* ROM 0x7206e0 */

static const char max_fn[] = "store_max_map_data"; /* ROM 0x78141c */
static const char max_raw[] =
    "max map compress mode is 0, no compress, copy raw data to decode buffer"; /* ROM 0x6fb84c */
static const char max_raw_short[] =
    "[navigation.ui]max map compress mode is 0, no compress, copy raw data to decode buffer"; /* ROM 0x6e4538 */
static const char max_rle[] = "rle decompress max map data len = %d"; /* ROM 0x74b8ec */
static const char max_rle_short[] = "[navigation.ui]rle decompress max map data len = %d"; /* ROM 0x72b160 */
static const char max_lz4[] = "lz4 decompress max map data len = %u"; /* ROM 0x74b914 */
static const char max_lz4_short[] = "[navigation.ui]lz4 decompress max map data len = %u"; /* ROM 0x72b194 */
static const char max_bad[] = "unsupported max map compress mode = %d"; /* ROM 0x74b93c */
static const char max_bad_short[] = "[navigation.ui]unsupported max map compress mode = %d"; /* ROM 0x720718 */

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

/* Stock log pattern: extended record when flag bit 1 is set, compressed record
 * when bit 0 or bit 2 is set. */
#define NAV_LOG0(level, fn, line, msg, msg_short)                                        \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg));   \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output(LOG_FLAGS((level), 0), (msg_short), (msg_short));  \
    } while (0)

#define NAV_LOG(level, fn, line, nargs, msg, msg_short, ...)                             \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg),    \
                               __VA_ARGS__);                                             \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output(LOG_FLAGS((level), (nargs)), (msg_short),          \
                                      (msg_short), __VA_ARGS__);                         \
    } while (0)

void navigation_container_B_fade_out_complete_cb_548484(void *anim);
void navigation_show_container_B_thunk_54853a(void);
void navigation_hide_container_B_thunk_548542(void);
int32_t navigation_ui_create_location_list_page_5485c4(void);
int32_t navigation_ui_create_mode_list_page_548b98(void);
int32_t NavigationInputEventHandler_548f80(uint32_t event, const void *param);
void navigation_ui_sync_navigation_info_5495a8(void);
void store_mini_map_data_549708(void);
void store_max_map_data_549994(void);

/* lv_anim completed_cb of the container B fade-out: hide B, show A at opacity 0
 * and fade A in over 100 ms. */
void navigation_container_B_fade_out_complete_cb_548484(void *anim)
{
    g2_lv_anim_t a;

    (void)anim;
    NAV_LOG0(4u, fade_out_fn, 0x5d4u, fade_out_msg, fade_out_short);
    audio_uart_page_43ded4(g2_navigation_container_b_200747c4, LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_navigation_container_a_200747c0, LV_OBJ_FLAG_HIDDEN);
    audio_uart_display_audio_reset_441488(g2_navigation_container_a_200747c0, LV_OPA_TRANSP, 0u);
    audio_uart_page_invalidate_440656(g2_navigation_container_a_200747c0);
    audio_uart_page_invalidate_440656(g2_navigation_container_b_200747c4);

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_navigation_container_a_200747c0;
    a.exec_cb = navigation_container_opa_anim_exec_cb_547abc;
    audio_uart_lv_anim_values_4506ce(&a, 0, 0xff);
    a.duration = 100;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = navigation_container_A_fade_in_complete_cb_5482c4;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void navigation_show_container_B_thunk_54853a(void)
{
    navigation_show_container_B_with_animation_547ad2();
}

void navigation_hide_container_B_thunk_548542(void)
{
    navigation_hide_container_B_with_animation_547dcc();
}

int32_t navigation_ui_create_location_list_page_5485c4(void)
{
    g2_navigation_location_list_t *list = &g2_navigation_location_list_20376c38;
    void *title;
    void *container;
    void *content;
    uint32_t count;
    int32_t content_h;
    uint32_t i;
    int32_t scroll_y;
    char name[0x40];

    if (g2_navigation_page_root_20074718 != NULL)
        audio_uart_page_44d878(g2_navigation_page_root_20074718);
    NAV_LOG(4u, loc_fn, 0x604u, 1, loc_creating, loc_creating_short, list->count);

    title = audio_uart_page_499416(g2_navigation_page_root_20074718);
    audio_uart_page_49942e(title, audio_uart_page_45fffe(title_key, audio_uart_page_460084(title_key)));
    audio_uart_page_44143e(title, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44140e(title, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f0e0(title, 0);
    audio_uart_page_43f142(title, 0);

    /* 552x200 scrolling viewport below the title. */
    g2_navigation_location_container_2007479c = audio_uart_page_43de82(g2_navigation_page_root_20074718);
    container = g2_navigation_location_container_2007479c;
    audio_uart_page_43f506(container, NAV_LIST_W);
    audio_uart_page_43f568(container, 200);
    audio_uart_page_43f0e0(container, 0);
    audio_uart_page_43f142(container, 60);
    audio_uart_page_44e368(container, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44e3ca(container, LV_DIR_VER);
    audio_uart_page_44129e(container, LV_OPA_TRANSP, 0u);
    audio_uart_page_44146a(container, 10, 0u);
    audio_uart_page_4412ec(container, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44131c(container, 0, 0u);
    audio_uart_page_44120e(container, 0, 0u);
    audio_uart_page_44121c(container, 0, 0u);
    audio_uart_page_44122a(container, 0, 0u);
    audio_uart_page_441238(container, 0, 0u);

    /* Content height: fewer than 5 rows keep the 216 px viewport content
     * (top-aligned); exactly 5 use 266; more use count * 40 + 60. */
    count = list->count;
    g2_navigation_location_content_200747a0 = audio_uart_page_43de82(container);
    content = g2_navigation_location_content_200747a0;
    if ((int32_t)count < 5)
        content_h = 216;
    else if (count == 5u)
        content_h = 266;
    else
        content_h = (int32_t)count * NAV_ITEM_H + 60;
    audio_uart_page_43f506(content, NAV_LIST_W);
    audio_uart_page_43f568(content, content_h);
    audio_uart_page_43f0e0(content, 0);
    audio_uart_page_43f142(content, 0);
    audio_uart_page_44129e(content, LV_OPA_TRANSP, 0u);
    audio_uart_page_44131c(content, 0, 0u);
    lv_obj_set_style_pad_all_545594(content, 0, 0u);
    audio_uart_page_43dfa4(content, LV_OBJ_FLAG_SCROLLABLE);
    (void)audio_uart_lv_style_unlink_450500(content, NULL);
    NAV_LOG(4u, loc_fn, 0x646u, 3, loc_height, loc_height_short, content_h, count,
            (int32_t)count < 5 ? layout_top_aligned : layout_normal);

    (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
    for (i = 0; i < list->count && (int32_t)i < NAV_MAX_LOCATIONS; i++) {
        void *item;
        void *icon;
        void *label;
        const void *icon_src;

        g2_navigation_location_items_20072c68[i] = audio_uart_page_43de82(content);
        item = g2_navigation_location_items_20072c68[i];
        audio_uart_page_44122a(item, 12, 0u);
        audio_uart_page_441238(item, 12, 0u);
        audio_uart_page_43f4c0(item, LV_SIZE_CONTENT, NAV_ITEM_H);
        audio_uart_page_43f0e0(item, 0);
        audio_uart_page_43f142(item, navigation_location_item_y_54c3ec((int32_t)i, (int32_t)count));
        audio_uart_page_44127e(item, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(item, LV_OPA_TRANSP, 0u);
        audio_uart_page_44146a(item, 10, 0u);
        if (i == 0u) {
            /* Row 0 starts selected: white 1 px frame. */
            audio_uart_page_44131c(g2_navigation_location_items_20072c68[0], 1, 0u);
            audio_uart_page_4412ec(g2_navigation_location_items_20072c68[0],
                                   audio_uart_page_44104c(0xffffffu), 0u);
        } else {
            audio_uart_page_44131c(item, 0, 0u);
        }
        audio_uart_page_43dfa4(item, LV_OBJ_FLAG_SCROLLABLE);

        icon = audio_uart_page_498668(item);
        if (list->icon_type[i] == 1u)
            icon_src = g2_navigation_icon_type1_76e654;
        else if (list->icon_type[i] == 2u)
            icon_src = g2_navigation_icon_type2_76e670;
        else
            icon_src = g2_navigation_icon_other_76e68c;
        audio_uart_page_498680(icon, icon_src);
        audio_uart_page_43f506(icon, 24);
        audio_uart_page_43f568(icon, 24);
        audio_uart_page_43f6b8(icon, LV_ALIGN_LEFT_MID, 0, 0);

        label = audio_uart_page_499416(item);
        (void)aeabi_memset_43c0e4(name, sizeof name, 0);
        (void)aeabi_memset_43c0e4(name, sizeof name, 0);
        (void)audio_settings_copy_text(name, list->name[i], g2_log_module_length(list->name[i]));
        name[sizeof name - 1u] = '\0';
        audio_uart_page_layout_499678(label, LV_LABEL_LONG_MODE_DOTS);
        audio_uart_page_441180(label, 490, 0u);
        audio_uart_page_43f568(label, audio_uart_ring_primary_head_cell->line_height);
        audio_uart_page_49942e(label, name);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_43f6d6(label, icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
        if (i == 0u) {
            audio_uart_page_4413ce(icon, LV_OPA_COVER, 0u);
            audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
        } else {
            audio_uart_page_4413ce(icon, 100u, 0u);
            audio_uart_page_44140e(label, audio_uart_page_44104c(NAV_GREY), 0u);
        }
        NAV_LOG(4u, loc_fn, 0x684u, 2, loc_item, loc_item_short, i, name);
    }
    (void)osMutexRelease(g2_navigation_mutex);

    g2_navigation_location_selected_200747a4 = 0;
    g2_navigation_location_scroll_offset_200747a8 = 0;
    audio_uart_page_43f66c(g2_navigation_page_root_20074718);
    scroll_y = navigation_calculate_scroll_position_for_item_54cc00(g2_navigation_location_selected_200747a4);
    NAV_LOG(4u, loc_fn, 0x693u, 2, loc_initial, loc_initial_short,
            g2_navigation_location_selected_200747a4, scroll_y);
    audio_uart_lv_scroll_to_y_44ea04(container, scroll_y, 0u);
    navigation_update_location_item_styles_54d9a4();
    NAV_LOG(4u, loc_fn, 0x69au, 1, loc_done, loc_done_short, list->count);
    return 0;
}

int32_t navigation_ui_create_mode_list_page_548b98(void)
{
    void *container;
    void *content;
    int32_t i;

    if (g2_navigation_page_root_20074718 != NULL)
        audio_uart_page_44d878(g2_navigation_page_root_20074718);
    NAV_LOG0(4u, mode_fn, 0x6a6u, mode_creating, mode_creating_short);

    g2_navigation_mode_container_200747ac = audio_uart_page_43de82(g2_navigation_page_root_20074718);
    container = g2_navigation_mode_container_200747ac;
    audio_uart_page_43f506(container, NAV_MODE_W);
    audio_uart_page_43f568(container, 200);
    audio_uart_page_43f0e0(container, 40);
    audio_uart_page_43f142(container, 20);
    audio_uart_page_44e368(container, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44e3ca(container, LV_DIR_VER);
    audio_uart_page_44129e(container, LV_OPA_TRANSP, 0u);
    audio_uart_page_44146a(container, 10, 0u);
    audio_uart_page_4412ec(container, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44131c(container, 0, 0u);
    audio_uart_page_44120e(container, 16, 0u);
    audio_uart_page_44121c(container, 16, 0u);
    audio_uart_page_44122a(container, 0, 0u);
    audio_uart_page_441238(container, 0, 0u);

    g2_navigation_mode_content_200747b0 = audio_uart_page_43de82(container);
    content = g2_navigation_mode_content_200747b0;
    audio_uart_page_43f506(content, NAV_MODE_W);
    audio_uart_page_43f568(content, 216);
    audio_uart_page_43f0e0(content, 0);
    audio_uart_page_43f142(content, 0);
    audio_uart_page_44129e(content, LV_OPA_TRANSP, 0u);
    audio_uart_page_44131c(content, 0, 0u);
    lv_obj_set_style_pad_all_545594(content, 0, 0u);
    audio_uart_page_43dfa4(content, LV_OBJ_FLAG_SCROLLABLE);
    (void)audio_uart_lv_style_unlink_450500(content, NULL);
    NAV_LOG(4u, mode_fn, 0x6ceu, 1, mode_height, mode_height_short, 216);

    for (i = 0; i < NAV_MODE_COUNT; i++) {
        void *item;
        void *label;
        const char *key;

        g2_navigation_mode_items_20074160[i] = audio_uart_page_43de82(content);
        item = g2_navigation_mode_items_20074160[i];
        audio_uart_page_44122a(item, 20, 0u);
        audio_uart_page_441238(item, 20, 0u);
        audio_uart_page_43f4c0(item, LV_SIZE_CONTENT, NAV_ITEM_H);
        audio_uart_page_43f0e0(item, 0);
        audio_uart_page_43f142(item, navigation_mode_item_y_54dad8(i, NAV_MODE_COUNT));
        audio_uart_page_44127e(item, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(item, LV_OPA_TRANSP, 0u);
        audio_uart_page_44146a(item, 10, 0u);
        if (i == 0) {
            audio_uart_page_44131c(g2_navigation_mode_items_20074160[0], 1, 0u);
            audio_uart_page_4412ec(g2_navigation_mode_items_20074160[0],
                                   audio_uart_page_44104c(0xffffffu), 0u);
        } else {
            audio_uart_page_44131c(item, 0, 0u);
        }
        audio_uart_page_43dfa4(item, LV_OBJ_FLAG_SCROLLABLE);

        label = audio_uart_page_499416(item);
        key = g2_navigation_mode_names_20002d00[i];
        audio_uart_page_49942e(label, audio_uart_page_45fffe(key, audio_uart_page_460084(key)));
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(NAV_GREY), 0u);
        lv_obj_center_4409fa(label);
        NAV_LOG(4u, mode_fn, 0x6f3u, 2, mode_item, mode_item_short, i, key);
    }

    g2_navigation_mode_selected_200747b4 = 0;
    g2_navigation_mode_scroll_offset_200747b8 = 0;
    audio_uart_page_43f66c(g2_navigation_page_root_20074718);
    /* Centre each option horizontally once its content width is known. */
    for (i = 0; i < NAV_MODE_COUNT; i++) {
        if (g2_navigation_mode_items_20074160[i] != NULL)
            audio_uart_page_43f0e0(g2_navigation_mode_items_20074160[i],
                                   (NAV_MODE_W - audio_uart_lv_obj_width_43fd9e(
                                                     g2_navigation_mode_items_20074160[i])) / 2);
    }
    navigation_update_mode_item_styles_54db30();
    NAV_LOG0(4u, mode_fn, 0x70au, mode_done, mode_done_short);
    return 0;
}

/* Sends one 6-byte input record to the master side (app 8) and logs the
 * result. Inlined at every send site in the stock. */
static void send_input_record(const uint8_t *msg, uint32_t line)
{
    uint32_t ret = audio_uart_master_display_refresh(8u, msg, 6u, 0u);

    NAV_LOG(4u, input_fn, line, 1, input_sent, input_sent_short, ret);
}

static void send_simple_event(uint8_t type, uint8_t event, uint32_t line)
{
    uint8_t msg[10];

    (void)aeabi_memset_43c0e4(msg, sizeof msg, 0);
    msg[0] = type;
    msg[1] = event;
    msg[2] = 0;
    msg[3] = 0;
    msg[4] = 0;
    msg[5] = 0;
    send_input_record(msg, line);
}

/* Returns 0 when a scroll is suppressed during a list animation; the other
 * paths fall off the end in the stock (r0 left from the last call). */
int32_t NavigationInputEventHandler_548f80(uint32_t event, const void *param)
{
    uint8_t msg[10];

    if (event == NAV_EVT_CLICK) {
        if ((uint8_t)audio_uart_service_mode() == 1u)
            send_simple_event(0xf2u, NAV_EVT_CLICK, 0x71eu);
    } else if (event == NAV_EVT_SCROLL_UP) {
        if (g2_navigation_ui_state_20074fed == NAVIGATION_LOCATION_LIST_SELECT_PAGE &&
            g2_navigation_location_animating_20074fe8 == 1u) {
            NAV_LOG0(4u, input_fn, 0x723u, input_loc_busy, input_loc_busy_short);
            return 0;
        }
        if (g2_navigation_ui_state_20074fed == NAVIGATION_MODE_SELECT_PAGE &&
            g2_navigation_mode_animating_20074fe9 == 1u) {
            NAV_LOG0(4u, input_fn, 0x728u, input_mode_busy, input_mode_busy_short);
            return 0;
        }
        if ((uint8_t)audio_uart_service_mode() == 1u)
            send_simple_event(0xf2u, NAV_EVT_SCROLL_UP, 0x737u);
    } else if (event == NAV_EVT_SCROLL_DOWN) {
        /* Same guard and the same "scroll up" messages as above. */
        if (g2_navigation_ui_state_20074fed == NAVIGATION_LOCATION_LIST_SELECT_PAGE &&
            g2_navigation_location_animating_20074fe8 == 1u) {
            NAV_LOG0(4u, input_fn, 0x73cu, input_loc_busy, input_loc_busy_short);
            return 0;
        }
        if (g2_navigation_ui_state_20074fed == NAVIGATION_MODE_SELECT_PAGE &&
            g2_navigation_mode_animating_20074fe9 == 1u) {
            NAV_LOG0(4u, input_fn, 0x741u, input_mode_busy, input_mode_busy_short);
            return 0;
        }
        if ((uint8_t)audio_uart_service_mode() == 1u)
            send_simple_event(0xf2u, NAV_EVT_SCROLL_DOWN, 0x750u);
    } else if (event == NAV_EVT_DOUBLE_CLICK) {
        if ((uint8_t)audio_uart_service_mode() == 1u)
            send_simple_event(0xf2u, NAV_EVT_DOUBLE_CLICK, 0x75eu);
    } else if (event == NAV_EVT_IMU_COMPASS) {
        NAV_LOG0(4u, input_fn, 0x761u, input_compass, input_compass_short);
        if ((uint8_t)audio_uart_service_mode() == 1u) {
            /* param + 0x10 points at the signed heading, sent little-endian. */
            const int32_t *heading = *(const int32_t *const *)((const uint8_t *)param + 0x10);

            (void)aeabi_memset_43c0e4(msg, sizeof msg, 0);
            msg[0] = 0xf2u;
            msg[1] = NAV_EVT_IMU_COMPASS;
            msg[2] = (uint8_t)*heading;
            msg[3] = (uint8_t)(*heading >> 8);
            msg[4] = (uint8_t)(*heading >> 16);
            msg[5] = (uint8_t)(*heading >> 24);
            send_input_record(msg, 0x774u);
        }
    } else if (event == NAV_EVT_IMU_COMPASS_RESET) {
        NAV_LOG0(4u, input_fn, 0x777u, input_compass, input_compass_short);
        if ((uint8_t)audio_uart_service_mode() == 1u)
            send_simple_event(0xf7u, 0u, 0x783u);
    } else if (event == NAV_EVT_SYSTEM_EXIT_NOTIFY) {
        NAV_LOG0(4u, input_fn, 0x786u, input_exit, input_exit_short);
        if ((uint8_t)audio_uart_service_mode() == 1u) {
            uint32_t ret;

            (void)aeabi_memset_43c0e4(msg, sizeof msg, 0);
            msg[0] = 0xf4u;
            msg[1] = 0u;
            ret = audio_uart_master_display_refresh(8u, msg, 6u, 0u);
            NAV_LOG(4u, input_fn, 0x78eu, 1, input_exit_sent, input_exit_sent_short, ret);
        }
    }
    return 0;
}

/* Copies one string field: clear the 64-byte slot, then copy strlen bytes. */
static void copy_info_text(char *dst, const char *src)
{
    (void)aeabi_memset_43c0e4(dst, 0x40u, 0);
    (void)audio_queue_copy_bytes(dst, src, g2_log_module_length(src));
}

/* Moves a pending navigation info record from the data handler staging slot
 * into the UI record and clears the staging slot; marks the UI copy invalid
 * when nothing is pending. */
void navigation_ui_sync_navigation_info_5495a8(void)
{
    g2_navigation_info_t *src = &g2_navigation_info_staging_2037bdd0;
    g2_navigation_info_t *dst = &g2_navigation_ui_data_202c0d70.info;

    (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
    if (src->valid == 1u) {
        dst->valid = 1u;
        dst->field_04 = src->field_04;
        copy_info_text(dst->distance, src->distance);
        copy_info_text(dst->road_name, src->road_name);
        copy_info_text(dst->spend_time, src->spend_time);
        copy_info_text(dst->remain_distance, src->remain_distance);
        copy_info_text(dst->eta_time, src->eta_time);
        copy_info_text(dst->speed, src->speed);
        dst->navigate_work_method = src->navigate_work_method;
        (void)aeabi_memset_43c0e4(src, sizeof *src, 0);
    } else {
        dst->valid = 0u;
    }
    (void)osMutexRelease(g2_navigation_mutex);
}

/* Unpacks the received mini map into its 18000-byte decode buffer. */
void store_mini_map_data_549708(void)
{
    g2_navigation_ui_data_t *nav = &g2_navigation_ui_data_202c0d70;
    uint8_t *decode = g2_navigation_mini_map_decode_2032dc74;
    uint32_t len;

    if (nav->mini_map_ready != 1u)
        return;
    NAV_LOG0(4u, mini_fn, 0x7b2u, mini_start, mini_start_short);
    (void)aeabi_memset_43c0e4(decode, NAV_MINI_MAP_SIZE, 0);
    NAV_LOG(4u, mini_fn, 0x7b4u, 1, mini_size, mini_size_short, nav->mini_map_size);
    if (nav->mini_map_compress_mode == 0u) {
        NAV_LOG0(4u, mini_fn, 0x7b6u, mini_raw, mini_raw_short);
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        len = NAV_MINI_MAP_SIZE;
        if (nav->mini_map_size < NAV_MINI_MAP_SIZE)
            len = nav->mini_map_size;
        (void)audio_queue_copy_bytes(decode, nav->mini_map_data, len);
        (void)osMutexRelease(g2_navigation_mutex);
    } else if (nav->mini_map_compress_mode == 1u) {
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        len = evenhub_rle_decompress_4e0c34(nav->mini_map_data, nav->mini_map_size, decode,
                                            NAV_MINI_MAP_SIZE);
        (void)osMutexRelease(g2_navigation_mutex);
        NAV_LOG(4u, mini_fn, 0x7bfu, 1, mini_rle, mini_rle_short, len);
    } else if (nav->mini_map_compress_mode == 2u) {
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        len = evenhub_lz4_decompress_4e0c0c(nav->mini_map_data, nav->mini_map_size, decode,
                                            NAV_MINI_MAP_SIZE);
        (void)osMutexRelease(g2_navigation_mutex);
        NAV_LOG(4u, mini_fn, 0x7c4u, 1, mini_lz4, mini_lz4_short, len);
    } else {
        NAV_LOG(2u, mini_fn, 0x7c6u, 1, mini_bad, mini_bad_short, nav->mini_map_compress_mode);
    }
}

/* Unpacks the received full-size map into its 60000-byte decode buffer. */
void store_max_map_data_549994(void)
{
    g2_navigation_ui_data_t *nav = &g2_navigation_ui_data_202c0d70;
    uint8_t *decode = g2_navigation_max_map_decode_202f3a44;
    uint32_t len;

    if (nav->max_map_ready != 1u)
        return;
    (void)aeabi_memset_43c0e4(decode, NAV_MAX_MAP_SIZE, 0);
    if (nav->max_map_compress_mode == 0u) {
        NAV_LOG0(4u, max_fn, 0x7d0u, max_raw, max_raw_short);
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        len = NAV_MAX_MAP_SIZE;
        if (nav->max_map_size < NAV_MAX_MAP_SIZE)
            len = nav->max_map_size;
        (void)audio_queue_copy_bytes(decode, nav->max_map_data, len);
        (void)osMutexRelease(g2_navigation_mutex);
    } else if (nav->max_map_compress_mode == 1u) {
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        len = evenhub_rle_decompress_4e0c34(nav->max_map_data, nav->max_map_size, decode,
                                            NAV_MAX_MAP_SIZE);
        (void)osMutexRelease(g2_navigation_mutex);
        NAV_LOG(4u, max_fn, 0x7d9u, 1, max_rle, max_rle_short, len);
    } else if (nav->max_map_compress_mode == 2u) {
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        len = evenhub_lz4_decompress_4e0c0c(nav->max_map_data, nav->max_map_size, decode,
                                            NAV_MAX_MAP_SIZE);
        (void)osMutexRelease(g2_navigation_mutex);
        NAV_LOG(4u, max_fn, 0x7deu, 1, max_lz4, max_lz4_short, len);
    } else {
        NAV_LOG(2u, max_fn, 0x7e0u, 1, max_bad, max_bad_short, nav->max_map_compress_mode);
    }
}
