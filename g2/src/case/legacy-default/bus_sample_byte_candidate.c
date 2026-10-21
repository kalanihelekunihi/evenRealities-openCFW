/* SPDX-License-Identifier: MIT
 * Stock 0x0800b5d6 eight-bit sample and 0x0800a176 parity response.
 * The single-bit timed sampler remains a live hardware contract.
 */
#include <stdint.h>
extern uint32_t case_bus_response_sample(uint32_t *bit); /* 0x0800b53c */
extern uint32_t case_bus_read(uint32_t value);           /* 0x0800c412 parity */
extern void case_bus_start(uint32_t bit);                /* 0x0800a19a */
uint32_t case_bus_byte_sample(uint8_t *output)
{
    uint32_t assembled=0u;
    uint32_t shift=7u;
    uint32_t success=1u;
    do{
        uint32_t bit=0u;
        if(case_bus_response_sample(&bit)==0u){success=0u;break;}
        assembled=((bit<<shift)+assembled)&0xffu;
        --shift;
    }while((int32_t)shift>=0);
    *output=(uint8_t)assembled;
    return success;
}
void case_bus_response_bit(uint32_t value)
{
    case_bus_start(case_bus_read(value)==1u?1u:0u);
}
