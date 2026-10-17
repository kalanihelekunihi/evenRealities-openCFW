/* Cordio slave connection update action at stock Main 0x56e526. */
#include <stdint.h>

extern uint32_t audio_ble_hci_get_le_supported_features_530d3c(void);
extern void audio_ble_hci_conn_update_52af40(uint16_t, const uint8_t *);
extern void audio_ble_l2c_conn_update_request_536ea4(uint16_t, const uint8_t *);
extern void audio_ble_dm_slave_update_response_56e4f8(uint8_t *, uint8_t);

void audio_ble_dm_action_56e526(uint8_t *ccb, const uint8_t *msg)
{
    if ((ccb[40] & 2u) != 0u &&
        (audio_ble_hci_get_le_supported_features_530d3c() & 2u) != 0u) {
        uint16_t handle = (uint16_t)ccb[12] | ((uint16_t)ccb[13] << 8);
        audio_ble_hci_conn_update_52af40(handle, msg + 4);
    } else if (ccb[17] == 0u) {
        uint16_t handle = (uint16_t)ccb[12] | ((uint16_t)ccb[13] << 8);
        ccb[17] = 1u;
        audio_ble_l2c_conn_update_request_536ea4(handle, msg + 4);
    } else {
        audio_ble_dm_slave_update_response_56e4f8(ccb, 12u);
    }
}
