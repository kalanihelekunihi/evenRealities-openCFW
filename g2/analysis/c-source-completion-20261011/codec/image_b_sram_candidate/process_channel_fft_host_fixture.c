#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include "backup_fft_profile.h"
const image_b_rfft_q15 gx8002_image_b_rifft_profile_2001700c={0};
static int energy_calls,rfft_calls;
void gx8002_image_b_energy_whole_experimental(
    const uint32_t *ctx,int16_t *samples,int32_t index,int32_t mode,
    volatile uint32_t *first) {
    assert(ctx && samples && index==0 && mode==1 && first);
    assert(samples[0]==8192 && samples[1]==-16384);
    ++energy_calls;
}
void gx8002_image_b_rfft_1000ef64(
    const image_b_rfft_q15 *profile,int16_t *source,int16_t *out) {
    assert(profile==&gx8002_image_b_rifft_profile_2001700c);
    assert(source[0]==8192 && source[1]==-16384);
    out[0]=8192; out[1]=-16384; ++rfft_calls;
}
extern int32_t gx8002_image_b_process_channel_fft_verified_chunk(
    const uint32_t *,int16_t *,uint32_t,volatile uint32_t *);
int main(void) {
    int16_t *p=mmap((void *)0x19b00000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19b00000);
    uint32_t ctx[38]={0}; ctx[0x18/4]=1; ctx[0x14/4]=2;
    ctx[0x84/4]=0x19b00040; ctx[0xb4/4]=0x19b00080;
    ctx[0x94/4]=0x19b000a0;
    p[0]=1; p[1]=-2; p[0x80/2]=1; p[0xa0/2]=2;
    volatile uint32_t first=1;
    int32_t headroom=gx8002_image_b_process_channel_fft_verified_chunk(
        ctx,p,0,&first);
    assert(headroom==13 && energy_calls==1 && rfft_calls==1);
    assert(p[0x40/2]==128 && p[0x40/2+1]==-256);
    return 0;
}
