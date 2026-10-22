/* SPDX-License-Identifier: MIT
 * Isolated stock value readers 0x08009ff0 and 0x0800a01e.
 * The underlying sensor/register read functions remain explicit lowers.
 */
#include <stdint.h>
extern uint32_t case_binary_read_byte_lower(uint32_t code,uint8_t *value);
extern uint32_t case_binary_read_word_lower(uint32_t code,uint32_t *value);
/* Stock 0x08009FF0 (sensor_default_value_read) */
uint32_t case_binary_14_read_a(uint32_t *out)
{
    uint8_t value=0;
    if(case_binary_read_byte_lower(6,&value)!=0) return 0xffffffffu;
    *out=(uint32_t)value*5u-400u;
    return 0;
}
/* Stock 0x0800A01E (scaled_sensor_value_read) */
uint32_t case_binary_14_read_c(uint32_t *out)
{
    uint32_t value=0;
    if(case_binary_read_word_lower(2,&value)!=0) return 0xffffffffu;
    *out=(value*5u)>>4;
    return 0;
}
