#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern int gx8002_image_b_process_adapt_stage_verified_chunk(
    const uint32_t *,uint32_t,uint32_t,uint32_t,float [14]);
int main(void) {
    float *p=mmap((void *)0x19900000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19900000);
    uint32_t ctx[54]={0};
    ctx[0x04/4]=2; ctx[0x08/4]=1; ctx[0x18/4]=9;
    ctx[0xb4/4]=0x19900000; ctx[0xcc/4]=0x19900040;
    ctx[0xb8/4]=0x19900080; ctx[0x68/4]=0x199000c0;
    ctx[0xc4/4]=0x19900100; ctx[0xd0/4]=0x19900140;
    ctx[0xc8/4]=0x19900180; ctx[0x90/4]=0x199001c0;
    ((uint16_t *)p)[1]=1;
    p[0x40/4]=2.0f; p[0x40/4+1]=3.0f;
    p[0x80/4]=1.0f;
    p[0xc0/4]=1.0f; p[0xc0/4+1]=2.0f;
    p[0x100/4]=1.0f; p[0x100/4+1]=0.0f;
    p[0x180/4]=4.0f; p[0x180/4+1]=6.0f;
    float scratch[14]={0};
    int ran=gx8002_image_b_process_adapt_stage_verified_chunk(
        ctx,0,0,0,scratch);
    assert(ran==1 && scratch[0]==5.0f && scratch[1]==0.0f);
    assert(p[0x80/4]>1.11f && p[0x80/4]<1.13f);
    assert(p[0x100/4]>1.04f && p[0x100/4]<1.05f);
    assert(p[0x140/4]>2.08f && p[0x140/4]<2.10f);
    assert(p[0xc0/4]<0.0f);
    ((uint16_t *)p)[1]=0;
    p[0x140/4]=0.0f;
    ran=gx8002_image_b_process_adapt_stage_verified_chunk(
        ctx,0,0,0,scratch);
    assert(ran==0);
    assert(p[0x140/4]>2.08f && p[0x140/4]<2.10f);
    return 0;
}
