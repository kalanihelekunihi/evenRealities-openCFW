/* Cordio dmConn2HciHandler at Apollo Main 0x4b6990. */
#include <stdint.h>

extern void *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t);
extern void audio_ble_dm_conn2_act_rssi_read_4b6a38(void *, void *);
extern void audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e(void *, void *);
extern void audio_ble_dm_conn2_act_data_len_change_4b6ab8(void *, void *);
extern void audio_ble_dm_conn2_act_write_auth_to_cmpl_4b6afa(void *, void *);
extern void audio_ble_dm_conn2_act_auth_to_expired_4b6b28(void *, void *);
extern void audio_ble_dm_conn2_act_read_remote_features_cmpl_4b6b50(void *, void *);
extern void audio_ble_dm_conn2_act_read_remote_ver_info_cmpl_4b6bac(void *, void *);
extern void audio_ble_dm_conn2_act_req_peer_sca_4b6bee(void *, void *);

void audio_ble_dm_conn2_hci_handler_4b6990(void *event)
{
    const uint8_t *e = (const uint8_t *)event;
    uint16_t handle = (uint16_t)e[0u] | ((uint16_t)e[1u] << 8u);
    void *ccb = audio_ble_dm_conn_ccb_by_handle_4b601c(handle);
    if (ccb == 0) return;
    switch (e[2u]) {
    case 7u: audio_ble_dm_conn2_act_rssi_read_4b6a38(ccb, event); break;
    case 0x23u: audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e(ccb, event); break;
    case 0x24u: audio_ble_dm_conn2_act_data_len_change_4b6ab8(ccb, event); break;
    case 0x27u: audio_ble_dm_conn2_act_write_auth_to_cmpl_4b6afa(ccb, event); break;
    case 0x28u: audio_ble_dm_conn2_act_auth_to_expired_4b6b28(ccb, event); break;
    case 0x0bu: audio_ble_dm_conn2_act_read_remote_features_cmpl_4b6b50(ccb, event); break;
    case 0x0au: audio_ble_dm_conn2_act_read_remote_ver_info_cmpl_4b6bac(ccb, event); break;
    case 0x47u: audio_ble_dm_conn2_act_req_peer_sca_4b6bee(ccb, event); break;
    default: break;
    }
}
