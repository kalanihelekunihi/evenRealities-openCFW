/* Native process 0x1000d7a0..0x1000d7f8: pack two strided complex
 * halfword streams into four binary32 words per mode. The source band byte
 * offset is produced by the parent loop and is passed explicitly here.
 */
#include <stdint.h>

void gx8002_image_b_process_pack_verified_chunk(
    const uint32_t *ctx, uint32_t band_byte_offset)
{
    int32_t modes=(int32_t)ctx[0x08/4];
    if (modes<=0) return; /* Native branch to 0x1000dd78. */
    uintptr_t first=(uintptr_t)(ctx[0x78/4]+band_byte_offset);
    uintptr_t second=(uintptr_t)(ctx[0x7c/4]+band_byte_offset);
    float *destination=(float *)(uintptr_t)ctx[0x6c/4];
    uint32_t stride=ctx[0x18/4]*4u;
    for (int32_t i=0;i<modes;++i) {
        const uint16_t *a=(const uint16_t *)first;
        const uint16_t *b=(const uint16_t *)second;
        destination[4*i]=(float)a[0];
        destination[4*i+1]=(float)a[1];
        destination[4*i+2]=(float)b[0];
        destination[4*i+3]=(float)b[1];
        first+=stride;
        second+=stride;
    }
}
