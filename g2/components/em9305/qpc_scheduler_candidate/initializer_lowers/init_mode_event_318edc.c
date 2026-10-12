#include <stdint.h>

/* Native 0x318edc..0x318f2a.  Default nonmatching events return their
 * incoming context pointer; state transition returns prior state unless
 * the prior state was 2, when scheduler-notify's R0 is returned. */
extern uint32_t opencfw_em9305_mode_event_32cf78(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_32cb40(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t context);
extern uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t context);
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object);

uint32_t opencfw_em9305_mode_event_318edc(uintptr_t context,uint32_t event)
{
    if(event==0x4cu) {
        (void)opencfw_em9305_mode_event_31ac3c(context);
        (void)opencfw_em9305_mode_event_3231c4(context);
        return opencfw_em9305_init_connection_release_31ad90(context);
    }
    if(event==0u) (void)opencfw_em9305_mode_event_32cf78(context);
    else if(event==0x48u) (void)opencfw_em9305_mode_event_32cb40(context);
    else if(event!=0x47u) return (uint32_t)context;

    uint32_t prior=*(volatile uint8_t *)(context+1u);
    *(volatile uint8_t *)(context+1u)=3u;
    *(volatile uint8_t *)(context+620u)=0u; /* BRNE delay slot */
    if(prior!=2u) return prior;
    return opencfw_em9305_ll_schedule_notify_313354(context+16u);
}
