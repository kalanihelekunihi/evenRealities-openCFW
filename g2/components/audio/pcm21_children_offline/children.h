#ifndef OPENCFW_PCM21_CHILDREN_H
#define OPENCFW_PCM21_CHILDREN_H
#include "../pcm21_control_offline/control.h"
void pcm21_prepare(struct pcm21_power_request *);
void pcm21_change_state(uint32_t next,uint32_t old);
uint32_t pcm21_plan(struct pcm21_power_request *,uint32_t *profile,uint32_t *ton);
void pcm21_apply(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
#endif
