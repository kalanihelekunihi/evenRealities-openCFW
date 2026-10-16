/* Cordio dmConnHciHandler, stock Apollo Main 0x4b68a4. Event values and
 * record offsets are from the pinned body; branch order follows dm_conn.c. */
#include <stdint.h>

extern void *audio_ble_dm_conn_ccb_by_address_4b6170(const void *);
extern void *audio_ble_dm_conn_complete_states_4b5b24(void);
extern void *audio_ble_dm_conn_ccb_alloc_4b5c78(const void *);
extern void *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t);
extern void audio_ble_dm_conn_sm_execute_533ef4(void *, void *);

void audio_ble_dm_conn_hci_handler_4b68a4(void *event)
{
    uint8_t *m = (uint8_t *)event;
    uint8_t *ccb;
    if (m[2u] == 1u || m[2u] == 2u) {
        ccb = (uint8_t *)audio_ble_dm_conn_ccb_by_address_4b6170(m + 10u);
        if (ccb == 0) {
            ccb = (uint8_t *)audio_ble_dm_conn_complete_states_4b5b24();
            if (ccb == 0 && m[3u] == 0u && m[8u] == 1u)
                ccb = (uint8_t *)audio_ble_dm_conn_ccb_alloc_4b5c78(m + 10u);
        }
        m[2u] = m[3u] == 0u ? 0x1cu : 0x1bu;
    } else {
        ccb = (uint8_t *)audio_ble_dm_conn_ccb_by_handle_4b601c(
            (uint16_t)m[0u] | ((uint16_t)m[1u] << 8u));
        m[2u] = (uint8_t)(m[2u] + 0x1au);
    }
    if (ccb != 0) {
        m[0u] = ccb[0x10u];
        m[1u] = 0u;
        audio_ble_dm_conn_sm_execute_533ef4(ccb, event);
    }
}
