#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32a47c..0x32a4be: associated-mode event callback. Event 10
 * counts in the context halfword +910; event 0 marks the context (+630 = 1),
 * counts in +904 and, when byte +341 is set, in the global counter at
 * ((uintptr_t)&em9305_ram_805688 + 0x4u). Other events are ignored. */
void opencfw_em9305_associated_callback_32a47c(uintptr_t object,uint32_t event)
{
    uintptr_t context=*(volatile uint32_t *)(object+36u);
    if(event==10u){
        uint32_t count=*(volatile uint16_t *)(context+910u);
        *(volatile uint16_t *)(context+910u)=(uint16_t)(count+1u);
        return;
    }
    if(event!=0u)return;
    uint32_t enabled=*(volatile uint8_t *)(context+341u);
    uint32_t count=*(volatile uint16_t *)(context+904u);
    *(volatile uint8_t *)(context+630u)=1u;
    *(volatile uint16_t *)(context+904u)=(uint16_t)(count+1u);
    if(enabled==0u)return;
    uint32_t total=*(volatile uint16_t *)((uintptr_t)&em9305_ram_805688 + 0x4u);
    *(volatile uint16_t *)((uintptr_t)&em9305_ram_805688 + 0x4u)=(uint16_t)(total+1u);
}
