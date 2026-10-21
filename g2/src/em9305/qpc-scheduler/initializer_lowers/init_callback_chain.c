#include "init_lower_native.h"

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);
extern uint32_t opencfw_em9305_common_init_303008(uint32_t incoming);
extern uint32_t opencfw_em9305_common_init_302ff4(uint32_t incoming);
extern uint32_t opencfw_em9305_init_lower_30e42c(uint32_t incoming);
extern uint32_t opencfw_em9305_init_child_318ab8(uint32_t incoming);

/* Native 0x31369c..0x3136a8: exact 144-byte state clear. */
uint32_t opencfw_em9305_init_child_31369c(uint32_t incoming)
{
    (void)incoming;
    return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)0x805f28u, 0u, 144u);
}

/* Native 0x31e604..0x31e61c. Each child receives its predecessor's R0;
 * selected 303008/302ff4/30e42c bodies already establish their ABI. */
uint32_t opencfw_em9305_callback_31e604(uint32_t incoming)
{
    uint32_t value = opencfw_em9305_common_init_303008(incoming);
    value = opencfw_em9305_common_init_302ff4(value);
    value = opencfw_em9305_init_child_31369c(value);
    value = opencfw_em9305_init_child_318ab8(value);
    return opencfw_em9305_init_lower_30e42c(value);
}
