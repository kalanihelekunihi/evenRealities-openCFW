/* Semantic C expression of stock descriptor table at 0x6becb0, selected by
 * native 0x47ef18. Values/extent were authenticated from ROM literal 0x47f944.
 * This emits native fields in the C power descriptor's typed order. */
#include "power.h"

uint32_t g2_power_get_descriptor(g2_power_descriptor *out,uint32_t peripheral)
{
    if(out==0 || peripheral>33u) return 6u;
    uint32_t enable_mask,status_mask;
    uintptr_t enable_register=0x40021004u,status_register=0x40021008u;
    if(peripheral==0u) {
        enable_mask=1u;status_mask=0x30000001u;
    } else if(peripheral==1u) {
        enable_mask=0x10000000u;status_mask=0x30000001u;
    } else if(peripheral==2u) {
        enable_mask=0x20000000u;status_mask=0x30000001u;
    } else if(peripheral<=29u) {
        enable_mask=1u<<(peripheral-2u);
        if(peripheral<=6u) status_mask=0x1eu;
        else if(peripheral<=10u) status_mask=0x1e0u;
        else if(peripheral<=14u) status_mask=0x1e00u;
        else status_mask=enable_mask;
    } else {
        enable_register=0x4002100cu;status_register=0x40021010u;
        if(peripheral==30u) enable_mask=status_mask=4u;
        else if(peripheral==31u) {enable_mask=0x40u;status_mask=0xc0u;}
        else if(peripheral==32u) {enable_mask=0x80u;status_mask=0xc0u;}
        else enable_mask=status_mask=0x400u;
    }
    out->enable_register=enable_register;
    out->status_register=status_register;
    out->enable_mask=enable_mask;
    out->status_mask=status_mask;
    return 0u;
}
