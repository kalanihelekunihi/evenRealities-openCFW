/* Complete native matrix leaf 0x1000df38..0x1000e002. The C-SKY pop at
 * e002 is a returning epilogue (pinned GCC csky.md *pop_multi RTL), so the
 * distinct e004 helper is not part of this call. Native order is outer
 * rows, output columns, then inner complex components. Each result starts
 * at zero and is stored after every inner accumulation.
 */
#include <stdint.h>

void gx8002_image_b_complex_matrix_product_1000df38(
    float *output, const float *first, const float *second,
    int32_t rows, int32_t inner, int32_t columns)
{
    if (rows<=0 || columns<=0) return;
    for (int32_t row=0;row<rows;++row) {
        const float *a=first+(uint32_t)row*(uint32_t)inner*2u;
        for (int32_t column=0;column<columns;++column) {
            float *out=output+((uint32_t)row*(uint32_t)columns+
                               (uint32_t)column)*2u;
            out[0]=0.0f; out[1]=0.0f;
            if (inner<=0) continue;
            const float *b=second+(uint32_t)column*(uint32_t)inner*2u;
            float real=0.0f,imag=0.0f;
            for (int32_t k=0;k<inner;++k) {
                float ar=a[2*k], ai=a[2*k+1];
                float br=b[2*k], bi=b[2*k+1];
                volatile float real_first=ai*bi;
                real+=real_first-ar*br;
                out[0]=real;
                volatile float imag_first=ai*br;
                imag+=imag_first+ar*bi;
                out[1]=imag;
            }
        }
    }
}
