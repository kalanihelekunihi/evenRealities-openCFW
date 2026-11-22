#include <stdint.h>

/* Native 0x3027f4 is owned by init_native_child_3027f4.c. */
extern uint64_t opencfw_em9305_child_3027f4(uint32_t,uint32_t,uint32_t);

/* Full native 0x324c68..0x324c96.  R16 increments in the branch delay slot
 * for every one of the 37 iterations, including the last. */
uint32_t opencfw_em9305_init_secondary_channel_324c68(uintptr_t channels)
{
    uint32_t count=0u,last=0u;
    for(uint32_t index=0u;index<37u;index++) {
        uint32_t low=*(volatile uint32_t *)channels;
        uint32_t high=*(volatile uint32_t *)(channels+4u);
        uint32_t shifted=(uint32_t)opencfw_em9305_child_3027f4(low,high,index);
        last=(uint32_t)(channels+count);
        if((shifted&1u)!=0u) {
            *(volatile uint8_t *)(channels+8u+count)=(uint8_t)index;
            count++;
        }
    }
    *(volatile uint8_t *)(channels+45u)=(uint8_t)count;
    return last;
}
