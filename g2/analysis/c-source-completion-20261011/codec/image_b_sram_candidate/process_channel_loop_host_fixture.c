#include <assert.h>
#include <stdint.h>
extern void gx8002_image_b_process_channel_loop_verified_chunk(
    const uint32_t *,volatile uint32_t *);
static uintptr_t inputs[4];
static uint32_t indices[4],offsets[4];
static unsigned nfft,nadd;
static volatile uint32_t *expected_word;
int32_t gx8002_image_b_process_channel_fft_verified_chunk(
    const uint32_t *ctx,int16_t *samples,uint32_t channel,
    volatile uint32_t *word)
{
    (void)ctx;
    assert(nfft==nadd && word==expected_word);
    inputs[nfft]=(uintptr_t)samples;
    indices[nfft++]=channel;
    return 0;
}
void gx8002_image_b_process_overlap_add_verified_chunk(
    const uint32_t *ctx,uint32_t offset)
{
    (void)ctx;
    assert(nfft==nadd+1);
    offsets[nadd++]=offset;
}
int main(void)
{
    uint32_t ctx[0x94/4+1]={0};
    volatile uint32_t word=7;
    expected_word=&word;
    ctx[0x08/4]=3;
    ctx[0x10/4]=5;
    ctx[0x18/4]=7;
    ctx[0x90/4]=0x19000000u;
    gx8002_image_b_process_channel_loop_verified_chunk(ctx,&word);
    assert(nfft==3 && nadd==3);
    for(unsigned i=0;i<3;++i) {
        assert(inputs[i]==0x19000000u+i*14u);
        assert(indices[i]==i);
        assert(offsets[i]==i*10u);
    }
    ctx[0x08/4]=0;
    gx8002_image_b_process_channel_loop_verified_chunk(ctx,&word);
    assert(nfft==3 && nadd==3);
    return 0;
}
