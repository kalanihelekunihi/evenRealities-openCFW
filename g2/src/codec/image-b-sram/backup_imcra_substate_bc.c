/* Native image-B 0x1000eb54 and 0x1000ec38 IMCRA substate constructors.
 * Both accept fr0-fr3 plus three incoming stack floats after destination.
 * Native SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
#include <stddef.h>
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern float gx8002_image_b_logf_10010768(float);
extern float gx8002_image_b_expf_100109c0(float);

void *gx8002_image_b_imcra_b_init_1000eb54(
    void *destination, float value0, float value1, float value2, float span0,
    float span1, float span2, float sample_rate)
{
    gx8002_image_b_zero_100113c4(destination, 0u, 52u);
    if (destination == NULL) return NULL;
    uint8_t *b = (uint8_t *)destination;
    *(float *)(void *)(b + 0x00) = value0;
    *(float *)(void *)(b + 0x04) = value1;
    *(float *)(void *)(b + 0x08) = value2;
    *(float *)(void *)(b + 0x0c) = span0;
    *(float *)(void *)(b + 0x10) = span1;
    *(float *)(void *)(b + 0x14) = span2;
    uint32_t samples = (uint32_t)sample_rate;
    *(uint32_t *)(void *)(b + 0x18) = samples;
    float log_window = gx8002_image_b_logf_10010768(9.0f);
    *(float *)(void *)(b + 0x24) = gx8002_image_b_expf_100109c0(
        -log_window / ((float)samples * span0));
    *(float *)(void *)(b + 0x28) = gx8002_image_b_expf_100109c0(
        -log_window / ((float)samples * span1));
    if (b[0x30] == 0u) {
        *(uint32_t *)(void *)(b + 0x1c) = 0u;
        *(uint32_t *)(void *)(b + 0x20) = 0u;
        *(uint32_t *)(void *)(b + 0x2c) = 0u;
    }
    b[0x30] = 1u;
    return destination;
}

void *gx8002_image_b_imcra_c_init_1000ec38(
    void *destination, float value0, float value1, float value2, float span0,
    float span1, float span2, float sample_rate)
{
    gx8002_image_b_zero_100113c4(destination, 0u, 64u);
    if (destination == NULL) return NULL;
    uint8_t *b = (uint8_t *)destination;
    *(float *)(void *)(b + 0x00) = value0;
    *(float *)(void *)(b + 0x04) = value1;
    *(float *)(void *)(b + 0x08) = value2;
    *(float *)(void *)(b + 0x0c) = span0;
    *(float *)(void *)(b + 0x10) = span1;
    *(float *)(void *)(b + 0x14) = span2;
    uint32_t samples = (uint32_t)sample_rate;
    *(uint32_t *)(void *)(b + 0x18) = samples;
    float log_window = gx8002_image_b_logf_10010768(9.0f);
    *(float *)(void *)(b + 0x24) = gx8002_image_b_expf_100109c0(
        -log_window / ((float)samples * span0));
    *(float *)(void *)(b + 0x28) = gx8002_image_b_expf_100109c0(
        -log_window / ((float)samples * span1));
    *(int32_t *)(void *)(b + 0x2c) = (int32_t)((float)samples * span2);
    if (b[0x3c] == 0u) {
        *(uint32_t *)(void *)(b + 0x1c) = 0u;
        *(uint32_t *)(void *)(b + 0x20) = 0u;
        *(uint32_t *)(void *)(b + 0x30) = 0u;
        *(uint32_t *)(void *)(b + 0x34) = 0u;
        *(uint32_t *)(void *)(b + 0x38) = 0u;
    }
    b[0x3c] = 1u;
    return destination;
}
