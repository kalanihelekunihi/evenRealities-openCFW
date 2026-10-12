/* Experimental whole-body C composition of native 0x1000cc70..0x1000ce02.
 * The first-use word is caller supplied: its product initialization remains
 * a separate image-layout obligation. The diagnostic's two %d arguments are
 * the low/high words of the exact finite float-to-double widening at 11af4.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_energy_float;
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

void gx8002_image_b_energy_prefix_verified_chunk(
    const uint32_t *, const int16_t *, int32_t, volatile uint32_t *);
void gx8002_image_b_energy_smoothing_verified_chunk(
    const uint32_t *, int32_t, int32_t);

static uint64_t gx8002_finite_binary32_to_binary64(uint32_t bits)
{
    uint64_t sign=(uint64_t)(bits>>31)<<63;
    uint32_t exponent=(bits>>23)&255u;
    uint32_t fraction=bits&0x7fffffu;
    if (exponent==0u) {
        if (fraction==0u) return sign;
        int32_t e=-126;
        while ((fraction&0x800000u)==0u) { fraction<<=1; --e; }
        return sign|((uint64_t)(e+1023)<<52)|((uint64_t)(fraction&0x7fffffu)<<29);
    }
    return sign|((uint64_t)(exponent+896u)<<52)|((uint64_t)fraction<<29);
}

void gx8002_image_b_energy_whole_experimental(
    const uint32_t *ctx, int16_t *samples, int32_t frame_index,
    int32_t mode, volatile uint32_t *first_use_word)
{
    int32_t frames=(int32_t)ctx[0x18/4];
    gx8002_image_b_energy_prefix_verified_chunk(
        ctx,samples,frame_index,first_use_word);
    if (mode!=0)
        gx8002_image_b_energy_smoothing_verified_chunk(ctx,frame_index,mode);
    if (frames<=0) return;
    uint32_t offset=(uint32_t)frame_index*(uint32_t)frames*4u;
    const uint32_t *energy=(const uint32_t *)(uintptr_t)(ctx[0xa0/4]+offset);
    const uint32_t *scaled=(const uint32_t *)(uintptr_t)(ctx[0x98/4]+offset);
    uint32_t *baseline=(uint32_t *)(uintptr_t)(ctx[0x9c/4]+offset);
    const gx8002_energy_float additive={.u=UINT32_C(0x467ffc00)};
    const gx8002_energy_float multiplier={.u=UINT32_C(0x46fffe00)};
    for (int32_t i=0;i<frames;++i) {
        int32_t old=(int32_t)baseline[i];
        float drift=(float)(int32_t)((uint32_t)old*116u);
        if (old<0) {
            gx8002_energy_float word={.f=drift};
            uint64_t widened=gx8002_finite_binary32_to_binary64(word.u);
            (void)gx8002_image_b_heap_log_10009934(
                "[error]:%d, %d,\n",(uint32_t)widened,
                (uint32_t)(widened>>32),old);
        }
        int32_t divisor=(int32_t)(scaled[i]+1u);
        int32_t quotient=(int32_t)energy[i]/divisor;
        baseline[i]=(uint32_t)quotient;
        int32_t excess=(int32_t)((uint32_t)quotient-127u);
        if (excess<0) excess=0;
        float numerator=(float)(int32_t)((uint32_t)excess*10u)+drift;
        float weighted=(numerator/(numerator+additive.f))*multiplier.f;
        int32_t gain=(int32_t)weighted;
        if (gain<9830) gain=9830;
        uint32_t rp=(uint32_t)(int32_t)samples[2*i]*(uint32_t)gain;
        uint32_t ip=(uint32_t)(int32_t)samples[2*i+1]*(uint32_t)gain;
        samples[2*i]=(int16_t)((int32_t)rp>>15);
        samples[2*i+1]=(int16_t)((int32_t)ip>>15);
    }
}
