/* MessageNotify page input, reflash and UI-event handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\message_notify.c.
 * Native 0x4e1c42..0x4e1f27; literal pool 0x4e1f28..0x4e1f7b (shared with
 * MessageNotify_common_data_handler 0x4e1b30 in app/message-notify).
 *
 * The page keeps a 3-byte state at RAM 0x20074714 (+0 phase: 1 init, 2 reflash;
 * +2 auto-close timer armed). While the list is animating (flag RAM 0x2007503c)
 * incoming events are queued in the ui_common_api FIFO at RAM 0x20074cd8 instead
 * of being applied. */
#include <stdint.h>

enum {
    UI_EVENT_TYPE_INIT = 2u,
    UI_EVENT_TYPE_REFLASH = 3u,
    UI_EVENT_TYPE_TIMER = 4u,
    UI_EVENT_TYPE_EXIT = 5u,
};

enum {
    MSG_NOTIF_EVENT_INPUT = 3u,           /* payload: 03 code u32(le) */
    MSG_NOTIF_EVENT_BASICINFO_UPDATE = 4u, /* payload: 04 update_type */
};

enum {
    INPUT_CLICK = 0x0au,
    INPUT_SCROLL_UP = 0x44u,
    INPUT_SCROLL_DOWN = 0x45u,
    INPUT_JUMP = 0x46u,
    INPUT_CLOSE = 0x48u,
};

enum { DEVICE_ROLE_MASTER = 1u, DEVICE_ROLE_SLAVE = 2u };

typedef struct {
    uint8_t phase;       /* +0 */
    uint8_t reserved;    /* +1 */
    uint8_t timer_armed; /* +2 */
} g2_msg_notif_page_state_t;

extern g2_msg_notif_page_state_t g2_msg_notif_page_state; /* RAM 0x20074714 */
extern void *g2_msg_notif_page;                           /* RAM 0x20074710 */
extern uint8_t g2_msg_notif_anim_busy;                    /* RAM 0x2007503c */
extern void *g2_msg_notif_event_fifo;                     /* RAM 0x20074cd8 */
extern uint8_t audio_message_notify_startup_state_20074fe5; /* RAM 0x20074fe5 */
extern uint8_t audio_uart_registry_context_20002cc4;        /* RAM 0x20002cc4, +4 page object */

extern uint8_t audio_uart_device_role_get(void);                           /* 0x45a568 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_uart_page_43de82(void *parent);                         /* lv_obj_create */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t flags);
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* fifo_push */

/* ui_msg_notif_list.c / msg_notif_timer.c (g2-ui-msg-notif-list). */
extern uint32_t msg_notif_input_forward_550334(uint32_t code, const void *event);
extern void msg_notif_virtual_scroll_tileview_550820(int32_t direction);
extern void msg_notif_jump_to_message_absolute_550968(uint32_t index);
extern void msg_notif_add_message_5511ce(void *page);
extern void msg_notif_remove_current_message_551240(void);
extern void message_notify_ui_reflash_551ed8(void *page, uint8_t animate);
extern void message_notify_page_init_55225c(void *page);
extern void message_notify_page_deinit_552820(void);
extern void msg_notif_timer_mgr_init_5528b8(void);
extern void msg_notif_timer_mgr_deinit_552906(void);
extern uint32_t msg_notif_timer_mgr_check_timeout_5529e4(void);
extern void msg_notif_timer_mgr_process_timeout_552a4a(void);
extern void msg_notif_timer_start_552ab0(void);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char page_tag[] = "message_notify.page"; /* ROM 0x7812c8 */
static const char page_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\message_notify.c"; /* ROM 0x6f45b8 */
static const char reflash_fn[] = "MessageNotify_ReflashEventHandler"; /* ROM 0x756b4c */
static const char basicinfo_msg[] = "MSG_NOTIF_EVENT_BASICINFO_UPDATE, update_type = %d"; /* ROM 0x72ae20 */
static const char basicinfo_short[] =
    "[message_notify.page]MSG_NOTIF_EVENT_BASICINFO_UPDATE, update_type = %d"; /* ROM 0x6fb654 */
static const char ui_event_fn[] = "MessageNotify_ui_event_handler";            /* ROM 0x7624f0 */
static const char init_msg[] = "UI_EVENT_TYPE_INIT";                           /* ROM 0x7812dc */
static const char init_short[] = "[message_notify.page]UI_EVENT_TYPE_INIT";    /* ROM 0x74b4dc */
static const char exit_msg[] = "UI_EVENT_TYPE_EXIT";                           /* ROM 0x7812f0 */
static const char exit_short[] = "[message_notify.page]UI_EVENT_TYPE_EXIT";    /* ROM 0x74b504 */

/* Input events on the page are only acted on by the master/unbound arm; the
 * slave (role 2) forwards nothing. Always reports the event as consumed. */
uint32_t message_notify_input_event_handler_4e1c42(void *obj, void *user, uint32_t code,
                                                   const void *event) {
    (void)obj;
    (void)user;
    if (code == INPUT_CLICK) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)msg_notif_input_forward_550334(code, event);
        return 1u;
    }
    if (code == INPUT_CLOSE) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)msg_notif_input_forward_550334(code, event);
        return 1u;
    }
    if (code == INPUT_SCROLL_UP) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)msg_notif_input_forward_550334(code, event);
        return 1u;
    }
    if (code == INPUT_SCROLL_DOWN) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)msg_notif_input_forward_550334(code, event);
        return 1u;
    }
    if (code == 0x40u)
        return 1u;
    return 1u;
}

/* MessageNotify_ReflashEventHandler. */
uint32_t message_notify_reflash_event_handler_4e1cc4(const uint8_t *data, uint32_t len) {
    if (data == 0 || len == 0u) {
        message_notify_ui_reflash_551ed8(g2_msg_notif_page, 0u);
        return 0u;
    }
    if (data[0] == MSG_NOTIF_EVENT_INPUT) {
        uint8_t code = data[1];
        uint32_t value = (uint32_t)data[2] | ((uint32_t)data[3] << 8) |
                         ((uint32_t)data[4] << 16) | ((uint32_t)data[5] << 24);
        if (g2_msg_notif_anim_busy != 0u) {
            (void)ui_common_api_fn_00509ca2(g2_msg_notif_event_fifo, data, 6u);
        } else if (code == INPUT_CLICK) {
            msg_notif_remove_current_message_551240();
        } else if (code == INPUT_CLOSE) {
            if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
                audio_system_alert_close_464c36(4u, 0u, 0u, 0u);
        } else if (code == INPUT_SCROLL_UP) {
            msg_notif_virtual_scroll_tileview_550820(1);
        } else if (code == INPUT_SCROLL_DOWN) {
            msg_notif_virtual_scroll_tileview_550820(-1);
        } else if (code == INPUT_JUMP) {
            msg_notif_jump_to_message_absolute_550968(value);
        }
    } else if (data[0] == MSG_NOTIF_EVENT_BASICINFO_UPDATE) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, page_tag, page_file, reflash_fn, 0xebu, basicinfo_msg, data[1]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x0c400000u, basicinfo_short, basicinfo_short, data[1]);
        if (data[1] == 1u) {
            if (g2_msg_notif_anim_busy != 0u)
                (void)ui_common_api_fn_00509ca2(g2_msg_notif_event_fifo, data, (uint16_t)len);
            else
                msg_notif_add_message_5511ce(g2_msg_notif_page);
        }
    }
    return 0u;
}

/* MessageNotify_ui_event_handler: UI registry slot 13 (ROM 0x6a4580).
 * Startup mode written by MessageNotify_common_data_handler: 1 arms the
 * auto-close timer, 2 cancels it; it is consumed once. */
uint32_t audio_uart_registry_callback_4e1dd4(uint32_t event, const uint8_t *data, uint32_t len,
                                             void *parent) {
    g2_msg_notif_page_state_t *state = &g2_msg_notif_page_state;

    if (event == UI_EVENT_TYPE_INIT) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, page_tag, page_file, ui_event_fn, 0x103u, init_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, init_short, init_short);
        audio_uart_buffer_zero(state, 3u, 0u);
        state->phase = 1u;
        g2_msg_notif_page = audio_uart_page_43de82(parent);
        *(void **)(void *)(&audio_uart_registry_context_20002cc4 + 4) = g2_msg_notif_page;
        message_notify_page_init_55225c(g2_msg_notif_page);
        if (audio_message_notify_startup_state_20074fe5 == 1u) {
            audio_message_notify_startup_state_20074fe5 = 0u;
            state->timer_armed = 1u;
            msg_notif_timer_mgr_init_5528b8();
            if (len != 0u)
                msg_notif_timer_start_552ab0();
        } else if (audio_message_notify_startup_state_20074fe5 == 2u) {
            audio_message_notify_startup_state_20074fe5 = 0u;
            state->timer_armed = 0u;
            msg_notif_timer_mgr_deinit_552906();
        }
    } else if (event == UI_EVENT_TYPE_REFLASH) {
        state->phase = 2u;
        (void)message_notify_reflash_event_handler_4e1cc4(data, len);
        if (audio_message_notify_startup_state_20074fe5 == 1u) {
            audio_message_notify_startup_state_20074fe5 = 0u;
            state->timer_armed = 1u;
            msg_notif_timer_mgr_init_5528b8();
        } else if (audio_message_notify_startup_state_20074fe5 == 2u) {
            audio_message_notify_startup_state_20074fe5 = 0u;
            state->timer_armed = 0u;
            msg_notif_timer_mgr_deinit_552906();
        }
        if (state->timer_armed == 1u)
            msg_notif_timer_start_552ab0();
    } else if (event == UI_EVENT_TYPE_TIMER) {
        if (msg_notif_timer_mgr_check_timeout_5529e4() != 0u)
            msg_notif_timer_mgr_process_timeout_552a4a();
    } else if (event == UI_EVENT_TYPE_EXIT) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, page_tag, page_file, ui_event_fn, 0x134u, exit_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x0c000000u, exit_short, exit_short);
        msg_notif_timer_mgr_deinit_552906();
        audio_uart_buffer_zero(state, 3u, 0u);
        audio_message_notify_startup_state_20074fe5 = 0u;
        message_notify_page_deinit_552820();
    }
    return 0u;
}
