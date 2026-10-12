/* Image-B native 0x1000e784..0x1000e8f1: IMCRA composite constructor.
 * Its two integer inputs are passed in r0/r1, destination in r2. Native
 * fr0-fr3 and incoming stack-word inputs to each child are spelled out in
 * the child prototypes below. Product floats at 0x20016fb8..0x20017008
 * and control word 0x2002d7b4 remain genuine initialized-data contracts.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
#include <stddef.h>
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern void *gx8002_image_b_imcra_a_init_1000ea74(
    void *, float, float, float, float, uint32_t, float);
extern uint32_t gx8002_image_b_imcra_a_size_1000ea68(const void *, int);
extern void *gx8002_image_b_imcra_b_init_1000eb54(
    void *, float, float, float, float, float, float, float);
extern uint32_t gx8002_image_b_imcra_b_size_1000eb48(const void *, int);
extern void *gx8002_image_b_imcra_c_init_1000ec38(
    void *, float, float, float, float, float, float, float);
extern uint32_t gx8002_image_b_imcra_c_size_1000ec2c(const void *, int);
extern void *gx8002_image_b_imcra_d_init_1000ed7c(
    void *, float, float, float, float, float);
extern int32_t gx8002_image_b_imcra_d_finish_1000ed2c(void *, float);
extern volatile uint32_t gx8002_image_b_imcra_cfg_words_20016fb8[21];
extern volatile uint32_t gx8002_image_b_imcra_setting_2002d7b4;
typedef union { uint32_t word; float number; } gx_imcra_value;
static float gx_imcra_config_float(uint32_t address)
{
    gx_imcra_value v;
    v.word = gx8002_image_b_imcra_cfg_words_20016fb8[
        (address - UINT32_C(0x20016fb8)) / 4u];
    return v.number;
}
#define CFG(address) gx_imcra_config_float(address)
#define CFG_WORD(address) gx8002_image_b_imcra_cfg_words_20016fb8[((address) - 0x20016fb8u) / 4u]

void *gx8002_image_b_imcra_constructor_1000e784(
    int32_t frame_rate, int32_t frame_samples, void *destination)
{
    uint8_t *const base = (uint8_t *)destination;
    gx8002_image_b_zero_100113c4(destination, 0u, 40u);
    uint32_t *header = (uint32_t *)(void *)base;
    header[2] = header[3] = header[4] = header[5] = 0u;
    header[0] = (uint32_t)frame_rate;
    header[1] = (uint32_t)frame_samples;
    float rate = (float)frame_rate;
    float samples = (float)frame_samples;
    uint8_t *next = base + 40u;

    void *a = gx8002_image_b_imcra_a_init_1000ea74(
        next, CFG(0x20016ff4u), CFG(0x20016fecu),
        CFG(0x20016fe8u) / samples, CFG(0x20016ff0u) / samples,
        gx8002_image_b_imcra_setting_2002d7b4, rate);
    header[6] = (uint32_t)(uintptr_t)a;
    next += gx8002_image_b_imcra_a_size_1000ea68(a, 2);

    void *b = gx8002_image_b_imcra_b_init_1000eb54(
        next, CFG(0x20016fccu), CFG(0x20016fc4u), CFG(0x20016fbcu),
        CFG(0x20016fb8u) / samples, CFG(0x20016fc8u) / samples,
        CFG(0x20016fc0u), rate);
    header[7] = (uint32_t)(uintptr_t)b;
    next += gx8002_image_b_imcra_b_size_1000eb48(b, 2);

    void *c = gx8002_image_b_imcra_c_init_1000ec38(
        next, CFG(0x20016fe4u), CFG(0x20016fdcu), CFG(0x20016fd8u),
        CFG(0x20016fd0u) / samples, CFG(0x20016fe0u) / samples,
        CFG(0x20016fd4u) / samples, rate);
    header[8] = (uint32_t)(uintptr_t)c;
    next += gx8002_image_b_imcra_c_size_1000ec2c(c, 2);

    void *d = gx8002_image_b_imcra_d_init_1000ed7c(
        next, CFG(0x20017008u), CFG(0x20016ff8u) / samples,
        CFG(0x20017004u) / samples, CFG(0x20017000u), rate);
    header[9] = (uint32_t)(uintptr_t)d;
    (void)gx8002_image_b_imcra_d_finish_1000ed2c(d, CFG(0x20016ffcu));
    return destination;
}
#undef CFG
#undef CFG_WORD
