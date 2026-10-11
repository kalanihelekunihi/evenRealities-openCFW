/* SPDX-License-Identifier: MIT
 * Isolated stock destination-2 opcode 0x3f output branch.
 */
#include <stdint.h>
extern uint32_t case_binary_3f_logger(const char *format, ...);
extern uint32_t case_binary_3f_enable(void);
extern uint32_t case_binary_3f_ack(uint32_t opcode);
uint32_t case_binary_3f_candidate(const uint8_t *command, uint32_t logical_length)
{
    if (logical_length<5) return *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t enabled=(command[4]!=0);
    *(volatile uint8_t *)(uintptr_t)0x20000891u=(uint8_t)enabled;
    if (*(volatile uint8_t *)(uintptr_t)0x200000bfu==0) {
        case_binary_3f_logger("%s output, reason: cmd", enabled ? "enable" : "disable");
        case_binary_3f_logger("\r\n");
    }
    if (*(volatile uint8_t *)(uintptr_t)0x20000891u != 0) {
        case_binary_3f_enable();
        *(volatile uint8_t *)(uintptr_t)0x2000088cu=0;
        *(volatile uint8_t *)(uintptr_t)0x2000088du=0;
    }
    return case_binary_3f_ack(0x3f);
}
