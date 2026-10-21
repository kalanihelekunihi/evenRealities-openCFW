#include <stdint.h>

/* Native 0x32c884..0x32c904. MPYWHL is retained as named ARC ISA;
 * the test-only host model qualifies branch/read/store composition only. */
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_pal_current_time(void);
#ifndef __arc__
extern uint32_t opencfw_em9305_test_mpywhl(uint32_t,uint32_t);
#endif
static uint32_t multiply_whl(uint32_t factor,uint32_t value)
{
#ifdef __arc__
    uint32_t result;
    __asm__ volatile("mpywhl %0,%1,%2":"=r"(result):"r"(factor),"r"(value));
    return result;
#else
    return opencfw_em9305_test_mpywhl(factor,value);
#endif
}
uint32_t opencfw_em9305_mode_callback_32c884(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint8_t mode=*(volatile uint8_t *)(context+2u);
    if (mode!=1u) {
        uint32_t state=*(volatile uint32_t *)(context+636u);
        *(volatile uint32_t *)(context+640u)=0u;
        *(volatile uint32_t *)(context+636u)=state&~(1u<<8);
        return opencfw_em9305_receive_terminate_325c08(context,110u);
    }
    uint8_t direction=*(volatile uint8_t *)(uintptr_t)0x80281cu;
    if (direction>=2u)
        return opencfw_em9305_phy_reject_32698c(context,30u,1u);
    uint8_t lower=*(volatile uint8_t *)(uintptr_t)0x80281du;
    if (lower<5u)
        return opencfw_em9305_phy_reject_32698c(context,30u,1u);
    uint8_t upper=*(volatile uint8_t *)(uintptr_t)0x80281eu;
    if (upper>150u||upper<5u||lower>150u||upper<lower)
        return opencfw_em9305_phy_reject_32698c(context,30u,1u);
    uint32_t upper_ticks=multiply_whl(0x30d40u,upper);
    uint32_t lower_ticks=multiply_whl(0x30d40u,lower);
    *(volatile uint8_t *)(context+565u)=(uint8_t)(direction!=0u);
    *(volatile uint32_t *)(context+236u)=upper_ticks;
    *(volatile uint32_t *)(context+232u)=lower_ticks;
    if (direction!=0u)
        *(volatile uint32_t *)(context+240u)=opencfw_em9305_pal_current_time();
    uint32_t now=opencfw_em9305_pal_current_time();
    *(volatile uint32_t *)(context+228u)=now;
    return now;
}
