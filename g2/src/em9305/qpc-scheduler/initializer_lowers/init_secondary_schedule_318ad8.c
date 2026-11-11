#include <stdint.h>

static uint32_t native_mpywhl(uint32_t value,int32_t factor)
{
    uint32_t out;
    if(factor==1250)
        out=(uint32_t)value*1250u;
    else
        out=(uint32_t)value*(uint32_t)-1250;
    return out;
}

/* Full native 0x318ad8..0x318b36; halfword addresses are byte+266 and
 * byte+262 because LDH.AS scales its immediate by two. */
uint32_t opencfw_em9305_init_secondary_schedule_318ad8(
    uintptr_t connection,uint32_t current)
{
    uint32_t flag=*(volatile uint8_t *)(connection+2u);
    uint32_t multiplier=*(volatile uint16_t *)(connection+266u);
    if(flag!=0u) {
        uint32_t limit=*(volatile uint16_t *)(connection+202u)-1u;
        uint32_t base=*(volatile uint32_t *)(connection+208u);
        uint32_t delta=(current-limit)&0xffffu;
        if(delta<=32766u)
            return base+native_mpywhl(
                (uint32_t)(uint16_t)delta*(uint32_t)(uint16_t)multiplier,1250);
        return base+native_mpywhl(
            (uint32_t)(uint16_t)(limit-current)*(uint32_t)(uint16_t)multiplier,
            -1250);
    }
    uint32_t limit=*(volatile uint16_t *)(connection+262u);
    uint32_t base=*(volatile uint32_t *)(connection+24u);
    uint32_t delta=(current-limit)&0xffffu;
    if(delta<=32766u)
        return base+native_mpywhl(
            (uint32_t)(uint16_t)delta*(uint32_t)(uint16_t)multiplier,1250);
    return base+native_mpywhl(
        (uint32_t)(uint16_t)(limit-current)*(uint32_t)(uint16_t)multiplier,-1250);
}
