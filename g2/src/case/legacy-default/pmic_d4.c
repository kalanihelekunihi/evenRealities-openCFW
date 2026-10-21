/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xd4 PMIC command and optional report.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
extern uint32_t case_legacy_pmic_set(uint32_t selector,uint32_t value);
static const char case_d4_message[]="Set PMIC chip id to 0x08";
static const char case_d4_newline[]="\r\n";
uint32_t case_legacy_d4_branch(const uint8_t *command,uint32_t length)
{
    (void)command;(void)length;
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u) {
        (void)case_legacy_logger(case_d4_message);
        (void)case_legacy_logger(case_d4_newline);
    }
    return case_legacy_pmic_set(20u,8u);
}
