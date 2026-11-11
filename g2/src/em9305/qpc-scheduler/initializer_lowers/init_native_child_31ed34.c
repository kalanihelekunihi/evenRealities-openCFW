#include <stdint.h>

/* Native 0x31ed34..0x31ef5c: handle a received AUX_SYNC_IND-style PDU
 * (LLID 7) for the owner's periodic-sync link (+36) and context (+44).
 * The header goes to 0x803b74 and the extended header to link+152 with
 * its flags at 0x803b72 (state block G = 0x803b68, H = 0x803b8c). With an
 * established sync (+153) the cached addresses (+156..+168) are used
 * unless the stored flags lack bit 0; otherwise AdvA/TargetA are cached
 * in G (+20..+39) under the H filters and the flags/addresses refreshed.
 * The resulting request {AdvA, TargetA, 7, flags, types} goes to 30301c.
 * When it is accepted and reporting is enabled (+153 bit 1, context
 * +100/+164, link bit 0, 325660) the link's addresses and identity
 * (+104/+108, +120, +194/+195, peer +114 via 303a40/303cc0) and header
 * (+112/+192) are set and 1 is returned; every non-error path refreshes
 * H[4]/H[6] and link +64/+77. G[1] is set when the PDU is rejected. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out, uintptr_t flags_out, uintptr_t in);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request, uintptr_t context,
                                            uint32_t flags, uintptr_t target);
extern uint32_t opencfw_em9305_child_325660(uintptr_t link);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t type, uint32_t low, uint32_t high,
                                                      uintptr_t address);
extern uint32_t opencfw_em9305_radio_peer_set_303cc0(uint32_t type, uint32_t low, uint32_t high,
                                                     uintptr_t address);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t,uintptr_t);

struct opencfw_em9305_request_31ed34 {
    uint32_t adv_low, adv_high, target_low, target_high;
    uint8_t kind, flags, adv_type, target_type;
};

uint32_t opencfw_em9305_child_31ed34(uintptr_t owner, uintptr_t pdu)
{
    struct opencfw_em9305_request_31ed34 request;
    uint32_t peer[2];
    const uintptr_t g=0x803b68u,h=0x803b8cu;
    volatile uint8_t *g8=(volatile uint8_t *)g;
    volatile uint8_t *h8=(volatile uint8_t *)h;
    uintptr_t context=*(volatile uint32_t *)(owner+44u);
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    volatile uint8_t *l8=(volatile uint8_t *)link;
    volatile uint32_t *cache=(volatile uint32_t *)(link+156u);
    uint32_t used=opencfw_em9305_child_32db0c(g+12u,pdu);
    g8[11]=(uint8_t)opencfw_em9305_dispatch_child_32df24(link+152u,g+10u,pdu+used);
    uint32_t llid=g8[12];
    g8[9]=1u;
    if(llid!=7u){
        g8[1]=1u;
        return 0u;
    }
    uint32_t adv_low,adv_high,target_low,target_high,adv_type,target_type,flags;
    if(l8[153]!=0u){
        uint32_t stored=l8[154];
        g8[10]=(uint8_t)(g8[10]&~0x34u);
        flags=stored&~0x34u;
        l8[154]=(uint8_t)flags;
        if((stored&1u)==0u){
            g8[1]=1u;
            return 0u;
        }
        target_high=cache[3];
        target_low=cache[2];
        adv_high=cache[1];
        adv_low=cache[0];
        target_type=g8[15];
        adv_type=g8[14];
    }else{
        uint32_t missing_adv=0u,missing_target=0u;
        if(h8[0]==0u){
            if((g8[10]&1u)==0u){
                missing_adv=1u;
            }else{
                uint32_t high=cache[1],low=cache[0];
                uint32_t type=g8[14];
                g8[36]=1u;
                *(volatile uint32_t *)(g+24u)=high;
                *(volatile uint32_t *)(g+20u)=low;
                g8[37]=(uint8_t)type;
            }
        }
        if(h8[2]==0u){
            if((g8[10]&2u)==0u){
                missing_target=1u;
            }else{
                uint32_t high=cache[3],low=cache[2];
                uint32_t type=g8[15];
                g8[38]=1u;
                *(volatile uint32_t *)(g+32u)=high;
                *(volatile uint32_t *)(g+28u)=low;
                g8[39]=(uint8_t)type;
            }
        }
        flags=l8[154];
        if(missing_adv==0u){
            flags|=1u;
            l8[154]=(uint8_t)flags;
        }
        adv_high=*(volatile uint32_t *)(g+24u);
        adv_low=*(volatile uint32_t *)(g+20u);
        adv_type=g8[37];
        cache[1]=adv_high;
        cache[0]=adv_low;
        g8[14]=(uint8_t)adv_type;
        if(missing_target==0u){
            flags|=2u;
            l8[154]=(uint8_t)flags;
        }
        target_high=*(volatile uint32_t *)(g+32u);
        target_low=*(volatile uint32_t *)(g+28u);
        target_type=g8[39];
        cache[3]=target_high;
        cache[2]=target_low;
        g8[15]=(uint8_t)target_type;
    }
    uintptr_t context_now=*(volatile uint32_t *)(owner+44u);
    uintptr_t target=context+144u;
    request.target_low=target_low;
    request.flags=(uint8_t)flags;
    request.adv_high=adv_high;
    request.target_high=target_high;
    request.adv_low=adv_low;
    request.kind=7u;
    request.adv_type=(uint8_t)adv_type;
    request.target_type=(uint8_t)target_type;
    if(opencfw_em9305_child_30301c((uintptr_t)&request,context_now+76u,0u,target)==0u){
        g8[1]=1u;
        return 0u;
    }
    if(g8[1]!=0u)return 0u;
    uint32_t result=0u;
    if((l8[153]&2u)!=0u&&*(volatile uint32_t *)(context+100u)!=0u){
        if(*(volatile uint8_t *)(target+20u)==0u||(l8[154]&1u)==0u){
            g8[1]=1u;
            return 0u;
        }
        if(opencfw_em9305_child_325660(link)!=0u){
            (void)opencfw_em9305_radio_address_write_3045e8(link+120u,
                *(volatile uint32_t *)target,*(volatile uint32_t *)(target+4u));
            uint32_t options=l8[13];
            uint32_t identity_type=*(volatile uint8_t *)(target+18u);
            uint32_t low=*(volatile uint32_t *)target;
            uint32_t high=*(volatile uint32_t *)(target+4u);
            *(volatile uint32_t *)(link+108u)=high;
            *(volatile uint32_t *)(link+104u)=low;
            l8[195]=(uint8_t)identity_type;
            if((options&2u)!=0u){
                uint32_t resolved;
                if((l8[154]&2u)==0u){
                    uint32_t key_high=*(volatile uint32_t *)(context+88u);
                    uint32_t peer_high=*(volatile uint32_t *)(context+156u);
                    uint32_t peer_low=*(volatile uint32_t *)(context+152u);
                    uint32_t peer_type=*(volatile uint8_t *)(context+163u);
                    uint32_t privacy=*(volatile uint8_t *)(context+80u);
                    peer[0]=*(volatile uint32_t *)(context+84u);
                    peer[1]=key_high;
                    if(opencfw_em9305_radio_peer_pair_303a40(peer_type,peer_low,peer_high,
                                                             (uintptr_t)peer)!=0u)resolved=1u;
                    else resolved=(privacy>>1)&1u;
                }else{
                    uint32_t high_word=cache[3];
                    uint32_t low_word=cache[2];
                    resolved=g8[15];
                    peer[1]=high_word;
                    peer[0]=low_word;
                    if((high_word&0xc000u)==0x4000u)
                        (void)opencfw_em9305_radio_peer_set_303cc0(*(volatile uint8_t *)(target+19u),
                            *(volatile uint32_t *)(target+8u),*(volatile uint32_t *)(target+12u),
                            (uintptr_t)peer);
                }
                (void)opencfw_em9305_radio_address_write_3045e8(link+114u,
                    ((volatile uint32_t *)peer)[0],((volatile uint32_t *)peer)[1]);
                l8[194]=(uint8_t)resolved;
            }
            (void)opencfw_em9305_radio_encode_3239d4(link+112u,link+192u);
            result=1u;
        }
    }
    uint32_t stored=l8[154];
    uint32_t sync=l8[153];
    *(volatile uint16_t *)(h+6u)=0u;
    *(volatile uint16_t *)(link+64u)=(uint16_t)((stored<<1)&4u);
    uint32_t sca=*(volatile uint8_t *)(context+133u);
    h8[4]=(uint8_t)sync;
    l8[77]=(uint8_t)sca;
    return result;
}
