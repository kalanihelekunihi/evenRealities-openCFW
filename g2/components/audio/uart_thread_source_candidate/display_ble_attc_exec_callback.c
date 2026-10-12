/* Native attcExecCallback 0x531ad6.  Its fifth stack argument to
 * attExecCallback is explicitly zeroed at 0x531ae2. */
#include <stdint.h>
extern void audio_ble_att_exec_callback_4b5074(uint8_t,uint8_t,uint16_t,uint8_t,uint16_t);
void audio_ble_attc_exec_callback_531ad6(uint8_t connection,uint8_t operation,
                                          uint16_t handle,uint8_t status) {
    if(operation!=1u)
        audio_ble_att_exec_callback_4b5074(connection,operation,handle,status,0u);
}
