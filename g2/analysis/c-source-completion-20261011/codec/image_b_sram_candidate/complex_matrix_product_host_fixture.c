#include <assert.h>
#include <stdint.h>
extern void gx8002_image_b_complex_matrix_product_1000df38(
    float *,const float *,const float *,int32_t,int32_t,int32_t);
int main(void) {
    const float a[]={1,2,3,4, 5,6,7,8};
    const float b[]={2,1,4,3, 6,5,8,7};
    float out[8]={99,99,99,99,99,99,99,99};
    gx8002_image_b_complex_matrix_product_1000df38(out,a,b,2,2,2);
    /* Row 0 / col 0: (2*1-1*2)+(4*3-3*4)=-0;
     * imaginary (2*2+1*1)+(4*4+3*3)=30. */
    assert(out[0]==0.0f && out[1]==30.0f);
    /* Row 0 / col 1: (2*5-1*6)+(4*7-3*8)=8;
     * imaginary (2*6+1*5)+(4*8+3*7)=70. */
    assert(out[2]==8.0f && out[3]==70.0f);
    float zero[2]={7,8};
    gx8002_image_b_complex_matrix_product_1000df38(zero,a,b,1,0,1);
    assert(zero[0]==0.0f && zero[1]==0.0f);
    return 0;
}
