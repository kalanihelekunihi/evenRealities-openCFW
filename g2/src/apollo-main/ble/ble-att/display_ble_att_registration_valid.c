/* Native 0x4b6ec6 and valid-connection domain of 0x534f14.
 * The registration failure assertion path remains an explicit lower contract. */
#include <stdint.h>

extern uint8_t audio_ble_connection_records[]; /* native 0x200712a4 */
extern uint8_t audio_ble_registration_records[]; /* native 0x2006e5f0 */
extern uint8_t *audio_ble_att_registration_invalid(uint8_t,uint8_t);

uint8_t audio_ble_connection_record_active(uint8_t connection) {
    return audio_ble_connection_records[(uint32_t)connection*0x30u-0x1au];
}

uint8_t *audio_ble_att_registration_lookup(uint8_t connection,
                                           uint8_t registration) {
    if(connection==0u || audio_ble_connection_record_active(connection)==0u)
        return audio_ble_att_registration_invalid(connection,registration);
    return audio_ble_registration_records +
           ((uint32_t)connection-1u)*0xc0u + (uint32_t)registration*0x40u;
}
