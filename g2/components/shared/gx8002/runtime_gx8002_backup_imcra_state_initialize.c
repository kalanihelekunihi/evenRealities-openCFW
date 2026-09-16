/* SPDX-License-Identifier: MIT
 * Reconstruction for backup 0x1000e384. See decoded verification reports;
 * complete firmware admission and hardware execution remain unqualified.
 * Named offsets reflect observed accesses; semantic names for the remaining
 * DSP arrays are deliberately left unresolved until processing is recovered.
 */
#include <stdint.h>
#include <stddef.h>
extern uint32_t open_cfw_gx8002_backup_imcra_workspace(const volatile uint32_t *, uint32_t);
extern float open_cfw_gx8002_powf(float, float);
extern float csky_cos_f32(float);
extern void *memset(void *, int, size_t);
extern int printf(const char *, ...);
extern const char imcra_error_header[], imcra_error_required[], imcra_error_space[];
extern const char imcra_memory_temp[], imcra_memory_static[], imcra_memory_total[];
/* Store float bits through the word-oriented header without aliasing violations. */
static inline uint32_t float_word(float value)
{
    union { float f; uint32_t u; } bits = { .f = value };
    return bits.u;
}
uint32_t open_cfw_gx8002_backup_imcra_state_initialize(uint32_t rate,
                                                     uint32_t buffer,
                                                     uint32_t bytes)
{
    volatile uint32_t *s = (volatile uint32_t *)(uintptr_t)buffer;
    uint32_t cursor = buffer + 196, remaining = bytes - 196;
    (void)rate; /* Stock writes a fixed rate irrespective of the argument. */
    if (bytes < 196) {
        printf(imcra_error_header, bytes, 196);
        return 0;
    }
    s[2] = 16000; s[3] = 512; s[4] = 512; s[6] = 512; s[7] = 257;
    s[18] = float_word(0.9f); s[19] = float_word(1.66f);
    s[20] = float_word(4.6f); s[21] = float_word(3.0f);
    s[22] = float_word(1.67f); s[23] = float_word(0.92f);
    s[24] = float_word(0.85f); s[25] = float_word(1.47f);
    s[5] = 256; s[8] = 0;
    float threshold = open_cfw_gx8002_powf(10.0f, -0.6f);
    s[26] = 8; s[48] = float_word(threshold); s[27] = 4;
    s[28] = 2; s[29] = 0; s[47] = 0;
    uint32_t required = open_cfw_gx8002_backup_imcra_workspace(s, 2) + 196;
    if ((int32_t)bytes < (int32_t)required) {
        printf(imcra_error_required, bytes, required);
        return 0;
    }
#define RESERVE(offset, amount) do { \
        uint32_t count = (amount); \
        if (remaining < count) goto insufficient; \
        remaining -= count; s[(offset)/4] = cursor; cursor += count; \
    } while (0)
    uint32_t frame = s[3], hop = s[5], transform = s[4], bins = s[7];
    RESERVE(0x24, frame * 2);
    RESERVE(0x2c, (frame - hop) * 2);
    RESERVE(0x30, frame * 2);
    RESERVE(0x34, hop * 2);
    RESERVE(0x38, transform * 2);
    RESERVE(0x3c, bins * 4); RESERVE(0x40, bins * 4);
    RESERVE(0x44, bins * 4); RESERVE(0x78, bins * 4);
    RESERVE(0x7c, bins * 4); RESERVE(0x80, bins * 4);
    RESERVE(0x84, bins * 4); RESERVE(0x88, bins * 32);
    RESERVE(0x8c, bins * 4); RESERVE(0x90, bins * 32);
    RESERVE(0x94, bins * 4); RESERVE(0x98, bins * 4);
    RESERVE(0x9c, bins * 4); RESERVE(0xa0, bins * 4);
    RESERVE(0xa4, bins * 4); RESERVE(0xa8, bins * 4);
    RESERVE(0xac, 4);
    RESERVE(0xb0, bins * 4); RESERVE(0xb4, bins * 4);
    RESERVE(0xb8, bins * 4);
#undef RESERVE
    float *ones_a = (float *)(uintptr_t)s[0xa8/4];
    float *ones_b = (float *)(uintptr_t)s[0x98/4];
    for (int32_t i = 0; i < (int32_t)bins; ++i) ones_a[i] = 1.0f;
    for (int32_t i = 0; i < (int32_t)bins; ++i) ones_b[i] = 1.0f;
    float half_window = 0.5f - csky_cos_f32(0x1.921fb6p+1f) * 0.5f;
    *(float *)(uintptr_t)s[0xac/4] = half_window / (half_window + 0.0f);
    int32_t length = (int32_t)s[3];
    float angle_step = 0x1.921fb6p+2f / (float)length;
    int16_t *window = (int16_t *)(uintptr_t)s[0x30/4];
    int16_t *normalization = (int16_t *)(uintptr_t)s[0x34/4];
    for (int32_t i = 0; i < length; ++i) {
        float weight = 0.54f - csky_cos_f32((float)i * angle_step) * 0.46f;
        window[i] = (int16_t)(int32_t)(weight * 32767.0f);
    }
    uint32_t clear_samples = s[3];
    for (int32_t i = 0; i < length / 2; ++i) {
        float a = (float)window[i] * 0x1p-15f;
        float b = (float)window[i + length / 2] * 0x1p-15f;
        /* Preserve stock: round b squared before accumulating a squared. */
        volatile float b_squared = b * b;
        normalization[i] = (int16_t)(int32_t)((1.0f / (b_squared + a*a)) * 16384.0f);
    }
    memset((void *)(uintptr_t)s[0x24/4], 0, clear_samples * 2);
    s[0] = buffer; s[1] = bytes;
    printf(imcra_memory_temp, (double)((float)(int32_t)open_cfw_gx8002_backup_imcra_workspace(s, 0) * 0x1p-10f));
    printf(imcra_memory_static, (double)((float)(int32_t)open_cfw_gx8002_backup_imcra_workspace(s, 1) * 0x1p-10f));
    printf(imcra_memory_total, (double)((float)(int32_t)open_cfw_gx8002_backup_imcra_workspace(s, 2) * 0x1p-10f));
    return buffer;
insufficient:
    printf(imcra_error_space);
    return 0;
}
