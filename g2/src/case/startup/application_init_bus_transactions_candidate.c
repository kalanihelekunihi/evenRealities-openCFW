/* SPDX-License-Identifier: MIT
 * Native CASE 0x0310 config input and 0x0420 motion input transaction paths.
 */
#include <stdint.h>
extern void case_bus_prepare(void);                  /* 0xa310 */
extern void case_bus_finish(void);                   /* 0xa24a */
extern void case_bus_send(uint32_t byte,uint32_t first); /* 0xa2c4 */
extern void case_bus_start(uint32_t bit);           /* 0xa19a */
extern uint32_t case_bus_poll(uint32_t *word);      /* 0xc43c */
extern uint32_t case_bus_read(uint32_t byte);       /* 0xc412 */
extern uint32_t case_bus_byte_sample(uint8_t *out); /* 0xb5d6 */
extern void case_bus_response_bit(uint32_t byte);   /* 0xa176 */
extern void case_bus_output_finish(void);           /* 0xa224 */
extern void case_bus_output_send(uint32_t byte,uint32_t first); /* 0xa2a2 */
extern void case_bus_output_start(uint32_t bit);    /* 0xa188 */
extern uint32_t case_bus_output_poll(uint32_t *word); /* 0xc42c */
extern uint32_t case_bus_output_parity(uint32_t byte); /* 0xc3f8 */
extern uint32_t case_bus_output_byte_sample(uint8_t *out); /* 0xb5ac */
extern void case_bus_output_response_bit(uint32_t byte); /* 0xa164 */
/* Stock 0x08000310 (case_wire_exchange_register) */
uint32_t case_bus_config_input_transaction(uint32_t command,uint32_t index,uint32_t count,uint8_t *out)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    diagnostics[2]=0u;
    if((command&0x40u)!=0u){diagnostics[2]=0x1fu;return 0u;}
    case_bus_prepare();case_bus_finish();
    case_bus_send(command,1u);case_bus_start(0u);
    uint32_t word=0u;
    if(case_bus_poll(&word)==0u){case_bus_finish();diagnostics[2]=0x20u;return 0u;}
    if(case_bus_read((command<<1)&0xffu)!=word){case_bus_finish();diagnostics[2]=0x21u;return 0u;}
    case_bus_send(index,0u);
    if(case_bus_poll(&word)==0u){case_bus_finish();diagnostics[2]=0x22u;return 0u;}
    if(case_bus_read(index)!=word){case_bus_finish();diagnostics[2]=0x23u;return 0u;}
    case_bus_finish();case_bus_send(command,1u);case_bus_start(1u);
    if(case_bus_poll(&word)==0u){case_bus_finish();diagnostics[2]=0x24u;return 0u;}
    if(case_bus_read((command<<1)+1u)!=word){case_bus_finish();diagnostics[2]=0x25u;return 0u;}
    for(uint32_t i=0u;i<count;++i){
        if(case_bus_byte_sample(out+i)==0u){case_bus_finish();diagnostics[2]=0x26u;return 0u;}
        if(i!=count-1u)case_bus_response_bit(out[i]);
    }
    case_bus_finish();return 1u;
}
/* Stock 0x08000420 (case_motion_input_transaction) */
uint32_t case_motion_input_transaction(uint32_t command,uint32_t index,uint32_t count,uint8_t *out)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x20000000u;
    diagnostics[1]=0u;
    if((command&0x40u)==0u){diagnostics[1]=0x29u;return 0u;}
    case_bus_output_finish();
    uint32_t address=((command&~0x0fu)+index)&0xffu;
    case_bus_output_send(address,1u);case_bus_output_start(1u);
    uint32_t word=0u;
    if(case_bus_output_poll(&word)==0u){case_bus_output_finish();diagnostics[1]=0x2au;return 0u;}
    if(case_bus_output_parity((address*2u+1u)&0xffu)!=word){case_bus_output_finish();diagnostics[1]=0x2bu;return 0u;}
    for(uint32_t i=0u;i<count;++i){
        if(case_bus_output_byte_sample(out+i)==0u){case_bus_output_finish();diagnostics[1]=0x2cu;return 0u;}
        if(i!=count-1u)case_bus_output_response_bit(out[i]);
    }
    case_bus_output_finish();return 1u;
}
