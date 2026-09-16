// SPDX-License-Identifier: MIT
// Package 0x476bc..0x477a4: fourth DRC state constructor.
#include <stdint.h>
struct drc_stage4 {
    float threshold, attack, release, duration, reserved0, sample_rate;
    float duration_samples, gain, attack_coefficient, release_coefficient;
    uint32_t reserved[6];
};
_Static_assert(sizeof(struct drc_stage4)==64, "stock state size");
extern void *open_cfw_gx8002_memset(void *, int, unsigned);
extern float drc_logf(float);
extern float open_cfw_gx8002_powf(float, float);
extern double open_cfw_gx8002_backup_exp(double);
struct drc_stage4 *open_cfw_gx8002_drc_stage4_initialize(
    struct drc_stage4 *memory, float threshold, float attack,
    float release, float duration, float sample_rate)
{
    open_cfw_gx8002_memset(memory,0,64);
    volatile struct drc_stage4 *s=memory;
    if (s) {
        s->attack=attack;
        s->duration=duration;
        float duration_samples=duration*sample_rate;
        s->release=release;
        s->threshold=threshold;
        s->sample_rate=sample_rate;
        s->duration_samples=duration_samples;
        s->gain=open_cfw_gx8002_powf(10.0f,threshold/20.0f);
        float logarithm=drc_logf(9.0f);
        float product=s->sample_rate*s->attack;
        float exponent=-logarithm/product;
        s->attack_coefficient=(float)open_cfw_gx8002_backup_exp((double)exponent);
        logarithm=drc_logf(9.0f);
        product=s->sample_rate*s->release;
        exponent=-logarithm/product;
        s->release_coefficient=(float)open_cfw_gx8002_backup_exp((double)exponent);
    }
    return memory;
}
