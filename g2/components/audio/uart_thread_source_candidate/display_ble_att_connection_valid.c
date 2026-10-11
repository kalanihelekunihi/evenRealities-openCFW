/* Native 0x52c928. The zero-connection assertion path remains a genuine
 * lower contract; nonzero connections use the authenticated Cordio table. */
#include <stdint.h>

extern uint8_t audio_ble_connection_state_table[]; /* native 0x20073e04 */
extern uint32_t audio_ble_att_zero_connection_assert(uint16_t);

uint32_t audio_ble_att_connection_valid(uint8_t connection,
                                        uint16_t attribute) {
    if(connection==0u)
        return audio_ble_att_zero_connection_assert(attribute);
    const uint8_t *record=audio_ble_connection_state_table+
                          ((uint32_t)connection-1u)*2u;
    return ((record[0]&1u)!=0u && record[1]==3u && attribute!=0x12u)
           ? 0u : 1u;
}
