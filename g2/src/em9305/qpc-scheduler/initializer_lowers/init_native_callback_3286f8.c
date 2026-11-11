#include <stdint.h>

/* Native 0x3286f8..0x328712: clear the 28-byte state block at 0x80542c,
 * then run the 328dd4 callback on the incoming argument. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_callback_328dd4(uint32_t);

uint32_t opencfw_em9305_callback_3286f8(uint32_t argument)
{
    (void)opencfw_em9305_memset((void *)(uintptr_t)0x80542cu,0u,0x1cu);
    return opencfw_em9305_callback_328dd4(argument);
}
