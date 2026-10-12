#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_ring_average_verified_chunk(
    const uint32_t *,uint32_t,volatile uint32_t *);
int main(void) {
    int16_t *p=mmap((void *)0x19100000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19100000);
    uint32_t ctx[46]={0};
    ctx[0x08/4]=3; ctx[0x48/4]=2; ctx[0x1c/4]=4;
    ctx[0xac/4]=0x19100000; ctx[0xb4/4]=0x19100040;
    ctx[0xa8/4]=0x19100080;
    int16_t *scratch=p+0x40/2;
    float *threshold=(float *)(p+0x80/2);
    threshold[1]=4.0f;
    p[1]=2; p[5]=4; /* mean 3, below 4 */
    volatile uint32_t counter=9;
    gx8002_image_b_process_ring_average_verified_chunk(ctx,1,&counter);
    assert(scratch[1]==1 && scratch[3]==1 && counter==10);
    threshold[1]=3.0f;
    gx8002_image_b_process_ring_average_verified_chunk(ctx,2,&counter);
    assert(scratch[2]==0 && scratch[3]==1 && counter==11);
    ctx[0x48/4]=0;
    gx8002_image_b_process_ring_average_verified_chunk(ctx,2,&counter);
    assert(counter==12);
    return 0;
}
