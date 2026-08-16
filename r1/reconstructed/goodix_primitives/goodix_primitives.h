#ifndef OPENR1_RECONSTRUCTED_GOODIX_PRIMITIVES_H
#define OPENR1_RECONSTRUCTED_GOODIX_PRIMITIVES_H

/*
 * Owner-authorized clean-room reconstruction of the Goodix-candidate
 * functions below from the SHA-pinned R1 application image.  This is not
 * Goodix source.  Exact address/extent and test correlation lives in
 * docs/correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "quantized_runtime/quantized_runtime.h"

#define GOODIX_PRIMITIVES_STATE_COUNT 7u
#define GOODIX_PRIMITIVES_RECORD_BYTES 35u
#define GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT 11u
#define GOODIX_PRIMITIVES_HRV_OK UINT32_C(0)
#define GOODIX_PRIMITIVES_HRV_INVALID UINT32_C(0x10000001)
#define GOODIX_PRIMITIVES_HRV_ALREADY_INITIALIZED UINT32_C(0x10000002)
#define GOODIX_PRIMITIVES_HRV_ALLOCATION_FAILED UINT32_C(0x10000004)
#define GOODIX_PRIMITIVES_HR_OK UINT32_C(0)
#define GOODIX_PRIMITIVES_HR_INVALID UINT32_C(1)
#define GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES 180u
#define GOODIX_PRIMITIVES_SPO2_PACKED_BANK_COUNT 3u
#define GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT 7u
#define GOODIX_PRIMITIVES_SPO2_PACKED_PREFIX_VALUES 720u
#define GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES 1260u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS 4u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS 4u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_CHANNELS 5u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES 60u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_STRIDE 3u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_VALUES 178u
#define GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES 128u
#define GOODIX_PRIMITIVES_SPO2_PROCESS_CHANNEL_GROUPS 3u
#define GOODIX_PRIMITIVES_SPO2_PROCESS_MAX_CHANNELS 4u
#define GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_ROWS 4u
#define GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS 99u
#define GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_VALUES 396u
#define GOODIX_PRIMITIVES_SPO2_PROCESS_OUTPUT_WORDS 5u
#define GOODIX_PRIMITIVES_FFT_COMPLEX_VALUES 256u
#define GOODIX_PRIMITIVES_FFT_REAL_VALUES 256u
#define GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES 129u
#define GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES 257u
#define GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES 125u
#define GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES 53u
#define GOODIX_PRIMITIVES_NADT_SPECTRAL_PEAK_CAPACITY 5u
#define GOODIX_PRIMITIVES_NADT_SPECTRAL_OUTPUT_CAPACITY 3u
#define GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY 3u
#define GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES 125u
#define GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_ROWS 62u
#define GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_CAPACITY 62u
#define GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE 63u
#define GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_CORRELATION_VALUES 249u
#define GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_MASK_BYTES 969u
#define GOODIX_PRIMITIVES_NADT_AUXILIARY_WINDOW_VALUES 50u
#define GOODIX_PRIMITIVES_NADT_AUXILIARY_EXTREMA_CAPACITY 25u
#define GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT 4u
#define GOODIX_PRIMITIVES_NADT_WINDOW_RANGE_VALUES 25u
#define GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES 100u
#define GOODIX_PRIMITIVES_NADT_PRIMARY_FIR_SCRATCH_VALUES 122u
#define GOODIX_PRIMITIVES_NADT_PRIMARY_BOUNDARY_COEFFICIENTS 253u
#define GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES 125u
#define GOODIX_PRIMITIVES_NADT_SIGNAL_DIFFERENCE_VALUES 124u
#define GOODIX_PRIMITIVES_NADT_PREPROCESS_RECORD_BYTES 24u
#define GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_BYTES 44u
#define GOODIX_PRIMITIVES_NADT_PREPROCESS_STAGE_COUNT 14u
#define GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT 200u
#define GOODIX_PRIMITIVES_NADT_ALTERNATE_EXTREMA_CAPACITY 100u
#define GOODIX_PRIMITIVES_NADT_ALTERNATE_INTERVAL_CAPACITY 199u
#define GOODIX_PRIMITIVES_HR_EXTREMA_SPLINE_POINTS 41u
#define GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT 2u
#define GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT 7u
#define GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES 125u
#define GOODIX_PRIMITIVES_NADT_GRAPH_PRIMARY_VALUES 120u
#define GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_VALUES 3u
#define GOODIX_PRIMITIVES_NADT_GRAPH_MERGED_VALUES 123u
#define GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK 248u
#define GOODIX_PRIMITIVES_NADT_GRAPH_STATE_BANK 496u
#define GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_BANK 558u
#define GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT 19u
#define GOODIX_PRIMITIVES_NADT_SUBGRAPH_WORKSPACE_FLOATS 496u
#define GOODIX_PRIMITIVES_NADT_SUBGRAPH_OUTPUT_VALUES 120u
#define GOODIX_PRIMITIVES_NADT_INITIALIZE_OK INT32_C(0)
#define GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID INT32_C(3)

typedef void (*goodix_primitives_state_handler_fn)(void *record);
typedef int32_t (*goodix_primitives_device_initialize_fn)(uint16_t device_id);
typedef void (*goodix_primitives_hook_fn)(void);
typedef void *(*goodix_primitives_allocate_fn)(void *context, size_t bytes);
typedef void (*goodix_primitives_release_fn)(void *context, void *allocation);
typedef uintptr_t (*goodix_primitives_hr_graph_build_fn)(
    void *context, const void *primary_binding, uintptr_t encoded_size,
    const void *secondary_binding);
typedef void (*goodix_primitives_hr_graph_release_fn)(
    void *context, uintptr_t graph);
typedef float (*goodix_primitives_float_unary_fn)(float value);
typedef double (*goodix_primitives_double_unary_fn)(double value);
typedef double (*goodix_primitives_double_binary_fn)(double first,
                                                      double second);
typedef int32_t (*goodix_primitives_i32_unary_fn)(int32_t value);
typedef uint16_t (*goodix_primitives_u32_to_u16_fn)(uint32_t value);
typedef int32_t (*goodix_primitives_status_fn)(void);
typedef int32_t (*goodix_primitives_indexed_operation_fn)(
    void *record, uintptr_t first, uintptr_t second, uintptr_t third,
    uintptr_t fourth, uintptr_t fifth);
typedef int32_t (*goodix_primitives_seven_word_operation_fn)(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth, uintptr_t sixth, uintptr_t seventh);
typedef int32_t (*goodix_primitives_five_word_operation_fn)(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth);
typedef void (*goodix_primitives_float_transform_fn)(
    float *values, size_t input_count, size_t transform_count);
typedef bool (*goodix_primitives_nadt_harmonic_candidate_fn)(
    void *context, float bin_width, const int32_t *peak_indices,
    const float *peak_values, size_t peak_count,
    int32_t *candidate_indices, uint8_t *candidate_flags,
    size_t candidate_capacity);

typedef struct {
    int32_t selected_indices[GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY];
    uint8_t selected_flags[GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY];
    int32_t candidate_indices[GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY];
    float candidate_values[GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY];
    uint8_t candidate_flags[GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY];
} goodix_primitives_nadt_harmonic_workspace;

typedef struct {
    goodix_primitives_nadt_harmonic_workspace *workspace;
    goodix_primitives_float_unary_fn square_root;
} goodix_primitives_nadt_harmonic_selector_context;
typedef void (*goodix_primitives_payload_send_fn)(
    uint8_t selector, const uint8_t *payload, uint32_t payload_length,
    uint32_t first, uint32_t second, void *context);
typedef struct {
    float *values;
    uint32_t count;
    uint32_t capacity;
} goodix_primitives_float_buffer;

typedef struct {
    float *values;
    size_t count;
} goodix_primitives_float_span;

typedef struct {
    const float *primary_values;
    size_t primary_count;
    const float *secondary_values;
    size_t secondary_count;
} goodix_primitives_nadt_dual_window_source;

typedef struct {
    float autocorrelation[GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES];
    float correlation[
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_CORRELATION_VALUES];
    uint8_t peak_mask[GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_MASK_BYTES];
    int16_t row_scores[GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_ROWS];
    int16_t column_counts[GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES];
    int16_t peak_index_scratch[
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_CAPACITY];
    uint16_t peak_indices[
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE];
    float peak_values[GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE];
    int32_t selected_positions[
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE];
    int32_t position_differences[
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_CAPACITY];
    uint16_t primary_packed[GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES];
} goodix_primitives_nadt_dual_window_workspace;

typedef struct {
    float primary_dispersion;
    float secondary_dispersion;
    float correlation;
    int32_t primary_rate;
    int32_t secondary_rate;
    float primary_quality;
    float secondary_quality;
} goodix_primitives_nadt_dual_window_result;

typedef struct {
    int32_t high_variation_windows;
    int32_t low_variation_windows;
    uint8_t hold_windows;
    float rolling_mean;
    float probability;
    goodix_primitives_float_buffer rate_history;
    int8_t mode;
} goodix_primitives_nadt_signal_confidence_state;

typedef struct {
    float differences[GOODIX_PRIMITIVES_NADT_SIGNAL_DIFFERENCE_VALUES];
} goodix_primitives_nadt_signal_confidence_workspace;

typedef struct {
    int32_t selected_rate;
    float selected_quality;
    float interval_deviation;
    bool rate_appended;
} goodix_primitives_nadt_signal_confidence_diagnostics;

typedef struct {
    uint8_t rate_threshold;
    uint8_t initial_sample;
    uint8_t override_sample;
    uint8_t flags;
} goodix_primitives_nadt_output_selection_configuration;

typedef struct {
    goodix_primitives_float_buffer rate_history;
    uint8_t signal_present;
    uint8_t persistence;
    uint8_t transition_state;
    uint8_t retained_rate;
    float gate_value;
    float phase_value;
} goodix_primitives_nadt_output_selection_state;

typedef enum {
    GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE = 0,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_BATCH_ACCUMULATE = 1,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_FAILURE_ENCODE = 2,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_ACCUMULATE = 3,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_SPECTRAL_PREPARE = 4,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_PRIMARY_PEAK_UPDATE = 5,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_DISPATCH = 6,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_QUALITY_UPDATE = 7,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_TRANSITION_UPDATE = 8,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE = 9,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_QUALITY = 10,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_SELECT = 11,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_SIGNAL_CONFIDENCE = 12,
    GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_BUILD = 13,
} goodix_primitives_nadt_preprocess_stage;

typedef struct {
    bool initialized;
    uint32_t process_count;
    uint32_t frame_count;
    uint32_t batch_index;
    uint32_t lane_count;
    bool adjustment_enabled;
    uint32_t summary_metric_threshold;
} goodix_primitives_nadt_preprocess_state;

typedef struct {
    uint8_t *assembled_records;
    size_t assembled_record_bytes;
    uint8_t *summaries;
    size_t summary_bytes;
    float *inference_values;
    size_t inference_capacity;
    float *adjusted_values;
    size_t adjusted_capacity;
    float *selected_rates;
    size_t selected_rate_capacity;
    uint8_t *selected_kinds;
    size_t selected_kind_capacity;
    float summary_metric;
} goodix_primitives_nadt_preprocess_workspace;

typedef struct {
    const void *source;
    uint32_t *output_words;
    size_t output_word_count;
    goodix_primitives_nadt_preprocess_state *state;
    goodix_primitives_nadt_preprocess_workspace *workspace;
} goodix_primitives_nadt_preprocess_frame;

typedef int32_t (*goodix_primitives_nadt_preprocess_stage_fn)(
    void *context, goodix_primitives_nadt_preprocess_stage stage,
    goodix_primitives_nadt_preprocess_frame *frame);

typedef struct {
    goodix_primitives_nadt_preprocess_stage_fn execute;
    void *context;
    const int32_t *quartic_coefficients;
    size_t quartic_coefficient_count;
} goodix_primitives_nadt_preprocess_plan;

typedef struct {
    bool enabled;
    int16_t range_threshold;
    int16_t deviation_threshold;
    uint8_t required_extrema_count;
    uint8_t required_consecutive_windows;
} goodix_primitives_nadt_auxiliary_configuration;

typedef struct {
    uint32_t current_result;
    uint8_t mode;
    uint8_t consecutive_matches;
    bool processing;
} goodix_primitives_nadt_auxiliary_state;

typedef struct {
    int16_t range;
    uint8_t maximum_count;
} goodix_primitives_nadt_auxiliary_diagnostics;

typedef struct {
    int16_t maximum_indices[
        GOODIX_PRIMITIVES_NADT_AUXILIARY_EXTREMA_CAPACITY];
    int16_t minimum_indices[
        GOODIX_PRIMITIVES_NADT_AUXILIARY_EXTREMA_CAPACITY];
} goodix_primitives_nadt_auxiliary_workspace;

typedef struct {
    float window_metrics[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT];
    int32_t window_maxima[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT];
    int32_t window_minima[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT];
    uint8_t window_count;
    uint8_t alternate_classifier_level;
    uint16_t elapsed_window_limit;
    uint8_t minimum_nonzero_tail_samples;
    uint8_t base_transition_windows;
    uint8_t axis_ratio_streak_limit;
    int32_t metric_threshold;
    int32_t spread_threshold;
} goodix_primitives_nadt_window_configuration;

typedef struct {
    const void *primary_source;
    const void *secondary_source;
    const int16_t *tail_samples;
    size_t tail_sample_count;
    const int16_t *range_samples;
    size_t range_sample_count;
    int32_t sample_count;
    int32_t axis_x;
    int32_t axis_y;
    int32_t axis_z;
} goodix_primitives_nadt_window_input;

typedef struct {
    int32_t current_result;
    bool classification_latched;
    bool alternate_probe_enabled;
    uint8_t stationary_latch;
    uint8_t transient_counters[4];
    uint8_t quality;
    uint8_t classification_mode;
    uint8_t rate;
    uint8_t axis_ratio_streak;
    uint8_t evidence_streak;
    uint8_t fallback_streak;
    uint8_t trigger_windows[4];
    uint8_t profile_release_streak;
    uint8_t profile;
    bool classifier_suppressed;
    uint16_t elapsed_windows;
    int16_t range_cursor;
    uint16_t axis_ratio_outside_band_windows;
    int32_t inactive_windows;
    int32_t long_window_score;
    int32_t energy_metric;
    int32_t profile_counter;
} goodix_primitives_nadt_window_state;

typedef struct {
    bool high_variation;
    uint8_t primary_classification;
    uint8_t auxiliary_classification;
    uint8_t alternate_classification;
    int32_t energy_metric;
} goodix_primitives_nadt_window_diagnostics;

typedef uint8_t (*goodix_primitives_nadt_primary_window_classifier_fn)(
    void *context, const void *primary_source,
    const void *secondary_source, int32_t sample_count);
typedef int32_t (*goodix_primitives_nadt_counter_classifier_fn)(
    void *context, uint16_t counter);
typedef int32_t (*goodix_primitives_nadt_alternate_classifier_fn)(
    void *context);

typedef struct {
    goodix_primitives_nadt_primary_window_classifier_fn classify_primary;
    void *primary_context;
    goodix_primitives_nadt_counter_classifier_fn classify_auxiliary;
    void *auxiliary_context;
    goodix_primitives_nadt_alternate_classifier_fn classify_alternate;
    void *alternate_context;
    goodix_primitives_double_unary_fn square_root;
} goodix_primitives_nadt_window_plan;

typedef struct {
    int32_t activity_maxima[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT];
    int32_t activity_minima[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT];
    bool enabled;
    uint8_t classifier_level;
    uint8_t base_transition_windows;
    uint8_t stable_hold_windows;
    int32_t trigger_energy_threshold;
    int32_t activity_span_threshold;
    int32_t cadence_scale;
    int32_t residual_near_zero_threshold;
    uint16_t minimum_near_zero_samples;
    uint16_t minimum_near_zero_run;
    int32_t minimum_extrema_amplitude;
    uint16_t minimum_periodic_rate;
    uint16_t maximum_periodic_rate;
    int32_t maximum_interval_variation;
    int32_t strong_periodic_variation;
    uint8_t quality_gate;
    uint16_t mode_zero_activity_threshold;
    uint16_t mode_one_residual_threshold;
    uint16_t quiet_quarter_range_threshold;
    uint16_t alternate_residual_threshold;
    bool trend_gate_enabled;
    uint16_t trend_count_threshold;
    uint16_t trend_percent_threshold;
    int32_t filtered_range_lower_threshold;
    int32_t filtered_range_upper_threshold;
    uint16_t residual_range_threshold;
    uint16_t mode_zero_residual_threshold;
    uint16_t raw_residual_threshold;
    uint8_t deviation_ratio_threshold;
    uint32_t filter_boundary_flags;
    const float *filter_boundary_coefficients;
    size_t filter_boundary_coefficient_count;
} goodix_primitives_nadt_primary_configuration;

typedef struct {
    int32_t filtered[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int32_t filter_scratch[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int32_t fir_scratch[GOODIX_PRIMITIVES_NADT_PRIMARY_FIR_SCRATCH_VALUES];
    int32_t residual[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int16_t autocorrelation[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int16_t extrema_indices[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int16_t transition_indices[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES / 2u];
    int32_t extrema_amplitudes[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES - 1u];
    int32_t phase_gaps[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES - 1u];
} goodix_primitives_nadt_primary_workspace;

typedef struct {
    uint32_t transition_count;
    int32_t normalized_residual_range;
    int16_t positive_difference_percent;
    int32_t filtered_range;
    int32_t periodic_rate;
    int32_t interval_variation;
    bool periodic_candidate;
    bool strong_periodic;
    uint8_t input_quality;
    uint8_t output_quality;
    uint16_t near_zero_samples;
    uint16_t longest_near_zero_run;
    int32_t quarter_ranges[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT];
} goodix_primitives_nadt_primary_diagnostics;

typedef struct {
    float x;
    float y;
} goodix_primitives_point2f;

typedef struct {
    float x[4];
} goodix_primitives_hr_extrema_curve;

typedef struct {
    int32_t direction_state;
    float trough_position;
    float trough_value;
    uint32_t pair_ready;
    float peak_position;
    float peak_value;
    float rise_amplitude;
    float fall_amplitude;
    float rise_span;
    float fall_span;
    uint32_t fall_complete;
    int32_t sample_index;
} goodix_primitives_hr_extrema_tracker;

typedef struct {
    goodix_primitives_point2f
        spline[GOODIX_PRIMITIVES_HR_EXTREMA_SPLINE_POINTS];
} goodix_primitives_hr_extrema_workspace;

typedef struct {
    uint32_t baseline;
    uint32_t elapsed_a;
    uint32_t elapsed_b;
    const uint32_t *slot_timestamps;
    size_t slot_count;
} goodix_primitives_elapsed_state;

typedef struct {
    uint32_t identity;
    uint32_t sample_count;
    int32_t calibration[4];
} goodix_primitives_hrv_configuration;

typedef struct {
    uint32_t mode;
    uint8_t scratch[44];
} goodix_primitives_hrv_work_a;

typedef struct {
    uint32_t channels;
    uint32_t factor;
    uint8_t scratch_008[0x28Cu];
    int32_t quarter_sample_count;
    uint32_t double_sample_count;
    uint8_t scratch_29c[8];
    uint32_t block_size;
    uint32_t reserved_2a8;
    float scale_a;
    float scale_b;
    uint32_t reserved_2b4;
} goodix_primitives_hrv_work_b;

typedef struct {
    uint32_t identity;
    uint32_t sample_count;
    uint32_t mode;
    uint32_t divisor;
    uint32_t window_a;
    uint32_t window_b;
    uint32_t group_count;
    uint32_t scaled_sample_bytes;
    uint32_t sample_count_copy;
    float calibration_e8;
    float calibration_ec;
    float calibration_f0;
    float calibration_f4;
    void *subobjects[GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT];
    size_t subobject_capacities[GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT];
    goodix_primitives_hrv_work_a *owned_6c;
    goodix_primitives_hrv_work_b *owned_70;
} goodix_primitives_hrv_context;

typedef struct {
    uint32_t element_bytes;
    uint32_t batches;
    uint32_t rows;
    uint32_t columns;
    void *data;
} goodix_primitives_tensor_descriptor;

typedef struct {
    goodix_primitives_tensor_descriptor *descriptor;
    uintptr_t auxiliary;
} goodix_primitives_tensor_binding;

#define GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS 561u

typedef struct {
    const float *primary_values;
    size_t primary_count;
    const float *secondary_values;
    size_t secondary_count;
} goodix_primitives_nadt_inference_source;

typedef struct {
    const float *spectrum_values;
    size_t spectrum_count;
    uint8_t outlier_multiplier_tenths;
    const float *mode_one_scales;
    size_t scale_count;
    float mode_one_factor;
} goodix_primitives_nadt_spectral_source;

typedef struct {
    float accumulated[GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES];
    float quantile_scratch[GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES];
    int8_t outlier_mask[GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES];
    float masked[GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES];
    float scaled[GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES];
    float fft_scratch[GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES];
    float fft_bins[GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES];
    int32_t peak_indices[GOODIX_PRIMITIVES_NADT_SPECTRAL_PEAK_CAPACITY];
    float peak_values[GOODIX_PRIMITIVES_NADT_SPECTRAL_PEAK_CAPACITY];
} goodix_primitives_nadt_spectral_workspace;

typedef struct {
    size_t spectral_bin_count;
    int32_t peak_begin;
    int32_t peak_radius;
    size_t peak_count;
    int32_t candidate_indices[
        GOODIX_PRIMITIVES_NADT_SPECTRAL_OUTPUT_CAPACITY];
    uint8_t candidate_flags[
        GOODIX_PRIMITIVES_NADT_SPECTRAL_OUTPUT_CAPACITY];
} goodix_primitives_nadt_spectral_result;

typedef struct {
    uint32_t primary_level_threshold;
    uint32_t secondary_level_threshold;
    uint8_t metric_limit_percent;
    uint8_t quality_threshold;
    uint8_t flag_mask;
} goodix_primitives_nadt_channel_quality_configuration;

typedef struct {
    uint8_t primary_level;
    int16_t secondary_level;
} goodix_primitives_nadt_channel_quality_summary;

typedef struct {
    int32_t primary_activity;
    int32_t secondary_activity;
    float primary_metric;
    float secondary_metric;
    bool primary_valid;
    bool secondary_valid;
    int8_t quality;
    uint8_t flags;
    uint8_t score;
} goodix_primitives_nadt_channel_quality_record;

typedef struct {
    const float *transformed_values;
    size_t transformed_value_count;
    const uint16_t *packed_channels[
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS];
    size_t packed_channel_counts[
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS];
} goodix_primitives_spo2_spectral_source;

typedef struct {
    float fft_scratch[GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES];
} goodix_primitives_spo2_spectral_workspace;

typedef struct {
    float channels[GOODIX_PRIMITIVES_SPO2_SPECTRAL_CHANNELS]
                  [GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES];
} goodix_primitives_spo2_spectral_result;

typedef struct {
    uint8_t primary_rows;
    uint8_t primary_columns;
    uint8_t secondary_rows;
    uint8_t secondary_columns;
    uintptr_t field_14;
    uintptr_t field_18;
    uintptr_t field_1c;
} goodix_primitives_nadt_inference_configuration;

typedef void (*goodix_primitives_tensor_stage_fn)(
    void *context, goodix_primitives_tensor_binding *input,
    goodix_primitives_tensor_binding *output);
typedef bool (*goodix_primitives_tensor_node_fn)(
    void *context,
    const goodix_primitives_tensor_descriptor *const *inputs,
    size_t input_count,
    goodix_primitives_tensor_descriptor *const *outputs,
    size_t output_count);
typedef bool (*goodix_primitives_nadt_subgraph_fn)(
    void *context, float *workspace, size_t workspace_count);

typedef struct {
    goodix_primitives_nadt_subgraph_fn
        subgraphs[GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT];
    void *subgraph_contexts[GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT];
    goodix_primitives_tensor_node_fn
        stages[GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT];
    void *stage_contexts[GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT];
    uint32_t first_stage_values;
    uint32_t shared_stage_values;
    uint32_t recurrent_values;
    float *recurrent_state;
    size_t recurrent_state_capacity;
    uint32_t penultimate_values;
    uint32_t output_values;
} goodix_primitives_nadt_generated_graph;

typedef struct {
    goodix_primitives_tensor_stage_fn
        operators[GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT];
    void *operator_contexts[GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT];
    float quantization_minimum;
    float quantization_maximum;
} goodix_primitives_nadt_generated_subgraph;

typedef struct {
    void *data;
    uint16_t count;
    uint16_t capacity;
} goodix_primitives_buffer_descriptor;

typedef struct {
    uint32_t maximum_threshold;
    uint32_t minimum_threshold;
    uint32_t deviation_factor;
} goodix_primitives_nadt_threshold_configuration;

typedef struct {
    int16_t mean;
    uint8_t threshold;
    uint8_t outlier_count;
} goodix_primitives_nadt_primary_summary;

typedef struct {
    int16_t mean;
    uint8_t threshold;
    uint8_t outlier_count;
    int16_t secondary_mean;
} goodix_primitives_nadt_sample_summary;

typedef struct {
    const goodix_primitives_nadt_threshold_configuration *configuration;
    const goodix_primitives_buffer_descriptor *primary;
    const goodix_primitives_buffer_descriptor *secondary;
    uintptr_t downstream_first;
    uintptr_t downstream_second;
} goodix_primitives_nadt_summary_context;

typedef struct {
    int32_t nonuniform_mask_count;
    uint32_t reserved_04;
    float mean_difference;
    float relative_variance;
    uint8_t accepted_count;
    uint8_t sufficient_coverage;
    uint8_t reserved_12[2];
} goodix_primitives_nadt_difference_summary;

typedef struct {
    uint32_t field_00;
    uint32_t field_04;
    uint32_t *primary;
    uint32_t *secondary;
    uint32_t count;
    uint32_t field_14;
} goodix_primitives_dual_buffer_descriptor;

typedef struct {
    float first;
    float second;
} goodix_primitives_biquad_state;

typedef struct {
    float input;
    float delayed_input;
    float second_delayed_input;
    float feedback;
    float second_feedback;
} goodix_primitives_biquad_coefficients;

typedef struct {
    uint8_t stage_count;
    goodix_primitives_biquad_state *states;
    size_t state_count;
    const goodix_primitives_biquad_coefficients *coefficients;
    size_t coefficient_count;
    float previous_input;
} goodix_primitives_biquad_cascade;

typedef struct {
    float groups[3][2];
} goodix_primitives_spo2_channel_record;

typedef struct {
    uint8_t channel_count;
    const uint8_t *presence_bytes;
    size_t presence_byte_count;
    int32_t *encoded_values;
    size_t encoded_value_count;
    uint32_t metadata[3];
    void *decode_context;
} goodix_primitives_spo2_channel_source;

typedef struct {
    uint8_t channel_count;
    const int32_t *encoded_values;
    size_t encoded_value_count;
    const uint8_t *scale_codes;
    size_t scale_code_count;
    const int16_t *divisors;
    size_t divisor_count;
    uint8_t bit_width;
    uint8_t scale_mode;
    uint8_t encoding_mode;
    const int32_t *scale_tables[3];
    size_t scale_table_counts[3];
    goodix_primitives_double_binary_fn power;
} goodix_primitives_spo2_channel_scaling;

typedef struct {
    int32_t sequence;
    uint8_t record_count;
    goodix_primitives_spo2_channel_record *records;
    size_t record_capacity;
    uint32_t metadata[3];
} goodix_primitives_spo2_channel_output;

typedef void (*goodix_primitives_spo2_channel_decode_fn)(
    void *context, uint8_t channel, uint16_t group, float destination[2]);

typedef struct {
    uint8_t primary_candidate;
    uint8_t first_harmonic_candidate;
    uint8_t second_harmonic_candidate;
    uint8_t spectral_candidate;
    uint8_t secondary_candidate;
    uint8_t reserved_05[3];
    float spectral_concentration;
    float score;
    float concentration_deviation;
    float metric_mean;
    uint8_t primary_spectral_proximity;
    uint8_t harmonic_consistency;
    uint8_t phase_gate;
    uint8_t acceptance_gate;
    uint8_t paired_gate_a;
    uint8_t paired_gate_b;
    uint8_t activation_gate;
    uint8_t hold_gate;
    uint8_t metrics_below_four;
    uint8_t secondary_consistency;
    uint8_t reserved_22[2];
} goodix_primitives_spo2_report_analysis;

typedef struct {
    const float *primary_spectrum;
    size_t primary_spectrum_count;
    const float *secondary_spectrum;
    size_t secondary_spectrum_count;
    float metrics[4];
    uint8_t reference_candidate;
} goodix_primitives_spo2_report_analyzer_input;

typedef struct {
    uint8_t selected_value;
    goodix_primitives_spo2_report_analysis analysis;
} goodix_primitives_spo2_report_output;

/* Transparent GH_SPO2/dlCom diagnostic bindings recovered from 0x0006CCC0.
 * The emitter receives the exact stock format string and a bounded vector of
 * the signed words consumed by its %d conversions. The values remain valid
 * only for the duration of the callback. */
typedef void (*goodix_primitives_spo2_diagnostic_emit_fn)(
    void *context, const char *format, const int32_t *values,
    size_t value_count);
typedef uint32_t (*goodix_primitives_spo2_memory_available_fn)(
    void *context);

typedef struct {
    uint16_t sample_frequency;
    uint32_t timestamp;
    uint8_t mode;
    int32_t latest_output_time;
    int32_t earliest_output_time;
    uint8_t valid_channel_count;
    int32_t sigma;
    int32_t delay_time;
    int32_t valid_score_scale;
    int32_t last_heart_rate;
    int32_t raw_ppg_scale;
} goodix_primitives_spo2_diagnostic_configuration;

typedef struct {
    uint8_t total_channel_count;
    const uint8_t *enable_flags;
    size_t enable_flag_count;
    const int32_t *ppg;
    size_t ppg_count;
    int32_t accelerometer[3];
    int32_t gyroscope[3];
} goodix_primitives_spo2_diagnostic_input;

typedef struct {
    goodix_primitives_spo2_diagnostic_emit_fn formatted_emit;
    void *formatted_context;
    goodix_primitives_spo2_diagnostic_emit_fn direct_emit;
    void *direct_context;
    goodix_primitives_spo2_memory_available_fn memory_available;
    void *memory_context;
} goodix_primitives_spo2_diagnostic_plan;

typedef struct {
    bool history_shift_a;
    bool history_shift_b;
    bool use_secondary_candidate;
    bool accepted;
    uint32_t minimum_selected_value;
    uint8_t event;
    uint8_t phase;
    uint8_t event_seen;
    uint8_t *history_destination;
    size_t history_destination_capacity;
    const uint8_t *history_source;
    size_t history_source_capacity;
} goodix_primitives_spo2_report_state;

typedef void (*goodix_primitives_spo2_report_analyze_fn)(
    void *context, goodix_primitives_spo2_report_analysis *analysis);

typedef struct {
    const uint16_t *values;
    size_t count;
} goodix_primitives_packed_u16_span;

typedef struct {
    uint32_t previous_sequence;
    uint32_t previous_scale_code;
} goodix_primitives_nadt_sample_preparation_state;

typedef struct {
    const int32_t *direct_values;
    size_t direct_value_count;
    const int32_t *calibration_values;
    size_t calibration_value_count;
    const uint8_t *scale_codes;
    size_t scale_code_count;
    uint16_t sequence;
    uint8_t lane_stride;
    uint8_t conversion_mode;
    bool calibrated;
} goodix_primitives_nadt_sample_preparation_input;

typedef struct {
    const goodix_primitives_nadt_sample_preparation_input *sample;
    int32_t axis_x;
    int32_t axis_y;
    int32_t axis_z;
    uint8_t profile;
    bool classifier_suppressed;
} goodix_primitives_nadt_stream_input;

typedef struct {
    bool initialized;
    uint8_t status;
    uint16_t cadence_counter;
    uint32_t batch_count;
    uint8_t batch_sample_count;
    uint8_t low_primary_count;
    uint8_t activity_lane;
    int32_t primary_average;
    int32_t secondary_average;
    size_t primary_history_count;
    size_t secondary_history_count;
    float activity_mean[4];
    float activity_squared_deviation_sum[4];
    int32_t activity_maximum[4];
    int32_t activity_minimum[4];
    bool result_flag;
    goodix_primitives_nadt_window_state classifier;
} goodix_primitives_nadt_stream_state;

typedef struct {
    int32_t primary_raw[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int32_t primary_filtered[GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int16_t configuration_markers[
        GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES];
    int16_t secondary_history[200];
} goodix_primitives_nadt_stream_workspace;

typedef struct {
    bool window_ready;
    uint8_t classification;
    uint8_t quality;
    uint8_t status;
    uint16_t configuration_changed;
} goodix_primitives_nadt_stream_output;

/* Transparent binding for the fixed two-stage optical transform recovered at
 * 0x000373A4. Each coefficient bank contains two consecutive three-float
 * sections, and each history bank contains two consecutive two-float pairs. */
typedef struct {
    const float *numerators;
    size_t numerator_count;
    const float *denominators;
    size_t denominator_count;
    float *input_histories;
    size_t input_history_count;
    float *output_histories;
    size_t output_history_count;
    float correction_threshold;
} goodix_primitives_nadt_optical_transform;

typedef struct {
    uint16_t sample_rate;
    int32_t primary_baseline;
    int32_t low_primary_threshold;
    float ratio_threshold;
    float strong_ratio_threshold;
    goodix_primitives_nadt_window_configuration *window_configuration;
    const goodix_primitives_nadt_window_plan *window_plan;
    goodix_primitives_nadt_sample_preparation_state *preparation_state;
    goodix_primitives_nadt_optical_transform *optical_transform;
    goodix_primitives_double_unary_fn round_provider;
    goodix_primitives_double_unary_fn square_root;
} goodix_primitives_nadt_stream_plan;

/* Exact 60-byte public GH_NADT configuration consumed by 0x0006E664. Field
 * names retain offsets where the recovered private meaning is not proven. */
typedef struct {
    uint16_t sample_rate;
    uint8_t mode;
    uint8_t reserved_03;
    uint16_t field_04;
    uint8_t field_06;
    uint8_t field_07;
    int32_t offset_08;
    int32_t offset_0c;
    uint32_t field_10;
    uint8_t field_14;
    uint8_t reserved_15[3];
    uint32_t field_18;
    uint16_t field_1c;
    uint16_t field_1e;
    uint32_t field_20;
    int16_t field_24;
    uint16_t field_26;
    int32_t field_28;
    int32_t timing_base;
    uint8_t field_30;
    uint8_t reserved_31;
    uint16_t field_32;
    uint8_t field_34;
    uint8_t field_35;
    uint16_t field_36;
    uint16_t field_38;
    uint16_t field_3a;
} goodix_primitives_nadt_initialize_configuration;

/* Observable 0x00..0x5B state bytes plus the allocation bound at stock +0x58.
 * Native pointers enlarge the host form without changing field semantics. */
typedef struct {
    uint8_t marker;
    uint8_t flag_01;
    uint8_t reserved_02;
    uint8_t flag_03;
    uint8_t flags_04_08[5];
    uint8_t threshold_09;
    uint8_t flag_0a;
    uint8_t flags_0b_18[14];
    uint8_t reserved_19_1b[3];
    uint16_t counter_1c;
    uint16_t counter_1e;
    uint16_t counter_20;
    uint16_t counter_22;
    uint16_t counter_24;
    uint16_t counter_26;
    uint32_t word_28;
    uint32_t word_2c;
    uint32_t word_30;
    uint32_t limit_34;
    uint32_t word_38;
    uint32_t word_3c;
    uint32_t word_40;
    uint32_t word_44;
    uint32_t word_48;
    uint32_t word_4c;
    uint8_t reserved_50_57[8];
    void *allocation_58;
} goodix_primitives_nadt_initializer_state;

/* Exact initialized fields of the 118-byte runtime configuration produced by
 * the scattered tail at 0x00073E2C. */
typedef struct {
    uint16_t sample_rate;
    uint8_t mode;
    uint8_t reserved_03;
    uint16_t field_04;
    uint8_t enabled_06;
    uint8_t field_07;
    uint8_t field_08;
    uint8_t reserved_09_0b[3];
    int32_t offset_0c;
    int32_t offset_10;
    uint32_t field_14;
    uint32_t enabled_18;
    float minimum_1c;
    float maximum_20;
    uint8_t field_24;
    uint8_t reserved_25_27[3];
    uint32_t constant_28;
    uint32_t field_2c;
    int32_t timing_30;
    uint16_t constant_34;
    uint16_t constant_36;
    int32_t timing_38;
    uint16_t field_3c;
    uint16_t field_3e;
    uint32_t field_40;
    int32_t half_field_44;
    uint8_t field_48;
    uint8_t reserved_49;
    uint16_t timing_4a;
    uint16_t constant_4c;
    uint16_t timing_4e;
    uint16_t timing_50;
    uint8_t field_52_enabled;
    uint8_t reserved_53;
    uint16_t constant_54;
    uint16_t field_56;
    int32_t doubled_field_58;
    int32_t field_5c;
    uint16_t timing_60;
    uint16_t constant_62;
    uint16_t timing_64;
    uint8_t constant_66;
    uint8_t field_67;
    uint16_t field_68;
    uint16_t field_6a;
    uint8_t field_6c;
    uint8_t field_6d;
    uint16_t field_6e;
    uint16_t field_70;
    uint16_t field_72;
    uint16_t constant_74;
} goodix_primitives_nadt_runtime_configuration;

typedef struct {
    uint8_t *bank_400_a;
    size_t bank_400_a_bytes;
    uint8_t *bank_400_b;
    size_t bank_400_b_bytes;
    uint8_t *bank_600;
    size_t bank_600_bytes;
    uint8_t *bank_68;
    size_t bank_68_bytes;
    uint32_t *counters;
    size_t counter_count;
    goodix_primitives_dual_buffer_descriptor *descriptor;
    uint32_t *descriptor_primary;
    size_t descriptor_primary_words;
    uint32_t *descriptor_secondary;
    size_t descriptor_secondary_words;
    uint32_t descriptor_field_00;
    uint32_t descriptor_field_04;
    uint32_t descriptor_field_14;
} goodix_primitives_nadt_initializer_workspace;

typedef struct {
    float *values;
    uint32_t count;
    uint32_t capacity;
    uint32_t limit;
} goodix_primitives_float_storage;

typedef struct {
    uint8_t count;
    void *records;
    const float *coefficient_record;
} goodix_primitives_pair_buffer;

typedef struct {
    void *data;
    uint16_t count;
    uint16_t capacity;
    uint16_t auxiliary;
    uint8_t status;
    uint8_t flag;
} goodix_primitives_extended_descriptor;

typedef struct {
    void *data;
    uint16_t count;
    uint16_t capacity;
    uint8_t flag;
    uint8_t status;
    uint16_t auxiliary;
    uint32_t reserved;
} goodix_primitives_float_descriptor;

typedef struct {
    goodix_primitives_pair_buffer pair_buffers[9];
    goodix_primitives_buffer_descriptor i16_buffers[9];
    goodix_primitives_float_descriptor float_histories[7];
} goodix_primitives_hr_secondary_context;

typedef struct {
    uint8_t algorithm_mode;
    uint8_t reserved_01[3];
    uint32_t sample_rate;
    int32_t minimum_batch;
    uint32_t secondary_window_override;
    uint32_t primary_window_override;
    int32_t feature_stride;
    int32_t terminal_default;
    uint32_t candidate_limit;
    uint32_t owner_word;
} goodix_primitives_hr_configuration;

typedef struct {
    goodix_primitives_hr_graph_build_fn build;
    goodix_primitives_hr_graph_release_fn release;
    void *context;
} goodix_primitives_hr_graph_binding;

typedef struct {
    goodix_primitives_hr_graph_binding selector_0;
    goodix_primitives_hr_graph_binding selector_1;
    goodix_primitives_hr_graph_binding selector_6;
} goodix_primitives_hr_graph_bindings;

typedef struct {
    uint16_t sample_rate;
    uint16_t samples_per_25hz_phase;
    uint32_t periodic_interval;
    uint32_t processed_count;
    uint32_t pending_count;
    uint8_t cleared_10_12[3];
    uint8_t configuration_selector;
    uint32_t primary_window;
    uint32_t secondary_window;
    uint8_t minimum_batch;
    int32_t feature_stride;
    uint32_t candidate_limit;
    uint32_t owner_word;
    uint8_t cleared_2c_57[44];
    uint8_t graph_control[6];
    uint8_t cleared_5e_5f[2];
    uint32_t graph_span;
    uint32_t graph_mode;
    uint32_t graph_enabled;
    uintptr_t graph_selector_0;
    uintptr_t graph_selector_1;
    uint8_t cleared_74_83[16];
    uintptr_t graph_selector_6;
    uint8_t cleared_88_ab[36];
    uint8_t primary_window_low_byte;
    uint8_t graph_latch;
    uint8_t cleared_ae_af[2];
    goodix_primitives_extended_descriptor short_history_a;
    goodix_primitives_float_descriptor float_history_a;
    goodix_primitives_extended_descriptor short_history_b;
    goodix_primitives_float_descriptor float_history_b;
    uint8_t cleared_e8_10f[40];
    uint8_t terminal_flags[3];
    uint8_t cleared_113;
    float initial_accumulators[4];
    uint32_t cleared_124;
    double initial_baselines[4];
    int32_t terminal_default;
    uint32_t cleared_14c;
} goodix_primitives_hr_primary_context;

typedef struct {
    goodix_primitives_hr_primary_context *primary;
    goodix_primitives_hr_secondary_context *secondary;
    goodix_primitives_hr_graph_bindings graph_bindings;
} goodix_primitives_hr_context_owner;

typedef struct {
    goodix_primitives_float_descriptor history;
    goodix_primitives_float_descriptor window;
    goodix_primitives_float_descriptor filtered;
    goodix_primitives_float_descriptor scalar;
    goodix_primitives_float_descriptor primary_buckets;
    goodix_primitives_float_descriptor secondary_buckets;
} goodix_primitives_channel_state;

typedef struct {
    goodix_primitives_channel_state primary;
    goodix_primitives_channel_state secondary;
    goodix_primitives_float_descriptor tail_a;
    goodix_primitives_float_descriptor tail_b;
    goodix_primitives_float_descriptor tail_c;
    goodix_primitives_extended_descriptor tail_d;
} goodix_primitives_session_state;

typedef struct {
    goodix_primitives_float_descriptor samples;
} goodix_primitives_owned_float_record;

typedef struct {
    uint8_t status;
    float lower;
    float upper;
    goodix_primitives_float_descriptor samples;
    uint8_t tag;
} goodix_primitives_channel_record;

typedef struct {
    uint32_t marker;
    goodix_primitives_buffer_descriptor full_rate;
    goodix_primitives_buffer_descriptor reduced_rate;
} goodix_primitives_dual_i16_storage;

typedef struct {
    goodix_primitives_buffer_descriptor first;
    goodix_primitives_buffer_descriptor second;
} goodix_primitives_descriptor_pair;

typedef struct {
    goodix_primitives_session_state *session;
    goodix_primitives_dual_i16_storage auxiliary;
    goodix_primitives_descriptor_pair *pair;
} goodix_primitives_session_aggregate;

typedef struct {
    uint8_t *buffer;
    uint8_t reserved_04;
    uint8_t flag_05;
    uint8_t flag_06;
    uint8_t reserved_07;
} goodix_primitives_buffer_record;

typedef struct {
    uint8_t reserved_00[8];
    void *records;
    uint8_t reserved_0c[12];
    void *scratch;
} goodix_primitives_record_pair_owner;

/* Native-pointer form of stock's 0xD4-byte outer SpO2 preprocessing
 * session.  Target offsets are asserted in the implementation. */
typedef struct {
    uint8_t reserved_000[12];
    uint8_t processing_record[96];
    goodix_primitives_record_pair_owner record_pair;
    goodix_primitives_session_aggregate aggregate;
    uint32_t reserved_after_aggregate;
    goodix_primitives_owned_float_record *owned_float;
    goodix_primitives_buffer_record *buffer_record;
    quantized_runtime_goodix_model_owner model;
    goodix_primitives_channel_record *channel_records;
} goodix_primitives_outer_session;

typedef struct {
    uint32_t *values;
    uint16_t count;
    uint16_t capacity;
} goodix_primitives_word_window;

typedef struct {
    uint32_t timestamp;
    float gate;
    float values[3];
} goodix_primitives_timed_triplet_source;

typedef struct {
    float values[3];
    uint32_t last_timestamp;
} goodix_primitives_timed_triplet_destination;

typedef struct {
    goodix_primitives_word_window window;
    uint16_t cursor;
    uint16_t emitted_count;
} goodix_primitives_threshold_history;

typedef struct {
    uint16_t row_count;
    uint16_t plateau_radius;
    uint16_t first_label;
} goodix_primitives_nadt_peak_mask_configuration;

typedef struct {
    uint32_t *values;
    uint32_t count;
    uint32_t capacity;
    uint32_t push_count;
} goodix_primitives_counted_word_history;

typedef struct {
    int32_t input_rate;
    uint32_t mode;
    int32_t midpoint_window;
    goodix_primitives_counted_word_history raw_history;
    goodix_primitives_counted_word_history periodic_history;
    goodix_primitives_counted_word_history mean_history;
    goodix_primitives_counted_word_history centered_history;
    goodix_primitives_counted_word_history weighted_history;
    int32_t interpolation_count;
    int32_t interpolation_phase;
    float previous_interpolation_sample;
    const float *mode_coefficients[4];
    size_t mode_coefficient_counts[4];
} goodix_primitives_hr_weighted_feature_state;

typedef struct {
    uint32_t tag;
    float position;
    float value;
    uint32_t alternate_tag;
    uint8_t suppressed;
} goodix_primitives_hr_candidate_record;

typedef struct {
    uint32_t call_count;
    int32_t position_origin;
    int32_t position_step;
} goodix_primitives_hr_candidate_selection_state;

typedef struct {
    float values[4];
    uint32_t count;
    uint32_t tags[4];
} goodix_primitives_hr_candidate_selection;

typedef bool (*goodix_primitives_hr_sample_invalid_fn)(
    void *context, int32_t sample);
typedef bool (*goodix_primitives_hr_decision_core_fn)(void *context);

typedef struct {
    int32_t *channel_values;
    size_t channel_value_count;
    const uint8_t *presence_bytes;
    size_t presence_byte_count;
    uint8_t channel_count;
    int32_t axis_x;
    int32_t axis_y;
    int32_t axis_z;
} goodix_primitives_hr_process_input;

typedef struct {
    goodix_primitives_hr_sample_invalid_fn sample_invalid;
    void *sample_invalid_context;
    goodix_primitives_hr_decision_core_fn decision_core;
    void *decision_context;
    goodix_primitives_float_unary_fn square_root;
    float outlier_maximum_threshold;
    float outlier_minimum_threshold;
    float outlier_deviation_multiplier;
    const goodix_primitives_hr_candidate_record *candidate_records;
    size_t candidate_record_count;
    int32_t candidate_lower_bound;
    int32_t candidate_upper_bound;
    int32_t candidate_warmup_limit;
    float candidate_scale;
} goodix_primitives_hr_process_plan;

typedef struct {
    uint32_t sample_rate;
    uint32_t process_count;
    uint32_t window_index;
    goodix_primitives_counted_word_history signal_history;
    goodix_primitives_counted_word_history motion_history;
    goodix_primitives_counted_word_history quality_history;
    goodix_primitives_hr_weighted_feature_state weighted_feature;
    goodix_primitives_hr_extrema_tracker extrema_tracker;
    const goodix_primitives_hr_extrema_curve *trough_curve;
    const goodix_primitives_hr_extrema_curve *peak_curve;
    goodix_primitives_hr_extrema_workspace *extrema_workspace;
    int32_t extrema_signal_mode;
    uint32_t extrema_interpolation_mode;
    int32_t extrema_position_base;
    int32_t extrema_period;
    goodix_primitives_hr_candidate_selection_state candidate_selector;
    float quality_reference;
    int32_t quality_threshold_first;
    int32_t quality_threshold_second;
    int32_t previous_output[6];
    uint32_t adjustment_age;
    int32_t previous_rate;
    float decision_reference_position;
    int32_t decision_reference_mode;
    int32_t latest_rates[4];
    uint32_t outlier_count;
    uint32_t tail_outlier_count;
} goodix_primitives_hr_process_state;

typedef struct {
    float *quality_sort_scratch;
    size_t quality_sort_capacity;
    float *signal_scratch;
    size_t signal_scratch_capacity;
} goodix_primitives_hr_process_workspace;

typedef struct {
    int32_t count;
    int32_t capacity;
    float mean[3];
    uint32_t timestamp;
} goodix_primitives_running_triplet;

#define GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES 10u

typedef struct {
    float position;
    float primary_first;
    float primary_second;
    float auxiliary_first;
    float auxiliary_second;
    float center;
    int32_t tag;
    uint8_t flag;
    uint8_t reserved[3];
} goodix_primitives_hr_decision_record;

typedef struct {
    float position;
    float primary_first;
    float primary_second;
    float auxiliary_first;
    float auxiliary_second;
    uint8_t ready;
    uint32_t update_count;
} goodix_primitives_hr_decision_source;

typedef struct {
    goodix_primitives_hr_decision_record *records;
    uint32_t record_count;
    uint32_t record_capacity;
    int32_t mode;
    int32_t latch;
    int32_t minimum_interval;
    int32_t maximum_interval;
    int32_t stale_count;
    goodix_primitives_running_triplet baseline;
    goodix_primitives_hr_decision_source source;
    goodix_primitives_counted_word_history primary_history;
    goodix_primitives_counted_word_history auxiliary_history;
    goodix_primitives_counted_word_history interval_history;
    uint32_t sample_rate;
    uint32_t timestamp;
    float diagnostic_variation_percent;
    float diagnostic_primary_mean;
    float diagnostic_auxiliary_mean;
    float diagnostic_interval_mean;
} goodix_primitives_hr_decision_state;

typedef struct {
    float mad_scratch[GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES];
    float compacted[GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES];
    uint8_t inlier_mask[GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES];
} goodix_primitives_hr_decision_workspace;

typedef struct {
    goodix_primitives_hr_decision_state *state;
    goodix_primitives_hr_decision_workspace *workspace;
    goodix_primitives_float_unary_fn square_root;
} goodix_primitives_hr_decision_context;

typedef struct {
    float mean;
    float squared_deviation_sum;
    int32_t maximum;
    int32_t minimum;
} goodix_primitives_running_i32_statistics;

typedef int32_t (*goodix_primitives_command_fn)(
    uint32_t command, void *context);
typedef int32_t (*goodix_primitives_register_read_fn)(
    uint32_t address, uint32_t count, void *context);
typedef uint32_t (*goodix_primitives_clock_fn)(void *context);
typedef void (*goodix_primitives_register_write_fn)(
    uint16_t address, uint16_t value, void *context);
typedef void (*goodix_primitives_register_bit_field_write_fn)(
    uint16_t address, uint8_t low_bit, uint8_t high_bit,
    uint16_t value, void *context);

typedef struct {
    goodix_primitives_command_fn command;
    goodix_primitives_register_read_fn register_read;
    goodix_primitives_clock_fn clock;
    void *context;
} goodix_primitives_command_poll_ops;

typedef struct {
    goodix_primitives_register_write_fn write_register;
    goodix_primitives_register_bit_field_write_fn write_bit_field;
    void *context;
} goodix_primitives_register_configuration_ops;

/* Ownership-only views of two stock Goodix contexts.  The names retain the
 * observed 32-bit target offsets while allowing the rebuilt firmware to use
 * native pointers without reproducing undocumented padding. */
typedef struct {
    void *owned_1c0;
    void *owned_1dc;
    void *owned_1f4;
    void *owned_260;
} goodix_primitives_algorithm_context_ownership;

typedef struct {
    void *descriptor_allocations[9];
    void *owned_slots[9];
    void *extended_owned_slots[7];
} goodix_primitives_record_family_ownership;

typedef struct {
    int16_t previous_output;
    int32_t previous_correlation;
} goodix_primitives_autocorrelation_state;

typedef struct {
    bool enabled;
    uint16_t sample_gate_limit;
    int16_t minimum_range;
    uint16_t minimum_interval;
    uint16_t maximum_interval_spread;
    uint16_t minimum_quality;
    uint8_t required_consecutive_windows;
} goodix_primitives_nadt_alternate_configuration;

typedef struct {
    int32_t current_result;
    uint8_t mode;
    uint8_t consecutive_matches;
    bool processing;
    uint16_t sample_gate;
    goodix_primitives_autocorrelation_state autocorrelation;
} goodix_primitives_nadt_alternate_state;

typedef struct {
    int16_t centered[GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT];
    int16_t transformed[GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT];
    int16_t maxima[GOODIX_PRIMITIVES_NADT_ALTERNATE_EXTREMA_CAPACITY];
    int16_t minima[GOODIX_PRIMITIVES_NADT_ALTERNATE_EXTREMA_CAPACITY];
    int16_t intervals[GOODIX_PRIMITIVES_NADT_ALTERNATE_INTERVAL_CAPACITY];
} goodix_primitives_nadt_alternate_workspace;

typedef struct {
    int16_t range;
    int16_t minimum_interval;
    int16_t interval_range;
    uint8_t quality;
    uint8_t maxima_count;
    uint8_t minima_count;
} goodix_primitives_nadt_alternate_diagnostics;

typedef struct {
    uint32_t *dispatch_record;
    uintptr_t field_64;
    uintptr_t field_68;
} goodix_primitives_word_dispatch_context;

typedef struct {
    float *workspace;
    size_t workspace_count;
    uint32_t *recent_inputs;
    size_t recent_input_count;
    goodix_primitives_word_dispatch_context dispatch;
} goodix_primitives_spo2_score_context;

typedef struct {
    goodix_primitives_elapsed_state *elapsed_state;
    const goodix_primitives_float_span *mode_buffers;
    uint32_t mode;
    uint32_t *dispatch_record;
    uintptr_t field_64;
    uintptr_t field_68;
} goodix_primitives_timed_dispatch_context;

typedef struct {
    uint32_t *state_6c;
    uint32_t *state_70;
    uint32_t *state_84;
    void *owned_b0;
    void *owned_bc;
    void *owned_cc;
    void *owned_d8;
} goodix_primitives_processing_context_ownership;

typedef struct {
    const int32_t *primary;
    uint16_t primary_count;
    uint16_t primary_start;
    const int32_t *secondary;
    uint16_t secondary_count;
    uint16_t secondary_start;
} goodix_primitives_event_pair_source;

typedef struct {
    size_t rising_count;
    size_t falling_count;
    size_t transition_count;
} goodix_primitives_extrema_index_counts;

typedef struct {
    int16_t *values;
    uint16_t count;
    uint16_t capacity;
} goodix_primitives_i16_window;

typedef struct {
    uint8_t *values;
    uint16_t count;
    uint16_t capacity;
    uint16_t cursor;
} goodix_primitives_byte_window;

typedef struct {
    int16_t *values;
    uint16_t count;
    uint16_t capacity;
    uint16_t cursor;
    uint8_t phase;
    uint8_t period;
} goodix_primitives_decimated_i16_window;

typedef struct {
    float *values;
    uint16_t count;
    uint16_t capacity;
    uint8_t period;
    uint8_t phase;
    uint16_t cursor;
    float sum;
} goodix_primitives_decimated_float_window;

typedef struct {
    goodix_primitives_byte_window primary_candidates;
    goodix_primitives_decimated_float_window concentrations;
    goodix_primitives_byte_window reference_candidates;
    goodix_primitives_decimated_float_window metric_history;
    uint8_t previous_primary_candidate;
    uint8_t primary_spectral_streak;
    uint8_t harmonic_streak;
    uint8_t stable_primary_streak;
    uint8_t reference_limit;
} goodix_primitives_spo2_report_analyzer_state;

typedef struct {
    uint32_t feature_average_period;
    uint32_t pair_average_period;
    uint32_t ratio_period;
    uint32_t geometry_period;
} goodix_primitives_nadt_cadence_configuration;

typedef struct {
    float feature_value;
    float average_value;
} goodix_primitives_nadt_feature_pair;

typedef struct {
    goodix_primitives_nadt_feature_pair primary;
    goodix_primitives_nadt_feature_pair secondary;
} goodix_primitives_nadt_channel_input;

typedef struct {
    goodix_primitives_decimated_float_window input;
    goodix_primitives_decimated_float_window smoothed;
    goodix_primitives_decimated_float_window residual;
    goodix_primitives_decimated_float_window residual_smoothed;
    goodix_primitives_decimated_float_window feature_average;
} goodix_primitives_nadt_rolling_feature_state;

typedef struct {
    goodix_primitives_nadt_rolling_feature_state feature;
    float average_accumulator;
    goodix_primitives_decimated_float_window pair_average;
} goodix_primitives_nadt_feature_pair_state;

typedef struct {
    goodix_primitives_nadt_feature_pair_state primary;
    goodix_primitives_nadt_feature_pair_state secondary;
    goodix_primitives_decimated_float_window combined_ratio;
    goodix_primitives_decimated_float_window primary_ratio;
    goodix_primitives_decimated_float_window secondary_ratio;
    goodix_primitives_decimated_i16_window half_primary_input;
} goodix_primitives_nadt_channel_state;

typedef struct {
    float magnitude;
    goodix_primitives_i16_window magnitude_delta;
    float angle_accumulator;
    goodix_primitives_i16_window angle_average;
} goodix_primitives_nadt_geometry_state;

typedef struct {
    uint32_t reserved[2];
    float primary[2];
    float secondary[2];
} goodix_primitives_nadt_channel_accumulator;

typedef struct {
    uint32_t sample_index;
    uint32_t selector;
    const goodix_primitives_nadt_channel_accumulator *channels;
    int32_t vector[3];
} goodix_primitives_nadt_batch_input;

typedef struct {
    size_t channel_count;
    uint32_t period;
} goodix_primitives_nadt_batch_configuration;

typedef struct {
    uint32_t batch_index;
    uint8_t selector;
    goodix_primitives_nadt_channel_accumulator *channels;
    size_t channel_capacity;
    int32_t vector[3];
    goodix_primitives_nadt_channel_accumulator aggregate;
} goodix_primitives_nadt_batch_state;

typedef struct {
    uint8_t primary_count;
    goodix_primitives_decimated_float_window history;
    uint8_t quality_flags;
    uint8_t secondary_count;
    float metric;
    int8_t direction;
    uint8_t category;
    float baseline;
    float reference;
    float scaled_reference;
    uint8_t source_flags;
    float first_score;
    float second_score;
    float third_score;
    float fourth_score;
    float output_metric;
} goodix_primitives_nadt_output_record;

typedef struct {
    float second_score;
    float fourth_score;
    float first_score;
    float third_score;
    uint8_t source_flags;
    uint8_t category;
} goodix_primitives_nadt_source_metrics;

typedef struct {
    float reference;
    float scaled_reference;
} goodix_primitives_nadt_reference_metrics;

typedef struct {
    uint8_t rounded_value_threshold;
    int8_t alternate_history_length;
    int8_t default_history_length;
    uint8_t alternate_tolerance;
    uint8_t default_tolerance;
} goodix_primitives_nadt_quality_configuration;

typedef struct {
    goodix_primitives_nadt_difference_summary secondary_difference;
    float secondary_average;
    goodix_primitives_nadt_difference_summary primary_difference;
    float primary_average;
    uint8_t cosine_percent;
} goodix_primitives_nadt_channel_analysis;

typedef struct {
    uint32_t first;
    uint32_t second;
} goodix_primitives_word_pair;

typedef struct {
    int32_t first;
    int32_t second;
    int32_t third;
    int32_t average;
    uint32_t reserved[11];
    uint32_t phase;
} goodix_primitives_warmup_average_state;

typedef struct {
    uint32_t scale_rate;
    int32_t minimum_scale;
    float residual_axis_scale;
    uint16_t motion_window_size;
    int32_t motion_spread_factor;
    goodix_primitives_float_unary_fn logarithm_base_10;
    goodix_primitives_float_unary_fn square_root;
} goodix_primitives_spo2_stream_plan;

typedef struct {
    uint32_t sample_count;
    double scale_accumulators[4];
    int32_t channel_discontinuity_limits[4];
    goodix_primitives_biquad_cascade channel_filters[4];
    goodix_primitives_i16_window channel_packed[4];
    goodix_primitives_biquad_cascade residual_filter;
    goodix_primitives_i16_window residual_packed;
    goodix_primitives_decimated_float_window motion_history[4];
    goodix_primitives_biquad_cascade motion_filters[4];
    goodix_primitives_i16_window motion_packed[4];
    float *motion_sorted[3];
    size_t motion_sorted_count[3];
    size_t motion_sorted_capacity[3];
    float motion_anchor[3];
} goodix_primitives_spo2_stream_state;

typedef struct {
    float *sort_scratch;
    size_t sort_scratch_capacity;
} goodix_primitives_spo2_stream_workspace;

typedef int32_t (*goodix_primitives_spo2_process_workspace_fn)(
    void *context, float *workspace, size_t workspace_count);

typedef struct {
    int32_t *channel_values;
    size_t channel_value_count;
    const uint8_t *enable_flags;
    size_t enable_flag_count;
    uint8_t channel_count;
    int32_t accelerometer[3];
    uint8_t mode;
    const uint8_t *filter_code;
    size_t filter_code_count;
} goodix_primitives_spo2_process_input;

typedef struct {
    uint32_t valid;
    uint32_t selected;
    uint32_t reserved;
    uint32_t score_at_least_70;
    uint32_t scaled_score;
} goodix_primitives_spo2_process_output;

typedef struct {
    uint16_t sample_frequency;
    uint16_t processing_cadence;
    uint8_t expected_valid_channels;
    uint8_t reserved_05[3];
    uint32_t report_selected_value;
    int32_t maximum_selection;
    int32_t selection_delay;
    uint32_t score_scale;
} goodix_primitives_spo2_process_configuration;

typedef struct {
    goodix_primitives_i32_unary_fn integrity_transform;
    const goodix_primitives_spo2_stream_plan *stream_plan;
    const uint16_t *packed_banks[
        GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT];
    goodix_primitives_packed_u16_span deviation_channels[4];
    uint8_t triplicate_disabled;
    uint8_t triplicate_ready;
    const uint16_t *triplicate_values;
    size_t triplicate_value_count;
    const uint16_t *spectral_packed_channels[
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS];
    size_t spectral_packed_channel_counts[
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS];
    goodix_primitives_spo2_process_workspace_fn workspace_process;
    void *workspace_process_context;
    const quantized_runtime *quantized;
    const goodix_primitives_timed_dispatch_context *timed_dispatch;
    const goodix_primitives_spo2_score_context *score_dispatch;
    const goodix_primitives_indexed_operation_fn *operations;
    goodix_primitives_float_unary_fn exponential;
    goodix_primitives_float_unary_fn logarithm_base_10;
} goodix_primitives_spo2_process_plan;

typedef struct {
    uint32_t invocation_count;
    uint32_t sample_count;
    uint32_t elapsed_seconds;
    int32_t latest_result;
    int16_t last_selected;
    uint8_t report_selected_candidate;
    uint8_t reserved_17;
    goodix_primitives_spo2_stream_state *stream;
    goodix_primitives_spo2_report_state report;
    goodix_primitives_spo2_report_analyzer_state analyzer;
} goodix_primitives_spo2_process_state;

typedef struct {
    goodix_primitives_warmup_average_state stream_sample;
    uint8_t stream_mode;
    uint8_t reserved_41[3];
    float packed[GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES];
    float deviation_scratch[GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES];
    float deviations[4];
    goodix_primitives_spo2_spectral_workspace spectral_workspace;
    goodix_primitives_spo2_spectral_result spectra;
    float model_values[GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_VALUES];
    float saved_model_row[GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS];
    uint32_t score_history_scratch[4];
    goodix_primitives_spo2_report_output report_output;
} goodix_primitives_spo2_process_workspace;

typedef struct {
    uint8_t descending;
    uint8_t reserved[3];
    int32_t extremum;
    int32_t emitted_count;
    int32_t extremum_count;
    int32_t sample_count;
} goodix_primitives_extrema_history;

typedef struct {
    uint8_t *records;
    uint32_t count;
    uint32_t capacity;
} goodix_primitives_record32_history;

typedef struct {
    uint8_t prefix[20];
    float center;
    int32_t eligible;
    uint8_t suffix[4];
} goodix_primitives_hr_event_record;

typedef struct {
    const void *table_9d640;
    const void *table_a04cc;
    const void *table_a50b0;
    const void *table_a692c;
    const void *table_ad1ac;
    const void *table_ad13c;
    const void *table_ad160;
} goodix_primitives_tables;

/* 0x6EB00 / 0x6CC34.  The stock routines fault for a zero capacity; the
 * reconstruction returns false instead.  Otherwise they preserve the stock
 * bounded-copy-and-final-NUL contract. */
bool goodix_primitives_copy_preprocess_version(char *destination,
                                               size_t capacity);
bool goodix_primitives_copy_process_version(char *destination,
                                            size_t capacity);

/* 0x29C74.  Stock copied a fixed seven-entry table to its stack, then called
 * table[record[0]].  Supplying that table explicitly removes the absolute,
 * opaque table dependency. */
bool goodix_primitives_dispatch_state(
    uint32_t *record,
    const goodix_primitives_state_handler_fn
        handlers[GOODIX_PRIMITIVES_STATE_COUNT]);

/* 0x29F88 / 0x2ACF4. */
bool goodix_primitives_record_initialize(uint8_t *record, size_t length);
bool goodix_primitives_record_initialize_once(uint8_t *record, size_t length);

/* 0x2D16C.  Returns 0 on provider success and -1 otherwise. */
int32_t goodix_primitives_initialize_device(
    uint16_t device_id, goodix_primitives_device_initialize_fn initialize);

/* 0x29D34: exact recovered 24-bit fixed-point pairs. */
void goodix_primitives_select_fixed_pair(bool alternate,
                                         uint32_t *first,
                                         uint32_t *second);

/* 0x2A474 / 0x2ABEC.  Globals become caller-owned records. */
bool goodix_primitives_reset_state_record(uint8_t *record, size_t length);
bool goodix_primitives_clear_state_flags(uint8_t *record, size_t length);

/* 0x6F9D4. */
bool goodix_primitives_call_hook(goodix_primitives_hook_fn hook);

/* 0x6A140 / 0x2E8C4 / 0x2E8C8 / 0x2AE00. */
uint32_t goodix_primitives_library_code(void);
uint32_t goodix_primitives_constant_four(void);
uint32_t goodix_primitives_constant_one_a(void);
uint32_t goodix_primitives_constant_one_b(void);

/* 0x6A130 / 0x6A138 / 0x6A148 / 0x6A150 / 0x6A018 / 0x6CC2C /
 * 0x6EAF8.  The stock functions returned absolute pointers into hidden
 * tables.  These accessors return the corresponding explicit binding. */
const void *goodix_primitives_table_9d640(
    const goodix_primitives_tables *tables);
const void *goodix_primitives_table_a04cc(
    const goodix_primitives_tables *tables);
const void *goodix_primitives_table_a50b0(
    const goodix_primitives_tables *tables);
const void *goodix_primitives_table_a692c(
    const goodix_primitives_tables *tables);
const void *goodix_primitives_table_ad1ac(
    const goodix_primitives_tables *tables);
const void *goodix_primitives_table_ad13c(
    const goodix_primitives_tables *tables);
const void *goodix_primitives_table_ad160(
    const goodix_primitives_tables *tables);

/* Additional closed Goodix utilities. */
bool goodix_primitives_buffer_record_initialize(
    goodix_primitives_buffer_record *record,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
bool goodix_primitives_buffer_record_create(
    goodix_primitives_buffer_record **record,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
bool goodix_primitives_buffer_record_destroy(
    goodix_primitives_buffer_record **record,
    goodix_primitives_release_fn release, void *release_context);
bool goodix_primitives_integer_max_index(const int32_t *values, size_t count,
                                         int32_t *maximum, size_t *index);
bool goodix_primitives_copy_dlcom_version(char *destination,
                                         size_t capacity);
bool goodix_primitives_copy_dsp_version(char *destination,
                                       size_t capacity);
bool goodix_primitives_build_spo2_version(char *destination,
                                          size_t capacity,
                                          const char *weights_version);
/* 0x0006D424: exact GH_HR exception/DSP/dlCom composite identity. */
bool goodix_primitives_build_hr_version(char *destination,
                                        size_t capacity);
/* 0x0006E788: exact GH_NADT preprocessing and DSP identity builder. */
bool goodix_primitives_build_nadt_version(char *destination,
                                          size_t capacity);
/* 0x0006E664: complete typed GH_NADT state/workspace/runtime-config
 * initializer. The stock 60-byte configuration and pv_v1.0.0 contract are
 * retained; every absolute RAM/table binding is explicit. */
int32_t goodix_primitives_nadt_context_initialize(
    const goodix_primitives_nadt_initialize_configuration *configuration,
    const char *version,
    goodix_primitives_nadt_initializer_state *state,
    goodix_primitives_nadt_runtime_configuration *runtime,
    goodix_primitives_nadt_initializer_workspace *workspace,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
/* 0x00032788: clear the public result status, copy the exact recovered
 * default configuration, override its sample rate, and invoke 0x0006E664. */
int32_t goodix_primitives_nadt_default_initialize(
    uint16_t sample_rate, uint8_t *result_status,
    goodix_primitives_nadt_initializer_state *state,
    goodix_primitives_nadt_runtime_configuration *runtime,
    goodix_primitives_nadt_initializer_workspace *workspace,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
/* 0x0006E574: reset the exact mutable GH_NADT state fields, clear and rebind
 * the recovered work banks, and release the initializer-owned record. */
int32_t goodix_primitives_nadt_context_reset(
    goodix_primitives_nadt_initializer_state *state,
    goodix_primitives_nadt_initializer_workspace *workspace,
    goodix_primitives_release_fn release, void *release_context);
/* 0x0006DF60: exact GH_HRV preprocessing identity builder. */
bool goodix_primitives_build_hrv_version(char *destination,
                                         size_t capacity);
bool goodix_primitives_word_window_push(goodix_primitives_word_window *window,
                                        uint32_t value);
/* 0x0002F260: fixed-capacity UInt32 history with a wrapping lifetime push
 * counter. Full histories evict the oldest value before appending. */
bool goodix_primitives_counted_word_history_push(
    goodix_primitives_counted_word_history *history, uint32_t value);
/* 0x00037588: convert a non-25-divisible input stream into the recovered
 * 25-phase periodic history. The previous-sample and phase banks that were
 * absolute stock globals are explicit fields in the caller-owned state. */
bool goodix_primitives_hr_interpolate_periodic_sample(
    goodix_primitives_hr_weighted_feature_state *state, bool *emitted);
/* 0x00030368: route each Float32 sample into the recovered five-history HR
 * feature pipeline, locally resample non-25-divisible input rates, and apply
 * the selected newest-first coefficient bank. */
bool goodix_primitives_hr_weighted_feature_update(
    goodix_primitives_hr_weighted_feature_state *state, float sample,
    bool *emitted);
/* 0x00086BAC: scan the recovered HR position band newest-first, retain four
 * bounded candidates with tags, and compact strictly positive results. */
bool goodix_primitives_hr_candidate_window_select(
    goodix_primitives_hr_candidate_selection_state *state,
    const goodix_primitives_hr_candidate_record *records,
    size_t record_count, int32_t raw_lower_bound,
    int32_t raw_upper_bound, int32_t warmup_count,
    int32_t warmup_limit, float scale,
    goodix_primitives_hr_candidate_selection *selection);
/* 0x0006D51C: GH_HR sample orchestration, periodic candidate extraction,
 * quality classification, history fallback, and reference-rate recovery. */
bool goodix_primitives_hr_process(
    const goodix_primitives_hr_process_input *input,
    const goodix_primitives_hr_process_plan *plan,
    goodix_primitives_hr_process_state *state,
    goodix_primitives_hr_process_workspace *workspace,
    int32_t output[6]);
/* 0x00030090: update three capped running means and bind the caller-supplied
 * current timestamp. Once full, the fixed capacity remains the divisor. */
bool goodix_primitives_running_triplet_update(
    goodix_primitives_running_triplet *state, float first, float second,
    float third, uint32_t timestamp);
/* 0x00032808: consume the pending GH_HR feature event, maintain the fixed
 * record/history windows, update diagnostics and running baselines, and run
 * the recovered feature/event decision state machine. The context signature
 * permits direct use as goodix_primitives_hr_process_plan.decision_core. */
bool goodix_primitives_hr_decision_update(void *context);
bool goodix_primitives_float_window_mean(
    const goodix_primitives_decimated_float_window *window, float *result);
bool goodix_primitives_float_window_remove(
    goodix_primitives_decimated_float_window *window, size_t index,
    float *removed);
bool goodix_primitives_i16_window_push(
    goodix_primitives_i16_window *window, int16_t value);
bool goodix_primitives_byte_window_push(
    goodix_primitives_byte_window *window, uint8_t value);
bool goodix_primitives_decimated_i16_window_push(
    goodix_primitives_decimated_i16_window *window, int16_t value);
bool goodix_primitives_decimated_float_window_push(
    goodix_primitives_decimated_float_window *window, float value);
bool goodix_primitives_truncate_decimal(float value, uint8_t places,
                                        float *result);
bool goodix_primitives_bit_reverse_permute_pairs(
    goodix_primitives_word_pair *pairs, size_t pair_count,
    uint8_t bit_count);
/* 0x000768B8: fixed 128-point complex radix-2 DIF transform over 256
 * interleaved Float32 values. Output pairs remain in bit-reversed order. */
bool goodix_primitives_fft_complex_128_dif(
    float *interleaved, size_t value_count);
/* 0x00075E1C: zero-pad a real signal to 256 samples, run the recovered
 * complex core and bit permutation, and emit bins 0..128 in place. The
 * stock transform deliberately replaces the DC magnitude with zero. */
bool goodix_primitives_fft_real_magnitude_256(
    float *values, size_t value_capacity, size_t input_count,
    goodix_primitives_float_unary_fn square_root);
bool goodix_primitives_finalize_warmup_average(
    goodix_primitives_warmup_average_state *state);
bool goodix_primitives_normalize_by_max(float *values, size_t count);
/* 0x00095750: choose the maximum absolute magnitude, cap it at exact
 * Float32 0.02, zero outputs below exact Float32 1e-7, otherwise clamp and
 * divide into [-1, 1]. */
bool goodix_primitives_nadt_clip_normalize(
    const float *input, size_t count, float *output, size_t output_capacity);
/* 0x000968C4: prepare both tail windows, execute the one-lane generated NADT
 * graph through an explicit provider, and clamp its scalar result to [0,2]. */
int32_t goodix_primitives_nadt_inference_bridge(
    const goodix_primitives_nadt_inference_source *source,
    const goodix_primitives_nadt_inference_configuration *configuration,
    uint8_t selector, goodix_primitives_seven_word_operation_fn execute,
    float *primary_scratch, size_t primary_scratch_capacity,
    float *normalized_workspace, size_t normalized_workspace_capacity,
    float *output);
/* 0x00037A84: append the perfect terminal phase, then derive RMS phase
 * dispersion and a 0..100 mean-absolute phase-quality score. */
bool goodix_primitives_nadt_peak_dispersion_quality(
    float *values, size_t value_capacity,
    uint16_t *phase_indices, size_t phase_capacity,
    size_t count, uint32_t period,
    goodix_primitives_float_unary_fn square_root,
    float *dispersion, float *quality);
/* 0x0003E6C8: right-endpoint Gaussian interval integration with exact
 * Float32 2*pi and binary64 exp/multiply/add intermediates. */
bool goodix_primitives_nadt_gaussian_interval_probability(
    float lower, float upper, float mean, float deviation, float step,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn exponential,
    float *probability);
/* 0x00066B30: mirror-pad signed samples and apply an odd-length Float32
 * finite-impulse-response kernel. Caller scratch replaces stock allocation. */
bool goodix_primitives_nadt_symmetric_fir_i32(
    const int32_t *input, size_t count,
    const float *coefficients, size_t coefficient_count,
    int32_t *output, size_t output_capacity,
    int32_t *scratch, size_t scratch_capacity);
/* 0x00030B6C: combine optional eleven-sample boundary projections with the
 * exact uniform 23-tap reflected FIR interior. The recovered 11x23 boundary
 * matrix is an explicit typed binding; both transient buffers are caller-owned. */
bool goodix_primitives_nadt_window_filter_i32(
    const int32_t *input, size_t count,
    int32_t *output, size_t output_capacity, uint32_t boundary_flags,
    const float *boundary_coefficients, size_t boundary_coefficient_count,
    int32_t *filtered_scratch, size_t filtered_scratch_capacity,
    int32_t *fir_scratch, size_t fir_scratch_capacity);
/* 0x00042BD0: select periodic peak positions, reject unstable adjacent
 * intervals, calculate a 1500-unit rate, round half up, and clamp to 40..200. */
bool goodix_primitives_nadt_periodic_peak_rate(
    const float *amplitudes, const uint16_t *positions, size_t count,
    int32_t *selected_scratch, size_t selected_scratch_capacity,
    int32_t *difference_scratch, size_t difference_scratch_capacity,
    int32_t *rate);
/* 0x00029144: extract the two fixed tail autocorrelation/peak feature sets,
 * retain the stock Float16 quantization of the primary autocorrelation, and
 * report its normalized correlation with the secondary autocorrelation. */
bool goodix_primitives_nadt_dual_window_features_extract(
    const goodix_primitives_nadt_dual_window_source *source,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_dual_window_workspace *workspace,
    goodix_primitives_nadt_dual_window_result *result);
/* 0x00095828: consume the typed 0x00029144 dual-window result, classify
 * interval variation, gate the rolling rate history, and update its
 * zero-centered Gaussian confidence probability. The stock heap scratch is
 * replaced by an exact 124-float caller workspace. */
bool goodix_primitives_nadt_signal_confidence_update(
    const goodix_primitives_nadt_dual_window_result *features,
    const uint16_t *interval_positions, size_t interval_position_count,
    bool enabled, goodix_primitives_nadt_signal_confidence_state *state,
    goodix_primitives_nadt_signal_confidence_workspace *workspace,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn exponential,
    goodix_primitives_nadt_signal_confidence_diagnostics *diagnostics);
/* 0x00036F88: select the one-lane NADT rate/output kind through the recovered
 * five-state latch. Rate history and configuration flags replace the stock
 * private 0x44-byte record and absolute configuration offsets. */
bool goodix_primitives_nadt_output_state_select(
    const goodix_primitives_nadt_output_selection_configuration *configuration,
    uint32_t sample_index,
    goodix_primitives_nadt_output_selection_state *state,
    float *output_rate, uint8_t *output_kind);
/* 0x0006E838: compose the exact GH_NADT preprocessing stage order with
 * caller-owned replacements for its five heap temporaries. The enum-backed
 * plan binds the already reconstructed leaf APIs without private pointers. */
int32_t goodix_primitives_nadt_preprocess_execute(
    const goodix_primitives_nadt_preprocess_plan *plan,
    const void *source, goodix_primitives_nadt_preprocess_state *state,
    goodix_primitives_nadt_preprocess_workspace *workspace,
    uint32_t *output_words, size_t output_word_count);
/* 0x0007DD58: classify the fixed 200-sample alternate NADT state from two
 * local autocorrelation passes, strict signed extrema, peak quality, and
 * alternating interval regularity. Five stock allocations are caller-owned. */
bool goodix_primitives_nadt_alternate_state_classify(
    const int16_t *samples, size_t count,
    const goodix_primitives_nadt_alternate_configuration *configuration,
    goodix_primitives_nadt_alternate_state *state,
    goodix_primitives_nadt_alternate_workspace *workspace,
    goodix_primitives_nadt_alternate_diagnostics *diagnostics,
    int32_t *result);
/* 0x00047240: classify paired NADT Int32 windows from activity, residual,
 * periodicity, and quality evidence. All stock heap allocations and absolute
 * configuration/state bindings are explicit caller-owned objects. */
bool goodix_primitives_nadt_primary_signal_classify(
    const int32_t *primary, const int32_t *secondary, size_t count,
    const goodix_primitives_nadt_primary_configuration *configuration,
    goodix_primitives_nadt_window_state *state,
    goodix_primitives_nadt_primary_workspace *workspace,
    goodix_primitives_autocorrelation_state *autocorrelation_state,
    goodix_primitives_float_unary_fn round_provider,
    goodix_primitives_nadt_primary_diagnostics *diagnostics,
    uint8_t *result);
/* 0x000856EC: fuse the four-window NADT energy/range history with the
 * primary, auxiliary, and alternate classifiers. Stock absolute globals are
 * explicit bounded inputs, state, diagnostics, and typed dependencies. */
bool goodix_primitives_nadt_window_classify(
    const goodix_primitives_nadt_window_configuration *configuration,
    const goodix_primitives_nadt_window_input *input,
    const goodix_primitives_nadt_window_plan *plan,
    goodix_primitives_nadt_window_state *state,
    goodix_primitives_nadt_window_diagnostics *diagnostics,
    int32_t *result);
/* 0x00037B80: classify the final 50 signed samples from their range,
 * rounded sample deviation, strict extrema, and extrema clustering. The
 * stock spin-wait is represented by a checked processing-state rejection. */
bool goodix_primitives_nadt_auxiliary_state_classify(
    int16_t *values, size_t count,
    const goodix_primitives_nadt_auxiliary_configuration *configuration,
    bool transition_enabled,
    goodix_primitives_nadt_auxiliary_state *state,
    goodix_primitives_nadt_auxiliary_workspace *workspace,
    goodix_primitives_nadt_auxiliary_diagnostics *diagnostics,
    goodix_primitives_float_unary_fn square_root, uint32_t *result);
/* 0x0002FF10: locate the strongest strict interior spectral peak and report
 * the local-energy concentration in decibels through an explicit log10. */
bool goodix_primitives_spo2_spectral_peak_concentration_db(
    const float *spectrum, size_t count, size_t radius,
    goodix_primitives_float_unary_fn logarithm_base_10,
    float *concentration_db, float *peak_index);
/* 0x00029AD8: clear and populate one report, apply the recovered candidate
 * acceptance gate, and advance the three-state event latch. */
bool goodix_primitives_spo2_report_state_update(
    goodix_primitives_spo2_report_state *state,
    uint32_t selected_value, int32_t reference_value,
    goodix_primitives_spo2_report_output *output,
    goodix_primitives_spo2_report_analyze_fn analyze, void *analyze_context);
/* 0x00034500: fill the exact 36-byte GH_SPO2/dlCom report analysis from
 * bounded spectra and four explicit rolling histories. */
bool goodix_primitives_spo2_report_analyze(
    const goodix_primitives_spo2_report_analyzer_input *input,
    goodix_primitives_spo2_report_analyzer_state *state,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_float_unary_fn logarithm_base_10,
    goodix_primitives_spo2_report_analysis *analysis);
/* 0x00034B54: decode four packed-6/9 channels and report population standard
 * deviation, decimating the first three channels by three. */
bool goodix_primitives_spo2_packed_channel_standard_deviations(
    const goodix_primitives_packed_u16_span channels[4],
    float output[4], float *scratch, size_t scratch_capacity,
    goodix_primitives_float_unary_fn square_root);
/* 0x00061DA4: validate the three packed channel groups, assemble fixed
 * 24-byte records, and expose the private scaling helper as a typed provider. */
bool goodix_primitives_spo2_channel_records_assemble(
    const goodix_primitives_spo2_channel_source *source,
    int32_t sequence, uint32_t expected_record_count,
    goodix_primitives_spo2_channel_output *output,
    goodix_primitives_i32_unary_fn integrity_transform,
    goodix_primitives_spo2_channel_decode_fn decode,
    bool *count_mismatch);
/* 0x000335B4: decode one direct or packed channel value and apply the
 * recovered scale-code/divisor formula through explicit table and pow
 * bindings. The callback signature plugs directly into 0x00061DA4. */
void goodix_primitives_spo2_channel_scale_decode(
    void *context, uint8_t channel, uint16_t group, float destination[2]);
/* 0x0006671C + 0x0009285E: one-sample cascaded direct-form-II filter,
 * including the recovered optional first-stage discontinuity correction. */
bool goodix_primitives_spo2_biquad_cascade_process(
    goodix_primitives_biquad_cascade *cascade, float input,
    bool update_previous, bool limit_discontinuity,
    int32_t discontinuity_limit, bool force_correction,
    float *output);
/* 0x000372B0: derive the signed four-to-eight-decimal residual after
 * log10-selected scaling; values below exact Float32 1e-6 leave output. */
bool goodix_primitives_spo2_decimal_residual(
    float value, goodix_primitives_float_unary_fn logarithm_base_10,
    float *output);
/* 0x00041F4C: update a sorted rolling window and select the newest value
 * unless its distance from the median exceeds IQR-or-five times scale. */
bool goodix_primitives_spo2_rolling_percentile_select(
    const float *source, size_t source_count,
    float *sorted, size_t *sorted_count, size_t sorted_capacity,
    float *prior_anchor, int32_t tolerance_scale, float *output);
/* 0x00028CF4: build a 60-sample mean, continue with a 59/60 exponential
 * update, and emit the rate-scaled positive mean every 25 samples after
 * warm-up. */
bool goodix_primitives_spo2_smoothed_scale(
    uint32_t sample_count, float sample, uint32_t rate,
    double *accumulator, int32_t *result);
/* 0x0003113C + 0x00031564: update the four optical-filter lanes and
 * motion histories, then initialize/advance the percentile-filtered motion
 * output banks without retaining stock RAM pointers or its temporary heap. */
bool goodix_primitives_spo2_stream_accumulate(
    goodix_primitives_warmup_average_state *sample,
    uint8_t filtering_mode,
    const goodix_primitives_spo2_stream_plan *plan,
    goodix_primitives_spo2_stream_state *state,
    goodix_primitives_spo2_stream_workspace *workspace);
/* 0x0006C6A8: complete GH_SPO2/dlCom per-sample processing root. The stock
 * global owner, two transient allocations, packed/spectral bindings, model
 * dispatch records, and report state are explicit typed caller bindings. */
uint32_t goodix_primitives_spo2_process(
    const goodix_primitives_spo2_process_configuration *configuration,
    const goodix_primitives_spo2_process_input *input,
    goodix_primitives_spo2_process_output *output,
    const goodix_primitives_spo2_process_plan *plan,
    goodix_primitives_spo2_process_state *state,
    goodix_primitives_spo2_stream_workspace *stream_workspace,
    goodix_primitives_spo2_process_workspace *workspace);
bool goodix_primitives_percentile_lookup(
    const float *values, size_t count, uint32_t percentage, float *result);
bool goodix_primitives_i32_mean(const int32_t *values, size_t count,
                                float *result);
bool goodix_primitives_i32_squared_deviation_sum(
    const int32_t *values, size_t count,
    goodix_primitives_float_unary_fn round_provider, uint32_t *result);
bool goodix_primitives_indexed_i16_trimmed_mean(
    const int16_t *values, size_t value_count, const int16_t *indices,
    size_t index_count, int16_t *result);
bool goodix_primitives_mask_columns_any(
    const uint8_t *packed_bits, size_t packed_bytes, size_t columns,
    size_t rows, uint8_t *output, size_t output_count);
bool goodix_primitives_channel_scale_copy(
    const float *source, size_t count, uint32_t mode,
    const float *mode_one_scales, float mode_one_factor,
    float *destination, size_t destination_count, float *factor);
/* 0x00035772: copy input into caller scratch, invoke the explicit transform
 * provider, and copy the requested transformed prefix to the destination. */
bool goodix_primitives_float_transform_prefix_copy(
    const float *input, size_t input_count, size_t transform_count,
    float *scratch, size_t scratch_capacity,
    float *output, size_t output_capacity, size_t output_count,
    goodix_primitives_float_transform_fn transform);
/* 0x000765E4: convert Float32 or packed-5/10 samples into caller scratch,
 * execute the recovered 256-sample magnitude transform, optionally apply
 * the stock 2/input_count scaling, and copy the requested prefix. Exactly
 * one input pointer, selected by packed_input, is required. */
bool goodix_primitives_fft_magnitude_prepare(
    const float *float_input, const uint16_t *packed_input,
    bool use_packed_input, size_t input_count, bool normalize,
    float *scratch, size_t scratch_capacity,
    float *output, size_t output_capacity, size_t output_count,
    goodix_primitives_float_unary_fn square_root);
/* 0x000708F8: prepare four normalized fixed-60 Float32 spectra and a fifth
 * spectrum formed by decimating and averaging four packed-6/9 channels. The
 * stock heap temporary and private +0x94..+0xAC bindings are caller-owned. */
bool goodix_primitives_spo2_normalized_spectra_prepare(
    const goodix_primitives_spo2_spectral_source *source,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_spo2_spectral_workspace *workspace,
    goodix_primitives_spo2_spectral_result *result);
/* 0x000766AC: complete fixed-125 GH_NADT spectral peak-preparation
 * pipeline. The stock -500-byte channel offset, private scale vector/factor,
 * heap temporaries, and 0x35850 harmonic selector are explicit bindings. */
bool goodix_primitives_nadt_spectral_peak_prepare(
    const goodix_primitives_nadt_spectral_source *source,
    goodix_primitives_nadt_harmonic_candidate_fn select_harmonics,
    void *harmonic_context, goodix_primitives_float_unary_fn square_root,
    goodix_primitives_float_unary_fn floor_provider,
    goodix_primitives_nadt_spectral_workspace *workspace,
    goodix_primitives_nadt_spectral_result *result);
/* 0x00035850: select a three-lane harmonic family from ranked spectral
 * peaks. The stock six allocations are one explicit fixed caller workspace. */
bool goodix_primitives_nadt_harmonic_candidates_select(
    void *context, float bin_width, const int32_t *peak_indices,
    const float *peak_values, size_t peak_count,
    int32_t *candidate_indices, uint8_t *candidate_flags,
    size_t candidate_capacity);
/* 0x00030CD8: type-5 interpolated quantile over caller-owned sort scratch. */
bool goodix_primitives_float_quantile_interpolated(
    const float *values, size_t count, float fraction,
    float *scratch, size_t scratch_capacity, float *result);
/* 0x0007309C: classify values outside the scaled interquartile interval as
 * signed low/high outliers. */
bool goodix_primitives_nadt_quartile_mask(
    const float *values, size_t count, float multiplier,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask, size_t mask_capacity);
/* 0x00030970: count nonzero mask entries, suppressing a uniformly signed
 * mask exactly as the stock wrapper does. */
bool goodix_primitives_nadt_nonuniform_mask_count(
    const float *values, size_t count, uint8_t multiplier_tenths,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask_scratch, size_t mask_capacity, int32_t *result);
/* 0x0002F2F8: summarize positive indexed differences, including the exact
 * final-zero recovery against the remaining-series minimum and 0.85..1.15
 * previous-difference band. */
bool goodix_primitives_nadt_positive_difference_statistics(
    const float *values, size_t value_count,
    const int32_t *first_indices, const int32_t *second_indices,
    size_t pair_count, goodix_primitives_nadt_difference_summary *summary);
/* 0x0007311E: complete local composition of 0x00030970 and 0x0002F2F8. */
bool goodix_primitives_nadt_difference_summary_execute(
    const float *values, size_t value_count,
    const int32_t *first_indices, const int32_t *second_indices,
    size_t pair_count, uint8_t multiplier_tenths,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask_scratch, size_t mask_capacity,
    goodix_primitives_nadt_difference_summary *summary, int32_t *result);
/* 0x00036DD4: update the five-stage rolling feature pipeline using the two
 * explicit 25-tap kernels recovered from the stock image. */
bool goodix_primitives_nadt_rolling_feature_update(
    float value, uint32_t sample_index, uint32_t average_period,
    goodix_primitives_nadt_rolling_feature_state *state);
/* 0x0002FEE2 (including its 0x0002F2AC shared tail): update one feature and
 * the separately accumulated pair average. */
bool goodix_primitives_nadt_feature_pair_update(
    const goodix_primitives_nadt_feature_pair *input,
    uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_feature_pair_state *state);
/* 0x0002F660: update both feature pairs, their bounded ratio products, and
 * the decimated half-scale primary sample. */
bool goodix_primitives_nadt_channel_ratio_update(
    const goodix_primitives_nadt_channel_input *input,
    uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_channel_state *state);
/* 0x00061C48: derive magnitude, magnitude delta, and cadence-averaged polar
 * angle from the signed three-axis vector. */
bool goodix_primitives_nadt_vector_geometry_update(
    const int32_t vector[3], uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_geometry_state *state,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn arc_tangent);
/* 0x000357CE: compose channel and geometry accumulation, returning stock
 * readiness status zero only at every 25th sample after the 125-sample
 * warm-up; all other successful calls return four. */
bool goodix_primitives_nadt_accumulation_execute(
    const goodix_primitives_nadt_channel_input *channel,
    const int32_t vector[3], uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_channel_state *channel_state,
    goodix_primitives_nadt_geometry_state *geometry_state,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn arc_tangent, int32_t *result);
/* 0x00072DCC: accumulate channel pairs and signed vector words across one
 * configured period, then emit per-channel and cross-channel averages. */
bool goodix_primitives_nadt_batch_accumulate(
    const goodix_primitives_nadt_batch_input *input,
    const goodix_primitives_nadt_batch_configuration *configuration,
    goodix_primitives_nadt_batch_state *state, int32_t *result);
/* 0x00076A68: serialize one completed NADT record to the exact sixteen-word
 * scaled integer result form. */
bool goodix_primitives_nadt_record_encode(
    const goodix_primitives_nadt_output_record *record,
    uint32_t output[16]);
/* 0x00036974: populate the completed record metrics and emit the same
 * sixteen-word form with the stock live-record marker at word twelve. */
bool goodix_primitives_nadt_output_record_build(
    bool reference_enabled, float metric, int8_t direction,
    const goodix_primitives_nadt_source_metrics *source,
    const goodix_primitives_nadt_reference_metrics *reference,
    float output_metric, goodix_primitives_nadt_output_record *record,
    uint32_t output[16]);
/* 0x00044A78: update saturating activity counters, append the newest metric,
 * select the configured tail span/tolerance, and emit stock quality bits. */
bool goodix_primitives_nadt_output_record_quality_update(
    const goodix_primitives_nadt_quality_configuration *configuration,
    uint8_t source_flags, float sample,
    goodix_primitives_nadt_output_record *record);
/* 0x00077D2C: align event indices in caller scratch, summarize both 125-sample
 * ratio tails, append pair-window means, and emit their cosine percentage. */
bool goodix_primitives_nadt_channel_analysis_execute(
    const goodix_primitives_nadt_channel_state *state,
    const goodix_primitives_event_pair_source *events, int32_t mode,
    uint8_t multiplier_tenths,
    int32_t *primary_index_scratch, int32_t *secondary_index_scratch,
    size_t index_scratch_capacity,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask_scratch, size_t mask_capacity,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_channel_analysis *analysis);
/* 0x00030178: construct the row-major packed extrema-neighborhood mask.
 * Caller-owned storage replaces the stock transient allocation. */
bool goodix_primitives_nadt_extrema_neighborhood_mask(
    const float *values, size_t count, size_t row_count,
    size_t plateau_radius, int32_t selector,
    uint8_t *packed_scratch, size_t packed_capacity);
/* 0x00076B78: select the mask row and reduce its prefix to one flag per
 * sample. Caller-owned packed storage replaces the stock heap buffer. */
bool goodix_primitives_nadt_peak_mask_columns(
    const float *values, size_t count,
    const goodix_primitives_nadt_peak_mask_configuration *configuration,
    int32_t selector, uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_flags, size_t column_capacity);
/* 0x00047FA8: collect zero-flagged extrema indices, retaining the newest
 * entries when the fixed-capacity output fills. */
bool goodix_primitives_nadt_peak_index_collect(
    const float *values, size_t count,
    const goodix_primitives_nadt_peak_mask_configuration *configuration,
    int32_t selector, uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_scratch, size_t column_capacity,
    int32_t *indices, size_t index_capacity, size_t *index_count);
/* 0x0003441C: collect both extrema polarities and append their threshold
 * crossings to the paired twelve-byte stock histories. */
bool goodix_primitives_nadt_peak_histories_update(
    const float *values, size_t count, int32_t mode,
    const goodix_primitives_nadt_peak_mask_configuration *configuration,
    uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_scratch, size_t column_capacity,
    int32_t *index_scratch, size_t index_capacity,
    goodix_primitives_threshold_history histories[2]);
/* 0x00030114: apply the fixed {36,2,1}, 125-sample, 20-index NADT peak
 * configuration to the tail of the primary-ratio window. */
bool goodix_primitives_nadt_primary_ratio_peak_update(
    const goodix_primitives_nadt_channel_state *state, int32_t mode,
    uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_scratch, size_t column_capacity,
    int32_t *index_scratch, size_t index_capacity,
    goodix_primitives_threshold_history histories[2]);
/* 0x00066900: build the multiscale local-maximum mask, choose the row with
 * the fewest non-maximum flags, and reduce its inclusive prefix by column. */
bool goodix_primitives_nadt_local_maximum_prefix_counts(
    const float *values, size_t count, size_t row_count,
    uint8_t *packed_scratch, size_t packed_capacity,
    int16_t *row_score_scratch, size_t row_score_capacity,
    int16_t *column_counts, size_t column_capacity);
/* 0x00036734: extract local peaks beyond warmup+1, including the recovered
 * equal-value plateau continuation rule. All stock heap storage is explicit. */
bool goodix_primitives_nadt_local_peak_indices(
    const float *values, size_t count, size_t row_count, size_t warmup,
    uint8_t *packed_scratch, size_t packed_capacity,
    int16_t *row_score_scratch, size_t row_score_capacity,
    int16_t *column_scratch, size_t column_capacity,
    int16_t *indices, size_t index_capacity, size_t *index_count);
/* 0x00092A04: centered full cross-correlation. The output has
 * 2*max(first_count, second_count)-1 elements; positions outside the shorter
 * input's centered nonzero span retain their caller-supplied values. */
bool goodix_primitives_centered_cross_correlation(
    const float *first, size_t first_count,
    const float *second, size_t second_count,
    float *output, size_t output_capacity);
/* 0x000666A4: retain the leading half of the equal-input correlation and
 * normalize it by its maximum when the maximum's signed Float32 bits meet
 * the recovered 0x358637BD threshold. */
bool goodix_primitives_nadt_normalized_autocorrelation(
    const float *values, size_t count, float *output, size_t output_capacity,
    float *correlation_scratch, size_t scratch_capacity);
bool goodix_primitives_i16_descriptor_mean(
    const goodix_primitives_buffer_descriptor *descriptor, int16_t *result);
/* 0x0003F89C: summarize at most 125 Int16 samples using the recovered
 * population deviation, configured min/max threshold, and strict outlier
 * count. */
bool goodix_primitives_nadt_sample_statistics(
    const goodix_primitives_nadt_threshold_configuration *configuration,
    const goodix_primitives_buffer_descriptor *descriptor,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_primary_summary *summary);
/* 0x00091870: append the secondary descriptor mean to 0x0003F89C's
 * four-byte summary and return the stock zero status. */
bool goodix_primitives_nadt_sample_summary_build(
    const goodix_primitives_nadt_summary_context *context,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_sample_summary *summary, int32_t *result);
/* 0x000290BC: build the summary, then forward the two recovered owner
 * bindings, both caller words, and summary pointer to the downstream stage. */
bool goodix_primitives_nadt_summary_dispatch(
    uintptr_t source, uintptr_t auxiliary,
    goodix_primitives_nadt_sample_summary *summary,
    const goodix_primitives_nadt_summary_context *context,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_five_word_operation_fn downstream, int32_t *result);
bool goodix_primitives_reverse_clamped_weighted_sum(
    const float *coefficients, size_t coefficient_count,
    const float *history, size_t history_count, size_t active_count,
    float *result);
bool goodix_primitives_extrema_history_update(
    goodix_primitives_extrema_history *state, int32_t sample,
    int32_t threshold, int32_t *transition);
bool goodix_primitives_normalize_rows_by_range(
    float *values, size_t row_count, size_t column_count);
bool goodix_primitives_record32_history_push(
    goodix_primitives_record32_history *history,
    const uint8_t record[32]);
/* 0x00037DEC: either split a qualifying pair about the recovered baseline
 * and retain both records, or discard one history slot and retain only the
 * second record. */
bool goodix_primitives_hr_rebalance_record_pair(
    float tolerance_scale, float baseline, int32_t gate_left,
    int32_t gate_right, goodix_primitives_record32_history *history,
    goodix_primitives_hr_event_record *first,
    goodix_primitives_hr_event_record *second);
bool goodix_primitives_select_mask_row(
    const uint8_t *packed_bits, size_t packed_bytes, size_t columns,
    uint16_t first_label, uint16_t last_label, uint16_t *selected_label);
bool goodix_primitives_logistic_score(float value, float threshold,
                                      float lower_scale, float upper_scale,
                                      goodix_primitives_float_unary_fn exp_provider,
                                      float *result);
/* 0x00088E80: update the first NADT quality record's six masked diagnostic
 * bits and exact 0.4/0.4/0.2 weighted logistic score. */
bool goodix_primitives_nadt_channel_quality_update(
    const goodix_primitives_nadt_channel_quality_configuration *configuration,
    const goodix_primitives_nadt_channel_quality_summary *summary,
    goodix_primitives_nadt_channel_quality_record *record,
    goodix_primitives_float_unary_fn exp_provider);

/* Additional exact leaf utilities from the closed Goodix call graph. */
void goodix_primitives_noop_a(void);
void goodix_primitives_noop_b(void);
int32_t goodix_primitives_zero_a(void);
int32_t goodix_primitives_zero_b(void);
uint32_t goodix_primitives_second_word(const uint32_t *words);
bool goodix_primitives_transformed_differs(
    int32_t value, goodix_primitives_i32_unary_fn transform);
uint32_t goodix_primitives_integrity_encode(uint32_t value);
bool goodix_primitives_integrity_invalid(uint32_t value);
uint32_t goodix_primitives_packed_5_10_to_f32_bits(uint16_t value);
uint32_t goodix_primitives_packed_6_9_to_f32_bits(uint16_t value);
uint16_t goodix_primitives_f32_bits_to_packed_5_10(uint32_t value);
/* 0x00028DDA six-byte head plus the shared tail at 0x000362F4: convert raw
 * Float32 bits to the recovered sign/6-bit-exponent/9-bit-fraction format. */
uint16_t goodix_primitives_f32_bits_to_packed_6_9(uint32_t value);
/* 0x0003F740: conditionally expand one 180-value packed-6/9 source into
 * three identical Float32 workspace banks after the recovered 720-value
 * prefix. */
bool goodix_primitives_spo2_expand_packed_triplicate(
    uint8_t disabled_flag, uint8_t ready_flag,
    const uint16_t *packed_values, size_t packed_count,
    float *workspace, size_t workspace_count);
/* 0x00037F54: expand all seven hidden 180-value packed-6/9 banks into the
 * complete 1,260-value Float32 workspace. */
bool goodix_primitives_spo2_expand_packed_banks(
    const uint16_t *const
        banks[GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT],
    float *workspace, size_t workspace_count);
bool goodix_primitives_u32_to_u16_transform(
    uint16_t *destination, const uint32_t *source, size_t count,
    goodix_primitives_u32_to_u16_fn transform);
bool goodix_primitives_transform_in_place(
    int32_t *value, goodix_primitives_i32_unary_fn transform);
int32_t goodix_primitives_initialize_status(
    goodix_primitives_status_fn initialize);
bool goodix_primitives_is_evenly_divisible(uint32_t total,
                                            uint32_t divisor);
float goodix_primitives_unsigned_power(float base, uint8_t exponent);
bool goodix_primitives_float_buffer_full(
    const goodix_primitives_float_buffer *buffer);
float goodix_primitives_float_buffer_get(
    const goodix_primitives_float_buffer *buffer, size_t index,
    float fallback);
bool goodix_primitives_float_buffer_mean(
    const goodix_primitives_float_buffer *buffer, float *result);
bool goodix_primitives_float_buffer_standard_deviation(
    const goodix_primitives_float_buffer *buffer,
    goodix_primitives_float_unary_fn square_root, float *result);
/* 0x00070B60: clamp multiplier-scaled sample deviation between the recovered
 * threshold bounds, then count mean-distance outliers overall and from index
 * 100 onward. Counts retain the stock UInt8 wrapping before widening. */
bool goodix_primitives_hr_count_mean_outliers(
    const goodix_primitives_float_buffer *buffer, size_t scan_count,
    float maximum_threshold, float minimum_threshold,
    float deviation_multiplier,
    goodix_primitives_float_unary_fn square_root,
    uint32_t *outlier_count, uint32_t *tail_outlier_count);
const uint16_t *goodix_primitives_nadt_result_binding(
    const uint16_t *result_words);
const void *goodix_primitives_hrv_configuration_binding(
    const void *configuration);
int8_t goodix_primitives_centered_i8(int32_t value);
float goodix_primitives_float_sum(const float *values, size_t count);
bool goodix_primitives_decrement_counter(int32_t *counter);
void *goodix_primitives_tensor_descriptor_initialize(
    goodix_primitives_tensor_descriptor *descriptor, uint32_t batches,
    uint32_t rows, uint32_t columns, uint32_t element_bytes, void *data);
/* 0x0006F838: execute three UInt8 tensor stages over one workspace. The
 * middle stage uses the recovered +0x3E0-byte workspace bank; the final
 * descriptor replaces the caller state descriptor. */
bool goodix_primitives_three_stage_u8_pipeline(
    const goodix_primitives_tensor_stage_fn stages[3],
    void *const stage_contexts[3],
    const goodix_primitives_tensor_binding *input,
    goodix_primitives_tensor_binding *state,
    const uint8_t dimensions[6], size_t workspace_bytes);
/* 0x00037890: explicit seven-stage NADT generated-graph topology around two
 * 0x34194 subgraphs. Stock model callbacks, recurrent state, and the implicit
 * +0x3E0/+0x7C0/+0x8B8 workspace banks are typed caller bindings. */
bool goodix_primitives_nadt_generated_graph_execute(
    const goodix_primitives_nadt_generated_graph *graph,
    const float *input, size_t input_count,
    float *workspace, size_t workspace_count, bool reset_recurrent_state,
    float *output, size_t output_capacity);
/* 0x00034194: execute the fixed generated NADT subgraph in-place across its
 * 0x7C0-byte workspace. All nineteen stock operator vectors and both
 * quantization range words are explicit typed plan fields. */
bool goodix_primitives_nadt_generated_subgraph_execute(
    const goodix_primitives_nadt_generated_subgraph *subgraph,
    float *workspace, size_t workspace_count);
uint32_t goodix_primitives_filter_code(uint32_t value);
uint32_t goodix_primitives_word_window_last(
    const goodix_primitives_word_window *window, uint32_t fallback);
uint16_t goodix_primitives_word_window_count(
    const goodix_primitives_word_window *window);
bool goodix_primitives_store_version_qualifier(uint16_t *destination);
bool goodix_primitives_copy_process_version_v1_1(char *destination,
                                                 size_t capacity);
bool goodix_primitives_copy_process_version_v1_0(char *destination,
                                                 size_t capacity);
bool goodix_primitives_reverse_low_bits(uint32_t value, uint8_t bit_count,
                                        uint32_t *result);
bool goodix_primitives_float_mean(const float *values, size_t count,
                                  float *result);
bool goodix_primitives_sample_variance(const float *values, size_t count,
                                       float *result);
bool goodix_primitives_sample_standard_deviation(
    const float *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
/* 0x00036394: Int16 sample standard deviation using the recovered centered
 * integer formulation and target-width modular accumulators. Invalid or
 * singleton inputs reproduce the stock zero result. */
bool goodix_primitives_i16_sample_standard_deviation(
    const int16_t *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
/* 0x000663B4: UInt8 population standard deviation. A zero populated count
 * retains the stock no-write result and reports false through the typed API. */
bool goodix_primitives_u8_population_standard_deviation(
    const uint8_t *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
/* 0x000377D8: dot(left,right)/(norm(left)*norm(right)), returned only when
 * strictly positive; zero norms, negative correlation, and invalid input
 * produce the recovered zero result. */
bool goodix_primitives_positive_cosine_similarity(
    const float *left, const float *right, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
/* 0x00087618: run the admitted alternating-extrema state machine and collect
 * its emitted rising, falling, and combined sample indices. */
bool goodix_primitives_collect_extrema_indices(
    const int32_t *samples, size_t count, int32_t threshold,
    int16_t *rising_indices, size_t rising_capacity,
    int16_t *falling_indices, size_t falling_capacity,
    int16_t *transition_indices, size_t transition_capacity,
    goodix_primitives_extrema_index_counts *counts);
/* 0x00030E1C: copy the source triplet when the wrapping timestamp delta is
 * greater than twenty and its gate is strictly between zero and thirty. */
bool goodix_primitives_copy_fresh_gated_triplet(
    goodix_primitives_timed_triplet_destination *destination,
    const goodix_primitives_timed_triplet_source *source, bool *copied);
/* 0x000419C8: append threshold crossings to the fixed-capacity history and
 * retain the stock cursor/emitted-count bookkeeping. */
bool goodix_primitives_accumulate_threshold_crossings(
    const int32_t *samples, size_t count, int32_t mode,
    goodix_primitives_threshold_history *history);
/* 0x00031774: select the greatest strictly positive interior sample that is
 * also strictly greater than both immediate neighbors. */
bool goodix_primitives_strict_local_peak_max(
    const float *values, size_t count, float *peak, uint32_t *index);
/* 0x000299EC: merge one fixed five-float record into a six-float state using
 * the stock continuation/advance branch and zero-clamped gap. */
bool goodix_primitives_merge_six_float_state(
    float state[6], const float incoming[5], bool advance);
/* 0x00072FB8: a marker on a nonzero sample zeroes its complete contiguous
 * same-sign run; unmarked samples are copied and marked zero/NaN is untouched. */
bool goodix_primitives_zero_masked_sign_runs(
    const float *source, const uint8_t *markers, size_t count, float *output);
/* 0x0005CED4: update one lane of signed min/max and Float32 online
 * mean/squared-deviation state using the caller's unsigned ordinal. */
bool goodix_primitives_running_i32_statistics_update(
    goodix_primitives_running_i32_statistics *state,
    int32_t sample, uint32_t ordinal);
/* 0x00028B18: evaluate the recovered second-order difference equation and,
 * unless denominator[0] is exactly +1.0f, divide and round through the
 * standard-double provider before returning Float32. */
bool goodix_primitives_second_order_difference_output(
    float input, const float numerator[3], const float denominator[3],
    const float input_history[2], const float output_history[2],
    goodix_primitives_double_unary_fn round_provider, float *result);
/* 0x000373A4: correct a discontinuous first input-history pair, run the
 * recovered two-stage second-order cascade, update all four history pairs,
 * and round the final Float32 value through the standard-double provider. */
bool goodix_primitives_nadt_optical_sample_transform(
    goodix_primitives_nadt_optical_transform *transform, float input,
    goodix_primitives_double_unary_fn round_provider, float *output);
/* 0x00036034: prepare three NADT lanes, report sequence/scale changes, and
 * apply the recovered seven-level calibrated conversion when enabled. */
bool goodix_primitives_nadt_sample_prepare(
    goodix_primitives_nadt_sample_preparation_state *state,
    const goodix_primitives_nadt_sample_preparation_input *input,
    int32_t output[3], uint16_t *configuration_changed);
/* 0x0006E008: run the recovered 25-sample NADT streaming cadence over typed
 * sample preparation, optical transform, histories, activity lanes, and the
 * now-local window classifier. All stock RAM banks are caller workspace. */
bool goodix_primitives_nadt_stream_process(
    const goodix_primitives_nadt_stream_input *input,
    const goodix_primitives_nadt_stream_plan *plan,
    goodix_primitives_nadt_stream_state *state,
    goodix_primitives_nadt_stream_workspace *workspace,
    goodix_primitives_nadt_window_diagnostics *window_diagnostics,
    goodix_primitives_nadt_stream_output *output);
/* 0x00034B08: issue command 0xA6 for flag bit 13, otherwise issue 0xAE and
 * poll register 0xAE until clear or the wrapping 320-tick timeout. */
bool goodix_primitives_command_status_poll(
    const goodix_primitives_command_poll_ops *operations,
    uint32_t flags, int32_t *result);
/* 0x0003E6B0: release +0x260 first, then the missed internal destructor at
 * 0x00029354 releases +0x1C0, +0x1DC, +0x1F4, and the root context. */
int32_t goodix_primitives_algorithm_context_destroy(
    goodix_primitives_algorithm_context_ownership *context,
    goodix_primitives_release_fn release, void *release_context);
/* 0x00029BBC: release the three recovered record families in their exact
 * stock call order.  The last two families are release-and-clear slots. */
int32_t goodix_primitives_record_family_teardown(
    goodix_primitives_record_family_ownership *ownership,
    goodix_primitives_release_fn release, void *release_context);
/* 0x000567C4: median through the recovered descending-selection helper.
 * Caller-owned scratch replaces the stock transient heap allocation. */
bool goodix_primitives_float_median(
    const float *values, size_t count, float *scratch,
    size_t scratch_capacity, float *median);
/* 0x0003DE20: median-absolute-deviation inlier mask using the exact
 * binary64 1.4826 scale. Caller scratch replaces the stock allocation. */
bool goodix_primitives_hr_mad_inlier_mask(
    const float *values, size_t count, int32_t deviation_multiplier,
    float *scratch, size_t scratch_capacity,
    uint8_t *mask, size_t mask_capacity);
/* 0x00028AD4: dispatch through one of seven operations selected by record[0].
 * Supplying the table explicitly replaces the copied absolute ROM table. */
bool goodix_primitives_dispatch_indexed_operation(
    uint32_t *record,
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT],
    uintptr_t first, uintptr_t second, uintptr_t third,
    uintptr_t fourth, uintptr_t fifth, int32_t *result);
/* 0x0002907C: explicit-provider form of the seven-argument NADT graph
 * executor veneer.  Raw AAPCS flow preserves four register arguments and
 * forwards all three caller stack arguments without transformation. */
bool goodix_primitives_nadt_graph_execute_veneer(
    goodix_primitives_seven_word_operation_fn execute,
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth, uintptr_t sixth, uintptr_t seventh, int32_t *result);
/* 0x0002A65C: send the fixed AA AA payload through the explicitly bound
 * provider operation and selector. */
bool goodix_primitives_send_fixed_aa_pair(
    uint8_t selector, uint32_t first, uint32_t second,
    goodix_primitives_payload_send_fn send, void *send_context);
/* 0x0003497C: append period-1 to the signed-index history, average the
 * normalized position/amplitude error, clamp it to 0.5, and emit 0..100. */
bool goodix_primitives_peak_quality_update(
    const int16_t *samples, size_t sample_count,
    int16_t *indices, size_t index_capacity, uint8_t *index_count,
    int32_t period, int32_t amplitude_scale, uint8_t *quality);
/* 0x00031624 / 0x00035F70: normalized modular-Int32 autocorrelation over
 * Int16 or Int32 samples, with the shared tie-break state made explicit. */
bool goodix_primitives_i16_autocorrelation_transform(
    const int16_t *samples, int16_t *output, size_t count,
    int32_t mean, int32_t scale,
    goodix_primitives_autocorrelation_state *state);
bool goodix_primitives_i32_autocorrelation_transform(
    const int32_t *samples, int16_t *output, size_t count,
    int32_t mean, int32_t scale,
    goodix_primitives_autocorrelation_state *state);
/* 0x0002E8CC: invoke the admitted GH3X2X register operations with the exact
 * reset constants and stock ordering. */
bool goodix_primitives_reset_register_fields(
    const goodix_primitives_register_configuration_ops *operations);
/* 0x0005CEA8: copy the input word, dispatch the recovered five bindings, and
 * return whether the propagated signed result is nonzero. */
bool goodix_primitives_dispatch_word_copy(
    const uint32_t *input, uint32_t *output,
    const goodix_primitives_word_dispatch_context *context,
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT]);
/* 0x000367C4: expose a transient four-word input history to one indexed
 * operation, restore it, and map the operation's logit to a 0..100 score.
 * Caller-owned four-word scratch replaces the stock temporary allocation. */
bool goodix_primitives_spo2_dispatch_logistic_score(
    goodix_primitives_spo2_score_context *context, float input,
    float *output, uint32_t history_scratch[4],
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT],
    goodix_primitives_float_unary_fn exponential);
/* 0x0005CDF8: gate one indexed operation through selected-slot elapsed
 * accounting, optionally clear the three mode-one buffers, and scale a
 * successful Float32 output through the recovered constant pipeline. */
uint32_t goodix_primitives_timed_dispatch_scaled_output(
    uintptr_t input, size_t slot, float *output,
    const goodix_primitives_timed_dispatch_context *context,
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT]);
/* 0x00035084: return an integral Float32 by rounding to nearest with exact
 * half values away from zero. */
float goodix_primitives_round_float_half_away_from_zero(float value);
/* 0x0006CC60: destroy the record family, dispatch three state destructors,
 * release-and-clear four owned slots, and finally release the owner. */
int32_t goodix_primitives_processing_context_destroy(
    goodix_primitives_record_family_ownership *record_family,
    goodix_primitives_processing_context_ownership *context,
    const goodix_primitives_state_handler_fn
        handlers[GOODIX_PRIMITIVES_STATE_COUNT],
    goodix_primitives_release_fn release, void *release_context);
/* 0x00061F04: recovered two-pass incremental sample standard deviation
 * over a caller-bounded strided float vector. */
bool goodix_primitives_strided_sample_standard_deviation(
    const float *values, size_t value_count, size_t stride, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
/* 0x00066430: nonempty float-buffer wrapper around 0x00061F04. */
bool goodix_primitives_float_buffer_incremental_standard_deviation(
    const goodix_primitives_float_buffer *buffer,
    goodix_primitives_float_unary_fn square_root, float *result);
bool goodix_primitives_sample_variance_or_zero(
    const float *values, size_t count, float *result);
bool goodix_primitives_population_variance_or_zero(
    const float *values, size_t count, float *result);
bool goodix_primitives_sample_standard_deviation_or_zero(
    const float *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
bool goodix_primitives_population_standard_deviation_or_zero(
    const float *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result);
float goodix_primitives_sum_squares(const float *values, size_t count);
float goodix_primitives_dot_product(const float *left, const float *right,
                                    size_t count);
int32_t goodix_primitives_copy_indexed_record(
    const uint8_t *records, size_t record_count, int32_t index,
    uint8_t destination[32]);
int32_t goodix_primitives_round_nearest(float value);
bool goodix_primitives_transform_packed24_lsb(
    uint8_t *records, size_t length, goodix_primitives_i32_unary_fn transform);
bool goodix_primitives_visit_packed24(
    const uint8_t *records, size_t length,
    goodix_primitives_i32_unary_fn visitor);
bool goodix_primitives_swap_u16_bytes(uint8_t *bytes, size_t length);
bool goodix_primitives_i32_range(const int32_t *values, size_t count,
                                 int32_t *maximum, int32_t *minimum,
                                 int32_t *range);
bool goodix_primitives_processing_record_initialize(
    uint8_t *destination, size_t destination_length,
    const uint8_t *source, size_t source_length);
/* 0x00036C32 and its one-record indirect veneer at 0x00036282. */
bool goodix_primitives_update_transition(uint8_t *record, size_t length,
                                         uint8_t state,
                                         uint8_t source_flag);
bool goodix_primitives_sort_floats(float *values, size_t count);
/* 0x000368D0: sort a scratch copy, derive quartiles, and replace source
 * samples outside the signed-factor-scaled interquartile band with the
 * selected median. */
bool goodix_primitives_replace_far_from_median(
    float *values, size_t count, int32_t spread_factor,
    float *sort_scratch, size_t scratch_capacity);
/* 0x00035812: stable ascending insertion sort. NaNs retain the stock
 * comparison behavior and move before every preceding element. */
bool goodix_primitives_insertion_sort_floats(float *values, size_t count);
/* 0x00036EFC: retain the largest requested strided samples in descending
 * order, inserting equal values before older equal values. */
bool goodix_primitives_top_descending_strided(
    float *output, size_t output_capacity, const float *source,
    size_t source_value_count, size_t stride, size_t sample_count,
    size_t selected_count);
/* 0x00098E4C: collect strict local maxima/minima indices from Int16 input.
 * Either output family may be omitted, matching the two optional stock
 * scans; counts retain the recovered UInt8 contract. */
bool goodix_primitives_i16_local_extrema_indices(
    const int16_t *values, size_t count,
    int16_t *maximum_indices, size_t maximum_capacity,
    uint8_t *maximum_count, int16_t *minimum_indices,
    size_t minimum_capacity, uint8_t *minimum_count);
/* 0x00034490: for each coefficient group and input row, dot the group with
 * a column-major row slice and emit group-major row outputs. */
bool goodix_primitives_grouped_row_weighted_sums(
    const float *coefficients, size_t coefficient_value_count,
    size_t group_count, size_t coefficient_count,
    const float *values, size_t value_count, size_t row_count,
    float *output, size_t output_count);
/* 0x00048018: evaluate the recovered four-control-point cardinal spline.
 * The signed shape parameter is converted to Float32 before the stock
 * half-tension matrix is assembled. */
bool goodix_primitives_cardinal_spline_point(
    float parameter, const goodix_primitives_point2f control_points[4],
    int32_t shape_parameter, goodix_primitives_point2f *output);
/* 0x0003773C: emit subdivisions + 1 evenly spaced spline points, including
 * both endpoints.  The stock GH_HR callers use shape parameter zero. */
bool goodix_primitives_sample_cardinal_spline(
    const goodix_primitives_point2f control_points[4],
    int32_t shape_parameter, size_t subdivisions,
    goodix_primitives_point2f *output, size_t output_capacity);
/* 0x00034CBC: update the GH_HR trough/peak tracker from the final two values
 * of a full rolling buffer. Mode one refines extrema through the recovered
 * four-point cardinal spline and a caller-owned 41-point workspace. */
bool goodix_primitives_hr_extrema_tracker_update(
    const goodix_primitives_float_buffer *history,
    int32_t signal_mode, uint32_t interpolation_mode,
    int32_t position_base, int32_t period,
    goodix_primitives_hr_extrema_tracker *tracker,
    const goodix_primitives_hr_extrema_curve *trough_curve,
    const goodix_primitives_hr_extrema_curve *peak_curve,
    goodix_primitives_hr_extrema_workspace *workspace);
/* 0x0006CCC0: emit the exact GH_SPO2/dlCom input diagnostics through typed
 * sinks. A zero timestamp emits the nine initial configuration records;
 * non-NULL input emits the dynamic records. The stock formatter and direct
 * routes are retained as separate sinks without exposing a variadic ABI. */
bool goodix_primitives_spo2_input_diagnostics_emit(
    const goodix_primitives_spo2_diagnostic_configuration *configuration,
    const goodix_primitives_spo2_diagnostic_input *input,
    const goodix_primitives_spo2_diagnostic_plan *plan);
/* 0x000481A4: align one secondary timestamp into each primary interval,
 * falling back to the adjusted primary value when no secondary fits. */
bool goodix_primitives_align_event_pairs(
    int32_t mode, const goodix_primitives_event_pair_source *source,
    int32_t *primary_output, int32_t *secondary_output,
    size_t output_capacity, size_t *produced_count);
/* 0x00036BFA / thunk 0x0002F65C: when mode is one, clear the three
 * recovered float-buffer bindings.  Stock read the pointers/counts from
 * state offsets 0x1C0/0x1BC, 0x1DC/0x1D8, and 0x1F4/0x1F0; this interface
 * makes those bindings and their extents explicit. */
bool goodix_primitives_clear_mode_buffers(
    const goodix_primitives_float_span buffers[3], uint32_t mode);
/* 0x00043B30 / thunk 0x00099010: update both elapsed counters relative to
 * the prior baseline from one explicitly bounded slot timestamp. */
bool goodix_primitives_update_elapsed_slot(
    goodix_primitives_elapsed_state *state, size_t slot);
bool goodix_primitives_sorted_insert(float *values, size_t *count,
                                     size_t capacity, float value);
float goodix_primitives_float_mean_or_zero(const float *values,
                                           size_t count);
bool goodix_primitives_word_window_full(
    const goodix_primitives_word_window *window);
bool goodix_primitives_i16_mean(const int16_t *values, size_t count,
                                int16_t *result);
bool goodix_primitives_i16_min_index(const int16_t *values, size_t count,
                                     size_t *index);
bool goodix_primitives_float_min_index(const float *values, size_t count,
                                       float *minimum, size_t *index);
bool goodix_primitives_float_max_index(const float *values, size_t count,
                                       float *maximum, size_t *index);
bool goodix_primitives_release_and_clear(
    void **allocation, goodix_primitives_release_fn release,
    void *release_context);
/* 0x0006DAD0 / thunk 0x0006DB58: complete GH_HRV context teardown.
 * The eleven subobject bindings correspond, in stock call order, to state
 * offsets 0x94, 0xA8, 0xB8, 0xC8, 0x1C, 0x2C, 0x3C, 0x4C, 0x5C, 0x74,
 * and 0x84; the two directly owned allocations came from 0x6C and 0x70. */
bool goodix_primitives_hrv_context_destroy(
    goodix_primitives_hrv_context **context,
    goodix_primitives_release_fn release, void *release_context);
/* 0x0006DB5C: complete GH_HRV initializer. */
uint32_t goodix_primitives_hrv_context_create(
    goodix_primitives_hrv_context **context,
    const goodix_primitives_hrv_configuration *configuration,
    const char *abi_tag, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
/* 0x0006DF14: copy the bound configuration, replace its sample count, and
 * invoke the complete initializer with the recovered private ABI tag. */
uint32_t goodix_primitives_hrv_initialize_for_sample_count(
    goodix_primitives_hrv_context **context,
    const goodix_primitives_hrv_configuration *bound_configuration,
    uint32_t sample_count, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
/* 0x0002CC5C: owner-facing initialization dispatcher with explicit former
 * global output/status bindings. */
int32_t goodix_primitives_hrv_initialize_dispatch(
    goodix_primitives_hrv_context **context,
    const goodix_primitives_hrv_configuration *bound_configuration,
    uint32_t sample_count, uint16_t *result_status,
    uint8_t *provider_active, uint32_t *owner_active,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
int32_t goodix_primitives_release_if_present(
    void *allocation, goodix_primitives_release_fn release,
    void *release_context);
bool goodix_primitives_allocate_record_pair(
    size_t count, void **records, void **scratch,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
int32_t goodix_primitives_release_context_pair(
    void *context, void *owned_allocation,
    goodix_primitives_release_fn release, void *release_context);

/* 0x00074AA4: destructor-vector accessor.  Stock returned absolute Thumb
 * address 0x00028EC9; the reconstruction returns the local function. */
uintptr_t goodix_primitives_release_context_pair_vector(void);

/* 0x0007412C: evaluate the recovered signed-coefficient quartic record.
 * Words 0..1 are metadata; words 2..6 are x^4..x^0 coefficients and the
 * result is divided by 10000. */
float goodix_primitives_quartic_evaluate(
    float value, const int32_t coefficient_record[7]);

/* 0x00074190: find bounded local peaks, retain up to capacity indices in
 * descending value order, and materialize the selected values. */
bool goodix_primitives_peak_select(
    float threshold_ratio, const float *values, int32_t value_count,
    int32_t begin, int32_t end, int32_t radius, int32_t capacity,
    int32_t *selected_indices, float *selected_values,
    int32_t *selected_count);
bool goodix_primitives_buffer_descriptor_initialize(
    goodix_primitives_buffer_descriptor *descriptor, void *data,
    uint16_t capacity, size_t element_bytes,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
bool goodix_primitives_extended_descriptor_initialize(
    goodix_primitives_extended_descriptor *descriptor, void *data,
    uint16_t capacity, size_t element_bytes, uint8_t flag,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
bool goodix_primitives_float_descriptor_initialize(
    goodix_primitives_float_descriptor *descriptor, void *data,
    uint16_t capacity, uint8_t flag,
    goodix_primitives_allocate_fn allocate, void *allocate_context);
bool goodix_primitives_release_two_and_clear(
    void **first, void **second, goodix_primitives_release_fn release,
    void *release_context);
bool goodix_primitives_release_two(
    void *first, void *second, goodix_primitives_release_fn release,
    void *release_context);
bool goodix_primitives_byte_fill(uint8_t value, uint8_t *destination,
                                 size_t length);
bool goodix_primitives_dual_buffer_descriptor_initialize(
    goodix_primitives_dual_buffer_descriptor *descriptor,
    uint32_t field_00, uint32_t field_04,
    uint32_t *primary, size_t primary_words,
    uint32_t *secondary, size_t secondary_words,
    uint32_t count, uint32_t field_14);
bool goodix_primitives_float_storage_initialize(
    goodix_primitives_float_storage *storage, float *values,
    uint32_t capacity, goodix_primitives_allocate_fn allocate,
    void *allocate_context);
bool goodix_primitives_pair_buffer_initialize(
    goodix_primitives_pair_buffer *buffer, uint32_t source_count,
    const float *coefficient_record, goodix_primitives_allocate_fn allocate,
    void *allocate_context);
/* 0x00072C48: construct the complete GH_HR secondary 0x158-byte logical
 * subcontext without retaining the stock 0x000B0F0C coefficient address. */
bool goodix_primitives_hr_secondary_context_initialize(
    goodix_primitives_hr_secondary_context *context,
    const float *coefficient_record,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_hr_secondary_context_release(
    goodix_primitives_hr_secondary_context *context,
    goodix_primitives_release_fn release, void *release_context);
/* 0x0006D204: complete GH_HR primary/private-context constructor.  The
 * former two globals, four absolute table pointers, and selectors 0/1/6 of
 * the copied seven-entry ROM constructor table are explicit owner inputs. */
uint32_t goodix_primitives_hr_primary_context_create(
    goodix_primitives_hr_context_owner *owner,
    const goodix_primitives_hr_configuration *configuration,
    size_t configuration_bytes, const char *abi_tag,
    const goodix_primitives_tables *tables,
    const float *coefficient_record,
    const goodix_primitives_hr_graph_bindings *graph_bindings,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_hr_primary_context_release(
    goodix_primitives_hr_context_owner *owner,
    goodix_primitives_release_fn release, void *release_context);
bool goodix_primitives_channel_state_initialize(
    goodix_primitives_channel_state *state,
    uint32_t primary_divisor, uint32_t secondary_divisor,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_channel_state_release(
    goodix_primitives_channel_state *state,
    goodix_primitives_release_fn release, void *release_context);
bool goodix_primitives_session_state_initialize(
    goodix_primitives_session_state *state,
    uint32_t primary_divisor, uint32_t secondary_divisor,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_session_state_release(
    goodix_primitives_session_state *state,
    goodix_primitives_release_fn release, void *release_context);
bool goodix_primitives_owned_float_record_create(
    goodix_primitives_owned_float_record **record,
    uint16_t first_capacity, uint16_t second_capacity,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_owned_float_record_destroy(
    goodix_primitives_owned_float_record **record,
    goodix_primitives_release_fn release, void *release_context);
bool goodix_primitives_channel_record_array_create(
    goodix_primitives_channel_record **records, size_t count,
    bool enabled, uint8_t tag, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_channel_record_array_destroy(
    goodix_primitives_channel_record **records, size_t count,
    bool enabled, goodix_primitives_release_fn release,
    void *release_context);
bool goodix_primitives_dual_i16_storage_initialize(
    goodix_primitives_dual_i16_storage *storage, uint32_t divisor,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_session_aggregate_create(
    goodix_primitives_session_aggregate *aggregate,
    uint32_t primary_divisor, uint32_t secondary_divisor,
    uint32_t auxiliary_divisor, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_session_aggregate_destroy(
    goodix_primitives_session_aggregate *aggregate,
    goodix_primitives_release_fn release, void *release_context);

/* 0x0006EB94 / 0x0006EB30: complete outer preprocessing-session lifecycle.
 * The source record must be exactly 76 bytes and the ABI tag exactly
 * "pre_pv_v1.1.0".  All nested allocations roll back on failure. */
bool goodix_primitives_outer_session_create(
    goodix_primitives_outer_session **session,
    const uint8_t *source, size_t source_length, const char *abi_tag,
    const quantized_runtime *runtime, const uint32_t *model_words,
    size_t model_word_count, uint32_t model_base_address,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context);
bool goodix_primitives_outer_session_destroy(
    goodix_primitives_outer_session **session,
    goodix_primitives_release_fn release, void *release_context);

#endif
