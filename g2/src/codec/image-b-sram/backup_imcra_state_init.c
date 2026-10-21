/* SPDX-License-Identifier: MIT
 * IMCRA state layout and window construction, native image-B
 * 0x1000e384..0x1000e714 with out-of-line error tails at 0x1000e75c.
 * The 0x1000e58c continuation is valid C-SKY floating ISA; the retained
 * decompiler's bad-data stop at 0x1000e58b is not a native control edge.
 * binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Power and cosine helpers retain real source/data contracts. C-SKY FPU
 * rounding, reciprocal precision, and physical audio behavior are open.
 */
#include <stdint.h>

extern float gx8002_image_b_power_float_100100a4(float base, float exponent);
extern float gx8002_image_b_cosine_lookup_1000ee64(float angle);
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

static float float_bits(uint32_t word)
{
    union { uint32_t word; float value; } converted;
    converted.word = word;
    return converted.value;
}

uint32_t gx8002_image_b_imcra_required_1000e314(
    const uint32_t *state, uint32_t kind)
{
    if (kind == 0u) return 0u;
    uint32_t bins = state[0x1cu / 4u];
    uint32_t frame = state[0x0cu / 4u];
    uint32_t scratch = state[0x10u / 4u];
    return bins * 72u + frame * 10u + bins * state[0x68u / 4u] * 8u
         + scratch * 4u + (state[0x74u / 4u] * 2u + 1u) * 4u;
}

static int reserve_region(uint32_t *state, uint32_t field,
                          uint32_t bytes, uintptr_t *cursor,
                          uint32_t *remaining)
{
    if (*remaining < bytes) return 0;
    state[field / 4u] = (uint32_t)*cursor;
    *cursor += bytes;
    *remaining -= bytes;
    return 1;
}

int32_t gx8002_image_b_imcra_state_init_1000e384(
    uint32_t sample_word, void *allocation, uint32_t bytes)
{
    (void)sample_word; /* Native entry retains r0 but does not read it. */
    uint32_t *state = (uint32_t *)allocation;
    if (bytes < 196u) {
        (void)gx8002_image_b_heap_log_10009934(
            "[ImcraStateInit Error] At least sizeof(ImcraState) is required (%d < %d)\n",
            bytes, 196);
        return 0;
    }
    state[0x08u / 4u] = 16000u;
    state[0x0cu / 4u] = 512u;
    state[0x10u / 4u] = 512u;
    state[0x18u / 4u] = 512u;
    state[0x1cu / 4u] = 257u;
    state[0x48u / 4u] = UINT32_C(0x3f666666);
    state[0x4cu / 4u] = UINT32_C(0x3fd47ae1);
    state[0x50u / 4u] = UINT32_C(0x40933333);
    state[0x54u / 4u] = UINT32_C(0x40400000);
    state[0x58u / 4u] = UINT32_C(0x3fd5c28f);
    state[0x5cu / 4u] = UINT32_C(0x3f6b851f);
    state[0x60u / 4u] = UINT32_C(0x3f59999a);
    state[0x64u / 4u] = UINT32_C(0x3fbc28f6);
    state[0x14u / 4u] = 256u;
    state[0x20u / 4u] = 0u;
    union { float value; uint32_t word; } power;
    power.value = gx8002_image_b_power_float_100100a4(
        10.0f, float_bits(UINT32_C(0xbf19999a)));
    state[0xc0u / 4u] = power.word;
    state[0x68u / 4u] = 8u;
    state[0x6cu / 4u] = 4u;
    state[0x70u / 4u] = 2u;
    state[0x74u / 4u] = 0u;
    state[0xbcu / 4u] = 0u;

    uint32_t required = gx8002_image_b_imcra_required_1000e314(state, 2u);
    if ((int32_t)bytes < (int32_t)(required + 196u)) {
        (void)gx8002_image_b_heap_log_10009934(
            "[ImcraStateInit Error] bufsize[%d] < required size[%d]\n",
            bytes, required + 196u);
        return 0;
    }
    uintptr_t cursor = (uintptr_t)allocation + 196u;
    uint32_t remaining = bytes - 196u;
    uint32_t frame_bytes = state[0x0cu / 4u] * 2u;
    uint32_t hop_bytes = (state[0x0cu / 4u] - state[0x14u / 4u]) * 2u;
    uint32_t small_bytes = state[0x14u / 4u] * 2u;
    uint32_t bin_bytes = state[0x1cu / 4u] * 4u;
    uint32_t large_bytes = state[0x1cu / 4u] * 32u;
#define RESERVE(field, size) \
    do { if (!reserve_region(state, (field), (size), &cursor, &remaining)) \
             goto insufficient_space; } while (0)
    RESERVE(0x24u, frame_bytes);
    RESERVE(0x2cu, hop_bytes);
    RESERVE(0x30u, frame_bytes);
    RESERVE(0x34u, small_bytes);
    RESERVE(0x38u, state[0x10u / 4u] * 2u);
    RESERVE(0x3cu, bin_bytes);
    RESERVE(0x40u, bin_bytes);
    RESERVE(0x44u, bin_bytes);
    RESERVE(0x78u, bin_bytes);
    RESERVE(0x7cu, bin_bytes);
    RESERVE(0x80u, bin_bytes);
    RESERVE(0x84u, bin_bytes);
    RESERVE(0x88u, large_bytes);
    RESERVE(0x8cu, bin_bytes);
    RESERVE(0x90u, large_bytes);
    RESERVE(0x94u, bin_bytes);
    RESERVE(0x98u, bin_bytes);
    RESERVE(0x9cu, bin_bytes);
    RESERVE(0xa0u, bin_bytes);
    RESERVE(0xa4u, bin_bytes);
    RESERVE(0xa8u, bin_bytes);
    RESERVE(0xacu, 4u);
    RESERVE(0xb0u, bin_bytes);
    RESERVE(0xb4u, bin_bytes);
    RESERVE(0xb8u, bin_bytes);
#undef RESERVE

    uint32_t *ones_a = (uint32_t *)(uintptr_t)state[0xa8u / 4u];
    uint32_t *ones_b = (uint32_t *)(uintptr_t)state[0x98u / 4u];
    for (uint32_t i = 0; i < state[0x1cu / 4u]; ++i)
        ones_a[i] = UINT32_C(0x3f800000);
    for (uint32_t i = 0; i < state[0x1cu / 4u]; ++i)
        ones_b[i] = UINT32_C(0x3f800000);

    float cosine_pi = gx8002_image_b_cosine_lookup_1000ee64(
        float_bits(UINT32_C(0x40490fdb)));
    float half = 0.5f;
    float top = half - cosine_pi * half;
    *(float *)(uintptr_t)state[0xacu / 4u] = top / (top + 0.0f);
    int16_t *window = (int16_t *)(uintptr_t)state[0x30u / 4u];
    int16_t *compensation = (int16_t *)(uintptr_t)state[0x34u / 4u];
    float phase_step = float_bits(UINT32_C(0x40c90fdb)) /
                       (float)(int32_t)state[0x0cu / 4u];
    for (uint32_t i = 0; i < state[0x0cu / 4u]; ++i) {
        float cosine = gx8002_image_b_cosine_lookup_1000ee64(
            (float)(int32_t)i * phase_step);
        float weight = float_bits(UINT32_C(0x3f0a3d71)) -
                       cosine * float_bits(UINT32_C(0x3eeb851f));
        window[i] = (int16_t)(int32_t)(weight * 32767.0f);
    }
    for (uint32_t i = 0; i < state[0x0cu / 4u] / 2u; ++i) {
        float left = (float)window[i] * float_bits(UINT32_C(0x38000000));
        float right = (float)window[i + state[0x0cu / 4u] / 2u] *
                      float_bits(UINT32_C(0x38000000));
        float inverse = 1.0f / (right * right + left * left);
        compensation[i] = (int16_t)(int32_t)(inverse * 16384.0f);
    }
    gx8002_image_b_zero_100113c4(
        (void *)(uintptr_t)state[0x24u / 4u], 0u, frame_bytes);
    state[0] = (uint32_t)(uintptr_t)state;
    state[1] = bytes;
    (void)gx8002_image_b_heap_log_10009934(
        "Imcra(Temp  )       Memory:%6.2fKB\n",
        (double)((float)gx8002_image_b_imcra_required_1000e314(state, 0u) /
                 1024.0f));
    (void)gx8002_image_b_heap_log_10009934(
        "Imcra(Static)       Memory:%6.2fKB\n",
        (double)((float)gx8002_image_b_imcra_required_1000e314(state, 1u) /
                 1024.0f));
    (void)gx8002_image_b_heap_log_10009934(
        "Imcra(Total )       Memory:%6.2fKB\n",
        (double)((float)gx8002_image_b_imcra_required_1000e314(state, 2u) /
                 1024.0f));
    return (int32_t)(uintptr_t)state;

insufficient_space:
    (void)gx8002_image_b_heap_log_10009934(
        "[ImcraStateInit Error] Not enough buffer space\n");
    return 0;
}
