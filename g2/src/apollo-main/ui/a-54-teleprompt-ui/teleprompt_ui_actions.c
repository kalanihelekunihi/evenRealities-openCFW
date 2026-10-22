/* Teleprompt page: file-list menu, main page create/display, page window
 * switching, AI/scroll sync, pause and elapsed-time title bar, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_ui.c
 * (log tag "teleprompt.ui"). Native 0x555514..0x5573e7 (functions
 * 0x555514..0x55558f, 0x5555a4..0x555741, 0x555758..0x5558b9,
 * 0x5558d4..0x555bfd, 0x555c04..0x555cef, 0x555d18..0x556009 and on to
 * 0x557280..0x5573e7); interleaved literal pools 0x555744..0x555757,
 * 0x5558bc..0x5558d3, 0x555c00 (inline ""), 0x555cf0..0x555d17 (inline "M",
 * "A"), 0x5560c8..0x5560cf, 0x556124..0x556133, 0x556260..0x556283,
 * 0x5563b8..0x5563bf, 0x55641c..0x556427, 0x556484..0x5564a7,
 * 0x55665c..0x556687, 0x556960..0x556963, 0x556a18..0x556a27,
 * 0x556b24..0x556b2b, 0x556c34..0x556c43, 0x556ca8..0x556cd7,
 * 0x556ea0..0x556ed3, 0x5570fc..0x557103, 0x557198..0x5571a7,
 * 0x557260..0x55727f, 0x5573e8..0x5574af.
 *
 * Every FSM action takes (current ui state, event argument) and returns 0,
 * or -1 when it could not run. Page/line pairs arrive either as
 * page * 10 + line or packed as (line << 16) | page. The 4 page labels in the
 * scroll container show pages [window_first_page, window_first_page + 4);
 * one page is 10 lines of 28 px (0x118 px). */
#include <stdint.h>
#include <stddef.h>
#include "teleprompt_ui_internal.h"

#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PCT_100 0x20000064
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_SCROLL_ELASTIC_MOMENTUM_CHAIN 0x360u
#define LV_DIR_VER 0xcu
#define LV_EVENT_SCROLL_BEGIN 0xcu
#define LV_EVENT_SCROLL_END 0xeu
#define LV_EVENT_SCROLL 0xfu
#define LV_LABEL_TEXT_SELECTION_OFF 0xffffu

enum {
    LV_ALIGN_TOP_LEFT = 1u,
    LV_ALIGN_BOTTOM_MID = 5u,
    LV_ALIGN_BOTTOM_RIGHT = 6u,
    LV_ALIGN_LEFT_MID = 7u,
    LV_ALIGN_RIGHT_MID = 8u,
    LV_ALIGN_CENTER = 9u,
    LV_ALIGN_OUT_RIGHT_MID = 0x14u,
};

enum {
    TELEPROMPT_STATE_MENU = 1u,
    TELEPROMPT_STATE_MAIN = 2u,
};

enum {
    TELEPROMPT_MODE_AI = 0u,
    TELEPROMPT_MODE_MANUAL = 1u,
    TELEPROMPT_MODE_AUTO = 2u,
};

#define TELEPROMPT_LIST_BOUNCE 0xaau   /* scroll count meaning "edge bounce" */
#define TELEPROMPT_EXIT_RECORD_KEY 0x40102u

/* LVGL v9 lv_anim_t (0x60 bytes); only the fields set here are named. */
typedef struct {
    void *var;                          /* +0x00 */
    void (*exec_cb)(void *, int32_t);   /* +0x04 */
    uint32_t reserved08[2];
    void (*completed_cb)(void *);       /* +0x10 */
    uint32_t reserved14[3];
    int32_t (*path_cb)(void *);         /* +0x20 */
    uint32_t reserved24[3];
    int32_t duration;                   /* +0x30 */
    uint32_t reserved34[11];
} teleprompt_lv_anim_t;
_Static_assert(sizeof(teleprompt_lv_anim_t) == 0x60, "lv_anim_t");

/* Usage record persisted on BLE loss: {widget, source}. */
typedef struct {
    uint32_t widget;
    uint32_t source;
} teleprompt_exit_record_t;

extern uint32_t audio_uart_ring_primary_head_cell;    /* RAM 0x200746dc: active lv_font_t * */
extern const uint8_t g2_translate_lang_pair_font[];   /* ROM 0x7547b8 lv_font_t (mode letter) */
extern const uint8_t g2_translate_pause_image[];      /* ROM 0x76f438 lv_image_dsc_t (pause) */
extern const uint8_t g2_teleprompt_file_icon_772a24[]; /* ROM 0x772a24 lv_image_dsc_t (file) */

/* teleprompt_ui.c functions reconstructed in ui/a-53-teleprompt-ui. */
extern void lv_obj_set_style_pad_all_554080(void *obj, int32_t value, uint32_t selector);
extern uint8_t teleprompt_ui_line_in_window_5549e6(void *obj, uint32_t first_page, uint32_t page, int32_t line);
extern uint32_t teleprompt_ui_window_first_page_for_554a16(void *obj, uint32_t first_page, uint32_t page,
                                                           int32_t line);
extern int32_t teleprompt_ui_get_scroll_y_by_page_line_id_554a84(void *obj, uint32_t page, int32_t line,
                                                                 uint8_t one_line_up);
extern void teleprompt_ui_ai_mode_page_process_554b2c(void *label, uint32_t page);
extern void *teleprompt_ui_scroll_bar_create_554c68(void *parent);
extern void teleprompt_ui_scroll_bar_set_value_554d58(void *bar, int32_t page, int32_t line);
extern void teleprompt_ui_scroll_to_top_554e9c(void);         /* GIF completion callback */
extern void teleprompt_ui_scroll_container_scroll_end_check_555200(uint8_t force);
extern void teleprompt_ui_scroll_event_cb_55545c(void *e);
extern void *teleprompt_ui_page_label_create_555486(void *parent);

/* Teleprompt data/FSM/protocol. */
extern void teleprompt_page_data_init(uint32_t start_page, uint32_t total_pages);   /* 0x58b1c0 */
extern void teleprompt_page_data_deinit(void);                                      /* 0x58b370 */
extern const uint8_t *teleprompt_page_data_get(uint32_t page);  /* 0x58b83c, text at +10 */
extern uint8_t semantic_page_in_ensure_window(uint32_t page);   /* 0x58b8f0 */
extern void teleprompt_page_data_set_window(uint32_t first_page); /* 0x58b980 */
extern const g2_teleprompt_file_list_t *teleprompt_file_list_get(void); /* 0x58bd70 */
extern void teleprompt_file_list_reset(void);                   /* 0x58bd74 */
extern void teleprompt_fsm_jump_set_58c874(uint32_t page);      /* ctrl +0x3d = 1, +0x40 = page */
extern void teleprompt_fsm_jump_clear_58c882(void);
extern uint32_t APP_PbTxEncodeFileListRequest(void *request);   /* 0x588968 */
extern uint32_t APP_PbTxEncodeFileSelect(void *request);        /* 0x588a56 */

/* Shared animations and system UI. */
extern uint32_t audio_terminal_session_animate_5896fc(void *from, void *to, uint32_t duration);
extern void audio_terminal_session_row_show_5897ee(void *row);
extern void audio_conversate_main_list_scroll_58a680(void *list, int32_t distance, uint32_t up,
                                                     uint32_t flags);        /* edge bounce */
extern uint32_t audio_conversate_ui_message_send_58bfb2(void *parent, const char *text,
                                                        uint32_t app_id, uint32_t animated,
                                                        uint32_t hold_ms); /* common_exit_prompt_show */
extern void audio_uart_page_58c238(void *obj, uint32_t duration, uint32_t delay); /* fade in */
extern void *audio_conversate_pre_notes_anim_create_58c7a0(void *parent, void (*complete)(void)); /* GIF */
extern void audio_conversate_route_before_release_58c836(void *gif);  /* GIF pause */
extern uint32_t audio_conversate_route_release_58c84e(void *gif);     /* GIF resume/restart */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t context);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern uint8_t UX_GetSystemBLEStatus(void);                     /* 0x47d8ce */
extern uint32_t display_driver_uled_mode_45a568(void);          /* device role, 1 = master */
extern uint32_t audio_uart_page_460084(const char *key);        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern uint32_t g2_log_module_length(const char *text);         /* strlen 0x44a43c */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */

/* LVGL 9.3 fork. */
extern void *audio_uart_page_43de82(void *parent);                        /* lv_obj_create */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);        /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                            /* lv_obj_clean */
extern void audio_uart_page_44daca(void *obj, int32_t index);             /* lv_obj_move_to_index */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);    /* lv_obj_get_child */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);         /* lv_obj_is_valid */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);      /* lv_obj_set_size */
extern void audio_uart_page_43f568(void *obj, int32_t h);                 /* lv_obj_set_height */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);      /* lv_obj_set_pos */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                            /* lv_obj_align_to */
extern void audio_uart_page_43f66c(void *obj);                            /* lv_obj_update_layout */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);             /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);             /* lv_obj_remove_flag */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);             /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);              /* lv_obj_set_scroll_dir */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void *audio_uart_page_451740(void *obj, void (*cb)(void *), uint32_t filter,
                                    void *user_data);                     /* lv_obj_add_event_cb */
extern uint32_t audio_uart_page_event_code_450286(const void *e);         /* lv_event_get_code */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);             /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main_place, uint32_t cross_place,
                                   uint32_t track_place);                 /* lv_obj_set_flex_align */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                     /* lv_color_hex */
extern void audio_uart_page_441180(void *obj, int32_t v, uint32_t sel);   /* max_width */
extern void audio_uart_page_4411aa(void *obj, int32_t v, uint32_t sel);   /* max_height */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);   /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);   /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);   /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);   /* pad_right */
extern void audio_uart_page_441246(void *obj, int32_t v, uint32_t sel);   /* pad_row */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);   /* pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t opa, uint32_t sel);   /* border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);   /* border_width */
extern void audio_uart_page_44132a(void *obj, uint32_t side, uint32_t sel);  /* border_side */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);   /* shadow_width */
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t sel);   /* image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel); /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);   /* radius */
extern void lv_obj_set_style_anim_duration_441498(void *obj, uint32_t ms, uint32_t sel); /* prop 0x67 */
extern void *audio_uart_page_498668(void *parent);                        /* lv_image_create */
extern void audio_uart_page_498680(void *img, const void *src);           /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                        /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void audio_lv_label_set_text_fmt_49954c(void *label, const char *fmt, ...);
extern void audio_uart_page_layout_499678(void *label, uint32_t mode);    /* lv_label_set_long_mode */
extern void lv_label_set_text_selection_start_499716(void *label, uint32_t index);
extern void lv_label_set_text_selection_end_499752(void *label, uint32_t index);
extern const char *audio_uart_page_text_pointer_4997f8(const void *label); /* lv_label_get_text */
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void *audio_uart_lv_anim_start_450408(const void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern int32_t audio_uart_lv_anim_default_path_450634(void *anim);        /* lv_anim_path_linear */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "teleprompt.ui"; /* ROM 0x7897d0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_ui.c"; /* ROM 0x6fd97c */
static const char empty_text[] = ""; /* ROM 0x555748 / 0x555c00 */
static const char mode_manual_text[] = "M"; /* ROM 0x555cf0 */
static const char mode_auto_text[] = "A"; /* ROM 0x555cf4 */

static const char id_bt_disconnect[] = "ID_GENERAL_BLUETOOTH_DISCONNECT"; /* ROM 0x766130 */
static const char id_elapsed[] = "ID_TELEPROMPT_ELAPSED"; /* ROM 0x77c5bc */
static const char id_no_file[] = "ID_TELEPROMPT_NO_FILE"; /* ROM 0x77c5d4 */
static const char id_select[] = "ID_TELEPROMPT_SELECT"; /* ROM 0x77c5ec */
static const char id_pause[] = "ID_GENERAL_PAUSE"; /* ROM 0x783f78 */
static const char id_closed[] = "ID_TELEPROMPT_CLOSED"; /* ROM 0x77c604 */
static const char elapsed_zero_fmt[] = "%s 0:00:00"; /* ROM 0x78c50c */
static const char elapsed_fmt[] = "%s %d:%02d:%02d"; /* ROM 0x7897f0 */

static const teleprompt_exit_record_t exit_record = {3u, 2u}; /* ROM 0x78eaf4 */

static const char fn_button_create[] = "teleprompt_ui_button_create"; /* ROM 0x772ef4 */
static const char m_button_done[] = "Button(%s) create completed"; /* ROM 0x772f10 */
static const char s_button_done[] = "[teleprompt.ui]Button(%s) create completed"; /* ROM 0x744960 */

static const char fn_display_menu[] = "teleprompt_ui_action_display_menu_page"; /* ROM 0x74f1f4 */
static const char m_ble_lost[] = "BLE disconnected, show exit prompt"; /* ROM 0x75b07c */
static const char s_ble_lost[] = "[teleprompt.ui]BLE disconnected, show exit prompt"; /* ROM 0x72e838 */
static const char m_menu_loading[] = "Menu page created with loading state"; /* ROM 0x74f21c */
static const char s_menu_loading[] = "[teleprompt.ui]Menu page created with loading state"; /* ROM 0x72e86c */
static const char m_request_list[] = "Request file list"; /* ROM 0x783f3c */
static const char s_request_list[] = "[teleprompt.ui]Request file list"; /* ROM 0x75b0a0 */

static const char fn_main_create[] = "teleprompt_ui_action_main_page_create"; /* ROM 0x74f244 */
static const char m_display_size[] = "display_width = %d, display_lines = %d"; /* ROM 0x74f26c */
static const char s_display_size[] = "[teleprompt.ui]display_width = %d, display_lines = %d"; /* ROM 0x723e70 */
static const char m_label_failed[] = "Failed to pre-create page label for index %d"; /* ROM 0x7394f4 */
static const char s_label_failed[] = "[teleprompt.ui]Failed to pre-create page label for index %d"; /* ROM 0x719828 */

static const char fn_display_main[] = "teleprompt_ui_action_display_main_page"; /* ROM 0x74f294 */
static const char m_window[] =
    "window_start_page_id = %d, current_page_id = %d, current_line_id = %d"; /* ROM 0x6fda0c */
static const char s_window[] =
    "[teleprompt.ui]window_start_page_id = %d, current_page_id = %d, current_line_id = %d"; /* ROM 0x6e54b0 */

static const char fn_list_update[] = "teleprompt_ui_action_file_list_update"; /* ROM 0x74f2bc */
static const char m_menu_null[] = "Menu page is NULL"; /* ROM 0x783f50 */
static const char s_menu_null[] = "[teleprompt.ui]Menu page is NULL"; /* ROM 0x75b0c4 */
static const char m_button_failed[] = "Failed to create button for: %s"; /* ROM 0x766150 */
static const char s_button_failed[] = "[teleprompt.ui]Failed to create button for: %s"; /* ROM 0x739524 */
static const char m_list_updated[] = "File list updated with %d items"; /* ROM 0x766170 */
static const char s_list_updated[] = "[teleprompt.ui]File list updated with %d items"; /* ROM 0x739554 */

static const char fn_file_select[] = "teleprompt_ui_action_file_select"; /* ROM 0x75b0e8 */
static const char m_list_empty[] = "file list is NULL or empty"; /* ROM 0x772f2c */
static const char s_list_empty[] = "[teleprompt.ui]file list is NULL or empty"; /* ROM 0x74498c */

static const char fn_menu_up[] = "teleprompt_ui_action_menu_scroll_up"; /* ROM 0x75b10c */
static const char m_menu_up[] = "menu scroll up, scroll_count: %d"; /* ROM 0x75b130 */
static const char s_menu_up[] = "[teleprompt.ui]menu scroll up, scroll_count: %d"; /* ROM 0x739584 */
static const char m_top[] = "Reached top button during scroll, stopping at index %d"; /* ROM 0x723ea8 */
static const char s_top[] = "[teleprompt.ui]Reached top button during scroll, stopping at index %d"; /* ROM 0x6fda54 */
static const char m_prev_failed[] = "Failed to get previous button at index %d"; /* ROM 0x7449b8 */
static const char s_prev_failed[] = "[teleprompt.ui]Failed to get previous button at index %d"; /* ROM 0x719864 */

static const char fn_menu_down[] = "teleprompt_ui_action_menu_scroll_down"; /* ROM 0x74f2e4 */
static const char m_menu_down[] = "menu scroll down, scroll_count: %d"; /* ROM 0x75b154 */
static const char s_menu_down[] = "[teleprompt.ui]menu scroll down, scroll_count: %d"; /* ROM 0x72e8a0 */
static const char m_bottom[] = "Reached bottom button during scroll, stopping at index %d"; /* ROM 0x7198a0 */
static const char s_bottom[] = "[teleprompt.ui]Reached bottom button during scroll, stopping at index %d"; /* ROM 0x6f6874 */
static const char m_next_failed[] = "Failed to get next button at index %d"; /* ROM 0x74f30c */
static const char s_next_failed[] = "[teleprompt.ui]Failed to get next button at index %d"; /* ROM 0x723ee0 */

static const char fn_main_up[] = "teleprompt_ui_action_main_scroll_up"; /* ROM 0x75b178 */
static const char fn_main_down[] = "teleprompt_ui_action_main_scroll_down"; /* ROM 0x74f35c */
static const char m_content_null[] = "scroll container is NULL"; /* ROM 0x772f48 */
static const char s_content_null[] = "[teleprompt.ui]scroll container is NULL"; /* ROM 0x74f334 */

static const char fn_ai_sync[] = "teleprompt_ui_action_ai_sync"; /* ROM 0x766190 */
static const char m_ai_sync[] = "Main page AI sync"; /* ROM 0x783f64 */
static const char s_ai_sync[] = "[teleprompt.ui]Main page AI sync"; /* ROM 0x75b19c */
static const char m_label_null[] = "label is NULL"; /* ROM 0x7897e0 */
static const char s_label_null[] = "[teleprompt.ui]label is NULL"; /* ROM 0x7661b0 */
static const char m_ai_mismatch[] =
    "ai sync payload mismatch: encoded(page=%d,line=%d) context(page=%d,line=%d)"; /* ROM 0x6f68c0 */
static const char s_ai_mismatch[] =
    "[teleprompt.ui]ai sync payload mismatch: encoded(page=%d,line=%d) context(page=%d,line=%d)"; /* ROM 0x6e1b60 */

static const char fn_scroll_sync[] = "teleprompt_ui_action_scroll_sync"; /* ROM 0x75b1c0 */
static const char m_no_pages[] = "total_pages is 0, skip scroll sync"; /* ROM 0x75b1e4 */
static const char s_no_pages[] = "[teleprompt.ui]total_pages is 0, skip scroll sync"; /* ROM 0x72e8d4 */
static const char m_bad_page[] = "scroll sync target page invalid: %u"; /* ROM 0x75b208 */
static const char s_bad_page[] = "[teleprompt.ui]scroll sync target page invalid: %u"; /* ROM 0x72e908 */
static const char m_bad_line[] = "scroll sync target line overflow: %u"; /* ROM 0x74f384 */
static const char s_bad_line[] = "[teleprompt.ui]scroll sync target line overflow: %u"; /* ROM 0x72e93c */
static const char m_outside_band[] =
    "scroll_sync: page %u outside 13-page ensure band, set_window(%u)"; /* ROM 0x706948 */
static const char s_outside_band[] =
    "[teleprompt.ui]scroll_sync: page %u outside 13-page ensure band, set_window(%u)"; /* ROM 0x6f02b8 */
static const char m_sync_not_ready[] = "scroll sync target page not ready: %u, wait page data"; /* ROM 0x723f18 */
static const char s_sync_not_ready[] =
    "[teleprompt.ui]scroll sync target page not ready: %u, wait page data"; /* ROM 0x6fda9c */

static const char fn_gif_complete[] = "teleprompt_ui_action_gif_complete"; /* ROM 0x75b22c */
static const char m_gif_not_ai[] = "GIF animation complete, but mode is not AI"; /* ROM 0x7449e4 */
static const char s_gif_not_ai[] = "[teleprompt.ui]GIF animation complete, but mode is not AI"; /* ROM 0x7198dc */

static const char fn_switch_prev[] = "teleprompt_ui_action_main_page_switch_prev"; /* ROM 0x744a10 */
static const char m_in_window[] = "switch page id is in window range, no need to switch"; /* ROM 0x723f50 */
static const char s_in_window[] =
    "[teleprompt.ui]switch page id is in window range, no need to switch"; /* ROM 0x70698c */
static const char m_prev_not_ready[] =
    "switch prev target page not ready: %d, keep current display and request it"; /* ROM 0x6f690c */
static const char s_prev_not_ready[] =
    "[teleprompt.ui]switch prev target page not ready: %d, keep current display and request it"; /* ROM 0x6e1bbc */
static const char m_prev_start[] =
    "switch start: [window: start_page_id=%d, size=%d], [current: page_id=%d, line_id=%d], "
    "[switch to page_id=%d]"; /* ROM 0x6d76d0 */
static const char s_prev_start[] =
    "[teleprompt.ui]switch start: [window: start_page_id=%d, size=%d], [current: page_id=%d, "
    "line_id=%d], [switch to page_id=%d]"; /* ROM 0x69ce14 */
static const char m_prev_done[] = "switch complete: [window: start_page_id=%d]"; /* ROM 0x744a3c */
static const char s_prev_done[] = "[teleprompt.ui]switch complete: [window: start_page_id=%d]"; /* ROM 0x719918 */

static const char fn_switch_next[] = "teleprompt_ui_action_main_page_switch_next"; /* ROM 0x744a68 */
static const char m_no_slide[] = "switch next: no need to slide forward"; /* ROM 0x74f3ac */
static const char s_no_slide[] = "[teleprompt.ui]switch next: no need to slide forward"; /* ROM 0x723f88 */
static const char m_next_not_ready[] =
    "switch next: target window page %d not ready, keep current display and request it"; /* ROM 0x6ea2d0 */
static const char s_next_not_ready[] =
    "[teleprompt.ui]switch next: target window page %d not ready, keep current display and "
    "request it"; /* ROM 0x6dbb8c */
static const char m_next_start[] =
    "switch start(next): [window start=%d->%d size=%d] [current page=%d line=%d]"; /* ROM 0x6f6958 */
static const char s_next_start[] =
    "[teleprompt.ui]switch start(next): [window start=%d->%d size=%d] [current page=%d line=%d]"; /* ROM 0x6e1c18 */
static const char m_next_done[] = "switch complete(next): [window start=%d]"; /* ROM 0x744a94 */
static const char s_next_done[] = "[teleprompt.ui]switch complete(next): [window start=%d]"; /* ROM 0x723fc0 */

static const char fn_height_anim[] = "teleprompt_ui_height_anim_exec_cb"; /* ROM 0x75b250 */
static const char m_anim_invalid[] = "obj or scroll_bar or title_bar is not valid"; /* ROM 0x744ac0 */
static const char s_anim_invalid[] = "[teleprompt.ui]obj or scroll_bar or title_bar is not valid"; /* ROM 0x719954 */

static const char fn_collapse[] = "teleprompt_ui_collapse_animate"; /* ROM 0x7661d0 */
static const char m_collapse_skip[] = "collapse animate skip: scroll_container is NULL"; /* ROM 0x7395b4 */
static const char s_collapse_skip[] =
    "[teleprompt.ui]collapse animate skip: scroll_container is NULL"; /* ROM 0x70fe64 */

static const char fn_elapsed[] = "teleprompt_ui_action_update_elapsed_time"; /* ROM 0x744aec */
static const char m_title_null[] = "title bar is NULL"; /* ROM 0x783f8c */
static const char s_title_null[] = "[teleprompt.ui]title bar is NULL"; /* ROM 0x75b274 */
static const char m_time_null[] = "time label is NULL"; /* ROM 0x783fa0 */
static const char s_time_null[] = "[teleprompt.ui]time label is NULL"; /* ROM 0x75b298 */
static const char m_elapsed[] =
    "Updated elapsed time: %s %d:%02d:%02d (start_timestamp: %d, elapsed_seconds: %d)"; /* ROM 0x6ea324 */
static const char s_elapsed[] =
    "[teleprompt.ui]Updated elapsed time: %s %d:%02d:%02d (start_timestamp: %d, elapsed_seconds: %d)"; /* ROM 0x6debb4 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

static const void *ui_font(void)
{
    return (const void *)(uintptr_t)audio_uart_ring_primary_head_cell;
}

/* Stock 0x5540f0 (no TSV row): text lines shown at once. */
uint32_t teleprompt_ui_visible_lines_5540f0(void)
{
    return g2_teleprompt_fsm_ctrl.doc.display_lines;
}

/* Stock 0x5540f8 (no TSV row): title-bar y above a text area of lines. */
int32_t teleprompt_ui_title_bar_y_5540f8(uint32_t lines)
{
    return 0xfc - (int32_t)(lines * TELEPROMPT_LINE_HEIGHT);
}

/* Stock 0x555514: page text into a page label, "" while the page has not
 * arrived. */
void teleprompt_ui_page_label_set_text_555514(void *label, uint32_t page)
{
    if (label == 0)
        return;
    const uint8_t *data = teleprompt_page_data_get(page);
    if (data == 0)
        (void)audio_uart_page_49942e(label, empty_text);
    else
        (void)audio_uart_page_49942e(label, (const char *)(data + 10));
}

/* Stock 0x55553c: reload the 4 page labels for a window starting at
 * first_page; labels past the last page are blanked. */
void teleprompt_ui_window_labels_refresh_55553c(g2_teleprompt_ui_t *ui, uint32_t first_page)
{
    const g2_teleprompt_doc_t *doc = &g2_teleprompt_fsm_ctrl.doc;

    for (uint32_t i = 0u; i < TELEPROMPT_WINDOW_PAGES; i++) {
        void *label = audio_uart_lv_child_get_44dce2(ui->content, (int32_t)i);
        uint32_t page = i + first_page;
        if (label == 0)
            continue;
        if (page < doc->total_pages) {
            teleprompt_ui_page_label_set_text_555514(label, page);
            teleprompt_ui_ai_mode_page_process_554b2c(label, page);
        } else {
            (void)audio_uart_page_49942e(label, empty_text);
        }
    }
}

/* Stock 0x5555a4 (teleprompt_ui_button_create): one file-list row, a dimmed
 * icon and a grey one-line title. */
void *teleprompt_ui_button_create_5555a4(void *parent, const void *icon, const char *text)
{
    void *button = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(button, LV_SIZE_CONTENT, 40);
    audio_uart_page_48ba78(button, 0u);
    audio_uart_page_48ba92(button, 0u, 2u, 2u);
    audio_uart_page_44146a(button, 6, 0u);
    audio_uart_page_441254(button, 8, 0u);
    audio_uart_page_44122a(button, 12, 0u);
    audio_uart_page_441238(button, 12, 0u);
    audio_uart_page_44131c(button, 1, 0u);
    audio_uart_page_44130c(button, 0u, 0u);
    audio_uart_page_44129e(button, 0u, 0u);
    audio_uart_page_44132a(button, 0xfu, 0u);
    audio_uart_page_4412ec(button, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43dfa4(button, LV_OBJ_FLAG_SCROLLABLE);

    void *image = audio_uart_page_498668(button);
    audio_uart_page_498680(image, icon);
    audio_uart_page_44127e(image, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(image, 0xffu, 0u);
    audio_uart_page_4413ce(image, 0x33u, 0u);

    void *label = audio_uart_page_499416(button);
    (void)audio_uart_page_49942e(label, text);
    audio_uart_page_44143e(label, ui_font(), 0u);
    audio_uart_page_441180(label, 500, 0u);
    audio_uart_page_4411aa(label, 28, 0u);
    audio_uart_page_layout_499678(label, 1u);
    audio_uart_page_44145a(label, 1u, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0u);

    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_button_create, 0x488u, m_button_done, text);
    if (log_compressed_on())
        (void)compress_log_output(0x10400000u, s_button_done, s_button_done, text);
    return button;
}

/* Stock 0x555710: number of files in the list. */
uint16_t teleprompt_ui_file_count_555710(void)
{
    return teleprompt_file_list_get()->count;
}

/* Stock 0x55571a: menu list scroll begin/end toggles the busy flag. */
void teleprompt_ui_menu_list_event_cb_55571a(void *e)
{
    uint32_t code = audio_uart_page_event_code_450286(e);
    if (code == LV_EVENT_SCROLL_BEGIN)
        g2_teleprompt_ui_window.busy = 1u;
    else if (code == LV_EVENT_SCROLL_END)
        g2_teleprompt_ui_window.busy = 0u;
}

/* Stock 0x555758: show the file-list page and ask the phone for the list;
 * without BLE persist the exit record and show the disconnect prompt. */
int32_t teleprompt_ui_action_display_menu_page_555758(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    (void)state;
    (void)arg;

    if (UX_GetSystemBLEStatus() == 0u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_display_menu, 0x4bfu, m_ble_lost);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_ble_lost, s_ble_lost);
        ui->start_timestamp = 0u;
        if (display_driver_uled_mode_45a568() == 1u) {
            teleprompt_exit_record_t record = exit_record;
            audio_uart_ring_wear_persist_48eb32(TELEPROMPT_EXIT_RECORD_KEY, 2u, &record);
        }
        (void)audio_conversate_ui_message_send_58bfb2(g2_teleprompt_root_20074a7c, localized(id_bt_disconnect),
                                                      TELEPROMPT_APP_ID, 0u, 5000u);
        return -1;
    }

    ui->menu_index = -1;
    ui->menu_selected = 0;
    ui->menu_list = 0;
    audio_uart_page_58c238(g2_teleprompt_root_20074a7c, 250u, 0u);
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_display_menu, 0x4ccu, m_menu_loading);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, s_menu_loading, s_menu_loading);

    uint8_t request[1];
    (void)aeabi_memset_43c0e4(request, sizeof request, 0);
    if (display_driver_uled_mode_45a568() == 1u) {
        (void)APP_PbTxEncodeFileListRequest(request);
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_display_menu, 0x4d2u, m_request_list);
        if (log_compressed_on())
            (void)compress_log_output(0x0c000000u, s_request_list, s_request_list);
    }
    return 0;
}

/* Stock 0x5558d4: build the reading page: scroll container with 4 page
 * labels, scroll bar, title bar with elapsed time and mode indicator. Coming
 * from the menu (state 1) the file-list page is deleted first. The page stays
 * hidden until display_main_page. */
int32_t teleprompt_ui_action_main_page_create_5558d4(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_doc_t *doc = &g2_teleprompt_fsm_ctrl.doc;
    (void)arg;

    ui->flag_45 = 0u;
    teleprompt_page_data_init(doc->start_page, doc->total_pages);
    if (state == TELEPROMPT_STATE_MENU && ui->menu_page != 0) {
        audio_uart_page_delete_event_filter_44d7b8(ui->menu_page);
        ui->menu_page = 0;
    }

    uint32_t lines = teleprompt_ui_visible_lines_5540f0();
    ui->content = audio_uart_page_43de82(ui->root);
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_main_create, 0x4f1u, m_display_size,
                           doc->display_width, lines);
    if (log_compressed_on())
        (void)compress_log_output(0x10800000u, s_display_size, s_display_size, doc->display_width, lines);

    audio_uart_page_43f4c0(ui->content, doc->display_width, (int32_t)(lines * TELEPROMPT_LINE_HEIGHT));
    audio_uart_page_43f6b8(ui->content, LV_ALIGN_BOTTOM_MID, -4, 0);
    audio_uart_page_44129e(ui->content, 0u, 0u);
    audio_uart_page_44131c(ui->content, 0, 0u);
    lv_obj_set_style_pad_all_554080(ui->content, 0, 0u);
    audio_uart_page_44146a(ui->content, 0, 0u);
    audio_uart_page_44e368(ui->content, 0u);
    audio_uart_page_43ded4(ui->content, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e3ca(ui->content, LV_DIR_VER);
    audio_uart_page_43dfa4(ui->content, LV_OBJ_FLAG_SCROLL_ELASTIC_MOMENTUM_CHAIN);
    audio_uart_page_48ba78(ui->content, 1u);
    audio_uart_page_48ba92(ui->content, 0u, 0u, 0u);
    audio_uart_page_441246(ui->content, 0, 0u);

    for (uint32_t i = 0u; i < TELEPROMPT_WINDOW_PAGES; i++) {
        void *label = teleprompt_ui_page_label_create_555486(ui->content);
        if (label != 0) {
            (void)audio_uart_page_49942e(label, empty_text);
            continue;
        }
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_main_create, 0x506u, m_label_failed, i);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, s_label_failed, s_label_failed, i);
    }
    (void)audio_uart_page_451740(ui->content, teleprompt_ui_scroll_event_cb_55545c, LV_EVENT_SCROLL_BEGIN, 0);
    (void)audio_uart_page_451740(ui->content, teleprompt_ui_scroll_event_cb_55545c, LV_EVENT_SCROLL, 0);
    (void)audio_uart_page_451740(ui->content, teleprompt_ui_scroll_event_cb_55545c, LV_EVENT_SCROLL_END, 0);

    ui->scroll_bar = teleprompt_ui_scroll_bar_create_554c68(ui->root);
    audio_uart_page_43f6b8(ui->scroll_bar, LV_ALIGN_BOTTOM_RIGHT, 0, 0);

    ui->title_bar = audio_uart_page_43de82(ui->root);
    audio_uart_page_43f4c0(ui->title_bar, 0x240, TELEPROMPT_LINE_HEIGHT);
    audio_uart_page_43f09a(ui->title_bar, 0, teleprompt_ui_title_bar_y_5540f8(lines));
    audio_uart_page_44129e(ui->title_bar, 0u, 0u);
    audio_uart_page_44131c(ui->title_bar, 0, 0u);
    lv_obj_set_style_pad_all_554080(ui->title_bar, 0, 0u);
    audio_uart_page_44146a(ui->title_bar, 0, 0u);
    audio_uart_page_43dfa4(ui->title_bar, LV_OBJ_FLAG_SCROLLABLE);

    void *time_label = audio_uart_page_499416(ui->title_bar);
    audio_uart_page_43f4c0(time_label, LV_SIZE_CONTENT, TELEPROMPT_LINE_HEIGHT);
    audio_uart_page_43f6b8(time_label, LV_ALIGN_RIGHT_MID, 0, 0);
    audio_lv_label_set_text_fmt_49954c(time_label, elapsed_zero_fmt, localized(id_elapsed));
    audio_uart_page_44143e(time_label, ui_font(), 0u);
    audio_uart_page_44140e(time_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44145a(time_label, 3u, 0u);

    void *mode_obj = 0;
    if (doc->mode == TELEPROMPT_MODE_AI) {
        mode_obj = audio_conversate_pre_notes_anim_create_58c7a0(ui->title_bar, teleprompt_ui_scroll_to_top_554e9c);
    } else if (doc->mode == TELEPROMPT_MODE_MANUAL) {
        mode_obj = audio_uart_page_499416(ui->title_bar);
        audio_uart_page_44143e(mode_obj, g2_translate_lang_pair_font, 0u);
        audio_uart_page_44140e(mode_obj, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44145a(mode_obj, 3u, 0u);
        (void)audio_uart_page_49942e(mode_obj, mode_manual_text);
    } else if (doc->mode == TELEPROMPT_MODE_AUTO) {
        mode_obj = audio_uart_page_499416(ui->title_bar);
        audio_uart_page_44143e(mode_obj, g2_translate_lang_pair_font, 0u);
        audio_uart_page_44140e(mode_obj, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44145a(mode_obj, 3u, 0u);
        (void)audio_uart_page_49942e(mode_obj, mode_auto_text);
    }
    audio_uart_page_43f4c0(mode_obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(mode_obj, LV_ALIGN_LEFT_MID, 0, 0);
    audio_uart_page_43ded4(ui->root, LV_OBJ_FLAG_HIDDEN);
    return 0;
}

/* Stock 0x555c04: unhide the page, choose the 4-page window around the start
 * page (one page of look-behind, clamped to the end), fill it and scroll to
 * the start line; fade in when entered from the main state. */
int32_t teleprompt_ui_action_display_main_page_555c04(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_doc_t *doc = &g2_teleprompt_fsm_ctrl.doc;
    (void)arg;

    audio_uart_page_43dfa4(ui->root, LV_OBJ_FLAG_HIDDEN);
    ui->last_scroll_y = 0x7fff;
    uint32_t total = doc->total_pages;
    uint32_t start = doc->start_page;
    if (total < 5u) {
        ui->window_first_page = 0u;
    } else {
        ui->window_first_page = start != 0u ? start - 1u : 0u;
        if (total < ui->window_first_page + TELEPROMPT_WINDOW_PAGES)
            ui->window_first_page = total - TELEPROMPT_WINDOW_PAGES;
    }
    ui->current_page = start;
    ui->current_line = doc->start_line;
    teleprompt_page_data_set_window(ui->window_first_page);
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_display_main, 0x55eu, m_window,
                           ui->window_first_page, ui->current_page, ui->current_line);
    if (log_compressed_on())
        (void)compress_log_output(0x0cc00000u, s_window, s_window, ui->window_first_page, ui->current_page,
                                  ui->current_line);

    teleprompt_ui_window_labels_refresh_55553c(ui, ui->window_first_page);
    uint32_t offset = ui->current_page - ui->window_first_page;
    if (offset >= TELEPROMPT_WINDOW_PAGES)
        offset = 3u;
    audio_uart_lv_scroll_to_y_44ea04(ui->content,
                                     (int32_t)(offset * TELEPROMPT_PAGE_HEIGHT + doc->start_line * TELEPROMPT_LINE_HEIGHT),
                                     0u);
    if (state == TELEPROMPT_STATE_MAIN)
        audio_uart_page_58c238(g2_teleprompt_root_20074a7c, 250u, 0u);
    return 0;
}

/* Stock 0x555d18: rebuild the file-list page from the received list; the
 * first button gets the focus frame. */
int32_t teleprompt_ui_action_file_list_update_555d18(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_file_list_t *list = teleprompt_file_list_get();
    (void)state;
    (void)arg;

    if (ui->menu_page == 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_list_update, 0x57cu, m_menu_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_menu_null, s_menu_null);
        return -1;
    }
    audio_uart_page_44d878(ui->menu_page);

    if (list->count == 0u) {
        void *label = audio_uart_page_499416(ui->menu_page);
        (void)audio_uart_page_49942e(label, localized(id_no_file));
        audio_uart_page_43f4c0(label, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        audio_uart_page_43f6b8(label, LV_ALIGN_CENTER, 0, 0);
        audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44143e(label, ui_font(), 0u);
        audio_uart_page_44145a(label, 2u, 0u);
        return 0;
    }

    void *heading = audio_uart_page_499416(ui->menu_page);
    (void)audio_uart_page_49942e(heading, localized(id_select));
    audio_uart_page_43f4c0(heading, LV_SIZE_CONTENT, 40);
    audio_uart_page_43f6b8(heading, LV_ALIGN_TOP_LEFT, 12, 0);
    audio_uart_page_44140e(heading, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(heading, ui_font(), 0u);
    audio_uart_page_44145a(heading, 2u, 0u);

    ui->menu_list = audio_uart_page_43de82(ui->menu_page);
    audio_uart_page_43f4c0(ui->menu_list, LV_PCT_100, 200);
    audio_uart_page_43f6b8(ui->menu_list, LV_ALIGN_TOP_LEFT, 0, 0x38);
    audio_uart_page_48ba78(ui->menu_list, 1u);
    audio_uart_page_48ba92(ui->menu_list, 0u, 0u, 0u);
    audio_uart_page_441246(ui->menu_list, 0, 0u);
    audio_uart_page_44122a(ui->menu_list, 0, 0u);
    audio_uart_page_441238(ui->menu_list, 0, 0u);
    audio_uart_page_44120e(ui->menu_list, 0, 0u);
    audio_uart_page_44121c(ui->menu_list, 0, 0u);
    audio_uart_page_44129e(ui->menu_list, 0u, 0u);
    audio_uart_page_44131c(ui->menu_list, 0, 0u);
    audio_uart_page_44146a(ui->menu_list, 0, 0u);
    audio_uart_page_441386(ui->menu_list, 0, 0u);
    audio_uart_page_44e368(ui->menu_list, 0u);
    audio_uart_page_43ded4(ui->menu_list, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43dfa4(ui->menu_list, LV_OBJ_FLAG_SCROLL_ELASTIC_MOMENTUM_CHAIN);
    (void)audio_uart_page_451740(ui->menu_list, teleprompt_ui_menu_list_event_cb_55571a, LV_EVENT_SCROLL_BEGIN, 0);
    (void)audio_uart_page_451740(ui->menu_list, teleprompt_ui_menu_list_event_cb_55571a, LV_EVENT_SCROLL_END, 0);
    lv_obj_set_style_anim_duration_441498(ui->menu_list, 200u, 0u);

    for (int32_t i = 0; i < (int32_t)list->count; i++) {
        const char *title = list->items[i].title;
        void *button = teleprompt_ui_button_create_5555a4(ui->menu_list, g2_teleprompt_file_icon_772a24, title);
        if (button == 0) {
            if (log_extended_on())
                audio_log_extended(1u, module_tag, source_file, fn_list_update, 0x5b5u, m_button_failed, title);
            if (log_compressed_on())
                (void)compress_log_output(0x04400000u, s_button_failed, s_button_failed, title);
        } else if (i == 0) {
            ui->menu_selected = button;
            ui->menu_index = 0;
            audio_terminal_session_row_show_5897ee(button);
            audio_uart_page_44130c(button, 0xffu, 0u);
        }
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_list_update, 0x5c2u, m_list_updated, list->count);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, s_list_updated, s_list_updated, list->count);
    return 0;
}

/* Stock 0x556010: send the focused file name to the phone (master only)
 * and drop the list. */
int32_t teleprompt_ui_action_file_select_556010(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_file_list_t *list = teleprompt_file_list_get();
    (void)state;
    (void)arg;

    if (list == 0 || list->count == 0u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_file_select, 0x5d0u, m_list_empty);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_list_empty, s_list_empty);
        return -1;
    }
    audio_uart_page_44d878(ui->menu_page);
    if (display_driver_uled_mode_45a568() == 1u) {
        g2_teleprompt_file_select_t request;
        const g2_teleprompt_file_item_t *item;
        (void)aeabi_memset_43c0e4(&request, sizeof request, 0);
        item = &list->items[ui->menu_index];
        (void)audio_queue_copy_bytes(request.name, item->name, item->name_len);
        request.name_len = list->items[ui->menu_index].name_len;
        (void)APP_PbTxEncodeFileSelect(&request);
    }
    teleprompt_file_list_reset();
    return 0;
}

/* Stock 0x5560d0: page data arrived; refresh its label when it is inside
 * the window and resync the scroll position, unless the page is busy. */
int32_t teleprompt_ui_action_page_data_5560d0(uint8_t state, uint32_t page)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_doc_t *doc = &g2_teleprompt_fsm_ctrl.doc;
    (void)state;

    if (ui->content == 0 || ui->busy != 0u || ui->switching != 0u)
        return 0;
    if (page >= ui->window_first_page && page < ui->window_first_page + TELEPROMPT_WINDOW_PAGES &&
        page < doc->total_pages) {
        void *label = audio_uart_lv_child_get_44dce2(ui->content, (int32_t)(page - ui->window_first_page));
        if (label != 0)
            teleprompt_ui_page_label_set_text_555514(label, page);
    }
    teleprompt_ui_scroll_container_scroll_end_check_555200(1u);
    return 0;
}

/* Stock 0x556134: move the file focus up by count rows (0xaa = bounce). */
int32_t teleprompt_ui_action_menu_scroll_up_556134(uint8_t state, uint32_t count)
{
    (void)state;
    if (count == TELEPROMPT_LIST_BOUNCE) {
        audio_conversate_main_list_scroll_58a680(g2_teleprompt_ui_window.menu_list, 0x38, 1u, 0u);
        return 0;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_menu_up, 0x60du, m_menu_up, count);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, s_menu_up, s_menu_up, count);

    for (uint32_t i = 0u; i < count; i++) {
        g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
        if (ui->menu_index < 1) {
            if (log_extended_on())
                audio_log_extended(4u, module_tag, source_file, fn_menu_up, 0x612u, m_top, ui->menu_index);
            if (log_compressed_on())
                (void)compress_log_output(0x10400000u, s_top, s_top, ui->menu_index);
            break;
        }
        void *button = audio_uart_lv_child_get_44dce2(ui->menu_list, ui->menu_index - 1);
        if (button == 0) {
            if (log_extended_on())
                audio_log_extended(2u, module_tag, source_file, fn_menu_up, 0x61au, m_prev_failed,
                                   ui->menu_index - 1);
            if (log_compressed_on())
                (void)compress_log_output(0x08400000u, s_prev_failed, s_prev_failed, ui->menu_index - 1);
            break;
        }
        (void)audio_terminal_session_animate_5896fc(ui->menu_selected, button, 200u);
        ui->menu_selected = button;
        ui->menu_index = ui->menu_index - 1;
    }
    return 0;
}

/* Stock 0x556284: move the file focus down by count rows (0xaa = bounce). */
int32_t teleprompt_ui_action_menu_scroll_down_556284(uint8_t state, uint32_t count)
{
    (void)state;
    if (count == TELEPROMPT_LIST_BOUNCE) {
        audio_conversate_main_list_scroll_58a680(g2_teleprompt_ui_window.menu_list, 0x38, 0u, 0u);
        return 0;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_menu_down, 0x635u, m_menu_down, count);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, s_menu_down, s_menu_down, count);

    for (uint32_t i = 0u; i < count; i++) {
        uint32_t files = teleprompt_ui_file_count_555710();
        g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
        if ((uint32_t)ui->menu_index >= files - 1u) {
            if (log_extended_on())
                audio_log_extended(4u, module_tag, source_file, fn_menu_down, 0x63cu, m_bottom, ui->menu_index);
            if (log_compressed_on())
                (void)compress_log_output(0x10400000u, s_bottom, s_bottom, ui->menu_index);
            break;
        }
        void *button = audio_uart_lv_child_get_44dce2(ui->menu_list, ui->menu_index + 1);
        if (button == 0) {
            if (log_extended_on())
                audio_log_extended(2u, module_tag, source_file, fn_menu_down, 0x644u, m_next_failed,
                                   ui->menu_index + 1);
            if (log_compressed_on())
                (void)compress_log_output(0x08400000u, s_next_failed, s_next_failed, ui->menu_index + 1);
            break;
        }
        (void)audio_terminal_session_animate_5896fc(ui->menu_selected, button, 200u);
        ui->menu_selected = button;
        ui->menu_index = ui->menu_index + 1;
    }
    return 0;
}

/* Stock 0x5563c0: animated scroll of the text to y. */
int32_t teleprompt_ui_action_main_scroll_up_5563c0(uint8_t state, uint32_t y)
{
    (void)state;
    if (g2_teleprompt_ui_window.content == 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_main_up, 0x65au, m_content_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_content_null, s_content_null);
        return 0;
    }
    audio_uart_lv_scroll_to_y_44ea04(g2_teleprompt_ui_window.content, (int32_t)y, 1u);
    return 0;
}

/* Stock 0x556428: same as main_scroll_up, separate FSM entry. */
int32_t teleprompt_ui_action_main_scroll_down_556428(uint8_t state, uint32_t y)
{
    (void)state;
    if (g2_teleprompt_ui_window.content == 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_main_down, 0x66bu, m_content_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_content_null, s_content_null);
        return 0;
    }
    audio_uart_lv_scroll_to_y_44ea04(g2_teleprompt_ui_window.content, (int32_t)y, 1u);
    return 0;
}

/* Stock 0x5564a8: AI read-along. Pages before the synced page are fully
 * selected, the synced page up to the synced character, later pages not at
 * all; then scroll to page*10+line. */
int32_t teleprompt_ui_action_ai_sync_5564a8(uint8_t state, uint32_t packed)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const uint32_t *sync = g2_teleprompt_fsm_ctrl.ai_sync;
    (void)state;

    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_ai_sync, 0x67du, m_ai_sync);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, s_ai_sync, s_ai_sync);
    if (audio_uart_lv_child_get_44dce2(ui->content, 0) == 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_ai_sync, 0x681u, m_label_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_label_null, s_label_null);
        return -1;
    }
    for (uint32_t i = 0u; i < TELEPROMPT_WINDOW_PAGES; i++) {
        void *label = audio_uart_lv_child_get_44dce2(ui->content, (int32_t)i);
        if (label == 0)
            continue;
        uint32_t page = i + ui->window_first_page;
        if (page < sync[0]) {
            lv_label_set_text_selection_start_499716(label, 0u);
            lv_label_set_text_selection_end_499752(label,
                g2_log_module_length(audio_uart_page_text_pointer_4997f8(label)));
        } else if (page == sync[0]) {
            lv_label_set_text_selection_start_499716(label, 0u);
            lv_label_set_text_selection_end_499752(label, sync[2]);
        } else {
            lv_label_set_text_selection_start_499716(label, LV_LABEL_TEXT_SELECTION_OFF);
            lv_label_set_text_selection_end_499752(label, LV_LABEL_TEXT_SELECTION_OFF);
        }
    }
    uint32_t page = packed / 10u;
    uint32_t line = packed % 10u;
    if (page != sync[0] || line != sync[1]) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_ai_sync, 0x69eu, m_ai_mismatch, page, line,
                               sync[0], sync[1]);
        if (log_compressed_on())
            (void)compress_log_output(0x09000000u, s_ai_mismatch, s_ai_mismatch, page, line, sync[0], sync[1]);
    }
    audio_uart_lv_scroll_to_y_44ea04(ui->content, teleprompt_ui_get_scroll_y_by_page_line_id_554a84(ui->content, page, (int32_t)line, 1u), 1u);
    return 0;
}

/* Stock 0x556688: phone scroll sync to page*10+line. Moves the window when
 * the line is not visible, requests a missing page through the FSM jump,
 * updates the scroll bar and scrolls (animated only when the target was
 * already visible in the old window). */
int32_t teleprompt_ui_action_scroll_sync_556688(uint8_t state, uint32_t packed)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_doc_t *doc = &g2_teleprompt_fsm_ctrl.doc;
    (void)state;

    if (ui->content == 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_scroll_sync, 0x6afu, m_content_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, s_content_null, s_content_null);
        return 0;
    }
    if (doc->total_pages == 0u) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_scroll_sync, 0x6b4u, m_no_pages);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_no_pages, s_no_pages);
        return 0;
    }
    uint32_t page = packed / 10u;
    uint32_t line = packed % 10u;
    if (page >= doc->total_pages) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_scroll_sync, 0x6bbu, m_bad_page, page);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, s_bad_page, s_bad_page, page);
        return 0;
    }
    if (line >= 10u) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_scroll_sync, 0x6bfu, m_bad_line, line);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, s_bad_line, s_bad_line, line);
        line = 9u;
    }

    uint32_t old_window = ui->window_first_page;
    uint8_t animate = (page >= old_window && page < old_window + TELEPROMPT_WINDOW_PAGES &&
                       teleprompt_ui_line_in_window_5549e6(ui->content, old_window, page, (int32_t)line) != 0u) ? 1u : 0u;
    uint32_t window = teleprompt_ui_window_first_page_for_554a16(ui->content, old_window, page, (int32_t)line);
    uint8_t moved = window != old_window ? 1u : 0u;
    if (moved != 0u) {
        ui->window_first_page = window;
        teleprompt_ui_window_labels_refresh_55553c(ui, ui->window_first_page);
        audio_uart_page_43f66c(ui->content);
    }
    uint8_t ready = teleprompt_page_data_get(page) != 0 ? 1u : 0u;
    uint8_t ensured = semantic_page_in_ensure_window(page);
    if ((uint8_t)((ready ^ 1u) | moved) != 0u || ensured == 0u) {
        if (ensured == 0u) {
            if (log_extended_on())
                audio_log_extended(3u, module_tag, source_file, fn_scroll_sync, 0x6dbu, m_outside_band, page,
                                   ui->window_first_page);
            if (log_compressed_on())
                (void)compress_log_output(0x0c800000u, s_outside_band, s_outside_band, page,
                                          ui->window_first_page);
        }
        teleprompt_page_data_set_window(ui->window_first_page);
    }
    if (ready != 0u) {
        teleprompt_fsm_jump_clear_58c882();
    } else {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_scroll_sync, 0x6e1u, m_sync_not_ready, page);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, s_sync_not_ready, s_sync_not_ready, page);
        teleprompt_fsm_jump_set_58c874(page);
    }
    int32_t y = teleprompt_ui_get_scroll_y_by_page_line_id_554a84(ui->content, page, (int32_t)line, 0u);
    ui->current_page = page;
    ui->current_line = line;
    ui->last_scroll_y = y;
    teleprompt_ui_scroll_bar_set_value_554d58(ui->scroll_bar, (int32_t)ui->current_page, (int32_t)ui->current_line);
    audio_uart_lv_scroll_to_y_44ea04(ui->content, y, animate);
    return 0;
}

/* Stock 0x556964: title-bar pause icon (child 2) with the localized "pause"
 * text (child 3) to its right, created on first use. */
void *teleprompt_ui_pause_icon_get_556964(void)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    void *icon = audio_uart_lv_child_get_44dce2(ui->title_bar, 2);
    if (icon != 0)
        return icon;

    icon = audio_uart_page_498668(ui->title_bar);
    audio_uart_page_498680(icon, g2_translate_pause_image);
    audio_uart_page_44127e(icon, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(icon, 0xffu, 0u);
    audio_uart_page_4413ce(icon, 0xffu, 0u);
    audio_uart_page_43f4c0(icon, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(icon, LV_ALIGN_LEFT_MID, 0, 0);

    void *text = audio_uart_page_499416(ui->title_bar);
    (void)audio_uart_page_49942e(text, localized(id_pause));
    audio_uart_page_44143e(text, ui_font(), 0u);
    audio_uart_page_44140e(text, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f6d6(text, icon, LV_ALIGN_OUT_RIGHT_MID, 8, 0);
    return icon;
}

/* Stock 0x556a28: swap the mode indicator (child 1) for the pause icon.
 * show = 1 hides the indicator (pausing the AI GIF) and shows the icon, its
 * text only when paused; show = 0 restores the indicator. */
void teleprompt_ui_title_pause_show_556a28(uint8_t show, uint8_t paused)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    if (ui->title_bar == 0)
        return;
    void *indicator = audio_uart_lv_child_get_44dce2(ui->title_bar, 1);
    if (indicator == 0)
        return;
    uint8_t ai_mode = g2_teleprompt_fsm_ctrl.doc.mode == TELEPROMPT_MODE_AI ? 1u : 0u;

    if (show != 0u) {
        if (ai_mode != 0u)
            audio_conversate_route_before_release_58c836(indicator);
        audio_uart_page_43ded4(indicator, LV_OBJ_FLAG_HIDDEN);
        audio_uart_page_43dfa4(teleprompt_ui_pause_icon_get_556964(), LV_OBJ_FLAG_HIDDEN);
        void *text = audio_uart_lv_child_get_44dce2(ui->title_bar, 3);
        if (text == 0)
            return;
        if (paused != 0u)
            audio_uart_page_43dfa4(text, LV_OBJ_FLAG_HIDDEN);
        else
            audio_uart_page_43ded4(text, LV_OBJ_FLAG_HIDDEN);
        return;
    }
    if (ai_mode != 0u)
        (void)audio_conversate_route_release_58c84e(indicator);
    audio_uart_page_43dfa4(indicator, LV_OBJ_FLAG_HIDDEN);
    void *icon = audio_uart_lv_child_get_44dce2(ui->title_bar, 2);
    if (icon != 0)
        audio_uart_page_43ded4(icon, LV_OBJ_FLAG_HIDDEN);
    void *text = audio_uart_lv_child_get_44dce2(ui->title_bar, 3);
    if (text != 0)
        audio_uart_page_43ded4(text, LV_OBJ_FLAG_HIDDEN);
}

/* Stock 0x556ad4: show the pause icon alone as a hint while not paused. */
void teleprompt_ui_pause_hint_show_556ad4(void)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    if (ui->title_bar != 0 && ui->paused == 0u && ui->pause_hint == 0u) {
        teleprompt_ui_title_pause_show_556a28(1u, 0u);
        ui->pause_hint = 1u;
    }
}

/* Stock 0x556b00: drop the hint again (unless paused meanwhile). */
void teleprompt_ui_pause_hint_hide_556b00(void)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    if (ui->pause_hint != 0u) {
        ui->pause_hint = 0u;
        if (ui->paused == 0u)
            teleprompt_ui_title_pause_show_556a28(0u, 0u);
    }
}

/* Stock 0x556b2c: pause: icon + text, collapse the text area. */
int32_t teleprompt_ui_action_pause_556b2c(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    (void)state;
    (void)arg;
    if (ui->paused != 0u)
        return 0;
    teleprompt_ui_title_pause_show_556a28(1u, 1u);
    ui->paused = 1u;
    teleprompt_ui_collapse_animate_5571a8(1u);
    return 0;
}

/* Stock 0x556b52: resume: restore indicator and text area. */
int32_t teleprompt_ui_action_resume_556b52(uint8_t state, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    (void)state;
    (void)arg;
    if (ui->paused == 0u)
        return 0;
    teleprompt_ui_title_pause_show_556a28(0u, 0u);
    ui->paused = 0u;
    teleprompt_ui_collapse_animate_5571a8(0u);
    return 0;
}

/* Stock 0x556b78: leave teleprompt. From the menu (state 1) only the master
 * closes the app; otherwise show "bluetooth disconnected" (reason 1, 5 s) or
 * "teleprompt closed". */
int32_t teleprompt_ui_action_exit_556b78(uint8_t state, uint32_t reason)
{
    g2_teleprompt_ui_window.start_timestamp = 0u;
    teleprompt_page_data_deinit();
    if (state == TELEPROMPT_STATE_MENU) {
        if (display_driver_uled_mode_45a568() == 1u)
            audio_system_alert_close_464c36(TELEPROMPT_APP_ID, 0u, 0u, 0u);
        return 0;
    }
    if (reason == 1u)
        (void)audio_conversate_ui_message_send_58bfb2(g2_teleprompt_root_20074a7c, localized(id_bt_disconnect),
                                                      TELEPROMPT_APP_ID, 0u, 5000u);
    else
        (void)audio_conversate_ui_message_send_58bfb2(g2_teleprompt_root_20074a7c, localized(id_closed),
                                                      TELEPROMPT_APP_ID, 0u, 0u);
    return 0;
}

/* Stock 0x556bfe: leave with the animated "teleprompt closed" prompt. */
int32_t teleprompt_ui_action_exit_animated_556bfe(uint8_t state, uint32_t arg)
{
    (void)state;
    (void)arg;
    g2_teleprompt_ui_window.start_timestamp = 0u;
    teleprompt_page_data_deinit();
    (void)audio_conversate_ui_message_send_58bfb2(g2_teleprompt_root_20074a7c, localized(id_closed),
                                                  TELEPROMPT_APP_ID, 1u, 0u);
    return 0;
}

/* Stock 0x556c44: AI GIF finished one loop: restart it. */
int32_t teleprompt_ui_action_gif_complete_556c44(uint8_t state, uint32_t arg)
{
    (void)state;
    (void)arg;
    if (g2_teleprompt_fsm_ctrl.doc.mode != TELEPROMPT_MODE_AI) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_gif_complete, 0x7c0u, m_gif_not_ai);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_gif_not_ai, s_gif_not_ai);
        return 0;
    }
    (void)audio_conversate_route_release_58c84e(audio_uart_lv_child_get_44dce2(g2_teleprompt_ui_window.title_bar, 1));
    return 0;
}

/* Stock 0x556cd8: scrolled above the window. packed = (line << 16) | page;
 * when page - 1 is before the window and ready, recycle the last label as
 * the new first one and shift the window back by one page. */
int32_t teleprompt_ui_action_main_page_switch_prev_556cd8(uint8_t state, uint32_t packed)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    (void)state;

    ui->switching = 1u;
    uint32_t line = packed >> 16;
    uint32_t page = packed & 0xffffu;
    uint32_t target = page - 1u;
    if (target >= ui->window_first_page) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_switch_prev, 0x7d9u, m_in_window);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_in_window, s_in_window);
        ui->switching = 0u;
        return 0;
    }
    if (teleprompt_page_data_get(target) == 0) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_switch_prev, 0x7dfu, m_prev_not_ready, target);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, s_prev_not_ready, s_prev_not_ready, target);
        teleprompt_fsm_jump_set_58c874(target);
        teleprompt_page_data_set_window(target);
        ui->switching = 0u;
        return 0;
    }
    teleprompt_fsm_jump_clear_58c882();
    ui->current_line = line;
    ui->current_page = page;
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_switch_prev, 0x7eau, m_prev_start,
                           ui->window_first_page, TELEPROMPT_WINDOW_PAGES, ui->current_page, ui->current_line, target);
    if (log_compressed_on())
        (void)compress_log_output(0x0d400000u, s_prev_start, s_prev_start, ui->window_first_page,
                                  TELEPROMPT_WINDOW_PAGES, ui->current_page, ui->current_line, target);

    void *label = audio_uart_lv_child_get_44dce2(ui->content, 3);
    teleprompt_ui_page_label_set_text_555514(label, target);
    teleprompt_ui_ai_mode_page_process_554b2c(label, target);
    audio_uart_page_44daca(label, 0);
    audio_uart_page_43f66c(ui->content);
    ui->window_first_page = target;
    teleprompt_page_data_set_window(ui->window_first_page);
    audio_uart_lv_scroll_to_y_44ea04(ui->content,
                                     (int32_t)(ui->current_line * TELEPROMPT_LINE_HEIGHT + TELEPROMPT_PAGE_HEIGHT), 0u);
    ui->switching = 0u;
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_switch_prev, 0x7fau, m_prev_done, ui->window_first_page);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, s_prev_done, s_prev_done, ui->window_first_page);
    return 0;
}

/* Stock 0x556ed4: scrolled past the window. The new window starts one page
 * before page (clamped to the last 4 pages); it is applied only when every
 * page of it is ready, otherwise the first missing page is requested. */
int32_t teleprompt_ui_action_main_page_switch_next_556ed4(uint8_t state, uint32_t packed)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_doc_t *doc = &g2_teleprompt_fsm_ctrl.doc;
    (void)state;

    ui->switching = 1u;
    uint32_t line = packed >> 16;
    uint32_t page = packed & 0xffffu;
    uint32_t target = page != 0u ? page - 1u : 0u;
    if (doc->total_pages >= 5u && doc->total_pages < target + TELEPROMPT_WINDOW_PAGES)
        target = doc->total_pages - TELEPROMPT_WINDOW_PAGES;
    if (doc->total_pages < 5u)
        target = 0u;
    if (ui->window_first_page >= target) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_switch_next, 0x819u, m_no_slide);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_no_slide, s_no_slide);
        ui->switching = 0u;
        return 0;
    }

    uint32_t missing = 0u;
    uint8_t all_ready = 1u;
    for (uint32_t p = target; p < target + TELEPROMPT_WINDOW_PAGES && p < doc->total_pages; p++) {
        if (teleprompt_page_data_get(p) == 0) {
            all_ready = 0u;
            missing = p;
            break;
        }
    }
    if (all_ready == 0u) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_switch_next, 0x829u, m_next_not_ready, missing);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, s_next_not_ready, s_next_not_ready, missing);
        teleprompt_fsm_jump_set_58c874(missing);
        teleprompt_page_data_set_window(target);
        ui->switching = 0u;
        return 0;
    }

    teleprompt_fsm_jump_clear_58c882();
    ui->current_line = line;
    ui->current_page = page;
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_switch_next, 0x834u, m_next_start, ui->window_first_page,
                           target, TELEPROMPT_WINDOW_PAGES, ui->current_page, ui->current_line);
    if (log_compressed_on())
        (void)compress_log_output(0x0d400000u, s_next_start, s_next_start, ui->window_first_page, target,
                                  TELEPROMPT_WINDOW_PAGES, ui->current_page, ui->current_line);
    ui->window_first_page = target;
    teleprompt_ui_window_labels_refresh_55553c(ui, target);
    teleprompt_page_data_set_window(target);
    audio_uart_page_43f66c(ui->content);
    audio_uart_lv_scroll_to_y_44ea04(ui->content,
                                     (int32_t)((ui->current_page - ui->window_first_page) * TELEPROMPT_PAGE_HEIGHT +
                                               ui->current_line * TELEPROMPT_LINE_HEIGHT),
                                     0u);
    ui->switching = 0u;
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_switch_next, 0x840u, m_next_done, ui->window_first_page);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, s_next_done, s_next_done, ui->window_first_page);
    return 0;
}

/* Stock 0x557104 (teleprompt_ui_height_anim_exec_cb): text area and scroll
 * bar take the animated height, the title bar rides on top of them. */
void teleprompt_ui_height_anim_exec_cb_557104(void *obj, int32_t height)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    if (audio_terminal_ui_object_valid_43e2ea(obj) != 0u &&
        audio_terminal_ui_object_valid_43e2ea(ui->scroll_bar) != 0u &&
        audio_terminal_ui_object_valid_43e2ea(ui->title_bar) != 0u) {
        audio_uart_page_43f568(obj, height);
        audio_uart_page_43f568(ui->scroll_bar, height);
        teleprompt_ui_scroll_container_scroll_end_check_555200(0u);
        audio_uart_page_43f09a(ui->title_bar, 0, 0xfc - height);
        return;
    }
    if (log_extended_on())
        audio_log_extended(2u, module_tag, source_file, fn_height_anim, 0x853u, m_anim_invalid);
    if (log_compressed_on())
        (void)compress_log_output(0x08000000u, s_anim_invalid, s_anim_invalid);
}

/* Stock 0x55718c: collapse/expand animation finished. */
void teleprompt_ui_collapse_anim_ready_cb_55718c(void *anim)
{
    (void)anim;
    g2_teleprompt_ui_window.busy = 0u;
}

/* Stock 0x5571a8 (teleprompt_ui_collapse_animate): 300 ms linear height
 * animation of the text area between 0 and display_lines * 28 px. */
void teleprompt_ui_collapse_animate_5571a8(uint8_t collapse)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    if (ui->content == 0) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_collapse, 0x869u, m_collapse_skip);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_collapse_skip, s_collapse_skip);
        return;
    }
    int32_t full = (int32_t)(teleprompt_ui_visible_lines_5540f0() * TELEPROMPT_LINE_HEIGHT);
    int32_t start = collapse != 0u ? full : 0;
    int32_t end = collapse != 0u ? 0 : full;
    ui->busy = 1u;

    teleprompt_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = ui->content;
    anim.duration = 300;
    anim.path_cb = audio_uart_lv_anim_default_path_450634;
    anim.exec_cb = teleprompt_ui_height_anim_exec_cb_557104;
    anim.completed_cb = teleprompt_ui_collapse_anim_ready_cb_55718c;
    audio_uart_lv_anim_values_4506ce(&anim, start, end);
    (void)audio_uart_lv_anim_start_450408(&anim);
}

/* Stock 0x557280: title-bar clock "<elapsed> h:mm:ss". */
int32_t teleprompt_ui_action_update_elapsed_time_557280(uint8_t state, uint32_t elapsed_sec)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    (void)state;

    if (ui->title_bar == 0) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_elapsed, 0x88bu, m_title_null);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_title_null, s_title_null);
        return 0;
    }
    void *time_label = audio_uart_lv_child_get_44dce2(ui->title_bar, 0);
    if (time_label == 0) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_elapsed, 0x892u, m_time_null);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, s_time_null, s_time_null);
        return 0;
    }
    uint32_t hours = elapsed_sec / 3600u;
    uint32_t minutes = (elapsed_sec % 3600u) / 60u;
    uint32_t seconds = elapsed_sec % 60u;
    audio_lv_label_set_text_fmt_49954c(time_label, elapsed_fmt, localized(id_elapsed), hours, minutes, seconds);
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_elapsed, 0x8a1u, m_elapsed, localized(id_elapsed),
                           hours, minutes, seconds, ui->start_timestamp, elapsed_sec);
    if (log_compressed_on())
        (void)compress_log_output(0x11800000u, s_elapsed, s_elapsed, localized(id_elapsed), hours, minutes,
                                  seconds, ui->start_timestamp, elapsed_sec);
    return 0;
}
