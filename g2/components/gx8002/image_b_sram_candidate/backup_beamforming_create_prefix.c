/* Native GSC create core 0x1000ce14..0x1000cf04, decoded as a bounded
 * source chunk. The caller supplies the operation-table allocator and the
 * integer/FPR argument map authenticated at the 0x1000de40 wrapper. Native
 * assumes the 220-byte context allocation succeeds before its first store.
 * This is not the complete 0x1000ce14 provider.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

typedef union { float f; uint32_t u; } gx8002_bf_word;

uint32_t *gx8002_image_b_create_prefix_verified_chunk(
    void *(*allocate)(uint32_t), int32_t sample_rate, int32_t mic_count,
    int32_t angle_count, int32_t linear, float elevation, float gain,
    float mic_distance, float mic_radius, int32_t circular,
    float short_alpha, float long_alpha, int32_t output_count)
{
    uint32_t *ctx=(uint32_t *)allocate(220u);
    ctx[0x08/4]=3;
    ctx[0x0c/4]=512;
    ctx[0x14/4]=512;
    ctx[0x18/4]=257;
    ctx[0x48/4]=5;
    ctx[0x4c/4]=9;
    ctx[0x50/4]=59;
    ctx[0x54/4]=51;
    ctx[0x10/4]=256;
    ctx[0x00/4]=(uint32_t)sample_rate;
    gx8002_bf_word w={.f=elevation};ctx[0x28/4]=w.u;
    w.f=gain;ctx[0x2c/4]=w.u;
    w.f=mic_distance;ctx[0x34/4]=w.u;
    w.f=mic_radius;ctx[0x3c/4]=w.u;
    ctx[0xd4/4]=100;
    ctx[0x04/4]=(uint32_t)mic_count;
    ctx[0x1c/4]=(uint32_t)angle_count;
    ctx[0x30/4]=(uint32_t)linear;
    ctx[0x38/4]=(uint32_t)circular;
    w.f=short_alpha;ctx[0x40/4]=w.u;
    w.f=long_alpha;ctx[0x44/4]=w.u;
    ctx[0x58/4]=(uint32_t)output_count;
    ctx[0xd8/4]=(uint32_t)(uintptr_t)allocate(400u);
    ctx[0x60/4]=0;
    ctx[0x64/4]=(uint32_t)(uintptr_t)allocate((uint32_t)angle_count*4u);
    if ((uint32_t)linear+(uint32_t)circular != 1u)
        (void)gx8002_image_b_heap_log_10009934(
            "[error], please set linear array or circular array. If one of them is set, the another must unset, %s, %d\n",
            "lvp/vma/lavaliermic/gsc.c", 1091);
    return ctx; /* native continues at 0x1000cf04 */
}
