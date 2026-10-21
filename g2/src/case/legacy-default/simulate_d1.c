/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xd1 simulated battery flags.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_d1_message[]="simu_full_bat:%d, simu_empty_bat:%d, simu_timeout:%d";
static const char case_d1_newline[]="\r\n";
uint32_t case_legacy_d1_branch(const uint8_t *command,uint32_t length)
{
    const uint8_t log_flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(length<4u)return log_flag;
    const uint32_t full=(command[1]!=0u);
    const uint32_t empty=(command[2]!=0u);
    const uint32_t timeout=(command[3]!=0u);
    *(volatile uint8_t *)(uintptr_t)0x200000c1u=(uint8_t)full;
    *(volatile uint8_t *)(uintptr_t)0x200000c2u=(uint8_t)empty;
    *(volatile uint8_t *)(uintptr_t)0x200000c3u=(uint8_t)timeout;
    if(log_flag!=0u)return log_flag;
    (void)case_legacy_logger(case_d1_message,full,empty,timeout);
    return case_legacy_logger(case_d1_newline);
}
