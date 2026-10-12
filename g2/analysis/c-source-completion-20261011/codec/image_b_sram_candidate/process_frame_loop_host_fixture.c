#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern void gx8002_image_b_process_frame_loop_experimental(const uint32_t *);
static unsigned calls;
static const uint32_t *saved_ctx;
void gx8002_image_b_process_diagonal_frame_verified_chunk(
    const uint32_t *ctx,uint32_t selected)
{
    assert(ctx==saved_ctx && calls%4u==0u);
    assert(selected==(calls/4u==0u?48u:48u+3u*5u*8u));
    ++calls;
}
void gx8002_image_b_process_pack_verified_chunk(
    const uint32_t *ctx,uint32_t band)
{
    assert(ctx==saved_ctx && calls%4u==1u);
    assert(band==(calls/4u)*4u);
    ++calls;
}
void gx8002_image_b_process_matrix_stage_verified_chunk(
    const uint32_t *ctx,uint32_t selected,uint32_t coeff,uint32_t band)
{
    assert(ctx==saved_ctx && calls%4u==2u);
    unsigned frame=calls/4u;
    assert(selected==48u+frame*3u*5u*8u);
    assert(coeff==frame*(2u*3u-2u)*4u && band==frame*4u);
    ++calls;
}
int gx8002_image_b_process_adapt_stage_verified_chunk(
    const uint32_t *ctx,uint32_t energy,uint32_t coeff,
    uint32_t band,float scratch[14])
{
    assert(ctx==saved_ctx && calls%4u==3u);
    unsigned frame=calls/4u;
    assert(energy==2u*2u*4u+frame*4u);
    assert(coeff==frame*(2u*3u-2u)*4u && band==frame*4u);
    if (frame==0u) scratch[0]=9.0f;
    else assert(scratch[0]==9.0f);
    ++calls;
    return 0;
}
int main(void)
{
    uint32_t *selected=mmap((void *)0x19e00000,4096,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,
        -1,0);
    assert(selected==(void *)0x19e00000);
    *selected=2u;
    uint32_t ctx[0x5c/4+1]={0};
    ctx[0x04/4]=3u;
    ctx[0x18/4]=2u;
    ctx[0x1c/4]=5u;
    ctx[0x5c/4]=0x19e00000u;
    saved_ctx=ctx;
    gx8002_image_b_process_frame_loop_experimental(ctx);
    assert(calls==8u);
    ctx[0x18/4]=0u;
    gx8002_image_b_process_frame_loop_experimental(ctx);
    assert(calls==8u);
    return 0;
}
