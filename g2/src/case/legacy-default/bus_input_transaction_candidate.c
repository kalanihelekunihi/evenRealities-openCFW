/* SPDX-License-Identifier: MIT
 * Full stock 0x080004c0 input transaction, through timed bit sampling.
 * Per-byte sampler and acknowledgement writer remain typed bus lowers.
 */
#include <stdint.h>
extern void case_bus_prepare(void);
extern void case_bus_finish(void);
extern void case_bus_send(uint32_t value,uint32_t first);
extern void case_bus_start(uint32_t bit);
extern uint32_t case_bus_poll(uint32_t *word);
extern uint32_t case_bus_read(uint32_t byte);
extern uint32_t case_bus_byte_sample(uint8_t *output); /* 0x0800b5d6 */
extern void case_bus_response_bit(uint32_t bit);       /* 0x0800a176 */
uint32_t case_bus_input_transaction(uint32_t command,uint32_t index,
                                    uint32_t count,void *output)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    uint8_t *out=(uint8_t *)output;
    diagnostics[2]=0u;
    if((command&0x40u)==0u){diagnostics[2]=0x29u;return 0u;}
    case_bus_prepare();case_bus_finish();
    uint32_t address=((command&~0x0fu)+index)&0xffu;
    case_bus_send(address,1u);case_bus_start(1u);
    uint32_t received=0u;
    if(case_bus_poll(&received)==0u){case_bus_finish();diagnostics[2]=0x2au;return 0u;}
    if(case_bus_read((address*2u+1u)&0xffu)!=received){case_bus_finish();diagnostics[2]=0x2bu;return 0u;}
    for(uint32_t i=0;i<count;++i){
        if(case_bus_byte_sample(out+i)==0u){case_bus_finish();diagnostics[2]=0x2cu;return 0u;}
        if(i!=count-1u)case_bus_response_bit(out[i]);
    }
    case_bus_finish();return 1u;
}
