#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x324734..0x324768: post event 0x100 to the task at ((uintptr_t)&em9305_ram_805af0 + 0x28u) and
 * set the record state byte (+36) to 2 when the state is 1, or when the
 * pending byte at +777 is set and the handle byte at +25 is 0xff. */
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t task, uint32_t event);

uint32_t opencfw_em9305_child_324734(uintptr_t record)
{
    if(*(volatile uint8_t *)(record+36u)!=1u){
        if(*(volatile uint8_t *)(record+777u)==0u)return 0u;
        uint32_t handle=*(volatile uint8_t *)(record+25u);
        if(handle!=255u)return handle;
    }
    uint32_t task=em9305_ram_805af0.u8_805b18;
    *(volatile uint8_t *)(record+36u)=2u;
    return opencfw_em9305_wsf_event_post(task,256u);
}
