#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t gx8002_image_b_process_output_prepare_verified_chunk(
    const uint32_t *,uint32_t);
int main(void) {
    int16_t *p=mmap((void *)0x19a00000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19a00000);
    uint32_t ctx[35]={0};
    ctx[0x08/4]=2; ctx[0x0c/4]=9; ctx[0x10/4]=3;
    ctx[0x80/4]=0x19a00000; ctx[0x88/4]=0x19a00080;
    for(int i=0;i<6;++i)p[i]=(int16_t)(i+1);
    for(int i=0;i<20;++i)p[0x80/2+i]=99;
    uint32_t offset=gx8002_image_b_process_output_prepare_verified_chunk(ctx,4);
    assert(offset==48);
    for(int i=0;i<6;++i)assert(p[0x80/2+i]==i+1);
    for(int i=6;i<12;++i)assert(p[0x80/2+i]==0);
    assert(p[0x80/2+12]==99);
    return 0;
}
