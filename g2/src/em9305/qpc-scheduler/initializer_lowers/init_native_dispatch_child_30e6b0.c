#include <stdint.h>

/* Native 0x30e6b0..0x30e758: channel selection algorithm #2 style hop.
 * Permute the 16-bit counter (+0x32) with the stock mask/shift network,
 * scale by 17, add the access-address half (+0x30) and store it back.
 * Pick a step k from the used-channel count (+45), then the next index
 * (+52) is ((n - 2k + 1) * (state ^ half) >> 16) + k + index, as a 16-bit
 * value, modulo n; return the used channel at +8 + index. */
uint32_t opencfw_em9305_dispatch_child_30e6b0(uintptr_t state)
{
    uint32_t counter=*(volatile uint16_t *)(state+0x32u);
    uint32_t bits=(counter&0xf0f0u)|((counter<<8)&0xf0f00u);
    bits=(bits&0xcccc0u)|((bits<<4)&0x333300u);
    bits=((bits&0x2aaa80u)|((bits<<2)&0x555500u))>>7;
    int32_t used=*(volatile uint8_t *)(state+45u);
    int32_t above=used-10;
    int32_t half=above>>1;
    uint32_t access=*(volatile uint16_t *)(state+0x30u);
    int32_t spare=used-5;
    uint32_t index=*(volatile uint8_t *)(state+52u);
    int32_t cap=spare<3?spare:3;
    int32_t pick=above>0x17?0xb:half;
    uint32_t mixed=(bits&0xffffu)*0x11u+access;
    *(volatile uint16_t *)(state+0x32u)=(uint16_t)mixed;
    int32_t step;
    if(pick>=cap) {
        if(above>=0x18) step=0xb;
        else step=above>=2?half:1;
    } else {
        if(spare>=4) step=3;
        else if(spare<1) step=1;
        else step=spare;
    }
    mixed^=access;
    uint32_t span=(uint32_t)used-((uint32_t)step<<1)+1u;
    uint32_t next=((span*(mixed&0xffffu))>>16)+(uint32_t)step+index;
    next=(uint16_t)next%(uint32_t)used;
    *(volatile uint8_t *)(state+52u)=(uint8_t)next;
    return *(volatile uint8_t *)(state+next+8u);
}
