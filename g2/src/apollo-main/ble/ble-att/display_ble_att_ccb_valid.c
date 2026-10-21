/* Native 0x4b4eee nonzero connection CCB lookup. The zero-connection
 * diagnostic assertion tree remains a genuine lower code contract. */
#include <stdint.h>
extern uint8_t audio_ble_att_runtime[]; /* native live base 0x200610ac */
extern uint8_t *audio_ble_att_ccb_zero_assert(void);

uint8_t *audio_ble_att_ccb_by_conn_id(uint8_t connection) {
    if(connection==0u)return audio_ble_att_ccb_zero_assert();
    return audio_ble_att_runtime+((uint32_t)connection-1u)*0x14u;
}
