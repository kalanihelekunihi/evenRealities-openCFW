#include <assert.h>
#include <math.h>
extern void gx8002_image_b_complex_ratio_1000e1e8(float out[2],const float a[2],const float b[2]);
extern void gx8002_image_b_complex_negative_ratio_1000e23c(float out[2],const float a[2],const float b[2]);
float gx8002_image_b_native_reciprocal_f32(float x) { return 1.0f/x; }
int main(void) {
    const float a[]={3.0f,4.0f}, b[]={1.0f,2.0f}; float out[2];
    gx8002_image_b_complex_ratio_1000e1e8(out,a,b);
    assert(fabsf(out[0]-2.2f)<0.000001f);
    assert(fabsf(out[1]+0.4f)<0.000001f);
    gx8002_image_b_complex_negative_ratio_1000e23c(out,a,b);
    assert(fabsf(out[0]+2.2f)<0.000001f);
    assert(fabsf(out[1]-0.4f)<0.000001f);
    const float c[]={-2.0f,1.5f}, d[]={0.5f,-0.25f};
    gx8002_image_b_complex_ratio_1000e1e8(out,c,d);
    assert(fabsf(out[0]-((-2.0f*0.5f+1.5f*(-0.25f))/0.3125f))<0.000001f);
    assert(fabsf(out[1]-((0.5f*1.5f-(-0.25f)*(-2.0f))/0.3125f))<0.000001f);
}
