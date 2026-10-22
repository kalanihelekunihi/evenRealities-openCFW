/* EvenAI page input, reflash and UI-event handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\even_ai.c.
 * Native 0x4e2a5c..0x4e2d6b; literal pools 0x4e2c24..0x4e2c3f and
 * 0x4e2d6c..0x4e2e0f (shared with EvenAI_common_data_handler 0x4e2976).
 *
 * Reflash payloads (first byte): 3 redraw, 4 input event (queued in the
 * ui_common_api FIFO while the page animates, except scroll 0x44/0x45 in
 * animation state 1), 5 stream phase + u16, 6 animation sync phase + u32,
 * 8 stream phase + session stop. */
#include <stdint.h>

enum {
    UI_EVENT_TYPE_INIT = 2u,
    UI_EVENT_TYPE_REFLASH = 3u,
    UI_EVENT_TYPE_TIMER = 4u,
    UI_EVENT_TYPE_EXIT = 5u,
};

enum {
    INPUT_CLICK = 0x0au,
    INPUT_SCROLL_UP = 0x44u,
    INPUT_SCROLL_DOWN = 0x45u,
    INPUT_CLOSE = 0x48u,
};

enum { DEVICE_ROLE_SLAVE = 2u };
enum { AUDM_APP_EVEN_AI = 3u };

extern void *g2_even_ai_page;          /* RAM 0x2007457c */
extern uint8_t g2_even_ai_anim_busy;   /* RAM 0x2007503a */
extern void *g2_even_ai_event_fifo;    /* RAM 0x20074c00 */
extern uint8_t audio_uart_registry_context_200009a4;          /* RAM 0x200009a4, +4 page object */
extern uint8_t audio_even_ai_service_state_2006ed10[0x218];   /* RAM 0x2006ed10 */
extern uint8_t audio_even_ai_ready_state_2006f138[0x218];     /* RAM 0x2006f138, +0 mode, +1 sub-mode */
extern uint8_t audio_even_ai_text_pending_200f39b4[0x400];    /* RAM 0x200f39b4 */
extern uint8_t audio_even_ai_text_merged_200f3db4[0x400];     /* RAM 0x200f3db4 */

extern uint8_t audio_uart_device_role_get(void);                            /* 0x45a568 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_uart_page_43de82(void *parent);                          /* lv_obj_create */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* fifo_push */
extern int32_t audio_even_ai_local_decode_498092(uint32_t data, uint32_t length); /* SVC_DecodeLocalEvenAIInfo */
extern void audio_even_ai_ready_4e20f2(uint32_t no_reply);
extern void audio_even_ai_prepare_4e1f7c(void);
extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern void audio_even_ai_stop_current_streaming_4e557c(uint32_t mode);
extern uint32_t audio_even_ai_timer_start_all_4e31a0(uint32_t duration); /* even_ai_timer_start_all */
extern void even_ai_timer_process_all(void);                             /* 0x4e31b0 */
extern void even_ai_timer_deinit_all(void);                              /* 0x4e3194 */
extern void service_even_ai_fn_004982d4(uint8_t value);                  /* 0x4982d4 */
extern void service_even_ai_reset_all_497db4(void);
extern uint8_t audio_ux_get_system_ble_status(void);                     /* UX_GetSystemBLEStatus 0x47d8ce */
extern uint32_t audio_even_ai_app_acquire_54f380(uint32_t app);          /* AUDM_appAcquire */
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t app);   /* AUDM_appRelease */
extern void audio_tracepoint_reset_pull_478110(uint8_t delayed);         /* ble_state_skip_manual_start */
extern void audio_ble_param_reset_delayed_event(uint32_t delay);         /* ble_param_reset_delayed_event */

/* even_ai_ui.c / even_ai_animation.c (g2-ui-even-ai, g2-even-ai-animation). */
extern void even_ai_stream_on_auto_reflash(void);                         /* 0x4e571a */
extern void even_ai_stream_phase_update(uint8_t phase, uint16_t value);   /* 0x4e5a0e */
extern int32_t even_ai_stream_event_forward(uint32_t code, const void *event); /* 0x4e5b48 */
extern int32_t EvenAI_InputEventWarp(const uint8_t *data, uint32_t len);  /* 0x4e5c1c */
extern void even_ai_ui_reflash(void *page);                               /* 0x4e6c44 */
extern void even_ai_page_init(void *page);                                /* 0x4e7170 */
extern void even_ai_page_deinit(void);                                    /* 0x4e74cc */
extern void even_ai_animation_process_5538d8(void);
extern void even_ai_animation_apply_sync_553d64(uint8_t phase, uint32_t tick);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char page_tag[] = "even_ai.page"; /* ROM 0x785de0 */
static const char page_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai.c"; /* ROM 0x70b3a4 */
static const char ui_event_fn[] = "EvenAI_ui_event_handler";    /* ROM 0x77712c */
static const char init_msg[] = "UI_EVENT_TYPE_INIT";            /* ROM 0x77f324 */
static const char init_short[] = "[even_ai.page]UI_EVENT_TYPE_INIT"; /* ROM 0x7543a4 */
static const char exit_msg[] = "UI_EVENT_TYPE_EXIT";            /* ROM 0x77f338 */
static const char exit_short[] = "[even_ai.page]UI_EVENT_TYPE_EXIT"; /* ROM 0x7543c8 */

/* Click is consumed without action; other page inputs are forwarded to the
 * stream unless this arm is the slave. */
uint32_t even_ai_input_event_handler_4e2a5c(void *obj, void *user, uint32_t code, const void *event) {
    (void)obj;
    (void)user;
    if (code == INPUT_CLICK) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        return 1u;
    }
    if (code == INPUT_CLOSE) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)even_ai_stream_event_forward(code, event);
        return 1u;
    }
    if (code == INPUT_SCROLL_UP) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)even_ai_stream_event_forward(code, event);
        return 1u;
    }
    if (code == INPUT_SCROLL_DOWN) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)even_ai_stream_event_forward(code, event);
        return 1u;
    }
    if (code == 0x40u)
        return 1u;
    return 1u;
}

/* EvenAI reflash event handler (UI_EVENT_TYPE_REFLASH payloads). */
uint32_t even_ai_reflash_event_handler_4e2ad6(const uint8_t *data, uint32_t len) {
    if (data == 0 || len == 0u) {
        even_ai_ui_reflash(g2_even_ai_page);
        return 0u;
    }
    if (audio_even_ai_local_decode_498092((uint32_t)(uintptr_t)data, len) == 0) {
        audio_even_ai_ready_4e20f2(1u);
        even_ai_ui_reflash(g2_even_ai_page);
        return 0u;
    }
    switch (data[0]) {
    case 3u:
        even_ai_ui_reflash(g2_even_ai_page);
        break;
    case 4u:
        if (g2_even_ai_anim_busy == 0u) {
            (void)EvenAI_InputEventWarp(data, len);
        } else if ((data[1] == INPUT_SCROLL_UP || data[1] == INPUT_SCROLL_DOWN) &&
                   g2_even_ai_anim_busy == 1u) {
            (void)EvenAI_InputEventWarp(data, len);
        } else {
            (void)ui_common_api_fn_00509ca2(g2_even_ai_event_fifo, data, (uint16_t)len);
        }
        break;
    case 5u:
        even_ai_stream_phase_update(data[1], (uint16_t)(data[2] | ((uint32_t)data[3] << 8)));
        break;
    case 6u:
        if (len >= 6u)
            even_ai_animation_apply_sync_553d64(
                data[1], (uint32_t)data[2] | ((uint32_t)data[3] << 8) |
                             ((uint32_t)data[4] << 16) | ((uint32_t)data[5] << 24));
        break;
    case 8u: {
        uint8_t *service = audio_even_ai_service_state_2006ed10;
        uint8_t *ready = audio_even_ai_ready_state_2006f138;
        even_ai_stream_phase_update(data[1], (uint16_t)(data[2] | ((uint32_t)data[3] << 8)));
        audio_even_ai_state_lock_4e1fa6();
        service_even_ai_fn_004982d4(data[2]);
        if (audio_ux_get_system_ble_status() == 1u) {
            (void)audio_even_ai_app_acquire_54f380(AUDM_APP_EVEN_AI);
            (void)audio_even_ai_timer_start_all_4e31a0(5000u);
        } else {
            service[1] = 7u;
            service[2] = 2u;
            (void)audio_even_ai_timer_start_all_4e31a0(3000u);
        }
        if (ready[0] == 3u || ready[0] == 4u)
            audio_even_ai_stop_current_streaming_4e557c(0u);
        else
            audio_even_ai_stop_current_streaming_4e557c(1u);
        ready[0] = service[1];
        ready[1] = service[2];
        audio_even_ai_state_unlock_4e1fbe();
        even_ai_ui_reflash(g2_even_ai_page);
        break;
    }
    default:
        break;
    }
    return 0u;
}

/* EvenAI_ui_event_handler: UI registry slot 5 (ROM 0x6a4500). */
uint32_t audio_uart_registry_callback_4e2c40(uint32_t event, const uint8_t *data, uint32_t len,
                                             void *parent) {
    if (event == UI_EVENT_TYPE_INIT) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, page_tag, page_file, ui_event_fn, 0x353u, init_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, init_short, init_short);
        audio_even_ai_prepare_4e1f7c();
        audio_tracepoint_reset_pull_478110(0u);
        g2_even_ai_page = audio_uart_page_43de82(parent);
        *(void **)(void *)(&audio_uart_registry_context_200009a4 + 4) = g2_even_ai_page;
        even_ai_page_init(g2_even_ai_page);
    } else if (event == UI_EVENT_TYPE_REFLASH) {
        (void)even_ai_reflash_event_handler_4e2ad6(data, len);
    } else if (event == UI_EVENT_TYPE_TIMER) {
        even_ai_stream_on_auto_reflash();
        even_ai_animation_process_5538d8();
        even_ai_timer_process_all();
    } else if (event == UI_EVENT_TYPE_EXIT) {
        uint8_t *ready = audio_even_ai_ready_state_2006f138;
        service_even_ai_reset_all_497db4();
        if (ready[0] != 6u || (ready[1] != 2u && ready[1] != 4u))
            service_even_ai_fn_004982d4(3u);
        (void)audio_terminal_reset_mode_notice_54f50e(AUDM_APP_EVEN_AI);
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, page_tag, page_file, ui_event_fn, 0x376u, exit_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x0c000000u, exit_short, exit_short);
        audio_even_ai_state_lock_4e1fa6();
        even_ai_timer_deinit_all();
        audio_uart_buffer_zero(ready, 0x210u, 0u);
        audio_uart_buffer_zero(audio_even_ai_text_pending_200f39b4, 0x400u, 0u);
        audio_uart_buffer_zero(audio_even_ai_text_merged_200f3db4, 0x400u, 0u);
        audio_even_ai_state_unlock_4e1fbe();
        even_ai_page_deinit();
        audio_ble_param_reset_delayed_event(10000u);
    }
    return 0u;
}
