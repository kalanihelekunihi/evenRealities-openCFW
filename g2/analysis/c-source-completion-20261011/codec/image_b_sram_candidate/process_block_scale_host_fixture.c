#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern float gx8002_image_b_process_block_scale_verified_chunk(
    const uint32_t *,uint32_t,float *);
int main(void) {
    float *p=mmap((void *)0x19700000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19700000);
    uint32_t ctx[47]={0};
    ctx[0x04/4]=2; ctx[0x08/4]=2;
    ctx[0x68/4]=0x19700000; ctx[0xb8/4]=0x19700080;
    p[0]=1.0f; p[1]=2.0f; p[2]=3.0f; p[3]=4.0f;
    p[0x80/4+1]=2.0f;
    float scratch[2]={99,99};
    float scale=gx8002_image_b_process_block_scale_verified_chunk(ctx,4,scratch);
    assert(scratch[0]==30.0f && scratch[1]==0.0f);
    assert(scale>0.004999f && scale<0.005001f);
    return 0;
}
