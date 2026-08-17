/*
 * Clean-room implementation of complete GoMore-candidate functions in the R1
 * application image.  The implementation contains no model weights,
 * original executable bytes, absolute firmware pointers, or vendor source.
 */

#include "gomore_primitives/gomore_primitives.h"

#include "gomore_tensor_runtime/gomore_tensor_runtime.h"
#include "openr1/r1_crc.h"

_Static_assert(sizeof(gomore_primitives_interval_descriptor) == 40u,
               "interval descriptor layout must match the recovered record");
_Static_assert(offsetof(gomore_primitives_interval_descriptor, type) == 36u,
               "interval descriptor tag offset must remain exact");
_Static_assert(offsetof(gomore_primitives_step_accumulator, history) == 20u,
               "step history offset must remain exact");
_Static_assert(sizeof(gomore_primitives_sleep_interval_source) == 40u,
               "sleep interval source layout must remain exact");
_Static_assert(sizeof(gomore_primitives_sleep_interval_result) == 32u,
               "sleep interval result layout must remain exact");
_Static_assert(sizeof(gomore_primitives_sps_model_state) == 28u,
               "SPS model state layout must remain exact");
_Static_assert(sizeof(gomore_primitives_sps_candidate_state) == 88u,
               "SPS candidate state layout must remain exact");
_Static_assert(offsetof(gomore_primitives_sps_candidate_state,
                        configuration_binding) == 64u,
               "SPS configuration binding offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sps_candidate_state,
                        startup_cooldown) == 80u,
               "SPS cooldown offset must remain exact");
_Static_assert(sizeof(gomore_primitives_health_lifecycle_state) == 32u,
               "health lifecycle state layout must remain exact");
_Static_assert(sizeof(gomore_primitives_scaled_sample_state) == 120u,
               "temperature sample state layout must remain exact");
_Static_assert(offsetof(gomore_primitives_scaled_sample_state,
                        attempt_count) == 11u,
               "temperature attempt-count offset must remain exact");
_Static_assert(offsetof(gomore_primitives_scaled_sample_state,
                        measurement_active) == 12u,
               "temperature measurement flag offset must remain exact");
_Static_assert(offsetof(gomore_primitives_scaled_sample_state,
                        capture_enabled) == 14u,
               "temperature capture flag offset must remain exact");
_Static_assert(offsetof(gomore_primitives_scaled_sample_state,
                        capture_count) == 16u,
               "temperature capture-count offset must remain exact");
_Static_assert(offsetof(gomore_primitives_scaled_sample_state,
                        captured) == 18u,
               "temperature capture-array offset must remain exact");
_Static_assert(offsetof(gomore_primitives_health_lifecycle_state,
                        output_record) == 28u,
               "health lifecycle output offset must remain exact");
_Static_assert(sizeof(gomore_primitives_activity_window_state) == 1028u,
               "activity-window state layout must remain exact");
_Static_assert(offsetof(gomore_primitives_activity_window_state,
                        transition_count) == 1008u,
               "activity-window transition offset must remain exact");
_Static_assert(offsetof(gomore_primitives_activity_window_state,
                        positive_windows) == 1024u,
               "activity-window counters offset must remain exact");
_Static_assert(sizeof(gomore_primitives_respiratory_rate_state) == 48u,
               "respiratory-rate state prefix must remain exact");
_Static_assert(offsetof(gomore_primitives_respiratory_rate_state,
                        modulo_counter) == 40u,
               "respiratory-rate modulo offset must remain exact");
_Static_assert(sizeof(gomore_primitives_optical_interval_record) == 16u,
               "optical interval record must remain exact");
_Static_assert(sizeof(gomore_primitives_optical_interval_state) == 1736u,
               "optical interval state must remain exact");
_Static_assert(offsetof(gomore_primitives_optical_interval_state,
                        intervals) == 88u,
               "optical interval bank offset must remain exact");
_Static_assert(offsetof(gomore_primitives_optical_interval_state,
                        signal) == 728u,
               "optical signal offset must remain exact");
_Static_assert(sizeof(gomore_primitives_sleep_stage_stream_state) == 8440u,
               "sleep-stage stream state size must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        previous_timestamp) == 0x2D0u,
               "sleep-stage stream timestamp offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        peaks) == 0x2D6u,
               "sleep-stage stream peaks offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        stage_window) == 0x3ECu,
               "sleep-stage stream window offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        tensor_storage) == 0x55Cu,
               "sleep-stage stream tensor-storage offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        tensor_binding) == 0x20ECu,
               "sleep-stage stream tensor-binding offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        last_tensor_binding) == 0x20F0u,
               "sleep-stage stream final-binding offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_stream_state,
                        selected_stage) == 0x20F4u,
               "sleep-stage stream selected-stage offset must remain exact");
_Static_assert(offsetof(gomore_primitives_sleep_stage_classifier_result,
                        selected) == 16u,
               "sleep-stage classifier selection offset must remain exact");

static void clear_bytes(uint8_t *bytes, size_t count) {
    for (size_t index = 0u; index < count; ++index) {
        bytes[index] = 0u;
    }
}

static void store_u32_le(uint8_t *bytes, uint32_t value) {
    bytes[0] = (uint8_t)(value & UINT32_C(0xFF));
    bytes[1] = (uint8_t)((value >> 8) & UINT32_C(0xFF));
    bytes[2] = (uint8_t)((value >> 16) & UINT32_C(0xFF));
    bytes[3] = (uint8_t)((value >> 24) & UINT32_C(0xFF));
}

static uint16_t load_u16_le_early(const uint8_t *bytes) {
    return (uint16_t)((uint16_t)bytes[0] |
                      (uint16_t)((uint16_t)bytes[1] << 8u));
}

static void store_u16_le_early(uint8_t *bytes, uint16_t value) {
    bytes[0] = (uint8_t)(value & UINT16_C(0xFF));
    bytes[1] = (uint8_t)(value >> 8u);
}

static uint32_t load_u32_le(const uint8_t *bytes) {
    return (uint32_t)bytes[0] |
           (uint32_t)bytes[1] << 8u |
           (uint32_t)bytes[2] << 16u |
           (uint32_t)bytes[3] << 24u;
}

static uint32_t float_bits(float value) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.f = value;
    return pun.u;
}

static float bits_float(uint32_t value) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.u = value;
    return pun.f;
}

static uint32_t float_to_u32_toward_zero(float value) {
    if (!(value > 0.0f)) {
        return 0u;
    }
    if (value >= 0x1p32f) {
        return UINT32_MAX;
    }
    return (uint32_t)value;
}

bool gomore_primitives_records_all_clear(const uint8_t *records,
                                         size_t record_bytes) {
    if (records == NULL ||
            record_bytes < GOMORE_PRIMITIVES_RECORD_COUNT *
                               GOMORE_PRIMITIVES_RECORD_STRIDE) {
        return false;
    }
    for (size_t index = 0u; index < GOMORE_PRIMITIVES_RECORD_COUNT; ++index) {
        if ((records[index * GOMORE_PRIMITIVES_RECORD_STRIDE] & 1u) != 0u) {
            return false;
        }
    }
    return true;
}

void gomore_primitives_record5_initialize(uint32_t record[5],
                                          bool add_record_offset,
                                          uint32_t field4,
                                          uint32_t field8,
                                          uint32_t base) {
    if (record == NULL) {
        return;
    }
    record[1] = field4;
    record[2] = field8;
    record[3] = base;
    record[4] = add_record_offset ? base + UINT32_C(0x14) : 0u;
}

void gomore_primitives_span_initialize(uint32_t record[2],
                                       bool add_record_offset,
                                       uint32_t base) {
    if (record == NULL) {
        return;
    }
    record[0] = base;
    record[1] = add_record_offset ? base + UINT32_C(0x14) : 0u;
}

bool gomore_primitives_clear_two_records(void *record, size_t length) {
    if (record == NULL || length < 0x28u) {
        return false;
    }
    clear_bytes(record, 0x14u);
    clear_bytes((uint8_t *)record + 0x14u, 0x14u);
    return true;
}

bool gomore_primitives_fill_missing_pair(float values[2]) {
    if (values == NULL) {
        return false;
    }
    values[0] = -1.0f;
    values[1] = -1.0f;
    return true;
}

bool gomore_primitives_clear_90(void *record, size_t length) {
    if (record == NULL || length < 0x5Au) {
        return false;
    }
    clear_bytes(record, 0x5Au);
    return true;
}

bool gomore_primitives_prepare_and_score(
    const gomore_primitives_score_providers *providers,
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *workspace, float *output) {
    if (providers == NULL || providers->prepare == NULL ||
            providers->score == NULL || workspace == NULL || output == NULL) {
        return false;
    }
    providers->prepare(first, second, third, fourth, workspace);
    *output = providers->score(workspace);
    return true;
}

bool gomore_primitives_float_in_encoded_range(float value) {
    return float_bits(value) + UINT32_C(0xBDE00000) <=
           UINT32_C(0x01500000);
}

float gomore_primitives_state1_cadence_estimate(
    float first, float middle, float latest, uint8_t *consensus) {
    if (consensus == NULL) {
        return middle;
    }
    *consensus = 0u;
    const bool first_in_range =
        float_bits(first) + UINT32_C(0xBDB7FFFF) < UINT32_C(0x00C3FFFF);
    const bool middle_in_range =
        float_bits(middle) + UINT32_C(0xBDDFFFFF) < UINT32_C(0x00EBFFFF);
    const bool latest_in_range =
        float_bits(latest) + UINT32_C(0xBDB7FFFF) < UINT32_C(0x00C3FFFF);
    if (first_in_range && middle_in_range && latest_in_range) {
        const float first_delta_f32 = first - middle;
        const double first_delta = first_delta_f32 < 0.0f
            ? -(double)first_delta_f32 : (double)first_delta_f32;
        if (first_delta < 10.0) {
            const float latest_delta_f32 = middle - latest;
            const double latest_delta = latest_delta_f32 < 0.0f
                ? -(double)latest_delta_f32 : (double)latest_delta_f32;
            if (latest_delta < 10.0) {
                *consensus = 1u;
            }
        }
    }

    float result = middle;
    if (*consensus == 1u &&
            (int32_t)float_bits(middle) >
                (int32_t)UINT32_C(0x42A00000)) {
        return result;
    }
    if (middle_in_range && latest_in_range) {
        if ((int32_t)float_bits(middle) <
                (int32_t)UINT32_C(0x42A00000)) {
            const float octave_delta_f32 = latest - middle * 2.0f;
            const double octave_delta = octave_delta_f32 < 0.0f
                ? -(double)octave_delta_f32 : (double)octave_delta_f32;
            if (octave_delta < 10.0) {
                result = latest;
            } else if (octave_delta < 15.0) {
                const float outer_delta_f32 = first - latest;
                const double outer_delta = outer_delta_f32 < 0.0f
                    ? -(double)outer_delta_f32 : (double)outer_delta_f32;
                if (outer_delta < 15.0) {
                    result = latest;
                }
            }
        }
        if ((int32_t)float_bits(result) <=
                (int32_t)UINT32_C(0x42480000) &&
                (int32_t)float_bits(middle) <=
                    (int32_t)UINT32_C(0x42480000) &&
                first_in_range) {
            const float crossing_delta_f32 = first - latest * 2.0f;
            const double crossing_delta = crossing_delta_f32 < 0.0f
                ? -(double)crossing_delta_f32 : (double)crossing_delta_f32;
            if (crossing_delta < 6.0) {
                result = first;
            }
        }
    }
    return result;
}

float gomore_primitives_state2_cadence_estimate(
    float first, float middle, float latest, uint8_t *consensus) {
    if (consensus == NULL) {
        return latest;
    }
    *consensus = 0u;
    const bool first_in_range =
        float_bits(first) + UINT32_C(0xBD0FFFFF) < UINT32_C(0x006BFFFF);
    const bool middle_in_range =
        float_bits(middle) + UINT32_C(0xBD0FFFFF) < UINT32_C(0x006BFFFF);
    const bool latest_in_range =
        float_bits(latest) + UINT32_C(0xBD0FFFFF) < UINT32_C(0x006BFFFF);
    if (first_in_range && middle_in_range && latest_in_range) {
        const float first_delta_f32 = first - middle;
        const double first_delta = first_delta_f32 < 0.0f
            ? -(double)first_delta_f32 : (double)first_delta_f32;
        if (first_delta < 10.0) {
            const float latest_delta_f32 = middle - latest;
            const double latest_delta = latest_delta_f32 < 0.0f
                ? -(double)latest_delta_f32 : (double)latest_delta_f32;
            if (latest_delta < 10.0) {
                *consensus = 1u;
            }
        }
    }
    if ((*consensus != 1u ||
            (int32_t)float_bits(latest) <= (int32_t)UINT32_C(0x42F00000)) &&
            middle_in_range && !latest_in_range) {
        return middle;
    }
    return latest;
}

bool gomore_primitives_locomotion_transition_accumulate(
    gomore_primitives_locomotion_transition_state *state,
    float target, uint8_t previous, uint8_t current,
    float shape_first, float shape_second, bool *updated) {
    if (state == NULL || updated == NULL ||
            state->accumulated > (uint32_t)INT32_MAX - (uint32_t)current) {
        return false;
    }
    *updated = false;
    const int32_t accumulated = (int32_t)state->accumulated;
    const int32_t sum = accumulated + (int32_t)current;
    const int32_t consistency = accumulated - (int32_t)previous;

    if (state->initialized) {
        const double sum_f64 = (double)sum;
        if (!((double)state->estimate * 0.9 < sum_f64 &&
                sum_f64 < (double)state->estimate * 1.1) ||
                consistency < -2 || consistency > 2) {
            return true;
        }
        state->accumulated = (uint32_t)sum;
        state->estimate = (float)(
            sum_f64 * 0.25 + (double)state->estimate * 0.75);
        *updated = true;
        return true;
    }

    const float shape_max = shape_first > shape_second
        ? shape_first : shape_second;
    float shape_ratio = 0.0f;
    if (shape_max != 0.0f) {
        const float shape_min = shape_first > shape_second
            ? shape_second : shape_first;
        shape_ratio = shape_min / shape_max;
    }
    const int32_t integer_max = accumulated > (int32_t)current
        ? accumulated : (int32_t)current;
    float integer_ratio = 0.0f;
    if (integer_max != 0) {
        const int32_t integer_min = accumulated > (int32_t)current
            ? (int32_t)current : accumulated;
        integer_ratio = (float)integer_min / (float)integer_max;
    }
    if ((int32_t)float_bits(shape_ratio) >=
            (int32_t)UINT32_C(0x3F19999A) &&
            (float)accumulated > target) {
        return true;
    }
    if ((int32_t)float_bits(integer_ratio) <=
            (int32_t)UINT32_C(0x3F333333) ||
            (double)sum >= (double)target * 2.5 ||
            consistency < -2 || consistency > 2) {
        return true;
    }
    state->accumulated = (uint32_t)sum;
    state->initialized = true;
    state->estimate = (float)sum;
    *updated = true;
    return true;
}

int32_t gomore_primitives_three_axis_window_gate(
    const int16_t *first, const int16_t *second, const int16_t *third,
    size_t sample_count, uint8_t ring_length, int32_t current_index,
    uint32_t window_count, int32_t primary_threshold,
    int32_t secondary_threshold) {
    if (first == NULL || second == NULL || third == NULL ||
            ring_length == 0u || ring_length > INT8_MAX ||
            (size_t)ring_length > sample_count || current_index < 0 ||
            current_index >= (int32_t)ring_length ||
            window_count > (uint32_t)ring_length) {
        return -1;
    }
    int32_t sums[3] = {0, 0, 0};
    uint8_t primary_counts[3] = {0u, 0u, 0u};
    uint8_t secondary_counts[3] = {0u, 0u, 0u};
    const int16_t *const channels[3] = {first, second, third};
    for (uint32_t offset = 1u; offset <= window_count; ++offset) {
        int32_t index = current_index - (int32_t)offset;
        if (index < 0) {
            index += (int32_t)ring_length;
        }
        for (size_t channel = 0u; channel < 3u; ++channel) {
            const int32_t sample = channels[channel][(size_t)index];
            sums[channel] += sample;
            if (sample > primary_threshold) {
                ++primary_counts[channel];
            }
            if (sample > secondary_threshold) {
                ++secondary_counts[channel];
            }
        }
    }

    int32_t maximum = 0;
    int32_t second_maximum = 0;
    size_t maximum_index = 0u;
    size_t second_index = 0u;
    for (size_t channel = 0u; channel < 3u; ++channel) {
        if (sums[channel] > maximum) {
            second_maximum = maximum;
            second_index = maximum_index;
            maximum = sums[channel];
            maximum_index = channel;
        } else if (sums[channel] > second_maximum) {
            second_maximum = sums[channel];
            second_index = channel;
        }
    }
    return primary_counts[maximum_index] >= 3u &&
           secondary_counts[second_index] >= 3u ? 1 : -1;
}

bool gomore_primitives_locomotion_window_classify(
    void *state, size_t state_length,
    void *output, size_t output_length,
    const gomore_primitives_locomotion_classifier_configuration *configuration) {
    if (state == NULL || state_length < 0x26Eu || output == NULL ||
            output_length < 0x3Eu || configuration == NULL ||
            configuration->ring_score_model == NULL ||
            configuration->linear_sign_coefficients == NULL ||
            configuration->autocorrelation == NULL ||
            configuration->crossing_estimate == NULL) {
        return false;
    }

    uint8_t *const state_bytes = state;
    uint8_t *const output_bytes = output;
    int16_t *const x_standard_deviation = (int16_t *)&state_bytes[0x02u];
    int16_t *const z_mean = (int16_t *)&state_bytes[0x12u];
    int16_t *const magnitude_standard_deviation =
        (int16_t *)&state_bytes[0x22u];
    int16_t *const magnitude_mean = (int16_t *)&state_bytes[0x32u];
    int16_t *const magnitude_range = (int16_t *)&state_bytes[0x42u];
    uint16_t *const magnitude_history = (uint16_t *)&state_bytes[0x54u];
    int16_t *const y_standard_deviation = (int16_t *)&state_bytes[0x204u];
    int16_t *const z_standard_deviation = (int16_t *)&state_bytes[0x214u];
    int16_t *const magnitude_mean_absolute_difference =
        (int16_t *)&state_bytes[0x224u];
    int16_t *const x_mean_absolute_difference =
        (int16_t *)&state_bytes[0x234u];
    int16_t *const y_mean_absolute_difference =
        (int16_t *)&state_bytes[0x244u];
    int16_t *const z_mean_absolute_difference =
        (int16_t *)&state_bytes[0x254u];
    const int32_t cursor = (int32_t)(int8_t)state_bytes[0x52u];
    if (cursor < 0 || cursor >= 8) {
        return false;
    }

    store_u32_le(&output_bytes[0x08u], float_bits(
        gomore_primitives_nonzero_i16_mean8(magnitude_mean)));
    store_u32_le(&output_bytes[0x0Cu], float_bits(
        gomore_primitives_nonzero_i16_mean8(z_mean)));
    store_u32_le(&output_bytes[0x04u], float_bits(
        gomore_primitives_nonzero_i16_mean8(x_standard_deviation)));
    store_u32_le(&output_bytes[0x00u], float_bits(
        gomore_primitives_nonzero_i16_mean8(
            magnitude_standard_deviation)));

    const int32_t primary_predicate =
        gomore_primitives_circular_count_predicate(
            magnitude_range, 8u, cursor, 5, 130, 20000,
            UINT8_C(0x3E), 3);
    float autocorrelation[5];
    uint32_t packed_counts = 0u;
    float shape[2] = {0.0f, 0.0f};
    if (!gomore_primitives_locomotion_autocorrelation_wrapper(
            primary_predicate == 1,
            &magnitude_history[75], autocorrelation,
            (uintptr_t)&packed_counts, (uintptr_t)shape,
            configuration->autocorrelation)) {
        return false;
    }
    store_u32_le(&output_bytes[0x20u], float_bits(autocorrelation[0]));
    store_u32_le(&output_bytes[0x28u], float_bits(autocorrelation[1]));
    store_u32_le(&output_bytes[0x2Cu], float_bits(autocorrelation[2]));
    store_u32_le(&output_bytes[0x30u], float_bits(autocorrelation[3]));
    store_u32_le(&output_bytes[0x34u], float_bits(autocorrelation[4]));

    uint8_t hysteresis_crossings = 0u;
    float crossing_mode2 = 0.0f;
    float crossing_mode1 = 0.0f;
    if (primary_predicate == 1) {
        hysteresis_crossings = gomore_primitives_count_hysteresis_crossings(
            magnitude_history, 200u);
        if (!gomore_primitives_locomotion_crossing_wrapper(
                magnitude_mean, cursor, magnitude_history, 200u,
                &crossing_mode2, &crossing_mode1,
                configuration->crossing_estimate)) {
            return false;
        }
    }
    const float output_primary = bits_float(load_u32_le(&output_bytes[0x00u]));
    const float output_magnitude_mean =
        bits_float(load_u32_le(&output_bytes[0x08u]));
    if ((output_primary < 150.0f && crossing_mode1 > 130.0f) ||
            (output_magnitude_mean < 1100.0f &&
             hysteresis_crossings < 13u && crossing_mode1 > 130.0f)) {
        crossing_mode1 *= 0.5f;
    }
    store_u32_le(&output_bytes[0x10u], float_bits(crossing_mode1));
    store_u32_le(&output_bytes[0x14u], float_bits(crossing_mode2));
    output_bytes[0x38u] = (uint8_t)primary_predicate;

    if (autocorrelation[1] <= 0.0f) {
        output_bytes[0x3Du] = UINT8_MAX;
    } else {
        const int8_t count0 = (int8_t)(packed_counts & UINT32_C(0xFF));
        const int8_t count1 =
            (int8_t)((packed_counts >> 8u) & UINT32_C(0xFF));
        float ratio = 0.0f;
        if (count0 != 0) {
            ratio = (float)count1 / (float)count0;
        }
        output_bytes[0x3Du] = (uint8_t)
            gomore_primitives_linear_sign_classify(
                shape[0], shape[1], ratio, (int32_t)count0,
                configuration->linear_sign_coefficients,
                configuration->linear_sign_bias);
    }

    output_bytes[0x39u] = (uint8_t)
        gomore_primitives_circular_signal_predicate(
            magnitude_range, x_standard_deviation,
            y_standard_deviation, z_standard_deviation,
            8u, cursor, 5u);
    int16_t ring_score = 0;
    if (!gomore_primitives_six_channel_ring_score(
            magnitude_range, magnitude_standard_deviation,
            magnitude_mean_absolute_difference,
            x_mean_absolute_difference, y_mean_absolute_difference,
            z_mean_absolute_difference, 8u, (size_t)cursor, 3u,
            configuration->ring_score_model, &ring_score)) {
        return false;
    }
    output_bytes[0x3Au] = (uint8_t)
        gomore_primitives_shift_i16_trend_gate5(
            (int16_t *)&state_bytes[0x264u], (int32_t)ring_score);
    output_bytes[0x3Bu] = (uint8_t)
        gomore_primitives_circular_count_predicate(
            magnitude_range, 8u, cursor, 5, 1900, 20000,
            UINT8_C(0x3E), 3);
    output_bytes[0x3Cu] = (uint8_t)
        gomore_primitives_three_axis_window_gate(
            x_standard_deviation, y_standard_deviation,
            z_standard_deviation, 8u, 8u, cursor, 5u, 400, 400);
    return true;
}

bool gomore_primitives_motion_iir4_filter(
    float *samples, size_t count,
    float input_history[5], float output_history[5]) {
    if (samples == NULL || input_history == NULL || output_history == NULL ||
            count < 5u || count > 30u) {
        return false;
    }
    static const uint32_t numerator_bits[5] = {
        UINT32_C(0x3C87D6D4), UINT32_C(0x00000000),
        UINT32_C(0xBD07D6D4), UINT32_C(0x00000000),
        UINT32_C(0x3C87D6D4),
    };
    static const uint32_t denominator_bits[5] = {
        UINT32_C(0x3F800000), UINT32_C(0xC06425DA),
        UINT32_C(0x4099D857), UINT32_C(0xC03A6D39),
        UINT32_C(0x3F2BA321),
    };
    float filtered[30];
    for (size_t sample_index = 0u; sample_index < count; ++sample_index) {
        float value = 0.0f;
        for (size_t coefficient = 0u; coefficient < 5u; ++coefficient) {
            const float input = sample_index >= coefficient
                ? samples[sample_index - coefficient]
                : input_history[5u + sample_index - coefficient];
            value += input * bits_float(numerator_bits[coefficient]);
        }
        filtered[sample_index] = value;
    }
    for (size_t sample_index = 0u; sample_index < count; ++sample_index) {
        float feedback = 0.0f;
        for (size_t coefficient = 1u; coefficient < 5u; ++coefficient) {
            const float prior = sample_index >= coefficient
                ? filtered[sample_index - coefficient]
                : output_history[5u + sample_index - coefficient];
            feedback += prior * bits_float(denominator_bits[coefficient]);
        }
        filtered[sample_index] -= feedback;
    }
    for (size_t index = 0u; index < 5u; ++index) {
        input_history[index] = samples[count - 5u + index];
        output_history[index] = filtered[count - 5u + index];
    }
    for (size_t index = 0u; index < count; ++index) {
        samples[index] = filtered[index];
    }
    return true;
}

bool gomore_primitives_weighted_histogram6_accumulate(
    float value, float denominator, float numerator,
    const float boundaries[5], float sums[6], float counts[6],
    float below_range_weight) {
    if (boundaries == NULL || sums == NULL || counts == NULL) {
        return false;
    }
    if (!(denominator > 0.0f)) {
        return true;
    }
    const float normalized = numerator / denominator;
    if (!(value >= boundaries[0])) {
        sums[0] += normalized * below_range_weight;
        counts[0] += 1.0f;
        return true;
    }
    size_t bin = 1u;
    while (bin < 5u && !(value < boundaries[bin])) {
        ++bin;
    }
    sums[bin] += normalized;
    counts[bin] += 1.0f;
    return true;
}

uint32_t gomore_primitives_speed_smoother_update(
    gomore_primitives_speed_smoother *state,
    float input, uint32_t interval_milliseconds,
    float *output, uint8_t *stable_or_clamped) {
    if (state == NULL || output == NULL || stable_or_clamped == NULL) {
        return UINT32_C(0x138B);
    }
    if (state->enabled != 1u) {
        return UINT32_C(0x1389);
    }
    if (interval_milliseconds < UINT32_C(700) ||
            interval_milliseconds > UINT32_C(1300)) {
        return UINT32_C(0x138A);
    }
    if (state->maximum_raw_rise == 0.0f ||
            state->maximum_raw_fall == 0.0f ||
            state->maximum_output_rise == 0.0f ||
            state->maximum_output_fall == 0.0f) {
        return UINT32_C(0x138B);
    }

    const uint8_t prior_count = state->sample_count;
    float selected_input = input;
    if (prior_count > 1u) {
        const float delta = input - state->previous_raw_input;
        if (delta > state->maximum_raw_rise) {
            selected_input =
                state->previous_raw_input + state->maximum_raw_rise;
        } else if (delta < -state->maximum_raw_fall) {
            selected_input =
                state->previous_raw_input - state->maximum_raw_fall;
        }
    }
    state->previous_raw_input = input;
    if (prior_count == 0u) {
        selected_input = input;
    }

    float candidate;
    if (prior_count < 10u) {
        state->sum += selected_input;
        state->sample_count = (uint8_t)(prior_count + 1u);
        candidate = state->sum / (float)state->sample_count;
    } else {
        candidate =
            selected_input * bits_float(UINT32_C(0x3EB33333)) +
            state->output * bits_float(UINT32_C(0x3F266666));
    }
    if (state->sample_count == 1u) {
        state->output = candidate;
    }

    const float prior_output = state->output;
    const float output_delta = candidate - prior_output;
    if (output_delta > state->maximum_output_rise) {
        candidate = prior_output + state->maximum_output_rise;
        *stable_or_clamped = 1u;
    } else if (output_delta < -state->maximum_output_fall) {
        candidate = prior_output - state->maximum_output_fall;
        *stable_or_clamped = 1u;
    } else {
        *stable_or_clamped = prior_output == candidate ? 1u : 0u;
    }
    state->output = candidate;
    *output = candidate;
    return UINT32_MAX;
}

float gomore_primitives_speed_gate(
    float raw_candidate, float previous_output,
    float history[6], int32_t sample_index, uint32_t flags) {
    if (history == NULL || sample_index < 0) {
        return raw_candidate;
    }

    const float selection_threshold =
        bits_float(UINT32_C(0x41DD851F));
    const float unflagged_rise = bits_float(UINT32_C(0x4039999A));
    float average = 0.0f;

    if (sample_index == 0 && raw_candidate >= 15.0f) {
        return 0.0f;
    }

    if ((flags & UINT32_C(0x1444)) == 0u) {
        if (sample_index < 4) {
            history[sample_index] = raw_candidate;
        } else {
            history[4] = raw_candidate;
            average = history[0] + history[1];
            average += history[2];
            average += history[3];
            average += history[4];
            average /= 5.0f;
            history[0] = history[1];
            history[1] = history[2];
            history[2] = history[3];
            history[3] = history[4];
        }
        if (average >= selection_threshold ||
                (average > 15.0f &&
                 average - previous_output >= unflagged_rise)) {
            return average;
        }
        return raw_candidate;
    }

    float rise_limit =
        5.5f - previous_output * bits_float(UINT32_C(0x3EEAA64C));
    if (rise_limit <= 0.0f) {
        rise_limit = 0.0f;
    }
    float selected = raw_candidate;
    if (raw_candidate - previous_output > rise_limit) {
        selected = previous_output + rise_limit;
    }

    if (sample_index < 5) {
        history[sample_index] = selected;
        average = history[0];
        for (int32_t index = 1; index <= sample_index; ++index) {
            average += history[index];
        }
        average /= (float)(sample_index + 1);
    } else {
        history[5] = selected;
        average = history[0] + history[1];
        average += history[2];
        average += history[3];
        average += history[4];
        average += history[5];
        average /= 6.0f;
        history[0] = history[1];
        history[1] = history[2];
        history[2] = history[3];
        history[3] = history[4];
        history[4] = history[5];
    }

    if (average >= selection_threshold ||
            rise_limit < average - previous_output) {
        return average;
    }
    return raw_candidate;
}

float gomore_primitives_speed_dynamics_baseline(
    float input, float auxiliary,
    float state_first_parameter, float state_second_parameter,
    uint16_t flags, gomore_primitives_float_binary_fn power) {
    if (!(input >= 0.0f) || power == NULL) {
        return 0.0f;
    }

    float normalized_input = input;
    float subunit_scale = 1.0f;
    if ((int32_t)float_bits(input) < (int32_t)UINT32_C(0x3F800000)) {
        normalized_input = 1.0f;
        subunit_scale = input;
    }

    const float cubic_coefficient = bits_float(UINT32_C(0x3E1704FF));
    float cubic = normalized_input * cubic_coefficient;
    cubic *= normalized_input;
    cubic *= normalized_input;

    float calibration;
    if ((flags & UINT16_C(0x0440)) != 0u &&
            (int32_t)float_bits(normalized_input) <=
                (int32_t)UINT32_C(0x3FA00000)) {
        calibration = state_first_parameter *
                      bits_float(UINT32_C(0x3CBD230C));
    } else {
        calibration = auxiliary * bits_float(UINT32_C(0xBAAA3573));
        calibration += normalized_input * bits_float(UINT32_C(0x3AFD428B));
        calibration += bits_float(UINT32_C(0x3E91BAD6));
        calibration /= bits_float(UINT32_C(0x3FE6B205));
        calibration *= state_first_parameter;
    }

    const float auxiliary_minutes = auxiliary /
                                    bits_float(UINT32_C(0x42700000));
    float linear = state_second_parameter * 2.0f;
    linear *= bits_float(UINT32_C(0x411CF5C3));
    linear *= calibration;
    linear *= auxiliary_minutes;

    float quadratic = power(normalized_input, 2.0f);
    float quadratic_scale = state_second_parameter *
                            bits_float(UINT32_C(0x3D1A2C67));
    quadratic *= quadratic_scale;
    quadratic *= auxiliary_minutes;

    float total = cubic + linear;
    total += quadratic;
    float rounded = gomore_primitives_round_decimal_places(
        total, 5.0f, power);
    if (!(rounded > 0.0f)) {
        return 0.0f;
    }
    rounded = gomore_primitives_round_decimal_places(total, 5.0f, power);
    if ((flags & UINT16_C(0x0440)) == 0u) {
        rounded *= subunit_scale;
    }
    rounded *= bits_float(UINT32_C(0x3F0DD2F2));
    return rounded;
}

static int32_t dormant_estimator_float_to_i32(float value) {
    if (value != value) {
        return 0;
    }
    if (value >= bits_float(UINT32_C(0x4F000000))) {
        return INT32_MAX;
    }
    if (value <= -bits_float(UINT32_C(0x4F000000))) {
        return INT32_MIN;
    }
    return (int32_t)value;
}

int32_t gomore_primitives_dormant_estimator_update(
    void *state, size_t state_length, uint32_t elapsed,
    const uint32_t *current_time, const float *selected_heart_rate,
    const float *selected_speed, const float profile[6],
    const float auxiliary[3], const float *total_energy,
    void *output, size_t output_length,
    gomore_primitives_record_step_fn process_record) {
    if (state == NULL ||
            state_length < GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES) {
        return -1;
    }
    uint8_t *state_bytes = state;
    const uint32_t mode = load_u32_le(&state_bytes[0x330u]);
    if (mode == 0u) {
        return 1;
    }
    if (current_time == NULL || selected_heart_rate == NULL ||
            selected_speed == NULL || profile == NULL || auxiliary == NULL ||
            total_energy == NULL ||
            (mode == 1u &&
             (output == NULL ||
              output_length < GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_OUTPUT_BYTES ||
              process_record == NULL))) {
        return -1;
    }

    float configuration[4] = {
        profile[0], profile[1], profile[2], profile[5],
    };
    const uint32_t prior_updates = load_u32_le(&state_bytes[0x32Cu]);
    if (prior_updates != 0u) {
        store_u32_le(&state_bytes[0x328u],
                     load_u32_le(&state_bytes[0x328u]) + elapsed);
    }

    gomore_primitives_dormant_estimator_record record = {
        .current_time = *current_time,
        .sample_index = load_u32_le(&state_bytes[0x328u]),
        .selected_heart_rate =
            dormant_estimator_float_to_i32(*selected_heart_rate),
        .selected_speed = *selected_speed,
        .current_auxiliary = auxiliary[1],
        .copied_auxiliary_1 = auxiliary[0],
        .copied_auxiliary_2 = auxiliary[2],
        .configuration = configuration,
        .trailing_total_energy = *total_energy,
    };
    if (state_bytes[0x334u] != 0u) {
        record.selected_heart_rate = -1;
        record.selected_speed = -1.0f;
    }

    if (mode == 1u) {
        (void)gomore_primitives_sequence_replay(
            state, state_length, &record, sizeof(record), process_record);
        (void)gomore_primitives_status_record_extract(
            state, state_length, output, output_length);
    }
    store_u32_le(&state_bytes[0x32Cu], prior_updates + 1u);
    return 0;
}

int32_t gomore_primitives_sleep_motion_feature(
    gomore_primitives_sleep_motion_state *state, uint32_t mode,
    const float *channels[3], bool input_unavailable, float output[2],
    gomore_primitives_float_unary_fn floor_value,
    gomore_primitives_float_unary_fn square_root) {
    _Static_assert(sizeof(gomore_primitives_sleep_motion_state) == 128u,
                   "sleep motion state layout must match the recovered ABI");
    if (state == NULL || output == NULL ||
            (!input_unavailable &&
             (channels == NULL || channels[0] == NULL ||
              channels[1] == NULL || channels[2] == NULL ||
              floor_value == NULL || square_root == NULL))) {
        return -1;
    }

    float samples[30] = {0.0f};
    output[0] = 0.0f;
    output[1] = 0.0f;
    if (mode > 1u || input_unavailable) {
        (void)gomore_primitives_clear_124(state, sizeof(*state));
    }
    if (input_unavailable) {
        (void)gomore_primitives_fill_missing_pair(output);
        return UINT32_C(0x40);
    }

    for (size_t axis = 0u; axis < 3u; ++axis) {
        gomore_primitives_linear_resample(
            channels[axis], 25, 30, 25, samples);
        (void)gomore_primitives_scale_milli(samples, 30u);
        (void)gomore_primitives_motion_iir4_filter(
            samples, 30u, state->input_history[axis],
            state->output_history[axis]);
        for (size_t index = 0u; index < 10u; ++index) {
            samples[index] = samples[index * 3u];
        }
        const float quantized =
            gomore_primitives_sleep_quantized_magnitude10(
                samples, floor_value);
        output[0] += quantized * quantized;
        const float magnitude = gomore_primitives_magnitude_score10(
            state->magnitude_threshold, samples);
        output[1] += magnitude * magnitude;
    }

    if (state->warmup_count < 5u) {
        ++state->warmup_count;
        (void)gomore_primitives_fill_missing_pair(output);
        return UINT32_C(0x41);
    }
    output[0] = square_root(output[0]);
    output[1] = square_root(output[1]);
    return 0;
}

bool gomore_primitives_minute_accumulator_update(
    gomore_primitives_minute_accumulator *state,
    uint32_t elapsed_seconds, uint32_t current_time, float sample) {
    _Static_assert(sizeof(gomore_primitives_minute_accumulator) == 72u,
                   "minute accumulator layout must match the recovered ABI");
    if (state == NULL) {
        return false;
    }

    uint32_t cursor = current_time - elapsed_seconds;
    if (cursor != 0u && current_time / 60u != cursor / 60u) {
        float completed = state->previous_zero_fraction;
        if (state->valid_count >= 1) {
            completed = (float)state->zero_count /
                        (float)state->valid_count;
            state->previous_zero_fraction = completed;
        }
        state->minute_zero_fraction[(cursor / 60u) % 15u] = completed;

        if (elapsed_seconds < 900u) {
            cursor += 60u;
            while (cursor < current_time) {
                state->minute_zero_fraction[(cursor / 60u) % 15u] =
                    state->previous_zero_fraction;
                cursor += 60u;
            }
        } else {
            (void)gomore_primitives_clear_72(state, sizeof(*state));
        }
        state->valid_count = 0;
        state->zero_count = 0;
        state->integer_sum = 0;
    }

    if (sample >= 0.0f) {
        state->valid_count = (int8_t)((uint8_t)state->valid_count + 1u);
        if (sample == 0.0f) {
            state->zero_count = (int8_t)((uint8_t)state->zero_count + 1u);
        }
        const int32_t converted = dormant_estimator_float_to_i32(sample);
        state->integer_sum = (int32_t)(
            (uint32_t)state->integer_sum + (uint32_t)converted);
    }
    return true;
}

bool gomore_primitives_tensor_bank_initialize(
    uintptr_t *layout, size_t layout_capacity,
    bool include_secondary_bank, bool paired, uint32_t item_count,
    uint32_t *tensor_bindings, size_t tensor_binding_capacity,
    uint8_t *records, size_t record_count,
    uintptr_t runtime_binding, uintptr_t pool_binding,
    gomore_primitives_tensor_fill_binding_fn create_filled_tensor) {
    if (layout == NULL || layout_capacity < 3u ||
            (item_count != 0u &&
             (tensor_bindings == NULL || records == NULL ||
              create_filled_tensor == NULL))) {
        return false;
    }
    const size_t count = (size_t)item_count;
    const size_t lanes = paired ? 2u : 1u;
    const size_t records_per_item = paired ? 4u : 2u;
    const size_t groups = include_secondary_bank ? 2u : 1u;
    if (count > SIZE_MAX / lanes ||
            count > SIZE_MAX / records_per_item ||
            count * records_per_item > SIZE_MAX / groups) {
        return false;
    }
    const size_t cursor_extent = count * lanes;
    const size_t required_records = count * records_per_item * groups;
    if (required_records > SIZE_MAX / 20u) {
        return false;
    }
    size_t required_layout = 3u;
    size_t required_bindings = 0u;
    if (count != 0u) {
        const size_t last_cursor = cursor_extent - lanes;
        const size_t maximum_offset = include_secondary_bank
            ? (paired ? 10u : 9u)
            : (paired ? 6u : 5u);
        if (last_cursor > SIZE_MAX - maximum_offset) {
            return false;
        }
        required_layout = last_cursor + maximum_offset + 1u;
        required_bindings = last_cursor + 1u;
    }
    if (layout_capacity < required_layout ||
            tensor_binding_capacity < required_bindings ||
            record_count < required_records) {
        return false;
    }

    layout[0] = include_secondary_bank ? 1u : 0u;
    layout[1] = paired ? 1u : 0u;
    layout[2] = (uintptr_t)item_count;
    size_t cursor = 0u;
    size_t record_index = 0u;
    for (size_t item = 0u; item < count; ++item) {
        (void)item;
        layout[cursor + 3u] =
            (uintptr_t)&records[record_index * 20u];
        layout[cursor + 5u] =
            (uintptr_t)&records[(record_index + 1u) * 20u];
        if (tensor_bindings[cursor] == 0u) {
            const uint16_t dimensions[1] = {
                load_u16_le_early(
                    &records[(record_index + 1u) * 20u + 10u]),
            };
            tensor_bindings[cursor] = create_filled_tensor(
                runtime_binding, pool_binding, 1u,
                dimensions, 1u, 0.0f);
        }
        if (paired) {
            layout[cursor + 4u] =
                (uintptr_t)&records[(record_index + 2u) * 20u];
            layout[cursor + 6u] =
                (uintptr_t)&records[(record_index + 3u) * 20u];
        }
        cursor += lanes;
        record_index += records_per_item;
    }

    if (include_secondary_bank) {
        cursor = 0u;
        for (size_t item = 0u; item < count; ++item) {
            (void)item;
            layout[cursor + 7u] =
                (uintptr_t)&records[record_index * 20u];
            layout[cursor + 9u] =
                (uintptr_t)&records[(record_index + 1u) * 20u];
            if (paired) {
                layout[cursor + 8u] =
                    (uintptr_t)&records[(record_index + 2u) * 20u];
                layout[cursor + 10u] =
                    (uintptr_t)&records[(record_index + 3u) * 20u];
            }
            cursor += lanes;
            record_index += records_per_item;
        }
    }
    return true;
}

bool gomore_primitives_sleep_iir2_filter(float *samples, size_t count) {
    if (samples == NULL && count != 0u) {
        return false;
    }
    const float feedback_1 = bits_float(UINT32_C(0xBFE71223));
    const float feedback_2 = bits_float(UINT32_C(0x3F511616));
    const float feedforward_0 = bits_float(UINT32_C(0x3DBBA7A8));
    const float feedforward_1 = bits_float(UINT32_C(0x00000000));
    const float feedforward_2 = bits_float(UINT32_C(0xBDBBA7A8));
    float input_history[2] = {0.0f, 0.0f};
    float output_history[2] = {0.0f, 0.0f};
    for (size_t index = 0u; index < count; ++index) {
        const float input = samples[index];
        double accumulated = (double)(feedforward_0 * input);
        accumulated += (double)(input_history[0] * feedforward_1);
        accumulated -= (double)(output_history[0] * feedback_1);
        accumulated += (double)(input_history[1] * feedforward_2);
        accumulated -= (double)(output_history[1] * feedback_2);
        const float filtered = (float)accumulated;
        input_history[1] = input_history[0];
        input_history[0] = input;
        output_history[1] = output_history[0];
        output_history[0] = filtered;
        samples[index] = filtered;
    }
    return true;
}

bool gomore_primitives_sleep_step_update(
    gomore_primitives_sleep_step_state *state,
    uint32_t elapsed_seconds, const uint8_t control[2],
    uint32_t current_time, int16_t utc_offset_minutes,
    float minute_sample, float ring_sample, bool external_activity,
    const uint8_t local_hour_window[8],
    gomore_primitives_civil_time *civil_time,
    bool *civil_time_updated) {
    _Static_assert(offsetof(gomore_primitives_sleep_step_state,
                            decimated_ring) == 0x48u,
                   "sleep-step ring offset must match the recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_step_state, active) ==
                       0xA8u,
                   "sleep-step active offset must match the recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_step_state, countdown) ==
                       0xB0u,
                   "sleep-step countdown offset must match the recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_step_state,
                            local_time_window) == 0xB6u,
                   "sleep-step local-window offset must match recovered ABI");
    if (state == NULL || control == NULL || local_hour_window == NULL ||
            civil_time_updated == NULL ||
            (control[0] == 0u && civil_time == NULL)) {
        return false;
    }

    *civil_time_updated = false;
    if (control[0] == 0u) {
        const uint32_t local_time = current_time +
            (uint32_t)((int32_t)utc_offset_minutes * INT32_C(60));
        if (!gomore_primitives_epoch_to_civil_time(local_time, civil_time)) {
            return false;
        }
        state->local_time_window =
            civil_time->hour < local_hour_window[6] &&
            local_hour_window[7] <= civil_time->hour ? 1u : 0u;
        *civil_time_updated = true;
    }

    if (!gomore_primitives_decimated_ring_write(
            ring_sample, state->decimated_ring,
            elapsed_seconds, current_time) ||
            !gomore_primitives_minute_accumulator_update(
                &state->minute_accumulator,
                elapsed_seconds, current_time, minute_sample)) {
        return false;
    }
    state->active = !external_activity || state->activity_latch != 0u
        ? 1u : 0u;

    if (control[1] == 3u) {
        state->countdown = UINT32_C(1200);
    } else if (control[1] == 1u || control[1] == 2u) {
        state->countdown = UINT32_C(300);
    }
    state->countdown = elapsed_seconds < state->countdown
        ? state->countdown - elapsed_seconds : 0u;
    return true;
}

bool gomore_primitives_sleep_stage_decide(
    const void *state, size_t state_length,
    uint32_t current_time, uint32_t elapsed_seconds,
    uint32_t reference_time, uint8_t prior_stage,
    bool external_active, float preceding_fraction,
    gomore_primitives_sleep_stage_decision *decision) {
    if (state == NULL || state_length < 0xB7u || decision == NULL) {
        return false;
    }
    const uint8_t *const bytes = state;
    gomore_primitives_sleep_stage_decision result = {0u, 0u, 0u, 0u, 0};

    if (bytes[0xB4u] == 1u) {
        result.stage = 1u;
        result.reason = 5u;
    } else if ((int32_t)load_u32_le(&bytes[0xB0u]) > 0) {
        result.stage = prior_stage;
        result.reason = 7u;
    } else if (external_active) {
        result.stage = prior_stage;
        result.reason = 6u;
    } else if (elapsed_seconds > 600u) {
        result.adjustment = -(int32_t)(elapsed_seconds / 60u);
        result.reason = 3u;
    } else if (prior_stage == 1u &&
            current_time - reference_time >= UINT32_C(0xA8C0)) {
        result.reason = 8u;
    } else {
        const bool flag_a8 = bytes[0xA8u] == 1u;
        const bool flag_a9 = bytes[0xA9u] != 0u;
        const bool transition_blocked =
            gomore_primitives_state_window_predicate(
                prior_stage == 1u, current_time,
                load_u32_le(&bytes[0xA4u]), flag_a8, flag_a9);
        if (transition_blocked || flag_a9) {
            result.adjustment = flag_a9 ? -5 : -15;
            result.reason = 4u;
        } else {
            uint32_t high_count = 0u;
            uint32_t valid_count = 0u;
            uint32_t valid_sum = 0u;
            for (size_t index = 0u; index < 15u; ++index) {
                const float fraction =
                    bits_float(load_u32_le(&bytes[index * 4u]));
                if (fraction >= bits_float(UINT32_C(0x3F75C28F))) {
                    ++high_count;
                }
                const uint8_t value = bytes[0x48u + index];
                if (value >= 40u && value <= 240u) {
                    ++valid_count;
                    valid_sum += value;
                }
            }
            const float high_fraction = (float)high_count / 15.0f;
            const float valid_average = valid_count == 0u ? 0.0f :
                (float)valid_sum / (float)valid_count;
            const uint32_t minute = (current_time - elapsed_seconds) / 60u;
            const size_t ring_index =
                (size_t)(((minute * 60u - 1u) / 60u) % 15u);
            const float current_fraction = bits_float(load_u32_le(
                &bytes[ring_index * 4u]));
            const float previous_fraction = ring_index == 0u ?
                preceding_fraction : bits_float(load_u32_le(
                    &bytes[(ring_index - 1u) * 4u]));

            if (prior_stage == 0u) {
                if (high_fraction >= 0.4f && valid_average < 100.0f &&
                        current_time - load_u32_le(&bytes[0xACu]) > 300u) {
                    result.stage = 1u;
                } else {
                    result.reason = valid_average < 100.0f ? 1u : 2u;
                }
            } else if (valid_average >= 100.0f) {
                result.reason = 2u;
            } else if (high_fraction < 0.3f ||
                    (current_fraction < 0.3f && previous_fraction < 0.3f) ||
                    (bytes[0xB6u] == 1u &&
                     (int32_t)load_u32_le(&bytes[0x44u]) > 3000)) {
                result.reason = 1u;
            } else {
                result.stage = 1u;
            }
        }
    }

    if (result.stage == 0u && prior_stage == 1u) {
        result.transition = 1u;
    } else if (result.stage == 1u && prior_stage == 0u) {
        result.transition = result.reason == 5u ? 4u : 2u;
    }
    *decision = result;
    return true;
}

bool gomore_primitives_sleep_cycle_update(
    gomore_primitives_sleep_cycle_state *state,
    const gomore_primitives_sleep_cycle_input *input,
    gomore_primitives_sleep_interval_result *output) {
    _Static_assert(sizeof(gomore_primitives_sleep_step_state) == 0xB8u,
                   "sleep-cycle step extent must match the recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_cycle_state,
                            last_decision) == 0xB8u,
                   "sleep-cycle decision offset must match recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_cycle_state,
                            current) == 0xC0u,
                   "sleep-cycle current-record offset must match recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_cycle_state,
                            previous_descriptor) == 0xE8u,
                   "sleep-cycle prior-descriptor offset must match recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_cycle_state,
                            previous_interval) == 0x110u,
                   "sleep-cycle prior-interval offset must match recovered ABI");
    _Static_assert(offsetof(gomore_primitives_sleep_cycle_state,
                            policy) == 0x130u,
                   "sleep-cycle policy offset must match recovered ABI");
    if (state == NULL || input == NULL || output == NULL) {
        return false;
    }

    uint8_t *const step_bytes = (uint8_t *)&state->step;
    const uint8_t active = input->input_active ? 1u : 0u;
    state->step.activity_latch = active;
    state->step.active = active;
    const bool output_had_flags = output->flags != 0u;
    if (active == 0u && state->step.countdown == 0u && !output_had_flags) {
        state->step.countdown = 300u;
        store_u32_le(&step_bytes[0xACu], input->current_time);
    } else if (active != 0u && !output_had_flags &&
            (state->previous_interval.flags == 0u ||
             ((state->previous_interval.flags == 12u ||
               state->previous_interval.flags == 28u) &&
              input->current_time -
                  load_u32_le(&step_bytes[0xACu]) > 840u))) {
        store_u32_le(&step_bytes[0xACu], 0u);
    }
    if (active == 0u) {
        store_u32_le(&step_bytes[0xA4u], 0u);
    } else if (load_u32_le(&step_bytes[0xA4u]) == 0u) {
        store_u32_le(&step_bytes[0xA4u], input->current_time);
    }

    output->flags = 0u;
    if (state->last_decision.stage == 1u &&
            state->step.activity_latch != 0u &&
            input->current_time -
                load_u32_le(&step_bytes[0xA4u]) < 300u) {
        state->step.activity_latch = 0u;
    }
    gomore_primitives_civil_time civil_time;
    bool civil_time_updated = false;
    if (!gomore_primitives_sleep_step_update(
            &state->step, input->elapsed_seconds,
            (const uint8_t *)&state->last_decision,
            input->current_time, input->utc_offset_minutes,
            input->minute_sample, input->ring_sample, active == 0u,
            (const uint8_t *)&state->policy, &civil_time,
            &civil_time_updated)) {
        return false;
    }
    (void)civil_time_updated;

    gomore_primitives_sleep_stage_decision decision;
    if (!gomore_primitives_sleep_stage_decide(
            &state->step, sizeof(state->step), input->current_time,
            input->elapsed_seconds, load_u32_le(state->current.bytes),
            state->last_decision.stage, state->policy.reserved5 != 0u,
            input->preceding_fraction, &decision)) {
        return false;
    }

    if (decision.transition == 2u || decision.transition == 4u) {
        store_u32_le(&state->current.bytes[4], input->current_time);
        for (size_t index = 0u; index < sizeof(state->current.bytes); ++index) {
            ((uint8_t *)&state->previous_descriptor)[index] =
                state->current.bytes[index];
        }
        if (!gomore_primitives_sleep_descriptor_initialize(
                &state->current.descriptor,
                state->step.minute_accumulator.minute_zero_fraction,
                state->step.local_time_window == 1u, input->current_time,
                input->elapsed_seconds, decision.transition,
                state->policy.disable_history_scan != 0u)) {
            return false;
        }
        output->flags |= 2u;
    } else if (decision.transition == 1u) {
        store_u32_le(&state->current.bytes[4], input->current_time);
        gomore_primitives_sleep_interval_source source;
        for (size_t index = 0u; index < sizeof(source); ++index) {
            ((uint8_t *)&source)[index] = state->current.bytes[index];
        }
        gomore_primitives_sleep_interval_result candidate;
        if (!gomore_primitives_sleep_interval_compose(
                &candidate,
                state->step.minute_accumulator.minute_zero_fraction,
                state->step.local_time_window == 1u,
                load_u32_le(&step_bytes[0xA4u]),
                load_u32_le(&step_bytes[0xACu]),
                0, state->previous_interval.end,
                input->utc_offset_minutes, decision.adjustment,
                decision.reason, &source, &state->policy,
                &state->previous_interval,
                state->previous_descriptor.totals[0],
                state->previous_descriptor.totals[3],
                (int16_t)state->policy.reserved)) {
            return false;
        }
        const uint32_t clamp_start =
            load_u32_le(&step_bytes[0xACu]);
        if (candidate.start < clamp_start &&
                clamp_start - candidate.start < 900u) {
            candidate.start = clamp_start;
            candidate.end = clamp_start +
                ((candidate.end - clamp_start) / 30u) * 30u;
        }
        if ((candidate.flags & 8u) != 0u) {
            state->previous_interval = candidate;
        }
        gomore_primitives_interval_descriptor addition;
        for (size_t index = 0u; index < sizeof(addition); ++index) {
            ((uint8_t *)&addition)[index] = ((const uint8_t *)&source)[index];
        }
        if (!gomore_primitives_interval_descriptor_merge(
                &state->current.interval_descriptor, input->current_time,
                (candidate.flags & 8u) != 0u,
                &state->previous_descriptor,
                &addition, decision.transition)) {
            return false;
        }
        *output = candidate;
    }

    if (!gomore_primitives_statistics_accumulate(
            &state->current.statistics, input->elapsed_seconds,
            input->upper_flag, input->lower_flag, input->minute_sample,
            input->quality_flag4, input->quality_flag6,
            input->ring_sample) ||
        !gomore_primitives_callback_record_initialize(
            (uint8_t *)state, sizeof(*state),
            load_u32_le((const uint8_t *)&decision),
            (uint32_t)decision.adjustment)) {
        return false;
    }
    output->flags |= decision.stage;
    output->auxiliary = decision.reason;
    return true;
}

bool gomore_primitives_composite_engine_initialize(
    void *state, size_t state_length,
    uint8_t *time_configuration, size_t time_configuration_length,
    void **active_estimator_state, uint8_t **result_pointer,
    gomore_primitives_mode2_init_fn initialize_large_filter,
    gomore_primitives_void_context_fn finish_sps_initialize,
    gomore_primitives_filter_init_fn initialize_filter) {
    if (state == NULL || state_length < 0x3894u ||
            time_configuration == NULL || time_configuration_length < 10u ||
            active_estimator_state == NULL || result_pointer == NULL ||
            initialize_large_filter == NULL ||
            finish_sps_initialize == NULL || initialize_filter == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const uint32_t binding = load_u32_le(&bytes[0x3890u]);

    if (!gomore_primitives_large_filter_state_initialize(
            &bytes[0x228u], state_length - 0x228u,
            initialize_large_filter)) {
        return false;
    }
    clear_bytes(&bytes[0x1F8u], 0x28u);
    bytes[0x220u] = 0u;
    clear_bytes(&bytes[0x221u], 4u);
    clear_bytes(&bytes[0x225u], 2u);
    bytes[0x3800u] = 0u;

    if (!gomore_primitives_mode8_state_initialize(
            &bytes[0x8F4u], state_length - 0x8F4u)) {
        return false;
    }
    bytes[0x3804u] = 0u;
    if (!gomore_primitives_pattern17_initialize(
            &bytes[0xB62u], state_length - 0xB62u)) {
        return false;
    }
    bytes[0x3805u] = 0u;
    if (!gomore_primitives_sps_engine_initialize(
            &bytes[0xB74u], state_length - 0xB74u, binding,
            finish_sps_initialize)) {
        return false;
    }
    bytes[0x3806u] = 0u;
    if (!gomore_primitives_clear_first_byte(&bytes[0xBD0u])) {
        return false;
    }
    bytes[0x3807u] = 0u;
    if (!gomore_primitives_float_state_initialize(
            &bytes[0xBD4u], state_length - 0xBD4u)) {
        return false;
    }
    bytes[0x3808u] = 0u;
    if (!gomore_primitives_clear_first_byte(&bytes[0xC54u])) {
        return false;
    }
    bytes[0x380Fu] = 0u;
    if (!gomore_primitives_energy_record_initialize(
            &bytes[0xC58u], state_length - 0xC58u,
            binding + UINT32_C(0x10))) {
        return false;
    }
    bytes[0x3811u] = 0u;
    if (!gomore_primitives_large_state_initialize(
            &bytes[0xCB4u], state_length - 0xCB4u,
            binding + UINT32_C(0x18), active_estimator_state)) {
        return false;
    }
    bytes[0x3814u] = 0u;
    if (!gomore_primitives_time_engine_initialize(
            &bytes[0xFF0u], state_length - 0xFF0u,
            time_configuration, time_configuration_length,
            binding + UINT32_C(0x290))) {
        return false;
    }
    bytes[0x3819u] = 0u;
    if (!gomore_primitives_filter_state_initialize(
            &bytes[0x112Cu], state_length - 0x112Cu,
            initialize_filter)) {
        return false;
    }
    bytes[0x381Bu] = 0u;
    if (!gomore_primitives_parameter_state_initialize(
            &bytes[0x12B8u], state_length - 0x12B8u,
            binding + UINT32_C(0x29A))) {
        return false;
    }
    bytes[0x381Du] = 0u;
    if (!gomore_primitives_clear_36(
            &bytes[0x33B4u], state_length - 0x33B4u)) {
        return false;
    }
    bytes[0x3820u] = 0u;
    if (!gomore_primitives_large_default_state_initialize(
            &bytes[0x33D8u], state_length - 0x33D8u)) {
        return false;
    }
    bytes[0x382Fu] = 0u;
    if (!gomore_primitives_step_record_initialize(
            &bytes[0x37DCu], state_length - 0x37DCu)) {
        return false;
    }
    bytes[0x3839u] = 0u;
    uint32_t final_binding = 0u;
    if (!gomore_primitives_store_first_word(
            &final_binding, binding + UINT32_C(0x29C))) {
        return false;
    }
    store_u32_le(&bytes[0x37F8u], final_binding);
    bytes[0x383Eu] = 0u;
    *result_pointer = &bytes[0x37FDu];
    return true;
}

static const gomore_primitives_output_stage_descriptor output_stages[
    GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT] = {
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_RESPIRATORY_RATE,
        0x01F8u, 0x3848u, 0x3800u, 3u, 3u,
        {0x0030u, 0x0040u, 0x0044u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_LOCOMOTION_PREPROCESS,
        0x08F4u, 0x384Cu, 0x3804u, 7u, 2u,
        {0x0088u, 0x0098u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_CLASSIFIER,
        0x0B62u, 0x384Du, 0x3805u, 8u, 4u,
        {0x0088u, 0x0000u, 0x0098u, 0x00D8u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_CANDIDATE,
        0x0B74u, 0x384Eu, 0x3806u, 9u, 4u,
        {0x0098u, 0x00D8u, 0x0074u, 0x00DCu},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_SELECT,
        0x0BD0u, 0x384Fu, 0x3807u, 10u, 4u,
        {0x0010u, 0x006Cu, 0x00DCu, 0x00E4u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_MOTION,
        0x0BD4u, 0x3850u, 0x3808u, 11u, 2u,
        {0x0088u, 0x00F0u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_HEART_RATE_SELECT,
        0x0C54u, 0x3857u, 0x380Fu, 18u, 3u,
        {0x002Cu, 0x00F8u, 0x0104u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_ENERGY,
        0x0C58u, 0x3859u, 0x3811u, 20u, 10u,
        {
            0x0104u, 0x0074u, 0x0028u, 0x0110u, 0x0020u,
            0x00E4u, 0x00F0u, 0x00D8u, 0x0014u, 0x0114u,
        },
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_DORMANT_ESTIMATOR,
        0x0CB4u, 0x385Cu, 0x3814u, 23u, 7u,
        {0x0050u, 0x0104u, 0x00E4u, 0x0054u,
         0x0014u, 0x0114u, 0x0140u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_GATE,
        0x33B4u, 0x3868u, 0x3820u, 35u, 3u,
        {0x0050u, 0x00F0u, 0x01B8u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_CYCLE,
        0x0FF0u, 0x3861u, 0x3819u, 28u, 9u,
        {0x0050u, 0x004Cu, 0x00F0u, 0x0088u, 0x0030u,
         0x0104u, 0x01C0u, 0x01B8u, 0x0184u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_OPTICAL_PEAK,
        0x112Cu, 0x3863u, 0x381Bu, 30u, 2u,
        {0x0030u, 0x01A4u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_STREAM,
        0x12B8u, 0x3865u, 0x381Du, 32u, 5u,
        {0x01A4u, 0x0184u, 0x0050u, 0x01B8u, 0x01B5u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_WINDOW,
        0x33D8u, 0x3877u, 0x382Fu, 50u, 3u,
        {0x0030u, 0x0038u, 0x01C0u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_STEP_ACCUMULATE,
        0x37DCu, 0x3881u, 0x3839u, 60u, 3u,
        {0x00D8u, 0x00F0u, 0x01C4u},
    },
    {
        GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_ACCUMULATE,
        0x37F8u, 0x3886u, 0x383Eu, 65u, 6u,
        {0x0050u, 0x004Cu, 0x01C4u, 0x0114u, 0x00E4u, 0x01C8u},
    },
};

bool gomore_primitives_output_orchestrate(
    void *engine, size_t engine_length, uint32_t elapsed_updates,
    const gomore_primitives_output_orchestrator_providers *providers,
    uint8_t **result_pointer) {
    if (engine == NULL || engine_length < 0x3894u || providers == NULL ||
            result_pointer == NULL) {
        return false;
    }
    for (size_t index = 0u;
            index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++index) {
        if (providers->stages[index] == NULL) {
            return false;
        }
    }

    uint8_t *const bytes = engine;
    for (size_t index = 0u;
            index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++index) {
        const gomore_primitives_output_stage_descriptor *const descriptor =
            &output_stages[index];
        const uint8_t control = bytes[descriptor->control_offset];
        uint32_t status = 0u;
        if (control == 0u || control == 1u) {
            const uint32_t effective_elapsed = control == 1u
                ? 1u : elapsed_updates;
            if (!providers->stages[index](
                    providers->context, bytes, engine_length,
                    effective_elapsed, descriptor, &status)) {
                return false;
            }
            if (control == 1u) {
                bytes[descriptor->control_offset] = 0u;
            }
        } else if (control == 2u) {
            bytes[descriptor->control_offset] = 3u;
        }
        bytes[descriptor->status_offset] = (uint8_t)status;
    }
    *result_pointer = &bytes[0x37FDu];
    return true;
}

int32_t gomore_primitives_sleep_algorithm_initialize(
    void *engine, size_t engine_length, uint32_t runtime_value,
    const gomore_primitives_profile_input *profile,
    void *previous_state, size_t previous_state_length,
    uint32_t previous_state_binding,
    const gomore_primitives_sleep_algorithm_configuration *configuration,
    gomore_primitives_sleep_algorithm_outputs *outputs) {
    if (engine == NULL || engine_length < 0x39E0u || profile == NULL ||
            previous_state == NULL || previous_state_length < 0x2E0u ||
            configuration == NULL || outputs == NULL ||
            configuration->time_configuration == NULL ||
            configuration->time_configuration_length < 10u ||
            configuration->seed_random == NULL ||
            configuration->random_value == NULL ||
            configuration->initialize_small_filter == NULL ||
            configuration->initialize_large_filter == NULL ||
            configuration->finish_sps_initialize == NULL ||
            configuration->initialize_filter == NULL) {
        return -1;
    }

    uint8_t *bytes = engine;
    uint8_t *previous_bytes = previous_state;
    configuration->seed_random(configuration->random_seed);
    clear_bytes(bytes, 0x39E0u);
    store_u32_le(&bytes[0x39DCu], previous_state_binding);

    const int32_t random_value = configuration->random_value();
    const int32_t random_remainder =
        random_value - (random_value / 100) * 100;
    store_u16_le_early(
        &bytes[0x39DAu], (uint16_t)(random_remainder + 23));

    int32_t status = gomore_primitives_runtime_version_validate(
        runtime_value, true,
        configuration->version_validation_enabled,
        configuration->configured_runtime_limit,
        configuration->runtime_present,
        configuration->configured_version,
        configuration->runtime_version);
    if (status < 0) {
        (void)gomore_primitives_log_u32(
            configuration->logger, 1u, 1u,
            "[InitAuth] errorCode : %u", (uint32_t)status);
        bytes[0x39D8u] = (uint8_t)status;
        return status;
    }

    if ((int32_t)load_u32_le(previous_bytes) >= 0) {
        for (size_t index = 0u;
                index < (size_t)gomore_primitives_size_736(); ++index) {
            if (previous_bytes[index] != 0u) {
                status = -5;
                (void)gomore_primitives_log_u32(
                    configuration->logger, 1u, 1u,
                    "[InitPre] errorCode : %u", (uint32_t)status);
                bytes[0x39D8u] = (uint8_t)status;
                return status;
            }
        }
        store_u32_le(previous_bytes,
                     load_u32_le(previous_bytes) | UINT32_C(0x80000000));
    }

    if (!gomore_primitives_filter_bank_initialize(
            bytes, engine_length,
            configuration->initialize_small_filter,
            configuration->initialize_large_filter)) {
        bytes[0x39D8u] = UINT8_MAX;
        return -1;
    }

    uint8_t *nested = &bytes[0x140u];
    clear_bytes(nested, 0x3894u);
    store_u32_le(&nested[0x3890u],
                 previous_state_binding + UINT32_C(8));
    if (!gomore_primitives_sps_state_initialize(nested, 0x3894u)) {
        bytes[0x39D8u] = UINT8_MAX;
        return -1;
    }
    store_u32_le(&bytes[0x190u], runtime_value);

    float persistent_cache[2] = {
        bits_float(load_u32_le(&previous_bytes[0x2D8u])),
        bits_float(load_u32_le(&previous_bytes[0x2DCu])),
    };
    gomore_primitives_profile_output converted;
    status = gomore_primitives_profile_convert(
        profile, persistent_cache, &converted);
    store_u32_le(&previous_bytes[0x2D8u],
                 float_bits(persistent_cache[0]));
    store_u32_le(&previous_bytes[0x2DCu],
                 float_bits(persistent_cache[1]));
    nested[0x7Cu] = converted.age_years;
    nested[0x7Du] = converted.binary_sex;
    store_u32_le(&nested[0x74u],
                 float_bits(converted.height_centimeters));
    store_u32_le(&nested[0x78u],
                 float_bits(converted.weight_kilograms));
    store_u32_le(&nested[0x80u], float_bits(converted.parameter_4));
    store_u32_le(&nested[0x84u],
                 float_bits(converted.parameter_5_raw));
    store_u32_le(&nested[0x28u], float_bits(converted.parameter_4));
    store_u32_le(&nested[0x110u],
                 float_bits(converted.parameter_5_normalized));
    store_u32_le(&nested[0x20u],
                 float_bits(converted.cached_parameters[0]));
    store_u32_le(&nested[0x24u],
                 float_bits(converted.cached_parameters[1]));
    if (status < 0) {
        (void)gomore_primitives_log_u32(
            configuration->logger, 1u, 1u,
            "[InitUser] errorCode : %u", (uint32_t)status);
        bytes[0x39D8u] = (uint8_t)status;
        return status;
    }

    if (!gomore_primitives_composite_engine_initialize(
            nested, engine_length - 0x140u,
            configuration->time_configuration,
            configuration->time_configuration_length,
            &outputs->active_estimator_state, &outputs->result_pointer,
            configuration->initialize_large_filter,
            configuration->finish_sps_initialize,
            configuration->initialize_filter)) {
        bytes[0x39D8u] = UINT8_MAX;
        return -1;
    }
    status = gomore_primitives_profile_state_apply(
        bytes, engine_length, 0, -1, 0u);
    (void)gomore_primitives_return_zero();
    bytes[0x39D8u] = (uint8_t)status;
    return status;
}

bool gomore_primitives_cardano_candidates(
    float discriminant, float leading_coefficient, float linear_coefficient,
    void *destination, size_t destination_length,
    const float root_of_unity[2], float first_radical[2],
    float second_radical[2], gomore_primitives_float_binary_fn power,
    gomore_primitives_float_binary_fn arctangent2,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_float_unary_fn logarithm,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine) {
    if (destination == NULL || destination_length < 0x24u ||
            root_of_unity == NULL || first_radical == NULL ||
            second_radical == NULL ||
            (discriminant < 0.0f &&
             (arctangent2 == NULL || square_root == NULL ||
              logarithm == NULL || exponential == NULL || cosine == NULL ||
              sine == NULL)) ||
            (!(discriminant < 0.0f) && power == NULL)) {
        return false;
    }

    if (discriminant < 0.0f) {
        if (!gomore_primitives_complex_power(
                bits_float(UINT32_C(0x3EAAAAAB)), first_radical,
                arctangent2, square_root, logarithm, exponential,
                cosine, sine) ||
                !gomore_primitives_complex_power(
                    bits_float(UINT32_C(0x3EAAAAAB)), second_radical,
                    arctangent2, square_root, logarithm, exponential,
                    cosine, sine)) {
            return false;
        }
    } else {
        if (!gomore_primitives_signed_power_third(first_radical, power)) {
            return false;
        }
        first_radical[1] = bits_float(UINT32_C(0x358637BD));
        if (!gomore_primitives_signed_power_third(
                second_radical, power)) {
            return false;
        }
    }

    float candidate_pairs[3][2];
    if (!gomore_primitives_vector_pair_transform(
            leading_coefficient, linear_coefficient,
            first_radical, second_radical, candidate_pairs[0])) {
        return false;
    }

    float first_product[2];
    float root_square[2];
    float second_product[2];
    if (!gomore_primitives_complex_multiply(
            root_of_unity, first_radical, first_product) ||
            !gomore_primitives_complex_multiply(
                root_of_unity, root_of_unity, root_square) ||
            !gomore_primitives_complex_multiply(
                root_square, second_radical, second_product) ||
            !gomore_primitives_vector_pair_transform(
                leading_coefficient, linear_coefficient,
                first_product, second_product, candidate_pairs[1]) ||
            !gomore_primitives_complex_multiply(
                root_square, first_radical, first_product) ||
            !gomore_primitives_complex_multiply(
                root_of_unity, second_radical, second_product) ||
            !gomore_primitives_vector_pair_transform(
                leading_coefficient, linear_coefficient,
                first_product, second_product, candidate_pairs[2])) {
        return false;
    }

    gomore_primitives_quality_sample candidates[3];
    for (size_t index = 0u; index < 3u; ++index) {
        candidates[index].value = candidate_pairs[index][0];
        candidates[index].metadata =
            (int32_t)float_bits(candidate_pairs[index][1]);
    }
    return gomore_primitives_quality_samples_copy(
        destination, destination_length, candidates);
}

float gomore_primitives_sps_secondary_model(
    const float features[3],
    gomore_primitives_double_unary_fn square_root) {
    if (features == NULL || square_root == NULL) {
        return 0.0f;
    }

    const float center0 = bits_float(UINT32_C(0x432DAD60));
    const float center1 = bits_float(UINT32_C(0x432F2E7B));
    const float center2 = bits_float(UINT32_C(0x44DF07BD));
    const float scale0 = bits_float(UINT32_C(0x40B908FD));
    const float scale1 = bits_float(UINT32_C(0x41471339));
    const float scale2 = bits_float(UINT32_C(0x43982465));
    const float weight0 = bits_float(UINT32_C(0x3F5ABE4F));
    const float weight1 = bits_float(UINT32_C(0x3F8EE557));
    const float root_amplitude = bits_float(UINT32_C(0x3FC4413D));
    const float output_offset = bits_float(UINT32_C(0x4131EECE));

    const float normalized0 = (features[0] - center0) / scale0;
    const float term0 = normalized0 * weight0;
    const float normalized1 = (features[1] - center1) / scale1;
    const float term1 = normalized1 * weight1;
    const float linear = term0 + term1;
    const float normalized2 = (features[2] - center2) / scale2;
    const float sign = normalized2 > 0.0f ? 1.0f : -1.0f;

    union {
        double value;
        uint64_t bits;
    } magnitude;
    magnitude.value = (double)normalized2;
    magnitude.bits &= UINT64_C(0x7FFFFFFFFFFFFFFF);
    const double signed_root = square_root(magnitude.value) * (double)sign;
    const double transformed = signed_root * (double)root_amplitude;
    const float combined = (float)((double)linear + transformed);
    return output_offset + combined;
}

bool gomore_primitives_expand_half_positions(
    const uint16_t *positions, const float *control_values,
    size_t control_count, float *output, size_t output_count,
    gomore_primitives_double_unary_fn round_value) {
    if (positions == NULL || control_values == NULL ||
            control_count == 0u || output == NULL ||
            output_count > (size_t)INT32_MAX || round_value == NULL) {
        return false;
    }

    const double first_rounded = round_value(
        (double)((float)positions[0] * 0.5f));
    if (first_rounded != first_rounded || first_rounded < 0.0 ||
            first_rounded > (double)INT32_MAX) {
        return false;
    }
    int32_t output_index = (int32_t)first_rounded;
    if ((size_t)output_index > output_count ||
            !gomore_primitives_fill_float_progression(
                output, output_count, 0u, (size_t)output_index,
                control_values[0], 0.0f)) {
        return false;
    }

    for (size_t index = 0u; index + 1u < control_count; ++index) {
        const int32_t position_delta =
            (int32_t)((uint32_t)positions[index + 1u] -
                      (uint32_t)positions[index]);
        const double rounded = round_value(
            (double)((float)position_delta * 0.5f));
        if (rounded != rounded || rounded < (double)INT32_MIN ||
                rounded > (double)INT32_MAX) {
            return false;
        }
        const int32_t segment_length = (int32_t)rounded;
        const int64_t end_wide =
            (int64_t)output_index + (int64_t)segment_length;
        if (segment_length < 1 || end_wide > (int64_t)output_count ||
                end_wide < 0) {
            return false;
        }
        const int32_t end = (int32_t)end_wide;
        const float step =
            (control_values[index + 1u] - control_values[index]) /
            (float)segment_length;
        if (!gomore_primitives_fill_float_progression(
                output, output_count, (size_t)output_index, (size_t)end,
                control_values[index], step)) {
            return false;
        }
        output_index = end;
    }

    if ((size_t)output_index < output_count) {
        return gomore_primitives_fill_float_progression(
            output, output_count, (size_t)output_index, output_count,
            control_values[control_count - 1u], 0.0f);
    }
    return true;
}

static bool locomotion_period_append(
    float periods[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY],
    size_t *period_count, uint8_t later, uint8_t earlier) {
    if (*period_count >= GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY ||
            later < earlier) {
        return false;
    }
    const float sample_distance = (float)((uint32_t)later -
                                          (uint32_t)earlier);
    periods[*period_count] =
        (float)((12.5 / (double)sample_distance) * 60.0);
    ++*period_count;
    return true;
}

static bool locomotion_extrema_periods(
    const float expanded[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT],
    const uint8_t first_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    size_t first_count,
    const uint8_t second_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    size_t second_count,
    float first_threshold, float second_threshold,
    float periods[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY],
    size_t *period_count) {
    size_t first_cursor = 0u;
    size_t second_cursor = 0u;
    int32_t previous = -1;
    while (first_cursor < first_count && second_cursor < second_count) {
        const uint8_t current = first_indices[first_cursor];
        if (expanded[current] > first_threshold) {
            if (previous < 0) {
                previous = (int32_t)current;
                while (second_indices[second_cursor] < current &&
                       second_cursor + 1u < second_count) {
                    ++second_cursor;
                }
            } else {
                size_t matches = 0u;
                while (second_indices[second_cursor] < current) {
                    if (expanded[second_indices[second_cursor]] <
                            second_threshold) {
                        ++matches;
                    }
                    if (second_cursor + 1u >= second_count) {
                        break;
                    }
                    ++second_cursor;
                }
                if (matches == 1u &&
                        !locomotion_period_append(
                            periods, period_count, current,
                            (uint8_t)previous)) {
                    return false;
                }
                previous = (int32_t)current;
            }
        }
        ++first_cursor;
    }

    first_cursor = 0u;
    second_cursor = 0u;
    previous = -1;
    while (second_cursor < second_count && first_cursor < first_count) {
        const uint8_t current = second_indices[second_cursor];
        if (expanded[current] < second_threshold) {
            if (previous < 0) {
                previous = (int32_t)current;
                while (first_indices[first_cursor] < current &&
                       first_cursor + 1u < first_count) {
                    ++first_cursor;
                }
            } else {
                size_t matches = 0u;
                while (first_indices[first_cursor] < current) {
                    if (expanded[first_indices[first_cursor]] >
                            first_threshold) {
                        ++matches;
                    }
                    if (first_cursor + 1u >= first_count) {
                        break;
                    }
                    ++first_cursor;
                }
                if (matches == 1u &&
                        !locomotion_period_append(
                            periods, period_count, current,
                            (uint8_t)previous)) {
                    return false;
                }
                previous = (int32_t)current;
            }
        }
        ++second_cursor;
    }
    return true;
}

bool gomore_primitives_locomotion_feature_reduce(
    float expanded[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT],
    uint8_t first_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    uint8_t second_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    float controls[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY],
    float *primary, float *secondary,
    const gomore_primitives_locomotion_feature_reduce_math *math) {
    if (expanded == NULL || first_indices == NULL ||
            second_indices == NULL || controls == NULL || primary == NULL ||
            secondary == NULL || math == NULL ||
            math->qsort_provider == NULL || math->compare == NULL ||
            math->power_f32 == NULL || math->square_root_f32 == NULL ||
            math->power_f64 == NULL || math->square_root_f64 == NULL) {
        return false;
    }

    float standard_deviation = 0.0f;
    if (!gomore_primitives_standard_deviation(
            expanded, GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT,
            math->power_f32, math->square_root_f32,
            &standard_deviation)) {
        return false;
    }
    const float mean = gomore_primitives_mean(
        expanded, GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT);
    for (size_t index = 0u;
            index < GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT; ++index) {
        expanded[index] = standard_deviation == 0.0f
            ? 0.0f : (expanded[index] - mean) / standard_deviation;
    }
    if (!gomore_primitives_sleep_iir2_filter(
            expanded, GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT)) {
        return false;
    }

    size_t first_count = 0u;
    size_t second_count = 0u;
    const bool extrema_valid =
        gomore_primitives_moving_average_extrema_indices(
            expanded, GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT,
            38u, 12u,
            first_indices,
            GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY,
            &first_count,
            second_indices,
            GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY,
            &second_count);

    *primary = -1.0f;
    *secondary = 0.0f;
    if (!extrema_valid || first_count == 0u || second_count == 0u) {
        return true;
    }

    for (size_t index = 0u; index < first_count; ++index) {
        controls[index] = expanded[first_indices[index]];
    }
    float first_percentile = 0.0f;
    if (!gomore_primitives_sorted_percentile(
            controls, first_count, 75u,
            math->qsort_provider, math->compare, &first_percentile)) {
        return false;
    }
    const float first_threshold =
        (float)((double)first_percentile * 0.2);

    for (size_t index = 0u; index < second_count; ++index) {
        controls[index] = expanded[second_indices[index]];
    }
    float second_percentile = 0.0f;
    if (!gomore_primitives_sorted_percentile(
            controls, second_count, 25u,
            math->qsort_provider, math->compare, &second_percentile)) {
        return false;
    }
    const float second_threshold =
        (float)((double)second_percentile * 0.2);

    size_t period_count = 0u;
    if (!locomotion_extrema_periods(
            expanded, first_indices, first_count,
            second_indices, second_count,
            first_threshold, second_threshold,
            controls, &period_count)) {
        return false;
    }

    if (first_count < 6u && period_count < 2u) {
        period_count = 0u;
        /* The production body scans the second extrema bank in both fallback
         * loops.  Preserve that observed behavior rather than correcting it. */
        for (size_t pass = 0u; pass < 2u; ++pass) {
            for (size_t index = 0u; index + 1u < second_count; ++index) {
                const uint8_t earlier = second_indices[index];
                const uint8_t later = second_indices[index + 1u];
                const uint32_t distance =
                    (uint32_t)later - (uint32_t)earlier;
                if (distance > 50u && (double)distance <
                        114.99999999999999 &&
                        !locomotion_period_append(
                            controls, &period_count, later, earlier)) {
                    return false;
                }
            }
        }
    }

    if (period_count <= 1u) {
        return true;
    }
    const float period_mean = gomore_primitives_mean(
        controls, period_count);
    float period_standard_deviation = 0.0f;
    if (!gomore_primitives_standard_deviation(
            controls, period_count,
            math->power_f32, math->square_root_f32,
            &period_standard_deviation)) {
        return false;
    }
    const float upper = period_mean + period_standard_deviation * 2.0f;
    const float lower = period_mean - period_standard_deviation * 2.0f;
    float included_sum = 0.0f;
    size_t included_count = 0u;
    for (size_t index = 0u; index < period_count; ++index) {
        if (controls[index] < upper && controls[index] > lower) {
            included_sum += controls[index];
            ++included_count;
        }
    }
    if (included_count <= 2u) {
        return true;
    }

    const float included_mean = included_sum / (float)included_count;
    float squared_sum = 0.0f;
    for (size_t index = 0u; index < period_count; ++index) {
        if (controls[index] < upper && controls[index] > lower) {
            const float difference = included_mean - controls[index];
            const double square = math->power_f64(
                (double)difference, 2.0);
            squared_sum += (float)square;
        }
    }
    const float population_variance =
        squared_sum / (float)included_count;
    const float dispersion =
        (float)math->square_root_f64((double)population_variance);
    const float one_third = bits_float(UINT32_C(0x3EAAAAAB));
    const float denominator = included_mean * one_third * 2.0f;
    const float complement =
        1.0f - (float)included_count / denominator;
    *primary = included_mean;
    *secondary = gomore_primitives_bounded_linear_complement(
        dispersion, complement);
    return true;
}

bool gomore_primitives_locomotion_control_extract(
    const gomore_primitives_locomotion_control_sample *samples,
    size_t sample_count, float sample_period, float difference_scale,
    uint32_t mode,
    gomore_primitives_locomotion_control_workspace *workspace,
    gomore_primitives_double_unary_fn round_value,
    gomore_primitives_locomotion_feature_reduce_fn reduce,
    const gomore_primitives_locomotion_feature_reduce_math *reduce_math,
    float *primary, float *secondary,
    size_t *accepted_count, int32_t *status) {
    if (samples == NULL || sample_count == 0u ||
            sample_count > GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY ||
            workspace == NULL || round_value == NULL || reduce == NULL ||
            reduce_math == NULL ||
            primary == NULL || secondary == NULL || accepted_count == NULL ||
            status == NULL) {
        return false;
    }

    *primary = -1.0f;
    *secondary = 0.0f;
    *accepted_count = 0u;
    *status = 0;
    for (size_t index = 0u;
            index < GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY; ++index) {
        workspace->positions[index] = 0u;
    }

    size_t retained = 0u;
    for (size_t index = 0u; index + 1u < sample_count; ++index) {
        const int32_t delta =
            (int32_t)samples[index + 1u].position -
            (int32_t)samples[index].position;
        const double delta_f64 = (double)delta;
        const double delta_magnitude = delta_f64 < 0.0
            ? -delta_f64 : delta_f64;
        const double lower = (double)sample_period * 0.6;
        const double lower_magnitude = lower < 0.0 ? -lower : lower;
        const double upper = (double)sample_period * 1.5;
        const double upper_magnitude = upper < 0.0 ? -upper : upper;
        if (!(lower_magnitude < delta_magnitude &&
                delta_magnitude < upper_magnitude)) {
            continue;
        }

        workspace->positions[retained] = samples[index].position;
        if (mode == 1u) {
            workspace->controls[retained] = (float)delta;
        } else {
            const float difference =
                samples[index].first - samples[index].second;
            const double difference_f64 = (double)difference;
            const double difference_magnitude = difference_f64 < 0.0
                ? -difference_f64 : difference_f64;
            const double floor = (double)difference_scale * 0.25;
            const double floor_magnitude = floor < 0.0 ? -floor : floor;
            if (difference_magnitude <= floor_magnitude ||
                    !(difference_scale * 2.0f > difference)) {
                workspace->controls[retained] = difference_scale;
            } else {
                workspace->controls[retained] = difference;
            }
        }
        ++retained;
    }
    *accepted_count = retained;

    float required_base = 0.0f;
    if (sample_period > 0.0f) {
        required_base = 500.0f / sample_period;
    }
    const double required = (double)required_base * 0.7;
    if ((double)retained < required) {
        *status = 1;
        return true;
    }

    if (!gomore_primitives_expand_half_positions(
            workspace->positions, workspace->controls, retained,
            workspace->expanded,
            GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT,
            round_value)) {
        return true;
    }
    if (!reduce(
        workspace->expanded,
        workspace->first_indices,
        workspace->second_indices,
        workspace->controls,
        primary, secondary, reduce_math)) {
        return false;
    }
    return true;
}

bool gomore_primitives_pkey_load(
    gomore_primitives_pkey_store *store,
    uint8_t *key, size_t key_capacity,
    gomore_primitives_pkey_result *result) {
    if (result == NULL) {
        return false;
    }
    result->valid = false;
    result->stored_length = 0u;
    result->stored_crc = 0u;
    result->computed_crc = 0u;
    result->status = GOMORE_PRIMITIVES_PKEY_STORE_UNAVAILABLE;

    if (store == NULL) {
        return false;
    }
    if (!store->initialized) {
        if (store->initialize == NULL || !store->initialize(store)) {
            return false;
        }
    }
    if (!store->initialized || store->read == NULL) {
        return false;
    }
    if (key == NULL || key_capacity < 64u) {
        result->status = GOMORE_PRIMITIVES_PKEY_OUTPUT_NULL;
        return false;
    }

    uint8_t header[8];
    if (!store->read(store->flash_context, store->partition_offset,
                     header, sizeof(header))) {
        result->status = GOMORE_PRIMITIVES_PKEY_READ_FAILED;
        return false;
    }
    result->stored_length = load_u32_le(&header[0]);
    result->stored_crc = load_u32_le(&header[4]);
    if (result->stored_length != 64u) {
        result->status = GOMORE_PRIMITIVES_PKEY_NOT_FOUND;
        return false;
    }
    if (store->partition_offset > UINT32_MAX - 8u ||
            !store->read(store->flash_context,
                         store->partition_offset + 8u,
                         key, 64u)) {
        result->status = GOMORE_PRIMITIVES_PKEY_READ_FAILED;
        return false;
    }
    result->computed_crc = r1_crc32_castagnoli(key, 64u);
    if (result->computed_crc != result->stored_crc) {
        result->status = GOMORE_PRIMITIVES_PKEY_CRC_MISMATCH;
        return false;
    }
    result->valid = true;
    result->status = GOMORE_PRIMITIVES_PKEY_OK;
    return true;
}

bool gomore_primitives_auth_parameters_setup(
    const gomore_primitives_auth_setup_configuration *configuration,
    int32_t *status) {
    if (configuration == NULL || status == NULL ||
            configuration->timestamp == NULL ||
            configuration->apply == NULL ||
            (configuration->device_uuid_cache_valid &&
             (configuration->device_uuid_cache == NULL ||
              configuration->device_uuid_cache_length >= 28u)) ||
            (configuration->pkey_cache_valid &&
             configuration->pkey_cache == NULL) ||
            (!configuration->pkey_cache_valid &&
             configuration->pkey_loader == NULL)) {
        return false;
    }

    uint8_t device_uuid[28] = {0u};
    uint8_t key[68] = {0u};
    size_t device_uuid_written = 0u;
    if (!gomore_primitives_key_or_cached_copy(
            device_uuid, sizeof(device_uuid),
            configuration->device_uuid_cache_valid,
            configuration->device_uuid_cache,
            configuration->device_uuid_cache_length,
            configuration->device_id_0, configuration->device_id_1,
            configuration->address_word, &device_uuid_written)) {
        return false;
    }
    (void)device_uuid_written;

    const int32_t key_length = gomore_primitives_copy_key_blob(
        key, sizeof(key), configuration->pkey_cache_valid,
        configuration->pkey_cache, configuration->pkey_loader,
        configuration->pkey_loader_context);
    if (key_length < 0) {
        *status = -1;
        return true;
    }

    size_t device_uuid_length = 0u;
    while (device_uuid_length < sizeof(device_uuid) &&
           device_uuid[device_uuid_length] != 0u) {
        ++device_uuid_length;
    }
    if (device_uuid_length == sizeof(device_uuid) ||
            device_uuid_length > UINT8_MAX) {
        return false;
    }
    const gomore_primitives_auth_parameters parameters = {
        .key = key,
        .device_uuid = device_uuid,
        .device_uuid_length = (uint8_t)device_uuid_length,
        .timestamp = configuration->timestamp(
            configuration->timestamp_context),
    };
    *status = configuration->apply(&parameters);
    return true;
}

static size_t sdk_auth_field_count(const uint8_t *message, size_t length) {
    size_t count = 1u;
    for (size_t index = 0u; index < length; ++index) {
        if (message[index] == (uint8_t)',') {
            ++count;
        }
    }
    return count;
}

static void sdk_auth_clear_workspace(
    uint8_t key[68], uint8_t decoded[128], uint8_t plaintext[128]) {
    clear_bytes(key, 68u);
    clear_bytes(decoded, 128u);
    clear_bytes(plaintext, 128u);
}

bool gomore_primitives_sdk_auth_parse(
    const gomore_primitives_auth_parameters *parameters,
    const gomore_primitives_sdk_auth_configuration *configuration,
    gomore_primitives_sdk_auth_status *status, int32_t *result) {
    if (parameters == NULL || parameters->key == NULL ||
            parameters->device_uuid == NULL || configuration == NULL ||
            configuration->decrypt_keys[0] == NULL ||
            configuration->decrypt_keys[1] == NULL ||
            configuration->decrypt == NULL ||
            configuration->message_matches == NULL || status == NULL ||
            result == NULL) {
        return false;
    }
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT; ++index) {
        if (configuration->parse_fields[index] == NULL ||
                (index + 1u < GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT &&
                 configuration->validate_fields[index] == NULL)) {
            return false;
        }
    }
    if (parameters->device_uuid_length != 24u) {
        clear_bytes((uint8_t *)status, sizeof(*status));
        status->error = -1;
        *result = -1005;
        return true;
    }

    uint8_t normalized_uuid[17] = {0u};
    for (size_t index = 0u; index < 16u; ++index) {
        uint8_t value = parameters->device_uuid[index + 8u];
        if (value >= (uint8_t)'a' && value <= (uint8_t)'f') {
            value = (uint8_t)(value - ((uint8_t)'a' - (uint8_t)'A'));
        }
        normalized_uuid[index] = value;
    }

    uint8_t key[68] = {0u};
    for (size_t index = 0u; index < 64u; ++index) {
        key[index] = parameters->key[index];
    }
    size_t key_length = 0u;
    while (key_length < sizeof(key) && key[key_length] != 0u) {
        ++key_length;
    }
    if (key_length > 128u || key_length % 4u != 0u) {
        clear_bytes(key, sizeof(key));
        return false;
    }

    uint8_t decoded[128] = {0u};
    uint8_t plaintext[128] = {0u};
    size_t decoded_length = 0u;
    if (!gomore_primitives_base64_decode_blocks(
            key, key_length, decoded, sizeof(decoded), &decoded_length)) {
        sdk_auth_clear_workspace(key, decoded, plaintext);
        return false;
    }

    clear_bytes((uint8_t *)status, sizeof(*status));
    status->error = -1;
    const gomore_primitives_auth_parameters local_parameters = {
        .key = key,
        .device_uuid = normalized_uuid,
        .device_uuid_length = 16u,
        .timestamp = parameters->timestamp,
    };
    size_t plaintext_length = 0u;
    bool accepted = false;
    for (size_t attempt = 0u; attempt < 2u; ++attempt) {
        clear_bytes(plaintext, sizeof(plaintext));
        plaintext_length = 0u;
        if (!configuration->decrypt(
                configuration->decrypt_context, decoded, decoded_length,
                configuration->decrypt_keys[attempt], plaintext,
                sizeof(plaintext) - 1u, &plaintext_length) ||
                plaintext_length >= sizeof(plaintext)) {
            sdk_auth_clear_workspace(key, decoded, plaintext);
            return false;
        }
        plaintext[plaintext_length] = 0u;
        const bool matches = configuration->message_matches(
            configuration->match_context, plaintext, plaintext_length);
        const size_t field_count = sdk_auth_field_count(
            plaintext, plaintext_length);
        if (attempt == 1u && field_count !=
                GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT) {
            status->error = -1002;
        } else if (matches) {
            status->error = 0;
            accepted = true;
            break;
        }
        if (attempt == 1u && status->error < 0) {
            *result = -1002;
            sdk_auth_clear_workspace(key, decoded, plaintext);
            return true;
        }
    }
    if (!accepted || sdk_auth_field_count(plaintext, plaintext_length) !=
            GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT) {
        status->error = -1002;
        *result = -1002;
        sdk_auth_clear_workspace(key, decoded, plaintext);
        return true;
    }

    char *fields[GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT];
    size_t field_index = 0u;
    fields[field_index++] = (char *)plaintext;
    for (size_t index = 0u; index < plaintext_length; ++index) {
        if (plaintext[index] == (uint8_t)',') {
            plaintext[index] = 0u;
            fields[field_index++] = (char *)&plaintext[index + 1u];
        }
    }
    uint32_t scratch[4] = {parameters->timestamp, 0u, 0u, 0u};
    int32_t selected = 0;
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT; ++index) {
        const int32_t parsed = configuration->parse_fields[index](
            configuration->dispatch_context, fields[index],
            &local_parameters, status, scratch);
        if (parsed < 0) {
            *result = (int32_t)(int16_t)parsed;
            sdk_auth_clear_workspace(key, decoded, plaintext);
            return true;
        }
        if (index + 1u < GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT &&
                configuration->validate_fields[index](
                    configuration->dispatch_context, fields[index],
                    &local_parameters, status) > 1) {
            selected = parsed;
        }
    }
    *result = (int32_t)(int16_t)selected;
    sdk_auth_clear_workspace(key, decoded, plaintext);
    return true;
}

bool gomore_primitives_previous_state_restore(
    gomore_primitives_pkey_store *store,
    uint8_t key[64], void *state, size_t state_length,
    gomore_primitives_previous_state_result *result) {
    if (result == NULL) {
        return false;
    }
    result->found = false;
    result->slot = UINT8_MAX;
    result->record_offset = 0u;
    result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_OUTPUT_INVALID;
    if (store == NULL || key == NULL || state == NULL ||
            state_length == 0u || state_length > UINT32_MAX - 3u) {
        return false;
    }

    gomore_primitives_pkey_result pkey_result;
    if (!gomore_primitives_pkey_load(
            store, key, 64u, &pkey_result)) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_PKEY_INVALID;
        return false;
    }

    const uint32_t aligned_state_length =
        ((uint32_t)state_length + 3u) & ~UINT32_C(3);
    const uint64_t stride = (uint64_t)aligned_state_length + 8u;
    const uint64_t records_base =
        (uint64_t)store->partition_offset + 72u;
    for (int32_t slot = 3; slot >= 0; --slot) {
        const uint64_t record_offset_wide =
            records_base + stride * (uint32_t)slot;
        if (record_offset_wide > UINT32_MAX) {
            result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_READ_FAILED;
            return false;
        }
        const uint32_t record_offset = (uint32_t)record_offset_wide;
        uint8_t header[8];
        if (!store->read(store->flash_context, record_offset,
                         header, sizeof(header))) {
            result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_READ_FAILED;
            return false;
        }
        const uint32_t stored_length = load_u32_le(&header[0]);
        if (stored_length == UINT32_MAX || stored_length != state_length) {
            continue;
        }
        if (record_offset > UINT32_MAX - 8u ||
                !store->read(store->flash_context, record_offset + 8u,
                             state, state_length)) {
            result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_READ_FAILED;
            return false;
        }
        result->found = true;
        result->slot = (uint8_t)slot;
        result->record_offset = record_offset;
        result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_OK;
        return true;
    }
    result->status = GOMORE_PRIMITIVES_PREVIOUS_STATE_NOT_FOUND;
    return false;
}

gomore_primitives_previous_append_status
gomore_primitives_previous_state_append(
    gomore_primitives_pkey_store *store,
    const void *state, size_t state_length, size_t state_capacity,
    void *scratch, size_t scratch_capacity,
    gomore_primitives_previous_append_result *result) {
    if (result == NULL) {
        return GOMORE_PRIMITIVES_PREVIOUS_APPEND_BAD_ARGUMENT;
    }
    result->compacted = false;
    result->slot = UINT8_MAX;
    result->key_length = 0u;
    result->aligned_key_length = 0u;
    result->aligned_state_length = 0u;
    result->record_offset = 0u;
    result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_BAD_ARGUMENT;

    if (store == NULL || state == NULL || state_length == 0u ||
            state_length > UINT32_MAX - 3u ||
            store->read == NULL || store->write == NULL ||
            store->erase == NULL ||
            store->partition_offset >
                UINT32_MAX - GOMORE_PRIMITIVES_PKEY_PARTITION_BYTES) {
        return result->status;
    }
    const uint32_t aligned_state_length =
        ((uint32_t)state_length + 3u) & ~UINT32_C(3);
    if (state_capacity < aligned_state_length) {
        return result->status;
    }
    result->aligned_state_length = aligned_state_length;

    if (!store->initialized) {
        if (store->initialize == NULL || !store->initialize(store)) {
            result->status =
                GOMORE_PRIMITIVES_PREVIOUS_APPEND_STORE_UNAVAILABLE;
            return result->status;
        }
    }
    if (!store->initialized) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_STORE_UNAVAILABLE;
        return result->status;
    }

    uint8_t header[GOMORE_PRIMITIVES_PREVIOUS_STATE_SLOT_HEADER_BYTES];
    if (!store->read(store->flash_context, store->partition_offset,
                     header, sizeof(header))) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_READ_FAILED;
        return result->status;
    }
    const uint32_t key_length = load_u32_le(&header[0]);
    result->key_length = key_length;
    if (key_length > UINT32_MAX - 3u) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_TOO_LARGE;
        return result->status;
    }
    const uint32_t aligned_key_length =
        (key_length + 3u) & ~UINT32_C(3);
    result->aligned_key_length = aligned_key_length;
    if ((uint64_t)aligned_key_length + aligned_state_length + 16u >
            GOMORE_PRIMITIVES_PKEY_APPEND_WINDOW_BYTES) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_TOO_LARGE;
        return result->status;
    }

    const uint32_t records_offset =
        store->partition_offset + aligned_key_length + 8u;
    const uint32_t stride = aligned_state_length + 8u;
    const uint32_t trigger_offset = records_offset + 2u * stride;
    if (!store->read(store->flash_context, trigger_offset,
                     header, sizeof(header))) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_READ_FAILED;
        return result->status;
    }

    uint8_t selected_slot = 0u;
    if (load_u32_le(&header[0]) != UINT32_MAX) {
        const size_t key_record_length = (size_t)aligned_key_length + 8u;
        if (scratch == NULL || scratch_capacity < key_record_length) {
            result->status =
                GOMORE_PRIMITIVES_PREVIOUS_APPEND_SCRATCH_TOO_SMALL;
            return result->status;
        }
        if (!store->read(store->flash_context, store->partition_offset,
                         scratch, key_record_length)) {
            result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_READ_FAILED;
            return result->status;
        }
        if (!store->erase(store->flash_context, store->partition_offset,
                          GOMORE_PRIMITIVES_PKEY_PARTITION_BYTES)) {
            result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_ERASE_FAILED;
            return result->status;
        }
        if (!store->write(store->flash_context, store->partition_offset,
                          scratch, key_record_length)) {
            result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_WRITE_FAILED;
            return result->status;
        }
        result->compacted = true;
    } else {
        bool found = false;
        for (uint8_t slot = 0u;
             slot < GOMORE_PRIMITIVES_PREVIOUS_STATE_SLOT_COUNT; ++slot) {
            const uint32_t slot_offset = records_offset + slot * stride;
            if (!store->read(store->flash_context, slot_offset,
                             header, sizeof(header))) {
                result->status =
                    GOMORE_PRIMITIVES_PREVIOUS_APPEND_READ_FAILED;
                return result->status;
            }
            if (load_u32_le(&header[0]) == UINT32_MAX) {
                selected_slot = slot;
                found = true;
                break;
            }
        }
        if (!found) {
            result->status =
                GOMORE_PRIMITIVES_PREVIOUS_APPEND_NO_ERASED_SLOT;
            return result->status;
        }
    }

    const uint32_t record_offset = records_offset + selected_slot * stride;
    store_u32_le(&header[0], (uint32_t)state_length);
    store_u32_le(&header[4], 0u);
    if (!store->write(store->flash_context, record_offset,
                      header, sizeof(header)) ||
            !store->write(store->flash_context, record_offset + 8u,
                          state, aligned_state_length)) {
        result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_WRITE_FAILED;
        return result->status;
    }
    result->slot = selected_slot;
    result->record_offset = record_offset;
    result->status = GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK;
    return result->status;
}

bool gomore_primitives_cubic_candidates(
    float a, float b, float c, float d,
    void *destination, size_t destination_length,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_float_binary_fn arctangent2,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_float_unary_fn logarithm,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine) {
    if (destination == NULL || destination_length < 0x24u ||
            power == NULL) {
        return false;
    }

    const float a_squared = power(a, 2.0f);
    const float b_over_three_a = b / (a * 3.0f);
    const float b_ratio_cubed = power(b_over_three_a, 3.0f);
    const float q = ((b * c) / (a_squared * 6.0f) - b_ratio_cubed) -
        d / (a * 2.0f);
    const float q_squared = power(q, 2.0f);
    const float b_ratio_squared = power(b_over_three_a, 2.0f);
    const float p = c / (a * 3.0f) - b_ratio_squared;
    const float p_cubed = power(p, 3.0f);
    const float discriminant = q_squared + p_cubed;

    const float root_of_unity[2] = {
        -0.5f,
        power(3.0f, 0.5f) * 0.5f,
    };
    float signed_root[2];
    if (!gomore_primitives_split_signed_root(
            discriminant, signed_root, power)) {
        return false;
    }
    float first_radical[2] = {
        signed_root[0] + q,
        signed_root[1],
    };
    float second_radical[2] = {
        q - signed_root[0],
        -signed_root[1],
    };
    return gomore_primitives_cardano_candidates(
        discriminant, a, b, destination, destination_length,
        root_of_unity, first_radical, second_radical,
        power, arctangent2, square_root, logarithm, exponential,
        cosine, sine);
}

bool gomore_primitives_scale(float factor, const float *source,
                             float *destination, size_t count) {
    if ((source == NULL || destination == NULL) && count != 0u) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = source[index] * factor;
    }
    return true;
}

bool gomore_primitives_callback_record_initialize(uint8_t *record,
                                                  size_t length,
                                                  uint32_t field_b8,
                                                  uint32_t field_bc) {
    if (record == NULL || length < GOMORE_PRIMITIVES_CALLBACK_RECORD_BYTES) {
        return false;
    }
    record[0xB4u] = 0u;
    store_u32_le(&record[0xB8u], field_b8);
    store_u32_le(&record[0xBCu], field_bc);
    return true;
}

bool gomore_primitives_sort_float_subrange(
    float *values, size_t value_count, size_t first, size_t last,
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare) {
    if (values == NULL || qsort_provider == NULL || compare == NULL ||
            first > last || last >= value_count) {
        return false;
    }
    qsort_provider(&values[first], (last - first) + 1u, sizeof(*values),
                   compare);
    return true;
}

int32_t gomore_primitives_max_index(const float *values, uint32_t count,
                                    gomore_primitives_max_index_fn provider) {
    if (provider == NULL || (values == NULL && count != 0u)) {
        return -1;
    }
    return provider(values, count);
}

bool gomore_primitives_set_second_word(uint32_t record[2], uint32_t value) {
    if (record == NULL) {
        return false;
    }
    record[1] = value;
    return true;
}

uint32_t gomore_primitives_size_736(void) {
    return UINT32_C(0x2E0);
}

uint32_t gomore_primitives_size_14816(void) {
    return UINT32_C(0x39E0);
}

uint32_t gomore_primitives_return_zero(void) {
    return 0u;
}

void gomore_primitives_noop_76500(void) {
}

void gomore_primitives_noop_578c8(void) {
}

void gomore_primitives_noop_49e58(void) {
}

void gomore_primitives_noop_91080(void) {
}

bool gomore_primitives_clear_72(void *record, size_t length) {
    if (record == NULL || length < 0x48u) {
        return false;
    }
    clear_bytes(record, 0x48u);
    return true;
}

bool gomore_primitives_store_first_word(uint32_t *record, uint32_t value) {
    if (record == NULL) {
        return false;
    }
    *record = value;
    return true;
}

bool gomore_primitives_clear_first_byte(uint8_t *record) {
    if (record == NULL) {
        return false;
    }
    *record = 0u;
    return true;
}

bool gomore_primitives_triplet_initialize(uint32_t record[3],
                                          uint32_t field4,
                                          uint32_t field0,
                                          uint32_t field8) {
    if (record == NULL) {
        return false;
    }
    record[1] = field4;
    record[0] = field0;
    record[2] = field8;
    return true;
}

float gomore_primitives_interpolate(float weight, float first, float second) {
    return second + weight * (first - second);
}

bool gomore_primitives_byte_in_70_100(uint8_t value) {
    return (uint8_t)(value - UINT8_C(70)) <= UINT8_C(30);
}

bool gomore_primitives_clear_flag_1000(uint8_t *state, size_t length) {
    if (state == NULL || length <= 1000u) {
        return false;
    }
    if (state[1000] == 1u) {
        state[1000] = 0u;
    }
    return true;
}

float gomore_primitives_cubic_scale(float value) {
    return value * 0x1.2e09fep-3f * value * value;
}

float gomore_primitives_linear_evaluate(float value, float slope,
                                        float intercept) {
    return intercept + slope * value;
}

bool gomore_primitives_shift_u8_window5(uint8_t values[5], uint8_t value) {
    if (values == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        values[index] = values[index + 1u];
    }
    values[4] = value;
    return true;
}

size_t gomore_primitives_nullable_strlen(const char *text) {
    if (text == NULL) {
        return 0u;
    }
    size_t length = 0u;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}

bool gomore_primitives_u16_in_30000_50000(uint16_t value) {
    return (uint16_t)(value - UINT16_C(30000)) <= UINT16_C(20000);
}

bool gomore_primitives_clear_36(void *record, size_t length) {
    if (record == NULL || length < 0x24u) {
        return false;
    }
    clear_bytes(record, 0x24u);
    return true;
}

bool gomore_primitives_step_record_initialize(void *record, size_t length) {
    if (record == NULL || length < 0x1Cu) {
        return false;
    }
    clear_bytes(record, 0x1Cu);
    store_u32_le((uint8_t *)record + 0x10u, 5u);
    return true;
}

bool gomore_primitives_clear_124(void *record, size_t length) {
    if (record == NULL || length < 0x7Cu) {
        return false;
    }
    clear_bytes(record, 0x7Cu);
    return true;
}

bool gomore_primitives_float_state_initialize(void *record, size_t length) {
    if (record == NULL || length < 0x80u ||
            !gomore_primitives_clear_124(record, length)) {
        return false;
    }
    store_u32_le((uint8_t *)record + 0x7Cu, UINT32_C(0x3C54FDF4));
    return true;
}

uint32_t gomore_primitives_half_to_float_bits(uint16_t value) {
    return ((uint32_t)value >> 15u) << 31u |
           ((((uint32_t)value & UINT32_C(0x7FFF)) >> 10u) +
            UINT32_C(0x70)) << 23u |
           ((uint32_t)value & UINT32_C(0x03FF)) << 13u;
}

bool gomore_primitives_store_half_as_float_bits(uint32_t *destination,
                                                uint16_t value) {
    if (destination == NULL) {
        return false;
    }
    *destination = gomore_primitives_half_to_float_bits(value);
    return true;
}

int32_t gomore_primitives_find_next_nonnegative_i16(
    const int16_t *values, size_t count, size_t start) {
    if (values == NULL || count <= 1u || start >= count - 1u) {
        return -1;
    }
    while (start < count - 1u) {
        if (values[start] >= 0) {
            return (int32_t)start;
        }
        ++start;
    }
    return -1;
}

bool gomore_primitives_shift_two_u8_windows5(
    uint8_t first[5], uint8_t second[5],
    uint8_t first_value, uint8_t second_value) {
    return gomore_primitives_shift_u8_window5(first, first_value) &&
           gomore_primitives_shift_u8_window5(second, second_value);
}

float gomore_primitives_normalized_position(float value, float high,
                                            float low) {
    const float span = high - low;
    return span == 0.0f ? 0.0f : (value - low) / span;
}

bool gomore_primitives_packed_2bit_get(const uint8_t *bytes,
                                       size_t length, uint32_t index,
                                       uint8_t *value) {
    const uint32_t wrapped = index % UINT32_C(0xB40);
    const size_t byte_index = (size_t)(wrapped >> 2u);
    if (bytes == NULL || value == NULL || byte_index >= length) {
        return false;
    }
    *value = (uint8_t)((bytes[byte_index] >>
                        ((wrapped & UINT32_C(3)) << 1u)) & UINT8_C(3));
    return true;
}

bool gomore_primitives_energy_state_reset(void *record, size_t length) {
    if (record == NULL || length < 0x58u) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0x4Cu], 0u);
    store_u32_le(&bytes[0x50u], 0u);
    store_u32_le(&bytes[0x54u], 0u);
    store_u32_le(&bytes[0x0Cu], 0u);
    store_u32_le(&bytes[0x14u], UINT32_C(0x3F800000));
    bytes[0x18u] = 0u;
    return true;
}

bool gomore_primitives_large_default_state_initialize(void *record,
                                                      size_t length) {
    if (record == NULL || length < 0x404u) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x404u);
    store_u32_le(&bytes[0x3F8u], 3u);
    store_u32_le(&bytes[0x3FCu], UINT32_C(0x3F000000));
    return true;
}

bool gomore_primitives_scale_milli(float *values, size_t count) {
    if (values == NULL && count != 0u) {
        return false;
    }
    const float scale = bits_float(UINT32_C(0x3A83126F));
    for (size_t index = 0u; index < count; ++index) {
        values[index] *= scale;
    }
    return true;
}

bool gomore_primitives_sps_state_reset(void *record, size_t length) {
    if (record == NULL || length < 0x58u) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0x54u], 0u);
    store_u32_le(&bytes[0x4Cu], 0u);
    store_u32_le(&bytes[0x2Cu], 0u);
    store_u32_le(&bytes[0x28u], 0u);
    store_u16_le_early(&bytes[0x30u], 0u);
    store_u32_le(&bytes[0x10u], 0u);
    store_u32_le(&bytes[0x0Cu], 0u);
    store_u16_le_early(&bytes[0x14u], 0u);
    return true;
}

bool gomore_primitives_shift_status_windows(uint8_t history[10],
                                            uint8_t output[3]) {
    if (history == NULL || output == NULL ||
            !gomore_primitives_shift_two_u8_windows5(
                &history[5], &history[0], 0u, UINT8_C(0xFE))) {
        return false;
    }
    output[0] = UINT8_C(0xFF);
    output[1] = UINT8_C(0xFE);
    output[2] = 0u;
    return true;
}

size_t gomore_primitives_count_byte_plus_one(const uint8_t *values,
                                             size_t count,
                                             uint8_t target) {
    if (values == NULL && count != 0u) {
        return 0u;
    }
    size_t matches = 0u;
    for (size_t index = 0u; index < count; ++index) {
        matches += values[index] == target ? 1u : 0u;
    }
    return matches + 1u;
}

bool gomore_primitives_accumulate_pair(void *record, size_t length,
                                       float first, float second) {
    if (record == NULL || length < 0x0Eu) {
        return false;
    }
    uint8_t *bytes = record;
    const float accumulated_second =
        bits_float(load_u32_le(&bytes[4])) + second;
    const float accumulated_first =
        bits_float(load_u32_le(&bytes[8])) + first;
    store_u32_le(&bytes[4], float_bits(accumulated_second));
    store_u32_le(&bytes[8], float_bits(accumulated_first));
    store_u16_le_early(
        &bytes[0x0Cu],
        (uint16_t)(load_u16_le_early(&bytes[0x0Cu]) + 1u));
    return true;
}

bool gomore_primitives_selected_state_reset(void *record, size_t length) {
    if (record == NULL || length < 0x64u) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0x10u], 0u);
    store_u32_le(&bytes[0x0Cu], 0u);
    bytes[4] = 0u;
    bytes[1] = 0u;
    for (size_t index = 0u; index < 20u; ++index) {
        store_u32_le(&bytes[0x14u + index * 4u], 0u);
    }
    return true;
}

bool gomore_primitives_pattern17_initialize(void *record, size_t length) {
    if (record == NULL || length < 17u) {
        return false;
    }
    uint8_t *bytes = record;
    for (size_t index = 0u; index < 5u; ++index) {
        bytes[index] = UINT8_C(0xFE);
        bytes[index + 5u] = 0u;
        bytes[index + 10u] = 0u;
    }
    bytes[15] = 1u;
    bytes[16] = 1u;
    return true;
}

bool gomore_primitives_energy_record_initialize(void *record, size_t length,
                                                uint32_t binding) {
    if (record == NULL || length < 0x5Cu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x5Cu);
    if (!gomore_primitives_energy_state_reset(record, length)) {
        return false;
    }
    bytes[8] = 0u;
    store_u32_le(&bytes[0], 1u);
    store_u32_le(&bytes[0x58u], binding);
    return true;
}

bool gomore_primitives_large_state_initialize(void *record, size_t length,
                                              uint32_t binding,
                                              void **active_record) {
    if (record == NULL || active_record == NULL || length < 0x33Cu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x33Cu);
    *active_record = record;
    store_u32_le(&bytes[0x338u], binding);
    return true;
}

bool gomore_primitives_low24_binding_initialize(
    uint32_t record[2], const uint8_t value[3], uint32_t binding) {
    if (record == NULL || value == NULL) {
        return false;
    }
    record[0] = (uint32_t)value[0] |
                (uint32_t)value[1] << 8u |
                (uint32_t)value[2] << 16u;
    record[1] = binding;
    return true;
}

bool gomore_primitives_pack4_binding_initialize(
    uint32_t record[2], uint8_t byte0, uint8_t byte1,
    uint8_t byte2, uint8_t byte3, uint32_t binding) {
    if (record == NULL) {
        return false;
    }
    record[0] = (uint32_t)byte0 |
                (uint32_t)byte1 << 8u |
                (uint32_t)byte2 << 16u |
                (uint32_t)byte3 << 24u;
    record[1] = binding;
    return true;
}

int16_t gomore_primitives_i16_mean(const int16_t *values, size_t count) {
    if (values == NULL || count == 0u || count > (size_t)INT32_MAX) {
        return 0;
    }
    uint32_t wrapped_sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        wrapped_sum += (uint32_t)(int32_t)values[index];
    }
    const int32_t signed_sum = (int32_t)wrapped_sum;
    return (int16_t)(signed_sum / (int32_t)count);
}

bool gomore_primitives_float_floor_update(float candidate, float *value) {
    if (value == NULL) {
        return false;
    }
    float difference = 0.0f;
    if (candidate <= *value) {
        difference = *value - candidate;
    }
    *value = difference + candidate;
    return true;
}

bool gomore_primitives_validate_selector(const uint8_t *state,
                                         size_t length, int8_t *selector) {
    if (state == NULL || selector == NULL || length < 17u) {
        return false;
    }
    if ((*selector == 1 && state[15] == 0u) ||
            (*selector == 2 && state[16] == 0u)) {
        *selector = -1;
    }
    return true;
}

int32_t gomore_primitives_nullable_compare(const uint8_t *left,
                                           const uint8_t *right) {
    if (left == NULL || right == NULL) {
        return 0;
    }
    while (*left == *right) {
        if (*left == 0u) {
            return 0;
        }
        ++left;
        ++right;
    }
    return (int32_t)*left - (int32_t)*right;
}

bool gomore_primitives_compact_u32_stride(uint32_t *values,
                                          size_t capacity,
                                          size_t count, size_t stride,
                                          size_t *output_count) {
    if (output_count == NULL || stride == 0u || count > capacity ||
            (values == NULL && count != 0u)) {
        return false;
    }
    size_t destination = 0u;
    for (size_t source = 0u; source < count; source += stride) {
        values[destination++] = values[source];
    }
    *output_count = destination;
    return true;
}

int32_t gomore_primitives_status_record_extract(const void *source,
                                                size_t source_length,
                                                void *destination,
                                                size_t destination_length) {
    if (source == NULL || destination == NULL || source_length < 0x56u ||
            destination_length < 0x44u) {
        return -1;
    }
    const uint8_t *source_bytes = source;
    uint8_t *destination_bytes = destination;
    if (load_u16_le_early(&source_bytes[0x54u]) != 0u) {
        clear_bytes(destination_bytes, 0x44u);
        return -1008;
    }
    store_u16_le_early(&destination_bytes[0x42u],
                       load_u16_le_early(&source_bytes[0x52u]));
    return 0;
}

bool gomore_primitives_half_span_initialize(uint32_t record[5],
                                            uint16_t half_value,
                                            uint32_t base) {
    if (record == NULL) {
        return false;
    }
    record[0] = gomore_primitives_half_to_float_bits(half_value);
    record[1] = base;
    record[2] = base + UINT32_C(0x14);
    record[3] = base + UINT32_C(0x28);
    record[4] = base + UINT32_C(0x3C);
    return true;
}

bool gomore_primitives_parameter_state_initialize(void *record,
                                                  size_t length,
                                                  uint32_t binding) {
    if (record == NULL || length < 0x20FCu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x20FCu);
    store_u32_le(&bytes[0x20F8u], binding);
    return true;
}

size_t gomore_primitives_count_encoded_i32(const int32_t *values,
                                           size_t count) {
    if (values == NULL && count != 0u) {
        return 0u;
    }
    size_t matches = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const uint32_t encoded =
            (uint32_t)values[index] + UINT32_C(0xBF200000);
        matches += encoded < UINT32_C(0x00E80001) ? 1u : 0u;
    }
    return matches;
}

float gomore_primitives_scaled_ratio(float numerator, float denominator) {
    const float scaled_denominator =
        denominator * bits_float(UINT32_C(0x40333333));
    if (scaled_denominator == 0.0f) {
        return 0.0f;
    }
    return (numerator * bits_float(UINT32_C(0x43480000))) /
           scaled_denominator;
}

uint8_t gomore_primitives_piecewise_clamp_70_100(int32_t value) {
    int64_t delta = (int64_t)value - INT64_C(96);
    delta *= delta < 0 ? INT64_C(5) : INT64_C(8);
    int64_t transformed = delta / INT64_C(10) + INT64_C(96);
    if (transformed < 70) {
        transformed = 70;
    } else if (transformed > 100) {
        transformed = 100;
    }
    return (uint8_t)transformed;
}

bool gomore_primitives_missing_window_initialize(void *record,
                                                 size_t length) {
    if (record == NULL || length < 0x3Eu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x38u);
    for (size_t index = 0u; index < 6u; ++index) {
        bytes[0x38u + index] = UINT8_C(0xFF);
    }
    return true;
}

bool gomore_primitives_modulo_value_get(const uint8_t *bytes,
                                        size_t length, uint32_t index,
                                        bool packed, uint8_t *value) {
    const uint32_t wrapped = index % UINT32_C(0xB40);
    const size_t byte_index = packed ? (size_t)(wrapped >> 2u)
                                     : (size_t)wrapped;
    if (bytes == NULL || value == NULL || byte_index >= length) {
        return false;
    }
    *value = packed
        ? (uint8_t)((bytes[byte_index] >>
                     ((wrapped & UINT32_C(3)) << 1u)) & UINT8_C(3))
        : bytes[byte_index];
    return true;
}

bool gomore_primitives_mode8_state_initialize(void *record, size_t length) {
    if (record == NULL || length < 0x26Eu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x26Eu);
    bytes[0] = 8u;
    return true;
}

bool gomore_primitives_vector_pair_transform(float scale, float offset,
                                             const float left[2],
                                             const float right[2],
                                             float output[2]) {
    if (left == NULL || right == NULL || output == NULL) {
        return false;
    }
    output[0] = (left[0] - offset / (scale * 3.0f)) + right[0];
    output[1] = left[1] + right[1];
    return true;
}

bool gomore_primitives_encode_short_record(uint8_t record[17],
                                           const uint8_t *payload,
                                           size_t payload_length) {
    if (record == NULL || payload_length > 16u ||
            (payload == NULL && payload_length != 0u)) {
        return false;
    }
    clear_bytes(record, 17u);
    record[16] = (uint8_t)((payload_length & 0x7Fu) | 0x80u);
    for (size_t index = 0u; index < payload_length; ++index) {
        record[index] = payload[index];
    }
    return true;
}

bool gomore_primitives_accumulate_i8x4_milli(float values[4],
                                             const int8_t increments[4]) {
    if (values == NULL || increments == NULL) {
        return false;
    }
    const float scale = bits_float(UINT32_C(0x3C23D70A));
    for (size_t index = 0u; index < 4u; ++index) {
        values[index] += (float)increments[index] * scale;
    }
    return true;
}

uint32_t gomore_primitives_shift_presence_history(uint8_t *record,
                                                  size_t length,
                                                  uint8_t value) {
    if (record == NULL || length < 0x19u) {
        return 0u;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        record[0x14u + index] = record[0x15u + index];
    }
    record[0x18u] = value;
    if (value != 0u && record[0x17u] == 0u) {
        if (record[0x16u] != 0u) {
            return 1u;
        }
        if (record[0x15u] != 0u) {
            return 2u;
        }
    }
    return 0u;
}

bool gomore_primitives_fill_float_progression(float *values, size_t count,
                                              size_t begin, size_t end,
                                              float first, float step) {
    if (values == NULL || begin > end || end > count) {
        return false;
    }
    size_t offset = 0u;
    for (size_t index = begin; index < end; ++index) {
        values[index] = first + (float)offset * step;
        ++offset;
    }
    return true;
}

bool gomore_primitives_time_record_valid(const void *record, size_t length) {
    if (record == NULL || length < 8u) {
        return false;
    }
    const uint8_t *bytes = record;
    const uint16_t first = load_u16_le_early(&bytes[0]);
    const uint16_t second = load_u16_le_early(&bytes[2]);
    return (uint16_t)(first - UINT16_C(15)) < UINT16_C(46) &&
           second < UINT16_C(241) && bytes[6] <= 23u && bytes[7] <= 23u;
}

size_t gomore_primitives_float_argmax_range(const float *values,
                                            size_t count, size_t begin,
                                            size_t end) {
    if (values == NULL || begin >= end || end > count) {
        return SIZE_MAX;
    }
    size_t result = begin;
    float largest = values[begin];
    for (size_t index = begin; index < end; ++index) {
        if (largest < values[index]) {
            result = index & 0xFFu;
            largest = values[index];
        }
    }
    return result;
}

int32_t gomore_primitives_float_argmax_above_floor(const float *values,
                                                   size_t count) {
    if (values == NULL && count != 0u) {
        return -1;
    }
    int32_t result = -1;
    float largest = bits_float(UINT32_C(0xCE6E6B28));
    for (size_t index = 0u; index < count; ++index) {
        if (largest < values[index]) {
            result = (int32_t)index;
            largest = values[index];
        }
    }
    return result;
}

int32_t gomore_primitives_i16_range(const int16_t *values, size_t count) {
    if (values == NULL || count == 0u) {
        return 32000;
    }
    int32_t minimum = values[0];
    int32_t maximum = values[0];
    for (size_t index = 0u; index < count; ++index) {
        if (values[index] < minimum) {
            minimum = values[index];
        }
        if (values[index] > maximum) {
            maximum = values[index];
        }
    }
    const int32_t range = maximum - minimum;
    return range < 32001 ? (int32_t)(int16_t)range : 32000;
}

bool gomore_primitives_packed_2bit_set(uint8_t *bytes, size_t length,
                                      uint32_t index, uint8_t value) {
    const uint32_t wrapped = index % UINT32_C(0xB40);
    const size_t byte_index = (size_t)(wrapped >> 2u);
    if (bytes == NULL || byte_index >= length) {
        return false;
    }
    const uint32_t shift = (wrapped & UINT32_C(3)) << 1u;
    const uint8_t clear_mask = (uint8_t)~(uint8_t)(UINT8_C(3) << shift);
    bytes[byte_index] = (uint8_t)((bytes[byte_index] & clear_mask) |
                                 (uint8_t)(value << shift));
    return true;
}

float gomore_primitives_rational_transform(float value, float state) {
    const float scaled = value * bits_float(UINT32_C(0x3E16277C)) *
                         state * bits_float(UINT32_C(0x42C80000));
    const float denominator = bits_float(UINT32_C(0x42700000)) -
        value * bits_float(UINT32_C(0x3E20FBA9)) * state *
        bits_float(UINT32_C(0x42C80000));
    return scaled / denominator;
}

int16_t gomore_primitives_i16_mean_absolute_difference(
    const int16_t *values, size_t count) {
    if (values == NULL || count <= 1u) {
        return 0;
    }
    uint32_t sum = 0u;
    for (size_t index = 0u; index + 1u < count; ++index) {
        int32_t difference = (int32_t)values[index + 1u] - values[index];
        if (difference < 0) {
            difference = -difference;
        }
        sum += (uint32_t)difference;
    }
    return (int16_t)(sum / (uint32_t)(count - 1u));
}

bool gomore_primitives_u16_all_within_300(const uint16_t *values,
                                         size_t count, uint16_t target) {
    if (values == NULL && count != 0u) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        const uint16_t difference = values[index] < target
            ? (uint16_t)(target - values[index])
            : (uint16_t)(values[index] - target);
        if (difference > 300u) {
            return false;
        }
    }
    return true;
}

float gomore_primitives_nonzero_i16_mean8(const int16_t values[8]) {
    if (values == NULL) {
        return 0.0f;
    }
    int32_t sum = 0;
    int32_t count = 0;
    for (size_t index = 0u; index < 8u; ++index) {
        if (values[index] != 0) {
            sum += values[index];
            ++count;
        }
    }
    return count > 0 ? (float)sum / (float)count : 0.0f;
}

float gomore_primitives_circular_u8_dot18(const uint8_t values[18],
                                         uint32_t sample_index,
                                         const float weights[18]) {
    if (values == NULL || weights == NULL) {
        return 0.0f;
    }
    float result = 0.0f;
    const uint32_t start = sample_index / UINT32_C(30);
    for (size_t index = 0u; index < 18u; ++index) {
        const size_t value_index =
            (size_t)((start + (uint32_t)index) % UINT32_C(18));
        result += (float)values[value_index] * weights[index];
    }
    return result;
}

bool gomore_primitives_motion_gate_accumulate(
    gomore_primitives_motion_gate_state *state,
    uint32_t elapsed_seconds, uint32_t current_timestamp,
    float sample, const float weights[18],
    gomore_primitives_motion_gate_output *output) {
    if (state == NULL || weights == NULL || output == NULL ||
            elapsed_seconds > current_timestamp) {
        return false;
    }
    output->updated = false;
    output->valid = true;

    const uint32_t bucket_start = current_timestamp - elapsed_seconds;
    if (current_timestamp != elapsed_seconds &&
            current_timestamp / UINT32_C(30) !=
            bucket_start / UINT32_C(30)) {
        uint8_t bucket = state->last_bucket;
        if (state->pending_count > 0) {
            const float average = state->pending_sum /
                (float)state->pending_count;
            float bounded = bits_float(UINT32_C(0x437F0000));
            if ((int32_t)float_bits(average) < INT32_C(0x437F0000)) {
                bounded = average;
            }
            float selected = 0.0f;
            if (bounded >= 0.0f) {
                selected = bits_float(UINT32_C(0x437F0000));
                if ((int32_t)float_bits(average) <
                        INT32_C(0x437F0000)) {
                    selected = average;
                }
            }
            bucket = (uint8_t)(uint32_t)selected;
            state->last_bucket = bucket;
        }
        state->buckets[(bucket_start / UINT32_C(30)) % UINT32_C(18)] =
            bucket;

        if (elapsed_seconds < UINT32_C(540)) {
            uint32_t fill_timestamp = bucket_start;
            while (fill_timestamp + UINT32_C(30) < current_timestamp) {
                fill_timestamp += UINT32_C(30);
                state->buckets[
                    (fill_timestamp / UINT32_C(30)) % UINT32_C(18)] =
                    state->last_bucket;
            }
        } else {
            for (size_t index = 0u; index < 18u; ++index) {
                state->buckets[index] = 0u;
            }
            state->pending_sum = 0.0f;
            state->pending_count = 0;
            state->last_bucket = 0u;
        }

        output->score = gomore_primitives_circular_u8_dot18(
            state->buckets, current_timestamp, weights);
        output->positive_after_bias =
            output->score + bits_float(UINT32_C(0x3FBF9D06)) > 0.0f;
        output->updated = true;
        state->pending_sum = 0.0f;
        state->pending_count = 0;
    }
    if (sample >= 0.0f) {
        state->pending_sum += sample;
        ++state->pending_count;
    }
    return true;
}

bool gomore_primitives_peak_statistics(
    const float *values, size_t count, size_t radius, float output[4],
    gomore_primitives_float_binary_fn power,
    gomore_primitives_float_unary_fn square_root) {
    if (values == NULL || output == NULL || power == NULL ||
            square_root == NULL || count > 46340u ||
            radius > count || radius > (count - radius)) {
        return false;
    }

    int32_t spacing_sum = 0;
    int32_t spacing_square_sum = 0;
    size_t peak_count = 0u;
    size_t previous_peak = 0u;
    float value_sum = 0.0f;
    float value_square_sum = 0.0f;
    const size_t end = count - radius;
    for (size_t index = radius; index < end; ++index) {
        bool peak = true;
        for (size_t neighbor = index - radius;
             neighbor <= index + radius; ++neighbor) {
            if (values[neighbor] > values[index]) {
                peak = false;
                break;
            }
        }
        if (!peak) {
            continue;
        }
        ++peak_count;
        value_sum += values[index];
        value_square_sum += power(values[index], 2.0f);
        if (peak_count > 1u) {
            const int32_t spacing =
                (int32_t)(index - previous_peak);
            spacing_sum += spacing;
            spacing_square_sum = (int32_t)(
                power((float)spacing, 2.0f) +
                (float)spacing_square_sum);
        }
        previous_peak = index;
    }

    output[0] = peak_count < 2u ? -1.0f :
        (float)spacing_sum / (float)(peak_count - 1u);
    output[2] = peak_count == 0u ? -1.0f :
        value_sum / (float)peak_count;
    if (peak_count == 0u) {
        output[3] = -1.0f;
    } else {
        const float peaks = (float)peak_count;
        output[3] = square_root(
            (value_square_sum - power(value_sum, 2.0f) / peaks) /
            peaks);
    }
    if (peak_count < 2u) {
        output[1] = -1.0f;
    } else {
        const float spacings = (float)(peak_count - 1u);
        output[1] = square_root(
            ((float)spacing_square_sum -
             power((float)spacing_sum, 2.0f) / spacings) /
            spacings);
    }
    return true;
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
    return (float)(values[index] - values[index - 1u]);
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
        variation_sum / normalizer;
    output->average_completed_run = direction_changes == 0 ? 0.0f :
        (float)completed_run_sum / (float)direction_changes;
    return true;
}

_Static_assert(
    sizeof(gomore_primitives_dormant_heart_rate_filter_state) == 100u,
    "dormant heart-rate filter state layout");

int32_t gomore_primitives_dormant_heart_rate_filter_update(
    void *state_pointer, int32_t input, int32_t output[2],
    uint32_t interval_milliseconds) {
    if (state_pointer == NULL || output == NULL) {
        return INT32_C(0x1775);
    }
    gomore_primitives_dormant_heart_rate_filter_state *state =
        state_pointer;
    output[1] = input;
    if (interval_milliseconds < UINT32_C(700) ||
            interval_milliseconds > UINT32_C(1300)) {
        return INT32_C(0x1771);
    }
    if (state->enabled != 1u) {
        return INT32_C(0x1772);
    }

    int32_t status = 1;
    int32_t effective_input = input;
    if (input < 1) {
        if (state->positive_streak == 0u &&
                state->has_seen_positive == 0u) {
            (void)gomore_primitives_selected_state_reset(
                state, sizeof(*state));
            output[0] = dormant_estimator_float_to_i32(state->average);
            return INT32_C(0x1775);
        }
        ++state->missing_count;
        state->positive_streak = 0u;
        state->unchanged_count = 0u;
        if (state->missing_count > 3u) {
            (void)gomore_primitives_selected_state_reset(
                state, sizeof(*state));
            output[0] = dormant_estimator_float_to_i32(state->average);
            return INT32_C(0x1773);
        }
    } else {
        state->missing_count = 0u;
        if (state->has_seen_positive == 0u) {
            state->has_seen_positive = 1u;
        }
        if (state->positive_streak < 3u) {
            ++state->positive_streak;
        }
        float delta = 0.0f;
        if (state->average > 0.0f) {
            const uint32_t raw_delta = (uint32_t)input -
                (uint32_t)state->last_effective_input;
            delta = (float)(int32_t)raw_delta;
        } else {
            state->unchanged_count = 0u;
        }
        if (delta == 0.0f) {
            ++state->unchanged_count;
            if (state->unchanged_count > 20u) {
                status = INT32_C(0x1774);
            }
        } else {
            state->unchanged_count = 0u;
            if ((int32_t)float_bits(delta) > INT32_C(0x40C00000)) {
                effective_input = state->last_effective_input + 6;
            } else if (float_bits(delta) > UINT32_C(0xC0E00000)) {
                effective_input = state->last_effective_input - 7;
            }
        }
    }

    const uint8_t count = state->history_count;
    if (count < 19u) {
        if (count == 0u) {
            state->average = (float)effective_input;
        } else {
            float sum = 0.0f;
            for (uint8_t index = 0u; index < count; ++index) {
                sum += state->history[index];
            }
            state->average = sum / (float)count;
        }
    } else {
        float sum = 0.0f;
        for (uint8_t index = 0u; index < 19u; ++index) {
            sum += state->history[index];
            state->history[index] = state->history[index + 1u];
        }
        state->history[19] = (float)effective_input;
        state->average = (sum + (float)effective_input) / 20.0f;
        --state->history_count;
    }
    const uint8_t append_index = state->history_count;
    ++state->history_count;
    state->history[append_index] = (float)effective_input;
    state->last_effective_input = effective_input;
    output[0] = dormant_estimator_float_to_i32(state->average);
    return status;
}

bool gomore_primitives_six_channel_ring_score(
    const int16_t *channel0, const int16_t *channel1,
    const int16_t *channel2, const int16_t *channel3,
    const int16_t *channel4, const int16_t *channel5,
    size_t ring_size, size_t cursor, size_t window_count,
    const gomore_primitives_six_channel_linear_model *model,
    int16_t *output) {
    if (channel0 == NULL || channel1 == NULL || channel2 == NULL ||
            channel3 == NULL || channel4 == NULL || channel5 == NULL ||
            model == NULL || output == NULL || ring_size == 0u ||
            ring_size > 127u || cursor >= ring_size ||
            window_count > ring_size || model->minimum_output > 32000) {
        return false;
    }

    const int16_t *const channels[6] = {
        channel0, channel1, channel2, channel3, channel4, channel5,
    };
    int32_t sums[6] = {0, 0, 0, 0, 0, 0};
    for (size_t distance = 1u; distance <= window_count; ++distance) {
        const size_t index = cursor >= distance
            ? cursor - distance
            : ring_size - (distance - cursor);
        for (size_t channel = 0u; channel < 6u; ++channel) {
            sums[channel] += channels[channel][index];
        }
    }

    int32_t maximum = sums[3];
    int32_t middle = sums[4];
    int32_t minimum = sums[5];
    if (maximum < middle) {
        const int32_t swap = maximum;
        maximum = middle;
        middle = swap;
    }
    if (middle < minimum) {
        const int32_t swap = middle;
        middle = minimum;
        minimum = swap;
    }
    if (maximum < middle) {
        const int32_t swap = maximum;
        maximum = middle;
        middle = swap;
    }

    float value = model->empty_window_value;
    if (window_count != 0u) {
        value = model->weights[0] * (float)sums[0];
        value += (float)sums[1] * model->weights[1];
        value += (float)sums[2] * model->weights[2];
        value += (float)maximum * model->weights[3];
        value += (float)middle * model->weights[4];
        value += (float)minimum * model->weights[5];
        value /= (float)window_count;
    }
    int32_t converted = dormant_estimator_float_to_i32(
        (value + model->bias) * model->scale);
    if (converted > 32000) {
        converted = 32000;
    } else if (converted < model->minimum_output) {
        converted = model->minimum_output;
    }
    *output = (int16_t)converted;
    return true;
}

int32_t gomore_primitives_filtered_u8_mean(const uint8_t *values,
                                          size_t count, int32_t center,
                                          int32_t tolerance) {
    if (values == NULL || count > 127u || tolerance < 0) {
        return 0;
    }
    int32_t sum = 0;
    int32_t included = 0;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t value = values[index];
        int32_t difference = value - center;
        if (difference < 0) {
            difference = -difference;
        }
        if (value != 0 && difference <= tolerance) {
            sum += value;
            ++included;
        }
    }
    return included != 0 ? sum / included : 0;
}

bool gomore_primitives_complex_multiply(const float left[2],
                                        const float right[2],
                                        float output[2]) {
    if (left == NULL || right == NULL || output == NULL) {
        return false;
    }
    const float left_real = left[0];
    const float left_imaginary = left[1];
    const float right_real = right[0];
    const float right_imaginary = right[1];
    output[0] = left_real * right_real - left_imaginary * right_imaginary;
    output[1] = left_imaginary * right_real + left_real * right_imaginary;
    return true;
}

bool gomore_primitives_complex_power(
    float exponent, float value[2],
    gomore_primitives_float_binary_fn arctangent2,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_float_unary_fn logarithm,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine) {
    if (value == NULL || arctangent2 == NULL || square_root == NULL ||
            logarithm == NULL || exponential == NULL || cosine == NULL ||
            sine == NULL) {
        return false;
    }
    const float real = value[0];
    const float imaginary = value[1];
    const float angle = arctangent2(imaginary, real);
    const float magnitude = square_root(
        real * real + imaginary * imaginary);
    const float powered_magnitude = exponential(exponent * logarithm(magnitude));
    const float powered_angle = exponent * angle;
    value[0] = cosine(powered_angle) * powered_magnitude;
    value[1] = sine(powered_angle) * powered_magnitude;
    return true;
}

bool gomore_primitives_circular_feature_slot_advance(
    void *state, size_t state_length) {
    if (state == NULL || state_length < 0x224u) {
        return false;
    }
    uint8_t *bytes = state;
    const uint8_t cursor = bytes[0x52u];
    if (cursor >= 8u) {
        return false;
    }
    const size_t slot_offset = (size_t)cursor * 2u;
    static const size_t bases[9] = {
        0x02u, 0x204u, 0x214u, 0x12u, 0x22u,
        0x32u, 0x42u, 0x1E4u, 0x1F4u,
    };
    for (size_t index = 0u; index < 9u; ++index) {
        store_u16_le_early(&bytes[bases[index] + slot_offset], 0u);
    }
    bytes[0x52u] = (uint8_t)((cursor + 1u) & 7u);
    return true;
}

bool gomore_primitives_circular_i16_mean3(
    const int16_t *first, const int16_t *second, const int16_t *third,
    size_t ring_size, size_t cursor, size_t count,
    int16_t output[3]) {
    if (output == NULL) {
        return false;
    }
    output[0] = 0;
    output[1] = 0;
    output[2] = 0;
    if (first == NULL || second == NULL || third == NULL ||
            ring_size == 0u || ring_size > 128u || cursor >= ring_size ||
            count > ring_size) {
        return false;
    }
    int32_t totals[3] = {0, 0, 0};
    for (size_t distance = 1u; distance <= count; ++distance) {
        const size_t index = (cursor + ring_size - distance) % ring_size;
        totals[0] += first[index];
        totals[1] += second[index];
        totals[2] += third[index];
    }
    if (count != 0u) {
        const int32_t divisor = (int32_t)count;
        output[0] = (int16_t)(totals[0] / divisor);
        output[1] = (int16_t)(totals[1] / divisor);
        output[2] = (int16_t)(totals[2] / divisor);
    }
    return true;
}

int16_t gomore_primitives_circular_positive_fill_mean(
    const int16_t *values, size_t ring_size, size_t cursor,
    size_t begin_distance, size_t end_distance) {
    if (values == NULL || ring_size == 0u || ring_size > 128u ||
            cursor >= ring_size || end_distance > ring_size ||
            begin_distance > end_distance) {
        return 0;
    }
    int32_t carried = 0;
    for (size_t distance = ring_size; distance > end_distance; --distance) {
        const size_t index = (cursor + ring_size - distance) % ring_size;
        if (values[index] > 0) {
            carried = values[index];
        }
    }
    int32_t total = 0;
    for (size_t distance = end_distance;; --distance) {
        const size_t index = (cursor + ring_size - distance) % ring_size;
        if (values[index] > 0) {
            carried = values[index];
        }
        total += carried;
        if (distance == begin_distance) {
            break;
        }
    }
    const size_t sample_count = end_distance - begin_distance + 1u;
    return (int16_t)(total / (int32_t)sample_count);
}

bool gomore_primitives_locomotion_crossing_wrapper(
    const int16_t baseline_ring[8], int32_t baseline_cursor,
    const uint16_t *samples, size_t sample_count,
    float *mode2_output, float *mode1_output,
    gomore_primitives_locomotion_crossing_estimate_fn estimate) {
    if (baseline_ring == NULL || baseline_cursor < 0 ||
            baseline_cursor >= 8 || samples == NULL || sample_count < 200u ||
            mode2_output == NULL || mode1_output == NULL || estimate == NULL) {
        return false;
    }
    const int16_t baseline = gomore_primitives_circular_positive_fill_mean(
        baseline_ring, 8u, (size_t)baseline_cursor, 1u, 8u);
    float mode2 = 0.0f;
    float mode1 = 0.0f;
    if (!estimate(samples, 200u, baseline, 2u, &mode2) ||
            !estimate(samples, 200u, baseline, 1u, &mode1)) {
        return false;
    }
    if (float_bits(mode2) + UINT32_C(0xBD900000) <=
            UINT32_C(0x01000000)) {
        *mode2_output = mode2;
    } else {
        *mode2_output = 0.0f;
    }
    if (float_bits(mode1) + UINT32_C(0xBD900000) <=
            UINT32_C(0x01000000)) {
        *mode1_output = mode1;
    } else {
        *mode1_output = 0.0f;
    }
    return true;
}

static int32_t crossing_signed_u32(uint32_t value) {
    return value <= (uint32_t)INT32_MAX
        ? (int32_t)value
        : (int32_t)((int64_t)value - INT64_C(4294967296));
}

static uint32_t crossing_integer_square_root(uint32_t value) {
    uint32_t root = 0u;
    uint32_t bit = UINT32_C(1) << 30u;
    while (bit > value) {
        bit >>= 2u;
    }
    while (bit != 0u) {
        if (value >= root + bit) {
            value -= root + bit;
            root = (root >> 1u) + bit;
        } else {
            root >>= 1u;
        }
        bit >>= 2u;
    }
    return root;
}

static void crossing_sort_u8(uint8_t *values, size_t count) {
    for (size_t index = 1u; index < count; ++index) {
        const uint8_t selected = values[index];
        size_t destination = index;
        while (destination > 0u &&
                values[destination - 1u] > selected) {
            values[destination] = values[destination - 1u];
            --destination;
        }
        values[destination] = selected;
    }
}

bool gomore_primitives_locomotion_crossing_period_estimate(
    const uint16_t *samples, size_t sample_count, int16_t baseline,
    uint32_t mode, float *output) {
    if (samples == NULL || sample_count < 200u || output == NULL ||
            (mode != 1u && mode != 2u)) {
        return false;
    }

    const int32_t long_length = mode == 1u ? 20 : 12;
    const int32_t short_length = mode == 1u ? 10 : 6;
    const int32_t long_half = long_length / 2;
    const int32_t short_half = short_length / 2;
    const float minimum_interval = mode == 1u ? 20.0f : 6.25f;
    const int32_t maximum_interval = mode == 1u ? 50 : 25;

    uint32_t square_sum = 0u;
    for (size_t index = 0u; index < 200u; ++index) {
        const int32_t centered = (int32_t)samples[index] - (int32_t)baseline;
        square_sum += (uint32_t)centered * (uint32_t)centered;
    }
    const int32_t signed_square_sum = crossing_signed_u32(square_sum);
    int32_t scale = 0;
    if (signed_square_sum > 0) {
        scale = (int32_t)crossing_integer_square_root(
            (uint32_t)(signed_square_sum / 200));
    }

    int32_t input_history[4] = {0, 0, 0, 0};
    int32_t output_history[4] = {0, 0, 0, 0};
    int32_t filtered[200];
    for (size_t index = 0u; index < 200u; ++index) {
        int32_t normalized = 0;
        if (scale != 0) {
            normalized = ((int32_t)samples[index] - (int32_t)baseline) *
                1000 / scale;
        }
        filtered[index] = gomore_primitives_integer_iir4_update(
            normalized, input_history, output_history, (int32_t)mode);
    }

    uint8_t intervals[80] = {0u};
    size_t interval_count = 0u;
    uint8_t maximum_pair[2] = {0u, 0u};
    uint8_t minimum_pair[2] = {0u, 0u};
    bool transition_initialized = false;
    float transition_estimate = -1.0f;
    int32_t previous_maximum_index = -1;
    int32_t previous_minimum_index = -1;
    int32_t previous_maximum_value = -1;
    int32_t previous_minimum_value = -1;
    int32_t selected_index = 0;
    int32_t selected_value = filtered[0];
    int32_t interval = -1;
    bool previous_regime = false;

    for (int32_t sample = 0; sample < 200; ++sample) {
        uint32_t long_sum = 0u;
        for (int32_t offset = -long_half;
                offset < long_length - long_half; ++offset) {
            int32_t source = sample + offset;
            if (source < 0) {
                source = 0;
            } else if (source >= 200) {
                source = 199;
            }
            long_sum += (uint32_t)filtered[source];
        }
        uint32_t short_sum = 0u;
        for (int32_t offset = -short_half;
                offset < short_length - short_half; ++offset) {
            int32_t source = sample + offset;
            if (source < 0) {
                source = 0;
            } else if (source >= 200) {
                source = 199;
            }
            short_sum += (uint32_t)filtered[source];
        }
        const bool regime =
            crossing_signed_u32(long_sum) / long_length <
            crossing_signed_u32(short_sum) / short_length;
        const int32_t current_value = filtered[sample];
        if (sample == 0) {
            selected_index = 0;
            selected_value = current_value;
        } else if (regime == previous_regime) {
            if ((regime && selected_value < current_value) ||
                    (!regime && current_value < selected_value)) {
                selected_index = sample;
                selected_value = current_value;
            }
        } else {
            uint8_t *pair = minimum_pair;
            float shape_first = 0.0f;
            float shape_second = 0.0f;
            bool has_new_interval = false;
            int32_t raw_interval = interval;
            if (previous_regime) {
                pair = maximum_pair;
                if (previous_maximum_index > 0) {
                    interval = selected_index - previous_maximum_index;
                    raw_interval = interval;
                    shape_first = (float)(selected_value -
                        previous_minimum_value);
                    shape_second = (float)(previous_maximum_value -
                        previous_minimum_value);
                    has_new_interval = true;
                }
                previous_maximum_index = selected_index;
                previous_maximum_value = selected_value;
            } else {
                if (previous_minimum_index > 0) {
                    interval = selected_index - previous_minimum_index;
                    raw_interval = interval;
                    shape_first = (float)(previous_maximum_value -
                        selected_value);
                    shape_second = (float)(previous_maximum_value -
                        previous_minimum_value);
                    has_new_interval = true;
                }
                previous_minimum_index = selected_index;
                previous_minimum_value = selected_value;
            }
            if (mode == 1u && has_new_interval) {
                gomore_primitives_locomotion_transition_state state = {
                    .accumulated = (uint32_t)interval,
                    .initialized = transition_initialized,
                    .estimate = transition_estimate,
                };
                bool updated = false;
                if (!gomore_primitives_locomotion_transition_accumulate(
                        &state, minimum_interval * 0.8f,
                        pair[0], pair[1], shape_first, shape_second,
                        &updated)) {
                    return false;
                }
                interval = (int32_t)state.accumulated;
                transition_initialized = state.initialized;
                transition_estimate = state.estimate;
                (void)updated;
            }
            if (has_new_interval) {
                pair[0] = pair[1];
                pair[1] = (uint8_t)raw_interval;
            }
            if ((float)interval >= minimum_interval &&
                    interval <= maximum_interval && interval_count < 80u) {
                intervals[interval_count++] = (uint8_t)interval;
            }
            selected_index = sample;
            selected_value = current_value;
        }
        previous_regime = regime;
    }

    if (transition_initialized && interval_count > 2u) {
        crossing_sort_u8(intervals, interval_count);
        size_t remove_count = 0u;
        const int16_t cutoff = (int16_t)(transition_estimate * 70.0f);
        while (remove_count < interval_count &&
                (int32_t)intervals[remove_count] * 100 < (int32_t)cutoff) {
            ++remove_count;
        }
        for (size_t index = 0u; index < interval_count - remove_count;
                ++index) {
            intervals[index] = intervals[index + remove_count];
        }
        interval_count -= remove_count;
    }

    *output = 0.0f;
    if (interval_count <= 2u) {
        return true;
    }
    crossing_sort_u8(intervals, interval_count);
    uint32_t median;
    if ((interval_count & 1u) == 0u) {
        median = ((uint32_t)intervals[interval_count / 2u - 1u] +
            (uint32_t)intervals[interval_count / 2u]) >> 1u;
    } else {
        median = intervals[(interval_count - 1u) / 2u];
    }
    const size_t first_quartile = interval_count / 4u;
    const size_t third_quartile = (interval_count * 3u) / 4u;
    float selected_period = (float)median;
    const float spread = (float)((int32_t)intervals[third_quartile] -
        (int32_t)intervals[first_quartile]) / selected_period;
    if ((int32_t)float_bits(spread) <
            (int32_t)UINT32_C(0x3E99999A)) {
        int16_t sum = 0;
        for (size_t index = first_quartile; index <= third_quartile;
                ++index) {
            sum = (int16_t)((uint16_t)sum + intervals[index]);
        }
        selected_period = (float)sum /
            (float)(third_quartile - first_quartile + 1u);
    }
    float estimate = (25.0f / selected_period) * 60.0f;
    if (mode == 1u) {
        estimate *= 2.0f;
    }
    *output = estimate;
    return true;
}

bool gomore_primitives_final_sleep_record_publish(
    bool enabled, uintptr_t record_binding,
    const gomore_primitives_final_sleep_providers *providers,
    bool *published, uint16_t *published_length) {
    if (providers == NULL || providers->lookup == NULL ||
            providers->log_modes == NULL ||
            providers->structured_log == NULL ||
            providers->secondary_log == NULL || providers->accept == NULL ||
            providers->publish == NULL || providers->release == NULL ||
            published == NULL || published_length == NULL) {
        return false;
    }
    *published = false;
    *published_length = 0u;
    if (!enabled || record_binding == 0u) {
        return true;
    }
    uint8_t *record = providers->lookup(record_binding);
    if (record == NULL) {
        return true;
    }

    const uint8_t record_type = record[0];
    const uint32_t start_timestamp = load_u32_le(&record[0x0Cu]);
    const uint32_t end_timestamp = load_u32_le(&record[0x10u]);
    const uint16_t compact_count = load_u16_le_early(&record[0x1Eu]);
    const uint32_t first_log_modes = providers->log_modes();
    if ((first_log_modes & UINT32_C(1)) != 0u ||
            (providers->log_modes() & UINT32_C(4)) != 0u) {
        providers->structured_log(
            record_type, start_timestamp, end_timestamp, compact_count);
    }
    if ((providers->log_modes() & UINT32_C(2)) != 0u) {
        providers->secondary_log(
            record_type, start_timestamp, end_timestamp, compact_count);
    }

    if (providers->accept(record)) {
        /* Stock applies UXTH after adding the 32-byte header. */
        const uint16_t payload_length =
            (uint16_t)(compact_count + UINT16_C(0x20));
        providers->publish(0x0Du, record, payload_length);
        *published = true;
        *published_length = payload_length;
    }
    providers->release(record);
    return true;
}

bool gomore_primitives_sleep_force_wake(
    bool mode_control_enabled,
    const gomore_primitives_sleep_force_wake_providers *providers,
    gomore_primitives_sleep_force_wake_status *status) {
    if (providers == NULL || providers->allocate == NULL ||
            providers->release == NULL || providers->prepare == NULL ||
            providers->set_mode == NULL || providers->dispatch == NULL ||
            providers->publish == NULL || status == NULL) {
        return false;
    }
    uint8_t *const record = providers->allocate(56u);
    if (record == NULL) {
        *status =
            GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_RECORD_ALLOCATION_FAILED;
        return true;
    }
    clear_bytes(record, 56u);
    providers->prepare(1u, record);
    if (mode_control_enabled) {
        providers->set_mode(4u, 0u);
    }
    if ((record[8] & UINT8_C(8)) != 0u) {
        uint32_t result_words[2] = {0u, 0u};
        uint8_t report[88];
        clear_bytes(report, sizeof(report));
        uint8_t *const timeline = providers->allocate(0xB40u);
        if (timeline == NULL) {
            providers->release(record);
            *status =
                GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_TIMELINE_ALLOCATION_FAILED;
            return true;
        }
        clear_bytes(timeline, 0xB40u);
        providers->dispatch(result_words, report, timeline);
        providers->publish(result_words, report);
        providers->release(timeline);
    }
    providers->release(record);
    *status = GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_COMPLETE;
    return true;
}

bool gomore_primitives_dormant_heart_rate_ratio_wrapper(
    void *state, size_t state_length, int32_t raw_heart_rate,
    gomore_primitives_integer_filter_update_fn filter_update,
    gomore_primitives_dormant_ratio_accumulate_fn ratio_accumulate,
    int32_t *filter_status) {
    if (state == NULL || state_length < 0x2DCu || filter_update == NULL ||
            ratio_accumulate == NULL || filter_status == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const uint16_t flags = load_u16_le_early(&bytes[0x56u]);
    int32_t filtered[2] = {0, 0};
    *filter_status = filter_update(
        &bytes[0x278u], raw_heart_rate, filtered, 1000u);
    const int32_t selected_heart_rate =
        *filter_status == 1 ? filtered[0] : raw_heart_rate;
    store_u32_le(&bytes[0x1Cu], (uint32_t)selected_heart_rate);

    gomore_primitives_dormant_ratio_input input = {
        .selected_heart_rate = (float)selected_heart_rate,
        .reserved_zero = 0.0f,
        .selected_speed = bits_float(load_u32_le(
            &bytes[(flags & UINT16_C(0x4203)) == 0u ? 0x24u : 0x2Cu])),
        .thresholds = (float *)(void *)&bytes[0x170u],
        .primary_sums = (float *)(void *)&bytes[0x1C0u],
        .primary_counts = (float *)(void *)&bytes[0x1D8u],
        .below_range_weight = 0.0f,
        .auxiliary_first = (float *)(void *)&bytes[0x1F0u],
        .auxiliary_second = (float *)(void *)&bytes[0x1F4u],
    };
    if ((flags & UINT16_C(0x4203)) == 0u &&
            (flags & UINT16_C(0x040C)) != 0u) {
        ratio_accumulate(state, &input);
    }
    return true;
}

static void dormant_ratio_reset_qualified(
    gomore_primitives_dormant_ratio_accumulator_state *state) {
    state->qualified_square_sum = 0.0f;
    state->qualified_heart_rate_mean = 0.0f;
    state->qualified_speed_mean = 0.0f;
    state->qualified_sample_count = 0.0f;
}

bool gomore_primitives_dormant_ratio_accumulator(
    gomore_primitives_dormant_ratio_accumulator_state *state,
    const gomore_primitives_dormant_ratio_input *input,
    gomore_primitives_float_binary_fn power) {
    if (state == NULL || input == NULL || power == NULL ||
            input->thresholds == NULL || input->primary_sums == NULL ||
            input->primary_counts == NULL) {
        return false;
    }

    const float all_count = state->all_sample_count;
    const float next_all_count = all_count + 1.0f;
    state->all_heart_rate_mean =
        (input->selected_heart_rate +
         state->all_heart_rate_mean * all_count) / next_all_count;
    state->all_sample_count = next_all_count;

    if ((int32_t)float_bits(input->selected_speed) <=
            INT32_C(0x40800000)) {
        return true;
    }

    const float below_range_weight = state->profile_flag == 0u
        ? bits_float(UINT32_C(0x3F9C28F6))
        : bits_float(UINT32_C(0x3FA8F5C3));
    if (!gomore_primitives_weighted_histogram6_accumulate(
            input->selected_heart_rate, input->selected_heart_rate,
            input->selected_speed, input->thresholds,
            input->primary_sums, input->primary_counts,
            below_range_weight)) {
        return false;
    }

    state->qualified_square_sum =
        power(input->selected_heart_rate, 2.0f) +
        state->qualified_square_sum;
    const float qualified_count = state->qualified_sample_count;
    const float next_qualified_count = qualified_count + 1.0f;
    state->qualified_heart_rate_mean =
        (input->selected_heart_rate +
         state->qualified_heart_rate_mean * qualified_count) /
        next_qualified_count;
    state->qualified_speed_mean =
        (input->selected_speed +
         state->qualified_speed_mean * qualified_count) /
        next_qualified_count;
    state->qualified_sample_count = next_qualified_count;

    const float dispersion = power(
        state->qualified_square_sum / next_qualified_count -
        power(state->qualified_heart_rate_mean, 2.0f),
        0.5f);
    const bool count_ready =
        (int32_t)float_bits(next_qualified_count) >=
        INT32_C(0x41F00000);
    const bool dispersion_high =
        (int32_t)float_bits(dispersion) > INT32_C(0x3F7FFFFF);
    if (!count_ready) {
        return true;
    }
    if (dispersion_high) {
        dormant_ratio_reset_qualified(state);
        return true;
    }
    if (state->all_heart_rate_mean <
            state->qualified_heart_rate_mean) {
        return gomore_primitives_weighted_histogram6_accumulate(
            state->qualified_heart_rate_mean,
            state->qualified_heart_rate_mean,
            state->qualified_speed_mean, input->thresholds,
            state->secondary_sums, state->secondary_counts, 1.0f);
    }
    dormant_ratio_reset_qualified(state);
    return true;
}

bool gomore_primitives_dormant_estimator_cycle(
    void *state, size_t state_length,
    gomore_primitives_dormant_cycle_input *input,
    const gomore_primitives_dormant_cycle_providers *providers,
    int32_t *result) {
    if (state == NULL || state_length < 0x328u || input == NULL ||
            input->auxiliary == NULL || providers == NULL ||
            providers->arctangent == NULL || providers->cosine == NULL ||
            providers->sine == NULL || providers->power == NULL ||
            providers->reduce == NULL || providers->finalize == NULL ||
            providers->filter_heart_rate == NULL ||
            providers->accumulate_ratio == NULL || result == NULL ||
            input->sample_index < 0) {
        return false;
    }
    uint8_t *bytes = state;
    store_u32_le(&bytes[0x24u], float_bits(input->selected_speed));
    store_u32_le(&bytes[0x2Cu], float_bits(input->auxiliary_speed));
    store_u32_le(&bytes[0x38u], float_bits(input->copied_auxiliary_1));
    store_u32_le(&bytes[0x3Cu], float_bits(input->copied_auxiliary_2));

    const uint16_t flags = load_u16_le_early(&bytes[0x56u]);
    float target = 0.0f;
    if ((flags & UINT16_C(0x1444)) != 0u) {
        if ((flags & UINT16_C(0x0004)) != 0u) {
            input->auxiliary->smoother_input = 0.0f;
        }
        float smoothed = 0.0f;
        uint8_t stable_or_clamped = 0u;
        (void)gomore_primitives_speed_smoother_update(
            (gomore_primitives_speed_smoother *)(void *)&bytes[0x2DCu],
            input->auxiliary->smoother_input, 1000u,
            &smoothed, &stable_or_clamped);
        (void)stable_or_clamped;
        store_u32_le(&bytes[0x34u], float_bits(smoothed));
        if (!gomore_primitives_dormant_speed_mode1_target_veneer(
                smoothed, bits_float(load_u32_le(&bytes[0x24u])),
                &bytes[0x2FCu], state_length - 0x2FCu,
                providers->power, providers->reduce, providers->finalize,
                &target)) {
            return false;
        }
        store_u32_le(&bytes[0x24u], float_bits(target));
    } else if ((flags & UINT16_C(0x0008)) != 0u) {
        if (!gomore_primitives_dormant_speed_mode0_target_veneer(
                input->auxiliary->mode0_first_input,
                bits_float(load_u32_le(&bytes[0x24u])),
                &bytes[0x2FCu], state_length - 0x2FCu,
                providers->arctangent, providers->cosine, providers->sine,
                providers->power, providers->reduce, providers->finalize,
                &target)) {
            return false;
        }
        store_u32_le(&bytes[0x24u], float_bits(target));
    }

    target = gomore_primitives_speed_gate(
        bits_float(load_u32_le(&bytes[0x24u])),
        bits_float(load_u32_le(&bytes[0x28u])),
        (float *)(void *)&bytes[0x184u], input->sample_index, flags);
    store_u32_le(&bytes[0x24u], float_bits(target));
    target = gomore_primitives_rolling_mean5_update(
        target, (float *)(void *)&bytes[0x184u],
        (uint32_t)input->sample_index);
    store_u32_le(&bytes[0x24u], float_bits(target));

    if (input->sample_index < 30) {
        if (bytes[0x60u] == 0u &&
                (input->raw_heart_rate < 36 ||
                 input->raw_heart_rate >= 250)) {
            store_u16_le_early(&bytes[0x52u], UINT16_C(0xFC08));
            *result = -1016;
            return true;
        }
        if (bytes[0x60u] == 0u) {
            bytes[0x60u] = 1u;
        }
    }
    if (input->sample_index > 0 && input->raw_heart_rate == 0) {
        input->raw_heart_rate = (int32_t)load_u32_le(&bytes[0x20u]);
    }
    int32_t filter_status = 0;
    if (!gomore_primitives_dormant_heart_rate_ratio_wrapper(
            state, state_length, input->raw_heart_rate,
            providers->filter_heart_rate, providers->accumulate_ratio,
            &filter_status)) {
        return false;
    }
    (void)filter_status;
    store_u32_le(&bytes[0x20u], load_u32_le(&bytes[0x1Cu]));
    store_u32_le(&bytes[0x28u], load_u32_le(&bytes[0x24u]));
    store_u32_le(&bytes[0x30u], load_u32_le(&bytes[0x2Cu]));
    store_u16_le_early(&bytes[0x52u], 0u);
    *result = 0;
    return true;
}

bool gomore_primitives_dormant_root_reduce(
    float primary, float secondary, float auxiliary,
    void *state, size_t state_length, int32_t mode,
    gomore_primitives_float_unary_fn arctangent,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_binary_fn power,
    float *output) {
    if (state == NULL || state_length < 0x26u ||
            arctangent == NULL || cosine == NULL || power == NULL ||
            output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const float state_first = bits_float(load_u32_le(&bytes[0]));
    const float state_second = bits_float(load_u32_le(&bytes[4]));
    const uint16_t flags = load_u16_le_early(&bytes[0x24u]);
    float projected_primary = primary;
    float retained_secondary = secondary;

    if (secondary != 0.0f) {
        float angle_input = 0.0f;
        if (primary > 0.0f) {
            angle_input = secondary / primary;
        }
        const float angle = arctangent(angle_input);
        if (cosine(angle) != 0.0f) {
            projected_primary = primary / cosine(angle);
        } else {
            projected_primary = 0.0f;
        }
        const float threshold = gomore_primitives_energy_core(
            state, state_length, projected_primary, auxiliary) * 2.0f;
        double absolute_secondary = (double)secondary;
        if (absolute_secondary < 0.0) {
            absolute_secondary = -absolute_secondary;
        }
        if (absolute_secondary < (double)threshold) {
            retained_secondary = 0.0f;
        }
    }

    float baseline;
    if ((flags & UINT16_C(0x0440)) != 0u) {
        const float baseline_input = bits_float(UINT32_C(0x3FA147AE));
        const float adjusted_auxiliary =
            gomore_primitives_clamped_rational(
                baseline_input, state_first);
        baseline = gomore_primitives_speed_dynamics_baseline(
            baseline_input, adjusted_auxiliary,
            state_first, state_second, flags, power);
    } else {
        baseline = gomore_primitives_speed_dynamics_baseline(
            1.0f, bits_float(UINT32_C(0x43250000)),
            state_first, state_second, flags, power);
    }

    float secondary_term = state_second *
        bits_float(UINT32_C(0x411CCCCD));
    secondary_term *= retained_secondary;
    float kinetic = power(projected_primary, 2.0f);
    kinetic *= state_second;
    kinetic *= 0.5f;

    float result;
    if ((int32_t)float_bits(primary) <= INT32_C(0x3F800000)) {
        result = secondary_term + baseline * primary;
        if (result <= 0.0f) {
            result = 0.0f;
        }
    } else {
        float kinetic_weight = 1.0f;
        const float previous_kinetic =
            bits_float(load_u32_le(&bytes[0x10u]));
        if (kinetic < previous_kinetic) {
            kinetic_weight = 0.1f;
        }
        float kinetic_delta = kinetic - previous_kinetic;
        if (kinetic_delta < 0.0f) {
            kinetic_delta = -kinetic_delta;
        }
        kinetic_delta *= kinetic_weight;
        if (kinetic_delta < baseline) {
            kinetic_delta = 0.0f;
        }

        const float mode_term = mode != 0
            ? gomore_primitives_cubic_scale(projected_primary) : 0.0f;
        const float scaled = gomore_primitives_energy_scaled(
            state, state_length, projected_primary, auxiliary);
        const float difference =
            gomore_primitives_activity_scaled_quadratic_difference(
                projected_primary,
                bits_float(load_u32_le(&bytes[0x08u])),
                auxiliary, state_second, power);
        float total = kinetic_delta + secondary_term;
        total += scaled;
        total += difference;
        total += mode_term;
        result = gomore_primitives_round_decimal_places(
            total, 3.0f, power);
        if (result > 0.0f) {
            result = gomore_primitives_round_decimal_places(
                total, 3.0f, power);
        } else {
            result = 0.0f;
        }
        store_u32_le(&bytes[0x10u], float_bits(kinetic));
        store_u32_le(&bytes[0x08u], float_bits(projected_primary));
    }

    *output = result * bits_float(UINT32_C(0x3F0DD2F2));
    return true;
}

bool gomore_primitives_dormant_speed_root_build(
    float primary, float auxiliary, void *state, size_t state_length,
    int32_t mode, gomore_primitives_float_binary_fn power,
    gomore_primitives_quadratic_dispatch_fn solve_quadratic,
    gomore_primitives_cubic_dispatch_fn solve_cubic) {
    if (state == NULL || state_length < 0x24u || power == NULL ||
            solve_quadratic == NULL || solve_cubic == NULL) {
        return false;
    }
    const uint8_t *bytes = state;
    const float state_first = bits_float(load_u32_le(&bytes[0]));
    const float state_second = bits_float(load_u32_le(&bytes[4]));
    const float coefficient_a = mode == 0
        ? 0.0f : bits_float(UINT32_C(0x3E1704FF));
    const float coefficient_b =
        state_second * bits_float(UINT32_C(0x3A252696)) * auxiliary;
    const float coefficient_c =
        bits_float(UINT32_C(0x39B7CCB5)) * auxiliary *
        state_second * state_first;
    const float auxiliary_squared = power(auxiliary, 2.0f);
    float coefficient_d_first =
        bits_float(UINT32_C(0x3D5385D9)) * auxiliary;
    coefficient_d_first *= state_second;
    coefficient_d_first *= state_first;
    float coefficient_d_second =
        auxiliary_squared * bits_float(UINT32_C(0x39770E14));
    coefficient_d_second *= state_second;
    coefficient_d_second *= state_first;
    float coefficient_d = coefficient_d_first - coefficient_d_second;
    coefficient_d -= primary;
    if (mode == 0) {
        solve_quadratic(
            coefficient_b, coefficient_c, coefficient_d, state);
    } else {
        solve_cubic(
            coefficient_a, coefficient_b, coefficient_c,
            coefficient_d, state);
    }
    return true;
}

bool gomore_primitives_dormant_alternate_root_solve(
    float primary, float auxiliary, void *state, size_t state_length,
    int32_t mode,
    gomore_primitives_quadratic_dispatch_fn solve_quadratic,
    gomore_primitives_cubic_dispatch_fn solve_cubic,
    float *output) {
    if (state == NULL || state_length < 0x24u ||
            solve_quadratic == NULL || solve_cubic == NULL ||
            output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const float state_first = bits_float(load_u32_le(&bytes[0]));
    const float state_second = bits_float(load_u32_le(&bytes[4]));
    const float target =
        gomore_primitives_rational_transform(auxiliary, state_first);
    const float coefficient_b =
        state_second * bits_float(UINT32_C(0x3A252696)) * auxiliary;
    float coefficient_d =
        state_first * bits_float(UINT32_C(0x3BF76450));
    coefficient_d *= state_second;
    coefficient_d *= auxiliary;
    coefficient_d -= primary;
    if (mode == 0) {
        solve_quadratic(coefficient_b, 0.0f, coefficient_d, state);
    } else {
        solve_cubic(bits_float(UINT32_C(0x3E1704FF)), coefficient_b,
                    0.0f, coefficient_d, state);
    }

    float selected = gomore_primitives_nearest_nonzero3(
        target, (const float *)(const void *)&bytes[0x18u]);
    if ((int32_t)float_bits(selected) > INT32_C(0x3FA00000)) {
        selected *= bits_float(UINT32_C(0x3F333333));
    }
    *output = selected > 0.0f ? selected : 0.0f;
    return true;
}

bool gomore_primitives_dormant_root_resolve(
    float primary, float auxiliary, void *state, size_t state_length,
    int32_t mode, gomore_primitives_float_binary_fn power,
    gomore_primitives_quadratic_dispatch_fn solve_quadratic,
    gomore_primitives_cubic_dispatch_fn solve_cubic,
    float *output) {
    if (state == NULL || state_length < 0x26u || power == NULL ||
            solve_quadratic == NULL || solve_cubic == NULL ||
            output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const float normalized =
        primary / bits_float(UINT32_C(0x3F0DD2F2));
    const uint16_t flags = load_u16_le_early(&bytes[0x24u]);
    float result = 0.0f;

    if ((flags & UINT16_C(0x0440)) != 0u) {
        const float target = gomore_primitives_rational_transform(
            auxiliary, bits_float(load_u32_le(&bytes[0])));
        if ((int32_t)float_bits(target) < INT32_C(0x3FA00000)) {
            if (!gomore_primitives_dormant_alternate_root_solve(
                    normalized, auxiliary, state, state_length, mode,
                    solve_quadratic, solve_cubic, &result)) {
                return false;
            }
        } else {
            if (!gomore_primitives_dormant_speed_root_build(
                    normalized, auxiliary, state, state_length, mode,
                    power, solve_quadratic, solve_cubic)) {
                return false;
            }
            result = gomore_primitives_nearest_nonzero3(
                target, (const float *)(const void *)&bytes[0x18u]);
        }
        *output = result;
        return true;
    }

    const float baseline = gomore_primitives_speed_dynamics_baseline(
        1.0f, auxiliary,
        bits_float(load_u32_le(&bytes[0])),
        bits_float(load_u32_le(&bytes[4])), flags, power);
    if (normalized < baseline) {
        if (baseline != 0.0f) {
            result = normalized / baseline;
            if (!(result > 0.0f)) {
                result = 0.0f;
            }
        }
        *output = result;
        return true;
    }

    if (!gomore_primitives_dormant_speed_root_build(
            normalized, auxiliary, state, state_length, mode,
            power, solve_quadratic, solve_cubic)) {
        return false;
    }
    const float first = bits_float(load_u32_le(&bytes[0x18u]));
    const float second = bits_float(load_u32_le(&bytes[0x1Cu]));
    const float third = bits_float(load_u32_le(&bytes[0x20u]));
    if (first != 0.0f || second != 0.0f || third != 0.0f) {
        if (second == 0.0f && third == 0.0f) {
            result = first;
        } else if (mode == 0) {
            result = (first + second) * 0.5f;
        } else {
            result = (first + second + third) / 3.0f;
        }
    }
    if (!(result > 0.0f)) {
        result = 0.0f;
    }
    *output = result;
    return true;
}

bool gomore_primitives_dormant_speed_mode1_target_update(
    float first_input, float selected_speed,
    void *state, size_t state_length, int32_t mode,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output) {
    if (state == NULL || state_length < 0x2Cu || power == NULL ||
            reduce == NULL || finalize == NULL || output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const float state_first = bits_float(load_u32_le(&bytes[0]));
    const float state_second = bits_float(load_u32_le(&bytes[4]));
    const float scale = bits_float(UINT32_C(0x40666666));
    const float primary = selected_speed / scale;
    float auxiliary = bits_float(UINT32_C(0x43250000));
    const uint16_t flags = load_u16_le_early(&bytes[0x24u]);
    if ((flags & UINT16_C(0x0440)) != 0u) {
        auxiliary = gomore_primitives_clamped_rational(
            primary, state_first);
    }
    store_u32_le(&bytes[0x18u], 0u);
    store_u32_le(&bytes[0x1Cu], 0u);
    store_u32_le(&bytes[0x20u], 0u);

    float secondary = 0.0f;
    if (bytes[0x26u] != 0u) {
        secondary = first_input -
            bits_float(load_u32_le(&bytes[0x0Cu]));
    } else {
        bytes[0x26u] = 1u;
        float power_history = power(primary, 2.0f);
        power_history *= state_second;
        power_history *= 0.5f;
        store_u32_le(&bytes[0x10u], float_bits(power_history));
        store_u32_le(&bytes[0x08u], float_bits(primary));
    }
    store_u32_le(&bytes[0x0Cu], float_bits(first_input));
    const float reduced = reduce(
        primary, secondary, auxiliary, state, mode);
    float result = finalize(reduced, auxiliary, state, mode) * scale;
    if (result < 0.0f) {
        result = 0.0f;
    }
    *output = result;
    return true;
}

bool gomore_primitives_dormant_speed_mode1_target_veneer(
    float first_input, float selected_speed,
    void *state, size_t state_length,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output) {
    return gomore_primitives_dormant_speed_mode1_target_update(
        first_input, selected_speed, state, state_length, 1,
        power, reduce, finalize, output);
}

bool gomore_primitives_dormant_speed_mode0_target_update(
    float first_input, float selected_speed,
    void *state, size_t state_length, int32_t mode,
    gomore_primitives_float_unary_fn arctangent,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output) {
    if (state == NULL || state_length < 0x2Cu || arctangent == NULL ||
            cosine == NULL || sine == NULL || power == NULL ||
            reduce == NULL || finalize == NULL || output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const float state_first = bits_float(load_u32_le(&bytes[0]));
    const float state_second = bits_float(load_u32_le(&bytes[4]));
    const float scale = bits_float(UINT32_C(0x40666666));
    const float primary = selected_speed / scale;
    float auxiliary = bits_float(UINT32_C(0x43250000));
    const uint16_t flags = load_u16_le_early(&bytes[0x24u]);
    if ((flags & UINT16_C(0x0440)) != 0u) {
        auxiliary = gomore_primitives_clamped_rational(
            primary, state_first);
    }
    store_u32_le(&bytes[0x18u], 0u);
    store_u32_le(&bytes[0x1Cu], 0u);
    store_u32_le(&bytes[0x20u], 0u);

    const float angle = arctangent(
        first_input / bits_float(UINT32_C(0x42C80000)));
    if (bytes[0x26u] == 0u) {
        bytes[0x26u] = 1u;
        const float initial_primary = primary * cosine(angle);
        store_u32_le(&bytes[0x08u], float_bits(initial_primary));
        float power_history = power(initial_primary, 2.0f);
        power_history *= state_second;
        power_history *= 0.5f;
        store_u32_le(&bytes[0x10u], float_bits(power_history));
    }
    const float projected_primary = primary * cosine(angle);
    const float projected_secondary = primary * sine(angle);
    const float reduced = reduce(
        projected_primary, projected_secondary, auxiliary, state, mode);
    float result = finalize(reduced, auxiliary, state, mode) * scale;
    if (result < 0.0f) {
        result = 0.0f;
    }
    *output = result;
    return true;
}

bool gomore_primitives_dormant_speed_mode0_target_veneer(
    float first_input, float selected_speed,
    void *state, size_t state_length,
    gomore_primitives_float_unary_fn arctangent,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output) {
    return gomore_primitives_dormant_speed_mode0_target_update(
        first_input, selected_speed, state, state_length, 0,
        arctangent, cosine, sine, power, reduce, finalize, output);
}

bool gomore_primitives_sleep_graph_family_dispatch(
    void *state, size_t state_length, uint32_t arena_seed,
    const uint8_t dimensions_by_family[24], size_t dimensions_length,
    uint32_t recurrent_executor, uint32_t softmax_executor,
    gomore_primitives_sleep_graph_zero_build_fn build_zero,
    gomore_primitives_sleep_graph_nonzero_build_fn build_nonzero,
    gomore_primitives_sleep_graph_recurrent_construct_fn construct_recurrent,
    gomore_primitives_sleep_graph_dense_construct_fn construct_dense) {
    if (state == NULL || state_length < 0x23Cu ||
            dimensions_by_family == NULL || dimensions_length < 24u ||
            build_zero == NULL || build_nonzero == NULL ||
            construct_recurrent == NULL || construct_dense == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const uint32_t family = load_u32_le(&bytes[0]);
    if (family > 2u) {
        return false;
    }
    uint32_t arena_cursor = family == 0u
        ? build_zero(&bytes[4])
        : build_nonzero((int32_t)family, &bytes[4], arena_seed);
    uint8_t descriptor[24];
    construct_recurrent(descriptor, 8u, 4u, &arena_cursor);
    for (size_t index = 0u; index < sizeof(descriptor); ++index) {
        bytes[0x1BCu + index] = descriptor[index];
    }
    store_u32_le(&bytes[0x1D4u], recurrent_executor);

    const uint8_t *dimensions =
        &dimensions_by_family[(size_t)family * 8u];
    construct_recurrent(
        descriptor, dimensions[0], dimensions[1], &arena_cursor);
    for (size_t index = 0u; index < sizeof(descriptor); ++index) {
        bytes[0x1D8u + index] = descriptor[index];
    }
    construct_recurrent(
        descriptor, dimensions[2], dimensions[3], &arena_cursor);
    for (size_t index = 0u; index < sizeof(descriptor); ++index) {
        bytes[0x1F0u + index] = descriptor[index];
    }
    construct_dense(
        descriptor, dimensions[4], dimensions[5], 1u, 1u,
        &arena_cursor);
    for (size_t index = 0u; index < sizeof(descriptor); ++index) {
        bytes[0x208u + index] = descriptor[index];
    }
    construct_dense(
        descriptor, dimensions[6], dimensions[7], 1u, 0u,
        &arena_cursor);
    for (size_t index = 0u; index < sizeof(descriptor); ++index) {
        bytes[0x220u + index] = descriptor[index];
    }
    if (family == 2u) {
        store_u32_le(&bytes[0x238u], softmax_executor);
    }
    return true;
}

static int32_t topic_signed_u16(uint16_t value) {
    return value < UINT16_C(0x8000)
        ? (int32_t)value
        : (int32_t)value - INT32_C(0x10000);
}

bool gomore_primitives_topic_accelerometer_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *batch, size_t batch_length) {
    if (state == NULL || batch == NULL ||
            batch_length != GOMORE_PRIMITIVES_TOPIC_ACC_BATCH_BYTES) {
        return false;
    }
    uint8_t count = batch[GOMORE_PRIMITIVES_TOPIC_ACC_COUNT_OFFSET];
    if (count > GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT) {
        count = GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT;
    }
    state->accelerometer_sample_count = count;
    const float scale = bits_float(UINT32_C(0x3F7A0000));
    for (size_t index = 0u; index < count; ++index) {
        const uint8_t *sample = &batch[index * 6u];
        const int32_t source_x = topic_signed_u16(
            load_u16_le_early(&sample[0]));
        const int32_t source_y = topic_signed_u16(
            load_u16_le_early(&sample[2]));
        const int32_t source_z = topic_signed_u16(
            load_u16_le_early(&sample[4]));
        state->accelerometer_axes[0][index] = -(float)source_y * scale;
        state->accelerometer_axes[1][index] = (float)source_x * scale;
        state->accelerometer_axes[2][index] = (float)source_z * scale;
    }
    state->ready_flags |= GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER;
    return true;
}

bool gomore_primitives_topic_raw_optical_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *packet, size_t packet_length) {
    if (state == NULL || packet == NULL || packet_length < 1u) {
        return false;
    }
    uint8_t count = packet[0];
    if (count > GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT) {
        count = GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT;
    }
    const size_t required = 4u + (size_t)count * 4u;
    if (packet_length < required) {
        return false;
    }
    state->raw_optical_sample_count = count;
    for (size_t index = 0u; index < count; ++index) {
        state->raw_optical[index] = (float)load_u32_le(
            &packet[4u + index * 4u]);
    }
    state->ready_flags |= GOMORE_PRIMITIVES_TOPIC_READY_RAW_OPTICAL;
    return true;
}

bool gomore_primitives_topic_heart_rate_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *packet, size_t packet_length) {
    if (state == NULL || packet == NULL || packet_length < 1u) {
        return false;
    }
    state->direct_heart_rate = (float)packet[0];
    state->ready_flags |= GOMORE_PRIMITIVES_TOPIC_READY_HEART_RATE;
    return true;
}

bool gomore_primitives_topic_hrv_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *packet, size_t packet_length) {
    if (state == NULL || packet == NULL ||
            packet_length <= GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET) {
        return false;
    }
    uint8_t count = packet[GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET];
    if (count > GOMORE_PRIMITIVES_TOPIC_HRV_LIMIT) {
        count = GOMORE_PRIMITIVES_TOPIC_HRV_LIMIT;
    }
    if (packet_length < (size_t)count * 2u) {
        return false;
    }
    clear_bytes((uint8_t *)state->hrv_auxiliary,
                sizeof(state->hrv_auxiliary));
    for (size_t index = 0u; index < count; ++index) {
        state->hrv_auxiliary[index] = load_u16_le_early(
            &packet[index * 2u]);
    }
    state->hrv_auxiliary_count = count;
    return true;
}

bool gomore_primitives_topic_update_take_ready(
    gomore_primitives_topic_input_state *state,
    bool accelerometer_required, bool raw_optical_required) {
    if (state == NULL ||
            (!accelerometer_required && !raw_optical_required)) {
        return false;
    }
    uint8_t required = 0u;
    if (accelerometer_required) {
        required |= GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER;
    }
    if (raw_optical_required) {
        required |= GOMORE_PRIMITIVES_TOPIC_READY_RAW_OPTICAL;
    }
    if ((state->ready_flags & required) != required) {
        return false;
    }
    state->ready_flags = 0u;
    return true;
}

void gomore_primitives_topic_update_complete(
    gomore_primitives_topic_input_state *state, bool succeeded) {
    if (state != NULL && succeeded) {
        state->accelerometer_sample_count = 0u;
        state->raw_optical_sample_count = 0u;
    }
}

bool gomore_primitives_host_input_adapter_update(
    void *engine, size_t engine_length,
    const gomore_primitives_host_input *input,
    uint32_t previous_update_timestamp,
    float raw_optical_output[25], float accelerometer_outputs[3][25],
    const gomore_primitives_host_input_bindings *bindings,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger,
    gomore_primitives_input_adapter_core_fn update_core) {
    if (engine == NULL || engine_length < 0x39D8u || input == NULL ||
            raw_optical_output == NULL || accelerometer_outputs == NULL ||
            bindings == NULL || resample == NULL || apply_filter == NULL ||
            update_core == NULL ||
            (input->raw_optical_channel_count != 0u &&
             input->raw_optical_samples == NULL) ||
            (input->accelerometer_sample_count != 0u &&
             (input->accelerometer_axes[0] == NULL ||
              input->accelerometer_axes[1] == NULL ||
              input->accelerometer_axes[2] == NULL))) {
        return false;
    }
    uint8_t *bytes = engine;
    store_u32_le(&bytes[0x190u], input->unix_seconds);
    store_u16_le_early(
        &bytes[0x18Cu], (uint16_t)input->timezone_offset_minutes);
    store_u32_le(
        &bytes[0x170u], bindings->raw_optical_output_binding);

    const float *raw_sources[1] = {input->raw_optical_samples};
    uint8_t raw_failed = 0u;
    uint32_t raw_status = 0u;
    if (!gomore_primitives_ppg_resample25(
            bytes, engine_length, raw_sources, 1u,
            (int32_t)input->raw_optical_channel_count,
            (int32_t)input->raw_optical_sample_count,
            raw_optical_output, &raw_failed, &raw_status,
            resample, apply_filter, logger)) {
        return false;
    }
    (void)raw_status;
    bytes[0x174u] = raw_failed;
    if (input->wear_state_is_unknown != 0u) {
        bytes[0x174u] = 1u;
    }
    bytes[0x175u] = input->wear_state_is_unknown;
    store_u32_le(&bytes[0x178u], input->raw_optical_binding);
    store_u16_le_early(
        &bytes[0x17Cu], (uint16_t)input->raw_optical_sample_count);
    bytes[0x17Eu] = input->raw_optical_channel_count > 1u
        ? 1u : input->raw_optical_channel_count;
    bytes[0x17Fu] = input->raw_optical_channel_count == 0u ||
        input->raw_optical_sample_count == 0u ? 1u : 0u;

    float *accelerometer_destinations[3] = {
        accelerometer_outputs[0],
        accelerometer_outputs[1],
        accelerometer_outputs[2],
    };
    for (size_t axis = 0u; axis < 3u; ++axis) {
        store_u32_le(&bytes[0x1C8u + axis * 4u],
                     bindings->accelerometer_output_bindings[axis]);
    }
    uint8_t accelerometer_failed = 0u;
    uint32_t accelerometer_status = 0u;
    if (!gomore_primitives_accelerometer_resample25(
            bytes, engine_length, input->accelerometer_axes, 3u,
            (int32_t)input->accelerometer_sample_count,
            accelerometer_destinations, 3u,
            &accelerometer_failed, &accelerometer_status,
            resample, apply_filter, logger)) {
        return false;
    }
    (void)accelerometer_status;
    bytes[0x1D4u] = accelerometer_failed;
    store_u32_le(&bytes[0x16Cu], float_bits(input->direct_heart_rate));
    store_u32_le(&bytes[0x150u], input->legacy_zero_word);
    if (load_u32_le(&bytes[0x39D4u]) == 2u) {
        bytes[0x2F5u] = input->mode2_legacy_byte0;
        bytes[0x2F6u] = input->mode2_legacy_byte1;
    }
    update_core(
        &bytes[0x140u], input->unix_seconds - previous_update_timestamp);
    return true;
}

bool gomore_primitives_sensor_update_orchestrate(
    const void *context,
    gomore_primitives_sensor_update_state *state,
    const gomore_primitives_host_input *input,
    const gomore_primitives_sensor_update_configuration *configuration,
    const gomore_primitives_sensor_update_providers *providers,
    int32_t *result_status) {
    if (state == NULL || input == NULL || configuration == NULL ||
            providers == NULL || result_status == NULL ||
            providers->log_error == NULL || providers->apply == NULL ||
            providers->snapshot == NULL ||
            (configuration->diagnostics_enabled &&
             providers->diagnose == NULL)) {
        return false;
    }
    if (configuration->diagnostics_enabled) {
        providers->diagnose(context, input);
    }
    if (state->initialization_status < 0) {
        *result_status = state->initialization_status;
        return true;
    }

    int32_t status = gomore_primitives_runtime_version_validate(
        input->unix_seconds, false, configuration->validation_enabled,
        configuration->configured_timestamp_limit,
        configuration->runtime_present,
        configuration->configured_version,
        configuration->runtime_version);
    if (status < 0) {
        providers->log_error(context, status);
        *result_status = status;
        return true;
    }

    const uint32_t timestamp = gomore_primitives_clamp_hysteresis(
        input->unix_seconds, state->previous_timestamp);
    if (state->previous_timestamp == 0u) {
        state->previous_timestamp = timestamp - 1u;
    }
    if (state->previous_timestamp >= timestamp) {
        status = -4;
        providers->log_error(context, status);
        *result_status = status;
        return true;
    }

    status = providers->apply(context, input, timestamp);
    providers->snapshot(context);
    state->previous_timestamp = timestamp;
    const uint32_t sign = state->update_flags >> 31u;
    const uint32_t shifted =
        (sign | state->update_flags << 1u) + UINT32_C(2);
    state->update_flags = (shifted >> 1u) | sign << 31u;
    *result_status = status;
    return true;
}

bool gomore_primitives_motion_classifier_update(
    uint8_t state[17], size_t state_length, uint32_t elapsed_seconds,
    const uint8_t *source, size_t source_length,
    const uint8_t features[62], size_t feature_length,
    uint8_t output[3], size_t output_length,
    gomore_primitives_state1_cadence_estimate_fn estimate_state1) {
    if (state == NULL || state_length < 17u || source == NULL ||
            source_length <= 0x0Cu || features == NULL ||
            feature_length < 62u || output == NULL || output_length < 3u) {
        return false;
    }
    output[0] = UINT8_C(0xFE);
    if (elapsed_seconds > 1u) {
        if (elapsed_seconds <= 5u) {
            for (uint32_t index = 0u; index < elapsed_seconds - 1u;
                    ++index) {
                (void)gomore_primitives_shift_two_u8_windows5(
                    &state[5], &state[0], 0u, UINT8_C(0xFE));
            }
        } else {
            for (size_t index = 0u; index < 5u; ++index) {
                state[index] = UINT8_C(0xFE);
                state[index + 5u] = 0u;
            }
        }
    }

    bool features_all_zero = true;
    for (size_t index = 0u; index < 8u; ++index) {
        if (bits_float(load_u32_le(&features[index * 4u])) != 0.0f) {
            features_all_zero = false;
        }
    }
    if (source[0x0Cu] == 1u || features_all_zero || elapsed_seconds > 5u) {
        return gomore_primitives_shift_status_windows(state, output);
    }

    if (!gomore_primitives_quality_code(features, feature_length, &output[0]) ||
            !gomore_primitives_selector_transition(
                features, feature_length, (int8_t *)(void *)&output[0]) ||
            !gomore_primitives_validate_selector(
                state, state_length, (int8_t *)(void *)&output[0])) {
        return false;
    }
    return gomore_primitives_motion_classifier_finalize(
        state, state_length, features, feature_length,
        output, output_length, estimate_state1);
}

bool gomore_primitives_activity_state_classify250(
    const float *samples, size_t sample_count, bool alternate_mode,
    float differences[249], size_t difference_capacity,
    gomore_primitives_activity_statistics_fn statistics,
    bool *classified) {
    if (samples == NULL || sample_count < 250u || differences == NULL ||
            difference_capacity < 249u || statistics == NULL ||
            classified == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 249u; ++index) {
        differences[index] = samples[index + 1u] - samples[index];
    }

    float sample_statistics[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    float difference_statistics[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    if (!alternate_mode) {
        statistics(samples, 250u, 3u, sample_statistics);
        statistics(differences, 249u, 7u, difference_statistics);
        *classified =
            (int32_t)float_bits(sample_statistics[0]) >=
                (int32_t)UINT32_C(0x4136147B) &&
            (int32_t)float_bits(difference_statistics[0]) <=
                (int32_t)UINT32_C(0x41CC0000);
        return true;
    }

    const float crossing_spacing =
        gomore_primitives_average_sign_crossing_spacing(differences, 249u);
    statistics(differences, 249u, 3u, difference_statistics);
    statistics(samples, 250u, 3u, sample_statistics);
    float center = 0.0f;
    float span = 0.0f;
    if (!gomore_primitives_range_center_span(
            samples, 250u, 1u, &center, &span)) {
        return false;
    }
    float normalized_offset = 0.0f;
    if (span != 0.0f) {
        normalized_offset = (sample_statistics[3] - center) / span;
    }
    if ((int32_t)float_bits(sample_statistics[0]) <
            (int32_t)UINT32_C(0x4146E148)) {
        *classified =
            (int32_t)float_bits(crossing_spacing) >
                (int32_t)UINT32_C(0x40600000) &&
            (int32_t)float_bits(normalized_offset) <=
                (int32_t)UINT32_C(0x3F11EB85);
    } else {
        *classified =
            (int32_t)float_bits(difference_statistics[1]) <
                (int32_t)UINT32_C(0x40E851EC) ||
            (int32_t)float_bits(crossing_spacing) >
                (int32_t)UINT32_C(0x40F66666);
    }
    return true;
}

bool gomore_primitives_activity_window_update(
    gomore_primitives_activity_window_state *state, float input_quality,
    const gomore_primitives_activity_window_input *input,
    const gomore_primitives_activity_window_providers *providers,
    float differences[249], size_t difference_capacity,
    gomore_primitives_activity_window_output *output) {
    if (state == NULL || input == NULL || providers == NULL ||
            output == NULL || differences == NULL ||
            difference_capacity < 249u || providers->statistics == NULL ||
            state->state > 6u ||
            input->sample_count < 0 ||
            (input->channel_count != 0u && input->samples == NULL) ||
            (!providers->alternate_conditioning &&
             (providers->square_root == NULL ||
              providers->axes[0] == NULL || providers->axes[1] == NULL ||
              providers->axes[2] == NULL))) {
        return false;
    }

    if (providers->alternate_conditioning) {
        const float decayed = state->score * 0.9f;
        state->score = (float)(
            (double)decayed + 0.05000000074505806);
    } else if ((int32_t)float_bits(input_quality) >
                   (int32_t)UINT32_C(0x41200000)) {
        state->score = 0.8f;
    } else if (!gomore_primitives_activity_score_variability_adjust(
                   &state->score, providers->axes, false,
                   providers->square_root)) {
        return false;
    }

    static const uint8_t positive_thresholds[7] = {
        5u, 0u, 7u, 6u, 0u, 2u, 7u,
    };
    static const uint8_t negative_thresholds[7] = {
        5u, 0u, 5u, 4u, 0u, 8u, 3u,
    };
    const uint8_t original_state = state->state;

    if (!(state->score < state->reset_threshold)) {
        state->reset_threshold = 0.5f;
        state->transition_count = 0;
        state->accumulated_samples = 0;
        state->positive_windows = 0u;
        state->negative_windows = 0u;
        if (original_state == 1u || original_state == 2u) {
            state->state = 3u;
        } else if (original_state == 4u || original_state == 5u) {
            state->state = 6u;
        }
    } else if (original_state == 1u || original_state == 4u) {
        state->transition_count = (int32_t)(
            (uint32_t)state->transition_count + UINT32_C(1));
        if (state->transition_count >= state->hold_samples) {
            state->state = (uint8_t)(original_state + 1u);
            state->transition_count = 0;
        }
    } else {
        const bool accepted =
            (int32_t)float_bits(input_quality) <=
                (int32_t)UINT32_C(0x3F800000) &&
            input->sample_count >= 23 && input->sample_count <= 27;
        const uint8_t admitted_channels = input->channel_count > 1u
            ? 1u : input->channel_count;
        if (!accepted) {
            state->accumulated_samples = 0;
            if (state->positive_windows != 0u) {
                --state->positive_windows;
            }
            if (state->negative_windows != 0u) {
                --state->negative_windows;
            }
        } else {
            for (uint8_t channel = 0u; channel < admitted_channels;
                    ++channel) {
                float *window = &state->window[channel * 250u];
                for (size_t index = 0u; index < 225u; ++index) {
                    window[index] = window[index + 25u];
                }
                /*
                 * The stock equal-rate transform copies the reported count,
                 * not the nominal 25. Counts 26 and 27 therefore overwrite
                 * the first one or two metadata words. Copy through the full
                 * state object's byte representation so that quirk remains
                 * exact without an out-of-bounds C array access.
                 */
                uint8_t *destination = (uint8_t *)(void *)state +
                    offsetof(gomore_primitives_activity_window_state,
                             window) + 225u * sizeof(float);
                const uint8_t *source =
                    (const uint8_t *)(const void *)input->samples;
                const size_t copied =
                    (size_t)input->sample_count * sizeof(float);
                for (size_t byte = 0u; byte < copied; ++byte) {
                    destination[byte] = source[byte];
                }
            }
            state->accumulated_samples = (int32_t)(
                (uint32_t)state->accumulated_samples + UINT32_C(25));
        }

        if (state->accumulated_samples >= 250) {
            state->accumulated_samples = 125;
            for (uint8_t channel = 0u; channel < admitted_channels;
                    ++channel) {
                bool classified = false;
                if (!gomore_primitives_activity_state_classify250(
                        &state->window[channel * 250u], 250u,
                        original_state > 3u, differences,
                        difference_capacity, providers->statistics,
                        &classified)) {
                    return false;
                }
                if (classified) {
                    ++state->positive_windows;
                } else {
                    ++state->negative_windows;
                }
            }

            if (state->positive_windows ==
                    (uint8_t)(positive_thresholds[original_state] *
                              admitted_channels)) {
                if (original_state == 5u) {
                    state->hold_samples = (int32_t)(
                        (double)state->hold_samples * 1.2);
                    state->reset_threshold = (float)(
                        (double)state->reset_threshold * 0.95);
                    if (state->hold_samples > 600) {
                        state->hold_samples = 600;
                    }
                    if (state->reset_threshold < 0.25f) {
                        state->reset_threshold = 0.25f;
                    }
                } else {
                    state->hold_samples = 180;
                }
                state->state = 4u;
                state->negative_windows = 0u;
                state->positive_windows = 0u;
                state->accumulated_samples = 0;
                state->transition_count = 0;
            } else if (state->negative_windows ==
                    (uint8_t)(negative_thresholds[original_state] *
                              admitted_channels)) {
                state->reset_threshold = 0.5f;
                if (original_state == 2u) {
                    state->hold_samples = (int32_t)(
                        (double)state->hold_samples * 1.2);
                    if (state->hold_samples > 600) {
                        state->hold_samples = 600;
                    }
                } else {
                    state->hold_samples = 180;
                }
                state->state = 1u;
                state->negative_windows = 0u;
                state->positive_windows = 0u;
                state->accumulated_samples = 0;
                state->transition_count = 0;
            }
        }
    }

    static const uint8_t activities[7] = {
        UINT8_C(0xFF), 0u, 0u, 0u, 1u, 1u, 1u,
    };
    output->activity = activities[state->state];
    if (state->state == 1u || state->state == 4u) {
        output->confidence = 0u;
    } else {
        output->confidence =
            (int32_t)float_bits(state->score) <=
                (int32_t)UINT32_C(0x3F266666) ? 1u : 0u;
    }
    return true;
}

bool gomore_primitives_respiratory_rate_update(
    gomore_primitives_respiratory_rate_state *state, uint32_t elapsed,
    const gomore_primitives_respiratory_rate_input *input,
    void *estimator_state,
    const gomore_primitives_respiratory_rate_providers *providers,
    float output[2], uint32_t *status) {
    if (state == NULL || input == NULL || estimator_state == NULL ||
            providers == NULL || providers->estimate == NULL ||
            providers->square_root == NULL || output == NULL ||
            status == NULL) {
        return false;
    }

    if (elapsed > 1u) {
        uint32_t missing = elapsed - 1u;
        if (missing > 20u) {
            missing = 20u;
        }
        for (uint32_t index = 0u; index < missing; ++index) {
            if (!gomore_primitives_modulo5_record(
                    (uint8_t *)(void *)state, sizeof(*state), 2u, 2u)) {
                return false;
            }
        }
    }
    if (!gomore_primitives_modulo5_record(
            (uint8_t *)(void *)state, sizeof(*state),
            input->secondary_code, input->primary_code)) {
        return false;
    }

    float secondary_square_mean = 0.0f;
    for (size_t index = 0u; index < 2u; ++index) {
        const uint32_t code = state->secondary_codes[index];
        secondary_square_mean += (float)(code * code);
    }
    secondary_square_mean *= 0.5f;
    float primary_square_mean = 0.0f;
    for (size_t index = 0u; index < 4u; ++index) {
        const uint32_t code = state->primary_codes[index];
        primary_square_mean += (float)(code * code);
    }
    primary_square_mean *= 0.25f;

    uint32_t flags = input->input_unavailable ? UINT32_C(0x40) : 0u;
    float rate = 0.0f;
    float confidence = 0.0f;
    if (providers->estimate(
            estimator_state, elapsed, input->estimator_input, flags,
            &rate, &confidence) != 0) {
        flags |= UINT32_C(0x08);
    }

    const bool encoded_rate_valid =
        float_bits(rate) + UINT32_C(0xBF200000) < UINT32_C(0x00E80001);
    if (!encoded_rate_valid) {
        if (rate > 0.0f && confidence > 0.0f) {
            if ((int32_t)float_bits(rate) >
                    (int32_t)UINT32_C(0x41C80000)) {
                rate = 25.0f;
            } else if ((int32_t)float_bits(rate) <
                           (int32_t)UINT32_C(0x40E00000)) {
                rate = 7.0f;
            }
        } else if (float_bits(rate) != UINT32_C(0xBF800000)) {
            rate = -1.0f;
        }
        flags |= UINT32_C(0x10);
    }

    if (elapsed > 1u) {
        if (!gomore_primitives_clear_two_records(state, sizeof(*state))) {
            return false;
        }
        flags |= UINT32_C(0x20);
    }

    if ((int32_t)float_bits(secondary_square_mean) >
            (int32_t)UINT32_C(0x3F800000)) {
        const double adjustment =
            providers->square_root((double)secondary_square_mean) *
            0.25 * 0.30000001192092896;
        confidence = (float)((double)confidence - adjustment);
    }
    if ((int32_t)float_bits(primary_square_mean) >
            (int32_t)UINT32_C(0x3F000000)) {
        const double adjustment =
            providers->square_root((double)primary_square_mean) *
            0.25 * 0.30000001192092896;
        confidence = (float)((double)confidence - adjustment);
    }
    if (confidence < 0.0f) {
        confidence = 0.0f;
        rate = -1.0f;
    }

    for (size_t index = 1u; index < 5u; ++index) {
        state->rate_history[index - 1u] = state->rate_history[index];
        state->confidence_history[index - 1u] =
            state->confidence_history[index];
    }
    state->rate_history[4] = rate;
    state->confidence_history[4] = confidence;

    if (gomore_primitives_count_encoded_i32(
            (const int32_t *)(const void *)state->rate_history, 5u) < 1u) {
        output[0] = rate;
        output[1] = confidence;
        *status = flags;
        return true;
    }

    const int32_t maximum_index = gomore_primitives_argmax_from_zero(
        state->confidence_history, 5u);
    if (maximum_index < 0) {
        return false;
    }
    const float maximum_confidence =
        state->confidence_history[(size_t)maximum_index];
    const float threshold =
        (int32_t)float_bits(maximum_confidence) >
            (int32_t)UINT32_C(0x3F000000)
        ? 0.5f
        : (float)((double)maximum_confidence * 0.8);
    const int32_t included = gomore_primitives_thresholded_mean5(
        threshold, state->rate_history, state->confidence_history,
        &output[0]);
    if (included < 0) {
        return false;
    }
    float inclusion_share = (float)included / 5.0f;
    inclusion_share *= 0.30000001192092896f;
    output[1] = (float)(
        (double)maximum_confidence * 0.7 + (double)inclusion_share);
    *status = flags;
    return true;
}

static bool float_is_nan(float value) {
    const uint32_t bits = float_bits(value);
    return (bits & UINT32_C(0x7F800000)) == UINT32_C(0x7F800000) &&
           (bits & UINT32_C(0x007FFFFF)) != 0u;
}

bool gomore_primitives_optical_period_candidates_select(
    float mode1_rate, float mode1_quality,
    float mode2_rate, float mode2_quality,
    float fallback_rate, float fallback_quality,
    float output[2]) {
    if (output == NULL) {
        return false;
    }
    output[0] = -1.0f;
    output[1] = 0.0f;

    if (mode2_quality == 0.0f && mode1_quality == 0.0f) {
        if (fallback_quality > 0.0f &&
                (int32_t)float_bits(fallback_rate) <=
                    INT32_C(0x41C80000) &&
                (int32_t)float_bits(fallback_quality) >
                    INT32_C(0x3F000000)) {
            output[0] = fallback_rate;
            output[1] = fallback_quality;
        }
        return true;
    }

    if (mode2_quality > 0.0f && !float_is_nan(mode1_quality)) {
        double rate_difference = (double)(mode1_rate - mode2_rate);
        if (rate_difference < 0.0) {
            rate_difference = -rate_difference;
        }
        if (rate_difference < 1.0) {
            output[0] = (mode2_rate + mode1_rate) * 0.5f;
            const double scaled_quality =
                (double)((mode2_quality + mode1_quality) * 0.5f) * 1.2;
            output[1] = (float)(scaled_quality < 1.0
                ? scaled_quality : 1.0);
            return true;
        }
    }

    if (mode1_quality < mode2_quality) {
        output[0] = mode2_rate;
        output[1] = mode2_quality;
    } else {
        output[0] = mode1_rate;
        output[1] = mode1_quality;
    }
    if ((int32_t)float_bits(fallback_quality) > INT32_C(0x3F000000) &&
            (int32_t)float_bits(output[1]) < INT32_C(0x3E99999A) &&
            (int32_t)float_bits(fallback_rate) <= INT32_C(0x41C80000)) {
        output[0] = fallback_rate;
        output[1] = fallback_quality;
    }
    return true;
}

static void optical_period_window_advance(
    gomore_primitives_optical_interval_state *state) {
    if (state->current_window < UINT32_MAX - 1u) {
        ++state->current_window;
    }
}

static bool optical_period_shift(
    gomore_primitives_optical_interval_state *state,
    const float input[25], bool zero_fill,
    const gomore_primitives_optical_period_providers *providers) {
    return gomore_primitives_shift_negated_filter_history(
        state, sizeof(*state), input, zero_fill, providers->apply_filter);
}

static float optical_period_tolerance_update(float previous,
                                             float measurement) {
    if (previous < 0.0f && measurement > 0.0f) {
        return measurement;
    }
    return (float)((double)previous * 0.75 +
                   (double)measurement * 0.25);
}

bool gomore_primitives_optical_period_estimate(
    gomore_primitives_optical_interval_state *state,
    uint32_t elapsed_windows, const float input[25], uint32_t flags,
    const gomore_primitives_optical_period_providers *providers,
    gomore_primitives_optical_period_workspace *workspace,
    float output[2], int32_t *status) {
    if (state == NULL || providers == NULL || workspace == NULL ||
            output == NULL || status == NULL ||
            providers->initialize_filter_state == NULL ||
            providers->apply_filter == NULL ||
            providers->round_value == NULL ||
            providers->feature_math.qsort_provider == NULL ||
            providers->feature_math.compare == NULL ||
            providers->feature_math.power_f32 == NULL ||
            providers->feature_math.square_root_f32 == NULL ||
            providers->feature_math.power_f64 == NULL ||
            providers->feature_math.square_root_f64 == NULL ||
            state->interval_count > 40u ||
            ((elapsed_windows < 2u || flags == 0u) && input == NULL)) {
        return false;
    }

    output[0] = -1.0f;
    output[1] = 0.0f;
    *status = 1;
    const bool ordinary = elapsed_windows < 2u &&
                          (flags & UINT32_C(0x40)) == 0u;
    if (!ordinary) {
        if (elapsed_windows > 20u) {
            if (!gomore_primitives_large_filter_state_initialize(
                    state, sizeof(*state),
                    providers->initialize_filter_state)) {
                return false;
            }
            return true;
        }
        state->prefix[80] = 9u;
        for (uint32_t index = 0u; index < elapsed_windows; ++index) {
            if (!gomore_primitives_compact_25_windows(
                    (uint8_t *)(void *)state->intervals, 40u,
                    &state->interval_count, state->current_window)) {
                return false;
            }
            const bool zero_fill = index + 1u != elapsed_windows ||
                                   flags != 0u;
            if (!optical_period_shift(
                    state, input, zero_fill, providers)) {
                return false;
            }
            optical_period_window_advance(state);
        }
        return true;
    }

    if (state->prefix[80] != 0u) {
        --state->prefix[80];
        if (!optical_period_shift(state, input, false, providers) ||
                !gomore_primitives_compact_25_windows(
                    (uint8_t *)(void *)state->intervals, 40u,
                    &state->interval_count, state->current_window)) {
            return false;
        }
        optical_period_window_advance(state);
        return true;
    }

    optical_period_window_advance(state);
    if (!optical_period_shift(state, input, false, providers)) {
        return false;
    }
    if (state->current_window < 10u) {
        return true;
    }

    size_t first_count = 0u;
    size_t second_count = 0u;
    (void)gomore_primitives_moving_average_extrema_indices(
        state->signal, 250u, 25u, 6u,
        workspace->first_indices, GOMORE_PRIMITIVES_EXTREMA_CAPACITY,
        &first_count,
        workspace->second_indices, GOMORE_PRIMITIVES_EXTREMA_CAPACITY,
        &second_count);
    uint8_t first_count_u8 = (uint8_t)first_count;
    uint8_t second_count_u8 = (uint8_t)second_count;
    float median_spacing = 0.0f;
    (void)gomore_primitives_peak_candidate_match(
        state->signal, 250u,
        workspace->first_indices, workspace->second_indices,
        &first_count_u8, &second_count_u8,
        &median_spacing, workspace->peak_workspace,
        providers->feature_math.qsort_provider,
        providers->feature_math.compare,
        providers->feature_math.power_f32,
        providers->feature_math.square_root_f32);
    float mean_amplitude = 0.0f;
    if (!gomore_primitives_optical_interval_merge(
            state, workspace->first_indices, workspace->second_indices,
            first_count_u8, &mean_amplitude)) {
        return false;
    }
    state->position_tolerance_scale = optical_period_tolerance_update(
        state->position_tolerance_scale, median_spacing);
    state->amplitude_tolerance_scale = optical_period_tolerance_update(
        state->amplitude_tolerance_scale, mean_amplitude);
    if (state->interval_count <= 2u) {
        return true;
    }

    for (size_t index = 0u; index < state->interval_count; ++index) {
        workspace->control_samples[index].position =
            state->intervals[index].peak_position;
        workspace->control_samples[index].first =
            state->intervals[index].end_value;
        workspace->control_samples[index].second =
            state->intervals[index].start_value;
    }

    float mode1_rate = -1.0f;
    float mode1_quality = 0.0f;
    float mode2_rate = -1.0f;
    float mode2_quality = 0.0f;
    size_t accepted_count = 0u;
    int32_t extraction_status = 0;
    if (!gomore_primitives_locomotion_control_extract(
            workspace->control_samples, state->interval_count,
            state->position_tolerance_scale,
            state->amplitude_tolerance_scale, 1u,
            &workspace->control_workspace,
            providers->round_value,
            gomore_primitives_locomotion_feature_reduce,
            &providers->feature_math,
            &mode1_rate, &mode1_quality,
            &accepted_count, &extraction_status) ||
            !gomore_primitives_locomotion_control_extract(
                workspace->control_samples, state->interval_count,
                state->position_tolerance_scale,
                state->amplitude_tolerance_scale, 2u,
                &workspace->control_workspace,
                providers->round_value,
                gomore_primitives_locomotion_feature_reduce,
                &providers->feature_math,
                &mode2_rate, &mode2_quality,
                &accepted_count, &extraction_status)) {
        return false;
    }

    float fallback_rate = -1.0f;
    float fallback_quality = 0.0f;
    const float required_base =
        500.0f / state->position_tolerance_scale;
    const double required_intervals = (double)required_base * 0.85;
    if ((double)state->interval_count < required_intervals) {
        const float weight = bits_float(UINT32_C(0x3C888889));
        float smoothed = 0.0f;
        for (size_t index = 0u; index < 60u; ++index) {
            smoothed += state->signal[index] * weight;
        }
        for (size_t index = 0u; index < 125u; ++index) {
            smoothed = (state->signal[index * 2u] +
                        state->signal[index * 2u + 1u]) *
                           weight * 0.5f +
                       (1.0f - weight) * smoothed;
            workspace->control_workspace.expanded[index] = smoothed;
            workspace->control_workspace.expanded[249u - index] = smoothed;
        }
        if (!gomore_primitives_locomotion_feature_reduce(
                workspace->control_workspace.expanded,
                workspace->control_workspace.first_indices,
                workspace->control_workspace.second_indices,
                workspace->control_workspace.controls,
                &fallback_rate, &fallback_quality,
                &providers->feature_math)) {
            return false;
        }
    }

    if (!gomore_primitives_optical_period_candidates_select(
            mode1_rate, mode1_quality,
            mode2_rate, mode2_quality,
            fallback_rate, fallback_quality, output)) {
        return false;
    }
    *status = 0;
    return true;
}

bool gomore_primitives_optical_interval_merge(
    gomore_primitives_optical_interval_state *state,
    const uint8_t *end_positions, const uint8_t *start_positions,
    size_t candidate_count, float *mean_amplitude) {
    if (state == NULL || mean_amplitude == NULL ||
            candidate_count > UINT8_MAX || state->interval_count > 40u ||
            ((end_positions == NULL || start_positions == NULL) &&
             candidate_count != 0u)) {
        return false;
    }
    for (size_t index = 0u; index < candidate_count; ++index) {
        if (start_positions[index] >= end_positions[index] ||
                end_positions[index] >= 250u) {
            return false;
        }
    }
    *mean_amplitude = 0.0f;

    if (!gomore_primitives_compact_25_windows(
            (uint8_t *)(void *)state->intervals, 40u,
            &state->interval_count, state->current_window)) {
        return false;
    }
    size_t cached_count = state->interval_count;
    size_t cursor = 0u;
    const uint16_t window_offset = state->current_window < 20u
        ? (uint16_t)(((int32_t)state->current_window - 10) * 25)
        : UINT16_C(250);

    for (size_t candidate_index = 0u;
            candidate_index < candidate_count; ++candidate_index) {
        const uint8_t local_end = end_positions[candidate_index];
        const uint8_t local_start = start_positions[candidate_index];
        const uint32_t local_peak = gomore_primitives_max_difference_index(
            state->signal, local_start, local_end);
        if (local_peak == UINT32_MAX) {
            return false;
        }
        const gomore_primitives_optical_interval_record candidate = {
            .end_position = (uint16_t)(window_offset + local_end),
            .start_position = (uint16_t)(window_offset + local_start),
            .peak_position = (uint16_t)(window_offset + local_peak),
            .padding = 0u,
            .end_value = state->signal[local_end],
            .start_value = state->signal[local_start],
        };

        bool use_tail = cached_count == 0u || cursor >= cached_count - 1u;
        if (!use_tail) {
            while (state->intervals[cursor].end_position <
                       candidate.end_position &&
                    state->intervals[cursor].start_position <
                       candidate.start_position &&
                    cursor + 1u < cached_count) {
                ++cursor;
            }
            const gomore_primitives_optical_interval_record *current =
                &state->intervals[cursor];
            if (cursor >= cached_count - 1u &&
                    current->end_position < candidate.end_position) {
                use_tail = true;
            } else if (current->end_position == candidate.end_position &&
                    current->start_position == candidate.start_position) {
                /* Stock retries forever on an exact duplicate; one copy is
                 * the complete observable bounded result. */
                continue;
            } else if (current->end_position > candidate.end_position &&
                    current->start_position > candidate.start_position) {
                if (state->interval_count >= 40u) {
                    return false;
                }
                for (size_t index = state->interval_count; index > cursor;
                        --index) {
                    state->intervals[index] = state->intervals[index - 1u];
                }
                state->intervals[cursor] = candidate;
                ++state->interval_count;
                ++cached_count;
                continue;
            } else {
                /*
                 * The stock tolerance/amplitude block selects only between
                 * stack-local copies and never commits either record.
                 */
                continue;
            }
        }

        if (use_tail) {
            bool replace_last = false;
            if (state->interval_count != 0u) {
                const gomore_primitives_optical_interval_record *last =
                    &state->intervals[state->interval_count - 1u];
                replace_last = candidate.end_position <= last->end_position ||
                    candidate.start_position <= last->start_position;
            }
            if (replace_last) {
                state->intervals[state->interval_count - 1u] = candidate;
            } else {
                if (state->interval_count >= 40u) {
                    return false;
                }
                state->intervals[state->interval_count] = candidate;
                ++state->interval_count;
            }
        }
    }

    for (size_t index = 0u; index + 1u < state->interval_count; ++index) {
        if (state->intervals[index + 1u].end_position <=
                    state->intervals[index].end_position ||
                state->intervals[index + 1u].start_position <=
                    state->intervals[index].start_position) {
            state->interval_count = 0u;
            return false;
        }
    }
    float total = 0.0f;
    for (size_t index = 0u; index < state->interval_count; ++index) {
        total += state->intervals[index].end_value -
            state->intervals[index].start_value;
    }
    if (state->interval_count != 0u) {
        *mean_amplitude = total / (float)state->interval_count;
    }
    return true;
}

enum {
    SLEEP_CLASSIFIER_BANK_FLOATS = 720,
    SLEEP_CLASSIFIER_WEIGHT_FLOATS = 192,
    SLEEP_CLASSIFIER_HIDDEN_UNITS = 32,
    SLEEP_CLASSIFIER_POOL_FLOATS = 1764,
    SLEEP_CLASSIFIER_WEIGHT_OFFSET = 1440,
    SLEEP_CLASSIFIER_HIDDEN_OFFSET = 1632,
};

static float sleep_classifier_half_to_float(int16_t value) {
    return bits_float(gomore_primitives_half_to_float_bits((uint16_t)value));
}

static bool sleep_classifier_affine_valid(
    const gomore_primitives_sleep_stage_affine_model *model,
    size_t rows, size_t columns) {
    return model != NULL && model->weights != NULL &&
        model->rows == rows && model->columns == columns &&
        rows <= SIZE_MAX / columns &&
        model->weight_count >= rows * columns &&
        model->bias_half != NULL && model->bias_count >= rows;
}

static bool sleep_classifier_model_valid(
    const gomore_primitives_sleep_stage_classifier_model *model) {
    if (model == NULL) {
        return false;
    }
    static const size_t weight_counts[7] = {
        12u, 96u, 192u, 192u, 192u, 192u, 192u,
    };
    static const size_t parameter_counts[7] = {
        4u, 8u, 8u, 8u, 8u, 8u, 8u,
    };
    for (size_t index = 0u; index < 7u; ++index) {
        const gomore_primitives_sleep_stage_conv_model *block =
            &model->convolution[index];
        if (block->weights_half == NULL ||
                block->weight_count < weight_counts[index] ||
                block->scale_half == NULL || block->offset_half == NULL ||
                block->variance_half == NULL || block->mean_half == NULL ||
                block->parameter_count < parameter_counts[index]) {
            return false;
        }
    }
    if (!sleep_classifier_affine_valid(&model->projection[0], 32u, 120u) ||
            !sleep_classifier_affine_valid(
                &model->projection[1], 32u, 32u) ||
            !sleep_classifier_affine_valid(
                &model->post_recurrent, 32u, 32u) ||
            !sleep_classifier_affine_valid(&model->output, 4u, 32u)) {
        return false;
    }
    for (size_t index = 0u; index < 2u; ++index) {
        if (!sleep_classifier_affine_valid(
                &model->recurrent[index].input, 96u, 32u) ||
                !sleep_classifier_affine_valid(
                    &model->recurrent[index].recurrent, 96u, 32u)) {
            return false;
        }
    }
    return true;
}

static bool sleep_classifier_affine(
    const gomore_primitives_sleep_stage_affine_model *model,
    const float *input, float *output) {
    return gomore_tensor_int8_float_affine(
        model->weights, model->rows, model->columns,
        model->weight_scale, input, model->bias_half, output,
        sleep_classifier_half_to_float);
}

static bool sleep_classifier_recurrent_transform(
    const gomore_primitives_sleep_stage_affine_model *model,
    size_t gate, const float input[32], float output[32]) {
    const size_t rows = SLEEP_CLASSIFIER_HIDDEN_UNITS;
    const size_t columns = SLEEP_CLASSIFIER_HIDDEN_UNITS;
    const size_t weight_offset = gate * rows * columns;
    const size_t bias_offset = gate * rows;
    if (!gomore_tensor_int8_float_dot(
            &model->weights[weight_offset], rows, columns,
            model->weight_scale, input, output)) {
        return false;
    }
    for (size_t index = 0u; index < rows; ++index) {
        output[index] += sleep_classifier_half_to_float(
            model->bias_half[bias_offset + index]);
    }
    return true;
}

static bool sleep_classifier_recurrent_layer(
    const gomore_primitives_sleep_stage_recurrent_model *model,
    const gomore_primitives_sleep_stage_classifier_math *math,
    const float input[32], float hidden[32],
    float output[32], float scratch[128]) {
    float *gate0 = &scratch[0];
    float *gate1 = &scratch[32];
    float *candidate = &scratch[64];
    float *temporary = &scratch[96];
    for (size_t gate = 0u; gate < 3u; ++gate) {
        float *current = gate == 0u
            ? gate0 : (gate == 1u ? gate1 : candidate);
        if (!sleep_classifier_recurrent_transform(
                &model->input, gate, input, current) ||
                !sleep_classifier_recurrent_transform(
                    &model->recurrent, gate, hidden, temporary)) {
            return false;
        }
        for (size_t index = 0u;
                index < SLEEP_CLASSIFIER_HIDDEN_UNITS; ++index) {
            if (gate == 2u) {
                temporary[index] *= gate0[index];
            }
            current[index] += temporary[index];
            current[index] = gate == 2u
                ? math->hyperbolic_tangent(current[index])
                : math->logistic(current[index]);
        }
    }
    for (size_t index = 0u;
            index < SLEEP_CLASSIFIER_HIDDEN_UNITS; ++index) {
        const float retained = gate1[index] * hidden[index];
        const float replacement =
            (1.0f - gate1[index]) * candidate[index];
        output[index] = retained + replacement;
        hidden[index] = output[index];
    }
    return true;
}

bool gomore_primitives_sleep_stage_classify(
    gomore_primitives_sleep_stage_classifier_result *result,
    gomore_primitives_sleep_stage_stream_state *state,
    uint8_t iteration, const int8_t mode_adjustment[4], void *context) {
    if (result == NULL || state == NULL) {
        return false;
    }
    if (iteration != 1u) {
        const gomore_primitives_sleep_stage_classifier_result pending = {
            1.0f, {0.0f, 0.0f, 0.0f}, 0,
        };
        *result = pending;
        return true;
    }
    const gomore_primitives_sleep_stage_classifier_context *configuration =
        context;
    if (configuration == NULL || mode_adjustment == NULL ||
            configuration->math.square_root == NULL ||
            configuration->math.exponential == NULL ||
            configuration->math.logistic == NULL ||
            configuration->math.hyperbolic_tangent == NULL) {
        return false;
    }
    const gomore_primitives_sleep_stage_classifier_model *model =
        state->mode < 100u ? configuration->mode_below_100
                           : configuration->mode_100_and_above;
    if (!sleep_classifier_model_valid(model)) {
        return false;
    }

    float *pool = (float *)(void *)state->tensor_storage;
    float *banks[2] = {
        &pool[0], &pool[SLEEP_CLASSIFIER_BANK_FLOATS],
    };
    float *weight_scratch = &pool[SLEEP_CLASSIFIER_WEIGHT_OFFSET];
    float *hidden[2] = {
        &pool[SLEEP_CLASSIFIER_HIDDEN_OFFSET],
        &pool[SLEEP_CLASSIFIER_HIDDEN_OFFSET +
              SLEEP_CLASSIFIER_HIDDEN_UNITS],
    };
    _Static_assert(sizeof(state->tensor_storage) / sizeof(float) ==
                       SLEEP_CLASSIFIER_POOL_FLOATS,
                   "sleep classifier pool size must remain exact");

    const float negative_scale = bits_float(
        gomore_primitives_half_to_float_bits(UINT16_C(0x31D1)));
    const uint16_t epsilon_half = UINT16_C(0x00A8);
    const float *source = state->stage_window;
    size_t source_count = 90u;
    size_t channels = 1u;
    size_t width = 90u;
    size_t destination_bank = 0u;
    for (size_t block_index = 0u; block_index < 7u; ++block_index) {
        const gomore_primitives_sleep_stage_conv_model *block =
            &model->convolution[block_index];
        const size_t output_channels = block_index == 0u ? 4u : 8u;
        float *destination = banks[destination_bank];
        size_t output_width = 0u;
        if (!gomore_tensor_conv1d_half(
                source, source_count, channels, width,
                block->weights_half, block->weight_count,
                output_channels, 3u, 1u, 1u,
                weight_scratch, SLEEP_CLASSIFIER_WEIGHT_FLOATS,
                destination, SLEEP_CLASSIFIER_BANK_FLOATS, &output_width,
                gomore_primitives_half_to_float_bits)) {
            return false;
        }
        const uint16_t dimensions[2] = {
            (uint16_t)output_channels, (uint16_t)output_width,
        };
        const size_t output_count = output_channels * output_width;
        if (!gomore_tensor_batch_normalize_half(
                destination, output_count, dimensions, 2u, epsilon_half,
                block->scale_half, block->offset_half,
                block->variance_half, block->mean_half,
                block->parameter_count, destination, output_count,
                gomore_primitives_half_to_float_bits,
                configuration->math.square_root) ||
                !gomore_tensor_leaky_relu(
                    destination, destination, output_count,
                    negative_scale)) {
            return false;
        }
        source = destination;
        source_count = output_count;
        channels = output_channels;
        width = output_width;
        destination_bank ^= 1u;

        if (block_index == 3u || block_index == 6u) {
            const uint8_t window = block_index == 3u ? 2u : 3u;
            const size_t pooled_width = width / (size_t)window;
            destination = banks[destination_bank];
            if (!gomore_tensor_pool_1d(
                    source, source_count, channels, width,
                    destination, SLEEP_CLASSIFIER_BANK_FLOATS,
                    channels, pooled_width, 1u, window, window, 0u, NULL)) {
                return false;
            }
            source = destination;
            source_count = channels * pooled_width;
            width = pooled_width;
            destination_bank ^= 1u;
        }
    }
    if (source_count != 120u) {
        return false;
    }

    float *destination = banks[destination_bank];
    if (!sleep_classifier_affine(&model->projection[0], source, destination)) {
        return false;
    }
    source = destination;
    destination_bank ^= 1u;
    destination = banks[destination_bank];
    if (!sleep_classifier_affine(&model->projection[1], source, destination) ||
            !gomore_tensor_leaky_relu(
                destination, destination, 32u, negative_scale)) {
        return false;
    }
    source = destination;
    destination_bank ^= 1u;

    for (size_t layer = 0u; layer < 2u; ++layer) {
        destination = banks[destination_bank];
        float *scratch = &banks[destination_bank ^ 1u][64];
        if (!sleep_classifier_recurrent_layer(
                &model->recurrent[layer], &configuration->math,
                source, hidden[layer], destination, scratch)) {
            return false;
        }
        source = destination;
        destination_bank ^= 1u;
    }

    destination = banks[destination_bank];
    if (!sleep_classifier_affine(
            &model->post_recurrent, source, destination) ||
            !gomore_tensor_leaky_relu(
                destination, destination, 32u, negative_scale)) {
        return false;
    }
    source = destination;
    destination_bank ^= 1u;
    destination = banks[destination_bank];
    if (!sleep_classifier_affine(&model->output, source, destination) ||
            !gomore_tensor_softmax(
                destination, destination, 4u,
                configuration->math.exponential)) {
        return false;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        destination[index] +=
            (float)mode_adjustment[index] *
            bits_float(UINT32_C(0x3C23D70A));
    }
    size_t selected = 0u;
    for (size_t index = 1u; index < 4u; ++index) {
        if (destination[selected] < destination[index]) {
            selected = index;
        }
    }
    const gomore_primitives_sleep_stage_classifier_result classified = {
        destination[0],
        {destination[1], destination[2], destination[3]},
        (int8_t)selected,
    };
    *result = classified;
    state->last_tensor_binding = 0u;
    return true;
}

bool gomore_primitives_sleep_stage_stream_update(
    gomore_primitives_sleep_stage_stream_state *state,
    uint32_t timestamp,
    const gomore_primitives_sleep_stage_peak_input *peaks,
    const uint8_t *activity_record, size_t activity_record_length,
    const gomore_primitives_sleep_stage_status *status,
    uint8_t output[3],
    const uint8_t *mode_table, size_t mode_table_length,
    gomore_primitives_tensor_construct_binding_fn construct_tensor,
    gomore_primitives_sleep_stage_classify_fn classify,
    void *classify_context) {
    if (state == NULL || peaks == NULL || activity_record == NULL ||
            activity_record_length < 27u || status == NULL || output == NULL ||
            state->peak_count > 136u ||
            (peaks->count_with_flags & UINT8_C(0x7F)) > 16u) {
        return false;
    }
    const bool should_open = state->active == 0u &&
        (activity_record[26] & 1u) != 0u;
    const bool remains_active = state->active > 1u ||
        (state->active == 1u && (activity_record[26] & 1u) != 0u) ||
        should_open;
    const bool will_classify = state->classifier_iteration != 0u ||
        (remains_active && state->batch_count == 31u);
    if ((should_open && construct_tensor == NULL) ||
            (will_classify && classify == NULL)) {
        return false;
    }
    uint8_t mode_record[11];
    if (will_classify &&
            !gomore_primitives_table_record11(
                mode_table, mode_table_length, (int32_t)state->mode,
                mode_record)) {
        return false;
    }

    output[1] = 0u;
    if (!gomore_primitives_fill_packed_time_gap(
            state, sizeof(*state), timestamp)) {
        return false;
    }
    if (should_open) {
        if (!gomore_primitives_sleep_engine_open(
                state, sizeof(*state), construct_tensor)) {
            return false;
        }
    } else if (state->active == 1u &&
            (activity_record[26] & 1u) == 0u) {
        if (!gomore_primitives_clear_flag_1000(
                (uint8_t *)(void *)state, sizeof(*state))) {
            return false;
        }
    }

    if (state->active == 0u) {
        if (!gomore_primitives_packed_2bit_set(
                state->packed_stages, sizeof(state->packed_stages),
                timestamp / 30u,
                (uint8_t)((status->packed_value & UINT8_C(0x7F)) << 1u))) {
            return false;
        }
    } else {
        const size_t input_count =
            (size_t)(peaks->count_with_flags & UINT8_C(0x7F));
        for (size_t index = 0u; index < input_count; ++index) {
            const uint16_t position = (uint16_t)(
                (uint16_t)peaks->positions[index] +
                (uint16_t)((uint16_t)state->batch_count * UINT16_C(25)));
            const size_t count = state->peak_count;
            if (count < 136u && (count == 0u ||
                    (uint16_t)state->peaks[count - 1u] < position)) {
                state->peaks[count] = (int16_t)position;
                state->peak_count = (uint8_t)(count + 1u);
            }
        }
        state->batch_count = (uint8_t)(state->batch_count + 1u);
        if (state->batch_count == 32u) {
            if (!gomore_primitives_sleep_peak_window_update(
                    state->peaks, 136u, state->peak_count, state->mode,
                    &state->update_counter, state->stage_window, 90u)) {
                return false;
            }
            state->classifier_iteration = 1u;
            size_t peak_count = state->peak_count;
            if (!gomore_primitives_sleep_peak_tail_rebase(
                    state->peaks, 136u, &peak_count)) {
                return false;
            }
            state->peak_count = (uint8_t)peak_count;
            state->batch_count = 2u;
        }
    }

    if (state->classifier_iteration != 0u) {
        gomore_primitives_sleep_stage_classifier_result result = {
            0.0f, {0.0f, 0.0f, 0.0f}, -1,
        };
        if (!classify(
                &result, state, state->classifier_iteration,
                (const int8_t *)(const void *)&mode_record[7],
                classify_context)) {
            return false;
        }
        state->classifier_iteration =
            (uint8_t)(state->classifier_iteration + 1u);
        if (result.selected >= 0) {
            if (result.selected > 3) {
                return false;
            }
            state->classifier_iteration = 0u;
            for (size_t index = 0u; index < 60u; ++index) {
                state->stage_window[index] = state->stage_window[index + 30u];
            }
            int8_t selected = result.selected;
            if (state->active != 0u && selected == 0) {
                selected = (int8_t)(
                    gomore_primitives_float_argmax_above_floor(
                        result.candidates, 3u) + 1);
            }

            float coefficient = (float)mode_record[6];
            coefficient *= bits_float(UINT32_C(0x3C23D70A));
            const float condition = status->value +
                coefficient * bits_float(UINT32_C(0x3FBF9D06));
            const bool positive = condition > 0.0f;
            if (mode_record[5] == 1u) {
                if (status->enabled != 0u &&
                        (positive || selected != 0)) {
                    selected = (int8_t)(
                        gomore_primitives_float_argmax_above_floor(
                            result.candidates, 3u) + 1);
                }
            } else if (mode_record[5] == 2u) {
                if (status->enabled != 0u) {
                    selected = positive
                        ? (int8_t)(
                            gomore_primitives_float_argmax_above_floor(
                                result.candidates, 3u) + 1)
                        : 0;
                }
            } else if (mode_record[5] == 3u &&
                    status->enabled != 0u && !positive) {
                selected = 0;
            }
            state->selected_stage = selected;
            output[0] = (uint8_t)selected;
            output[1] = 1u;
            if (!gomore_primitives_packed_2bit_set(
                    state->packed_stages, sizeof(state->packed_stages),
                    (timestamp / 30u - 1u) % UINT32_C(0xB40),
                    (uint8_t)selected)) {
                return false;
            }
        }
    }

    if (state->active == 0u) {
        output[0] = 0u;
        output[2] = 0u;
    } else {
        const uint8_t mode = state->mode;
        const uint16_t counter = state->update_counter;
        output[2] = (uint8_t)(mode < 100u ||
            ((counter % 6u) < 3u && mode != 101u && mode != 102u) ||
            ((counter % 9u) < 3u && mode == 101u) ||
            ((counter % 12u) < 3u && mode == 102u));
    }
    state->previous_packed_value = status->packed_value;
    state->previous_timestamp = timestamp;
    return true;
}

bool gomore_primitives_peak_candidate_match(
    const float *signal, size_t signal_count,
    uint8_t candidates[20], uint8_t references[20],
    uint8_t *candidate_count, uint8_t *reference_count,
    float *median_spacing, float workspace[25],
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_float_unary_fn square_root) {
    if (signal == NULL || candidates == NULL || references == NULL ||
            candidate_count == NULL || reference_count == NULL ||
            median_spacing == NULL || workspace == NULL ||
            qsort_provider == NULL || compare == NULL || power == NULL ||
            square_root == NULL || *candidate_count > 20u ||
            *reference_count > 20u) {
        return false;
    }
    for (size_t index = 0u; index < *candidate_count; ++index) {
        if ((size_t)candidates[index] >= signal_count) {
            return false;
        }
    }

    *median_spacing = 0.0f;
    if (*candidate_count < 2u || *reference_count < 2u) {
        *candidate_count = 0u;
        *reference_count = 0u;
        return false;
    }

    uint8_t original_references[20] = {0u};
    uint8_t filtered_candidates[20] = {0u};
    const size_t original_reference_count = *reference_count;
    for (size_t index = 0u; index < original_reference_count; ++index) {
        original_references[index] = references[index];
    }
    for (size_t index = 0u; index < 25u; ++index) {
        workspace[index] = index < *candidate_count
            ? signal[candidates[index]] : 0.0f;
    }

    float deviation = 0.0f;
    if (!gomore_primitives_standard_deviation(
            workspace, *candidate_count, power, square_root, &deviation)) {
        return false;
    }
    const float mean = gomore_primitives_mean(workspace, *candidate_count);
    size_t filtered_count = 0u;
    if (deviation > mean) {
        if (!gomore_primitives_sort_float_subrange(
                workspace, 25u, 0u, (size_t)*candidate_count - 1u,
                qsort_provider, compare)) {
            return false;
        }
        const size_t lower = (size_t)((double)*candidate_count * 0.25);
        const size_t upper = (size_t)((double)*candidate_count * 0.75);
        float trimmed_sum = 0.0f;
        for (size_t index = lower; index <= upper; ++index) {
            trimmed_sum += workspace[index];
        }
        const float trimmed_mean = trimmed_sum /
            (float)((upper - lower) + 1u);
        const float threshold = trimmed_mean +
            (workspace[upper] - workspace[lower]) * 3.0f;
        for (size_t index = 0u; index < *candidate_count; ++index) {
            if (signal[candidates[index]] < threshold) {
                filtered_candidates[filtered_count++] = candidates[index];
            }
        }
    } else {
        filtered_count = *candidate_count;
        for (size_t index = 0u; index < filtered_count; ++index) {
            filtered_candidates[index] = candidates[index];
        }
    }
    if (filtered_count < 2u) {
        *candidate_count = 0u;
        *reference_count = 0u;
        return false;
    }

    for (size_t index = 0u; index < 20u; ++index) {
        candidates[index] = 0u;
        references[index] = 0u;
    }
    for (size_t index = 0u; index + 1u < filtered_count; ++index) {
        workspace[index] = (float)((int32_t)filtered_candidates[index + 1u] -
                                  (int32_t)filtered_candidates[index]);
    }
    float median = 0.0f;
    if (!gomore_primitives_median(
            workspace, filtered_count - 1u,
            qsort_provider, compare, &median)) {
        *candidate_count = 0u;
        *reference_count = 0u;
        return false;
    }

    size_t reference_index = 0u;
    size_t output_count = 0u;
    for (size_t candidate_index = 0u;
            candidate_index < filtered_count; ++candidate_index) {
        const uint8_t candidate = filtered_candidates[candidate_index];
        while (reference_index < original_reference_count &&
                candidate > original_references[reference_index]) {
            const int32_t difference = (int32_t)candidate -
                (int32_t)original_references[reference_index];
            if ((double)difference < (double)median * 0.75) {
                break;
            }
            ++reference_index;
        }
        if (reference_index >= original_reference_count) {
            break;
        }

        const uint8_t reference = original_references[reference_index];
        const int32_t reference_difference =
            (int32_t)candidate - (int32_t)reference;
        if (reference_difference > 0 &&
                (double)reference_difference < (double)median * 0.75) {
            if (reference != 0u && candidate > 12u) {
                candidates[output_count] = candidate;
                references[output_count] = reference;
                ++reference_index;
                ++output_count;
            }
            continue;
        }

        const uint8_t previous = output_count == 0u
            ? 0u : candidates[output_count - 1u];
        const int32_t spacing = (int32_t)candidate - (int32_t)previous;
        if ((double)median * 0.75 >= (double)spacing ||
                (double)median * 1.25 < (double)spacing) {
            continue;
        }
        const int32_t valley = gomore_primitives_quantized_argmin(
            signal, (uint32_t)previous + 1u, candidate);
        if (valley < 0 || (size_t)valley >= signal_count) {
            *candidate_count = 0u;
            *reference_count = 0u;
            *median_spacing = 0.0f;
            return false;
        }
        const int32_t tail = (int32_t)candidate - valley;
        if ((double)median * 0.1 >= (double)tail ||
                (double)median * 0.5 < (double)tail) {
            continue;
        }
        candidates[output_count] = candidate;
        references[output_count] = (uint8_t)valley;
        ++output_count;
    }

    if (output_count < 2u) {
        *candidate_count = 0u;
        *reference_count = 0u;
        *median_spacing = 0.0f;
        return false;
    }
    *candidate_count = (uint8_t)output_count;
    *reference_count = (uint8_t)output_count;
    for (size_t index = 0u; index + 1u < output_count; ++index) {
        workspace[index] = (float)((int32_t)candidates[index + 1u] -
                                  (int32_t)candidates[index]);
    }
    if (!gomore_primitives_median(
            workspace, output_count - 1u,
            qsort_provider, compare, median_spacing)) {
        *candidate_count = 0u;
        *reference_count = 0u;
        *median_spacing = 0.0f;
        return false;
    }
    return true;
}

bool gomore_primitives_motion_classifier_finalize(
    uint8_t state[17], size_t state_length,
    const uint8_t *features, size_t feature_length,
    uint8_t output[3], size_t output_length,
    gomore_primitives_state1_cadence_estimate_fn estimate_state1) {
    if (state == NULL || state_length < 17u || features == NULL ||
            feature_length < 0x38u || output == NULL || output_length < 3u) {
        return false;
    }

    const int32_t mode = (int32_t)(int8_t)output[0];
    int32_t cadence = 0;
    uint8_t consensus = 0u;
    const float first = bits_float(load_u32_le(&features[0x2Cu]));
    const float middle = bits_float(load_u32_le(&features[0x30u]));
    const float latest = bits_float(load_u32_le(&features[0x34u]));
    if (mode == 2) {
        cadence = (int32_t)gomore_primitives_state2_cadence_estimate(
            first, middle, latest, &consensus);
        if (cadence <= 120 || cadence >= 220) {
            cadence = output[2];
        }
    } else if (mode == 1) {
        const gomore_primitives_state1_cadence_estimate_fn estimator =
            estimate_state1 != NULL
                ? estimate_state1
                : gomore_primitives_state1_cadence_estimate;
        cadence = (int32_t)estimator(
            first, middle, latest, &consensus);
        if ((int8_t)consensus == 0 ||
                ((int8_t)consensus == 1 &&
                 (int32_t)float_bits(middle) <=
                     (int32_t)UINT32_C(0x42A00000))) {
            const int32_t previous = output[2];
            int32_t delta = cadence - previous * 2;
            if (delta < 0) {
                delta = -delta;
            }
            if (delta < 10) {
                cadence = previous;
            } else {
                delta = cadence * 2 - previous;
                if (delta < 0) {
                    delta = -delta;
                }
                if (delta < 7) {
                    cadence = previous;
                }
            }
        }
        if ((uint32_t)(cadence - 51) <= 14u) {
            const int32_t previous =
                (int32_t)bits_float(load_u32_le(&features[0x10u]));
            int32_t delta = cadence * 2 - previous;
            if (delta < 0) {
                delta = -delta;
            }
            if (delta <= 6) {
                cadence = previous;
            }
        }
        if (cadence <= 50 || cadence >= 150) {
            cadence = output[2];
        }
    }

    (void)gomore_primitives_shift_u8_window5(
        &state[10], (uint8_t)cadence);
    if (mode == 2 && cadence > 140) {
        cadence = gomore_primitives_dominant_quantized_u8_mean5(&state[10]);
    }
    (void)gomore_primitives_shift_two_u8_windows5(
        &state[5], &state[0], (uint8_t)cadence, (uint8_t)mode);

    int32_t selected_cadence = 0;
    int32_t selected_mode = -1;
    if (!gomore_primitives_dual_dominant_u8_select(
            &state[5], (const int8_t *)(const void *)&state[0],
            &selected_cadence, &selected_mode)) {
        return false;
    }
    output[1] = (uint8_t)selected_mode;
    output[2] = (uint8_t)selected_cadence;
    return true;
}

bool gomore_primitives_sps_state_initialize(
    void *state, size_t state_length) {
    if (state == NULL || state_length < 0x1F8u) {
        return false;
    }
    uint8_t *bytes = state;
    clear_bytes(bytes, 0x1F8u);
    static const size_t minus_one_offsets[15] = {
        0x10u, 0x6Cu, 0xDCu, 0xE4u, 0x14u,
        0x18u, 0x1Cu, 0x140u, 0x144u, 0x148u,
        0x14Cu, 0x150u, 0x154u, 0x158u, 0x15Cu,
    };
    for (size_t index = 0u; index < 15u; ++index) {
        store_u32_le(&bytes[minus_one_offsets[index]],
                     UINT32_C(0xBF800000));
    }
    store_u32_le(&bytes[0x164u], UINT32_MAX);
    store_u32_le(&bytes[0x168u], UINT32_MAX);
    bytes[0x94u] = 1u;
    bytes[0x0Cu] = 1u;
    bytes[0x34u] = 1u;
    store_u32_le(&bytes[0x5Cu], UINT32_C(0xC97423F0));
    store_u32_le(&bytes[0x58u], UINT32_C(0xC479C000));
    store_u32_le(&bytes[0x54u], UINT32_C(0xC479C000));
    store_u32_le(&bytes[0x60u], UINT32_C(0xBF800000));
    store_u32_le(&bytes[0x64u], UINT32_C(0xBF800000));
    bytes[0x1C0u] = 1u;
    return true;
}

float gomore_primitives_rolling_mean5_update(
    float value, float window[5], uint32_t observation_index) {
    if (window == NULL) {
        return 0.0f;
    }
    if (observation_index > 3u) {
        window[4] = value;
        float total = 0.0f;
        for (size_t index = 0u; index < 5u; ++index) {
            total += window[index];
        }
        for (size_t index = 0u; index < 4u; ++index) {
            window[index] = window[index + 1u];
        }
        return total / 5.0f;
    }
    window[observation_index] = value;
    float total = 0.0f;
    for (uint32_t index = 0u; index <= observation_index; ++index) {
        total += window[index];
    }
    return total / (float)(observation_index + 1u);
}

float gomore_primitives_nearest_nonzero3(
    float target, const float values[3]) {
    if (values == NULL) {
        return 0.0f;
    }
    float selected = values[0] != 0.0f ? values[0] : 0.0f;
    for (size_t index = 1u; index < 3u; ++index) {
        const float candidate = values[index];
        if (candidate != 0.0f) {
            double candidate_distance = (double)(candidate - target);
            double selected_distance = (double)(selected - target);
            if (candidate_distance < 0.0) {
                candidate_distance = -candidate_distance;
            }
            if (selected_distance < 0.0) {
                selected_distance = -selected_distance;
            }
            if (candidate_distance <= selected_distance) {
                selected = candidate;
            }
        }
    }
    return selected;
}

float gomore_primitives_activity_scaled_quadratic_difference(
    float primary, float reference, float scale, float gain,
    gomore_primitives_float_binary_fn power) {
    if (power == NULL) {
        return 0.0f;
    }
    float difference = primary - reference;
    if (difference < 0.0f) {
        difference = -difference;
    }
    if ((int32_t)float_bits(difference) > INT32_C(0x40600000)) {
        difference = 3.5f;
    }
    if (difference < 0.0f) {
        difference = -difference;
    }
    const float attenuation = 1.0f - difference *
        bits_float(UINT32_C(0xBE924745));
    const float offset = primary * bits_float(UINT32_C(0x3C9BA5E3));
    const float primary_square = power(primary, 2.0f);
    const float shifted_square = power(primary - offset, 2.0f);
    float factor = attenuation * 2.0f;
    factor *= 0.5f;
    factor *= gain;
    factor *= scale;
    return ((primary_square - shifted_square) * factor) / 60.0f;
}

float gomore_primitives_affine_reciprocal_model4_evaluate(
    const float values[4],
    const gomore_primitives_affine_reciprocal_model4 *model) {
    if (values == NULL || model == NULL) {
        return 0.0f;
    }
    const float reciprocal = values[1] == 0.0f
        ? 0.0f : 1.0f / values[1];
    const float affine =
        model->coefficients[0] * values[0] +
        model->coefficients[1] * values[1] +
        model->coefficients[2] * reciprocal +
        model->coefficients[3] * values[2] +
        model->coefficients[4] * values[3] +
        model->coefficients[5];
    const float scaled = (values[0] / 50.0f) * affine;
    return (float)((double)scaled / 3.6);
}

float gomore_primitives_bounded_linear_complement(
    float primary, float secondary) {
    if ((int32_t)float_bits(primary) > INT32_C(0x40A00000) ||
            (int32_t)float_bits(secondary) > INT32_C(0x3F333333)) {
        return 0.0f;
    }
    const double normalized = (double)secondary / 0.7 +
        (double)(primary / 5.0f);
    return (float)(1.0 - normalized * 0.5);
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

bool gomore_primitives_locomotion_autocorrelation_analyze(
    const uint16_t samples[100],
    float *first, float *second, float *third, float *fourth, float *fifth,
    uintptr_t first_binding, uintptr_t second_binding) {
    if (samples == NULL || first == NULL || second == NULL || third == NULL ||
            fourth == NULL || fifth == NULL || first_binding == 0u ||
            second_binding == 0u) {
        return false;
    }
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
    const int32_t variance_scale = (energy / 100) * 100;

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
    if (*first >= 0.0f) {
        int32_t band_maximum = -variance_scale;
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
        if (value >= correlation[lag - 1u] &&
                value >= correlation[lag + 1u] &&
                (float)value >= peak_threshold) {
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

    if (*second >= 0.0f) {
        gomore_primitives_direction_change_output direction;
        if (!gomore_primitives_direction_change_statistics(
                (float)(strongest_value - minimum_before_peak), 0.3f,
                GOMORE_PRIMITIVES_DIFFERENCE_INT32,
                correlation, strongest_lag, &direction)) {
            return false;
        }
        turning_counts[0] = direction.direction_changes;
        turning_counts[1] = direction.above_threshold_changes;
        shape[0] = direction.normalized_variation;
        shape[1] = direction.average_completed_run;
        const int32_t direction_count = direction.direction_changes;
        if (direction_count > 4) {
            const float minimum_share = direction_count > 8 ? 0.35f : 0.45f;
            if ((float)direction.above_threshold_changes /
                    (float)direction_count < minimum_share) {
                *second = -1.0f;
            }
        }
    }
    if (peak_count > 7u &&
            (float)strongest_value > (float)variance_scale * 0.35f &&
            peaks[7] < 48u) {
        *second = -1.0f;
    }
    if ((float)minimum_before_peak > (float)variance_scale * -0.1f) {
        *second = -1.0f;
    }

    uint8_t selected_lag = 0u;
    if (*second >= 0.0f && peak_count > 2u) {
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
    return true;
}

bool gomore_primitives_locomotion_autocorrelation_wrapper(
    bool enabled, const uint16_t *samples, float outputs[5],
    uintptr_t first_binding, uintptr_t second_binding,
    gomore_primitives_autocorrelation_analyze_fn analyze) {
    if (outputs == NULL || (enabled && (samples == NULL || analyze == NULL))) {
        return false;
    }
    outputs[0] = -1.0f;
    outputs[1] = -1.0f;
    outputs[2] = 0.0f;
    outputs[3] = 0.0f;
    outputs[4] = 0.0f;
    if (enabled) {
        if (!analyze(samples, &outputs[0], &outputs[1], &outputs[2],
                     &outputs[3], &outputs[4], first_binding,
                     second_binding)) {
            return false;
        }
    }
    return true;
}

bool gomore_primitives_select_heart_rate(
    uint8_t state, float direct,
    const gomore_primitives_hr_candidate *estimated,
    gomore_primitives_hr_selection *output) {
    if (estimated == NULL || output == NULL) {
        return false;
    }
    if (state == 0u && gomore_primitives_float_in_encoded_range(direct)) {
        output->heart_rate = direct;
        output->quality = 1u;
        output->source = 0u;
    } else if (gomore_primitives_float_in_encoded_range(
                   estimated->heart_rate)) {
        output->heart_rate = estimated->heart_rate;
        output->quality = estimated->quality;
        output->source = 1u;
    } else {
        output->heart_rate = 0.0f;
        output->quality = 0u;
        output->source = UINT8_C(0x40);
    }
    return true;
}

bool gomore_primitives_sps_model_dispatch(
    void *state, size_t state_length, const float values[4],
    gomore_primitives_feature_model_fn primary_model0,
    gomore_primitives_feature_model_fn secondary_model0,
    gomore_primitives_feature_model_fn primary_model1,
    gomore_primitives_feature_model_fn secondary_model1,
    gomore_primitives_state_adjust_fn adjust,
    gomore_primitives_state_pair_commit_fn commit,
    float *primary, float *secondary) {
    if (state == NULL || state_length < 0x1Cu || values == NULL ||
            primary_model0 == NULL || secondary_model0 == NULL ||
            primary_model1 == NULL || secondary_model1 == NULL ||
            adjust == NULL || commit == NULL || primary == NULL ||
            secondary == NULL) {
        return false;
    }
    const uint8_t *bytes = state;
    float local_primary;
    float local_secondary;
    if (load_u32_le(bytes) == 0u) {
        local_primary = primary_model0(values);
        local_secondary = secondary_model0(values);
    } else {
        local_primary = primary_model1(values);
        local_secondary = secondary_model1(values);
    }
    if (load_u32_le(&bytes[0x18u]) == 1u) {
        local_secondary = adjust(local_primary, state);
    }
    commit(state, local_primary, local_secondary);
    *primary = local_primary;
    *secondary = local_secondary;
    return true;
}

bool gomore_primitives_sps_accelerometer_candidate_update(
    gomore_primitives_sps_candidate_state *state, uint32_t elapsed_updates,
    const gomore_primitives_sps_features *features,
    const gomore_primitives_sps_motion *motion, float height_centimeters,
    const gomore_primitives_sps_candidate_providers *providers,
    gomore_primitives_sps_candidate_output *output) {
    if (state == NULL || features == NULL || motion == NULL ||
            providers == NULL || output == NULL ||
            providers->state2_primary == NULL ||
            providers->state2_secondary == NULL ||
            providers->state1_primary == NULL ||
            providers->state1_secondary == NULL ||
            providers->adjust == NULL || providers->commit == NULL) {
        return false;
    }

    if (elapsed_updates < 2u) {
        if (motion->smoothed_state == -2 && state->startup_cooldown == 0u) {
            state->missing_update_count += 1u;
        }
    } else {
        state->missing_update_count += elapsed_updates - 1u;
        if (state->latest_primary_model > 0.0f && elapsed_updates < 8u) {
            gomore_primitives_sps_model_state *replay = NULL;
            if (motion->raw_state == 2) {
                replay = &state->state2_model;
            } else if (motion->raw_state == 1) {
                replay = &state->state1_model;
            }
            if (replay != NULL) {
                for (uint32_t index = 1u; index < elapsed_updates; ++index) {
                    (void)gomore_primitives_accumulate_pair(
                        replay, sizeof(*replay), state->latest_primary_model,
                        state->latest_candidate);
                }
            }
        }
    }
    if (state->startup_cooldown != 0u) {
        state->startup_cooldown -= 1u;
    }

    float cadence_reference = 0.0f;
    if (motion->raw_state == 2) {
        cadence_reference = features->values[5];
    } else if (motion->raw_state == 1) {
        cadence_reference = features->values[4];
    }
    float relative_difference;
    if (motion->cadence == 0u) {
        relative_difference = cadence_reference == 0.0f ? 0.0f : 1.0f;
    } else {
        double difference =
            (double)cadence_reference - (double)motion->cadence;
        if (difference < 0.0) {
            difference = -difference;
        }
        relative_difference =
            (float)(difference / (double)motion->cadence);
    }
    if (motion->smoothed_state != motion->raw_state ||
            !(relative_difference < 0.2f) || motion->raw_state == -1) {
        output->candidate = -1.0f;
        output->status = 1u;
        return true;
    }

    gomore_primitives_sps_model_state *model_state = NULL;
    float values[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    float *smoothed = NULL;
    double new_weight = 0.0;
    double prior_weight = 0.0;
    float minimum = 0.0f;
    float maximum = 0.0f;
    if (motion->raw_state == 2) {
        model_state = &state->state2_model;
        values[0] = height_centimeters;
        values[1] = features->values[5];
        values[2] = features->values[2];
        smoothed = &state->smoothed_state2;
        new_weight = 0.25;
        prior_weight = 0.75;
        minimum = 6.0f;
        maximum = model_state->calibration_enabled == 1u ? 20.0f : 14.0f;
    } else if (motion->raw_state == 1) {
        model_state = &state->state1_model;
        values[0] = features->values[4];
        values[1] = height_centimeters;
        values[2] = features->values[0];
        values[3] = features->values[3];
        smoothed = &state->smoothed_state1;
        new_weight = 0.15;
        prior_weight = 0.85;
        minimum = model_state->calibration_enabled == 1u ? 2.0f : 4.0f;
        maximum = 7.0f;
    } else {
        output->candidate = 0.0f;
        output->status = 1u;
        return true;
    }

    float primary_model;
    float candidate;
    if (!gomore_primitives_sps_model_dispatch(
            model_state, sizeof(*model_state), values,
            providers->state2_primary, providers->state2_secondary,
            providers->state1_primary, providers->state1_secondary,
            providers->adjust, providers->commit,
            &primary_model, &candidate)) {
        return false;
    }
    state->latest_candidate = candidate;
    state->latest_primary_model = primary_model;
    if (*smoothed <= 0.0f) {
        *smoothed = candidate;
    } else {
        *smoothed = (float)((double)candidate * new_weight +
                            (double)*smoothed * prior_weight);
    }

    float bounded_candidate = *smoothed;
    if (bounded_candidate > maximum) {
        bounded_candidate = maximum;
    }
    if (bounded_candidate < minimum) {
        bounded_candidate = minimum;
    }
    output->candidate = bounded_candidate;
    output->status = model_state->calibration_enabled == 1u ? 3u : 2u;
    return true;
}

gomore_primitives_health_lifecycle_result
gomore_primitives_health_lifecycle_initialize(
    gomore_primitives_health_lifecycle_state *state,
    bool force_default_previous,
    uint8_t previous_data[GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES],
    const uint8_t default_profile[GOMORE_PRIMITIVES_USER_PROFILE_BYTES],
    uint8_t output_descriptor[GOMORE_PRIMITIVES_OUTPUT_DESCRIPTOR_BYTES],
    uint32_t output_storage_address, uint32_t output_record_address,
    const gomore_primitives_health_lifecycle_providers *providers,
    int32_t *provider_status) {
    if (state == NULL || previous_data == NULL || default_profile == NULL ||
            output_descriptor == NULL || providers == NULL ||
            output_storage_address > UINT32_MAX - 300u ||
            providers->query_previous_size == NULL ||
            providers->query_engine_size == NULL ||
            providers->configure_authorization == NULL ||
            providers->restore_previous == NULL ||
            providers->crash_record_present == NULL ||
            providers->restore_crash_previous == NULL ||
            providers->clear_crash_previous == NULL ||
            providers->load_user_profile == NULL ||
            providers->timestamp == NULL ||
            providers->initialize_health == NULL ||
            providers->apply_profile_state == NULL ||
            providers->configure_state_mode == NULL ||
            providers->subscribe == NULL) {
        return GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_BAD_ARGUMENT;
    }

    (void)providers->query_previous_size(providers->context);
    (void)providers->query_engine_size(providers->context);
    state->auth_pending = 0u;
    int32_t status =
        providers->configure_authorization(providers->context);
    if (status != 0) {
        state->auth_retry_attempted = 1u;
        state->auth_pending = 1u;
        status = providers->configure_authorization(providers->context);
        if (status != 0) {
            if (provider_status != NULL) {
                *provider_status = status;
            }
            return GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_AUTH_FAILED;
        }
        state->auth_pending = 0u;
    }

    if (!providers->restore_previous(providers->context, previous_data)) {
        clear_bytes(previous_data, GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES);
    }
    if (!force_default_previous &&
            providers->crash_record_present(providers->context) != 0) {
        size_t restored_length = 0u;
        if (providers->restore_crash_previous(
                providers->context, previous_data, &restored_length) &&
                restored_length == GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES) {
            providers->clear_crash_previous(providers->context);
        }
    }

    uint8_t profile[GOMORE_PRIMITIVES_USER_PROFILE_BYTES];
    clear_bytes(profile, sizeof(profile));
    if (!providers->load_user_profile(providers->context, profile)) {
        for (size_t index = 0u; index < sizeof(profile); ++index) {
            profile[index] = default_profile[index];
        }
    }
    if (force_default_previous) {
        clear_bytes(previous_data, GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES);
    }

    const uint32_t timestamp = providers->timestamp(providers->context);
    status = providers->initialize_health(
        providers->context, timestamp, profile, previous_data);
    if (status != 0) {
        if (status != -5) {
            if (provider_status != NULL) {
                *provider_status = status;
            }
            return GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_INITIALIZE_FAILED;
        }
        clear_bytes(previous_data, GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES);
        status = providers->initialize_health(
            providers->context, timestamp, profile, previous_data);
        if (status != 0) {
            if (provider_status != NULL) {
                *provider_status = status;
            }
            return GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_INITIALIZE_FAILED;
        }
    }

    state->initialized = 1u;
    clear_bytes(output_descriptor,
                GOMORE_PRIMITIVES_OUTPUT_DESCRIPTOR_BYTES);
    store_u32_le(&output_descriptor[8], output_storage_address);
    store_u32_le(&output_descriptor[0x0Cu], output_storage_address + 100u);
    store_u32_le(&output_descriptor[0x10u], output_storage_address + 200u);
    store_u32_le(&output_descriptor[0x18u], output_storage_address + 300u);
    store_u32_le(&output_descriptor[0x20u], output_record_address);
    providers->apply_profile_state(providers->context, 1u, 0u);
    providers->configure_state_mode(providers->context, 1u, 0x66u);
    if (state->subscription == 0u) {
        state->subscription = providers->subscribe(
            providers->context, 0u, providers->event_callback,
            providers->event_callback_context);
    }
    if (provider_status != NULL) {
        *provider_status = 0;
    }
    return GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_OK;
}

static uint32_t base64_stock_value(uint8_t value, bool *padding) {
    if (value == (uint8_t)'+') {
        return 62u;
    }
    if (value == (uint8_t)'=') {
        *padding = true;
        return 0u;
    }
    if (value == (uint8_t)'/') {
        return 63u;
    }
    if (value < (uint8_t)':') {
        return (uint32_t)value + 4u;
    }
    if (value < (uint8_t)'[') {
        return (uint32_t)value - (uint32_t)'A';
    }
    return (uint32_t)value - (uint32_t)'G';
}

bool gomore_primitives_base64_decode_blocks(
    const uint8_t *input, size_t input_length,
    uint8_t *output, size_t output_capacity, size_t *written) {
    if (written == NULL || input_length % 4u != 0u ||
            (input == NULL && input_length != 0u) ||
            (output == NULL && input_length != 0u)) {
        return false;
    }
    const size_t produced = (input_length / 4u) * 3u;
    if (output_capacity < produced) {
        return false;
    }
    size_t padding_count = 0u;
    size_t output_index = 0u;
    for (size_t offset = 0u; offset < input_length; offset += 4u) {
        uint32_t aggregate = 0u;
        for (size_t index = 0u; index < 4u; ++index) {
            bool padding = false;
            const uint32_t decoded = base64_stock_value(
                input[offset + index], &padding);
            aggregate += decoded << ((3u - index) * 6u);
            if (padding) {
                ++padding_count;
            }
        }
        output[output_index++] = (uint8_t)(aggregate >> 16u);
        output[output_index++] = (uint8_t)(aggregate >> 8u);
        output[output_index++] = (uint8_t)aggregate;
    }
    if (padding_count > produced) {
        return false;
    }
    *written = produced - padding_count;
    return true;
}

uint8_t gomore_primitives_dominant_quantized_u8_mean5(
    const uint8_t values[5]) {
    if (values == NULL) {
        return 0u;
    }
    int32_t quantized[5];
    size_t quantized_count = 0u;
    for (size_t index = 0u; index < 5u; ++index) {
        if (values[index] != 0u) {
            quantized[quantized_count++] =
                (int32_t)((uint32_t)values[index] / 80u) * 80;
        }
    }
    if (quantized_count > 2u) {
        int32_t dominant = -1;
        size_t dominant_count = 0u;
        if (gomore_primitives_dominant_sorted_i32(
                quantized, quantized_count, &dominant, &dominant_count) &&
                dominant_count >= quantized_count / 2u) {
            return (uint8_t)gomore_primitives_filtered_u8_mean(
                values, 5u, dominant, 80);
        }
    }
    return values[4];
}

bool gomore_primitives_dual_dominant_u8_select(
    const uint8_t values[5], const int8_t categories[5],
    int32_t *value_output, int32_t *category_output) {
    if (values == NULL || categories == NULL || value_output == NULL ||
            category_output == NULL) {
        return false;
    }
    int32_t candidates[5] = {0, 0, 0, 0, 0};
    size_t candidate_count = 0u;
    for (size_t index = 0u; index < 5u; ++index) {
        if (categories[index] != -2) {
            candidates[candidate_count++] = categories[index];
        }
    }
    if (candidate_count > 2u) {
        int32_t dominant = -1;
        size_t dominant_count = 0u;
        if (!gomore_primitives_dominant_sorted_i32(
                candidates, candidate_count, &dominant, &dominant_count)) {
            return false;
        }
        *category_output = dominant_count > candidate_count / 2u
            ? dominant : -1;
    }

    const int32_t divisor = categories[4] == 2 ? 50 : 35;
    candidate_count = 0u;
    for (size_t index = 0u; index < 5u; ++index) {
        if (values[index] != 0u) {
            candidates[candidate_count++] =
                ((int32_t)values[index] / divisor) * divisor;
        }
    }
    if (candidate_count > 2u) {
        int32_t dominant = -1;
        size_t dominant_count = 0u;
        if (!gomore_primitives_dominant_sorted_i32(
                candidates, candidate_count, &dominant, &dominant_count)) {
            return false;
        }
        *value_output = dominant_count < candidate_count / 2u
            ? 0
            : gomore_primitives_filtered_u8_mean(
                values, 5u, dominant, divisor);
    }
    return true;
}

uint32_t gomore_primitives_update_failure_counter(
    uint32_t status, uint32_t timestamp, uint8_t *counter,
    gomore_primitives_update_failure_log_fn log_failure,
    gomore_primitives_simple_fn reset_provider) {
    if (counter == NULL) {
        return 0u;
    }
    if (status == 0u) {
        *counter = 0u;
        return 1u;
    }
    if (*counter <= 2u && log_failure != NULL) {
        log_failure(status, timestamp);
    }
    *counter = (uint8_t)(*counter + 1u);
    if (*counter > 59u) {
        *counter = 0u;
        if (reset_provider != NULL) {
            reset_provider();
        }
    }
    return 0u;
}

int32_t gomore_primitives_shift_i16_trend_gate5(
    int16_t history[5], int32_t sample) {
    if (history == NULL) {
        return -1;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        history[index] = history[index + 1u];
    }
    history[4] = (int16_t)sample;
    if (sample > 0) {
        return 1;
    }
    if (sample > -500 && history[3] > -1800 && history[2] > -1200 &&
            history[1] > 1000 && history[0] > 1000) {
        return 1;
    }
    return -1;
}

bool gomore_primitives_sps_refresh_affine_pairs(
    const float source[4], float first[2], uint32_t *first_mode,
    float second[2], uint32_t *second_mode) {
    if (source == NULL || first == NULL || first_mode == NULL ||
            second == NULL || second_mode == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 2u; ++index) {
        if (source[index] != 0.0f) {
            first[index] = source[index];
        }
        if (source[index + 2u] != 0.0f) {
            second[index] = source[index + 2u];
        }
    }
    *first_mode = first[0] == 1.0f && first[1] == 0.0f ? 0u : 1u;
    *second_mode = second[0] == 1.0f && second[1] == 0.0f ? 0u : 1u;
    return true;
}

bool gomore_primitives_positive_quadratic_roots(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float roots[2], gomore_primitives_float_binary_fn power) {
    if (roots == NULL || power == NULL) {
        return false;
    }
    const float discriminant = power(coefficient_b, 2.0f) -
        coefficient_a * 4.0f * coefficient_c;
    if (discriminant < 0.0f || coefficient_a == 0.0f) {
        roots[0] = 0.0f;
        roots[1] = 0.0f;
        return true;
    }
    float root = (power(discriminant, 0.5f) - coefficient_b) /
        (coefficient_a * 2.0f);
    if (root > 0.0f) {
        roots[0] = root;
    }
    root = (-coefficient_b - power(discriminant, 0.5f)) /
        (coefficient_a * 2.0f);
    if (root > 0.0f) {
        roots[1] = root;
    }
    return true;
}

bool gomore_primitives_activity_score_variability_adjust(
    float *score, const float *const axes[3], bool skip_variability,
    gomore_primitives_float_unary_fn square_root) {
    if (score == NULL || axes == NULL || square_root == NULL ||
            (!skip_variability &&
             (axes[0] == NULL || axes[1] == NULL || axes[2] == NULL))) {
        return false;
    }
    *score *= 0.9f;
    float variability = 0.0f;
    if (!skip_variability) {
        float sum = 0.0f;
        for (size_t index = 0u; index < 25u; ++index) {
            const float magnitude_squared =
                axes[0][index] * axes[0][index] +
                axes[1][index] * axes[1][index] +
                axes[2][index] * axes[2][index];
            const float first_magnitude = square_root(magnitude_squared);
            const float second_magnitude = square_root(magnitude_squared);
            sum += (first_magnitude - 1000.0f) *
                (second_magnitude - 1000.0f);
        }
        variability = square_root(sum / 25.0f);
    }
    if ((int32_t)variability > 200) {
        *score += 0.1f;
    }
    return true;
}

static int32_t low_signed_byte(uint32_t value) {
    const uint32_t low = value & UINT32_C(0xFF);
    return low < UINT32_C(0x80) ? (int32_t)low : (int32_t)low - 256;
}

bool gomore_primitives_epoch_to_civil_time(
    uint32_t timestamp, gomore_primitives_civil_time *output) {
    if (output == NULL) {
        return false;
    }
    output->reserved = 0u;
    output->timestamp = timestamp;
    output->second = (uint8_t)(timestamp % 60u);
    timestamp /= 60u;
    output->minute = (uint8_t)(timestamp % 60u);
    timestamp /= 60u;
    output->hour = (uint8_t)(timestamp % 24u);
    const uint32_t days = timestamp / 24u;
    uint32_t correction =
        (UINT32_C(102032) + days * 4u) / UINT32_C(146097) + 15u;
    int32_t intermediate = (int32_t)(days + correction -
        (correction >> 2u) + UINT32_C(2442113));
    const uint32_t year_base =
        (uint32_t)(intermediate * 20 - 2442) / UINT32_C(7305);
    intermediate = intermediate - (int32_t)(year_base * 365u) -
        (int32_t)(year_base >> 2u);
    correction = (uint32_t)(intermediate * 1000) / UINT32_C(30601);
    if (correction < 14u) {
        output->year = (int16_t)(year_base - UINT32_C(4716));
        output->month = (uint8_t)(correction - 1u);
    } else {
        output->year = (int16_t)(year_base - UINT32_C(4715));
        output->month = (uint8_t)(correction - 13u);
    }
    const int32_t day = low_signed_byte((uint32_t)intermediate) -
        low_signed_byte(correction) * 30 -
        low_signed_byte((correction * UINT32_C(601)) / UINT32_C(1000));
    output->day = (uint8_t)day;
    return true;
}

bool gomore_primitives_copy_algorithm_output_snapshot(
    uint8_t *destination, size_t destination_length,
    const uint8_t *source, size_t source_length) {
    if (destination == NULL || source == NULL ||
            destination_length <
                GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_DESTINATION_BYTES ||
            source_length < GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_SOURCE_BYTES) {
        return false;
    }
    static const uint16_t fields[][3] = {
        {0x58u, 0x224u, 4u}, {0x5Cu, 0x22Cu, 1u},
        {0x48u, 0x254u, 4u}, {0x4Cu, 0x278u, 4u},
        {0x50u, 0x27Cu, 4u}, {0xA0u, 0x184u, 4u},
        {0xA4u, 0x188u, 4u}, {0x60u, 0x2F5u, 1u},
        {0x61u, 0x2F6u, 1u}, {0x62u, 0x2F7u, 1u},
        {0x68u, 0x2C4u, 4u}, {0x6Cu, 0x2C8u, 4u},
        {0x70u, 0x2DEu, 1u}, {0x71u, 0x2DFu, 1u},
        {0x72u, 0x2E0u, 1u}, {0x73u, 0x2E1u, 1u},
        {0x44u, 0x2C2u, 2u}, {0x54u, 0x21Au, 1u},
        {0x33u, 0x219u, 1u}, {0x80u, 0x181u, 1u},
        {0x81u, 0x182u, 1u}, {0x82u, 0x180u, 1u},
        {0x74u, 0x300u, 1u}, {0x75u, 0x301u, 1u},
        {0x78u, 0x308u, 4u}, {0x7Eu, 0x310u, 2u},
        {0x7Cu, 0x30Cu, 2u},
    };
    for (size_t field = 0u; field < sizeof(fields) / sizeof(fields[0]);
            ++field) {
        for (size_t byte = 0u; byte < fields[field][2]; ++byte) {
            destination[(size_t)fields[field][0] + byte] =
                source[(size_t)fields[field][1] + byte];
        }
    }
    return true;
}

bool gomore_primitives_sleep_descriptor_initialize(
    gomore_primitives_sleep_descriptor *descriptor,
    const float history[15], bool use_high_threshold,
    uint32_t current, uint32_t reference, uint8_t profile,
    bool skip_history_scan) {
    if (descriptor == NULL || (!skip_history_scan && history == NULL)) {
        return false;
    }
    clear_bytes((uint8_t *)descriptor, sizeof(*descriptor));
    descriptor->type = 2u;
    descriptor->start = current;
    descriptor->profile = profile;
    const float threshold = use_high_threshold ? 0.8f : 0.7f;
    if (!skip_history_scan) {
        for (uint32_t index = 0u; index < 15u; ++index) {
            const uint32_t elapsed = current - reference - index * 60u;
            const uint32_t minutes = elapsed / 60u;
            uint32_t slot;
            if (elapsed % 60u == 59u) {
                slot = minutes % 15u;
            } else if (minutes == (minutes / 15u) * 15u) {
                slot = 14u;
            } else {
                slot = minutes % 15u - 1u;
            }
            if (history[slot] < threshold) {
                break;
            }
            ++descriptor->preceding_count;
        }
        descriptor->start = current -
            (uint32_t)descriptor->preceding_count * 60u;
    }
    return true;
}

bool gomore_primitives_sliding_window_mean(
    const float *input, size_t rows, size_t columns,
    size_t window, size_t stride, size_t padding,
    float *output, size_t output_capacity, size_t *written) {
    if (written == NULL || window == 0u || stride == 0u ||
            (input == NULL && rows != 0u && columns != 0u) ||
            (output == NULL && rows != 0u)) {
        return false;
    }
    if (padding > (size_t)INT32_MAX / 2u ||
            columns > (size_t)INT32_MAX - padding * 2u ||
            window > (size_t)INT32_MAX || stride > (size_t)INT32_MAX) {
        return false;
    }
    const int32_t padded_columns = (int32_t)columns +
        (int32_t)padding * 2;
    if (padded_columns < (int32_t)window) {
        return false;
    }
    const size_t output_columns =
        (size_t)((padded_columns - (int32_t)window) /
                 (int32_t)stride + 1);
    if (rows != 0u && output_columns > output_capacity / rows) {
        return false;
    }
    size_t output_index = 0u;
    for (size_t row = 0u; row < rows; ++row) {
        for (int32_t begin = -(int32_t)padding;
                begin < (int32_t)columns + (int32_t)padding -
                    (int32_t)window + 1;
                begin += (int32_t)stride) {
            float sum = 0.0f;
            for (int32_t offset = 0; offset < (int32_t)window; ++offset) {
                const int32_t column = begin + offset;
                if (column >= 0 && column < (int32_t)columns) {
                    sum += input[row * columns + (size_t)column];
                }
            }
            output[output_index++] = sum / (float)window;
        }
    }
    *written = output_index;
    return true;
}

int32_t gomore_primitives_profile_state_apply(
    uint8_t *state, size_t state_length,
    int32_t profile, int32_t selector, uint8_t requested) {
    if (state == NULL || state_length < 0x39D8u) {
        return -1;
    }
    store_u32_le(&state[0x39D4u], (uint32_t)profile);
    if (selector == 0) {
        requested = 4u;
    } else if (selector == 1) {
        requested = 5u;
    }
    switch (profile) {
        case 0:
            gomore_primitives_slot_state_transition(
                &state[0x3996u], 0u, true);
            gomore_primitives_slot_state_transition(
                &state[0x3986u], 3u, true);
            break;
        case 1:
            gomore_primitives_slot_state_transition(
                &state[0x3996u], 3u, true);
            gomore_primitives_slot_state_transition(
                &state[0x3986u], 0u, true);
            break;
        case 2:
            gomore_primitives_slot_state_transition(
                &state[0x39A5u], 3u, true);
            gomore_primitives_slot_state_transition(
                &state[0x3996u], 0u, true);
            gomore_primitives_slot_state_transition(
                &state[0x3986u], 3u, true);
            break;
        case 11:
            gomore_primitives_slot_state_transition(
                &state[0x39CAu], requested, true);
            break;
        default:
            store_u32_le(&state[0x39D4u], UINT32_MAX);
            return -1;
    }
    return 0;
}

bool gomore_primitives_sorted_percentile(
    float *values, size_t count, uint32_t percentile,
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare, float *result) {
    if (values == NULL || count == 0u || percentile > 100u ||
            qsort_provider == NULL || compare == NULL || result == NULL) {
        return false;
    }
    qsort_provider(values, count, sizeof(values[0]), compare);
    if (percentile == 0u || count == 1u) {
        *result = values[0];
        return true;
    }
    if (percentile == 100u) {
        *result = values[count - 1u];
        return true;
    }
    const float step = 100.0f / (float)(count - 1u);
    const float position = (float)percentile / step;
    const size_t index = (size_t)position;
    const float remainder = (float)percentile - (float)index * step;
    if (remainder >= 0.1f) {
        const float slope = (values[index + 1u] - values[index]) / step;
        *result = values[index] + slope * remainder;
    } else {
        *result = values[index];
    }
    return true;
}

uint32_t gomore_primitives_sps_select_available(
    float reference, float gpd, float accelerometer,
    uint8_t accelerometer_auxiliary,
    gomore_primitives_sps_selection_log_fn log_values,
    gomore_primitives_sps_selection *output) {
    if (output == NULL) {
        return UINT32_C(0x40);
    }
    if (log_values != NULL) {
        log_values(reference, gpd, accelerometer);
    }
    uint32_t status;
    if (reference >= 0.0f) {
        output->value = reference;
        output->source = 0u;
        status = 0u;
    } else if (gpd >= 0.0f) {
        output->value = gpd;
        output->source = 1u;
        status = 1u;
    } else if (accelerometer >= 0.0f) {
        output->value = accelerometer;
        output->source = 2u;
        status = 2u;
    } else {
        output->value = -1.0f;
        output->source = 3u;
        status = UINT32_C(0x40);
    }
    output->reciprocal_hours =
        output->value > 0.0f ? 3600.0f / output->value : 0.0f;
    output->auxiliary = accelerometer_auxiliary;
    return status;
}

bool gomore_primitives_statistics_accumulate(
    gomore_primitives_statistics_accumulator *accumulator,
    uint32_t span, bool upper_flag, bool lower_flag,
    float signed_value, bool quality_flag4, bool quality_flag6,
    float mean_value) {
    if (accumulator == NULL) {
        return false;
    }
    ++accumulator->observations;
    if (span > 1u) {
        accumulator->upper_count += span - 1u;
        accumulator->lower_count += span - 1u;
    }
    if (upper_flag) {
        ++accumulator->upper_count;
    }
    if (lower_flag) {
        ++accumulator->lower_count;
    }
    if (signed_value > 0.0f) {
        ++accumulator->positive_count;
    }
    if (quality_flag4 || !quality_flag6) {
        ++accumulator->quality_count;
    }
    if (float_bits(mean_value) + UINT32_C(0xBDE00000) <=
            UINT32_C(0x01500000)) {
        const uint32_t previous_count = accumulator->mean_count;
        ++accumulator->mean_count;
        if (accumulator->mean_count == 0u) {
            accumulator->mean = 0.0f;
        } else {
            accumulator->mean =
                (mean_value + accumulator->mean * (float)previous_count) /
                (float)accumulator->mean_count;
        }
    }
    return true;
}

bool gomore_primitives_interval_descriptor_merge(
    gomore_primitives_interval_descriptor *output,
    uint32_t initial_start, bool bypass_merge,
    const gomore_primitives_interval_descriptor *previous,
    const gomore_primitives_interval_descriptor *addition,
    uint8_t profile) {
    if (output == NULL || (!bypass_merge &&
            (previous == NULL || addition == NULL))) {
        return false;
    }
    clear_bytes((uint8_t *)output, sizeof(*output));
    output->type = 3u;
    output->start = initial_start;
    output->profile = profile;
    if (bypass_merge) {
        return true;
    }
    output->start = previous->start;
    for (size_t index = 0u; index < 5u; ++index) {
        output->totals[index] = (int32_t)(
            (uint32_t)previous->totals[index] +
            (uint32_t)addition->totals[index]);
    }
    const int32_t combined_count = (int32_t)(
        (uint32_t)previous->mean_count + (uint32_t)addition->mean_count);
    if (combined_count > 0) {
        output->mean_count = combined_count;
        output->mean =
            ((float)previous->mean_count * previous->mean +
             (float)addition->mean_count * addition->mean) /
            (float)combined_count;
    }
    return true;
}

bool gomore_primitives_step_accumulate(
    gomore_primitives_step_accumulator *state,
    uint32_t scale, uint8_t value, float *completed) {
    if (state == NULL || completed == NULL) {
        return false;
    }
    *completed = 0.0f;
    const uint32_t lag = gomore_primitives_shift_presence_history(
        (uint8_t *)state, sizeof(*state), value);
    float contribution =
        ((float)value + 1.0f) / 60.0f * (float)(lag + 1u);
    if (scale < 4u) {
        contribution *= (float)scale;
    }
    if (value == 0u) {
        ++state->zero_streak;
        state->positive_streak = 0u;
        state->accumulated = 0.0f;
    } else {
        state->zero_streak = 0u;
        ++state->positive_streak;
        state->accumulated += contribution;
    }
    if (state->required_streak <= state->positive_streak &&
            contribution > 0.0f) {
        *completed = state->accumulated;
        state->accumulated = 0.0f;
    }
    return true;
}

bool gomore_primitives_packed_timeline_extract(
    uint8_t *packed, size_t packed_length,
    uint32_t begin, uint32_t end, uint32_t cleanup_end,
    uint32_t alternate_cleanup_begin, uint32_t alternate_cleanup_end,
    uint8_t *output, size_t output_capacity, size_t *written) {
    if (packed == NULL || output == NULL || written == NULL ||
            end < begin) {
        return false;
    }
    const uint32_t span = end - begin;
    const size_t needed = (size_t)(span / 30u) +
        (span % 30u != 0u ? 1u : 0u);
    if (needed > output_capacity || needed > 2880u) {
        return false;
    }
    uint32_t clear_begin = begin;
    uint32_t clear_end = cleanup_end;
    if (cleanup_end - begin >= 901u) {
        if (alternate_cleanup_begin == 0u) {
            clear_begin = 0u;
            clear_end = 0u;
        } else {
            clear_begin = alternate_cleanup_begin;
            clear_end = alternate_cleanup_end;
        }
    }
    for (uint32_t timestamp = clear_begin; timestamp < clear_end;
            timestamp += 30u) {
        uint8_t value = 0u;
        if (!gomore_primitives_packed_2bit_get(
                packed, packed_length, timestamp / 30u, &value)) {
            return false;
        }
        if (value != 0u && !gomore_primitives_packed_2bit_set(
                packed, packed_length, timestamp / 30u, 0u)) {
            return false;
        }
        if (UINT32_MAX - timestamp < 30u) {
            break;
        }
    }
    size_t output_index = 0u;
    for (uint32_t timestamp = begin; timestamp < end;
            timestamp += 30u) {
        if (!gomore_primitives_packed_2bit_get(
                packed, packed_length, timestamp / 30u,
                &output[output_index])) {
            return false;
        }
        ++output_index;
        if (UINT32_MAX - timestamp < 30u) {
            break;
        }
    }
    *written = output_index;
    return true;
}

static uint32_t sleep_history_slot(uint32_t timestamp) {
    const uint32_t minutes = timestamp / 60u;
    if (timestamp % 60u == 59u) {
        return minutes % 15u;
    }
    if (minutes % 15u == 0u) {
        return 14u;
    }
    return minutes % 15u - 1u;
}

bool gomore_primitives_sleep_interval_build(
    gomore_primitives_sleep_interval_result *output,
    const float history[15], bool high_threshold,
    uint32_t clamp_end, uint32_t clamp_start,
    int32_t mode, uint32_t metadata, int16_t timezone_minutes,
    int32_t shift_minutes, uint8_t auxiliary,
    const gomore_primitives_sleep_interval_source *source,
    const gomore_primitives_sleep_interval_policy *policy) {
    if (output == NULL || history == NULL || source == NULL || policy == NULL) {
        return false;
    }
    clear_bytes((uint8_t *)output, sizeof(*output));
    output->flags = 4u;
    output->source_start = source->start +
        (uint32_t)source->preceding_count * 60u;
    output->source_end = source->end;
    output->start = output->source_start;
    if (source->type == 2u && policy->disable_history_scan == 0u) {
        output->start = source->start;
    }
    if (clamp_start != 0u && output->start < clamp_start) {
        output->start = clamp_start;
    }
    uint32_t end = output->source_end;
    if (mode != 1 && policy->disable_history_scan == 0u) {
        if (shift_minutes == 0) {
            const float threshold = high_threshold ? 0.85f : 0.7f;
            uint32_t count = 0u;
            for (uint32_t index = 0u; index < 15u; ++index) {
                const uint32_t slot = sleep_history_slot(
                    output->source_end - 1u - index * 60u);
                if (history[slot] > threshold) {
                    break;
                }
                ++count;
            }
            end = output->source_end - count * 60u;
        } else {
            end = output->source_end +
                (uint32_t)((int64_t)shift_minutes * 60);
        }
    }
    if (end < output->start) {
        end = output->start;
    }
    if (clamp_end != 0u && clamp_end < end) {
        end = clamp_end;
    }
    output->end = end;
    output->metadata = metadata;
    output->clamp_start = output->start;
    const uint32_t duration = (output->end - output->start) / 60u;
    gomore_primitives_civil_time local_time;
    clear_bytes((uint8_t *)&local_time, sizeof(local_time));
    const uint32_t local_timestamp = output->start +
        (uint32_t)((int32_t)timezone_minutes * 60);
    if (!gomore_primitives_epoch_to_civil_time(
            local_timestamp, &local_time)) {
        return false;
    }
    const bool outside_hours = local_time.hour >= policy->end_hour ||
        local_time.hour < policy->begin_hour;
    const uint32_t duration_limit = outside_hours ? 20u : 180u;
    output->auxiliary = auxiliary;
    if ((int32_t)float_bits(source->metric) <
            (int32_t)UINT32_C(0x42C80000)) {
        if (duration > 899u) {
            const float average = source->count == 0u ? 0.0f :
                (float)source->sum / (float)source->count;
            if ((int32_t)float_bits(average) >
                    (int32_t)UINT32_C(0x3E570A3D)) {
                output->status = 2u;
                return true;
            }
        }
        if (duration < duration_limit) {
            if ((int32_t)duration < (int32_t)policy->minimum_slots ||
                    outside_hours) {
                output->status = 4u;
            } else {
                output->flags |= 8u;
                output->status = 3u;
            }
        } else {
            output->flags |= 0x18u;
            output->status = 0u;
        }
    } else {
        output->status = 1u;
    }
    return true;
}

bool gomore_primitives_sleep_interval_refine(
    gomore_primitives_sleep_interval_result *output,
    const gomore_primitives_sleep_interval_result *previous,
    const gomore_primitives_sleep_interval_result *current,
    int32_t average_count, int32_t average_sum,
    int16_t gap_limit_minutes) {
    if (output == NULL || previous == NULL || current == NULL) {
        return false;
    }
    *output = *current;
    if ((current->flags & 8u) == 0u) {
        return true;
    }
    const uint32_t span = current->end - previous->start;
    const uint32_t gap = current->start - previous->end;
    const float average = average_count == 0 ? 0.0f :
        (float)average_sum / (float)average_count;
    if ((previous->flags & 8u) == 0u) {
        output->status = 2u;
    } else if (span > 43200u) {
        output->status = 1u;
    } else if ((int32_t)gap > (int32_t)gap_limit_minutes * 60) {
        output->status = 3u;
    } else if (average_count >= 1800 && average > 0.32f && gap > 1800u) {
        output->status = 5u;
    } else {
        if (span >= 10800u) {
            output->flags |= 0x10u;
        }
        output->status = 0u;
        output->start = previous->start;
    }
    return true;
}

bool gomore_primitives_sleep_interval_compose(
    gomore_primitives_sleep_interval_result *output,
    const float history[15], bool high_threshold,
    uint32_t clamp_end, uint32_t clamp_start,
    int32_t mode, uint32_t metadata, int16_t timezone_minutes,
    int32_t shift_minutes, uint8_t auxiliary,
    const gomore_primitives_sleep_interval_source *source,
    const gomore_primitives_sleep_interval_policy *policy,
    const gomore_primitives_sleep_interval_result *previous,
    int32_t average_count, int32_t average_sum,
    int16_t gap_limit_minutes) {
    if (output == NULL || previous == NULL) {
        return false;
    }
    gomore_primitives_sleep_interval_result built;
    if (!gomore_primitives_sleep_interval_build(
            &built, history, high_threshold, clamp_end, clamp_start,
            mode, metadata, timezone_minutes, shift_minutes, auxiliary,
            source, policy) ||
        !gomore_primitives_sleep_interval_refine(
            output, previous, &built, average_count, average_sum,
            gap_limit_minutes)) {
        return false;
    }
    output->end = output->start +
        ((output->end - output->start) / 30u) * 30u;
    return true;
}

bool gomore_primitives_sleep_interval_select(
    gomore_primitives_sleep_interval_result *output,
    const gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes) {
    if (output == NULL || context == NULL) {
        return false;
    }
    if (!context->enabled) {
        *output = context->stored;
        return true;
    }
    gomore_primitives_sleep_interval_source source = context->base_source;
    source.end = current;
    gomore_primitives_sleep_interval_result candidate;
    if (!gomore_primitives_sleep_interval_compose(
            &candidate, context->history, context->high_threshold,
            context->clamp_end, context->clamp_start,
            1, context->stored.end, timezone_minutes,
            0, 0u, &source, &context->policy, &context->stored,
            context->aggregation.totals[0],
            context->aggregation.totals[3],
            (int16_t)context->policy.reserved)) {
        return false;
    }
    *output = (candidate.flags & 8u) != 0u ?
        candidate : context->stored;
    return true;
}

uint32_t gomore_primitives_sleep_interval_run(
    gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes, int32_t mode,
    const uint8_t *policy_source, size_t policy_source_length,
    gomore_primitives_sleep_interval_result *output) {
    if (context == NULL || output == NULL) {
        return UINT32_MAX;
    }
    output->flags = 0u;
    if (!context->enabled) {
        return UINT32_C(0x40);
    }
    if (policy_source == NULL || policy_source_length < 10u) {
        return UINT32_MAX;
    }

    gomore_primitives_sleep_interval_source source = context->base_source;
    source.end = current;
    gomore_primitives_sleep_interval_result candidate;
    if (!gomore_primitives_sleep_interval_compose(
            &candidate, context->history, context->high_threshold,
            context->clamp_end, context->clamp_start,
            mode, context->stored.end, timezone_minutes,
            0, 5u, &source, &context->policy, &context->stored,
            context->aggregation.totals[0],
            context->aggregation.totals[3],
            (int16_t)context->policy.reserved)) {
        return UINT32_MAX;
    }

    if (candidate.start < context->clamp_start &&
            context->clamp_start - candidate.start < 900u) {
        candidate.start = context->clamp_start;
        candidate.end = candidate.start +
            ((candidate.end - candidate.start) / 30u) * 30u;
    }
    if ((candidate.flags & 8u) != 0u) {
        context->stored = candidate;
    }

    gomore_primitives_interval_descriptor addition;
    gomore_primitives_interval_descriptor merged;
    for (size_t index = 0u; index < sizeof(addition); ++index) {
        ((uint8_t *)&addition)[index] = ((const uint8_t *)&source)[index];
    }
    if (!gomore_primitives_interval_descriptor_merge(
            &merged, current, (candidate.flags & 8u) != 0u,
            &context->aggregation, &addition, 3u)) {
        return UINT32_MAX;
    }
    for (size_t index = 0u; index < sizeof(context->base_source); ++index) {
        ((uint8_t *)&context->base_source)[index] =
            ((const uint8_t *)&merged)[index];
    }
    *output = candidate;

    store_u32_le((uint8_t *)&context->policy,
                 load_u32_le(&policy_source[2]));
    store_u32_le((uint8_t *)&context->policy + 4u,
                 load_u32_le(&policy_source[6]));
    context->enabled = false;
    context->control_profile = 3u;
    context->control_auxiliary = 5u;
    return 0u;
}

bool gomore_primitives_sleep_interval_update(
    gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes, int32_t mode,
    const uint8_t *policy_source, size_t policy_source_length,
    uint8_t *pending,
    uint8_t *output_record, size_t output_record_length,
    uint8_t profile_state,
    void *packed_state, size_t packed_state_length,
    uint8_t *propagated_value) {
    if (context == NULL || pending == NULL ||
            (output_record != NULL && output_record_length < 56u) ||
            (profile_state != 3u &&
             (packed_state == NULL || propagated_value == NULL))) {
        return false;
    }
    *pending = 0u;
    if (output_record != NULL) {
        clear_bytes(output_record, 56u);
    }
    gomore_primitives_sleep_interval_result result;
    clear_bytes((uint8_t *)&result, sizeof(result));
    if (gomore_primitives_sleep_interval_run(
            context, current, timezone_minutes, mode,
            policy_source, policy_source_length, &result) == UINT32_MAX) {
        return false;
    }
    if (output_record != NULL) {
        for (size_t index = 0u; index < 8u; ++index) {
            output_record[index] = ((const uint8_t *)&result)[index];
        }
        output_record[8] = result.flags;
        output_record[9] = result.auxiliary;
        output_record[10] = result.status;
        output_record[11] = result.tail[0];
    }
    if (profile_state != 3u && !gomore_primitives_propagate_packed_status(
            packed_state, packed_state_length, propagated_value)) {
        return false;
    }
    return true;
}

int32_t gomore_primitives_sleep_interval_dispatch(
    const gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes,
    uint32_t output_binding, uint8_t *output_record,
    size_t output_record_length,
    uintptr_t first, uintptr_t second, uintptr_t fourth, uintptr_t fifth,
    gomore_primitives_stage_consumer_fn consumer) {
    if (output_record == NULL || output_record_length < 12u ||
            consumer == NULL) {
        return -1;
    }
    gomore_primitives_sleep_interval_result selected;
    if (!gomore_primitives_sleep_interval_select(
            &selected, context, current, timezone_minutes) ||
            selected.flags == 0u) {
        return -1;
    }
    uint8_t staged[32];
    for (size_t index = 0u; index < sizeof(staged); ++index) {
        staged[index] = ((const uint8_t *)&selected)[index];
    }
    store_u32_le(staged, output_binding);
    const uint32_t preserved = load_u32_le(&output_record[8]);
    const int32_t status = gomore_primitives_stage_32_and_consume(
        first, second, staged, sizeof(staged), fourth, fifth, consumer);
    store_u32_le(&output_record[8], preserved);
    return status == 0 ? 0 : -1;
}

uint8_t gomore_primitives_count_hysteresis_crossings(
    const uint16_t *values, size_t count) {
    if (values == NULL && count != 0u) {
        return 0u;
    }
    bool armed = true;
    uint8_t crossings = 0u;
    for (size_t index = 0u; index < count; ++index) {
        if (armed && values[index] > UINT16_C(1200)) {
            armed = false;
            ++crossings;
        } else if (!armed && values[index] < UINT16_C(1000)) {
            armed = true;
        }
    }
    return crossings;
}

int32_t gomore_primitives_nullable_compare_n(const uint8_t *left,
                                             const uint8_t *right,
                                             size_t count) {
    if (left == NULL || right == NULL || count == 0u) {
        return 0xFFFF;
    }
    for (size_t index = 0u; index < count; ++index) {
        if (left[index] < right[index]) {
            return -1;
        }
        if (left[index] > right[index]) {
            return 1;
        }
    }
    return 0;
}

bool gomore_primitives_recent_interval_predicate(const void *record,
                                                 size_t length,
                                                 uint32_t now) {
    if (record == NULL || length < 0x1Bu) {
        return false;
    }
    const uint8_t *bytes = record;
    if ((bytes[0x1Au] & UINT8_C(8)) == 0u) {
        return false;
    }
    const uint32_t begin = load_u32_le(&bytes[0]);
    const uint32_t end = load_u32_le(&bytes[4]);
    const uint32_t duration = end - begin;
    return begin < end && duration <= UINT32_C(86400) &&
           duration >= UINT32_C(900) &&
           begin + UINT32_C(86400) > now && now >= end;
}

int32_t gomore_primitives_record_quality_classify(const void *record,
                                                  size_t length) {
    if (record == NULL || length < 0x3Du) {
        return -1;
    }
    const uint8_t *bytes = record;
    const int8_t flag_39 = (int8_t)bytes[0x39u];
    const int8_t flag_3a = (int8_t)bytes[0x3Au];
    const int8_t flag_3b = (int8_t)bytes[0x3Bu];
    const int8_t flag_3c = (int8_t)bytes[0x3Cu];
    if (flag_3b >= 1 && flag_3c >= 1) {
        return 2;
    }
    const int32_t word_2c = (int32_t)load_u32_le(&bytes[0x2Cu]);
    const int32_t word_30 = (int32_t)load_u32_le(&bytes[0x30u]);
    if ((word_2c <= INT32_C(0x43480000) ||
         word_30 <= INT32_C(0x43340000)) &&
            flag_3a >= 0 && flag_39 >= 0) {
        return 1;
    }
    return -1;
}

int32_t gomore_primitives_seeded_random_offset(
    uint32_t seed, uint32_t *stored_seed,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (stored_seed == NULL || prepare == NULL || random_value == NULL) {
        return -1;
    }
    *stored_seed = seed;
    prepare();
    return random_value() % 100 + 23;
}

static void *allocate_mode_state(
    size_t length, uint32_t mode, uintptr_t binding,
    gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    if (allocate == NULL || initialize == NULL) {
        return NULL;
    }
    uint8_t *record = allocate(length);
    if (record == NULL) {
        return NULL;
    }
    store_u32_le(record, mode);
    initialize(record, binding);
    return record;
}

void *gomore_primitives_allocate_mode2_state(
    uintptr_t binding, gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    return allocate_mode_state(0x23Cu, 2u, binding, allocate, initialize);
}

void *gomore_primitives_allocate_mode1_state(
    uintptr_t binding, gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    return allocate_mode_state(0x238u, 1u, binding, allocate, initialize);
}

void *gomore_primitives_allocate_mode0_state_remap(
    uintptr_t binding,
    const uint32_t *descriptor_table, size_t descriptor_bytes,
    uint32_t descriptor_table_binding,
    gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    size_t descriptor_count = 0u;
    size_t descriptor_stride = 0u;
    if (allocate == NULL || initialize == NULL) {
        return NULL;
    }
    if (descriptor_table != NULL) {
        const size_t descriptor_words = descriptor_bytes / sizeof(uint32_t);
        if (descriptor_words < 3u || descriptor_table[0] == 0u) {
            return NULL;
        }
        descriptor_count = descriptor_table[0];
        descriptor_stride = (descriptor_words - 1u) / descriptor_count;
        for (size_t index = 0u; index < descriptor_count; ++index) {
            const size_t source = index * descriptor_stride;
            if (source + 2u >= descriptor_words ||
                    descriptor_table[source + 1u] > 40u ||
                    source + 2u >
                        (UINT32_MAX - descriptor_table_binding) / 4u) {
                return NULL;
            }
        }
    }

    uint8_t *record = allocate(0x2DCu);
    if (record == NULL) {
        return NULL;
    }
    clear_bytes(record, 0x2DCu);
    store_u32_le(record, 0u);
    initialize(record, binding);
    store_u32_le(&record[0x238u], load_u32_le(&record[0x1E0u]));

    for (size_t index = 0u; index < descriptor_count; ++index) {
        const size_t source = index * descriptor_stride;
        const size_t destination = 0x238u +
            (size_t)descriptor_table[source + 1u] * sizeof(uint32_t);
        const uint32_t payload_binding = descriptor_table_binding +
            (uint32_t)((source + 2u) * sizeof(uint32_t));
        store_u32_le(&record[destination], payload_binding);
    }
    return record;
}

int32_t gomore_primitives_decimal_parse(const uint8_t *text) {
    if (text == NULL) {
        return 0;
    }
    int32_t value = 0;
    for (size_t index = 0u; text[index] != 0u; ++index) {
        value = (int32_t)((uint32_t)value * UINT32_C(10) +
                          (uint32_t)text[index] - UINT32_C(0x30));
    }
    return value;
}

uint32_t gomore_primitives_tensor_call_optional_finish(
    const uint32_t descriptor[3], uintptr_t first, uintptr_t second,
    bool finish, gomore_primitives_tensor_call_fn call,
    gomore_primitives_tensor_finish_fn finish_call) {
    if (descriptor == NULL || call == NULL || (finish && finish_call == NULL)) {
        return UINT32_MAX;
    }
    const uint32_t result = call(first, second, descriptor[0],
                                 descriptor[1], descriptor[2]);
    if (finish) {
        finish_call(first, second);
    }
    return result;
}

int32_t gomore_primitives_all_class_0x20(const uint8_t *bytes,
                                        size_t count,
                                        const uint8_t classes[256]) {
    if ((bytes == NULL && count != 0u) || classes == NULL) {
        return -1;
    }
    for (size_t index = 0u; index < count; ++index) {
        if (classes[bytes[index]] != UINT8_C(0x20)) {
            return -1;
        }
    }
    return 0;
}

bool gomore_primitives_filter_state_initialize(
    void *record, size_t length, gomore_primitives_filter_init_fn initialize) {
    if (record == NULL || length < 0x18Cu || initialize == NULL) {
        return false;
    }
    static const float parameters[2] = {
        0x1.0624dep-6f, 0x1.47ae14p-3f
    };
    clear_bytes(record, 0x18Cu);
    initialize(record, 2u, 2u, parameters);
    return true;
}

bool gomore_primitives_quality_samples_copy(
    void *record, size_t length,
    const gomore_primitives_quality_sample samples[3]) {
    if (record == NULL || length < 0x24u || samples == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    for (size_t index = 0u; index < 3u; ++index) {
        if (samples[index].metadata < INT32_C(0x3727C5AC) &&
                samples[index].value >= 0.0f) {
            store_u32_le(&bytes[0x18u + index * 4u],
                         float_bits(samples[index].value));
        }
    }
    return true;
}

bool gomore_primitives_dual_stage(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *output, size_t output_length,
    gomore_primitives_dual_stage_fn first_stage,
    gomore_primitives_dual_stage_fn second_stage) {
    if (output == NULL || output_length < 0x38u || first_stage == NULL ||
            second_stage == NULL) {
        return false;
    }
    first_stage(first, second, third, fourth, output);
    second_stage(first, second, third, fourth, (uint8_t *)output + 0x1Cu);
    return true;
}

bool gomore_primitives_composite_record_initialize(
    void *record, size_t length,
    gomore_primitives_record_init_fn tail_initialize) {
    if (record == NULL || length < 0x30u || tail_initialize == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    tail_initialize(&bytes[0x30u]);
    clear_bytes(&bytes[0x29u], 4u);
    clear_bytes(&bytes[0x2Du], 2u);
    bytes[0x28u] = 0u;
    clear_bytes(bytes, 0x28u);
    return true;
}

bool gomore_primitives_quality_code(const void *record, size_t length,
                                    uint8_t *code) {
    if (record == NULL || length < 0x3Eu || code == NULL) {
        return false;
    }
    const uint8_t *bytes = record;
    uint8_t result = UINT8_C(0xFF);
    if ((int8_t)bytes[0x38u] < 0) {
        result = 0u;
    } else if (bits_float(load_u32_le(&bytes[0x28u])) >= 0.0f &&
               (int8_t)bytes[0x3Du] >= 0) {
        result = (uint8_t)gomore_primitives_record_quality_classify(
            record, length);
    }
    *code = result;
    return true;
}

float gomore_primitives_i16_standard_deviation(
    const int16_t *values, size_t count, int32_t center,
    gomore_primitives_float_unary_fn square_root) {
    if (square_root == NULL || (values == NULL && count != 0u)) {
        return 0.0f;
    }
    uint32_t sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t difference = (int32_t)values[index] - center;
        const int64_t wide_square = (int64_t)difference * difference;
        sum += (uint32_t)wide_square;
    }
    int32_t variance = 0;
    if (count > 1u && count <= (size_t)INT32_MAX) {
        variance = (int32_t)sum / (int32_t)(count - 1u);
    }
    return square_root((float)variance);
}

bool gomore_primitives_locomotion_summary_update(
    gomore_primitives_locomotion_summary_state *state,
    const int16_t *const channels[4], size_t sample_count,
    gomore_primitives_float_unary_fn square_root) {
    if (state == NULL || channels == NULL || square_root == NULL ||
            state->next_slot >= 8u || sample_count > (size_t)INT8_MAX) {
        return false;
    }
    for (size_t channel = 0u; channel < 4u; ++channel) {
        if (channels[channel] == NULL) {
            return false;
        }
    }

    const size_t slot = state->next_slot;
    int16_t means[4];
    for (size_t channel = 0u; channel < 4u; ++channel) {
        means[channel] = gomore_primitives_i16_mean(
            channels[channel], sample_count);
        state->means[channel][slot] = means[channel];
    }
    for (size_t channel = 0u; channel < 4u; ++channel) {
        const float deviation = gomore_primitives_i16_standard_deviation(
            channels[channel], sample_count, means[channel], square_root);
        state->standard_deviations[channel][slot] =
            (int16_t)dormant_estimator_float_to_i32(deviation);
    }
    state->fourth_range[slot] = (int16_t)gomore_primitives_i16_range(
        channels[3], sample_count);

    const int8_t signed_difference_count = (int8_t)(uint8_t)sample_count;
    const size_t difference_count = signed_difference_count > 0
        ? (size_t)signed_difference_count : 0u;
    for (size_t channel = 0u; channel < 4u; ++channel) {
        state->mean_absolute_differences[channel][slot] =
            gomore_primitives_i16_mean_absolute_difference(
                channels[channel], difference_count);
    }
    state->next_slot = (uint8_t)((slot + 1u) & 7u);
    return true;
}

static bool locomotion_raw_summary_update(
    uint8_t *state, size_t state_length,
    const int16_t *const channels[4],
    gomore_primitives_float_unary_fn square_root) {
    if (state_length < 0x264u || state[0x52u] >= 8u) {
        return false;
    }
    const size_t slot_offset = (size_t)state[0x52u] * 2u;
    static const size_t mean_offsets[4] = {
        0x1E4u, 0x1F4u, 0x12u, 0x32u,
    };
    static const size_t deviation_offsets[4] = {
        0x02u, 0x204u, 0x214u, 0x22u,
    };
    static const size_t difference_offsets[4] = {
        0x234u, 0x244u, 0x254u, 0x224u,
    };
    int16_t means[4];
    for (size_t channel = 0u; channel < 4u; ++channel) {
        means[channel] = gomore_primitives_i16_mean(
            channels[channel], 25u);
        store_u16_le_early(
            &state[mean_offsets[channel] + slot_offset],
            (uint16_t)means[channel]);
    }
    for (size_t channel = 0u; channel < 4u; ++channel) {
        const float deviation =
            gomore_primitives_i16_standard_deviation(
                channels[channel], 25u, means[channel], square_root);
        store_u16_le_early(
            &state[deviation_offsets[channel] + slot_offset],
            (uint16_t)(int16_t)dormant_estimator_float_to_i32(deviation));
        store_u16_le_early(
            &state[difference_offsets[channel] + slot_offset],
            (uint16_t)gomore_primitives_i16_mean_absolute_difference(
                channels[channel], 25u));
    }
    store_u16_le_early(
        &state[0x42u + slot_offset],
        (uint16_t)(int16_t)gomore_primitives_i16_range(
            channels[3], 25u));
    state[0x52u] = (uint8_t)((state[0x52u] + 1u) & 7u);
    return true;
}

int32_t gomore_primitives_locomotion_window_preprocess(
    void *state, size_t state_length, uint32_t elapsed_windows,
    const float *const axes[3], bool input_unavailable,
    void *output, size_t output_length,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_locomotion_classify_fn classify) {
    if (state == NULL || state_length < 0x26Eu || output == NULL ||
            output_length < 0x3Eu || square_root == NULL ||
            classify == NULL ||
            (!input_unavailable &&
             (axes == NULL || axes[0] == NULL ||
              axes[1] == NULL || axes[2] == NULL))) {
        return -1;
    }
    uint8_t *const bytes = state;

    if (elapsed_windows < 2u && !input_unavailable) {
        if ((int8_t)bytes[0] > 0) {
            --bytes[0];
        }
    } else {
        if (elapsed_windows > 8u) {
            (void)gomore_primitives_missing_window_initialize(
                output, output_length);
            (void)gomore_primitives_mode8_state_initialize(
                state, state_length);
            return 1;
        }
        if (input_unavailable) {
            ++elapsed_windows;
        }
        for (uint32_t gap = 0u; gap + 1u < elapsed_windows; ++gap) {
            if (!gomore_primitives_circular_feature_slot_advance(
                    state, state_length)) {
                return -1;
            }
            for (size_t index = 0u; index < 175u; ++index) {
                store_u16_le_early(
                    &bytes[0x54u + index * 2u],
                    load_u16_le_early(
                        &bytes[0x54u + (index + 25u) * 2u]));
            }
            for (size_t index = 0u; index < 25u; ++index) {
                store_u16_le_early(
                    &bytes[0x54u + (175u + index) * 2u],
                    load_u16_le_early(
                        &bytes[0x54u + (174u - index) * 2u]));
            }
        }
    }

    if (input_unavailable) {
        (void)gomore_primitives_missing_window_initialize(
            output, output_length);
        return 1;
    }

    int16_t axis_values[3][26] = {{0}};
    int16_t magnitude[26] = {0};
    for (size_t index = 0u; index < 25u; ++index) {
        uint32_t square_sum = 0u;
        for (size_t axis = 0u; axis < 3u; ++axis) {
            const int32_t converted =
                dormant_estimator_float_to_i32(axes[axis][index]);
            axis_values[axis][index] = (int16_t)converted;
            const int32_t widened = (int32_t)axis_values[axis][index];
            square_sum += (uint32_t)(widened * widened);
        }
        const float absolute = square_root(
            (float)(int32_t)square_sum);
        magnitude[index] =
            (int16_t)dormant_estimator_float_to_i32(absolute);
    }

    for (size_t index = 0u; index < 175u; ++index) {
        store_u16_le_early(
            &bytes[0x54u + index * 2u],
            load_u16_le_early(
                &bytes[0x54u + (index + 25u) * 2u]));
    }
    for (size_t index = 0u; index < 25u; ++index) {
        store_u16_le_early(
            &bytes[0x54u + (175u + index) * 2u],
            (uint16_t)magnitude[index]);
    }

    const int16_t *const channels[4] = {
        axis_values[0], axis_values[1], axis_values[2], magnitude,
    };
    if (!locomotion_raw_summary_update(
            bytes, state_length, channels, square_root)) {
        return -1;
    }

    if ((int8_t)bytes[0] >= 8) {
        for (size_t block = 0u; block < 7u; ++block) {
            for (size_t index = 0u; index < 25u; ++index) {
                store_u16_le_early(
                    &bytes[0x54u + (block * 25u + index) * 2u],
                    (uint16_t)magnitude[index]);
            }
        }
    }
    bytes[0] = 0u;
    for (size_t slot = 0u; slot < 8u; ++slot) {
        if (load_u16_le_early(&bytes[0x32u + slot * 2u]) == 0u) {
            ++bytes[0];
        }
    }
    if (bytes[0] < 5u) {
        classify(state, output);
    } else {
        (void)gomore_primitives_missing_window_initialize(
            output, output_length);
    }
    return 0;
}

float gomore_primitives_energy_core(const void *state, size_t length,
                                    float primary, float secondary) {
    if (state == NULL || length < 0x26u) {
        return 0.0f;
    }
    const uint8_t *bytes = state;
    const float state_value = bits_float(load_u32_le(&bytes[0]));
    const uint16_t flags = load_u16_le_early(&bytes[0x24u]);
    if ((flags & UINT16_C(0x0440)) != 0u &&
            (int32_t)float_bits(primary) <= INT32_C(0x3FA00000)) {
        return state_value * bits_float(UINT32_C(0x3CBD230C));
    }
    return ((secondary * bits_float(UINT32_C(0xBAAA3573)) +
             primary * bits_float(UINT32_C(0x3AFD428B)) +
             bits_float(UINT32_C(0x3E91BAD6))) /
            bits_float(UINT32_C(0x3FE6B205))) * state_value;
}

float gomore_primitives_energy_scaled(const void *state, size_t length,
                                      float primary, float scale_input) {
    if (state == NULL || length < 0x26u) {
        return 0.0f;
    }
    const uint8_t *bytes = state;
    const float core = gomore_primitives_energy_core(
        state, length, primary, scale_input);
    const float multiplier = bits_float(load_u32_le(&bytes[4]));
    return (core * multiplier * 2.0f *
            bits_float(UINT32_C(0x411CF5C3)) * scale_input) /
           bits_float(UINT32_C(0x42700000));
}

float gomore_primitives_daily_resting_kcal(const void *profile,
                                           size_t profile_length) {
    if (profile == NULL || profile_length < 10u) {
        return 0.0f;
    }
    const uint8_t *bytes = profile;
    const double height = (double)bits_float(load_u32_le(&bytes[0]));
    const double weight = (double)bits_float(load_u32_le(&bytes[4]));
    const double age = (double)bytes[8];
    double age_term;
    double height_term;
    double result;
    if (bytes[9] != 0u) {
        age_term = age * 0x1.75a858793dd98p+2;
        height_term = height * 0x1.61e4f765fd8aep+2;
        result = weight * 0x1.7666666666666p+3;
        result += 0x1.6faacd9e83e42p+5;
    } else {
        age_term = age * 0x1.2ac710cb295eap+2;
        height_term = height * 0x1.2ad42c3c9eeccp+2;
        result = weight * 0x1.33f7ced916873p+3;
        result += 0x1.1fe075f6fd220p+7;
    }
    result += height_term;
    result -= age_term;
    return (float)result;
}

float gomore_primitives_substrate_fat_fraction(
    float value, float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential) {
    if (exponential == NULL) {
        return 0.0f;
    }
    const float contraction = bits_float(UINT32_C(0x3F733333));
    const float contracted_upper = lower_reference +
        (upper_reference - lower_reference) * contraction;
    const float normalized = gomore_primitives_normalized_position(
        value, contracted_upper, lower_reference);
    const float exponential_term = gomore_primitives_exponential_affine(
        normalized, bits_float(UINT32_C(0x3F240200)), 0.0f,
        bits_float(UINT32_C(0xBF71006E)), exponential);
    const float transform =
        (bits_float(UINT32_C(0x3F312ADE)) +
         exponential_term * contraction *
             bits_float(UINT32_C(0x3EB52383))) *
        bits_float(UINT32_C(0x3F8147AE));
    float fat =
        (bits_float(UINT32_C(0x3FD72B02)) -
         transform * bits_float(UINT32_C(0x3FD72B02))) *
        bits_float(UINT32_C(0x4114A3D7));
    float carbohydrate = (float)(
        ((double)transform * 0x1.05c28f5c28f5cp+2 -
         0x1.6e5604189374cp+1) *
        0x1.070a3d70a3d71p+2);
    if (fat < 0.0f) {
        fat = 0.0f;
    }
    if (carbohydrate < 0.0f) {
        carbohydrate = 0.0f;
    }
    const float total = fat + carbohydrate;
    return total == 0.0f ? 0.0f : fat / total;
}

bool gomore_primitives_energy_zone_thresholds(
    float feature, float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential, float thresholds[7]) {
    if (exponential == NULL || thresholds == NULL) {
        return false;
    }
    float first;
    float neutral;
    float fifth;
    float local[5];
    if (!gomore_primitives_logistic_score(
            bits_float(UINT32_C(0xBDCCCCCD)), -0.25f, feature,
            bits_float(UINT32_C(0x3A83126F)), exponential, &first) ||
        !gomore_primitives_logistic_score(
            bits_float(UINT32_C(0xBDCCCCCD)), 0.0f, 0.0f, 0.0f,
            exponential, &neutral) ||
        !gomore_primitives_logistic_score(
            bits_float(UINT32_C(0xBD4CCCCD)),
            bits_float(UINT32_C(0x3E0F5C29)), -feature,
            bits_float(UINT32_C(0x3A03126F)), exponential, &fifth) ||
        !gomore_primitives_logistic_score(
            bits_float(UINT32_C(0xBD4CCCCD)),
            bits_float(UINT32_C(0xBEBD70A4)), feature,
            bits_float(UINT32_C(0x3A03126F)), exponential, &local[0]) ||
        !gomore_primitives_logistic_score(
            bits_float(UINT32_C(0xBE051EB8)),
            bits_float(UINT32_C(0xBE99999A)), feature,
            bits_float(UINT32_C(0x3A83126F)), exponential, &local[1])) {
        return false;
    }
    local[2] = (first + neutral) * 0.5f;
    local[3] = (fifth + neutral) * 0.5f;
    local[4] = fifth;
    const float span = upper_reference - lower_reference;
    thresholds[0] = lower_reference;
    for (size_t index = 0u; index < 5u; ++index) {
        thresholds[index + 1u] = lower_reference + local[index] * span;
    }
    thresholds[6] = upper_reference;
    return true;
}

bool gomore_primitives_energy_zone_accumulate(
    void *state, size_t state_length, int32_t elapsed_seconds,
    float increment, float metric, float upper_reference,
    float lower_reference, float feature,
    gomore_primitives_float_unary_fn exponential, float totals[5]) {
    if (state == NULL || state_length < 0x4Cu || totals == NULL) {
        return false;
    }
    float thresholds[7];
    if (!gomore_primitives_energy_zone_thresholds(
            feature, upper_reference, lower_reference,
            exponential, thresholds)) {
        return false;
    }
    const float first_boundary = gomore_primitives_interpolate(
        bits_float(UINT32_C(0x3E4CCCCD)),
        upper_reference, lower_reference);
    size_t zone;
    if (metric < first_boundary) {
        zone = 0u;
    } else if (metric < thresholds[1]) {
        zone = 1u;
    } else if (metric >= thresholds[1] && metric < thresholds[3]) {
        zone = 2u;
    } else {
        zone = 3u;
    }
    totals[zone] += increment;

    uint8_t *bytes = state;
    if (metric < thresholds[1]) {
        store_u32_le(&bytes[0x44u], float_bits(0.0f));
        store_u32_le(&bytes[0x48u], 0u);
        return true;
    }
    const float sustained =
        bits_float(load_u32_le(&bytes[0x44u])) + increment;
    store_u32_le(&bytes[0x44u], float_bits(sustained));
    const uint32_t elapsed_bits = load_u32_le(&bytes[0x48u]) +
        (uint32_t)elapsed_seconds;
    store_u32_le(&bytes[0x48u], elapsed_bits);
    if ((int32_t)elapsed_bits >= 600) {
        totals[4] += sustained;
        store_u32_le(&bytes[0x44u], float_bits(0.0f));
    }
    return true;
}

bool gomore_primitives_energy_projection(
    const void *state, size_t state_length, float first, float second,
    float output[4]) {
    if (state == NULL || state_length < 8u || output == NULL) {
        return false;
    }
    const float scaled_first = (float)((double)first *
                                       0x1.0624dd2f1a9fcp-10);
    const float scaled_second = (float)((double)second *
                                        0x1.0624dd2f1a9fcp-10);
    float first_component =
        ((scaled_second * bits_float(UINT32_C(0x4082E148)) -
          scaled_first * bits_float(UINT32_C(0x40372B02))) /
         bits_float(UINT32_C(0x42700000))) *
        bits_float(UINT32_C(0x4083851F));
    float second_component =
        ((scaled_first * bits_float(UINT32_C(0x3FD72B02)) -
          scaled_second * bits_float(UINT32_C(0x3FD72B02))) /
         bits_float(UINT32_C(0x42700000))) *
        bits_float(UINT32_C(0x4114A3D7));
    if (second_component < 0.0f) {
        first_component += second_component;
        second_component = 0.0f;
    }
    if (first_component < 0.0f) {
        first_component = 0.0f;
    }
    const float multiplier = bits_float(
        load_u32_le((const uint8_t *)state + 4u));
    output[0] = multiplier * (first_component + second_component);
    output[1] = gomore_primitives_scaled_ratio(output[0], multiplier);
    output[2] = multiplier * second_component;
    output[3] = multiplier * first_component;
    return true;
}

float gomore_primitives_energy_nonlinear_scale(
    float primary, float scale_input) {
    float base = bits_float(UINT32_C(0x3F4572DA)) +
        scale_input * bits_float(UINT32_C(0x3C15D7F2));
    const uint32_t base_bits = float_bits(base);
    if ((base_bits & UINT32_C(0x80000000)) != 0u ||
            base_bits < UINT32_C(0x3F800000)) {
        base = 1.0f;
    }
    const double ratio = (double)(1.0f - base) /
                         0x1.999999999999ap-2;
    const float result = (float)((double)base +
                                 (double)primary * ratio);
    return primary < 0.0f ? base : result;
}

bool gomore_primitives_energy_mode_rate(
    void *state, size_t state_length,
    const void *profile, size_t profile_length,
    float input, float *output) {
    if (state == NULL || state_length < 0x1Au ||
            profile == NULL || profile_length < 8u || output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const uint8_t mode = bytes[8];
    uint32_t input_bits = float_bits(input);
    if ((input_bits & UINT32_C(0x80000000)) == 0u &&
            input_bits > UINT32_C(0x41A00000) && mode <= 3u) {
        input = 20.0f;
    } else if ((input_bits & UINT32_C(0x80000000)) == 0u &&
               input_bits > UINT32_C(0x41F00000) &&
               (mode == 4u || mode == 5u)) {
        input = 30.0f;
    }
    if (input >= 0.0f) {
        const float previous = bits_float(load_u32_le(&bytes[0x0Cu]));
        const float updated = (float)(
            (double)previous * 0x1.ccccccccccccdp-1 +
            (double)input * 0x1.999999999999ap-4);
        store_u32_le(&bytes[0x0Cu], float_bits(updated));
    }

    float derived = 0.0f;
    input_bits = float_bits(input);
    const bool encoded_below_two =
        (input_bits & UINT32_C(0x80000000)) != 0u ||
        input_bits < UINT32_C(0x40000000);
    if (encoded_below_two) {
        bytes[0x18u] = 0u;
        bytes[0x19u] = (uint8_t)(bytes[0x19u] + 1u);
        if (bytes[0x19u] > 10u) {
            bytes[0x19u] = 10u;
        }
    } else {
        bytes[0x18u] = (uint8_t)(bytes[0x18u] + 1u);
        bytes[0x19u] = 0u;
        if (bytes[0x18u] > 10u) {
            bytes[0x18u] = 10u;
        }
        const float average = bits_float(load_u32_le(&bytes[0x0Cu]));
        if (mode == 1u || mode == 2u || mode == 26u) {
            const bool encoded_above_six =
                (input_bits & UINT32_C(0x80000000)) == 0u &&
                input_bits > UINT32_C(0x40C00000);
            derived = encoded_above_six
                ? average + bits_float(UINT32_C(0x40133333))
                : average * 0.75f + 2.0f;
        } else if (mode == 3u) {
            derived = average * 0.75f + 1.0f;
        } else if (mode == 4u || mode == 5u) {
            derived = bits_float(UINT32_C(0x3E65BE5C)) +
                average * bits_float(UINT32_C(0x3EA520D2));
        }
    }
    const float multiplier = bits_float(
        load_u32_le((const uint8_t *)profile + 4u));
    *output = ((derived / bits_float(UINT32_C(0x42700000))) *
               bits_float(UINT32_C(0x404CCCCD)) * multiplier) /
              bits_float(UINT32_C(0x43480000));
    return true;
}

bool gomore_primitives_energy_interpolate_pair(
    bool alternate_mode, float primary, float secondary, float tertiary,
    gomore_primitives_float_unary_fn exponential,
    float output[2]) {
    if (exponential == NULL || output == NULL) {
        return false;
    }
    const float coefficient = bits_float(UINT32_C(0x3EB52383));
    const float intercept = bits_float(UINT32_C(0x3F312ADE));
    if (alternate_mode) {
        const float affine = gomore_primitives_exponential_affine(
            primary, bits_float(UINT32_C(0x3F240200)), 0.0f,
            bits_float(UINT32_C(0xBF71006E)), exponential);
        const float scaled = affine *
            bits_float(UINT32_C(0x3F733333)) * tertiary;
        output[0] = scaled * secondary;
        output[1] = (intercept + scaled * coefficient) * output[0];
    } else {
        const float denominator = gomore_primitives_energy_nonlinear_scale(
            primary, secondary);
        const float affine = gomore_primitives_exponential_affine(
            primary, bits_float(UINT32_C(0x40F1D654)),
            bits_float(UINT32_C(0x3F162A26)),
            bits_float(UINT32_C(0x3DB47916)), exponential);
        output[0] = 0.0f;
        if (denominator != 0.0f) {
            output[0] = (affine * secondary) / denominator;
        }
        output[1] = (intercept + affine * coefficient) * output[0];
    }
    return true;
}

bool gomore_primitives_energy_estimator_family_a(
    void *state, size_t state_length,
    const void *projection_state, size_t projection_state_length,
    float primary, float value, float upper_reference,
    float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    float output[4]) {
    if (state == NULL || state_length < 0x58u ||
            projection_state == NULL || projection_state_length < 8u ||
            exponential == NULL || output == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    const float contracted_upper = lower_reference +
        (upper_reference - lower_reference) *
            bits_float(UINT32_C(0x3F733333));
    float normalized = gomore_primitives_normalized_position(
        value, contracted_upper, lower_reference);
    if (float_bits(normalized) >= UINT32_C(0xBD23D70A)) {
        normalized = bits_float(UINT32_C(0xBD23D70A));
    }

    uint32_t count_bits = load_u32_le(&bytes[0x4Cu]);
    int32_t count = (int32_t)count_bits;
    const uint32_t normalized_bits = float_bits(normalized);
    const bool above_threshold =
        (normalized_bits & UINT32_C(0x80000000)) == 0u &&
        normalized_bits > UINT32_C(0x3ECCCCCD);
    if (above_threshold) {
        count_bits += 1u;
        store_u32_le(&bytes[0x4Cu], count_bits);
        store_u32_le(&bytes[0x50u], 0u);
    } else if (count > 0) {
        const uint32_t fall_bits = load_u32_le(&bytes[0x50u]) + 1u;
        store_u32_le(&bytes[0x50u], fall_bits);
        if ((int32_t)fall_bits > 300 && bytes[0x19u] == 10u) {
            if (!gomore_primitives_energy_state_reset(state, state_length)) {
                return false;
            }
        }
    }

    count = (int32_t)load_u32_le(&bytes[0x4Cu]);
    float pair[2];
    if (count <= 0) {
        if (!gomore_primitives_energy_interpolate_pair(
                false, normalized, primary, 1.0f,
                exponential, pair)) {
            return false;
        }
    } else {
        if (count > 600 && above_threshold) {
            const float previous = bits_float(load_u32_le(&bytes[0x54u]));
            const float divisor = (float)(count - 600);
            const float updated =
                (previous * (float)(count - 601)) / divisor +
                normalized / divisor;
            store_u32_le(&bytes[0x54u], float_bits(updated));
        }
        float factor = 1.0f;
        if (count > 1200 && above_threshold) {
            factor = 1.0f + (float)(count - 1200) *
                bits_float(UINT32_C(0x38D1ECD5));
            const uint32_t factor_bits = float_bits(factor);
            if ((factor_bits & UINT32_C(0x80000000)) == 0u &&
                    factor_bits > UINT32_C(0x3F971023)) {
                factor = bits_float(UINT32_C(0x3F971023));
            }
            const float average = bits_float(load_u32_le(&bytes[0x54u]));
            const uint32_t average_bits = float_bits(average);
            if ((average_bits & UINT32_C(0x80000000)) != 0u ||
                    average_bits < UINT32_C(0x3F19999A)) {
                factor = (float)(
                    ((double)average - 0x1.999999999999ap-2) *
                        ((double)(factor - 1.0f) /
                         0x1.999999999999ap-3) +
                    0x1.0000000000000p+0);
            }
        }
        float ratio = normalized / factor;
        const uint32_t ratio_bits = float_bits(ratio);
        if ((ratio_bits & UINT32_C(0x80000000)) == 0u &&
                ratio_bits > UINT32_C(0x3F800000)) {
            ratio = 1.0f;
        }
        if (!gomore_primitives_energy_interpolate_pair(
                true, ratio, primary, 1.0f,
                exponential, pair)) {
            return false;
        }
    }
    return gomore_primitives_energy_projection(
        projection_state, projection_state_length,
        pair[0], pair[1], output);
}

bool gomore_primitives_energy_estimator_family_b(
    const void *projection_state, size_t projection_state_length,
    float primary, float value, float upper_reference,
    float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn logarithm,
    float output[4]) {
    if (projection_state == NULL || projection_state_length < 8u ||
            exponential == NULL || logarithm == NULL ||
            output == NULL) {
        return false;
    }
    const float normalized = gomore_primitives_normalized_position(
        value, upper_reference, lower_reference);
    const float log_power = logarithm((float)(
        ((double)primary * 0x1.999999999999ap-2) /
        0x1.6666666666666p+1));
    const float shaped = (float)((double)log_power /
                                 0x1.999999999999ap-2);
    double primary_power = 0.0;
    if (primary != 0.0f) {
        primary_power = 0x1.6666666666666p+1 / (double)primary;
    }
    const float primary_log = logarithm((float)primary_power);

    const uint32_t normalized_bits = float_bits(normalized);
    const bool below_point_four =
        (normalized_bits & UINT32_C(0x80000000)) != 0u ||
        normalized_bits < UINT32_C(0x3ECCCCCD);
    float first_factor;
    if (below_point_four) {
        first_factor = exponential(primary_log + shaped * normalized);
    } else {
        first_factor = gomore_primitives_exponential_affine(
            normalized, 1.0f,
            bits_float(UINT32_C(0x3F37074F)),
            bits_float(UINT32_C(0xBEA8DE5E)), exponential);
    }

    float second_factor;
    if (below_point_four) {
        second_factor = gomore_primitives_exponential_affine(
            normalized, bits_float(UINT32_C(0x4003519B)),
            bits_float(UINT32_C(0x3F908E09)),
            bits_float(UINT32_C(0x3F26C5B0)), exponential);
    } else {
        const bool above_point_nine =
            (normalized_bits & UINT32_C(0x80000000)) == 0u &&
            normalized_bits > UINT32_C(0x3F666666);
        if (above_point_nine) {
            second_factor = (float)(
                (double)normalized * 0x1.d59697dc801e2p-2 +
                0x1.4867e744f3242p-1);
        } else {
            second_factor = gomore_primitives_exponential_affine(
                normalized, bits_float(UINT32_C(0x40B5ECBA)),
                bits_float(UINT32_C(0x3F989C4B)),
                bits_float(UINT32_C(0x3F5D432A)), exponential);
        }
    }
    const float pair_first = primary * first_factor;
    const float pair_second = pair_first * second_factor;
    return gomore_primitives_energy_projection(
        projection_state, projection_state_length,
        pair_first, pair_second, output);
}

const gomore_primitives_energy_table_configuration
gomore_primitives_energy_table_defaults = {
    .first = {
        0x0.0p+0f, 0x0.0p+0f, 0x0.0p+0f, 0x0.0p+0f, 0x0.0p+0f,
        0x0.0p+0f, 0x1.533334p+2f, 0x1.4p+2f, 0x1.333334p+2f,
        0x1.8p+2f, 0x1.19999ap+3f, 0x1.cp+2f, 0x1.533334p+2f,
        0x1.2p+3f, 0x1.333334p+2f, 0x1.0p+2f, 0x1.cp+2f,
        0x1.6p+2f, 0x1.d33334p+2f, 0x1.d33334p+2f, 0x1.0p+2f,
        0x1.333334p+2f, 0x1.6p+2f, 0x1.0p+3f, 0x1.0p+3f,
        0x1.cp+1f, 0x0.0p+0f,
    },
    .second = {
        0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f,
        0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f,
        0x1.0p+2f, 0x1.0p+0f, 0x1.0p+0f, 0x1.0p+2f, 0x1.0p+0f,
        0x1.0p+0f, 0x1.0p+1f, 0x1.0p+0f, 0x1.0p+1f, 0x1.0p+1f,
        0x1.0p+0f, 0x1.0p+0f, 0x1.0p+0f, 0x1.0p+2f, 0x1.0p+2f,
        0x1.0p+0f, 0x1.0p+0f,
    },
    .weights = {
        0x0.0p+0f, 0x0.0p+0f, 0x0.0p+0f, 0x0.0p+0f, 0x0.0p+0f,
        0x0.0p+0f, 0x1.ccccccp-2f, 0x1.ccccccp-2f,
        0x1.ccccccp-2f, 0x1.0p-1f, 0x1.99999ap-1f,
        0x1.19999ap-1f, 0x1.ccccccp-2f, 0x1.99999ap-1f,
        0x1.ccccccp-2f, 0x1.ccccccp-2f, 0x1.19999ap-1f,
        0x1.ccccccp-2f, 0x1.19999ap-1f, 0x1.19999ap-1f,
        0x1.ccccccp-2f, 0x1.ccccccp-2f, 0x1.ccccccp-2f,
        0x1.99999ap-1f, 0x1.99999ap-1f, 0x1.ccccccp-2f,
        0x0.0p+0f,
    },
};

bool gomore_primitives_energy_table_estimator(
    const void *state, size_t state_length,
    const void *projection_state, size_t projection_state_length,
    const gomore_primitives_energy_table_configuration *configuration,
    float primary, float value, float upper_reference,
    float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    float output[4]) {
    if (state == NULL || state_length < 9u ||
            projection_state == NULL || projection_state_length < 8u ||
            configuration == NULL || exponential == NULL ||
            output == NULL) {
        return false;
    }
    const uint8_t mode = ((const uint8_t *)state)[8];
    if (mode >= GOMORE_PRIMITIVES_ENERGY_TABLE_MODES) {
        return false;
    }
    const float table_first = configuration->first[mode];
    const float table_second = configuration->second[mode];
    const float selected_reference = gomore_primitives_interpolate(
        configuration->weights[mode], upper_reference, lower_reference);
    const float contracted_upper = lower_reference +
        (upper_reference - lower_reference) *
            bits_float(UINT32_C(0x3F733333));
    const float normalized = gomore_primitives_normalized_position(
        value, contracted_upper, lower_reference);
    const float normalized_reference = gomore_primitives_normalized_position(
        selected_reference, contracted_upper, lower_reference);

    float pair[2];
    float projection[4];
    if (!gomore_primitives_energy_interpolate_pair(
            true, normalized_reference, 35.0f, 1.0f,
            exponential, pair) ||
        !gomore_primitives_energy_projection(
            projection_state, projection_state_length,
            pair[0], pair[1], projection)) {
        return false;
    }
    const float reference_energy = projection[1] * 60.0f;

    if (!gomore_primitives_energy_interpolate_pair(
            false, 0.0f, 35.0f, 1.0f,
            exponential, pair) ||
        !gomore_primitives_energy_projection(
            projection_state, projection_state_length,
            pair[0], pair[1], projection)) {
        return false;
    }
    const float zero_energy = projection[1] * 60.0f;

    float primary_scale = 1.0f;
    const uint32_t normalized_bits = float_bits(normalized);
    const bool above_point_four =
        (normalized_bits & UINT32_C(0x80000000)) == 0u &&
        normalized_bits > UINT32_C(0x3ECCCCCD);
    if (above_point_four) {
        if (!gomore_primitives_energy_interpolate_pair(
                true, normalized, 35.0f, 1.0f,
                exponential, pair)) {
            return false;
        }
    } else {
        if (!gomore_primitives_energy_interpolate_pair(
                false, normalized, 35.0f, 1.0f,
                exponential, pair)) {
            return false;
        }
        primary_scale = gomore_primitives_energy_nonlinear_scale(
            normalized, 35.0f);
    }
    if (!gomore_primitives_energy_projection(
            projection_state, projection_state_length,
            pair[0], pair[1], projection)) {
        return false;
    }
    const float current_energy = projection[1] * 60.0f;
    const float denominator = reference_energy - zero_energy;
    float interpolated = 0.0f;
    if (denominator != 0.0f) {
        interpolated =
            ((current_energy - zero_energy) * table_first -
             table_second * (current_energy - reference_energy)) /
            denominator;
    }

    const float secondary_scale = primary_scale == 1.0f
        ? 1.0f
        : gomore_primitives_energy_nonlinear_scale(
            normalized, primary);
    float scaled_primary = 0.0f;
    if (secondary_scale != 0.0f) {
        scaled_primary = primary / secondary_scale;
    }
    double combined_factor = 0.0;
    if (primary_scale != 0.0f) {
        const double scale_denominator = 35.0 / (double)primary_scale;
        if (scale_denominator != 0.0) {
            const double numerator = (double)interpolated / 60.0;
            combined_factor = numerator / scale_denominator;
        }
    }
    const float combined = (float)(combined_factor *
                                   (double)scaled_primary);
    const float multiplier = bits_float(load_u32_le(
        (const uint8_t *)projection_state + 4u));
    output[0] = gomore_primitives_scaled_product(combined, multiplier);
    return true;
}

bool gomore_primitives_energy_dispatch(
    void *state, size_t state_length,
    const void *projection_state, size_t projection_state_length,
    const float settings[2], float value,
    float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn float_logarithm,
    gomore_primitives_double_unary_fn double_logarithm,
    const gomore_primitives_energy_table_configuration *table_configuration,
    float output[4]) {
    if (state == NULL || state_length < 9u ||
            projection_state == NULL || projection_state_length < 8u ||
            settings == NULL || output == NULL) {
        return false;
    }
    float normalized = gomore_primitives_normalized_position(
        value, upper_reference, lower_reference);
    uint32_t normalized_bits = float_bits(normalized);
    if ((normalized_bits & UINT32_C(0x80000000)) != 0u ||
            normalized_bits < UINT32_C(0x3DCCCCCD)) {
        normalized = bits_float(UINT32_C(0x3DCCCCCD));
    } else if (normalized_bits > UINT32_C(0x3F800000)) {
        normalized = 1.0f;
    }
    const uint8_t mode = ((const uint8_t *)state)[8];
    if (mode == 3u) {
        if (double_logarithm == NULL) {
            return false;
        }
        const float rate = (float)(
            (double_logarithm((double)normalized) *
                 0x1.27ae140000000p+1 +
             0x1.c147ae0000000p+2) *
                0x1.8000000000000p-1 +
            0x1.0000000000000p+0);
        const float multiplier = bits_float(load_u32_le(
            (const uint8_t *)projection_state + 4u));
        output[0] = ((rate / bits_float(UINT32_C(0x42700000))) *
                     bits_float(UINT32_C(0x404CCCCD)) * multiplier) /
                    bits_float(UINT32_C(0x43480000));
        return true;
    }
    if (mode == 26u) {
        const float rate = bits_float(UINT32_C(0x3F9CCCCD)) +
            normalized * bits_float(UINT32_C(0x41306666));
        const float multiplier = bits_float(load_u32_le(
            (const uint8_t *)projection_state + 4u));
        output[0] = ((rate / bits_float(UINT32_C(0x42700000))) *
                     bits_float(UINT32_C(0x404CCCCD)) * multiplier) /
                    bits_float(UINT32_C(0x43480000));
        return true;
    }
    if (mode == 0u || mode == 1u || mode == 2u) {
        return gomore_primitives_energy_estimator_family_a(
            state, state_length,
            projection_state, projection_state_length,
            settings[0], value, upper_reference, lower_reference,
            exponential, output);
    }
    if (mode == 4u || mode == 5u) {
        return gomore_primitives_energy_estimator_family_b(
            projection_state, projection_state_length,
            settings[1], value, upper_reference, lower_reference,
            exponential, float_logarithm, output);
    }
    return gomore_primitives_energy_table_estimator(
        state, state_length,
        projection_state, projection_state_length,
        table_configuration, settings[0], value,
        upper_reference, lower_reference, exponential, output);
}

_Static_assert(sizeof(gomore_primitives_energy_update_state) == 0x5Cu,
               "energy update state layout");
_Static_assert(offsetof(gomore_primitives_energy_update_state,
                        auxiliary_history) == 0x1Cu,
               "energy update history offset");
_Static_assert(offsetof(gomore_primitives_energy_update_state,
                        reference_value) == 0x58u,
               "energy update reference offset");
_Static_assert(sizeof(gomore_primitives_energy_update_output) == 0x2Cu,
               "energy update output layout");

static bool energy_update_dispatch(
    gomore_primitives_energy_update_state *state,
    const void *profile, size_t profile_length,
    const float settings[2], float current_input,
    float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn float_logarithm,
    gomore_primitives_double_unary_fn double_logarithm,
    const gomore_primitives_energy_table_configuration *table_configuration,
    float *rate) {
    float projection[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    if (!gomore_primitives_energy_dispatch(
            state, sizeof(*state), profile, profile_length,
            settings, current_input, upper_reference, lower_reference,
            exponential, float_logarithm, double_logarithm,
            table_configuration, projection)) {
        return false;
    }
    *rate = projection[0];
    return true;
}

static bool energy_update_finish(
    gomore_primitives_energy_update_state *state,
    int32_t elapsed_seconds, float current_input,
    const void *profile,
    float upper_reference, float lower_reference, float feature,
    float auxiliary, float resting_rate, float total_rate,
    bool all_active, gomore_primitives_float_unary_fn exponential,
    gomore_primitives_energy_update_output *output) {
    if (all_active) {
        if (total_rate < 0.0f) {
            total_rate = 0.0f;
        }
        output->resting_kcal = 0.0f;
        output->active_kcal = total_rate * (float)elapsed_seconds;
    } else {
        if (!gomore_primitives_float_floor_update(
                resting_rate, &total_rate)) {
            return false;
        }
        const float previous = state->current_rate;
        if (float_bits(previous < 0.0f ? -previous : previous) >
                UINT32_C(0x358637BD)) {
            const float delta = total_rate - previous;
            const float limit =
                (bits_float(UINT32_C(0x3951B717)) /
                 (previous * bits_float(UINT32_C(0x42C80000)))) *
                bits_float(load_u32_le(
                    (const uint8_t *)profile + 4u));
            const float lower_limit = limit * -1.5f;
            float bounded_delta = delta;
            if (delta < lower_limit) {
                bounded_delta = lower_limit;
            } else if (delta > limit * 2.0f) {
                bounded_delta = limit * 2.0f;
            }
            total_rate = total_rate *
                ((previous + bounded_delta) / total_rate);
        }

        float resting_component = resting_rate;
        if (!(auxiliary < 0.0f)) {
            resting_component *=
                bits_float(UINT32_C(0x3F28F5C3)) /
                    (exponential(-auxiliary) + 1.0f) +
                bits_float(UINT32_C(0x3F2B851F));
        }
        float active_component = 0.0f;
        if (total_rate > resting_component) {
            active_component = total_rate - resting_component;
        }
        output->resting_kcal = resting_component *
                               (float)elapsed_seconds;
        output->active_kcal = active_component *
                              (float)elapsed_seconds;
    }

    state->current_rate = total_rate;
    state->reference_value = current_input;
    output->total_kcal = output->resting_kcal + output->active_kcal;
    const float weight = bits_float(load_u32_le(
        (const uint8_t *)profile + 4u));
    output->metabolic_equivalent = gomore_primitives_scaled_ratio(
        output->total_kcal, weight);
    const float fat_fraction = gomore_primitives_substrate_fat_fraction(
        current_input, upper_reference, lower_reference, exponential);
    output->fat_kcal = output->total_kcal * fat_fraction;
    output->carbohydrate_kcal = output->total_kcal - output->fat_kcal;
    return gomore_primitives_energy_zone_accumulate(
        state, sizeof(*state), elapsed_seconds,
        output->metabolic_equivalent, current_input,
        upper_reference, lower_reference, feature,
        exponential, output->zone_totals);
}

uint32_t gomore_primitives_energy_update(
    gomore_primitives_energy_update_state *state,
    int32_t elapsed_seconds, float current_input,
    const void *profile, size_t profile_length,
    float upper_reference, float lower_reference,
    const float settings[2], float metric, float auxiliary,
    int8_t control_code, float secondary_value,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn float_logarithm,
    gomore_primitives_double_unary_fn double_logarithm,
    const gomore_primitives_energy_table_configuration *table_configuration,
    gomore_primitives_energy_update_output *output) {
    if (output != NULL) {
        clear_bytes((uint8_t *)output, sizeof(*output));
    }
    if (state == NULL || profile == NULL || profile_length < 10u ||
            settings == NULL || exponential == NULL ||
            float_logarithm == NULL || double_logarithm == NULL ||
            output == NULL || elapsed_seconds < 1) {
        return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
    }
    const gomore_primitives_energy_table_configuration *tables =
        table_configuration != NULL
            ? table_configuration
            : &gomore_primitives_energy_table_defaults;
    const float resting_rate = gomore_primitives_daily_resting_kcal(
        profile, profile_length) / bits_float(UINT32_C(0x47A8C000));

    bool recent_reference = true;
    if (gomore_primitives_float_in_encoded_range(current_input)) {
        state->elapsed_since_reference = 0;
    } else {
        state->elapsed_since_reference = (int32_t)(
            (uint32_t)state->elapsed_since_reference +
            (uint32_t)elapsed_seconds);
        if (!gomore_primitives_float_in_encoded_range(
                state->reference_value)) {
            state->reference_value = lower_reference;
        }
        current_input = state->reference_value;
    }
    if (state->elapsed_since_reference > 600) {
        recent_reference = false;
        current_input = lower_reference;
    }
    if (elapsed_seconds > 600) {
        state->current_rate = 0.0f;
        if (!gomore_primitives_energy_state_reset(state, sizeof(*state))) {
            return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
        }
        elapsed_seconds = 1;
    }

    for (size_t index = 0u; index < 9u; ++index) {
        state->auxiliary_history[index] =
            state->auxiliary_history[index + 1u];
    }
    if (auxiliary < 0.0f) {
        for (size_t index = 0u; index < 10u; ++index) {
            state->auxiliary_history[index] = 0.0f;
        }
    } else {
        state->auxiliary_history[9] = auxiliary > 1000.0f
            ? 1000.0f
            : auxiliary;
    }
    float auxiliary_average = 0.0f;
    for (size_t index = 0u; index < 10u; ++index) {
        auxiliary_average += state->auxiliary_history[index];
    }
    auxiliary_average /= 10.0f;

    float normalized = gomore_primitives_normalized_position(
        current_input, upper_reference, lower_reference);
    if (normalized < 0.0f) {
        normalized = 0.0f;
    } else if (float_bits(normalized) > UINT32_C(0x3F800000)) {
        normalized = 1.0f;
    }

    float rate = 0.0f;
    if (!energy_update_dispatch(
            state, profile, profile_length, settings,
            current_input, upper_reference, lower_reference,
            exponential, float_logarithm, double_logarithm,
            tables, &rate)) {
        return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
    }

    const bool auxiliary_at_least_ten =
        (int32_t)float_bits(auxiliary) >= (int32_t)UINT32_C(0x41200000);
    if (recent_reference &&
            float_bits(normalized) <= UINT32_C(0x3DE147AE) &&
            !auxiliary_at_least_ten && state->mode == 0u) {
        rate = resting_rate;
    } else if (state->mode == 0u) {
        if (!(auxiliary < 0.0f)) {
            float activity = exponential(
                auxiliary_average * bits_float(UINT32_C(0x36B88CA4))) -
                1.0f;
            activity *= bits_float(load_u32_le(
                (const uint8_t *)profile + 4u));
            if (control_code == 0 || control_code == -2) {
                activity *= bits_float(UINT32_C(0x3F19999A));
            } else if (control_code == -1) {
                activity *= bits_float(UINT32_C(0x3F333333));
            } else {
                activity *= bits_float(UINT32_C(0x3F8CCCCD));
            }
            rate = resting_rate + activity;
        }
    } else if (state->mode <= 5u) {
        const float weight = bits_float(load_u32_le(
            (const uint8_t *)profile + 4u));
        if (state->variant == 0) {
            const bool secondary_override =
                (state->mode == 4u || state->mode == 5u) &&
                secondary_value > 0.0f &&
                secondary_value <
                    weight * bits_float(UINT32_C(0x41C970A4));
            if (!energy_update_dispatch(
                    state, profile, profile_length, settings,
                    current_input, upper_reference, lower_reference,
                    exponential, float_logarithm, double_logarithm,
                    tables, &rate)) {
                return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
            }
            if (secondary_override) {
                const float secondary_rate = (float)(
                    ((double)secondary_value /
                     0x1.c28f5c28f5c29p-3) /
                    0x1.0cccccccccccdp+2 /
                    0x1.f400000000000p+9);
                rate = (rate + secondary_rate) * 0.5f;
            } else if (float_bits(metric) > UINT32_C(0x40000000)) {
                float mode_rate = 0.0f;
                if (!gomore_primitives_energy_mode_rate(
                        state, sizeof(*state), profile, profile_length,
                        metric, &mode_rate)) {
                    return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
                }
                rate = (rate + mode_rate) * 0.5f;
            }
        } else if (state->variant == 1) {
            float positive_metric = metric > 0.0f ? metric : 0.0f;
            if (state->mode == 1u) {
                if (float_bits(positive_metric) > UINT32_C(0x40000000)) {
                    const float scaled = positive_metric *
                        bits_float(UINT32_C(0x39837C77));
                    rate = weight * (float)(
                        (double)scaled + 0x1.60981b3f4b9a6p-12);
                }
            } else if (state->mode == 2u) {
                if (auxiliary_average < 0.0f) {
                    rate = resting_rate;
                } else if (control_code == 2) {
                    rate = rate * bits_float(UINT32_C(0x3DCCCCCD)) +
                        weight *
                            (bits_float(UINT32_C(0x3AE6E121)) +
                             auxiliary_average *
                                 bits_float(UINT32_C(0x36067DC3))) *
                            bits_float(UINT32_C(0x3F99999A)) *
                            bits_float(UINT32_C(0x3F666666));
                } else {
                    const float auxiliary_rate = weight *
                        (bits_float(UINT32_C(0x3ABC0F6D)) +
                         auxiliary_average *
                             bits_float(UINT32_C(0x364D3A87)));
                    float alternate_rate = 0.0f;
                    if (!energy_update_dispatch(
                            state, profile, profile_length, settings,
                            current_input, upper_reference, 50.0f,
                            exponential, float_logarithm,
                            double_logarithm, tables, &alternate_rate)) {
                        return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
                    }
                    rate = (alternate_rate + auxiliary_rate) * 0.5f;
                }
            } else if (state->mode == 3u) {
                rate = positive_metric > 0.0f
                    ? (rate + resting_rate +
                       (bits_float(UINT32_C(0x39A46956)) +
                        positive_metric *
                            bits_float(UINT32_C(0x39252137))) * weight) *
                          0.5f
                    : resting_rate;
            } else if (state->mode == 4u) {
                if (positive_metric > 0.0f) {
                    float addition =
                        positive_metric * bits_float(UINT32_C(0x38E339F7)) -
                        bits_float(UINT32_C(0x3A1B70DF));
                    if (addition < 0.0f) {
                        addition = 0.0f;
                    }
                    rate = resting_rate + addition * weight;
                } else {
                    rate = resting_rate;
                }
            } else if (state->mode == 5u) {
                rate = weight *
                    (current_input * bits_float(UINT32_C(0x377338C6)) +
                     auxiliary_average * bits_float(UINT32_C(0x36E9DCBA)) -
                     bits_float(UINT32_C(0x39077371)));
            }
        } else {
            rate = resting_rate;
            if (state->variant == 2) {
                if (state->mode == 1u || state->mode == 2u) {
                    rate = weight *
                        (bits_float(UINT32_C(0x39178DA0)) +
                         (metric > 0.0f ? metric : 0.0f) *
                             bits_float(UINT32_C(0x3B2D0C52)));
                } else if (state->mode == 3u) {
                    float mode_rate = 0.0f;
                    if (!gomore_primitives_energy_mode_rate(
                            state, sizeof(*state), profile, profile_length,
                            metric, &mode_rate)) {
                        return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
                    }
                    if (float_bits(metric) > UINT32_C(0x40000000)) {
                        rate = mode_rate;
                        if (state->high_counter == 10u && recent_reference) {
                            const float unit = mode_rate / mode_rate;
                            state->blend = (float)(
                                (double)state->blend *
                                    0x1.ccccccccccccdp-1 +
                                (double)unit *
                                    0x1.999999999999ap-4);
                        }
                        if (float_bits(metric) < UINT32_C(0x40C00000)) {
                            float factor = 0.5f - metric * 0.25f;
                            if (factor < 0.0f) {
                                factor = 0.0f;
                            }
                            rate = mode_rate * state->blend *
                                       (1.0f - factor) +
                                   mode_rate * factor;
                        }
                    }
                    rate *= bits_float(UINT32_C(0x3F666666));
                } else if (state->mode == 4u) {
                    rate = weight *
                        (metric * bits_float(UINT32_C(0x3B2FC8C9)) -
                         bits_float(UINT32_C(0x37B905C0)));
                } else if (state->mode == 5u) {
                    rate = weight *
                        (bits_float(UINT32_C(0x3911AF7F)) +
                         metric * bits_float(UINT32_C(0x3B0BFC6C)));
                }
            }
        }
    }

    if (!energy_update_finish(
            state, elapsed_seconds, current_input,
            profile,
            upper_reference, lower_reference, settings[0],
            auxiliary, resting_rate, rate, state->variant == 2,
            exponential, output)) {
        clear_bytes((uint8_t *)output, sizeof(*output));
        return GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID;
    }
    return GOMORE_PRIMITIVES_ENERGY_STATUS_OK;
}

_Static_assert(sizeof(gomore_primitives_activity_accumulator_state) == 0x34u,
               "activity accumulator state layout");
_Static_assert(sizeof(gomore_primitives_activity_accumulator_output) == 0x2Cu,
               "activity accumulator output layout");
_Static_assert(sizeof(gomore_primitives_sleep_statistics) == 0x4Cu,
               "sleep statistics layout");
_Static_assert(sizeof(gomore_primitives_sleep_optical_history) == 0x18Cu,
               "sleep optical history layout");

static int32_t energy_float_to_i32(float value) {
    if (value != value) {
        return 0;
    }
    if (value >= 2147483648.0f) {
        return INT32_MAX;
    }
    if (value <= -2147483648.0f) {
        return INT32_MIN;
    }
    return (int32_t)value;
}

bool gomore_primitives_activity_accumulate(
    gomore_primitives_activity_accumulator_state *state,
    uint32_t unix_seconds, int16_t timezone_minutes,
    float step_increment,
    const gomore_primitives_energy_update_output *energy,
    float selected_speed,
    gomore_primitives_activity_accumulator_output *output) {
    if (state == NULL || energy == NULL || output == NULL) {
        return false;
    }
    const uint32_t local_seconds = unix_seconds +
        (uint32_t)((int32_t)timezone_minutes * 60);
    const uint32_t local_day = local_seconds / UINT32_C(86400);
    if ((int32_t)state->local_day < (int32_t)local_day) {
        clear_bytes((uint8_t *)state, sizeof(*state));
        state->timezone_minutes = (int32_t)timezone_minutes;
        state->local_day = local_day;
        clear_bytes((uint8_t *)output, sizeof(*output));
    }
    if (state->timezone_minutes != (int32_t)timezone_minutes) {
        state->timezone_minutes = (int32_t)timezone_minutes;
        if ((int32_t)state->local_day < (int32_t)local_day) {
            state->local_day = local_day;
        }
    }
    if (!(step_increment < 0.0f)) {
        state->cumulative_steps += step_increment;
    }
    if (!(energy->active_kcal < 0.0f)) {
        state->cumulative_active_kcal += energy->active_kcal;
    }
    if (!(energy->total_kcal < 0.0f)) {
        state->cumulative_total_kcal += energy->total_kcal;
    }
    if (!(selected_speed < 0.0f)) {
        state->cumulative_distance += selected_speed /
                                      bits_float(UINT32_C(0x45610000));
    }
    output->steps = (uint32_t)energy_float_to_i32(
        state->cumulative_steps);
    output->active_kcal = energy_float_to_i32(
        state->cumulative_active_kcal);
    output->total_kcal = energy_float_to_i32(
        state->cumulative_total_kcal);
    output->distance = state->cumulative_distance;
    return true;
}

int32_t gomore_primitives_profile_convert(
    const gomore_primitives_profile_input *input,
    float persistent_cache[2],
    gomore_primitives_profile_output *output) {
    if (input == NULL || persistent_cache == NULL || output == NULL) {
        return -1;
    }
    int32_t status = 0;

    uint8_t age;
    if (float_bits(input->age_years) + UINT32_C(0xBEE00000) <=
            UINT32_C(0x01A60000)) {
        age = (uint8_t)(uint32_t)input->age_years;
    } else {
        age = 30u;
        status = -101;
    }

    uint8_t binary_sex;
    if (input->binary_sex == 0.0f || input->binary_sex == 1.0f) {
        binary_sex = (uint8_t)(uint32_t)input->binary_sex;
    } else {
        binary_sex = 1u;
        status = -102;
    }

    float height = input->height_centimeters;
    if (float_bits(height) + UINT32_C(0xBD380000) >
            UINT32_C(0x00940000)) {
        height = 170.0f;
        status = -103;
    }

    float weight = input->weight_kilograms;
    if (float_bits(weight) + UINT32_C(0xBEE00000) >
            UINT32_C(0x01F60000)) {
        weight = 60.0f;
        status = -104;
    }

    float parameter_4 = input->parameter_4;
    if (float_bits(parameter_4) + UINT32_C(0xBCF60000) >
            UINT32_C(0x00520000)) {
        parameter_4 = 208.0f - (float)age *
                      bits_float(UINT32_C(0x3F333333));
        if (float_bits(input->parameter_4) != UINT32_C(0xBF800000)) {
            status = -105;
        }
    }

    float parameter_5_normalized = input->parameter_5;
    if (float_bits(parameter_5_normalized) + UINT32_C(0xBDE00000) >
            UINT32_C(0x00A80000)) {
        parameter_5_normalized = 60.0f;
        if (float_bits(input->parameter_5) != UINT32_C(0xBF800000)) {
            status = -106;
        }
    }

    float cached[2];
    if (input->parameter_6 > 0.0f) {
        cached[0] = input->parameter_6;
    } else {
        cached[0] = 35.0f;
        if (float_bits(input->parameter_6) != UINT32_C(0xBF800000)) {
            status = -107;
        }
    }
    cached[1] = 35.0f;
    for (size_t index = 0u; index < 2u; ++index) {
        if (persistent_cache[index] > 0.0f) {
            cached[index] = persistent_cache[index];
        } else {
            /* Stock stores both fallback iterations into cache slot zero. */
            persistent_cache[0] = cached[index];
        }
    }

    output->age_years = age;
    output->binary_sex = binary_sex;
    output->reserved[0] = 0u;
    output->reserved[1] = 0u;
    output->height_centimeters = height;
    output->weight_kilograms = weight;
    output->parameter_4 = parameter_4;
    output->parameter_5_raw = input->parameter_5;
    output->parameter_5_normalized = parameter_5_normalized;
    output->cached_parameters[0] = cached[0];
    output->cached_parameters[1] = cached[1];
    return status;
}

bool gomore_primitives_sleep_interval_statistics(
    const uint8_t *stages, size_t stage_bytes,
    uint32_t start_timestamp, uint32_t end_timestamp,
    bool packed, float output[7]) {
    if (stages == NULL || output == NULL) {
        return false;
    }
    const uint32_t duration = end_timestamp - start_timestamp;
    const float duration_epochs_float = (float)duration / 30.0f;
    const int32_t duration_epochs =
        float_bits(duration_epochs_float) < UINT32_C(0x45340000)
            ? energy_float_to_i32(duration_epochs_float)
            : 2880;
    const int32_t first_epoch = energy_float_to_i32(
        (float)start_timestamp / 30.0f);
    const int32_t end_epoch = energy_float_to_i32(
        (float)end_timestamp / 30.0f);

    bool sleep_seen = false;
    float leading_awake = 0.0f;
    float trailing_awake = 0.0f;
    float sleep = 0.0f;
    float awake = 0.0f;
    for (int32_t epoch = first_epoch; epoch < end_epoch; ++epoch) {
        uint8_t stage = 0u;
        if (!gomore_primitives_modulo_value_get(
                stages, stage_bytes, (uint32_t)epoch, packed, &stage)) {
            return false;
        }
        if (stage == 0u) {
            awake += 1.0f;
            trailing_awake += 1.0f;
            if (!sleep_seen) {
                leading_awake += 1.0f;
            }
        } else {
            sleep += 1.0f;
            sleep_seen = true;
            trailing_awake = 0.0f;
        }
    }

    const float middle_awake = awake - (leading_awake + trailing_awake);
    if (middle_awake < 0.0f || duration_epochs < 1) {
        for (size_t index = 0u; index < 7u; ++index) {
            output[index] = -1.0f;
        }
        return true;
    }

    const float leading_minutes = leading_awake * 0.5f;
    const float sleep_minutes = sleep * 0.5f;
    const float middle_minutes = middle_awake * 0.5f;
    const float trailing_minutes = trailing_awake * 0.5f;
    const float interval_minutes = leading_minutes + sleep_minutes +
        middle_minutes + trailing_minutes;
    output[0] = interval_minutes;
    output[1] = leading_minutes;
    output[2] = sleep_minutes;
    output[3] = middle_minutes;
    output[4] = middle_minutes + trailing_minutes;
    output[5] = sleep_minutes + middle_minutes;
    output[6] = sleep_minutes / interval_minutes;
    return true;
}

bool gomore_primitives_sleep_stage_statistics(
    const uint8_t *stages, size_t stage_bytes,
    uint32_t start_timestamp, uint32_t end_timestamp,
    bool packed, float output[12]) {
    if (stages == NULL || output == NULL) {
        return false;
    }
    const uint32_t duration = end_timestamp - start_timestamp;
    const float duration_epochs_float = (float)duration / 30.0f;
    const int32_t duration_epochs =
        float_bits(duration_epochs_float) < UINT32_C(0x45340000)
            ? energy_float_to_i32(duration_epochs_float)
            : 2880;
    const int32_t first_epoch = energy_float_to_i32(
        (float)start_timestamp / 30.0f);
    const int32_t end_epoch = energy_float_to_i32(
        (float)end_timestamp / 30.0f);

    float counts[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    for (int32_t epoch = first_epoch; epoch < end_epoch; ++epoch) {
        uint8_t stage = 0u;
        if (!gomore_primitives_modulo_value_get(
                stages, stage_bytes, (uint32_t)epoch, packed, &stage)) {
            return false;
        }
        if (stage <= 3u) {
            counts[stage] += 1.0f;
        }
    }

    const float nrem_count = counts[2] + counts[3];
    const float duration_denominator = (float)duration_epochs;
    output[0] = duration_epochs == 0
        ? 0.0f : nrem_count / duration_denominator;
    output[1] = duration_epochs == 0
        ? 0.0f : counts[1] / duration_denominator;
    output[2] = duration_epochs == 0
        ? 0.0f : counts[2] / duration_denominator;
    output[3] = duration_epochs == 0
        ? 0.0f : counts[3] / duration_denominator;
    output[4] = nrem_count == 0.0f
        ? 0.0f : counts[1] / nrem_count;
    output[5] = counts[2] == 0.0f
        ? 0.0f : counts[3] / counts[2];
    output[6] = counts[1] == 0.0f
        ? 0.0f : counts[3] / counts[1];
    output[7] = nrem_count == 0.0f
        ? 0.0f : counts[3] / nrem_count;
    output[8] = counts[0] * 0.5f;
    output[9] = counts[1] * 0.5f;
    output[10] = counts[2] * 0.5f;
    output[11] = counts[3] * 0.5f;
    return true;
}

bool gomore_primitives_sleep_score(
    const gomore_primitives_sleep_statistics *statistics,
    gomore_primitives_double_unary_fn hyperbolic_tangent,
    gomore_primitives_float_binary_fn power,
    float *score) {
    if (statistics == NULL || hyperbolic_tangent == NULL ||
            power == NULL || score == NULL) {
        return false;
    }

    const float sleep_minutes = statistics->non_awake_minutes;
    const uint32_t sleep_bits = float_bits(sleep_minutes);
    float baseline = 0.0f;
    float factor = 0.0f;
    float target_hours = 0.0f;
    if (sleep_bits + UINT32_C(0xBC4C0000) < UINT32_C(0x003C0000)) {
        baseline = 95.0f;
        factor = 6.0f;
        target_hours = 7.0f;
    } else if (sleep_bits + UINT32_C(0xBC6A0000) <
                   UINT32_C(0x001E0000) ||
               sleep_bits + UINT32_C(0xBC100000) <
                   UINT32_C(0x000F0000)) {
        baseline = 89.0f;
        factor = 15.0f;
        target_hours = (int32_t)sleep_bits <
                (int32_t)(UINT32_C(0) - UINT32_C(0xBC4C0000))
            ? 6.0f : 8.0f;
    } else if (sleep_bits + UINT32_C(0xBC790000) <
                   UINT32_C(0x000F0000) ||
               sleep_bits + UINT32_C(0xBC010000) <
                   UINT32_C(0x00080000)) {
        baseline = 74.0f;
        factor = 15.0f;
        target_hours = (int32_t)sleep_bits <
                (int32_t)(UINT32_C(0) - UINT32_C(0xBC6A0000))
            ? 5.0f : 8.5f;
    } else if (UINT32_C(0x00800000) <
               sleep_bits + UINT32_C(0xBC790000)) {
        baseline = 59.0f;
        factor = 15.0f;
        target_hours = (int32_t)sleep_bits <
                (int32_t)(UINT32_C(0) - UINT32_C(0xBC790000))
            ? 4.5f : 9.0f;
    }

    float duration_delta = sleep_minutes / 60.0f - target_hours;
    duration_delta = bits_float(
        float_bits(duration_delta) & UINT32_C(0x7FFFFFFF));
    const float duration_score = (float)(
        (double)baseline - (double)factor *
        hyperbolic_tangent((double)duration_delta));

    float wake_ratio = 0.0f;
    if (sleep_minutes != 0.0f) {
        wake_ratio = statistics->awake_after_onset_minutes / sleep_minutes;
    }
    const float wake_percentage = wake_ratio * 100.0f;
    const float wake_exponent = wake_ratio +
        ((int32_t)float_bits(wake_percentage) < INT32_C(0x42200000)
            ? bits_float(UINT32_C(0x3DE147AE))
            : bits_float(UINT32_C(0x4050A3D7)));
    const float wake_adjusted = duration_score /
        power(bits_float(UINT32_C(0x3F8CCCCD)), wake_exponent);

    const uint32_t rem_bits = float_bits(statistics->rem_fraction);
    float rem_weight = 0.1f;
    if (rem_bits + UINT32_C(0xC2333333) <= UINT32_C(0x01000000)) {
        if (rem_bits + UINT32_C(0xC1E66666) < UINT32_C(0x0099999A)) {
            rem_weight = rem_bits + UINT32_C(0xC1B33333) <
                    UINT32_C(0x004CCCCE)
                ? 0.3f : 0.4f;
        } else {
            rem_weight = 0.2f;
        }
    }

    const uint32_t deep_bits = float_bits(statistics->deep_fraction);
    float deep_weight;
    if ((int32_t)deep_bits < INT32_C(0x3D4CCCCD)) {
        deep_weight = 0.1f;
    } else if ((int32_t)deep_bits <
               (int32_t)(UINT32_C(0) - UINT32_C(0xC2333333))) {
        deep_weight = 0.2f;
    } else if (deep_bits + UINT32_C(0xC1E66666) <
               UINT32_C(0x00666667)) {
        deep_weight = 0.4f;
    } else {
        deep_weight = 0.3f;
    }

    float result = wake_adjusted + rem_weight + deep_weight;
    const float upper_candidate =
        (int32_t)float_bits(result) < INT32_C(0x42C80000)
            ? result : 100.0f;
    if (!(upper_candidate >= 0.0f)) {
        result = 0.0f;
    } else if ((int32_t)float_bits(result) >= INT32_C(0x42C80000)) {
        result = 100.0f;
    }
    *score = result;
    return true;
}

bool gomore_primitives_moving_average_extrema_indices(
    const float *values, size_t count,
    uint32_t long_window, uint32_t short_window,
    uint8_t *maxima, size_t maxima_capacity, size_t *maxima_count,
    uint8_t *minima, size_t minima_capacity, size_t *minima_count) {
    if (values == NULL || maxima == NULL || maxima_count == NULL ||
            minima == NULL || minima_count == NULL || count > 256u ||
            long_window == 0u || short_window == 0u ||
            (count != 0u &&
             ((size_t)long_window > count ||
              (size_t)short_window > count)) ||
            maxima_capacity < GOMORE_PRIMITIVES_EXTREMA_CAPACITY ||
            minima_capacity < GOMORE_PRIMITIVES_EXTREMA_CAPACITY) {
        return false;
    }

    *maxima_count = 0u;
    *minima_count = 0u;
    if (count == 0u) {
        return true;
    }

    uint8_t pending_maxima[GOMORE_PRIMITIVES_EXTREMA_CAPACITY];
    uint8_t pending_minima[GOMORE_PRIMITIVES_EXTREMA_CAPACITY];
    size_t pending_maxima_count = 0u;
    size_t pending_minima_count = 0u;
    const size_t long_half = (size_t)(long_window >> 1u);
    const size_t short_half = (size_t)(short_window >> 1u);
    float long_sum = 0.0f;
    float short_sum = 0.0f;
    float extremum = 0.0f;
    size_t extremum_index = 0u;
    bool previous_above = false;

    for (size_t index = 0u; index < count; ++index) {
        if (index == 0u) {
            for (int64_t offset = -(int64_t)long_half;
                 offset < (int64_t)(size_t)long_window -
                              (int64_t)long_half;
                 ++offset) {
                long_sum += offset < 0
                    ? values[0] : values[(size_t)offset];
            }
            for (int64_t offset = -(int64_t)short_half;
                 offset < (int64_t)(size_t)short_window -
                              (int64_t)short_half;
                 ++offset) {
                short_sum += offset < 0
                    ? values[0] : values[(size_t)offset];
            }
        } else {
            const size_t long_out = index <= long_half
                ? 0u : index - long_half - 1u;
            size_t long_in = index + (size_t)long_window - long_half - 1u;
            if (long_in >= count) {
                long_in = count - 1u;
            }
            long_sum = values[long_in] + (long_sum - values[long_out]);

            const size_t short_out = index <= short_half
                ? 0u : index - short_half - 1u;
            size_t short_in =
                index + (size_t)short_window - short_half - 1u;
            if (short_in >= count) {
                short_in = count - 1u;
            }
            short_sum = values[short_in] +
                        (short_sum - values[short_out]);
        }

        const bool above = short_sum / (float)short_window >
                           long_sum / (float)long_window;
        if (index == 0u) {
            extremum = values[0];
            extremum_index = 0u;
        } else if (above == previous_above) {
            if ((above && values[index] > extremum) ||
                    (!above && values[index] < extremum)) {
                extremum = values[index];
                extremum_index = index;
            }
        } else {
            if (previous_above) {
                if (pending_maxima_count >=
                        GOMORE_PRIMITIVES_EXTREMA_CAPACITY) {
                    return false;
                }
                pending_maxima[pending_maxima_count++] =
                    (uint8_t)extremum_index;
            } else {
                if (pending_minima_count >=
                        GOMORE_PRIMITIVES_EXTREMA_CAPACITY) {
                    return false;
                }
                pending_minima[pending_minima_count++] =
                    (uint8_t)extremum_index;
            }
            extremum = values[index];
            extremum_index = index;
        }
        previous_above = above;
    }

    for (size_t index = 0u; index < pending_maxima_count; ++index) {
        maxima[index] = pending_maxima[index];
    }
    for (size_t index = 0u; index < pending_minima_count; ++index) {
        minima[index] = pending_minima[index];
    }
    *maxima_count = pending_maxima_count;
    *minima_count = pending_minima_count;
    return true;
}

bool gomore_primitives_final_sleep_build(
    uint8_t *packed_timeline, size_t packed_timeline_length,
    uint32_t now, const uint8_t configuration[11],
    const gomore_primitives_sleep_interval_result *interval,
    gomore_primitives_sleep_stage_refine_fn refine,
    gomore_primitives_double_unary_fn hyperbolic_tangent,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_final_sleep_build_output *output,
    int32_t *status) {
    if (packed_timeline == NULL || configuration == NULL ||
            interval == NULL || refine == NULL ||
            hyperbolic_tangent == NULL || power == NULL ||
            output == NULL || status == NULL || output->stages == NULL ||
            output->stage_capacity > 2880u) {
        return false;
    }

    int8_t *const stages = output->stages;
    const size_t stage_capacity = output->stage_capacity;
    clear_bytes((uint8_t *)output, sizeof(*output));
    output->stages = stages;
    output->stage_capacity = stage_capacity;
    *status = 0;

    if (!gomore_primitives_recent_interval_predicate(
            interval, sizeof(*interval), now)) {
        *status = -1;
        return true;
    }

    output->wire_type = (interval->flags & UINT8_C(0x10)) != 0u ? 1u : 2u;
    output->start_timestamp = interval->start;
    output->end_timestamp = interval->end;
    if (output->wire_type != 1u) {
        return true;
    }

    const uint32_t offset_seconds = (uint32_t)configuration[1] * 30u;
    size_t stage_count = 0u;
    if (!gomore_primitives_packed_timeline_extract(
            packed_timeline, packed_timeline_length,
            output->start_timestamp + offset_seconds,
            output->end_timestamp + offset_seconds,
            interval->source_start, interval->source_end,
            interval->metadata, (uint8_t *)stages,
            stage_capacity, &stage_count)) {
        return false;
    }

    if (stage_count > 0u) {
        if (!refine(configuration, stages, stage_capacity, &stage_count,
                    output->end_timestamp - output->start_timestamp) ||
                stage_count > stage_capacity) {
            return false;
        }
        output->stage_count = stage_count;
        float *const statistics =
            (float *)(void *)&output->statistics;
        if (!gomore_primitives_sleep_interval_statistics(
                (const uint8_t *)stages, stage_count, 0u,
                output->end_timestamp - output->start_timestamp,
                false, statistics) ||
                !gomore_primitives_sleep_stage_statistics(
                    (const uint8_t *)stages, stage_count, 0u,
                    output->end_timestamp - output->start_timestamp,
                    false, &statistics[7]) ||
                !gomore_primitives_sleep_score(
                    &output->statistics, hyperbolic_tangent,
                    power, &output->score)) {
            return false;
        }
    }

    if (output->statistics.leading_awake_minutes > 0.0f) {
        float extension =
            output->statistics.leading_awake_minutes * 0.5f;
        float candidate = extension;
        if ((int32_t)float_bits(extension) < INT32_C(0x3F000000)) {
            candidate = 0.5f;
        }
        if ((int32_t)float_bits(candidate) < INT32_C(0x41200000)) {
            if ((int32_t)float_bits(extension) < INT32_C(0x3F000000)) {
                extension = 0.5f;
            }
        } else {
            extension = 10.0f;
        }
        const int8_t shift =
            (int8_t)energy_float_to_i32(extension * 2.0f);
        if (shift < 0 || !gomore_primitives_shift_marked_history(
                (uint8_t *)stages, stage_capacity, &stage_count,
                (size_t)shift)) {
            return false;
        }
        output->start_timestamp -= (uint32_t)(int32_t)shift * 30u;
        output->stage_count = stage_count;
        float *const statistics =
            (float *)(void *)&output->statistics;
        if (!gomore_primitives_sleep_interval_statistics(
                (const uint8_t *)stages, stage_count, 0u,
                output->end_timestamp - output->start_timestamp,
                false, statistics) ||
                !gomore_primitives_sleep_stage_statistics(
                    (const uint8_t *)stages, stage_count, 0u,
                    output->end_timestamp - output->start_timestamp,
                    false, &statistics[7]) ||
                !gomore_primitives_sleep_score(
                    &output->statistics, hyperbolic_tangent,
                    power, &output->score)) {
            return false;
        }
    }
    return true;
}

bool gomore_primitives_sleep_peak_rate_interpolate(
    const int16_t *peaks, size_t peak_count,
    int32_t scale, int32_t output_start,
    float *output, size_t output_count) {
    if (peaks == NULL || output == NULL || scale <= 0 ||
            scale > INT32_MAX / 60 || output_count > (size_t)INT32_MAX ||
            (output_count > 0u &&
             output_start > INT32_MAX - (int32_t)output_count)) {
        return false;
    }
    for (size_t index = 0u; index < output_count; ++index) {
        output[index] = 60.0f;
    }

    int32_t left_index = gomore_primitives_find_next_nonnegative_i16(
        peaks, peak_count, 0u);
    if (left_index < 0) {
        return true;
    }
    const float numerator = (float)(scale * 60);
    size_t output_index = 0u;
    const uint16_t first_position = (uint16_t)peaks[(size_t)left_index];
    while (output_index < output_count) {
        const float grid = (float)(output_start + (int32_t)output_index);
        if (!((float)first_position / (float)scale > grid)) {
            break;
        }
        const uint16_t next_position =
            (uint16_t)peaks[(size_t)left_index + 1u] & UINT16_C(0x7FFF);
        const uint16_t current_position = first_position & UINT16_C(0x7FFF);
        output[output_index] = numerator /
            (float)((int32_t)next_position - (int32_t)current_position);
        ++output_index;
    }

    for (;;) {
        const int32_t right_index =
            gomore_primitives_find_next_nonnegative_i16(
                peaks, peak_count, (size_t)left_index + 1u);
        if (right_index < 0) {
            break;
        }
        const uint16_t left_position =
            (uint16_t)peaks[(size_t)left_index];
        const uint16_t right_position =
            (uint16_t)peaks[(size_t)right_index];
        const uint16_t left_next =
            (uint16_t)peaks[(size_t)left_index + 1u] & UINT16_C(0x7FFF);
        const uint16_t right_next =
            (uint16_t)peaks[(size_t)right_index + 1u] & UINT16_C(0x7FFF);
        const uint16_t left_low = left_position & UINT16_C(0x7FFF);
        const uint16_t right_low = right_position & UINT16_C(0x7FFF);
        if (left_next == left_low || right_next == right_low ||
                right_position == left_position) {
            return false;
        }
        const float left_rate = numerator /
            (float)((int32_t)left_next - (int32_t)left_low);
        const float right_rate = numerator /
            (float)((int32_t)right_next - (int32_t)right_low);
        const float gradient = ((right_rate - left_rate) * (float)scale) /
            (float)((int32_t)right_position - (int32_t)left_position);
        int32_t grid = (int32_t)((float)left_position / (float)scale);
        const int32_t right_grid =
            (int32_t)((float)right_position / (float)scale);
        for (; grid <= right_grid; ++grid) {
            const int32_t destination = grid - output_start;
            if (destination >= (int32_t)output_count) {
                break;
            }
            if (destination >= 0) {
                output[(size_t)destination] = left_rate +
                    ((float)grid - (float)left_position / (float)scale) *
                    gradient;
            }
        }
        left_index = right_index;
    }
    return true;
}

bool gomore_primitives_sleep_peak_window_update(
    int16_t *peaks, size_t peak_capacity, size_t peak_count,
    uint8_t mode, uint16_t *update_counter,
    float *window, size_t window_count) {
    if (peaks == NULL || update_counter == NULL || window == NULL ||
            peak_count > peak_capacity || window_count < 90u) {
        return false;
    }
    for (size_t index = 0u; index + 1u < peak_count; ++index) {
        const uint16_t current =
            (uint16_t)peaks[index] & UINT16_C(0x7FFF);
        const uint16_t next =
            (uint16_t)peaks[index + 1u] & UINT16_C(0x7FFF);
        const int32_t spacing = (int32_t)next - (int32_t)current;
        if (spacing < 10 || spacing > 37) {
            peaks[index] = (int16_t)(
                (uint16_t)peaks[index] | UINT16_C(0x8000));
        }
    }

    bool generate = mode < 100u;
    if (!generate) {
        if (mode == 101u) {
            generate = (uint16_t)(*update_counter % 9u) < 3u;
        } else if (mode == 102u) {
            generate = (uint16_t)(*update_counter % 12u) < 3u;
        } else {
            generate = (uint16_t)(*update_counter % 6u) < 3u;
        }
    }
    if (generate) {
        if (!gomore_primitives_sleep_peak_rate_interpolate(
                peaks, peak_count, 25, 2, window + 60u, 30u)) {
            return false;
        }
        for (size_t index = 60u; index < 90u; ++index) {
            window[index] = (window[index] - 60.0f) *
                bits_float(UINT32_C(0x3E4CCCCD));
        }
    } else {
        float first_third[30];
        for (size_t index = 0u; index < 30u; ++index) {
            first_third[index] = window[index];
        }
        for (size_t index = 0u; index < 60u; ++index) {
            window[index] = window[index + 30u];
        }
        for (size_t index = 0u; index < 30u; ++index) {
            window[index + 60u] = first_third[index];
        }
    }
    *update_counter = (uint16_t)(*update_counter + 1u);
    return true;
}

bool gomore_primitives_sleep_peak_tail_rebase(
    int16_t *peaks, size_t peak_capacity, size_t *peak_count) {
    if (peaks == NULL || peak_count == NULL || *peak_count > peak_capacity) {
        return false;
    }
    size_t retained = 0u;
    size_t index = *peak_count;
    while (index > 0u) {
        const uint16_t position =
            (uint16_t)peaks[index - 1u] & UINT16_C(0x7FFF);
        if (position <= UINT16_C(749)) {
            break;
        }
        ++retained;
        --index;
    }
    for (size_t destination = 0u; destination < retained; ++destination) {
        peaks[destination] = peaks[index + destination];
    }
    *peak_count = retained;
    for (size_t item = 0u; item < retained; ++item) {
        const uint16_t encoded = (uint16_t)peaks[item];
        const uint16_t rebased = (uint16_t)(
            (encoded & UINT16_C(0x7FFF)) - UINT16_C(750));
        peaks[item] = (int16_t)(
            rebased | (encoded & UINT16_C(0x8000)));
    }
    return true;
}

bool gomore_primitives_sleep_valley_candidates(
    const float *values, size_t value_count,
    uint8_t candidates[12], size_t *candidate_count) {
    if (values == NULL || candidates == NULL || candidate_count == NULL ||
            value_count > 256u || *candidate_count > 12u) {
        return false;
    }
    for (size_t index = 0u; index < 12u; ++index) {
        candidates[index] = 0u;
    }
    if (value_count < 3u) {
        return true;
    }
    for (size_t index = 1u; index + 1u < value_count; ++index) {
        const float center = values[index];
        const float left = values[(index - 1u) & 0xFFu];
        const float right = values[(index + 1u) & 0xFFu];
        if (center <= left && center < right &&
                (right - center * 2.0f) + left > 0.0f &&
                *candidate_count < 12u) {
            candidates[*candidate_count] = (uint8_t)index;
            ++*candidate_count;
        }
    }
    return true;
}

float gomore_primitives_sleep_quantized_magnitude10(
    const float values[10], gomore_primitives_float_unary_fn floor_value) {
    if (values == NULL || floor_value == NULL) {
        return 0.0f;
    }
    const float upper = bits_float(UINT32_C(0x400851EC));
    const float scale = bits_float(UINT32_C(0x4273E706));
    const int32_t upper_bits = INT32_C(0x400851EC);
    const int32_t lower_bits = INT32_C(0x3D8B4396);
    float total = 0.0f;
    for (size_t index = 0u; index < 10u; ++index) {
        float magnitude = values[index];
        if (magnitude < 0.0f) {
            magnitude = -magnitude;
        }
        const int32_t encoded = (int32_t)float_bits(magnitude);
        if (encoded > upper_bits) {
            magnitude = upper;
        } else if (encoded < lower_bits) {
            magnitude = 0.0f;
        }
        const float quantized = floor_value(magnitude * scale);
        if (quantized >= 0.0f) {
            total += quantized;
        }
    }
    return total;
}

bool gomore_primitives_range_center_span(
    const float *values, size_t count, uint8_t mode,
    float *center, float *span) {
    if (values == NULL || count == 0u || mode > 1u ||
            center == NULL || span == NULL) {
        return false;
    }
    float minimum = values[0];
    float maximum = values[0];
    for (size_t index = 0u; index < count; ++index) {
        const float value = values[index];
        if (value < minimum) {
            minimum = value;
        } else if (value > maximum) {
            maximum = value;
        }
    }
    if (mode == 0u) {
        *center = minimum;
        *span = maximum - minimum;
    } else {
        *center = (minimum + maximum) * 0.5f;
        *span = (maximum - minimum) * 0.5f;
    }
    return true;
}

float gomore_primitives_linear_model3_evaluate(
    const float values[3], const gomore_primitives_linear_model3 *model) {
    if (values == NULL || model == NULL) {
        return 0.0f;
    }
    float result = 0.0f;
    for (size_t index = 0u; index < 3u; ++index) {
        result += ((values[index] - model->centers[index]) /
                   model->divisors[index]) * model->weights[index];
    }
    return model->bias + result;
}

bool gomore_primitives_sleep_repair_deep_awake_transition(
    uint8_t *stages, size_t count) {
    if (stages == NULL && count != 0u) {
        return false;
    }
    for (size_t index = 0u; index + 1u < count; ++index) {
        size_t run = 0u;
        if (stages[index] == 3u && stages[index + 1u] == 0u) {
            size_t cursor = index + 1u;
            while (cursor > 0u && stages[cursor - 1u] == 3u) {
                ++run;
                --cursor;
            }
        } else if (stages[index] == 0u && stages[index + 1u] == 3u) {
            size_t cursor = index + 1u;
            while (cursor < count && stages[cursor] == 3u) {
                ++run;
                ++cursor;
            }
        }
        size_t rewrite = run < 6u ? run : 6u;
        if (rewrite > index + 1u) {
            rewrite = index + 1u;
        }
        for (size_t offset = 0u; offset < rewrite; ++offset) {
            stages[index - offset] = 2u;
        }
    }
    return true;
}

static bool sleep_refine_statistics(
    const int8_t *stages, size_t count, uint32_t duration_seconds,
    float interval[7], float stage[12]) {
    return gomore_primitives_sleep_interval_statistics(
               (const uint8_t *)stages, count, 0u, duration_seconds,
               false, interval) &&
           gomore_primitives_sleep_stage_statistics(
               (const uint8_t *)stages, count, 0u, duration_seconds,
               false, stage);
}

bool gomore_primitives_sleep_stage_refine(
    const uint8_t configuration[11], int8_t *stages,
    size_t stage_capacity, size_t *stage_count,
    uint32_t duration_seconds) {
    if (configuration == NULL || stages == NULL || stage_count == NULL ||
            *stage_count == 0u || *stage_count > stage_capacity ||
            *stage_count > 2880u || duration_seconds / 30u > *stage_count) {
        return false;
    }
    const size_t count = *stage_count;
    for (size_t index = 0u; index < count; ++index) {
        if (stages[index] < 0 || stages[index] > 3) {
            return false;
        }
    }

    const size_t radius = configuration[2];
    if (radius >= 1u && radius <= 29u) {
        int8_t votes[58];
        size_t buffered = 0u;
        for (size_t index = 0u; index < count; ++index) {
            uint32_t frequencies[4] = {0u, 0u, 0u, 0u};
            const size_t begin = index > radius ? index - radius : 0u;
            const size_t end = index + radius + 1u < count
                ? index + radius + 1u : count;
            for (size_t cursor = begin; cursor < end; ++cursor) {
                ++frequencies[(uint8_t)stages[cursor]];
            }
            int8_t selected = 0;
            uint32_t maximum = 0u;
            if (frequencies[0] < 3u) {
                for (int32_t stage = 3; stage >= 0; --stage) {
                    if (maximum < frequencies[(uint32_t)stage]) {
                        maximum = frequencies[(uint32_t)stage];
                        selected = (int8_t)stage;
                    }
                }
            }
            if (index > radius && index % radius == 0u) {
                const size_t destination = index - radius * 2u;
                for (size_t offset = 0u; offset < radius; ++offset) {
                    stages[destination + offset] = votes[offset];
                    votes[offset] = votes[radius + offset];
                }
                buffered = radius;
            }
            votes[buffered++] = selected;
        }
        const size_t destination = count - buffered;
        for (size_t index = 0u; index < buffered; ++index) {
            stages[destination + index] = votes[index];
        }
    }

    if (!gomore_primitives_smooth_target_run_edges(
            0, stages, count, true) ||
            !gomore_primitives_smooth_target_run_edges(
                1, stages, count, false) ||
            !gomore_primitives_sleep_repair_deep_awake_transition(
                (uint8_t *)stages, count)) {
        return false;
    }

    float interval[7];
    float stage[12];
    if (!sleep_refine_statistics(
            stages, count, duration_seconds, interval, stage)) {
        return false;
    }
    const float efficiency = interval[6];
    const float deep_fraction = efficiency == 0.0f
        ? 0.0f : stage[3] / efficiency;
    const float rem_fraction = efficiency == 0.0f
        ? 0.0f : stage[1] / efficiency;
    int32_t deep_adjustment = (int32_t)(
        (deep_fraction + (0.18f - deep_fraction) * 0.5f) *
        efficiency * (float)count - stage[11] * 2.0f);
    int32_t rem_adjustment = (int32_t)(
        (rem_fraction + (0.225f - rem_fraction) * 0.5f) *
        efficiency * (float)count - stage[9] * 2.0f);

    for (size_t attempt = 0u; attempt < 10u; ++attempt) {
        if (!gomore_primitives_sleep_stage_proportion_adjust(
                stages, count, 1, rem_adjustment, &rem_adjustment) ||
                !gomore_primitives_sleep_stage_proportion_adjust(
                    stages, count, 3, deep_adjustment, &deep_adjustment) ||
                !sleep_refine_statistics(
                    stages, count, duration_seconds, interval, stage)) {
            return false;
        }
        const float current_efficiency = interval[6];
        const float current_deep = current_efficiency == 0.0f
            ? 0.0f : stage[3] / current_efficiency;
        const float current_rem = current_efficiency == 0.0f
            ? 0.0f : stage[1] / current_efficiency;
        if (deep_adjustment < -6 && current_deep < 0.1f) {
            deep_adjustment = -deep_adjustment;
        }
        if (rem_adjustment < -6 && current_rem < 0.1f) {
            rem_adjustment = -rem_adjustment;
        }
        if (!(current_rem <= 0.1f || current_rem >= 0.25f ||
              current_deep <= 0.1f)) {
            break;
        }
    }

    const size_t chunk = configuration[4];
    if (chunk != 0u) {
        for (size_t begin = 0u; begin < count; begin += chunk) {
            uint32_t frequencies[4] = {0u, 0u, 0u, 0u};
            const size_t end = begin + chunk < count
                ? begin + chunk : count;
            for (size_t index = begin; index < end; ++index) {
                ++frequencies[(uint8_t)stages[index]];
            }
            int8_t selected = 0;
            uint32_t maximum = 0u;
            for (int32_t candidate = 3; candidate >= 0; --candidate) {
                if (maximum < frequencies[(uint32_t)candidate]) {
                    maximum = frequencies[(uint32_t)candidate];
                    selected = (int8_t)candidate;
                }
            }
            for (size_t index = begin; index < end; ++index) {
                stages[index] = selected;
            }
        }
    }

    if (!sleep_refine_statistics(
            stages, count, duration_seconds, interval, stage)) {
        return false;
    }
    float rem_minutes = stage[9];
    float light_minutes = stage[10];
    float deep_minutes = stage[11];
    for (size_t cursor = count;
         cursor > 0u && deep_minutes + light_minutes + rem_minutes > 0.0f &&
         deep_minutes / (deep_minutes + light_minutes + rem_minutes) >= 0.35f;
         --cursor) {
        if (stages[cursor - 1u] == 3) {
            stages[cursor - 1u] = 2;
            deep_minutes -= 0.5f;
            light_minutes += 0.5f;
        }
    }
    for (size_t cursor = 0u;
         cursor < count && deep_minutes + light_minutes + rem_minutes > 0.0f &&
         rem_minutes / (deep_minutes + light_minutes + rem_minutes) > 0.25f;
         ++cursor) {
        if (stages[cursor] == 1) {
            stages[cursor] = 2;
            rem_minutes -= 0.5f;
            light_minutes += 0.5f;
        }
    }
    if ((configuration[3] & 1u) != 0u) {
        stages[count - 1u] = 0;
    }
    return true;
}

bool gomore_primitives_sleep_optical_history_advance(
    gomore_primitives_sleep_optical_history *state,
    uint32_t elapsed_blocks,
    gomore_primitives_filter_init_fn initialize) {
    if (state == NULL || initialize == NULL || state->position_count > 12u) {
        return false;
    }
    if (elapsed_blocks > 2u) {
        return gomore_primitives_filter_state_initialize(
            state, sizeof(*state), initialize);
    }
    for (uint32_t block = 0u; block < elapsed_blocks; ++block) {
        for (size_t index = 0u; index < 50u; ++index) {
            state->window[index] = state->window[index + 25u];
        }
        size_t removed = 0u;
        for (size_t index = 0u; index < state->position_count; ++index) {
            if (state->positions[index] < 25u) {
                ++removed;
            } else {
                state->positions[index] =
                    (uint8_t)(state->positions[index] - 25u);
            }
        }
        if (removed == state->position_count) {
            state->position_count = 0u;
        } else {
            const size_t retained = (size_t)state->position_count - removed;
            for (size_t index = 0u; index < retained; ++index) {
                state->positions[index] = state->positions[index + removed];
            }
            state->position_count = (uint8_t)retained;
        }
    }
    return true;
}

bool gomore_primitives_sleep_optical_peak_update(
    gomore_primitives_sleep_optical_history *state,
    uint32_t elapsed_blocks,
    const gomore_primitives_sleep_optical_input *input,
    uint8_t record[17],
    gomore_primitives_filter_init_fn initialize,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (state == NULL || input == NULL || record == NULL ||
            state->position_count > 12u ||
            (!input->invalid && (input->samples == NULL ||
                                 resample == NULL || apply_filter == NULL))) {
        return false;
    }
    clear_bytes(record, 17u);

    uint8_t candidates[12];
    uint8_t positions[12];
    clear_bytes(candidates, sizeof(candidates));
    clear_bytes(positions, sizeof(positions));
    size_t candidate_count = 0u;
    size_t position_count = 0u;

    if (!gomore_primitives_sleep_optical_history_advance(
            state, elapsed_blocks, initialize) ||
            !gomore_primitives_prepare_filter_input(
                state, sizeof(*state), input->samples, input->invalid, 25,
                resample, apply_filter) ||
            !gomore_primitives_sleep_valley_candidates(
                state->window, 75u, candidates, &candidate_count) ||
            !gomore_primitives_interval_nonzero_argmax(
                state->window, 75u, candidates, candidate_count,
                positions, sizeof(positions), &position_count) ||
            !gomore_primitives_trim_below_reference_tail(
                state->positions, state->position_count,
                positions, sizeof(positions), &position_count) ||
            !gomore_primitives_encode_short_record(
                record, positions, position_count)) {
        return false;
    }

    for (size_t index = 0u; index < 12u; ++index) {
        state->positions[index] = positions[index];
    }
    state->position_count = (uint8_t)position_count;
    return true;
}

bool gomore_primitives_state_word_24(const void *state, size_t length,
                                     uint32_t *value) {
    if (state == NULL || length < 0x1Cu || value == NULL) {
        return false;
    }
    *value = load_u32_le((const uint8_t *)state + 0x18u);
    return true;
}

bool gomore_primitives_split_signed_root(
    float value, float output[2],
    gomore_primitives_float_binary_fn power) {
    if (output == NULL || power == NULL) {
        return false;
    }
    if (value < 0.0f) {
        output[0] = 0.0f;
        output[1] = power(-value, 0.5f);
    } else {
        output[0] = power(value, 0.5f);
        output[1] = 0.0f;
    }
    return true;
}

float gomore_primitives_clamped_rational(float value, float state) {
    const float absolute = value < 0.0f ? -value : value;
    const float adjusted = bits_float(UINT32_C(0x3F0A2728)) +
        (absolute - 2.5f) * bits_float(UINT32_C(0x3E20FBA9));
    float result = (value /
        (state * adjusted * bits_float(UINT32_C(0x42C80000)))) *
        bits_float(UINT32_C(0x42700000));
    if ((int32_t)float_bits(result) > INT32_C(0x435C0000)) {
        result = bits_float(UINT32_C(0x435C0000));
    }
    return result;
}

bool gomore_primitives_table_record11(const uint8_t *table,
                                      size_t table_length, int32_t index,
                                      uint8_t output[11]) {
    if (table == NULL || output == NULL || index < 0) {
        return false;
    }
    const size_t offset = index < 100
        ? (size_t)index * 11u
        : (size_t)(index - 100) * 11u + 44u;
    if (offset > table_length || table_length - offset < 11u) {
        return false;
    }
    for (size_t byte = 0u; byte < 11u; ++byte) {
        output[byte] = table[offset + byte];
    }
    return true;
}

int32_t gomore_primitives_status_or_random(
    uint8_t *state, size_t state_length,
    const void *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (state == NULL || state_length < 0x14u || status_record == NULL ||
            status_length < 12u) {
        return -1;
    }
    const uint8_t *status = status_record;
    for (size_t index = 0u; index < 4u; ++index) {
        const int16_t code = (int16_t)load_u16_le_early(
            &status[4u + index * 2u]);
        if (code < 0) {
            return code;
        }
    }
    if (state[0x10u] != 4u) {
        return 0;
    }
    if (prepare == NULL || random_value == NULL) {
        return -1;
    }
    store_u32_le(state, load_u32_le(status));
    prepare();
    return (int16_t)(random_value() % 100 + 23);
}

static void identifier_status_commit(
    uint8_t *state, size_t state_length,
    uint8_t *status, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value,
    bool set_error, bool clear_state_word) {
    if (set_error) {
        store_u16_le_early(&status[4], (uint16_t)(int16_t)-1004);
    }
    const int32_t result = gomore_primitives_status_or_random(
        state, state_length, status, status_length, prepare, random_value);
    store_u16_le_early(&state[4], (uint16_t)result);
    if (clear_state_word) {
        store_u32_le(&state[8], 0u);
    }
}

int32_t gomore_primitives_validate_identifier_status(
    const uint8_t *identifier, const uint8_t classes[256],
    uint8_t *state, size_t state_length,
    uint8_t *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (classes == NULL || state == NULL || state_length < 0x14u ||
            status_record == NULL || status_length < 12u) {
        return -1;
    }
    static const uint8_t template_identifier[] = "1726247936995224";
    static const uint8_t special_identifier0[] = "1839052049009318";
    static const uint8_t special_identifier1[] = "1839052049073388";
    ++state[0x10u];
    const size_t length = gomore_primitives_nullable_strlen(
        (const char *)identifier);
    if (gomore_primitives_all_class_0x20(
            identifier, length, classes) != 0) {
        identifier_status_commit(
            state, state_length, status_record, status_length,
            prepare, random_value, true, true);
        return -1004;
    }
    const bool special =
        gomore_primitives_nullable_compare(
            identifier, special_identifier0) == 0 ||
        gomore_primitives_nullable_compare(
            identifier, special_identifier1) == 0;
    if (!special) {
        identifier_status_commit(
            state, state_length, status_record, status_length,
            prepare, random_value, true, true);
        return -1004;
    }
    if (gomore_primitives_nullable_compare(
            template_identifier, identifier) == 0) {
        identifier_status_commit(
            state, state_length, status_record, status_length,
            prepare, random_value, false, false);
        return 0;
    }
    identifier_status_commit(
        state, state_length, status_record, status_length,
        prepare, random_value, true, true);
    return -1020;
}

bool gomore_primitives_mode_state_configure(
    void *record, size_t length, uint32_t mode, uint32_t count,
    const float parameters[2],
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2) {
    if (record == NULL || length < 0x50u || parameters == NULL ||
            (mode < 2u && initialize_lt2 == NULL) ||
            (mode == 2u && initialize_mode2 == NULL)) {
        return false;
    }
    uint8_t *bytes = record;
    if (mode < 2u) {
        initialize_lt2(record, mode, count, parameters[0]);
        store_u32_le(bytes, count);
    } else if (mode == 2u) {
        initialize_mode2(record, count, parameters);
        store_u32_le(bytes, count << 1u);
    }
    clear_bytes(&bytes[0x30u], 16u);
    clear_bytes(&bytes[0x40u], 16u);
    return true;
}

bool gomore_primitives_iir_low_high_coefficients(
    gomore_primitives_iir_coefficients *record,
    uint32_t mode, uint32_t order, float normalized_cutoff,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_binary_fn power) {
    _Static_assert(sizeof(gomore_primitives_iir_coefficients) == 0x30u,
                   "IIR coefficient record must match recovered extent");
    if (record == NULL || mode > 1u || order == 0u || order > 4u ||
            !(normalized_cutoff > 0.0f && normalized_cutoff < 1.0f) ||
            cosine == NULL || sine == NULL || power == NULL) {
        return false;
    }

    const float pi = bits_float(UINT32_C(0x40490FDB));
    const float angle = normalized_cutoff * pi;
    const float angle_cosine = cosine(angle);
    const float angle_sine = sine(angle);
    float root_real[4];
    float root_imaginary[4];
    float gain_denominator = 1.0f;

    for (uint32_t index = 0u; index < order; ++index) {
        const float numerator_angle = (float)(index * 2u + 1u) * pi;
        const float pole_angle = numerator_angle / (float)(order * 2u);
        const float pole_cosine = cosine(pole_angle);
        const float pole_sine = sine(pole_angle);
        const float denominator = angle_sine * pole_sine + 1.0f;
        if (index < order / 2u) {
            gain_denominator *= denominator;
        }
        root_real[index] = -angle_cosine / denominator;
        root_imaginary[index] =
            (-angle_sine * pole_cosine) / denominator;
    }

    float polynomial_real[4] = {root_real[0], 0.0f, 0.0f, 0.0f};
    float polynomial_imaginary[4] = {
        root_imaginary[0], 0.0f, 0.0f, 0.0f};
    for (uint32_t index = 1u; index < order; ++index) {
        for (uint32_t cursor = index; cursor > 0u; --cursor) {
            polynomial_real[cursor] +=
                polynomial_real[cursor - 1u] * root_real[index] -
                polynomial_imaginary[cursor - 1u] *
                    root_imaginary[index];
            polynomial_imaginary[cursor] +=
                polynomial_real[cursor - 1u] * root_imaginary[index] +
                polynomial_imaginary[cursor - 1u] * root_real[index];
        }
        polynomial_real[0] += root_real[index];
        polynomial_imaginary[0] += root_imaginary[index];
    }

    record->reserved = 0.0f;
    record->feedback[0] = 1.0f;
    for (uint32_t index = 1u; index <= order; ++index) {
        record->feedback[index] = polynomial_real[index - 1u];
    }

    const float half_angle = angle * 0.5f;
    const float half_cosine = cosine(half_angle);
    const float half_sine = sine(half_angle);
    if ((order & 1u) != 0u) {
        gain_denominator *= half_cosine + half_sine;
    }
    const float gain_base = mode == 0u ? half_sine : half_cosine;
    record->feedforward[0] =
        power(gain_base, (float)order) / gain_denominator;
    record->feedforward[1] = record->feedforward[0];
    for (uint32_t index = 1u; index < order; ++index) {
        record->feedforward[index + 1u] = 0.0f;
        for (uint32_t cursor = index + 1u; cursor > 0u; --cursor) {
            record->feedforward[cursor] +=
                record->feedforward[cursor - 1u];
        }
    }
    if (mode != 0u) {
        for (uint32_t index = 1u; index <= order; index += 2u) {
            record->feedforward[index] = -record->feedforward[index];
        }
    }
    return true;
}

bool gomore_primitives_iir_bandpass_coefficients(
    gomore_primitives_iir_coefficients *record,
    uint32_t order, const float normalized_cutoffs[2],
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_unary_fn tangent) {
    if (record == NULL || order == 0u || order > 2u ||
            normalized_cutoffs == NULL ||
            !(normalized_cutoffs[0] > 0.0f &&
              normalized_cutoffs[0] < normalized_cutoffs[1] &&
              normalized_cutoffs[1] < 1.0f) ||
            cosine == NULL || sine == NULL || tangent == NULL) {
        return false;
    }

    const float pi = bits_float(UINT32_C(0x40490FDB));
    const float half_width =
        (normalized_cutoffs[1] - normalized_cutoffs[0]) * pi * 0.5f;
    const float center_cosine = cosine(
        (normalized_cutoffs[0] + normalized_cutoffs[1]) * pi * 0.5f);
    const float width_cosine = cosine(half_width);
    const float width_sine = sine(half_width);
    const float full_width_cosine = cosine(
        (normalized_cutoffs[1] - normalized_cutoffs[0]) * pi);
    const float full_width_sine = sine(
        (normalized_cutoffs[1] - normalized_cutoffs[0]) * pi);
    const float reciprocal_tangent = 1.0f / tangent(half_width);

    float root_imaginary_first[2];
    float root_real_first[2];
    float root_imaginary_second[2];
    float root_real_second[2];
    float gain_accumulator = 0.0f;
    float gain_denominator = 1.0f;
    for (uint32_t index = 0u; index < order; ++index) {
        const float pole_angle =
            ((float)(index * 2u + 1u) * pi) / (float)(order * 2u);
        const float pole_cosine = cosine(pole_angle);
        const float pole_sine = sine(pole_angle);
        const float gain_term = pole_sine + reciprocal_tangent;
        const float previous_scaled_cosine = gain_accumulator * pole_cosine;
        gain_accumulator =
            ((gain_denominator + gain_accumulator) *
                 ((reciprocal_tangent + pole_sine) - pole_cosine) -
             gain_denominator * gain_term) +
            gain_accumulator * pole_cosine;
        const float denominator = full_width_sine * pole_sine + 1.0f;
        root_real_second[index] = full_width_cosine / denominator;
        root_imaginary_second[index] =
            (full_width_sine * pole_cosine) / denominator;
        root_real_first[index] =
            (center_cosine * -2.0f *
             (width_cosine + width_sine * pole_sine)) /
            denominator;
        root_imaginary_first[index] =
            (center_cosine * -2.0f * width_sine * pole_cosine) /
            denominator;
        gain_denominator =
            gain_term * gain_denominator + previous_scaled_cosine;
    }

    float polynomial_imaginary[4] = {
        root_imaginary_first[0], root_imaginary_second[0], 0.0f, 0.0f};
    float polynomial_real[4] = {
        root_real_first[0], root_real_second[0], 0.0f, 0.0f};
    for (uint32_t index = 1u; index < order; ++index) {
        const float imaginary_first = root_imaginary_first[index];
        const float real_first = root_real_first[index];
        const float imaginary_second = root_imaginary_second[index];
        const float real_second = root_real_second[index];
        for (uint32_t cursor = index; cursor > 0u; --cursor) {
            const size_t position = (size_t)cursor * 2u;
            polynomial_real[position + 1u] +=
                polynomial_real[position - 1u] * real_second +
                polynomial_real[position] * real_first -
                polynomial_imaginary[position - 1u] * imaginary_second -
                polynomial_imaginary[position] * imaginary_first;
            polynomial_imaginary[position + 1u] +=
                polynomial_real[position - 1u] * imaginary_second +
                polynomial_imaginary[position] * real_first +
                polynomial_imaginary[position - 1u] * real_second +
                polynomial_real[position] * imaginary_first;
            polynomial_real[position] +=
                polynomial_real[position - 2u] * real_second +
                polynomial_real[position - 1u] * real_first -
                polynomial_imaginary[position - 2u] * imaginary_second -
                polynomial_imaginary[position - 1u] * imaginary_first;
            polynomial_imaginary[position] +=
                polynomial_real[position - 2u] * imaginary_second +
                polynomial_real[position - 1u] * imaginary_first +
                polynomial_imaginary[position - 2u] * real_second +
                polynomial_imaginary[position - 1u] * real_first;
        }
        polynomial_real[1] +=
            real_second + polynomial_real[0] * real_first -
            polynomial_imaginary[0] * imaginary_first;
        polynomial_imaginary[1] +=
            imaginary_second + polynomial_real[0] * imaginary_first +
            polynomial_imaginary[0] * real_first;
        polynomial_real[0] += real_first;
        polynomial_imaginary[0] += imaginary_first;
    }

    record->reserved = 0.0f;
    record->feedback[0] = 1.0f;
    for (uint32_t index = 1u; index <= order * 2u; ++index) {
        record->feedback[index] = polynomial_real[index - 1u];
    }
    record->feedforward[0] = 1.0f / gain_denominator;
    record->feedforward[1] = 0.0f;
    record->feedforward[2] = record->feedforward[0];
    for (uint32_t index = 1u; index < order; ++index) {
        record->feedforward[index * 2u + 1u] = 0.0f;
        record->feedforward[index * 2u + 2u] = 0.0f;
        for (uint32_t cursor = index + 1u; cursor > 0u; --cursor) {
            record->feedforward[cursor * 2u] +=
                record->feedforward[(cursor - 1u) * 2u];
        }
    }
    for (uint32_t index = 2u; index < order * 2u + 1u; index += 4u) {
        record->feedforward[index] = -record->feedforward[index];
    }
    return true;
}

bool gomore_primitives_large_filter_state_initialize(
    void *record, size_t length,
    gomore_primitives_mode2_init_fn initialize_mode2) {
    if (record == NULL || length < 0x6C8u || initialize_mode2 == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x6C8u);
    store_u32_le(&bytes[0x6C0u], UINT32_C(0xBF800000));
    store_u32_le(&bytes[0x6C4u], UINT32_C(0xBF800000));
    for (size_t index = 0u; index < 250u; ++index) {
        store_u32_le(&bytes[0x2D8u + index * 4u], 0u);
    }
    const float parameters[2] = {
        bits_float(UINT32_C(0x3D23D70A)),
        bits_float(UINT32_C(0x3EA3D70A))
    };
    return gomore_primitives_mode_state_configure(
        record, length, 2u, 2u, parameters, NULL, initialize_mode2);
}

bool gomore_primitives_engine_state_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_large_init_fn initialize) {
    if (record == NULL || length < 0x3894u || initialize == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x3894u);
    store_u32_le(&bytes[0x3890u], binding);
    initialize(record);
    return true;
}

void gomore_primitives_linear_resample(
    const float *source, int32_t input_count, int32_t output_count,
    int32_t source_total, float *destination) {
    if (source == NULL || destination == NULL || input_count < 0 ||
            output_count < 0 || source_total < 0) {
        return;
    }
    if (input_count == output_count) {
        for (int32_t index = 0; index < source_total; ++index) {
            destination[index] = source[index];
        }
        return;
    }

    const int32_t blocks = input_count == 0
        ? 0 : source_total / input_count;
    if (output_count != 0 && blocks > INT32_MAX / output_count) {
        return;
    }
    const int32_t produced = output_count * blocks;
    const float ratio = output_count == 0
        ? 0.0f : (float)input_count / (float)output_count;
    for (int32_t index = 0; index < produced; ++index) {
        const float position = ratio * (float)index;
        const int32_t left = (int32_t)position;
        int32_t right = left + 1;
        if (right >= source_total) {
            right = source_total - 1;
        }
        const float left_value = source[left];
        destination[index] = left_value +
            (source[right] - left_value) * (position - (float)left);
    }
}

static bool resample25_and_filter_common(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (filter_state == NULL || source == NULL || destination == NULL ||
            resample == NULL || apply_filter == NULL) {
        return false;
    }
    resample(source, input_count, 25, source_total, destination);
    apply_filter(filter_state, destination, 25u);
    return true;
}

int32_t gomore_primitives_resample25_and_filter(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    return resample25_and_filter_common(
        filter_state, source, input_count, source_total, destination,
        resample, apply_filter) ? 0 : -1;
}

void gomore_primitives_resample25_and_filter_tail(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    (void)resample25_and_filter_common(
        filter_state, source, input_count, source_total, destination,
        resample, apply_filter);
}

bool gomore_primitives_prepare_filter_input(
    void *filter_state, size_t filter_length,
    const float *source, bool clear_only, int32_t source_total,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (filter_state == NULL || filter_length < 0x17Cu) {
        return false;
    }
    float *destination = (float *)((uint8_t *)filter_state + 0x118u);
    if (clear_only) {
        clear_bytes((uint8_t *)destination, 100u);
        return true;
    }
    return resample25_and_filter_common(
        filter_state, source, 25, source_total, destination,
        resample, apply_filter);
}

bool gomore_primitives_commit_valid_time_record(
    void *context, size_t context_length,
    void *destination, size_t destination_length,
    const void *record, size_t record_length) {
    if (context == NULL || context_length < 0x13Cu || destination == NULL ||
            destination_length < 10u || record == NULL || record_length < 8u ||
            !gomore_primitives_time_record_valid(record, record_length)) {
        return false;
    }
    uint8_t *context_bytes = context;
    uint8_t *destination_bytes = destination;
    const uint8_t *record_bytes = record;
    for (size_t index = 0u; index < 8u; ++index) {
        destination_bytes[2u + index] = record_bytes[index];
    }
    if (context_bytes[0xB8u] == 0u && context_bytes[0xB4u] == 0u) {
        for (size_t index = 0u; index < 8u; ++index) {
            context_bytes[0x130u + index] = record_bytes[index];
        }
    }
    return true;
}

bool gomore_primitives_signed_power_third(
    float values[2], gomore_primitives_float_binary_fn power) {
    if (values == NULL || power == NULL) {
        return false;
    }
    const float input = values[0];
    const float magnitude = power(input <= 0.0f ? -input : input,
                                  bits_float(UINT32_C(0x3EAAAAAB)));
    values[0] = input <= 0.0f ? -magnitude : magnitude;
    values[1] = 0.0f;
    return true;
}

bool gomore_primitives_trim_below_reference_tail(
    const uint8_t *reference, size_t reference_count,
    uint8_t *values, size_t capacity, size_t *value_count) {
    if (reference == NULL || values == NULL || value_count == NULL ||
            *value_count > capacity) {
        return false;
    }
    size_t remove = 0u;
    if (reference_count > 0u) {
        const uint8_t threshold = reference[reference_count - 1u];
        for (size_t index = 0u; index < *value_count; ++index) {
            if (values[index] <= threshold) {
                ++remove;
            }
        }
    }
    if (remove == *value_count) {
        *value_count = 0u;
        return true;
    }
    for (size_t index = remove; index < *value_count; ++index) {
        values[index - remove] = values[index];
    }
    *value_count -= remove;
    return true;
}

bool gomore_primitives_selector_transition(const void *record,
                                           size_t length,
                                           int8_t *selector) {
    if (record == NULL || length < 0x3Eu || selector == NULL) {
        return false;
    }
    const uint8_t *bytes = record;
    if (bits_float(load_u32_le(&bytes[0x20u])) > 0.0f &&
            (int8_t)bytes[0x39u] > 0 && *selector == -1) {
        *selector = 1;
    }
    if ((*selector == 1 || *selector == 2) &&
            (bits_float(load_u32_le(&bytes[0x28u])) < 0.0f ||
             (int8_t)bytes[0x3Du] < 0)) {
        *selector = -1;
    }
    return true;
}

bool gomore_primitives_fill_packed_time_gap(void *record, size_t length,
                                            uint32_t now) {
    if (record == NULL || length < 0x2D5u) {
        return false;
    }
    uint8_t *bytes = record;
    const uint32_t previous = load_u32_le(&bytes[0x2D0u]);
    const uint32_t elapsed = now - previous;
    if (elapsed >= UINT32_C(86400)) {
        clear_bytes(bytes, 0x2D0u);
        return true;
    }
    if (elapsed > 1u) {
        uint32_t slot = previous / UINT32_C(30) + 1u;
        const uint32_t end = now / UINT32_C(30);
        while (slot < end) {
            if (!gomore_primitives_packed_2bit_set(
                    bytes, 0x2D0u, slot, bytes[0x2D4u])) {
                return false;
            }
            ++slot;
        }
    }
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

bool gomore_primitives_iir_filter_apply(void *state, size_t state_length,
                                       float *values, size_t count) {
    if (state == NULL || (values == NULL && count != 0u) ||
            state_length < 0x44u) {
        return false;
    }
    uint8_t *bytes = state;
    const int32_t order = (int32_t)load_u32_le(bytes);
    const size_t required_length = order > 0
        ? 0x40u + (size_t)order * 4u : 0x44u;
    if (order < 0 || order > 11 || state_length < required_length) {
        return false;
    }
    for (size_t sample = 0u; sample < count; ++sample) {
        float output = bits_float(load_u32_le(&bytes[0x1Cu])) * values[sample];
        for (int32_t index = 1; index <= order; ++index) {
            const size_t input_history = 0x30u + (size_t)(index - 1) * 4u;
            const size_t input_coefficient = 0x1Cu + (size_t)index * 4u;
            const size_t output_history = 0x40u + (size_t)(index - 1) * 4u;
            const size_t output_coefficient = 8u + (size_t)index * 4u;
            output += bits_float(load_u32_le(&bytes[input_history])) *
                      bits_float(load_u32_le(&bytes[input_coefficient]));
            output -= bits_float(load_u32_le(&bytes[output_history])) *
                      bits_float(load_u32_le(&bytes[output_coefficient]));
        }
        for (int32_t index = order - 1; index > 0; --index) {
            store_u32_le(&bytes[0x30u + (size_t)index * 4u],
                         load_u32_le(&bytes[0x30u +
                                            (size_t)(index - 1) * 4u]));
            store_u32_le(&bytes[0x40u + (size_t)index * 4u],
                         load_u32_le(&bytes[0x40u +
                                            (size_t)(index - 1) * 4u]));
        }
        store_u32_le(&bytes[0x30u], float_bits(values[sample]));
        store_u32_le(&bytes[0x40u], float_bits(output));
        values[sample] = output;
    }
    store_u32_le(&bytes[4], 1u);
    return true;
}

int32_t gomore_primitives_integer_iir4_update(
    int32_t input, int32_t input_history[4],
    int32_t output_history[4], int32_t profile) {
    if (input_history == NULL || output_history == NULL) {
        return 0;
    }
    static const int32_t feedback[2][5] = {
        {1000, -2595, 2746, -1459, 347},
        {1000, -3722, 5276, -3374, 822},
    };
    static const int32_t feedforward[2][5] = {
        {9131, 0, -18262, 0, 9131},
        {434, 0, -869, 0, 434},
    };
    const size_t selected = profile == 1 ? 1u : 0u;
    uint32_t accumulated =
        (uint32_t)feedforward[selected][0] * (uint32_t)input;
    for (size_t index = 0u; index < 4u; ++index) {
        accumulated += (uint32_t)input_history[index] *
            (uint32_t)feedforward[selected][index + 1u];
        accumulated -= (uint32_t)output_history[index] *
            (uint32_t)feedback[selected][index + 1u];
    }
    for (size_t index = 3u; index > 0u; --index) {
        input_history[index] = input_history[index - 1u];
        output_history[index] = output_history[index - 1u];
    }
    input_history[0] = input;
    const int64_t signed_accumulated = accumulated <= (uint32_t)INT32_MAX
        ? (int64_t)accumulated
        : (int64_t)accumulated - INT64_C(4294967296);
    output_history[0] = (int32_t)(signed_accumulated / INT64_C(1000));
    return output_history[0];
}

int32_t gomore_primitives_thresholded_mean5(
    float threshold, const float values[5], const float comparisons[5],
    float *mean) {
    if (values == NULL || comparisons == NULL || mean == NULL) {
        return -1;
    }
    float sum = 0.0f;
    int32_t included = 0;
    for (size_t index = 0u; index < 5u; ++index) {
        if (comparisons[index] >= threshold) {
            sum += values[index];
            ++included;
        }
    }
    *mean = sum / (float)included;
    return included;
}

float gomore_primitives_magnitude_score10(float threshold,
                                         const float values[10]) {
    if (values == NULL) {
        return 0.0f;
    }
    float score = 0.0f;
    const float limit = bits_float(UINT32_C(0x400851EC));
    const float factor = bits_float(UINT32_C(0x4273E706));
    for (size_t index = 0u; index < 10u; ++index) {
        float magnitude = values[index] < 0.0f ? -values[index] : values[index];
        if ((int32_t)float_bits(magnitude) > INT32_C(0x400851EC)) {
            magnitude = limit;
        } else if (magnitude < threshold) {
            magnitude = 0.0f;
        }
        const float contribution = magnitude * factor;
        if (contribution >= 0.0f) {
            score += contribution;
        }
    }
    return score;
}

int32_t gomore_primitives_circular_count_predicate(
    const int16_t *values, size_t count, int32_t cursor,
    int32_t lookback, int32_t lower, int32_t upper,
    uint8_t comparison, int32_t required) {
    if (values == NULL || count == 0u || count > 127u || cursor < 0 ||
            cursor >= (int32_t)count || lookback < 0) {
        return -1;
    }
    int32_t matches = 0;
    for (int32_t offset = 1; offset <= lookback; ++offset) {
        int32_t index = cursor - offset;
        if (index < 0) {
            index += (int32_t)count;
        }
        const int32_t value = values[index];
        if (value > lower && value < upper) {
            ++matches;
        }
    }
    if (comparison == UINT8_C(0x3E)) {
        return matches >= required ? 1 : -1;
    }
    if (comparison == UINT8_C(0x3C)) {
        return matches < required ? 1 : -1;
    }
    return -1;
}

bool gomore_primitives_run_length_encode_2bit(
    const int8_t *values, size_t count,
    uint8_t *output, size_t capacity, size_t *written) {
    if (output == NULL || written == NULL ||
            (values == NULL && count != 0u)) {
        return false;
    }
    *written = 0u;
    if (count == 0u) {
        return true;
    }
    int8_t current = values[0];
    uint8_t run_minus_one = UINT8_C(0xFF);
    for (size_t index = 0u; index < count; ++index) {
        ++run_minus_one;
        if (values[index] != current || run_minus_one > UINT8_C(0x3E)) {
            if (*written >= capacity) {
                return false;
            }
            output[(*written)++] = (uint8_t)((uint8_t)current & UINT8_C(3)) |
                (uint8_t)((run_minus_one & UINT8_C(0x3F)) << 2u);
            current = values[index];
            run_minus_one = 0u;
        }
        if (index == count - 1u) {
            if (*written >= capacity) {
                return false;
            }
            output[(*written)++] = (uint8_t)((uint8_t)current & UINT8_C(3)) |
                (uint8_t)(((uint8_t)(run_minus_one + 1u) & UINT8_C(0x3F)) << 2u);
        }
    }
    return true;
}

bool gomore_primitives_final_sleep_record_serialize(
    const gomore_primitives_final_sleep_record *record,
    uint8_t *output, size_t capacity, size_t *written) {
    if (record == NULL || output == NULL || written == NULL ||
            record->stage_count > UINT16_MAX ||
            (record->stages == NULL && record->stage_count != 0u)) {
        return false;
    }

    size_t compact_count = 0u;
    if (record->stage_count != 0u) {
        int8_t current = record->stages[0];
        uint8_t run_minus_one = UINT8_MAX;
        for (size_t index = 0u; index < record->stage_count; ++index) {
            ++run_minus_one;
            if (record->stages[index] != current ||
                    run_minus_one > UINT8_C(0x3E)) {
                ++compact_count;
                current = record->stages[index];
                run_minus_one = 0u;
            }
            if (index == record->stage_count - 1u) {
                ++compact_count;
            }
        }
    }

    const size_t serialized_length =
        GOMORE_PRIMITIVES_FINAL_SLEEP_HEADER_BYTES +
        (record->wire_type == 1u ? compact_count : 0u);
    if (capacity < serialized_length) {
        return false;
    }

    clear_bytes(output, serialized_length);
    output[0] = record->wire_type;
    store_u32_le(&output[0x0Cu], record->start_timestamp < 0
        ? 0u : (uint32_t)record->start_timestamp);
    store_u32_le(&output[0x10u], (uint32_t)record->end_timestamp);

    if (record->wire_type == 1u) {
        output[1] = (uint8_t)float_to_u32_toward_zero(
            record->efficiency * 100.0f);
        output[2] = (uint8_t)float_to_u32_toward_zero(record->score);
        output[5] = (uint8_t)float_to_u32_toward_zero(
            record->rem_fraction * 100.0f);
        output[6] = (uint8_t)float_to_u32_toward_zero(
            record->light_fraction * 100.0f);
        output[7] = (uint8_t)float_to_u32_toward_zero(
            record->deep_fraction * 100.0f);
        output[4] = (uint8_t)(UINT32_C(100) - (uint32_t)output[5] -
                              (uint32_t)output[6] - (uint32_t)output[7]);
        store_u16_le_early(&output[8], record->body_temperature);
        store_u16_le_early(&output[0x14u],
            (uint16_t)float_to_u32_toward_zero(
                record->total_minutes * 60.0f));
        store_u16_le_early(&output[0x16u],
            (uint16_t)float_to_u32_toward_zero(
                record->wake_minutes * 60.0f));
        store_u16_le_early(&output[0x18u],
            (uint16_t)float_to_u32_toward_zero(
                record->rem_minutes * 60.0f));
        store_u16_le_early(&output[0x1Au],
            (uint16_t)float_to_u32_toward_zero(
                record->light_minutes * 60.0f));
        store_u16_le_early(&output[0x1Cu],
            (uint16_t)float_to_u32_toward_zero(
                record->deep_minutes * 60.0f));

        size_t encoded_count = 0u;
        if (!gomore_primitives_run_length_encode_2bit(
                record->stages, record->stage_count,
                &output[GOMORE_PRIMITIVES_FINAL_SLEEP_HEADER_BYTES],
                compact_count, &encoded_count) ||
                encoded_count != compact_count) {
            return false;
        }
        store_u16_le_early(&output[0x1Eu], (uint16_t)encoded_count);
    }
    *written = serialized_length;
    return true;
}

bool gomore_primitives_output_lifecycle_dispatch(
    void *context, gomore_primitives_output_lifecycle_state *state,
    const gomore_primitives_output_lifecycle_providers *providers) {
    if (state == NULL || providers == NULL ||
            providers->refresh_input == NULL ||
            providers->update_engine == NULL ||
            providers->result_ready == NULL ||
            providers->consume_activity == NULL ||
            providers->publish_sleep_status == NULL ||
            providers->publish_final_sleep == NULL ||
            providers->authorize == NULL) {
        return false;
    }

    providers->refresh_input(context);
    providers->update_engine(context);
    if (!providers->result_ready(context)) {
        return true;
    }

    for (uint32_t slot = 0u; slot < 7u; ++slot) {
        if ((state->active_slot_mask & (uint8_t)(UINT8_C(1) << slot)) == 0u) {
            continue;
        }
        if (slot == 0u) {
            providers->consume_activity(context, state->activity);
            continue;
        }
        if (slot != 3u) {
            /* Slot two routes to the recovered no-op; 1/4/5/6 have no route. */
            continue;
        }

        bool final_workspace_available = true;
        if ((state->sleep_lifecycle_flags & UINT8_C(0x02)) != 0u) {
            providers->publish_sleep_status(context, 1u);
        } else if ((state->sleep_lifecycle_flags & UINT8_C(0x04)) != 0u) {
            providers->publish_sleep_status(context, 0u);
            if ((state->sleep_lifecycle_flags & UINT8_C(0x08)) != 0u) {
                final_workspace_available =
                    providers->publish_final_sleep(context);
            }
        }

        if (final_workspace_available &&
                (int32_t)state->stage_ppg_request !=
                    (int32_t)state->previous_stage_ppg_request) {
            providers->authorize(
                context, 4u, !state->previous_stage_ppg_request);
        }
    }

    state->accelerometer_pending = false;
    state->optical_pending = false;
    return true;
}

static bool authorization_any_stream_requirement(
    const gomore_primitives_authorization_state *state,
    uint8_t requirement_mask) {
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_RECORD_COUNT; ++index) {
        const uint8_t flags = state->slots[index].flags;
        if ((flags & UINT8_C(0x01)) != 0u &&
                (flags & requirement_mask) != 0u) {
            return true;
        }
    }
    return false;
}

static bool authorization_all_slots_clear(
    const gomore_primitives_authorization_state *state) {
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_RECORD_COUNT; ++index) {
        if ((state->slots[index].flags & UINT8_C(0x01)) != 0u) {
            return false;
        }
    }
    return true;
}

bool gomore_primitives_authorization_dispatch(
    gomore_primitives_authorization_state *state,
    uint32_t slot, bool enable,
    const gomore_primitives_authorization_providers *providers) {
    if (state == NULL || providers == NULL ||
            providers->register_stream == NULL ||
            providers->unregister_stream == NULL ||
            providers->create_timer == NULL ||
            providers->delete_timer == NULL ||
            !state->initialized ||
            slot >= GOMORE_PRIMITIVES_RECORD_COUNT) {
        return false;
    }
    gomore_primitives_authorization_slot *const selected =
        &state->slots[slot];
    if (((selected->flags & UINT8_C(0x01)) != 0u) == enable) {
        return false;
    }

    if (enable) {
        for (uint8_t stream = 0u; stream < 4u; ++stream) {
            const uint8_t mask =
                (uint8_t)(UINT8_C(1) << (uint8_t)(stream + 1u));
            if ((selected->flags & mask) != 0u &&
                    !authorization_any_stream_requirement(state, mask) &&
                    state->stream_handles[stream] == (uintptr_t)0) {
                state->stream_handles[stream] =
                    providers->register_stream(
                        providers->context, stream);
            }
        }
        if (selected->on_enable != NULL) {
            selected->on_enable(selected->context);
        }
    }

    selected->flags = (uint8_t)(
        (selected->flags & UINT8_C(0xFE)) |
        (enable ? UINT8_C(0x01) : UINT8_C(0x00)));

    if (!enable) {
        for (uint8_t stream = 0u; stream < 4u; ++stream) {
            const uint8_t mask =
                (uint8_t)(UINT8_C(1) << (uint8_t)(stream + 1u));
            if ((selected->flags & mask) != 0u &&
                    !authorization_any_stream_requirement(state, mask) &&
                    state->stream_handles[stream] != (uintptr_t)0) {
                providers->unregister_stream(
                    providers->context, stream,
                    state->stream_handles[stream]);
                state->stream_handles[stream] = (uintptr_t)0;
                if (stream == 2u) {
                    state->heart_rate_state = 0.0f;
                } else if (stream == 3u) {
                    state->auxiliary_handles[0] = (uintptr_t)0;
                    state->auxiliary_handles[1] = (uintptr_t)0;
                    state->hrv_state = 0u;
                }
            }
        }
        if (selected->on_disable != NULL) {
            selected->on_disable(selected->context);
        }
    }

    const bool all_clear = authorization_all_slots_clear(state);
    if (all_clear && state->idle_timer_handle == (uintptr_t)0) {
        state->idle_timer_handle = providers->create_timer(
            providers->context, UINT32_C(1000));
    } else if (!all_clear &&
               state->idle_timer_handle != (uintptr_t)0) {
        providers->delete_timer(
            providers->context, state->idle_timer_handle);
        state->idle_timer_handle = (uintptr_t)0;
    }
    return true;
}

bool gomore_primitives_propagate_packed_status(
    void *state, size_t length, uint8_t *value) {
    if (state == NULL || length < 1001u || value == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    if (bytes[1000] != 0u) {
        const uint32_t slot = load_u32_le(&bytes[0x2D0u]) / UINT32_C(30);
        uint8_t previous = 0u;
        if (!gomore_primitives_packed_2bit_get(
                bytes, 0x2D0u, (slot - 2u) % UINT32_C(0xB40), &previous) ||
            !gomore_primitives_packed_2bit_set(
                bytes, 0x2D0u, (slot - 1u) % UINT32_C(0xB40), previous)) {
            return false;
        }
        *value = previous;
        bytes[1000] = 0u;
    }
    return true;
}

bool gomore_primitives_filter_bank_initialize(
    void *record, size_t length,
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2) {
    if (record == NULL || length < 0x140u || initialize_lt2 == NULL ||
            initialize_mode2 == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    const float first_parameters[2] = {
        bits_float(UINT32_C(0x3C2A64C3)),
        bits_float(UINT32_C(0x3F75C28F))
    };
    if (!gomore_primitives_mode_state_configure(
            bytes, length, 2u, 2u, first_parameters,
            initialize_lt2, initialize_mode2)) {
        return false;
    }
    const float remaining_parameters[2] = {
        bits_float(UINT32_C(0x3F75C28F)), 0.0f
    };
    for (size_t index = 1u; index < 4u; ++index) {
        if (!gomore_primitives_mode_state_configure(
                &bytes[index * 0x50u], length - index * 0x50u,
                0u, 2u, remaining_parameters,
                initialize_lt2, initialize_mode2)) {
            return false;
        }
    }
    return true;
}

bool gomore_primitives_target_runs(
    int8_t target, const int8_t *values, size_t count,
    uint16_t (*runs)[2], size_t run_capacity,
    size_t *run_count, size_t *match_count) {
    if ((values == NULL && count != 0u) || runs == NULL ||
            run_count == NULL || match_count == NULL) {
        return false;
    }
    *run_count = 0u;
    *match_count = 0u;
    int32_t previous = -1;
    const size_t stock_capacity = run_capacity < 40u ? run_capacity : 40u;
    for (size_t index = 0u; index < count; ++index) {
        if (values[index] == target && *run_count < stock_capacity) {
            if (previous == target) {
                runs[*run_count - 1u][1] = (uint16_t)(index + 1u);
            } else {
                runs[*run_count][0] = (uint16_t)index;
                runs[*run_count][1] = (uint16_t)(index + 1u);
                ++*run_count;
            }
            ++*match_count;
        }
        previous = values[index];
    }
    return true;
}

bool gomore_primitives_sleep_stage_proportion_adjust(
    int8_t *values, size_t count, int8_t target,
    int32_t adjustment, int32_t *remaining_adjustment) {
    if ((values == NULL && count != 0u) || count > UINT16_MAX ||
            remaining_adjustment == NULL ||
            (adjustment < -6 &&
             (int64_t)adjustment - (int64_t)count < INT32_MIN)) {
        return false;
    }

    int32_t remaining = adjustment;
    if (remaining >= -6 && remaining <= 6) {
        *remaining_adjustment = remaining;
        return true;
    }

    uint16_t runs[40][2];
    size_t run_count = 0u;
    size_t match_count = 0u;
    if (!gomore_primitives_target_runs(
            target, values, count, runs, 40u,
            &run_count, &match_count)) {
        return false;
    }
    (void)match_count;

    if (remaining < -6) {
        size_t visited = 0u;
        while (visited < run_count && remaining < -6) {
            const size_t run = target == 1 ? visited : run_count - visited - 1u;
            const size_t begin = runs[run][0];
            const size_t end = runs[run][1];
            const size_t span = end - begin;
            if (span < 13u) {
                for (size_t index = begin; index < end; ++index) {
                    values[index] = 2;
                }
                remaining -= (int32_t)span;
            } else {
                for (size_t index = 0u; index < 6u; ++index) {
                    values[begin + index] = 2;
                    values[end - index - 1u] = 2;
                }
                remaining += 12;
            }
            ++visited;
        }
        *remaining_adjustment = remaining;
        return true;
    }

    const int32_t original_adjustment = remaining;
    for (size_t run = 0u; run < run_count && remaining > 12; ++run) {
        const size_t begin = runs[run][0];
        const size_t leading_begin = begin > 12u ? begin - 12u : 0u;
        bool all_two = true;
        for (size_t index = begin + 1u; index > leading_begin; --index) {
            if (values[index - 1u] != 2) {
                all_two = false;
            }
        }
        if (all_two) {
            const size_t replacement_begin = begin > 6u ? begin - 6u : 0u;
            for (size_t index = begin + 1u;
                    index > replacement_begin; --index) {
                values[index - 1u] = target;
                --remaining;
            }
        }

        const size_t end = runs[run][1];
        const size_t scan_end = end + 12u < count ? end + 12u : count;
        all_two = true;
        for (size_t index = end; index < scan_end; ++index) {
            if (values[index] != 2) {
                all_two = false;
            }
        }
        if (all_two) {
            const size_t replacement_end = end + 6u < count ? end + 6u : count;
            for (size_t index = end; index < replacement_end; ++index) {
                values[index] = target;
                --remaining;
            }
        }
    }

    if (original_adjustment - remaining < 12) {
        run_count = 0u;
        match_count = 0u;
        if (!gomore_primitives_target_runs(
                2, values, count, runs, 40u,
                &run_count, &match_count)) {
            return false;
        }
        for (size_t run = 0u; run < run_count; ++run) {
            const size_t begin = runs[run][0];
            const size_t end = runs[run][1];
            if (end - begin >= 40u) {
                const size_t center = (begin + end) / 2u;
                for (size_t index = center - 6u; index < center + 6u;
                        ++index) {
                    values[index] = target;
                }
                remaining -= 12;
                break;
            }
        }
    }
    *remaining_adjustment = remaining;
    return true;
}

bool gomore_primitives_smooth_target_run_edges(
    int8_t target, int8_t *values, size_t count,
    bool alternate_policy) {
    if ((values == NULL && count != 0u) || count > UINT16_MAX) {
        return false;
    }
    uint16_t runs[40][2];
    size_t run_count = 0u;
    size_t match_count = 0u;
    if (!gomore_primitives_target_runs(
            target, values, count, runs, 40u,
            &run_count, &match_count)) {
        return false;
    }
    (void)match_count;

    if (target == 0) {
        for (size_t run = 0u; run < run_count; ++run) {
            const size_t begin = runs[run][0];
            const size_t end = runs[run][1];
            if (begin == 0u) {
                continue;
            }
            const size_t span = end - begin;
            size_t edge = span / 3u;
            if (!alternate_policy) {
                edge = span < 11u ? (span + 1u) / 2u : 0u;
            } else if (span >= 10u && span < 20u) {
                edge = (span + 1u) / 2u;
            } else if (span >= 20u && edge > 20u) {
                edge = 20u;
            }
            if (((span - edge) & 1u) == 1u) {
                ++edge;
            }
            const int8_t leading = values[begin - 1u];
            for (size_t index = 0u; index < edge; ++index) {
                values[begin + index] = leading;
            }
            const int8_t trailing = end < count ? values[end] : 0;
            for (size_t index = 0u; index < edge; ++index) {
                values[end - index - 1u] = trailing;
            }
        }
    } else if (target == 1) {
        for (size_t run = 0u; run < run_count; ++run) {
            const size_t begin = runs[run][0];
            const size_t end = runs[run][1];
            const size_t span = end - begin;
            const size_t edge = (span + 1u) / 3u;
            if (span > 40u) {
                for (size_t index = 0u; index < edge; ++index) {
                    values[begin + index] = 2;
                }
                for (size_t index = 0u; index < edge; ++index) {
                    values[end - index - 1u] = 2;
                }
            }
        }
    }
    return true;
}

bool gomore_primitives_shift_marked_history(uint8_t *values,
                                            size_t capacity,
                                            size_t *count,
                                            size_t shift) {
    if (values == NULL || count == NULL || *count > capacity ||
            shift > capacity - *count) {
        return false;
    }
    if (shift == 0u) {
        return true;
    }
    for (size_t remaining = *count; remaining != 0u; --remaining) {
        values[remaining - 1u + shift] = values[remaining - 1u];
    }
    clear_bytes(values, shift);
    *count += shift;
    size_t marked = 0u;
    for (size_t index = 0u; index < *count && values[index] != 2u &&
            marked < 21u; ++index) {
        if (values[index] != 0u) {
            values[index] = 2u;
            ++marked;
        }
    }
    return true;
}

bool gomore_primitives_register_mode_topics(
    uintptr_t context, uintptr_t mode4_handler, uintptr_t mode3_handler,
    gomore_primitives_topic_register_fn register_topic) {
    if (register_topic == NULL) {
        return false;
    }
    register_topic(4u, mode4_handler, context);
    register_topic(3u, mode3_handler, context);
    return true;
}

float gomore_primitives_exponential_affine(
    float value, float scale, float center, float offset,
    gomore_primitives_float_unary_fn exponential) {
    if (exponential == NULL) {
        return 0.0f;
    }
    return exponential((value - center) * scale) + offset;
}

int32_t gomore_primitives_seed_and_test_text_class(
    const uint8_t *text, size_t text_length,
    const uint8_t classes[256],
    const void *source_record, size_t source_length,
    void *destination_record, size_t destination_length,
    gomore_primitives_seed_fn seed) {
    if ((text == NULL && text_length != 0u) || classes == NULL ||
            source_record == NULL || source_length < 0x10u ||
            destination_record == NULL || destination_length < 0x10u ||
            seed == NULL) {
        return -1;
    }
    const uint8_t *source = source_record;
    uint8_t *destination = destination_record;
    const uint32_t seed_value = load_u32_le(&source[0x0Cu]);
    store_u32_le(&destination[0x0Cu], seed_value);
    seed(seed_value);
    return gomore_primitives_all_class_0x20(text, text_length, classes) != 0
        ? -1004 : 0;
}

int32_t gomore_primitives_validate_record_bytes(
    const uint8_t *candidate, size_t candidate_length,
    const void *source_record, size_t source_length,
    void *destination_record, size_t destination_length) {
    if (candidate == NULL || source_record == NULL || source_length < 9u ||
            destination_record == NULL || destination_length < 0x10u) {
        return -1;
    }
    const uint8_t *source = source_record;
    const size_t compare_length = source[8];
    if (compare_length > candidate_length ||
            compare_length > source_length - 4u) {
        return -1;
    }
    for (size_t index = 0u; index < compare_length; ++index) {
        if (source[4u + index] != candidate[index]) {
            store_u32_le(&((uint8_t *)destination_record)[0x0Cu], 0u);
            return -1005;
        }
    }
    return 0;
}

int32_t gomore_primitives_validate_su_signature(
    const uint8_t *candidate, size_t candidate_length,
    void *destination_record, size_t destination_length) {
    static const uint8_t signature[3] = {'S', 'U', 0u};
    if (candidate == NULL || candidate_length < sizeof(signature) ||
            destination_record == NULL || destination_length < 0x10u) {
        return -1;
    }
    for (size_t index = 0u; index < sizeof(signature); ++index) {
        if (candidate[index] != signature[index]) {
            store_u32_le(&((uint8_t *)destination_record)[0x0Cu], 0u);
            return -1007;
        }
    }
    return 0;
}

bool gomore_primitives_sps_engine_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_void_context_fn finish_initialize) {
    if (record == NULL || length < 0x58u || finish_initialize == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0], 0u);
    store_u32_le(&bytes[4], 0u);
    store_u32_le(&bytes[8], 0u);
    store_u32_le(&bytes[0x24u], 1u);
    store_u32_le(&bytes[0x40u], binding);
    store_u16_le_early(&bytes[0x50u], 8u);
    store_u32_le(&bytes[0x44u], 0u);
    store_u32_le(&bytes[0x48u], 0u);
    store_u32_le(&bytes[0x3Cu], 0u);
    store_u32_le(&bytes[0x34u], UINT32_C(0x3F800000));
    store_u32_le(&bytes[0x38u], 0u);
    store_u32_le(&bytes[0x20u], 0u);
    store_u32_le(&bytes[0x18u], UINT32_C(0x3F800000));
    store_u32_le(&bytes[0x1Cu], 0u);
    if (!gomore_primitives_sps_state_reset(record, length)) {
        return false;
    }
    finish_initialize(record);
    return true;
}

int32_t gomore_primitives_state_mode_dispatch(
    void *state, size_t state_length, int32_t mode, uint8_t value,
    gomore_primitives_state_byte_fn mode0,
    gomore_primitives_state_byte_fn mode1,
    gomore_primitives_state_call_fn mode2,
    gomore_primitives_state_call_fn mode3) {
    if (state == NULL) {
        return -1;
    }
    uint8_t *bytes = state;
    int32_t status = -1;
    if (mode == 0 && state_length >= 0xD15u && mode0 != NULL) {
        status = mode0(&bytes[0xD14u], value);
    } else if (mode == 1 && state_length >= 0x13F9u && mode1 != NULL) {
        status = mode1(&bytes[0x13F8u], value);
    } else if (mode == 2 && state_length >= 0xD99u && mode2 != NULL) {
        status = mode2(&bytes[0xD98u]);
    } else if (mode == 3 && state_length >= 0x391Du && mode3 != NULL) {
        status = mode3(&bytes[0x391Cu]);
    }
    return status == 0 ? 0 : -1;
}

bool gomore_primitives_commit_valid_time_record_adapter(
    void *engine, size_t engine_length,
    void *destination, size_t destination_length,
    const void *record, size_t record_length) {
    if (engine == NULL || engine_length < 0x126Cu) {
        return false;
    }
    return gomore_primitives_commit_valid_time_record(
        &((uint8_t *)engine)[0x1130u], engine_length - 0x1130u,
        destination, destination_length, record, record_length);
}

float gomore_primitives_one_minus(float value) {
    return 1.0f - value;
}

float gomore_primitives_logistic(
    float value, gomore_primitives_float_unary_fn exponential) {
    if (exponential == NULL) {
        return 0.0f;
    }
    return 1.0f / (exponential(-value) + 1.0f);
}

float gomore_primitives_scaled_product(float first, float second) {
    const double scaled = (double)first * 2.8;
    const double product = scaled * (double)second;
    return (float)(product / 200.0);
}

int32_t gomore_primitives_linear_sign_classify(
    float first, float second, float third, int32_t integer,
    const float coefficients[4], float bias) {
    if (coefficients == NULL) {
        return -1;
    }
    float sum = coefficients[0] * (float)integer;
    sum += first * coefficients[1];
    sum += second * coefficients[2];
    sum += third * coefficients[3];
    sum += bias;
    return sum >= 0.0f ? -1 : 1;
}

int32_t gomore_primitives_validate_key_and_update_status(
    const uint8_t *candidate, size_t candidate_length,
    const void *configuration, size_t configuration_length,
    void *state, size_t state_length,
    void *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (candidate == NULL || configuration == NULL ||
            configuration_length < 9u || state == NULL ||
            state_length < 0x14u || status_record == NULL ||
            status_length < 12u) {
        return -1;
    }
    const uint8_t *config = configuration;
    const size_t compare_length = config[8];
    if (compare_length > candidate_length ||
            compare_length > configuration_length - 4u) {
        return -1;
    }
    uint8_t *state_bytes = state;
    uint8_t *status = status_record;
    state_bytes[0x10u] = (uint8_t)(state_bytes[0x10u] + 1u);
    const int32_t comparison = gomore_primitives_nullable_compare_n(
        &config[4], candidate, compare_length);
    if (comparison != 0) {
        store_u16_le_early(&status[6], (uint16_t)(int16_t)-1005);
        const int32_t result = gomore_primitives_status_or_random(
            state_bytes, state_length, status, status_length,
            prepare, random_value);
        store_u16_le_early(&state_bytes[4], (uint16_t)result);
        store_u32_le(&state_bytes[8], 0u);
        return -1005;
    }
    const int32_t result = gomore_primitives_status_or_random(
        state_bytes, state_length, status, status_length,
        prepare, random_value);
    store_u16_le_early(&state_bytes[4], (uint16_t)result);
    return 0;
}

int32_t gomore_primitives_decimal_config_update(
    const uint8_t *text,
    const void *configuration, size_t configuration_length,
    void *state, size_t state_length,
    void *status_record, size_t status_length,
    bool validation_enabled,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (text == NULL || configuration == NULL ||
            configuration_length < 0x10u || state == NULL ||
            state_length < 0x14u || status_record == NULL ||
            status_length < 12u) {
        return -1;
    }
    const uint32_t parsed = (uint32_t)gomore_primitives_decimal_parse(text);
    uint8_t *state_bytes = state;
    uint8_t *status = status_record;
    state_bytes[0x10u] = (uint8_t)(state_bytes[0x10u] + 1u);
    if (validation_enabled) {
        const uint32_t cap = parsed <= UINT32_C(0x6953F6FF)
            ? parsed : UINT32_C(0x6953F6FF);
        const uint32_t configured =
            load_u32_le(&((const uint8_t *)configuration)[0x0Cu]);
        if (cap < configured || configured < UINT32_C(0x688A4180)) {
            store_u16_le_early(&status[8], (uint16_t)(int16_t)-1006);
            const int32_t result = gomore_primitives_status_or_random(
                state_bytes, state_length, status, status_length,
                prepare, random_value);
            store_u16_le_early(&state_bytes[4], (uint16_t)result);
            store_u32_le(&state_bytes[8], 0u);
            return -1006;
        }
    }
    const int32_t result = gomore_primitives_status_or_random(
        state_bytes, state_length, status, status_length,
        prepare, random_value);
    store_u16_le_early(&state_bytes[4], (uint16_t)result);
    store_u32_le(&state_bytes[8], parsed);
    return 0;
}

int32_t gomore_primitives_runtime_version_validate(
    uint32_t value, bool allow_missing_runtime, bool validation_enabled,
    uint32_t configured_limit, bool runtime_present,
    int16_t configured_version, int16_t runtime_version) {
    int32_t status = 0;
    if (validation_enabled &&
            (configured_limit <= value || value <= UINT32_C(0x688A4180))) {
        status = -1006;
    }
    if (!allow_missing_runtime && !runtime_present) {
        return -1;
    }
    if (configured_version != runtime_version) {
        return -1008;
    }
    return status;
}

bool gomore_primitives_dominant_sorted_i32(
    int32_t *values, size_t count,
    int32_t *dominant_value, size_t *dominant_count) {
    if (values == NULL || count == 0u || dominant_value == NULL ||
            dominant_count == NULL) {
        return false;
    }
    for (size_t index = 1u; index < count; ++index) {
        const int32_t value = values[index];
        size_t position = index;
        while (position != 0u && values[position - 1u] > value) {
            values[position] = values[position - 1u];
            --position;
        }
        values[position] = value;
    }
    int32_t current_value = values[0];
    size_t current_count = 1u;
    *dominant_value = current_value;
    *dominant_count = 1u;
    for (size_t index = 1u; index < count; ++index) {
        const int32_t next_value = values[index];
        if (next_value == current_value) {
            ++current_count;
        }
        if (next_value != current_value || index == count - 1u) {
            if (current_count >= *dominant_count) {
                *dominant_count = current_count;
                *dominant_value = current_value;
            }
            current_value = next_value;
            current_count = 1u;
        }
    }
    return true;
}

int32_t gomore_primitives_circular_signal_predicate(
    const int16_t *primary, const int16_t *first,
    const int16_t *second, const int16_t *third,
    size_t count, int32_t cursor, size_t lookback) {
    if (primary == NULL || first == NULL || second == NULL || third == NULL ||
            count == 0u || count > 127u || lookback > count ||
            cursor < 0 || cursor >= (int32_t)count) {
        return -1;
    }
    int32_t primary_matches = 0;
    int32_t combined_matches = 0;
    for (size_t offset = 1u; offset <= lookback; ++offset) {
        int32_t index = cursor - (int32_t)offset;
        if (index < 0) {
            index += (int32_t)count;
        }
        if (primary[index] > 200) {
            ++primary_matches;
        }
        const int32_t combined = (int32_t)first[index] +
                                 (int32_t)second[index] +
                                 (int32_t)third[index];
        if (combined > 180) {
            ++combined_matches;
        }
    }
    return primary_matches >= 3 && combined_matches >= 3 ? 1 : -1;
}

float gomore_primitives_average_sign_crossing_spacing(
    const float *values, size_t count) {
    if (values == NULL || count < 2u) {
        return -1.0f;
    }
    int32_t first_crossing = -1;
    int32_t last_crossing = -1;
    int32_t crossing_divisor = -1;
    for (size_t index = 0u; index + 1u < count; ++index) {
        if (values[index] * values[index + 1u] < 0.0f) {
            if (first_crossing == -1) {
                first_crossing = (int32_t)index;
            }
            last_crossing = (int32_t)index;
            ++crossing_divisor;
        }
    }
    if (crossing_divisor <= 0) {
        return -1.0f;
    }
    return (float)(last_crossing - first_crossing) /
           (float)crossing_divisor;
}

float gomore_primitives_round_decimal_places(
    float value, float places,
    gomore_primitives_float_binary_fn power) {
    if (power == NULL) {
        return 0.0f;
    }
    const float scale = power(10.0f, places);
    if (scale == 0.0f) {
        return 0.0f;
    }
    const float adjusted = value >= 0.0f
        ? value * scale + 0.5f
        : value * scale - bits_float(UINT32_C(0x3ECCCCCD));
    int32_t converted;
    if (adjusted != adjusted) {
        converted = 0;
    } else if (adjusted >= 2147483648.0f) {
        converted = INT32_MAX;
    } else if (adjusted <= -2147483648.0f) {
        converted = INT32_MIN;
    } else {
        converted = (int32_t)adjusted;
    }
    return (float)converted / scale;
}

bool gomore_primitives_time_engine_initialize(
    void *state, size_t state_length,
    uint8_t *configuration, size_t configuration_length,
    uint32_t configuration_binding) {
    if (state == NULL || state_length < 0x13Cu || configuration == NULL ||
            configuration_length < 10u) {
        return false;
    }
    uint8_t *bytes = state;
    clear_bytes(bytes, 0x13Cu);
    if (configuration[0] == 0u) {
        configuration[0] = 1u;
        store_u16_le_early(&configuration[2], 15u);
        store_u16_le_early(&configuration[4], 120u);
        configuration[6] = 0u;
        configuration[7] = 0u;
        configuration[8] = 20u;
        configuration[9] = 8u;
    }
    store_u32_le(&bytes[0x138u], configuration_binding);
    if (bytes[0xB8u] == 0u) {
        store_u32_le(&bytes[0xB0u], 600u);
    }
    if (!gomore_primitives_clear_90(&bytes[0x48u],
                                    state_length - 0x48u) ||
            !gomore_primitives_clear_72(bytes, state_length)) {
        return false;
    }
    store_u32_le(&bytes[0x130u], load_u32_le(&configuration[2]));
    store_u32_le(&bytes[0x134u], load_u32_le(&configuration[6]));
    return true;
}

bool gomore_primitives_interval_nonzero_argmax(
    const float *values, size_t value_count,
    const uint8_t *boundaries, size_t boundary_count,
    uint8_t *output, size_t output_capacity, size_t *output_count) {
    if (values == NULL || boundaries == NULL || boundary_count == 0u ||
            boundary_count > 256u || output == NULL || output_count == NULL ||
            *output_count > output_capacity) {
        return false;
    }
    for (size_t index = 0u; index + 1u < boundary_count; ++index) {
        const int32_t begin = boundaries[index];
        const int32_t end = boundaries[index + 1u];
        if ((double)(end - begin) <= 7.5) {
            continue;
        }
        if (begin < 0 || end <= begin || (size_t)end > value_count) {
            continue;
        }
        const size_t selected = gomore_primitives_float_argmax_range(
            values, value_count, (size_t)begin, (size_t)end);
        if (selected != SIZE_MAX && values[selected] != 0.0f) {
            if (*output_count >= output_capacity || selected > UINT8_MAX) {
                return false;
            }
            output[(*output_count)++] = (uint8_t)selected;
        }
    }
    return true;
}

int32_t gomore_primitives_sequence_replay(
    void *state, size_t state_length,
    void *record, size_t record_length,
    gomore_primitives_record_step_fn process_record) {
    if (state == NULL || state_length < 0x54u || record == NULL ||
            record_length < 8u || process_record == NULL) {
        return -1;
    }
    uint8_t *state_bytes = state;
    uint8_t *record_bytes = record;
    uint32_t base = load_u32_le(&state_bytes[0x48u]);
    uint32_t sequence = load_u32_le(&record_bytes[4]);
    if (base == UINT32_MAX) {
        base = sequence;
        store_u32_le(&state_bytes[0x48u], base);
    }
    const uint32_t difference = sequence - base;
    uint32_t iterations;
    if (difference - 2u < 14u) {
        iterations = difference;
        store_u32_le(&state_bytes[0x4Cu], iterations);
        sequence = base + 1u;
        store_u32_le(&record_bytes[4], sequence);
    } else if (difference == 1u || sequence == base) {
        iterations = 1u;
        store_u32_le(&state_bytes[0x4Cu], iterations);
    } else {
        store_u16_le_early(&state_bytes[0x52u],
                           (uint16_t)(int16_t)-1027);
        return -1027;
    }
    int32_t status = -1016;
    for (uint32_t index = 0u; index < iterations; ++index) {
        status = process_record(state, record);
        if (iterations != 1u) {
            sequence = load_u32_le(&record_bytes[4]) + 1u;
            store_u32_le(&record_bytes[4], sequence);
        }
    }
    store_u32_le(&state_bytes[0x48u], load_u32_le(&record_bytes[4]));
    return status;
}

bool gomore_primitives_state_window_predicate(bool requested_active,
                                              uint32_t now,
                                              uint32_t last_transition,
                                              bool flag_a8,
                                              bool flag_a9) {
    if (!requested_active) {
        return flag_a8 || flag_a9;
    }
    return (flag_a8 || flag_a9) &&
           now - last_transition > UINT32_C(300);
}

static char hex_digit(uint32_t nibble) {
    return (char)(nibble < 10u ? (uint32_t)'0' + nibble
                              : (uint32_t)'a' + (nibble - 10u));
}

static void store_hex8(uint8_t *destination, uint32_t value) {
    for (size_t index = 0u; index < 8u; ++index) {
        const uint32_t shift = (uint32_t)((7u - index) * 4u);
        destination[index] = (uint8_t)hex_digit((value >> shift) & 0x0Fu);
    }
}

bool gomore_primitives_key_or_cached_copy(
    uint8_t *destination, size_t capacity,
    bool cache_valid, const uint8_t *cache, size_t cache_length,
    uint32_t device_id_0, uint32_t device_id_1, uint32_t address_word,
    size_t *written) {
    if (destination == NULL || written == NULL) {
        return false;
    }
    if (cache_valid) {
        if ((cache == NULL && cache_length != 0u) || cache_length > capacity) {
            return false;
        }
        for (size_t index = 0u; index < cache_length; ++index) {
            destination[index] = cache[index];
        }
        *written = cache_length;
        return true;
    }
    if (capacity < 25u) {
        return false;
    }
    store_hex8(&destination[0], address_word);
    store_hex8(&destination[8], device_id_0);
    store_hex8(&destination[16], device_id_1);
    destination[24] = 0u;
    *written = 24u;
    return true;
}

void gomore_primitives_slot_state_transition(uint8_t *state,
                                             uint8_t requested,
                                             bool guarded_mode) {
    if (state == NULL) {
        return;
    }
    if (guarded_mode) {
        if (*state == 4u) {
            if (requested == 5u) {
                *state = 1u;
            }
        } else {
            *state = requested;
        }
    } else if (*state != 3u && *state != 4u) {
        *state = requested;
    }
}

int32_t gomore_primitives_copy_key_blob(
    uint8_t *destination, size_t capacity,
    bool cache_valid, const uint8_t *cache,
    gomore_primitives_blob_loader_fn loader, void *loader_context) {
    if (destination == NULL || capacity < 0x40u) {
        return -2;
    }
    uint8_t loaded[0x40];
    const uint8_t *source = cache;
    if (!cache_valid) {
        if (loader == NULL || !loader(loader_context, loaded, sizeof(loaded))) {
            return -2;
        }
        source = loaded;
    }
    if (source == NULL) {
        return -2;
    }
    for (size_t index = 0u; index < 0x40u; ++index) {
        destination[index] = source[index];
    }
    return 0x40;
}

int32_t gomore_primitives_stage_32_and_consume(
    uintptr_t first, uintptr_t second, const uint8_t *source,
    size_t source_length, uintptr_t fourth, uintptr_t fifth,
    gomore_primitives_stage_consumer_fn consumer) {
    if (source == NULL || source_length < 32u || consumer == NULL) {
        return -1;
    }
    uint8_t staged[32];
    clear_bytes(staged, sizeof(staged));
    for (size_t index = 0u; index < sizeof(staged); ++index) {
        staged[index] = source[index];
    }
    return consumer(first, second, staged, fourth, fifth);
}

float gomore_primitives_mean(const float *values, size_t count) {
    if (values == NULL || count == 0u) {
        return 0.0f;
    }
    float sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        sum += values[index];
    }
    return sum / (float)count;
}

int32_t gomore_primitives_argmax_from_zero(const float *values, size_t count) {
    if (values == NULL || count == 0u || count > (size_t)INT32_MAX) {
        return -1;
    }
    int32_t result = (int32_t)(count - 1u);
    float largest = 0.0f;
    for (size_t remaining = count; remaining != 0u; --remaining) {
        const size_t index = remaining - 1u;
        if (values[index] > largest) {
            largest = values[index];
            result = (int32_t)index;
        }
    }
    return result;
}

bool gomore_primitives_reset_provider_state(
    uint8_t *state, size_t length, bool active,
    gomore_primitives_mode_fn set_mode,
    gomore_primitives_void_context_fn release,
    void *release_context, gomore_primitives_init_fn initialize) {
    if (state == NULL || length < 0x2E0u || release == NULL ||
            initialize == NULL || (active && set_mode == NULL)) {
        return false;
    }
    if (active) {
        set_mode(4u, 0u);
    }
    release(release_context);
    clear_bytes(state, 0x2E0u);
    initialize(1u);
    return true;
}

bool gomore_primitives_sample_plausible(const uint8_t sample[4]) {
    return sample != NULL && sample[0] > 10u && sample[0] < 100u &&
           sample[1] < 2u && sample[2] > 100u && sample[2] < 0xDCu &&
           sample[3] > 0x1Eu && sample[3] < 0x96u;
}

uint32_t gomore_primitives_health_sample_features(
    const uint8_t record[12], float output[7]) {
    if (record == NULL || output == NULL) {
        return 0u;
    }
    output[0] = (float)record[0];
    output[1] = record[1] == 1u ? 1.0f : 0.0f;
    output[2] = (float)record[2];
    output[3] = (float)record[3];
    for (size_t index = 0u; index < 3u; ++index) {
        const uint16_t encoded = load_u16_le_early(&record[4u + index * 2u]);
        const int32_t value = (encoded & UINT16_C(0x8000)) != 0u
            ? (int32_t)encoded - INT32_C(65536)
            : (int32_t)encoded;
        output[4u + index] = value == 0 ? -1.0f : (float)value;
    }
    return gomore_primitives_sample_plausible(record) ? 1u : 0u;
}

bool gomore_primitives_scaled_sample_publish(
    gomore_primitives_scaled_sample_state *state,
    bool publish_enabled, gomore_primitives_event_publish_fn publish) {
    if (state == NULL || (publish_enabled && publish == NULL)) {
        return false;
    }
    if (state->recent_count < 5u) {
        return true;
    }
    uint32_t total = 0u;
    for (size_t index = 0u; index < 5u; ++index) {
        total += state->recent[index];
    }
    const uint16_t average = (uint16_t)(total / 5u);
    const uint16_t event_value =
        (uint16_t)((double)average * 0x1.47ae147ae147bp-7);
    const uint16_t captured_value =
        (uint16_t)((double)average * 0x1.999999999999ap-4);
    if (state->capture_enabled && state->capture_count < 50u) {
        state->captured[state->capture_count] = captured_value;
        ++state->capture_count;
    }
    if (publish_enabled) {
        uint8_t payload[8] = {0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u};
        store_u16_le_early(payload, event_value);
        publish(9u, payload, sizeof(payload));
    }
    return true;
}

bool gomore_primitives_temperature_measurement_begin(
    gomore_primitives_scaled_sample_state *state) {
    if (state == NULL) {
        return false;
    }
    /* Stock 0x0004B6C0 clears exactly the first 14 bytes, preserving the
     * independent capture-mode block beginning at +0x0E. */
    clear_bytes((uint8_t *)state, 14u);
    state->measurement_active = true;
    return true;
}

gomore_primitives_temperature_measurement_result
gomore_primitives_temperature_measurement_step(
    gomore_primitives_scaled_sample_state *state, uint16_t sample) {
    if (state == NULL || state->recent_count > 5u) {
        return GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_INVALID;
    }

    state->attempt_count = (uint8_t)(state->attempt_count + 1u);
    if (state->attempt_count > 30u) {
        return GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_TIMEOUT;
    }
    if (!gomore_primitives_u16_in_30000_50000(sample)) {
        return GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE;
    }
    if (!gomore_primitives_u16_all_within_300(
            state->recent, state->recent_count, sample)) {
        state->recent_count = 0u;
        return GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE;
    }
    if (state->recent_count == 5u) {
        return GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_COMPLETE;
    }
    state->recent[state->recent_count] = sample;
    state->recent_count = (uint8_t)(state->recent_count + 1u);
    return state->recent_count >= 5u
        ? GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_COMPLETE
        : GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE;
}

uint16_t gomore_primitives_stable_trimmed_median(
    const uint16_t *values, size_t count, uint16_t *unscaled) {
    if (unscaled == NULL) {
        return 0u;
    }
    *unscaled = 0u;
    if (count < 12u) {
        return 0u;
    }
    if (values == NULL || count > 50u) {
        return 0u;
    }
    uint16_t sorted[50];
    for (size_t index = 0u; index < count; ++index) {
        sorted[index] = values[index];
    }
    for (size_t pass = 0u; pass + 1u < count; ++pass) {
        for (size_t index = 0u; index + 1u < count - pass; ++index) {
            if (sorted[index] > sorted[index + 1u]) {
                const uint16_t temporary = sorted[index];
                sorted[index] = sorted[index + 1u];
                sorted[index + 1u] = temporary;
            }
        }
    }
    size_t begin = count / 10u;
    size_t end = count - begin;
    if (end <= begin) {
        begin = 0u;
        end = count;
    }
    uint32_t total = 0u;
    for (size_t index = begin; index < end; ++index) {
        total += sorted[index];
    }
    const uint16_t mean = (uint16_t)(total / (uint32_t)(end - begin));
    const uint16_t median = (count & 1u) != 0u
        ? sorted[count / 2u]
        : (uint16_t)(((uint32_t)sorted[count / 2u] +
                      (uint32_t)sorted[count / 2u - 1u]) >> 1u);
    const uint16_t difference = mean < median
        ? (uint16_t)(median - mean) : (uint16_t)(mean - median);
    if (difference > 100u) {
        return 0u;
    }
    *unscaled = (uint16_t)(((uint32_t)mean + (uint32_t)median) >> 1u);
    return (uint16_t)((double)*unscaled * 0x1.999999999999ap-4);
}

bool gomore_primitives_stamp_time_record(
    uint8_t *record, size_t length,
    gomore_primitives_time_fn time_provider,
    gomore_primitives_offset_fn offset_provider,
    gomore_primitives_sync_state_fn sync_provider,
    void *provider_context) {
    if (record == NULL || length < 0x31u || time_provider == NULL ||
            offset_provider == NULL || sync_provider == NULL) {
        return false;
    }
    store_u32_le(&record[0], time_provider(provider_context));
    const uint16_t offset = offset_provider(provider_context);
    record[4] = (uint8_t)(offset & UINT16_C(0xFF));
    record[5] = (uint8_t)(offset >> 8);
    record[0x1Du] = 1u;
    record[0x30u] = sync_provider(provider_context) == 0 ? 1u : 0u;
    return true;
}

uint32_t gomore_primitives_clamp_hysteresis(uint32_t value,
                                            uint32_t baseline) {
    if (value == 0u) {
        return 1u;
    }
    if (value <= baseline + 3u && baseline <= value + 3u) {
        return baseline + 1u;
    }
    return value;
}

uint32_t gomore_primitives_parameter_commit(
    uint8_t *state, size_t length, uint32_t value,
    gomore_primitives_parameter_validate_fn validate,
    void *validate_context) {
    if (state == NULL || length <= 0x20F5u || validate == NULL ||
            !validate(validate_context, value)) {
        return UINT32_C(0x40);
    }
    state[0x20F5u] = (uint8_t)value;
    return 0u;
}

static bool records_any_enabled_bit(const uint8_t *records,
                                    size_t record_bytes, uint8_t mask) {
    if (records == NULL ||
            record_bytes < GOMORE_PRIMITIVES_RECORD_COUNT *
                               GOMORE_PRIMITIVES_RECORD_STRIDE) {
        return false;
    }
    for (size_t index = 0u; index < GOMORE_PRIMITIVES_RECORD_COUNT; ++index) {
        const uint8_t flags =
            records[index * GOMORE_PRIMITIVES_RECORD_STRIDE];
        if ((flags & 1u) != 0u && (flags & mask) != 0u) {
            return true;
        }
    }
    return false;
}

bool gomore_primitives_records_any_bit2(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x04));
}

bool gomore_primitives_records_any_bit4(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x10));
}

bool gomore_primitives_records_any_bit3(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x08));
}

bool gomore_primitives_records_any_bit1(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x02));
}

int32_t gomore_primitives_quantized_argmin(const float *values,
                                           uint32_t begin,
                                           uint32_t end_exclusive) {
    if (values == NULL || end_exclusive < begin ||
            begin > (uint32_t)INT32_MAX) {
        return -1;
    }
    uint32_t result = begin;
    int32_t threshold = (int32_t)values[begin];
    for (uint32_t index = begin; index < end_exclusive; ++index) {
        if (values[index] < (float)threshold) {
            threshold = (int32_t)values[index];
            result = index;
        }
    }
    return (int32_t)result;
}

uint32_t gomore_primitives_max_difference_index(const float *values,
                                                uint32_t begin,
                                                uint32_t end_exclusive) {
    if (values == NULL || begin >= end_exclusive) {
        return UINT32_MAX;
    }
    uint32_t result = begin;
    float largest = values[begin + 1u] - values[begin];
    for (uint32_t index = begin; index < end_exclusive; ++index) {
        const float difference = values[index + 1u] - values[index];
        if (difference > largest) {
            largest = difference;
            result = index & UINT32_C(0xFFFF);
        }
    }
    return result;
}

bool gomore_primitives_median(float *values, size_t count,
                              gomore_primitives_qsort_fn qsort_provider,
                              gomore_primitives_compare_fn compare,
                              float *result) {
    if (values == NULL || count == 0u || qsort_provider == NULL ||
            compare == NULL || result == NULL) {
        return false;
    }
    qsort_provider(values, count, sizeof(*values), compare);
    const size_t middle = count / 2u;
    *result = (count & 1u) != 0u
        ? values[middle]
        : (values[middle - 1u] + values[middle]) * 0.5f;
    return true;
}

bool gomore_primitives_standard_deviation(
    const float *values, size_t count,
    gomore_primitives_float_binary_fn pow_provider,
    gomore_primitives_float_unary_fn sqrt_provider,
    float *result) {
    if (values == NULL || count == 0u || pow_provider == NULL ||
            sqrt_provider == NULL || result == NULL) {
        return false;
    }
    const float mean = gomore_primitives_mean(values, count);
    float sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        sum += pow_provider(values[index] - mean, 2.0f);
    }
    const float variance = count == 1u ? 0.0f : sum / (float)(count - 1u);
    *result = sqrt_provider(variance);
    return true;
}

bool gomore_primitives_logistic_score(
    float scale, float bias, float feature, float coefficient,
    gomore_primitives_float_unary_fn exp_provider, float *result) {
    if (exp_provider == NULL || result == NULL) {
        return false;
    }
    const float exponent = exp_provider((feature - 64.0f) * scale);
    float logistic = 0.0f;
    if (exponent + 1.0f != 0.0f) {
        logistic = 0.15000000596046448f / (exponent + 1.0f);
    }
    *result = logistic + 0.7749999761581421f + bias +
              feature * coefficient;
    return true;
}

bool gomore_primitives_modulo5_record(uint8_t *record, size_t length,
                                      uint8_t secondary,
                                      uint8_t primary) {
    if (record == NULL || length < 0x2Fu || record[0x28u] >= 20u) {
        return false;
    }
    const uint8_t counter = record[0x28u];
    if ((counter % 5u) == 0u) {
        const size_t slot = (size_t)(counter / 5u);
        record[0x29u + slot] = primary == UINT8_C(0xFF) ? 1u : primary;
        record[0x2Du + (slot & 1u)] =
            secondary == UINT8_C(0xFF) ? 1u : secondary;
    }
    record[0x28u] = (uint8_t)((counter + 1u) % 20u);
    return true;
}

static uint16_t load_u16_le(const uint8_t *bytes) {
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}

static void store_u16_le(uint8_t *bytes, uint16_t value) {
    bytes[0] = (uint8_t)(value & UINT16_C(0xFF));
    bytes[1] = (uint8_t)(value >> 8);
}

bool gomore_primitives_compact_25_windows(uint8_t *records,
                                         size_t record_capacity,
                                         uint8_t *record_count,
                                         uint32_t current_window) {
    if (records == NULL || record_count == NULL ||
            (size_t)*record_count > record_capacity) {
        return false;
    }
    if (*record_count == 0u || current_window <= 20u) {
        return true;
    }
    size_t drop = 0u;
    while (drop < (size_t)*record_count &&
            load_u16_le(&records[drop * 16u + 2u]) < 25u) {
        ++drop;
    }
    const size_t retained = (size_t)*record_count - drop;
    for (size_t index = 0u; index < retained; ++index) {
        uint8_t *destination = &records[index * 16u];
        const uint8_t *source = &records[(index + drop) * 16u];
        for (size_t byte = 0u; byte < 16u; ++byte) {
            destination[byte] = source[byte];
        }
        for (size_t field = 0u; field < 3u; ++field) {
            const uint16_t adjusted = (uint16_t)(
                load_u16_le(&destination[field * 2u]) - UINT16_C(25));
            store_u16_le(&destination[field * 2u], adjusted);
        }
    }
    *record_count = (uint8_t)retained;
    return true;
}

bool gomore_primitives_decimated_ring_write(float value, uint8_t ring[90],
                                            uint32_t begin_tick,
                                            uint32_t end_tick) {
    if (ring == NULL || end_tick < begin_tick) {
        return false;
    }
    uint32_t elapsed = end_tick - begin_tick;
    const uint8_t previous = ring[(elapsed / 10u) % 90u];
    if (!gomore_primitives_float_in_encoded_range(value)) {
        value = 0.0f;
    }
    ring[(end_tick / 10u) % 90u] = (uint8_t)value;
    if (begin_tick > 899u) {
        clear_bytes(ring, 90u);
        return true;
    }
    for (elapsed += 10u; elapsed < end_tick; elapsed += 10u) {
        ring[(elapsed / 10u) % 90u] = previous;
    }
    return true;
}

int32_t gomore_primitives_csv4_prefix_compare(
    const uint8_t *pattern, size_t pattern_length,
    const uint8_t *candidate, size_t candidate_length) {
    if ((pattern == NULL && pattern_length != 0u) ||
            (candidate == NULL && candidate_length != 0u)) {
        return -1;
    }
    uint8_t buffer[48];
    clear_bytes(buffer, sizeof(buffer));
    const size_t copied = candidate_length < 48u ? candidate_length : 47u;
    for (size_t index = 0u; index < copied; ++index) {
        buffer[index] = candidate[index];
    }
    buffer[copied] = 0u;

    /* Stock passed the original length to the comma counter after truncating
     * into this 48-byte local.  Lengths above 48 therefore read beyond the
     * stack object.  Count only admitted bytes while retaining its 4-field
     * result for every defined stock input. */
    size_t fields = 1u;
    for (size_t index = 0u; index < copied; ++index) {
        if (buffer[index] == UINT8_C(0x2C)) {
            ++fields;
        }
    }
    if (fields != 4u) {
        return -1;
    }

    size_t token_begin = 0u;
    while (token_begin < copied &&
            buffer[token_begin] == UINT8_C(0x2C)) {
        ++token_begin;
    }
    if (token_begin >= copied || buffer[token_begin] == 0u) {
        return 0;
    }
    size_t token_end = token_begin;
    while (token_end < copied && buffer[token_end] != 0u &&
            buffer[token_end] != UINT8_C(0x2C)) {
        ++token_end;
    }
    for (size_t index = 0u; index < pattern_length; ++index) {
        const uint8_t left = pattern[index];
        const uint8_t right = token_begin + index < token_end
            ? buffer[token_begin + index] : 0u;
        if (left != right || left == 0u) {
            const int32_t difference = (int32_t)left - (int32_t)right;
            const uint8_t low = (uint8_t)((uint32_t)difference & UINT32_C(0xFF));
            return low < UINT8_C(0x80)
                ? (int32_t)low : (int32_t)low - 256;
        }
    }
    return 0;
}

bool gomore_primitives_sleep_engine_open(
    void *state, size_t state_length,
    gomore_primitives_tensor_construct_binding_fn construct_tensor) {
    if (state == NULL || state_length < 0x20F0u ||
            construct_tensor == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    if (bytes[0x3E8u] == 1u) {
        (void)gomore_primitives_clear_flag_1000(bytes, state_length);
    }
    clear_bytes(&bytes[0x55Cu], 0x1B90u);
    const uint16_t dimensions[2] = {1u, 90u};
    const uint32_t tensor_binding = construct_tensor(
        &bytes[0x55Cu], 0x1B90u, 2u, dimensions, 2u);
    store_u32_le(&bytes[0x20ECu], tensor_binding);
    store_u32_le(&bytes[0x554u], 0u);
    store_u32_le(&bytes[0x558u], 0u);
    bytes[0x3E8u] = 1u;
    bytes[0x3E9u] = 0u;
    store_u16_le_early(&bytes[0x3E6u], 0u);
    bytes[0x3EAu] = 0u;
    clear_bytes(&bytes[0x2D6u], 0x110u);
    return true;
}

bool gomore_primitives_shift_negated_filter_history(
    void *state, size_t state_length,
    const float input[25], bool zero_fill,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (state == NULL || state_length < 0x6C0u ||
            (!zero_fill && (input == NULL || apply_filter == NULL))) {
        return false;
    }
    uint8_t *bytes = state;
    float *history = (float *)(void *)&bytes[0x2D8u];
    for (size_t index = 0u; index < 225u; ++index) {
        history[index] = history[index + 25u];
    }
    for (size_t index = 0u; index < 25u; ++index) {
        history[225u + index] = zero_fill ? 0.0f : -input[index];
    }
    if (!zero_fill) {
        apply_filter(state, &history[225u], 25u);
    }
    return true;
}

bool gomore_primitives_log_u32(
    const gomore_primitives_log_config *configuration,
    uint32_t level, uint32_t category,
    const char *format, uint32_t value) {
    if (configuration == NULL || !configuration->enabled ||
            configuration->emit == NULL || level >= 32u || category >= 32u ||
            (configuration->level_mask & (UINT32_C(1) << level)) == 0u ||
            ((uint32_t)configuration->category_mask &
             (UINT32_C(1) << category)) == 0u) {
        return false;
    }
    if (configuration->format_u32 == NULL || format == NULL) {
        return false;
    }
    char message[256];
    clear_bytes((uint8_t *)message, sizeof(message));
    static const char prefix[8] = {'[', 'G', 'o', 'M', 'o', 'R', 'e', ']'};
    for (size_t index = 0u; index < sizeof(prefix); ++index) {
        message[index] = prefix[index];
    }
    const uint32_t formatted = configuration->format_u32(
        &message[8], 248u, format, value);
    message[255] = '\0';
    /* Stock appended CRLF whenever the formatter reported <248 characters,
     * which overflows its 256-byte aggregate buffer for lengths 246/247.
     * Preserve the suffix for every fitting result and keep the local bound. */
    if (formatted <= 245u) {
        const size_t end = 8u + (size_t)formatted;
        message[end] = '\r';
        message[end + 1u] = '\n';
        message[end + 2u] = '\0';
    }
    configuration->emit("%s", message);
    return true;
}

bool gomore_primitives_accelerometer_resample25(
    void *filter_states, size_t filter_state_length,
    const float *const sources[3], size_t source_count,
    int32_t sample_count,
    float *const destinations[3], size_t destination_count,
    uint8_t *failed, uint32_t *status,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger) {
    if (filter_states == NULL || filter_state_length < 0x140u ||
            sources == NULL || source_count < 3u || destinations == NULL ||
            destination_count < 3u || failed == NULL || status == NULL ||
            resample == NULL || apply_filter == NULL) {
        return false;
    }
    for (size_t axis = 0u; axis < 3u; ++axis) {
        if (destinations[axis] == NULL ||
                (sample_count != 0 && sources[axis] == NULL)) {
            return false;
        }
    }
    for (size_t axis = 0u; axis < 3u; ++axis) {
        clear_bytes((uint8_t *)destinations[axis], 25u * sizeof(float));
    }
    *failed = 0u;
    *status = 0u;
    if (sample_count == 0) {
        *status = UINT32_C(0x20);
        *failed = 1u;
    } else {
        uint8_t *states = filter_states;
        for (size_t axis = 0u; axis < 3u; ++axis) {
            (void)gomore_primitives_resample25_and_filter(
                &states[0x50u + axis * 0x50u], sources[axis], sample_count,
                sample_count, destinations[axis], resample, apply_filter);
        }
    }
    (void)gomore_primitives_log_u32(
        logger, 2u, 2u, "[SnP][ACC]status:%u\r\n", *status);
    return true;
}

bool gomore_primitives_ppg_resample25(
    void *filter_states, size_t filter_state_length,
    const float *const *sources, size_t source_count,
    int32_t channel_count, int32_t sample_count,
    float output[25], uint8_t *failed, uint32_t *status,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger) {
    if (filter_states == NULL || filter_state_length < 0x50u ||
            output == NULL || failed == NULL || status == NULL ||
            resample == NULL || apply_filter == NULL ||
            (channel_count > 0 &&
             (sources == NULL || source_count == 0u || sources[0] == NULL))) {
        return false;
    }
    clear_bytes((uint8_t *)output, 25u * sizeof(float));
    *failed = 0u;
    *status = 0u;
    if (sample_count == 0 || channel_count == 0) {
        *status = UINT32_C(0x40);
        *failed = 1u;
    } else {
        if (channel_count > 0) {
            float filtered[25];
            clear_bytes((uint8_t *)filtered, sizeof(filtered));
            gomore_primitives_resample25_and_filter_tail(
                filter_states, sources[0], sample_count, sample_count,
                filtered, resample, apply_filter);
            for (size_t index = 0u; index < 25u; ++index) {
                output[index] += filtered[index];
            }
        }
        const float reciprocal = 1.0f / (float)channel_count;
        for (size_t index = 0u; index < 25u; ++index) {
            output[index] *= reciprocal;
        }
    }
    (void)gomore_primitives_log_u32(
        logger, 2u, 2u, "[SnP][Ppg]status:%u\r\n", *status);
    return true;
}
