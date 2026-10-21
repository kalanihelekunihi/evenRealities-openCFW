/* SPDX-License-Identifier: MIT
 * Native 0xee branch including the full USB-absent standby call chain.
 * Peripheral effects remain explicit lower contracts.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
extern uint32_t case_legacy_ee_first(uint32_t selector,uint32_t *response,uint32_t count);
extern uint32_t case_legacy_watchdog_set(uint32_t enabled);
extern uint32_t case_legacy_ee_power_stop(uint32_t mode); /* 0x08002c30 */
extern uint32_t case_legacy_ee_wake_prepare(uint32_t mode); /* 0x08005094 */
extern uint32_t case_legacy_ee_wake_enable(uint32_t mask); /* 0x080050a8 */
extern uint32_t case_legacy_ee_enter_standby(void); /* 0x080050c4 */
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
    (void)case_legacy_ee_first(16u,&response,1u);
    (void)case_legacy_ee_first(17u,&response,1u);
    (void)case_legacy_watchdog_set(0u);
    (void)case_legacy_ee_power_stop(0u);
    (void)case_legacy_ee_wake_prepare(43u);
    (void)case_legacy_ee_wake_enable(0x2020u);
    *(volatile uint32_t *)(uintptr_t)0x40007018u=0x1003fu;
    return case_legacy_ee_enter_standby();
}
