/* Native ANCC state children 0x4bea04/14/24/36, matched to the pinned
 * Ambiq ANCC list algorithm. The control block is live product RAM. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* 0x200695c8 */
extern void audio_ble_ancc_reset_state_machine(void); /* 0x4bf6c4 */

void audio_ble_ancc_conn_open_4bea04(uint8_t conn_id, uint32_t context) {
    audio_ble_ancc_state[0] = conn_id;
    audio_ble_ancc_state[4] = (uint8_t)context;
    audio_ble_ancc_state[5] = (uint8_t)(context >> 8);
    audio_ble_ancc_state[6] = (uint8_t)(context >> 16);
    audio_ble_ancc_state[7] = (uint8_t)(context >> 24);
    audio_ble_ancc_reset_state_machine();
}

void audio_ble_ancc_conn_close_4bea14(void) {
    audio_ble_ancc_state[0] = 0;
    audio_ble_ancc_reset_state_machine();
}

uint32_t audio_ble_ancc_no_connection_active_4bea24(void) {
    return audio_ble_ancc_state[0] == 0u;
}

uint32_t audio_ble_ancc_action_pop_4bea36(void) {
    for (uint32_t i = 0; i < 64u; ++i) {
        uint32_t off = 0x318u - 12u * i;
        if (audio_ble_ancc_state[off] == 1u) {
            audio_ble_ancc_state[off] = 0u;
            uint32_t index = 63u - i;
            audio_ble_ancc_state[8] = (uint8_t)index;
            audio_ble_ancc_state[9] = (uint8_t)(index >> 8);
            return 1u;
        }
    }
    return 0u;
}
