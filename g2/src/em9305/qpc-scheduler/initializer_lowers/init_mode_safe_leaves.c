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

#include <stdint.h>

/* Native 0x313338..0x313352. The comparison reads the live registered
 * context at 0x805f14; the state byte is read only on a matching context. */
extern uint32_t opencfw_em9305_auxiliary_transition_333a60(void);
uint32_t opencfw_em9305_mode_event_313338(uintptr_t field)
{
    volatile uint8_t *const root=(volatile uint8_t *)(uintptr_t)0x805f04u;
    if (*(volatile uint32_t *)(uintptr_t)0x805f14u != (uint32_t)field)
        return (uint32_t)field;
    uint32_t state=root[0];
    if (state==2u) return state;
    return opencfw_em9305_auxiliary_transition_333a60();
}
#include <stdint.h>

/* Native return-delay slot stores at 0x32cb40 and 0x32cf78. */
uint32_t opencfw_em9305_mode_event_32cb40(uintptr_t context)
{
    *(volatile uint8_t *)(context+12u)=0x3du;
    return (uint32_t)context;
}

uint32_t opencfw_em9305_mode_event_32cf78(uintptr_t context)
{
    *(volatile uint8_t *)(context+12u)=0xffu;
    return (uint32_t)context;
}
