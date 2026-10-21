/* Complete native image-B GSC matrix leaf 0x1000e148..0x1000e1e4.
 * The live caller at 0x1000d82c supplies a register word and three stack
 * words; this body reads only the latter two at stack +4/+8 as column and
 * row counts. Each row reuses one complex vector and advances through one
 * contiguous row of the matrix. Intermediate output stores are retained.
 */
#include <stdint.h>

void gx8002_image_b_complex_rows_1000e148(
    float *output, const float *vector, const float *matrix,
    int32_t unused_register, int32_t unused_stack,
    int32_t columns, int32_t rows)
{
    (void)unused_register;
    (void)unused_stack;
    for (int32_t row=0; row<rows; ++row) {
        volatile float *slot=output+(uint32_t)row*2u;
        slot[0]=0.0f;
        slot[1]=0.0f;
        float real_sum=0.0f, imaginary_sum=0.0f;
        for (int32_t column=0; column<columns; ++column) {
            const float *a=vector+(uint32_t)column*2u;
            const float *b=matrix+
                ((uint32_t)row*(uint32_t)columns+(uint32_t)column)*2u;
            volatile float real_product=a[1]*b[1];
            real_sum+=real_product+a[0]*b[0];
            slot[0]=real_sum;
            volatile float imaginary_product=a[1]*b[0];
            imaginary_sum+=a[0]*b[1]-imaginary_product;
            slot[1]=imaginary_sum;
        }
    }
}
