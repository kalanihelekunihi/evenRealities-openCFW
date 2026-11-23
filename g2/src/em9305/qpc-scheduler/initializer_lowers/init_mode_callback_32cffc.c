#include <stdint.h>
#include "em9305_ram.h"

/* Complete native 0x32cffc..0x32d0f2. The native callback's R1 is its code
 * identity, but this body replaces R1 before either child call. Reads and
 * stores remain ordered as in the native instruction stream. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t,uint32_t);

static uint32_t extract_native_bit(uint32_t value,unsigned bit)
{
    uint32_t out;
    if (bit==10u) out=((uint32_t)value>>10u)&0x1u;
    else out=((uint32_t)value>>9u)&0x1u;
    return out;
}

uint32_t opencfw_em9305_mode_callback_32cffc(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint32_t mode=*(volatile uint8_t *)(context+2u);
    uint32_t word_four=em9305_ram_8027e0.u32_802820;
    uint32_t r0=em9305_ram_8027e0.u32_80281c;
    uint32_t mask_four=em9305_ram_805a6c.u32_805a98;
    uint32_t mask_zero=em9305_ram_805a6c.u32_805a94;
    uint32_t part_four=word_four&0x1befu;
    uint32_t tested_four=word_four&mask_four;
    uint32_t tested_zero=mask_zero&r0;
    uint32_t part_zero=r0&0xf787cf2fu;
    uint32_t bit_ten=extract_native_bit(r0,10u);
    r0=extract_native_bit(r0,9u);
    uint32_t masked_four=0x1befu&tested_four;
    uint32_t masked_zero=0xf787cf2fu&tested_zero;
    *(volatile uint8_t *)(context+534u)=1u;
    *(volatile uint32_t *)(context+540u)=part_four;
    *(volatile uint32_t *)(context+536u)=part_zero;
    *(volatile uint8_t *)(context+81u)=(uint8_t)bit_ten;
    *(volatile uint8_t *)(context+80u)=(uint8_t)r0;
    *(volatile uint32_t *)(context+548u)=masked_four;
    *(volatile uint32_t *)(context+544u)=masked_zero;
    if (mode==0u) {
        uint32_t flag=*(volatile uint8_t *)(context+565u);
        if (flag==0u && (tested_four&0x80u)!=0u) {
            uint32_t flags=*(volatile uint8_t *)(context+6u);
            if ((flags&4u)!=0u) {
                uintptr_t event=opencfw_em9305_wsf_event_allocate(8u);
                r0=(uint32_t)event;
                if (event!=0u) {
                    *(volatile uint16_t *)(event+2u)=0x6c01u;
                    uintptr_t base=em9305_ram_805c5c.u32_805c70;
                    uintptr_t root=em9305_ram_805c5c.u32_805cac;
                    int32_t index=(int32_t)(uint32_t)(context-base)/912;
                    uint32_t record=*(volatile uint8_t *)(root+68u);
                    *(volatile uint8_t *)(event+4u)=1u;
                    uint32_t incremented=(uint8_t)(record+0x69u);
                    r0=em9305_ram_805af0.u8_805b18;
                    uint32_t selected=(incremented>=0x6eu)?record:0x96u;
                    *(volatile uint8_t *)(event+5u)=(uint8_t)selected;
                    *(volatile uint16_t *)event=(uint8_t)index;
                    *(volatile uint8_t *)(event+6u)=(uint8_t)selected;
                    r0=opencfw_em9305_wsf_task_message_send(r0,event);
                }
            }
        }
    }
    r0=*(volatile uint8_t *)(context+548u);
    if ((r0&2u)==0u) return r0;
    r0=*(volatile uint8_t *)(context+770u);
    if (r0!=1u) return r0;
    r0=*(volatile uint8_t *)(context+769u);
    if (r0!=0u) return r0;
    uint32_t enable=em9305_ram_805a6c.u8_805a85;
    if ((enable&0x80u)==0u) return 800u;
    uint32_t unit=*(volatile uint16_t *)(context+532u);
    r0=opencfw_em9305_radio_record_timing_30c40c(800u,unit);
    *(volatile uint8_t *)(context+772u)=(uint8_t)r0;
    return r0;
}
