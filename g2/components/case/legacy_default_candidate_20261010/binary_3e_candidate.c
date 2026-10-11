/* SPDX-License-Identifier: MIT
 * Isolated stock destination-2 opcode 0x3e branch.
 */
#include <stdint.h>
extern uint32_t case_binary_3e_control(uint32_t object, uint32_t mask);
extern uint32_t case_binary_3e_logger(const char *format);
extern uint32_t case_binary_3e_ack(uint32_t opcode);
uint32_t case_binary_3e_candidate(const uint8_t *command, uint32_t logical_length)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x200000f4u;
    uint32_t old=*state;
    if (logical_length < 5) return *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t incoming=command[4];
    if (old != incoming) {
        uint32_t next=(incoming != 0);
        *state=(uint8_t)next;
        *(volatile uint32_t *)(uintptr_t)0x200000fcu=0;
        if (next==0 && *(volatile uint8_t *)(uintptr_t)0x200000f5u != 0) {
            case_binary_3e_control(*(volatile uint32_t *)(uintptr_t)0x200000f0u,128);
            if (*(volatile uint8_t *)(uintptr_t)0x200000bfu==0) {
                case_binary_3e_logger("[AGING_NOT]: exit aging status(0x3E).");
                case_binary_3e_logger("\r\n");
            }
        }
    }
    return case_binary_3e_ack(0x3e);
}
