/* Native process 0x1000dc94..0x1000dcc8 overlap-add after inverse RFFT.
 * The transformed input loads unsigned halfwords, window coefficients load
 * 32-bit words, the product wraps at 32 bits before arithmetic Q15 shift,
 * then adds the signed destination halfword and stores a halfword.
 */
#include <stdint.h>

void gx8002_image_b_process_overlap_add_verified_chunk(
    const uint32_t *ctx,uint32_t destination_byte_offset)
{
    int32_t tail=(int32_t)(ctx[0x0c/4]-ctx[0x10/4]);
    if (tail<=0) return;
    int32_t count=(int32_t)ctx[0x0c/4];
    const uint16_t *source=(const uint16_t *)(uintptr_t)ctx[0x84/4];
    const uint32_t *window=(const uint32_t *)(uintptr_t)ctx[0x70/4];
    int16_t *output=(int16_t *)(uintptr_t)
        (ctx[0x88/4]+destination_byte_offset);
    for (int32_t i=0;i<count;++i) {
        uint32_t product=(uint32_t)source[i]*window[i];
        int32_t scaled=(int32_t)product>>15;
        output[i]=(int16_t)((uint32_t)scaled+(uint32_t)(int32_t)output[i]);
    }
}
