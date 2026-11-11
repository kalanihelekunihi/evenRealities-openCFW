/* Stock 0x8eeba: preserve sentinel read and live record count. */
#include <stdint.h>
static uint8_t byte(uint32_t p){return *(volatile uint8_t *)(uintptr_t)p;}
static uint16_t half(uint32_t p){return *(volatile uint16_t *)(uintptr_t)p;}
static uint32_t word(uint32_t p){return *(volatile uint32_t *)(uintptr_t)p;}
static void put(uint32_t p,uint32_t v){*(volatile uint32_t *)(uintptr_t)p=v;}
uint32_t r1_gomore_optical_compact_native(uint32_t state)
{
    uint32_t count=byte(state+81u);
    if(!count || word(state+84u)<=20u) return state;
    uint32_t drop=0;
    while(half(state+90u+drop*16u)<25u && (int32_t)count>(int32_t)drop) drop++;
    for(uint32_t i=0;(int32_t)(byte(state+81u)-drop)>(int32_t)i;i++) {
        uint32_t source=state+(i+drop)*16u,destination=state+i*16u+88u;
        uint32_t b=word(source+92u),c=word(source+96u);
        uint32_t a=word(source+88u),d=word(source+100u);
        put(destination,a);put(destination+4u,b);put(destination+8u,c);put(destination+12u,d);
        *(volatile uint16_t *)(uintptr_t)destination=(uint16_t)(half(destination)-25u);
        *(volatile uint16_t *)(uintptr_t)(destination+2u)=(uint16_t)(half(destination+2u)-25u);
        *(volatile uint16_t *)(uintptr_t)(destination+4u)=(uint16_t)(half(destination+4u)-25u);
    }
    *(volatile uint8_t *)(uintptr_t)(state+81u)=(uint8_t)(byte(state+81u)-drop);
    return state+81u;
}
