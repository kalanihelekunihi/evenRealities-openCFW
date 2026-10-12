#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
float gx8002_image_b_native_reciprocal_f32(float x) { return 1.0f/x; }
extern void gx8002_image_b_process_diagonal_verified_chunk(const uint32_t *);
extern void gx8002_image_b_process_diagonal_frame_verified_chunk(
    const uint32_t *,uint32_t);
int main(void) {
    float *p=mmap((void *)0x19200000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19200000);
    uint32_t ctx[49]={0};
    ctx[0x04/4]=3; ctx[0x18/4]=2;
    ctx[0x5c/4]=0x19200080;
    ctx[0xa4/4]=0x19200000; ctx[0xc0/4]=0x19200100;
    *(uint32_t *)(p+0x80/4)=1;
    /* base=1*3 complex coefficients=6 floats. Native neighboring pairs:
     * bin0 2/1 => -2, bin1 1/3 => -1/3. Destination rows are strided. */
    p[6]=2.0f; p[7]=0.0f; p[8]=1.0f; p[9]=0.0f;
    p[10]=3.0f; p[11]=0.0f;
    gx8002_image_b_process_diagonal_verified_chunk(ctx);
    float *out=p+0x100/4;
    assert(out[0]==1.0f && out[1]==0.0f);
    assert(out[2]==-2.0f && out[3]==0.0f);
    assert(out[8]==1.0f && out[9]==0.0f);
    assert(out[10]<-0.3333f && out[10]>-0.3334f && out[11]==0.0f);
    /* The next frame uses native stack+0x20 after its db48 increment. */
    p[18]=8.0f; p[19]=0.0f; p[20]=2.0f; p[21]=0.0f;
    p[22]=4.0f; p[23]=0.0f;
    gx8002_image_b_process_diagonal_frame_verified_chunk(ctx,18u*4u);
    assert(out[2]==-4.0f && out[3]==0.0f);
    assert(out[10]==-0.5f && out[11]==0.0f);
    return 0;
}
