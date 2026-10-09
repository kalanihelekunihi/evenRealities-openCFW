/* Offline stock buck and registered-callback interfaces. */
#ifndef OPENCFW_EARLY_PCM_DISPATCH_H
#define OPENCFW_EARLY_PCM_DISPATCH_H
#include <stdint.h>
void pcm_buck_control(uint32_t enable);
uint32_t pcm_before_enable_dispatch(void);
uint32_t pcm_after_enable_dispatch(void);
uint32_t pcm_tempco_suspend_dispatch(void);
uint32_t pcm_lp_switch_initialize_dispatch(void);
uint32_t pcm_ton_dispatch(uint32_t gpu_on,uint32_t gpu_mode);
#endif
