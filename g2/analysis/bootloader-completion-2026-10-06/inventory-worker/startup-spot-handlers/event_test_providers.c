/* SPDX-License-Identifier: BSD-3-Clause
 * Delay math and critical-save are linked native sources; only resident ROM
 * cycle burning is intercepted. This fixture does not model real hardware.
 */
#include <stdint.h>

volatile uint32_t event_test_event_count;
volatile uint32_t event_test_event_log[64];
static void log_event(uint32_t kind,uint32_t arg)
{uint32_t n=event_test_event_count++;event_test_event_log[n*2U]=kind;event_test_event_log[n*2U+1U]=arg;}
void event_child_delay(uint32_t usec)
{extern void opencfw_boot_delay_us_math(uint32_t);log_event(3U,usec);opencfw_boot_delay_us_math(usec);}
