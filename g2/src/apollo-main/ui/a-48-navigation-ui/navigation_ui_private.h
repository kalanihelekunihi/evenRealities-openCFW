/* Private declarations for the a-48 part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c (log tag
 * "navigation.ui", ROM 0x787ab0; file string ROM 0x6fb6e4). Native 0x5455e4..0x548483:
 * compass start/stop, the 576x188 L8 "max map" image, the startup / calibrate / map /
 * exit pages and the container A/B cross-fade. The neighbouring rows of the same TU
 * (0x545588..0x5455e3 and 0x548484..) are in segments a-47 and a-49.
 *
 * Page model: root 0x20074718 (576x288, created by the startup page) holds one page at a
 * time. The map page holds three full-size layers: A (mini map: turn icon, road texts,
 * clock, rotated compass), B (max map: clock row and the 576x188 map image, hidden at
 * start) and C ("recalculating", hidden). A tap queued in the page FIFO toggles A <-> B
 * with 100 ms opacity fades. */
#ifndef G2_A48_NAVIGATION_UI_PRIVATE_H
#define G2_A48_NAVIGATION_UI_PRIVATE_H

#include <stdint.h>
#include <stddef.h>
#include "g2_ui_common_api.h"

/* LVGL 9 constants as used by the stock calls. */
#define LV_PART_MAIN 0u
#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_OPA_TRANSP 0u
#define LV_OPA_COVER 0xffu
#define LV_ALIGN_TOP_MID 2u
#define LV_ALIGN_TOP_RIGHT 3u
#define LV_ALIGN_CENTER 9u
#define LV_ALIGN_OUT_LEFT_MID 0x11u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_EVENT_CLICKED 10u
#define WAIT_FOREVER 0xffffffffu

#define NAV_SCREEN_W 0x240 /* 576 */
#define NAV_SCREEN_H 0x120 /* 288 */
#define NAV_MAX_MAP_W 0x240u
#define NAV_MAX_MAP_H 0xbcu /* 188 */
#define NAV_MAX_MAP_L8_SIZE 0x1a700u /* 576 * 188 bytes of L8 */
#define NAV_BMP_SIGNATURE 0x4d42u
#define NAV_BMP_BIT_DEPTH 4u
#define NAV_BMP_PALETTE_DEFAULT 16u
#define NAV_BMP_ROW_STRIDE 0x120u /* 576 4-bit pixels */

#define LV_IMAGE_HEADER_MAGIC 0x19u
#define LV_COLOR_FORMAT_L8 0x06u

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

/* LVGL 9 lv_image_header_t / lv_image_dsc_t. */
typedef struct {
    uint32_t magic : 8;
    uint32_t cf : 8;
    uint32_t flags : 16;
    uint32_t w : 16;
    uint32_t h : 16;
    uint32_t stride : 16;
    uint32_t reserved_2 : 16;
} nav_image_header_t;

typedef struct {
    nav_image_header_t header;           /* +0x00 */
    uint32_t data_size;                  /* +0x0c */
    const uint8_t *data;                 /* +0x10 */
    const void *reserved;                /* +0x14 */
    const void *reserved_2;              /* +0x18 */
} nav_image_dsc_t;
_Static_assert(sizeof(nav_image_dsc_t) == 0x1c, "lv_image_dsc_t");

/* Windows BMP file + info header, 4-bit palette layout. */
typedef struct __attribute__((packed)) {
    uint16_t signature;                  /* +0x00 */
    uint32_t file_size;                  /* +0x02 */
    uint32_t reserved;                   /* +0x06 */
    uint32_t data_offset;                /* +0x0a */
    uint32_t info_size;                  /* +0x0e */
    int32_t width;                       /* +0x12 */
    int32_t height;                      /* +0x16 >0: bottom-up rows */
    uint16_t planes;                     /* +0x1a */
    uint16_t bit_count;                  /* +0x1c */
    uint32_t compression;                /* +0x1e */
    uint32_t image_size;                 /* +0x22 */
    int32_t x_ppm;                       /* +0x26 */
    int32_t y_ppm;                       /* +0x2a */
    uint32_t colors_used;                /* +0x2e 0 = 16 */
    uint32_t colors_important;           /* +0x32 */
    uint8_t palette[1][4];               /* +0x36 {blue, green, red, 0} */
} nav_bmp_header_t;
_Static_assert(offsetof(nav_bmp_header_t, palette) == 0x36, "bmp header");

/* Shared with segment a-49 (ui/a-49-navigation-ui/navigation_ui_pages.c): same layouts.
 * Location list pushed by the phone (RAM 0x20376c38). */
#define NAV_MAX_LOCATIONS 20
#define NAV_MODE_COUNT 2
#define NAV_MINI_MAP_SIZE 18000u     /* 0x4650 */
#define NAV_MAX_MAP_SIZE 60000u      /* 0xea60 */

typedef struct {
    uint32_t count;                               /* +0x000 */
    uint8_t header_04[2];                         /* +0x004 */
    char name[NAV_MAX_LOCATIONS][0x40];           /* +0x006 */
    uint8_t reserved_506[2];                      /* +0x506 */
    uint32_t icon_type[NAV_MAX_LOCATIONS];        /* +0x508 1 / 2 / other */
    uint8_t reserved_558[4];                      /* +0x558 */
} g2_navigation_location_list_t;
/* Stock clears 0x55c bytes (ui/a-61-navigation-data/navigation_data_handler.c). */
_Static_assert(sizeof(g2_navigation_location_list_t) == 0x55c, "location list");

/* Navigation info record (staged at RAM 0x2037bdd0, head of the UI record). */
typedef struct {
    uint8_t valid;                 /* +0x000 */
    uint8_t reserved_01[3];
    uint32_t field_04;             /* +0x004 turn icon code (navigation_icon_name_for_code) */
    char distance[0x40];           /* +0x008 A: right of the turn icon */
    char road_name[0x40];          /* +0x048 A: 368x30 at (72, 260) */
    char spend_time[0x40];         /* +0x088 A/B: top right */
    char remain_distance[0x40];    /* +0x0c8 A/B: left of spend_time */
    char eta_time[0x40];           /* +0x108 B: left of speed (or of remain_distance) */
    char speed[0x40];              /* +0x148 B: left of remain_distance, hidden in method 1 */
    uint32_t navigate_work_method; /* +0x188 1: no speed, alternative clock icon */
} g2_navigation_info_t;
_Static_assert(sizeof(g2_navigation_info_t) == 0x18c, "navigation info record");

/* UI navigation record (RAM 0x202c0d70, 0x13258 bytes). */
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
_Static_assert(offsetof(g2_navigation_ui_data_t, max_map_ready) == 0x47ed, "max map flag");
_Static_assert(sizeof(g2_navigation_ui_data_t) == 0x13258, "navigation ui record");

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

/* generic_animation config / handle (ui/a-10-generic-animation). */
typedef struct {
    const void *const *frames;           /* +0x00 */
    uint32_t frame_count;                /* +0x04 */
    uint32_t period_ms;                  /* +0x08 */
    uint8_t mode;                        /* +0x0c */
    uint8_t reserved_0d[3];
    int32_t width;                       /* +0x10 */
    int32_t height;                      /* +0x14 */
    uint8_t color_a[3];                  /* +0x18 */
    uint8_t opa_a;                       /* +0x1b */
    uint8_t bg_color[3];                 /* +0x1c */
    uint8_t bg_opa;                      /* +0x1f */
} g2_generic_animation_config_t;
_Static_assert(sizeof(g2_generic_animation_config_t) == 0x20, "anim config");

typedef struct {
    void *image;                         /* +0x00 lv_image */
} g2_generic_animation_t;

/* am_hal_rtc_time_t word layout filled by service_time_epoch_to_calendar. */
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

/* LVGL 9 (stock copies). lv_color_t {blue, green, red} travels in r0. */
extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag);    /* lv_obj_has_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                       /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                       /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);            /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                       /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                                  /* lv_obj_update_layout */
extern void audio_uart_page_43f6ac(void *obj, uint32_t align);                  /* lv_obj_set_align */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                                  /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);                       /* lv_obj_get_width */
extern void audio_uart_page_invalidate_440656(void *obj);                       /* lv_obj_invalidate */
extern void lv_obj_center_4409fa(void *obj);                                    /* lv_obj_center */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern uint32_t audio_uart_page_441068(uint32_t r, uint32_t g, uint32_t b);     /* lv_color_make */
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
extern void audio_uart_page_44d878(void *obj);                                  /* lv_obj_clean */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *anim);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *anim);
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *anim, int32_t start, int32_t end);
extern int32_t audio_uart_lv_anim_path_450688(void *anim);                      /* ease_in_out */
extern void *audio_uart_page_498668(void *parent);                              /* lv_image_create */
extern void audio_uart_page_498680(void *obj, const void *src);                 /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *obj, const char *text);                /* lv_label_set_text */
extern uint32_t audio_uart_lv_image_cache_enabled_4d4b24(void);
/* Static inline LVGL header helpers emitted in this TU (segment a-47). */
extern uint8_t lv_obj_get_style_opa_545588(void *obj, uint32_t part);           /* LV_STYLE_OPA */
extern void lv_obj_set_style_pad_all_545594(void *obj, int32_t v, uint32_t sel);

/* i18n. */
extern uint32_t audio_uart_page_460084(const char *key);                        /* index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);     /* localized text */

/* Common UI / services. */
extern g2_generic_animation_t *generic_animation_create_463c68(void *parent,
                                                               const g2_generic_animation_config_t *config);
extern void generic_animation_destroy_463e1c(g2_generic_animation_t *anim, uint8_t delete_image);
extern void generic_animation_start_463ea6(g2_generic_animation_t *anim);
extern uint32_t UX_GetSystemBLEStatus(void);                                    /* 0x47d8ce */
extern uint32_t audio_uart_service_mode(void);                                  /* 0x45a570, 1 = master */
extern uint32_t semantic_get_flag_20074fdc(void);                               /* 0x4a6562 */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);              /* 0x464bb2 */
extern uint32_t service_time_current_epoch_get(void);                           /* 0x44a1c6 */
extern void service_time_epoch_to_calendar(uint32_t epoch, g2_calendar_t *out); /* 0x44a100 */
extern uint32_t audio_time_format_mode_46650c(void);                            /* 1 = 12-hour clock */
extern int32_t HUB_Open(uint8_t func_type);                                     /* 0x4a6d58 */
extern int32_t HUB_Close(uint8_t func_type);                                    /* 0x4a6dca */
extern uint32_t audio_hub_parameter_config_4a6e3c(uint32_t type, const int32_t *param); /* HUB_ParameterConfig */
extern void navigation_mutex_init_585ca4(void);
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                     /* 0x44981c */

/* navigation_data_handler.c. */
extern int32_t navigation_send_type_1_allocating(void);                         /* 0x586448 */
extern int32_t navigation_send_type_16_allocating(void);                        /* 0x5867fc */
extern int32_t navigation_send_type_5_shared(uint8_t value, uint32_t arg);      /* 0x5869b4 */
extern const void *navigation_icon_name_for_code(uint32_t code);                /* 0x588388 */

/* navigation_ui.c rows outside this segment. */
extern void *navigation_create_rotated_img_54e44c(void *parent, int32_t w, int32_t h, int32_t x,
                                                  int32_t y);
extern int32_t navigation_update_rotated_img_54e660(void *img, const uint8_t *bmp, int32_t w,
                                                    int32_t h, int32_t angle, uint32_t bpp);
extern void navigation_container_B_fade_out_complete_cb_548484(void *anim);
extern void navigation_show_container_B_thunk_54853a(void);                     /* -> 0x547ad2 */
extern void navigation_hide_container_B_thunk_548542(void);                     /* -> 0x547dcc */

/* Runtime. */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy4 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);     /* memset 0x43c0e4 */
extern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *range);     /* {addr, size} */
extern int32_t iar_abs_509694(int32_t v);
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...);  /* sprintf 0x4b4728 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* RAM state of navigation_ui.c. */
extern void *g2_navigation_page_root_20074718;              /* RAM 0x20074718 page root (576x288) */
extern void *g2_navigation_mutex;                   /* RAM 0x2007471c */
extern uint32_t g2_navigation_var_20074720;                /* RAM 0x20074720 */
extern g2_ui_fifo_t *g2_nav_event_fifo_20074734;    /* RAM 0x20074734 queued input events */
extern uint32_t g2_nav_container_b_shown_2007473c;  /* RAM 0x2007473c tap toggle */
extern void *g2_navigation_startup_obj_20074740;           /* RAM 0x20074740 startup page layer */
extern uint32_t g2_navigation_var_20074744;                /* RAM 0x20074744 */
extern uint32_t g2_nav_var_20074748;                /* RAM 0x20074748 0xf0 when BLE is down */
extern uint32_t g2_nav_var_2007474c;                /* RAM 0x2007474c 1 when BLE is down */
extern g2_generic_animation_t *g2_nav_calibrate_anim_20074750; /* RAM 0x20074750 */
extern uint32_t g2_nav_var_20074754;                /* RAM 0x20074754 */
extern uint32_t g2_nav_var_20074758;                /* RAM 0x20074758 */
extern uint32_t g2_navigation_clock_hour_2007475c;         /* RAM 0x2007475c */
extern uint32_t g2_navigation_clock_minute_20074760;       /* RAM 0x20074760 */
extern void *g2_nav_b_clock_label_20074764;         /* RAM 0x20074764 */
extern void *g2_navigation_b_text_c8_label_20074768;       /* RAM 0x20074768 */
extern void *g2_navigation_b_text_88_label_2007476c;       /* RAM 0x2007476c */
extern void *g2_navigation_b_text_148_label_20074770;      /* RAM 0x20074770 */
extern void *g2_navigation_b_clock_icon_20074774;          /* RAM 0x20074774 */
extern void *g2_navigation_b_text_108_label_20074778;      /* RAM 0x20074778 */
extern void *g2_nav_max_map_img_2007477c;           /* RAM 0x2007477c */
extern void *g2_nav_b_loading_label_20074780;       /* RAM 0x20074780 */
extern void *g2_navigation_a_marker_img_20074784;          /* RAM 0x20074784 */
extern void *g2_navigation_a_corner_tl_img_20074788;       /* RAM 0x20074788 */
extern void *g2_navigation_a_corner_tr_img_2007478c;       /* RAM 0x2007478c */
extern void *g2_navigation_a_corner_bl_img_20074790;       /* RAM 0x20074790 */
extern void *g2_navigation_a_corner_br_img_20074794;       /* RAM 0x20074794 */
extern void *g2_navigation_c_recalculating_label_20074798; /* RAM 0x20074798 */
extern void *g2_navigation_location_container_2007479c;                /* RAM 0x2007479c */
extern void *g2_navigation_location_content_200747a0;                /* RAM 0x200747a0 */
extern int32_t g2_navigation_location_selected_200747a4;                /* RAM 0x200747a4 */
extern int32_t g2_navigation_location_scroll_offset_200747a8;                /* RAM 0x200747a8 */
extern void *g2_navigation_mode_container_200747ac;                /* RAM 0x200747ac */
extern void *g2_navigation_mode_content_200747b0;                /* RAM 0x200747b0 */
extern int32_t g2_navigation_mode_selected_200747b4;                /* RAM 0x200747b4 */
extern int32_t g2_navigation_mode_scroll_offset_200747b8;                /* RAM 0x200747b8 */
extern void *g2_navigation_map_page_200747bc;              /* RAM 0x200747bc */
extern void *g2_navigation_container_a_200747c0;           /* RAM 0x200747c0 mini map layer */
extern void *g2_navigation_container_b_200747c4;           /* RAM 0x200747c4 max map layer */
extern void *g2_nav_container_c_200747c8;           /* RAM 0x200747c8 recalculating layer */
extern void *g2_navigation_a_turn_icon_200747cc;           /* RAM 0x200747cc */
extern void *g2_navigation_a_turn_label_200747d0;          /* RAM 0x200747d0 */
extern void *g2_navigation_a_road_label_200747d4;          /* RAM 0x200747d4 */
extern void *g2_navigation_a_text_c8_label_200747d8;       /* RAM 0x200747d8 */
extern void *g2_navigation_a_text_88_label_200747dc;       /* RAM 0x200747dc */
extern void *g2_nav_a_clock_label_200747e0;         /* RAM 0x200747e0 */
extern void *g2_navigation_a_clock_icon_200747e4;          /* RAM 0x200747e4 */
extern void *g2_nav_a_compass_img_200747e8;         /* RAM 0x200747e8 */
extern void *g2_nav_a_loading_label_200747ec;       /* RAM 0x200747ec */
extern uint32_t g2_navigation_var_200747f0;                /* RAM 0x200747f0 */
extern uint32_t g2_navigation_var_200747f4;                /* RAM 0x200747f4 */
extern uint32_t g2_navigation_var_200747f8;                /* RAM 0x200747f8 */
extern uint32_t g2_navigation_var_200747fc;                /* RAM 0x200747fc */
extern void *g2_navigation_calibrate_page_20074800;        /* RAM 0x20074800 */
extern void *g2_navigation_calibrate_label_20074804;       /* RAM 0x20074804 */
extern uint32_t g2_nav_compass_enabled_20074808;    /* RAM 0x20074808 */
extern int32_t g2_nav_compass_heading_2007480c;     /* RAM 0x2007480c degrees */
extern uint8_t g2_navigation_flag_20074fe6;                /* RAM 0x20074fe6 */
extern uint8_t g2_nav_flag_20074fe7;                /* RAM 0x20074fe7 */
extern uint8_t g2_navigation_location_animating_20074fe8;                /* RAM 0x20074fe8 */
extern uint8_t g2_navigation_mode_animating_20074fe9;                /* RAM 0x20074fe9 */
extern uint8_t g2_navigation_flag_20074fea;                /* RAM 0x20074fea */
extern uint8_t g2_navigation_flag_20074feb;                /* RAM 0x20074feb */
extern uint8_t g2_nav_animation_running_20074fec;   /* RAM 0x20074fec */
extern uint8_t g2_navigation_ui_state_20074fed;            /* RAM 0x20074fed */
extern uint32_t g2_nav_var_20002cfc;                /* RAM 0x20002cfc (.data), reset to 20 */
extern void *g2_navigation_location_items_20072c68[NAV_MAX_LOCATIONS];           /* RAM 0x20072c68 */
extern void *g2_navigation_mode_items_20074160[NAV_MODE_COUNT];              /* RAM 0x20074160 */
extern uint8_t g2_nav_buf_200f4784[0x40];           /* RAM 0x200f4784 */
extern uint8_t g2_navigation_max_map_buf_202a6670[NAV_MAX_MAP_L8_SIZE]; /* RAM 0x202a6670 L8 pixels */
extern nav_image_dsc_t g2_navigation_max_map_dsc_20073aac; /* RAM 0x20073aac */
extern g2_navigation_ui_data_t g2_navigation_ui_data_202c0d70;          /* RAM 0x202c0d70 */
extern uint8_t g2_nav_buf_202e4fc8[0xea7c];         /* RAM 0x202e4fc8 */
extern uint8_t g2_navigation_max_map_decode_202f3a44[NAV_MAX_MAP_SIZE]; /* RAM 0x202f3a44 BMP */
extern uint8_t g2_nav_buf_20329600[0x4674];         /* RAM 0x20329600 */
extern uint8_t g2_navigation_mini_map_decode_2032dc74[NAV_MINI_MAP_SIZE]; /* RAM 0x2032dc74 BMP */
extern g2_navigation_location_list_t g2_navigation_location_list_20376c38;          /* RAM 0x20376c38 */
extern g2_navigation_info_t g2_navigation_info_staging_2037bdd0;          /* RAM 0x2037bdd0 */
extern const void *audio_uart_ring_primary_head_cell; /* RAM 0x200746dc: active lv_font_t * */

/* ROM lv_image_dsc_t (cf 0x19 L8 header word 0x619). */
extern const uint8_t g2_navigation_img_clock_mode1_7747c8[];  /* ROM 0x7747c8 24x24 */
extern const uint8_t g2_navigation_img_clock_76a86c[];        /* ROM 0x76a86c 24x24 */
extern const uint8_t g2_navigation_img_marker_76acb0[];       /* ROM 0x76acb0 20x18 */
extern const uint8_t g2_navigation_img_corner_tl_76c4f8[];    /* ROM 0x76c4f8 6x6 */
extern const uint8_t g2_navigation_img_corner_tr_770ac0[];    /* ROM 0x770ac0 6x6 */
extern const uint8_t g2_navigation_img_corner_bl_76be84[];    /* ROM 0x76be84 6x6 */
extern const uint8_t g2_navigation_img_corner_br_7709a8[];    /* ROM 0x7709a8 6x6 */
/* {frames 0x20002d08, 64 frames, 50 ms, loop, 32x32, black/opa 0xff, 0}. */
extern const g2_generic_animation_config_t g2_navigation_calibrate_anim_config_762870; /* ROM 0x762870 */

static const char nav_tag[] = "navigation.ui"; /* ROM 0x787ab0 */
static const char nav_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_ui.c"; /* ROM 0x6fb6e4 */

#define NAV_LOG(level, func, line, cflags, text, short_text, ...)                             \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), nav_tag, nav_file, (func), (line), (text),            \
                               ##__VA_ARGS__);                                                \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

/* This segment's functions (stock names from the log strings, plus address suffix). */
int32_t StartIMUCompassFunc_5455e4(void);
int32_t StopIMUCompassFunc_54566c(void);
uint8_t color_to_gray_5456d6(uint32_t color);
void *navigation_create_max_map_5456f6(void *parent, int32_t x, int32_t y);
uint16_t navigation_crc16_ccitt_545868(const uint8_t *data, uint32_t len);
int32_t navigation_set_max_map_data_5458a2(void *img, const uint8_t *bmp);
void navigation_free_max_map_buffer_545c5a(void);
int32_t navigation_ui_startup_page_create_545d18(void *parent, const uint8_t *msg, uint16_t wait_map);
void navigation_ui_update_map_texts_5464b8(void);
int32_t navigation_ui_create_calibrate_compass_page_546620(void);
int32_t navigation_ui_create_map_page_54692c(void);
void navigation_ui_create_break_exit_page_5476e4(void);
void navigation_ui_create_none_location_list_page_5477ac(void);
void navigation_ui_startup_failed_exit_page_54787c(uint32_t reason);
void navigation_ui_completed_exit_page_5479c8(void);
void navigation_container_opa_anim_exec_cb_547abc(void *obj, int32_t opa);
void navigation_show_container_B_with_animation_547ad2(void);
void navigation_hide_container_B_with_animation_547dcc(void);
void navigation_container_A_fade_out_complete_cb_547ec8(void *anim);
void navigation_container_B_fade_in_complete_cb_548014(void *anim);
void navigation_container_A_fade_in_complete_cb_5482c4(void *anim);

#endif
