#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x322754..0x32279a: PAwR receive callback. For an active entry
 * (+0) decode the packet against the shared report (((uintptr_t)&em9305_ram_8027e0 + 0x30u)) in the
 * entry's mode (+2), then map the decode status to a report code (0x1e:
 * 0x0e, other nonzero: 0x0d, 0: 0x0c) and report it through 32a000, or
 * through 31e4a0 when the mode byte is 0. Returns 0 for an idle entry. */
extern uint32_t opencfw_em9305_child_3191dc(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_32a000(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_31e4a0(uint32_t,uint32_t);

uint32_t opencfw_em9305_callback_322754(uintptr_t entry,uint32_t packet)
{
    if(*(volatile uint8_t *)entry==0u) return 0u;
    uint32_t status=opencfw_em9305_child_3191dc((uint32_t)((uintptr_t)&em9305_ram_8027e0 + 0x30u),packet,
                                                *(volatile uint8_t *)(entry+2u));
    uint32_t mode=*(volatile uint8_t *)(entry+2u);
    uint32_t code=(status==0x1eu)?0x0eu:((status!=0u)?0x0du:0x0cu);
    if(mode==0u) return opencfw_em9305_child_31e4a0(entry,code);
    return opencfw_em9305_child_32a000(entry,code);
}
