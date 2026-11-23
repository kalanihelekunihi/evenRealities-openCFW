#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32c884..0x32c904. Stock MPYWHL: low word of a 32 x 16 product,
 * the 16-bit operand sign-extended. */
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_pal_current_time(void);
static uint32_t multiply_whl(uint32_t factor,uint32_t value)
{
    return (uint32_t)factor*(uint32_t)(int32_t)(int16_t)value;
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
    uint8_t direction=em9305_ram_8027e0.u8_80281c;
    if (direction>=2u)
        return opencfw_em9305_phy_reject_32698c(context,30u,1u);
    uint8_t lower=em9305_ram_8027e0.u8_80281d;
    if (lower<5u)
        return opencfw_em9305_phy_reject_32698c(context,30u,1u);
    uint8_t upper=em9305_ram_8027e0.u8_80281e;
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
