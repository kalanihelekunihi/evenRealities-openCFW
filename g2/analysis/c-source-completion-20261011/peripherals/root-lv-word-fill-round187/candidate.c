#include <stdint.h>
/* Native4d555c..4d558e; repeated WORD pattern, not byte-replicating memset.
 * Return is the advanced destination; exact 16/8/4/2/1 store staging. */
void *audio_uart_lv_word_fill_4d555c(void *destination,uint32_t size,uint32_t pattern) {
    volatile uint8_t *p=destination;
    while(size>=16u) {
        *(volatile uint32_t *)(p+0u)=pattern;
        *(volatile uint32_t *)(p+4u)=pattern;
        *(volatile uint32_t *)(p+8u)=pattern;
        *(volatile uint32_t *)(p+12u)=pattern;
        p+=16u;size-=16u;
    }
    if(size&8u) {
        *(volatile uint32_t *)(p+0u)=pattern;
        *(volatile uint32_t *)(p+4u)=pattern;
        p+=8u;
    }
    if(size&4u){*(volatile uint32_t *)p=pattern;p+=4u;}
    if(size&2u){*(volatile uint16_t *)p=(uint16_t)pattern;p+=2u;}
    if(size&1u){*p=(uint8_t)pattern;p+=1u;}
    return (void *)p;
}
/* Native48949c..4894a2: two consumed arguments; zero pattern imposed. */
void audio_uart_lv_memzero_48949c(void *destination,uint32_t size) {
    (void)audio_uart_lv_word_fill_4d555c(destination,size,0u);
}
