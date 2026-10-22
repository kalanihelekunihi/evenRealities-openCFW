/* EvenAI dialog list: scrolling, height cache, character window, listening
 * label and question labels, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\ui_even_ai.c.
 * Native 0x4e5d54..0x4e5f8d, 0x4e5fa4..0x4e607b, 0x4e6088..0x4e60e3,
 * 0x4e6100..0x4e61a1, 0x4e61b4..0x4e61e9, 0x4e61f0..0x4e654b; literal pools
 * 0x4e64a8, 0x4e6550..0x4e655f, 0x4e69e0, 0x4e6a70..0x4e6a7f, 0x4e6ae0..0x4e6aeb,
 * 0x4e6c18..0x4e6c43.
 *
 * The list keeps at most 5 dialogs and about EVEN_AI_CHAR_WINDOW characters:
 * once total_chars exceeds 1024 the oldest dialogs are dropped. */
#include <stdint.h>
#include <stddef.h>
#include "ui_even_ai_internal.h"

extern uint32_t audio_even_ai_text_stream_handle_20074c04;  /* RAM 0x20074c04 */
extern uint32_t audio_system_alert_font_200746e0;           /* RAM 0x200746e0 lv_font_t * */

extern const char *audio_text_stream_pending_text_552ce8(uint32_t stream); /* text_stream_pending_text */
extern uint16_t text_stream_current_length(void *stream);                 /* 0x552cf8 */
extern uint16_t text_stream_pending_length(void *stream);                 /* 0x552d04 */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                /* lv_obj_get_height */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                     /* lv_obj_get_scroll_y */
extern int32_t common_ui_get_scroll_y_5546be(void *obj, int32_t delta, int32_t speed,
                                             int32_t step);               /* teleprompt_ui.c */
extern void service_even_ai_fn_00498310(uint8_t value);
extern void even_ai_common_timer_mgr_deinit(void);                        /* 0x4e2e10 */
extern const char *audio_uart_page_text_pointer_4997f8(const void *label); /* lv_label_get_text */
extern uint32_t g2_log_module_length(const char *text);                   /* strlen 0x44a43c */
extern void even_ai_dialogs_refresh(void);                                /* 0x4e6a80 drop oldest */
extern void even_ai_dialog_node_apply(g2_even_ai_dialog_node_t *node, uint8_t arg); /* 0x4e69e4 */
extern g2_even_ai_dialog_node_t *even_ai_create_dialog_node(void);        /* 0x4e6956 */
extern void even_ai_dialog_index_set(g2_even_ai_dialog_node_t *node);     /* 0x4e6a4e */
extern g2_even_ai_dialog_node_t *even_ai_dialog_get(uint8_t index);       /* 0x4e6aaa */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag);  /* lv_obj_clear_flag */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);        /* lv_obj_add_flag */
extern void audio_lv_delete_44d7b8(void *obj);                            /* lv_obj_del */
extern void *audio_lv_label_create_499416(void *parent);                  /* lv_label_create */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);   /* border_width */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);                      /* lv_color_hex */
extern void audio_lv_style_color_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_lv_style_font_44143e(void *obj, uint32_t font, uint32_t sel);   /* text_font */
extern void audio_lv_style_a_44145a(void *obj, uint32_t value, uint32_t sel);
extern void audio_lv_width_43f506(void *obj, int32_t width);              /* lv_obj_set_width */
extern void audio_lv_object_position_43f09a(void *obj, int32_t x, int32_t y);

static const char module_tag[] = "even_ai.ui"; /* ROM 0x78c824 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\ui_even_ai.c"; /* ROM 0x710f64 */
static const char window_fn[] = "even_ai_manage_char_window"; /* ROM 0x773e7c */
static const char window_msg[] =
    "Even AI: Character window management completed, removed %d dialogs, total chars: %d"; /* ROM 0x6eaa5c */
static const char window_short[] =
    "[even_ai.ui]Even AI: Character window management completed, removed %d dialogs, total chars: %d"; /* ROM 0x6ded94 */
static const char show_fn[] = "even_ai_show_listening_text"; /* ROM 0x773e98 */
static const char hide_fn[] = "even_ai_hide_listening_text"; /* ROM 0x773eb4 */
static const char listening_msg[] = "label_listening is NULL"; /* ROM 0x77d234 */
static const char listening_short[] = "[even_ai.ui]label_listening is NULL"; /* ROM 0x75c330 */
static const char add_fn[] = "even_ai_add_question"; /* ROM 0x77d24c */
static const char create_msg[] = "create_dialog_node failed"; /* ROM 0x773ed0 */
static const char create_short[] = "[even_ai.ui]create_dialog_node failed"; /* ROM 0x750784 */
static const char gray_fn[] = "even_ai_gray_question"; /* ROM 0x77d264 */
static const char gray_msg[] = "dialog_index %d >= dialog_count %d"; /* ROM 0x75c354 */
static const char gray_short[] = "[even_ai.ui]dialog_index %d >= dialog_count %d"; /* ROM 0x73a754 */

#define STREAM_STATE ((g2_even_ai_stream_state_t *)(void *)audio_even_ai_stream_display_state_20073a1c)
#define TEXT_STREAM ((void *)(uintptr_t)audio_even_ai_text_stream_handle_20074c04)
#define QUESTION_COLOR 0x444444u   /* ROM pool 0x4e6c30 */
#define QUESTION_WIDTH 523
#define DIALOG_GAP 8               /* question to answer */
#define DIALOG_SPACING 16          /* between dialogs */
#define DIALOG_WINDOW_HEIGHT 200
#define SCROLL_STEP 28

#define LOG_COMPRESSED() \
    ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

static int obj_ok(void *obj) {
    return obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) != 0u;
}

/* 1 while nothing is streaming any more (manual scrolling allowed). */
uint32_t even_ai_scroll_needed(void) {
    if (STREAM_STATE->phase == 1u)
        return 0u;
    if (audio_even_ai_text_stream_handle_20074c04 != 0u &&
        audio_text_stream_pending_text_552ce8(audio_even_ai_text_stream_handle_20074c04) != NULL) {
        uint16_t pending = text_stream_pending_length(TEXT_STREAM);
        if (text_stream_current_length(TEXT_STREAM) < pending)
            return 0u;
    }
    return 1u;
}

uint32_t even_ai_dialog_height_exceeds_window(void) {
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;

    if (!obj_ok(d->dialog_cont))
        return 0u;
    int32_t height = 0;
    int32_t index = 0;
    g2_even_ai_dialog_node_t *node = d->head;
    do {
        if (node == NULL)
            return 0u;
        if (obj_ok(node->question_label))
            height += audio_uart_lv_obj_height_43fdda(node->question_label);
        if (obj_ok(node->answer_obj)) {
            if (obj_ok(node->question_label))
                height += DIALOG_GAP;
            height += audio_uart_lv_obj_height_43fdda(node->answer_obj);
        }
        index++;
        if (index < (int32_t)d->count)
            height += DIALOG_SPACING;
        node = node->next;
    } while (height <= DIALOG_WINDOW_HEIGHT);
    return 1u;
}

/* direction > 0 scrolls by +delta, else by -delta; the user stopping to read
 * also stops the auto-advance timer. */
void even_ai_scroll_by_delta(int32_t direction, int32_t delta, int32_t speed) {
    if (even_ai_scroll_needed() == 0u)
        return;
    service_even_ai_fn_00498310(1u);
    even_ai_common_timer_mgr_deinit();
    if ((g2_even_ai_anim_busy == 0u || g2_even_ai_anim_busy == 1u) &&
        even_ai_dialog_height_exceeds_window() != 0u) {
        g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
        int32_t current = audio_uart_lv_obj_y_44e498(d->dialog_cont);
        int32_t target;
        if (direction >= 1)
            target = common_ui_get_scroll_y_5546be(d->dialog_cont, delta, speed, SCROLL_STEP);
        else
            target = common_ui_get_scroll_y_5546be(d->dialog_cont, -delta, speed, SCROLL_STEP);
        if (target != current) {
            g2_even_ai_anim_busy = 1u;
            even_ai_scroll_to(d->dialog_cont, target, delta < 3 ? 100u : 200u);
        }
    }
}

/* 1 when the cached heights of the newest dialog no longer match. */
uint32_t even_ai_layout_cache_changed(void) {
    g2_even_ai_layout_cache_t *c = &g2_even_ai_layout_cache;

    if (c->valid == 0u)
        return 1u;
    if (c->count != g2_even_ai_dialogs.count)
        return 1u;
    g2_even_ai_dialog_node_t *node = g2_even_ai_dialogs.tail;
    if (node == NULL)
        return 1u;
    if (obj_ok(node->question_label)) {
        int32_t h = audio_uart_lv_obj_height_43fdda(node->question_label);
        if (c->has_question != 1u || c->question_height != h)
            return 1u;
    } else if (c->has_question != 0u) {
        return 1u;
    }
    if (obj_ok(node->answer_obj)) {
        int32_t h = audio_uart_lv_obj_height_43fdda(node->answer_obj);
        if (c->has_answer != 1u || c->answer_height != h)
            return 1u;
    } else if (c->has_answer != 0u) {
        return 1u;
    }
    return 0u;
}

/* Note: does not set valid; the caller does. */
void even_ai_layout_cache_update(void) {
    g2_even_ai_layout_cache_t *c = &g2_even_ai_layout_cache;

    c->count = g2_even_ai_dialogs.count;
    g2_even_ai_dialog_node_t *node = g2_even_ai_dialogs.tail;
    if (node == NULL) {
        c->has_question = 0u;
        c->has_answer = 0u;
        return;
    }
    if (obj_ok(node->question_label)) {
        c->has_question = 1u;
        c->question_height = audio_uart_lv_obj_height_43fdda(node->question_label);
    } else {
        c->has_question = 0u;
    }
    if (obj_ok(node->answer_obj)) {
        c->has_answer = 1u;
        c->answer_height = audio_uart_lv_obj_height_43fdda(node->answer_obj);
    } else {
        c->has_answer = 0u;
    }
}

void even_ai_layout_cache_invalidate(void) {
    g2_even_ai_layout_cache.valid = 0u;
}

/* Characters shown by a dialog (question + answer label text lengths). */
uint16_t even_ai_text_width_measure(const g2_even_ai_dialog_node_t *node) {
    if (node == NULL)
        return 0u;
    uint32_t chars = 0u;
    const char *text;
    if (obj_ok(node->question_label) &&
        (text = audio_uart_page_text_pointer_4997f8(node->question_label)) != NULL)
        chars += g2_log_module_length(text);
    if (obj_ok(node->answer_label) &&
        (text = audio_uart_page_text_pointer_4997f8(node->answer_label)) != NULL)
        chars += g2_log_module_length(text);
    return (uint16_t)chars;
}

/* Set a node's question or answer char count and move the list totals by the
 * difference (clamped at 0). */
void even_ai_node_stream_state_init(g2_even_ai_dialog_node_t *node, uint8_t question,
                                    uint16_t chars) {
    if (node == NULL)
        return;
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
    uint16_t old = question != 0u ? node->question_chars : node->answer_chars;
    if (question != 0u) {
        node->question_chars = chars;
        if ((int32_t)(d->question_chars + chars) < (int32_t)old)
            d->question_chars = 0u;
        else
            d->question_chars = (uint16_t)(chars + d->question_chars - old);
    } else {
        node->answer_chars = chars;
        if ((int32_t)(d->answer_chars + chars) < (int32_t)old)
            d->answer_chars = 0u;
        else
            d->answer_chars = (uint16_t)(chars + d->answer_chars - old);
    }
    if ((int32_t)(d->total_chars + chars) < (int32_t)old)
        d->total_chars = 0u;
    else
        d->total_chars = (uint16_t)(chars + d->total_chars - old);
}

/* Remove a node's counts from the list totals (clamped) and clear them. */
void even_ai_node_stream_state_update(g2_even_ai_dialog_node_t *node) {
    if (node == NULL)
        return;
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
    if ((int32_t)(node->answer_chars + node->question_chars) < (int32_t)d->total_chars)
        d->total_chars = (uint16_t)(d->total_chars - node->question_chars - node->answer_chars);
    else
        d->total_chars = 0u;
    if (node->question_chars < d->question_chars)
        d->question_chars = (uint16_t)(d->question_chars - node->question_chars);
    else
        d->question_chars = 0u;
    if (node->answer_chars < d->answer_chars)
        d->answer_chars = (uint16_t)(d->answer_chars - node->answer_chars);
    else
        d->answer_chars = 0u;
    node->question_chars = 0u;
    node->answer_chars = 0u;
}

void even_ai_manage_char_window(void) {
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
    uint16_t removed = 0u;

    while (d->total_chars > EVEN_AI_CHAR_WINDOW && d->count >= 2u && d->head != NULL) {
        uint16_t chars = even_ai_text_width_measure(d->head);
        even_ai_dialogs_refresh();
        if (chars >= d->total_chars)
            d->total_chars = 0u;
        else
            d->total_chars = (uint16_t)(d->total_chars - chars);
        removed++;
    }
    if (removed == 0u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, window_fn, 0x4eeu, window_msg, removed,
                           d->total_chars);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x0c800000u, window_short, window_short, removed,
                                  d->total_chars);
}

/* Applies even_ai_dialog_node_apply(node, arg) to every dialog (releasing it)
 * and empties the list. */
void even_ai_listening_visibility_set(uint8_t arg) {
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
    g2_even_ai_dialog_node_t *node = d->head;

    while (node != NULL) {
        g2_even_ai_dialog_node_t *next = node->next;
        even_ai_dialog_node_apply(node, arg);
        node = next;
    }
    d->head = NULL;
    d->tail = NULL;
    d->count = 0u;
    d->total_chars = 0u;
    d->question_chars = 0u;
    d->answer_chars = 0u;
}

void even_ai_show_listening_text(void) {
    void *label = g2_even_ai_dialogs.label_listening;

    if (obj_ok(label)) {
        audio_lv_object_clear_flag_43dfa4(label, 1u); /* LV_OBJ_FLAG_HIDDEN */
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module_tag, source_file, show_fn, 0x549u, listening_msg);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x04000000u, listening_short, listening_short);
}

void even_ai_hide_listening_text(void) {
    void *label = g2_even_ai_dialogs.label_listening;

    if (obj_ok(label)) {
        audio_lv_object_flag_43ded4(label, 1u); /* LV_OBJ_FLAG_HIDDEN */
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module_tag, source_file, hide_fn, 0x552u, listening_msg);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x04000000u, listening_short, listening_short);
}

/* Clear all dialogs and show the "listening" label again. */
void even_ai_listening_text_toggle(void) {
    even_ai_listening_visibility_set(1u);
    even_ai_show_listening_text();
}

/* Show a question. Without new_dialog the newest dialog's question is updated
 * in place while it has no answer yet (returns 1 only when that ungrays it).
 * A newest dialog without a question but with an answer is reused after its
 * answer objects are deleted; otherwise a new dialog is created (dropping the
 * oldest when five exist). Returns 1 when a label was created or on failure. */
uint32_t even_ai_add_question(const char *text, uint8_t new_dialog) {
    if (text == NULL)
        return 0u;
    uint8_t empty = g2_log_module_length(text) == 0u ? 1u : 0u;
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;
    g2_even_ai_dialog_node_t *node = d->tail;

    if (new_dialog == 0u && node != NULL && obj_ok(node->question_label) &&
        !obj_ok(node->answer_obj)) {
        if (empty == 0u) {
            audio_lv_label_text_49942e(node->question_label, text);
            even_ai_node_stream_state_init(node, 1u, (uint16_t)g2_log_module_length(text));
            if (d->total_chars > EVEN_AI_CHAR_WINDOW)
                even_ai_manage_char_window();
        }
        if (node->grayed == 1u) {
            node->grayed = 0u;
            return 1u;
        }
        return 0u;
    }

    if (node != NULL && node->question_label == NULL &&
        audio_terminal_ui_object_valid_43e2ea(node->question_label) == 0u &&
        obj_ok(node->answer_obj)) {
        if (node->answer_obj != NULL) {
            audio_lv_delete_44d7b8(node->answer_obj);
            node->answer_obj = NULL;
            node->answer_label = NULL;
            node->answer_extra0 = NULL;
            node->answer_extra1 = NULL;
        }
    } else {
        if (d->count >= 5u) {
            even_ai_dialogs_refresh();
            even_ai_layout_cache_invalidate();
        }
        node = even_ai_create_dialog_node();
        if (node == NULL) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module_tag, source_file, add_fn, 0x5a4u, create_msg);
            if (LOG_COMPRESSED())
                (void)compress_log_output(0x04000000u, create_short, create_short);
            return 1u;
        }
        even_ai_dialog_index_set(node);
        d->count++;
    }

    void *label = audio_lv_label_create_499416(d->dialog_cont);
    audio_uart_page_44131c(label, 0, 0u);
    even_ai_style_apply(label, 0, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(QUESTION_COLOR), 0u);
    audio_lv_style_font_44143e(label, audio_system_alert_font_200746e0, 0u);
    audio_lv_style_a_44145a(label, 1u, 0u);
    audio_lv_width_43f506(label, QUESTION_WIDTH);
    if (empty == 0u) {
        audio_lv_label_text_49942e(label, text);
        even_ai_node_stream_state_init(node, 1u, (uint16_t)g2_log_module_length(text));
        if (d->total_chars > EVEN_AI_CHAR_WINDOW)
            even_ai_manage_char_window();
    }
    audio_lv_object_position_43f09a(label, 0, 0);
    node->question_label = label;
    node->grayed = 0u;
    return 1u;
}

void even_ai_gray_question(uint8_t index) {
    g2_even_ai_dialogs_t *d = &g2_even_ai_dialogs;

    if (index >= d->count) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, gray_fn, 0x62bu, gray_msg, index,
                               d->count);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x08800000u, gray_short, gray_short, index, d->count);
        return;
    }
    g2_even_ai_dialog_node_t *node = even_ai_dialog_get(index);
    if (node != NULL && obj_ok(node->question_label) && node->grayed == 0u)
        node->grayed = 1u;
}
