/* SPDX-License-Identifier: MIT
 * Isolated stock opcode 0x14, destination-2 branch.
 */
#include <stdint.h>
extern uint32_t case_binary_14_read_a(uint32_t *out);
extern uint32_t case_binary_14_scale(uint32_t value, uint32_t radix);
extern void case_binary_14_read_b(uint32_t *out);
extern uint32_t case_binary_14_read_c(uint32_t *out);
extern uint32_t case_binary_14_send(const uint8_t *payload, uint32_t length);
uint32_t case_binary_14_candidate(const uint8_t *command, uint32_t logical_length)
{
    (void)command;
    (void)logical_length;
    uint32_t a=0,b=0,c=0;
    (void)case_binary_14_read_a(&a);
    a=case_binary_14_scale(a,10);
    case_binary_14_read_b(&b);
    (void)case_binary_14_read_c(&c);
    uint8_t reply[11]={0x14,0x01,0x03,0x07,0,0,0,0,0,0,0};
    reply[4]=*(volatile uint8_t *)(uintptr_t)0x2000087du;
    reply[5]=(uint8_t)((int32_t)b<0);
    uint32_t magnitude=(int32_t)b<0 ? 0u-b : b;
    reply[6]=(uint8_t)magnitude;
    reply[7]=(uint8_t)(magnitude>>8);
    reply[8]=(uint8_t)a;
    reply[9]=(uint8_t)c;
    reply[10]=(uint8_t)(c>>8);
    return case_binary_14_send(reply,11);
}
