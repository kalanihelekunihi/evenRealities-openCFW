#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_output_finish_verified_chunk(
    const uint32_t *,uint8_t *,uint32_t);
int main(void) {
    int16_t *p=mmap((void *)0x19d00000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19d00000);
    uint32_t ctx[36]={0};
    ctx[0x04/4]=2; ctx[0x08/4]=1;
    ctx[0x0c/4]=3; ctx[0x10/4]=1;
    ctx[0x88/4]=0x19d00000; ctx[0x80/4]=0x19d00080;
    ctx[0x74/4]=0x19d000c0; ctx[0x2c/4]=0x3f800000u;
    for(int i=0;i<5;++i)p[i]=(int16_t)((i+1)*1000);
    uint32_t *window=(uint32_t *)(p+0xc0/2);
    window[0]=window[1]=window[2]=16384;
    uint8_t output[16]={0};
    gx8002_image_b_process_output_finish_verified_chunk(ctx,output,4u);
    assert(p[0x80/2]==2000 && p[0x80/2+1]==3000);
    int16_t lane;
    memcpy(&lane,output+4,2); assert(lane==500);
    assert(output[0]==0 && output[6]==0);
    return 0;
}
