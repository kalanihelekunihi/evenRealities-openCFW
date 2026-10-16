#include <stdint.h>

/* Native 0x32ce84..0x32cf4e. BC aliases unsigned LO on this ARC target:
 * global+6 below 328 returns before global+2 is read; global+2 below 328
 * also returns. BRNE.D at 0x32cf00 stores the fourth min on both paths. */
extern uint32_t opencfw_em9305_phy_length_notify_32317c(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_mode_callback_32ce84(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint32_t remote_four=*(volatile uint16_t *)(uintptr_t)0x802820u;
    if (remote_four<27u) return (uint32_t)context;
    uint32_t remote_zero=*(volatile uint16_t *)(uintptr_t)0x80281cu;
    if (remote_zero<27u) return (uint32_t)context;
    uint32_t remote_six=*(volatile uint16_t *)(uintptr_t)0x802822u;
    if (remote_six<328u) return remote_six;
    uint32_t remote_two=*(volatile uint16_t *)(uintptr_t)0x80281eu;
    if (remote_two<328u) return remote_six;

    uint8_t enabled=*(volatile uint8_t *)(context+534u);
    uint32_t local_zero=*(volatile uint16_t *)(context+568u);
    uint32_t local_four=*(volatile uint16_t *)(context+572u);
    if (enabled==0u) {
        if (local_zero>0x848u) local_zero=0x848u;
        if (local_four>0x848u) local_four=0x848u;
    } else {
        uint8_t flags=*(volatile uint8_t *)(context+545u);
        if ((flags&8u)==0u) {
            if (local_zero>0x848u) local_zero=0x848u;
            if (local_four>0x848u) local_four=0x848u;
        }
    }
    uint32_t local_two=*(volatile uint16_t *)(context+570u);
    uint32_t local_six=*(volatile uint16_t *)(context+566u);
    uint8_t mode_upper=*(volatile uint8_t *)(context+77u);
    uint32_t old_four=*(volatile uint16_t *)(context+580u);
    uint32_t old_two=*(volatile uint16_t *)(context+578u);
    uint32_t old_zero=*(volatile uint16_t *)(context+576u);
    uint32_t old_six=*(volatile uint16_t *)(context+574u);
    uint32_t new_four=(local_four<remote_two)?local_four:remote_two;
    uint32_t new_zero=(local_zero<remote_six)?local_zero:remote_six;
    uint32_t new_two=(local_two<remote_zero)?local_two:remote_zero;
    uint32_t new_six=(local_six<remote_four)?local_six:remote_four;
    *(volatile uint16_t *)(context+580u)=(uint16_t)new_four;
    *(volatile uint16_t *)(context+576u)=(uint16_t)new_zero;
    *(volatile uint16_t *)(context+578u)=(uint16_t)new_two;
    *(volatile uint16_t *)(context+574u)=(uint16_t)new_six;
    if (mode_upper==3u) {
        if (new_zero<0xa90u) new_zero=0xa90u;
        *(volatile uint16_t *)(context+576u)=(uint16_t)new_zero;
    }
    uint8_t mode_lower=*(volatile uint8_t *)(context+76u);
    if (mode_lower==3u) {
        if (new_four<0xa90u) new_four=0xa90u;
        *(volatile uint16_t *)(context+580u)=(uint16_t)new_four;
    }
    if (old_zero!=new_zero||old_four!=new_four||old_two!=new_two||old_six!=new_six)
        (void)opencfw_em9305_phy_length_notify_32317c(context,0u);
    uint32_t result=opencfw_em9305_radio_limit_317b10(context,context+574u);
    *(volatile uint16_t *)(context+592u)=(uint16_t)result;
    return result;
}
