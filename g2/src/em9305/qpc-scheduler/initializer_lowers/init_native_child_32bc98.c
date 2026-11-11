#include <stdint.h>

/* Native 0x32bc98..0x32bdfc: handle a received periodic-advertising
 * response PDU (LLID 5, opcode 0x22) while the auxiliary hook (0x802954)
 * is armed. The payload is copied and checked, then offered to 30301c as
 * the request {16 payload bytes, LLID, 3, header} with the context's +76
 * and the link's +2700. If accepted and the link expects it (+2720), the
 * link records the advertiser address (+1021), its options (+2791), the
 * peer address from the PDU (resolved through 303cc0 for a resolvable
 * private address when bit 1 of +57 is set, else cleared at
 * 0x805be4/0x805be8) at +1015, the encoded header (+1011/+2788, opcode at
 * +2790) and the response timing (+2252..+2260). Returns 1 on success. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_init_transition_packet_check_32e278(uintptr_t packet);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request, uintptr_t context,
                                            uint32_t flags, uintptr_t link);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);
extern uint32_t opencfw_em9305_radio_peer_set_303cc0(uint32_t type, uint32_t low, uint32_t high,
                                                     uintptr_t address);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy, uint32_t coded, uint32_t length);

struct opencfw_em9305_request_32bc98 {
    uint32_t words[4];
    uint8_t llid;
    uint8_t kind;
    uint16_t header;
};

uint32_t opencfw_em9305_child_32bc98(uintptr_t owner, uintptr_t pdu)
{
    struct opencfw_em9305_request_32bc98 request;
    uint32_t payload[4];
    uint32_t peer[2];
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uint32_t used=opencfw_em9305_child_32db0c(0x8019fcu,pdu);
    (void)opencfw_em9305_init_transition_packet_copy_32dd54((uintptr_t)payload,pdu+used);
    if(*(volatile uint8_t *)(uintptr_t)0x801a00u!=0x22u)return 0u;
    if(*(volatile uint8_t *)(uintptr_t)0x8019fcu!=5u)return 0u;
    if(*(volatile uint32_t *)(uintptr_t)0x802954u==0u)return 0u;
    if(opencfw_em9305_init_transition_packet_check_32e278((uintptr_t)payload)==0u)return 0u;
    uintptr_t context=*(volatile uint32_t *)(owner+44u);
    request.words[3]=((volatile uint32_t *)payload)[3];
    request.words[2]=((volatile uint32_t *)payload)[2];
    request.llid=*(volatile uint8_t *)(uintptr_t)0x8019fcu;
    request.header=*(volatile uint16_t *)(uintptr_t)0x8019feu;
    request.kind=3u;
    request.words[1]=((volatile uint32_t *)payload)[1];
    request.words[0]=((volatile uint32_t *)payload)[0];
    uintptr_t target=link+2700u;
    if(opencfw_em9305_child_30301c((uintptr_t)&request,context+76u,0u,target)==0u)return 0u;
    if(*(volatile uint8_t *)(link+2720u)==0u)return 0u;
    (void)opencfw_em9305_radio_address_write_3045e8(link+1021u,*(volatile uint32_t *)target,
                                                     *(volatile uint32_t *)(target+4u));
    uint32_t opcode=*(volatile uint8_t *)(uintptr_t)0x8019ffu;
    *(volatile uint8_t *)(link+2791u)=*(volatile uint8_t *)(link+2718u);
    uint64_t address=opencfw_em9305_controller_pack_address(pdu+8u);
    uint32_t low=(uint32_t)address,high=(uint32_t)(address>>32);
    volatile uint32_t *resolved=(volatile uint32_t *)(uintptr_t)0x805be4u;
    peer[1]=high;
    peer[0]=low;
    if((*(volatile uint8_t *)(link+57u)&2u)==0u){
        resolved[1]=0u;
        resolved[0]=0u;
    }else if((high&0xc000u)==0x4000u){
        resolved[1]=high;
        resolved[0]=low;
        (void)opencfw_em9305_radio_peer_set_303cc0(*(volatile uint8_t *)(link+2719u),
            *(volatile uint32_t *)(link+2708u),*(volatile uint32_t *)(link+2712u),(uintptr_t)peer);
        high=((volatile uint32_t *)peer)[1];
        low=((volatile uint32_t *)peer)[0];
    }
    (void)opencfw_em9305_radio_address_write_3045e8(link+1015u,low,high);
    *(volatile uint8_t *)(link+2790u)=(uint8_t)opcode;
    (void)opencfw_em9305_radio_encode_3239d4(link+1011u,link+2788u);
    uint32_t coded=*(volatile uint8_t *)(link+2693u);
    *(volatile uint16_t *)(link+2260u)=257u;
    uint32_t phy=*(volatile uint8_t *)(link+2529u);
    uint32_t anchor=*(volatile uint32_t *)(link+2696u);
    *(volatile uint8_t *)(link+2252u)=1u;
    *(volatile uint32_t *)(link+2256u)=
        opencfw_em9305_radio_duration_piece_312b88(phy,coded,0x24u)+anchor;
    return 1u;
}
