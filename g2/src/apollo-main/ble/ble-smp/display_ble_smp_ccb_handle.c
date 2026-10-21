/* Native DmConnIdByHandle 0x4b6e96 and smpCcbByHandle 0x5375c8.
 * Both scan selected live Cordio connection/CCB rows. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* RAM 0x200712a4 */
extern uint8_t audio_ble_smp_handler_state[]; /* RAM 0x20070aec */
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
uint8_t DmConnIdByHandle(uint16_t handle){
    const uint8_t *row=audio_dm_connection_records;
    for(uint32_t i=0u;i<3u;i++,row+=0x30u)
        if(row[0x16u]!=0u&&rd16(row+0x0cu)==handle)return row[0x10u];
    return 0u;
}
uint8_t *smpCcbByHandle(uint16_t handle){
    const uint8_t connection=DmConnIdByHandle(handle);
    return connection==0u?0:audio_ble_smp_handler_state+((uint32_t)connection-1u)*0x4cu;
}
