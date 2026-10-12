#include <assert.h>
extern void gx8002_image_b_complex_rows_1000e148(float *,const float *,const float *,int,int,int,int);
int main(void) {
    const float vector[]={1,2,3,4};
    const float matrix[]={5,6,7,8,9,10,11,12};
    float out[]={99,99,99,99};
    gx8002_image_b_complex_rows_1000e148(out,vector,matrix,123,456,2,2);
    assert(out[0]==70 && out[1]==-8 && out[2]==110 && out[3]==-16);
    gx8002_image_b_complex_rows_1000e148(out,vector,matrix,123,456,0,2);
    assert(out[0]==0 && out[1]==0 && out[2]==0 && out[3]==0);
    out[0]=99;
    gx8002_image_b_complex_rows_1000e148(out,vector,matrix,123,456,2,0);
    assert(out[0]==99);
}
