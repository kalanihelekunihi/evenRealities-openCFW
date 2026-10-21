/* SPDX-License-Identifier: MIT
 * In-image IAR-style initialization helpers reconstructed from415326/431e38.
 * Raw interfaces have no input/output bounds; this is not a safe file parser.
 */
#include "initialize.h"
uint32_t *opencfw_boot_expand_record(uint32_t *record,uint32_t static_base) {
    uint8_t *input=(uint8_t *)((uintptr_t)record+record[0]);
    uint8_t *end=input+(record[1]>>1);
    uint8_t *output=(uint8_t *)(uintptr_t)(record[2]+((record[1]&1u)?static_base:0u));
    while(input!=end) {
        uint32_t token=*input++,literal=token&3u,match=token>>4;
        if(!literal)literal=*input++ + 3u;
        if(match==15u)match=*input++ + 15u;
        while(--literal)*output++=*input++;
        if(match) {
            uint32_t low=*input++,high=(token>>2)&3u;
            if(high==3u)high=*input++;
            uint8_t *back=output-(low+(high<<8));
            for(uint32_t i=0;i<match+2u;i++)*output++=*back++;
        }
    }
    return record+3;
}
uint32_t *opencfw_boot_zero_table(uint32_t *table,uint32_t static_base) {
    for(;;) {
        uint32_t size=*table++;
        if(!size)return table;
        uint32_t address=*table++;
        if(address&1u)address=address+static_base-1u;
        volatile uint32_t *word=(volatile uint32_t *)(uintptr_t)address;
        /* Stock stores at least one word before testing the remaining size.
         * Supported initialized-image records have size>=4. */
        do {size-=4u;*word++=0;}while(size>=4u);
        volatile uint8_t *byte=(volatile uint8_t *)word;
        if(size&2u){*(volatile uint16_t *)byte=0;byte+=2;}
        if(size&1u)*byte=0;
    }
}
