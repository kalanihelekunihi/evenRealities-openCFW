#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_matrix_stage_verified_chunk(
    const uint32_t *,uint32_t,uint32_t,uint32_t);
int main(void) {
    float *p=mmap((void *)0x19500000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19500000);
    uint32_t ctx[54]={0};
    /* Deliberately distinct frame/selection values expose any stack+0x18
     * versus ctx+0x18 alias mistake in the composed call ABI. */
    ctx[0x04/4]=1; ctx[0x08/4]=1; ctx[0x18/4]=9; ctx[0x48/4]=1;
    ctx[0xc0/4]=0x19500000; ctx[0x6c/4]=0x19500020;
    ctx[0xcc/4]=0x19500040; ctx[0xc8/4]=0x19500060;
    ctx[0xd0/4]=0x19500080; ctx[0xa4/4]=0x195000a0;
    ctx[0xc4/4]=0x195000c0; ctx[0x68/4]=0x195000e0;
    ctx[0x90/4]=0x19500100;
    p[0]=1; p[1]=0;
    p[0x20/4]=2; p[0x20/4+1]=3;
    p[0xa0/4]=1; p[0xa0/4+1]=0;
    p[0xc0/4]=1; p[0xc0/4+1]=0;
    gx8002_image_b_process_matrix_stage_verified_chunk(ctx,0,0,0);
    assert(p[0x40/4]==-2 && p[0x40/4+1]==3);
    assert(p[0x60/4]==2 && p[0x60/4+1]==3);
    assert(p[0x80/4]==-2 && p[0x80/4+1]==3);
    assert(p[0xe0/4]==4 && p[0xe0/4+1]==0);
    int16_t *samples=(int16_t *)(p+0x100/4);
    assert(samples[0]==4 && samples[1]==0);
    return 0;
}
