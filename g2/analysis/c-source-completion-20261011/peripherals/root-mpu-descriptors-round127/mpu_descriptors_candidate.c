#include <stdint.h>
extern void audio_uart_mpu_attribute_write_4d4434(uint32_t,uint32_t);
extern void audio_uart_mpu_regions_write_4d44d2(uint32_t,const uint32_t *,uint32_t);
uint32_t audio_uart_mpu_attributes_4d450c(const void *descriptors,uint32_t count) {
    const volatile uint8_t *d=descriptors;
    if((*(volatile uint32_t *)(uintptr_t)0xe000ed94u&1u)!=0u)return 3u;
    for(uint32_t i=0;i<count;i++,d+=11u) {
        uint32_t id=d[0];
        if(id>=8u)return 5u;
        uint32_t outer,inner;
        if(d[1]==0u) {outer=0;inner=(uint32_t)d[10]<<2;}
        else {
            uint32_t a=d[2],b=d[3];outer=(a<<3)|(b<<2);
            outer|=(uint32_t)d[4]<<1;outer|=d[5];
            a=d[6];b=d[7];inner=(a<<3)|(b<<2);
            inner|=(uint32_t)d[8]<<1;inner|=d[9];
        }
        if((outer&15u)==0u)inner=((uint32_t)(uint8_t)inner<<2)&12u;
        else inner=(uint32_t)(uint8_t)inner&15u;
        audio_uart_mpu_attribute_write_4d4434((uint8_t)id,(uint8_t)(inner|(outer<<4)));
    }
    return 0u;
}
uint32_t audio_uart_mpu_region_4d4596(const void *descriptors,uint32_t count) {
    const volatile uint8_t *d=descriptors;
    uint32_t start=*(const volatile uint32_t *)(const void *)d;
    if((*(volatile uint32_t *)(uintptr_t)0xe000ed94u&1u)!=0u)return 3u;
    if(count+start>=17u)return 5u;
    uint32_t packed[32];
    for(uint32_t i=0;i<count;i++,d+=24u) {
        uint32_t base=*(const volatile uint32_t *)(const void *)(d+4u)&~31u;
        base|=(uint32_t)d[8]<<3;base|=(uint32_t)d[9]<<1;base|=d[10];
        packed[i*2u]=base;
        uint32_t limit=*(const volatile uint32_t *)(const void *)(d+12u)&~31u;
        limit|=*(const volatile uint32_t *)(const void *)(d+16u)<<1;limit|=d[20];
        packed[i*2u+1u]=limit;
    }
    audio_uart_mpu_regions_write_4d44d2(start,packed,count);
    return 0u;
}
