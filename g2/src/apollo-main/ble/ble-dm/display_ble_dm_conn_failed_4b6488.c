/* Cordio dmConnSmActConnFailed at stock Apollo Main 0x4b6488.
 * Message offsets and call order are from the pinned body; the corresponding
 * path is in third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c. */
#include <stdint.h>

extern void audio_ble_dm_ccb_dealloc_4b5ef0(void *);
extern void audio_ble_dm_dev_pass_priv_4b2ea6(
    uint8_t, uint8_t, uint32_t, uint32_t);
extern uint32_t audio_ble_dm_conn_num_4b62ca(void);
extern void audio_ble_dm_conn_exec_callback_4b62ea(void *);

void audio_ble_dm_conn_sm_act_failed_4b6488(void *ccb, void *message)
{
    uint8_t *c = (uint8_t *)ccb;
    uint8_t *m = (uint8_t *)message;
    audio_ble_dm_ccb_dealloc_4b5ef0(ccb);
    if (c[0x19u] == 0u) {
        audio_ble_dm_dev_pass_priv_4b2ea6(0x0eu, 1u, 0u, 0u);
        if (audio_ble_dm_conn_num_4b62ca() == 0u)
            audio_ble_dm_dev_pass_priv_4b2ea6(0x0du, 0x28u, 0u, 0u);
    }
    m[2u] = 0x28u;
    m[8u] = 0u;
    m[6u] = 0u;
    m[7u] = 0u;
    audio_ble_dm_conn_exec_callback_4b62ea(message);
}
