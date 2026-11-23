#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31cbb0..0x31ccf2: prepare the BIG transmit descriptor at
 * (uintptr_t)&em9305_ram_8029ac for the group (object +36) in state 2, else signal the
 * auxiliary task. The descriptor (136 bytes, cleared) takes the BIG handle
 * (+268), the first PDU source (+16: the second (+260) or first (+256)
 * stream's +176 block, else the group's own +408 block) and the event
 * offset (+12): the sub-interval (+12) or its multiple by the stream count
 * (+52) for sequential multi-stream groups, the ISO interval (+48) plus,
 * for single-stream framed groups with one burst and pre-transmission
 * (+24 * +27 == 1, +26, +25 >= 2), the slot of the first unacknowledged
 * stream found by 317418 times +48. The 64-bit anchor is +32/+36 times the
 * burst number (+24), plus the descriptor's subevent byte (+1) for stream
 * sources. Then the transmit chain (31d5e8) is started, signalling the
 * auxiliary task when it fails. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern uint32_t opencfw_em9305_dispatch_child_317418(uintptr_t config,
                                                     uintptr_t state);
extern uint32_t opencfw_em9305_dispatch_child_31d5e8(uintptr_t set,uint32_t done,
                                                     uintptr_t buffer);
extern void opencfw_em9305_auxiliary_signal_304394(void);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

#define TX (uintptr_t)&em9305_ram_8029ac

void opencfw_em9305_dispatch_callback_31cbb0(uintptr_t object)
{
    uintptr_t group=r32(object+36u);
    if(r8(group+1u)!=2u){
        opencfw_em9305_auxiliary_signal_304394();
        return;
    }
    (void)opencfw_em9305_memset((void *)TX,0u,0x88u);
    uint32_t framing=r8(group+31u);
    w8(TX,r8(group+268u));
    uintptr_t source=0u;
    if(framing==1u){
        uint32_t streams=r8(group+52u);
        uint32_t offset=r32(group+12u);
        if(streams>=2u){
            uintptr_t stream=r32(group+260u);
            if(stream==0u)stream=r32(group+256u);
            source=stream+176u;
            w32(TX+16u,source);
            w32(TX+12u,offset);
            if(r32(group+260u)==0u){
                uint32_t total=offset*streams;
                if(r8(group+25u)>=2u){
                    w32(TX+12u,total);
                    source=r32(group+256u)+176u;
                    w32(TX+16u,source);
                    goto anchor;
                }
                w32(TX+12u,total);
            }
        }else{
            if(r8(group+25u)>=2u){
                source=r32(group+256u)+176u;
                w32(TX+16u,source);
            }
            w32(TX+12u,offset);
        }
    }else{
        uint32_t bursts=r8(group+25u);
        if(bursts>=2u){
            source=r32(group+256u)+176u;
            w32(TX+16u,source);
        }else if(r8(group+52u)>=2u&&r32(group+260u)!=0u){
            source=r32(group+260u)+176u;
            w32(TX+16u,source);
        }
        if((r8(group+27u)*r8(group+24u)&0xffffu)==1u&&r8(group+26u)!=0u
           &&r8(group+52u)<2u&&bursts>=2u){
            _Alignas(4) uint8_t cursor[8];
            uint32_t slot=1u;
            *(uint32_t *)(void *)cursor=r32(TX);
            cursor[4]=(uint8_t)r8(TX+4u);
            for(;;){
                if(opencfw_em9305_dispatch_child_317418(group,(uintptr_t)cursor)==0u){
                    source=group+408u;
                    break;
                }
                uintptr_t stream=r32(group+cursor[0]*4u+56u);
                if(stream!=0u&&cursor[3]==0u){
                    source=stream+176u;
                    break;
                }
                ++slot;
            }
            uint32_t interval=r32(group+48u);
            uint32_t base=r32(TX+12u);
            w32(TX+16u,source);
            w32(TX+12u,interval*(uint8_t)slot+base);
            goto anchor;
        }
        w32(TX+12u,r32(group+48u));
    }
    if(source==0u){
        source=group+408u;
        w32(TX+16u,source);
    }
anchor:;
    uint32_t burst=r8(group+24u);
    uint64_t anchor=((uint64_t)r32(group+36u)<<32|r32(group+32u))*burst;
    if(source!=group+408u)anchor+=r8(TX+1u);
    w32(TX+128u,(uint32_t)anchor);
    w32(TX+132u,(uint32_t)(anchor>>32));
    w8(TX+8u,0xffu);
    w8(TX+7u,1u);
    if(opencfw_em9305_dispatch_child_31d5e8(group,0u,0u)==0u)
        opencfw_em9305_auxiliary_signal_304394();
}
