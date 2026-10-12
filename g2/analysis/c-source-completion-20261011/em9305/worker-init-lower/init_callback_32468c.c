#include <stdint.h>

/* Native 0x32468c..0x324696: load fixed queue 0x805194 into R0,
 * then unconditional branch to the already selected 0x314134 remover. */
extern uintptr_t opencfw_em9305_wsf_queue_remove(uintptr_t);
uint32_t opencfw_em9305_init_callback_32468c(uint32_t ignored)
{
    (void)ignored;
    return (uint32_t)opencfw_em9305_wsf_queue_remove(0x805194u);
}
