/* Test-only whole-call fixture: native/source create followed by one process.
 * The callback table is fixture input at the authentic SRAM address. */
#include <stdint.h>
static unsigned char pool[32u*65536u];
static uint32_t allocations,releases;
static uint32_t fixture_hash(const void *memory,uint32_t length)
{
    const uint8_t *bytes=(const uint8_t *)memory;
    uint32_t value=2166136261u;
    for (uint32_t i=0;i<length;++i)
        value=(value^bytes[i])*16777619u;
    return value;
}
static uint8_t output[4096];
static uint32_t imcra_work[65536];
static volatile uint32_t ring_counter,energy_first_use;
static void *test_allocate(uint32_t size)
{
    if (allocations>=32u || size>65536u) return 0;
    return &pool[(allocations++)*65536u];
}
static void test_release(void *ptr)
{
    if ((uintptr_t)ptr<(uintptr_t)pool ||
        (uintptr_t)ptr>=(uintptr_t)(pool+sizeof pool)) { releases=100u; return; }
#ifdef ACTIVE_PRODUCT_TABLE_SLICES
    if (allocations>17u) {
        uint32_t index=(uint32_t)(((uintptr_t)ptr-(uintptr_t)pool)/65536u);
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=index;
        const uint32_t *words=(const uint32_t *)ptr;
        for (uint32_t i=0;i<4u;++i)
            *(volatile uint32_t *)(uintptr_t)0xffffc040u=words[i];
    }
#endif
    ++releases;
}
typedef void *(*create_fn)(int,int,int,int,float,float,float,float,int,
                           float,float,int,int,const int *);
typedef void (*process_fn)(const uint32_t *,uint8_t *,uint32_t,uint32_t);
typedef int (*angle_fn)(void *,int,const int16_t *);
/* Test-only application of the authenticated native 0x1000d1fc work-buffer
 * layout. The real product initializer calls that body after core create;
 * this fixture has no initialized diagnostic transport for its log call. */
static void install_imcra_layout(uint32_t *ctx,uint32_t base)
{
    uint32_t channels=ctx[0x08/4], band_stride=ctx[0x04/4];
    uint32_t history=ctx[0x0c/4], hop=ctx[0x10/4];
    uint32_t bins=ctx[0x18/4], count=ctx[0x1c/4];
    uint32_t bin_bytes=channels*bins*4u;
    uint32_t region=base+ctx[0x14/4]*2u;
    uint32_t band_count=band_stride*channels;
    ctx[0x78/4]=region; region+=bin_bytes;
    ctx[0x84/4]=base;
    ctx[0x7c/4]=region; region+=bin_bytes;
    ctx[0x6c/4]=region; region+=band_count*8u;
    ctx[0xcc/4]=region; region+=(band_count-channels)*8u;
    ctx[0xc8/4]=region; region+=channels*8u;
    ctx[0xd0/4]=region; region+=channels*8u;
    ctx[0x68/4]=region; region+=channels*8u;
    ctx[0x90/4]=region; region+=bin_bytes;
    ctx[0x88/4]=region;
    region+=(history+(channels-1u)*hop)*2u;
    ctx[0x80/4]=region;
    region+=count*(history-hop)*2u;
    ctx[0xa0/4]=region; region+=bins*4u;
    ctx[0x98/4]=region;
    ctx[0x9c/4]=region+bins*4u;
}
#ifdef SOURCE_MODE
extern void *gx8002_image_b_beamforming_core_1000ce14(
    int,int,int,int,float,float,float,float,int,float,float,int,int,const int *);
extern void gx8002_image_b_process_whole_experimental(
    const uint32_t *,uint8_t *,uint32_t,uint32_t,
    volatile uint32_t *,volatile uint32_t *);
extern int gx8002_image_b_beamforming_angles_1000c6e8(
    void *,int,const int16_t *);
#ifdef SOURCE_BOUND_CORE
extern void gx8002_image_b_beamforming_process_core_1000d46c(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
#endif
#endif
int main(void)
{
#ifndef SOURCE_MODE
    /* Test-only reproduction of the native initialized-data copy.  The
     * sealed stock image owns 0x10016f60..0x1001708b; the loaded image's
     * runtime alias begins at 0x20016f60.  This includes the RIFFT profile
     * consumed at 0x1000dc72, without inventing descriptor fields. */
    for (uint32_t i=0;i<0x12cu;++i)
        *(volatile uint8_t *)(uintptr_t)(0x20016f60u+i)=
            *(const volatile uint8_t *)(uintptr_t)(0x10016f60u+i);
#endif
    volatile uint32_t *ops=(volatile uint32_t *)(uintptr_t)0x2002d7a4u;
    ops[0]=(uint32_t)(uintptr_t)test_allocate;
    ops[3]=(uint32_t)(uintptr_t)test_release;
    const int outputs[1]={1};
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x1111u;
#ifdef SOURCE_MODE
    uint32_t *ctx=gx8002_image_b_beamforming_core_1000ce14(
#else
    uint32_t *ctx=((create_fn)(uintptr_t)0x1000ce14)(
#endif
        16000,2,3,1,0.0f,2.0f,0.035f,1.0f,0,0.2f,0.01f,0,1,outputs);
    if (!ctx) return 1;
#ifdef ACTIVE_PRODUCT_ANGLES
    static const int16_t product_angles[3]={35,45,55};
#ifdef SOURCE_MODE
    int angle_status=gx8002_image_b_beamforming_angles_1000c6e8(
        ctx,3,product_angles);
#else
    int angle_status=((angle_fn)(uintptr_t)0x1000c6e8)(
        ctx,3,product_angles);
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=(uint32_t)angle_status;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        fixture_hash((const void *)(uintptr_t)ctx[0xa4/4],
                     2u*3u*257u*8u);
#ifdef ACTIVE_PRODUCT_TABLE_WORDS
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x54424c45u;
    const uint32_t *all_phase_words=
        (const uint32_t *)(uintptr_t)ctx[0xa4/4];
    for (uint32_t i=0;i<2u*3u*257u*2u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=all_phase_words[i];
#endif
#ifdef ACTIVE_PRODUCT_TABLE_SLICES
    const uint8_t *phase=(const uint8_t *)(uintptr_t)ctx[0xa4/4];
    for (uint32_t i=0;i<16u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=
            ((const uint32_t *)(const void *)phase)[i];
    for (uint32_t i=0;i<2u*3u*257u*8u;i+=256u) {
        uint32_t count=2u*3u*257u*8u-i;
        if (count>256u) count=256u;
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=
            fixture_hash(phase+i,count);
    }
#endif
#endif
    install_imcra_layout(ctx,(uint32_t)(uintptr_t)imcra_work);
#ifdef ACTIVE_INITIAL_STATE
    ring_counter=2u;
    energy_first_use=1u;
    *(volatile uint32_t *)(uintptr_t)0x2002d7a0u=2u;
    *(volatile uint32_t *)(uintptr_t)0x2002d79cu=1u;
#endif
#ifdef SHORT_ACTIVE_BAND
    /* Explicit fixture mutation after create: NaN takes the native
     * unordered band path and sets a single first band. */
    ctx[0x34/4]=0x7fc00000u;
    ctx[0x4c/4]=0u;
    ctx[0x50/4]=0u;
    ctx[0x08/4]=1u;
#endif
#ifdef ACTIVE_INPUT_IMPULSE
    int16_t *input=(int16_t *)(uintptr_t)ctx[0x90/4];
    for (uint32_t c=0;c<ctx[0x08/4];++c) {
        uint32_t step=ctx[0x18/4];
        input[c*step]= (int16_t)(4096u+1024u*c);
        input[c*step+1u]=(int16_t)(-512-(int)c*128);
    }
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint16_t)input[0];
#endif
#ifdef ACTIVE_INPUT_DC
    int16_t *input_dc=(int16_t *)(uintptr_t)ctx[0x90/4];
    for (uint32_t c=0;c<ctx[0x08/4];++c)
        for (uint32_t i=0;i<ctx[0x18/4];++i)
            input_dc[c*ctx[0x18/4]+i]=(int16_t)(4000+1000*c);
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint16_t)input_dc[0];
#endif
#ifdef ACTIVE_OVERLAP_HISTORY
    int16_t *history=(int16_t *)(uintptr_t)ctx[0x80/4];
    for (uint32_t i=0;i<ctx[0x0c/4]-ctx[0x10/4];++i)
        history[i]=(int16_t)(30000+(int16_t)(i&127u));
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint16_t)history[0];
    const int32_t *window_before=(const int32_t *)(uintptr_t)ctx[0x74/4];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)window_before[128];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)window_before[256];
#endif
#ifdef ACTIVE_HIGH_GAIN
    /* Explicit product gain word, with the native output gain multiplier. */
    ctx[0x2c/4]=0x447a0000u; /* 1000.0f */
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x2222u;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx[0x08/4];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx[0x18/4];
#ifdef STOP_BEFORE_PROCESS
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=allocations;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=releases;
    return (ctx[0x08/4]==3u && ctx[0x18/4]==257u &&
            allocations==17u && releases==1u)?0:31;
#endif
#ifdef ACTIVE_REPEAT
    for (uint32_t pass=0;pass<8u;++pass) {
#endif
#if defined(SOURCE_MODE) && defined(SOURCE_BOUND_CORE)
        gx8002_image_b_beamforming_process_core_1000d46c(
            (uint32_t)(uintptr_t)ctx,(uint32_t)(uintptr_t)output,0u,0u,0u);
#elif defined(SOURCE_MODE)
        gx8002_image_b_process_whole_experimental(
            ctx,output,0u,0u,&ring_counter,&energy_first_use);
#else
        ((process_fn)(uintptr_t)0x1000d46c)(ctx,output,0u,0u);
#endif
#ifdef ACTIVE_REPEAT
    }
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=allocations;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=releases;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)output[0]|((uint32_t)output[1]<<8);
#if defined(SOURCE_MODE) && !defined(SOURCE_BOUND_CORE)
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ring_counter;
#else
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        *(const volatile uint32_t *)(uintptr_t)0x2002d7a0u;
#endif
    const uint16_t *scratch=(const uint16_t *)(uintptr_t)ctx[0xb4/4];
#ifdef ACTIVE_OVERLAP_HISTORY
    const int16_t *history_after=(const int16_t *)(uintptr_t)ctx[0x80/4];
    const int16_t *mixed_after=(const int16_t *)(uintptr_t)ctx[0x88/4];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint16_t)history_after[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint16_t)mixed_after[256];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)output[512]|((uint32_t)output[513]<<8);
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=scratch[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=scratch[1];
    uint32_t output_sum=0u;
    for (uint32_t i=0;i<sizeof output;++i)
        output_sum=(output_sum*16777619u)^(uint32_t)output[i];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=output_sum;
#ifdef ACTIVE_DUMP_OUTPUT_WORDS
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x4f555450u;
    for (uint32_t i=0;i<sizeof output/4u;++i) {
        const uint8_t *b=output+i*4u;
        uint32_t value=(uint32_t)b[0]|((uint32_t)b[1]<<8)|
            ((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=value;
    }
#endif
    const uint16_t *transformed=
        (const uint16_t *)(uintptr_t)ctx[0x84/4];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        (uint32_t)transformed[0]|((uint32_t)transformed[1]<<16);
    const uint16_t *processed_input=
        (const uint16_t *)(uintptr_t)ctx[0x90/4];
    uint32_t input_sum=0u;
    for (uint32_t i=0;i<ctx[0x08/4]*ctx[0x18/4];++i)
        input_sum=(input_sum*16777619u)^(uint32_t)processed_input[i];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=input_sum;
    return 0;
}
