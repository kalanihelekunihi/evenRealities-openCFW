/* Fixed-address reconstruction interfaces. See README.md for integration limits. */
#ifndef OPENCFW_BOOT_IDLE_SLEEP_H
#define OPENCFW_BOOT_IDLE_SLEEP_H
#include <stdint.h>
uint32_t expected_idle_ticks(void),confirm_sleep(void);
void idle_entry(void),step_ticks(uint32_t ticks),tickless_sleep(uint32_t ticks);
uint32_t counter_read(void),timer_compare(uint32_t channel,uint32_t counter_delta);
void sample_three(uintptr_t address,uint32_t out[3]);
uint32_t irq_save(void),stimer_interrupt_clear(uint32_t bits);
void irq_clear(uint32_t irq);
uint32_t pre_sleep(uint32_t ticks),deep_sleep(uint32_t deep);
void post_sleep(uint32_t ticks),cp_get(uint8_t out[3]);
uint32_t cp_set(uint32_t config),lp_enable(void),lp_disable(void);
#endif
