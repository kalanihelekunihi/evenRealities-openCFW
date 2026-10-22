/* SPDX-License-Identifier: MIT
 * CASE 0x0800085c received-frame dispatch. Native buffer/count addresses and
 * branch arithmetic are retained; command bodies live in the command graph.
 */
#include <stdint.h>

extern uint32_t case_legacy_command_candidate(const uint8_t *,uint32_t); /* 0x0928 */
extern uint32_t case_binary_command_candidate(const uint8_t *,uint32_t,uint32_t); /* 0x0e1c */
/* Stock 0x08009B94 (case_hex_value) */
uint32_t case_boot_hex_digit(uint32_t value) /* 0x9b94 */
{
    if(value-0x30u<10u)return (uint8_t)(value-0x30u);
    if(value-0x61u<6u)return (uint8_t)(value-0x57u);
    if(value-0x41u<6u)return (uint8_t)(value-0x37u);
    return 0u;
}

#define COUNT (*(volatile uint16_t *)(uintptr_t)0x2000010au)
#define FRAME ((uint8_t *)(uintptr_t)0x20000974u)
#define RETRY (*(volatile uint8_t *)(uintptr_t)0x20000893u)

/* Stock 0x0800085C (gls_rx_buffer_parse_dispatch) */
void case_boot_transport_event_085c(void)
{
    uint32_t n=COUNT;
    if(n<2u)return;
    if(RETRY<30u)RETRY=0u;
    uint8_t *frame=FRAME;
    if(frame[0]==0xdeu){(void)case_legacy_command_candidate(frame+1u,(uint16_t)(n-1u));return;}
    if(case_boot_hex_digit(frame[0])==13u && case_boot_hex_digit(frame[1])==14u){
        for(uint16_t k=1u;k<(COUNT>>1);k++)
            frame[k]=(uint8_t)((case_boot_hex_digit(frame[2u*k])<<4)|case_boot_hex_digit(frame[2u*k+1u]));
        (void)case_legacy_command_candidate(frame+1u,(uint16_t)((COUNT>>1)-1u));
        return;
    }
    n=COUNT;
    if(n<5u || frame[0]!=0x5au || frame[1]!=0xa5u)return;
    if(frame[2]==0x7fu){
        if(frame[3]!=n-5u)return;
        (void)case_binary_command_candidate(frame+4u,(uint16_t)(n-4u),0u);
        return;
    }
    if(frame[2]==0xcfu){
        int32_t body=(int32_t)n-6;
        if(frame[3]!=(uint8_t)body || (int32_t)frame[4]!=(body>>8))return;
        (void)case_binary_command_candidate(frame+5u,(uint16_t)(n-5u),1u);
    }
}
