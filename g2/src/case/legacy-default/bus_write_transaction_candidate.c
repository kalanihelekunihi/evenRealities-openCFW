/* SPDX-License-Identifier: MIT
 * Full stock 0x0800056c alternate-bus output transaction control.
 * Timed waveform and response polling remain named physical lowers.
 */
#include <stdint.h>
extern void case_bus_output_finish(void);               /* 0x0800a224 */
extern void case_bus_output_send(uint32_t byte,uint32_t first); /* 0x0800a2a2 */
extern void case_bus_output_start(uint32_t bit);        /* 0x0800a188 */
extern uint32_t case_bus_output_poll(uint32_t *word);   /* 0x0800c42c */
extern uint32_t case_bus_read(uint32_t byte);           /* sourced parity */
/* Stock 0x0800056C (case_bus_write_transaction) */
uint32_t case_bus_write_transaction(uint32_t command,uint32_t index,
                                    uint32_t count,const uint8_t *bytes)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x20000000u;
    diagnostics[1]=0u;
    if((command&0x40u)==0u){diagnostics[1]=0x15u;return 0u;}
    uint32_t address=((command&~0x0fu)+index)&0xffu;
    uint32_t received=count;
    case_bus_output_finish();
    case_bus_output_send(address,1u);
    case_bus_output_start(0u);
    if(case_bus_output_poll(&received)==0u){case_bus_output_finish();diagnostics[1]=0x16u;return 0u;}
    if(case_bus_read((address&0x7fu)<<1)!=received){case_bus_output_finish();diagnostics[1]=0x17u;return 0u;}
    for(uint32_t i=0;i<count;++i){
        uint32_t byte=bytes[i];
        case_bus_output_send(byte,0u);
        if(case_bus_output_poll(&received)==0u){case_bus_output_finish();diagnostics[1]=0x18u;return 0u;}
        if(case_bus_read(byte)!=received){case_bus_output_finish();diagnostics[1]=0x19u;return 0u;}
    }
    case_bus_output_finish();return 1u;
}
