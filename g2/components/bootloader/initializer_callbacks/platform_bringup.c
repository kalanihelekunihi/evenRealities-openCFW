/* SPDX-License-Identifier: MIT */
#include <stdint.h>

struct adc_coefficients {
    float first;
    float second;
    float third;
    uint32_t scale;
};

extern uint32_t opencfw_bl_power_register_update(uint32_t id, uint32_t value);
#include "adc_context.h"
#include "adc_control.h"
#include "adc_configuration.h"
#include "adc_samples.h"
#include "adc_profile.h"


extern void opencfw_bl_generic_log(const char *format, ...);

#define ADC_READY (*(volatile uint32_t *)0x40038038u)
#define ADC_RESULT ((volatile uint8_t *)0x20027018u)
#define ADC_POWER_MODE (*(volatile const uint32_t *)0x434170u)
#define ADC_FINAL_MODE (*(volatile const uint32_t *)0x434174u)

static float float_from_bits(uint32_t bits)
{
    union { uint32_t bits; float value; } convert = { .bits = bits };
    return convert.value;
}

static uint64_t float_to_double_bits(float value)
{
    union { float value; uint32_t bits; } input = { .value = value };
    const uint64_t sign = (uint64_t)(input.bits >> 31) << 63;
    const uint32_t exponent = (input.bits >> 23) & 0xffu;
    const uint32_t fraction = input.bits & 0x7fffffu;
    if (exponent == 0xffu)
        return sign | 0x7ff0000000000000ull | ((uint64_t)fraction << 29);
    if (exponent != 0u)
        return sign | ((uint64_t)(exponent + 896u) << 52) |
               ((uint64_t)fraction << 29);
    if (fraction == 0u)
        return sign;
    uint32_t highest = 0u;
    for (uint32_t value_bits = fraction; value_bits >>= 1; ++highest) { }
    const int32_t unbiased = (int32_t)highest - 149;
    const uint64_t normalized = (uint64_t)(fraction - (1u << highest))
                                << (52u - highest);
    return sign | ((uint64_t)(unbiased + 1023) << 52) | normalized;
}

static void compare_float(float left, float right)
{
    __asm__ volatile("vcmp.f32 %0, %1\n\tvmrs APSR_nzcv, FPSCR"
                     :: "t"(left), "t"(right) : "cc");
}

/* Reconstructed ADC bringup body 0x430000..0x4301d5. The ready bit and ADC
 * samples are peripheral fixtures; this code does not model ADC timing.
 */
void opencfw_bl_platform_bringup(void)
{
    uint32_t context = 0u;
    uint32_t ready = 1u;
    uint32_t sample[2] = {0u, 0u};
    struct adc_coefficients coefficients = {
        .first = 0.0f,
        .second = 0.0f,
        .third = 0.0f,
        .scale = 0xc2f6e979u,
    };
    uint32_t descriptor[2];
    const uint8_t profile[7] = {2u, 1u, 0u, 7u, 1u, 0u, 1u};
    struct {
        uint8_t slot;
        uint8_t padding[3];
        uint32_t word;
        uint8_t tail[4];
    } channel = { .slot = 7u, .padding = {0}, .word = 0x20u,
                  .tail = {0u, 3u, 0u, 1u} };

    (void)opencfw_bl_power_register_update(0x10u, ADC_POWER_MODE);
    if (opencfw_bl_adc_context_initialize(0u, &context) != 0u)
        opencfw_bl_generic_log((const char *)(uintptr_t)0x431ea4u);

    opencfw_bl_adc_configure(context, 3u, &coefficients);
    opencfw_bl_generic_log((const char *)(uintptr_t)0x4325f8u,
                           float_to_double_bits(coefficients.first),
                           float_to_double_bits(coefficients.second));
    if (opencfw_bl_adc_profile_transfer(context, 0u, 0u) != 0u)
        opencfw_bl_generic_log((const char *)(uintptr_t)0x433140u);

    const volatile uint32_t *const descriptor_source =
        (const volatile uint32_t *)0x43402cu;
    descriptor[0] = descriptor_source[0];
    descriptor[1] = descriptor_source[1];
    opencfw_bl_adc_context_configure(context, descriptor);
    if (opencfw_bl_adc_apply_profile(context, profile) != 0u)
        opencfw_bl_generic_log((const char *)(uintptr_t)0x432c7cu);
    if (opencfw_bl_adc_configure_channel(context, 0u, &channel) != 0u)
        opencfw_bl_generic_log((const char *)(uintptr_t)0x4329d4u);
    if (opencfw_bl_adc_activate(context) != 0u)
        opencfw_bl_generic_log((const char *)(uintptr_t)0x433160u);
    opencfw_bl_adc_enable(context);
    opencfw_bl_adc_command(context);

    for (uint32_t index = 0; index < 3u; ++index) {
        while (((ADC_READY & 0x0fffffffu) >> 20) == 0u) {
            /* Hardware waits until the ADC-ready field becomes nonzero. */
        }
        ready = 1u;
        sample[0] = 0u;
        sample[1] = 0u;
        opencfw_bl_adc_enumerate(context, 0u, 0u, &ready, (opencfw_boot_adc_sample *)sample);
        if (index != 2u)
            continue;

        opencfw_bl_adc_disable(context);
        opencfw_bl_adc_normalize(context);
        const uint32_t scaled = (sample[0] * 0x4a6u) >> 12;
        const float measured = (float)scaled;
        const float low = float_from_bits(0x44610001u);
        const float high = float_from_bits(0x447a0000u);
        compare_float(measured, low);
        if (measured < low) {
            ADC_RESULT[0] = 0u;
            *(volatile uint16_t *)(void *)(ADC_RESULT + 2) = 3u;
        } else {
            compare_float(measured, high);
            if (measured < high) {
                ADC_RESULT[0] = 1u;
                *(volatile uint16_t *)(void *)(ADC_RESULT + 2) = 1u;
            } else {
            ADC_RESULT[0] = 0u;
            *(volatile uint16_t *)(void *)(ADC_RESULT + 2) = 3u;
            }
        }
        *(volatile uint16_t *)(void *)(ADC_RESULT + 4) = (uint16_t)measured;
        opencfw_bl_generic_log((const char *)(uintptr_t)0x431ab8u,
                               sample[0], float_to_double_bits(measured));
    }

    (void)opencfw_bl_adc_profile_transfer(context, 2u, 0u);
    opencfw_bl_adc_reset(context);
    (void)opencfw_bl_power_register_update(0x10u, ADC_FINAL_MODE);
}
