#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x320b3c..0x320d68: complete an AUX_CONNECT_RSP-style reply on
 * the initiator's periodic link. The PDU header and extended header go to
 * a local record and link+152 (flags in a local byte). With the link's
 * sync established and its stored flags bit 0 set (+153/+154), the request
 * {cached AdvA/TargetA (+156..+168), LLID, flags, TxAdd, RxAdd} goes to
 * 30301c; it must be accepted (or the link PHY +98 be 4 with an AUX
 * channel +240 of 9), the target filter (initiator +164) must allow it and
 * a reply PDU (+100) must exist. The reply gets the initiator address
 * (+144/+148) and own address type (+162 -> link +195). With address
 * resolution (link +99 bit 1) the peer address comes from the received
 * TargetA (registering a resolvable private one through 303cc0) or the
 * peer pair (303a40) and is written to the reply with its type (+194);
 * otherwise the pair (+80/+84) is cleared. The header is encoded (+112,
 * +192), the first anchor is scheduled from the transmit window (+266 of
 * the connection * 1250 us after the request end plus the two packet
 * durations and the 2500/3750 us offset), the window offset goes to link
 * +134/+135 and the anchor to the connection (+24); CSA (+97), started
 * (+96) and PHY (+100) are set. Returns 1 when the connection was set up. */
extern uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t out,uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out,
    uintptr_t flags_out,uintptr_t in);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request,uintptr_t context,
                                            uint32_t flags,uintptr_t target);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,
    uint32_t coded,uint32_t length);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,
    uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t output);
extern uint32_t opencfw_em9305_radio_peer_set_303cc0(uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t source);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t output,
                                                   uintptr_t input);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t incoming,
    uint32_t index,uint32_t timestamp,uint32_t existing,uint32_t action);

struct opencfw_em9305_request_320b3c {
    uint32_t adv_low,adv_high,target_low,target_high;
    uint8_t kind,flags,adv_type,target_type;
};

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_child_320b3c(uintptr_t object,uintptr_t pdu)
{
    struct opencfw_em9305_request_320b3c request;
    volatile uint8_t header[5];
    volatile uint8_t ext_flags;
    uint32_t pair[2];
    uintptr_t initiator=r32(object+44u);
    uintptr_t link=r32(object+36u);
    uint32_t used=opencfw_em9305_dispatch_child_32db0c((uintptr_t)header,pdu);
    (void)opencfw_em9305_dispatch_child_32df24(link+152u,(uintptr_t)&ext_flags,
                                               pdu+used);
    if((r8(link+153u)&1u)==0u)return 0u;
    uint32_t stored=r8(link+154u);
    if((stored&1u)==0u)return 0u;
    uintptr_t cache=link+156u;
    uint32_t aux=0u;
    request.kind=header[0];
    request.adv_type=header[2];
    request.target_type=header[3];
    request.flags=(uint8_t)stored;
    request.adv_high=r32(cache+4u);
    uint32_t phy=r8(link+98u);
    request.adv_low=r32(cache);
    request.target_high=r32(cache+12u);
    request.target_low=r32(cache+8u);
    if(phy==4u)aux=r8(cache+84u)==9u;
    uintptr_t filter=initiator+144u;
    uint32_t accepted=opencfw_em9305_child_30301c((uintptr_t)&request,
        r32(object+44u)+76u,0u,filter);
    if(accepted==0u&&aux==0u)return 0u;
    if(aux==0u&&r8(filter+20u)==0u)return 0u;
    if(r32(initiator+100u)==0u)return 0u;
    uint32_t length=header[4];
    uint32_t coded=r8(initiator+134u);
    uint32_t start_phy=r8(initiator+13u);
    uintptr_t anchor=initiator+140u;
    uint32_t handle=r16(link+88u);
    uint32_t end=r32(anchor);
    uintptr_t base=r32(((uintptr_t)&em9305_ram_805c5c + 0x14u));
    uint32_t request_time=opencfw_em9305_radio_duration_piece_312b88(start_phy,
        coded,length+2u);
    uint32_t reply_coded=r8(initiator+15u);
    uint32_t reply_phy=r8(initiator+12u);
    if(reply_coded==0u)reply_coded=r8(initiator+134u);
    uintptr_t connection=base+handle*912u;
    uint32_t reply_time=opencfw_em9305_radio_duration_piece_312b88(reply_phy,
        reply_coded,36u);
    (void)opencfw_em9305_radio_address_write_3045e8(r32(initiator+100u)+8u,
        r32(anchor+4u),r32(anchor+8u));
    uint32_t options=r8(link+99u);
    w8(link+195u,r8(initiator+162u));
    if((options&2u)==0u){
        w32(link+84u,0u);
        w32(link+80u,0u);
    }else{
        uint32_t type;
        if((ext_flags&2u)==0u){
            uint32_t own=r32(initiator+80u);
            pair[0]=r32(initiator+84u);
            pair[1]=r32(initiator+88u);
            if(opencfw_em9305_radio_peer_pair_303a40(r8(initiator+163u),
                   r32(anchor+12u),r32(anchor+16u),(uintptr_t)pair)!=0u){
                type=1u;
                w32(link+84u,pair[1]);
                w32(link+80u,pair[0]);
            }else{
                type=(own>>1)&1u;
                w32(link+84u,0u);
                w32(link+80u,0u);
            }
        }else{
            uint32_t high=r32(link+168u);
            uint32_t low=r32(link+164u);
            type=header[3];
            pair[1]=high;
            pair[0]=low;
            if((high&0xc000u)==0x4000u){
                w32(link+80u,low);
                w32(link+84u,high);
                (void)opencfw_em9305_radio_peer_set_303cc0(r8(filter+19u),
                    r32(filter+8u),r32(filter+12u),(uintptr_t)pair);
            }
        }
        (void)opencfw_em9305_radio_address_write_3045e8(r32(initiator+100u)+2u,
                                                       pair[0],pair[1]);
        w8(link+194u,type);
    }
    (void)opencfw_em9305_radio_encode_3239d4(link+112u,link+192u);
    uint32_t spacing=r8(initiator+13u)==3u?3750u:2500u;
    uintptr_t current=r32(((uintptr_t)&em9305_ram_805c5c + 0x14u));
    int32_t index=(int32_t)(connection-current)/912;
    uint32_t window=r16(connection+266u);
    uint32_t start=end+request_time+reply_time+spacing;
    uint32_t offset=opencfw_em9305_radio_schedule_313424(window*1250u,
        (uint8_t)index,start+150u,0u,0u);
    uint64_t scaled=(uint64_t)offset*0x1a36e3u;
    uint32_t units=(uint16_t)(scaled>>31);
    uint32_t interval=r16(connection+266u);
    units%=interval;
    uint32_t phase=offset%(interval*1250u);
    w8(link+134u,units);
    w8(link+135u,units>>8);
    w32(connection+24u,start+phase+150u);
    w8(link+97u,1u);
    uint32_t mode=r8(initiator+12u);
    w8(link+96u,0u);
    w8(link+100u,mode);
    return 1u;
}
