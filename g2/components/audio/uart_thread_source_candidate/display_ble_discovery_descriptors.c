/* Native Cordio attcDiscDescriptors 0x56b86a and attcDiscVerify 0x56b834. */
#include <stdint.h>
extern void audio_ble_attc_find_info_request_4b571e(uint8_t,uint16_t,uint16_t,uint8_t);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
uint8_t audio_ble_discovery_verify_56b834(const uint8_t *context){
    const uint8_t *entries=(const uint8_t *)(uintptr_t)rd32(context);
    const uint8_t *handles=(const uint8_t *)(uintptr_t)rd32(context+4);
    for(uint8_t i=0;i<context[0x0c];i++){
        const uint8_t *entry=(const uint8_t *)(uintptr_t)rd32(entries+(uint32_t)i*4u);
        if((entry[4]&2u)!=0u && rd16(handles+(uint32_t)i*2u)==0u)return 0x76u;
    }
    return 0u;
}
uint8_t audio_ble_discovery_descriptors_56b86a(uint8_t connection,uint8_t *context){
    uint8_t *entries=(uint8_t *)(uintptr_t)rd32(context);
    uint8_t *handles=(uint8_t *)(uintptr_t)rd32(context+4);
    uint16_t start=0u,end=0u;
    while(context[0x12]<context[0x0c]){
        const uint8_t index=context[0x12];
        const uint8_t *entry=(const uint8_t *)(uintptr_t)rd32(entries+(uint32_t)index*4u);
        if((entry[4]&4u)!=0u){
            start=(uint16_t)(rd16(handles+((uint32_t)index*2u)-2u)+1u);
            end=rd16(handles+(uint32_t)index*2u);
            handles[(uint32_t)index*2u]=0;handles[(uint32_t)index*2u+1u]=0;
            if(start<=end)break;
            do{context[0x12]=(uint8_t)(context[0x12]+1u);}while(context[0x12]<context[0x0c]);
        }else context[0x12]=(uint8_t)(context[0x12]+1u);
    }
    if(context[0x12]==context[0x0c])return audio_ble_discovery_verify_56b834(context);
    audio_ble_attc_find_info_request_4b571e(connection,start,end,1u);
    return 0x79u;
}
