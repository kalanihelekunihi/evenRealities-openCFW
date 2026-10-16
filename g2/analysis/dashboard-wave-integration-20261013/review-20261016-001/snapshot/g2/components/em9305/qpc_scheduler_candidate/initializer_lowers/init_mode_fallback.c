#include <stdint.h>

/* Complete native 0x31c420..0x31c48c. Child returns on the transition
 * routes are overwritten by the context state read before the rejoin. */
extern uint32_t opencfw_em9305_mode_event_32cac4(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cacc(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cad4(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t);
extern uint32_t opencfw_em9305_init_response_packet_326a84(uintptr_t);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t);
uint32_t opencfw_em9305_mode_event_31c420(uintptr_t context,
                                            uint32_t event)
{
    if (event==0x0du)
        return opencfw_em9305_init_response_packet_326a84(context);
    if (event==0x0eu)
        return opencfw_em9305_phy_reject_32698c(context,0x1eu,0u);
    switch (event) {
    case 0x49u:(void)opencfw_em9305_mode_event_32cac4(context);break;
    case 0x4au:(void)opencfw_em9305_mode_event_32cacc(context);break;
    case 0x51u:(void)opencfw_em9305_mode_event_32cadc(context);break;
    case 0x73u:(void)opencfw_em9305_mode_event_32cad4(context);break;
    default:return (uint32_t)context;
    }
    uint32_t prior=*(volatile uint8_t *)(context+1u);
    *(volatile uint8_t *)(context+620u)=0u;
    /* Native 31c482 is the BRNE.D delay slot and runs on either path. */
    *(volatile uint8_t *)(context+1u)=3u;
    if (prior!=2u) return prior;
    return opencfw_em9305_ll_schedule_notify_313354(context+16u);
}
