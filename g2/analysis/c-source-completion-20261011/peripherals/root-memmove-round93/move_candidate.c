#include <stdint.h>
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
/* Full native439710..4397a6. Forward branch delegates to canonical439be4;
 * reverse preserves byte alignment, four-word blocks and unaligned stores.
 * Compiler helper has no stable R0 return contract. */
void audio_uart_compiler_move_439710(void *destination,const void *source,uint32_t length)
{
    uint32_t d=(uint32_t)(uintptr_t)destination,s=(uint32_t)(uintptr_t)source;
    if(s>=d || d>=s+length) { (void)audio_queue_copy_bytes(destination,source,length);return; }
    s+=length;d+=length;
    while((s&3u)!=0u && length!=0u) {
        --s;--d;*(volatile uint8_t *)(uintptr_t)d=*(const volatile uint8_t *)(uintptr_t)s;--length;
    }
    if((d&3u)==0u) {
        while(length>=16u) {
            uint32_t a=*(const volatile uint32_t *)(uintptr_t)(s-16u);
            uint32_t b=*(const volatile uint32_t *)(uintptr_t)(s-12u);
            uint32_t c=*(const volatile uint32_t *)(uintptr_t)(s-8u);
            uint32_t e=*(const volatile uint32_t *)(uintptr_t)(s-4u);
            s-=16u;d-=16u;
            *(volatile uint32_t *)(uintptr_t)d=a;
            *(volatile uint32_t *)(uintptr_t)(d+4u)=b;
            *(volatile uint32_t *)(uintptr_t)(d+8u)=c;
            *(volatile uint32_t *)(uintptr_t)(d+12u)=e;
            length-=16u;
        }
        while(length>=4u) {
            s-=4u;uint32_t value=*(const volatile uint32_t *)(uintptr_t)s;d-=4u;
            *(volatile uint32_t *)(uintptr_t)d=value;length-=4u;
        }
    } else {
        while(length>=4u) {
            s-=4u;uint32_t value=*(const volatile uint32_t *)(uintptr_t)s;d-=4u;
            if((d&1u)==0u) {
                *(volatile uint16_t *)(uintptr_t)d=(uint16_t)value;
                *(volatile uint16_t *)(uintptr_t)(d+2u)=(uint16_t)(value>>16u);
            } else {
                *(volatile uint8_t *)(uintptr_t)d=(uint8_t)value;
                *(volatile uint16_t *)(uintptr_t)(d+1u)=(uint16_t)(value>>8u);
                *(volatile uint8_t *)(uintptr_t)(d+3u)=(uint8_t)(value>>24u);
            }
            length-=4u;
        }
    }
    while(length!=0u) {
        --s;--d;*(volatile uint8_t *)(uintptr_t)d=*(const volatile uint8_t *)(uintptr_t)s;--length;
    }
}
/* Full native45475a..454768 restores destination after void compiler helper. */
void *audio_uart_lv_grid_move_45475a(void *destination,const void *source,uint32_t length)
{
    audio_uart_compiler_move_439710(destination,source,length);return destination;
}
