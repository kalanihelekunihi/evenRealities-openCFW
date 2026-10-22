/* Five more source-owned Cordio DM actions, at stock call boundaries. */
#include <stdint.h>

extern void audio_ble_l2c_dm_conn_update_rsp_537230(uint8_t, uint16_t, uint8_t);
extern void audio_ble_hci_conn_update_52af40(uint16_t, const uint8_t *);
extern void audio_ble_dm_adv_stop_directed_4ba864(void);
extern void audio_ble_dm_conn_sm_act_failed_4b6488(void *, void *);
extern void audio_ble_dm_adv_connected_4ba9d4(void);
extern void audio_ble_dm_conn_sm_act_opened_4b63d8(void *, void *);
extern void audio_ble_dm_adv_connect_failed_4bab04(void);
extern void audio_ble_dm_slave_update_response_56e4f8(const uint8_t *, uint8_t);

static uint16_t le16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}


void audio_ble_dm_action_536adc(const uint8_t *ccb, const uint8_t *msg)
{
    audio_ble_dm_adv_stop_directed_4ba864();
    audio_ble_dm_conn_sm_act_failed_4b6488((void *)ccb, (void *)msg);
}

void audio_ble_dm_action_536af0(const uint8_t *ccb, const uint8_t *msg)
{
    audio_ble_dm_adv_connected_4ba9d4();
    audio_ble_dm_conn_sm_act_opened_4b63d8((void *)ccb, (void *)msg);
}

void audio_ble_dm_action_536b04(const uint8_t *ccb, const uint8_t *msg)
{
    audio_ble_dm_adv_connect_failed_4bab04();
    audio_ble_dm_conn_sm_act_failed_4b6488((void *)ccb, (void *)msg);
}

void audio_ble_dm_action_56e564(uint8_t *ccb, const uint8_t *msg)
{
    if (ccb[17] != 0u) {
        ccb[17] = 0u;
        if (le16(msg + 4) != 0u)
            audio_ble_dm_slave_update_response_56e4f8(ccb, msg[4]);
    }
}
