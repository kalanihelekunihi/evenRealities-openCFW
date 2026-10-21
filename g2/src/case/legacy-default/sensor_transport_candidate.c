/* SPDX-License-Identifier: MIT
 * Serial sensor transport helpers from fixed-image entries 0x0800a3d2,
 * 0x0800a414, 0x0800a436, 0x0800a46c, 0x0800a4dc and 0x0800a4fa.
 * GPIO input at 0x0800a528 remains a typed electrical contract.
 */
#include <stdint.h>
extern void case_binary_sensor_line_a(uint32_t level);
extern void case_binary_sensor_line_b(uint32_t level);
extern uint32_t case_binary_sensor_delay(void);
extern uint32_t case_binary_sensor_sample(void);

void case_binary_sensor_interbyte_pulse(void)
{
    case_binary_sensor_line_a(0u); case_binary_sensor_delay();
    case_binary_sensor_line_b(0u); case_binary_sensor_delay();
    case_binary_sensor_line_a(1u); case_binary_sensor_delay();
    case_binary_sensor_line_a(0u); case_binary_sensor_delay();
    case_binary_sensor_line_b(1u); case_binary_sensor_delay();
}
void case_binary_sensor_final_pulse(void)
{
    case_binary_sensor_line_b(1u); case_binary_sensor_delay();
    case_binary_sensor_line_a(1u); case_binary_sensor_delay();
    case_binary_sensor_line_a(0u); case_binary_sensor_delay();
}
uint32_t case_binary_sensor_byte_input(void)
{
    uint32_t value=0u;
    for(uint32_t bit=0;bit<8u;++bit){
        value=(value&0x7fu)*2u;
        case_binary_sensor_line_a(1u); case_binary_sensor_delay();
        if(case_binary_sensor_sample()!=0u) ++value;
        case_binary_sensor_line_a(0u); case_binary_sensor_delay();
    }
    return value;
}
void case_binary_sensor_byte_output(uint32_t value)
{
    for(uint32_t bit=0;bit<8u;++bit){
        case_binary_sensor_line_b((int32_t)(value<<24)<0 ? 1u : 0u);
        case_binary_sensor_delay();
        case_binary_sensor_line_a(1u); case_binary_sensor_delay();
        case_binary_sensor_line_a(0u); case_binary_sensor_delay();
        if(bit==7u){case_binary_sensor_line_b(1u);case_binary_sensor_delay();}
        value=(value&0x7fu)<<1;
    }
}
void case_binary_sensor_stop(void)
{
    case_binary_sensor_line_b(0u);
    case_binary_sensor_line_a(1u); case_binary_sensor_delay();
    case_binary_sensor_line_b(1u); case_binary_sensor_delay();
}
uint32_t case_binary_sensor_ack(void)
{
    case_binary_sensor_line_b(1u);
    case_binary_sensor_line_a(1u); case_binary_sensor_delay();
    uint32_t sampled=case_binary_sensor_sample();
    case_binary_sensor_line_a(0u); case_binary_sensor_delay();
    return sampled!=0u;
}
