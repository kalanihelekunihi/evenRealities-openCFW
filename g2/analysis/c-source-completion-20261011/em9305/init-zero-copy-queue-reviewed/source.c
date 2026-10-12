#include <stdint.h>

/* Complete native 0x324698..0x3246be. The source argument to native
 * memcpy33301c is literal address zero. This preserves the stock read as
 * an explicit platform memory contract; its content is not invented here. */
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_init_callback_324698(uintptr_t slot)
{
    uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uintptr_t node=*(volatile uint32_t *)slot;
    uint32_t bytes=*(volatile uint16_t *)(root+26u);
    (void)opencfw_em9305_memcpy((void *)node,(const void *)(uintptr_t)0u,bytes);
    node=*(volatile uint32_t *)slot;
    uint32_t result=opencfw_em9305_wsf_queue_prepend(0x805194u,node);
    *(volatile uint32_t *)slot=0u;
    return result;
}
