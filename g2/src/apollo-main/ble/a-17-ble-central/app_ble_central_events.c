/* BLE central (ring master) event posters, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_central.c.
 * Native APP_MasterUnpairDevEvent 0x4a1f38, APP_MasterUnpairConnIdEvent 0x4a1fc4,
 * APP_MasterScanEvent 0x4a21cc, auth_state_clear_wrapper 0x4a22e8,
 * APP_MasterCancelRingConnectRetry 0x4a2ea4.
 *
 * The posters build a 12-byte EVEN_MASTER_* WSF message that _masterProcMsg
 * (0x4a06d4) consumes on the BLE stack thread. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t param;       /* +0 connection id */
    uint8_t event;        /* +2 EVEN_MASTER_* */
    uint8_t status;       /* +3 */
    const void *addr;     /* +4 UNPAIR_DEV: device address record */
    uint16_t value;       /* +8 scan state / disconnect flags */
} g2_even_master_msg_t;
_Static_assert(sizeof(g2_even_master_msg_t) == 12u, "WsfMsgAlloc(12)");

/* Master context (pointer cell RAM 0x200742fc). */
typedef struct {
    uint8_t reserved_00[0x55];
    uint8_t conn_id;     /* +0x55 MConnId */
    uint8_t handler_id;  /* +0x56 WSF handler */
} g2_ble_master_ctx_t;

enum { EVEN_MASTER_DISCONNECT_EVT = 0xaf, EVEN_MASTER_UNPAIR_DEV_EVT = 0xb1, EVEN_MASTER_SCAN_EVT = 0xb2 };
/* Disconnect flags: 0x002 disconnect, 0x040 unpair, 0x100 initiated locally. */
#define DISC_FLAGS_UNPAIR_LOCAL 0x142u
#define DISC_FLAGS_LOCAL        0x102u

extern g2_ble_master_ctx_t *audio_ble_master_context;    /* RAM 0x200742fc */
extern volatile uint16_t audio_ble_master_connect_wait;   /* RAM 0x20074f18 */
extern volatile uint8_t audio_ble_ring_link_state;        /* RAM 0x20074f85 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);
extern void *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler, void *message);
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay_ms);
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));
extern const char *_ringLinkStateName(uint8_t state);
extern void APP_MasterConnectEvent(uint32_t event);
extern void APP_MasterSysStartTryConnectRing(void);
extern void APP_MasterResetRetryConnectCnt(void);
extern void APP_MasterClearRingConnectFailureNotifyAfterRetry(void);
extern void APP_MasterResetSceneConnectPending(void);
extern uint8_t auth_mode_set(uint8_t mode);

static const char module_tag[] = "ble.master"; /* ROM 0x78a028 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c"; /* ROM 0x6ff9b8 */
static const char fn_unpair_dev[] = "APP_MasterUnpairDevEvent";            /* ROM 0x768e2c */
static const char fn_unpair_conn[] = "APP_MasterUnpairConnIdEvent";        /* ROM 0x768e64 */
static const char fn_scan[] = "APP_MasterScanEvent";                       /* ROM 0x77dba0 */
static const char fn_cancel[] = "APP_MasterCancelRingConnectRetry";        /* ROM 0x751b00 */

#define MASTER_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[ble.master]" fmt, "[ble.master]" fmt, ##__VA_ARGS__); \
} while (0)

void APP_MasterUnpairDevEvent(const void *device)
{
    MASTER_LOG(4u, fn_unpair_dev, 0x455u, 0x10400000u, "state = 0x%x", device);
    g2_even_master_msg_t *msg = (g2_even_master_msg_t *)WsfMsgAlloc(sizeof *msg);
    if (msg != NULL) {
        msg->event = EVEN_MASTER_UNPAIR_DEV_EVT;
        msg->param = audio_ble_master_context->conn_id;
        msg->addr = device;
        WsfMsgSend(audio_ble_master_context->handler_id, msg);
    }
}

/* Unpair: disconnect the given master link locally with the unpair flag set. */
void APP_MasterUnpairConnIdEvent(uint8_t conn_id)
{
    g2_even_master_msg_t *msg;
    if (conn_id != 0u && (msg = (g2_even_master_msg_t *)WsfMsgAlloc(sizeof *msg)) != NULL) {
        MASTER_LOG(3u, fn_unpair_conn, 0x46au, 0x0c400000u, "APP_MasterUnpairConnIdEvent: connId=%d", conn_id);
        msg->event = EVEN_MASTER_DISCONNECT_EVT;
        msg->param = conn_id;
        msg->value = DISC_FLAGS_UNPAIR_LOCAL;
        WsfMsgSend(audio_ble_master_context->handler_id, msg);
    }
}

void APP_MasterScanEvent(uint8_t state)
{
    MASTER_LOG(4u, fn_scan, 0x498u, 0x10400000u, "state = 0x%x", state);
    g2_even_master_msg_t *msg = (g2_even_master_msg_t *)WsfMsgAlloc(sizeof *msg);
    if (msg != NULL) {
        msg->event = EVEN_MASTER_SCAN_EVT;
        msg->param = audio_ble_master_context->conn_id;
        msg->value = state;
        WsfMsgSend(audio_ble_master_context->handler_id, msg);
    }
}

/* Despite the inventory name this only returns the current master connection id. */
uint8_t auth_state_clear_wrapper(void)
{
    return audio_ble_master_context->conn_id;
}

void APP_MasterCancelRingConnectRetry(uint8_t disconnect_if_connected)
{
    MASTER_LOG(3u, fn_cancel, 0x5e7u, 0x0d000000u,
               "APP_MasterCancelRingConnectRetry: disconnectIfConnected=%d, retryCnt=%d, MConnId=%d state=%s",
               disconnect_if_connected, audio_ble_master_connect_wait, audio_ble_master_context->conn_id,
               _ringLinkStateName(audio_ble_ring_link_state));
    (void)fw_event_loop_remove_delayed((void (*)(void))APP_MasterConnectEvent);
    (void)fw_event_loop_remove_delayed(APP_MasterSysStartTryConnectRing);
    APP_MasterResetRetryConnectCnt();
    APP_MasterClearRingConnectFailureNotifyAfterRetry();
    APP_MasterResetSceneConnectPending();
    if (disconnect_if_connected != 0u && audio_ble_master_context != NULL &&
        audio_ble_master_context->conn_id != 0u) {
        MASTER_LOG(3u, fn_cancel, 0x5eeu, 0x0c000000u, "APP_MasterCancelRingConnectRetry: disconnect local ring");
        (void)auth_mode_set(0u);
        fw_event_loop_push_delayed((void (*)(void))APP_MasterConnectEvent, DISC_FLAGS_LOCAL, 0u);
    }
}
