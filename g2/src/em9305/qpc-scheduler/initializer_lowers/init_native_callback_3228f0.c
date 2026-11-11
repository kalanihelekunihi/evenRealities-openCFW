#include <stdint.h>

/* Native 0x3228f0..0x322908: common init, clear the 404-byte scan state
 * block at 0x804fd8, then run native 0x30e564 on it. */
extern uint32_t opencfw_em9305_common_init_303d18(uint32_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_lower_30e564(uint32_t);

uint32_t opencfw_em9305_callback_3228f0(uint32_t incoming)
{
    (void)opencfw_em9305_common_init_303d18(incoming);
    void *state = opencfw_em9305_memset((void *)(uintptr_t)0x804fd8u, 0u, 404u);
    return opencfw_em9305_init_lower_30e564((uint32_t)(uintptr_t)state);
}
