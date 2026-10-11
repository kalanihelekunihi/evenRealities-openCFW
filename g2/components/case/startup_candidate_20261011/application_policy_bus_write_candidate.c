/* SPDX-License-Identifier: MIT
 * Native CASE 0x0610 guarded configuration bus write transaction.
 */
#include <stdint.h>
extern void case_bus_prepare(void); /* 0xa310 */
extern void case_bus_finish(void); /* 0xa24a */
extern void case_bus_send(uint32_t byte,uint32_t first); /* 0xa2c4 */
extern void case_bus_start(uint32_t bit); /* 0xa19a */
extern uint32_t case_bus_poll(uint32_t *word); /* 0xc43c */
extern uint32_t case_bus_read(uint32_t byte); /* 0xc412 */
uint32_t case_policy_bus_write(uint32_t bus,uint32_t channel,uint32_t count,const uint8_t *value)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    diagnostics[2]=0u;
    if((bus&0x40u)==0u){diagnostics[2]=21u;return 0u;}
    uint32_t address=((bus&~15u)+channel)&0xffu;
    case_bus_prepare();case_bus_finish();
    case_bus_send(address,1u);case_bus_start(0u);
    uint32_t sample=0u;
    if(case_bus_poll(&sample)==0u){case_bus_finish();diagnostics[2]=22u;return 0u;}
    if(case_bus_read((address<<1u)&0xffu)!=sample){case_bus_finish();diagnostics[2]=23u;return 0u;}
    for(uint32_t i=0u;(int32_t)i<(int32_t)count;++i){
        uint32_t byte=value[i];
        case_bus_send(byte,0u);
        if(case_bus_poll(&sample)==0u){case_bus_finish();diagnostics[2]=24u;return 0u;}
        if(case_bus_read(byte)!=sample){case_bus_finish();diagnostics[2]=25u;return 0u;}
    }
    case_bus_finish();return 1u;
}
