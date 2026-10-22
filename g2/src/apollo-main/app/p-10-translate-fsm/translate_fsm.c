/* Translate app state machine, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate_fsm.c (module
 * tag "translate.fsm"). Native 0x596b00..0x597017; literal pool
 * 0x597018..0x5970a7; action table ROM 0x773b88 (7 entries, [0] empty).
 *
 * Same shape as conversate_machine_handler: the phone's translate protobuf
 * events (0..6) dispatch to actions that receive the 16-byte machine context
 * (RAM 0x2011df24: +0 active flag, +1 language pair text[8], +0xc audio flag).
 * Actions post UI events to the translate app (id 5) through 0x59ec28; on the
 * master side (device role 1) open/close also notify the peer with persist
 * keys 0x40101/0x40102 and descriptor {2, 2}. */
#include <stdint.h>
#include <stddef.h>

#define TRANSLATE_EVENT_COUNT 7u
#define TRANSLATE_APP_ID 5u
#define DEVICE_ROLE_MASTER 1u
#define LANGUAGE_PAIR_UNSUPPORTED 8u
#define TRANSLATE_CONTEXT_SIZE 0x10u
#define LANGUAGE_PAIR_SIZE 8u

enum {
    TRANSLATE_UI_CLOSED = 0u,
    TRANSLATE_UI_OPEN = 1u,
    TRANSLATE_UI_CLOSING = 2u,
};

/* UI events posted to the translate page (0x59ec28). */
enum {
    TRANSLATE_UI_EVT_RESULT = 2u,
    TRANSLATE_UI_EVT_START = 4u,
    TRANSLATE_UI_EVT_5 = 5u,
    TRANSLATE_UI_EVT_6 = 6u,
    TRANSLATE_UI_EVT_STOP = 8u,
};

typedef struct {
    uint8_t active;                       /* +0x0 */
    char language_pair[LANGUAGE_PAIR_SIZE]; /* +0x1 */
    uint8_t reserved[3];                  /* +0x9 */
    uint32_t use_audio;                   /* +0xc */
} g2_translate_context_t;
_Static_assert(sizeof(g2_translate_context_t) == TRANSLATE_CONTEXT_SIZE, "stock translate context");

/* App-open payload. */
typedef struct {
    uint16_t reserved;                      /* +0x0 */
    uint16_t language_pair_len;             /* +0x2 */
    char language_pair[LANGUAGE_PAIR_SIZE]; /* +0x4 */
    uint32_t use_audio;                     /* +0xc */
    uint8_t language_pair_status;           /* +0x10, 8 = unsupported */
} g2_translate_open_t;

typedef int32_t (*translate_action_t)(g2_translate_context_t *ctx, const void *data, uint32_t length);

extern g2_translate_context_t g2_translate_session; /* RAM 0x2011df24 (uint8_t[16] in p-14-translate) */
extern const char *g2_translate_event_names[TRANSLATE_EVENT_COUNT]; /* RAM 0x200041a8 */

extern uint8_t translate_ui_0059db5c(void);              /* UI state */
extern const char *translate_ui_0059db66(uint8_t state); /* UI state name */
extern void translate_ui_0059d9d4(void);                 /* force UI closed */
extern void translate_ui_0059e6d0(const void *result);   /* show result */
extern uint32_t translate_request_display_59ec28(uint8_t event, uint32_t value); /* post UI event to app 5 */
extern void translate_buffers_reset_59e9e2(void);
extern uint32_t audio_system_close_active_app_get_443504(uint32_t *background, uint32_t *foreground);
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t, uint32_t, uint32_t);
extern int32_t AUDM_appAcquire(uint32_t user);  /* 0x54f380 */
extern int32_t AUDM_appRelease(uint32_t user);  /* 0x54f50e */
extern void audio_uart_buffer_zero(void *dst, uint32_t size, uint32_t value); /* 0x43c0e4 memset */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "translate.fsm"; /* ROM 0x789c50 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\translate\\translate_fsm.c"; /* ROM 0x6fe5dc */
static const char handler_fn[] = "translate_machine_handler"; /* ROM 0x773b34 */
static const char invalid_event[] = "event is invalid"; /* ROM 0x784568 */
static const char invalid_event_short[] = "[translate.fsm]event is invalid"; /* ROM 0x766f10 */
static const char recv_event[] = "recv event [%d|%s]"; /* ROM 0x78457c */
static const char recv_event_short[] = "[translate.fsm]recv event [%d|%s]"; /* ROM 0x75bf64 */
static const char no_action[] = "event[%d|%s] no match action"; /* ROM 0x766f30 */
static const char no_action_short[] = "[translate.fsm]event[%d|%s] no match action"; /* ROM 0x745a38 */
static const char action_failed[] = "action execution failed"; /* ROM 0x77cff4 */
static const char action_failed_short[] = "[translate.fsm]action execution failed"; /* ROM 0x75043c */
static const char open_fn[] = "translate_action_app_open"; /* ROM 0x773b50 */
static const char null_data[] = "pData is NULL"; /* ROM 0x789c60 */
static const char null_data_short[] = "[translate.fsm]pData is NULL"; /* ROM 0x766f50 */
static const char stuck[] =
    "translate ui stuck in closing while app not running, reset to closed"; /* ROM 0x6fe624 */
static const char stuck_short[] =
    "[translate.fsm]translate ui stuck in closing while app not running, reset to closed"; /* ROM 0x6ea66c */
static const char pair_log[] = "language pair: %s"; /* ROM 0x784590 */
static const char pair_log_short[] = "[translate.fsm]language pair: %s"; /* ROM 0x75bfac */
static const char pair_unsupported[] = "translate language pair not support"; /* ROM 0x75bf88 */
static const char pair_unsupported_short[] =
    "[translate.fsm]translate language pair not support"; /* ROM 0x72f8ac */
static const char bad_state[] = "translate ui state is invalid, no need to start: [%d|%s]"; /* ROM 0x71a5c0 */
static const char bad_state_short[] =
    "[translate.fsm]translate ui state is invalid, no need to start: [%d|%s]"; /* ROM 0x6fe66c */
static const char result_fn[] = "translate_action_result"; /* ROM 0x77d00c */
static const char null_result[] = "translate result data is NULL"; /* ROM 0x766f70 */
static const char null_result_short[] = "[translate.fsm]translate result data is NULL"; /* ROM 0x73a394 */
static const char heartbeat_fn[] = "translate_action_heartbeat"; /* ROM 0x773b6c */
static const char heartbeat_bad[] = "recv heartbeat, translate ui state is invalid: [%d|%s]"; /* ROM 0x724e30 */
static const char heartbeat_bad_short[] =
    "[translate.fsm]recv heartbeat, translate ui state is invalid: [%d|%s]"; /* ROM 0x6fe6b4 */

#define FSM_LOG(level, fn, line, compact, msg, short_msg, ...)                              \
    do {                                                                                  \
        if (audio_log_flags() & 2u)                                                       \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg)      \
                               __VA_OPT__(, ) __VA_ARGS__);                               \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                         \
            (void)compress_log_output((compact), (short_msg), (short_msg)                 \
                                      __VA_OPT__(, ) __VA_ARGS__);                        \
    } while (0)

const char *translate_event_name_get_596b00(uint8_t event)
{
    return g2_translate_event_names[event];
}

int32_t translate_action_app_open_596c98(g2_translate_context_t *ctx, const void *data, uint32_t length)
{
    const g2_translate_open_t *open = (const g2_translate_open_t *)data;
    (void)length;
    if (open == NULL) {
        FSM_LOG(1u, open_fn, 119u, 0x04000000u, null_data, null_data_short);
        return -1;
    }
    uint8_t state = translate_ui_0059db5c();
    if (state == TRANSLATE_UI_CLOSING) {
        uint32_t background = 0u;
        uint32_t foreground = 0u;
        (void)audio_system_close_active_app_get_443504(&background, &foreground);
        if (foreground != TRANSLATE_APP_ID && background != TRANSLATE_APP_ID) {
            FSM_LOG(2u, open_fn, 133u, 0x08000000u, stuck, stuck_short);
            (void)AUDM_appRelease(1u);
            audio_uart_buffer_zero(&g2_translate_session, TRANSLATE_CONTEXT_SIZE, 0u);
            translate_ui_0059d9d4();
            state = translate_ui_0059db5c();
        }
    }
    if (state == TRANSLATE_UI_CLOSED) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
            uint32_t descriptor[2] = {2u, 2u}; /* ROM 0x78ec5c */
            audio_uart_ring_wear_persist_48eb32(0x40101u, 2u, descriptor);
        }
        if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
            (void)audio_system_alert_command_45a8ee(TRANSLATE_APP_ID, 0u, 0u, 500u);
    } else if (state == TRANSLATE_UI_OPEN) {
        if (open->language_pair_status == LANGUAGE_PAIR_UNSUPPORTED) {
            FSM_LOG(1u, open_fn, 150u, 0x04000000u, pair_unsupported, pair_unsupported_short);
            if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
                uint32_t descriptor[2] = {2u, 2u}; /* ROM 0x78ec64 */
                audio_uart_ring_wear_persist_48eb32(0x40102u, 2u, descriptor);
            }
            (void)translate_request_display_59ec28(TRANSLATE_UI_EVT_STOP, 1u);
        } else {
            (void)translate_request_display_59ec28(TRANSLATE_UI_EVT_START, 0u);
        }
    } else {
        FSM_LOG(1u, open_fn, 157u, 0x04800000u, bad_state, bad_state_short, state,
                translate_ui_0059db66(state));
        return -1;
    }
    g2_translate_session.active = 1u;
    translate_buffers_reset_59e9e2();
    audio_uart_buffer_zero(ctx->language_pair, LANGUAGE_PAIR_SIZE, 0u);
    (void)audio_queue_copy_bytes(ctx->language_pair, open->language_pair, open->language_pair_len);
    FSM_LOG(4u, open_fn, 167u, 0x10400000u, pair_log, pair_log_short, ctx->language_pair);
    ctx->use_audio = open->use_audio;
    if (ctx->use_audio != 0u)
        (void)AUDM_appAcquire(1u);
    return 0;
}

int32_t translate_action_ui_event5_596ef4(g2_translate_context_t *ctx, const void *data, uint32_t length)
{
    (void)ctx;
    (void)data;
    (void)length;
    (void)translate_request_display_59ec28(TRANSLATE_UI_EVT_5, 0u);
    return 0;
}

int32_t translate_action_ui_event6_596f02(g2_translate_context_t *ctx, const void *data, uint32_t length)
{
    (void)ctx;
    (void)data;
    (void)length;
    (void)translate_request_display_59ec28(TRANSLATE_UI_EVT_6, 0u);
    return 0;
}

int32_t translate_action_app_close_596f10(g2_translate_context_t *ctx, const void *data, uint32_t length)
{
    (void)ctx;
    (void)data;
    (void)length;
    audio_uart_buffer_zero(&g2_translate_session, TRANSLATE_CONTEXT_SIZE, 0u);
    if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
        uint32_t descriptor[2] = {2u, 2u}; /* ROM 0x78ec6c */
        audio_uart_ring_wear_persist_48eb32(0x40102u, 2u, descriptor);
    }
    (void)translate_request_display_59ec28(TRANSLATE_UI_EVT_STOP, 0u);
    return 0;
}

int32_t translate_action_result_596f48(g2_translate_context_t *ctx, const void *data, uint32_t length)
{
    (void)ctx;
    (void)length;
    if (data == NULL) {
        FSM_LOG(1u, result_fn, 231u, 0x04000000u, null_result, null_result_short);
        return -1;
    }
    translate_ui_0059e6d0(data);
    (void)translate_request_display_59ec28(TRANSLATE_UI_EVT_RESULT, 0u);
    return 0;
}

int32_t translate_action_heartbeat_596f9e(g2_translate_context_t *ctx, const void *data, uint32_t length)
{
    (void)ctx;
    (void)data;
    (void)length;
    uint8_t state = translate_ui_0059db5c();
    if (state == TRANSLATE_UI_CLOSED || state == TRANSLATE_UI_CLOSING) {
        FSM_LOG(2u, heartbeat_fn, 251u, 0x08800000u, heartbeat_bad, heartbeat_bad_short, state,
                translate_ui_0059db66(state));
        return -1;
    }
    return 0;
}

/* ROM 0x773b88. */
static const translate_action_t translate_actions[TRANSLATE_EVENT_COUNT] = {
    NULL,
    translate_action_app_open_596c98,
    translate_action_ui_event5_596ef4,
    translate_action_ui_event6_596f02,
    translate_action_app_close_596f10,
    translate_action_result_596f48,
    translate_action_heartbeat_596f9e,
};

int32_t translate_machine_handler_596b0c(uint8_t event, const void *data, uint32_t length)
{
    if (event >= TRANSLATE_EVENT_COUNT) {
        FSM_LOG(1u, handler_fn, 83u, 0x04000000u, invalid_event, invalid_event_short);
        return -1;
    }
    FSM_LOG(3u, handler_fn, 87u, 0x0c800000u, recv_event, recv_event_short, event,
            translate_event_name_get_596b00(event));
    translate_action_t action = translate_actions[event];
    if (action == NULL) {
        FSM_LOG(2u, handler_fn, 94u, 0x08800000u, no_action, no_action_short, event,
                translate_event_name_get_596b00(event));
        return -1;
    }
    int32_t status = action(&g2_translate_session, data, length);
    if (status != 0)
        FSM_LOG(2u, handler_fn, 101u, 0x08000000u, action_failed, action_failed_short);
    return status;
}
