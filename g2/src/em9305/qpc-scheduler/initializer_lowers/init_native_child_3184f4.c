#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3184f4..0x31855a: refresh the request's resolved address pair
 * (+24/+28) from its identity pair (+48/+52) and report in out[3] whether
 * the address kind (+58) is non-zero. When address resolution is enabled
 * (((uintptr_t)&em9305_ram_805a6c + 0x31u)) and the request asks for it (bit 1 of +57), look up the
 * identity pair (303a60, falling back to 303918); a non-zero result
 * replaces the address pair and sets out[3]. Then set bit 6 of the link
 * flags word (+80). */
extern uint32_t opencfw_em9305_radio_identity_pair_303a60(uint32_t kind,
    uint32_t low,uint32_t high,uintptr_t output);
extern uint32_t opencfw_em9305_init_callback_child_303918(uint32_t kind,
    uint32_t low,uint32_t high,uintptr_t output);

void opencfw_em9305_child_3184f4(uintptr_t out,uintptr_t link,uintptr_t request)
{
    uint32_t kind=*(volatile uint8_t *)(request+58u);
    uint32_t enabled=*(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x31u);
    uint32_t high=*(volatile uint32_t *)(request+52u);
    uint32_t low=*(volatile uint32_t *)(request+48u);
    *(volatile uint32_t *)(request+28u)=high;
    *(volatile uint32_t *)(request+24u)=low;
    *(volatile uint8_t *)(out+3u)=(uint8_t)(kind!=0u);
    if(enabled==0u)return;
    if((*(volatile uint8_t *)(request+57u)&2u)!=0u){
        uint32_t pair[2];
        pair[1]=0u;
        pair[0]=0u;
        if(opencfw_em9305_radio_identity_pair_303a60(kind,low,high,
                                                     (uintptr_t)pair)==0u)
            (void)opencfw_em9305_init_callback_child_303918(
                *(volatile uint8_t *)(request+58u),
                *(volatile uint32_t *)(request+48u),
                *(volatile uint32_t *)(request+52u),(uintptr_t)pair);
        uint32_t resolved_high=pair[1],resolved_low=pair[0];
        if((resolved_low|resolved_high)!=0u){
            *(volatile uint32_t *)(request+24u)=resolved_low;
            *(volatile uint8_t *)(out+3u)=1u;
            *(volatile uint32_t *)(request+28u)=resolved_high;
        }
    }
    uint32_t flags=*(volatile uint32_t *)(link+80u);
    *(volatile uint32_t *)(link+80u)=flags|0x40u;
}
