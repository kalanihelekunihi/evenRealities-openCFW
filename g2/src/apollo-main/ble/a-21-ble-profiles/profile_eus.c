/* EUS (Even UART service) GATT profile, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\eus\profile_eus.c.
 * Native 0x4bdf3c..0x4bdf98 (eusWriteCallback) and 0x4bdff4..0x4be1c8
 * (APP_BleEusSendDataMsg, APP_BleEusDirectSendDataMsg); literal pool
 * 0x4be1c8..0x4be228. eusProcCccState/eusProcMsg/APP_BleEusHandlerInit/
 * APP_BleEusProcMsg live in ble/ble-profile and ble/ble-slave.
 *
 * The 4-byte state cell eusCb (RAM 0x200748ac) is {connId, wsf handler id,
 * cccd enabled, tx-busy}. Send posts a 12-byte WSF message (event 0xa8) to the
 * profile's own handler; eusProcMsg turns it into AttsHandleValueNtf on
 * attribute 0x844. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t param;      /* +0 connId */
    uint8_t event;       /* +2 0xa8 EUS send */
    uint8_t status;      /* +3 */
    const uint8_t *data; /* +4 */
    uint16_t length;     /* +8 */
} g2_profile_send_msg_t;
_Static_assert(sizeof(g2_profile_send_msg_t) == 12u, "WsfMsgAlloc(12)");

extern uint8_t audio_ble_eus_handler_state[4]; /* RAM 0x200748ac eusCb */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t TPL_ReceivePacket(uint8_t pipe, const uint8_t *packet, uint16_t length); /* 0x4b910c */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void audio_ble_comm_link_delayed(void); /* 0x4b81b8 APP_BleConnectTimeoutCheckEvt */
extern uint8_t profile_get_conn_state_byte(void); /* 0x46efd8 */
extern uint32_t semantic_OtaTransferActive(void); /* 0x4487ac */
extern void thread_ble_wsf_wait_tx_ready(void); /* 0x4d0b64 */
extern void thread_ble_wsf_tx_complete_notify(void); /* 0x4d0c36 */
extern void *WsfMsgAlloc(uint16_t length); /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message); /* 0x4bf9ba */

static const char module_tag[] = "profile.eus"; /* ROM 0x78b804 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\eus\\profile_eus.c"; /* ROM 0x6f5490 */
static const char write_fn[] = "APP_BleEusWriteCb"; /* ROM 0x7825ec */
static const char rx_state[] = "eus rx state = %d"; /* ROM 0x782600 */
static const char rx_state_short[] = "[profile.eus]eus rx state = %d"; /* ROM 0x763b10 */
static const char send_fn[] = "APP_BleEusSendDataMsg"; /* ROM 0x77a7d4 */
static const char direct_fn[] = "APP_BleEusDirectSendDataMsg"; /* ROM 0x76fc88 */
static const char ota_busy[] = "OTA is going, eus send data msg failed"; /* ROM 0x74c9a4 */
static const char ota_busy_short[] = "[profile.eus]OTA is going, eus send data msg failed"; /* ROM 0x72bf98 */
static const char ccc_state[] =
    "eusCb.cccdEnable ccc state = %d, connId = %d, eusCb.connId = %d"; /* ROM 0x70de24 */
static const char ccc_state_short[] =
    "[profile.eus]eusCb.cccdEnable ccc state = %d, connId = %d, eusCb.connId = %d"; /* ROM 0x6eeff8 */
static const char send_hex[] = "APP_BleEusSendDataMsg %x\t"; /* ROM 0x76fc6c */
static const char send_hex_short[] = "[profile.eus]APP_BleEusSendDataMsg %x\t"; /* ROM 0x74c9cc */
static const char alloc_fail[] = "APP_BleEusSendDataMsg WsfMsgAlloc failed"; /* ROM 0x7419c4 */
static const char alloc_fail_short[] = "[profile.eus]APP_BleEusSendDataMsg WsfMsgAlloc failed"; /* ROM 0x721780 */

#define LOG_COMPACT_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* Cordio attsWriteCback_t: incoming EUS RX write goes to the transport layer
 * (pipe 0); then the connect-timeout check is cancelled. */
uint8_t eusWriteCallback(uint8_t conn_id, uint16_t handle, uint8_t operation,
                         uint16_t offset, uint16_t length, uint8_t *value, void *attr)
{
    (void)conn_id; (void)handle; (void)operation; (void)offset; (void)attr;
    uint32_t status = TPL_ReceivePacket(0u, value, length);
    if (status != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module_tag, source_file, write_fn, 0x93u, rx_state, status);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x04400000u, rx_state_short, rx_state_short, status);
    }
    (void)fw_event_loop_remove_delayed(audio_ble_comm_link_delayed);
    return 0u;
}

uint32_t APP_BleEusSendDataMsg(const uint8_t *data, uint16_t length)
{
    uint8_t *cb = audio_ble_eus_handler_state;
    uint8_t conn_state = profile_get_conn_state_byte();
    if (semantic_OtaTransferActive() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module_tag, source_file, send_fn, 0xd0u, ota_busy);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x10000000u, ota_busy_short, ota_busy_short);
        return 0u;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0xd8u, ccc_state,
                           cb[2], conn_state, cb[0]);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10c00000u, ccc_state_short, ccc_state_short,
                                  cb[2], conn_state, cb[0]);
    if (cb[0] == 0u || cb[2] != 1u)
        return 0u;
    thread_ble_wsf_wait_tx_ready();
    g2_profile_send_msg_t *msg = (g2_profile_send_msg_t *)WsfMsgAlloc(12u);
    if (msg == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module_tag, source_file, send_fn, 0xe9u, alloc_fail);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x04000000u, alloc_fail_short, alloc_fail_short);
        thread_ble_wsf_tx_complete_notify();
        return 0u;
    }
    msg->event = 0xa8u;
    msg->param = cb[0];
    msg->data = data;
    msg->length = length;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0xe1u, send_hex, cb[1]);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10400000u, send_hex_short, send_hex_short, cb[1]);
    WsfMsgSend(cb[1], msg);
    return 0u;
}

/* Same post without the tx-ready wait, logging or allocation-failure notify. */
uint32_t APP_BleEusDirectSendDataMsg(const uint8_t *data, uint16_t length)
{
    uint8_t *cb = audio_ble_eus_handler_state;
    if (semantic_OtaTransferActive() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module_tag, source_file, direct_fn, 0xf6u, ota_busy);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x10000000u, ota_busy_short, ota_busy_short);
        return 0u;
    }
    if (cb[0] != 0u && cb[2] == 1u) {
        g2_profile_send_msg_t *msg = (g2_profile_send_msg_t *)WsfMsgAlloc(12u);
        if (msg != NULL) {
            msg->event = 0xa8u;
            msg->param = cb[0];
            msg->data = data;
            msg->length = length;
            WsfMsgSend(cb[1], msg);
        }
    }
    return 0u;
}
