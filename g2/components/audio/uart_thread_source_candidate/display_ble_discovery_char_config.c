/* Native Cordio AttcDiscCharStart 0x56c1b8 and AttcDiscConfigCmpl 0x56c396. */
#include <stdint.h>
extern void audio_ble_attc_read_by_type_56c4ee(uint8_t,uint16_t,uint16_t,uint8_t,const uint8_t *,uint32_t);
extern uint32_t audio_ble_discovery_config_next_56beb6(uint8_t,uint8_t *);
static uint16_t word16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
void audio_ble_discovery_char_start_56c1b8(uint8_t connection,uint8_t *context) {
    static const uint8_t characteristic_uuid[2]={0x03u,0x28u}; /* ROM 0x78f53e */
    context[0x12]=0u;
    context[0x13]=0xffu;
    audio_ble_attc_read_by_type_56c4ee(connection,word16(context+0x0e),
                                         word16(context+0x10),2u,characteristic_uuid,1u);
}
uint8_t audio_ble_discovery_config_complete_56c396(uint8_t connection,uint8_t *context) {
    context[0x12]=(uint8_t)(context[0x12]+1u);
    return (uint8_t)audio_ble_discovery_config_next_56beb6(connection,context);
}
