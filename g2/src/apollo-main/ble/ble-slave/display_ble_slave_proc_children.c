/* Native 0x4b46a8, 0x4bac4e, 0x47a676, 0x47aec0, 0x47aec8. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[]; /* 0x200719c8 */
extern uint8_t audio_ble_dm_adv_control[]; /* 0x20073394 */
extern uint8_t audio_ble_privacy_rows[10u*200u]; /* 0x20067a30 */

uint8_t audio_ble_dm_adv_state(uint8_t index) {
    return index<2u?audio_ble_dm_adv_control[0x1du+index]:0u;
}
uint8_t audio_ble_pair_count(uint8_t type) {
    uint8_t count=0u;
    for(uint8_t i=0u;i<10u;i++) {
        uint8_t *row=audio_ble_privacy_rows+(uint32_t)i*200u;
        if(row[0x2fu] && row[0xc3u]==type)count++;
    }
    return count;
}
const uint8_t *audio_ble_dm_conn_peer_address(const uint8_t *record) {
    return record;
}
uint8_t audio_ble_dm_conn_address_type(const uint8_t *record) {
    return record?record[6u]:0xffu;
}
