/* Complete native image-B GSC matrix leaf 0x1000e0b8..0x1000e144.
 * The seventh argument is the row count at caller stack+8. The two earlier
 * stack words are present but unused by this leaf. The native
 * input matrix advances by `rows * 8` bytes for each inner column, then by
 * eight bytes for the next row. Each output pair starts at zero. There are
 * no hidden product defaults or denominator guards in this leaf.
 */
#include <stdint.h>

void gx8002_image_b_complex_matrix_1000e0b8(
    float *output, const float *vector, const float *matrix,
    int32_t columns, int32_t unused_stack0,
    int32_t unused_stack4, int32_t rows)
{
    (void)unused_stack0;
    (void)unused_stack4;
    for (int32_t row=0; row<rows; ++row) {
        volatile float *slot=output+(uint32_t)row*2u;
        float real_sum=0.0f, imaginary_sum=0.0f;
        slot[0]=0.0f;
        slot[1]=0.0f;
        for (int32_t column=0; column<columns; ++column) {
            const float *a=vector+(uint32_t)column*2u;
            const float *b=matrix+
                ((uint32_t)column*(uint32_t)rows+(uint32_t)row)*2u;
            volatile float real_product=a[1]*b[1];
            real_sum+=real_product+a[0]*b[0];
            slot[0]=real_sum;
            volatile float imaginary_product=a[1]*b[0];
            imaginary_sum+=a[0]*b[1]-imaginary_product;
            slot[1]=imaginary_sum;
        }
    }
}
