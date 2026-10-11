#include <stdint.h>

/* PCM2.1 temperature range classifier, native 0x5a0a70..0x5a0ae7.
 * The caller in the selected C graph uses the softfp float ABI.
 * Native stock receives its float in S0; the independent oracle
 * compares those two entry conventions with identical input bits. */
uint32_t pcm21_classify(float value) {
    if (value < -20.0f && value >= -273.0f)
        return 0u;
    if (value >= -20.0f && value < 0.0f)
        return 1u;
    if (value >= 0.0f && value < 50.0f)
        return 2u;
    if (value >= 50.0f && value < 1000.0f)
        return 3u;
    return 4u;
}
