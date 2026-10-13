#include <stdint.h>
static uint32_t clean_read(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void clean_write(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void clean_barrier(void){__asm__ volatile("dsb sy\n\tisb sy" ::: "memory");}
/* Native47510e..475194: source-owned SCB addresses and native cache policy. */
uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *range) {
    if(!(clean_read(0xe000ed14u)&(1u<<16))) {clean_barrier();return 0u;}
    if(!range) {
        clean_write(0xe000ed84u,0u);
        __asm__ volatile("dsb sy" ::: "memory");
        uint32_t ccsidr=clean_read(0xe000ed80u);
        uint32_t set=(ccsidr>>13)&0x7fffu;
        do {
            uint32_t way=(ccsidr>>3)&0x3ffu;
            do {
                clean_write(0xe000ef6cu,((set<<5)&0x3fe0u)|(way<<30));
                if(way==0u)break;
                --way;
            } while(1);
            if(set==0u)break;
            --set;
        } while(1);
        clean_barrier();
    } else {
        const volatile uint32_t *r=range;
        uint32_t size=r[1];
        uint32_t address=r[0];
        if((int32_t)size>=1) {
            uint32_t remaining=(address&31u)+size;
            __asm__ volatile("dsb sy" ::: "memory");
            do {
                clean_write(0xe000ef68u,address);
                address+=32u;
                remaining-=32u;
            } while((int32_t)remaining>=1);
            clean_barrier();
        }
    }
    return 0u;
}
