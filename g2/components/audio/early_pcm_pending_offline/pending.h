#ifndef OPENCFW_EARLY_PCM_PENDING_H
#define OPENCFW_EARLY_PCM_PENDING_H
#include <stdint.h>
void pcm_hardware_temperature(uint32_t range);
uint32_t pcm_postpone(void);
uint32_t pcm_pending_handle(void);
uint32_t pcm_ton_initialize(void);
uint32_t pcm_ton_config_update(uint32_t gpu_on,uint32_t mode);
uint32_t pcm_lp_switch_initialize(void);
uint32_t pcm_lp_switch_enable(void);
uint32_t pcm_lp_switch_disable(void);
uint32_t pcm_early_before_enable(void);
uint32_t pcm_early_after_enable(void);
uint32_t pcm_middle_before_enable(void);
uint32_t pcm_middle_after_enable(void);
#endif
