#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_coeff_update_verified_chunk(
    const uint32_t *,uint32_t,const float [14],float);
int main(void) {
    float *p=mmap((void *)0x19800000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19800000);
    uint32_t ctx[50]={0}; ctx[0xc4/4]=0x19800000;
    float scratch[14]={1,2,3,4,5,6,7,8,9,10,11,12,13,14};
    for(int i=0;i<20;++i)p[i]=10.0f;
    ctx[0x04/4]=2;
    gx8002_image_b_process_coeff_update_verified_chunk(ctx,4,scratch,0.5f);
    assert(p[1]==10.5f && p[2]==11.0f && p[3]==10.0f);
    ctx[0x04/4]=4;
    gx8002_image_b_process_coeff_update_verified_chunk(ctx,4,scratch,0.5f);
    assert(p[1]==11.0f && p[2]==12.0f && p[6]==13.0f);
    assert(p[7]==10.0f);
    return 0;
}
