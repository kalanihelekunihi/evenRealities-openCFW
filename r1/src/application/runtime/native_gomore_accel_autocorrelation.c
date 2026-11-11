/* Stock-derived autocorrelation for the accelerometer classifier. */
#include "native_gomore_accel_autocorrelation.h"
#include "gomore_primitives/gomore_primitives.h"
#include <stdbool.h>
#include <limits.h>
static uint32_t float_bits(float value) {
    union { float f; uint32_t u; } bits = { .f = value };
    return bits.u;
}
static float difference_sample(const void *samples,
                               gomore_primitives_difference_mode mode,
                               size_t index) {
    if (mode == GOMORE_PRIMITIVES_DIFFERENCE_FLOAT32) {
        const float *values = samples;
        return values[index] - values[index - 1u];
    }
    if (mode == GOMORE_PRIMITIVES_DIFFERENCE_INT16) {
        const int16_t *values = samples;
        return (float)((int32_t)values[index] -
                       (int32_t)values[index - 1u]);
    }
    const int32_t *values = samples;
    return (float)(int32_t)((uint32_t)values[index] - (uint32_t)values[index - 1u]);
}

/* Keep guarded divisions observable: stock does not execute 0/0 when a
 * direction count or normalizer is zero. Volatile operands prevent speculative
 * division under compilers that otherwise ignore floating-point exceptions. */
static __attribute__((noinline)) float direction_guarded_divide(
    float numerator, float denominator) {
    volatile float left = numerator;
    volatile float right = denominator;
    return left / right;
}

bool gomore_primitives_direction_change_statistics(
    float normalizer, float threshold_scale,
    gomore_primitives_difference_mode mode,
    const void *samples, size_t difference_count,
    gomore_primitives_direction_change_output *output) {
    if (samples == NULL || output == NULL || difference_count > 127u ||
            (mode != GOMORE_PRIMITIVES_DIFFERENCE_FLOAT32 &&
             mode != GOMORE_PRIMITIVES_DIFFERENCE_INT16 &&
             mode != GOMORE_PRIMITIVES_DIFFERENCE_INT32)) {
        return false;
    }
    if (difference_count < 6u) {
        output->direction_changes = -1;
        output->normalized_variation = -1.0f;
        output->average_completed_run = -1.0f;
        output->above_threshold_changes = -1;
        return true;
    }

    const float threshold = normalizer * threshold_scale;
    int8_t direction_changes = 0;
    int8_t above_threshold_changes = 0;
    int8_t run_length = 1;
    int16_t completed_run_sum = 0;
    float variation_sum = 0.0f;
    float previous = difference_sample(samples, mode, 1u);
    for (size_t index = 2u; index <= difference_count; ++index) {
        const float current = difference_sample(samples, mode, index);
        const bool same_direction =
            (current > 0.0f && previous > 0.0f) ||
            (current < 0.0f && previous < 0.0f);
        if (same_direction) {
            ++run_length;
        } else {
            ++direction_changes;
            completed_run_sum = (int16_t)(completed_run_sum + run_length);
            const float delta = current - previous;
            variation_sum += (delta < 0.0f ? -delta : delta) /
                (float)run_length;
            const float magnitude = current < 0.0f ? -current : current;
            if (normalizer > 0.0f && magnitude > threshold) {
                ++above_threshold_changes;
            }
            run_length = 1;
        }
        previous = current;
    }
    output->direction_changes = direction_changes;
    output->above_threshold_changes = above_threshold_changes;
    output->normalized_variation = normalizer == 0.0f ? 0.0f :
        direction_guarded_divide(variation_sum, normalizer);
    output->average_completed_run = direction_changes == 0 ? 0.0f :
        direction_guarded_divide((float)completed_run_sum, (float)direction_changes);
    return true;
}

float gomore_primitives_centered_ratio(int32_t first, int32_t middle,
                                      int32_t last) {
    const uint32_t wrapped =
        ((uint32_t)first + (uint32_t)last - (uint32_t)middle * 2u) * 2u;
    const int32_t denominator = (int32_t)wrapped;
    const float magnitude = denominator < 0
        ? -(float)denominator : (float)denominator;
    if ((int32_t)float_bits(magnitude) < INT32_C(0x358637BD)) {
        return 0.0f;
    }
    const int32_t numerator = (int32_t)((uint32_t)first - (uint32_t)last);
    return (float)numerator / (float)denominator;
}

static int32_t autocorrelation_wrap_multiply_add(
    int32_t accumulator, int32_t left, int32_t right) {
    union {
        uint32_t unsigned_value;
        int32_t signed_value;
    } converted;
    converted.unsigned_value = (uint32_t)accumulator +
        (uint32_t)left * (uint32_t)right;
    return converted.signed_value;
}

static float autocorrelation_peak_rate(const int32_t values[100],
                                       uint8_t lag) {
    if (lag == 0u || lag >= 99u) {
        return 0.0f;
    }
    const float refined = (float)lag + gomore_primitives_centered_ratio(
        values[lag - 1u], values[lag], values[lag + 1u]);
    const float absolute = refined < 0.0f ? -refined : refined;
    if ((int32_t)float_bits(absolute) < INT32_C(0x358637BD)) {
        return 0.0f;
    }
    return 1500.0f / refined;
}

uint64_t r1_gomore_accel_autocorrelation_native(
    const uint16_t *samples, float *first, float *second, float *third,
    float *fourth, float *fifth, uintptr_t first_binding,
    uintptr_t second_binding) {
    int8_t *const turning_counts = (int8_t *)first_binding;
    float *const shape = (float *)second_binding;
    int32_t correlation[100];
    uint8_t peaks[12] = {0u};
    *first = 1.0f;

    int32_t sum = 0;
    for (size_t index = 0u; index < 100u; ++index) {
        sum += samples[index];
    }
    const int32_t mean = sum / 100;
    int32_t energy = 0;
    for (size_t index = 0u; index < 100u; ++index) {
        const int32_t centered = (int32_t)samples[index] - mean;
        energy = autocorrelation_wrap_multiply_add(
            energy, centered, centered);
    }
    for (size_t lag = 0u; lag < 100u; ++lag) {
        int32_t accumulator = 0;
        for (size_t index = 0u; index < 100u - lag; ++index) {
            const int32_t first_centered =
                (int32_t)samples[index] - mean;
            const int32_t second_centered =
                (int32_t)samples[index + lag] - mean;
            accumulator = autocorrelation_wrap_multiply_add(
                accumulator, first_centered, second_centered);
        }
        correlation[lag] = accumulator;
    }
    const int32_t variance_scale = (int32_t)((uint32_t)(energy / 100) * 100u);

    uint8_t strict_count = 0u;
    for (uint8_t lag = 1u; lag < 99u; ++lag) {
        if (correlation[lag - 1u] < correlation[lag] &&
                correlation[lag + 1u] < correlation[lag]) {
            if (strict_count < 10u) {
                peaks[strict_count] = lag;
            }
            ++strict_count;
        }
    }
    if (strict_count < 2u) {
        *first = -1.0f;
    }
    if (strict_count > 10u) {
        if (strict_count > 15u) {
            *first = -1.0f;
        }
        strict_count = 10u;
    }
    if (*first > 0.0f) {
        int32_t band_maximum = (int32_t)(0u - (uint32_t)variance_scale);
        for (uint8_t index = 0u; index < strict_count; ++index) {
            const uint8_t lag = peaks[index];
            if (band_maximum < correlation[lag] && lag > 12u && lag < 40u) {
                band_maximum = correlation[lag];
            }
        }
        for (uint8_t index = 0u; index + 1u < strict_count; ++index) {
            peaks[index] = (uint8_t)(peaks[index + 1u] - peaks[index]);
        }
        --strict_count;
        bool consistent = strict_count >= 2u;
        for (uint8_t index = 0u; index + 1u < strict_count; ++index) {
            const int32_t difference =
                (int32_t)peaks[index] - (int32_t)peaks[index + 1u];
            if (difference < -3 || difference > 3) {
                consistent = false;
            }
        }
        const float scaled_variance = (float)variance_scale;
        if ((float)band_maximum > scaled_variance * 0.55f ||
                (consistent &&
                 (float)band_maximum > scaled_variance * 0.4f)) {
            *first = 1.0f;
        } else {
            *first = -1.0f;
        }
    }

    uint8_t peak_count = 0u;
    uint8_t strongest_lag = 0u;
    int32_t strongest_value = 0;
    const float peak_threshold = (float)variance_scale * 0.03f;
    for (uint8_t lag = 1u; lag < 99u; ++lag) {
        const int32_t value = correlation[lag];
        if ((int32_t)((uint32_t)value - (uint32_t)correlation[lag - 1u]) >= 0 &&
                (int32_t)((uint32_t)correlation[lag + 1u] - (uint32_t)value) <= 0 &&
                (float)value > peak_threshold) {
            peaks[peak_count] = lag;
            if (strongest_value < value && lag < 51u) {
                strongest_lag = lag;
                strongest_value = value;
            }
            ++peak_count;
            if (peak_count > 10u) {
                peak_count = 11u;
                break;
            }
        }
    }

    uint8_t secondary_lag = 0u;
    int32_t secondary_value = 0;
    for (uint8_t index = 0u; index < peak_count; ++index) {
        const uint8_t lag = peaks[index];
        const int32_t value = correlation[lag];
        if (secondary_value < value && value < strongest_value && lag < 51u) {
            secondary_lag = lag;
            secondary_value = value;
        }
    }
    int32_t minimum_before_peak = variance_scale;
    for (uint8_t lag = 0u; lag < strongest_lag; ++lag) {
        if (correlation[lag] < minimum_before_peak) {
            minimum_before_peak = correlation[lag];
        }
    }

    const int32_t harmonic_tolerance = strongest_lag < 30u
        ? 4 : (strongest_lag < 35u ? 5 : 6);
    if ((float)strongest_value > (float)variance_scale * 0.17f &&
            strongest_lag > 5u) {
        for (uint8_t index = 0u; index < peak_count; ++index) {
            const int32_t distance = (int32_t)strongest_lag * 2 -
                                     (int32_t)peaks[index];
            if (distance >= -harmonic_tolerance &&
                    distance <= harmonic_tolerance) {
                *second = 1.0f;
                break;
            }
        }
    }

    if (*second > 0.0f) {
        gomore_primitives_direction_change_output direction;
        if (!gomore_primitives_direction_change_statistics(
                (float)(int32_t)((uint32_t)strongest_value - (uint32_t)minimum_before_peak), 0.3f,
                GOMORE_PRIMITIVES_DIFFERENCE_INT32,
                correlation, strongest_lag, &direction)) {
            return (uint32_t)(uintptr_t)samples | ((uint64_t)(uint32_t)(uintptr_t)first << 32);
        }
        turning_counts[0] = direction.direction_changes;
        turning_counts[1] = direction.above_threshold_changes;
        shape[0] = direction.normalized_variation;
        shape[1] = direction.average_completed_run;
        const int32_t direction_count = direction.direction_changes;
        if (direction_count > 4) {
            const float minimum_share = direction_count > 8 ? 0.35f : 0.45f;
            if ((float)direction.above_threshold_changes /
                    (float)direction_count > minimum_share) {
                *second = -1.0f;
            }
        }
    }
    if (peak_count > 7u &&
            (float)variance_scale * 0.35f > (float)strongest_value &&
            peaks[7] < 48u) {
        *second = -1.0f;
    }
    if ((float)minimum_before_peak > (float)variance_scale * -0.1f) {
        *second = -1.0f;
    }

    uint8_t selected_lag = 0u;
    if (*second > 0.0f && peak_count > 2u) {
        const uint16_t third_peak = peaks[2];
        *third = third_peak == 0u ? 0.0f : 4500.0f / (float)third_peak;
        const int32_t harmonic_distance =
            (int32_t)secondary_lag * 2 - (int32_t)strongest_lag;
        selected_lag = strongest_lag;
        if (harmonic_distance >= -2 && harmonic_distance <= 2) {
            selected_lag = secondary_lag;
        }
        *fourth = autocorrelation_peak_rate(correlation, selected_lag);
    }

    int32_t selected_index = -1;
    for (uint8_t index = 0u; index < peak_count; ++index) {
        if (peaks[index] == selected_lag) {
            selected_index = (int32_t)index;
            break;
        }
    }
    uint8_t earlier_lag = 0u;
    if (selected_index == 0) {
        earlier_lag = peaks[0];
    } else if (selected_index == 1) {
        earlier_lag = peaks[0];
        if (earlier_lag < 6u || earlier_lag > 50u) {
            earlier_lag = peaks[1];
        }
    } else if (selected_index > 1) {
        int32_t best_value = 0;
        for (int32_t index = 0; index < selected_index; ++index) {
            const uint8_t lag = peaks[index];
            if (lag >= 6u && lag <= 50u && best_value < correlation[lag]) {
                earlier_lag = lag;
                best_value = correlation[lag];
            }
        }
    }
    *fifth = autocorrelation_peak_rate(correlation, earlier_lag);
    return (uint32_t)(uintptr_t)samples | ((uint64_t)(uint32_t)(uintptr_t)first << 32);
}

uint64_t r1_gomore_accel_autocorrelation_wrapper_native(
    uint32_t enabled, const uint16_t *samples, float *first, float *second,
    float *third, float *fourth, float *fifth, uintptr_t first_binding,
    uintptr_t second_binding) {
    *(volatile float *)first = -1.0f;
    *(volatile float *)second = -1.0f;
    *(volatile float *)third = 0.0f;
    *(volatile float *)fourth = 0.0f;
    *(volatile float *)fifth = 0.0f;
    if (enabled == 1u) {
        (void)r1_gomore_accel_autocorrelation_native(samples, first, second,
            third, fourth, fifth, first_binding, second_binding);
        /* Stock reuses the saved R0/R1 slots for outgoing arguments. */
        return (uint32_t)(uintptr_t)fourth |
            ((uint64_t)(uint32_t)(uintptr_t)fifth << 32);
    }
    return enabled | ((uint64_t)(uint32_t)(uintptr_t)samples << 32);
}
