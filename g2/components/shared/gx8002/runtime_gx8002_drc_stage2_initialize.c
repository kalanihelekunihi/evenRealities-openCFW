// SPDX-License-Identifier: MIT
// Reconstructed package 0x47494..0x4756c. Field names describe observed use;
// precise DRC algorithm semantics remain under reconstruction.
#include <stdint.h>
#include <stddef.h>
struct drc_stage2 {
    float threshold, ratio, parameter2, time0, time1;
    uint32_t control, sample_rate;
    float history0, history1, attack_coefficient, release_coefficient, history2;
    uint8_t initialized;
    uint8_t padding[3];
};
_Static_assert(sizeof(struct drc_stage2)==52, "stock stage size");
_Static_assert(offsetof(struct drc_stage2, initialized)==48, "stock flag offset");
extern void *open_cfw_gx8002_memset(void *, int, unsigned);
extern float drc_logf(float);
extern float drc_expf(float);
struct drc_stage2 *open_cfw_gx8002_drc_stage2_initialize(
    struct drc_stage2 *memory, float threshold, float ratio,
    float parameter2, float time0, float time1, float control_bits, float sample_rate)
{
    union { float f; uint32_t u; } control = { .f = control_bits };
    // Stock clears before checking the returned storage address.
    open_cfw_gx8002_memset(memory, 0, 52);
    volatile struct drc_stage2 *s=memory;
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
        if (!s->initialized) {
            s->history0=0;
            s->history1=0;
            s->history2=0;
        }
        s->initialized=1;
    }
    return memory;
}
