#include <stdint.h>

/* Native callback bodies 0x326a64..0x326a82 and 0x326aa8..0x326afe.
 * 0x326aa8 stores ctx+525 in the packet-alloc BL.D delay slot, including
 * the allocation failure route. Each root pointer load is separately
 * volatile, as in the native byte-copy sequence. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_mode_callback_326a64(uintptr_t context,
                                               uintptr_t callback_code)
{
    (void)callback_code;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(2u);
    if (packet==0u) return 0u;
    *(volatile uint8_t *)packet=2u;
    uint8_t value=*(volatile uint8_t *)(context+12u);
    *(volatile uint8_t *)(packet+1u)=value;
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
uint32_t opencfw_em9305_mode_callback_326aa8(uintptr_t context,
                                               uintptr_t callback_code)
{
    (void)callback_code;
    if (*(volatile uint8_t *)(context+525u)!=0u)
        return opencfw_em9305_phy_reject_32698c(context,0x24u,0u);
    *(volatile uint8_t *)(context+525u)=1u;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(6u);
    if (packet==0u) return 0u;
    *(volatile uint8_t *)packet=12u;
    uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint8_t value=*(volatile uint8_t *)(root+4u);
    *(volatile uint8_t *)(packet+1u)=value;
    root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    value=*(volatile uint8_t *)root;
    *(volatile uint8_t *)(packet+2u)=value;
    root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    value=*(volatile uint8_t *)(root+1u);
    *(volatile uint8_t *)(packet+3u)=value;
    root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    value=*(volatile uint8_t *)(root+2u);
    *(volatile uint8_t *)(packet+4u)=value;
    value=*(volatile uint8_t *)(root+3u);
    *(volatile uint8_t *)(packet+5u)=value;
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
