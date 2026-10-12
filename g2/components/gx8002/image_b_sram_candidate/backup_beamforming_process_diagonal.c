/* Native process 0x1000d6b6..0x1000d79a diagonal initialization.
 * The selected row comes from the word at ctx+0x5c; no initial row is
 * substituted. Each frequency bin first stores (1,0) then evaluates the
 * existing source-owned negative complex ratio leaf over adjacent rows.
 */
#include <stdint.h>

extern void gx8002_image_b_complex_negative_ratio_1000e23c(
    float output[2], const float first[2], const float second[2]);

void gx8002_image_b_process_diagonal_frame_verified_chunk(
    const uint32_t *ctx,uint32_t coefficient_byte_offset)
{
    uint32_t row_width=ctx[0x04/4];
    /* Native stack+0x18 was initialized from ctx+0x04 minus one at d4a0.
     * It is distinct from the ctx+0x18 frame count at stack+0x38. */
    int32_t bins=(int32_t)ctx[0x04/4]-1;
    if (bins<=0) return;
    const float *coeff=(const float *)(uintptr_t)ctx[0xa4/4];
    float *diagonal=(float *)(uintptr_t)ctx[0xc0/4];
    uint32_t row_stride=(row_width+1u)*2u;
    uint32_t base=coefficient_byte_offset/4u;
    for (int32_t bin=0;bin<bins;++bin) {
        float *row=diagonal+(uint32_t)bin*row_stride;
        row[0]=1.0f;
        row[1]=0.0f;
        const float *first=coeff+base+(uint32_t)bin*2u;
        const float *second=first+2;
        gx8002_image_b_complex_negative_ratio_1000e23c(
            row+2,first,second);
    }
}

void gx8002_image_b_process_diagonal_verified_chunk(const uint32_t *ctx)
{
    uint32_t selected_row=*(const uint32_t *)(uintptr_t)ctx[0x5c/4];
    gx8002_image_b_process_diagonal_frame_verified_chunk(
        ctx,selected_row*ctx[0x04/4]*8u);
}
