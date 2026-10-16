/* Cordio dmConn2MsgHandler at Apollo Main 0x4b6914. Event cases and payload
 * offsets follow pinned Thumb and the registered Cordio dm_conn.c source. */
#include <stdint.h>

extern void *dmConnCcbById(uint8_t);
extern void audio_ble_hci_read_rssi_cmd_52b63a(uint16_t);
extern void audio_ble_hci_remote_conn_param_req_reply_52b0be(
    uint16_t, uint16_t, uint16_t, uint16_t, uint16_t, uint16_t, uint16_t);
extern void audio_ble_hci_remote_conn_param_req_neg_reply_52b146(uint16_t, uint8_t);
extern void audio_ble_hci_set_data_len_52b176(uint16_t, uint16_t, uint16_t);
extern void audio_ble_hci_write_auth_payload_timeout_52b70c(uint16_t, uint16_t);
extern void audio_ble_hci_request_peer_sca_52b87a(uint16_t);

static uint16_t u16(const uint8_t *p)
{
    return (uint16_t)p[0u] | ((uint16_t)p[1u] << 8u);
}

void audio_ble_dm_conn2_msg_handler_4b6914(void *message)
{
    const uint8_t *m = (const uint8_t *)message;
    const uint8_t *ccb = (const uint8_t *)dmConnCcbById(m[0u]);
    if (ccb == 0)
        return;
    uint16_t handle = u16(ccb + 0x0cu);
    switch (m[2u]) {
    case 0x21u:
        audio_ble_hci_read_rssi_cmd_52b63a(handle);
        break;
    case 0x22u:
        audio_ble_hci_remote_conn_param_req_reply_52b0be(
            handle, u16(m + 4u), u16(m + 6u), u16(m + 8u),
            u16(m + 10u), u16(m + 12u), u16(m + 14u));
        break;
    case 0x23u:
        audio_ble_hci_remote_conn_param_req_neg_reply_52b146(handle, m[4u]);
        break;
    case 0x24u:
        audio_ble_hci_set_data_len_52b176(handle, u16(m + 4u), u16(m + 6u));
        break;
    case 0x25u:
        audio_ble_hci_write_auth_payload_timeout_52b70c(handle, u16(m + 4u));
        break;
    case 0x26u:
        audio_ble_hci_request_peer_sca_52b87a(handle);
        break;
    default:
        break;
    }
}
