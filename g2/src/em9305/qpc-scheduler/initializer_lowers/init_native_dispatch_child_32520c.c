#include <stdint.h>

/* Native 0x32520c..0x32524e: store the two channel words into every
 * attached channel block (object words 14.., count at +52; block + 120)
 * and into the object's own block (+352), transforming each block. */
extern uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t channels);

uint32_t opencfw_em9305_dispatch_child_32520c(uintptr_t object,uint32_t first,
                                              uint32_t second)
{
    uint32_t count=*(volatile uint8_t *)(object+52u);
    if(count!=0u){
        uint32_t index=0u;
        do{
            uintptr_t child=*(volatile uint32_t *)(object+56u+index*4u);
            if(child!=0u){
                uintptr_t block=child+120u;
                *(volatile uint32_t *)block=first;
                *(volatile uint32_t *)(block+4u)=second;
                (void)opencfw_em9305_radio_channel_transform_30e3fc(block);
                count=*(volatile uint8_t *)(object+52u);
            }
            ++index;
        }while(index<count);
    }
    *(volatile uint32_t *)(object+352u)=first;
    *(volatile uint32_t *)(object+356u)=second;
    return opencfw_em9305_radio_channel_transform_30e3fc(object+352u);
}
