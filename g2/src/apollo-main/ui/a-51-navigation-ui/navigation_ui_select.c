/* Navigation UI location / travel-mode select pages, part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c (log tag
 * "navigation.ui", ROM 0x787ab0). Native 0x54c268..0x54c3bd (exit page handler),
 * 0x54c3ec..0x54c575, 0x54c5b0..0x54c7f3, 0x54c83c..0x54cc8d, 0x54ccd4..0x54cea9,
 * 0x54cebc..0x54cf2b, 0x54cfd0..0x54d92b, 0x54d948..0x54d97b, 0x54d9a4..0x54dabb,
 * 0x54dad8..0x54db1d, 0x54db30..0x54dbfb, 0x54dc24..0x54dd7f, 0x54dd9c..0x54dfa9,
 * 0x54dfb4..0x54e199 and 0x54e1a8..0x54e43f; literal pools in between. The page
 * builders and the input dispatcher of the same TU are in ui/a-49-navigation-ui.
 *
 * Location list: up to 20 rows of 40 px in a 5-row viewport (RAM 0x2007479c) whose
 * content (0x200747a0) scrolls by whole rows. Up/down move the focus border and, once
 * the focus reaches row 1 / row 3 of the viewport, scroll the content by one row with a
 * 200 ms ease-in-out animation. At either end a 16 px "rubber band" bounce (200 ms out,
 * 200 ms back) is played instead. Input arriving while an animation runs is queued in
 * the select page FIFO (RAM 0x20074738) and drained by the animation completion
 * callbacks. A click on a location copies its name, clears the page and opens the
 * 2-row travel mode list (Walking / Cycling), whose click stores the mode (1-based).
 *
 * The page FIFO delivers 0x44 for "scroll up" and 0x45 for "scroll down"; the stock
 * handlers map 0x44 to NAV_EVENT_DOWN and 0x45 to NAV_EVENT_UP. */
#include <stdint.h>
#include <stddef.h>
#include "g2_ui_common_api.h"

#define NAV_MAX_LOCATIONS 20
#define NAV_MODE_COUNT 2
#define NAV_ITEM_H 40
#define NAV_VISIBLE_ITEMS 5
#define NAV_RUBBER_BAND_PX 16
#define NAV_ANIM_MS 200
#define NAV_GREY 0x444444u /* ROM 0x54e1a4 */
#define LV_SCALE_NONE 0x100

/* Page FIFO events. */
enum { NAV_FIFO_CLICK = 0x0a, NAV_FIFO_SCROLL_UP = 0x44, NAV_FIFO_SCROLL_DOWN = 0x45 };

/* navigation_inject_event / mode_inject_event arguments. */
enum { NAV_EVENT_UP = 0, NAV_EVENT_DOWN = 1, NAV_EVENT_SELECT = 2, NAV_EVENT_CANCEL = 3 };

/* navigation_ui_state values (RAM byte 0x20074fed). */
enum { NAVIGATION_LOCATION_LIST_SELECT_PAGE = 2, NAVIGATION_MODE_SELECT_PAGE = 9 };

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stock 0x60-byte frames. */
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
    uint32_t reverse_delay;             /* +0x38 (playback delay) */
    uint32_t reverse_duration;          /* +0x3c (playback time) */
    uint8_t rest[0x20];                 /* +0x40 */
} g2_lv_anim_t;
_Static_assert(offsetof(g2_lv_anim_t, reverse_duration) == 0x3c, "lv_anim_t playback time");
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* Location list pushed by the phone (RAM 0x20376c38, cleared as 0x55c bytes on exit;
 * same layout as ui/a-49-navigation-ui). */
typedef struct {
    uint32_t count;                               /* +0x000 */
    uint8_t header_04[2];                         /* +0x004 */
    char name[NAV_MAX_LOCATIONS][0x40];           /* +0x006 */
    uint8_t reserved_506[2];                      /* +0x506 */
    uint32_t icon_type[NAV_MAX_LOCATIONS];        /* +0x508 */
    uint8_t reserved_558[4];                      /* +0x558 */
} g2_navigation_location_list_t;
_Static_assert(offsetof(g2_navigation_location_list_t, name) == 0x006, "location name");
_Static_assert(sizeof(g2_navigation_location_list_t) == 0x55c, "location list");

/* RAM state of navigation_ui.c (names shared with ui/a-48 and ui/a-49). */
extern void *g2_navigation_page_root_20074718;                      /* RAM 0x20074718 */
extern g2_ui_fifo_t *g2_nav_list_event_fifo_20074738;            /* RAM 0x20074738 */
extern uint32_t g2_nav_var_20074754;                                /* RAM 0x20074754 selected location */
extern uint32_t g2_nav_var_20074758;                                /* RAM 0x20074758 */
extern void *g2_nav_b_clock_label_20074764;                         /* RAM 0x20074764 */
extern void *g2_navigation_location_container_2007479c;             /* RAM 0x2007479c viewport */
extern void *g2_navigation_location_content_200747a0;               /* RAM 0x200747a0 */
extern int32_t g2_navigation_location_selected_200747a4;            /* RAM 0x200747a4 */
extern int32_t g2_navigation_location_scroll_offset_200747a8;       /* RAM 0x200747a8, in rows */
extern void *g2_navigation_mode_container_200747ac;                 /* RAM 0x200747ac */
extern void *g2_navigation_mode_content_200747b0;                   /* RAM 0x200747b0 */
extern int32_t g2_navigation_mode_selected_200747b4;                /* RAM 0x200747b4 */
extern int32_t g2_navigation_mode_scroll_offset_200747b8;           /* RAM 0x200747b8 */
extern void *g2_nav_a_clock_label_200747e0;                         /* RAM 0x200747e0 */
extern void *g2_navigation_location_items_20072c68[NAV_MAX_LOCATIONS]; /* RAM 0x20072c68 */
extern void *g2_navigation_mode_items_20074160[NAV_MODE_COUNT];     /* RAM 0x20074160 */
extern const char *g2_navigation_mode_names_20002d00[NAV_MODE_COUNT]; /* RAM .data 0x20002d00 */
extern uint8_t g2_nav_flag_20074fe7;                                /* RAM 0x20074fe7 chosen mode + 1 */
extern uint8_t g2_navigation_location_animating_20074fe8;           /* RAM 0x20074fe8 */
extern uint8_t g2_navigation_mode_animating_20074fe9;               /* RAM 0x20074fe9 */
extern uint8_t g2_navigation_ui_state_20074fed;                     /* RAM 0x20074fed */
extern g2_navigation_location_list_t g2_navigation_location_list_20376c38; /* RAM 0x20376c38 */
extern uint8_t g2_nav_buf_200f4784[0x40];                            /* RAM 0x200f4784 selected name */

/* LVGL 9 (stock copies). */
extern void audio_uart_page_43f142(void *obj, int32_t y);                     /* lv_obj_set_y */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                         /* lv_obj_get_y */
extern uint32_t audio_uart_page_44104c(uint32_t hex);                         /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);  /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);    /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);  /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);       /* border_width */
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t sel);    /* image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);  /* text_color */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void audio_uart_page_44d878(void *obj);                                /* lv_obj_clean */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);        /* lv_obj_get_child */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                         /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *obj);                    /* lv_obj_get_scroll_top */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *anim);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *anim);
extern uint32_t audio_uart_anim_delete_450500(void *var, void (*exec_cb)(void *, int32_t)); /* lv_anim_delete */
extern int32_t audio_uart_lv_anim_default_path_450634(void *anim);           /* lv_anim_path_linear */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);                   /* lv_anim_path_ease_out */
extern int32_t audio_uart_lv_anim_path_450688(void *anim);                   /* lv_anim_path_ease_in_out */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *anim, int32_t start, int32_t end);
/* Static inline LVGL helper emitted in this TU (segment a-47): transform_scale_x + _y. */
extern void lv_obj_set_style_transform_scale_5455c6(void *obj, int32_t v, uint32_t sel);

/* Runtime. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Same TU, reconstructed in ui/a-48-navigation-ui and ui/a-49-navigation-ui. */
extern void navigation_free_max_map_buffer_545c5a(void);
extern int32_t navigation_ui_create_mode_list_page_548b98(void);
/* navigation_data_handler.c. */
extern int32_t navigation_send_type_13_allocating(void); /* 0x586584 */

/* This segment. */
uint32_t navigation_ui_exit_page_handler_54c268(void);
int32_t navigation_location_item_y_54c3ec(int32_t index, int32_t count);
void navigation_location_list_select_page_motion_fifo_handler_54c3f2(void);
void navigation_rubber_band_anim_complete_cb_54c5b0(void *anim);
void navigation_anim_set_y_exec_cb_54c83c(void *obj, int32_t y);
void trigger_navigation_rubber_band_effect_54c844(uint8_t is_top);
void navigation_focus_change_anim_exec_cb_54cb56(void *var, int32_t value);
void navigation_focus_change_anim_ready_cb_54cb58(void *anim);
void navigation_focus_change_anim_start_54cbaa(void);
int32_t navigation_calculate_scroll_position_for_item_54cc00(int32_t item_index);
void navigation_scroll_anim_complete_cb_54ccd4(void *anim);
void navigation_scroll_anim_exec_cb_54cebc(void *obj, int32_t y);
void navigation_scroll_anim_ready_cb_54cec6(void *anim);
void navigation_scroll_anim_start_54cece(void *obj, int32_t target_y, int32_t duration);
void navigation_inject_event_54cfd0(uint8_t event);
void navigation_clear_location_focus_border_54d948(void);
void navigation_update_location_item_styles_54d9a4(void);
int32_t navigation_mode_item_y_54dad8(int32_t index, int32_t count);
void mode_scroll_anim_exec_cb_54daea(void *obj, int32_t y);
void navigation_clear_mode_focus_border_54daf4(void);
void navigation_update_mode_item_styles_54db30(void);
void navigation_mode_select_page_anim_handler_54dc24(void);
void mode_rubber_band_anim_complete_cb_54dd9c(void *anim);
void trigger_mode_rubber_band_effect_54dfb4(uint8_t is_top);
void mode_inject_event_54e1a8(uint8_t event);

static const char module_tag[] = "navigation.ui"; /* ROM 0x787ab0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_ui.c"; /* ROM 0x6fb6e4 */

#define NAV_LOG(level, fn, line, cflags, msg, msg_short, ...)                                        \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

/* Function names (__func__ strings). */
static const char fn_exit[] = "navigation_ui_exit_page_handler"; /* ROM 0x762710 */
static const char fn_motion_fifo[] = "navigation_location_list_select_page_motion_fifo_handler"; /* ROM 0x7169fc */
static const char fn_rubber_done[] = "navigation_rubber_band_anim_complete_cb"; /* ROM 0x74b9b4 */
static const char fn_rubber[] = "trigger_navigation_rubber_band_effect"; /* ROM 0x74b9dc */
static const char fn_focus_ready[] = "navigation_focus_change_anim_ready_cb"; /* ROM 0x74ba04 */
static const char fn_calc[] = "navigation_calculate_scroll_position_for_item"; /* ROM 0x735b64 */
static const char fn_scroll_done[] = "navigation_scroll_anim_complete_cb"; /* ROM 0x756f84 */
static const char fn_inject[] = "navigation_inject_event"; /* ROM 0x7799ac */
static const char fn_mode_fifo[] = "navigation_mode_select_page_anim_handler"; /* ROM 0x7406dc */
static const char fn_mode_rubber_done[] = "mode_rubber_band_anim_complete_cb"; /* ROM 0x757038 */
static const char fn_mode_rubber[] = "trigger_mode_rubber_band_effect"; /* ROM 0x762770 */
static const char fn_mode_inject[] = "mode_inject_event"; /* ROM 0x781430 */

/* Exit page handler. */
static const char exit_msg[] = "navigation_ui_exit_page_handler"; /* ROM 0x762730 */
static const char exit_msg_s[] = "[navigation.ui]navigation_ui_exit_page_handler"; /* ROM 0x735b34 */
static const char reset_nav_y[] = "Reset navigation_content_container Y to 0"; /* ROM 0x74062c */
static const char reset_nav_y_s[] = "[navigation.ui]Reset navigation_content_container Y to 0"; /* ROM 0x7169c0 */
static const char reset_mode_y[] = "Reset mode_content_container Y to 0"; /* ROM 0x756f60 */
static const char reset_mode_y_s[] = "[navigation.ui]Reset mode_content_container Y to 0"; /* ROM 0x72b264 */

/* Location page FIFO drain. */
static const char fifo_rx[] = "navigation_ui_reflash_page_handler: receive event from fifo"; /* ROM 0x716a38 */
static const char fifo_rx_s[] =
    "[navigation.ui]navigation_ui_reflash_page_handler: receive event from fifo"; /* ROM 0x6f4bf4 */
static const char fifo_click[] = "navigation_ui_reflash_page_handler: receive clicked event"; /* ROM 0x71681c */
static const char fifo_click_s[] =
    "[navigation.ui]navigation_ui_reflash_page_handler: receive clicked event"; /* ROM 0x6f4948 */
static const char fifo_up[] = "navigation_ui_reflash_page_handler: receive scroll up event"; /* ROM 0x716858 */
static const char fifo_up_s[] =
    "[navigation.ui]navigation_ui_reflash_page_handler: receive scroll up event"; /* ROM 0x6f4994 */
static const char fifo_down[] = "navigation_ui_reflash_page_handler: receive scroll down event"; /* ROM 0x70d0a4 */
static const char fifo_down_s[] =
    "[navigation.ui]navigation_ui_reflash_page_handler: receive scroll down event"; /* ROM 0x6ee878 */

/* Location rubber band. */
static const char rubber_done[] = "Navigation rubber band animation complete"; /* ROM 0x740658 */
static const char rubber_done_s[] = "[navigation.ui]Navigation rubber band animation complete"; /* ROM 0x716a74 */
static const char y_after[] = "Navigation content container Y not zero after animation: %d, resetting"; /* ROM 0x6fb9b4 */
static const char y_after_s[] =
    "[navigation.ui]Navigation content container Y not zero after animation: %d, resetting"; /* ROM 0x6e45e8 */
static const char y_before[] =
    "Navigation content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6eeaa8 */
static const char y_before_s[] =
    "[navigation.ui]Navigation content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6ddfb4 */
static const char rubber_top[] =
    "Navigation rubber band TOP: normal_y=%d, stretch_y=%d (content_container)"; /* ROM 0x6f4c40 */
static const char rubber_top_s[] =
    "[navigation.ui]Navigation rubber band TOP: normal_y=%d, stretch_y=%d (content_container)"; /* ROM 0x6e0ecc */
static const char rubber_bottom_few[] =
    "Navigation rubber band BOTTOM (item<5): normal_y=%d, stretch_y=%d"; /* ROM 0x704170 */
static const char rubber_bottom_few_s[] =
    "[navigation.ui]Navigation rubber band BOTTOM (item<5): normal_y=%d, stretch_y=%d"; /* ROM 0x6e8e24 */
static const char rubber_bottom_many[] =
    "Navigation rubber band BOTTOM (item>=5): current=%d, overshoot=%d, max=%d"; /* ROM 0x6f4c8c */
static const char rubber_bottom_many_s[] =
    "[navigation.ui]Navigation rubber band BOTTOM (item>=5): current=%d, overshoot=%d, max=%d"; /* ROM 0x6e0f28 */

/* Focus / scroll animations. */
static const char focus_done[] = "Navigation focus change animation complete"; /* ROM 0x740684 */
static const char focus_done_s[] = "[navigation.ui]Navigation focus change animation complete"; /* ROM 0x716ab0 */
static const char calc_msg[] =
    "Navigation calculate scroll: item_index=%d, scroll_offset=%d, target_scroll=%d, max_scroll=%d"; /* ROM 0x6de014 */
static const char calc_msg_s[] =
    "[navigation.ui]Navigation calculate scroll: item_index=%d, scroll_offset=%d, target_scroll=%d, "
    "max_scroll=%d"; /* ROM 0x6d73c0 */
static const char scroll_done[] = "Navigation animation complete: index=%d, scroll=%d, expected=%d"; /* ROM 0x70d1e4 */
static const char scroll_done_s[] =
    "[navigation.ui]Navigation animation complete: index=%d, scroll=%d, expected=%d"; /* ROM 0x6eeaf8 */

/* navigation_inject_event. */
static const char not_init[] = "Navigation page not initialized"; /* ROM 0x762750 */
static const char not_init_s[] = "[navigation.ui]Navigation page not initialized"; /* ROM 0x735b94 */
static const char busy[] = "Navigation animation in progress, ignoring input"; /* ROM 0x72b298 */
static const char busy_s[] = "[navigation.ui]Navigation animation in progress, ignoring input"; /* ROM 0x70d224 */
static const char no_locations[] = "No navigation locations available"; /* ROM 0x756fa8 */
static const char no_locations_s[] = "[navigation.ui]No navigation locations available"; /* ROM 0x72b2cc */
static const char up_few[] = "NAV_EVENT_UP (total<5): index=%d"; /* ROM 0x756fcc */
static const char up_few_s[] = "[navigation.ui]NAV_EVENT_UP (total<5): index=%d"; /* ROM 0x735bc4 */
static const char up_first[] = "NAV_EVENT_UP: At first item, trigger rubber band"; /* ROM 0x72b300 */
static const char up_first_s[] = "[navigation.ui]NAV_EVENT_UP: At first item, trigger rubber band"; /* ROM 0x70d264 */
static const char down_few[] = "NAV_EVENT_DOWN (total<5): index=%d"; /* ROM 0x756ff0 */
static const char down_few_s[] = "[navigation.ui]NAV_EVENT_DOWN (total<5): index=%d"; /* ROM 0x72b334 */
static const char down_last[] = "NAV_EVENT_DOWN: At last item, trigger rubber band"; /* ROM 0x72b368 */
static const char down_last_s[] = "[navigation.ui]NAV_EVENT_DOWN: At last item, trigger rubber band"; /* ROM 0x7041b4 */
static const char selected[] = "Navigation location selected: %s (index: %d)"; /* ROM 0x735bf4 */
static const char selected_s[] = "[navigation.ui]Navigation location selected: %s (index: %d)"; /* ROM 0x716aec */
static const char selected_var[] =
    "navigation_inject_event: navigation_select_location_name=%s, navigation_select_location_index=%d"; /* ROM 0x6db22c */
static const char selected_var_s[] =
    "[navigation.ui]navigation_inject_event: navigation_select_location_name=%s, "
    "navigation_select_location_index=%d"; /* ROM 0x6d7430 */
static const char cancel[] = "Navigation cancel event"; /* ROM 0x7799c4 */
static const char cancel_s[] = "[navigation.ui]Navigation cancel event"; /* ROM 0x74ba2c */
static const char up_many[] = "NAV_EVENT_UP: index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x7207f8 */
static const char up_many_s[] = "[navigation.ui]NAV_EVENT_UP: index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x6fb9fc */
static const char move_focus[] = "  -> Move focus only: new index=%d"; /* ROM 0x757014 */
static const char move_focus_s[] = "[navigation.ui]  -> Move focus only: new index=%d"; /* ROM 0x72b39c */
static const char scroll_content[] =
    "  -> Scroll content: new index=%d, scroll_offset=%d, target_scroll=%d"; /* ROM 0x6fba44 */
static const char scroll_content_s[] =
    "[navigation.ui]  -> Scroll content: new index=%d, scroll_offset=%d, target_scroll=%d"; /* ROM 0x6e4640 */
static const char at_top[] = "  -> At top, move focus: new index=%d"; /* ROM 0x74ba54 */
static const char at_top_s[] = "[navigation.ui]  -> At top, move focus: new index=%d"; /* ROM 0x720830 */
static const char down_many[] = "NAV_EVENT_DOWN: index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x716b28 */
static const char down_many_s[] =
    "[navigation.ui]NAV_EVENT_DOWN: index=%d, focus_pos=%d, scroll_offset=%d"; /* ROM 0x6fba8c */
static const char at_bottom[] = "  -> At bottom, move focus: new index=%d"; /* ROM 0x7406b0 */
static const char at_bottom_s[] = "[navigation.ui]  -> At bottom, move focus: new index=%d"; /* ROM 0x720868 */

/* Mode select page. */
static const char mode_rx[] = "Mode select page: receive event from fifo"; /* ROM 0x740708 */
static const char mode_rx_s[] = "[navigation.ui]Mode select page: receive event from fifo"; /* ROM 0x716b64 */
static const char mode_click[] = "Mode select page: receive clicked event"; /* ROM 0x74ba7c */
static const char mode_click_s[] = "[navigation.ui]Mode select page: receive clicked event"; /* ROM 0x7208a0 */
static const char mode_up[] = "Mode select page: receive scroll up event"; /* ROM 0x740734 */
static const char mode_up_s[] = "[navigation.ui]Mode select page: receive scroll up event"; /* ROM 0x716ba0 */
static const char mode_down[] = "Mode select page: receive scroll down event"; /* ROM 0x740760 */
static const char mode_down_s[] = "[navigation.ui]Mode select page: receive scroll down event"; /* ROM 0x716bdc */
static const char mode_rubber_done[] = "Mode rubber band animation complete"; /* ROM 0x75705c */
static const char mode_rubber_done_s[] = "[navigation.ui]Mode rubber band animation complete"; /* ROM 0x72b3d0 */
static const char mode_y_after[] = "Mode content container Y not zero after animation: %d, resetting"; /* ROM 0x7041f8 */
static const char mode_y_after_s[] =
    "[navigation.ui]Mode content container Y not zero after animation: %d, resetting"; /* ROM 0x6eeb48 */
static const char mode_y_before[] =
    "Mode content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6f4cd8 */
static const char mode_y_before_s[] =
    "[navigation.ui]Mode content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6e0f84 */
static const char mode_rubber_top[] = "Mode rubber band TOP: normal_y=%d, stretch_y=%d"; /* ROM 0x735c24 */
static const char mode_rubber_top_s[] = "[navigation.ui]Mode rubber band TOP: normal_y=%d, stretch_y=%d"; /* ROM 0x70d2a4 */
static const char mode_rubber_bottom[] = "Mode rubber band BOTTOM: current=%d, overshoot=%d"; /* ROM 0x72b404 */
static const char mode_rubber_bottom_s[] =
    "[navigation.ui]Mode rubber band BOTTOM: current=%d, overshoot=%d"; /* ROM 0x70423c */
static const char mode_busy[] = "Mode is animating, ignore event"; /* ROM 0x762790 */
static const char mode_busy_s[] = "[navigation.ui]Mode is animating, ignore event"; /* ROM 0x735c54 */
static const char mode_selected[] = "Mode selected: %s (index=%d)"; /* ROM 0x7627b0 */
static const char mode_selected_s[] = "[navigation.ui]Mode selected: %s (index=%d)"; /* ROM 0x74078c */
static const char mode_up_idx[] = "Mode UP: new index=%d (%s)"; /* ROM 0x76e7a4 */
static const char mode_up_idx_s[] = "[navigation.ui]Mode UP: new index=%d (%s)"; /* ROM 0x7407b8 */
static const char mode_up_first[] = "Mode UP: At first item, trigger rubber band"; /* ROM 0x7407e4 */
static const char mode_up_first_s[] = "[navigation.ui]Mode UP: At first item, trigger rubber band"; /* ROM 0x716c18 */
static const char mode_down_idx[] = "Mode DOWN: new index=%d (%s)"; /* ROM 0x7627d0 */
static const char mode_down_idx_s[] = "[navigation.ui]Mode DOWN: new index=%d (%s)"; /* ROM 0x740810 */
static const char mode_down_last[] = "Mode DOWN: At last item, trigger rubber band"; /* ROM 0x735c84 */
static const char mode_down_last_s[] = "[navigation.ui]Mode DOWN: At last item, trigger rubber band"; /* ROM 0x716c54 */
static const char mode_unknown[] = "Mode inject event: unknown event type"; /* ROM 0x74baa4 */
static const char mode_unknown_s[] = "[navigation.ui]Mode inject event: unknown event type"; /* ROM 0x7208d8 */

uint32_t navigation_ui_exit_page_handler_54c268(void)
{
    NAV_LOG(4, fn_exit, 0xb65u, LOG_FLAGS(4, 0), exit_msg, exit_msg_s);
    navigation_free_max_map_buffer_545c5a();
    (void)navigation_send_type_13_allocating();
    g2_navigation_location_animating_20074fe8 = 0u;
    if (g2_navigation_location_content_200747a0 != NULL) {
        (void)audio_uart_anim_delete_450500(g2_navigation_location_content_200747a0, NULL);
        NAV_LOG(4, fn_exit, 0xb6du, LOG_FLAGS(4, 0), reset_nav_y, reset_nav_y_s);
    }
    if (g2_navigation_location_container_2007479c != NULL)
        (void)audio_uart_anim_delete_450500(g2_navigation_location_container_2007479c, NULL);
    if (g2_navigation_mode_content_200747b0 != NULL) {
        (void)audio_uart_anim_delete_450500(g2_navigation_mode_content_200747b0, NULL);
        NAV_LOG(4, fn_exit, 0xb75u, LOG_FLAGS(4, 0), reset_mode_y, reset_mode_y_s);
    }
    if (g2_navigation_mode_container_200747ac != NULL)
        (void)audio_uart_anim_delete_450500(g2_navigation_mode_container_200747ac, NULL);
    g2_nav_b_clock_label_20074764 = NULL;
    g2_nav_a_clock_label_200747e0 = NULL;
    g2_navigation_mode_animating_20074fe9 = 0u;
    g2_navigation_mode_scroll_offset_200747b8 = 0;
    (void)aeabi_memset_43c0e4(&g2_navigation_location_list_20376c38, sizeof g2_navigation_location_list_20376c38, 0);
    g2_nav_var_20074758 = 0u;
    return 0u;
}

/* Row index -> y offset inside the location content (count is not used). */
int32_t navigation_location_item_y_54c3ec(int32_t index, int32_t count)
{
    (void)count;
    return index * NAV_ITEM_H;
}

/* One queued location-page event, handled once the running animation is over (the
 * stock repeats this block textually, with its own __func__ and __LINE__, in the three
 * location callbacks). */
static void location_page_drain_fifo(const char *fn, uint32_t line_rx, uint32_t line_click,
                                     uint32_t line_up, uint32_t line_down)
{
    uint8_t event = 0u;

    if (g2_navigation_ui_state_20074fed != NAVIGATION_LOCATION_LIST_SELECT_PAGE)
        return;
    if (ui_common_api_fn_00509dfa(g2_nav_list_event_fifo_20074738) != 0)
        return;
    NAV_LOG(4, fn, line_rx, LOG_FLAGS(4, 0), fifo_rx, fifo_rx_s);
    (void)ui_common_api_fn_00509e14(g2_nav_list_event_fifo_20074738, &event, 1u);
    if (event == NAV_FIFO_CLICK) {
        NAV_LOG(4, fn, line_click, LOG_FLAGS(4, 0), fifo_click, fifo_click_s);
        navigation_inject_event_54cfd0(NAV_EVENT_SELECT);
        if (g2_navigation_page_root_20074718 != NULL)
            audio_uart_page_44d878(g2_navigation_page_root_20074718);
        g2_navigation_ui_state_20074fed = NAVIGATION_MODE_SELECT_PAGE;
        g2_navigation_mode_animating_20074fe9 = 0u;
        g2_navigation_location_animating_20074fe8 = 0u;
        ui_common_api_fn_00509f52(g2_nav_list_event_fifo_20074738);
        (void)navigation_ui_create_mode_list_page_548b98();
    } else if (event == NAV_FIFO_SCROLL_UP) {
        NAV_LOG(4, fn, line_up, LOG_FLAGS(4, 0), fifo_up, fifo_up_s);
        navigation_inject_event_54cfd0(NAV_EVENT_DOWN);
    } else if (event == NAV_FIFO_SCROLL_DOWN) {
        NAV_LOG(4, fn, line_down, LOG_FLAGS(4, 0), fifo_down, fifo_down_s);
        navigation_inject_event_54cfd0(NAV_EVENT_UP);
    }
}

void navigation_location_list_select_page_motion_fifo_handler_54c3f2(void)
{
    location_page_drain_fifo(fn_motion_fifo, 0xb8fu, 0xb94u, 0xba9u, 0xbacu);
}

void navigation_rubber_band_anim_complete_cb_54c5b0(void *anim)
{
    int32_t y;

    (void)anim;
    NAV_LOG(4, fn_rubber_done, 0xbb5u, LOG_FLAGS(4, 0), rubber_done, rubber_done_s);
    if (g2_navigation_location_content_200747a0 != NULL) {
        y = audio_uart_lv_obj_y_43fce0(g2_navigation_location_content_200747a0);
        if (y != 0) {
            NAV_LOG(2, fn_rubber_done, 0xbbbu, LOG_FLAGS(2, 1), y_after, y_after_s, y);
            audio_uart_page_43f142(g2_navigation_location_content_200747a0, 0);
        }
    }
    g2_navigation_location_animating_20074fe8 = 0u;
    location_page_drain_fifo(fn_rubber_done, 0xbc4u, 0xbc9u, 0xbd7u, 0xbdau);
}

void navigation_anim_set_y_exec_cb_54c83c(void *obj, int32_t y)
{
    audio_uart_page_43f142(obj, y);
}

/* 16 px bounce out and back (200 ms each way, ease-out) at the ends of the list. */
static void start_bounce(void *var, void (*exec_cb)(void *, int32_t), int32_t from, int32_t to,
                         void (*completed_cb)(void *), uint8_t *animating)
{
    g2_lv_anim_t a;

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = var;
    audio_uart_lv_anim_values_4506ce(&a, from, to);
    a.duration = NAV_ANIM_MS;
    a.exec_cb = exec_cb;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.reverse_duration = NAV_ANIM_MS;
    a.reverse_delay = 0u;
    a.completed_cb = completed_cb;
    *animating = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void trigger_navigation_rubber_band_effect_54c844(uint8_t is_top)
{
    int32_t y;

    if (g2_navigation_location_container_2007479c == NULL)
        return;
    if (is_top != 0u) {
        if (g2_navigation_location_content_200747a0 == NULL)
            return;
        y = audio_uart_lv_obj_y_43fce0(g2_navigation_location_content_200747a0);
        if (y != 0) {
            NAV_LOG(2, fn_rubber, 0xbf3u, LOG_FLAGS(2, 1), y_before, y_before_s, y);
            audio_uart_page_43f142(g2_navigation_location_content_200747a0, 0);
        }
        NAV_LOG(4, fn_rubber, 0xbfbu, LOG_FLAGS(4, 2), rubber_top, rubber_top_s, 0, NAV_RUBBER_BAND_PX);
        start_bounce(g2_navigation_location_content_200747a0, navigation_anim_set_y_exec_cb_54c83c, 0,
                     NAV_RUBBER_BAND_PX, navigation_rubber_band_anim_complete_cb_54c5b0,
                     &g2_navigation_location_animating_20074fe8);
        return;
    }
    if ((int32_t)g2_navigation_location_list_20376c38.count < NAV_VISIBLE_ITEMS) {
        if (g2_navigation_location_content_200747a0 == NULL)
            return;
        y = audio_uart_lv_obj_y_43fce0(g2_navigation_location_content_200747a0);
        if (y != 0) {
            NAV_LOG(2, fn_rubber, 0xc15u, LOG_FLAGS(2, 1), y_before, y_before_s, y);
            audio_uart_page_43f142(g2_navigation_location_content_200747a0, 0);
        }
        NAV_LOG(4, fn_rubber, 0xc1du, LOG_FLAGS(4, 2), rubber_bottom_few, rubber_bottom_few_s, 0,
                -NAV_RUBBER_BAND_PX);
        start_bounce(g2_navigation_location_content_200747a0, navigation_anim_set_y_exec_cb_54c83c, 0,
                     -NAV_RUBBER_BAND_PX, navigation_rubber_band_anim_complete_cb_54c5b0,
                     &g2_navigation_location_animating_20074fe8);
    } else {
        /* Scrolled list: overshoot the viewport scroll instead of moving the content. */
        int32_t current = audio_uart_lv_scroll_top_44e4aa(g2_navigation_location_container_2007479c);
        int32_t max = ((int32_t)g2_navigation_location_list_20376c38.count - NAV_VISIBLE_ITEMS) * NAV_ITEM_H;
        int32_t overshoot;
        if (max < 0)
            max = 0;
        overshoot = current + NAV_RUBBER_BAND_PX;
        NAV_LOG(4, fn_rubber, 0xc34u, LOG_FLAGS(4, 3), rubber_bottom_many, rubber_bottom_many_s, current,
                overshoot, max);
        start_bounce(g2_navigation_location_container_2007479c, navigation_scroll_anim_exec_cb_54cebc,
                     current, overshoot, navigation_rubber_band_anim_complete_cb_54c5b0,
                     &g2_navigation_location_animating_20074fe8);
    }
}

void navigation_focus_change_anim_exec_cb_54cb56(void *var, int32_t value)
{
    (void)var;
    (void)value;
}

void navigation_focus_change_anim_ready_cb_54cb58(void *anim)
{
    (void)anim;
    NAV_LOG(4, fn_focus_ready, 0xc4du, LOG_FLAGS(4, 0), focus_done, focus_done_s);
    g2_navigation_location_animating_20074fe8 = 0u;
    navigation_location_list_select_page_motion_fifo_handler_54c3f2();
}

/* A 200 ms no-op animation on the page root: it only delays the next queued input. */
void navigation_focus_change_anim_start_54cbaa(void)
{
    g2_lv_anim_t a;

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_navigation_page_root_20074718;
    a.exec_cb = navigation_focus_change_anim_exec_cb_54cb56;
    audio_uart_lv_anim_values_4506ce(&a, 0, 0);
    a.duration = NAV_ANIM_MS;
    a.path_cb = audio_uart_lv_anim_default_path_450634;
    a.completed_cb = navigation_focus_change_anim_ready_cb_54cb58;
    g2_navigation_location_animating_20074fe8 = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Viewport scroll for the current scroll offset: min(offset * 40, (count - 5) * 40). */
int32_t navigation_calculate_scroll_position_for_item_54cc00(int32_t item_index)
{
    int32_t count = (int32_t)g2_navigation_location_list_20376c38.count;
    int32_t max_scroll;
    int32_t target;

    if (count < NAV_VISIBLE_ITEMS)
        return 0;
    max_scroll = (count - NAV_VISIBLE_ITEMS) * NAV_ITEM_H;
    if (max_scroll < 0)
        max_scroll = 0;
    target = g2_navigation_location_scroll_offset_200747a8 * NAV_ITEM_H;
    if (max_scroll < target)
        target = max_scroll;
    if (target < 0)
        target = 0;
    NAV_LOG(4, fn_calc, 0xc75u, LOG_FLAGS(4, 4), calc_msg, calc_msg_s, item_index,
            g2_navigation_location_scroll_offset_200747a8, target, max_scroll);
    return target;
}

void navigation_scroll_anim_complete_cb_54ccd4(void *anim)
{
    int32_t scroll;
    int32_t expected;

    (void)anim;
    scroll = audio_uart_lv_scroll_top_44e4aa(g2_navigation_location_container_2007479c);
    expected = navigation_calculate_scroll_position_for_item_54cc00(g2_navigation_location_selected_200747a4);
    NAV_LOG(4, fn_scroll_done, 0xc7fu, LOG_FLAGS(4, 3), scroll_done, scroll_done_s,
            g2_navigation_location_selected_200747a4, scroll, expected);
    navigation_update_location_item_styles_54d9a4();
    g2_navigation_location_animating_20074fe8 = 0u;
    location_page_drain_fifo(fn_scroll_done, 0xc84u, 0xc89u, 0xc96u, 0xc99u);
}

void navigation_scroll_anim_exec_cb_54cebc(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

void navigation_scroll_anim_ready_cb_54cec6(void *anim)
{
    navigation_scroll_anim_complete_cb_54ccd4(anim);
}

void navigation_scroll_anim_start_54cece(void *obj, int32_t target_y, int32_t duration)
{
    g2_lv_anim_t a;

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(obj), target_y);
    a.duration = duration;
    a.exec_cb = navigation_scroll_anim_exec_cb_54cebc;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = navigation_scroll_anim_ready_cb_54cec6;
    g2_navigation_location_animating_20074fe8 = 1u;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Move the focus border by one row and play the focus delay animation. */
static void location_move_focus(int32_t delta, uint32_t line, const char *msg, const char *msg_s)
{
    navigation_clear_location_focus_border_54d948();
    g2_navigation_location_selected_200747a4 += delta;
    NAV_LOG(4, fn_inject, line, LOG_FLAGS(4, 1), msg, msg_s, g2_navigation_location_selected_200747a4);
    navigation_update_location_item_styles_54d9a4();
    navigation_focus_change_anim_start_54cbaa();
}

static void location_select(uint32_t line)
{
    int32_t index = g2_navigation_location_selected_200747a4;
    const char *name = g2_navigation_location_list_20376c38.name[index];

    NAV_LOG(4, fn_inject, line, LOG_FLAGS(4, 2), selected, selected_s, name, index);
    (void)aeabi_memset_43c0e4(g2_nav_buf_200f4784, sizeof g2_nav_buf_200f4784, 0);
    (void)audio_settings_copy_text(g2_nav_buf_200f4784, g2_navigation_location_list_20376c38.name[index],
                                   sizeof g2_nav_buf_200f4784 - 1u);
    g2_nav_var_20074754 = (uint32_t)g2_navigation_location_selected_200747a4;
}

void navigation_inject_event_54cfd0(uint8_t event)
{
    int32_t count;
    int32_t focus_pos;
    int32_t target;

    if (g2_navigation_page_root_20074718 == NULL || g2_navigation_location_container_2007479c == NULL) {
        NAV_LOG(2, fn_inject, 0xcbfu, LOG_FLAGS(2, 0), not_init, not_init_s);
        return;
    }
    if (g2_navigation_location_animating_20074fe8 != 0u) {
        NAV_LOG(4, fn_inject, 0xcc5u, LOG_FLAGS(4, 0), busy, busy_s);
        return;
    }
    count = (int32_t)g2_navigation_location_list_20376c38.count;
    if (count < 1) {
        NAV_LOG(2, fn_inject, 0xccbu, LOG_FLAGS(2, 0), no_locations, no_locations_s);
        return;
    }

    if (count < NAV_VISIBLE_ITEMS) {
        /* Everything fits: only the focus moves. */
        if (event == NAV_EVENT_UP) {
            if (g2_navigation_location_selected_200747a4 < 1) {
                NAV_LOG(4, fn_inject, 0xcdau, LOG_FLAGS(4, 0), up_first, up_first_s);
                trigger_navigation_rubber_band_effect_54c844(1u);
            } else {
                location_move_focus(-1, 0xcd6u, up_few, up_few_s);
            }
        } else if (event == NAV_EVENT_SELECT) {
            location_select(0xcefu);
            NAV_LOG(4, fn_inject, 0xcf3u, LOG_FLAGS(4, 2), selected_var, selected_var_s, g2_nav_buf_200f4784,
                    g2_nav_var_20074754);
        } else if (event == NAV_EVENT_DOWN) {
            if (g2_navigation_location_selected_200747a4 < count - 1) {
                location_move_focus(1, 0xce3u, down_few, down_few_s);
            } else {
                NAV_LOG(4, fn_inject, 0xce7u, LOG_FLAGS(4, 0), down_last, down_last_s);
                trigger_navigation_rubber_band_effect_54c844(0u);
            }
        } else if (event == NAV_EVENT_CANCEL) {
            NAV_LOG(4, fn_inject, 0xcf7u, LOG_FLAGS(4, 0), cancel, cancel_s);
        }
        return;
    }

    focus_pos = g2_navigation_location_selected_200747a4 - g2_navigation_location_scroll_offset_200747a8;
    if (event == NAV_EVENT_UP) {
        if (g2_navigation_location_selected_200747a4 < 1) {
            NAV_LOG(4, fn_inject, 0xd2cu, LOG_FLAGS(4, 0), up_first, up_first_s);
            trigger_navigation_rubber_band_effect_54c844(1u);
            return;
        }
        NAV_LOG(4, fn_inject, 0xd05u, LOG_FLAGS(4, 3), up_many, up_many_s, g2_navigation_location_selected_200747a4,
                focus_pos, g2_navigation_location_scroll_offset_200747a8);
        if (focus_pos >= 3) {
            location_move_focus(-1, 0xd0bu, move_focus, move_focus_s);
        } else if (focus_pos != 1) {
            location_move_focus(-1, 0xd26u, move_focus, move_focus_s);
        } else if (g2_navigation_location_scroll_offset_200747a8 < 1) {
            location_move_focus(-1, 0xd1eu, at_top, at_top_s);
        } else {
            navigation_clear_location_focus_border_54d948();
            g2_navigation_location_scroll_offset_200747a8--;
            g2_navigation_location_selected_200747a4--;
            target = navigation_calculate_scroll_position_for_item_54cc00(g2_navigation_location_selected_200747a4);
            NAV_LOG(4, fn_inject, 0xd18u, LOG_FLAGS(4, 3), scroll_content, scroll_content_s,
                    g2_navigation_location_selected_200747a4, g2_navigation_location_scroll_offset_200747a8, target);
            navigation_scroll_anim_start_54cece(g2_navigation_location_container_2007479c, target, NAV_ANIM_MS);
        }
    } else if (event == NAV_EVENT_SELECT) {
        location_select(0xd67u);
    } else if (event == NAV_EVENT_DOWN) {
        if (g2_navigation_location_selected_200747a4 >= count - 1) {
            NAV_LOG(4, fn_inject, 0xd5fu, LOG_FLAGS(4, 0), down_last, down_last_s);
            trigger_navigation_rubber_band_effect_54c844(0u);
            return;
        }
        NAV_LOG(4, fn_inject, 0xd35u, LOG_FLAGS(4, 3), down_many, down_many_s,
                g2_navigation_location_selected_200747a4, focus_pos, g2_navigation_location_scroll_offset_200747a8);
        if (focus_pos < 3) {
            location_move_focus(1, 0xd3bu, move_focus, move_focus_s);
        } else if (focus_pos == 3) {
            int32_t max_offset = count - NAV_VISIBLE_ITEMS;
            if (max_offset < 0)
                max_offset = 0;
            if (g2_navigation_location_scroll_offset_200747a8 < max_offset) {
                navigation_clear_location_focus_border_54d948();
                g2_navigation_location_scroll_offset_200747a8++;
                g2_navigation_location_selected_200747a4++;
                g2_navigation_location_animating_20074fe8 = 1u;
                target = navigation_calculate_scroll_position_for_item_54cc00(g2_navigation_location_selected_200747a4);
                NAV_LOG(4, fn_inject, 0xd4bu, LOG_FLAGS(4, 3), scroll_content, scroll_content_s,
                        g2_navigation_location_selected_200747a4, g2_navigation_location_scroll_offset_200747a8,
                        target);
                navigation_scroll_anim_start_54cece(g2_navigation_location_container_2007479c, target, NAV_ANIM_MS);
            } else {
                location_move_focus(1, 0xd51u, at_bottom, at_bottom_s);
            }
        } else {
            location_move_focus(1, 0xd59u, move_focus, move_focus_s);
        }
    } else if (event == NAV_EVENT_CANCEL) {
        NAV_LOG(4, fn_inject, 0xd70u, LOG_FLAGS(4, 0), cancel, cancel_s);
    }
}

void navigation_clear_location_focus_border_54d948(void)
{
    int32_t index = g2_navigation_location_selected_200747a4;

    if (index >= 0 && (uint32_t)index < g2_navigation_location_list_20376c38.count &&
        g2_navigation_location_items_20072c68[index] != NULL)
        audio_uart_page_44131c(g2_navigation_location_items_20072c68[index], 0, 0u);
}

/* Focused row: 50 % black fill, 1 px white border, opaque icon, white name. Other
 * rows: no fill or border, icon at opacity 100, grey name. */
void navigation_update_location_item_styles_54d9a4(void)
{
    int32_t count;

    if (g2_navigation_location_container_2007479c == NULL)
        return;
    count = (int32_t)g2_navigation_location_list_20376c38.count;
    for (int32_t i = 0; i < count; i++) {
        void *item = g2_navigation_location_items_20072c68[i];
        void *icon;
        void *label;

        if (item == NULL)
            continue;
        icon = audio_uart_lv_child_get_44dce2(item, 0);
        label = audio_uart_lv_child_get_44dce2(item, 1);
        if (i == g2_navigation_location_selected_200747a4) {
            audio_uart_page_44129e(item, 0x32u, 0u);
            audio_uart_page_44127e(item, audio_uart_page_44104c(0u), 0u);
            audio_uart_page_44131c(item, 1, 0u);
            audio_uart_page_4412ec(item, audio_uart_page_44104c(0xffffffu), 0u);
            if (icon != NULL)
                audio_uart_page_4413ce(icon, 0xffu, 0u);
            if (label != NULL)
                audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
        } else {
            audio_uart_page_44129e(item, 0u, 0u);
            audio_uart_page_44131c(item, 0, 0u);
            if (icon != NULL)
                audio_uart_page_4413ce(icon, 100u, 0u);
            if (label != NULL) {
                audio_uart_page_44140e(label, audio_uart_page_44104c(NAV_GREY), 0u);
                lv_obj_set_style_transform_scale_5455c6(label, LV_SCALE_NONE, 0u);
            }
        }
        audio_uart_display_audio_reset_441488(item, 0xffu, 0u);
        lv_obj_set_style_transform_scale_5455c6(item, LV_SCALE_NONE, 0u);
    }
}

/* Mode rows are centred in the 5-row viewport. */
int32_t navigation_mode_item_y_54dad8(int32_t index, int32_t count)
{
    return (index + (NAV_VISIBLE_ITEMS - count) / 2) * NAV_ITEM_H;
}

void mode_scroll_anim_exec_cb_54daea(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

void navigation_clear_mode_focus_border_54daf4(void)
{
    uint32_t index = (uint32_t)g2_navigation_mode_selected_200747b4;

    if (index < NAV_MODE_COUNT && g2_navigation_mode_items_20074160[index] != NULL)
        audio_uart_page_44131c(g2_navigation_mode_items_20074160[index], 0, 0u);
}

void navigation_update_mode_item_styles_54db30(void)
{
    if (g2_navigation_mode_container_200747ac == NULL)
        return;
    for (int32_t i = 0; i < NAV_MODE_COUNT; i++) {
        void *item = g2_navigation_mode_items_20074160[i];
        void *label;

        if (item == NULL)
            continue;
        label = audio_uart_lv_child_get_44dce2(item, 0);
        if (i == g2_navigation_mode_selected_200747b4) {
            audio_uart_page_44129e(item, 0x32u, 0u);
            audio_uart_page_44127e(item, audio_uart_page_44104c(0u), 0u);
            audio_uart_page_44131c(item, 1, 0u);
            audio_uart_page_4412ec(item, audio_uart_page_44104c(0xffffffu), 0u);
            if (label != NULL)
                audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
        } else {
            audio_uart_page_44129e(item, 0u, 0u);
            audio_uart_page_44131c(item, 0, 0u);
            if (label != NULL)
                audio_uart_page_44140e(label, audio_uart_page_44104c(NAV_GREY), 0u);
        }
        audio_uart_display_audio_reset_441488(item, 0xffu, 0u);
    }
}

/* One queued mode-page event (no page-state check, unlike the location page). */
static void mode_page_drain_fifo(const char *fn, uint32_t line_rx, uint32_t line_click, uint32_t line_up,
                                 uint32_t line_down)
{
    uint8_t event = 0u;

    if (ui_common_api_fn_00509dfa(g2_nav_list_event_fifo_20074738) != 0)
        return;
    NAV_LOG(4, fn, line_rx, LOG_FLAGS(4, 0), mode_rx, mode_rx_s);
    (void)ui_common_api_fn_00509e14(g2_nav_list_event_fifo_20074738, &event, 1u);
    if (event == NAV_FIFO_CLICK) {
        NAV_LOG(4, fn, line_click, LOG_FLAGS(4, 0), mode_click, mode_click_s);
        mode_inject_event_54e1a8(NAV_EVENT_SELECT);
    } else if (event == NAV_FIFO_SCROLL_UP) {
        NAV_LOG(4, fn, line_up, LOG_FLAGS(4, 0), mode_up, mode_up_s);
        mode_inject_event_54e1a8(NAV_EVENT_DOWN);
    } else if (event == NAV_FIFO_SCROLL_DOWN) {
        NAV_LOG(4, fn, line_down, LOG_FLAGS(4, 0), mode_down, mode_down_s);
        mode_inject_event_54e1a8(NAV_EVENT_UP);
    }
}

void navigation_mode_select_page_anim_handler_54dc24(void)
{
    mode_page_drain_fifo(fn_mode_fifo, 0xe45u, 0xe4au, 0xe4du, 0xe50u);
}

void mode_rubber_band_anim_complete_cb_54dd9c(void *anim)
{
    int32_t y;

    (void)anim;
    NAV_LOG(4, fn_mode_rubber_done, 0xe58u, LOG_FLAGS(4, 0), mode_rubber_done, mode_rubber_done_s);
    if (g2_navigation_mode_content_200747b0 != NULL) {
        y = audio_uart_lv_obj_y_43fce0(g2_navigation_mode_content_200747b0);
        if (y != 0) {
            NAV_LOG(4, fn_mode_rubber_done, 0xe5eu, LOG_FLAGS(4, 1), mode_y_after, mode_y_after_s, y);
            audio_uart_page_43f142(g2_navigation_mode_content_200747b0, 0);
        }
    }
    g2_navigation_mode_animating_20074fe9 = 0u;
    mode_page_drain_fifo(fn_mode_rubber_done, 0xe67u, 0xe6cu, 0xe6fu, 0xe72u);
}

void trigger_mode_rubber_band_effect_54dfb4(uint8_t is_top)
{
    int32_t y;

    if (g2_navigation_mode_container_200747ac == NULL)
        return;
    if (is_top == 0u) {
        int32_t current = audio_uart_lv_scroll_top_44e4aa(g2_navigation_mode_container_200747ac);
        int32_t overshoot = current + NAV_RUBBER_BAND_PX;
        NAV_LOG(4, fn_mode_rubber, 0xea1u, LOG_FLAGS(4, 2), mode_rubber_bottom, mode_rubber_bottom_s, current,
                overshoot);
        start_bounce(g2_navigation_mode_container_200747ac, mode_scroll_anim_exec_cb_54daea, current, overshoot,
                     mode_rubber_band_anim_complete_cb_54dd9c, &g2_navigation_mode_animating_20074fe9);
        return;
    }
    if (g2_navigation_mode_content_200747b0 == NULL)
        return;
    y = audio_uart_lv_obj_y_43fce0(g2_navigation_mode_content_200747b0);
    if (y != 0) {
        NAV_LOG(4, fn_mode_rubber, 0xe83u, LOG_FLAGS(4, 1), mode_y_before, mode_y_before_s, y);
        audio_uart_page_43f142(g2_navigation_mode_content_200747b0, 0);
    }
    NAV_LOG(4, fn_mode_rubber, 0xe8bu, LOG_FLAGS(4, 2), mode_rubber_top, mode_rubber_top_s, 0, NAV_RUBBER_BAND_PX);
    start_bounce(g2_navigation_mode_content_200747b0, navigation_anim_set_y_exec_cb_54c83c, 0, NAV_RUBBER_BAND_PX,
                 mode_rubber_band_anim_complete_cb_54dd9c, &g2_navigation_mode_animating_20074fe9);
}

void mode_inject_event_54e1a8(uint8_t event)
{
    if (g2_navigation_mode_animating_20074fe9 != 0u) {
        NAV_LOG(4, fn_mode_inject, 0xeb6u, LOG_FLAGS(4, 0), mode_busy, mode_busy_s);
        return;
    }
    if (event == NAV_EVENT_UP) {
        if (g2_navigation_mode_selected_200747b4 < 1) {
            NAV_LOG(4, fn_mode_inject, 0xeccu, LOG_FLAGS(4, 0), mode_up_first, mode_up_first_s);
            trigger_mode_rubber_band_effect_54dfb4(1u);
        } else {
            navigation_clear_mode_focus_border_54daf4();
            g2_navigation_mode_selected_200747b4--;
            NAV_LOG(4, fn_mode_inject, 0xec8u, LOG_FLAGS(4, 2), mode_up_idx, mode_up_idx_s,
                    g2_navigation_mode_selected_200747b4,
                    g2_navigation_mode_names_20002d00[g2_navigation_mode_selected_200747b4]);
            navigation_update_mode_item_styles_54db30();
            navigation_mode_select_page_anim_handler_54dc24();
        }
    } else if (event == NAV_EVENT_SELECT) {
        NAV_LOG(4, fn_mode_inject, 0xec0u, LOG_FLAGS(4, 2), mode_selected, mode_selected_s,
                g2_navigation_mode_names_20002d00[g2_navigation_mode_selected_200747b4],
                g2_navigation_mode_selected_200747b4);
        g2_nav_flag_20074fe7 = (uint8_t)(g2_navigation_mode_selected_200747b4 + 1);
    } else if (event == NAV_EVENT_DOWN) {
        if (g2_navigation_mode_selected_200747b4 < NAV_MODE_COUNT - 1) {
            navigation_clear_mode_focus_border_54daf4();
            g2_navigation_mode_selected_200747b4++;
            NAV_LOG(4, fn_mode_inject, 0xed5u, LOG_FLAGS(4, 2), mode_down_idx, mode_down_idx_s,
                    g2_navigation_mode_selected_200747b4,
                    g2_navigation_mode_names_20002d00[g2_navigation_mode_selected_200747b4]);
            navigation_update_mode_item_styles_54db30();
            navigation_mode_select_page_anim_handler_54dc24();
        } else {
            NAV_LOG(4, fn_mode_inject, 0xed9u, LOG_FLAGS(4, 0), mode_down_last, mode_down_last_s);
            trigger_mode_rubber_band_effect_54dfb4(0u);
        }
    } else {
        NAV_LOG(2, fn_mode_inject, 0xedeu, LOG_FLAGS(2, 0), mode_unknown, mode_unknown_s);
    }
}
