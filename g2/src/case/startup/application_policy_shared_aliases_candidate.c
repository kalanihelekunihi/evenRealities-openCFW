#include "case_logger_contract.h"
/* SPDX-License-Identifier: MIT
 * Native CASE shared formatter 0x9170, idle setter 0xd154 and LED GPIO.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern uint32_t case_binary_3f_enable(void); /* 0xd154 */
/* Same native variadic entry0x9170: retain registers and caller stack words. */
__attribute__((naked)) uint32_t case_policy_log(uint32_t format,...)
{
    __asm__ volatile("push {r3}\n"
                     "ldr r3, =case_legacy_logger\n"
                     "mov ip, r3\n"
                     "pop {r3}\n"
                     "bx ip\n");
}
uint32_t case_policy_log_number(uint32_t format,uint32_t value)
{return case_legacy_logger((const char *)(uintptr_t)format,value);}
uint32_t case_policy_log_four(uint32_t format,uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{return case_legacy_logger((const char *)(uintptr_t)format,a,b,c,d);}
uint32_t case_record_log(uint32_t format,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f)
{return case_legacy_logger((const char *)(uintptr_t)format,a,b,c,d,e,f);}
uint32_t case_policy_service_idle(void)
{return case_binary_3f_enable();}
static void led(uint32_t mask,uint32_t enabled)
{*(volatile uint32_t *)(uintptr_t)(0x50000000u+(enabled?24u:40u))=mask;}
void case_policy_led_left_clear(uint32_t enabled)
{led(0x40u,enabled!=0u);}
void case_policy_led_right_clear(uint32_t enabled)
{led(0x80u,enabled!=0u);}
