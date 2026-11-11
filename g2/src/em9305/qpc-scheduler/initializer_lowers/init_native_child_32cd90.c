#include <stdint.h>

/* Native 0x32cd90..0x32cdde: power-control update. When the record has
 * power control enabled (+768) and the reported PHY (0x80281c) is in the
 * record's PHY mask bit (+77 minus 1), report the change (new level
 * 0x80281f, flags 0x80281d, signed delta against the stored level) through
 * 323620. Always store the new level in the per-PHY slot at +553. */
extern uint32_t opencfw_em9305_callback_323620(uintptr_t,uint32_t,uint32_t,uint32_t,
                                               int32_t,uint32_t,int32_t);

void opencfw_em9305_child_32cd90(uintptr_t record)
{
    volatile uint8_t *report=(volatile uint8_t *)(uintptr_t)0x802810u;
    if(*(volatile uint8_t *)(record+768u)!=0u) {
        uint32_t phy=*(volatile uint8_t *)(record+77u);
        uint32_t reported=report[0xc];
        if((reported>>((phy-1u)&31u))&1u) {
            int32_t level=(int8_t)report[0xf];
            uint32_t previous=*(volatile uint8_t *)(record+reported+553u);
            uint32_t flags=report[0xd];
            (void)opencfw_em9305_callback_323620(record,0u,1u,phy,level,flags,
                                                 (int8_t)(level-(int32_t)previous));
        }
    }
    *(volatile uint8_t *)(record+report[0xc]+553u)=report[0xf];
}
