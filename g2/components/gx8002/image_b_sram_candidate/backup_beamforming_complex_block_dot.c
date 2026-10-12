/* Complete native 0x1000e004..0x1000e0b4. Independent callable entry:
 * the preceding df38 pop returns, as specified by pinned C-SKY GCC RTL.
 * The fifth stack word is the number of complex pairs per output. First
 * blocks advance by that many pairs; the second block restarts each output.
 */
#include <stdint.h>

void gx8002_image_b_complex_block_dot_1000e004(
    float *output, const float *first, const float *second,
    int32_t blocks, int32_t pairs)
{
    if (blocks<=0) return;
    for (int32_t block=0;block<blocks;++block) {
        float *out=output+2*block;
        out[0]=0.0f; out[1]=0.0f;
        if (pairs<=0) continue;
        float real=0.0f,imag=0.0f;
        const float *a=first+(uint32_t)block*(uint32_t)pairs*2u;
        for (int32_t k=0;k<pairs;++k) {
            float ar=a[2*k], ai=a[2*k+1];
            float br=second[2*k], bi=second[2*k+1];
            volatile float real_first=ai*bi;
            real+=real_first+ar*br;
            out[0]=real;
            volatile float imag_first=ai*br;
            imag+=imag_first-ar*bi;
            out[1]=imag;
        }
    }
}
