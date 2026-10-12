/* Image-B native 0x1000ed7c..0x1000ee63: IMCRA D record constructor.
 * The two decay calculations follow the native float -> binary64 exp ->
 * float path. The binary64 exp provider is a genuine remaining source body.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
#include <stddef.h>

extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern float gx8002_image_b_power_float_100100a4(float, float);
extern float gx8002_image_b_logf_entry_100100ac(float);
extern double gx8002_image_b_exp_double_1000f84c(double);

void *gx8002_image_b_imcra_d_init_1000ed7c(
    void *destination, float value, float span0, float span1,
    float span2, float sample_rate)
{
    gx8002_image_b_zero_100113c4(destination, 0u, 64u);
    if (destination == NULL) return NULL;

    uint8_t *b = (uint8_t *)destination;
    *(float *)(void *)(b + 0x00) = value;
    *(float *)(void *)(b + 0x04) = span0;
    *(float *)(void *)(b + 0x08) = span1;
    *(float *)(void *)(b + 0x0c) = span2;
    *(float *)(void *)(b + 0x14) = sample_rate;
    *(float *)(void *)(b + 0x18) = sample_rate * span2;
    *(float *)(void *)(b + 0x1c) =
        gx8002_image_b_power_float_100100a4(10.0f, value / 20.0f);

    float logarithm = gx8002_image_b_logf_entry_100100ac(9.0f);
    float argument0 = -logarithm / (sample_rate * span0);
    *(float *)(void *)(b + 0x20) =
        (float)gx8002_image_b_exp_double_1000f84c((double)argument0);
    logarithm = gx8002_image_b_logf_entry_100100ac(9.0f);
    float argument1 = -logarithm / (sample_rate * span1);
    *(float *)(void *)(b + 0x24) =
        (float)gx8002_image_b_exp_double_1000f84c((double)argument1);
    return destination;
}
