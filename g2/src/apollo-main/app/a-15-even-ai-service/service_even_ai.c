/* EvenAI service control and peer sync, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\evenAI\service_even_ai.c.
 * Native 0x497de6..0x497ea1 (wake debounce, _evenaiSyncEventCallback) and
 * 0x4982d4..0x4985a5 (protobuf notify wrappers, SVC_EvenAICtrl, SVC_EvenAIVADInfo);
 * literal pool 0x4985a8..0x498633.
 *
 * SVC_EvenAICtrl and SVC_EvenAIVADInfo do not act locally: they send a small sync
 * frame to both glasses on sync channel 7 with _evenaiSyncEventCallback as the
 * completion callback; the receiving side decodes it in SVC_DecodeLocalEvenAIInfo
 * (0x498092, app/even-ai/even_ai_local_decode_498092.c). Frame byte 0 is 2 (EvenAI),
 * byte 1 the command (1 ctrl, 2 ctrl-without-arg, 3 VAD). */
#include <stdint.h>
#include <stddef.h>

/* Ctrl frame; initialiser at ROM 0x78bf18 = {2, 1, 0...}; 11 bytes are sent. */
typedef struct {
    uint8_t type;            /* +0x0 2 = EvenAI */
    uint8_t command;         /* +0x1 1 = ctrl */
    uint8_t event;           /* +0x2 1 = wake up / start */
    uint8_t arg[4];          /* +0x3 caller argument, unaligned little endian */
    uint8_t voice_config;    /* +0x7 EvenAI config byte 1 (RAM 0x20074975) */
    uint8_t stream_state;    /* +0x8 text stream service +1 */
    uint8_t stream_len[2];   /* +0x9 text stream service +4 (u16) */
    uint8_t pad;             /* +0xb */
} g2_even_ai_ctrl_frame_t;
_Static_assert(sizeof(g2_even_ai_ctrl_frame_t) == 12u, "ctrl frame template");

/* Short frame {type, command, value}; initialisers ROM 0x78f3c0 = {2, 2, 0, 0}
 * (ctrl event 3) and ROM 0x78f3c4 = {2, 3, 0, 0} (VAD); 3 bytes are sent. */
typedef struct {
    uint8_t type;
    uint8_t command;
    uint8_t value;
    uint8_t pad;
} g2_even_ai_short_frame_t;

#define EVEN_AI_SYNC_APP 7u
#define EVEN_AI_SYNC_EVENT 5u
#define EVEN_AI_WAKE_DEBOUNCE_TICKS 300u

extern uint8_t audio_even_ai_service_state_2006ed10[0x218]; /* RAM 0x2006ed10, +0 session active */
extern uint8_t audio_even_ai_config_state_20074974[3];      /* RAM 0x20074974, +0 voice switch */
extern uint32_t g2_even_ai_last_wakeup_tick;               /* RAM 0x20074978 */

static const g2_even_ai_ctrl_frame_t ctrl_frame_init = {2u, 1u, 0u, {0u, 0u, 0u, 0u}, 0u, 0u, {0u, 0u}, 0u}; /* ROM 0x78bf18 */
static const g2_even_ai_short_frame_t ctrl_short_frame_init = {2u, 2u, 0u, 0u}; /* ROM 0x78f3c0 */
static const g2_even_ai_short_frame_t vad_frame_init = {2u, 3u, 0u, 0u};        /* ROM 0x78f3c4 */

extern uint32_t osKernelGetTickCount(void);                 /* 0x4490cc */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_even_ai_encode_ctrl_4e3788(uint32_t unused, const void *payload); /* APP_PbNotifyEncodeEvenAICtrl */
extern uint32_t audio_even_ai_encode_vad_4e3b80(uint32_t unused, const void *payload);  /* APP_PbNotifyEncodeEvenAIVADInfo */
extern uint32_t APP_PbNotifyEncodeEvenAIEvent(uint32_t unused, const void *payload);    /* 0x4e4cb8 */
extern uint8_t productModeGet(void);                        /* 0x4abe60 */
extern uint32_t semantic_OtaTransferActive(void);           /* 0x4487ac */
extern uint32_t onboarding_should_run(void);                /* 0x468034 */
extern uint8_t onboarding_active_flag_467f08(void);         /* 0x467f08 calibration_ui_status */
extern uint32_t get_silent_mode_ui_showing(void);           /* 0x469ae2 */
extern uint32_t even_ai_scroll_needed(void);                /* 0x4e5d54 */
extern const uint8_t *even_ai_text_stream_service_get(void); /* 0x4e5672 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t len,
                                                   uint32_t id, uint32_t event);
extern uint32_t audio_log_flags(void);                      /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "service.evenAI"; /* ROM 0x788940 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\evenAI\\service_even_ai.c"; /* ROM 0x6ef8b8 */
static const char sync_cb_fn[] = "_evenaiSyncEventCallback"; /* ROM 0x7711dc */
static const char ctrl_fn[] = "SVC_EvenAICtrl"; /* ROM 0x788960 */
static const char vad_fn[] = "SVC_EvenAIVADInfo"; /* ROM 0x78321c */
static const char sync_status[] = "SyncStatus = %d"; /* ROM 0x788950 */
static const char sync_status_short[] = "[service.evenAI]SyncStatus = %d"; /* ROM 0x764e50 */
static const char sync_error[] =
    "!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!"; /* ROM 0x705914 */
static const char sync_error_short[] =
    "[service.evenAI]!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!"; /* ROM 0x6e9b98 */
static const char ctrl_blocked[] =
    "warn: can not ctrl evenai, product_mode = %d, ota_status = %d, voice_switch = %d"; /* ROM 0x6e9bec */
static const char ctrl_blocked_short[] =
    "[service.evenAI]warn: can not ctrl evenai, product_mode = %d, ota_status = %d, voice_switch = %d"; /* ROM 0x6db86c */
static const char ctrl_blocked_ui[] =
    "onboarding_status = %d, calibration_ui_status = %d, silent_mode_ui_status = %d"; /* ROM 0x6ef908 */
static const char ctrl_blocked_ui_short[] =
    "[service.evenAI]onboarding_status = %d, calibration_ui_status = %d, silent_mode_ui_status = %d"; /* ROM 0x6de614 */
static const char debounced[] = "evenai wake up debounced"; /* ROM 0x771214 */
static const char debounced_short[] = "[service.evenAI]evenai wake up debounced"; /* ROM 0x74322c */
static const char vad_timeout[] = "vad timeout"; /* ROM 0x78bf0c */
static const char vad_timeout_short[] = "[service.evenAI]vad timeout"; /* ROM 0x771230 */

int32_t service_even_ai_fn_00497e08(int32_t status);

static void log0(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, msg_short, msg_short);
}

static uint32_t sync_callback_id(void)
{
    return (uint32_t)(uintptr_t)&service_even_ai_fn_00497e08; /* pool 0x49861c = 0x497e09 */
}

/* Wake-up debounce: 1 while less than 300 ticks have passed since the last
 * accepted wake (or the tick counter is behind it). */
uint32_t service_even_ai_fn_00497de6(void)
{
    uint32_t now = osKernelGetTickCount();
    if (now < g2_even_ai_last_wakeup_tick ||
        now - g2_even_ai_last_wakeup_tick < EVEN_AI_WAKE_DEBOUNCE_TICKS)
        return 1u;
    return 0u;
}

/* _evenaiSyncEventCallback: completion of an EvenAI sync frame to the peer. */
int32_t service_even_ai_fn_00497e08(int32_t status)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, sync_cb_fn, 75u, sync_status, status);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, sync_status_short, sync_status_short, status);
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, sync_cb_fn, 77u, sync_error, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04400000u, sync_error_short, sync_error_short, status);
    }
    return status;
}

/* One-byte protobuf notifications to the app (2-byte payload, byte 0 = value). */
void service_even_ai_fn_004982d4(uint8_t value)
{
    uint8_t payload[2];
    audio_uart_buffer_zero(payload, sizeof(payload), 0u);
    payload[0] = value;
    (void)audio_even_ai_encode_ctrl_4e3788(0u, payload);
}

void service_even_ai_fn_004982f2(uint8_t value)
{
    uint8_t payload[2];
    audio_uart_buffer_zero(payload, sizeof(payload), 0u);
    payload[0] = value;
    (void)audio_even_ai_encode_vad_4e3b80(0u, payload);
}

void service_even_ai_fn_00498310(uint8_t value)
{
    uint8_t payload[2];
    audio_uart_buffer_zero(payload, sizeof(payload), 0u);
    payload[0] = value;
    (void)APP_PbNotifyEncodeEvenAIEvent(0u, payload);
}

/* SVC_EvenAICtrl(event, arg). Event 1 (wake up) is refused in product mode, during
 * OTA, onboarding, calibration UI or silent-mode UI, and when arg == 0 while the
 * voice switch is on; otherwise it is debounced (300 ticks) and synced to both
 * glasses with the voice config and the current text stream position. Event 3 is
 * synced only while an EvenAI session is active. */
void service_even_ai_fn_0049832e(uint32_t event, uint32_t arg)
{
    if ((uint8_t)event == 1u) {
        if (productModeGet() == 1u || semantic_OtaTransferActive() == 1u ||
            onboarding_should_run() == 1u || onboarding_active_flag_467f08() == 1u ||
            get_silent_mode_ui_showing() == 1u ||
            (arg == 0u && audio_even_ai_config_state_20074974[0] == 1u)) {
            if (audio_log_flags() & 2u) {
                uint8_t ota = (uint8_t)semantic_OtaTransferActive();
                uint8_t product = productModeGet();
                audio_log_extended(2u, module_tag, source_file, ctrl_fn, 366u, ctrl_blocked,
                                   product, ota, audio_even_ai_config_state_20074974[0]);
            }
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
                uint8_t ota = (uint8_t)semantic_OtaTransferActive();
                uint8_t product = productModeGet();
                (void)compress_log_output(0x08c00000u, ctrl_blocked_short, ctrl_blocked_short,
                                          product, ota, audio_even_ai_config_state_20074974[0]);
            }
            if (audio_log_flags() & 2u) {
                uint8_t silent = (uint8_t)get_silent_mode_ui_showing();
                uint8_t calibration = onboarding_active_flag_467f08();
                uint32_t onboarding = onboarding_should_run();
                audio_log_extended(2u, module_tag, source_file, ctrl_fn, 368u, ctrl_blocked_ui,
                                   onboarding, calibration, silent);
            }
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
                uint8_t silent = (uint8_t)get_silent_mode_ui_showing();
                uint8_t calibration = onboarding_active_flag_467f08();
                uint32_t onboarding = onboarding_should_run();
                (void)compress_log_output(0x08c00000u, ctrl_blocked_ui_short, ctrl_blocked_ui_short,
                                          onboarding, calibration, silent);
            }
            return;
        }
        if (service_even_ai_fn_00497de6() != 0u) {
            log0(2u, ctrl_fn, 374u, debounced, debounced_short);
            return;
        }
        g2_even_ai_last_wakeup_tick = osKernelGetTickCount();
        g2_even_ai_ctrl_frame_t frame = ctrl_frame_init;
        frame.event = (uint8_t)event;
        frame.voice_config = audio_even_ai_config_state_20074974[1];
        (void)audio_queue_copy_bytes(frame.arg, &arg, sizeof(frame.arg));
        if (even_ai_scroll_needed() == 0u) {
            frame.stream_state = even_ai_text_stream_service_get()[1];
            uint16_t length = *(const uint16_t *)(const void *)(even_ai_text_stream_service_get() + 4);
            frame.stream_len[0] = (uint8_t)length;
            length = *(const uint16_t *)(const void *)(even_ai_text_stream_service_get() + 4);
            frame.stream_len[1] = (uint8_t)(length >> 8);
        }
        (void)audio_sync_send_to_both_ext_464f76(EVEN_AI_SYNC_APP, &frame, 11u, sync_callback_id(),
                                                 EVEN_AI_SYNC_EVENT);
    } else if ((uint8_t)event == 3u && audio_even_ai_service_state_2006ed10[0] != 0u) {
        g2_even_ai_short_frame_t frame = ctrl_short_frame_init;
        frame.value = (uint8_t)event;
        (void)audio_sync_send_to_both_ext_464f76(EVEN_AI_SYNC_APP, &frame, 3u, sync_callback_id(),
                                                 EVEN_AI_SYNC_EVENT);
    }
}

/* SVC_EvenAIVADInfo(vad): 1 speech start, 2 speech end, 3 timeout (logged); synced
 * to both glasses only while an EvenAI session is active. */
void service_even_ai_fn_00498528(uint32_t vad)
{
    if (audio_even_ai_service_state_2006ed10[0] == 0u)
        return;
    if ((uint8_t)vad != 1u && (uint8_t)vad != 2u) {
        if ((uint8_t)vad != 3u)
            return;
        log0(2u, vad_fn, 424u, vad_timeout, vad_timeout_short);
    }
    g2_even_ai_short_frame_t frame = vad_frame_init;
    frame.value = (uint8_t)vad;
    (void)audio_sync_send_to_both_ext_464f76(EVEN_AI_SYNC_APP, &frame, 3u, sync_callback_id(),
                                             EVEN_AI_SYNC_EVENT);
}
