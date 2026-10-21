/* Native DMA queue setup 0x538d58. ROM slots 0x539244/248 point to live
 * 0x2006ef28 channel rows and 0x6c0f40 descriptor table respectively. */
#include <stdint.h>
extern uint8_t audio_ble_dma_channel_rows_2006ef28[]; /* twelve 0x2c rows */
extern const uint8_t audio_ble_dma_channels_rom_6c0f40[]; /* twelve 0x28 descriptors */
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
static volatile uint32_t *target(const uint8_t *desc,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)get(desc+offset);
}

uint32_t audio_ble_vendor_dma_queue_538d58(uint32_t channel,const void *parameters,
                                             void *out) {
    uint8_t id=(uint8_t)channel;
    if(id>=12u)return 5u;
    const uint8_t *p=(const uint8_t *)parameters;
    if(p==0||get(p+4u)==0u||out==0||get(p)<2u)return 6u;
    uint8_t *row=audio_ble_dma_channel_rows_2006ef28+(uint32_t)id*0x2cu;
    if((get(row)&0x01000000u)!=0u)return 7u;
    uint32_t size=get(p),address=get(p+4u);
    put(row+24u,size<<3);
    put(row+4u,address);put(row+12u,address);put(row+20u,address);
    put(row+16u,address);put(row+8u,address+size*8u);
    put(row,(get(row)|0x01000000u)&0xfdffffffu);
    put(row,(get(row)&0xff000000u)|0x00cdcdcdu);
    const uint8_t *desc=audio_ble_dma_channels_rom_6c0f40+(uint32_t)id*0x28u;
    put(row+36u,(uint32_t)(uintptr_t)desc);
    put(row+28u,0u);put(row+32u,0u);
    *target(desc,8u)=0u;
    *target(desc,12u)=0u;
    *target(desc,16u)|=get(desc+20u);
    *target(desc,4u)=address;
    *target(desc,0u)=(p[8u]&1u)<<1;
    put((uint8_t *)out,(uint32_t)(uintptr_t)row);
    return 0u;
}
