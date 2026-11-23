#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31f538..0x31f868: periodic-sync receive handler for the
 * owner's link (+36) and context (+44); G = (uintptr_t)&em9305_ram_803b68 holds the last
 * advertiser/target addresses, K = ((uintptr_t)&em9305_ram_805194 + 0x10u) the sync-transfer filter.
 * LLID 9 PDUs go to the hook at ((uintptr_t)&em9305_ram_805160 + 0xcu) and, when accepted with a
 * SyncInfo (+154 bit 4), arm the next receive; LLID 7 PDUs are parsed
 * (32df24, flags local) and, for a new sync, cache AdvA/TargetA in G and
 * offer the request to 30301c. With an established filter (K[0] = 1 and
 * AdvA+ADI present) the advertiser is matched against K (3036b4 or the
 * stored address) and the transfer record at *(K+20) is filled. Then
 * either the SyncInfo arms the next receive (32db74/312b88/31c7c4,
 * signalling the auxiliary hook when scheduled) or the PDU is validated
 * and the session key steps run (319ee8/31a1b0/31a1fc). Other LLIDs clear
 * the extended header at +152 first. G[1] is set on rejection. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out, uintptr_t flags_out, uintptr_t in);
extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request, uintptr_t context,
                                            uint32_t flags, uintptr_t target);
extern uint32_t opencfw_em9305_address_contains_3036b4(uint32_t type, uint32_t low, uint32_t high);
extern uint32_t opencfw_em9305_child_319ee8(uintptr_t link, uint32_t mode, uintptr_t header,
                                            uint32_t id_low, uint32_t id_high,
                                            uint32_t flags, int32_t key_state,
                                            uintptr_t pdu, uintptr_t session);
extern uint32_t opencfw_em9305_child_31a1b0(uintptr_t link, uintptr_t session, uintptr_t key);
extern uint32_t opencfw_em9305_child_31a1fc(uintptr_t link, uintptr_t session, uintptr_t key);
extern uint32_t opencfw_em9305_child_32db74(uintptr_t out, uintptr_t sync_info);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy, uint32_t coded, uint32_t length);
extern uint32_t opencfw_em9305_child_31c7c4(uintptr_t record, uintptr_t parameters, uint32_t start);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);

struct opencfw_em9305_request_31f538 {
    uint32_t adv_low, adv_high, target_low, target_high;
    uint8_t llid, flags;
    uint16_t header;
};

static uint32_t opencfw_em9305_offer_31f538(uintptr_t owner, uintptr_t link, uintptr_t context,
                                            volatile const uint8_t *header, uint32_t flags)
{
    struct opencfw_em9305_request_31f538 request;
    volatile const uint32_t *cache=(volatile const uint32_t *)(link+156u);
    uint32_t adv_high=cache[1],adv_low=cache[0],target_high=cache[3],target_low=cache[2];
    uintptr_t context_now=*(volatile uint32_t *)(owner+44u);
    uint32_t llid=header[0];
    uint32_t header_word=*(volatile const uint16_t *)(header+2);
    uint32_t stored=*(volatile uint8_t *)(link+154u);
    request.adv_high=adv_high;
    request.adv_low=adv_low;
    request.target_high=target_high;
    request.target_low=target_low;
    request.llid=(uint8_t)llid;
    request.header=(uint16_t)header_word;
    request.flags=(uint8_t)stored;
    return opencfw_em9305_child_30301c((uintptr_t)&request,context_now+76u,flags,context+168u);
}

static void opencfw_em9305_arm_31f538(uintptr_t owner, uintptr_t link, uintptr_t context)
{
    *(volatile uint32_t *)(owner+12u)=0u;
    uintptr_t sync=link+198u;
    (void)opencfw_em9305_child_32db74(sync,*(volatile uint32_t *)(link+184u));
    (void)opencfw_em9305_radio_duration_piece_312b88(*(volatile uint8_t *)(context+13u),
        *(volatile uint8_t *)(context+153u),*(volatile uint8_t *)(context+185u)+2u);
    (void)opencfw_em9305_child_31c7c4(link,sync,*(volatile uint32_t *)(context+160u));
}

void opencfw_em9305_child_31f538(uintptr_t owner, uintptr_t pdu)
{
    uint8_t header[8] __attribute__((aligned(4)));
    uint8_t flags;
    const uintptr_t g=(uintptr_t)&em9305_ram_803b68,k=((uintptr_t)&em9305_ram_805194 + 0x10u);
    volatile uint8_t *g8=(volatile uint8_t *)g;
    volatile uint8_t *k8=(volatile uint8_t *)k;
    volatile uint8_t *busy=&em9305_ram_803d70.u8_803d70;
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uintptr_t context=*(volatile uint32_t *)(owner+44u);
    volatile uint8_t *l8=(volatile uint8_t *)link;
    volatile uint32_t *cache=(volatile uint32_t *)(link+156u);
    (void)opencfw_em9305_child_32db0c((uintptr_t)header,pdu);
    uint32_t llid=*(volatile uint8_t *)&header[0];
    g8[1]=0u;
    if(llid==9u){
        uintptr_t hook=em9305_ram_805160.u32_80516c;
        uint32_t accepted=0u;
        if(hook!=0u)
            accepted=((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uintptr_t))hook)
                (owner,pdu,(uintptr_t)header,hook);
        uint32_t stored=l8[154];
        if((stored&0x10u)==0u){
            g8[1]=1u;
            return;
        }
        uint32_t adv_type=0u;
        if((stored&1u)!=0u){
            uint32_t high=cache[1],low=cache[0];
            adv_type=*(volatile uint8_t *)&header[2];
            g8[36]=1u;
            *(volatile uint32_t *)(g+24u)=high;
            *(volatile uint32_t *)(g+20u)=low;
        }else{
            *(volatile uint32_t *)(g+24u)=0u;
            *(volatile uint32_t *)(g+20u)=0u;
            g8[36]=0u;
        }
        *(volatile uint32_t *)(g+32u)=0u;
        *(volatile uint32_t *)(g+28u)=0u;
        g8[37]=(uint8_t)adv_type;
        *(volatile uint16_t *)(g+38u)=0u;
        if(accepted==0u)return;
        opencfw_em9305_arm_31f538(owner,link,context);
        if(l8[241]!=0u)(void)opencfw_em9305_auxiliary_signal_304394();
        return;
    }
    if(llid!=7u){
        (void)opencfw_em9305_memset((void *)(link+152u),0u,40u);
    }else{
        l8[154]=0u;
        (void)opencfw_em9305_dispatch_child_32df24(link+152u,(uintptr_t)&flags,pdu+2u);
        if(l8[153]==0u){
            uint32_t present=*(volatile uint8_t *)&flags;
            if((present&0x10u)!=0u){
                uint32_t adv_type=0u;
                if((present&1u)!=0u){
                    uint32_t high=cache[1],low=cache[0];
                    adv_type=*(volatile uint8_t *)&header[2];
                    g8[36]=1u;
                    *(volatile uint32_t *)(g+24u)=high;
                    *(volatile uint32_t *)(g+20u)=low;
                }else{
                    *(volatile uint32_t *)(g+24u)=0u;
                    *(volatile uint32_t *)(g+20u)=0u;
                    g8[36]=0u;
                }
                em9305_ram_803b8c.u8_803b8d=(uint8_t)adv_type;
                if((present&2u)!=0u){
                    uint32_t target_type=*(volatile uint8_t *)&header[3];
                    uint32_t high=cache[3],low=cache[2];
                    g8[38]=1u;
                    g8[39]=(uint8_t)target_type;
                    *(volatile uint32_t *)(g+32u)=high;
                    *(volatile uint32_t *)(g+28u)=low;
                }else{
                    *(volatile uint32_t *)(g+32u)=0u;
                    *(volatile uint32_t *)(g+28u)=0u;
                    *(volatile uint16_t *)(g+38u)=0u;
                }
            }else{
                if((present&1u)==0u||
                   opencfw_em9305_offer_31f538(owner,link,context,header,1u)==0u){
                    g8[1]=1u;
                    return;
                }
            }
        }
        *busy=1u;
        if(k8[0]==1u&&(*(volatile uint8_t *)&flags&9u)==9u){
            (void)opencfw_em9305_offer_31f538(owner,link,context,header,0u);
            uint32_t options=*(volatile uint8_t *)(context+187u);
            uint32_t previous=*(volatile uint8_t *)(context+186u);
            uint32_t id_high=*(volatile uint32_t *)(context+180u);
            uint32_t id_low=*(volatile uint32_t *)(context+176u);
            if(options!=previous||*(volatile uint32_t *)(context+168u)!=id_low||
               *(volatile uint32_t *)(context+172u)!=id_high)options|=2u;
            uint32_t adv_type=l8[176];
            if(k8[4]==1u){
                if(opencfw_em9305_address_contains_3036b4(options&1u,id_low,id_high)==0u)return;
                adv_type=l8[176];
            }else{
                if(k8[5]!=adv_type)return;
                if(k8[6]!=(options&1u))return;
                if(*(volatile uint32_t *)(k+8u)!=id_low||*(volatile uint32_t *)(k+12u)!=id_high)return;
            }
            uintptr_t record=*(volatile uint32_t *)(k+20u);
            *busy=0u;
            *(volatile uint32_t *)(record+724u)=id_high;
            *(volatile uint32_t *)(record+720u)=id_low;
            *(volatile uint32_t *)(record+732u)=cache[1];
            uint32_t low=cache[0];
            uint32_t header_type=*(volatile uint8_t *)&header[2];
            *(volatile uint32_t *)(record+728u)=low;
            *(volatile uint8_t *)(record+717u)=(uint8_t)options;
            *(volatile uint8_t *)(record+716u)=(uint8_t)adv_type;
            *(volatile uint8_t *)(record+718u)=(uint8_t)header_type;
        }
        if((*(volatile uint8_t *)&flags&0x10u)!=0u){
            opencfw_em9305_arm_31f538(owner,link,context);
            uint32_t pending=*busy;
            uint32_t scheduled=l8[241];
            if(pending==0u&&scheduled==0u&&k8[0]==1u)*busy=1u;
            if(scheduled!=0u)(void)opencfw_em9305_auxiliary_signal_304394();
            return;
        }
    }
    uint32_t options=*(volatile uint8_t *)(context+187u);
    uint32_t previous=*(volatile uint8_t *)(context+186u);
    uint32_t key_high=*(volatile uint32_t *)(context+180u);
    uint32_t key_low=*(volatile uint32_t *)(context+176u);
    if(options!=previous||*(volatile uint32_t *)(context+168u)!=key_low||
       *(volatile uint32_t *)(context+172u)!=key_high)options|=2u;
    uintptr_t session=link+20u;
    if(opencfw_em9305_child_319ee8(link,0u,(uintptr_t)header,key_low,key_high,options,
                                   *(volatile int8_t *)(context+152u),pdu,session)==0u)return;
    uintptr_t session_key=link+56u;
    l8[34]=0u;
    if(opencfw_em9305_child_31a1b0(link,session,session_key)==0u)return;
    (void)opencfw_em9305_child_31a1fc(link,session,session_key);
}
