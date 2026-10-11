/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xd0 watchdog mode request/report.
 */
#include <stdint.h>
extern uint32_t case_legacy_watchdog_set(uint32_t enabled);
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_d0_message[]="%s watchdog 4005";
static const char case_d0_enable[]="Enable";
static const char case_d0_disable[]="Disable";
static const char case_d0_newline[]="\r\n";
uint32_t case_legacy_d0_branch(const uint8_t *command,uint32_t length)
{
    const volatile uint8_t *const flag=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(length<2u)return *flag;
    const uint8_t value=(command[1]!=0u);
    (void)case_legacy_watchdog_set(value);
    const uint8_t current=*flag;
    if(current!=0u)return current;
    (void)case_legacy_logger(case_d0_message,value?case_d0_enable:case_d0_disable);
    return case_legacy_logger(case_d0_newline);
}
