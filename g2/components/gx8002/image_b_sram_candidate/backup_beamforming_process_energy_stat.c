/* Native process 0x1000d8ce..0x1000d926. The aggregate scratch flag at
 * index ctx+0x08 gates this path. The source dot product is over every
 * binary32 component of ctx+0xcc. The observed row/band byte offset is
 * supplied by the caller; no product row default is inferred.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_process_float_word;

void gx8002_image_b_process_energy_stat_verified_chunk(
    const uint32_t *ctx, uint32_t energy_slot_byte_offset)
{
    int32_t modes=(int32_t)ctx[0x08/4];
    const int16_t *scratch=(const int16_t *)(uintptr_t)ctx[0xb4/4];
    if ((uint16_t)scratch[(uint32_t)modes]==0u) return;
    if (modes<=0) return; /* Native branches to 0x1000ddde. */
    const float *components=(const float *)(uintptr_t)ctx[0xcc/4];
    float sum=0.0f;
    for (int32_t i=0;i<modes*2;++i)
        sum+=components[i]*components[i];
    const gx8002_process_float_word scale={.u=UINT32_C(0x3c23d700)};
    const gx8002_process_float_word decay={.u=UINT32_C(0x3f7d70a4)};
    float *slot=(float *)(uintptr_t)(ctx[0xb8/4]+energy_slot_byte_offset);
    *slot=sum*scale.f+(*slot)*decay.f;
}
