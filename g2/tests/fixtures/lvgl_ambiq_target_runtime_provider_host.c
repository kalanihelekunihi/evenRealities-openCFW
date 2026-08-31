/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_target_runtime_provider.h"

#include <assert.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>

typedef union test_double_bits {
    double value;
    uint64_t bits;
} test_double_bits;

typedef union test_float_bits {
    float value;
    uint32_t bits;
} test_float_bits;

static void test_memory(void)
{
    uint8_t source[17];
    uint8_t output[17];
    size_t index;

    for(index = 0; index < sizeof(source); ++index) source[index] = (uint8_t)(index * 13U);
    assert(memset(output, 0xa5, sizeof(output)) == output);
    for(index = 0; index < sizeof(output); ++index) assert(output[index] == 0xa5U);
    assert(memcpy(output, source, sizeof(output)) == output);
    for(index = 0; index < sizeof(output); ++index) assert(output[index] == source[index]);

    memset(output, 0, sizeof(output));
    __aeabi_memcpy4(output, source, 16U);
    for(index = 0; index < 16U; ++index) assert(output[index] == source[index]);
    assert(output[16] == 0U);

    assert(memcpy(NULL, NULL, 0U) == NULL);
    assert(memset(NULL, 0, 0U) == NULL);
    memset(output, 0x3c, sizeof(output));
    assert(memcpy(output, NULL, 4U) == output);
    for(index = 0; index < sizeof(output); ++index) assert(output[index] == 0x3cU);
    assert(memset(NULL, 0, 4U) == NULL);
    __aeabi_memcpy4(NULL, NULL, 0U);
    __aeabi_memcpy4(output, NULL, 4U);
}

static void test_signed_conversion(void)
{
    test_double_bits sampled;
    uint64_t state = UINT64_C(0x9e3779b97f4a7c15);
    unsigned int iteration;

    assert(__aeabi_d2lz(0.0) == 0);
    assert(__aeabi_d2lz(-0.0) == 0);
    assert(__aeabi_d2lz(0.999) == 0);
    assert(__aeabi_d2lz(-0.999) == 0);
    assert(__aeabi_d2lz(1.999) == 1);
    assert(__aeabi_d2lz(-1.999) == -1);
    assert(__aeabi_d2lz(4294967296.0) == INT64_C(4294967296));
    assert(__aeabi_d2lz(-4294967296.0) == -INT64_C(4294967296));
    assert(__aeabi_d2lz(0x1.fffffffffffffp62) == INT64_C(9223372036854774784));
    assert(__aeabi_d2lz(-0x1p63) == INT64_MIN);
    assert(__aeabi_d2lz(0x1p63) == INT64_MAX);
    assert(__aeabi_d2lz(INFINITY) == INT64_MAX);
    assert(__aeabi_d2lz(-INFINITY) == INT64_MIN);
    assert(__aeabi_d2lz(NAN) == INT64_MAX);
    sampled.bits = UINT64_C(0xfff8000000000001);
    assert(__aeabi_d2lz(sampled.value) == INT64_MIN);

    for(iteration = 0; iteration < 10000U; ++iteration) {
        state ^= state << 13U;
        state ^= state >> 7U;
        state ^= state << 17U;
        sampled.bits = state;
        if(isfinite(sampled.value) && sampled.value >= -0x1p63 && sampled.value < 0x1p63) {
            assert(__aeabi_d2lz(sampled.value) == (int64_t)sampled.value);
        }
    }
}

static void test_unsigned_conversion(void)
{
    test_float_bits sampled;
    uint32_t state = UINT32_C(0x6d2b79f5);
    unsigned int iteration;

    assert(__aeabi_f2ulz(0.0F) == UINT64_C(0));
    assert(__aeabi_f2ulz(-0.0F) == UINT64_C(0));
    assert(__aeabi_f2ulz(0.999F) == UINT64_C(0));
    assert(__aeabi_f2ulz(-1.0F) == UINT64_C(0));
    assert(__aeabi_f2ulz(1.999F) == UINT64_C(1));
    assert(__aeabi_f2ulz(0x1p32F) == UINT64_C(4294967296));
    assert(__aeabi_f2ulz(0x1.fffffep63F) == UINT64_C(18446742974197923840));
    assert(__aeabi_f2ulz(INFINITY) == UINT64_MAX);
    assert(__aeabi_f2ulz(-INFINITY) == UINT64_C(0));
    assert(__aeabi_f2ulz(NAN) == UINT64_MAX);
    sampled.bits = UINT32_C(0xffc00001);
    assert(__aeabi_f2ulz(sampled.value) == UINT64_C(0));

    for(iteration = 0; iteration < 10000U; ++iteration) {
        state ^= state << 13U;
        state ^= state >> 17U;
        state ^= state << 5U;
        sampled.bits = state;
        if(isfinite(sampled.value) && sampled.value >= 0.0F && sampled.value < 0x1p64F) {
            assert(__aeabi_f2ulz(sampled.value) == (uint64_t)sampled.value);
        }
    }
}

int main(void)
{
    test_memory();
    test_signed_conversion();
    test_unsigned_conversion();
    return 0;
}
