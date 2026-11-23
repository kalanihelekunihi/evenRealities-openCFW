#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3235bc..0x323620: collect the completed-packet counts of the
 * object's streams (table +56, count +52): for each live stream (+36
 * clear) with a non-zero count (+16), record its handle (+2) and count and
 * clear the count. When any were found and a host callback is registered
 * at ((uintptr_t)&em9305_ram_805af0 + 0x48u), report them as (number, handles[4], counts[4]). The stock
 * frame holds four entries; more than four live streams overflow it. */
typedef void (*opencfw_em9305_completed_callback_t)(uint32_t number,
                                                    uint16_t *handles,
                                                    uint16_t *counts);

void opencfw_em9305_child_3235bc(uintptr_t object)
{
    uint16_t handles[4]={0u,0u,0u,0u};
    uint16_t counts[4]={0u,0u,0u,0u};
    uint32_t found=0u;
    for(uint32_t index=0u;index<*(volatile uint8_t *)(object+52u);++index){
        uintptr_t stream=*(volatile uint32_t *)(object+56u+index*4u);
        if(stream==0u)continue;
        if(*(volatile uint8_t *)(stream+36u)!=0u)continue;
        if(*(volatile uint8_t *)(stream+16u)==0u)continue;
        handles[found&0xffu]=*(volatile uint16_t *)(stream+2u);
        counts[found&0xffu]=*(volatile uint8_t *)(stream+16u);
        ++found;
        *(volatile uint8_t *)(stream+16u)=0u;
    }
    uintptr_t callback=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805af0 + 0x48u);
    if(callback==0u||(uint8_t)found==0u)return;
    ((opencfw_em9305_completed_callback_t)callback)((uint8_t)found,handles,counts);
}
