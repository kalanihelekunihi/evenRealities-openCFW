/* Cordio dmConnSmActConnOpened, Apollo Main stock entry 0x4b63d8.
 * Offsets and event order are checked against the pinned stock body; control
 * flow follows the registered Cordio dm_conn.c source. */
#include <stdint.h>

extern void audio_ble_copy_address6_4d293c(void *, const void *);
extern uint32_t audio_ble_pair_address_type_4d2aa8(uint32_t);
extern uint8_t *HciGetBdAddr(void);
extern uint8_t audio_ble_dm_handler_state[];
extern void audio_ble_dm_dev_pass_priv_4b2ea6(
    uint8_t, uint8_t, uint32_t, uint32_t);
extern uint32_t audio_ble_dm_conn_num_4b62ca(void);
extern void audio_ble_dm_dev_pass_conn_cte_4b3008(uint8_t, uint8_t);
extern void audio_ble_dm_conn_exec_callback_4b62ea(void *);

void audio_ble_dm_conn_sm_act_opened_4b63d8(void *ccb, void *message)
{
    uint8_t *c = (uint8_t *)ccb;
    uint8_t *m = (uint8_t *)message;
    audio_ble_copy_address6_4d293c(c, m + 10u);
    c[0x0cu] = m[6u];
    c[0x0du] = m[7u];
    c[0x13u] = (uint8_t)audio_ble_pair_address_type_4d2aa8(m[9u]);
    c[0x19u] = m[8u];
    c[0x14u] = audio_ble_dm_handler_state[c[0x19u] == 0u ? 0x0du : 0x0eu];
    audio_ble_copy_address6_4d293c(c + 6u,
        c[0x14u] == 0u ? HciGetBdAddr() : audio_ble_dm_handler_state);
    audio_ble_copy_address6_4d293c(c + 0x1au, m + 0x17u);
    audio_ble_copy_address6_4d293c(c + 0x20u, m + 0x1du);
    c[0x0eu] = 0u;
    c[0x0fu] = 0u;
    if (c[0x19u] == 0u) {
        audio_ble_dm_dev_pass_priv_4b2ea6(0x0eu, 1u, 0u, 0u);
        if (audio_ble_dm_conn_num_4b62ca() == 1u)
            audio_ble_dm_dev_pass_priv_4b2ea6(0x0cu, 0x27u, 0u, 0u);
    }
    audio_ble_dm_dev_pass_conn_cte_4b3008(0x27u, c[0x10u]);
    m[2u] = 0x27u;
    audio_ble_dm_conn_exec_callback_4b62ea(message);
}
