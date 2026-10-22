/* NUS (Nordic-UART-style production service) GATT profile, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\nus\profile_nus.c.
 * Native 0x4be7d2..0x4be7fa (nusWriteCallback) and 0x4be856..0x4be9b0
 * (APP_BleNusSendDataMsg); inline string "Nus" at 0x4be9b4, literal pool
 * 0x4be9b8..0x4bea04. The other NUS entries live in ble/ble-profile and
 * ble/ble-slave.
 *
 * Writes are hex-dumped and queued to the BLE production (factory test)
 * thread; responses come back through APP_BleNusSendDataMsg. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t param;      /* +0 connId */
    uint8_t event;       /* +2 0xab NUS send */
    uint8_t status;      /* +3 */
    const uint8_t *data; /* +4 */
    uint16_t length;     /* +8 */
} g2_profile_send_msg_t;
_Static_assert(sizeof(g2_profile_send_msg_t) == 12u, "WsfMsgAlloc(12)");

extern uint8_t audio_ble_nus_handler_state[4]; /* RAM 0x200748b0 nusCb */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data, uint32_t length); /* 0x43dacc elog hexdump */
extern int32_t Thread_SendMsgToBleProductionTask(const void *data, uint16_t length); /* 0x538992 */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void audio_ble_comm_link_delayed(void); /* 0x4b81b8 APP_BleConnectTimeoutCheckEvt */
extern uint8_t profile_get_conn_state_byte(void); /* 0x46efd8 */
extern uint32_t semantic_OtaTransferActive(void); /* 0x4487ac */
extern void thread_ble_wsf_wait_tx_ready(void); /* 0x4d0b64 */
extern void thread_ble_wsf_tx_complete_notify(void); /* 0x4d0c36 */
extern void *WsfMsgAlloc(uint16_t length); /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message); /* 0x4bf9ba */

static const char dump_label[] = "Nus"; /* ROM 0x4be9b4 */
static const char module_tag[] = "profile.nus"; /* ROM 0x78b81c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\nus\\profile_nus.c"; /* ROM 0x6f54dc */
static const char send_fn[] = "APP_BleNusSendDataMsg"; /* ROM 0x77a804 */
static const char ota_busy[] = "OTA is going, nus send data msg failed"; /* ROM 0x74c9f4 */
static const char ota_busy_short[] = "[profile.nus]OTA is going, nus send data msg failed"; /* ROM 0x72c000 */
static const char ccc_state[] =
    "nusCb.cccdEnable ccc state = %d, connId = %d, nusCb.connId = %d"; /* ROM 0x70de64 */
static const char ccc_state_short[] =
    "[profile.nus]nusCb.cccdEnable ccc state = %d, connId = %d, nusCb.connId = %d"; /* ROM 0x6ef098 */
static const char send_hex[] = "APP_BleNusSendDataMsg %x\t"; /* ROM 0x76fcc0 */
static const char send_hex_short[] = "[profile.nus]APP_BleNusSendDataMsg %x\t"; /* ROM 0x74ca1c */
static const char alloc_fail[] = "APP_BleNusSendDataMsg WsfMsgAlloc failed"; /* ROM 0x741a1c */
static const char alloc_fail_short[] = "[profile.nus]APP_BleNusSendDataMsg WsfMsgAlloc failed"; /* ROM 0x7217f0 */

#define LOG_COMPACT_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

uint8_t nusWriteCallback(uint8_t conn_id, uint16_t handle, uint8_t operation,
                         uint16_t offset, uint16_t length, uint8_t *value, void *attr)
{
    (void)conn_id; (void)handle; (void)operation; (void)offset; (void)attr;
    audio_dump_hex(dump_label, 8u, value, length);
    (void)Thread_SendMsgToBleProductionTask(value, length);
    (void)fw_event_loop_remove_delayed(audio_ble_comm_link_delayed);
    return 0u;
}

uint32_t APP_BleNusSendDataMsg(const uint8_t *data, uint16_t length)
{
    uint8_t *cb = audio_ble_nus_handler_state;
    uint8_t conn_state = profile_get_conn_state_byte();
    if (semantic_OtaTransferActive() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module_tag, source_file, send_fn, 0xcfu, ota_busy);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x10000000u, ota_busy_short, ota_busy_short);
        return 0u;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0xd2u, ccc_state,
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
            audio_log_extended(1u, module_tag, source_file, send_fn, 0xe3u, alloc_fail);
        if (LOG_COMPACT_ON())
            (void)compress_log_output(0x04000000u, alloc_fail_short, alloc_fail_short);
        thread_ble_wsf_tx_complete_notify();
        return 0u;
    }
    msg->event = 0xabu;
    msg->param = cb[0];
    msg->data = data;
    msg->length = length;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0xdbu, send_hex, cb[1]);
    if (LOG_COMPACT_ON())
        (void)compress_log_output(0x10400000u, send_hex_short, send_hex_short, cb[1]);
    WsfMsgSend(cb[1], msg);
    return 0u;
}
