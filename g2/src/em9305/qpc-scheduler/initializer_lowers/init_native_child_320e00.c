#include <stdint.h>

/* Native 0x320e00..0x320f2e: handle a received periodic-sync PDU for the
 * owner's link (+36) and context (+44). LLID 9 goes to the registered
 * hook (0x80516c), LLID 7 is parsed as an extended header (into link
 * +152, flags local) and needs SyncInfo. The SyncInfo (32db74, from the
 * pointer at link+184) is accepted unless its PHY is unsupported (1M
 * needs bit 8, 2M bit 11 of 0x805a94); then the LLID is latched at
 * link+240, owner+12 cleared, the packet duration computed (312b88) and
 * the receive armed (31c7c4) at the context anchor (+160); a link that
 * became scheduled (+241) signals the auxiliary hook. */
extern uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out, uintptr_t flags_out, uintptr_t in);
extern uint32_t opencfw_em9305_child_32db74(uintptr_t out, uintptr_t sync_info);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy, uint32_t coded, uint32_t length);
extern uint32_t opencfw_em9305_child_31c7c4(uintptr_t record, uintptr_t parameters, uint32_t start);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);

static uint32_t opencfw_em9305_sync_phy_ok_320e00(uint32_t phy)
{
    uint32_t features=*(volatile uint32_t *)(uintptr_t)0x805a94u;
    if(phy==1u)return (features&0x100u)!=0u;
    if(phy==2u)return (features&0x800u)!=0u;
    return 1u;
}

void opencfw_em9305_child_320e00(uintptr_t owner, uintptr_t pdu)
{
    uint8_t header[8] __attribute__((aligned(4)));
    uint8_t sync[8] __attribute__((aligned(4)));
    uint8_t flags;
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uintptr_t context=*(volatile uint32_t *)(owner+44u);
    (void)opencfw_em9305_dispatch_child_32db0c((uintptr_t)header,pdu);
    uint32_t llid=*(volatile uint8_t *)&header[0];
    if(llid==9u){
        uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x80516cu;
        uint32_t accepted=0u;
        if(hook!=0u)
            accepted=((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uintptr_t))hook)
                (owner,pdu,(uintptr_t)header,hook);
        (void)opencfw_em9305_child_32db74((uintptr_t)sync,*(volatile uint32_t *)(link+184u));
        if(hook==0u||accepted==0u)return;
    }else if(llid==7u){
        *(volatile uint8_t *)(link+154u)=0u;
        (void)opencfw_em9305_dispatch_child_32df24(link+152u,(uintptr_t)&flags,pdu+2u);
        if((*(volatile uint8_t *)&flags&0x10u)==0u)return;
        (void)opencfw_em9305_child_32db74((uintptr_t)sync,*(volatile uint32_t *)(link+184u));
    }else{
        return;
    }
    if(opencfw_em9305_sync_phy_ok_320e00(*(volatile uint8_t *)&sync[6])==0u)return;
    *(volatile uint32_t *)(owner+12u)=0u;
    *(volatile uint8_t *)(link+240u)=*(volatile uint8_t *)&header[0];
    (void)opencfw_em9305_radio_duration_piece_312b88(*(volatile uint8_t *)(context+13u),
        *(volatile uint8_t *)(context+153u),*(volatile uint8_t *)(context+185u)+2u);
    (void)opencfw_em9305_child_31c7c4(link,(uintptr_t)sync,*(volatile uint32_t *)(context+160u));
    if(*(volatile uint8_t *)(link+241u)!=0u)(void)opencfw_em9305_auxiliary_signal_304394();
}
