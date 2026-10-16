/* Cordio dmConnSmActConnClosed 0x4b64ce.
 * CCB offsets/event value follow the pinned Apollo body; control flow follows
 * third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c. */
#include <stdint.h>

extern void audio_ble_dm_dev_pass_conn_cte_4b3008(uint8_t, uint8_t);
extern void audio_ble_dm_ccb_dealloc_4b5ef0(void *);
extern uint32_t audio_ble_dm_conn_num_4b62ca(void);
extern void audio_ble_dm_dev_pass_priv_4b2ea6(
    uint8_t, uint8_t, uint32_t, uint32_t);
extern void audio_ble_dm_conn_exec_callback_4b62ea(void *);

void audio_ble_dm_conn_sm_act_closed_4b64ce(void *ccb, void *message)
{
    uint8_t *c = (uint8_t *)ccb;
    uint8_t *m = (uint8_t *)message;
    audio_ble_dm_dev_pass_conn_cte_4b3008(0x28u, c[0x10u]);
    audio_ble_dm_ccb_dealloc_4b5ef0(ccb);
    if (c[0x19u] == 0u && audio_ble_dm_conn_num_4b62ca() == 0u)
        audio_ble_dm_dev_pass_priv_4b2ea6(0x0du, 0x28u, 0u, 0u);
    m[2u] = 0x28u;
    audio_ble_dm_conn_exec_callback_4b62ea(message);
}
