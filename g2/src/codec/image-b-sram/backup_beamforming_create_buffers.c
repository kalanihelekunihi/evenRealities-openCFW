/* Native GSC create core 0x1000cfd8..0x1000d03c. This zeroes four
 * allocation extents using the source-owned 0x100113c4 byte writer, seeds
 * the angle-by-bin table with the authenticated 0x47c35000 word, then
 * copies output-index bytes. The native call order is retained.
 */
#include <stdint.h>

extern void gx8002_image_b_zero_100113c4(
    void *destination, uint32_t value, uint32_t bytes);

void gx8002_image_b_create_buffers_verified_chunk(
    uint32_t *ctx, uint32_t mic_count, uint32_t angle_count,
    uint32_t output_count, const uint32_t *output_indices)
{
    uint32_t angle_bins=angle_count*257u;
    uint32_t cross_bytes=angle_bins*(mic_count-1u)*8u;
    gx8002_image_b_zero_100113c4(
        (void *)(uintptr_t)ctx[0xd8/4],0u,ctx[0xd4/4]*4u);
    gx8002_image_b_zero_100113c4(
        (void *)(uintptr_t)ctx[0xb8/4],0u,angle_bins*4u);
    gx8002_image_b_zero_100113c4(
        (void *)(uintptr_t)ctx[0xc4/4],0u,cross_bytes);
    gx8002_image_b_zero_100113c4(
        (void *)(uintptr_t)ctx[0xac/4],0u,ctx[0x48/4]*angle_count*2u);
    if ((int32_t)angle_bins>0) {
        uint32_t *target=(uint32_t *)(uintptr_t)ctx[0xb8/4];
        for (int32_t i=0; i<(int32_t)angle_bins; ++i)
            target[i]=UINT32_C(0x47c35000);
    }
    if ((int32_t)output_count>0) {
        uint8_t *target=(uint8_t *)(uintptr_t)ctx[0x5c/4];
        const uint8_t *source=(const uint8_t *)output_indices;
        for (uint32_t i=0; i<output_count*4u; ++i)
            target[i]=source[i];
    }
}
