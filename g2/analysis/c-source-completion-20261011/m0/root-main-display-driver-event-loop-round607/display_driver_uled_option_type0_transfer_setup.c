/* Apollo S200 DMA transfer setup at 0x538d58. */
#include <stdint.h>

static uint32_t get(uint32_t address) {
    return *(volatile const uint32_t *)(uintptr_t)address;
}
static void set(uint32_t address,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)address=value;
}

uint32_t display_driver_uled_setup_lower_538d58(uint32_t channel,
                                                  const void *parameters,
                                                  uint32_t *output) {
    uint32_t index=channel&255u;
    if (index>=12u) return 5u;
    if (parameters==0 || output==0) return 6u;
    const uint8_t *arg=(const uint8_t *)parameters;
    uint32_t count=(uint32_t)arg[0]|((uint32_t)arg[1]<<8)|
                   ((uint32_t)arg[2]<<16)|((uint32_t)arg[3]<<24);
    uint32_t base=(uint32_t)arg[4]|((uint32_t)arg[5]<<8)|
                  ((uint32_t)arg[6]<<16)|((uint32_t)arg[7]<<24);
    if (count<2u || base==0u) return 6u;
    uint32_t state=0x2006ef28u+index*44u;
    if (get(state)&0x01000000u) return 7u;
    set(state+24u,count*8u);
    for (uint32_t offset=4u;offset<=20u;offset+=4u)
        set(state+offset,base);
    set(state+8u,base+count*8u);
    set(state,(get(state)&0xfc000000u)|0x01cdcdcdu);
    uint32_t table=0x6c0f40u+index*40u;
    set(state+36u,table);
    set(state+28u,0u);set(state+32u,0u);
    set(get(table+8u),0u);
    set(get(table+12u),0u);
    set(get(table+16u),get(get(table+16u))|get(table+20u));
    set(get(table+4u),base);
    set(get(table),((uint32_t)arg[8]&1u)<<1);
    *output=state;
    return 0u;
}
