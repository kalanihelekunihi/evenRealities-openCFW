/* Charging-case (box) detect service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\box_detect\service_box_detect.c.
 * Native rows 0x4abfba, 0x4ac0f8, 0x4ac278, 0x4ac66a, 0x4ac672 of
 * 0x4abec8..0x4acb3f; literal pools 0x4ac818.., 0x4aca98.., 0x4acaf8..,
 * 0x4acd4c.., 0x4acda4...
 *
 * Other functions of this source live in app/box-detect, app/case-* and
 * app/case-reconnect (BoxDetect_Init 0x4ac02a, timer callbacks 0x4ac016 /
 * 0x4ac020, BoxDetect_SetForceOutBox 0x4ac5a2, 0x4ac19c, 0x4abf86, 0x4abec8).
 * 0x4abfac, 0x4ac130 (VBUS attach) and 0x4ac154 (VBUS removal, starts the
 * 3 s box_detect_out_timer) are called but not written here.
 *
 * Case state record at RAM 0x20074928: +0 SoC, +1 charging, +2 lid open,
 * +3 in case (as printed by the case-status notify log). */
#include <stddef.h>
#include <stdint.h>

/* Box-detect message as queued to DEV_BoxDetectMsgProcess. */
typedef struct {
    uint16_t id;     /* +0 */
    uint16_t length; /* +2 must be non-zero */
    uint8_t event;   /* +4 box event, see DEV_BoxDetectMsgProcess_4ac278 */
} g2_box_detect_msg_t;

enum {
    BOX_EVT_PMIC_INTERRUPT = 0u,  /* run the nPM1300 interrupt handler (charger family 1 only) */
    BOX_EVT_IN_BOX = 1u,
    BOX_EVT_GLASSES_WEAR = 2u,    /* worn: force state to out of box, lid open */
    BOX_EVT_RING_CONNECTED = 3u,
    BOX_EVT_RING_CLOSED = 4u,
    BOX_EVT_RING_CONNECT_FAILED = 5u,
    BOX_EVT_RING_CONNECT_CANCELLED = 6u,
    BOX_EVT_RING_RECONNECT_TIMEOUT = 7u,
};

#define NPMX_SUCCESS 0x2bad0000u

struct npmx_instance;
extern struct npmx_instance g2_npmx_instance;         /* RAM 0x20070f78 */
extern void *audio_box_detect_timer;                   /* RAM 0x20074920 box_detect_out_timer */
extern void *audio_box_reconnect_timer;                /* RAM 0x20074924 ring_reconnect_timer */
extern uint8_t g2_box_case_state[4];                   /* RAM 0x20074928 */
extern volatile uint8_t audio_box_reconnect_suppressed_20075010; /* RAM 0x20075010 */
extern volatile uint8_t audio_box_reconnect_pending_20075011;    /* RAM 0x20075011 */
extern volatile uint8_t audio_uart_case_status_disabled; /* RAM 0x20075012 force-out-box flag */

extern int32_t osTimerStop(void *timer);
extern int32_t osTimerDelete(void *timer);
extern uint32_t npmx_interrupt_handler_510fe2(struct npmx_instance *p_pm);
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t index);
extern void box_detect_set_in_case_4abfac(uint8_t in_case);
extern void audio_uart_case_force_out_finish_4ac19c(uint32_t scene_arg);
extern void audio_uart_case_force_out_4ac5a2(uint32_t value);
extern void audio_uart_case_force_out_apply_4ac798(void);
extern void APP_MasterResetSceneConnectPending(void);
extern uint32_t display_driver_uled_mode_45a568(void); /* local device role */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t service, const void *data, uint32_t len,
                                                   uint32_t flags, uint32_t retries);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void BoxDetect_SyncForceOutBox_4ac672(uint8_t force_out);

static const char module_tag[] = "box.detect"; /* ROM 0x78be64 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c"; /* ROM 0x6e4b68 */
static const char fn_clear_force[] = "_BoxDetect_ClearForceOutBoxOnRealOut"; /* ROM 0x74d91c */
static const char fn_msg[] = "DEV_BoxDetectMsgProcess"; /* ROM 0x77b434 */
static const char fn_sync[] = "BoxDetect_SyncForceOutBox"; /* ROM 0x770c9c */
static const char s_clear_force[] = "clear force out box flag on real out"; /* ROM 0x74d944 */
static const char c_clear_force[] = "[box.detect]clear force out box flag on real out"; /* ROM 0x72cf3c */
static const char s_msg_err[] = "box rcv msg err\n"; /* ROM 0x782e70 */
static const char c_msg_err[] = "[box.detect]box rcv msg err\n"; /* ROM 0x7648d0 */
static const char s_npmx_irq[] = "npmx_interrupt_handler failed: %d\n"; /* ROM 0x7592d0 */
static const char c_npmx_irq[] = "[box.detect]npmx_interrupt_handler failed: %d\n"; /* ROM 0x737d54 */
static const char s_wear[] = "glasses wear, update state to out box and lid to open"; /* ROM 0x7226d0 */
static const char c_wear[] = "[box.detect]glasses wear, update state to out box and lid to open"; /* ROM 0x7055e4 */
static const char s_ring_connected[] = "[Box] Ring connected"; /* ROM 0x77b44c */
static const char c_ring_connected[] = "[box.detect][Box] Ring connected"; /* ROM 0x7592f4 */
static const char s_ring_closed[] = "[Box] Ring established then closed"; /* ROM 0x759318 */
static const char c_ring_closed[] = "[box.detect][Box] Ring established then closed"; /* ROM 0x737d84 */
static const char s_ring_failed[] = "[Box] Ring connect attempt failed"; /* ROM 0x75933c */
static const char c_ring_failed[] = "[box.detect][Box] Ring connect attempt failed"; /* ROM 0x737db4 */
static const char s_ring_cancel[] = "[Box] Ring connect event cancelled"; /* ROM 0x759360 */
static const char c_ring_cancel[] = "[box.detect][Box] Ring connect event cancelled"; /* ROM 0x737de4 */
static const char s_ring_timeout[] = "[Box] Ring reconnect trigger timeout (60s), auto-reset"; /* ROM 0x722708 */
static const char c_ring_timeout[] = "[box.detect][Box] Ring reconnect trigger timeout (60s), auto-reset"; /* ROM 0x705628 */
static const char s_sync[] = "sync force out box flag to both: %d"; /* ROM 0x759384 */
static const char c_sync[] = "[box.detect]sync force out box flag to both: %d"; /* ROM 0x737e14 */

#define BOX_LOG0(level, fn, line, plain, compact)                                        \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (plain)); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output((uint32_t)(level) << 26, (compact), (compact));    \
    } while (0)

/* A real removal from the case cancels a forced out-of-box state locally
 * and on the peer temple. */
void _BoxDetect_ClearForceOutBoxOnRealOut_4abfba(void) {
    if (audio_uart_case_status_disabled == 0u)
        return;
    BOX_LOG0(3u, fn_clear_force, 0x99u, s_clear_force, c_clear_force);
    audio_uart_case_force_out_4ac5a2(0u);
    BoxDetect_SyncForceOutBox_4ac672(0u);
}

void BoxDetect_Deinit_4ac0f8(void) {
    if (audio_box_detect_timer != NULL) {
        (void)osTimerStop(audio_box_detect_timer);
        (void)osTimerDelete(audio_box_detect_timer);
        audio_box_detect_timer = NULL;
    }
    if (audio_box_reconnect_timer != NULL) {
        (void)osTimerStop(audio_box_reconnect_timer);
        (void)osTimerDelete(audio_box_reconnect_timer);
        audio_box_reconnect_timer = NULL;
    }
}

/* Event 0 is the PMIC interrupt, serviced only when board record 0 byte 0 is
 * 1 (charger family 1, nPM1300). Events 3..7 track the ring reconnect that
 * the case scene queues. */
void DEV_BoxDetectMsgProcess_4ac278(const g2_box_detect_msg_t *msg) {
    if (msg == NULL || msg->length == 0u) {
        BOX_LOG0(1u, fn_msg, 299u, s_msg_err, c_msg_err);
        return;
    }
    uint8_t event = msg->event;
    if (event == BOX_EVT_PMIC_INTERRUPT) {
        const uint8_t *board = audio_ble_hci_radio_mode_state_50938e(0u);
        if (board[0] == 1u) {
            uint32_t err = npmx_interrupt_handler_510fe2(&g2_npmx_instance);
            if (err != NPMX_SUCCESS) {
                if (audio_log_flags() & 2u)
                    audio_log_extended(1u, module_tag, source_file, fn_msg, 0x13au, s_npmx_irq, err);
                if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                    (void)compress_log_output(0x04400000u, c_npmx_irq, c_npmx_irq, err);
            }
        }
    } else if (event == BOX_EVT_GLASSES_WEAR) {
        BOX_LOG0(3u, fn_msg, 0x146u, s_wear, c_wear);
        _BoxDetect_ClearForceOutBoxOnRealOut_4abfba();
        if (g2_box_case_state[3] != 0u)
            g2_box_case_state[3] = 0u;
        audio_uart_case_force_out_finish_4ac19c(1u);
        if (g2_box_case_state[2] != 0u)
            g2_box_case_state[2] = 0u;
        audio_uart_case_force_out_apply_4ac798();
    } else if (event == BOX_EVT_IN_BOX) {
        _BoxDetect_ClearForceOutBoxOnRealOut_4abfba();
        box_detect_set_in_case_4abfac(0u);
        audio_uart_case_force_out_finish_4ac19c(0u);
    } else if (event == BOX_EVT_RING_CLOSED) {
        BOX_LOG0(3u, fn_msg, 0x160u, s_ring_closed, c_ring_closed);
        audio_box_reconnect_suppressed_20075010 = 0u;
        audio_box_reconnect_pending_20075011 = 0u;
        if (audio_box_reconnect_timer != NULL)
            (void)osTimerStop(audio_box_reconnect_timer);
    } else if (event == BOX_EVT_RING_CONNECTED) {
        BOX_LOG0(3u, fn_msg, 0x157u, s_ring_connected, c_ring_connected);
        audio_box_reconnect_suppressed_20075010 = 1u;
        if (audio_box_reconnect_timer != NULL)
            (void)osTimerStop(audio_box_reconnect_timer);
    } else if (event == BOX_EVT_RING_CONNECT_CANCELLED) {
        BOX_LOG0(3u, fn_msg, 0x16eu, s_ring_cancel, c_ring_cancel);
        audio_box_reconnect_pending_20075011 = 0u;
        if (audio_box_reconnect_timer != NULL)
            (void)osTimerStop(audio_box_reconnect_timer);
    } else if (event == BOX_EVT_RING_CONNECT_FAILED) {
        BOX_LOG0(3u, fn_msg, 0x169u, s_ring_failed, c_ring_failed);
        audio_box_reconnect_suppressed_20075010 = 0u;
    } else if (event == BOX_EVT_RING_RECONNECT_TIMEOUT && audio_box_reconnect_pending_20075011 != 0u) {
        BOX_LOG0(2u, fn_msg, 0x177u, s_ring_timeout, c_ring_timeout);
        audio_box_reconnect_pending_20075011 = 0u;
        APP_MasterResetSceneConnectPending();
    }
}

uint8_t BoxDetect_GetForceOutBox_4ac66a(void) {
    return audio_uart_case_status_disabled;
}

/* Sync record on service 0x81: {4, 1, src role, dst role, 0, 0, 0, !flag}. */
void BoxDetect_SyncForceOutBox_4ac672(uint8_t force_out) {
    uint8_t record[8];
    audio_uart_buffer_zero(record, sizeof(record), 0u);
    uint8_t role = (uint8_t)display_driver_uled_mode_45a568();
    record[0] = 4u;
    record[1] = 1u;
    record[2] = role;
    record[3] = role == 1u ? 2u : 1u;
    record[7] = force_out == 0u ? 1u : 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, fn_sync, 0x1b6u, s_sync, force_out);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, c_sync, c_sync, force_out);
    (void)audio_sync_send_to_both_ext_464f76(0x81u, record, sizeof(record), 0u, 5u);
}
