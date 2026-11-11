#include <stdint.h>

/* Native 0x320f30..0x320f78: if the context (object +36) has a pending
 * flag (+700), clear it; when the time elapsed since the context's base
 * (+492 plus +496) is below the limit, attach the +484 block to the
 * object's radio (+44 word 33) and run child 304184 on it. Returns 1 when
 * the block was attached. */
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t current,
                                                        uint32_t previous);
extern uint32_t opencfw_em9305_child_304184(uintptr_t context,uintptr_t radio);

uint32_t opencfw_em9305_child_320f30(uintptr_t object,uint32_t now,uint32_t limit)
{
    uintptr_t context=*(volatile uint32_t *)(object+36u);
    uintptr_t block=context+484u;
    if(*(volatile uint8_t *)(context+700u)==0u)return 0u;
    uint32_t base=*(volatile uint32_t *)(context+492u)
                  +*(volatile uint32_t *)(context+496u);
    *(volatile uint8_t *)(context+700u)=0u;
    if(opencfw_em9305_auxiliary_elapsed_303f8c(base,now)>=limit)return 0u;
    uintptr_t radio=*(volatile uint32_t *)(object+44u);
    *(volatile uint32_t *)(radio+132u)=block;
    (void)opencfw_em9305_child_304184(block,context+532u);
    return 1u;
}
