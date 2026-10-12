#include <stdint.h>

/* Native 0x32c978 and 0x32cadc: return-delay byte stores preserve R0. */
uint32_t opencfw_em9305_mode_event_32c978(uintptr_t context)
{
    *(volatile uint8_t *)(context+12u)=0x3eu;
    return (uint32_t)context;
}

uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t context)
{
    *(volatile uint8_t *)(context+12u)=0x22u;
    return (uint32_t)context;
}

/* Native 0x32279c tail-branches to 0x313338 with R0=context+16. */
extern uint32_t opencfw_em9305_mode_event_313338(uintptr_t field);
uint32_t opencfw_em9305_mode_event_32279c(uintptr_t context)
{ return opencfw_em9305_mode_event_313338(context+16u); }

/* Native 0x31ac3c: bit17 clear and word640 zero occur before the tail call.
 * The skip path returns its incoming R0 pointer without a child call. */
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t context,
                                                    uint32_t byte12);
uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t context)
{
    uint32_t flags=*(volatile uint32_t *)(context+636u);
    if((flags&(1u<<17u))==0u) return (uint32_t)context;
    uint32_t byte12=*(volatile uint8_t *)(context+12u);
    *(volatile uint32_t *)(context+636u)=flags&~(1u<<17u);
    *(volatile uint32_t *)(context+640u)=0u;
    return opencfw_em9305_mode_event_322fdc(context,byte12);
}
