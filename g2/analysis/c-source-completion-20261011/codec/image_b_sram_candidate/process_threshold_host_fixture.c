#include <assert.h>
#include <stdint.h>
extern void gx8002_image_b_process_thresholds_verified_chunk(
    const int16_t *,const int16_t *,const float *,int16_t *,int32_t,int32_t);
int main(void) {
    int16_t denominator[]={1,0,1,0,1,0};
    int16_t numerator[]={0,2,0,3,0,4};
    float coeff[36]={0};
    for (int i=0;i<3;++i) { coeff[12*i]=1.0f; coeff[12*i+8]=3.0f; }
    int16_t ring[]={0,0};
    gx8002_image_b_process_thresholds_verified_chunk(
        denominator,numerator,coeff,ring,9,11);
    assert(ring[1]==1);
    ring[1]=7;
    gx8002_image_b_process_thresholds_verified_chunk(
        denominator,numerator,coeff,ring,9,8);
    assert(ring[1]==7);
    return 0;
}
