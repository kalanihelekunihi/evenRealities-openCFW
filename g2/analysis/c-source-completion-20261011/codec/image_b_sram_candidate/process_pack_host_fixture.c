#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_pack_verified_chunk(
    const uint32_t *,uint32_t);
int main(void) {
    uint16_t *p=mmap((void *)0x19300000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19300000);
    uint32_t ctx[32]={0};
    ctx[0x08/4]=2; ctx[0x18/4]=3;
    ctx[0x78/4]=0x19300000; ctx[0x7c/4]=0x19300080;
    ctx[0x6c/4]=0x19300100;
    p[2]=1; p[3]=2; p[8]=3; p[9]=4;
    p[0x80/2+2]=5; p[0x80/2+3]=6;
    p[0x80/2+8]=7; p[0x80/2+9]=8;
    gx8002_image_b_process_pack_verified_chunk(ctx,4);
    float *out=(float *)(p+0x100/2);
    const float expected[]={1,2,5,6,3,4,7,8};
    for (int i=0;i<8;++i) assert(out[i]==expected[i]);
    ctx[0x08/4]=0; out[0]=99.0f;
    gx8002_image_b_process_pack_verified_chunk(ctx,4);
    assert(out[0]==99.0f);
    return 0;
}
