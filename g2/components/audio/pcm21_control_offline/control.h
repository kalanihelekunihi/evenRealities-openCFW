#ifndef OPENCFW_PCM21_CONTROL_OFFLINE_H
#define OPENCFW_PCM21_CONTROL_OFFLINE_H
#include <stdint.h>
struct pcm21_power_request { uint32_t masks[4]; uint8_t range,cpu,gpu; };
uint32_t pcm21_control(uint32_t action,uint32_t enable,uint8_t *metadata);
#endif
