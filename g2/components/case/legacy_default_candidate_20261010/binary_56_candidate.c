/* SPDX-License-Identifier: MIT
 * Isolated stock destination-2 opcode 0x56 branch.
 */
#include <stdint.h>
extern uint32_t case_binary_56_logger(const char *format);
extern uint32_t case_binary_56_exit(void);
extern uint32_t case_binary_56_ack(uint32_t opcode);
uint32_t case_binary_56_candidate(const uint8_t *command, uint32_t logical_length)
{
    uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (logical_length<6) return flag;
    if (command[4]) {
        if (flag==0) {
            case_binary_56_logger("Exit GLS_OTA Status");
            case_binary_56_logger("\r\n");
        }
        *(volatile uint8_t *)(uintptr_t)0x20000895u=0;
        case_binary_56_exit();
        return case_binary_56_ack(0x56);
    }
    uint32_t side=command[5] ? 2u : 1u;
    if (flag==0) {
        case_binary_56_logger(command[5] ? "Enter GLS_OTA Status, R" : "Enter GLS_OTA Status, L");
        case_binary_56_logger("\r\n");
    }
    *(volatile uint8_t *)(uintptr_t)0x20000895u=(uint8_t)side;
    *(volatile uint8_t *)(uintptr_t)0x20000896u=0;
    return side;
}
