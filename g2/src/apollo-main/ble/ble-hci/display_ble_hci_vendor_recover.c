/* Native vendor transfer recovery 0x55bdac, MMIO 0x40050000 from ROM
 * 0x55c548; recovery pattern 0xdeadbeef from ROM 0x55c554. */
#include <stdint.h>

extern void audio_ble_vendor_yield_4807a0(uint32_t);
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static uint32_t read_reg(const volatile uint8_t *p,uint32_t off) {
    return *(volatile const uint32_t *)(const void *)(p+off);
}
static void write_reg(volatile uint8_t *p,uint32_t off,uint32_t value) {
    *(volatile uint32_t *)(void *)(p+off)=value;
}
static uint32_t available_rx(const volatile uint8_t *p) {
    return (read_reg(p,0x100u)&0xffffffu)>>16u;
}

void audio_ble_vendor_recover_55bdac(uint8_t *row,uint32_t status) {
    uint32_t channel=get(row+4u);
    uint32_t interval=get(row+0x864u);
    volatile uint8_t *base=(volatile uint8_t *)(uintptr_t)(0x40050000u+channel*0x1000u);
    uint32_t saved=read_reg(base,0x200u);
    write_reg(base,0x200u,0u);
    if((status&0x800u)!=0u) {
        if((read_reg(base,0x218u)&2u)!=0u) {
            uint32_t remaining=read_reg(base,0x21cu);
            while(remaining!=0u) {
                if(((read_reg(base,0x100u)&0xffffu)>>8u)>3u) {
                    write_reg(base,0x10cu,0xdeadbeefu);
                    if(remaining<5u)break;
                    remaining-=4u;
                }
            }
            do {} while((read_reg(base,0x248u)&6u)!=4u);
        } else {
            while((read_reg(base,0x248u)&2u)!=0u) {
                do {} while(available_rx(base)>3u);
            }
            do {} while((read_reg(base,0x248u)&6u)!=4u);
            while(available_rx(base)!=0u) {
                do {} while(available_rx(base)>3u);
            }
        }
    }
    if((status&0x210u)!=0u) {
        uint32_t saved_cfg=read_reg(base,0x388u);
        do {} while((read_reg(base,0x248u)&6u)!=4u);
        write_reg(base,0x11cu,read_reg(base,0x11cu)&~0x10u);
        write_reg(base,0x110u,read_reg(base,0x110u)&~2u);
        write_reg(base,0x388u,read_reg(base,0x388u)|2u);
        audio_ble_vendor_yield_4807a0(interval*6u);
        write_reg(base,0x388u,saved_cfg);
        write_reg(base,0x110u,read_reg(base,0x110u)|2u);
        write_reg(base,0x11cu,read_reg(base,0x11cu)|0x10u);
    }
    write_reg(base,0x208u,0xffffffffu);
    write_reg(base,0x200u,saved);
}
