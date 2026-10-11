/* SPDX-License-Identifier: MIT
 * Isolated 0xee USB-present return and USB-absent prefix through first child.
 * Behavior after the first standby child is intentionally unmodeled.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
extern uint32_t case_legacy_ee_first(uint32_t selector,uint32_t *response,uint32_t count);
static const char case_ee_usb[]="usb in, cannot enter shipmode.";
static const char case_ee_standby[]="Standby, reason: cmd.";
static const char case_ee_newline[]="\r\n";
uint32_t case_legacy_ee_prefix(const uint8_t *command,uint32_t length)
{
    (void)command;(void)length;
    const uint8_t log_flag=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    const uint8_t usb=*(volatile uint8_t *)(uintptr_t)0x2000087fu;
    if(usb!=0u) {
        if(log_flag!=0u)return log_flag;
        (void)case_legacy_logger(case_ee_usb);
        return case_legacy_logger(case_ee_newline);
    }
    if(log_flag==0u) {
        (void)case_legacy_logger(case_ee_standby);
        (void)case_legacy_logger(case_ee_newline);
    }
    uint32_t response;
    return case_legacy_ee_first(16u,&response,1u);
}
