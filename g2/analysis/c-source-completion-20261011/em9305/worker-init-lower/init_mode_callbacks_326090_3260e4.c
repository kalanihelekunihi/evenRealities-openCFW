#include <stdint.h>

/* Complete native callback envelopes 0x326090..0x326106. The 0x318920
 * packet-value child is a genuine source obligation until independently
 * attributed; it is never replaced with a constant. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_value_318920(uintptr_t);
uint32_t opencfw_em9305_mode_callback_326090(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint8_t mode=*(volatile uint8_t *)(context+744u);
    if (mode==0u||mode==1u) {
        int32_t current=(int8_t)*(volatile uint8_t *)(context+746u);
        int32_t limit=(int8_t)*(volatile uint8_t *)(uintptr_t)0x805aa8u;
        if ((mode==0u&&current<limit)||(mode==1u&&limit<current))
            *(volatile uint8_t *)(context+746u)=(uint8_t)limit;
    }
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(2u);
    if (packet==0u) return 0u;
    *(volatile uint8_t *)packet=29u;
    uint32_t value=opencfw_em9305_mode_callback_value_318920(context);
    *(volatile uint8_t *)(packet+1u)=(uint8_t)value;
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
uint32_t opencfw_em9305_mode_callback_3260e4(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(2u);
    if (packet==0u) return 0u;
    *(volatile uint8_t *)packet=30u;
    uint32_t value=opencfw_em9305_mode_callback_value_318920(context);
    *(volatile uint8_t *)(packet+1u)=(uint8_t)value;
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
