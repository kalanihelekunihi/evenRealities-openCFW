#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31e940..0x31e9f6: build the scan/advertising report block at
 * ((uintptr_t)&em9305_ram_803d58 + 0x1280u) from the active scanner (object +44, set +104) when its state
 * (+184) is 0 or 6 and it has an address type (+188): write the advertiser
 * address (+168/+172) at ((uintptr_t)&em9305_ram_803d58 + 0x1288u) and mirror it at ((uintptr_t)&em9305_ram_80505c + 0x8u), store the
 * address type (+186) at ((uintptr_t)&em9305_ram_805160 + 0x3u) and, when the report requests it (bit 1
 * of ((uintptr_t)&em9305_ram_805010 + 0x9u)), resolve the peer pair (+176/+180, kind +187, current
 * +84/+88) into ((uintptr_t)&em9305_ram_803d58 + 0x1282u) with the resolved flag at ((uintptr_t)&em9305_ram_805160 + 0x2u). Encode the
 * report ((uintptr_t)&em9305_ram_805160). Returns 1 unless the limited report counter at
 * ((uintptr_t)&em9305_ram_805160 + 0x8u) (enabled by bit 2 of ((uintptr_t)&em9305_ram_805a6c + 0x1fu)) is still non-zero after its
 * decrement; returns 0 when nothing was reported. */
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,
    uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,
    uint32_t low,uint32_t high,uintptr_t output);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t output,
                                                   uintptr_t input);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}

uint32_t opencfw_em9305_scan_callback_31e940(uintptr_t object)
{
    uintptr_t scanner=r32(object+44u);
    if(r32(scanner+104u)==0u)return 0u;
    uint32_t state=r8(scanner+184u);
    if(state!=6u&&state!=0u)return 0u;
    if(r8(scanner+188u)==0u)return 0u;
    (void)opencfw_em9305_radio_address_write_3045e8(((uintptr_t)&em9305_ram_803d58 + 0x1288u),r32(scanner+168u),
                                                   r32(scanner+172u));
    uint32_t request=r8(((uintptr_t)&em9305_ram_805010 + 0x9u));
    uint32_t high=r32(scanner+172u),low=r32(scanner+168u);
    uint32_t type=r8(scanner+186u);
    *(volatile uint32_t *)((uintptr_t)&em9305_ram_80505c + 0xcu)=high;
    *(volatile uint32_t *)((uintptr_t)&em9305_ram_80505c + 0x8u)=low;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805160 + 0x3u)=(uint8_t)type;
    if((request&2u)!=0u){
        uint32_t pair[2];
        uint32_t current_low=r32(scanner+84u),current_high=r32(scanner+88u);
        uint32_t peer_high=r32(scanner+180u),peer_low=r32(scanner+176u);
        uint32_t kind=r8(scanner+187u);
        uint32_t options=r8(scanner+80u);
        pair[0]=current_low;
        pair[1]=current_high;
        uint32_t resolved=opencfw_em9305_radio_peer_pair_303a40(kind,peer_low,
                                                               peer_high,(uintptr_t)pair);
        (void)opencfw_em9305_radio_address_write_3045e8(((uintptr_t)&em9305_ram_803d58 + 0x1282u),pair[0],pair[1]);
        uint32_t flag=(options>>1)&1u;
        if(resolved!=0u)flag=1u;
        *(volatile uint8_t *)((uintptr_t)&em9305_ram_805160 + 0x2u)=(uint8_t)flag;
    }
    (void)opencfw_em9305_radio_encode_3239d4(((uintptr_t)&em9305_ram_803d58 + 0x1280u),(uintptr_t)&em9305_ram_805160);
    if((r8(((uintptr_t)&em9305_ram_805a6c + 0x1fu))&4u)==0u)return 1u;
    uint32_t remaining=r8(((uintptr_t)&em9305_ram_805160 + 0x8u));
    if(remaining==0u)return 1u;
    remaining-=1u;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805160 + 0x8u)=(uint8_t)remaining;
    return (uint8_t)remaining!=0u?0u:1u;
}
