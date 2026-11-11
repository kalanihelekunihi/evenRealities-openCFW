#include <stdint.h>

/* Native 0x31ba24..0x31ba52: pack a descriptor into bytes. Byte 0 is
 * type | sub<<1; a zero type adds {len+3, u32 value low byte, its second
 * byte, low byte of the halfword at +6} and returns 5, otherwise the
 * length byte is copied and 2 is returned. */
uint32_t opencfw_em9305_child_31ba24(uintptr_t out, uintptr_t in)
{
    volatile uint8_t *o=(volatile uint8_t *)out;
    volatile const uint8_t *i=(volatile const uint8_t *)in;
    o[0]=(uint8_t)((i[1]<<1)|i[0]);
    uint32_t type=i[0];
    uint32_t length=i[2];
    if(type!=0u){
        o[1]=(uint8_t)length;
        return 2u;
    }
    o[1]=(uint8_t)(length+3u);
    o[2]=(uint8_t)*(volatile const uint32_t *)(in+4u);
    o[3]=(uint8_t)(*(volatile const uint32_t *)(in+4u)>>8);
    o[4]=(uint8_t)*(volatile const uint16_t *)(in+6u);
    return 5u;
}
