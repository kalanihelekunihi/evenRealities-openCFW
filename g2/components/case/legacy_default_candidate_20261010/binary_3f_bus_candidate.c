/* SPDX-License-Identifier: MIT
 * Full stock 0x08000610 output transaction control and diagnostics.
 * Serial transport and device response are typed external contracts.
 */
#include <stdint.h>
extern void case_bus_prepare(void);             /* 0x0800a310 */
extern void case_bus_finish(void);              /* 0x0800a24a */
extern void case_bus_send(uint32_t byte,uint32_t first); /* 0x0800a2c4 */
extern void case_bus_start(uint32_t mode);      /* 0x0800a19a */
extern uint32_t case_bus_poll(uint32_t *word);  /* 0x0800c43c */
extern uint32_t case_bus_read(uint32_t value);  /* 0x0800c412 */
uint32_t case_binary_3f_bus(uint32_t command,uint32_t index,uint32_t count,
                            const uint8_t *value)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    diagnostics[2]=0u;
    if((command&0x40u)==0u){diagnostics[2]=0x15u;return 0u;}
    uint32_t address=((command&~0x0fu)+index)&0xffu;
    uint32_t received=count;
    case_bus_prepare();case_bus_finish();case_bus_send(address,1u);case_bus_start(0u);
    if(case_bus_poll(&received)==0u){case_bus_finish();diagnostics[2]=0x16u;return 0u;}
    if(case_bus_read((address&0x7fu)<<1)!=received){case_bus_finish();diagnostics[2]=0x17u;return 0u;}
    for(uint32_t i=0;i<count;++i){
        uint32_t byte=value[i];
        case_bus_send(byte,0u);
        if(case_bus_poll(&received)==0u){case_bus_finish();diagnostics[2]=0x18u;return 0u;}
        if(case_bus_read(byte)!=received){case_bus_finish();diagnostics[2]=0x19u;return 0u;}
    }
    case_bus_finish();return 1u;
}
