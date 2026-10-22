/* Cordio ATT control callbacks from pinned attc_main.c, atts_ind.c,
 * atts_main.c; stock Main 0x531330, 0x533c4c, 0x534c8a. */
#include <stdint.h>

extern uint8_t *audio_ble_attc_ccb_by_conn_id_531820(uint8_t, uint8_t);
extern void audio_ble_attc_ind_confirm_4b5838(uint8_t);
extern void audio_ble_attc_write_cmd_callback_530de6(uint8_t, void *, uint32_t);
extern uint8_t *audio_ble_att_registration_lookup(uint8_t, uint8_t);
extern void audio_ble_atts_ind_ntf_callback_53394c(uint8_t, void *, uint32_t);
extern uint8_t audio_ble_atts_state[];

void audio_ble_attc_ctrl_531330(const void *message)
{
    const uint8_t connection = (uint8_t)*(const uint16_t *)message;
    void *const ccb = audio_ble_attc_ccb_by_conn_id_531820(connection, 0u);
    if (ccb != 0) {
        audio_ble_attc_ind_confirm_4b5838(connection);
        audio_ble_attc_write_cmd_callback_530de6(connection, ccb, 0u);
    }
}


