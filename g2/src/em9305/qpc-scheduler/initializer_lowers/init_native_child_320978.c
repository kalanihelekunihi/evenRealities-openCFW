#include <stdint.h>

/* Native 0x320978..0x320b08: complete a connection request sent by the
 * initiator (object +44) for the link (object +36). Requires an address
 * type (+188) and a request PDU buffer (+104). The peer address goes into
 * the PDU, the own address type into the link (+195); with address
 * resolution on the link (bit 1 of +99) the peer's resolvable address is
 * taken from the received PDU (registering a resolvable private address
 * through 303cc0) or resolved from the peer pair (303a40), and written to
 * the PDU with its type (+194); otherwise the resolved pair (+80/+84) is
 * cleared. The PDU is encoded with the channel-selection bit (bit 14 of
 * 0x805a94, +193), the first anchor is scheduled from the transmit window
 * (+90 * 1250 us after the request end) and stored in the PDU (window
 * offset bytes 22/23), the link (+76) and the connection (+24); the CSA
 * flag (+97), started flag (+96) and PHY (+100) are set. Returns 1 when
 * the connection was set up. */
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,
    uint32_t coded,uint32_t length);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,
    uint32_t low,uint32_t high);
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);
extern uint32_t opencfw_em9305_radio_peer_set_303cc0(uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t source);
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t output);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t output,
                                                   uintptr_t input);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t incoming,
    uint32_t index,uint32_t timestamp,uint32_t existing,uint32_t action);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_child_320978(uintptr_t object,uintptr_t pdu)
{
    uintptr_t initiator=r32(object+44u);
    uintptr_t link=r32(object+36u);
    uint32_t length=r8(initiator+185u);
    uint32_t coded=r8(initiator+153u);
    uint32_t phy=r8(initiator+13u);
    uintptr_t base=r32(0x805c70u);
    uint32_t end=r32(initiator+160u);
    uint32_t handle=r16(link+88u);
    uint32_t duration=opencfw_em9305_radio_duration_piece_312b88(phy,coded,length+2u);
    if(r8(initiator+188u)==0u)return 0u;
    uintptr_t request=r32(initiator+104u);
    if(request==0u)return 0u;
    uintptr_t connection=base+handle*912u;
    (void)opencfw_em9305_radio_address_write_3045e8(request+8u,r32(initiator+168u),
                                                   r32(initiator+172u));
    uint32_t options=r8(link+99u);
    w8(link+195u,r8(initiator+186u));
    if((options&2u)==0u){
        w32(link+84u,0u);
        w32(link+80u,0u);
    }else{
        uint32_t pair[2];
        uint32_t type;
        if(r8(initiator+184u)==1u){
            type=r8(pdu);
            uint64_t address=opencfw_em9305_controller_pack_address(pdu+8u);
            uint32_t low=(uint32_t)address,high=(uint32_t)(address>>32);
            w32(link+80u,low);
            pair[0]=low;
            type>>=7;
            w32(link+84u,high);
            pair[1]=high;
            if((high&0xc000u)==0x4000u)
                (void)opencfw_em9305_radio_peer_set_303cc0(r8(initiator+187u),
                    r32(initiator+176u),r32(initiator+180u),(uintptr_t)pair);
        }else{
            uint32_t own=r32(initiator+80u);
            pair[0]=r32(initiator+84u);
            pair[1]=r32(initiator+88u);
            if(opencfw_em9305_radio_peer_pair_303a40(r8(initiator+187u),
                   r32(initiator+176u),r32(initiator+180u),(uintptr_t)pair)!=0u){
                type=1u;
                w32(link+84u,pair[1]);
                w32(link+80u,pair[0]);
            }else{
                type=(own>>1)&1u;
                w32(link+84u,0u);
                w32(link+80u,0u);
            }
        }
        (void)opencfw_em9305_radio_address_write_3045e8(r32(initiator+104u)+2u,
                                                       pair[0],pair[1]);
        w8(link+194u,type);
    }
    uint32_t csa=(r32(0x805a94u)>>14)&1u;
    w8(link+193u,csa);
    (void)opencfw_em9305_radio_encode_3239d4(r32(initiator+104u),link+192u);
    uintptr_t current=r32(0x805c70u);
    uint32_t window=r16(link+90u);
    uint32_t start=end+duration;
    int32_t index=(int32_t)(connection-current)/912;
    uint32_t offset=opencfw_em9305_radio_schedule_313424(window*1250u,(uint8_t)index,
                                                         start+1752u,0u,0u);
    uint64_t scaled=(uint64_t)offset*0x1a36e3u;
    uint32_t units=(uint32_t)(scaled>>31);
    w8(r32(initiator+104u)+22u,units);
    w8(r32(initiator+104u)+23u,(uint32_t)(scaled>>32)>>7);
    uint32_t enabled=r8(link+193u);
    *(volatile uint16_t *)(link+76u)=(uint16_t)units;
    w32(base+handle*912u+24u,offset+start+1752u);
    if(enabled==1u&&(r8(pdu)&0x20u)!=0u)w8(link+97u,1u);
    else w8(link+97u,0u);
    uint32_t mode=r8(initiator+12u);
    w8(link+96u,1u);
    w8(link+100u,mode);
    return 1u;
}
