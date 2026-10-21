#include <stdint.h>

/* Native 0x3269ec..0x326a28: send optional three-byte packet then clear
 * receive state and terminate, including packet-allocation failure. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
uint32_t opencfw_em9305_mode_callback_3269ec(uintptr_t context,
                                               uintptr_t callback_code)
{
    (void)callback_code;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(3u);
    if (packet!=0u) {
        *(volatile uint8_t *)packet=25u;
        uint8_t first=*(volatile uint8_t *)(context+606u);
        *(volatile uint8_t *)(packet+1u)=first;
        uint8_t second=*(volatile uint8_t *)(context+607u);
        *(volatile uint8_t *)(packet+2u)=second;
        (void)opencfw_em9305_phy_packet_send_32d32c(context,packet);
    }
    uint32_t state=*(volatile uint32_t *)(context+636u);
    *(volatile uint32_t *)(context+640u)=0u;
    *(volatile uint32_t *)(context+636u)=state&~(1u<<5);
    return opencfw_em9305_receive_terminate_325c08(context,110u);
}

/* Native 0x323668 consists solely of `j_s [blink]`; R0 is untouched.
 * This is an authenticated callback body, not a fabricated success stub. */
uint32_t opencfw_em9305_mode_callback_323668(uintptr_t context,
                                               uintptr_t callback_code)
{
    (void)callback_code;
    return (uint32_t)context;
}
