#include <stdint.h>

/* Full native 0x325b98..0x325c04: 9 packed four-field bytes plus the
 * tenth terminal byte, optional packet send, then clear receive bit9 and
 * terminate even when allocation fails. Native reloads the live 805c6c
 * source pointer for each record. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
uint32_t opencfw_em9305_mode_callback_325b98(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(11u);
    if (packet!=0u) {
        *(volatile uint8_t *)packet=0x29u;
        for (uint32_t index=0;index<9u;++index) {
            uintptr_t source=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
            source+=index*4u;
            uint32_t field0=*(volatile uint8_t *)(source+4u);
            uint32_t field1=*(volatile uint8_t *)(source+5u);
            uint32_t field2=*(volatile uint8_t *)(source+6u);
            uint32_t field3=*(volatile uint8_t *)(source+7u);
            *(volatile uint8_t *)(packet+index+1u)=
                (uint8_t)(field0|(field1<<2)|(field2<<4)|(field3<<6));
        }
        uintptr_t source=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
        *(volatile uint8_t *)(packet+10u)=*(volatile uint8_t *)(source+40u);
        (void)opencfw_em9305_phy_packet_send_32d32c(context,packet);
    }
    uint32_t state=*(volatile uint32_t *)(context+636u);
    *(volatile uint32_t *)(context+640u)=0u;
    *(volatile uint32_t *)(context+636u)=state&~(1u<<9);
    return opencfw_em9305_receive_terminate_325c08(context,110u);
}
