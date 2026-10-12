/* Numeric path of native GSC energy gain loop 0x1000cd50..0x1000cdae.
 * Native 0x1000cdc0..0x1000cddc additionally prints a diagnostic when the
 * previous baseline is negative. That side effect requires the separately
 * authenticated 0x10011af4 conversion and is intentionally outside this
 * source slice; this is not the full 0x1000cc70 provider.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_gain_word;

void gx8002_image_b_energy_gain_numeric_verified_chunk(
    const uint32_t *ctx, int16_t *complex_samples, int32_t frame_index)
{
    int32_t frames=(int32_t)ctx[0x18/4];
    uint32_t offset=(uint32_t)frame_index*(uint32_t)frames*4u;
    const uint32_t *energy=(const uint32_t *)(uintptr_t)(ctx[0xa0/4]+offset);
    const uint32_t *scaled=(const uint32_t *)(uintptr_t)(ctx[0x98/4]+offset);
    uint32_t *baseline=(uint32_t *)(uintptr_t)(ctx[0x9c/4]+offset);
    const gx8002_gain_word additive={.u=UINT32_C(0x467ffc00)};
    const gx8002_gain_word multiplier={.u=UINT32_C(0x46fffe00)};
    for (int32_t i=0;i<frames;++i) {
        int32_t old=(int32_t)baseline[i];
        uint32_t old_product=(uint32_t)old*116u;
        float drift=(float)(int32_t)old_product;
        int32_t divisor=(int32_t)(scaled[i]+1u);
        int32_t quotient=(int32_t)energy[i]/divisor;
        baseline[i]=(uint32_t)quotient;
        int32_t excess=(int32_t)((uint32_t)quotient-127u);
        if (excess<0) excess=0;
        uint32_t tenfold=(uint32_t)excess*10u;
        float numerator=(float)(int32_t)tenfold+drift;
        float denominator=numerator+additive.f;
        float weighted=(numerator/denominator)*multiplier.f;
        int32_t gain=(int32_t)weighted;
        if (gain<9830) gain=9830;
        uint32_t real_product=(uint32_t)(int32_t)complex_samples[2*i]
                              *(uint32_t)gain;
        uint32_t imag_product=(uint32_t)(int32_t)complex_samples[2*i+1]
                              *(uint32_t)gain;
        complex_samples[2*i]=(int16_t)((int32_t)real_product>>15);
        complex_samples[2*i+1]=(int16_t)((int32_t)imag_product>>15);
    }
}
