#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3136fc..0x313744: pick an associated slot value in
 * [minimum, maximum] by step (excluding id), and if it is available for
 * the extent, record it in the per-id table at ((uintptr_t)&em9305_ram_805eec + 0x4cu) and in *out and
 * reserve it. Returns the availability result. */
extern uint32_t opencfw_em9305_associated_select_333948(uint32_t minimum,
    uint32_t maximum,uint32_t step,uint32_t direction,uint32_t exclude);
extern uint32_t opencfw_em9305_associated_available_33382c(uint32_t id,
    uint32_t value,uint32_t extent,uint32_t existing);
extern uint32_t opencfw_em9305_associated_set_3338f4(uint32_t id,uint32_t value,
                                                     uint32_t extent);

uint32_t opencfw_em9305_child_3136fc(uint32_t id,uint32_t minimum,
                                     uint32_t maximum,uint32_t step,
                                     uint32_t extent,uintptr_t out)
{
    uint32_t value=opencfw_em9305_associated_select_333948(minimum,maximum,
                                                           step,0u,id);
    uint32_t available=opencfw_em9305_associated_available_33382c(id,value,
                                                                  extent,1u);
    if(available!=0u){
        *(volatile uint32_t *)(((uintptr_t)&em9305_ram_805eec + 0x4cu)+id*4u)=value;
        *(volatile uint32_t *)out=value;
        (void)opencfw_em9305_associated_set_3338f4(id,value,extent);
    }
    return available;
}
