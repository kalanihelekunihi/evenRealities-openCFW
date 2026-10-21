#include <stdint.h>

/* Native 0x32182c is an unconditional branch to the already selected
 * full 0x303650 common initializer; the incoming R0 is forwarded. */
extern uint32_t opencfw_em9305_common_init_303650(uint32_t);
uint32_t opencfw_em9305_init_registered_32182c(uint32_t incoming)
{ return opencfw_em9305_common_init_303650(incoming); }

/* Native 0x3266f8..0x32671a, including the delayed store at 0x326718.
 * The early JNE retains incoming R0=context. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
uint32_t opencfw_em9305_init_registered_3266f8(uintptr_t context)
{
    uint8_t initialized=*(volatile uint8_t *)(context+608u);
    if (initialized!=0u) return (uint32_t)context;
    uint32_t state=*(volatile uint32_t *)(context+636u);
    *(volatile uint8_t *)(context+608u)=1u;
    state&=~(1u<<6);
    *(volatile uint32_t *)(context+640u)=0u;
    *(volatile uint32_t *)(context+636u)=state;
    return opencfw_em9305_receive_terminate_325c08(context,110u);
}
