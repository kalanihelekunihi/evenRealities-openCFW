#define _GNU_SOURCE
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stddef.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
volatile uint32_t gx8002_image_b_dsp_config_2002d7a4[4];
static uint32_t sizes[32]; static void *addresses[32]; static int count;
static void *alloc_low(uint32_t size) {
    uintptr_t address=0x10000000u+(uintptr_t)count*0x10000u;
    void *p=mmap((void *)address,0x10000,PROT_READ|PROT_WRITE,
                 MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)address && size<=0x10000 && count<32);
    sizes[count]=size; addresses[count]=p; ++count; return p;
}
static void *releases[8]; static int release_count;
static void release_low(void *p) { assert(release_count<8); releases[release_count++]=p; }
static int mismatch_diagnostic_count;
int gx8002_image_b_heap_log_10009934(const char *format, ...) {
    assert(strcmp(format,
        "You must set the beamforming_angle_num equal as you set before")==0);
    ++mismatch_diagnostic_count;
    return 0;
}
void gx8002_image_b_zero_100113c4(void *p,uint32_t value,uint32_t n) {
    assert(value==0); unsigned char *b=p; for(uint32_t i=0;i<n;++i)b[i]=0;
}
float gx8002_image_b_sin_float_1000ded0(float x) { return sinf(x); }
void gx8002_image_b_sin_float_array_1000dee0(float *out,const float *in,int n) {
    for(int i=0;i<n;++i)out[i]=sinf(in[i]);
}
void gx8002_image_b_cos_float_array_1000df0c(float *out,const float *in,int n) {
    for(int i=0;i<n;++i)out[i]=cosf(in[i]);
}
float gx8002_image_b_native_reciprocal_f32(float x) { return 1.0f/x; }
extern void *gx8002_image_b_beamforming_core_whole_candidate(
    int,int,int,int,float,float,float,float,int,float,float,int,int,const int *);
extern int gx8002_image_b_beamforming_angles_whole_candidate(
    void *,int,const int16_t *);
struct gx8002_image_b_process_prepare {
    uint32_t first_threshold_address,second_threshold_address;
    uint32_t coefficient_address,ring_row_address;
};
extern void gx8002_image_b_process_prepare_verified_chunk(
    const uint32_t *,uint32_t,uint32_t,int32_t,
    struct gx8002_image_b_process_prepare *);
extern void gx8002_image_b_energy_prefix_verified_chunk(
    const uint32_t *,const int16_t *,int32_t,volatile uint32_t *);
extern void gx8002_image_b_energy_smoothing_verified_chunk(
    const uint32_t *,int32_t,int32_t);
extern void gx8002_image_b_energy_gain_numeric_verified_chunk(
    const uint32_t *,int16_t *,int32_t);
int main(void) {
    assert((uintptr_t)&alloc_low<=UINT32_MAX);
    assert((uintptr_t)&release_low<=UINT32_MAX);
    gx8002_image_b_dsp_config_2002d7a4[0]=(uint32_t)(uintptr_t)&alloc_low;
    gx8002_image_b_dsp_config_2002d7a4[3]=(uint32_t)(uintptr_t)&release_low;
    const int outputs[]={1};
    uint32_t *ctx=gx8002_image_b_beamforming_core_whole_candidate(
        16000,2,3,1,0.0f,2.0f,0.035f,1.0f,0,0.2f,0.01f,0,1,outputs);
    assert(ctx==addresses[0]); assert(count==17);
    static const uint32_t expected_sizes[]={220,400,12,2048,3072,6,
        12336,30,12,8,3084,16,16,6168,12,4,6144};
    for (int i=0;i<17;++i) assert(sizes[i]==expected_sizes[i]);
    assert(release_count==1 && releases[0]==addresses[16]);
    assert(ctx[0x04/4]==2 && ctx[0x08/4]==3);
    assert(ctx[0x0c/4]==512 && ctx[0x18/4]==257);
    assert(ctx[0x1c/4]==3 && ctx[0x58/4]==1);
    assert(ctx[0xa8/4]==(uint32_t)(uintptr_t)addresses[14]);
    assert(((uint32_t *)addresses[14])[0]==0x40875c29u);
    assert(((uint32_t *)addresses[14])[1]==0x40875c29u);
    assert(((uint32_t *)addresses[15])[0]==1u);
    const int16_t degrees[]={-30,0,30};
    assert(gx8002_image_b_beamforming_angles_whole_candidate(ctx,3,degrees)==0);
    assert(count==23 && release_count==7);
    static const uint32_t angle_sizes[]={12,8,8,8,24,12};
    for(int i=0;i<6;++i) {
        assert(sizes[17+i]==angle_sizes[i]);
        assert(releases[1+i]==addresses[17+i]);
    }
    assert(ctx[0x60/4]==1);
    float *radians=(float *)(uintptr_t)ctx[0x64/4];
    assert(fabsf(radians[0]+0.5235988f)<0.00001f);
    assert(radians[1]==0.0f);
    assert(fabsf(radians[2]-0.5235988f)<0.00001f);
    float *table=(float *)(uintptr_t)ctx[0xa4/4];
    for(int mic=0;mic<2;++mic) {
        assert(table[2*mic]==0.0f);
        assert(table[2*mic+1]==1.0f);
    }
    assert(gx8002_image_b_beamforming_angles_whole_candidate(ctx,2,degrees)==-1);
    assert(ctx[0x60/4]==0 && count==23 && release_count==7);
    assert(mismatch_diagnostic_count==1);
    ctx[0x78/4]=0x20000000u; ctx[0x7c/4]=0x20001000u;
    int16_t *ring=(int16_t *)(uintptr_t)ctx[0xac/4];
    int16_t *scratch=(int16_t *)(uintptr_t)ctx[0xb4/4];
    for(int i=0;i<15;++i) ring[i]=9;
    for(int i=0;i<4;++i) scratch[i]=9;
    struct gx8002_image_b_process_prepare setup;
    gx8002_image_b_process_prepare_verified_chunk(ctx,7u,9u,3,&setup);
    assert(setup.first_threshold_address==0x20000024u);
    assert(setup.second_threshold_address==0x20001024u);
    assert(setup.coefficient_address==ctx[0xa4/4]+444u);
    assert(setup.ring_row_address==ctx[0xac/4]+12u);
    for(int i=0;i<4;++i) assert(scratch[i]==0);
    for(int i=0;i<15;++i) assert(ring[i]==(i>=6 && i<9?0:9));
    uint32_t *energy=alloc_low(24), *scaled=alloc_low(24), *baseline=alloc_low(24);
    ctx[0x18/4]=3;
    ctx[0xa0/4]=(uint32_t)(uintptr_t)energy;
    ctx[0x98/4]=(uint32_t)(uintptr_t)scaled;
    ctx[0x9c/4]=(uint32_t)(uintptr_t)baseline;
    const int16_t samples[]={3,4,-5,12,-32768,-32768};
    volatile uint32_t first_use=0;
    gx8002_image_b_energy_prefix_verified_chunk(ctx,samples,1,&first_use);
    assert(first_use==1);
    assert(energy[3]==25 && energy[4]==169 && energy[5]==0x80000000u);
    assert(scaled[3]==0 && scaled[4]==1 && scaled[5]==0xff000000u);
    assert(baseline[3]==127 && baseline[4]==127 && baseline[5]==127);
    const int16_t silence[]={0,0,0,0,0,0};
    gx8002_image_b_energy_prefix_verified_chunk(ctx,silence,1,&first_use);
    assert(energy[3]==0 && energy[4]==0 && energy[5]==0);
    assert(scaled[4]==1 && baseline[5]==127);
    scaled[3]=128; scaled[4]=256; energy[3]=256; energy[4]=1024;
    gx8002_image_b_energy_smoothing_verified_chunk(ctx,1,0);
    assert(scaled[3]==128 && scaled[4]==256);
    gx8002_image_b_energy_smoothing_verified_chunk(ctx,1,1);
    assert(scaled[3]==107 && scaled[4]==215);
    for(int i=3;i<6;++i) { energy[i]=0; scaled[i]=0; baseline[i]=0; }
    int16_t gain_samples[]={32767,-32768,1000,-1000,0,0};
    gx8002_image_b_energy_gain_numeric_verified_chunk(ctx,gain_samples,1);
    assert(baseline[3]==0 && baseline[4]==0 && baseline[5]==0);
    assert(gain_samples[0]==9829 && gain_samples[1]==-9830);
    assert(gain_samples[2]==299 && gain_samples[3]==-300);
    puts("create and angle whole host 32-bit-address fixture PASS");
}
