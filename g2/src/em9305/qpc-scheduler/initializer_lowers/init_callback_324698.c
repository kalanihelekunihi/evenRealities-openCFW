#include <stdint.h>
#include "em9305_ram.h"

/* Full native324698..3246be; BL33301c fills destination with R1 byte0.
 * Correct binding supersedes the erroneous memcpy-from-zero interpretation. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_init_callback_324698(uintptr_t slot)
{
    uintptr_t root=em9305_ram_805c5c.u32_805cac;
    uintptr_t node=*(volatile uint32_t *)slot;
    uint32_t bytes=*(volatile uint16_t *)(root+26u);
    (void)opencfw_em9305_memset((void *)node,0u,bytes);
    node=*(volatile uint32_t *)slot;
    uint32_t result=opencfw_em9305_wsf_queue_prepend((uintptr_t)&em9305_ram_805194,node);
    *(volatile uint32_t *)slot=0u;
    return result;
}
