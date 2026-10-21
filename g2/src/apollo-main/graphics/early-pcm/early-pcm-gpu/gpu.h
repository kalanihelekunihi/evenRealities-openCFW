#ifndef OPENCFW_EARLY_PCM_GPU_H
#define OPENCFW_EARLY_PCM_GPU_H
#include <stdint.h>
void pcm_early_switch(uint32_t enable);
uint32_t pcm_early_on(uint32_t state);
uint32_t pcm_early_off(void);
void pcm_temperature_publish(uint32_t range);
uint32_t pcm_temperature(uint32_t metadata[3]);
void pcm_sleep(uint32_t state);
uint32_t pcm_middle_on(uint32_t state);
uint32_t pcm_middle_off(void);
#endif
