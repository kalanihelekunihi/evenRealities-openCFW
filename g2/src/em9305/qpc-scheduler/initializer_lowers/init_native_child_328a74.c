#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x328a74..0x328d76: start a slave BIG on the record. Clear the
 * schedule (+296, 48 bytes) and descriptor (+72, 108 bytes) blocks, copy
 * the 76-byte BIG info from the source (+56 -> +176), install the
 * callbacks and owner, then size the BIG: the sub-event and BIS spacing
 * (+12, +48), event length (+40) and transport latency (+44) from the
 * PDU duration (31737c of PHY +292, length +4, encryption +484) plus
 * 150 us, NSE (+25), BN (+24), IRC (+27), PTO (+26), BIS count (+52),
 * framing (+30) and packing (+31). With pre-transmission (+29) the
 * parameters are reduced until the BIG fits before its deadline (+8),
 * failing with 0x0d when IRC cannot drop further. The BIG anchor offset
 * (+308/+312) adds the 312bc0 margin; the BIG gets the interleaved or
 * sequential transmit completion, a slot (3133b4, 0x0d when none) and
 * its first anchor (313424, relative to the previous active BIG or the
 * advertising train), then is inserted event by event until it fits.
 * Stock relies on 31737c preserving R3..R12; the C passes values. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_callback_3286f8(uint32_t argument);
extern uint32_t opencfw_em9305_callback_328dd4(uint32_t);
extern uint32_t opencfw_em9305_radio_phy_duration_31737c(uint32_t phy,
    uint32_t length,uint32_t encrypted);
extern uint32_t opencfw_em9305_dispatch_child_312bc0(uint32_t phy,uint32_t length);
extern void opencfw_em9305_lctrSlvBigBeginOp(uint32_t ctx);
extern void opencfw_em9305_lctrSlvBisTxCompletionInterleaved(uint32_t ctx,
                                                             uint32_t kind);
extern void opencfw_em9305_lctrSlvBisTxCompletionSequential(uint32_t ctx,
                                                            uint32_t kind);
extern uint32_t opencfw_em9305_lctrGetBigRefTime(uint32_t idx,uint32_t *hi);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t id,
    uint32_t direction,uint32_t minimum,uint32_t maximum,uint32_t extent,
    uintptr_t output,uintptr_t callback);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t incoming,
    uint32_t index,uint32_t timestamp,uint32_t existing,uint32_t action);
extern uint32_t opencfw_em9305_dispatch_child_3257f4(uintptr_t context);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,
                                                                 uintptr_t tie);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
#define CODE(f) ((uint32_t)(uintptr_t)(f))
#define BIGS ((uintptr_t)&em9305_ram_805be0 + 0x5cu)

uint32_t opencfw_em9305_child_328a74(uintptr_t big)
{
    uintptr_t source=r32(big+56u);
    uintptr_t schedule=big+296u;
    uintptr_t descriptor=big+72u;
    (void)opencfw_em9305_memset((void *)schedule,0u,0x30u);
    (void)opencfw_em9305_memset((void *)descriptor,0u,0x6cu);
    uintptr_t train=r32(big+180u);
    uint32_t train_anchor=r32(train+392u);
    uint32_t now=opencfw_em9305_scan_current_303f80();
    w16(big+320u,256u);
    w32(big+340u,descriptor);
    w8(big+322u,1u);
    w32(big+328u,CODE(opencfw_em9305_callback_3286f8));
    w32(big+324u,CODE(opencfw_em9305_callback_328dd4));
    w32(big+332u,big);
    (void)opencfw_em9305_memcpy((void *)descriptor,(const void *)(source+176u),76u);
    uint32_t phy;
    uint32_t offset;
    if(r8(big+29u)!=0u){
        uintptr_t config=r32(((uintptr_t)&em9305_ram_805c5c + 0x50u));
        uintptr_t bigs=r32(BIGS);
        uint32_t deadline=train_anchor+now;
        uint32_t busy=r16(config+50u);
        uint32_t count=((big-bigs)>>9)&0xffu;
        for(uint32_t index=0u;index<count;++index){
            uintptr_t entry=bigs+index*512u;
            if(r8(entry)==0u)continue;
            uint32_t length=r32(entry+308u);
            busy+=length+opencfw_em9305_scan_current_303f80();
            bigs=r32(BIGS);
        }
        deadline+=busy;
        for(;;){
            uint32_t encrypted=r8(big+484u);
            uint32_t octets=r8(big+4u);
            phy=r8(big+292u);
            uint32_t packing=r8(big+31u);
            uint32_t bis=r8(big+52u);
            uint32_t duration=opencfw_em9305_radio_phy_duration_31737c(phy,octets,
                                                                      encrypted);
            uint32_t nse=r8(big+25u);
            uint32_t pdu=duration+150u;
            uint32_t sub,spacing;
            if(packing==1u){
                spacing=pdu*bis;
                sub=pdu;
            }else{
                sub=pdu*nse;
                spacing=pdu;
            }
            w32(big+12u,sub);
            uint32_t length=spacing*(nse-1u)+duration+sub*(bis-1u);
            uint32_t burst=r8(big+24u);
            w32(big+48u,spacing);
            w32(big+40u,length);
            uint32_t latency=5000u;
            if(burst!=0u&&r32(big+8u)!=0u){
                uint32_t limit=r32(big+8u);
                uint32_t groups=(nse/burst-r8(big+27u))*r8(big+26u);
                uint32_t interval=r32(big+16u);
                if(r8(big+30u)==1u)latency=limit+length+interval+groups*interval;
                else latency=length-limit+(groups+1u)*interval;
            }
            uint32_t total=spacing*nse;
            w32(big+44u,latency);
            if(packing!=1u){
                w32(big+12u,total);
                total*=bis;
            }
            offset=opencfw_em9305_dispatch_child_312bc0(phy,7u)+total;
            w32(big+312u,offset);
            w32(big+308u,offset);
            if(r8(big+25u)<9u){
                uint32_t start=deadline+offset;
                uint32_t end=opencfw_em9305_scan_current_303f80()+start;
                if(end<r32(big+8u)){
                    if(r8(big+25u)/r8(big+24u)==r8(big+27u))w8(big+26u,0u);
                    break;
                }
            }
            uint32_t pto=r8(big+26u);
            uint32_t irc=r8(big+27u);
            if(pto!=0u){
                uint32_t bn=r8(big+24u);
                uint32_t nse_now=r8(big+25u);
                uint32_t needed=irc*bn;
                if(needed<nse_now){
                    uint32_t reduced=nse_now-bn;
                    w8(big+25u,reduced);
                    if(needed==(uint8_t)reduced)w8(big+26u,0u);
                    continue;
                }
            }
            if(irc<2u)return 0x0du;
            uint32_t bn=r8(big+24u);
            uint32_t nse_now=r8(big+25u);
            w8(big+27u,irc-1u);
            w8(big+25u,nse_now-bn);
        }
    }else{
        uint32_t encrypted=r8(big+484u);
        phy=r8(big+292u);
        uint32_t octets=r8(big+4u);
        uint32_t packing=r8(big+31u);
        uint32_t bis=r8(big+52u);
        uint32_t duration=opencfw_em9305_radio_phy_duration_31737c(phy,octets,
                                                                  encrypted);
        uint32_t nse=r8(big+25u);
        uint32_t pdu=duration+150u;
        uint32_t sub,spacing,total;
        if(packing==1u){
            spacing=pdu*bis;
            total=spacing*nse;
            sub=pdu;
        }else{
            total=pdu*nse;
            spacing=pdu;
            sub=total;
        }
        w32(big+12u,sub);
        w32(big+48u,spacing);
        w32(big+40u,duration+sub*(bis-1u)+spacing*(nse-1u));
        if(packing!=1u){
            w32(big+12u,total);
            total*=bis;
        }
        offset=opencfw_em9305_dispatch_child_312bc0(phy,7u)+total;
        w32(big+312u,offset);
        w32(big+308u,offset);
    }
    uint32_t interleaved=r8(big+31u);
    w32(big+172u,CODE(opencfw_em9305_lctrSlvBigBeginOp));
    uint32_t completion=interleaved==1u
        ?CODE(opencfw_em9305_lctrSlvBisTxCompletionInterleaved)
        :CODE(opencfw_em9305_lctrSlvBisTxCompletionSequential);
    uintptr_t bigs=r32(BIGS);
    uintptr_t owner=r32(big+180u);
    uintptr_t previous=0u;
    uint32_t index=(big-bigs)>>9;
    uint32_t count=index&0xffu;
    w32(big+176u,completion);
    if(count!=0u){
        for(int32_t k=(int32_t)count-1;k>=0;--k){
            uintptr_t entry=bigs+(uint32_t)k*512u;
            if(r8(entry)!=0u){
                previous=entry+296u;
                break;
            }
        }
    }
    uint32_t interval=r32(big+16u);
    uint32_t extent=r32(big+308u);
    uint32_t reference=r32(owner+388u);
    w32(big+316u,interval);
    if(opencfw_em9305_associated_slot_allocate_3133b4((uint8_t)(index+7u),0u,
           interval,interval,extent,0u,CODE(opencfw_em9305_lctrGetBigRefTime))==0u)
        return 0x0du;
    uint32_t gap=0u;
    if(previous==0u){
        uintptr_t train_now=r32(big+180u);
        uintptr_t config=r32(((uintptr_t)&em9305_ram_805c5c + 0x50u));
        uint32_t used=r32(train_now+392u);
        uint32_t busy=r16(config+50u);
        previous=train_now+380u;
        if(used<busy)gap=busy-used;
    }
    uint32_t slot=(uint8_t)(((big-r32(BIGS))>>9)+7u);
    uint32_t anchor=opencfw_em9305_radio_schedule_313424(r32(big+308u),slot,
                                                         reference,previous,3u)
                    +gap+reference;
    for(;;){
        w32(big+304u,anchor);
        (void)opencfw_em9305_dispatch_child_3257f4(big);
        if(opencfw_em9305_associated_schedule_insert_312da4(schedule,0u)!=0u)
            return 0u;
        uint32_t low=r32(big+32u);
        uint32_t step=r32(big+16u);
        anchor=r32(big+304u)+step;
        uint64_t counter=((uint64_t)r32(big+36u)<<32|low)+1u;
        w32(big+32u,(uint32_t)counter);
        w32(big+36u,(uint32_t)(counter>>32));
    }
}
