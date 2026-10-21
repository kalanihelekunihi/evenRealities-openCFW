/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xdf dog-feed flag and conditional report.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_df_message[]="%s dog feed";
static const char case_df_enable[]="Enable";
static const char case_df_disable[]="Disable";
static const char case_df_newline[]="\r\n";
uint32_t case_legacy_df_branch(const uint8_t *command,uint32_t length)
{
    const uint8_t log_flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(length<2u)return log_flag;
    const uint8_t value=(command[1]!=0u);
    *(volatile uint8_t *)(uintptr_t)0x200000beu=value;
    if(log_flag!=0u)return log_flag;
    (void)case_legacy_logger(case_df_message,value?case_df_enable:case_df_disable);
    return case_legacy_logger(case_df_newline);
}
