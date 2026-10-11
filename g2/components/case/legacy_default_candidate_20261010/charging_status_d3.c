/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xd3 report of one-side charging state.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_d3_message[]="One-side charging: %s";
static const char case_d3_enabled[]="enabled";
static const char case_d3_disabled[]="disabled";
static const char case_d3_newline[]="\r\n";
uint32_t case_legacy_d3_branch(const uint8_t *command,uint32_t length)
{
    (void)command;(void)length;
    const uint8_t log_flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(log_flag!=0u)return log_flag;
    const uint8_t disabled=*(volatile uint8_t *)(uintptr_t)0x20000105u;
    (void)case_legacy_logger(case_d3_message,disabled?case_d3_disabled:case_d3_enabled);
    return case_legacy_logger(case_d3_newline);
}
