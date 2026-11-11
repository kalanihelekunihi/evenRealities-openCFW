/* Fixed-address reconstruction interfaces. See README.md for integration limits. */
#ifndef OPENCFW_BOOT_IDLE_SLEEP_H
#define OPENCFW_BOOT_IDLE_SLEEP_H
#include <stdint.h>
uint32_t expected_idle_ticks(void),confirm_sleep(void);
void idle_entry(void),step_ticks(uint32_t ticks),tickless_sleep(uint32_t ticks);
/* STIMER counter/compare: port-timer/port_timer.h; IRQ disable: am_hal_interrupt_master_disable. */
uint32_t stimer_interrupt_clear(uint32_t bits);
void irq_clear(uint32_t irq);
uint32_t pre_sleep(uint32_t ticks),deep_sleep(uint32_t deep);
void post_sleep(uint32_t ticks);
#endif
