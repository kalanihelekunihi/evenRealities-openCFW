#ifndef OPENCFW_PCM21_COMPLETION_H
#define OPENCFW_PCM21_COMPLETION_H
#include <stdint.h>
void pcm21_ton(uint32_t selector,uint32_t profile);
void pcm21_timer_publish(uint32_t boost_memory);
void pcm21_boost_remove(uint32_t remove_core);
void pcm21_buck_complete(void);
void pcm21_timer_isr(void);
/* Lifecycle callbacks return stock status codes. */
uint32_t pcm21_before_override(void);
uint32_t pcm21_before_enable(void);
uint32_t pcm21_after_enable(void);
uint32_t pcm21_initialize(void);
#endif
