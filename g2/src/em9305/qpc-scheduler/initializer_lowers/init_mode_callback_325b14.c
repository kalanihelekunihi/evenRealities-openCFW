#include <stdint.h>

/* Full native 0x325b14..0x325b96. The DSP MPYWHL is retained as a named
 * ARC ISA operation because host integer multiplication does not state its
 * halfword/sign contract. Host fixture supplies only a test-only model. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_pal_current_time(void);
#ifndef __arc__
extern uint32_t opencfw_em9305_test_mpywhl(uint32_t,uint32_t);
#endif
uint32_t opencfw_em9305_mode_callback_325b14(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint8_t mode=*(volatile uint8_t *)(context+2u);
    if (mode!=0u) {
        uint32_t state=*(volatile uint32_t *)(context+636u);
        *(volatile uint32_t *)(context+640u)=0u;
        *(volatile uint32_t *)(context+636u)=state&~(1u<<8);
        return opencfw_em9305_receive_terminate_325c08(context,110u);
    }
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(4u);
    if (packet!=0u) {
        *(volatile uint8_t *)packet=0x28u;
        uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
        *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(root+4u);
        root=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
        *(volatile uint8_t *)(packet+2u)=*(volatile uint8_t *)(root+5u);
        root=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
        *(volatile uint8_t *)(packet+3u)=*(volatile uint8_t *)(root+6u);
        (void)opencfw_em9305_phy_packet_send_32d32c(context,packet);
    }
    uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
    uint8_t enabled=*(volatile uint8_t *)(root+4u);
    *(volatile uint8_t *)(context+565u)=(uint8_t)(enabled!=0u);
    uint32_t period=*(volatile uint8_t *)(root+5u);
    uint32_t product;
#ifdef __arc__
    __asm__ volatile("mpywhl %0,%1,%2":"=r"(product):"r"(0x30d40u),"r"(period));
#else
    product=opencfw_em9305_test_mpywhl(0x30d40u,period);
#endif
    *(volatile uint32_t *)(context+236u)=product;
    uint32_t now=opencfw_em9305_pal_current_time();
    uint32_t state=*(volatile uint32_t *)(context+636u);
    uint32_t saved_product=*(volatile uint32_t *)(context+236u);
    *(volatile uint32_t *)(context+636u)=state&~(1u<<8);
    *(volatile uint32_t *)(context+232u)=now-saved_product;
    return opencfw_em9305_receive_terminate_325c08(context,110u);
}
