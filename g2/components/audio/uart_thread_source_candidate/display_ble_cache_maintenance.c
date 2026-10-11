/* Native ARM SCB D-cache maintenance 0x475014, including set/way and range. */
#include <stdint.h>
#include <stddef.h>
static volatile uint32_t *const ccr=(volatile uint32_t *)(uintptr_t)0xe000ed14u;
static volatile uint32_t *const csselr=(volatile uint32_t *)(uintptr_t)0xe000ed84u;
static volatile uint32_t *const ccsidr=(volatile uint32_t *)(uintptr_t)0xe000ed80u;
static volatile uint32_t *const dcisw=(volatile uint32_t *)(uintptr_t)0xe000ef60u;
static volatile uint32_t *const dccisw=(volatile uint32_t *)(uintptr_t)0xe000ef74u;
static volatile uint32_t *const dcimvac=(volatile uint32_t *)(uintptr_t)0xe000ef5cu;
static volatile uint32_t *const dccimvac=(volatile uint32_t *)(uintptr_t)0xe000ef70u;
static void barrier(void) { __asm__ volatile("dsb sy\n\tisb sy" ::: "memory"); }
void audio_ble_privacy_cache_maintenance(const uint32_t *range,uint8_t clean) {
    if((*ccr&(1u<<16))==0u) { barrier();return; }
    if(range==NULL) {
        *csselr=0u;
        __asm__ volatile("dsb sy" ::: "memory");
        uint32_t geometry=*ccsidr;
        uint32_t sets=(geometry&0x0fffffffu)>>13;
        do {
            uint32_t ways=(geometry&0x1fffu)>>3;
            do {
                uint32_t selector=((sets&0x1ffu)<<5)|(ways<<30);
                if(clean==0u) *dcisw=selector;
                else *dccisw=selector;
            } while(ways--!=0u);
        } while(sets--!=0u);
        barrier();
        return;
    }
    uint32_t address=range[0];
    int32_t remaining=(int32_t)range[1];
    if(remaining>0) {
        remaining+=(int32_t)(address&31u);
        __asm__ volatile("dsb sy" ::: "memory");
        do {
            if(clean==0u) *dcimvac=address;
            else *dccimvac=address;
            address+=32u;
            remaining-=32;
        } while(remaining>0);
        barrier();
    }
}
