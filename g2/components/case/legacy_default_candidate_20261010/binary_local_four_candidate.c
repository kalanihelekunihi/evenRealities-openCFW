/* SPDX-License-Identifier: MIT
 * Destination-2 binary 0x50/0x5c/0x5d/0x68 branches, lower calls explicit.
 */
#include <stdint.h>
extern uint32_t case_binary_local_send(const uint8_t *payload,uint32_t length);
extern uint32_t case_binary_local_ack(uint32_t opcode);
extern void case_binary_local_control_a(uint32_t value);
extern void case_binary_local_control_b(uint32_t value);
uint32_t case_binary_local_four_candidate(const uint8_t *p,uint32_t n)
{
    uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    switch(p[0]) {
    case 0x50: {
        const uint8_t reply[7]={0x50,0x01,0x03,0x03,0x01,0x02,0x39};
        return case_binary_local_send(reply,7);
    }
    case 0x5c: {
        const uint8_t reply[5]={0x5c,0x01,0x03,0x01,(uint8_t)(!*(volatile uint8_t *)(uintptr_t)0x20000880u)};
        return case_binary_local_send(reply,5);
    }
    case 0x5d:
        if(n<6) return flag;
        if(p[4]) case_binary_local_control_a(!p[5]);
        else case_binary_local_control_b(!p[5]);
        return case_binary_local_ack(0x5d);
    case 0x68:
        if(n<5) return flag;
        *(volatile uint8_t *)(uintptr_t)0x200000bfu=(uint8_t)(p[4]!=0);
        return case_binary_local_ack(0x68);
    default:return flag;
    }
}
