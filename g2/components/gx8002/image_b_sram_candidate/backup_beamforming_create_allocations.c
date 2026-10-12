/* Native GSC create core 0x1000cf04..0x1000cfae. These thirteen calls
 * follow the 220/400/angle-vector allocations in the prefix. Exact sizes
 * and context offsets come from authenticated C-SKY instructions. Native
 * does not check individual allocation results here; callers must preserve
 * its later failure policy rather than fabricate early success/failure.
 */
#include <stdint.h>

void gx8002_image_b_create_allocations_verified_chunk(
    uint32_t *ctx, void *(*allocate)(uint32_t bytes),
    uint32_t mic_count, uint32_t angle_count, uint32_t output_count)
{
    ctx[0x70/4]=(uint32_t)(uintptr_t)allocate(2048u);
    ctx[0x74/4]=(uint32_t)(uintptr_t)allocate(3072u);
    ctx[0x94/4]=(uint32_t)(uintptr_t)allocate(6u);
    ctx[0xa4/4]=(uint32_t)(uintptr_t)
        allocate(mic_count*angle_count*257u*8u);
    ctx[0xac/4]=(uint32_t)(uintptr_t)allocate(5u*angle_count*2u);
    ctx[0xb0/4]=(uint32_t)(uintptr_t)allocate(angle_count*4u);
    ctx[0xb4/4]=(uint32_t)(uintptr_t)allocate(8u);
    ctx[0xb8/4]=(uint32_t)(uintptr_t)allocate(angle_count*257u*4u);
    ctx[0xbc/4]=(uint32_t)(uintptr_t)allocate(mic_count*8u);
    ctx[0xc0/4]=(uint32_t)(uintptr_t)
        allocate(mic_count*(mic_count-1u)*8u);
    ctx[0xc4/4]=(uint32_t)(uintptr_t)
        allocate(angle_count*257u*(mic_count-1u)*8u);
    ctx[0xa8/4]=(uint32_t)(uintptr_t)allocate(angle_count*4u);
    ctx[0x5c/4]=(uint32_t)(uintptr_t)allocate(output_count*4u);
    ctx[0x24/4]=angle_count;
}
