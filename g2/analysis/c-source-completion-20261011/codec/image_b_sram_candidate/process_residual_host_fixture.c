#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_residual_verified_chunk(
    const uint32_t *,uint32_t);
int main(void) {
    float *p=mmap((void *)0x19400000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19400000);
    uint32_t ctx[53]={0};
    ctx[0x04/4]=2; ctx[0x08/4]=2; ctx[0x18/4]=3;
    ctx[0xc8/4]=0x19400000; ctx[0xd0/4]=0x19400040;
    ctx[0x68/4]=0x19400080; ctx[0x90/4]=0x19400100;
    p[0]=11.0f; p[1]=-9.0f; p[2]=20.0f; p[3]=4.0f;
    p[0x40/4]=1.0f; p[0x40/4+1]=-1.0f;
    p[0x40/4+2]=2.0f; p[0x40/4+3]=0.0f;
    gx8002_image_b_process_residual_verified_chunk(ctx,4);
    float *r=p+0x80/4;
    assert(r[0]==4.5f && r[1]==-3.5f && r[2]==8.0f && r[3]==2.0f);
    int16_t *samples=(int16_t *)(p+0x100/4);
    assert(samples[2]==4 && samples[3]==-3);
    assert(samples[8]==8 && samples[9]==2);
    return 0;
}
