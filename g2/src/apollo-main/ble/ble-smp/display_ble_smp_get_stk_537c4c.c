/* Native Cordio SmpDmGetStk 0x537c4c and SC level logic 0x537c00. */
#include <stdint.h>

extern uint8_t *smpCcbByConnId(uint8_t);
extern uint8_t audio_ble_smp_handler_state[];

uint8_t *audio_ble_smp_get_stk_537c4c(uint8_t conn_id, uint8_t *level)
{
    uint8_t *const ccb = smpCcbByConnId(conn_id);
    if (ccb == 0 || ccb[0x44u] == 0u) return 0;

    if (audio_ble_smp_handler_state[0xf8u] != 0u) {
        uint8_t *const sc = *(uint8_t **)(void *)(ccb + 0x48u);
        if (sc[0u] != 0u) {
            uint8_t *const ltk = *(uint8_t **)(void *)(sc + 0x18u);
            if (ltk != 0) {
                if ((ccb[0x40u] & 4u) == 0u) *level = 1u;
                else {
                    const uint8_t key_size = ccb[0x24u] < ccb[0x2bu] ? ccb[0x24u] : ccb[0x2bu];
                    *level = key_size == 16u ? 3u : 2u;
                }
                return ltk + 0x10u;
            }
        }
    }

    uint8_t *const scratch = *(uint8_t **)(void *)(ccb + 0x30u);
    if (scratch != 0) {
        *level = (ccb[0x40u] & 4u) != 0u ? 2u : 1u;
        return scratch + 0x20u;
    }
    return 0;
}
