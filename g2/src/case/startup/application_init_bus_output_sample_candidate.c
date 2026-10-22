/* SPDX-License-Identifier: MIT
 * Native CASE 0xb5ac/0xa164 output-channel byte and parity response.
 */
#include <stdint.h>
extern uint32_t case_bus_positive_sample(uint32_t *bit); /* 0xb4e0 */
extern uint32_t case_bus_read(uint32_t byte); /* identical native 0xc412 parity */
extern void case_bus_output_start(uint32_t bit); /* 0xa188 */
/* Stock 0x0800C3F8 (case_parity8) */
uint32_t case_bus_output_parity(uint32_t byte)
{return case_bus_read(byte);}
/* Stock 0x0800B5AC (case_collect_bits) */
uint32_t case_bus_output_byte_sample(uint8_t *out)
{
    uint32_t value=0u;
    uint32_t success=1u;
    for(int32_t shift=7;shift>=0;--shift){
        uint32_t bit=0u;
        if(case_bus_positive_sample(&bit)==0u){success=0u;break;}
        value=((bit<<shift)+value)&0xffu;
    }
    *out=(uint8_t)value;
    return success;
}
/* Stock 0x0800A164 (case_route_parity) */
void case_bus_output_response_bit(uint32_t byte)
{case_bus_output_start(case_bus_output_parity(byte)==1u?1u:0u);}
