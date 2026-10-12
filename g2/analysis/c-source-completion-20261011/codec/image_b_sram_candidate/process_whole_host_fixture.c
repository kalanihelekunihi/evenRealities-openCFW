#include <assert.h>
#include <stdint.h>
struct gx8002_image_b_process_band {
    uint32_t mode_count,coefficient_bytes,band_index,active_stages;
};
struct gx8002_image_b_process_prepare {
    uint32_t first_threshold_address,second_threshold_address;
    uint32_t coefficient_address,ring_row_address;
};
extern void gx8002_image_b_process_whole_experimental(
    const uint32_t *,uint8_t *,uint32_t,uint32_t,
    volatile uint32_t *,volatile uint32_t *);
static char trace[16]; static unsigned n;
static const uint32_t *expected_ctx;
static uint8_t *expected_output;
static volatile uint32_t *expected_first_use;
void gx8002_image_b_process_band_verified_chunk(
    const uint32_t *ctx,struct gx8002_image_b_process_band *out)
{ assert(ctx==expected_ctx); trace[n++]='B';
  *out=(struct gx8002_image_b_process_band){9,36,10,2}; }
void gx8002_image_b_process_prepare_verified_chunk(
    const uint32_t *ctx,uint32_t counter,uint32_t modes,int32_t stages,
    struct gx8002_image_b_process_prepare *out)
{ assert(ctx==expected_ctx && counter==4u && modes==9u && stages==2);
  trace[n++]='P';
  *out=(struct gx8002_image_b_process_prepare){100,200,300,400}; }
void gx8002_image_b_process_thresholds_verified_chunk(
    const int16_t *a,const int16_t *b,const float *coeff,int16_t *ring,
    int32_t first,int32_t last)
{ unsigned stage=(n==2u?0u:1u);
  assert((uintptr_t)a==100u+stage*12u);
  assert((uintptr_t)b==200u+stage*12u);
  assert((uintptr_t)coeff==300u);
  assert((uintptr_t)ring==(stage==0u?400u:506u));
  assert(first==9 && last==10); trace[n++]='T'; }
void gx8002_image_b_dsp_clear_1000f1ac(
    uint32_t value,int16_t *dest,uint32_t count)
{ assert(value==0u && (uintptr_t)dest==506u && count==3u);
  trace[n++]='C'; }
void gx8002_image_b_process_ring_average_verified_chunk(
    const uint32_t *ctx,uint32_t stage,volatile uint32_t *counter)
{ assert(ctx==expected_ctx && stage==(n==3u?0u:1u));
  ++*counter; trace[n++]='R'; }
void gx8002_image_b_process_post_ring_experimental(
    const uint32_t *ctx,uint8_t *output,uint32_t frame,
    volatile uint32_t *first_use)
{ assert(ctx==expected_ctx && output==expected_output && frame==7u);
  assert(first_use==expected_first_use); trace[n++]='O'; }
int main(void)
{
    uint32_t ctx[0xac/4+1]={0};
    uint8_t output[8]={0};
    volatile uint32_t ring=4,first_use=8;
    ctx[0x08/4]=2; ctx[0x18/4]=3;
    ctx[0x48/4]=2; ctx[0x1c/4]=3; ctx[0xac/4]=500;
    expected_ctx=ctx;expected_output=output;expected_first_use=&first_use;
    gx8002_image_b_process_whole_experimental(
        ctx,output,0x1234u,7u,&ring,&first_use);
    assert(n==8u && ring==6u);
    assert(trace[0]=='B' && trace[1]=='P' && trace[2]=='T');
    assert(trace[3]=='R' && trace[4]=='C' && trace[5]=='T');
    assert(trace[6]=='R' && trace[7]=='O');
    return 0;
}
