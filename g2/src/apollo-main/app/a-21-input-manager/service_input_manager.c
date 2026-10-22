/* Input manager (temple touch bars and ring touch), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\input\service_input_manager.c.
 * Native 0x4c5886..0x4c5916 and 0x4c59aa..0x4c6148 (INPM_EventSend at
 * 0x4c5916 lives in drivers/peripherals/ring-touch); literal pool
 * 0x4c6148..0x4c6240.
 *
 * Input event record (12 bytes, message 0x108): +0 u16 device type
 * (0 left touch bar, 1 right touch bar, 4 ring), +4 u32 event id (0 single,
 * 1 double, 3 long press, 4 up-roll, 5 down-roll, 13 press, 14 release,
 * 0x1010 deca click), +8 u8 diffx, +9 u8 speed.
 *
 * Arbitration: the first device to deliver an event owns UI injection until it
 * releases (event 14) or 1000 ms pass without its events. Pressing both
 * temple bars within 1000 ms of each other and holding 1000 ms toggles silent
 * mode, and while both are held no event reaches the UI. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t dev_type; /* +0 */
    uint16_t pad;      /* +2 */
    uint32_t event_id; /* +4 */
    uint8_t diffx;     /* +8 */
    uint8_t speed;     /* +9 */
    uint8_t pad2[2];   /* +10 */
} g2_input_event_t;
_Static_assert(sizeof(g2_input_event_t) == 12u, "stock input event is 12 bytes");

enum {
    INPM_DEV_LEFT = 0u, INPM_DEV_RIGHT = 1u, INPM_DEV_RING = 4u,
    INPM_EVT_UPROLL = 4u, INPM_EVT_DOWNROLL = 5u,
    INPM_EVT_PRESS = 13u, INPM_EVT_RELEASE = 14u, INPM_EVT_DECA_CLICK = 0x1010u,
    INPM_DEV_NONE = 0xffffu
};

extern uint32_t g2_inpm_left_press_tick;     /* RAM 0x2007497c g_left_press_tick */
extern uint32_t g2_inpm_right_press_tick;    /* RAM 0x20074980 g_right_press_tick */
extern uint32_t g2_inpm_last_inject_tick;    /* RAM 0x20074984 */
extern uint32_t g2_inpm_current_dev_type;    /* RAM 0x200036f8 (initialised data, 0xffff = none) */
extern uint32_t g2_inpm_tp_press_tick[3];    /* RAM 0x20074098, index left/right/ring */
extern uint32_t g2_inpm_tp_release_tick[3];  /* RAM 0x200740a4 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t osKernelGetTickCount(void); /* 0x4490cc */
extern void SilentMode_ToggleByLocalLongPress(void); /* 0x469388 */
extern uint32_t onboarding_should_run(void); /* 0x468034 */
extern uint32_t settings_get_terminal_mode(void); /* 0x46c630 */
extern uint32_t SVC_Settings_InputEventCheck(void); /* 0x46b0ec */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay_ms); /* 0x47697e */
extern int32_t iar_abs_509694(int32_t value); /* 0x509694 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload); /* tracepoint record */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568, 2 = slave */
extern void audio_uart_buffer_zero(void *destination, uint32_t length, uint32_t fill); /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *destination, const void *source, uint32_t length); /* 0x439be4 */
extern void audio_uart_master_display_start(uint32_t id, const void *payload, uint16_t length, uint32_t extra); /* 0x464b2e */
extern int32_t audio_uart_master_input_event(uint32_t device, uint32_t event, uint32_t value, uint32_t context); /* 0x465748 SendInputEventToPeers */

static const char module_tag[] = "input.manager"; /* ROM 0x7889e0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\input\\service_input_manager.c"; /* ROM 0x6f5e5c */
static const char name_press[] = "PRESS"; /* ROM 0x78e554 */
static const char name_release[] = "RELEASE"; /* ROM 0x78e55c */
static const char name_single[] = "SINGLE_CLICK"; /* ROM 0x788990 */
static const char name_double[] = "DOUBLE_CLICK"; /* ROM 0x7889a0 */
static const char name_long[] = "LONG_PRESS"; /* ROM 0x78bf3c */
static const char name_uproll[] = "UPROLL"; /* ROM 0x78e564 */
static const char name_downroll[] = "DOWNROLL"; /* ROM 0x78bf48 */
static const char name_deca[] = "DECA_CLICK"; /* ROM 0x78bf54 */
static const char name_unknown[] = "UNKNOWN"; /* ROM 0x78e56c */
static const char name_left[] = "TOUCH_BAR_LEFT"; /* ROM 0x7889b0 */
static const char name_right[] = "TOUCH_BAR_RIGHT"; /* ROM 0x7889c0 */
static const char name_ring[] = "RING_TOUCH_SENSOR"; /* ROM 0x7832a8 */
static const char check_fn[] = "INPM_BothLongPressEventCheck"; /* ROM 0x764ed0 */
static const char not_both[] = "not both long press event"; /* ROM 0x771268 */
static const char not_both_short[] = "[input.manager]not both long press event"; /* ROM 0x743284 */
static const char both[] = "both long press event"; /* ROM 0x77b86c */
static const char both_short[] = "[input.manager]both long press event"; /* ROM 0x74de94 */
static const char process_fn[] = "INPM_BothLongPressEventProcess"; /* ROM 0x764ef0 */
static const char onboarding[] = "onboarding is running, not process both long press event"; /* ROM 0x7185e0 */
static const char onboarding_short[] =
    "[input.manager]onboarding is running, not process both long press event"; /* ROM 0x6fcdac */
static const char ticks[] = "g_left_press_tick = %d, g_right_press_tick = %d"; /* ROM 0x738444 */
static const char ticks_short[] = "[input.manager]g_left_press_tick = %d, g_right_press_tick = %d"; /* ROM 0x70eca4 */
static const char interval_text[] = "interval = %d"; /* ROM 0x7889f0 */
static const char interval_short[] = "[input.manager]interval = %d"; /* ROM 0x764f10 */
static const char start_check[] = "start both long press event check"; /* ROM 0x759ab0 */
static const char start_check_short[] = "[input.manager]start both long press event check"; /* ROM 0x72d4b8 */
static const char tracepoint_fn[] = "INPM_TouchTracepoint"; /* ROM 0x77b884 */
static const char tp_ring[] = "[TP] ring_touch_release duration=%ums"; /* ROM 0x74debc */
static const char tp_ring_short[] = "[input.manager][TP] ring_touch_release duration=%ums"; /* ROM 0x722c10 */
static const char tp_glasses[] = "[TP] glasses_touch_release duration=%ums temple=%u"; /* ROM 0x72d4ec */
static const char tp_glasses_short[] =
    "[input.manager][TP] glasses_touch_release duration=%ums temple=%u"; /* ROM 0x705958 */
static const char recv_fn[] = "INPM_EventRecvHandler"; /* ROM 0x77b89c */
static const char roll_text[] = "%s(%d), %s(%d), diffx = %d, speed = %d"; /* ROM 0x74dee4 */
static const char roll_short[] = "[input.manager]%s(%d), %s(%d), diffx = %d, speed = %d"; /* ROM 0x722c48 */
static const char event_text[] = "%s(%d), %s(%d)"; /* ROM 0x788a00 */
static const char event_short[] = "[input.manager]%s(%d), %s(%d)"; /* ROM 0x764f30 */
static const char owner_text[] = "current input dev type is %d, inject to UI layer"; /* ROM 0x72d520 */
static const char owner_short[] = "[input.manager]current input dev type is %d, inject to UI layer"; /* ROM 0x70ece4 */
static const char timeout_text[] =
    "current input time is greater than the timeout time, inject to UI layer"; /* ROM 0x6fcdf4 */
static const char timeout_short[] =
    "[input.manager]current input time is greater than the timeout time, inject to UI layer"; /* ROM 0x6e4d20 */
static const char busy_text[] = "other device is using, not inject to UI layer"; /* ROM 0x738474 */
static const char busy_short[] = "[input.manager]other device is using, not inject to UI layer"; /* ROM 0x70ed24 */
static const char reject_text[] = "both long press event, reject other event to inject to UI layer"; /* ROM 0x70ed64 */
static const char reject_short[] =
    "[input.manager]both long press event, reject other event to inject to UI layer"; /* ROM 0x6ef9a8 */
static const char check_failed[] = "input event check failed, do not inject to UI layer"; /* ROM 0x72d554 */
static const char check_failed_short[] =
    "[input.manager]input event check failed, do not inject to UI layer"; /* ROM 0x70599c */
static const char peers_text[] =
    "send input event to peers, input dev type = %d, event id = %d, event value = 0x%02x"; /* ROM 0x6e9c40 */
static const char peers_short[] =
    "[input.manager]send input event to peers, input dev type = %d, event id = %d, event value = 0x%02x"; /* ROM 0x6db8d0 */

#define LOG_COMPACT_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

uint32_t inpm_pack_event_value_4c5886(uint8_t diffx, uint8_t speed)
{
    return (uint32_t)speed | ((uint32_t)diffx << 16);
}

const char *inpm_event_id_name_4c5892(uint32_t event_id)
{
    switch (event_id) {
    case 0u: return name_single;
    case 1u: return name_double;
    case 3u: return name_long;
    case 4u: return name_uproll;
    case 5u: return name_downroll;
    case 13u: return name_press;
    case 14u: return name_release;
    case 0x1010u: return name_deca;
    default: return name_unknown;
    }
}

const char *inpm_dev_type_name_4c58ee(uint16_t dev_type)
{
    switch (dev_type) {
    case INPM_DEV_LEFT: return name_left;
    case INPM_DEV_RIGHT: return name_right;
    case INPM_DEV_RING: return name_ring;
    default: return name_unknown;
    }
}

/* Delayed 1000 ms after both bars went down: still both held for >= 1 s? */
void INPM_BothLongPressEventCheck_4c59aa(void)
{
    uint32_t now = osKernelGetTickCount();
    if (now - g2_inpm_left_press_tick < 1000u || now - g2_inpm_right_press_tick < 1000u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module_tag, source_file, check_fn, 0x71u, not_both);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x08000000u, not_both_short, not_both_short);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module_tag, source_file, check_fn, 0x76u, both);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x08000000u, both_short, both_short);
    SilentMode_ToggleByLocalLongPress();
}

void INPM_BothLongPressEventProcess_4c5a58(uint16_t dev_type, uint32_t event_id, uint32_t tick)
{
    if (onboarding_should_run() == 1u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module_tag, source_file, process_fn, 0x7fu, onboarding);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x08000000u, onboarding_short, onboarding_short);
        return;
    }
    if (settings_get_terminal_mode() != 0u)
        return;
    if (dev_type == INPM_DEV_LEFT) {
        if (event_id == INPM_EVT_PRESS)
            g2_inpm_left_press_tick = tick;
        else if (event_id == INPM_EVT_RELEASE)
            g2_inpm_left_press_tick = 0u;
        else
            return;
    } else if (dev_type == INPM_DEV_RIGHT) {
        if (event_id == INPM_EVT_PRESS)
            g2_inpm_right_press_tick = tick;
        else if (event_id == INPM_EVT_RELEASE)
            g2_inpm_right_press_tick = 0u;
        else
            return;
    } else {
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, process_fn, 0xabu, ticks,
                           g2_inpm_left_press_tick, g2_inpm_right_press_tick);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10800000u, ticks_short, ticks_short,
                                  g2_inpm_left_press_tick, g2_inpm_right_press_tick);
    if (g2_inpm_left_press_tick == 0u || g2_inpm_right_press_tick == 0u) {
        (void)fw_event_loop_remove_delayed(INPM_BothLongPressEventCheck_4c59aa);
        return;
    }
    uint32_t interval = (uint32_t)iar_abs_509694(
        (int32_t)(g2_inpm_left_press_tick - g2_inpm_right_press_tick));
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, process_fn, 0xb4u, interval_text, interval);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10400000u, interval_short, interval_short, interval);
    if (interval >= 2001u) {
        (void)fw_event_loop_remove_delayed(INPM_BothLongPressEventCheck_4c59aa);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module_tag, source_file, process_fn, 0xbau, start_check);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x0c000000u, start_check_short, start_check_short);
    fw_event_loop_push_delayed(INPM_BothLongPressEventCheck_4c59aa, 0u, 1000u);
}

uint32_t inpm_both_long_press_active_4c5c30(void)
{
    return (g2_inpm_left_press_tick != 0u && g2_inpm_right_press_tick != 0u) ? 1u : 0u;
}

int32_t inpm_dev_type_index_4c5c4c(uint16_t dev_type)
{
    switch (dev_type) {
    case INPM_DEV_LEFT: return 0;
    case INPM_DEV_RIGHT: return 1;
    case INPM_DEV_RING: return 2;
    default: return -1;
    }
}

/* Touch-release tracepoints. The record is only emitted on the next press
 * that comes more than 5000 ms after the previous release; the reported
 * duration is release + 5000 - press (stock arithmetic, kept as is). */
void INPM_TouchTracepoint_4c5c6e(uint16_t dev_type, uint32_t event_id, uint32_t tick)
{
    int32_t index = inpm_dev_type_index_4c5c4c(dev_type);
    if (index < 0)
        return;
    if (event_id == INPM_EVT_PRESS) {
        if (g2_inpm_tp_press_tick[index] == 0u) {
            g2_inpm_tp_press_tick[index] = tick;
            return;
        }
        if (g2_inpm_tp_release_tick[index] == 0u)
            return;
        if (tick - g2_inpm_tp_release_tick[index] < 5001u)
            return;
        uint32_t duration = g2_inpm_tp_release_tick[index] + 5000u - g2_inpm_tp_press_tick[index];
        if (dev_type == INPM_DEV_RING) {
            uint32_t record[1];
            record[0] = duration;
            audio_uart_ring_wear_persist_48eb32(0x30102u, 1u, record);
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(3u, module_tag, source_file, tracepoint_fn, 0xfeu, tp_ring, duration);
            if (LOG_COMPACT_ON())
                (void)compress_log_output(0x0c400000u, tp_ring_short, tp_ring_short, duration);
        } else {
            uint32_t record[2];
            record[0] = duration;
            record[1] = dev_type;
            audio_uart_ring_wear_persist_48eb32(0x30101u, 2u, record);
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(3u, module_tag, source_file, tracepoint_fn, 0x104u, tp_glasses,
                                   duration, (uint32_t)dev_type);
            if (LOG_COMPACT_ON())
                (void)compress_log_output(0x0c800000u, tp_glasses_short, tp_glasses_short,
                                          duration, (uint32_t)dev_type);
        }
        g2_inpm_tp_press_tick[index] = tick;
        g2_inpm_tp_release_tick[index] = 0u;
    } else if (event_id == INPM_EVT_RELEASE) {
        g2_inpm_tp_release_tick[index] = tick;
    }
}

/* INPM_EventRecvHandler: registry callback for message 0x108 (UI registry
 * slot 23). The copy length is not bounded by the 12-byte record (stock). */
uint32_t audio_uart_registry_callback_4c5dbc(uint32_t id, const void *data, uint32_t length)
{
    (void)id;
    g2_input_event_t event;
    if (audio_uart_device_role_get() == 2u)
        return 0u;
    audio_uart_buffer_zero(&event, 12u, 0u);
    audio_uart_checksum_copy(&event, data, length);
    if (event.event_id == INPM_EVT_UPROLL || event.event_id == INPM_EVT_DOWNROLL) {
        if ((audio_log_flags() & 2u) != 0u) {
            const char *event_name = inpm_event_id_name_4c5892(event.event_id);
            const char *dev_name = inpm_dev_type_name_4c58ee(event.dev_type);
            audio_log_extended(3u, module_tag, source_file, recv_fn, 0x122u, roll_text,
                               dev_name, event.dev_type, event_name, event.event_id,
                               event.diffx, event.speed);
        }
        if (LOG_COMPACT_ON()) {
            const char *event_name = inpm_event_id_name_4c5892(event.event_id);
            const char *dev_name = inpm_dev_type_name_4c58ee(event.dev_type);
            (void)compress_log_output(0x0d800000u, roll_short, roll_short, dev_name,
                                      event.dev_type, event_name, event.event_id,
                                      event.diffx, event.speed);
        }
    } else {
        if ((audio_log_flags() & 2u) != 0u) {
            const char *event_name = inpm_event_id_name_4c5892(event.event_id);
            const char *dev_name = inpm_dev_type_name_4c58ee(event.dev_type);
            audio_log_extended(3u, module_tag, source_file, recv_fn, 0x128u, event_text,
                               dev_name, event.dev_type, event_name, event.event_id);
        }
        if (LOG_COMPACT_ON()) {
            const char *event_name = inpm_event_id_name_4c5892(event.event_id);
            const char *dev_name = inpm_dev_type_name_4c58ee(event.dev_type);
            (void)compress_log_output(0x0d000000u, event_short, event_short, dev_name,
                                      event.dev_type, event_name, event.event_id);
        }
    }
    uint32_t now = osKernelGetTickCount();
    INPM_BothLongPressEventProcess_4c5a58(event.dev_type, event.event_id, now);
    INPM_TouchTracepoint_4c5c6e(event.dev_type, event.event_id, now);

    if (g2_inpm_current_dev_type == INPM_DEV_NONE || g2_inpm_current_dev_type == event.dev_type) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module_tag, source_file, recv_fn, 0x135u, owner_text,
                               g2_inpm_current_dev_type);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x10400000u, owner_short, owner_short,
                                      g2_inpm_current_dev_type);
    } else if (now - g2_inpm_last_inject_tick >= 1001u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module_tag, source_file, recv_fn, 0x13au, timeout_text);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x10000000u, timeout_short, timeout_short);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module_tag, source_file, recv_fn, 0x13fu, busy_text);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x08000000u, busy_short, busy_short);
        return 0u;
    }
    g2_inpm_last_inject_tick = now;
    if (event.event_id == INPM_EVT_RELEASE)
        g2_inpm_current_dev_type = INPM_DEV_NONE;
    else
        g2_inpm_current_dev_type = event.dev_type;

    if (inpm_both_long_press_active_4c5c30() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module_tag, source_file, recv_fn, 0x151u, reject_text);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x08000000u, reject_short, reject_short);
        return 0u;
    }
    if (SVC_Settings_InputEventCheck() == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module_tag, source_file, recv_fn, 0x157u, check_failed);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x08000000u, check_failed_short, check_failed_short);
        return 0u;
    }
    if (event.event_id == INPM_EVT_DECA_CLICK) {
        audio_uart_master_display_start(0x109u, NULL, 0u, 0u);
        return 0u;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, recv_fn, 0x161u, peers_text,
                           event.dev_type, event.event_id,
                           inpm_pack_event_value_4c5886(event.diffx, event.speed));
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10c00000u, peers_short, peers_short, event.dev_type,
                                  event.event_id,
                                  inpm_pack_event_value_4c5886(event.diffx, event.speed));
    (void)audio_uart_master_input_event(event.dev_type, event.event_id,
                                        inpm_pack_event_value_4c5886(event.diffx, event.speed), 0u);
    return 0u;
}
