/* Reconstructed interfaces: scheduler ticks versus raw STIMER counts. */
#ifndef OPENCFW_IDLE_CHAIN_H
#define OPENCFW_IDLE_CHAIN_H
#include <stdint.h>
#define OPENCFW_STIMER_BAD_CHANNEL 5u
#define OPENCFW_STIMER_DELTA_TOO_SMALL 0x08000000u
/* Jump must not pass next-unblock. Equality needs suspended scheduler and jump>0. */
void step_ticks(uint32_t scheduler_ticks);
/* Three masked reads of STTMR; first pair equal -> second, otherwise third. */
uint32_t counter_read(void);
/* Channel 0..7; raw counter-count delta, not an absolute deadline. May poll. */
uint32_t timer_compare(uint32_t channel,uint32_t counter_delta);
/* W1C register write followed by status read; does not enable the timer. */
uint32_t stimer_interrupt_clear(uint32_t bits);
void irq_clear(uint32_t irq_number);
/* Calls deeper sleep routine with argument1 and returns0; no physical wake proof. */
uint32_t pre_sleep(uint32_t expected_scheduler_ticks);
void post_sleep(uint32_t expected_scheduler_ticks);
void tickless_sleep(uint32_t expected_scheduler_ticks);
void idle_entry(void);
#endif
