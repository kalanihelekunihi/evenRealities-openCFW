/* Native GSC frame-energy prefix 0x1000cc82..0x1000ccfc, with empty-frame
 * jump through 0x1000cdf4. The product word at 0x2002d79c is a caller
 * supplied volatile pointer, retaining the native first-use transition.
 * This is only the prefix of the larger 0x1000cc70 DSP provider.
 */
#include <stdint.h>

void gx8002_image_b_energy_prefix_verified_chunk(
    const uint32_t *ctx, const int16_t *complex_samples,
    int32_t frame_index, volatile uint32_t *first_use_word)
{
    int32_t frames=(int32_t)ctx[0x18/4];
    uint32_t offset=(uint32_t)frame_index*(uint32_t)frames*4u;
    uint32_t *energy=(uint32_t *)(uintptr_t)(ctx[0xa0/4]+offset);
    uint32_t *scaled=(uint32_t *)(uintptr_t)(ctx[0x98/4]+offset);
    uint32_t *baseline=(uint32_t *)(uintptr_t)(ctx[0x9c/4]+offset);
    for (int32_t i=0;i<frames;++i) {
        int32_t real=complex_samples[2*i];
        int32_t imag=complex_samples[2*i+1];
        energy[i]=(uint32_t)(real*real)+(uint32_t)(imag*imag);
    }
    if (*first_use_word==0u) {
        for (int32_t i=0;i<frames;++i) {
            scaled[i]=(uint32_t)((int32_t)energy[i]>>7);
            baseline[i]=127u;
        }
        *first_use_word=1u;
    }
}
