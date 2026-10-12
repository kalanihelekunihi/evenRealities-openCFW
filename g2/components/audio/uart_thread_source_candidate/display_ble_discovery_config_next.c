/* Native Cordio attcDiscConfigNext 0x56beb6 and resume 0x56c3a6.
 * The config descriptor and handle arrays are caller-owned runtime storage. */
#include <stdint.h>
extern void audio_ble_attc_read_request(uint8_t,uint16_t); /* AttcReadReq 0x4b575a */
extern void audio_ble_attc_write_request(uint8_t,uint16_t,uint16_t,const uint8_t *); /* AttcWriteReq 0x4b579c */

static uint32_t word_at(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static uint16_t half_at(const uint8_t *p) {return (uint16_t)p[0]|((uint16_t)p[1]<<8);}

uint32_t audio_ble_discovery_config_next_56beb6(uint8_t connection,uint8_t *context) {
    uint8_t index=context[0x12];
    const uint8_t *descriptors=(const uint8_t *)(uintptr_t)word_at(context+8);
    const uint8_t *handles=(const uint8_t *)(uintptr_t)word_at(context+4);
    while(index<context[0x0d]){
        const uint8_t *descriptor=descriptors+(uint32_t)index*8u;
        const uint16_t handle=half_at(handles+(uint32_t)descriptor[5]*2u);
        if(handle!=0u){
            if(descriptor[4]==0u)audio_ble_attc_read_request(connection,handle);
            else audio_ble_attc_write_request(connection,handle,descriptor[4],
                                               (const uint8_t *)(uintptr_t)word_at(descriptor));
            return 0x79u;
        }
        context[0x12]=++index;
    }
    return 0u;
}

void audio_ble_discovery_config_resume(uint8_t connection,uint32_t context) {
    (void)audio_ble_discovery_config_next_56beb6(connection,(uint8_t *)(uintptr_t)context);
}
