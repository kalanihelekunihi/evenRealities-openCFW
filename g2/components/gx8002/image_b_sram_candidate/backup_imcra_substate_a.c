/* Native image-B IMCRA substate-A constructor 0x1000ea74 and three
 * native size queries 0x1000ea68, 0x1000eb48, 0x1000ec2c.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * C arguments name the native fr0-fr3 and two incoming stack words;
 * parent C and child C must share this prototype at final integration.
 */
#include <stdint.h>
#include <stddef.h>
typedef union { float f; uint32_t u; } gx_imcra_word;
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern float gx8002_image_b_logf_10010768(float);
extern float gx8002_image_b_expf_100109c0(float);

uint32_t gx8002_image_b_imcra_a_size_1000ea68(const void *state, int mode)
{
    (void)state;
    return mode != 0 ? 48u : 0u;
}
uint32_t gx8002_image_b_imcra_b_size_1000eb48(const void *state, int mode)
{
    (void)state;
    return mode != 0 ? 52u : 0u;
}
uint32_t gx8002_image_b_imcra_c_size_1000ec2c(const void *state, int mode)
{
    (void)state;
    return mode != 0 ? 64u : 0u;
}

void *gx8002_image_b_imcra_a_init_1000ea74(
    void *destination, float value0, float value1, float span0, float span1,
    uint32_t setting, float sample_rate)
{
    gx8002_image_b_zero_100113c4(destination, 0u, 48u);
    if (destination == NULL) return NULL;
    uint8_t *b = (uint8_t *)destination;
    *(float *)(void *)(b + 0x00) = value0;
    *(float *)(void *)(b + 0x04) = value1;
    *(float *)(void *)(b + 0x08) = span0;
    *(float *)(void *)(b + 0x0c) = span1;
    *(uint32_t *)(void *)(b + 0x10) = setting;
    uint32_t samples = (uint32_t)sample_rate;
    *(uint32_t *)(void *)(b + 0x14) = samples;
    float log_window = gx8002_image_b_logf_10010768(9.0f);
    *(float *)(void *)(b + 0x20) = gx8002_image_b_expf_100109c0(
        -log_window / ((float)samples * span0));
    *(float *)(void *)(b + 0x24) = gx8002_image_b_expf_100109c0(
        -log_window / ((float)samples * span1));
    if (b[0x2c] == 0u) {
        *(uint32_t *)(void *)(b + 0x18) = 0u;
        *(uint32_t *)(void *)(b + 0x1c) = 0u;
        *(uint32_t *)(void *)(b + 0x28) = 0u;
    }
    b[0x2c] = 1u;
    return destination;
}
