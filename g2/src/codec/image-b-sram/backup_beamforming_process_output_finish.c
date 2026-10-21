/* Native process 0x1000dcd4..0x1000dd44 final overlap retention and
 * caller output. Stack+0x18 is reused at db86 for the frame output byte
 * offset; its earlier ctx+0x04-1 value is no longer live at dd06.
 * Byte stores preserve the native little-endian halfword placement.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_output_float_word;
extern void gx8002_image_b_dsp_copy_1000f180(
    const int16_t *,int16_t *,uint32_t);

void gx8002_image_b_process_output_finish_verified_chunk(
    const uint32_t *ctx,uint8_t *caller_output,
    uint32_t output_frame_byte_offset)
{
    uint32_t prefill=ctx[0x10/4]*ctx[0x08/4];
    uint32_t tail=ctx[0x0c/4]-ctx[0x10/4];
    /* Native stack+0x1c retains prefill; the clear call uses
     * prefill+tail in a transient register. */
    uint32_t count=prefill;
    const int16_t *mixed=(const int16_t *)(uintptr_t)ctx[0x88/4];
    gx8002_image_b_dsp_copy_1000f180(
        mixed+count,(int16_t *)(uintptr_t)ctx[0x80/4],tail);
    if ((int32_t)count<=0) return;
    const uint32_t *window=(const uint32_t *)(uintptr_t)ctx[0x74/4];
    const gx8002_output_float_word gain_word={.u=ctx[0x2c/4]};
    int32_t gain=(int32_t)(gain_word.f*10.0f);
    uint8_t *output=caller_output+output_frame_byte_offset;
    for (uint32_t i=0;i<count;++i) {
        uint32_t product=(uint32_t)(uint16_t)mixed[i]*window[i];
        int16_t q15=(int16_t)(product>>15);
        uint32_t scaled=(uint32_t)(int32_t)q15*(uint32_t)gain;
        int16_t lane=(int16_t)((int32_t)scaled/10);
        output[i*2u]=(uint8_t)(uint16_t)lane;
        output[i*2u+1u]=(uint8_t)((uint16_t)lane>>8);
    }
}
