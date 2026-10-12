#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_overlap_add_verified_chunk(
    const uint32_t *,uint32_t);
int main(void) {
    uint16_t *p=mmap((void *)0x19c00000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19c00000);
    uint32_t ctx[35]={0};
    ctx[0x0c/4]=3; ctx[0x10/4]=1;
    ctx[0x84/4]=0x19c00000; ctx[0x70/4]=0x19c00040;
    ctx[0x88/4]=0x19c00080;
    p[0]=1000; p[1]=2000; p[2]=3000;
    uint32_t *window=(uint32_t *)(p+0x40/2);
    window[0]=window[1]=window[2]=16384;
    int16_t *out=(int16_t *)(p+0x80/2);
    out[2]=1; out[3]=2; out[4]=3;
    gx8002_image_b_process_overlap_add_verified_chunk(ctx,4);
    assert(out[2]==501 && out[3]==1002 && out[4]==1503);
    ctx[0x10/4]=3; out[2]=7;
    gx8002_image_b_process_overlap_add_verified_chunk(ctx,4);
    assert(out[2]==7);
    return 0;
}
