#include "native_nadt_public_view.h"
#include <string.h>

static uint16_t read_half(const volatile uint8_t *source, size_t offset)
{
    return (uint16_t)((uint16_t)source[offset] |
        ((uint16_t)source[offset + 1u] << 8u));
}

static uint32_t read_word(const volatile uint8_t *source, size_t offset)
{
    return (uint32_t)read_half(source, offset) |
        ((uint32_t)read_half(source, offset + 2u) << 16u);
}

static int16_t read_signed_half(const volatile uint8_t *source, size_t offset)
{
    const uint16_t bits = read_half(source, offset);
    int16_t value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static int32_t read_signed_word(const volatile uint8_t *source, size_t offset)
{
    const uint32_t bits = read_word(source, offset);
    int32_t value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static void write_half(volatile uint8_t *destination, size_t offset,
    uint16_t value)
{
    destination[offset] = (uint8_t)value;
    destination[offset + 1u] = (uint8_t)(value >> 8u);
}

static void write_word(volatile uint8_t *destination, size_t offset,
    uint32_t value)
{
    write_half(destination, offset, (uint16_t)value);
    write_half(destination, offset + 2u, (uint16_t)(value >> 16u));
}

bool r1_goodix_nadt_public_sample_view(
    const goodix_nadt_input_rawdata *raw,
    goodix_primitives_nadt_sample_preparation_input *view)
{
    if (raw == NULL || view == NULL || raw->total_ch_num == 0u ||
            raw->total_ch_num > PPG_CHANNEL_NUM ||
            raw->ppg_rawdata == NULL || raw->ch_agc_gain == NULL ||
            raw->ch_agc_drv == NULL) {
        return false;
    }
    const goodix_nadt_input_unique *const unique =
        (const goodix_nadt_input_unique *)raw->pst_module_unique;
    const bool calibrated = raw->data_type != 0u;
    if (calibrated && (unique == NULL || unique->ch_ipd == NULL)) {
        return false;
    }
    const size_t lane_count = (size_t)raw->total_ch_num * 3u;
    *view = (goodix_primitives_nadt_sample_preparation_input){
        .direct_values = raw->ppg_rawdata,
        .prepared_values = raw->ppg_rawdata,
        .direct_value_count = lane_count,
        .calibration_values = calibrated ? unique->ch_ipd : NULL,
        .calibration_value_count = calibrated ? lane_count : 0u,
        .scale_codes = raw->ch_agc_gain,
        .scale_code_count = lane_count,
        .sequence = raw->ch_agc_drv[0],
        .lane_stride = raw->total_ch_num,
        .conversion_mode = raw->chip_type,
        .calibrated = calibrated,
    };
    return true;
}

bool r1_goodix_nadt_window_configuration_load(
    const uint8_t tail[68], const volatile uint8_t configuration[120],
    goodix_primitives_nadt_window_configuration *view)
{
    if (tail == NULL || configuration == NULL || view == NULL ||
            tail[64] > GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT) {
        return false;
    }
    memcpy(view->window_metrics, tail + 16u, sizeof(view->window_metrics));
    memcpy(view->window_maxima, tail + 32u, sizeof(view->window_maxima));
    memcpy(view->window_minima, tail + 48u, sizeof(view->window_minima));
    view->window_count = tail[64];
    view->alternate_classifier_level = configuration[2];
    view->elapsed_window_limit = read_half(configuration, 4u);
    view->minimum_nonzero_tail_samples = configuration[6];
    view->base_transition_windows = configuration[7];
    view->axis_ratio_streak_limit = configuration[8];
    view->metric_threshold = (int32_t)read_word(configuration, 0x14u);
    view->spread_threshold = (int32_t)read_word(configuration, 0x18u);
    return true;
}

void r1_goodix_nadt_window_configuration_store(
    uint8_t tail[68],
    const goodix_primitives_nadt_window_configuration *view)
{
    if (tail == NULL || view == NULL) return;
    memcpy(tail + 16u, view->window_metrics, sizeof(view->window_metrics));
    memcpy(tail + 32u, view->window_maxima, sizeof(view->window_maxima));
    memcpy(tail + 48u, view->window_minima, sizeof(view->window_minima));
    tail[64] = view->window_count;
}

bool r1_goodix_nadt_stream_state_load(
    const volatile uint8_t native_state[92], const uint8_t tail[68],
    goodix_primitives_nadt_stream_state *view)
{
    if (native_state == NULL || tail == NULL || view == NULL) return false;
    const uint16_t primary_count = read_half(native_state, 32u);
    const uint16_t secondary_count = read_half(native_state, 34u);
    if (primary_count > GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES ||
            secondary_count > 200u || native_state[13] > 3u) return false;
    memset(view, 0, sizeof(*view));
    view->initialized = native_state[0] == 0xbfu;
    view->status = native_state[3];
    view->cadence_counter = read_half(native_state, 30u);
    view->batch_count = read_word(native_state, 40u);
    view->batch_sample_count = native_state[11];
    view->low_primary_count = native_state[12];
    view->activity_lane = native_state[13];
    view->primary_average = read_signed_word(native_state, 56u);
    view->secondary_average = read_signed_word(native_state, 64u);
    view->primary_history_count = primary_count;
    view->secondary_history_count = secondary_count;
    memcpy(view->activity_mean, tail, sizeof(view->activity_mean));
    memcpy(view->activity_squared_deviation_sum, tail + 16u,
        sizeof(view->activity_squared_deviation_sum));
    memcpy(view->activity_maximum, tail + 32u,
        sizeof(view->activity_maximum));
    memcpy(view->activity_minimum, tail + 48u,
        sizeof(view->activity_minimum));
    view->result_flag = native_state[5] != 0u;

    goodix_primitives_nadt_window_state *const classifier =
        &view->classifier;
    classifier->current_result = read_signed_word(native_state, 44u);
    classifier->classification_latched = native_state[1] != 0u;
    classifier->alternate_probe_enabled = native_state[2] != 0u;
    classifier->stationary_latch = native_state[4];
    for (size_t index = 0u; index < 4u; ++index) {
        classifier->transient_counters[index] = native_state[5u + index];
        classifier->trigger_windows[index] = native_state[20u + index];
    }
    classifier->quality = native_state[9];
    classifier->classification_mode = native_state[10];
    classifier->rate = native_state[16];
    classifier->axis_ratio_streak = native_state[17];
    classifier->evidence_streak = native_state[18];
    classifier->fallback_streak = native_state[19];
    classifier->profile_release_streak = native_state[24];
    classifier->profile = native_state[25];
    classifier->classifier_suppressed = native_state[26] != 0u;
    classifier->elapsed_windows = read_half(native_state, 28u);
    classifier->range_cursor = (int16_t)secondary_count;
    classifier->axis_ratio_outside_band_windows =
        read_half(native_state, 38u);
    classifier->inactive_windows = read_signed_word(native_state, 72u);
    classifier->long_window_score = read_signed_word(native_state, 76u);
    classifier->energy_metric = read_signed_word(native_state, 80u);
    classifier->profile_counter = read_signed_word(native_state, 84u);
    return true;
}

void r1_goodix_nadt_stream_state_store(
    volatile uint8_t native_state[92], uint8_t tail[68],
    const goodix_primitives_nadt_stream_state *view)
{
    if (native_state == NULL || tail == NULL || view == NULL) return;
    native_state[3] = view->status;
    write_half(native_state, 30u, view->cadence_counter);
    write_word(native_state, 40u, view->batch_count);
    native_state[11] = view->batch_sample_count;
    native_state[12] = view->low_primary_count;
    native_state[13] = view->activity_lane;
    write_word(native_state, 56u, (uint32_t)view->primary_average);
    write_word(native_state, 64u, (uint32_t)view->secondary_average);
    write_half(native_state, 32u, (uint16_t)view->primary_history_count);
    write_half(native_state, 34u, (uint16_t)view->secondary_history_count);
    memcpy(tail, view->activity_mean, sizeof(view->activity_mean));
    memcpy(tail + 16u, view->activity_squared_deviation_sum,
        sizeof(view->activity_squared_deviation_sum));
    memcpy(tail + 32u, view->activity_maximum,
        sizeof(view->activity_maximum));
    memcpy(tail + 48u, view->activity_minimum,
        sizeof(view->activity_minimum));

    const goodix_primitives_nadt_window_state *const classifier =
        &view->classifier;
    write_word(native_state, 44u, (uint32_t)classifier->current_result);
    /* Byte +1 also carries auxiliary mode 5 and alternate mode 4. The
     * classifier callbacks own writes to it; the stream view must preserve
     * their last writer's exact mode. */
    /* The stream reads this byte as a flag, but does not write it. Preserve
     * its original byte value, including noncanonical nonzero values. */
    native_state[4] = classifier->stationary_latch;
    for (size_t index = 0u; index < 4u; ++index) {
        native_state[5u + index] = classifier->transient_counters[index];
        native_state[20u + index] = classifier->trigger_windows[index];
    }
    native_state[9] = classifier->quality;
    native_state[10] = classifier->classification_mode;
    native_state[16] = classifier->rate;
    native_state[17] = classifier->axis_ratio_streak;
    native_state[18] = classifier->evidence_streak;
    native_state[19] = classifier->fallback_streak;
    native_state[24] = classifier->profile_release_streak;
    native_state[25] = classifier->profile;
    native_state[26] = classifier->classifier_suppressed ? 1u : 0u;
    write_half(native_state, 28u, classifier->elapsed_windows);
    write_half(native_state, 38u,
        classifier->axis_ratio_outside_band_windows);
    write_word(native_state, 72u, (uint32_t)classifier->inactive_windows);
    write_word(native_state, 76u, (uint32_t)classifier->long_window_score);
    write_word(native_state, 80u, (uint32_t)classifier->energy_metric);
    write_word(native_state, 84u, (uint32_t)classifier->profile_counter);
}

void r1_goodix_nadt_preparation_state_load(
    const volatile uint8_t native_state[92],
    goodix_primitives_nadt_sample_preparation_state *view)
{
    if (native_state == NULL || view == NULL) return;
    view->previous_sequence = read_word(native_state, 48u);
    view->previous_scale_code = read_word(native_state, 52u);
}

void r1_goodix_nadt_preparation_state_store(
    volatile uint8_t native_state[92],
    const goodix_primitives_nadt_sample_preparation_state *view)
{
    if (native_state == NULL || view == NULL) return;
    write_word(native_state, 48u, view->previous_sequence);
    write_word(native_state, 52u, view->previous_scale_code);
}

bool r1_goodix_nadt_auxiliary_configuration_load(
    const volatile uint8_t configuration[120],
    goodix_primitives_nadt_auxiliary_configuration *view)
{
    if (configuration == NULL || view == NULL) return false;
    *view = (goodix_primitives_nadt_auxiliary_configuration){
        .enabled = configuration[0x67u] != 0u,
        .range_threshold = read_signed_half(configuration, 0x68u),
        .deviation_threshold = read_signed_half(configuration, 0x6au),
        .required_extrema_count = configuration[0x6cu],
        .required_consecutive_windows = configuration[7u],
    };
    return true;
}

bool r1_goodix_nadt_alternate_configuration_load(
    const volatile uint8_t configuration[120],
    goodix_primitives_nadt_alternate_configuration *view)
{
    if (configuration == NULL || view == NULL) return false;
    *view = (goodix_primitives_nadt_alternate_configuration){
        .enabled = configuration[0x6du] != 0u,
        .sample_gate_limit = read_half(configuration, 4u),
        .minimum_range = read_signed_half(configuration, 0x6eu),
        .minimum_interval = read_half(configuration, 0x70u),
        .maximum_interval_spread = read_half(configuration, 0x72u),
        .minimum_quality = read_half(configuration, 0x74u),
        .required_consecutive_windows = configuration[7u],
    };
    return true;
}

bool r1_goodix_nadt_primary_configuration_load(
    const uint8_t tail[68], const volatile uint8_t configuration[120],
    const float *boundary_coefficients, size_t boundary_coefficient_count,
    goodix_primitives_nadt_primary_configuration *view)
{
    if (tail == NULL || configuration == NULL || view == NULL ||
            boundary_coefficients == NULL ||
            boundary_coefficient_count <
                GOODIX_PRIMITIVES_NADT_PRIMARY_BOUNDARY_COEFFICIENTS) {
        return false;
    }
    *view = (goodix_primitives_nadt_primary_configuration){0};
    memcpy(view->activity_maxima, tail + 32u,
        sizeof(view->activity_maxima));
    memcpy(view->activity_minima, tail + 48u,
        sizeof(view->activity_minima));
    view->enabled = configuration[0x24u] != 0u;
    view->classifier_level = configuration[2u];
    view->base_transition_windows = configuration[7u];
    view->stable_hold_windows = configuration[8u];
    view->trigger_energy_threshold = read_signed_word(configuration, 0x14u);
    view->activity_span_threshold = read_signed_word(configuration, 0x28u);
    view->cadence_scale = read_signed_word(configuration, 0x2cu);
    view->residual_near_zero_threshold =
        read_signed_word(configuration, 0x30u);
    view->minimum_near_zero_samples = read_half(configuration, 0x34u);
    view->minimum_near_zero_run = read_half(configuration, 0x36u);
    view->minimum_extrema_amplitude =
        read_signed_word(configuration, 0x38u);
    view->minimum_periodic_rate = read_half(configuration, 0x3cu);
    view->maximum_periodic_rate = read_half(configuration, 0x3eu);
    view->maximum_interval_variation =
        read_signed_word(configuration, 0x40u);
    view->strong_periodic_variation =
        read_signed_word(configuration, 0x44u);
    view->quality_gate = configuration[0x48u];
    view->mode_zero_activity_threshold = read_half(configuration, 0x4au);
    view->mode_one_residual_threshold = read_half(configuration, 0x4cu);
    view->quiet_quarter_range_threshold = read_half(configuration, 0x4eu);
    view->alternate_residual_threshold = read_half(configuration, 0x50u);
    view->trend_gate_enabled = configuration[0x52u] != 0u;
    view->trend_count_threshold = read_half(configuration, 0x54u);
    view->trend_percent_threshold = read_half(configuration, 0x56u);
    view->filtered_range_lower_threshold =
        read_signed_word(configuration, 0x58u);
    view->filtered_range_upper_threshold =
        read_signed_word(configuration, 0x5cu);
    view->residual_range_threshold = read_half(configuration, 0x60u);
    view->mode_zero_residual_threshold = read_half(configuration, 0x62u);
    view->raw_residual_threshold = read_half(configuration, 0x64u);
    view->deviation_ratio_threshold = configuration[0x66u];
    view->filter_boundary_flags = 3u;
    view->filter_boundary_coefficients = boundary_coefficients;
    view->filter_boundary_coefficient_count = boundary_coefficient_count;
    return true;
}

bool r1_goodix_nadt_auxiliary_state_load(
    const volatile uint8_t native_state[92],
    goodix_primitives_nadt_auxiliary_state *view)
{
    if (native_state == NULL || view == NULL) return false;
    *view = (goodix_primitives_nadt_auxiliary_state){
        .current_result = read_signed_word(native_state, 44u),
        .mode = native_state[1u],
        .consecutive_matches = native_state[14u],
        .processing = native_state[25u] == 1u,
    };
    return true;
}

void r1_goodix_nadt_auxiliary_state_store(
    volatile uint8_t native_state[92],
    const goodix_primitives_nadt_auxiliary_state *view)
{
    if (native_state == NULL || view == NULL) return;
    native_state[1u] = view->mode;
    native_state[14u] = view->consecutive_matches;
    /* The stock auxiliary root returns a proposed classification; the
     * caller owns committing the shared result word. */
}

bool r1_goodix_nadt_alternate_state_load(
    const volatile uint8_t native_state[92],
    goodix_primitives_nadt_alternate_state *view)
{
    if (native_state == NULL || view == NULL) return false;
    *view = (goodix_primitives_nadt_alternate_state){
        .current_result = read_signed_word(native_state, 44u),
        .mode = native_state[1u],
        .consecutive_matches = native_state[15u],
        .processing = native_state[25u] == 1u,
        .sample_gate = read_half(native_state, 28u),
        .autocorrelation = {
            .previous_output = read_signed_half(native_state, 36u),
            .previous_correlation = read_signed_word(native_state, 68u),
        },
    };
    return true;
}

void r1_goodix_nadt_alternate_state_store(
    volatile uint8_t native_state[92],
    const goodix_primitives_nadt_alternate_state *view)
{
    if (native_state == NULL || view == NULL) return;
    native_state[1u] = view->mode;
    native_state[15u] = view->consecutive_matches;
    write_half(native_state, 36u,
        (uint16_t)view->autocorrelation.previous_output);
    write_word(native_state, 68u,
        (uint32_t)view->autocorrelation.previous_correlation);
    /* Sample gate is read-only here; the stream owns its counter. */
}
