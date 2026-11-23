#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x323314..0x323370: report mode event 10 for the connection
 * context (handle = context index in the 912-byte table at *((uintptr_t)&em9305_ram_805c5c + 0x14u)).
 * The 16-byte event carries the handle at +0 and +6, the reason at +3 and
 * +4, and an 8-byte primary query result at +8 (cleared first). The
 * query uses the context words +536/+540 when the configuration byte
 * (*((uintptr_t)&em9305_ram_805c5c + 0x50u))+4 is at least 9, otherwise +544/+548. Byte +5 is not
 * written, as in stock. */
extern uint32_t opencfw_em9305_primary_query_313960(uintptr_t packet,
                                                   uint32_t first,
                                                   uint32_t second);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_mode_event_323314(uintptr_t context,uint32_t reason)
{
    _Alignas(4) uint8_t event[16];
    uintptr_t base=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x14u);
    uintptr_t config=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x50u);
    *(uint32_t *)(void *)(event+12)=0u;
    int32_t index=(int32_t)(context-base)/912;
    *(uint32_t *)(void *)(event+8)=0u;
    event[4]=(uint8_t)reason;
    event[3]=(uint8_t)reason;
    event[2]=10u;
    *(uint16_t *)(void *)(event+6)=(uint8_t)index;
    *(uint16_t *)(void *)event=(uint8_t)index;
    uint32_t first,second;
    if(*(volatile uint8_t *)(config+4u)>=9u){
        second=*(volatile uint32_t *)(context+540u);
        first=*(volatile uint32_t *)(context+536u);
    }else{
        second=*(volatile uint32_t *)(context+548u);
        first=*(volatile uint32_t *)(context+544u);
    }
    (void)opencfw_em9305_primary_query_313960((uintptr_t)(event+8),first,second);
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
