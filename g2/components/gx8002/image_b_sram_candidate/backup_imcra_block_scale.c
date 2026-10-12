/* Native image-B 0x1000e28c and 0x1000e2c4, SHA256
 * d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * The former scales signed 16-bit samples in place. The latter scans their
 * maximum absolute magnitude, including abs(-32768)=32768, then returns
 * floor(log2(max))-14, or -15 when max is zero. Both native routines assume
 * at least one valid sample for the peak query; no fabricated null behavior.
 */
#include <stdint.h>

void gx8002_image_b_imcra_block_scale_1000e28c(int16_t *samples,
                                                  int count, int shift)
{
    if (count <= 0) return;
    if (shift > 0) {
        for (int i=0; i<count; ++i)
            samples[i] = (int16_t)((int32_t)samples[i] >> shift);
    } else {
        unsigned left = (unsigned)(-shift);
        for (int i=0; i<count; ++i)
            samples[i] = (int16_t)((uint32_t)(int32_t)samples[i] << left);
    }
}

int gx8002_image_b_imcra_peak_shift_1000e2c4(const int16_t *samples, int count)
{
    int32_t first = samples[0];
    uint32_t peak = (uint32_t)(first < 0 ? -first : first);
    for (int i=1; i<count; ++i) {
        int32_t v = samples[i];
        uint32_t mag = (uint32_t)(v < 0 ? -v : v);
        if (mag > peak) peak = mag;
    }
    if (peak == 0) return -15;
    for (int bit=31; bit>=0; --bit)
        if (peak & (UINT32_C(1) << bit)) return bit - 14;
    return -15;
}
