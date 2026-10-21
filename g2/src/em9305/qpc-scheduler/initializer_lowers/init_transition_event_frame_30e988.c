#include <stdint.h>
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

/* Native 0x30e988..0x30e9a0: BLINK at frame+0, initialized event word
 * at+4 and incoming halfword at+8. Bytes+10/+11 are ambient native stack
 * contents. The ARC wrapper keeps their actual frame provenance. */
#ifdef __arc__
__attribute__((naked))
uint32_t opencfw_em9305_init_transition_event_30e988(uint32_t id __attribute__((unused)))
{
    __asm__ volatile(
        "st.aw blink,[sp,-12]\n\t"
        "sth r0,[sp,8]\n\t"
        "mov r0,0x1f\n\t"
        "asl r0,r0,0x10\n\t"
        "st r0,[sp,4]\n\t"
        "add r0,sp,4\n\t"
        "bl opencfw_em9305_ll_event_callback_30e79c\n\t"
        "ld.ab blink,[sp,12]\n\t"
        "j [blink]\n\t"
    );
}
#else
uint32_t opencfw_em9305_init_transition_event_30e988(uint32_t id)
{
    /* Host fixture observes only the six native initialized event bytes. */
    _Alignas(4) uint8_t event[8];
    *(uint32_t *)(void *)event=0x001f0000u;
    *(uint16_t *)(void *)(event+4u)=(uint16_t)id;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
#endif
