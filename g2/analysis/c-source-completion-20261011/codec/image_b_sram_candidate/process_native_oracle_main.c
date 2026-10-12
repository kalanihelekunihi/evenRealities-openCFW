#include <stdint.h>
static uint32_t ctx[0xd4/4+1];
static uint32_t selected_row;
static uint16_t scratch[8];
static uint16_t source[8],mixed[8],transformed[8];
static uint32_t output_window[8];
static uint8_t output[16];
static volatile uint32_t observed_ring_counter;
static volatile uint32_t energy_first_use_word;
typedef void (*gx8002_native_process)(
    const uint32_t *,uint8_t *,uint32_t,uint32_t);
#ifdef SOURCE_MODE
extern void gx8002_image_b_process_whole_experimental(
    const uint32_t *,uint8_t *,uint32_t,uint32_t,
    volatile uint32_t *,volatile uint32_t *);
#endif
int main(void)
{
    ctx[0x04/4]=1u;
    ctx[0x08/4]=0u;
    ctx[0x0c/4]=0u;
    ctx[0x10/4]=0u;
    ctx[0x18/4]=0u;
    ctx[0x1c/4]=1u;
    ctx[0x34/4]=0u;
    ctx[0x48/4]=1u;
    ctx[0x5c/4]=(uint32_t)(uintptr_t)&selected_row;
    ctx[0x78/4]=(uint32_t)(uintptr_t)source;
    ctx[0x7c/4]=(uint32_t)(uintptr_t)source;
    ctx[0x80/4]=(uint32_t)(uintptr_t)source;
    ctx[0x84/4]=(uint32_t)(uintptr_t)transformed;
    ctx[0x88/4]=(uint32_t)(uintptr_t)mixed;
    ctx[0x74/4]=(uint32_t)(uintptr_t)output_window;
    ctx[0xb4/4]=(uint32_t)(uintptr_t)scratch;
    scratch[0]=0x7777u;
    output[0]=0x5au;
#ifdef SOURCE_MODE
    gx8002_image_b_process_whole_experimental(
        ctx,output,0u,0u,&observed_ring_counter,&energy_first_use_word);
#else
    ((gx8002_native_process)(uintptr_t)0x1000d46c)(ctx,output,0u,0u);
#endif
    if (scratch[0]!=0u) return 1;
    if (output[0]!=0x5au) return 2;

    ctx[0x0c/4]=3u;
    ctx[0x10/4]=1u;
    ctx[0x2c/4]=0x3f800000u;
    source[0]=1000u; source[1]=2000u;
    mixed[2]=3000u; mixed[3]=4000u;
    output_window[0]=16384u; output_window[1]=16384u;
    scratch[0]=0x7777u;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx[0x0c/4];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx[0x10/4];
#ifdef SOURCE_MODE
    gx8002_image_b_process_whole_experimental(
        ctx,output,0u,0u,&observed_ring_counter,&energy_first_use_word);
#else
    ((gx8002_native_process)(uintptr_t)0x1000d46c)(ctx,output,0u,0u);
#endif
    if (scratch[0]!=0u) return 3;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=source[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=source[1];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)output[0]|((uint32_t)output[1]<<8);
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)output[2]|((uint32_t)output[3]<<8);
    if (source[0]!=1000u || source[1]!=2000u) return 4;
    if (output[0]!=0x5au || output[1]!=0u) return 5;
    if (output[2]!=0u || output[3]!=0u) return 6;
    return 0;
}
