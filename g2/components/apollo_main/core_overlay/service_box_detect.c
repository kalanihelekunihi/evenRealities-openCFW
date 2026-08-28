/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room source replacement for the G2 2.2.6.10 box-detect service.
 * Diagnostics are intentionally excluded; the state, timer, case-sync,
 * display, ring-reconnect and device-manager effects are preserved.
 */

typedef unsigned char box_u8;
typedef unsigned short box_u16;
typedef unsigned int box_u32;

typedef struct {
    box_u16 type;
    box_u16 length;
    box_u8 event;
    box_u8 reserved[3];
} box_detect_event;

void *open_cfw_retained_box_detect_memcpy(void *, const void *, box_u32);
void *open_cfw_retained_box_detect_memset(void *, int, box_u32);
void *open_cfw_retained_box_detect_timer_new(
    void (*)(void *), box_u32, void *, const void *
);
int open_cfw_retained_box_detect_timer_start(void *, box_u32);
int open_cfw_retained_box_detect_timer_stop(void *);
int open_cfw_retained_box_detect_timer_is_running(void *);
int open_cfw_retained_box_detect_timer_delete(void *);
int open_cfw_retained_box_detect_display_ready(void);
int open_cfw_retained_box_detect_should_publish_status(void);
box_u8 open_cfw_retained_box_detect_lens_side(void);
int open_cfw_retained_box_detect_send_notification(
    box_u32, const void *, box_u32, box_u32, box_u32
);
int open_cfw_retained_box_detect_send_sync(
    box_u32, const void *, box_u32, box_u32, box_u32
);
int open_cfw_retained_box_detect_display_is_active(void);
void open_cfw_retained_box_detect_display_open(void);
void open_cfw_retained_box_detect_display_close(void);
void open_cfw_retained_box_detect_ring_state_changed(void);
int open_cfw_retained_box_detect_ring_reconnect(void);
int open_cfw_retained_box_detect_ring_reconnect_queue(box_u8);
box_u8 open_cfw_retained_box_detect_product_mode(void);
int open_cfw_retained_box_detect_queue(const void *);
box_u8 *open_cfw_retained_box_detect_device_state(box_u32);
int open_cfw_retained_box_detect_case_request(const box_u8 *, box_u16);
int open_cfw_retained_box_detect_case_status(box_u32, const void *);
int open_cfw_retained_box_detect_case_interrupt(box_u32);
void open_cfw_retained_box_detect_input_out(void);

#ifndef OPEN_CFW_BOX_DETECT_TIMER_FORCE
#define OPEN_CFW_BOX_DETECT_TIMER_FORCE \
    (*(void *volatile *)0x20074920U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_TIMER_RECONNECT
#define OPEN_CFW_BOX_DETECT_TIMER_RECONNECT \
    (*(void *volatile *)0x20074924U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_LOCAL_STATE
#define OPEN_CFW_BOX_DETECT_LOCAL_STATE \
    ((volatile box_u8 *)0x20074928U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_RING_CONNECTED
#define OPEN_CFW_BOX_DETECT_RING_CONNECTED \
    (*(volatile box_u8 *)0x20075010U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_RING_RECONNECT
#define OPEN_CFW_BOX_DETECT_RING_RECONNECT \
    (*(volatile box_u8 *)0x20075011U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_FORCE_OUT
#define OPEN_CFW_BOX_DETECT_FORCE_OUT \
    (*(volatile box_u8 *)0x20075012U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_LAST_LOCAL_STATE
#define OPEN_CFW_BOX_DETECT_LAST_LOCAL_STATE \
    ((volatile box_u8 *)0x200036D8U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_CASE_STATE
#define OPEN_CFW_BOX_DETECT_CASE_STATE \
    ((volatile box_u8 *)0x20074188U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_CASE_IRQ_CONTEXT
#define OPEN_CFW_BOX_DETECT_CASE_IRQ_CONTEXT ((box_u32)0x20070F78U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_CASE_IRQ_OK
#define OPEN_CFW_BOX_DETECT_CASE_IRQ_OK ((box_u32)0x2BAD0000U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_TIMER_FORCE_ATTRIBUTES
#define OPEN_CFW_BOX_DETECT_TIMER_FORCE_ATTRIBUTES ((const void *)0x00788750U)
#endif
#ifndef OPEN_CFW_BOX_DETECT_TIMER_RECONNECT_ATTRIBUTES
#define OPEN_CFW_BOX_DETECT_TIMER_RECONNECT_ATTRIBUTES ((const void *)0x00788760U)
#endif
#if defined(OPEN_CFW_BOX_DETECT_PUBLISH_STATUS_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 1
#elif defined(OPEN_CFW_BOX_DETECT_REFRESH_DISPLAY_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 2
#elif defined(OPEN_CFW_BOX_DETECT_SET_WEAR_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 3
#elif defined(OPEN_CFW_BOX_DETECT_CLEAR_FORCE_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 4
#elif defined(OPEN_CFW_BOX_DETECT_TIMER_FORCE_CALLBACK_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 5
#elif defined(OPEN_CFW_BOX_DETECT_TIMER_RECONNECT_CALLBACK_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 6
#elif defined(OPEN_CFW_BOX_DETECT_TIMERS_INIT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 7
#elif defined(OPEN_CFW_BOX_DETECT_TIMERS_DEINIT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 8
#elif defined(OPEN_CFW_BOX_DETECT_FORCE_TIMER_EXPIRED_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 9
#elif defined(OPEN_CFW_BOX_DETECT_FORCE_TIMER_START_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 10
#elif defined(OPEN_CFW_BOX_DETECT_NOTIFY_DEVICE_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 11
#elif defined(OPEN_CFW_BOX_DETECT_TRY_RECONNECT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 12
#elif defined(OPEN_CFW_BOX_DETECT_HANDLE_EVENT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 13
#elif defined(OPEN_CFW_BOX_DETECT_GET_WEAR_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 14
#elif defined(OPEN_CFW_BOX_DETECT_SET_FORCE_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 15
#elif defined(OPEN_CFW_BOX_DETECT_GET_FORCE_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 16
#elif defined(OPEN_CFW_BOX_DETECT_NOTIFY_FORCE_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 17
#elif defined(OPEN_CFW_BOX_DETECT_SET_LOCAL_LEVEL_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 18
#elif defined(OPEN_CFW_BOX_DETECT_GET_LOCAL_LEVEL_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 19
#elif defined(OPEN_CFW_BOX_DETECT_SET_LOCAL_CHARGING_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 20
#elif defined(OPEN_CFW_BOX_DETECT_GET_LOCAL_CHARGING_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 21
#elif defined(OPEN_CFW_BOX_DETECT_SET_LOCAL_LID_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 22
#elif defined(OPEN_CFW_BOX_DETECT_GET_LOCAL_LID_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 23
#elif defined(OPEN_CFW_BOX_DETECT_IS_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 24
#elif defined(OPEN_CFW_BOX_DETECT_GET_LOCAL_STATE_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 25
#elif defined(OPEN_CFW_BOX_DETECT_STATE_UPDATED_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 26
#elif defined(OPEN_CFW_BOX_DETECT_SEND_STATE_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 27
#elif defined(OPEN_CFW_BOX_DETECT_PROCESS_CASE_STATE_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 28
#elif defined(OPEN_CFW_BOX_DETECT_GET_EFFECTIVE_LEVEL_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 29
#elif defined(OPEN_CFW_BOX_DETECT_GET_EFFECTIVE_CHARGING_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 30
#elif defined(OPEN_CFW_BOX_DETECT_GET_EFFECTIVE_LID_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 31
#elif defined(OPEN_CFW_BOX_DETECT_GET_EFFECTIVE_WEAR_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 32
#elif defined(OPEN_CFW_BOX_DETECT_EFFECTIVE_OUT_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 33
#elif defined(OPEN_CFW_BOX_DETECT_COMMON_DATA_ONLY)
#define OPEN_CFW_BOX_DETECT_SELECTOR 34
#elif !defined(OPEN_CFW_BOX_DETECT_SELECTOR)
#define OPEN_CFW_BOX_DETECT_SELECTOR 0
#endif
#define BOX_BUILD(n) \
    (OPEN_CFW_BOX_DETECT_SELECTOR == 0 || OPEN_CFW_BOX_DETECT_SELECTOR == (n))

void open_cfw_box_detect_publish_status(void);
void open_cfw_box_detect_refresh_display(void);
void open_cfw_box_detect_set_wear_out(box_u8 value);
void open_cfw_box_detect_clear_force_on_real_out(void);
void open_cfw_box_detect_timer_force_callback(void *argument);
void open_cfw_box_detect_timer_reconnect_callback(void *argument);
void open_cfw_box_detect_timers_init(void);
void open_cfw_box_detect_timers_deinit(void);
void open_cfw_box_detect_force_timer_expired(void);
void open_cfw_box_detect_force_timer_start(void);
void open_cfw_box_detect_notify_device(box_u8 event);
void open_cfw_box_detect_try_reconnect(box_u8 scene);
void open_cfw_box_detect_handle_event(const box_detect_event *event);
box_u8 open_cfw_box_detect_get_wear_out(void);
void open_cfw_box_detect_set_force_out(box_u8 value);
box_u8 open_cfw_box_detect_get_force_out(void);
void open_cfw_box_detect_notify_force_out(box_u8 value);
void open_cfw_box_detect_set_local_level(box_u8 value);
box_u8 open_cfw_box_detect_get_local_level(void);
void open_cfw_box_detect_set_local_charging(box_u8 value);
box_u8 open_cfw_box_detect_get_local_charging(void);
void open_cfw_box_detect_set_local_lid(box_u8 value);
box_u8 open_cfw_box_detect_get_local_lid(void);
box_u8 open_cfw_box_detect_is_out(void);
int open_cfw_box_detect_get_local_state(box_u8 *state);
void open_cfw_box_detect_state_updated(void);
void open_cfw_box_detect_send_state(box_u8 message_id);
void open_cfw_box_detect_process_case_state(const box_u8 *message);
box_u8 open_cfw_box_detect_get_effective_level(void);
box_u8 open_cfw_box_detect_get_effective_charging(void);
box_u8 open_cfw_box_detect_get_effective_lid(void);
box_u8 open_cfw_box_detect_get_effective_wear(void);
box_u8 open_cfw_box_detect_effective_out(void);
int open_cfw_box_detect_common_data(box_u32 type, box_u8 *data, box_u32 length);

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_box_detect_publish_status,%function\n"
    ".type open_cfw_box_detect_refresh_display,%function\n"
    ".type open_cfw_box_detect_set_wear_out,%function\n"
    ".type open_cfw_box_detect_clear_force_on_real_out,%function\n"
    ".type open_cfw_box_detect_timer_force_callback,%function\n"
    ".type open_cfw_box_detect_timer_reconnect_callback,%function\n"
    ".type open_cfw_box_detect_timers_init,%function\n"
    ".type open_cfw_box_detect_timers_deinit,%function\n"
    ".type open_cfw_box_detect_force_timer_expired,%function\n"
    ".type open_cfw_box_detect_force_timer_start,%function\n"
    ".type open_cfw_box_detect_notify_device,%function\n"
    ".type open_cfw_box_detect_try_reconnect,%function\n"
    ".type open_cfw_box_detect_handle_event,%function\n"
    ".type open_cfw_box_detect_get_wear_out,%function\n"
    ".type open_cfw_box_detect_set_force_out,%function\n"
    ".type open_cfw_box_detect_get_force_out,%function\n"
    ".type open_cfw_box_detect_notify_force_out,%function\n"
    ".type open_cfw_box_detect_set_local_level,%function\n"
    ".type open_cfw_box_detect_get_local_level,%function\n"
    ".type open_cfw_box_detect_set_local_charging,%function\n"
    ".type open_cfw_box_detect_get_local_charging,%function\n"
    ".type open_cfw_box_detect_set_local_lid,%function\n"
    ".type open_cfw_box_detect_get_local_lid,%function\n"
    ".type open_cfw_box_detect_is_out,%function\n"
    ".type open_cfw_box_detect_get_local_state,%function\n"
    ".type open_cfw_box_detect_state_updated,%function\n"
    ".type open_cfw_box_detect_send_state,%function\n"
    ".type open_cfw_box_detect_process_case_state,%function\n"
    ".type open_cfw_box_detect_get_effective_level,%function\n"
    ".type open_cfw_box_detect_get_effective_charging,%function\n"
    ".type open_cfw_box_detect_get_effective_lid,%function\n"
    ".type open_cfw_box_detect_get_effective_wear,%function\n"
    ".type open_cfw_box_detect_effective_out,%function\n"
    ".type open_cfw_box_detect_common_data,%function\n"
);
#endif

#if BOX_BUILD(1)
__attribute__((used, noinline))
void open_cfw_box_detect_publish_status(void)
{
    box_u8 payload[5];
    payload[0] = open_cfw_box_detect_get_effective_level();
    payload[1] = open_cfw_box_detect_get_effective_charging();
    payload[2] = open_cfw_box_detect_get_effective_lid();
    payload[3] = open_cfw_box_detect_effective_out();
    payload[4] = 0U;
    if (open_cfw_retained_box_detect_should_publish_status() == 0) {
        (void)open_cfw_retained_box_detect_case_status(0U, payload);
    }
}
#endif

#if BOX_BUILD(2)
__attribute__((used, noinline))
void open_cfw_box_detect_refresh_display(void)
{
    if (open_cfw_retained_box_detect_display_ready() != 0) {
        if (open_cfw_box_detect_effective_out() != 0U) {
            open_cfw_retained_box_detect_display_close();
        } else if (open_cfw_retained_box_detect_display_is_active() != 0) {
            open_cfw_retained_box_detect_display_open();
        }
    }
}
#endif

#if BOX_BUILD(3)
__attribute__((used, noinline))
void open_cfw_box_detect_set_wear_out(box_u8 value)
{
    OPEN_CFW_BOX_DETECT_LOCAL_STATE[3] = value;
    open_cfw_box_detect_state_updated();
}
#endif

#if BOX_BUILD(4)
__attribute__((used, noinline))
void open_cfw_box_detect_clear_force_on_real_out(void)
{
    if (OPEN_CFW_BOX_DETECT_FORCE_OUT != 0U) {
        open_cfw_box_detect_set_force_out(0U);
        open_cfw_box_detect_notify_force_out(0U);
    }
}
#endif

#if BOX_BUILD(5)
__attribute__((used, noinline))
void open_cfw_box_detect_timer_force_callback(void *argument)
{
    (void)argument;
    open_cfw_box_detect_notify_device(1U);
}
#endif

#if BOX_BUILD(6)
__attribute__((used, noinline))
void open_cfw_box_detect_timer_reconnect_callback(void *argument)
{
    (void)argument;
    open_cfw_box_detect_notify_device(7U);
}
#endif

#if BOX_BUILD(7)
__attribute__((used, noinline))
void open_cfw_box_detect_timers_init(void)
{
    if (OPEN_CFW_BOX_DETECT_TIMER_FORCE == (void *)0) {
        OPEN_CFW_BOX_DETECT_TIMER_FORCE = open_cfw_retained_box_detect_timer_new(
            open_cfw_box_detect_timer_force_callback, 0U, (void *)0,
            OPEN_CFW_BOX_DETECT_TIMER_FORCE_ATTRIBUTES
        );
    }
    if (OPEN_CFW_BOX_DETECT_TIMER_RECONNECT == (void *)0) {
        OPEN_CFW_BOX_DETECT_TIMER_RECONNECT =
            open_cfw_retained_box_detect_timer_new(
                open_cfw_box_detect_timer_reconnect_callback, 0U, (void *)0,
                OPEN_CFW_BOX_DETECT_TIMER_RECONNECT_ATTRIBUTES
            );
    }
}
#endif

#if BOX_BUILD(8)
__attribute__((used, noinline))
void open_cfw_box_detect_timers_deinit(void)
{
    if (OPEN_CFW_BOX_DETECT_TIMER_FORCE != (void *)0) {
        (void)open_cfw_retained_box_detect_timer_stop(
            OPEN_CFW_BOX_DETECT_TIMER_FORCE
        );
        (void)open_cfw_retained_box_detect_timer_delete(
            OPEN_CFW_BOX_DETECT_TIMER_FORCE
        );
        OPEN_CFW_BOX_DETECT_TIMER_FORCE = (void *)0;
    }
    if (OPEN_CFW_BOX_DETECT_TIMER_RECONNECT != (void *)0) {
        (void)open_cfw_retained_box_detect_timer_stop(
            OPEN_CFW_BOX_DETECT_TIMER_RECONNECT
        );
        (void)open_cfw_retained_box_detect_timer_delete(
            OPEN_CFW_BOX_DETECT_TIMER_RECONNECT
        );
        OPEN_CFW_BOX_DETECT_TIMER_RECONNECT = (void *)0;
    }
}
#endif

#if BOX_BUILD(9)
__attribute__((used, noinline))
void open_cfw_box_detect_force_timer_expired(void)
{
    if (OPEN_CFW_BOX_DETECT_TIMER_FORCE != (void *)0 &&
        open_cfw_retained_box_detect_timer_is_running(
            OPEN_CFW_BOX_DETECT_TIMER_FORCE
        ) != 0) {
        (void)open_cfw_retained_box_detect_timer_stop(
            OPEN_CFW_BOX_DETECT_TIMER_FORCE
        );
    }
    open_cfw_box_detect_set_wear_out(1U);
}
#endif

#if BOX_BUILD(10)
__attribute__((used, noinline))
void open_cfw_box_detect_force_timer_start(void)
{
    if (OPEN_CFW_BOX_DETECT_TIMER_FORCE != (void *)0) {
        (void)open_cfw_retained_box_detect_timer_start(
            OPEN_CFW_BOX_DETECT_TIMER_FORCE, 3000U
        );
    }
}
#endif

#if BOX_BUILD(11)
__attribute__((used, noinline))
void open_cfw_box_detect_notify_device(box_u8 event)
{
    box_detect_event message;
    if (open_cfw_retained_box_detect_product_mode() == 1U) {
        return;
    }
    message.type = 3U;
    message.length = 1U;
    message.event = event;
    message.reserved[0] = 0U;
    message.reserved[1] = 0U;
    message.reserved[2] = 0U;
    (void)open_cfw_retained_box_detect_queue(&message);
}
#endif

#if BOX_BUILD(12)
__attribute__((used, noinline))
void open_cfw_box_detect_try_reconnect(box_u8 scene)
{
    if (OPEN_CFW_BOX_DETECT_RING_RECONNECT == 0U &&
        OPEN_CFW_BOX_DETECT_RING_CONNECTED == 0U &&
        open_cfw_retained_box_detect_ring_reconnect_queue(scene) != 0) {
        OPEN_CFW_BOX_DETECT_RING_RECONNECT = 1U;
        if (OPEN_CFW_BOX_DETECT_TIMER_RECONNECT != (void *)0) {
            (void)open_cfw_retained_box_detect_timer_start(
                OPEN_CFW_BOX_DETECT_TIMER_RECONNECT, 60000U
            );
        }
    }
}
#endif

#if BOX_BUILD(13)
__attribute__((used, noinline))
void open_cfw_box_detect_handle_event(const box_detect_event *event)
{
    box_u8 code;
    box_u8 *device;
    if (event == (const box_detect_event *)0 || event->length == 0U) {
        return;
    }
    code = event->event;
    if (code == 0U) {
        device = open_cfw_retained_box_detect_device_state(0U);
        if (device != (box_u8 *)0 && device[0] == 1U) {
            (void)open_cfw_retained_box_detect_case_interrupt(
                OPEN_CFW_BOX_DETECT_CASE_IRQ_CONTEXT
            );
        }
    } else if (code == 1U) {
        open_cfw_box_detect_clear_force_on_real_out();
        open_cfw_box_detect_set_wear_out(0U);
        open_cfw_box_detect_try_reconnect(0U);
    } else if (code == 2U) {
        open_cfw_box_detect_clear_force_on_real_out();
        OPEN_CFW_BOX_DETECT_LOCAL_STATE[3] = 0U;
        open_cfw_box_detect_try_reconnect(1U);
        OPEN_CFW_BOX_DETECT_LOCAL_STATE[2] = 0U;
        open_cfw_box_detect_state_updated();
    } else if (code == 3U) {
        OPEN_CFW_BOX_DETECT_RING_CONNECTED = 1U;
        if (OPEN_CFW_BOX_DETECT_TIMER_RECONNECT != (void *)0) {
            (void)open_cfw_retained_box_detect_timer_stop(
                OPEN_CFW_BOX_DETECT_TIMER_RECONNECT
            );
        }
    } else if (code == 4U) {
        OPEN_CFW_BOX_DETECT_RING_CONNECTED = 0U;
        OPEN_CFW_BOX_DETECT_RING_RECONNECT = 0U;
        if (OPEN_CFW_BOX_DETECT_TIMER_RECONNECT != (void *)0) {
            (void)open_cfw_retained_box_detect_timer_stop(
                OPEN_CFW_BOX_DETECT_TIMER_RECONNECT
            );
        }
    } else if (code == 5U) {
        OPEN_CFW_BOX_DETECT_RING_CONNECTED = 0U;
    } else if (code == 6U) {
        OPEN_CFW_BOX_DETECT_RING_RECONNECT = 0U;
        if (OPEN_CFW_BOX_DETECT_TIMER_RECONNECT != (void *)0) {
            (void)open_cfw_retained_box_detect_timer_stop(
                OPEN_CFW_BOX_DETECT_TIMER_RECONNECT
            );
        }
    } else if (code == 7U && OPEN_CFW_BOX_DETECT_RING_RECONNECT != 0U) {
        OPEN_CFW_BOX_DETECT_RING_RECONNECT = 0U;
        (void)open_cfw_retained_box_detect_ring_reconnect();
    }
}
#endif

#if BOX_BUILD(14)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_wear_out(void)
{
    return OPEN_CFW_BOX_DETECT_LOCAL_STATE[3];
}
#endif

#if BOX_BUILD(15)
__attribute__((used, noinline))
void open_cfw_box_detect_set_force_out(box_u8 value)
{
    if (OPEN_CFW_BOX_DETECT_FORCE_OUT == value) {
        return;
    }
    OPEN_CFW_BOX_DETECT_FORCE_OUT = value;
    open_cfw_box_detect_state_updated();
    open_cfw_box_detect_refresh_display();
    open_cfw_box_detect_publish_status();
    open_cfw_retained_box_detect_ring_state_changed();
    if (value != 0U) {
        open_cfw_box_detect_try_reconnect(0U);
    }
}
#endif

#if BOX_BUILD(16)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_force_out(void)
{
    return OPEN_CFW_BOX_DETECT_FORCE_OUT;
}
#endif

#if BOX_BUILD(17)
__attribute__((used, noinline))
void open_cfw_box_detect_notify_force_out(box_u8 value)
{
    box_u8 payload[8];
    box_u8 side;
    open_cfw_retained_box_detect_memset(payload, 0, sizeof(payload));
    side = open_cfw_retained_box_detect_lens_side();
    payload[0] = 4U;
    payload[1] = 1U;
    payload[2] = side;
    payload[3] = side == 1U ? 2U : 1U;
    payload[7] = value == 0U ? 1U : 0U;
    (void)open_cfw_retained_box_detect_send_notification(
        0x81U, payload, sizeof(payload), 0U, 5U
    );
}
#endif

#if BOX_BUILD(18)
__attribute__((used, noinline))
void open_cfw_box_detect_set_local_level(box_u8 value)
{
    OPEN_CFW_BOX_DETECT_LOCAL_STATE[0] = value;
    open_cfw_box_detect_state_updated();
}
#endif

#if BOX_BUILD(19)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_local_level(void)
{
    return OPEN_CFW_BOX_DETECT_LOCAL_STATE[0];
}
#endif

#if BOX_BUILD(20)
__attribute__((used, noinline))
void open_cfw_box_detect_set_local_charging(box_u8 value)
{
    OPEN_CFW_BOX_DETECT_LOCAL_STATE[1] = value;
    open_cfw_box_detect_state_updated();
}
#endif

#if BOX_BUILD(21)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_local_charging(void)
{
    return OPEN_CFW_BOX_DETECT_LOCAL_STATE[1];
}
#endif

#if BOX_BUILD(22)
__attribute__((used, noinline))
void open_cfw_box_detect_set_local_lid(box_u8 value)
{
    OPEN_CFW_BOX_DETECT_LOCAL_STATE[2] = value;
    open_cfw_box_detect_state_updated();
}
#endif

#if BOX_BUILD(23)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_local_lid(void)
{
    return OPEN_CFW_BOX_DETECT_LOCAL_STATE[2];
}
#endif

#if BOX_BUILD(24)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_is_out(void)
{
    return (box_u8)(open_cfw_box_detect_get_wear_out() == 1U ||
                    open_cfw_box_detect_get_local_lid() == 1U);
}
#endif

#if BOX_BUILD(25)
__attribute__((used, noinline))
int open_cfw_box_detect_get_local_state(box_u8 *state)
{
    if (state == (box_u8 *)0) {
        return -1;
    }
    state[0] = OPEN_CFW_BOX_DETECT_LOCAL_STATE[0];
    state[1] = OPEN_CFW_BOX_DETECT_LOCAL_STATE[1];
    state[2] = OPEN_CFW_BOX_DETECT_LOCAL_STATE[2];
    state[3] = OPEN_CFW_BOX_DETECT_LOCAL_STATE[3];
    return 0;
}
#endif

#if BOX_BUILD(26)
__attribute__((used, noinline))
void open_cfw_box_detect_state_updated(void)
{
    box_u8 state[4];
    box_u32 index;
    box_u8 changed = 0U;
    (void)open_cfw_retained_box_detect_lens_side();
    open_cfw_retained_box_detect_memset(state, 0, sizeof(state));
    (void)open_cfw_box_detect_get_local_state(state);
    for (index = 0U; index < 4U; ++index) {
        if (OPEN_CFW_BOX_DETECT_LAST_LOCAL_STATE[index] != state[index]) {
            OPEN_CFW_BOX_DETECT_LAST_LOCAL_STATE[index] = state[index];
            changed = 1U;
        }
    }
    if (changed != 0U) {
        open_cfw_box_detect_send_state(3U);
    }
}
#endif

#if BOX_BUILD(27)
__attribute__((used, noinline))
void open_cfw_box_detect_send_state(box_u8 message_id)
{
    box_u8 payload[8];
    box_u8 side;
    open_cfw_retained_box_detect_memset(payload, 0, sizeof(payload));
    side = open_cfw_retained_box_detect_lens_side();
    payload[0] = message_id;
    payload[1] = 4U;
    payload[2] = side;
    payload[3] = side == 1U ? 2U : 1U;
    (void)open_cfw_box_detect_get_local_state(&payload[4]);
    (void)open_cfw_retained_box_detect_send_sync(
        0x81U, payload, sizeof(payload), 0U, 5U
    );
}
#endif

#if BOX_BUILD(28)
__attribute__((used, noinline))
void open_cfw_box_detect_process_case_state(const box_u8 *message)
{
    box_u8 local[4];
    box_u8 effective[4];
    box_u8 changed = 0U;
    box_u32 index;
    if (message == (const box_u8 *)0) {
        return;
    }
    for (index = 0U; index < 4U; ++index) {
        OPEN_CFW_BOX_DETECT_CASE_STATE[index] = message[4U + index];
    }
    (void)open_cfw_box_detect_get_local_state(local);
    effective[0] = message[4] < local[0] ? message[4] : local[0];
    effective[1] = (box_u8)(local[1] != 0U && message[5] != 0U);
    effective[2] = (box_u8)(local[2] == 1U && message[6] == 1U);
    effective[3] = (box_u8)(local[3] == 1U && message[7] == 1U);
    for (index = 0U; index < 4U; ++index) {
        if (OPEN_CFW_BOX_DETECT_CASE_STATE[4U + index] != effective[index]) {
            OPEN_CFW_BOX_DETECT_CASE_STATE[4U + index] = effective[index];
            changed = 1U;
        }
    }
    if (changed != 0U) {
        if (OPEN_CFW_BOX_DETECT_FORCE_OUT == 0U) {
            open_cfw_box_detect_refresh_display();
            if (effective[3] == 1U) {
                open_cfw_retained_box_detect_input_out();
            }
            open_cfw_retained_box_detect_ring_state_changed();
        }
        open_cfw_box_detect_publish_status();
    }
    if (message[0] == 3U) {
        open_cfw_box_detect_send_state(2U);
    }
}
#endif

#if BOX_BUILD(29)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_effective_level(void)
{
    return OPEN_CFW_BOX_DETECT_CASE_STATE[4];
}
#endif
#if BOX_BUILD(30)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_effective_charging(void)
{
    return OPEN_CFW_BOX_DETECT_CASE_STATE[5];
}
#endif
#if BOX_BUILD(31)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_effective_lid(void)
{
    return OPEN_CFW_BOX_DETECT_CASE_STATE[6];
}
#endif
#if BOX_BUILD(32)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_get_effective_wear(void)
{
    return OPEN_CFW_BOX_DETECT_CASE_STATE[7];
}
#endif

#if BOX_BUILD(33)
__attribute__((used, noinline))
box_u8 open_cfw_box_detect_effective_out(void)
{
    if (OPEN_CFW_BOX_DETECT_FORCE_OUT != 0U) {
        return 0U;
    }
    return (box_u8)(open_cfw_box_detect_get_effective_wear() == 1U ||
                    open_cfw_box_detect_get_effective_lid() == 1U);
}
#endif

#if BOX_BUILD(34)
__attribute__((used, noinline))
int open_cfw_box_detect_common_data(box_u32 type, box_u8 *data, box_u32 length)
{
    if (type == 0U) {
        (void)open_cfw_retained_box_detect_case_request(
            data, (box_u16)length
        );
        return 0;
    }
    if (type != 5U || data == (box_u8 *)0 || length < 8U) {
        return -1;
    }
    if (data[0] == 1U) {
        open_cfw_box_detect_send_state(2U);
    } else if (data[0] == 2U || data[0] == 3U) {
        open_cfw_box_detect_process_case_state(data);
    } else if (data[0] == 4U) {
        open_cfw_box_detect_set_force_out((box_u8)(data[7] == 0U));
    } else {
        return -1;
    }
    return 0;
}
#endif
