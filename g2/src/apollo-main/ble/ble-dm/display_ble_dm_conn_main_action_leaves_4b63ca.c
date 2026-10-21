/* Cordio dmConnSmActNone 0x4b63ca and dmConnSmActClose 0x4b63cc.
 * The close leaf forwards CCB handle +12 and API-close reason +4. */
#include <stdint.h>

extern void audio_ble_hci_disconnect_cmd_52af10(uint16_t, uint8_t);

void audio_ble_dm_conn_sm_act_none_4b63ca(void *ccb, void *message)
{
    (void)ccb;
    (void)message;
}

void audio_ble_dm_conn_sm_act_close_4b63cc(void *ccb, void *message)
{
    const uint8_t *c = (const uint8_t *)ccb;
    const uint8_t *m = (const uint8_t *)message;
    uint16_t handle = (uint16_t)((uint16_t)c[12u] | ((uint16_t)c[13u] << 8u));
    audio_ble_hci_disconnect_cmd_52af10(handle, m[4u]);
}
