#include <assert.h>
#include <stdint.h>
extern void gx8002_image_b_process_post_ring_experimental(
    const uint32_t *,uint8_t *,uint32_t,volatile uint32_t *);
static unsigned phase;
static const uint32_t *expected_ctx;
static uint8_t *expected_output;
static volatile uint32_t *expected_word;
void gx8002_image_b_process_frame_loop_experimental(const uint32_t *ctx)
{ assert(phase++==0 && ctx==expected_ctx); }
uint32_t gx8002_image_b_process_output_prepare_verified_chunk(
    const uint32_t *ctx,uint32_t index)
{ assert(phase++==1 && ctx==expected_ctx && index==3u); return 42u; }
void gx8002_image_b_process_channel_loop_verified_chunk(
    const uint32_t *ctx,volatile uint32_t *word)
{ assert(phase++==2 && ctx==expected_ctx && word==expected_word); }
void gx8002_image_b_process_output_finish_verified_chunk(
    const uint32_t *ctx,uint8_t *out,uint32_t offset)
{ assert(phase++==3 && ctx==expected_ctx && out==expected_output && offset==42u); }
int main(void)
{
    uint32_t ctx[36]={0};
    uint8_t out[16]={0};
    volatile uint32_t word=0;
    expected_ctx=ctx; expected_output=out; expected_word=&word;
    gx8002_image_b_process_post_ring_experimental(ctx,out,3u,&word);
    assert(phase==4u);
    return 0;
}
