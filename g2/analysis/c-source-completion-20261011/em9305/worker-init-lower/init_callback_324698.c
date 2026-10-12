#include <stdint.h>

/* Complete native 0x324698..0x3246be. Native 0x33301c is the byte-fill
 * entry, with R1=0 and R2=length here. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_init_callback_324698(uintptr_t slot)
{
    uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uintptr_t node=*(volatile uint32_t *)slot;
    uint32_t bytes=*(volatile uint16_t *)(root+26u);
    (void)opencfw_em9305_memset((void *)node,0u,bytes);
    node=*(volatile uint32_t *)slot;
    uint32_t result=opencfw_em9305_wsf_queue_prepend(0x805194u,node);
    *(volatile uint32_t *)slot=0u;
    return result;
}
