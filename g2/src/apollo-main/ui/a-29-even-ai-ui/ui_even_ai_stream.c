/* EvenAI dialog streaming and input glue, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\ui_even_ai.c.
 * Native 0x4e54c8..0x4e5509 and 0x4e55f8..0x4e5d53 (0x4e550a, 0x4e551e and
 * 0x4e557c live in app/even-ai/); literal pools 0x4e5f90..0x4e5fa3,
 * 0x4e607c..0x4e6087, 0x4e60e4..0x4e60ff, 0x4e61a4..0x4e61b3, 0x4e61ec,
 * 0x4e62b8..0x4e62bf, 0x4e64a8..0x4e64b3, 0x4e654c..0x4e6557.
 *
 * The text stream service reveals the question or answer text step by step
 * (one boundary per interval tick). The glasses side that owns the stream
 * (device role 1) sends {5, kind, u16 shown length} on sync app 7 after every
 * chunk_size steps; the peer then calls even_ai_stream_phase_update with that
 * length. Scroll and close gestures arrive as 6-byte frames {4, code, x, y}. */
#include <stdint.h>
#include <stddef.h>
#include "ui_even_ai_internal.h"

/* lv_event_t (LVGL 8 layout) as far as it is read here. */
typedef struct {
    void *target;          /* +0x00 */
    void *current_target;  /* +0x04 */
    uint32_t code;         /* +0x08 */
    void *user_data;       /* +0x0c */
    void *param;           /* +0x10 */
} g2_lv_event_t;

enum {
    EVEN_AI_INPUT_FRAME = 4u,
    EVEN_AI_INPUT_CLICK = 0x0au,
    EVEN_AI_INPUT_SCROLL_UP = 0x44u,
    EVEN_AI_INPUT_SCROLL_DOWN = 0x45u,
    EVEN_AI_INPUT_CLOSE = 0x48u,
    EVEN_AI_SYNC_STREAM_STEP = 5u,
};

extern uint32_t audio_even_ai_text_stream_handle_20074c04;  /* RAM 0x20074c04 g_even_ai_text_stream_service */
extern g2_even_ai_dialog_node_t *g2_even_ai_current_streaming_node; /* RAM 0x20074c08 */
extern uint8_t g2_even_ai_stream_flag;                      /* RAM 0x2007503b */
extern uint8_t audio_even_ai_ready_state_2006f138[0x218];   /* RAM 0x2006f138, +8 interval,
                                                               +9 finish animation, +0xc finish now */

extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern uint32_t osKernelGetTickCount(void);                               /* 0x4490cc */
extern void even_ai_relayout_dialogs(void);                               /* 0x4e68a2 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void text_stream_destroy(void *stream);                            /* 0x552be6 */
extern const char *text_stream_current_text(void *stream);                /* 0x552cdc */
extern uint16_t text_stream_current_length(void *stream);                 /* 0x552cf8 */
extern uint16_t text_stream_pending_length(void *stream);                 /* 0x552d04 */
extern void text_stream_copy_until_boundary(void *stream, uint32_t notify); /* 0x5531a8 */
extern void audio_text_stream_copy_bytes_553274(void *stream, uint32_t requested,
                                                uint32_t notify);
extern uint8_t audio_even_ai_stream_interval_get_4e550a(void);            /* even_ai_stream_interval_get */
extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern uint8_t audio_uart_device_role_get(void);                          /* 0x45a568 */
extern void service_even_ai_fn_00498310(uint8_t value);
extern uint32_t audio_even_ai_common_timer_start_4e2e62(uint32_t duration); /* even_ai_common_timer_mgr_start */
extern void audio_uart_master_display_refresh(uint32_t app, const void *payload,
                                              uint16_t length, uint32_t extra); /* 0x464bb2 sync send */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t extra);              /* sync app close */
extern int32_t even_ai_animation_show_phase_5537cc(uint8_t phase);
extern void even_ai_animation_hide_all_55389a(void);
extern int32_t ui_common_api_fn_00509dfa(void *fifo);                     /* 1 empty, 0 has data */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len); /* pop */
extern uint32_t audio_uart_page_event_code_450286(const void *e);         /* lv_event_get_code */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim);

static const char module_tag[] = "even_ai.ui"; /* ROM 0x78c824 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\ui_even_ai.c"; /* ROM 0x710f64 */
static const char deinit_fn[] = "even_ai_deinit_text_stream_service"; /* ROM 0x75c2e8 */
static const char deinit_msg[] = "Even AI text stream service destroyed"; /* ROM 0x75075c */
static const char deinit_short[] =
    "[even_ai.ui]Even AI text stream service destroyed"; /* ROM 0x72fcf0 */
static const char init_fn[] = "even_ai_stream_init_from_service"; /* ROM 0x75c30c */
static const char reflash_fn[] = "even_ai_stream_on_auto_reflash"; /* ROM 0x767470 */
static const char null_msg[] =
    "g_even_ai_text_stream_service or g_current_streaming_node is NULL"; /* ROM 0x707b58 */
static const char null_short[] =
    "[even_ai.ui]g_even_ai_text_stream_service or g_current_streaming_node is NULL"; /* ROM 0x6f0a88 */
static const char wait_msg[] =
    "even_ai: wait sync timeout, continue stepping, char_count=%u, chunk_size=%u"; /* ROM 0x6f72d8 */
static const char wait_short[] =
    "[even_ai.ui]even_ai: wait sync timeout, continue stepping, char_count=%u, chunk_size=%u"; /* ROM 0x6e5878 */
static const char warp_fn[] = "EvenAI_InputEventWarp"; /* ROM 0x77d21c */
static const char warp_msg[] = "raw_data is NULL or len is 0"; /* ROM 0x767490 */
static const char warp_short[] = "[even_ai.ui]raw_data is NULL or len is 0"; /* ROM 0x745e58 */

#define STREAM_STATE ((g2_even_ai_stream_state_t *)(void *)audio_even_ai_stream_display_state_20073a1c)
#define TEXT_STREAM ((void *)(uintptr_t)audio_even_ai_text_stream_handle_20074c04)

#define LOG_COMPRESSED() \
    ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

void even_ai_style_apply(void *obj, int32_t value, uint32_t selector) {
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

uint32_t even_ai_tick_get(void) {
    return osKernelGetTickCount();
}

void even_ai_layout_refresh(void) {
    even_ai_relayout_dialogs();
}

void even_ai_deinit_text_stream_service(void) {
    if (audio_even_ai_text_stream_handle_20074c04 != 0u) {
        text_stream_destroy(TEXT_STREAM);
        audio_even_ai_text_stream_handle_20074c04 = 0u;
        g2_even_ai_current_streaming_node = NULL;
        g2_even_ai_stream_flag = 0u;
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, deinit_fn, 0x156u, deinit_msg);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x0c000000u, deinit_short, deinit_short);
    }
    (void)aeabi_memset_43c0e4(audio_even_ai_stream_display_state_20073a1c, 0x20u, 0);
}

uint8_t *even_ai_text_stream_service_get(void) {
    return audio_even_ai_stream_display_state_20073a1c;
}

/* question != 0 streams into the question label, else into the answer label. */
void even_ai_stream_init_from_service(uint8_t question) {
    g2_even_ai_stream_state_t *st = STREAM_STATE;

    if (audio_even_ai_text_stream_handle_20074c04 == 0u ||
        g2_even_ai_current_streaming_node == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, init_fn, 0x17fu, null_msg);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x04000000u, null_short, null_short);
        return;
    }
    if (st->phase != 1u)
        (void)aeabi_memset_43c0e4(st, 0x20u, 0);
    st->phase = 1u;
    st->kind = question != 0u ? 1u : 2u;
    st->start_len = text_stream_current_length(TEXT_STREAM);
    st->shown_len = text_stream_pending_length(TEXT_STREAM);
    st->chunk_size = 6u;
    st->interval = audio_even_ai_stream_interval_get_4e550a();
}

/* End of the visible text: an answer waits in phase 2 for the finish
 * animation (or its 5 s timeout), a question simply stops. */
static inline void stream_answer_finished(g2_even_ai_stream_state_t *st) {
    st->phase = 2u;
    st->finish_tick = even_ai_tick_get();
    if (audio_even_ai_ready_state_2006f138[9] == 1u)
        (void)even_ai_animation_show_phase_5537cc(0u);
    else
        even_ai_animation_hide_all_55389a();
}

void even_ai_stream_on_auto_reflash(void) {
    g2_even_ai_stream_state_t *st = STREAM_STATE;

    if (st->phase == 0u || st->kind == 0u)
        return;
    audio_even_ai_state_lock_4e1fa6();
    if (audio_even_ai_text_stream_handle_20074c04 == 0u ||
        g2_even_ai_current_streaming_node == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, reflash_fn, 0x19au, null_msg);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x04000000u, null_short, null_short);
        st->phase = 0u;
        goto out;
    }

    uint32_t now = even_ai_tick_get();
    if (st->phase == 2u) {
        if (st->kind == 2u &&
            (audio_even_ai_ready_state_2006f138[0xc] == 1u ||
             (st->finish_tick != 0u && now - st->finish_tick > 5000u))) {
            st->phase = 0u;
            service_even_ai_fn_00498310(2u);
        }
        goto out;
    }
    if (now - st->last_tick < st->interval)
        goto out;

    uint8_t role = audio_uart_device_role_get();
    if (st->step_count >= st->chunk_size) {
        /* Wait up to 12 intervals for the peer's sync before stepping on. */
        if (st->wait_sync == 0u) {
            st->wait_sync = 1u;
            st->wait_tick = now;
        }
        if (now - st->wait_tick < (uint32_t)audio_even_ai_stream_interval_get_4e550a() * 12u)
            goto out;
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, reflash_fn, 0x1c6u, wait_msg,
                               st->step_count, st->chunk_size);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x08800000u, wait_short, wait_short, st->step_count,
                                      st->chunk_size);
        st->wait_sync = 0u;
    }

    uint16_t before = text_stream_current_length(TEXT_STREAM);
    text_stream_copy_until_boundary(TEXT_STREAM, 0u);
    uint16_t after = text_stream_current_length(TEXT_STREAM);
    if (after == before) {
        if (st->kind == 2u)
            stream_answer_finished(st);
        else if (st->kind == 1u)
            st->phase = 0u;
        goto out;
    }

    const char *text = text_stream_current_text(TEXT_STREAM);
    g2_even_ai_dialog_node_t *node = g2_even_ai_current_streaming_node;
    if (st->kind == 1u) {
        if (node->question_label != NULL &&
            audio_terminal_ui_object_valid_43e2ea(node->question_label) != 0u) {
            audio_lv_label_text_49942e(node->question_label, text);
            (void)audio_even_ai_common_timer_start_4e2e62(8000u);
            even_ai_node_stream_state_init(node, 1u, text_stream_current_length(TEXT_STREAM));
            if (g2_even_ai_dialogs.total_chars > EVEN_AI_CHAR_WINDOW)
                even_ai_manage_char_window();
        }
    } else if (st->kind == 2u && node->answer_label != NULL &&
               audio_terminal_ui_object_valid_43e2ea(node->answer_label) != 0u) {
        audio_lv_label_text_49942e(node->answer_label, text);
        (void)audio_even_ai_common_timer_start_4e2e62(10000u);
        even_ai_node_stream_state_init(node, 0u, text_stream_current_length(TEXT_STREAM));
        if (g2_even_ai_dialogs.total_chars > EVEN_AI_CHAR_WINDOW)
            even_ai_manage_char_window();
    }
    st->step_count++;
    st->shown_len = after;
    st->last_tick = even_ai_tick_get();
    even_ai_layout_refresh();

    uint16_t pending = text_stream_pending_length(TEXT_STREAM);
    if (role == 1u && (st->step_count >= st->chunk_size ||
                       text_stream_current_length(TEXT_STREAM) >= pending)) {
        uint8_t frame[4];
        frame[0] = EVEN_AI_SYNC_STREAM_STEP;
        frame[1] = st->kind;
        uint16_t shown = text_stream_current_length(TEXT_STREAM);
        frame[2] = (uint8_t)shown;
        frame[3] = (uint8_t)(shown >> 8);
        audio_uart_master_display_refresh(EVEN_AI_SYNC_APP, frame, 4u, 0u);
    }
    if (text_stream_current_length(TEXT_STREAM) >= pending) {
        if (st->kind == 2u)
            stream_answer_finished(st);
        else
            st->phase = 0u;
    }
out:
    audio_even_ai_state_unlock_4e1fbe();
}

/* Peer sync: jump the local stream to the length the stream owner shows. */
void even_ai_stream_phase_update(uint8_t kind, uint16_t length) {
    g2_even_ai_stream_state_t *st = STREAM_STATE;

    if (st->phase == 0u || kind == 0u || st->kind != kind ||
        audio_even_ai_text_stream_handle_20074c04 == 0u)
        return;
    audio_even_ai_state_lock_4e1fa6();
    uint16_t pending = text_stream_pending_length(TEXT_STREAM);
    if (pending < length)
        length = pending;
    if (text_stream_current_length(TEXT_STREAM) != length) {
        audio_text_stream_copy_bytes_553274(TEXT_STREAM, length, 0u);
        const char *text = text_stream_current_text(TEXT_STREAM);
        g2_even_ai_dialog_node_t *node = g2_even_ai_current_streaming_node;
        if (st->kind == 1u) {
            if (node != NULL && node->question_label != NULL &&
                audio_terminal_ui_object_valid_43e2ea(node->question_label) != 0u)
                audio_lv_label_text_49942e(node->question_label, text);
        } else if (st->kind == 2u) {
            if (node != NULL && node->answer_label != NULL &&
                audio_terminal_ui_object_valid_43e2ea(node->answer_label) != 0u)
                audio_lv_label_text_49942e(node->answer_label, text);
        }
        even_ai_layout_refresh();
    }
    st->shown_len = length;
    st->step_count = 0u;
    st->last_tick = even_ai_tick_get();
    st->wait_sync = 0u;
    pending = text_stream_pending_length(TEXT_STREAM);
    if (text_stream_current_length(TEXT_STREAM) >= pending) {
        if (st->kind == 2u)
            stream_answer_finished(st);
        else if (st->kind == 1u)
            st->phase = 0u;
    }
    audio_even_ai_state_unlock_4e1fbe();
}

/* Forward a local gesture to the peer as {4, code, x16, y16}. */
int32_t even_ai_stream_event_forward(uint32_t code, const g2_lv_event_t *e) {
    uint8_t frame[6];

    if (code == EVEN_AI_INPUT_CLICK || code == EVEN_AI_INPUT_CLOSE) {
        frame[0] = EVEN_AI_INPUT_FRAME;
        frame[1] = (uint8_t)code;
        frame[2] = 0u;
        frame[3] = 0u;
        frame[4] = 0u;
        frame[5] = 0u;
        audio_uart_master_display_refresh(EVEN_AI_SYNC_APP, frame, 6u, 0u);
    } else if (code == EVEN_AI_INPUT_SCROLL_DOWN || code == EVEN_AI_INPUT_SCROLL_UP) {
        const int32_t *point = (const int32_t *)e->param;
        frame[0] = EVEN_AI_INPUT_FRAME;
        frame[1] = (uint8_t)code;
        frame[2] = (uint8_t)point[0];
        frame[3] = (uint8_t)(point[0] >> 8);
        frame[4] = (uint8_t)point[1];
        frame[5] = (uint8_t)(point[1] >> 8);
        audio_uart_master_display_refresh(EVEN_AI_SYNC_APP, frame, 6u, 0u);
    }
    return 0;
}

int32_t EvenAI_InputEventWarp(const uint8_t *raw, uint32_t len) {
    if (raw == NULL || len == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, warp_fn, 0x2b0u, warp_msg);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x08000000u, warp_short, warp_short);
        return -1;
    }
    if (raw[0] == EVEN_AI_INPUT_FRAME) {
        uint8_t code = raw[1];
        int16_t x = (int16_t)(raw[2] | (raw[3] << 8));
        int16_t y = (int16_t)(raw[4] | (raw[5] << 8));
        switch (code) {
        case EVEN_AI_INPUT_CLICK:
            break;
        case EVEN_AI_INPUT_SCROLL_UP:
            even_ai_scroll_by_delta(1, y, x);
            break;
        case EVEN_AI_INPUT_SCROLL_DOWN:
            even_ai_scroll_by_delta(-1, y, x);
            break;
        case EVEN_AI_INPUT_CLOSE:
            if (audio_uart_device_role_get() == 1u)
                audio_system_alert_close_464c36(EVEN_AI_SYNC_APP, 0u, 0u, 0u);
            break;
        default:
            break;
        }
    }
    return 0;
}

/* Drain one queued input frame once the page animation is idle. */
void even_ai_input_event_adapter(void *unused) {
    uint8_t raw[6];

    (void)unused;
    g2_even_ai_anim_busy = 0u;
    if (g2_even_ai_event_fifo != NULL && ui_common_api_fn_00509dfa(g2_even_ai_event_fifo) == 0) {
        (void)aeabi_memset_43c0e4(raw, 6u, 0);
        if (ui_common_api_fn_00509e14(g2_even_ai_event_fifo, raw, 6u) >= 0)
            (void)EvenAI_InputEventWarp(raw, 6u);
    }
}

/* Dialog-container event callback: code 14 releases the input queue (the
 * scroll animation started by even_ai_scroll_to is over); 12 is ignored. */
void even_ai_input_event_callback(void *e) {
    uint32_t code = audio_uart_page_event_code_450286(e);
    if (code == 12u) {
        /* nothing */
    } else if (code == 14u) {
        even_ai_input_event_adapter(NULL);
    }
}

void even_ai_scroll_to(void *obj, int32_t y, uint32_t anim_time) {
    if (anim_time != 0u)
        audio_uart_lv_scroll_to_y_44ea04(obj, y, 1u);
    else
        audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}
