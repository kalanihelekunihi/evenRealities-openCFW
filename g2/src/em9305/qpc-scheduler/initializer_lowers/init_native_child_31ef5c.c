#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31ef5c..0x31f17e: periodic-advertising sync establishment from
 * a received AUX_ADV_IND (report header (uintptr_t)&em9305_ram_803b68; anything but type 7 marks
 * the report rejected). The advertiser (scanner object +44: address
 * +152/+156, type +163 with bit 1 set when it differs from the original
 * +144/+148/+162) is matched against the pending create-sync request
 * (((uintptr_t)&em9305_ram_805194 + 0x10u): active, +4 list mode, SID +5, type +6, address +8/+12) once
 * per request ((uintptr_t)&em9305_ram_803d70); with the filter-accept list mode the address is
 * looked up (3036b4). On a match the sync context (object +36) gets its
 * SyncInfo encoded (32e164 when bit 5 of +154), and if valid the receiver
 * (*(uintptr_t)&em9305_ram_8051b8) is set up: copy of the 40-byte SyncInfo, timing (+212 * 1250,
 * skip +616), PHY, counters (+248/+278), clock accuracy and the advertiser
 * identity when matched; the first event is scheduled through the host
 * hook (*((uintptr_t)&em9305_ram_805c5c + 0x2cu), with *((uintptr_t)&em9305_ram_805c5c + 0x34u) notified) or 321490, from the
 * advertiser's end time plus the packet duration. Clears ((uintptr_t)&em9305_ram_803d70 + 0x1u). */
extern uint32_t opencfw_em9305_address_contains_3036b4(uint32_t type,
    uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_radio_secondary_encode_32e164(uintptr_t,uintptr_t);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern void opencfw_em9305_child_31c530(uintptr_t record);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,
    uint32_t coded,uint32_t length);
extern void opencfw_em9305_child_321490(uintptr_t receiver,uintptr_t request,
                                        uintptr_t info,uint32_t reference);
typedef void (*opencfw_em9305_sync_hook_t)(uintptr_t,uintptr_t,uintptr_t,
                                           uint32_t,uint32_t);
typedef void (*opencfw_em9305_sync_notify_t)(uintptr_t);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

#define REPORT (uintptr_t)&em9305_ram_803b68
#define REQUEST ((uintptr_t)&em9305_ram_805194 + 0x10u)
#define ONCE (uintptr_t)&em9305_ram_803d70

void opencfw_em9305_child_31ef5c(uintptr_t object)
{
    if(r8(REPORT+12u)!=7u){
        w8(REPORT+1u,1u);
        return;
    }
    uintptr_t scanner=r32(object+44u);
    uintptr_t timing=scanner+140u;
    uint32_t type=r8(scanner+163u);
    uint32_t original=r8(scanner+162u);
    uint32_t high=r32(scanner+156u);
    uint32_t low=r32(scanner+152u);
    if(type!=original||((r32(scanner+144u)^low)|(r32(scanner+148u)^high))!=0u)
        type|=2u;
    uintptr_t context=r32(object+36u);
    uintptr_t info=context+156u;
    uint32_t pending=r8(REQUEST);
    uint32_t flag=r8(ONCE);
    if(pending==1u&&flag==0u){
        if(r8(REQUEST+5u)!=r8(info+20u)||r8(REQUEST+6u)!=(type&1u)
           ||((r32(REQUEST+8u)^low)|(r32(REQUEST+12u)^high))!=0u){
            flag=1u;
            w8(ONCE,1u);
        }else{
            flag=0u;
        }
    }
    uint32_t matched=0u;
    if(pending==1u&&flag!=0u){
        uint32_t options=r8(REPORT+10u);
        if((options&8u)!=0u&&(options&0x21u)!=0u){
            uint32_t sid=r8(info+20u);
            if(r8(REQUEST+4u)==1u){
                if(opencfw_em9305_address_contains_3036b4(type&1u,low,high)==0u)
                    return;
            }else{
                if(r8(REQUEST+5u)!=sid)return;
                if(r8(REQUEST+6u)!=(type&1u))return;
                if(((r32(REQUEST+8u)^low)|(r32(REQUEST+12u)^high))!=0u)return;
            }
            flag=0u;
            matched=1u;
            w8(ONCE,0u);
        }
    }
    if((r8(context+154u)&0x20u)!=0u){
        (void)opencfw_em9305_radio_secondary_encode_32e164(context+208u,r32(info+32u));
        flag=r8(ONCE);
    }
    if(r8(REQUEST)!=1u||flag!=0u)return;
    if((r8(context+154u)&0x20u)==0u)return;
    if(r8(REQUEST+1u)!=0u)return;
    if(r16(info+52u)==0u)return;
    uintptr_t receiver=r32(REQUEST+20u);
    uintptr_t sync=receiver+736u;
    (void)opencfw_em9305_memcpy((void *)sync,(const void *)(context+152u),40u);
    opencfw_em9305_child_31c530(receiver);
    uint32_t interval=r16(info+56u);
    uint32_t phy=r8(info+48u);
    uint32_t accuracy=r8(info+68u);
    uint32_t skip=r16(sync-120u);
    interval*=1250u;
    uint32_t counter=r16(info+80u);
    w8(receiver+256u,accuracy);
    uint32_t mode=(phy==1u)+1u;
    uint32_t timeout=interval*(uint16_t)skip;
    if(phy==2u)mode=3u;
    w16(receiver+278u,counter);
    w16(receiver+248u,counter);
    w32(receiver+252u,interval);
    w8(sync+40u,mode);
    w32(receiver+260u,timeout);
    if(matched!=0u){
        uint32_t peer_high=r32(info+4u),peer_low=r32(info);
        uint32_t sid=r8(info+20u);
        uint32_t clock=r8(REPORT+14u);
        w32(receiver+720u,low);
        w32(receiver+724u,high);
        w8(sync-19u,type);
        w32(receiver+732u,peer_high);
        w32(receiver+728u,peer_low);
        w8(sync-20u,sid);
        w8(sync-18u,clock);
    }
    uint32_t length=r8(scanner+124u);
    uint32_t coded=r8(scanner+134u);
    uint32_t aux_phy=r8(scanner+13u);
    uint32_t end=r32(timing);
    uintptr_t request=context+198u;
    uintptr_t window=context+208u;
    uint32_t start=opencfw_em9305_radio_duration_piece_312b88(aux_phy,coded,length)+end;
    if(r8(sync+41u)!=0u){
        uintptr_t hook=r32(((uintptr_t)&em9305_ram_805c5c + 0x2cu));
        uint32_t second=r32(((uintptr_t)&em9305_ram_805c5c + 0x30u)),first=r32(((uintptr_t)&em9305_ram_805c5c + 0x28u));
        uint32_t clock=r32(((uintptr_t)&em9305_ram_805be0 + 0x30u));
        uintptr_t state=r32(receiver+780u);
        w32(receiver+76u,second);
        w32(receiver+80u,first);
        w32(receiver+212u,clock);
        w32(state+16u,0u);
        if(hook!=0u)
            ((opencfw_em9305_sync_hook_t)hook)(context,request,window,r32(timing),start);
        uintptr_t notify=r32(((uintptr_t)&em9305_ram_805c5c + 0x34u));
        if(notify!=0u)((opencfw_em9305_sync_notify_t)notify)(receiver);
    }else{
        opencfw_em9305_child_321490(context,request,window,r32(timing));
    }
    w8(ONCE+1u,0u);
}
