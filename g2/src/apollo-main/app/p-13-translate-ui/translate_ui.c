/* D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate_ui.c
 * (module "translate.ui"), firmware 2.2.6.10, native 0x59d380..0x59e5c6.
 *
 * Translate app UI: a root page, a 576x288 main page holding a destination
 * (translated text) container at the bottom, a source container aligned above
 * it, and a GIF + language-pair strip; a 3-state x 10-event transition table
 * (ROM 0x6d035c) drives the actions. Context record at RAM 0x20073784.
 *
 * The TSV row 0x59d476 is not a function entry: it falls inside
 * translate_ui_create_gif_lang_pair_container_59d400 (instruction `movs r1,#7`
 * of the lv_obj_align call), so it is covered by that function.
 * 0x59d380 is IAR's out-of-line copy of LVGL's static inline
 * lv_obj_set_style_pad_all (pad left, right, top, bottom). */
#include <stddef.h>
#include <stdint.h>

/* --- logging (0x43d0ce / 0x43d574 / 0x43ce9e) ------------------------- */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

/* --- LVGL v9 wrappers (names from existing g2/src definitions) --------- */
extern void *audio_uart_page_43de82(void *parent);                          /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);              /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);              /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);        /* lv_obj_set_pos */
extern void audio_uart_page_43f142(void *obj, int32_t y);                   /* lv_obj_set_y (anim exec) */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);        /* lv_obj_set_size */
extern void audio_uart_page_43f66c(void *obj);                              /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align,
                                   int32_t x, int32_t y);                   /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                  /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                       /* lv_color_hex */
extern void audio_uart_page_4411aa(void *obj, int32_t v, uint32_t sel);     /* style height */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);     /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);     /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);     /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);     /* style pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);  /* style bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);     /* style border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);
extern void audio_uart_page_4413be(void *obj, int32_t v, uint32_t sel);
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t sel);
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* style text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* style text_font */
extern void audio_uart_page_44144c(void *obj, int32_t v, uint32_t sel);     /* style text_line_space */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel); /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* style opa */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);          /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                              /* lv_obj_clean */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);      /* lv_obj_get_child */
extern uint32_t audio_uart_page_44e368(void *obj, uint32_t mode);           /* scrollbar mode */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim);
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern int32_t audio_uart_lv_anim_path_450688(void *anim);                  /* ease-in-out path */
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern void *audio_uart_page_498668(void *parent);                          /* lv_image_create */
extern void audio_uart_page_498680(void *img, const void *src);             /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                          /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);   /* lv_label_set_text */
extern void *audio_uart_page_layout_499678(void *label, uint32_t mode);     /* lv_label_set_long_mode */

/* --- product helpers ------------------------------------------------------ */
extern uint32_t display_driver_uled_mode_45a568(void);       /* 1 = master role */
extern uint32_t audio_uart_page_460084(const char *key);     /* locale index of a text ID */
extern uint32_t audio_uart_page_45fffe(uint32_t fallback, uint32_t index); /* text lookup */
extern void system_close_page_factory_0046ae9c(uint32_t, uint32_t);
extern uint8_t audio_ux_get_system_ble_status(void);         /* 0x47d8ce UX_GetSystemBLEStatus */
extern uint32_t audio_conversate_ui_message_send_58bfb2(void *parent, const char *text,
                                                        uint32_t app_id, uint32_t animated,
                                                        uint32_t hold_ms); /* TSV: common_exit_prompt_show */
extern void audio_uart_page_58c238(void *obj, uint32_t duration, uint32_t delay); /* fade in */
extern void audio_terminal_fade_out_58c426(void *obj, uint32_t duration, uint32_t delay);
extern void *audio_conversate_pre_notes_anim_create_58c7a0(void *parent, void (*complete)(void)); /* GIF */
extern void audio_conversate_route_before_release_58c836(void *gif);  /* GIF pause */
extern uint32_t audio_conversate_route_release_58c84e(void *gif);     /* GIF resume/restart */
extern void translate_data_clear_59e9e2(void);
extern const char *translate_data_get_src_text_59ea10(void);
extern const char *translate_data_get_dst_text_59ea14(void);
extern uint32_t translate_request_display_59ec28(uint8_t event, uint32_t value);
extern uint32_t APP_PbTranslateTxEncodeNotify(void *message);         /* 0x59f71a */
extern uint32_t APP_PbTranslateTxEncodeModeSwitch(uint32_t *mode);    /* 0x59f960 */
extern uint32_t osKernelGetTickCount(void);                           /* 0x4490cc */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PCT_100 0x20000064
#define TRANSLATE_APP_ID 5u
#define TRANSLATE_UI_STATE_NUM 3u
#define TRANSLATE_UI_EVENT_NUM 10u

typedef struct {
    void *main_page;      /* +0x00 */
    void *gif_pair;       /* +0x04 GIF + language-pair strip */
    void *gif;            /* +0x08 */
    void *lang_label;     /* +0x0c */
    void *src_container;  /* +0x10 */
    void *src_label;      /* +0x14 */
    void *dst_container;  /* +0x18 */
    void *dst_label;      /* +0x1c */
    uint8_t state;        /* +0x20 0 closed, 1 running, 2 closing */
    uint8_t animating;    /* +0x21 mode-change animation in flight */
    uint32_t mode;        /* +0x24 0 = source shown, 1 = minimised */
    uint32_t text_tick;   /* +0x28 tick of last text update, 0 = none */
} translate_ui_ctx_t;
_Static_assert(sizeof(translate_ui_ctx_t) == 0x2c, "translate ui context");

/* LVGL v9 lv_anim_t (0x60 bytes); only the fields set here are named. */
typedef struct {
    void *var;                               /* +0x00 */
    void (*exec_cb)(void *, int32_t);        /* +0x04 */
    uint32_t reserved08[2];
    void (*completed_cb)(void *);            /* +0x10 */
    uint32_t reserved14[3];
    int32_t (*path_cb)(void *);              /* +0x20 */
    uint32_t reserved24[3];
    int32_t duration;                        /* +0x30 */
    uint32_t reserved34[11];
} translate_lv_anim_t;
_Static_assert(sizeof(translate_lv_anim_t) == 0x60, "lv_anim_t");

typedef int32_t (*translate_ui_action_t)(uint8_t state, uint32_t arg);
typedef struct {
    uint8_t next_state;
    translate_ui_action_t action;
} translate_ui_transition_t;
_Static_assert(sizeof(translate_ui_transition_t) == 8, "transition");

extern translate_ui_ctx_t g2_translate_ui_ctx;             /* RAM 0x20073784 */
extern void *g2_translate_root_page;                       /* RAM 0x20074afc */
extern uint32_t audio_uart_ring_primary_head_cell;         /* RAM 0x200746dc: active lv_font_t * */
extern const char *const g2_translate_ui_state_names[TRANSLATE_UI_STATE_NUM]; /* RAM 0x200041c8 */
extern const char *const g2_translate_ui_event_names[TRANSLATE_UI_EVENT_NUM]; /* RAM 0x200041d8 */
extern const uint8_t g2_translate_lang_pair_font[];        /* ROM 0x7547b8 lv_font_t */
extern char g2_translate_lang_pair_text[];                 /* RAM 0x2011df25 */
extern const uint8_t g2_translate_pause_image[];           /* ROM 0x76f438 lv_image_dsc_t */

static const char module[] = "translate.ui"; /* ROM 0x789c70 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\translate\\translate_ui.c"; /* ROM 0x6fe6fc */
static const char blank_text[] = " "; /* ROM 0x59d8ec */

static const char fn_gif_cb[] = "translate_ui_gif_animation_complete_callback"; /* ROM 0x73a3c4 */
static const char m_gif_cb[] = "gif animation complete"; /* ROM 0x77d024 */
static const char s_gif_cb[] = "[translate.ui]gif animation complete"; /* ROM 0x750464 */
static const char fn_pair[] = "translate_ui_create_gif_lang_pair_container"; /* ROM 0x745a64 */
static const char m_pair[] = "GIF and language pair container created"; /* ROM 0x75048c */
static const char s_pair[] = "[translate.ui]GIF and language pair container created"; /* ROM 0x724e68 */
static const char fn_src[] = "translate_ui_create_src_container"; /* ROM 0x75bfd0 */
static const char fn_dst[] = "translate_ui_create_dst_container"; /* ROM 0x75bff4 */
static const char m_font[] = "font_height: %d, line_space: %d"; /* ROM 0x766f90 */
static const char s_font[] = "[translate.ui]font_height: %d, line_space: %d"; /* ROM 0x73a3f4 */
static const char m_src[] = "Source container created"; /* ROM 0x773ba4 */
static const char s_src[] = "[translate.ui]Source container created"; /* ROM 0x7504b4 */
static const char m_dst[] = "Destination container created"; /* ROM 0x766fb0 */
static const char s_dst[] = "[translate.ui]Destination container created"; /* ROM 0x745a90 */
static const char fn_main[] = "translate_ui_main_page_create"; /* ROM 0x766fd0 */
static const char m_main[] = "Main page container created"; /* ROM 0x773bc0 */
static const char s_main[] = "[translate.ui]Main page container created"; /* ROM 0x745abc */
static const char fn_init[] = "translate_ui_init"; /* ROM 0x7845a4 */
static const char m_init[] = "Root page created"; /* ROM 0x7845b8 */
static const char s_init[] = "[translate.ui]Root page created"; /* ROM 0x766ff0 */
static const char fn_deinit[] = "translate_ui_deinit"; /* ROM 0x7845cc */
static const char m_deinit[] = "Translate UI deinit completed"; /* ROM 0x767010 */
static const char s_deinit[] = "[translate.ui]Translate UI deinit completed"; /* ROM 0x745ae8 */
static const char fn_page_input[] = "translate_ui_main_page_input_event_handler"; /* ROM 0x745b14 */
static const char m_no_page[] = "main_page is NULL"; /* ROM 0x7845e0 */
static const char s_no_page[] = "[translate.ui]main_page is NULL"; /* ROM 0x767030 */
static const char fn_input[] = "translate_input_event_handler"; /* ROM 0x767050 */
static const char m_not_master[] = "translate input event handler, but role is not master"; /* ROM 0x724ea0 */
static const char s_not_master[] =
    "[translate.ui]translate input event handler, but role is not master"; /* ROM 0x707718 */
static const char m_input[] = "translate input event handler, current ui state: %d, code: %d"; /* ROM 0x7109e4 */
static const char s_input[] =
    "[translate.ui]translate input event handler, current ui state: %d, code: %d"; /* ROM 0x6f6f48 */
static const char unknown_state[] = "UNKNOWN_STATE"; /* ROM 0x789c80 */
static const char unknown_event[] = "UNKNOWN_EVENT"; /* ROM 0x789c90 */
static const char fn_fsm[] = "translate_ui_fsm_handler"; /* ROM 0x773c84 */
static const char m_bad_event[] = "UI event is invalid: %d"; /* ROM 0x77d084 */
static const char s_bad_event[] = "[translate.ui]UI event is invalid: %d"; /* ROM 0x7504dc */
static const char m_event[] = "UI event [%d|%s]"; /* ROM 0x7845f4 */
static const char s_event[] = "[translate.ui]UI event [%d|%s]"; /* ROM 0x767130 */
static const char m_bad_state[] = "UI current state is invalid: %d"; /* ROM 0x767150 */
static const char s_bad_state[] = "[translate.ui]UI current state is invalid: %d"; /* ROM 0x73a424 */
static const char m_no_action[] =
    "UI current state[%d|%s] no match action for event[%d|%s]"; /* ROM 0x71a5fc */
static const char s_no_action[] =
    "[translate.ui]UI current state[%d|%s] no match action for event[%d|%s]"; /* ROM 0x6fe744 */
static const char m_transition[] = "UI state [%d|%s] -> [%d|%s]"; /* ROM 0x773ca0 */
static const char s_transition[] = "[translate.ui]UI state [%d|%s] -> [%d|%s]"; /* ROM 0x745b40 */
static const char m_failed[] = "UI transition action failed"; /* ROM 0x773cbc */
static const char s_failed[] = "[translate.ui]UI transition action failed"; /* ROM 0x745b6c */
static const char fn_gif_complete[] = "translate_ui_action_gif_complete"; /* ROM 0x75c018 */
static const char m_gif_null[] = "gif_animation is NULL, skip gif_complete action"; /* ROM 0x73a454 */
static const char s_gif_null[] =
    "[translate.ui]gif_animation is NULL, skip gif_complete action"; /* ROM 0x710a24 */
static const char fn_show_main[] = "translate_ui_action_display_main_page"; /* ROM 0x750504 */
static const char m_show_main[] = "Minimized page displayed"; /* ROM 0x773cd8 */
static const char s_show_main[] = "[translate.ui]Minimized page displayed"; /* ROM 0x75052c */
static const char fn_refresh[] = "translate_ui_text_refresh_check"; /* ROM 0x767170 */
static const char m_refresh[] = "Text refresh time out, refresh text"; /* ROM 0x75c03c */
static const char s_refresh[] = "[translate.ui]Text refresh time out, refresh text"; /* ROM 0x72f8e0 */
static const char fn_text[] = "translate_ui_action_text_update"; /* ROM 0x767190 */
static const char m_no_label[] = "src_text_label or dst_text_label is NULL"; /* ROM 0x745b98 */
static const char s_no_label[] = "[translate.ui]src_text_label or dst_text_label is NULL"; /* ROM 0x724ed8 */
static const char m_target[] = "src_target_y: %d, dst_target_y: %d"; /* ROM 0x75c060 */
static const char s_target[] = "[translate.ui]src_target_y: %d, dst_target_y: %d"; /* ROM 0x72f914 */
static const char m_text_done[] = "Text updated"; /* ROM 0x789ca0 */
static const char s_text_done[] = "[translate.ui]Text updated"; /* ROM 0x773cf4 */
static const char id_ble_disconnect[] = "ID_GENERAL_BLUETOOTH_DISCONNECT"; /* ROM 0x7671b0 */
static const char id_end_saved[] = "ID_TRANSLATE_END_SAVED"; /* ROM 0x77d09c */
static const char id_unsupported[] = "ID_TRANSLATE_UNSUPPORTED_LANGUAGE_REMINDER"; /* ROM 0x745bc4 */
static const char fn_mode_cb[] = "translate_ui_mode_change_animation_completed_cb"; /* ROM 0x73a484 */
static const char m_mode_cb[] = "Mode change animation completed"; /* ROM 0x7671d0 */
static const char s_mode_cb[] = "[translate.ui]Mode change animation completed"; /* ROM 0x73a4b4 */
static const char fn_mode[] = "translate_ui_action_mode_change"; /* ROM 0x7671f0 */
static const char m_no_container[] = "src_container or dst_container is NULL"; /* ROM 0x750554 */
static const char s_no_container[] = "[translate.ui]src_container or dst_container is NULL"; /* ROM 0x724f10 */
static const char fn_loading[] = "translate_ui_action_display_loading_page"; /* ROM 0x745bf0 */
static const char m_ble_off[] = "BLE disconnected, show exit prompt"; /* ROM 0x75c084 */
static const char s_ble_off[] = "[translate.ui]BLE disconnected, show exit prompt"; /* ROM 0x72f948 */
static const char m_notify[] = "notify app to start"; /* ROM 0x784608 */
static const char s_notify[] = "[translate.ui]notify app to start"; /* ROM 0x75c0a8 */
static const char fn_pause[] = "translate_ui_action_pause"; /* ROM 0x773d10 */
static const char m_pause_null[] = "gif_animation is NULL or invalid, skip pause action"; /* ROM 0x72f97c */
static const char s_pause_null[] =
    "[translate.ui]gif_animation is NULL or invalid, skip pause action"; /* ROM 0x70775c */
static const char fn_resume[] = "translate_ui_action_resume"; /* ROM 0x773d2c */
static const char m_resume_null[] = "gif_animation is NULL or invalid, skip resume action"; /* ROM 0x724f48 */
static const char s_resume_null[] =
    "[translate.ui]gif_animation is NULL or invalid, skip resume action"; /* ROM 0x7077a0 */

/* Stock pattern: extended log when flag bit1, compressed log when bit0 or
 * bit2 (mask = level << 26 | argument count << 22). */
#define TUI_LOG(level, line, mask, func, msg, short_msg, ...)                     \
    do {                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                       \
            audio_log_extended((level), module, path, (func), (line), (msg),      \
                               ##__VA_ARGS__);                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((mask), (short_msg), (short_msg),           \
                                      ##__VA_ARGS__);                             \
    } while (0)

static int32_t font_line_height(void)
{
    const uint8_t *font = (const uint8_t *)(uintptr_t)audio_uart_ring_primary_head_cell;
    return *(const int32_t *)(const void *)(font + 0xc);
}

void lv_obj_set_style_pad_all_59d380(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

void translate_ui_gif_animation_complete_callback_59d3b2(void)
{
    (void)translate_request_display_59ec28(9u, 0u);
    TUI_LOG(4u, 0x55u, 0x10000000u, fn_gif_cb, m_gif_cb, s_gif_cb);
}

void translate_ui_create_gif_lang_pair_container_59d400(void *parent)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;

    ctx->gif_pair = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(ctx->gif_pair, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f09a(ctx->gif_pair, 0, 166);
    audio_uart_page_44127e(ctx->gif_pair, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ctx->gif_pair, 0xffu, 0u);
    audio_uart_page_44131c(ctx->gif_pair, 0, 0u);
    lv_obj_set_style_pad_all_59d380(ctx->gif_pair, 0, 0u);
    audio_uart_page_44146a(ctx->gif_pair, 0, 0u);
    ctx->gif = audio_conversate_pre_notes_anim_create_58c7a0(
        ctx->gif_pair, translate_ui_gif_animation_complete_callback_59d3b2);
    audio_uart_page_43f4c0(ctx->gif, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(ctx->gif, 7u /* LEFT_MID */, 0, 0);
    ctx->lang_label = audio_uart_page_499416(ctx->gif_pair);
    audio_uart_page_43f4c0(ctx->lang_label, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(ctx->lang_label, ctx->gif, 20u /* OUT_RIGHT_MID */, 16, 0);
    audio_uart_page_44140e(ctx->lang_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(ctx->lang_label, g2_translate_lang_pair_font, 0u);
    (void)audio_uart_page_49942e(ctx->lang_label, g2_translate_lang_pair_text);
    TUI_LOG(4u, 0x73u, 0x10000000u, fn_pair, m_pair, s_pair);
}

/* Source (original speech) text, aligned 12 px above the destination box and
 * created fully transparent (style opa 0) until a mode change fades it in. */
void translate_ui_create_src_container_59d50c(void *parent)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    int32_t height;

    ctx->src_container = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(ctx->src_container, LV_PCT_100, LV_SIZE_CONTENT);
    audio_uart_page_4411aa(ctx->src_container, 112, 0u);
    audio_uart_page_43f6d6(ctx->src_container, ctx->dst_container, 11u /* OUT_TOP_MID */, 0, -12);
    audio_uart_page_44127e(ctx->src_container, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ctx->src_container, 0xffu, 0u);
    audio_uart_page_44131c(ctx->src_container, 0, 0u);
    lv_obj_set_style_pad_all_59d380(ctx->src_container, 0, 0u);
    audio_uart_page_44146a(ctx->src_container, 0, 0u);
    (void)audio_uart_page_44e368(ctx->src_container, 0u);
    audio_uart_page_43dfa4(ctx->src_container, 0x20u);
    audio_uart_page_43ded4(ctx->src_container, 0x80u);
    ctx->src_label = audio_uart_page_499416(ctx->src_container);
    audio_uart_page_43f4c0(ctx->src_label, LV_PCT_100, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(ctx->src_label, 5u /* BOTTOM_MID */, 0, 0);
    audio_uart_page_44140e(ctx->src_label, audio_uart_page_44104c(0x444444u), 0u);
    audio_uart_page_44143e(ctx->src_label,
                           (const void *)(uintptr_t)audio_uart_ring_primary_head_cell, 0u);
    height = font_line_height();
    audio_uart_page_44144c(ctx->src_label, 28 - height, 0u);
    TUI_LOG(4u, 0x90u, 0x10800000u, fn_src, m_font, s_font, height, 28 - height);
    audio_uart_page_44129e(ctx->src_label, 0u, 0u);
    audio_uart_page_44131c(ctx->src_label, 0, 0u);
    (void)audio_uart_page_layout_499678(ctx->src_label, 0u);
    audio_uart_page_44145a(ctx->src_label, 1u, 0u);
    (void)audio_uart_page_49942e(ctx->src_label, blank_text);
    audio_uart_display_audio_reset_441488(ctx->src_container, 0u, 0u);
    TUI_LOG(4u, 0x98u, 0x10000000u, fn_src, m_src, s_src);
}

void translate_ui_create_dst_container_59d6b6(void *parent)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    int32_t height;

    ctx->dst_container = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(ctx->dst_container, LV_PCT_100, LV_SIZE_CONTENT);
    audio_uart_page_4411aa(ctx->dst_container, 84, 0u);
    audio_uart_page_43f6b8(ctx->dst_container, 5u /* BOTTOM_MID */, 0, 0);
    audio_uart_page_44127e(ctx->dst_container, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ctx->dst_container, 0u, 0u);
    audio_uart_page_44131c(ctx->dst_container, 0, 0u);
    lv_obj_set_style_pad_all_59d380(ctx->dst_container, 0, 0u);
    audio_uart_page_44146a(ctx->dst_container, 0, 0u);
    (void)audio_uart_page_44e368(ctx->dst_container, 0u);
    audio_uart_page_43dfa4(ctx->dst_container, 0x20u);
    audio_uart_page_43ded4(ctx->dst_container, 0x80u);
    ctx->dst_label = audio_uart_page_499416(ctx->dst_container);
    audio_uart_page_43f4c0(ctx->dst_label, LV_PCT_100, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(ctx->dst_label, 5u /* BOTTOM_MID */, 0, 0);
    audio_uart_page_44140e(ctx->dst_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(ctx->dst_label,
                           (const void *)(uintptr_t)audio_uart_ring_primary_head_cell, 0u);
    height = font_line_height();
    audio_uart_page_44144c(ctx->dst_label, 28 - height, 0u);
    TUI_LOG(4u, 0xb7u, 0x10800000u, fn_dst, m_font, s_font, height, 28 - height);
    audio_uart_page_44129e(ctx->dst_label, 0u, 0u);
    audio_uart_page_44131c(ctx->dst_label, 0, 0u);
    (void)audio_uart_page_layout_499678(ctx->dst_label, 0u);
    audio_uart_page_44145a(ctx->dst_label, 1u, 0u);
    (void)audio_uart_page_49942e(ctx->dst_label, blank_text);
    TUI_LOG(4u, 0xbeu, 0x10000000u, fn_dst, m_dst, s_dst);
}

void translate_ui_main_page_create_59d850(void *parent)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;

    ctx->main_page = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(ctx->main_page, 576, 288);
    audio_uart_page_43f6b8(ctx->main_page, 2u /* TOP_MID */, 0, 0);
    audio_uart_page_44129e(ctx->main_page, 0u, 0u);
    audio_uart_page_44131c(ctx->main_page, 0, 0u);
    audio_uart_page_44146a(ctx->main_page, 0, 0u);
    lv_obj_set_style_pad_all_59d380(ctx->main_page, 0, 0u);
    audio_uart_page_43dfa4(ctx->main_page, 0x70u);
    TUI_LOG(4u, 0xceu, 0x10000000u, fn_main, m_main, s_main);
}

void translate_ui_init_59d8f0(void *parent)
{
    (void)aeabi_memset_43c0e4(&g2_translate_ui_ctx, sizeof(g2_translate_ui_ctx), 0);
    g2_translate_root_page = audio_uart_page_43de82(parent);
    audio_uart_page_43dfa4(g2_translate_root_page, 0x370u);
    audio_uart_page_43f4c0(g2_translate_root_page, 576, 288);
    audio_uart_page_43f09a(g2_translate_root_page, 0, 0);
    audio_uart_page_44127e(g2_translate_root_page, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(g2_translate_root_page, 0xffu, 0u);
    audio_uart_page_44131c(g2_translate_root_page, 0, 0u);
    audio_uart_page_44133a(g2_translate_root_page, 0, 0u);
    audio_uart_page_441378(g2_translate_root_page, 0, 0u);
    audio_uart_page_441386(g2_translate_root_page, 0, 0u);
    audio_uart_page_4413be(g2_translate_root_page, 0, 0u);
    audio_uart_page_44146a(g2_translate_root_page, 0, 0u);
    lv_obj_set_style_pad_all_59d380(g2_translate_root_page, 0, 0u);
    TUI_LOG(3u, 0xe9u, 0x0c000000u, fn_init, m_init, s_init);
}

void translate_ui_deinit_59d9d4(void)
{
    TUI_LOG(3u, 0xeeu, 0x0c000000u, fn_deinit, m_deinit, s_deinit);
    (void)aeabi_memset_43c0e4(&g2_translate_ui_ctx, sizeof(g2_translate_ui_ctx), 0);
}

/* Running-state input: code 0x48 closes the app page, code 10 requests a
 * mode change (event 1) with the current mode; the second argument is unused. */
void translate_ui_main_page_input_event_handler_59da28(uint32_t code, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;

    (void)arg;
    if (ctx->main_page == NULL) {
        TUI_LOG(1u, 0xfbu, 0x04000000u, fn_page_input, m_no_page, s_no_page);
    } else if (code == 0x48u) {
        system_close_page_factory_0046ae9c(1u, TRANSLATE_APP_ID);
    } else if (code == 10u) {
        (void)translate_request_display_59ec28(1u, ctx->mode);
    }
}

void translate_input_event_handler_59da94(uint32_t code, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;

    if (display_driver_uled_mode_45a568() != 1u) {
        TUI_LOG(4u, 0x109u, 0x10000000u, fn_input, m_not_master, s_not_master);
        return;
    }
    TUI_LOG(4u, 0x10du, 0x10800000u, fn_input, m_input, s_input,
            (uint32_t)ctx->state, code);
    if (ctx->state == 1u)
        translate_ui_main_page_input_event_handler_59da28(code, arg);
}

uint8_t translate_ui_get_state_59db5c(void)
{
    return g2_translate_ui_ctx.state;
}

const char *translate_ui_state_to_string_59db66(uint8_t state)
{
    if (state >= TRANSLATE_UI_STATE_NUM)
        return unknown_state;
    return g2_translate_ui_state_names[state];
}

const char *translate_ui_event_to_string_59db80(uint8_t event)
{
    if (event >= TRANSLATE_UI_EVENT_NUM)
        return unknown_event;
    return g2_translate_ui_event_names[event];
}

int32_t translate_ui_action_gif_complete_59de2a(uint8_t state, uint32_t arg);
int32_t translate_ui_action_display_main_page_59de88(uint8_t state, uint32_t arg);
int32_t translate_ui_action_text_update_59dfa0(uint8_t state, uint32_t arg);
int32_t translate_ui_action_exit_prompt_59e11c(uint8_t state, uint32_t arg);
int32_t translate_ui_action_exit_reminder_59e176(uint8_t state, uint32_t arg);
int32_t translate_ui_action_mode_change_59e270(uint8_t state, uint32_t arg);
int32_t translate_ui_action_display_loading_page_59e3c4(uint8_t state, uint32_t arg);
int32_t translate_ui_action_pause_59e498(uint8_t state, uint32_t arg);
int32_t translate_ui_action_resume_59e55c(uint8_t state, uint32_t arg);

/* ROM 0x6d035c: [state][event] -> {next state, action}. Empty slots are
 * {0, NULL}. State 2 has no transitions. */
static const translate_ui_transition_t translate_ui_fsm_table[TRANSLATE_UI_STATE_NUM]
                                                             [TRANSLATE_UI_EVENT_NUM] = {
    [0] = {
        [3] = {1u, translate_ui_action_display_loading_page_59e3c4},
        [4] = {1u, translate_ui_action_display_main_page_59de88},
    },
    [1] = {
        [1] = {1u, translate_ui_action_mode_change_59e270},
        [2] = {1u, translate_ui_action_text_update_59dfa0},
        [4] = {1u, translate_ui_action_display_main_page_59de88},
        [5] = {1u, translate_ui_action_pause_59e498},
        [6] = {1u, translate_ui_action_resume_59e55c},
        [7] = {2u, translate_ui_action_exit_prompt_59e11c},
        [8] = {2u, translate_ui_action_exit_reminder_59e176},
        [9] = {1u, translate_ui_action_gif_complete_59de2a},
    },
};

void translate_ui_fsm_handler_59db9a(uint8_t event, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    const translate_ui_transition_t *entry;

    if (event >= TRANSLATE_UI_EVENT_NUM) {
        TUI_LOG(1u, 0x173u, 0x04400000u, fn_fsm, m_bad_event, s_bad_event,
                (uint32_t)event);
        return;
    }
    TUI_LOG(3u, 0x177u, 0x0c800000u, fn_fsm, m_event, s_event, (uint32_t)event,
            translate_ui_event_to_string_59db80(event));
    if (ctx->state >= TRANSLATE_UI_STATE_NUM) {
        TUI_LOG(1u, 0x17bu, 0x04400000u, fn_fsm, m_bad_state, s_bad_state,
                (uint32_t)ctx->state);
        return;
    }
    entry = &translate_ui_fsm_table[ctx->state][event];
    if (entry->action == NULL) {
        TUI_LOG(2u, 0x185u, 0x09000000u, fn_fsm, m_no_action, s_no_action,
                (uint32_t)ctx->state, translate_ui_state_to_string_59db66(ctx->state),
                (uint32_t)event, translate_ui_event_to_string_59db80(event));
        return;
    }
    if (entry->action(ctx->state, arg) != 0) {
        TUI_LOG(1u, 0x195u, 0x04000000u, fn_fsm, m_failed, s_failed);
        return;
    }
    if (ctx->state != entry->next_state)
        TUI_LOG(3u, 0x191u, 0x0d000000u, fn_fsm, m_transition, s_transition,
                (uint32_t)ctx->state, translate_ui_state_to_string_59db66(ctx->state),
                (uint32_t)entry->next_state,
                translate_ui_state_to_string_59db66(entry->next_state));
    ctx->state = entry->next_state;
}

int32_t translate_ui_action_gif_complete_59de2a(uint8_t state, uint32_t arg)
{
    (void)state;
    (void)arg;
    if (g2_translate_ui_ctx.gif == NULL) {
        TUI_LOG(2u, 0x1a5u, 0x08000000u, fn_gif_complete, m_gif_null, s_gif_null);
        return 0;
    }
    (void)audio_conversate_route_release_58c84e(g2_translate_ui_ctx.gif);
    return 0;
}

/* Rebuilds the running page: destination box first (the source box aligns
 * to it), then source, then the GIF / language-pair strip. */
int32_t translate_ui_action_display_main_page_59de88(uint8_t state, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;

    (void)state;
    (void)arg;
    audio_uart_page_44d878(g2_translate_root_page);
    translate_ui_main_page_create_59d850(g2_translate_root_page);
    translate_ui_create_dst_container_59d6b6(ctx->main_page);
    translate_ui_create_src_container_59d50c(ctx->main_page);
    translate_ui_create_gif_lang_pair_container_59d400(ctx->main_page);
    TUI_LOG(4u, 0x1c2u, 0x10000000u, fn_show_main, m_show_main, s_show_main);
    return 0;
}

/* Periodic check: more than 10000 ticks without a text update requests a
 * display refresh (event 2, value 1), which clears the stored text. */
void translate_ui_text_refresh_check_59df04(void)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;

    if (display_driver_uled_mode_45a568() != 1u || ctx->text_tick == 0u)
        return;
    if (osKernelGetTickCount() - ctx->text_tick < 10001u)
        return;
    TUI_LOG(2u, 0x1cfu, 0x08000000u, fn_refresh, m_refresh, s_refresh);
    (void)translate_request_display_59ec28(2u, 1u);
    ctx->text_tick = 0u;
}

int32_t translate_ui_action_text_update_59dfa0(uint8_t state, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    const char *src_text;
    const char *dst_text;
    int32_t src_target_y;
    int32_t dst_target_y;

    (void)state;
    if (arg == 1u)
        translate_data_clear_59e9e2();
    else
        ctx->text_tick = osKernelGetTickCount();
    src_text = translate_data_get_src_text_59ea10();
    dst_text = translate_data_get_dst_text_59ea14();
    if (ctx->src_label == NULL || ctx->dst_label == NULL) {
        TUI_LOG(2u, 0x1e6u, 0x08000000u, fn_text, m_no_label, s_no_label);
        return -1;
    }
    (void)audio_uart_page_49942e(ctx->src_label, src_text);
    (void)audio_uart_page_49942e(ctx->dst_label, dst_text);
    audio_uart_page_43f66c(ctx->dst_container);
    audio_uart_page_43f6d6(ctx->src_container, ctx->dst_container, 11u, 0, -12);
    src_target_y = audio_uart_lv_obj_height_43fdda(ctx->src_label) -
                   audio_uart_lv_obj_height_43fdda(ctx->src_container);
    dst_target_y = audio_uart_lv_obj_height_43fdda(ctx->dst_label) -
                   audio_uart_lv_obj_height_43fdda(ctx->dst_container);
    TUI_LOG(4u, 0x1f8u, 0x10800000u, fn_text, m_target, s_target, src_target_y,
            dst_target_y);
    audio_uart_lv_scroll_to_y_44ea04(ctx->src_container, src_target_y, 0u);
    audio_uart_lv_scroll_to_y_44ea04(ctx->dst_container, dst_target_y, 0u);
    TUI_LOG(4u, 0x1fdu, 0x10000000u, fn_text, m_text_done, s_text_done);
    return 0;
}

static const char *translate_ui_text(const char *id)
{
    return (const char *)(uintptr_t)audio_uart_page_45fffe((uint32_t)(uintptr_t)id,
                                                          audio_uart_page_460084(id));
}

/* Event 7 (to state 2): arg 1 = BLE dropped (5 s prompt), otherwise
 * "translation saved". */
int32_t translate_ui_action_exit_prompt_59e11c(uint8_t state, uint32_t arg)
{
    (void)state;
    if (arg == 1u)
        (void)audio_conversate_ui_message_send_58bfb2(
            g2_translate_root_page, translate_ui_text(id_ble_disconnect), TRANSLATE_APP_ID, 0u, 5000u);
    else
        (void)audio_conversate_ui_message_send_58bfb2(
            g2_translate_root_page, translate_ui_text(id_end_saved), TRANSLATE_APP_ID, 0u, 0u);
    return 0;
}

/* Event 8 (to state 2): arg 1 = unsupported language (5 s), otherwise
 * "translation saved" with the animated flag set. */
int32_t translate_ui_action_exit_reminder_59e176(uint8_t state, uint32_t arg)
{
    (void)state;
    if (arg == 1u)
        (void)audio_conversate_ui_message_send_58bfb2(
            g2_translate_root_page, translate_ui_text(id_unsupported), TRANSLATE_APP_ID, 0u, 5000u);
    else
        (void)audio_conversate_ui_message_send_58bfb2(
            g2_translate_root_page, translate_ui_text(id_end_saved), TRANSLATE_APP_ID, 1u, 0u);
    return 0;
}

void translate_ui_notify_mode_switch_59e1d0(void)
{
    uint32_t mode;

    if (display_driver_uled_mode_45a568() == 1u) {
        mode = g2_translate_ui_ctx.mode;
        (void)APP_PbTranslateTxEncodeModeSwitch(&mode);
    }
}

void translate_ui_mode_change_animation_completed_cb_59e1ea(void *anim)
{
    (void)anim;
    g2_translate_ui_ctx.animating = 0u;
    translate_ui_notify_mode_switch_59e1d0();
    TUI_LOG(4u, 0x233u, 0x10000000u, fn_mode_cb, m_mode_cb, s_mode_cb);
}

/* Animation exec callback: keeps the source box aligned above the
 * destination box at vertical offset `value`. */
void translate_ui_src_anim_exec_59e248(void *obj, int32_t value)
{
    audio_uart_page_43f6d6(obj, g2_translate_ui_ctx.dst_container, 11u, 0, value);
}

/* arg 1: minimise (mode 0): fade the source out, destination height 84,
 * strip y 0 -> 166, source offset -12 -> 0. Otherwise expand (mode 1): fade
 * in, height 112, strip 166 -> 0, offset 0 -> -12. 300 ms ease-in-out. */
int32_t translate_ui_action_mode_change_59e270(uint8_t state, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    translate_lv_anim_t src_anim;
    translate_lv_anim_t pair_anim;

    (void)state;
    if (ctx->src_container == NULL || ctx->dst_container == NULL) {
        TUI_LOG(2u, 0x244u, 0x08000000u, fn_mode, m_no_container, s_no_container);
        return -1;
    }
    ctx->animating = 1u;
    audio_uart_lv_anim_init_4503d6(&pair_anim);
    pair_anim.var = ctx->gif_pair;
    pair_anim.duration = 300;
    pair_anim.path_cb = audio_uart_lv_anim_path_450688;
    pair_anim.exec_cb = (void (*)(void *, int32_t))audio_uart_page_43f142;
    pair_anim.completed_cb = translate_ui_mode_change_animation_completed_cb_59e1ea;
    audio_uart_lv_anim_init_4503d6(&src_anim);
    src_anim.var = ctx->src_container;
    src_anim.duration = 300;
    src_anim.path_cb = audio_uart_lv_anim_path_450688;
    src_anim.exec_cb = translate_ui_src_anim_exec_59e248;
    if (arg == 1u) {
        ctx->mode = 0u;
        audio_terminal_fade_out_58c426(ctx->src_container, 300u, 0u);
        audio_uart_page_4411aa(ctx->dst_container, 84, 0u);
        audio_uart_lv_anim_values_4506ce(&pair_anim, 0, 166);
        audio_uart_lv_anim_values_4506ce(&src_anim, -12, 0);
    } else {
        ctx->mode = 1u;
        audio_uart_page_58c238(ctx->src_container, 300u, 0u);
        audio_uart_page_4411aa(ctx->dst_container, 112, 0u);
        audio_uart_lv_anim_values_4506ce(&pair_anim, 166, 0);
        audio_uart_lv_anim_values_4506ce(&src_anim, 0, -12);
    }
    (void)audio_uart_lv_anim_start_450408(&pair_anim);
    (void)audio_uart_lv_anim_start_450408(&src_anim);
    return 0;
}

int32_t translate_ui_action_display_loading_page_59e3c4(uint8_t state, uint32_t arg)
{
    /* Stack copy of the ROM initializer at 0x78f6c4 (bytes 01 00). */
    uint8_t notify[2] = {1u, 0u};

    (void)state;
    (void)arg;
    if (audio_ux_get_system_ble_status() == 0u) {
        TUI_LOG(1u, 0x275u, 0x04000000u, fn_loading, m_ble_off, s_ble_off);
        (void)audio_conversate_ui_message_send_58bfb2(
            g2_translate_root_page, translate_ui_text(id_ble_disconnect), TRANSLATE_APP_ID, 0u, 5000u);
        return -1;
    }
    TUI_LOG(3u, 0x27eu, 0x0c000000u, fn_loading, m_notify, s_notify);
    (void)APP_PbTranslateTxEncodeNotify(notify);
    return 0;
}

/* Pause: stop and hide the GIF and, once, add a pause icon as child 2 of the
 * strip. */
int32_t translate_ui_action_pause_59e498(uint8_t state, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    void *icon;

    (void)state;
    (void)arg;
    if (ctx->gif == NULL) {
        TUI_LOG(2u, 0x28au, 0x08000000u, fn_pause, m_pause_null, s_pause_null);
        return 0;
    }
    audio_conversate_route_before_release_58c836(ctx->gif);
    audio_uart_page_43ded4(ctx->gif, 1u /* HIDDEN */);
    if (audio_uart_lv_child_get_44dce2(ctx->gif_pair, 2) == NULL) {
        icon = audio_uart_page_498668(ctx->gif_pair);
        audio_uart_page_498680(icon, g2_translate_pause_image);
        audio_uart_page_44127e(icon, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(icon, 0xffu, 0u);
        audio_uart_page_4413ce(icon, 0xffu, 0u);
        audio_uart_page_43f4c0(icon, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        audio_uart_page_43f6b8(icon, 7u /* LEFT_MID */, 0, 0);
    }
    return 0;
}

int32_t translate_ui_action_resume_59e55c(uint8_t state, uint32_t arg)
{
    translate_ui_ctx_t *ctx = &g2_translate_ui_ctx;
    void *icon;

    (void)state;
    (void)arg;
    if (ctx->gif == NULL) {
        TUI_LOG(2u, 0x2a7u, 0x08000000u, fn_resume, m_resume_null, s_resume_null);
        return 0;
    }
    (void)audio_conversate_route_release_58c84e(ctx->gif);
    audio_uart_page_43dfa4(ctx->gif, 1u /* HIDDEN */);
    icon = audio_uart_lv_child_get_44dce2(ctx->gif_pair, 2);
    if (icon != NULL)
        audio_uart_page_delete_event_filter_44d7b8(icon);
    return 0;
}
