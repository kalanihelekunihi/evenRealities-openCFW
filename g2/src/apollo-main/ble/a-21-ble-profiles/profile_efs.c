/* EFS (Even file service) GATT profile, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\efs\profile_efs.c.
 * Native 0x4be486..0x4be524 (efsWriteCallback) and 0x4be580..0x4be696
 * (APP_BleEfsSendDataMsg); literal pool 0x4be69c..0x4be6f0. The other EFS
 * entries live in ble/ble-profile and ble/ble-slave.
 *
 * Writes are refused while OTA runs, otherwise handed to EFS_ReceivePacket
 * (efs_transport.c). Unlike EUS/NUS, the send path has no OTA gate. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t param;      /* +0 connId */
    uint8_t event;       /* +2 0xaa EFS send */
    uint8_t status;      /* +3 */
    const uint8_t *data; /* +4 */
    uint16_t length;     /* +8 */
} g2_profile_send_msg_t;
_Static_assert(sizeof(g2_profile_send_msg_t) == 12u, "WsfMsgAlloc(12)");

extern uint8_t audio_ble_efs_handler_state[4]; /* RAM 0x200748a4 efsCb */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t efs_transport_receive_4d0d80(const uint8_t *packet, uint16_t length); /* EFS_ReceivePacket */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void audio_ble_comm_link_delayed(void); /* 0x4b81b8 APP_BleConnectTimeoutCheckEvt */
extern uint8_t profile_get_conn_state_byte(void); /* 0x46efd8 */
extern uint32_t semantic_OtaTransferActive(void); /* 0x4487ac */
extern void thread_ble_wsf_wait_tx_ready(void); /* 0x4d0b64 */
extern void thread_ble_wsf_tx_complete_notify(void); /* 0x4d0c36 */
extern void *WsfMsgAlloc(uint16_t length); /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message); /* 0x4bf9ba */

static const char module_tag[] = "profile.efs"; /* ROM 0x78b7ec */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\efs\\profile_efs.c"; /* ROM 0x6f53f8 */
static const char write_fn[] = "APP_BleEfsWriteCb"; /* ROM 0x7825c4 */
static const char ota_busy[] = "OTA is going, efs write cb failed"; /* ROM 0x7581f0 */
static const char ota_busy_short[] = "[profile.efs]OTA is going, efs write cb failed"; /* ROM 0x736c74 */
static const char rx_state[] = "efs rx state = %d"; /* ROM 0x7825d8 */
static const char rx_state_short[] = "[profile.efs]efs rx state = %d"; /* ROM 0x763af0 */
static const char send_fn[] = "APP_BleEfsSendDataMsg"; /* ROM 0x77a78c */
static const char ccc_state[] =
    "efsCb.cccdEnable ccc state = %d, connId = %d, efsCb.connId = %d"; /* ROM 0x70dde4 */
static const char ccc_state_short[] =
    "[profile.efs]efsCb.cccdEnable ccc state = %d, connId = %d, efsCb.connId = %d"; /* ROM 0x6eefa8 */
static const char send_hex[] = "APP_BleEfsSendDataMsg %x\t"; /* ROM 0x76fc34 */
static const char send_hex_short[] = "[profile.efs]APP_BleEfsSendDataMsg %x\t"; /* ROM 0x74c97c */
static const char alloc_fail[] = "APP_BleEfsSendDataMsg WsfMsgAlloc failed"; /* ROM 0x74196c */
static const char alloc_fail_short[] = "[profile.efs]APP_BleEfsSendDataMsg WsfMsgAlloc failed"; /* ROM 0x7216d8 */

#define LOG_COMPACT_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

uint8_t efsWriteCallback(uint8_t conn_id, uint16_t handle, uint8_t operation,
                         uint16_t offset, uint16_t length, uint8_t *value, void *attr)
{
    (void)conn_id; (void)handle; (void)operation; (void)offset; (void)attr;
    if (semantic_OtaTransferActive() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module_tag, source_file, write_fn, 0x93u, ota_busy);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x10000000u, ota_busy_short, ota_busy_short);
        return 0u;
    }
    uint32_t status = efs_transport_receive_4d0d80(value, length);
    if (status != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module_tag, source_file, write_fn, 0x99u, rx_state, status);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x04400000u, rx_state_short, rx_state_short, status);
    }
    (void)fw_event_loop_remove_delayed(audio_ble_comm_link_delayed);
    return 0u;
}

uint32_t APP_BleEfsSendDataMsg(const uint8_t *data, uint16_t length)
{
    uint8_t *cb = audio_ble_efs_handler_state;
    uint8_t conn_state = profile_get_conn_state_byte();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0xd5u, ccc_state,
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
            audio_log_extended(1u, module_tag, source_file, send_fn, 0xe6u, alloc_fail);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x04000000u, alloc_fail_short, alloc_fail_short);
        thread_ble_wsf_tx_complete_notify();
        return 0u;
    }
    msg->event = 0xaau;
    msg->param = cb[0];
    msg->data = data;
    msg->length = length;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0xdeu, send_hex, cb[1]);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10400000u, send_hex_short, send_hex_short, cb[1]);
    WsfMsgSend(cb[1], msg);
    return 0u;
}
