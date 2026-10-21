/* Native Cordio attcDiscProcChar 0x56be30 and attcDiscProcDesc 0x56ba82. */
#include <stdint.h>
extern void audio_ble_discovery_proc_char_decl_56bb1c(uint8_t *,uint8_t,const uint8_t *);
extern void audio_ble_discovery_proc_desc_pair_56b8fa(uint8_t *,uint8_t,const uint8_t *);
extern uint8_t audio_ble_discovery_descriptors_56b86a(uint8_t,uint8_t *);
static uint16_t h16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t w32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}

uint8_t audio_ble_discovery_proc_char_56be30(uint8_t *context,const uint8_t *message){
    if(message[3]==0u){
        const uint8_t *base=(const uint8_t *)(uintptr_t)w32(message+4);
        const uint8_t length=base[0];
        const uint8_t *item=base+1;
        uint8_t wide;
        if(length==7u)wide=0u;
        else if(length==0x15u)wide=1u;
        else return 0x73u;
        for(;item<base+h16(message+8);item+=length)
            audio_ble_discovery_proc_char_decl_56bb1c(context,wide,item);
    }
    if(message[3]==0u && message[12]!=0u)return 0x79u;
    if(context[0x13]!=0xffu){
        uint8_t *handles=(uint8_t *)(uintptr_t)w32(context+4);
        put16(handles+(uint32_t)context[0x13]*2u,h16(context+0x10));
    }
    context[0x12]=0u;
    return audio_ble_discovery_descriptors_56b86a(message[0],context);
}

uint8_t audio_ble_discovery_proc_desc_56ba82(uint8_t *context,const uint8_t *message){
    if(message[3]==0u){
        const uint8_t *base=(const uint8_t *)(uintptr_t)w32(message+4);
        const uint8_t length=base[0];
        const uint8_t *item=base+1;
        uint8_t wide,step;
        if(length==1u){wide=0u;step=4u;}
        else if(length==2u){wide=1u;step=0x12u;}
        else return 0x73u;
        for(;item<base+h16(message+8);item+=step)
            audio_ble_discovery_proc_desc_pair_56b8fa(context,wide,item);
    }
    if(message[3]==0u && message[12]!=0u)return 0x79u;
    uint8_t *entries=(uint8_t *)(uintptr_t)w32(context);
    do {
        context[0x12]=(uint8_t)(context[0x12]+1u);
        if(context[0x12]==context[0x0c])break;
        const uint8_t *entry=(const uint8_t *)(uintptr_t)w32(entries+(uint32_t)context[0x12]*4u);
        if((entry[4]&4u)==0u)break;
    }while(1);
    return audio_ble_discovery_descriptors_56b86a(message[0],context);
}
