#include "case_logger_contract.h"
/* SPDX-License-Identifier: MIT
 * Native CASE shared formatter 0x9170, idle setter 0xd154 and LED GPIO.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern uint32_t case_binary_3f_enable(void); /* 0xd154 */
/* case_policy_log (same variadic entry 0x9170) is an alias of g2_log_printf
 * in case/glue/log_wrapper_provider.c. */
uint32_t case_policy_log_number(uint32_t format,uint32_t value)
{return case_legacy_logger((const char *)(uintptr_t)format,value);}
uint32_t case_policy_log_four(uint32_t format,uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{return case_legacy_logger((const char *)(uintptr_t)format,a,b,c,d);}
uint32_t case_record_log(uint32_t format,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f)
{return case_legacy_logger((const char *)(uintptr_t)format,a,b,c,d,e,f);}
/* Dedup (0x0800d154): case_policy_service_idle is an alias of case_binary_3f_enable (legacy-default/binary_3f_enable_candidate.c). */
extern uint32_t case_policy_service_idle(void);
/* Dedup (0x08006b80): case_policy_led_left_clear is an alias of case_control_a (glue/control_providers.c). */
extern void case_policy_led_left_clear(uint32_t enabled);
/* Dedup (0x08006b98): case_policy_led_right_clear is an alias of case_control_b (glue/control_providers.c). */
extern void case_policy_led_right_clear(uint32_t enabled);
