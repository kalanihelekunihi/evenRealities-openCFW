/* SPDX-License-Identifier: MIT
 * Typed quarter-wave source for image-B native cosine interpolator
 * 0x1000ee64..0x1000eedb. Native table starts at 0x100148d4.
 * All 513 original float32 words are reconstructed exactly by quarter-wave
 * symmetry; exceptional native zero-crossing residuals 256 and 512 remain
 * explicit product values. Formula and reconstructed words checked against
 * binh_b_stage2.bin
 * SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * This is a behavioral size variant, with execution time and exceptional
 * FPU inputs still unqualified on hardware.
 */
#include <stdint.h>

static const float sine_quarter[129] = {
    0x0.0p+0f, 0x1.921d200000000p-7f, 0x1.9215600000000p-6f, 0x1.2d86580000000p-5f,
    0x1.91f6600000000p-5f, 0x1.f656e80000000p-5f, 0x1.2d520a0000000p-4f, 0x1.5f6d000000000p-4f,
    0x1.917a6c0000000p-4f, 0x1.c3785c0000000p-4f, 0x1.f564e60000000p-4f, 0x1.139f0c0000000p-3f,
    0x1.2c81060000000p-3f, 0x1.45576c0000000p-3f, 0x1.5e21440000000p-3f, 0x1.76dd9e0000000p-3f,
    0x1.8f8b840000000p-3f, 0x1.a82a020000000p-3f, 0x1.c0b8260000000p-3f, 0x1.d934fe0000000p-3f,
    0x1.f19f980000000p-3f, 0x1.04fb800000000p-2f, 0x1.111d260000000p-2f, 0x1.1d34440000000p-2f,
    0x1.2940620000000p-2f, 0x1.35410c0000000p-2f, 0x1.4135ca0000000p-2f, 0x1.4d1e240000000p-2f,
    0x1.58f9a80000000p-2f, 0x1.64c7de0000000p-2f, 0x1.7088540000000p-2f, 0x1.7c3a940000000p-2f,
    0x1.87de2a0000000p-2f, 0x1.9372a60000000p-2f, 0x1.9ef7940000000p-2f, 0x1.aa6c820000000p-2f,
    0x1.b5d1000000000p-2f, 0x1.c1249e0000000p-2f, 0x1.cc66ea0000000p-2f, 0x1.d797760000000p-2f,
    0x1.e2b5d40000000p-2f, 0x1.edc1960000000p-2f, 0x1.f8ba4e0000000p-2f, 0x1.01cfc80000000p-1f,
    0x1.07387a0000000p-1f, 0x1.0c97040000000p-1f, 0x1.11eb360000000p-1f, 0x1.1734d60000000p-1f,
    0x1.1c73b40000000p-1f, 0x1.21a79a0000000p-1f, 0x1.26d0540000000p-1f, 0x1.2bedb20000000p-1f,
    0x1.30ff800000000p-1f, 0x1.36058c0000000p-1f, 0x1.3affa20000000p-1f, 0x1.3fed960000000p-1f,
    0x1.44cf320000000p-1f, 0x1.49a44a0000000p-1f, 0x1.4e6cac0000000p-1f, 0x1.53282a0000000p-1f,
    0x1.57d6940000000p-1f, 0x1.5c77bc0000000p-1f, 0x1.610b760000000p-1f, 0x1.6591920000000p-1f,
    0x1.6a09e60000000p-1f, 0x1.6e74460000000p-1f, 0x1.72d0840000000p-1f, 0x1.771e760000000p-1f,
    0x1.7b5df20000000p-1f, 0x1.7f8ece0000000p-1f, 0x1.83b0e00000000p-1f, 0x1.87c4000000000p-1f,
    0x1.8bc8060000000p-1f, 0x1.8fbcca0000000p-1f, 0x1.93a2240000000p-1f, 0x1.9777f00000000p-1f,
    0x1.9b3e040000000p-1f, 0x1.9ef43e0000000p-1f, 0x1.a29a7a0000000p-1f, 0x1.a630920000000p-1f,
    0x1.a9b6620000000p-1f, 0x1.ad2bca0000000p-1f, 0x1.b090a60000000p-1f, 0x1.b3e4d40000000p-1f,
    0x1.b728340000000p-1f, 0x1.ba5aa60000000p-1f, 0x1.bd7c0a0000000p-1f, 0x1.c08c420000000p-1f,
    0x1.c38b300000000p-1f, 0x1.c678b40000000p-1f, 0x1.c954b20000000p-1f, 0x1.cc1f100000000p-1f,
    0x1.ced7b00000000p-1f, 0x1.d17e780000000p-1f, 0x1.d4134e0000000p-1f, 0x1.d696180000000p-1f,
    0x1.d906bc0000000p-1f, 0x1.db65260000000p-1f, 0x1.ddb13c0000000p-1f, 0x1.dfeae60000000p-1f,
    0x1.e212100000000p-1f, 0x1.e426a40000000p-1f, 0x1.e6288e0000000p-1f, 0x1.e817ba0000000p-1f,
    0x1.e9f4160000000p-1f, 0x1.ebbd8c0000000p-1f, 0x1.ed740e0000000p-1f, 0x1.ef178a0000000p-1f,
    0x1.f0a7f00000000p-1f, 0x1.f225300000000p-1f, 0x1.f38f3a0000000p-1f, 0x1.f4e6040000000p-1f,
    0x1.f6297c0000000p-1f, 0x1.f7599a0000000p-1f, 0x1.f876500000000p-1f, 0x1.f97f920000000p-1f,
    0x1.fa75580000000p-1f, 0x1.fb57980000000p-1f, 0x1.fc26480000000p-1f, 0x1.fce1600000000p-1f,
    0x1.fd88da0000000p-1f, 0x1.fe1cb00000000p-1f, 0x1.fe9cda0000000p-1f, 0x1.ff09560000000p-1f,
    0x1.ff621e0000000p-1f, 0x1.ffa72e0000000p-1f, 0x1.ffd8860000000p-1f, 0x1.fff6220000000p-1f,
    0x1.0000000000000p+0f,
};

static const uint32_t residual_256 = UINT32_C(0x2768d16e);
static const uint32_t residual_512 = UINT32_C(0xa7e8d16e);

static float float_bits(uint32_t word)
{
    union { uint32_t word; float value; } converted;
    converted.word = word;
    return converted.value;
}

static float sine_at(uint32_t index)
{
    if (index <= 128u) return sine_quarter[index];
    if (index < 256u) return sine_quarter[256u - index];
    if (index == 256u) return float_bits(residual_256);
    if (index <= 384u) return -sine_quarter[index - 256u];
    if (index < 512u) return -sine_quarter[512u - index];
    return float_bits(residual_512);
}

float gx8002_image_b_cosine_lookup_1000ee64(float angle)
{
    float phase = 0.25f + angle * float_bits(UINT32_C(0x3e22f983));
    int32_t integer = (int32_t)phase;
    if (phase < 0.0f) --integer;
    float scaled = (phase - (float)integer) * 512.0f;
    uint32_t index = ((uint32_t)scaled) & 511u;
    float fraction = scaled - (float)index;
    return fraction * sine_at(index + 1u) +
           (1.0f - fraction) * sine_at(index);
}
