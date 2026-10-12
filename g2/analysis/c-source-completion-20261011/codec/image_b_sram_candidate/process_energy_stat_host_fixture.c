#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_energy_stat_verified_chunk(
    const uint32_t *,uint32_t);
int main(void) {
    float *p=mmap((void *)0x19600000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19600000);
    uint32_t ctx[47]={0};
    ctx[0x08/4]=2; ctx[0xb4/4]=0x19600000;
    ctx[0xcc/4]=0x19600040; ctx[0xb8/4]=0x19600080;
    float *slot=p+0x80/4;
    slot[1]=10.0f;
    p[0x40/4]=1.0f; p[0x40/4+1]=2.0f;
    p[0x40/4+2]=3.0f; p[0x40/4+3]=4.0f;
    gx8002_image_b_process_energy_stat_verified_chunk(ctx,4);
    assert(slot[1]==10.0f);
    int16_t *scratch=(int16_t *)p; scratch[2]=1;
    gx8002_image_b_process_energy_stat_verified_chunk(ctx,4);
    assert(slot[1]>10.19f && slot[1]<10.21f);
    return 0;
}
