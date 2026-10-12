#include <assert.h>
extern void gx8002_image_b_complex_matrix_1000e0b8(float *,const float *,const float *,int,int,int,int);
int main(void) {
    const float vector[]={1,2,3,4};
    const float matrix[]={5,6,7,8,9,10,11,12};
    float out[]={99,99,99,99};
    gx8002_image_b_complex_matrix_1000e0b8(out,vector,matrix,2,1,9,2);
    assert(out[0]==84 && out[1]==-10 && out[2]==104 && out[3]==-14);
    gx8002_image_b_complex_matrix_1000e0b8(out,vector,matrix,0,1,9,2);
    assert(out[0]==0 && out[1]==0 && out[2]==0 && out[3]==0);
    out[0]=99;
    gx8002_image_b_complex_matrix_1000e0b8(out,vector,matrix,2,1,9,0);
    assert(out[0]==99);
}
