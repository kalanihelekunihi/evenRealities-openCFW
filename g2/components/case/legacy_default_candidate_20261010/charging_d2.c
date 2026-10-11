/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xd2 charging toggle and optional logger report.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_d2_message[]="%s one side charging";
static const char case_d2_enable[]="Enable";
static const char case_d2_disable[]="Disable";
static const char case_d2_newline[]="\r\n";
uint32_t case_legacy_d2_branch(const uint8_t *command,uint32_t length)
{
    const uint8_t log_flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(length<2u)return log_flag;
    const uint8_t value=(command[1]!=0u);
    *(volatile uint8_t *)(uintptr_t)0x20000105u=value;
    if(log_flag!=0u)return log_flag;
    (void)case_legacy_logger(case_d2_message,value?case_d2_disable:case_d2_enable);
    return case_legacy_logger(case_d2_newline);
}
