/* EvenAI page: answer dialogs, dialog pool/list, reflash state machine and
 * page lifecycle, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\ui_even_ai.c
 * (log tag "even_ai.ui"). Native 0x4e6560..0x4e6ade, 0x4e6aec..0x4e6c15,
 * 0x4e6c44..0x4e7161 (4-byte inline "" literal at 0x4e6fd0), 0x4e7170..0x4e74c1,
 * 0x4e74cc..0x4e74f9; literal pools 0x4e69e0, 0x4e6a70..0x4e6a7f,
 * 0x4e6c18..0x4e6c43 (0x4e6c20 is an inline ""), 0x4e7164..0x4e716f,
 * 0x4e74c4..0x4e74cb, 0x4e74fc..0x4e75af.
 *
 * Shares the private layouts of the a-29 reconstruction of the same stock
 * file (dialog list at RAM 0x200739fc, 0x24-byte dialog nodes).
 *
 * Service state (RAM 0x2006f138) as read here: +0 mode (1 wake, 3 ask,
 * 4 analyse, 5 reply, 6 result, 7 error), +1 sub mode / error code,
 * +4 u32 progress value, +9 1 = keep the phase animation on finish,
 * +0x0a 1 = direct display (no text streaming), +0x0e u16 text length,
 * +0x10 text bytes. LVGL 9.3 fork: 0x44146a radius, 0x44145a text_align,
 * 0x4412ec border_color, 0x4411aa max_height, align ids 1 TOP_LEFT,
 * 2 TOP_MID, 4 BOTTOM_LEFT, 5 BOTTOM_MID, 20 OUT_RIGHT_MID. Page words: +0 content
 * column, +4 bordered frame. */
#include <stdint.h>
#include <stddef.h>
#include "../a-29-even-ai-ui/ui_even_ai_internal.h"

#define EVEN_AI_POOL_SIZE 5u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PART_INDICATOR 0x20000u
#define LV_OBJ_FLAG_HIDDEN 1u
#define TEXT_BUF_LEN 0x201u

/* Service mode byte +0 of the service state. */
enum {
    EVEN_AI_MODE_WAKE = 1u,
    EVEN_AI_MODE_ASK = 3u,
    EVEN_AI_MODE_ANALYSE = 4u,
    EVEN_AI_MODE_REPLY = 5u,
    EVEN_AI_MODE_RESULT = 6u,
    EVEN_AI_MODE_ERROR = 7u,
};

/* Phase ids of the EvenAI animation module (0x5537cc). */
enum {
    EVEN_AI_PHASE_LISTEN = 0u,
    EVEN_AI_PHASE_ASK = 1u,
    EVEN_AI_PHASE_ANALYSE = 2u,
    EVEN_AI_PHASE_REPLY = 3u,
};

extern g2_even_ai_dialog_node_t g2_even_ai_dialog_pool[EVEN_AI_POOL_SIZE]; /* RAM 0x20120254 */
extern uint8_t audio_even_ai_ready_state_2006f138[0x218];   /* RAM 0x2006f138 service state */
extern uint32_t audio_even_ai_text_stream_handle_20074c04;  /* RAM 0x20074c04 */
extern g2_even_ai_dialog_node_t *g2_even_ai_current_streaming_node; /* RAM 0x20074c08 */
extern uint8_t g2_even_ai_stream_flag;                      /* RAM 0x2007503b 1 question, 0 answer */
extern uint32_t audio_system_alert_font_200746e0;           /* RAM 0x200746e0 lv_font_t * */

/* 24x24 lv_image_dsc_t icons in ROM. */
extern const uint8_t audio_system_alert_icon_disconnect_7747e4[]; /* generic error icon */
extern const uint8_t g2_even_ai_icon_769e40[];              /* bluetooth disconnected */
extern const uint8_t g2_even_ai_icon_769f20[];              /* result with progress bar */
extern const uint8_t g2_onboarding_status_img_76e7f8[];     /* result sub mode 3 */
extern const uint8_t g2_even_ai_icon_769d7c[];              /* result sub mode 8 */

/* ui_even_ai.c functions owned by the a-29 files. */
extern uint32_t even_ai_layout_cache_changed(void);         /* 0x4e5e92 */
extern void even_ai_layout_cache_update(void);              /* 0x4e5f20 */
extern void even_ai_node_stream_state_update(g2_even_ai_dialog_node_t *node); /* 0x4e6088 */
extern void even_ai_listening_visibility_set(uint8_t delete_objs); /* 0x4e61b4 */
extern void even_ai_hide_listening_text(void);              /* 0x4e6254 */
extern void even_ai_listening_text_toggle(void);            /* 0x4e62c0 */
extern uint32_t even_ai_add_question(const char *text, uint8_t new_dialog); /* 0x4e62ce */
extern void even_ai_gray_question(uint8_t index);           /* 0x4e64b4 */
extern void even_ai_deinit_text_stream_service(void);       /* 0x4e55f8 */
extern void even_ai_stream_init_from_service(uint8_t question); /* 0x4e5678 */
extern void even_ai_stream_on_auto_reflash(void);           /* 0x4e571a */
extern void even_ai_input_event_callback(void *e);          /* 0x4e5d16 */

/* Defined in this file (also called from the a-29 files). */
uint32_t even_ai_add_answer(const char *text, const void *icon, uint8_t bar_value,
                            uint8_t new_dialog, uint8_t compact);
void even_ai_relayout_dialogs(void);
g2_even_ai_dialog_node_t *even_ai_create_dialog_node(void);
void even_ai_dialog_node_apply(g2_even_ai_dialog_node_t *node, uint8_t delete_objs);
void even_ai_dialog_index_set(g2_even_ai_dialog_node_t *node);
void even_ai_dialogs_refresh(void);
g2_even_ai_dialog_node_t *even_ai_dialog_get(uint8_t index);
void even_ai_answer_text_reflash(void);
void even_ai_ui_reflash(void *page);
void even_ai_page_init(void *page);
void even_ai_page_deinit(void);

/* EvenAI animation module (g2-even-ai-animation). */
extern int32_t even_ai_animation_show_phase_5537cc(uint8_t phase);
extern void even_ai_animation_hide_all_55389a(void);
extern uint8_t even_ai_animation_phase_get_553d28(void);    /* 0 when not running */
extern int32_t text_stream_animation_presets_init(void *parent, uint8_t mode); /* 0x55344e, 0 ok */
extern void *text_stream_animation_preset_get(uint8_t index);  /* 0x553794 */

extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern const char *audio_text_stream_pending_text_552ce8(uint32_t stream); /* text_stream_pending_text */
extern void service_even_ai_fn_00498310(uint8_t value);
extern void *ui_common_api_fn_00509c1c(void);               /* byte FIFO create */
extern void ui_common_api_fn_00509c96(void *fifo);          /* byte FIFO destroy */
extern uint8_t audio_uart_device_role_get(void);            /* 0x45a568 */
extern uint32_t audio_uart_page_460084(const char *key);    /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern uint32_t g2_log_module_length(const char *text);     /* strlen 0x44a43c */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */

/* LVGL 9.3 fork. */
extern void *audio_uart_page_43de82(void *parent);                        /* lv_obj_create */
extern void audio_lv_delete_44d7b8(void *obj);                            /* lv_obj_delete */
extern void audio_lv_width_43f506(void *obj, int32_t width);              /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);            /* lv_obj_set_height */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);      /* lv_obj_set_size */
extern void audio_lv_object_position_43f09a(void *obj, int32_t x, int32_t y); /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                 /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                 /* lv_obj_set_y */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                            /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                /* lv_obj_get_height */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                     /* lv_obj_get_scroll_y */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);        /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag);  /* lv_obj_remove_flag */
extern uint32_t audio_uart_page_44e368(void *obj, uint32_t mode);         /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);              /* lv_obj_set_scroll_dir */
extern void *audio_uart_page_451740(void *obj, void (*cb)(void *), uint32_t filter,
                                    void *user_data);                     /* lv_obj_add_event_cb */
extern void audio_uart_page_invalidate_440656(void *obj);                 /* lv_obj_invalidate */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);                      /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);   /* border_width */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);   /* radius */
extern void audio_uart_page_4411aa(void *obj, int32_t v, uint32_t sel);   /* max_height */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);   /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);   /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);   /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);   /* pad_right */
extern void audio_lv_style_color_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_lv_style_font_44143e(void *obj, uint32_t font, uint32_t sel);   /* text_font */
extern void audio_lv_style_a_44145a(void *obj, uint32_t value, uint32_t sel);     /* text_align */
extern void *audio_lv_label_create_499416(void *parent);                  /* lv_label_create */
extern void *audio_lv_image_create_498668(void *parent);                  /* lv_image_create */
extern void audio_lv_image_source_498680(void *img, const void *src);     /* lv_image_set_src */
extern void *lv_bar_create_55751e(void *parent);
extern void lv_bar_set_range_557630(void *bar, int32_t min, int32_t max);
extern void lv_bar_set_value_557536(void *bar, int32_t value, uint32_t anim);

static const char module_tag[] = "even_ai.ui"; /* ROM 0x78c824 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\ui_even_ai.c"; /* ROM 0x710f64 */
static const char empty_text[] = ""; /* ROM 0x4e6c20 / 0x4e6fd0 inline literals */

static const char add_answer_fn[] = "even_ai_add_answer"; /* ROM 0x7847d4 */
static const char create_failed[] = "create_dialog_node failed"; /* ROM 0x773ed0 */
static const char create_failed_short[] = "[even_ai.ui]create_dialog_node failed"; /* ROM 0x750784 */
static const char create_node_fn[] = "even_ai_create_dialog_node"; /* ROM 0x773eec */
static const char pool_exhausted[] = "failed to allocate dialog node: pool exhausted"; /* ROM 0x73a784 */
static const char pool_exhausted_short[] =
    "[even_ai.ui]failed to allocate dialog node: pool exhausted"; /* ROM 0x71a8cc */
static const char answer_reflash_fn[] = "even_ai_answer_text_reflash"; /* ROM 0x773f08 */
static const char reply_stream[] =
    "Even AI REPLY: using streaming mode via DISPLAY_AUTO_REFLASH"; /* ROM 0x710fe4 */
static const char reply_stream_short[] =
    "[even_ai.ui]Even AI REPLY: using streaming mode via DISPLAY_AUTO_REFLASH"; /* ROM 0x6f7324 */
static const char reply_direct[] = "Even AI REPLY: using direct display mode"; /* ROM 0x745e84 */
static const char reply_direct_short[] =
    "[even_ai.ui]Even AI REPLY: using direct display mode"; /* ROM 0x7253e0 */
static const char ui_reflash_fn[] = "even_ai_ui_reflash"; /* ROM 0x7847e8 */
static const char wake_up[] = "Even AI wake up, showing listening text"; /* ROM 0x7507ac */
static const char wake_up_short[] =
    "[even_ai.ui]Even AI wake up, showing listening text"; /* ROM 0x72fd24 */
static const char ask_stream[] =
    "Even AI ASK: using streaming mode via DISPLAY_AUTO_REFLASH"; /* ROM 0x71a908 */
static const char ask_stream_short[] =
    "[even_ai.ui]Even AI ASK: using streaming mode via DISPLAY_AUTO_REFLASH"; /* ROM 0x6feaa4 */
static const char ask_direct[] = "Even AI ASK: using direct display mode"; /* ROM 0x7507d4 */
static const char ask_direct_short[] =
    "[even_ai.ui]Even AI ASK: using direct display mode"; /* ROM 0x72fd58 */
static const char analyse_none[] = "Even AI analyse: no dialog to gray"; /* ROM 0x75c378 */
static const char analyse_none_short[] =
    "[even_ai.ui]Even AI analyse: no dialog to gray"; /* ROM 0x73a7b4 */
static const char page_init_fn[] = "even_ai_page_init"; /* ROM 0x7847fc */
static const char anim_init_failed[] = "Failed to initialize EvenAI animation module"; /* ROM 0x73a7e4 */
static const char anim_init_failed_short[] =
    "[even_ai.ui]Failed to initialize EvenAI animation module"; /* ROM 0x71a944 */

static const char id_network_error[] = "ID_EVEN_AI_NETWORK_ERROR"; /* ROM 0x773f24 */
static const char id_bluetooth_disconnected[] = "ID_EVEN_AI_BLUETOOTH_DISCONNECTED"; /* ROM 0x75c39c */
static const char id_server_error[] = "ID_EVEN_AI_SERVER_ERROR"; /* ROM 0x77d27c */
static const char id_having_trouble[] = "ID_EVEN_AI_HAVING_TROUBLE_UNDERSTANDING"; /* ROM 0x7507fc */
static const char id_currently_unsupported[] = "ID_EVEN_AI_CURRENTLY_UNSUPPORTED"; /* ROM 0x75c3c0 */
static const char id_audio_error[] = "ID_EVEN_AI_AUDIO_ERROR"; /* ROM 0x77d294 */
static const char id_asr_server_error[] = "ID_EVEN_AI_ASR_SERVER_ERROR"; /* ROM 0x773f40 */
static const char id_ai_server_error[] = "ID_EVEN_AI_AI_SERVER_ERROR"; /* ROM 0x773f5c */
static const char id_command_failed[] = "ID_EVEN_AI_COMMAND_EXECUTION_FAILED"; /* ROM 0x75c3e4 */
static const char id_listening[] = "ID_EVEN_AI_LISTENING"; /* ROM 0x77d2ac */
static const char unknown_error[] = "Unknown Error"; /* ROM 0x789d30 */

#define EVEN_AI_LOG(level, func, line, cflags, text, short_text)                              \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), module_tag, source_file, (func), (line), (text));     \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text));                  \
    } while (0)

#define SERVICE_STATE audio_even_ai_ready_state_2006f138
#define SERVICE_MODE (SERVICE_STATE[0])
#define SERVICE_SUB (SERVICE_STATE[1])
#define SERVICE_VALUE (*(const uint32_t *)(const void *)&SERVICE_STATE[4])
#define SERVICE_KEEP_PHASE (SERVICE_STATE[9])
#define SERVICE_DIRECT (SERVICE_STATE[10])
#define SERVICE_TEXT_LEN (*(const uint16_t *)(const void *)&SERVICE_STATE[0x0e])
#define SERVICE_TEXT (&SERVICE_STATE[0x10])

#define TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))

static int obj_ok(void *obj)
{
    return obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) != 0u;
}

/* Answer text, optionally prefixed by a 32x32 icon and a 200x4 progress bar
 * (bar_value 0xff: no bar). Without new_dialog the text replaces the newest
 * answer label when one exists; otherwise the answer is attached to the newest
 * dialog when that still has only a question, or a new dialog is created
 * (dropping the oldest when five exist). compact moves the label next to the
 * icon. Returns 1 when a new answer was built or the node allocation failed,
 * 0 when text is NULL or an existing label was updated. */
uint32_t even_ai_add_answer(const char *text, const void *icon, uint8_t bar_value,
                            uint8_t new_dialog, uint8_t compact)
{
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
    g2_even_ai_dialog_node_t *node;

    if (text == NULL)
        return 0u;
    uint8_t empty = g2_log_module_length(text) == 0u ? 1u : 0u;

    node = d->tail;
    if (d->count != 0u && new_dialog == 0u && node != NULL && obj_ok(node->answer_obj) &&
        obj_ok(node->answer_label)) {
        if (empty == 0u) {
            audio_lv_label_text_49942e(node->answer_label, text);
            even_ai_node_stream_state_init(node, 0u, (uint16_t)g2_log_module_length(text));
            if (d->total_chars > EVEN_AI_CHAR_WINDOW)
                even_ai_manage_char_window();
        }
        return 0u;
    }

    node = d->tail;
    if (d->count == 0u || node == NULL || !obj_ok(node->question_label) ||
        node->answer_obj != NULL || audio_terminal_ui_object_valid_43e2ea(node->answer_obj) != 0u) {
        if (d->count >= EVEN_AI_POOL_SIZE) {
            even_ai_dialogs_refresh();
            even_ai_layout_cache_invalidate();
        }
        node = even_ai_create_dialog_node();
        if (node == NULL) {
            EVEN_AI_LOG(1u, add_answer_fn, 0x68du, 0x04000000u, create_failed, create_failed_short);
            return 1u;
        }
        even_ai_dialog_index_set(node);
        d->count++;
    }

    void *cont = audio_uart_page_43de82(d->dialog_cont);
    audio_lv_width_43f506(cont, 523);
    audio_uart_page_43f568(cont, LV_SIZE_CONTENT);
    audio_uart_page_44131c(cont, 0, 0u);
    even_ai_style_apply(cont, 0, 0u);
    audio_uart_page_44129e(cont, 0u, 0u);
    audio_lv_object_position_43f09a(cont, 0, 0);

    if (icon != NULL) {
        void *img = audio_lv_image_create_498668(cont);
        audio_lv_image_source_498680(img, icon);
        audio_uart_page_43f4c0(img, 32, 32);
        even_ai_style_apply(img, 4, 0u);
        audio_lv_object_position_43f09a(img, 0, 0);
        node->answer_extra0 = img;
        if (bar_value != 0xffu) {
            void *bar = lv_bar_create_55751e(cont);
            audio_uart_page_43f4c0(bar, 200, 4);
            audio_uart_page_43f6d6(bar, img, 20u /* LV_ALIGN_OUT_RIGHT_MID */, 8, 0);
            lv_bar_set_range_557630(bar, 0, 100);
            audio_uart_page_44127e(bar, audio_lv_color_44104c(0x222222u), 0u);
            audio_uart_page_44129e(bar, 0xffu, 0u);
            audio_uart_page_44131c(bar, 0, 0u);
            audio_uart_page_44146a(bar, 0, 0u);
            even_ai_style_apply(bar, 0, 0u);
            audio_uart_page_44127e(bar, audio_lv_color_44104c(0xffffffu), LV_PART_INDICATOR);
            audio_uart_page_44129e(bar, 0xffu, LV_PART_INDICATOR);
            audio_uart_page_44146a(bar, 0, LV_PART_INDICATOR);
            lv_bar_set_value_557536(bar, bar_value, 0u);
            audio_uart_page_invalidate_440656(bar);
            node->answer_extra1 = bar;
        } else {
            node->answer_extra1 = NULL;
        }
    } else {
        node->answer_extra0 = NULL;
        node->answer_extra1 = NULL;
    }

    void *label = audio_lv_label_create_499416(cont);
    audio_uart_page_44131c(label, 0, 0u);
    even_ai_style_apply(label, 0, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(0xffffffu), 0u);
    audio_lv_style_font_44143e(label, audio_system_alert_font_200746e0, 0u);
    audio_lv_style_a_44145a(label, 1u /* LV_TEXT_ALIGN_LEFT */, 0u);
    if (empty == 0u) {
        audio_lv_label_text_49942e(label, text);
        even_ai_node_stream_state_init(node, 0u, (uint16_t)g2_log_module_length(text));
        if (d->total_chars > EVEN_AI_CHAR_WINDOW)
            even_ai_manage_char_window();
    }
    if (icon != NULL && compact == 1u) {
        audio_lv_width_43f506(label, 487);
        audio_lv_object_position_43f09a(label, 36, 0);
    } else {
        audio_lv_width_43f506(label, 523);
        if (icon != NULL)
            audio_lv_object_position_43f09a(label, 0, 40);
        else
            audio_lv_object_position_43f09a(label, 0, 0);
    }
    node->answer_label = label;
    node->answer_obj = cont;
    return 1u;
}

/* Stack the dialogs vertically (8 px question->answer, 16 px between dialogs)
 * and keep the container scrolled to the bottom; skipped while the cached
 * heights of the newest dialog are unchanged. */
void even_ai_relayout_dialogs(void)
{
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;

    if (even_ai_layout_cache_changed() == 0u)
        return;
    int32_t y = 0;
    int32_t i = 0;
    for (g2_even_ai_dialog_node_t *n = d->head; n != NULL; n = n->next) {
        if (obj_ok(n->question_label)) {
            audio_lv_object_position_43f09a(n->question_label, 0, y);
            y = audio_uart_lv_obj_height_43fdda(n->question_label) + y;
        }
        if (obj_ok(n->answer_obj)) {
            if (obj_ok(n->question_label))
                y += 8;
            audio_lv_object_position_43f09a(n->answer_obj, 0, y);
            y = audio_uart_lv_obj_height_43fdda(n->answer_obj) + y;
        }
        i++;
        if (i < (int32_t)d->count)
            y += 16;
    }
    int32_t view = audio_uart_lv_obj_height_43fdda(d->dialog_cont);
    int32_t scroll = audio_uart_lv_obj_y_44e498(d->dialog_cont);
    y -= view;
    if (y >= 1) {
        if (y != scroll)
            even_ai_scroll_to(d->dialog_cont, y, 0u);
    } else if (scroll != 0) {
        even_ai_scroll_to(d->dialog_cont, 0, 0u);
    }
    even_ai_layout_cache_update();
}

/* Take the first free slot of the five-node pool, zeroed and marked busy. */
g2_even_ai_dialog_node_t *even_ai_create_dialog_node(void)
{
    for (uint8_t i = 0u; i < EVEN_AI_POOL_SIZE; i++) {
        if (g2_even_ai_dialog_pool[i].in_use == 0u) {
            g2_even_ai_dialog_node_t *node = &g2_even_ai_dialog_pool[i];
            aeabi_memset_43c0e4(node, sizeof(*node), 0);
            node->in_use = 1u;
            node->next = NULL;
            return node;
        }
    }
    EVEN_AI_LOG(1u, create_node_fn, 0x741u, 0x04000000u, pool_exhausted, pool_exhausted_short);
    return NULL;
}

/* Release a node: account its characters, optionally delete its LVGL objects,
 * and clear the slot (in_use = 0). */
void even_ai_dialog_node_apply(g2_even_ai_dialog_node_t *node, uint8_t delete_objs)
{
    if (node == NULL)
        return;
    even_ai_node_stream_state_update(node);
    if (node->question_label != NULL) {
        if (delete_objs != 0u && audio_terminal_ui_object_valid_43e2ea(node->question_label) != 0u)
            audio_lv_delete_44d7b8(node->question_label);
        node->question_label = NULL;
    }
    if (node->answer_obj != NULL) {
        if (delete_objs != 0u && audio_terminal_ui_object_valid_43e2ea(node->answer_obj) != 0u)
            audio_lv_delete_44d7b8(node->answer_obj);
        node->answer_obj = NULL;
        node->answer_label = NULL;
        node->answer_extra0 = NULL;
        node->answer_extra1 = NULL;
    }
    aeabi_memset_43c0e4(node, sizeof(*node), 0);
}

/* Append a node at the tail of the dialog list. */
void even_ai_dialog_index_set(g2_even_ai_dialog_node_t *node)
{
    if (node == NULL)
        return;
    node->next = NULL;
    if (g2_even_ai_dialogs.head == NULL) {
        g2_even_ai_dialogs.head = node;
        g2_even_ai_dialogs.tail = node;
    } else {
        g2_even_ai_dialogs.tail->next = node;
        g2_even_ai_dialogs.tail = node;
    }
}

/* Drop the oldest dialog (head) and delete its objects. */
void even_ai_dialogs_refresh(void)
{
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;

    if (d->head == NULL)
        return;
    g2_even_ai_dialog_node_t *old = d->head;
    d->head = old->next;
    if (d->head == NULL)
        d->tail = NULL;
    even_ai_dialog_node_apply(old, 1u);
    d->count--;
}

g2_even_ai_dialog_node_t *even_ai_dialog_get(uint8_t index)
{
    if (index >= g2_even_ai_dialogs.count)
        return NULL;
    g2_even_ai_dialog_node_t *node = g2_even_ai_dialogs.head;
    for (uint8_t i = 0u; node != NULL && i < index; i++)
        node = node->next;
    return node;
}

/* Reply text: either shown at once from the text stream (direct mode) or an
 * empty answer is created and filled by the streaming service. */
void even_ai_answer_text_reflash(void)
{
    char text[TEXT_BUF_LEN + 3u];

    if (SERVICE_TEXT_LEN == 0u)
        return;
    aeabi_memset_43c0e4(text, TEXT_BUF_LEN, 0);
    audio_queue_copy_bytes(text, SERVICE_TEXT, SERVICE_TEXT_LEN);
    if (SERVICE_DIRECT != 0u) {
        EVEN_AI_LOG(3u, answer_reflash_fn, 0x7e8u, 0x0c000000u, reply_direct, reply_direct_short);
        audio_even_ai_state_lock_4e1fa6();
        if (even_ai_add_answer(audio_text_stream_pending_text_552ce8(
                                   audio_even_ai_text_stream_handle_20074c04),
                               NULL, 0xffu, 0u, 0u) != 0u)
            (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_LISTEN);
        audio_even_ai_state_unlock_4e1fbe();
        even_ai_layout_refresh();
        return;
    }
    EVEN_AI_LOG(3u, answer_reflash_fn, 0x7d9u, 0x0c000000u, reply_stream, reply_stream_short);
    if (even_ai_add_answer(empty_text, NULL, 0xffu, 0u, 0u) != 0u)
        (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_REPLY);
    g2_even_ai_current_streaming_node = g2_even_ai_dialogs.tail;
    g2_even_ai_stream_flag = 0u;
    even_ai_stream_init_from_service(0u);
    even_ai_stream_on_auto_reflash();
}

/* Result answer with icon, built from the service text (stock leaves the
 * buffer unset when the service text is empty). */
static void result_answer(const void *icon, uint8_t bar_value, uint8_t compact)
{
    char text[TEXT_BUF_LEN + 3u];

    if (SERVICE_KEEP_PHASE == 1u)
        (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_LISTEN);
    else
        even_ai_animation_hide_all_55389a();
    if (SERVICE_TEXT_LEN != 0u) {
        aeabi_memset_43c0e4(text, TEXT_BUF_LEN, 0);
        audio_queue_copy_bytes(text, SERVICE_TEXT, SERVICE_TEXT_LEN);
    }
    (void)even_ai_add_answer(text, icon, bar_value, 1u, compact);
    even_ai_layout_refresh();
    service_even_ai_fn_00498310(2u);
}

static void error_answer(const char *key, const void *icon, uint8_t compact)
{
    (void)even_ai_add_answer(TR(key), icon, 0xffu, 1u, compact);
}

/* Redraw the page for the current service mode. The page argument is unused
 * by the stock code. */
void even_ai_ui_reflash(void *page)
{
    (void)page;
    if (g2_even_ai_event_fifo == NULL)
        g2_even_ai_event_fifo = ui_common_api_fn_00509c1c();

    switch (SERVICE_MODE) {
    case EVEN_AI_MODE_WAKE:
        if (SERVICE_SUB == 1u)
            EVEN_AI_LOG(3u, ui_reflash_fn, 0x806u, 0x0c000000u, wake_up, wake_up_short);
        else if (SERVICE_SUB != 2u)
            return;
        if (g2_even_ai_dialogs.count == 0u)
            even_ai_listening_text_toggle();
        (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_LISTEN);
        return;

    case EVEN_AI_MODE_ASK:
        even_ai_hide_listening_text();
        if (SERVICE_DIRECT == 0u) {
            EVEN_AI_LOG(3u, ui_reflash_fn, 0x86eu, 0x0c000000u, ask_stream, ask_stream_short);
            if (even_ai_add_question(empty_text, 0u) != 0u)
                (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_ASK);
            g2_even_ai_current_streaming_node = g2_even_ai_dialogs.tail;
            g2_even_ai_stream_flag = 1u;
            even_ai_stream_init_from_service(1u);
            even_ai_stream_on_auto_reflash();
            return;
        }
        EVEN_AI_LOG(3u, ui_reflash_fn, 0x87bu, 0x0c000000u, ask_direct, ask_direct_short);
        audio_even_ai_state_lock_4e1fa6();
        if (even_ai_add_question(audio_text_stream_pending_text_552ce8(
                                     audio_even_ai_text_stream_handle_20074c04),
                                 0u) != 0u)
            (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_ASK);
        audio_even_ai_state_unlock_4e1fbe();
        even_ai_layout_refresh();
        return;

    case EVEN_AI_MODE_ANALYSE:
        (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_ANALYSE);
        if (g2_even_ai_dialogs.count != 0u) {
            even_ai_gray_question((uint8_t)(g2_even_ai_dialogs.count - 1u));
            return;
        }
        EVEN_AI_LOG(2u, ui_reflash_fn, 0x896u, 0x08000000u, analyse_none, analyse_none_short);
        return;

    case EVEN_AI_MODE_REPLY:
        even_ai_hide_listening_text();
        if (even_ai_animation_phase_get_553d28() != EVEN_AI_PHASE_REPLY)
            (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_REPLY);
        if (g2_even_ai_dialogs.count != 0u)
            even_ai_gray_question((uint8_t)(g2_even_ai_dialogs.count - 1u));
        even_ai_answer_text_reflash();
        return;

    case EVEN_AI_MODE_RESULT:
        even_ai_hide_listening_text();
        if (g2_even_ai_dialogs.count != 0u)
            even_ai_gray_question((uint8_t)(g2_even_ai_dialogs.count - 1u));
        switch (SERVICE_SUB) {
        case 1u:
            result_answer(g2_even_ai_icon_769f20, (uint8_t)SERVICE_VALUE, 0u);
            return;
        case 3u:
            result_answer(g2_onboarding_status_img_76e7f8, 0xffu, 1u);
            return;
        case 4u:
        case 5u:
        case 6u:
        case 7u:
            if (even_ai_animation_phase_get_553d28() != EVEN_AI_PHASE_REPLY)
                (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_REPLY);
            if (SERVICE_VALUE == 0u)
                even_ai_answer_text_reflash();
            return;
        case 8u:
            result_answer(g2_even_ai_icon_769d7c, 0xffu, 1u);
            return;
        default:
            return;
        }

    case EVEN_AI_MODE_ERROR:
        if (g2_even_ai_dialogs.count == 0u)
            even_ai_listening_visibility_set(1u);
        even_ai_hide_listening_text();
        if (SERVICE_KEEP_PHASE == 1u)
            (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_LISTEN);
        else
            even_ai_animation_hide_all_55389a();
        switch (SERVICE_SUB) {
        case 1u:
            error_answer(id_network_error, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        case 2u:
            error_answer(id_bluetooth_disconnected, g2_even_ai_icon_769e40, 1u);
            break;
        case 3u:
            error_answer(id_server_error, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        case 4u:
            error_answer(id_having_trouble, NULL, 0u);
            break;
        case 5u:
            error_answer(id_currently_unsupported, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        case 6u:
            error_answer(id_audio_error, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        case 7u:
            error_answer(id_asr_server_error, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        case 8u:
            error_answer(id_ai_server_error, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        case 9u:
            error_answer(id_command_failed, audio_system_alert_icon_disconnect_7747e4, 1u);
            break;
        default:
            (void)even_ai_add_answer(unknown_error, audio_system_alert_icon_disconnect_7747e4,
                                     0xffu, 1u, 1u);
            break;
        }
        even_ai_layout_refresh();
        return;

    default:
        return;
    }
}

/* Build the page: 576x288 root, black content column, 560-wide bordered
 * frame (shifted 8 px towards the wearer's side, -8 on device role 1), the
 * scrollable dialog container and the centred "listening" label, then place
 * the four animation presets at the bottom of the frame. */
void even_ai_page_init(void *page)
{
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;

    if (g2_even_ai_event_fifo == NULL)
        g2_even_ai_event_fifo = ui_common_api_fn_00509c1c();
    g2_even_ai_anim_busy = 0u;
    even_ai_listening_visibility_set(0u);

    audio_lv_width_43f506(page, 576);
    audio_uart_page_43f568(page, 288);
    audio_uart_page_43f0e0(page, 0);
    audio_uart_page_43f142(page, 0);
    audio_lv_object_flag_43ded4(page, 0x50000u);
    audio_lv_object_clear_flag_43dfa4(page, 0xb014u);
    (void)audio_uart_page_44e368(page, 0u);
    audio_uart_page_44146a(page, 0, 0u);
    audio_uart_page_44127e(page, audio_lv_color_44104c(0u), 0u);
    audio_uart_page_44129e(page, 0u, 0u);
    audio_uart_page_44131c(page, 0, 0u);
    even_ai_style_apply(page, 0, 0u);

    void *root = audio_uart_page_43de82(page);
    d->word0 = (uint32_t)(uintptr_t)root;
    audio_lv_width_43f506(root, 576);
    audio_uart_page_43f568(root, LV_SIZE_CONTENT);
    audio_uart_page_4411aa(root, 256, 0u);
    audio_uart_page_43f6b8(root, 4u, 0, 0);
    audio_uart_page_44131c(root, 0, 0u);
    audio_uart_page_44127e(root, audio_lv_color_44104c(0u), 0u);
    audio_uart_page_44129e(root, 0xffu, 0u);
    audio_uart_page_44146a(root, 0, 0u);
    even_ai_style_apply(root, 0, 0u);
    audio_uart_page_44121c(root, 16, 0u);
    audio_lv_object_clear_flag_43dfa4(root, 0x12u);

    int32_t x_ofs = 8;
    if (audio_uart_device_role_get() == 1u)
        x_ofs = -x_ofs;

    void *frame = audio_uart_page_43de82(root);
    d->word4 = (uint32_t)(uintptr_t)frame;
    audio_lv_width_43f506(frame, 560);
    audio_uart_page_43f568(frame, LV_SIZE_CONTENT);
    audio_uart_page_4411aa(frame, 240, 0u);
    audio_uart_page_43f6b8(frame, 2u, x_ofs, 0);
    audio_uart_page_44131c(frame, 1, 0u);
    audio_uart_page_4412ec(frame, audio_lv_color_44104c(0xffffffu), 0u);
    audio_uart_page_44146a(frame, 6, 0u);
    audio_uart_page_44127e(frame, audio_lv_color_44104c(0u), 0u);
    audio_uart_page_44129e(frame, 0xffu, 0u);
    audio_uart_page_44120e(frame, 16, 0u);
    audio_uart_page_44121c(frame, 24, 0u);
    audio_uart_page_44122a(frame, 20, 0u);
    audio_uart_page_441238(frame, 0, 0u);
    audio_lv_object_clear_flag_43dfa4(frame, 0x12u);

    d->dialog_cont = audio_uart_page_43de82(frame);
    audio_lv_width_43f506(d->dialog_cont, 540);
    audio_uart_page_43f568(d->dialog_cont, LV_SIZE_CONTENT);
    audio_uart_page_4411aa(d->dialog_cont, 200, 0u);
    audio_uart_page_43f6b8(d->dialog_cont, 1u, 0, 0);
    audio_uart_page_44131c(d->dialog_cont, 0, 0u);
    audio_uart_page_44146a(d->dialog_cont, 0, 0u);
    audio_uart_page_44127e(d->dialog_cont, audio_lv_color_44104c(0u), 0u);
    audio_uart_page_44129e(d->dialog_cont, 0xffu, 0u);
    even_ai_style_apply(d->dialog_cont, 0, 0u);
    (void)audio_uart_page_44e368(d->dialog_cont, 3u);
    audio_uart_page_44e3ca(d->dialog_cont, 0x0cu /* LV_DIR_VER */);
    audio_lv_object_flag_43ded4(d->dialog_cont, 0x10u);
    audio_lv_object_clear_flag_43dfa4(d->dialog_cont, 0x300u);
    (void)audio_uart_page_451740(d->dialog_cont, even_ai_input_event_callback, 0x0eu, NULL);

    d->label_listening = audio_lv_label_create_499416(frame);
    audio_lv_width_43f506(d->label_listening, 523);
    audio_uart_page_43f568(d->label_listening, 30);
    audio_uart_page_43f6b8(d->label_listening, 1u, 0, 0);
    audio_lv_style_a_44145a(d->label_listening, 2u /* LV_TEXT_ALIGN_CENTER */, 0u);
    audio_lv_style_color_44140e(d->label_listening, audio_lv_color_44104c(0xffffffu), 0u);
    audio_lv_style_font_44143e(d->label_listening, audio_system_alert_font_200746e0, 0u);
    audio_uart_page_44131c(d->label_listening, 0, 0u);
    even_ai_style_apply(d->label_listening, 0, 0u);
    audio_lv_object_clear_flag_43dfa4(d->label_listening, 0x12u);
    audio_lv_label_text_49942e(d->label_listening, TR(id_listening));

    if (text_stream_animation_presets_init(root, 1u) != 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module_tag, source_file, page_init_fn, 0x9dau, anim_init_failed);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08000000u, anim_init_failed_short, anim_init_failed_short);
        return;
    }
    for (int32_t i = 0; i < 4; i++) {
        void *preset = text_stream_animation_preset_get((uint8_t)i);
        if (preset != NULL)
            audio_uart_page_43f6b8(preset, 5u, x_ofs, 9);
    }
    (void)even_ai_animation_show_phase_5537cc(EVEN_AI_PHASE_LISTEN);
}

void even_ai_page_deinit(void)
{
    audio_even_ai_state_lock_4e1fa6();
    even_ai_deinit_text_stream_service();
    audio_even_ai_state_unlock_4e1fbe();
    g2_even_ai_dialogs.count = 0u;
    g2_even_ai_anim_busy = 0u;
    if (g2_even_ai_event_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_even_ai_event_fifo);
        g2_even_ai_event_fifo = NULL;
    }
}
