// SPDX-License-Identifier: MIT
// Reconstructed package 0x47578..0x4766c. Field names describe observed use;
// precise DRC algorithm semantics remain under reconstruction.
#include <stdint.h>
#include <stddef.h>
struct drc_stage3 {
    float threshold, ratio, parameter2, time0, time1;
    uint32_t control, sample_rate;
    float history0, history1, attack_coefficient, release_coefficient;
    int32_t duration_samples;
    float history2, history3, history4;
    uint8_t initialized;
    uint8_t padding[3];
};
_Static_assert(sizeof(struct drc_stage3)==64, "stock stage size");
_Static_assert(offsetof(struct drc_stage3, initialized)==60, "stock flag offset");
extern void *open_cfw_gx8002_memset(void *, int, unsigned);
extern float drc_logf(float);
extern float drc_expf(float);
struct drc_stage3 *open_cfw_gx8002_drc_stage3_initialize(
    struct drc_stage3 *memory, float threshold, float ratio,
    float parameter2, float time0, float time1, float control_bits, float sample_rate)
{
    union { float f; uint32_t u; } control = { .f = control_bits };
    // Stock clears before checking the returned storage address.
    open_cfw_gx8002_memset(memory, 0, 64);
    volatile struct drc_stage3 *s=memory;
    if (s) {
        s->threshold=threshold;
        s->initialized=0;
        s->time0=time0;
        s->ratio=ratio;
        s->parameter2=parameter2;
        s->sample_rate=(uint32_t)sample_rate;
        s->time1=time1;
        s->control=control.u;
        float logarithm=drc_logf(9.0f);
        float product=(float)s->sample_rate*s->time0;
        s->attack_coefficient=drc_expf(-logarithm/product);
        logarithm=drc_logf(9.0f);
        product=(float)s->sample_rate*s->time1;
        s->release_coefficient=drc_expf(-logarithm/product);
        union { uint32_t u; float f; } duration = { .u = s->control };
        float scaled_duration=(float)s->sample_rate*duration.f;
        s->duration_samples=(int32_t)scaled_duration;
        if (!s->initialized) {
            s->history0=0;
            s->history1=0;
            s->history2=0;
            s->history3=0;
            s->history4=0;
        }
        s->initialized=1;
    }
    return memory;
}
