#ifndef OPENCFW_STARTUP_TON_HOOKS_H
#define OPENCFW_STARTUP_TON_HOOKS_H
#include <stdint.h>
uint32_t opencfw_boot_ton_trim_cache(void);
uint32_t opencfw_boot_ton_trim_apply(uint32_t,uint32_t);
void opencfw_boot_ton_clock_gate(uint32_t);
uint32_t opencfw_boot_ton_lowpower_begin(uint32_t);
uint32_t opencfw_boot_ton_lowpower_end(void);
uint32_t opencfw_boot_ton_state_event(uint32_t,uint32_t,void *);
#endif
