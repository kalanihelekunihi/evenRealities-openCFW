/* Native image-B 0x1000ed2c..0x1000ed7b, IMCRA D finishing policy.
 * C-SKY direct ISA: positive input -> -1; input <-80 -> zero gain;
 * otherwise store input at +0x10 and 10^(input/20) at +0x3c.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
extern float gx8002_image_b_power_float_100100a4(float,float);
int32_t gx8002_image_b_imcra_d_finish_1000ed2c(void *destination, float level)
{
    uint8_t *b=(uint8_t *)destination;
    if (0.0f < level) return -1;
    if (level < -80.0f) {
        *(float *)(void *)(b + 0x3c) = 0.0f;
        return 0;
    }
    *(float *)(void *)(b + 0x10) = level;
    *(float *)(void *)(b + 0x3c) =
        gx8002_image_b_power_float_100100a4(10.0f, level / 20.0f);
    return 0;
}
