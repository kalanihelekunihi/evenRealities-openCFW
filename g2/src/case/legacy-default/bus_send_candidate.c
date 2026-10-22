/* SPDX-License-Identifier: MIT
 * Stock 0x0800a2c4 sends seven address or eight data bits, most first.
 */
#include <stdint.h>
extern void case_bus_start(uint32_t bit);
/* Stock 0x0800A2C4 (case_emit_bits_alt) */
void case_bus_send(uint32_t value,uint32_t first)
{
    uint32_t bit=first==1u?6u:7u;
    do{
        case_bus_start((value>>bit)&1u);
        --bit;
    }while((int32_t)bit>=0);
}
