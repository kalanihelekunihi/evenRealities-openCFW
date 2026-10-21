/* Authenticated forward copy439be4..439c88, aligned fast entry439c04.
 * Preserve native staged reads and access widths; this is not memmove.
 * Callers ignore the native alignment-dependent r0 result. */
#include <stdint.h>
void audio_uart_checksum_copy(void *destination,const void *source,uint32_t length) {
    volatile uint8_t *d=destination;
    const volatile uint8_t *s=source;
    while(length && ((uintptr_t)s&3u)) { *d++=*s++; --length; }
    if(!length) return;
    if(((uintptr_t)d&3u)==0u) {
        while(length>=16u) {
            uint32_t a=*(const volatile uint32_t *)(s+0);
            uint32_t b=*(const volatile uint32_t *)(s+4);
            uint32_t c=*(const volatile uint32_t *)(s+8);
            uint32_t e=*(const volatile uint32_t *)(s+12);
            *(volatile uint32_t *)(d+0)=a;
            *(volatile uint32_t *)(d+4)=b;
            *(volatile uint32_t *)(d+8)=c;
            *(volatile uint32_t *)(d+12)=e;
            s+=16;d+=16;length-=16;
        }
        if(length&8u) {
            uint32_t a=*(const volatile uint32_t *)(s+0);
            uint32_t b=*(const volatile uint32_t *)(s+4);
            *(volatile uint32_t *)(d+0)=a;
            *(volatile uint32_t *)(d+4)=b;
            s+=8;d+=8;
        }
        if(length&4u) { *(volatile uint32_t *)d=*(const volatile uint32_t *)s;s+=4;d+=4; }
        if(length&2u) { *(volatile uint16_t *)d=*(const volatile uint16_t *)s;s+=2;d+=2; }
        if(length&1u) *d=*s;
    } else {
        while(length>=4u) {
            uint32_t a=*(const volatile uint32_t *)s;
            if(((uintptr_t)d&1u)==0u) {
                *(volatile uint16_t *)d=(uint16_t)a;
                *(volatile uint16_t *)(d+2)=(uint16_t)(a>>16);
            } else {
                d[0]=(uint8_t)a;
                *(volatile uint16_t *)(d+1)=(uint16_t)(a>>8);
                d[3]=(uint8_t)(a>>24);
            }
            s+=4;d+=4;length-=4;
        }
        while(length--) *d++=*s++;
    }
}
