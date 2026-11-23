#include <stdint.h>
#include "em9305_ram.h"

extern uint32_t opencfw_em9305_radio_peer_pair_303a40(
    uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_callback_child_303918(
    uint32_t,uint32_t,uint32_t,uintptr_t);

/* Native 0x318290..0x318346. The seventh argument is incoming R6. */
uint32_t opencfw_em9305_init_transition_stage_318290(
    uintptr_t packet,uintptr_t frame,uint32_t kind,uint32_t low,
    uint32_t high,uint32_t extra,uintptr_t output)
{
    uint32_t state=0u;
    em9305_ram_805be0.u32_805be8=0u;
    em9305_ram_805be0.u32_805be4=0u;
    uint32_t pair_high,pair_low;
    em9305_ram_805be0.u8_805be2=(uint8_t)(kind&~2u);
    if ((kind&~2u)==1u) {
        uintptr_t mode=((uintptr_t)&em9305_ram_805a6c + 0x4u);
        if (*(volatile uint8_t *)(mode+17u)!=0u) {
            pair_low=*(volatile uint32_t *)(mode+28u);
            pair_high=*(volatile uint32_t *)(mode+32u);
            *(volatile uint8_t *)(frame+2u)=1u;
            *(volatile uint8_t *)(mode+15u)=0u;
            state=1u;
            *(volatile uint32_t *)(output+4u)=pair_high;
            *(volatile uint32_t *)output=pair_low;
            goto after_pair;
        }
    }
    {
        uintptr_t source=((uintptr_t)&em9305_ram_805af0 + 0x50u);
        pair_high=*(volatile uint32_t *)(source+4u);
        pair_low=*(volatile uint32_t *)source;
        *(volatile uint8_t *)(frame+2u)=0u;
        *(volatile uint32_t *)(output+4u)=pair_high;
        *(volatile uint32_t *)output=pair_low;
    }
after_pair:
    if ((kind&2u)!=0u) {
        uint32_t pair[2];
        uint32_t found=opencfw_em9305_radio_peer_pair_303a40(
            low,high,extra,(uintptr_t)pair);
        if (found!=0u) {
            pair_high=pair[1];pair_low=pair[0];
            state=1u;
            *(volatile uint8_t *)(frame+2u)=1u;
            em9305_ram_805be0.u8_805be2=(uint8_t)kind;
            *(volatile uint32_t *)(output+4u)=pair_high;
            *(volatile uint32_t *)output=pair_low;
            em9305_ram_805be0.u32_805be8=pair_high;
            em9305_ram_805be0.u32_805be4=pair_low;
        } else {
            state=*(volatile uint8_t *)(frame+2u);
        }
        pair_high=*(volatile uint32_t *)(output+4u);
        pair_low=*(volatile uint32_t *)output;
    }
    uint32_t flags=*(volatile uint32_t *)(packet+80u);
    *(volatile uint32_t *)(packet+84u)=pair_low;
    if (state!=0u) flags|=2u;
    uint32_t enabled=flags|1u;
    *(volatile uint32_t *)(packet+88u)=pair_high;
    *(volatile uint32_t *)(packet+92u)=high;
    *(volatile uint32_t *)(packet+96u)=extra;
    *(volatile uint32_t *)(packet+80u)=enabled;
    if (low!=0u) {
        enabled=flags|9u;
        *(volatile uint32_t *)(packet+80u)=enabled;
    }
    return enabled;
}

/* Native 0x318348..0x31836a. Call R0=kind(R2), R1=low(R3),
 * R2=high(R4), R3=extra(R5); packet R0 is restored after child call. */
uint32_t opencfw_em9305_init_transition_stage_318348(
    uintptr_t packet,uint32_t unused,uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t extra)
{
    (void)unused;
    (void)opencfw_em9305_init_callback_child_303918(kind,low,high,extra);
    uint32_t flags=*(volatile uint32_t *)(packet+80u);
    uint32_t enabled=em9305_ram_805a6c.u8_805a9d;
    flags=(flags&~64u)|(enabled<<6u);
    *(volatile uint32_t *)(packet+80u)=flags;
    return flags;
}
