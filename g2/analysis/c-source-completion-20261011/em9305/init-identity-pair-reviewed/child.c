#include <stdint.h>

/* Native 0x303918..0x303950. Complete identity pair acquisition. */
extern uintptr_t opencfw_em9305_radio_identity_find_31441c(uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t);
uint32_t opencfw_em9305_init_callback_child_303918(uint32_t kind,
    uint32_t low,uint32_t high,uintptr_t output)
{
    uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
    if (row==0u) return 0u;
    uint8_t flag=*(volatile uint8_t *)(row+64u);
    if (flag!=0u) return 0u;
    uint8_t cached=*(volatile uint8_t *)(row+66u);
    uint32_t lower,upper;
    if (cached!=0u) {
        upper=*(volatile uint32_t *)(row+44u);
        lower=*(volatile uint32_t *)(row+40u);
    } else {
        uint64_t address=opencfw_em9305_radio_private_address_31467c(row);
        lower=(uint32_t)address;
        upper=(uint32_t)(address>>32u);
        *(volatile uint32_t *)(row+44u)=upper;
        *(volatile uint32_t *)(row+40u)=lower;
        *(volatile uint8_t *)(row+66u)=1u;
    }
    *(volatile uint32_t *)output=lower;
    *(volatile uint32_t *)(output+4u)=upper;
    return 1u;
}
