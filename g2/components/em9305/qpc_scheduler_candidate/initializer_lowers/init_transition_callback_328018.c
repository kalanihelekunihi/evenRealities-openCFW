#include <stdint.h>

extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);

/* Native 0x318b38..0x318b74. Incoming R1 is a selector, R2 is a
 * source byte pointer. The first branch retains incoming R0. */
uintptr_t opencfw_em9305_init_transition_flag_318b38(
    uintptr_t incoming,uint32_t selector,uintptr_t source)
{
    if(selector!=0x22u)return incoming;
    uint32_t ready=*(volatile uint32_t *)(uintptr_t)0x802954u;
    if(ready==0u)return ready;
    uintptr_t root=0x8052d4u;
    *(volatile uint8_t *)(root+40u)=1u; /* BL delay slot. */
    (void)opencfw_em9305_auxiliary_signal_304394();
    uint8_t flags=*(volatile uint8_t *)root;
    uintptr_t target=0x8052feu;
    if((flags&(1u<<5u))!=0u) {
        uint8_t source_flags=*(volatile uint8_t *)source;
        if((source_flags&(1u<<5u))!=0u) {
            *(volatile uint8_t *)target=1u;
            return target;
        }
    }
    *(volatile uint8_t *)target=0u;
    return target;
}

/* Native 0x328018..0x32805a. The branch delay slot captures byte149
 * even when byte148 selects the flag child. ADD3 0x2c scales by eight. */
uint32_t opencfw_em9305_init_transition_callback_328018(
    uintptr_t owner,uintptr_t source)
{
    uintptr_t record=*(volatile uint32_t *)(owner+44u);
    uint8_t kind=*(volatile uint8_t *)(record+148u);
    uint8_t selector=*(volatile uint8_t *)(record+149u);
    if(kind==5u) {
        (void)opencfw_em9305_init_transition_flag_318b38(
            kind,selector,source);
        uintptr_t row=*(volatile uint32_t *)(record+128u);
        *(volatile uint32_t *)(uintptr_t)0x8053ccu=(uint32_t)(row+352u);
        return 0u;
    }
    if(kind==3u) {
        uint8_t active=*(volatile uint8_t *)(record+152u);
        if(active!=0u) {
            uint32_t linked=*(volatile uint32_t *)(record+108u);
            return (linked!=0u && selector==12u)?1u:0u;
        }
    }
    return 0u;
}
