#include <assert.h>
#include <stdint.h>
extern void gx8002_image_b_complex_block_dot_1000e004(
    float *,const float *,const float *,int32_t,int32_t);
int main(void) {
    const float a[]={1,2,3,4, 5,6,7,8};
    const float b[]={2,1,4,3};
    float out[4]={99,99,99,99};
    gx8002_image_b_complex_block_dot_1000e004(out,a,b,2,2);
    assert(out[0]==28.0f && out[1]==10.0f);
    assert(out[2]==68.0f && out[3]==18.0f);
    gx8002_image_b_complex_block_dot_1000e004(out,a,b,2,0);
    assert(out[0]==0.0f && out[1]==0.0f);
    assert(out[2]==0.0f && out[3]==0.0f);
    return 0;
}
