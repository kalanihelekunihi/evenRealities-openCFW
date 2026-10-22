/* Even OTA GATT profile glue, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\ota\profile_ota.c.
 * Native APP_EvenOtaWriteCback 0x4bdc9c, APP_EvenOtaDisconnect 0x4bdd18 and
 * APP_EvenOtaSendDataMsg 0x4bdd7e (literal pool 0x4bde08..0x4bde48).
 * _evenOtaProcCccState 0x4bdb90, evenOtaProcMsg 0x4bdc0c, APP_EvenOtaHandlerInit
 * 0x4bdd00 and APP_EvenOtaProcMsg 0x4bdd70 live in ble/ble-profile and ble/ble-slave.
 *
 * Handler state (RAM 0x200748b4): [0] connection id, [1] WSF handler id,
 * [2] CCC notify enabled, [3] pending-send flag. Messages posted to the
 * handler: 0xa1 = disconnect request, 0xa7 = send data (pointer +4, length +8). */
#include <stdint.h>

/* 12-byte WSF message posted to the OTA handler. */
typedef struct {
    uint16_t param;       /* +0 connection id */
    uint8_t event;        /* +2 */
    uint8_t status;       /* +3 */
    const uint8_t *data;  /* +4 */
    uint16_t length;      /* +8 */
    uint16_t reserved;
} g2_ota_profile_msg_t;
_Static_assert(sizeof(g2_ota_profile_msg_t) == 12u, "OTA profile WSF message");

#define OTA_EVT_DISCONNECT 0xa1u
#define OTA_EVT_SEND_DATA  0xa7u

extern uint8_t audio_ble_ota_handler_state[4]; /* RAM 0x200748b4 */

extern void *WsfMsgAlloc(uint16_t length);                 /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message);    /* 0x4bf9ba */
extern uint32_t ota_transport_receive_48d8d8(const uint8_t *packet, uint16_t length); /* OTA_ReceivePacket */
extern uint8_t audio_ble_profile_get_connection_state(void); /* profile_get_conn_state_byte 0x46efd8 */
extern void audio_ble_tx_ready_wait(void);      /* thread_ble_wsf_wait_tx_ready 0x4d0b64 */
extern void audio_ble_tx_complete_notify(void); /* thread_ble_wsf_tx_complete_notify 0x4d0c36 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "profile.ota"; /* ROM 0x78b828 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ota\\profile_ota.c"; /* ROM 0x6f5528 */
static const char fn_write[] = "APP_EvenOtaWriteCback";        /* ROM 0x77a834 */
static const char fn_disconnect[] = "APP_EvenOtaDisconnect";   /* ROM 0x77a84c */
static const char fn_send[] = "APP_EvenOtaSendDataMsg";        /* ROM 0x77a864 */
static const char rx_state[] = "ota rx state = %d";            /* ROM 0x782628 */
static const char rx_state_short[] = "[profile.ota]ota rx state = %d"; /* ROM 0x763b30 */
static const char disconnect_msg[] = "disconnect BLE connection"; /* ROM 0x76fcdc */
static const char disconnect_short[] = "[profile.ota]disconnect BLE connection"; /* ROM 0x74ca6c */
static const char alloc_fail[] = "APP_EvenOtaSendDataMsg WsfMsgAlloc failed"; /* ROM 0x741a48 */
static const char alloc_fail_short[] = "[profile.ota]APP_EvenOtaSendDataMsg WsfMsgAlloc failed"; /* ROM 0x721860 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Cordio ATTS write callback for the OTA characteristic: every write is fed
 * to the OTA transport; a nonzero transport state is only logged. */
uint8_t APP_EvenOtaWriteCback(uint8_t conn_id, uint16_t handle, uint8_t operation, uint16_t offset,
                              uint16_t length, uint8_t *value, void *attr)
{
    (void)conn_id; (void)handle; (void)operation; (void)offset; (void)attr;
    uint8_t state = (uint8_t)ota_transport_receive_48d8d8(value, length);
    if (state != 0u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_write, 0xbdu, rx_state, (uint32_t)state);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, rx_state_short, rx_state_short, (uint32_t)state);
    }
    return 0u;
}

/* Delayed callback (OTA file parse, 3 s): ask the OTA handler to drop the link. */
void APP_EvenOtaDisconnect(void)
{
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_disconnect, 0xdbu, disconnect_msg);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, disconnect_short, disconnect_short);
    g2_ota_profile_msg_t *msg = (g2_ota_profile_msg_t *)WsfMsgAlloc(sizeof *msg);
    if (msg != 0) {
        msg->event = OTA_EVT_DISCONNECT;
        msg->param = audio_ble_ota_handler_state[0];
        WsfMsgSend(audio_ble_ota_handler_state[1], msg);
    }
}

/* Queue a notification only while connected with CCC enabled; always returns 0. */
uint32_t APP_EvenOtaSendDataMsg(const uint8_t *data, uint16_t length)
{
    (void)audio_ble_profile_get_connection_state();
    if (audio_ble_ota_handler_state[0] == 0u || audio_ble_ota_handler_state[2] != 1u)
        return 0u;
    audio_ble_tx_ready_wait();
    g2_ota_profile_msg_t *msg = (g2_ota_profile_msg_t *)WsfMsgAlloc(sizeof *msg);
    if (msg != 0) {
        msg->event = OTA_EVT_SEND_DATA;
        msg->param = audio_ble_ota_handler_state[0];
        msg->data = data;
        msg->length = length;
        WsfMsgSend(audio_ble_ota_handler_state[1], msg);
        return 0u;
    }
    if (log_extended_on())
        audio_log_extended(1u, module_tag, source_file, fn_send, 0x116u, alloc_fail);
    if (log_compressed_on())
        (void)compress_log_output(0x04000000u, alloc_fail_short, alloc_fail_short);
    /* Give back the tx-ready token taken above. */
    audio_ble_tx_complete_notify();
    return 0u;
}
