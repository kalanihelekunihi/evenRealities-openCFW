#include <stdint.h>
void audio_uart_mpu_attribute_write_raw_4d43f6(void *registers,uint32_t id,uint32_t attribute) {
    uint32_t bank=(uint8_t)id>>2;
    uint32_t shift=((uint32_t)(uint8_t)id<<3)&24u;
    uint32_t mask=255u<<shift;
    uint32_t value=(uint32_t)(uint8_t)attribute<<shift;
    if(bank<2u) {
        volatile uint32_t *cell=(volatile uint32_t *)((uint8_t *)registers+48u+bank*4u);
        *cell=(*cell&~mask)|(value&mask);
    }
}
void audio_uart_mpu_attribute_write_4d4434(uint32_t id,uint32_t attribute) {
    audio_uart_mpu_attribute_write_raw_4d43f6((void *)(uintptr_t)0xe000ed90u,(uint8_t)id,(uint8_t)attribute);
}
void audio_uart_mpu_copy_words_4d4446(void *destination,const void *source,uint32_t count) {
    volatile uint32_t *d=destination;
    const volatile uint32_t *s=source;
    for(uint32_t i=0;i<count;i++)d[i]=s[i];
}
void audio_uart_mpu_regions_write_raw_4d445e(void *registers,uint32_t start,const uint32_t *packed,uint32_t count) {
    volatile uint32_t *region_number=(volatile uint32_t *)((uint8_t *)registers+8u);
    if(count==1u) {
        *region_number=start;
        audio_uart_mpu_copy_words_4d4446((uint8_t *)registers+12u,packed,2u);
        return;
    }
    uint32_t aligned=start&~3u;
    uint32_t index=start&3u;
    *region_number=aligned;
    while(count+index>=5u) {
        uint32_t chunk=4u-index;
        audio_uart_mpu_copy_words_4d4446((uint8_t *)registers+12u+index*8u,packed,2u*chunk);
        packed+=2u*chunk;
        count-=chunk;index=0u;aligned+=4u;
        *region_number=aligned;
    }
    audio_uart_mpu_copy_words_4d4446((uint8_t *)registers+12u+index*8u,packed,2u*count);
}
void audio_uart_mpu_regions_write_4d44d2(uint32_t start,const uint32_t *packed,uint32_t count) {
    audio_uart_mpu_regions_write_raw_4d445e((void *)(uintptr_t)0xe000ed90u,start,packed,count);
}
