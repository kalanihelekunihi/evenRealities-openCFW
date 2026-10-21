/* SPDX-License-Identifier: MIT
 * Isolated stock destination-2 opcode 0x5e branch.
 */
#include <stdint.h>
extern uint32_t case_binary_5e_apply(const uint8_t *sixteen);
extern void case_binary_5e_ack(uint32_t opcode);
extern void case_binary_5e_send(const uint8_t *payload, uint32_t length);
extern uint32_t case_binary_5e_logger(const char *format);
extern uint32_t case_binary_5e_hex(const uint8_t *sixteen, uint32_t length);
uint32_t case_binary_5e_candidate(const uint8_t *command, uint32_t logical_length)
{
    uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (logical_length<20) {
        if (flag) return flag;
        return case_binary_5e_logger("SN Even length wrong.");
    }
    if (case_binary_5e_apply(command+4)) {
        case_binary_5e_ack(0x5e);
        if (*(volatile uint8_t *)(uintptr_t)0x200000bfu==0)
            case_binary_5e_logger("Set SN Even done:");
    } else {
        static const uint8_t fail[5]={0x5e,0x01,0x03,0x01,0x01};
        case_binary_5e_send(fail,5);
        if (*(volatile uint8_t *)(uintptr_t)0x200000bfu==0)
            case_binary_5e_logger("Set SN Even fail:");
    }
    return case_binary_5e_hex(command+4,16);
}
