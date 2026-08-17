#ifndef OPENR1_RECONSTRUCTED_GOMORE_PRIMITIVES_H
#define OPENR1_RECONSTRUCTED_GOMORE_PRIMITIVES_H

/*
 * Owner-authorized clean-room reconstruction of small GoMore-candidate
 * functions from the SHA-pinned R1 application image.  This is not GoMore
 * source.  See docs/correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define GOMORE_PRIMITIVES_RECORD_COUNT 7u
#define GOMORE_PRIMITIVES_RECORD_STRIDE 16u
#define GOMORE_PRIMITIVES_CALLBACK_RECORD_BYTES 0xC0u
#define GOMORE_PRIMITIVES_ENERGY_TABLE_MODES 27u
#define GOMORE_PRIMITIVES_ENERGY_OUTPUT_FLOATS 11u
#define GOMORE_PRIMITIVES_ENERGY_STATUS_OK UINT32_C(0)
#define GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID UINT32_C(0x40)
#define GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_SOURCE_BYTES 0x312u
#define GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_DESTINATION_BYTES 0xA8u
#define GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES 0x33Cu
#define GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_OUTPUT_BYTES 0x44u
#define GOMORE_PRIMITIVES_FINAL_SLEEP_HEADER_BYTES 0x20u
#define GOMORE_PRIMITIVES_EXTREMA_CAPACITY 20u
#define GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES 736u
#define GOMORE_PRIMITIVES_USER_PROFILE_BYTES 28u
#define GOMORE_PRIMITIVES_OUTPUT_DESCRIPTOR_BYTES 264u
#define GOMORE_PRIMITIVES_PKEY_PARTITION_BYTES 4096u
#define GOMORE_PRIMITIVES_PKEY_APPEND_WINDOW_BYTES 1024u
#define GOMORE_PRIMITIVES_PREVIOUS_STATE_SLOT_COUNT 3u
#define GOMORE_PRIMITIVES_PREVIOUS_STATE_SLOT_HEADER_BYTES 8u

typedef void (*gomore_primitives_prepare_fn)(uintptr_t first,
                                             uintptr_t second,
                                             uintptr_t third,
                                             uintptr_t fourth,
                                             void *workspace);
typedef float (*gomore_primitives_score_fn)(const void *workspace);
typedef int (*gomore_primitives_compare_fn)(const void *left,
                                            const void *right);
typedef void (*gomore_primitives_qsort_fn)(void *base, size_t count,
                                          size_t size,
                                          gomore_primitives_compare_fn compare);
typedef int32_t (*gomore_primitives_max_index_fn)(const float *values,
                                                  uint32_t count);
typedef bool (*gomore_primitives_blob_loader_fn)(void *context,
                                                 uint8_t *destination,
                                                 size_t length);
typedef int32_t (*gomore_primitives_stage_consumer_fn)(
    uintptr_t first, uintptr_t second, const uint8_t staged[32],
    uintptr_t fourth, uintptr_t fifth);
typedef void (*gomore_primitives_mode_fn)(uint32_t mode, uint32_t value);
typedef void (*gomore_primitives_void_context_fn)(void *context);
typedef void (*gomore_primitives_init_fn)(uint32_t mode);
typedef uint32_t (*gomore_primitives_time_fn)(void *context);
typedef uint16_t (*gomore_primitives_offset_fn)(void *context);
typedef int32_t (*gomore_primitives_sync_state_fn)(void *context);
typedef bool (*gomore_primitives_parameter_validate_fn)(void *context,
                                                        uint32_t value);
typedef float (*gomore_primitives_float_unary_fn)(float value);
typedef float (*gomore_primitives_float_binary_fn)(float left, float right);
typedef double (*gomore_primitives_double_unary_fn)(double value);
typedef double (*gomore_primitives_double_binary_fn)(double left,
                                                      double right);
typedef bool (*gomore_primitives_store_read_fn)(
    void *context, uint32_t offset, uint8_t *destination, size_t length);
typedef bool (*gomore_primitives_store_write_fn)(
    void *context, uint32_t offset, const uint8_t *source, size_t length);
typedef bool (*gomore_primitives_store_erase_fn)(
    void *context, uint32_t offset, size_t length);
typedef bool (*gomore_primitives_autocorrelation_analyze_fn)(
    const uint16_t *samples,
    float *first, float *second, float *third, float *fourth, float *fifth,
    uintptr_t first_binding, uintptr_t second_binding);
typedef float (*gomore_primitives_feature_model_fn)(const float *values);
typedef float (*gomore_primitives_state_adjust_fn)(float primary,
                                                   void *state);
typedef void (*gomore_primitives_state_pair_commit_fn)(
    void *state, float primary, float secondary);

/* Exact target layout used by the accelerometer-derived SPS candidate at
 * 0x0005EF1C.  The stock pointer word at +0x40 is retained only as an
 * explicit caller binding; the checked updater never dereferences it. */
typedef struct {
    uint32_t model_type;
    float accumulated_secondary;
    float accumulated_primary;
    uint16_t accepted_count;
    uint16_t count_padding;
    float calibration_slope;
    float calibration_intercept;
    uint32_t calibration_enabled;
} gomore_primitives_sps_model_state;

typedef struct {
    float smoothed_state2;
    float smoothed_state1;
    gomore_primitives_sps_model_state state2_model;
    gomore_primitives_sps_model_state state1_model;
    uint32_t configuration_binding;
    float latest_candidate;
    float latest_primary_model;
    uint32_t missing_update_count;
    uint16_t startup_cooldown;
    uint16_t cooldown_padding;
    uint32_t reserved_word;
} gomore_primitives_sps_candidate_state;

typedef struct {
    float values[6];
} gomore_primitives_sps_features;

typedef struct {
    int8_t raw_state;
    int8_t smoothed_state;
    uint8_t cadence;
} gomore_primitives_sps_motion;

typedef struct {
    float candidate;
    uint8_t status;
    uint8_t reserved[3];
} gomore_primitives_sps_candidate_output;

typedef struct {
    gomore_primitives_feature_model_fn state2_primary;
    gomore_primitives_feature_model_fn state2_secondary;
    gomore_primitives_feature_model_fn state1_primary;
    gomore_primitives_feature_model_fn state1_secondary;
    gomore_primitives_state_adjust_fn adjust;
    gomore_primitives_state_pair_commit_fn commit;
} gomore_primitives_sps_candidate_providers;

typedef struct {
    uint8_t initialized;
    uint8_t reserved1;
    uint8_t subscription;
    uint8_t reserved3;
    uint8_t auth_pending;
    uint8_t auth_retry_attempted;
    uint8_t reserved6[22];
    uint32_t output_record;
} gomore_primitives_health_lifecycle_state;

typedef uint32_t (*gomore_primitives_size_query_fn)(void *context);
typedef int32_t (*gomore_primitives_status_context_fn)(void *context);
typedef bool (*gomore_primitives_previous_restore_fn)(
    void *context,
    uint8_t previous_data[GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES]);
typedef bool (*gomore_primitives_crash_restore_fn)(
    void *context,
    uint8_t previous_data[GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES],
    size_t *restored_length);
typedef bool (*gomore_primitives_user_profile_load_fn)(
    void *context,
    uint8_t profile[GOMORE_PRIMITIVES_USER_PROFILE_BYTES]);
typedef int32_t (*gomore_primitives_health_initialize_fn)(
    void *context, uint32_t timestamp,
    const uint8_t profile[GOMORE_PRIMITIVES_USER_PROFILE_BYTES],
    const uint8_t previous_data[GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES]);
typedef void (*gomore_primitives_mode_value_fn)(
    void *context, uint32_t mode, uint32_t value);
typedef uint8_t (*gomore_primitives_event_subscribe_fn)(
    void *context, uint32_t topic, uintptr_t callback, uintptr_t callback_context);

typedef struct {
    void *context;
    gomore_primitives_size_query_fn query_previous_size;
    gomore_primitives_size_query_fn query_engine_size;
    gomore_primitives_status_context_fn configure_authorization;
    gomore_primitives_previous_restore_fn restore_previous;
    gomore_primitives_status_context_fn crash_record_present;
    gomore_primitives_crash_restore_fn restore_crash_previous;
    gomore_primitives_void_context_fn clear_crash_previous;
    gomore_primitives_user_profile_load_fn load_user_profile;
    gomore_primitives_time_fn timestamp;
    gomore_primitives_health_initialize_fn initialize_health;
    gomore_primitives_mode_value_fn apply_profile_state;
    gomore_primitives_mode_value_fn configure_state_mode;
    gomore_primitives_event_subscribe_fn subscribe;
    uintptr_t event_callback;
    uintptr_t event_callback_context;
} gomore_primitives_health_lifecycle_providers;

typedef enum {
    GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_OK = 0,
    GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_BAD_ARGUMENT,
    GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_AUTH_FAILED,
    GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_INITIALIZE_FAILED
} gomore_primitives_health_lifecycle_result;
typedef void (*gomore_primitives_update_failure_log_fn)(
    uint32_t status, uint32_t timestamp);
typedef void (*gomore_primitives_sps_selection_log_fn)(
    float reference, float gpd, float accelerometer);
typedef void (*gomore_primitives_simple_fn)(void);
typedef int32_t (*gomore_primitives_random_fn)(void);
typedef void *(*gomore_primitives_zero_allocate_fn)(size_t length);
typedef void (*gomore_primitives_allocated_init_fn)(void *record,
                                                    uintptr_t binding);
typedef uint32_t (*gomore_primitives_tensor_call_fn)(
    uintptr_t first, uintptr_t second,
    uint32_t descriptor0, uint32_t descriptor1, uint32_t descriptor2);
typedef void (*gomore_primitives_tensor_finish_fn)(uintptr_t first,
                                                  uintptr_t second);
typedef void (*gomore_primitives_filter_init_fn)(
    void *record, uint32_t rows, uint32_t columns,
    const float parameters[2]);
typedef void (*gomore_primitives_dual_stage_fn)(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *output);
typedef void (*gomore_primitives_record_init_fn)(void *record);
typedef void (*gomore_primitives_mode_lt2_init_fn)(
    void *record, uint32_t mode, uint32_t count, float parameter);
typedef void (*gomore_primitives_mode2_init_fn)(
    void *record, uint32_t count, const float parameters[2]);
typedef void (*gomore_primitives_large_init_fn)(void *record);
typedef void (*gomore_primitives_resample_fn)(
    const float *source, int32_t input_count, int32_t output_count,
    int32_t source_total, float *destination);
typedef void (*gomore_primitives_filter_apply_fn)(
    void *filter_state, float *values, size_t count);
typedef void (*gomore_primitives_seed_fn)(uint32_t seed);
typedef void (*gomore_primitives_topic_register_fn)(
    uint32_t topic, uintptr_t handler, uintptr_t context);
typedef void (*gomore_primitives_event_publish_fn)(
    uint32_t topic, const void *payload, size_t payload_length);
typedef int32_t (*gomore_primitives_state_byte_fn)(void *state,
                                                   uint8_t value);
typedef int32_t (*gomore_primitives_state_call_fn)(void *state);
typedef int32_t (*gomore_primitives_record_step_fn)(void *state,
                                                    void *record);
typedef uint32_t (*gomore_primitives_tensor_construct_binding_fn)(
    void *pool, size_t pool_length, uint32_t rank,
    const uint16_t *dimensions, size_t dimension_count);
typedef uint32_t (*gomore_primitives_tensor_fill_binding_fn)(
    uintptr_t runtime_binding, uintptr_t pool_binding, uint32_t rank,
    const uint16_t *dimensions, size_t dimension_count, float fill);
typedef uint32_t (*gomore_primitives_format_u32_fn)(
    char *destination, size_t capacity, const char *format, uint32_t value);
typedef void (*gomore_primitives_log_emit_fn)(const char *format,
                                              const char *message);
typedef bool (*gomore_primitives_locomotion_crossing_estimate_fn)(
    const uint16_t *samples, size_t sample_count, int16_t baseline,
    uint32_t mode, float *output);
typedef void (*gomore_primitives_locomotion_classify_fn)(
    void *state, void *output);
typedef uint8_t *(*gomore_primitives_final_sleep_lookup_fn)(
    uintptr_t record_binding);
typedef uint32_t (*gomore_primitives_log_modes_fn)(void);
typedef void (*gomore_primitives_final_sleep_log_fn)(
    uint8_t record_type, uint32_t start_timestamp,
    uint32_t end_timestamp, uint16_t compact_count);
typedef bool (*gomore_primitives_final_sleep_accept_fn)(
    const uint8_t *record);
typedef int32_t (*gomore_primitives_integer_filter_update_fn)(
    void *state, int32_t input, int32_t output[2],
    uint32_t interval_milliseconds);

typedef struct {
    float selected_heart_rate;
    float reserved_zero;
    float selected_speed;
    float *thresholds;
    float *primary_sums;
    float *primary_counts;
    float below_range_weight;
    float *auxiliary_first;
    float *auxiliary_second;
} gomore_primitives_dormant_ratio_input;

typedef struct {
    uint8_t profile_flag;
    float all_heart_rate_mean;
    float all_sample_count;
    float qualified_square_sum;
    float qualified_heart_rate_mean;
    float qualified_speed_mean;
    float qualified_sample_count;
    float secondary_sums[6];
    float secondary_counts[6];
} gomore_primitives_dormant_ratio_accumulator_state;

typedef struct {
    uint8_t next_slot;
    int16_t means[4][8];
    int16_t standard_deviations[4][8];
    int16_t fourth_range[8];
    int16_t mean_absolute_differences[4][8];
} gomore_primitives_locomotion_summary_state;

typedef struct {
    uint8_t buckets[18];
    float pending_sum;
    int32_t pending_count;
    uint8_t last_bucket;
} gomore_primitives_motion_gate_state;

typedef struct {
    float score;
    bool positive_after_bias;
    bool updated;
    bool valid;
} gomore_primitives_motion_gate_output;

typedef enum {
    GOMORE_PRIMITIVES_DIFFERENCE_FLOAT32 = 0,
    GOMORE_PRIMITIVES_DIFFERENCE_INT16 = 1,
    GOMORE_PRIMITIVES_DIFFERENCE_INT32 = 2
} gomore_primitives_difference_mode;

typedef struct {
    int8_t direction_changes;
    float normalized_variation;
    float average_completed_run;
    int8_t above_threshold_changes;
} gomore_primitives_direction_change_output;

typedef struct {
    uint8_t enabled;
    uint8_t has_seen_positive;
    uint8_t unchanged_count;
    uint8_t positive_streak;
    uint8_t history_count;
    uint8_t reserved[3];
    uint32_t missing_count;
    int32_t last_effective_input;
    float average;
    float history[20];
} gomore_primitives_dormant_heart_rate_filter_state;

typedef struct {
    float weights[6];
    float bias;
    float scale;
    float empty_window_value;
    int16_t minimum_output;
} gomore_primitives_six_channel_linear_model;

typedef struct {
    const gomore_primitives_six_channel_linear_model *ring_score_model;
    const float *linear_sign_coefficients;
    float linear_sign_bias;
    gomore_primitives_autocorrelation_analyze_fn autocorrelation;
    gomore_primitives_locomotion_crossing_estimate_fn crossing_estimate;
} gomore_primitives_locomotion_classifier_configuration;

typedef struct {
    uint32_t accumulated;
    bool initialized;
    float estimate;
} gomore_primitives_locomotion_transition_state;

#define GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT 16u
#define GOMORE_PRIMITIVES_OUTPUT_STAGE_MAX_ARGUMENTS 10u

typedef enum {
    GOMORE_PRIMITIVES_OUTPUT_STAGE_RESPIRATORY_RATE = 0,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_LOCOMOTION_PREPROCESS,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_CLASSIFIER,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_CANDIDATE,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_SELECT,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_MOTION,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_HEART_RATE_SELECT,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_ENERGY,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_DORMANT_ESTIMATOR,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_GATE,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_CYCLE,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_OPTICAL_PEAK,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_STREAM,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_WINDOW,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_STEP_ACCUMULATE,
    GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_ACCUMULATE,
} gomore_primitives_output_stage_id;

typedef struct {
    gomore_primitives_output_stage_id id;
    uint16_t stage_state_offset;
    uint16_t control_offset;
    uint16_t status_offset;
    uint8_t stock_stage_number;
    uint8_t argument_count;
    uint16_t argument_offsets[
        GOMORE_PRIMITIVES_OUTPUT_STAGE_MAX_ARGUMENTS];
} gomore_primitives_output_stage_descriptor;

typedef bool (*gomore_primitives_output_stage_fn)(
    void *context, uint8_t *engine, size_t engine_length,
    uint32_t elapsed_updates,
    const gomore_primitives_output_stage_descriptor *descriptor,
    uint32_t *status);

typedef struct {
    void *context;
    gomore_primitives_output_stage_fn stages[
        GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT];
} gomore_primitives_output_orchestrator_providers;

#define GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY 40u
#define GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT 250u
#define GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY 20u

typedef struct {
    uint16_t position;
    float first;
    float second;
} gomore_primitives_locomotion_control_sample;

typedef struct {
    uint16_t positions[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY];
    float controls[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY];
    float expanded[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT];
    uint8_t first_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY];
    uint8_t second_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY];
} gomore_primitives_locomotion_control_workspace;

typedef struct {
    gomore_primitives_qsort_fn qsort_provider;
    gomore_primitives_compare_fn compare;
    gomore_primitives_float_binary_fn power_f32;
    gomore_primitives_float_unary_fn square_root_f32;
    gomore_primitives_double_binary_fn power_f64;
    gomore_primitives_double_unary_fn square_root_f64;
} gomore_primitives_locomotion_feature_reduce_math;

typedef bool (*gomore_primitives_locomotion_feature_reduce_fn)(
    float expanded[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT],
    uint8_t first_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    uint8_t second_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    float controls[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY],
    float *primary, float *secondary,
    const gomore_primitives_locomotion_feature_reduce_math *math);

typedef void (*gomore_primitives_dormant_ratio_accumulate_fn)(
    void *state, const gomore_primitives_dormant_ratio_input *input);
typedef void (*gomore_primitives_quadratic_dispatch_fn)(
    float coefficient_a, float coefficient_b, float coefficient_c,
    void *state);
typedef void (*gomore_primitives_cubic_dispatch_fn)(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float coefficient_d, void *state);
typedef float (*gomore_primitives_dormant_root_reduce_fn)(
    float primary, float secondary, float auxiliary,
    void *state, int32_t mode);
typedef float (*gomore_primitives_dormant_root_finalize_fn)(
    float reduced, float auxiliary, void *state, int32_t mode);
typedef uint32_t (*gomore_primitives_sleep_graph_zero_build_fn)(
    void *graph_state);
typedef uint32_t (*gomore_primitives_sleep_graph_nonzero_build_fn)(
    int32_t family, void *graph_state, uint32_t arena_seed);
typedef void (*gomore_primitives_sleep_graph_recurrent_construct_fn)(
    uint8_t descriptor[24], uint8_t units, uint8_t input_dimension,
    uint32_t *arena_cursor);
typedef void (*gomore_primitives_sleep_graph_dense_construct_fn)(
    uint8_t descriptor[24], uint8_t dim_a, uint8_t dim_b,
    uint8_t flag_a, uint8_t flag_b, uint32_t *arena_cursor);
typedef void (*gomore_primitives_input_adapter_core_fn)(
    void *engine_state, uint32_t elapsed_seconds);
typedef float (*gomore_primitives_state1_cadence_estimate_fn)(
    float first, float middle, float latest, uint8_t *consensus);
typedef void (*gomore_primitives_activity_statistics_fn)(
    const float *values, uint32_t count, uint32_t mode, float output[4]);

typedef struct {
    float score;
    uint8_t state;
    uint8_t state_padding[3];
    float window[250];
    int32_t transition_count;
    int32_t accumulated_samples;
    int32_t hold_samples;
    float reset_threshold;
    uint8_t positive_windows;
    uint8_t negative_windows;
    uint8_t tail_padding[2];
} gomore_primitives_activity_window_state;

typedef struct {
    const float *samples;
    int16_t sample_count;
    uint8_t channel_count;
} gomore_primitives_activity_window_input;

typedef struct {
    const float *axes[3];
    bool alternate_conditioning;
    gomore_primitives_float_unary_fn square_root;
    gomore_primitives_activity_statistics_fn statistics;
} gomore_primitives_activity_window_providers;

typedef struct {
    uint8_t activity;
    uint8_t confidence;
} gomore_primitives_activity_window_output;

typedef int32_t (*gomore_primitives_respiratory_estimate_fn)(
    void *state, uint32_t elapsed, const void *input, uint32_t status,
    float *rate, float *confidence);

typedef struct {
    float rate_history[5];
    float confidence_history[5];
    uint8_t modulo_counter;
    uint8_t primary_codes[4];
    uint8_t secondary_codes[2];
    uint8_t padding;
} gomore_primitives_respiratory_rate_state;

typedef struct {
    const void *estimator_input;
    bool input_unavailable;
    uint8_t secondary_code;
    uint8_t primary_code;
} gomore_primitives_respiratory_rate_input;

typedef struct {
    gomore_primitives_respiratory_estimate_fn estimate;
    gomore_primitives_double_unary_fn square_root;
} gomore_primitives_respiratory_rate_providers;

typedef struct {
    uint16_t end_position;
    uint16_t start_position;
    uint16_t peak_position;
    uint16_t padding;
    float end_value;
    float start_value;
} gomore_primitives_optical_interval_record;

typedef struct {
    uint8_t prefix[81];
    uint8_t interval_count;
    uint8_t alignment[2];
    uint32_t current_window;
    gomore_primitives_optical_interval_record intervals[40];
    float signal[250];
    float position_tolerance_scale;
    float amplitude_tolerance_scale;
} gomore_primitives_optical_interval_state;

typedef struct {
    gomore_primitives_mode2_init_fn initialize_filter_state;
    gomore_primitives_filter_apply_fn apply_filter;
    gomore_primitives_double_unary_fn round_value;
    gomore_primitives_locomotion_feature_reduce_math feature_math;
} gomore_primitives_optical_period_providers;

typedef struct {
    uint8_t first_indices[GOMORE_PRIMITIVES_EXTREMA_CAPACITY];
    uint8_t second_indices[GOMORE_PRIMITIVES_EXTREMA_CAPACITY];
    float peak_workspace[25];
    gomore_primitives_locomotion_control_sample control_samples[
        GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY];
    gomore_primitives_locomotion_control_workspace control_workspace;
} gomore_primitives_optical_period_workspace;

typedef struct {
    uint8_t packed_stages[720];
    uint32_t previous_timestamp;
    uint8_t previous_packed_value;
    uint8_t alignment_2d5;
    int16_t peaks[136];
    uint16_t update_counter;
    uint8_t active;
    uint8_t batch_count;
    uint8_t peak_count;
    uint8_t classifier_iteration;
    float stage_window[90];
    uint32_t tensor_words[2];
    uint8_t tensor_storage[7056];
    uint32_t tensor_binding;
    uint32_t last_tensor_binding;
    int8_t selected_stage;
    uint8_t mode;
} gomore_primitives_sleep_stage_stream_state;

typedef struct {
    uint8_t positions[16];
    uint8_t count_with_flags;
} gomore_primitives_sleep_stage_peak_input;

typedef struct {
    float value;
    uint8_t packed_value;
    uint8_t reserved;
    uint8_t enabled;
} gomore_primitives_sleep_stage_status;

typedef struct {
    float primary;
    float candidates[3];
    int8_t selected;
} gomore_primitives_sleep_stage_classifier_result;

typedef struct {
    const uint16_t *weights_half;
    size_t weight_count;
    const uint16_t *scale_half;
    const uint16_t *offset_half;
    const uint16_t *variance_half;
    const uint16_t *mean_half;
    size_t parameter_count;
} gomore_primitives_sleep_stage_conv_model;

typedef struct {
    const int8_t *weights;
    size_t weight_count;
    size_t rows;
    size_t columns;
    float weight_scale;
    const int16_t *bias_half;
    size_t bias_count;
} gomore_primitives_sleep_stage_affine_model;

typedef struct {
    gomore_primitives_sleep_stage_affine_model input;
    gomore_primitives_sleep_stage_affine_model recurrent;
} gomore_primitives_sleep_stage_recurrent_model;

typedef struct {
    gomore_primitives_sleep_stage_conv_model convolution[7];
    gomore_primitives_sleep_stage_affine_model projection[2];
    gomore_primitives_sleep_stage_recurrent_model recurrent[2];
    gomore_primitives_sleep_stage_affine_model post_recurrent;
    gomore_primitives_sleep_stage_affine_model output;
} gomore_primitives_sleep_stage_classifier_model;

typedef struct {
    gomore_primitives_float_unary_fn square_root;
    gomore_primitives_float_unary_fn exponential;
    gomore_primitives_float_unary_fn logistic;
    gomore_primitives_float_unary_fn hyperbolic_tangent;
} gomore_primitives_sleep_stage_classifier_math;

typedef struct {
    const gomore_primitives_sleep_stage_classifier_model *mode_below_100;
    const gomore_primitives_sleep_stage_classifier_model *mode_100_and_above;
    gomore_primitives_sleep_stage_classifier_math math;
} gomore_primitives_sleep_stage_classifier_context;

typedef bool (*gomore_primitives_sleep_stage_classify_fn)(
    gomore_primitives_sleep_stage_classifier_result *result,
    gomore_primitives_sleep_stage_stream_state *state,
    uint8_t iteration, const int8_t mode_adjustment[4], void *context);
typedef void (*gomore_primitives_sleep_force_prepare_fn)(
    uint32_t mode, uint8_t record[56]);
typedef void (*gomore_primitives_sleep_force_mode_fn)(
    uint32_t mode, uint32_t enabled);
typedef void (*gomore_primitives_sleep_force_dispatch_fn)(
    uint32_t result_words[2], uint8_t report[88],
    uint8_t timeline[0xB40]);
typedef void (*gomore_primitives_sleep_force_publish_fn)(
    uint32_t result_words[2], uint8_t report[88]);

typedef struct {
    bool enabled;
    uint16_t category_mask;
    uint32_t level_mask;
    gomore_primitives_format_u32_fn format_u32;
    gomore_primitives_log_emit_fn emit;
} gomore_primitives_log_config;

typedef struct {
    gomore_primitives_final_sleep_lookup_fn lookup;
    gomore_primitives_log_modes_fn log_modes;
    gomore_primitives_final_sleep_log_fn structured_log;
    gomore_primitives_final_sleep_log_fn secondary_log;
    gomore_primitives_final_sleep_accept_fn accept;
    gomore_primitives_event_publish_fn publish;
    gomore_primitives_void_context_fn release;
} gomore_primitives_final_sleep_providers;

typedef struct {
    uint8_t wire_type;
    int32_t start_timestamp;
    int32_t end_timestamp;
    const int8_t *stages;
    size_t stage_count;
    float efficiency;
    float score;
    float rem_fraction;
    float light_fraction;
    float deep_fraction;
    float total_minutes;
    float wake_minutes;
    float rem_minutes;
    float light_minutes;
    float deep_minutes;
    uint16_t body_temperature;
} gomore_primitives_final_sleep_record;

typedef void (*gomore_primitives_output_action_fn)(void *context);
typedef bool (*gomore_primitives_output_ready_fn)(void *context);
typedef void (*gomore_primitives_activity_output_fn)(
    void *context, const uint32_t activity[2]);
typedef void (*gomore_primitives_sleep_status_output_fn)(
    void *context, uint8_t status);
typedef bool (*gomore_primitives_final_sleep_output_fn)(void *context);
typedef void (*gomore_primitives_output_authorize_fn)(
    void *context, uint32_t slot, bool enabled);

typedef struct {
    uint8_t active_slot_mask;
    uint32_t activity[2];
    uint8_t sleep_lifecycle_flags;
    int8_t stage_ppg_request;
    bool previous_stage_ppg_request;
    bool accelerometer_pending;
    bool optical_pending;
} gomore_primitives_output_lifecycle_state;

typedef struct {
    gomore_primitives_output_action_fn refresh_input;
    gomore_primitives_output_action_fn update_engine;
    gomore_primitives_output_ready_fn result_ready;
    gomore_primitives_activity_output_fn consume_activity;
    gomore_primitives_sleep_status_output_fn publish_sleep_status;
    gomore_primitives_final_sleep_output_fn publish_final_sleep;
    gomore_primitives_output_authorize_fn authorize;
} gomore_primitives_output_lifecycle_providers;

typedef struct {
    uint32_t unix_seconds;
    int16_t timezone_offset_minutes;
    const float *accelerometer_axes[3];
    uint8_t accelerometer_sample_count;
    const float *raw_optical_samples;
    uint8_t raw_optical_sample_count;
    uint8_t raw_optical_channel_count;
    const uint16_t *hrv_auxiliary_samples;
    uint8_t hrv_auxiliary_count;
    float direct_heart_rate;
    uint32_t legacy_zero_word;
    uint8_t wear_state_is_unknown;
    uint8_t mode2_legacy_byte0;
    uint8_t mode2_legacy_byte1;
    uint32_t raw_optical_binding;
} gomore_primitives_host_input;

/*
 * Exact host-side topic staging reconstructed from the four callbacks at
 * 0x0006B114, 0x0006B1B8, 0x0006B1F4, and 0x0006B228.  Stock stores the
 * arrays behind pointers in its 264-byte I/O record; the transparent form
 * owns the bounded storage directly and retains the same readiness bits.
 */
#define GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT 25u
#define GOMORE_PRIMITIVES_TOPIC_HRV_LIMIT 4u
#define GOMORE_PRIMITIVES_TOPIC_ACC_BATCH_BYTES 188u
#define GOMORE_PRIMITIVES_TOPIC_ACC_COUNT_OFFSET 180u
#define GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET 9u
#define GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER UINT8_C(0x01)
#define GOMORE_PRIMITIVES_TOPIC_READY_RAW_OPTICAL UINT8_C(0x02)
#define GOMORE_PRIMITIVES_TOPIC_READY_HEART_RATE UINT8_C(0x04)

typedef struct {
    float accelerometer_axes[3][GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT];
    float raw_optical[GOMORE_PRIMITIVES_TOPIC_SAMPLE_LIMIT];
    uint16_t hrv_auxiliary[GOMORE_PRIMITIVES_TOPIC_HRV_LIMIT];
    float direct_heart_rate;
    uint8_t accelerometer_sample_count;
    uint8_t raw_optical_sample_count;
    uint8_t hrv_auxiliary_count;
    uint8_t ready_flags;
} gomore_primitives_topic_input_state;

typedef struct {
    uint32_t raw_optical_output_binding;
    uint32_t accelerometer_output_bindings[3];
} gomore_primitives_host_input_bindings;

typedef void (*gomore_primitives_sensor_update_diagnose_fn)(
    const void *context, const gomore_primitives_host_input *input);
typedef void (*gomore_primitives_sensor_update_error_fn)(
    const void *context, int32_t status);
typedef int32_t (*gomore_primitives_sensor_update_apply_fn)(
    const void *context, const gomore_primitives_host_input *input,
    uint32_t normalized_timestamp);
typedef void (*gomore_primitives_sensor_update_snapshot_fn)(
    const void *context);

typedef struct {
    bool diagnostics_enabled;
    bool validation_enabled;
    uint32_t configured_timestamp_limit;
    bool runtime_present;
    int16_t configured_version;
    int16_t runtime_version;
} gomore_primitives_sensor_update_configuration;

typedef struct {
    int8_t initialization_status;
    uint32_t previous_timestamp;
    uint32_t update_flags;
} gomore_primitives_sensor_update_state;

typedef struct {
    gomore_primitives_sensor_update_diagnose_fn diagnose;
    gomore_primitives_sensor_update_error_fn log_error;
    gomore_primitives_sensor_update_apply_fn apply;
    gomore_primitives_sensor_update_snapshot_fn snapshot;
} gomore_primitives_sensor_update_providers;

typedef struct {
    float value;
    int32_t metadata;
} gomore_primitives_quality_sample;

typedef struct gomore_primitives_pkey_store gomore_primitives_pkey_store;
typedef bool (*gomore_primitives_pkey_store_initialize_fn)(
    gomore_primitives_pkey_store *store);

struct gomore_primitives_pkey_store {
    bool initialized;
    uint32_t partition_offset;
    void *flash_context;
    gomore_primitives_store_read_fn read;
    gomore_primitives_store_write_fn write;
    gomore_primitives_store_erase_fn erase;
    gomore_primitives_pkey_store_initialize_fn initialize;
};

typedef enum {
    GOMORE_PRIMITIVES_PKEY_OK = 0,
    GOMORE_PRIMITIVES_PKEY_STORE_UNAVAILABLE,
    GOMORE_PRIMITIVES_PKEY_OUTPUT_NULL,
    GOMORE_PRIMITIVES_PKEY_NOT_FOUND,
    GOMORE_PRIMITIVES_PKEY_CRC_MISMATCH,
    GOMORE_PRIMITIVES_PKEY_READ_FAILED
} gomore_primitives_pkey_status;

typedef struct {
    bool valid;
    uint32_t stored_length;
    uint32_t stored_crc;
    uint32_t computed_crc;
    gomore_primitives_pkey_status status;
} gomore_primitives_pkey_result;

typedef struct {
    const uint8_t *key;
    const uint8_t *device_uuid;
    uint8_t device_uuid_length;
    uint32_t timestamp;
} gomore_primitives_auth_parameters;

typedef int32_t (*gomore_primitives_auth_apply_fn)(
    const gomore_primitives_auth_parameters *parameters);

typedef struct {
    bool device_uuid_cache_valid;
    const uint8_t *device_uuid_cache;
    size_t device_uuid_cache_length;
    uint32_t device_id_0;
    uint32_t device_id_1;
    uint32_t address_word;
    bool pkey_cache_valid;
    const uint8_t *pkey_cache;
    gomore_primitives_blob_loader_fn pkey_loader;
    void *pkey_loader_context;
    gomore_primitives_time_fn timestamp;
    void *timestamp_context;
    gomore_primitives_auth_apply_fn apply;
} gomore_primitives_auth_setup_configuration;

#define GOMORE_PRIMITIVES_SDK_AUTH_KEY_BYTES 32u
#define GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT 4u

typedef struct {
    uint32_t field0;
    int16_t error;
    uint16_t reserved6;
    uint32_t field8;
    uint32_t field12;
    uint8_t field16;
    uint8_t reserved17[3];
} gomore_primitives_sdk_auth_status;

typedef bool (*gomore_primitives_sdk_auth_decrypt_fn)(
    void *context, const uint8_t *input, size_t input_length,
    const uint8_t key[GOMORE_PRIMITIVES_SDK_AUTH_KEY_BYTES],
    uint8_t *output, size_t output_capacity, size_t *written);
typedef bool (*gomore_primitives_sdk_auth_message_match_fn)(
    void *context, const uint8_t *message, size_t message_length);
typedef int32_t (*gomore_primitives_sdk_auth_field_parse_fn)(
    void *context, char *field,
    const gomore_primitives_auth_parameters *parameters,
    gomore_primitives_sdk_auth_status *status, uint32_t scratch[4]);
typedef int32_t (*gomore_primitives_sdk_auth_field_validate_fn)(
    void *context, char *field,
    const gomore_primitives_auth_parameters *parameters,
    gomore_primitives_sdk_auth_status *status);

typedef struct {
    const uint8_t *decrypt_keys[2];
    void *decrypt_context;
    gomore_primitives_sdk_auth_decrypt_fn decrypt;
    void *match_context;
    gomore_primitives_sdk_auth_message_match_fn message_matches;
    void *dispatch_context;
    gomore_primitives_sdk_auth_field_parse_fn
        parse_fields[GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT];
    gomore_primitives_sdk_auth_field_validate_fn
        validate_fields[GOMORE_PRIMITIVES_SDK_AUTH_FIELD_COUNT - 1u];
} gomore_primitives_sdk_auth_configuration;

typedef enum {
    GOMORE_PRIMITIVES_PREVIOUS_STATE_OK = 0,
    GOMORE_PRIMITIVES_PREVIOUS_STATE_PKEY_INVALID,
    GOMORE_PRIMITIVES_PREVIOUS_STATE_NOT_FOUND,
    GOMORE_PRIMITIVES_PREVIOUS_STATE_READ_FAILED,
    GOMORE_PRIMITIVES_PREVIOUS_STATE_OUTPUT_INVALID
} gomore_primitives_previous_state_status;

typedef struct {
    bool found;
    uint8_t slot;
    uint32_t record_offset;
    gomore_primitives_previous_state_status status;
} gomore_primitives_previous_state_result;

typedef enum {
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK = 0,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_BAD_ARGUMENT,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_STORE_UNAVAILABLE,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_READ_FAILED,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_TOO_LARGE,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_SCRATCH_TOO_SMALL,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_ERASE_FAILED,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_WRITE_FAILED,
    GOMORE_PRIMITIVES_PREVIOUS_APPEND_NO_ERASED_SLOT
} gomore_primitives_previous_append_status;

typedef struct {
    bool compacted;
    uint8_t slot;
    uint32_t key_length;
    uint32_t aligned_key_length;
    uint32_t aligned_state_length;
    uint32_t record_offset;
    gomore_primitives_previous_append_status status;
} gomore_primitives_previous_append_result;

typedef struct {
    uint32_t random_seed;
    bool version_validation_enabled;
    uint32_t configured_runtime_limit;
    bool runtime_present;
    int16_t configured_version;
    int16_t runtime_version;
    uint8_t *time_configuration;
    size_t time_configuration_length;
    gomore_primitives_seed_fn seed_random;
    gomore_primitives_random_fn random_value;
    gomore_primitives_mode_lt2_init_fn initialize_small_filter;
    gomore_primitives_mode2_init_fn initialize_large_filter;
    gomore_primitives_void_context_fn finish_sps_initialize;
    gomore_primitives_filter_init_fn initialize_filter;
    const gomore_primitives_log_config *logger;
} gomore_primitives_sleep_algorithm_configuration;

typedef struct {
    void *active_estimator_state;
    uint8_t *result_pointer;
} gomore_primitives_sleep_algorithm_outputs;

typedef struct {
    uint8_t enabled;
    uint8_t sample_count;
    uint8_t reserved[2];
    float sum;
    float output;
    float previous_raw_input;
    float maximum_raw_rise;
    float maximum_raw_fall;
    float maximum_output_rise;
    float maximum_output_fall;
} gomore_primitives_speed_smoother;

typedef struct {
    float smoother_input;
    float mode0_first_input;
} gomore_primitives_dormant_cycle_auxiliary;

typedef struct {
    int32_t sample_index;
    int32_t raw_heart_rate;
    float selected_speed;
    float auxiliary_speed;
    float copied_auxiliary_1;
    float copied_auxiliary_2;
    gomore_primitives_dormant_cycle_auxiliary *auxiliary;
    float unused_heart_rate_feature;
} gomore_primitives_dormant_cycle_input;

typedef struct {
    gomore_primitives_float_unary_fn arctangent;
    gomore_primitives_float_unary_fn cosine;
    gomore_primitives_float_unary_fn sine;
    gomore_primitives_float_binary_fn power;
    gomore_primitives_dormant_root_reduce_fn reduce;
    gomore_primitives_dormant_root_finalize_fn finalize;
    gomore_primitives_integer_filter_update_fn filter_heart_rate;
    gomore_primitives_dormant_ratio_accumulate_fn accumulate_ratio;
} gomore_primitives_dormant_cycle_providers;

typedef struct {
    gomore_primitives_zero_allocate_fn allocate;
    gomore_primitives_void_context_fn release;
    gomore_primitives_sleep_force_prepare_fn prepare;
    gomore_primitives_sleep_force_mode_fn set_mode;
    gomore_primitives_sleep_force_dispatch_fn dispatch;
    gomore_primitives_sleep_force_publish_fn publish;
} gomore_primitives_sleep_force_wake_providers;

typedef enum {
    GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_COMPLETE = 0,
    GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_RECORD_ALLOCATION_FAILED = 1,
    GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_TIMELINE_ALLOCATION_FAILED = 2,
} gomore_primitives_sleep_force_wake_status;

typedef void (*gomore_primitives_authorization_slot_fn)(void *context);
typedef uintptr_t (*gomore_primitives_authorization_stream_register_fn)(
    void *context, uint8_t stream_index);
typedef void (*gomore_primitives_authorization_stream_unregister_fn)(
    void *context, uint8_t stream_index, uintptr_t handle);
typedef uintptr_t (*gomore_primitives_authorization_timer_create_fn)(
    void *context, uint32_t period_milliseconds);
typedef void (*gomore_primitives_authorization_timer_delete_fn)(
    void *context, uintptr_t handle);

typedef struct {
    uint8_t flags;
    gomore_primitives_authorization_slot_fn on_enable;
    gomore_primitives_authorization_slot_fn on_disable;
    void *context;
} gomore_primitives_authorization_slot;

typedef struct {
    bool initialized;
    uintptr_t stream_handles[4];
    uintptr_t idle_timer_handle;
    uintptr_t auxiliary_handles[2];
    float heart_rate_state;
    uint8_t hrv_state;
    gomore_primitives_authorization_slot
        slots[GOMORE_PRIMITIVES_RECORD_COUNT];
} gomore_primitives_authorization_state;

typedef struct {
    void *context;
    gomore_primitives_authorization_stream_register_fn register_stream;
    gomore_primitives_authorization_stream_unregister_fn unregister_stream;
    gomore_primitives_authorization_timer_create_fn create_timer;
    gomore_primitives_authorization_timer_delete_fn delete_timer;
} gomore_primitives_authorization_providers;

typedef struct {
    uint32_t current_time;
    uint32_t sample_index;
    int32_t selected_heart_rate;
    float selected_speed;
    float current_auxiliary;
    float copied_auxiliary_1;
    float copied_auxiliary_2;
    float *configuration;
    float trailing_total_energy;
} gomore_primitives_dormant_estimator_record;

typedef struct {
    float input_history[3][5];
    float output_history[3][5];
    uint32_t warmup_count;
    float magnitude_threshold;
} gomore_primitives_sleep_motion_state;

typedef struct {
    uint32_t order;
    float reserved;
    float feedback[5];
    float feedforward[5];
} gomore_primitives_iir_coefficients;

typedef struct {
    float minute_zero_fraction[15];
    float previous_zero_fraction;
    int8_t zero_count;
    int8_t valid_count;
    uint8_t reserved[2];
    int32_t integer_sum;
} gomore_primitives_minute_accumulator;

typedef struct {
    gomore_primitives_minute_accumulator minute_accumulator;
    uint8_t decimated_ring[90];
    uint8_t reserved_a2[6];
    uint8_t active;
    uint8_t activity_latch;
    uint8_t reserved_aa[6];
    uint32_t countdown;
    uint8_t reserved_b4[2];
    uint8_t local_time_window;
} gomore_primitives_sleep_step_state;

typedef struct {
    uint8_t stage;
    uint8_t transition;
    uint8_t reason;
    uint8_t reserved;
    int32_t adjustment;
} gomore_primitives_sleep_stage_decision;

typedef struct {
    uint32_t timestamp;
    int16_t year;
    uint16_t reserved;
    uint8_t month;
    uint8_t day;
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
    uint8_t padding[3];
} gomore_primitives_civil_time;

typedef struct {
    uint32_t start;
    uint8_t reserved[32];
    uint8_t type;
    uint8_t profile;
    uint8_t preceding_count;
    uint8_t tail;
} gomore_primitives_sleep_descriptor;

typedef struct {
    float value;
    float reciprocal_hours;
    uint8_t source;
    uint8_t auxiliary;
    uint8_t reserved[2];
} gomore_primitives_sps_selection;

typedef struct {
    uint32_t reserved[2];
    uint32_t observations;
    uint32_t lower_count;
    uint32_t upper_count;
    uint32_t positive_count;
    uint32_t quality_count;
    float mean;
    uint32_t mean_count;
} gomore_primitives_statistics_accumulator;

typedef struct {
    uint16_t recent[5];
    uint8_t recent_count;
    uint8_t attempt_count;
    bool measurement_active;
    uint8_t reserved_0d;
    bool capture_enabled;
    uint8_t reserved_0f;
    uint8_t capture_count;
    uint8_t reserved_11;
    uint16_t captured[50];
    uint8_t reserved_76[2];
} gomore_primitives_scaled_sample_state;

typedef enum {
    GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE = 0,
    GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_COMPLETE,
    GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_TIMEOUT,
    GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_INVALID
} gomore_primitives_temperature_measurement_result;

typedef struct {
    uint32_t start;
    uint32_t reserved;
    int32_t totals[5];
    float mean;
    int32_t mean_count;
    uint8_t type;
    uint8_t profile;
    uint8_t tail[2];
} gomore_primitives_interval_descriptor;

typedef struct {
    uint32_t reserved;
    float accumulated;
    uint32_t positive_streak;
    uint32_t zero_streak;
    uint32_t required_streak;
    uint8_t history[5];
    uint8_t padding[3];
} gomore_primitives_step_accumulator;

typedef struct {
    uint32_t start;
    uint32_t end;
    uint32_t count;
    uint32_t reserved[3];
    int32_t sum;
    float metric;
    uint32_t reserved32;
    uint8_t type;
    uint8_t profile;
    uint8_t preceding_count;
    uint8_t tail;
} gomore_primitives_sleep_interval_source;

typedef struct {
    uint32_t start;
    uint32_t end;
    uint32_t source_start;
    uint32_t source_end;
    uint32_t metadata;
    uint32_t clamp_start;
    uint16_t reserved;
    uint8_t flags;
    uint8_t auxiliary;
    uint8_t status;
    uint8_t tail[3];
} gomore_primitives_sleep_interval_result;

typedef struct {
    int16_t minimum_slots;
    uint16_t reserved;
    uint8_t disable_history_scan;
    uint8_t reserved5;
    uint8_t end_hour;
    uint8_t begin_hour;
} gomore_primitives_sleep_interval_policy;

typedef union {
    gomore_primitives_statistics_accumulator statistics;
    gomore_primitives_sleep_descriptor descriptor;
    gomore_primitives_interval_descriptor interval_descriptor;
    gomore_primitives_sleep_interval_source interval_source;
    uint8_t bytes[40];
} gomore_primitives_sleep_cycle_record;

typedef struct {
    gomore_primitives_sleep_step_state step;
    gomore_primitives_sleep_stage_decision last_decision;
    gomore_primitives_sleep_cycle_record current;
    gomore_primitives_interval_descriptor previous_descriptor;
    gomore_primitives_sleep_interval_result previous_interval;
    gomore_primitives_sleep_interval_policy policy;
} gomore_primitives_sleep_cycle_state;

typedef struct {
    uint32_t elapsed_seconds;
    uint32_t current_time;
    int16_t utc_offset_minutes;
    float minute_sample;
    float ring_sample;
    bool input_active;
    bool upper_flag;
    bool lower_flag;
    bool quality_flag4;
    bool quality_flag6;
    float preceding_fraction;
} gomore_primitives_sleep_cycle_input;

typedef struct {
    bool enabled;
    uint8_t control_profile;
    uint8_t control_auxiliary;
    bool high_threshold;
    uint32_t clamp_end;
    uint32_t clamp_start;
    float history[15];
    gomore_primitives_sleep_interval_source base_source;
    gomore_primitives_sleep_interval_result stored;
    gomore_primitives_interval_descriptor aggregation;
    gomore_primitives_sleep_interval_policy policy;
} gomore_primitives_sleep_interval_context;

typedef struct {
    float first[GOMORE_PRIMITIVES_ENERGY_TABLE_MODES];
    float second[GOMORE_PRIMITIVES_ENERGY_TABLE_MODES];
    float weights[GOMORE_PRIMITIVES_ENERGY_TABLE_MODES];
} gomore_primitives_energy_table_configuration;

extern const gomore_primitives_energy_table_configuration
    gomore_primitives_energy_table_defaults;

/* Transparent replacement for the stock 0x5c-byte energy-update state. */
typedef struct {
    int32_t variant;
    int32_t elapsed_since_reference;
    uint8_t mode;
    uint8_t reserved_09_0b[3];
    float smoothed_input;
    float current_rate;
    float blend;
    uint8_t high_counter;
    uint8_t low_counter;
    uint8_t reserved_1a_1b[2];
    float auxiliary_history[10];
    float sustained_zone_increment;
    int32_t sustained_zone_seconds;
    int32_t adaptive_count;
    int32_t adaptive_fall_count;
    float adaptive_average;
    float reference_value;
} gomore_primitives_energy_update_state;

typedef struct {
    float total_kcal;
    float metabolic_equivalent;
    float fat_kcal;
    float carbohydrate_kcal;
    float zone_totals[5];
    float resting_kcal;
    float active_kcal;
} gomore_primitives_energy_update_output;

typedef struct {
    uint32_t local_day;
    int32_t timezone_minutes;
    float cumulative_steps;
    float cumulative_active_kcal;
    float cumulative_total_kcal;
    float cumulative_distance;
    uint8_t reset_visible_reserved[28];
} gomore_primitives_activity_accumulator_state;

typedef struct {
    uint32_t steps;
    int32_t total_kcal;
    int32_t active_kcal;
    float distance;
    uint8_t reserved[28];
} gomore_primitives_activity_accumulator_output;

typedef struct {
    float age_years;
    float binary_sex;
    float height_centimeters;
    float weight_kilograms;
    float parameter_4;
    float parameter_5;
    float parameter_6;
} gomore_primitives_profile_input;

typedef struct {
    uint8_t age_years;
    uint8_t binary_sex;
    uint8_t reserved[2];
    float height_centimeters;
    float weight_kilograms;
    float parameter_4;
    float parameter_5_raw;
    float parameter_5_normalized;
    float cached_parameters[2];
} gomore_primitives_profile_output;

typedef struct {
    float interval_minutes;
    float leading_awake_minutes;
    float non_awake_minutes;
    float middle_awake_minutes;
    float awake_after_onset_minutes;
    float non_awake_plus_middle_minutes;
    float efficiency;
    float nrem_fraction;
    float rem_fraction;
    float light_fraction;
    float deep_fraction;
    float rem_to_nrem_ratio;
    float deep_to_light_ratio;
    float deep_to_rem_ratio;
    float deep_to_nrem_ratio;
    float awake_minutes;
    float rem_minutes;
    float light_minutes;
    float deep_minutes;
} gomore_primitives_sleep_statistics;

typedef bool (*gomore_primitives_sleep_stage_refine_fn)(
    const uint8_t configuration[11], int8_t *stages,
    size_t stage_capacity, size_t *stage_count,
    uint32_t duration_seconds);

typedef struct {
    uint32_t start_timestamp;
    uint32_t end_timestamp;
    int8_t *stages;
    size_t stage_capacity;
    size_t stage_count;
    uint8_t wire_type;
    gomore_primitives_sleep_statistics statistics;
    float score;
} gomore_primitives_final_sleep_build_output;

typedef struct {
    uint8_t filter_state[0x50];
    float window[75];
    uint8_t positions[12];
    uint8_t position_count;
    uint8_t reserved[3];
} gomore_primitives_sleep_optical_history;

typedef struct {
    const float *samples;
    bool invalid;
} gomore_primitives_sleep_optical_input;

typedef struct {
    float centers[3];
    float divisors[3];
    float weights[3];
    float bias;
} gomore_primitives_linear_model3;

typedef struct {
    float coefficients[6];
} gomore_primitives_affine_reciprocal_model4;

typedef struct {
    float heart_rate;
    uint32_t quality;
} gomore_primitives_hr_candidate;

typedef struct {
    float heart_rate;
    uint32_t quality;
    uint8_t source;
} gomore_primitives_hr_selection;

typedef struct {
    gomore_primitives_prepare_fn prepare;
    gomore_primitives_score_fn score;
} gomore_primitives_score_providers;

/* 0x6AD04: true only when bit zero is clear in all seven 16-byte records. */
bool gomore_primitives_records_all_clear(const uint8_t *records,
                                         size_t record_bytes);

/* 0x715B8 / 0x71A20: recovered 32-bit record constructors. */
void gomore_primitives_record5_initialize(uint32_t record[5],
                                          bool add_record_offset,
                                          uint32_t field4,
                                          uint32_t field8,
                                          uint32_t base);
void gomore_primitives_span_initialize(uint32_t record[2],
                                       bool add_record_offset,
                                       uint32_t base);

/* 0x883D4 / 0x71B2A / 0x71704. */
bool gomore_primitives_clear_two_records(void *record, size_t length);
bool gomore_primitives_fill_missing_pair(float values[2]);
bool gomore_primitives_clear_90(void *record, size_t length);

/* 0x68FBC: call the five-argument preparation routine, then score its
 * workspace into the caller's output. */
bool gomore_primitives_prepare_and_score(
    const gomore_primitives_score_providers *providers,
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *workspace, float *output);

/* 0x72AD4: exact unsigned float-bit-pattern range predicate. */
bool gomore_primitives_float_in_encoded_range(float value);

/* 0x58060: choose the state-1 cadence sample and report 3-sample consensus. */
float gomore_primitives_state1_cadence_estimate(
    float first, float middle, float latest, uint8_t *consensus);

/* 0x57F8C: choose the state-2 cadence sample and report 3-sample consensus. */
float gomore_primitives_state2_cadence_estimate(
    float first, float middle, float latest, uint8_t *consensus);

/* 0x761F8: accumulate a consistent locomotion transition pair. */
bool gomore_primitives_locomotion_transition_accumulate(
    gomore_primitives_locomotion_transition_state *state,
    float target, uint8_t previous, uint8_t current,
    float shape_first, float shape_second, bool *updated);

/* 0x582C4: rank three circular Int16 windows and gate two crossing counts. */
int32_t gomore_primitives_three_axis_window_gate(
    const int16_t *first, const int16_t *second, const int16_t *third,
    size_t sample_count, uint8_t ring_length, int32_t current_index,
    uint32_t window_count, int32_t primary_threshold,
    int32_t secondary_threshold);

/* 0x67E4C: compose one complete locomotion feature/classification output. */
bool gomore_primitives_locomotion_window_classify(
    void *state, size_t state_length,
    void *output, size_t output_length,
    const gomore_primitives_locomotion_classifier_configuration *configuration);

/* 0x74914: fixed fourth-order motion filter with five-sample histories. */
bool gomore_primitives_motion_iir4_filter(
    float *samples, size_t count,
    float input_history[5], float output_history[5]);

/* 0x94698: accumulate a normalized value into six bounded histogram bins. */
bool gomore_primitives_weighted_histogram6_accumulate(
    float value, float denominator, float numerator,
    const float boundaries[5], float sums[6], float counts[6],
    float below_range_weight);
uint32_t gomore_primitives_speed_smoother_update(
    gomore_primitives_speed_smoother *state,
    float input, uint32_t interval_milliseconds,
    float *output, uint8_t *stable_or_clamped);

/* 0x908E0: flag-dependent active-estimator speed gate and rolling history. */
float gomore_primitives_speed_gate(
    float raw_candidate, float previous_output,
    float history[6], int32_t sample_index, uint32_t flags);

/* 0x90C54: flag-dependent speed-dynamics baseline contribution. */
float gomore_primitives_speed_dynamics_baseline(
    float input, float auxiliary,
    float state_first_parameter, float state_second_parameter,
    uint16_t flags, gomore_primitives_float_binary_fn power);

/* 0x5FEB8: dormant estimator mode gate, input composition, and replay wrapper. */
int32_t gomore_primitives_dormant_estimator_update(
    void *state, size_t state_length, uint32_t elapsed,
    const uint32_t *current_time, const float *selected_heart_rate,
    const float *selected_speed, const float profile[6],
    const float auxiliary[3], const float *total_energy,
    void *output, size_t output_length,
    gomore_primitives_record_step_fn process_record);

/* 0x5F3D8: three-axis resample/filter/compact sleep-motion feature. */
int32_t gomore_primitives_sleep_motion_feature(
    gomore_primitives_sleep_motion_state *state, uint32_t mode,
    const float *channels[3], bool input_unavailable, float output[2],
    gomore_primitives_float_unary_fn floor_value,
    gomore_primitives_float_unary_fn square_root);

/* 0x947DE: fifteen-slot per-minute zero-fraction accumulator. */
bool gomore_primitives_minute_accumulator_update(
    gomore_primitives_minute_accumulator *state,
    uint32_t elapsed_seconds, uint32_t current_time, float sample);

/* 0x71618: construct the pointer/tensor-binding plan for 20-byte banks. */
bool gomore_primitives_tensor_bank_initialize(
    uintptr_t *layout, size_t layout_capacity,
    bool include_secondary_bank, bool paired, uint32_t item_count,
    uint32_t *tensor_bindings, size_t tensor_binding_capacity,
    uint8_t *records, size_t record_count,
    uintptr_t runtime_binding, uintptr_t pool_binding,
    gomore_primitives_tensor_fill_binding_fn create_filled_tensor);

/* 0x64274: stateless fixed-coefficient second-order Float32 IIR. */
bool gomore_primitives_sleep_iir2_filter(float *samples, size_t count);

/* 0x94070: compose one private sleep-step state update. */
bool gomore_primitives_sleep_step_update(
    gomore_primitives_sleep_step_state *state,
    uint32_t elapsed_seconds, const uint8_t control[2],
    uint32_t current_time, int16_t utc_offset_minutes,
    float minute_sample, float ring_sample, bool external_activity,
    const uint8_t local_hour_window[8],
    gomore_primitives_civil_time *civil_time,
    bool *civil_time_updated);

/* 0x5C19C: select one private sleep stage and transition/reason record. */
bool gomore_primitives_sleep_stage_decide(
    const void *state, size_t state_length,
    uint32_t current_time, uint32_t elapsed_seconds,
    uint32_t reference_time, uint8_t prior_stage,
    bool external_active, float preceding_fraction,
    gomore_primitives_sleep_stage_decision *decision);

/* 0x60B80: compose one complete private sleep decision/update cycle. */
bool gomore_primitives_sleep_cycle_update(
    gomore_primitives_sleep_cycle_state *state,
    const gomore_primitives_sleep_cycle_input *input,
    gomore_primitives_sleep_interval_result *output);

/* 0x71A32: initialize every recovered substate in the 0x3894-byte engine. */
bool gomore_primitives_composite_engine_initialize(
    void *state, size_t state_length,
    uint8_t *time_configuration, size_t time_configuration_length,
    void **active_estimator_state, uint8_t **result_pointer,
    gomore_primitives_mode2_init_fn initialize_large_filter,
    gomore_primitives_void_context_fn finish_sps_initialize,
    gomore_primitives_filter_init_fn initialize_filter);

/* 0x5FF94: run the complete fixed-order output-stage schedule. */
bool gomore_primitives_output_orchestrate(
    void *engine, size_t engine_length, uint32_t elapsed_updates,
    const gomore_primitives_output_orchestrator_providers *providers,
    uint8_t **result_pointer);

/* 0x6FEA0: authorize and initialize the complete sleep-algorithm engine. */
int32_t gomore_primitives_sleep_algorithm_initialize(
    void *engine, size_t engine_length, uint32_t runtime_value,
    const gomore_primitives_profile_input *profile,
    void *previous_state, size_t previous_state_length,
    uint32_t previous_state_binding,
    const gomore_primitives_sleep_algorithm_configuration *configuration,
    gomore_primitives_sleep_algorithm_outputs *outputs);

/* 0x675DC: assemble three Cardano candidates from paired radicals. */
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
    gomore_primitives_float_unary_fn sine);

/* 0x68E5C: exact three-feature SPS secondary model. */
float gomore_primitives_sps_secondary_model(
    const float features[3],
    gomore_primitives_double_unary_fn square_root);

/* 0x67C30: expand control points over rounded half-position spans. */
bool gomore_primitives_expand_half_positions(
    const uint16_t *positions, const float *control_values,
    size_t control_count, float *output, size_t output_count,
    gomore_primitives_double_unary_fn round_value);

/* 0x56DC0: filter locomotion control points, expand, and reduce features. */
bool gomore_primitives_locomotion_control_extract(
    const gomore_primitives_locomotion_control_sample *samples,
    size_t sample_count, float sample_period, float difference_scale,
    uint32_t mode,
    gomore_primitives_locomotion_control_workspace *workspace,
    gomore_primitives_double_unary_fn round_value,
    gomore_primitives_locomotion_feature_reduce_fn reduce,
    const gomore_primitives_locomotion_feature_reduce_math *reduce_math,
    float *primary, float *secondary,
    size_t *accepted_count, int32_t *status);
/* 0x68840: normalize/filter extrema and reduce paired periods. */
bool gomore_primitives_locomotion_feature_reduce(
    float expanded[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT],
    uint8_t first_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    uint8_t second_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    float controls[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY],
    float *primary, float *secondary,
    const gomore_primitives_locomotion_feature_reduce_math *math);

/* 0x6AD80: load and CRC-validate the fixed 64-byte pKey record. */
bool gomore_primitives_pkey_load(
    gomore_primitives_pkey_store *store,
    uint8_t *key, size_t key_capacity,
    gomore_primitives_pkey_result *result);

/* 0x6B27C: assemble device/pKey authorization parameters and apply them. */
bool gomore_primitives_auth_parameters_setup(
    const gomore_primitives_auth_setup_configuration *configuration,
    int32_t *status);

/* 0x8EA0C: decode, authenticate, and dispatch a four-field SDK token. */
bool gomore_primitives_sdk_auth_parse(
    const gomore_primitives_auth_parameters *parameters,
    const gomore_primitives_sdk_auth_configuration *configuration,
    gomore_primitives_sdk_auth_status *status, int32_t *result);

/* 0x6AFB0: restore the newest exact-length previous-state slot. */
bool gomore_primitives_previous_state_restore(
    gomore_primitives_pkey_store *store,
    uint8_t key[64], void *state, size_t state_length,
    gomore_primitives_previous_state_result *result);

/* 0x6BBB0: append one aligned previous-state record, compacting the shared
 * pKey page when the third slot is occupied.  The source capacity makes the
 * stock routine's aligned read contract explicit; scratch is only consumed
 * during compaction and must hold the aligned key record. */
gomore_primitives_previous_append_status
gomore_primitives_previous_state_append(
    gomore_primitives_pkey_store *store,
    const void *state, size_t state_length, size_t state_capacity,
    void *scratch, size_t scratch_capacity,
    gomore_primitives_previous_append_result *result);

/* 0x6808C: solve cubic coefficients into three Cardano candidates. */
bool gomore_primitives_cubic_candidates(
    float a, float b, float c, float d,
    void *destination, size_t destination_length,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_float_binary_fn arctangent2,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_float_unary_fn logarithm,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine);

/* 0x928DA plus its shared head at 0x928CC: vector scalar multiply. */
bool gomore_primitives_scale(float factor, const float *source,
                             float *destination, size_t count);

/* 0x94A4C: clear byte +0xB4 and store two 32-bit callback fields. */
bool gomore_primitives_callback_record_initialize(uint8_t *record,
                                                  size_t length,
                                                  uint32_t field_b8,
                                                  uint32_t field_bc);

/* 0x87600: sort inclusive float subrange [first,last]. */
bool gomore_primitives_sort_float_subrange(
    float *values, size_t value_count, size_t first, size_t last,
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare);

/* 0x91A56: unpack {values,count} and tail-call the max-index provider. */
int32_t gomore_primitives_max_index(const float *values, uint32_t count,
                                    gomore_primitives_max_index_fn provider);

/* 0x64770. */
bool gomore_primitives_set_second_word(uint32_t record[2], uint32_t value);

/* 0x68720 / 0x6841A / 0x5A442. */
uint32_t gomore_primitives_size_736(void);
uint32_t gomore_primitives_size_14816(void);
uint32_t gomore_primitives_return_zero(void);

/* 0x76500 / 0x578C8 / 0x49E58: distinct empty callbacks retained as
 * distinct symbols because their ownership extents are distinct. */
void gomore_primitives_noop_76500(void);
void gomore_primitives_noop_578c8(void);
void gomore_primitives_noop_49e58(void);

/* Additional fully recovered leaf and initializer closure. */
void gomore_primitives_noop_91080(void);
bool gomore_primitives_clear_72(void *record, size_t length);
bool gomore_primitives_store_first_word(uint32_t *record, uint32_t value);
bool gomore_primitives_clear_first_byte(uint8_t *record);
bool gomore_primitives_triplet_initialize(uint32_t record[3],
                                          uint32_t field4,
                                          uint32_t field0,
                                          uint32_t field8);
float gomore_primitives_interpolate(float weight, float first, float second);
bool gomore_primitives_byte_in_70_100(uint8_t value);
bool gomore_primitives_clear_flag_1000(uint8_t *state, size_t length);
float gomore_primitives_cubic_scale(float value);
float gomore_primitives_linear_evaluate(float value, float slope,
                                        float intercept);
bool gomore_primitives_shift_u8_window5(uint8_t values[5], uint8_t value);
size_t gomore_primitives_nullable_strlen(const char *text);
bool gomore_primitives_u16_in_30000_50000(uint16_t value);
bool gomore_primitives_clear_36(void *record, size_t length);
bool gomore_primitives_step_record_initialize(void *record, size_t length);
bool gomore_primitives_clear_124(void *record, size_t length);
bool gomore_primitives_float_state_initialize(void *record, size_t length);
uint32_t gomore_primitives_half_to_float_bits(uint16_t value);
bool gomore_primitives_store_half_as_float_bits(uint32_t *destination,
                                                uint16_t value);

/* Fully recovered record/math utility and paired-initializer closure. */
int32_t gomore_primitives_find_next_nonnegative_i16(
    const int16_t *values, size_t count, size_t start);
bool gomore_primitives_shift_two_u8_windows5(
    uint8_t first[5], uint8_t second[5],
    uint8_t first_value, uint8_t second_value);
float gomore_primitives_normalized_position(float value, float high,
                                            float low);
bool gomore_primitives_packed_2bit_get(const uint8_t *bytes,
                                       size_t length, uint32_t index,
                                       uint8_t *value);
bool gomore_primitives_energy_state_reset(void *record, size_t length);
bool gomore_primitives_large_default_state_initialize(void *record,
                                                      size_t length);
bool gomore_primitives_scale_milli(float *values, size_t count);
bool gomore_primitives_sps_state_reset(void *record, size_t length);
bool gomore_primitives_shift_status_windows(uint8_t history[10],
                                            uint8_t output[3]);
size_t gomore_primitives_count_byte_plus_one(const uint8_t *values,
                                             size_t count,
                                             uint8_t target);
bool gomore_primitives_accumulate_pair(void *record, size_t length,
                                       float first, float second);
bool gomore_primitives_selected_state_reset(void *record, size_t length);
bool gomore_primitives_pattern17_initialize(void *record, size_t length);
bool gomore_primitives_energy_record_initialize(void *record, size_t length,
                                                uint32_t binding);
bool gomore_primitives_large_state_initialize(void *record, size_t length,
                                              uint32_t binding,
                                              void **active_record);

/* Pure constructor, lookup, reset, comparison, and transform closure. */
bool gomore_primitives_low24_binding_initialize(
    uint32_t record[2], const uint8_t value[3], uint32_t binding);
bool gomore_primitives_pack4_binding_initialize(
    uint32_t record[2], uint8_t byte0, uint8_t byte1,
    uint8_t byte2, uint8_t byte3, uint32_t binding);
int16_t gomore_primitives_i16_mean(const int16_t *values, size_t count);
bool gomore_primitives_float_floor_update(float candidate, float *value);
bool gomore_primitives_validate_selector(const uint8_t *state,
                                         size_t length, int8_t *selector);
int32_t gomore_primitives_nullable_compare(const uint8_t *left,
                                           const uint8_t *right);
bool gomore_primitives_compact_u32_stride(uint32_t *values,
                                          size_t capacity,
                                          size_t count, size_t stride,
                                          size_t *output_count);
int32_t gomore_primitives_status_record_extract(const void *source,
                                                size_t source_length,
                                                void *destination,
                                                size_t destination_length);
bool gomore_primitives_half_span_initialize(uint32_t record[5],
                                            uint16_t half_value,
                                            uint32_t base);
bool gomore_primitives_parameter_state_initialize(void *record,
                                                  size_t length,
                                                  uint32_t binding);
size_t gomore_primitives_count_encoded_i32(const int32_t *values,
                                           size_t count);
float gomore_primitives_scaled_ratio(float numerator, float denominator);
uint8_t gomore_primitives_piecewise_clamp_70_100(int32_t value);
bool gomore_primitives_missing_window_initialize(void *record,
                                                 size_t length);
bool gomore_primitives_modulo_value_get(const uint8_t *bytes,
                                        size_t length, uint32_t index,
                                        bool packed, uint8_t *value);
bool gomore_primitives_mode8_state_initialize(void *record, size_t length);

/* Pure 42...62-byte vector, record, and predicate closure. */
bool gomore_primitives_vector_pair_transform(float scale, float offset,
                                             const float left[2],
                                             const float right[2],
                                             float output[2]);
bool gomore_primitives_encode_short_record(uint8_t record[17],
                                           const uint8_t *payload,
                                           size_t payload_length);
bool gomore_primitives_accumulate_i8x4_milli(float values[4],
                                             const int8_t increments[4]);
uint32_t gomore_primitives_shift_presence_history(uint8_t *record,
                                                  size_t length,
                                                  uint8_t value);
bool gomore_primitives_fill_float_progression(float *values, size_t count,
                                              size_t begin, size_t end,
                                              float first, float step);
bool gomore_primitives_time_record_valid(const void *record, size_t length);
size_t gomore_primitives_float_argmax_range(const float *values,
                                            size_t count, size_t begin,
                                            size_t end);
int32_t gomore_primitives_float_argmax_above_floor(const float *values,
                                                   size_t count);
int32_t gomore_primitives_i16_range(const int16_t *values, size_t count);
bool gomore_primitives_packed_2bit_set(uint8_t *bytes, size_t length,
                                      uint32_t index, uint8_t value);
float gomore_primitives_rational_transform(float value, float state);
int16_t gomore_primitives_i16_mean_absolute_difference(
    const int16_t *values, size_t count);
bool gomore_primitives_u16_all_within_300(const uint16_t *values,
                                         size_t count, uint16_t target);
float gomore_primitives_nonzero_i16_mean8(const int16_t values[8]);
float gomore_primitives_circular_u8_dot18(const uint8_t values[18],
                                         uint32_t sample_index,
                                         const float weights[18]);
/* 0x5F264: 30-second motion bucket aggregation and weighted gate score. */
bool gomore_primitives_motion_gate_accumulate(
    gomore_primitives_motion_gate_state *state,
    uint32_t elapsed_seconds, uint32_t current_timestamp,
    float sample, const float weights[18],
    gomore_primitives_motion_gate_output *output);

/* 0x6859C: local-maximum spacing and value statistics. */
bool gomore_primitives_peak_statistics(
    const float *values, size_t count, size_t radius, float output[4],
    gomore_primitives_float_binary_fn power,
    gomore_primitives_float_unary_fn square_root);

/* 0x8F4E8: difference sign-run and transition statistics. */
bool gomore_primitives_direction_change_statistics(
    float normalizer, float threshold_scale,
    gomore_primitives_difference_mode mode,
    const void *samples, size_t difference_count,
    gomore_primitives_direction_change_output *output);

/* 0x70498: active-only dormant integer heart-rate filter. */
int32_t gomore_primitives_dormant_heart_rate_filter_update(
    void *state, int32_t input, int32_t output[2],
    uint32_t interval_milliseconds);

/* 0x56A0C: six-channel circular-window linear score. */
bool gomore_primitives_six_channel_ring_score(
    const int16_t *channel0, const int16_t *channel1,
    const int16_t *channel2, const int16_t *channel3,
    const int16_t *channel4, const int16_t *channel5,
    size_t ring_size, size_t cursor, size_t window_count,
    const gomore_primitives_six_channel_linear_model *model,
    int16_t *output);
int32_t gomore_primitives_filtered_u8_mean(const uint8_t *values,
                                          size_t count, int32_t center,
                                          int32_t tolerance);
bool gomore_primitives_complex_multiply(const float left[2],
                                        const float right[2],
                                        float output[2]);
bool gomore_primitives_complex_power(
    float exponent, float value[2],
    gomore_primitives_float_binary_fn arctangent2,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_float_unary_fn logarithm,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine);
bool gomore_primitives_circular_feature_slot_advance(
    void *state, size_t state_length);
bool gomore_primitives_circular_i16_mean3(
    const int16_t *first, const int16_t *second, const int16_t *third,
    size_t ring_size, size_t cursor, size_t count,
    int16_t output[3]);
int16_t gomore_primitives_circular_positive_fill_mean(
    const int16_t *values, size_t ring_size, size_t cursor,
    size_t begin_distance, size_t end_distance);
bool gomore_primitives_locomotion_crossing_wrapper(
    const int16_t baseline_ring[8], int32_t baseline_cursor,
    const uint16_t *samples, size_t sample_count,
    float *mode2_output, float *mode1_output,
    gomore_primitives_locomotion_crossing_estimate_fn estimate);
/* 0x56F94: derive one cadence estimate from 200 UInt16 magnitudes. */
bool gomore_primitives_locomotion_crossing_period_estimate(
    const uint16_t *samples, size_t sample_count, int16_t baseline,
    uint32_t mode, float *output);
bool gomore_primitives_final_sleep_record_publish(
    bool enabled, uintptr_t record_binding,
    const gomore_primitives_final_sleep_providers *providers,
    bool *published, uint16_t *published_length);
/* 0x6B50C: force one sleep interval update and optional final publication. */
bool gomore_primitives_sleep_force_wake(
    bool mode_control_enabled,
    const gomore_primitives_sleep_force_wake_providers *providers,
    gomore_primitives_sleep_force_wake_status *status);
bool gomore_primitives_dormant_heart_rate_ratio_wrapper(
    void *state, size_t state_length, int32_t raw_heart_rate,
    gomore_primitives_integer_filter_update_fn filter_update,
    gomore_primitives_dormant_ratio_accumulate_fn ratio_accumulate,
    int32_t *filter_status);
/* 0x96634: running dormant HR/speed ratio moments and secondary bins. */
bool gomore_primitives_dormant_ratio_accumulator(
    gomore_primitives_dormant_ratio_accumulator_state *state,
    const gomore_primitives_dormant_ratio_input *input,
    gomore_primitives_float_binary_fn power);
/* 0x721B4: compose one dormant speed/heart-rate estimator cycle. */
bool gomore_primitives_dormant_estimator_cycle(
    void *state, size_t state_length,
    gomore_primitives_dormant_cycle_input *input,
    const gomore_primitives_dormant_cycle_providers *providers,
    int32_t *result);
bool gomore_primitives_dormant_speed_root_build(
    float primary, float auxiliary, void *state, size_t state_length,
    int32_t mode, gomore_primitives_float_binary_fn power,
    gomore_primitives_quadratic_dispatch_fn solve_quadratic,
    gomore_primitives_cubic_dispatch_fn solve_cubic);
/* 0x888A0: shared dormant speed energy/root reduction. */
bool gomore_primitives_dormant_root_reduce(
    float primary, float secondary, float auxiliary,
    void *state, size_t state_length, int32_t mode,
    gomore_primitives_float_unary_fn arctangent,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_binary_fn power,
    float *output);
bool gomore_primitives_dormant_alternate_root_solve(
    float primary, float auxiliary, void *state, size_t state_length,
    int32_t mode,
    gomore_primitives_quadratic_dispatch_fn solve_quadratic,
    gomore_primitives_cubic_dispatch_fn solve_cubic,
    float *output);
/* 0x8141C: resolve the final normalized dormant speed root. */
bool gomore_primitives_dormant_root_resolve(
    float primary, float auxiliary, void *state, size_t state_length,
    int32_t mode, gomore_primitives_float_binary_fn power,
    gomore_primitives_quadratic_dispatch_fn solve_quadratic,
    gomore_primitives_cubic_dispatch_fn solve_cubic,
    float *output);
bool gomore_primitives_dormant_speed_mode1_target_update(
    float first_input, float selected_speed,
    void *state, size_t state_length, int32_t mode,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output);
bool gomore_primitives_dormant_speed_mode1_target_veneer(
    float first_input, float selected_speed,
    void *state, size_t state_length,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output);
bool gomore_primitives_dormant_speed_mode0_target_update(
    float first_input, float selected_speed,
    void *state, size_t state_length, int32_t mode,
    gomore_primitives_float_unary_fn arctangent,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output);
bool gomore_primitives_dormant_speed_mode0_target_veneer(
    float first_input, float selected_speed,
    void *state, size_t state_length,
    gomore_primitives_float_unary_fn arctangent,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_dormant_root_reduce_fn reduce,
    gomore_primitives_dormant_root_finalize_fn finalize,
    float *output);
bool gomore_primitives_sleep_graph_family_dispatch(
    void *state, size_t state_length, uint32_t arena_seed,
    const uint8_t dimensions_by_family[24], size_t dimensions_length,
    uint32_t recurrent_executor, uint32_t softmax_executor,
    gomore_primitives_sleep_graph_zero_build_fn build_zero,
    gomore_primitives_sleep_graph_nonzero_build_fn build_nonzero,
    gomore_primitives_sleep_graph_recurrent_construct_fn construct_recurrent,
    gomore_primitives_sleep_graph_dense_construct_fn construct_dense);
bool gomore_primitives_host_input_adapter_update(
    void *engine, size_t engine_length,
    const gomore_primitives_host_input *input,
    uint32_t previous_update_timestamp,
    float raw_optical_output[25], float accelerometer_outputs[3][25],
    const gomore_primitives_host_input_bindings *bindings,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger,
    gomore_primitives_input_adapter_core_fn update_core);
/* 0x6B114: decode the exact 188-byte acc batch into the GoMore axis order. */
bool gomore_primitives_topic_accelerometer_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *batch, size_t batch_length);
/* 0x6B228: decode count + UInt32LE raw optical samples. */
bool gomore_primitives_topic_raw_optical_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *packet, size_t packet_length);
/* 0x6B1B8: stage one UInt8 direct-heart-rate observation. */
bool gomore_primitives_topic_heart_rate_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *packet, size_t packet_length);
/* 0x6B1F4: clear and copy at most four UInt16LE HRV auxiliary values. */
bool gomore_primitives_topic_hrv_ingest(
    gomore_primitives_topic_input_state *state,
    const uint8_t *packet, size_t packet_length);
/* 0x6B0D4: consume the acc/raw readiness barrier and clear all ready bits. */
bool gomore_primitives_topic_update_take_ready(
    gomore_primitives_topic_input_state *state,
    bool accelerometer_required, bool raw_optical_required);
/* 0x6ACC8: successful engine updates consume only acc/raw sample counts. */
void gomore_primitives_topic_update_complete(
    gomore_primitives_topic_input_state *state, bool succeeded);
/* 0x94384: validate, normalize, apply, snapshot, and commit one sensor update. */
bool gomore_primitives_sensor_update_orchestrate(
    const void *context,
    gomore_primitives_sensor_update_state *state,
    const gomore_primitives_host_input *input,
    const gomore_primitives_sensor_update_configuration *configuration,
    const gomore_primitives_sensor_update_providers *providers,
    int32_t *result_status);
/* 0x96E74: classify one 250-sample activity window. */
bool gomore_primitives_activity_state_classify250(
    const float *samples, size_t sample_count, bool alternate_mode,
    float differences[249], size_t difference_capacity,
    gomore_primitives_activity_statistics_fn statistics,
    bool *classified);
/* 0x6138C: condition, accumulate, and classify activity windows. */
bool gomore_primitives_activity_window_update(
    gomore_primitives_activity_window_state *state, float input_quality,
    const gomore_primitives_activity_window_input *input,
    const gomore_primitives_activity_window_providers *providers,
    float differences[249], size_t difference_capacity,
    gomore_primitives_activity_window_output *output);
/* 0x60680: update the five-sample optical respiratory-rate history. */
bool gomore_primitives_respiratory_rate_update(
    gomore_primitives_respiratory_rate_state *state, uint32_t elapsed,
    const gomore_primitives_respiratory_rate_input *input,
    void *estimator_state,
    const gomore_primitives_respiratory_rate_providers *providers,
    float output[2], uint32_t *status);
bool gomore_primitives_optical_period_candidates_select(
    float mode1_rate, float mode1_quality,
    float mode2_rate, float mode2_quality,
    float fallback_rate, float fallback_quality,
    float output[2]);
/* 0x69834: update and reduce the complete optical-period estimator state. */
bool gomore_primitives_optical_period_estimate(
    gomore_primitives_optical_interval_state *state,
    uint32_t elapsed_windows, const float input[25], uint32_t flags,
    const gomore_primitives_optical_period_providers *providers,
    gomore_primitives_optical_period_workspace *workspace,
    float output[2], int32_t *status);
/* 0x4857C: merge ordered optical interval candidates and emit mean amplitude. */
bool gomore_primitives_optical_interval_merge(
    gomore_primitives_optical_interval_state *state,
    const uint8_t *end_positions, const uint8_t *start_positions,
    size_t candidate_count, float *mean_amplitude);
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
    void *classify_context);
/* 0x88450: execute the complete fixed sleep-stage neural classifier. */
bool gomore_primitives_sleep_stage_classify(
    gomore_primitives_sleep_stage_classifier_result *result,
    gomore_primitives_sleep_stage_stream_state *state,
    uint8_t iteration, const int8_t mode_adjustment[4], void *context);
bool gomore_primitives_peak_candidate_match(
    const float *signal, size_t signal_count,
    uint8_t candidates[20], uint8_t references[20],
    uint8_t *candidate_count, uint8_t *reference_count,
    float *median_spacing, float workspace[25],
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_float_unary_fn square_root);
bool gomore_primitives_motion_classifier_update(
    uint8_t state[17], size_t state_length, uint32_t elapsed_seconds,
    const uint8_t *source, size_t source_length,
    const uint8_t features[62], size_t feature_length,
    uint8_t output[3], size_t output_length,
    /* NULL selects gomore_primitives_state1_cadence_estimate. */
    gomore_primitives_state1_cadence_estimate_fn estimate_state1);
/* 0x9413C: estimate, range-gate, and smooth the final locomotion cadence. */
bool gomore_primitives_motion_classifier_finalize(
    uint8_t state[17], size_t state_length,
    const uint8_t *features, size_t feature_length,
    uint8_t output[3], size_t output_length,
    /* NULL selects gomore_primitives_state1_cadence_estimate. */
    gomore_primitives_state1_cadence_estimate_fn estimate_state1);
bool gomore_primitives_sps_state_initialize(
    void *state, size_t state_length);
float gomore_primitives_rolling_mean5_update(
    float value, float window[5], uint32_t observation_index);
float gomore_primitives_nearest_nonzero3(
    float target, const float values[3]);
float gomore_primitives_activity_scaled_quadratic_difference(
    float primary, float reference, float scale, float gain,
    gomore_primitives_float_binary_fn power);
float gomore_primitives_affine_reciprocal_model4_evaluate(
    const float values[4],
    const gomore_primitives_affine_reciprocal_model4 *model);
float gomore_primitives_bounded_linear_complement(
    float primary, float secondary);
bool gomore_primitives_locomotion_autocorrelation_wrapper(
    bool enabled, const uint16_t *samples, float outputs[5],
    uintptr_t first_binding, uintptr_t second_binding,
    gomore_primitives_autocorrelation_analyze_fn analyze);

bool gomore_primitives_locomotion_autocorrelation_analyze(
    const uint16_t samples[100],
    float *first, float *second, float *third, float *fourth, float *fifth,
    uintptr_t first_binding, uintptr_t second_binding);
bool gomore_primitives_select_heart_rate(
    uint8_t state, float direct,
    const gomore_primitives_hr_candidate *estimated,
    gomore_primitives_hr_selection *output);
bool gomore_primitives_sps_model_dispatch(
    void *state, size_t state_length, const float values[4],
    gomore_primitives_feature_model_fn primary_model0,
    gomore_primitives_feature_model_fn secondary_model0,
    gomore_primitives_feature_model_fn primary_model1,
    gomore_primitives_feature_model_fn secondary_model1,
    gomore_primitives_state_adjust_fn adjust,
    gomore_primitives_state_pair_commit_fn commit,
    float *primary, float *secondary);
/* 0x5EF1C: update the bounded accelerometer SPS candidate state. */
bool gomore_primitives_sps_accelerometer_candidate_update(
    gomore_primitives_sps_candidate_state *state, uint32_t elapsed_updates,
    const gomore_primitives_sps_features *features,
    const gomore_primitives_sps_motion *motion, float height_centimeters,
    const gomore_primitives_sps_candidate_providers *providers,
    gomore_primitives_sps_candidate_output *output);
/* 0x4BD98: complete authorization/restore/profile/health initialization. */
gomore_primitives_health_lifecycle_result
gomore_primitives_health_lifecycle_initialize(
    gomore_primitives_health_lifecycle_state *state,
    bool force_default_previous,
    uint8_t previous_data[GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES],
    const uint8_t default_profile[GOMORE_PRIMITIVES_USER_PROFILE_BYTES],
    uint8_t output_descriptor[GOMORE_PRIMITIVES_OUTPUT_DESCRIPTOR_BYTES],
    uint32_t output_storage_address, uint32_t output_record_address,
    const gomore_primitives_health_lifecycle_providers *providers,
    int32_t *provider_status);
bool gomore_primitives_base64_decode_blocks(
    const uint8_t *input, size_t input_length,
    uint8_t *output, size_t output_capacity, size_t *written);
uint8_t gomore_primitives_dominant_quantized_u8_mean5(
    const uint8_t values[5]);
bool gomore_primitives_dual_dominant_u8_select(
    const uint8_t values[5], const int8_t categories[5],
    int32_t *value_output, int32_t *category_output);
uint32_t gomore_primitives_update_failure_counter(
    uint32_t status, uint32_t timestamp, uint8_t *counter,
    gomore_primitives_update_failure_log_fn log_failure,
    gomore_primitives_simple_fn reset_provider);
int32_t gomore_primitives_shift_i16_trend_gate5(
    int16_t history[5], int32_t sample);
bool gomore_primitives_sps_refresh_affine_pairs(
    const float source[4], float first[2], uint32_t *first_mode,
    float second[2], uint32_t *second_mode);
bool gomore_primitives_positive_quadratic_roots(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float roots[2], gomore_primitives_float_binary_fn power);
bool gomore_primitives_activity_score_variability_adjust(
    float *score, const float *const axes[3], bool skip_variability,
    gomore_primitives_float_unary_fn square_root);
bool gomore_primitives_epoch_to_civil_time(
    uint32_t timestamp, gomore_primitives_civil_time *output);
bool gomore_primitives_copy_algorithm_output_snapshot(
    uint8_t *destination, size_t destination_length,
    const uint8_t *source, size_t source_length);
bool gomore_primitives_sleep_descriptor_initialize(
    gomore_primitives_sleep_descriptor *descriptor,
    const float history[15], bool use_high_threshold,
    uint32_t current, uint32_t reference, uint8_t profile,
    bool skip_history_scan);
bool gomore_primitives_sliding_window_mean(
    const float *input, size_t rows, size_t columns,
    size_t window, size_t stride, size_t padding,
    float *output, size_t output_capacity, size_t *written);
int32_t gomore_primitives_profile_state_apply(
    uint8_t *state, size_t state_length,
    int32_t profile, int32_t selector, uint8_t requested);
bool gomore_primitives_sorted_percentile(
    float *values, size_t count, uint32_t percentile,
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare, float *result);
uint32_t gomore_primitives_sps_select_available(
    float reference, float gpd, float accelerometer,
    uint8_t accelerometer_auxiliary,
    gomore_primitives_sps_selection_log_fn log_values,
    gomore_primitives_sps_selection *output);
bool gomore_primitives_statistics_accumulate(
    gomore_primitives_statistics_accumulator *accumulator,
    uint32_t span, bool upper_flag, bool lower_flag,
    float signed_value, bool quality_flag4, bool quality_flag6,
    float mean_value);
bool gomore_primitives_interval_descriptor_merge(
    gomore_primitives_interval_descriptor *output,
    uint32_t initial_start, bool bypass_merge,
    const gomore_primitives_interval_descriptor *previous,
    const gomore_primitives_interval_descriptor *addition,
    uint8_t profile);
bool gomore_primitives_step_accumulate(
    gomore_primitives_step_accumulator *state,
    uint32_t scale, uint8_t value, float *completed);
bool gomore_primitives_packed_timeline_extract(
    uint8_t *packed, size_t packed_length,
    uint32_t begin, uint32_t end, uint32_t cleanup_end,
    uint32_t alternate_cleanup_begin, uint32_t alternate_cleanup_end,
    uint8_t *output, size_t output_capacity, size_t *written);
bool gomore_primitives_sleep_interval_build(
    gomore_primitives_sleep_interval_result *output,
    const float history[15], bool high_threshold,
    uint32_t clamp_end, uint32_t clamp_start,
    int32_t mode, uint32_t metadata, int16_t timezone_minutes,
    int32_t shift_minutes, uint8_t auxiliary,
    const gomore_primitives_sleep_interval_source *source,
    const gomore_primitives_sleep_interval_policy *policy);
bool gomore_primitives_sleep_interval_refine(
    gomore_primitives_sleep_interval_result *output,
    const gomore_primitives_sleep_interval_result *previous,
    const gomore_primitives_sleep_interval_result *current,
    int32_t average_count, int32_t average_sum,
    int16_t gap_limit_minutes);
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
    int16_t gap_limit_minutes);
bool gomore_primitives_sleep_interval_select(
    gomore_primitives_sleep_interval_result *output,
    const gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes);
uint32_t gomore_primitives_sleep_interval_run(
    gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes, int32_t mode,
    const uint8_t *policy_source, size_t policy_source_length,
    gomore_primitives_sleep_interval_result *output);
bool gomore_primitives_sleep_interval_update(
    gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes, int32_t mode,
    const uint8_t *policy_source, size_t policy_source_length,
    uint8_t *pending,
    uint8_t *output_record, size_t output_record_length,
    uint8_t profile_state,
    void *packed_state, size_t packed_state_length,
    uint8_t *propagated_value);
int32_t gomore_primitives_sleep_interval_dispatch(
    const gomore_primitives_sleep_interval_context *context,
    uint32_t current, int16_t timezone_minutes,
    uint32_t output_binding, uint8_t *output_record,
    size_t output_record_length,
    uintptr_t first, uintptr_t second, uintptr_t fourth, uintptr_t fifth,
    gomore_primitives_stage_consumer_fn consumer);
uint8_t gomore_primitives_count_hysteresis_crossings(
    const uint16_t *values, size_t count);
int32_t gomore_primitives_nullable_compare_n(const uint8_t *left,
                                             const uint8_t *right,
                                             size_t count);
bool gomore_primitives_recent_interval_predicate(const void *record,
                                                 size_t length,
                                                 uint32_t now);
int32_t gomore_primitives_record_quality_classify(const void *record,
                                                  size_t length);

/* Explicit-provider and fully recovered 26...70-byte closure. */
int32_t gomore_primitives_seeded_random_offset(
    uint32_t seed, uint32_t *stored_seed,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value);
void *gomore_primitives_allocate_mode2_state(
    uintptr_t binding, gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize);
void *gomore_primitives_allocate_mode1_state(
    uintptr_t binding, gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize);
void *gomore_primitives_allocate_mode0_state_remap(
    uintptr_t binding,
    const uint32_t *descriptor_table, size_t descriptor_bytes,
    uint32_t descriptor_table_binding,
    gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize);
int32_t gomore_primitives_decimal_parse(const uint8_t *text);
uint32_t gomore_primitives_tensor_call_optional_finish(
    const uint32_t descriptor[3], uintptr_t first, uintptr_t second,
    bool finish, gomore_primitives_tensor_call_fn call,
    gomore_primitives_tensor_finish_fn finish_call);
int32_t gomore_primitives_all_class_0x20(const uint8_t *bytes,
                                        size_t count,
                                        const uint8_t classes[256]);
bool gomore_primitives_filter_state_initialize(
    void *record, size_t length, gomore_primitives_filter_init_fn initialize);
bool gomore_primitives_quality_samples_copy(
    void *record, size_t length,
    const gomore_primitives_quality_sample samples[3]);
bool gomore_primitives_dual_stage(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *output, size_t output_length,
    gomore_primitives_dual_stage_fn first_stage,
    gomore_primitives_dual_stage_fn second_stage);
bool gomore_primitives_composite_record_initialize(
    void *record, size_t length,
    gomore_primitives_record_init_fn tail_initialize);
bool gomore_primitives_quality_code(const void *record, size_t length,
                                    uint8_t *code);
float gomore_primitives_i16_standard_deviation(
    const int16_t *values, size_t count, int32_t center,
    gomore_primitives_float_unary_fn square_root);
/* 0x4834A: append one four-channel locomotion summary into 8-slot histories. */
bool gomore_primitives_locomotion_summary_update(
    gomore_primitives_locomotion_summary_state *state,
    const int16_t *const channels[4], size_t sample_count,
    gomore_primitives_float_unary_fn square_root);
/* 0x5ED14: advance and classify the 25-sample locomotion window. */
int32_t gomore_primitives_locomotion_window_preprocess(
    void *state, size_t state_length, uint32_t elapsed_windows,
    const float *const axes[3], bool input_unavailable,
    void *output, size_t output_length,
    gomore_primitives_float_unary_fn square_root,
    gomore_primitives_locomotion_classify_fn classify);
float gomore_primitives_energy_core(const void *state, size_t length,
                                    float primary, float secondary);
float gomore_primitives_energy_scaled(const void *state, size_t length,
                                      float primary, float scale_input);
float gomore_primitives_daily_resting_kcal(const void *profile,
                                           size_t profile_length);
float gomore_primitives_substrate_fat_fraction(
    float value, float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential);
bool gomore_primitives_energy_zone_thresholds(
    float feature, float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential, float thresholds[7]);
bool gomore_primitives_energy_zone_accumulate(
    void *state, size_t state_length, int32_t elapsed_seconds,
    float increment, float metric, float upper_reference,
    float lower_reference, float feature,
    gomore_primitives_float_unary_fn exponential, float totals[5]);
bool gomore_primitives_energy_projection(
    const void *state, size_t state_length, float first, float second,
    float output[4]);
float gomore_primitives_energy_nonlinear_scale(
    float primary, float scale_input);
bool gomore_primitives_energy_mode_rate(
    void *state, size_t state_length,
    const void *profile, size_t profile_length,
    float input, float *output);
bool gomore_primitives_energy_interpolate_pair(
    bool alternate_mode, float primary, float secondary, float tertiary,
    gomore_primitives_float_unary_fn exponential,
    float output[2]);
bool gomore_primitives_energy_estimator_family_a(
    void *state, size_t state_length,
    const void *projection_state, size_t projection_state_length,
    float primary, float value, float upper_reference,
    float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    float output[4]);
bool gomore_primitives_energy_estimator_family_b(
    const void *projection_state, size_t projection_state_length,
    float primary, float value, float upper_reference,
    float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn logarithm,
    float output[4]);
bool gomore_primitives_energy_table_estimator(
    const void *state, size_t state_length,
    const void *projection_state, size_t projection_state_length,
    const gomore_primitives_energy_table_configuration *configuration,
    float primary, float value, float upper_reference,
    float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    float output[4]);
bool gomore_primitives_energy_dispatch(
    void *state, size_t state_length,
    const void *projection_state, size_t projection_state_length,
    const float settings[2], float value,
    float upper_reference, float lower_reference,
    gomore_primitives_float_unary_fn exponential,
    gomore_primitives_float_unary_fn float_logarithm,
    gomore_primitives_double_unary_fn double_logarithm,
    const gomore_primitives_energy_table_configuration *table_configuration,
    float output[4]);
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
    gomore_primitives_energy_update_output *output);
bool gomore_primitives_activity_accumulate(
    gomore_primitives_activity_accumulator_state *state,
    uint32_t unix_seconds, int16_t timezone_minutes,
    float step_increment,
    const gomore_primitives_energy_update_output *energy,
    float selected_speed,
    gomore_primitives_activity_accumulator_output *output);
int32_t gomore_primitives_profile_convert(
    const gomore_primitives_profile_input *input,
    float persistent_cache[2],
    gomore_primitives_profile_output *output);
bool gomore_primitives_sleep_interval_statistics(
    const uint8_t *stages, size_t stage_bytes,
    uint32_t start_timestamp, uint32_t end_timestamp,
    bool packed, float output[7]);
bool gomore_primitives_sleep_stage_statistics(
    const uint8_t *stages, size_t stage_bytes,
    uint32_t start_timestamp, uint32_t end_timestamp,
    bool packed, float output[12]);
bool gomore_primitives_sleep_score(
    const gomore_primitives_sleep_statistics *statistics,
    gomore_primitives_double_unary_fn hyperbolic_tangent,
    gomore_primitives_float_binary_fn power,
    float *score);
/* 0x647C4: collect extrema at two moving-average state transitions. */
bool gomore_primitives_moving_average_extrema_indices(
    const float *values, size_t count,
    uint32_t long_window, uint32_t short_window,
    uint8_t *maxima, size_t maxima_capacity, size_t *maxima_count,
    uint8_t *minima, size_t minima_capacity, size_t *minima_count);
/* 0x69644: validate an interval and build its typed final sleep report. */
bool gomore_primitives_final_sleep_build(
    uint8_t *packed_timeline, size_t packed_timeline_length,
    uint32_t now, const uint8_t configuration[11],
    const gomore_primitives_sleep_interval_result *interval,
    gomore_primitives_sleep_stage_refine_fn refine,
    gomore_primitives_double_unary_fn hyperbolic_tangent,
    gomore_primitives_float_binary_fn power,
    gomore_primitives_final_sleep_build_output *output,
    int32_t *status);
bool gomore_primitives_sleep_peak_rate_interpolate(
    const int16_t *peaks, size_t peak_count,
    int32_t scale, int32_t output_start,
    float *output, size_t output_count);
bool gomore_primitives_sleep_peak_window_update(
    int16_t *peaks, size_t peak_capacity, size_t peak_count,
    uint8_t mode, uint16_t *update_counter,
    float *window, size_t window_count);
bool gomore_primitives_sleep_peak_tail_rebase(
    int16_t *peaks, size_t peak_capacity, size_t *peak_count);
bool gomore_primitives_sleep_valley_candidates(
    const float *values, size_t value_count,
    uint8_t candidates[12], size_t *candidate_count);
float gomore_primitives_sleep_quantized_magnitude10(
    const float values[10], gomore_primitives_float_unary_fn floor_value);
bool gomore_primitives_range_center_span(
    const float *values, size_t count, uint8_t mode,
    float *center, float *span);
float gomore_primitives_linear_model3_evaluate(
    const float values[3], const gomore_primitives_linear_model3 *model);
bool gomore_primitives_sleep_repair_deep_awake_transition(
    uint8_t *stages, size_t count);
/* 0x81040: apply the complete bounded sleep-stage postprocessor profile. */
bool gomore_primitives_sleep_stage_refine(
    const uint8_t configuration[11], int8_t *stages,
    size_t stage_capacity, size_t *stage_count,
    uint32_t duration_seconds);
bool gomore_primitives_sleep_optical_history_advance(
    gomore_primitives_sleep_optical_history *state,
    uint32_t elapsed_blocks,
    gomore_primitives_filter_init_fn initialize);
bool gomore_primitives_sleep_optical_peak_update(
    gomore_primitives_sleep_optical_history *state,
    uint32_t elapsed_blocks,
    const gomore_primitives_sleep_optical_input *input,
    uint8_t record[17],
    gomore_primitives_filter_init_fn initialize,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter);
bool gomore_primitives_state_word_24(const void *state, size_t length,
                                     uint32_t *value);
bool gomore_primitives_split_signed_root(
    float value, float output[2],
    gomore_primitives_float_binary_fn power);
float gomore_primitives_clamped_rational(float value, float state);
bool gomore_primitives_table_record11(const uint8_t *table,
                                      size_t table_length, int32_t index,
                                      uint8_t output[11]);
int32_t gomore_primitives_status_or_random(
    uint8_t *state, size_t state_length,
    const void *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value);
int32_t gomore_primitives_validate_identifier_status(
    const uint8_t *identifier, const uint8_t classes[256],
    uint8_t *state, size_t state_length,
    uint8_t *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value);

/* Initializer-chain, resample, compaction, and predicate closure. */
bool gomore_primitives_mode_state_configure(
    void *record, size_t length, uint32_t mode, uint32_t count,
    const float parameters[2],
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2);
/* 0x717AC: bounded order-one-through-four low/high-pass IIR designer. */
bool gomore_primitives_iir_low_high_coefficients(
    gomore_primitives_iir_coefficients *record,
    uint32_t mode, uint32_t order, float normalized_cutoff,
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_binary_fn power);
/* 0x711B4: bounded one/two-pole-pair band-pass IIR designer. */
bool gomore_primitives_iir_bandpass_coefficients(
    gomore_primitives_iir_coefficients *record,
    uint32_t order, const float normalized_cutoffs[2],
    gomore_primitives_float_unary_fn cosine,
    gomore_primitives_float_unary_fn sine,
    gomore_primitives_float_unary_fn tangent);
bool gomore_primitives_large_filter_state_initialize(
    void *record, size_t length,
    gomore_primitives_mode2_init_fn initialize_mode2);
bool gomore_primitives_engine_state_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_large_init_fn initialize);
void gomore_primitives_linear_resample(
    const float *source, int32_t input_count, int32_t output_count,
    int32_t source_total, float *destination);
int32_t gomore_primitives_resample25_and_filter(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter);
void gomore_primitives_resample25_and_filter_tail(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter);
bool gomore_primitives_prepare_filter_input(
    void *filter_state, size_t filter_length,
    const float *source, bool clear_only, int32_t source_total,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter);
bool gomore_primitives_commit_valid_time_record(
    void *context, size_t context_length,
    void *destination, size_t destination_length,
    const void *record, size_t record_length);
bool gomore_primitives_signed_power_third(
    float values[2], gomore_primitives_float_binary_fn power);
bool gomore_primitives_trim_below_reference_tail(
    const uint8_t *reference, size_t reference_count,
    uint8_t *values, size_t capacity, size_t *value_count);
bool gomore_primitives_selector_transition(const void *record,
                                           size_t length,
                                           int8_t *selector);
bool gomore_primitives_fill_packed_time_gap(void *record, size_t length,
                                            uint32_t now);
float gomore_primitives_centered_ratio(int32_t first, int32_t middle,
                                      int32_t last);

/* Direct-filter, compact encoding, and arithmetic-state closure. */
bool gomore_primitives_iir_filter_apply(void *state, size_t state_length,
                                       float *values, size_t count);
int32_t gomore_primitives_integer_iir4_update(
    int32_t input, int32_t input_history[4],
    int32_t output_history[4], int32_t profile);
int32_t gomore_primitives_thresholded_mean5(
    float threshold, const float values[5], const float comparisons[5],
    float *mean);
float gomore_primitives_magnitude_score10(float threshold,
                                         const float values[10]);
int32_t gomore_primitives_circular_count_predicate(
    const int16_t *values, size_t count, int32_t cursor,
    int32_t lookback, int32_t lower, int32_t upper,
    uint8_t comparison, int32_t required);
bool gomore_primitives_run_length_encode_2bit(
    const int8_t *values, size_t count,
    uint8_t *output, size_t capacity, size_t *written);
/* 0x8FA3C: serialize the final public sleep header and compact stages. */
bool gomore_primitives_final_sleep_record_serialize(
    const gomore_primitives_final_sleep_record *record,
    uint8_t *output, size_t capacity, size_t *written);
/* 0x6C294: dispatch active output slots and sleep lifecycle transitions. */
bool gomore_primitives_output_lifecycle_dispatch(
    void *context, gomore_primitives_output_lifecycle_state *state,
    const gomore_primitives_output_lifecycle_providers *providers);
/* 0x49410: reconcile one of seven authorization slots and shared streams. */
bool gomore_primitives_authorization_dispatch(
    gomore_primitives_authorization_state *state,
    uint32_t slot, bool enable,
    const gomore_primitives_authorization_providers *providers);
bool gomore_primitives_propagate_packed_status(
    void *state, size_t length, uint8_t *value);
bool gomore_primitives_filter_bank_initialize(
    void *record, size_t length,
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2);
bool gomore_primitives_target_runs(
    int8_t target, const int8_t *values, size_t count,
    uint16_t (*runs)[2], size_t run_capacity,
    size_t *run_count, size_t *match_count);
/* 0x64CC8: correct a signed target-stage proportion through bounded runs. */
bool gomore_primitives_sleep_stage_proportion_adjust(
    int8_t *values, size_t count, int8_t target,
    int32_t adjustment, int32_t *remaining_adjustment);
bool gomore_primitives_smooth_target_run_edges(
    int8_t target, int8_t *values, size_t count,
    bool alternate_policy);
bool gomore_primitives_shift_marked_history(uint8_t *values,
                                            size_t capacity,
                                            size_t *count,
                                            size_t shift);

/* Adapter, validation, exponential, and state-dispatch closure. */
bool gomore_primitives_register_mode_topics(
    uintptr_t context, uintptr_t mode4_handler, uintptr_t mode3_handler,
    gomore_primitives_topic_register_fn register_topic);
float gomore_primitives_exponential_affine(
    float value, float scale, float center, float offset,
    gomore_primitives_float_unary_fn exponential);
int32_t gomore_primitives_seed_and_test_text_class(
    const uint8_t *text, size_t text_length,
    const uint8_t classes[256],
    const void *source_record, size_t source_length,
    void *destination_record, size_t destination_length,
    gomore_primitives_seed_fn seed);
int32_t gomore_primitives_validate_record_bytes(
    const uint8_t *candidate, size_t candidate_length,
    const void *source_record, size_t source_length,
    void *destination_record, size_t destination_length);
int32_t gomore_primitives_validate_su_signature(
    const uint8_t *candidate, size_t candidate_length,
    void *destination_record, size_t destination_length);
bool gomore_primitives_sps_engine_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_void_context_fn finish_initialize);
int32_t gomore_primitives_state_mode_dispatch(
    void *state, size_t state_length, int32_t mode, uint8_t value,
    gomore_primitives_state_byte_fn mode0,
    gomore_primitives_state_byte_fn mode1,
    gomore_primitives_state_call_fn mode2,
    gomore_primitives_state_call_fn mode3);
bool gomore_primitives_commit_valid_time_record_adapter(
    void *engine, size_t engine_length,
    void *destination, size_t destination_length,
    const void *record, size_t record_length);
float gomore_primitives_one_minus(float value);
float gomore_primitives_logistic(
    float value, gomore_primitives_float_unary_fn exponential);
float gomore_primitives_scaled_product(float first, float second);
int32_t gomore_primitives_linear_sign_classify(
    float first, float second, float third, int32_t integer,
    const float coefficients[4], float bias);
int32_t gomore_primitives_validate_key_and_update_status(
    const uint8_t *candidate, size_t candidate_length,
    const void *configuration, size_t configuration_length,
    void *state, size_t state_length,
    void *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value);
int32_t gomore_primitives_decimal_config_update(
    const uint8_t *text,
    const void *configuration, size_t configuration_length,
    void *state, size_t state_length,
    void *status_record, size_t status_length,
    bool validation_enabled,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value);
int32_t gomore_primitives_runtime_version_validate(
    uint32_t value, bool allow_missing_runtime, bool validation_enabled,
    uint32_t configured_limit, bool runtime_present,
    int16_t configured_version, int16_t runtime_version);
bool gomore_primitives_dominant_sorted_i32(
    int32_t *values, size_t count,
    int32_t *dominant_value, size_t *dominant_count);
int32_t gomore_primitives_circular_signal_predicate(
    const int16_t *primary, const int16_t *first,
    const int16_t *second, const int16_t *third,
    size_t count, int32_t cursor, size_t lookback);
float gomore_primitives_average_sign_crossing_spacing(
    const float *values, size_t count);
float gomore_primitives_round_decimal_places(
    float value, float places,
    gomore_primitives_float_binary_fn power);
bool gomore_primitives_time_engine_initialize(
    void *state, size_t state_length,
    uint8_t *configuration, size_t configuration_length,
    uint32_t configuration_binding);
bool gomore_primitives_interval_nonzero_argmax(
    const float *values, size_t value_count,
    const uint8_t *boundaries, size_t boundary_count,
    uint8_t *output, size_t output_capacity, size_t *output_count);
int32_t gomore_primitives_sequence_replay(
    void *state, size_t state_length,
    void *record, size_t record_length,
    gomore_primitives_record_step_fn process_record);

/* Second reduction tier: 16 complete 32...63-byte functions. */
bool gomore_primitives_state_window_predicate(bool requested_active,
                                              uint32_t now,
                                              uint32_t last_transition,
                                              bool flag_a8,
                                              bool flag_a9);
bool gomore_primitives_key_or_cached_copy(
    uint8_t *destination, size_t capacity,
    bool cache_valid, const uint8_t *cache, size_t cache_length,
    uint32_t device_id_0, uint32_t device_id_1, uint32_t address_word,
    size_t *written);
void gomore_primitives_slot_state_transition(uint8_t *state,
                                             uint8_t requested,
                                             bool guarded_mode);
int32_t gomore_primitives_copy_key_blob(
    uint8_t *destination, size_t capacity,
    bool cache_valid, const uint8_t *cache,
    gomore_primitives_blob_loader_fn loader, void *loader_context);
int32_t gomore_primitives_stage_32_and_consume(
    uintptr_t first, uintptr_t second, const uint8_t *source,
    size_t source_length, uintptr_t fourth, uintptr_t fifth,
    gomore_primitives_stage_consumer_fn consumer);
float gomore_primitives_mean(const float *values, size_t count);
int32_t gomore_primitives_argmax_from_zero(const float *values, size_t count);
bool gomore_primitives_reset_provider_state(
    uint8_t *state, size_t length, bool active,
    gomore_primitives_mode_fn set_mode,
    gomore_primitives_void_context_fn release,
    void *release_context, gomore_primitives_init_fn initialize);
bool gomore_primitives_sample_plausible(const uint8_t sample[4]);
uint32_t gomore_primitives_health_sample_features(
    const uint8_t record[12], float output[7]);
bool gomore_primitives_scaled_sample_publish(
    gomore_primitives_scaled_sample_state *state,
    bool publish_enabled, gomore_primitives_event_publish_fn publish);
bool gomore_primitives_temperature_measurement_begin(
    gomore_primitives_scaled_sample_state *state);
gomore_primitives_temperature_measurement_result
gomore_primitives_temperature_measurement_step(
    gomore_primitives_scaled_sample_state *state, uint16_t sample);
uint16_t gomore_primitives_stable_trimmed_median(
    const uint16_t *values, size_t count, uint16_t *unscaled);
bool gomore_primitives_stamp_time_record(
    uint8_t *record, size_t length,
    gomore_primitives_time_fn time_provider,
    gomore_primitives_offset_fn offset_provider,
    gomore_primitives_sync_state_fn sync_provider,
    void *provider_context);
uint32_t gomore_primitives_clamp_hysteresis(uint32_t value,
                                            uint32_t baseline);
uint32_t gomore_primitives_parameter_commit(
    uint8_t *state, size_t length, uint32_t value,
    gomore_primitives_parameter_validate_fn validate,
    void *validate_context);
bool gomore_primitives_records_any_bit2(const uint8_t *records,
                                        size_t record_bytes);
bool gomore_primitives_records_any_bit4(const uint8_t *records,
                                        size_t record_bytes);
bool gomore_primitives_records_any_bit3(const uint8_t *records,
                                        size_t record_bytes);
bool gomore_primitives_records_any_bit1(const uint8_t *records,
                                        size_t record_bytes);

/* Selected fully recovered utilities from the 64...127-byte tier. */
int32_t gomore_primitives_quantized_argmin(const float *values,
                                           uint32_t begin,
                                           uint32_t end_exclusive);
uint32_t gomore_primitives_max_difference_index(const float *values,
                                                uint32_t begin,
                                                uint32_t end_exclusive);
bool gomore_primitives_median(float *values, size_t count,
                              gomore_primitives_qsort_fn qsort_provider,
                              gomore_primitives_compare_fn compare,
                              float *result);
bool gomore_primitives_standard_deviation(
    const float *values, size_t count,
    gomore_primitives_float_binary_fn pow_provider,
    gomore_primitives_float_unary_fn sqrt_provider,
    float *result);
bool gomore_primitives_logistic_score(
    float scale, float bias, float feature, float coefficient,
    gomore_primitives_float_unary_fn exp_provider, float *result);
bool gomore_primitives_modulo5_record(uint8_t *record, size_t length,
                                      uint8_t secondary,
                                      uint8_t primary);
bool gomore_primitives_compact_25_windows(uint8_t *records,
                                         size_t record_capacity,
                                         uint8_t *record_count,
                                         uint32_t current_window);
bool gomore_primitives_decimated_ring_write(float value, uint8_t ring[90],
                                            uint32_t begin_tick,
                                            uint32_t end_tick);
int32_t gomore_primitives_csv4_prefix_compare(
    const uint8_t *pattern, size_t pattern_length,
    const uint8_t *candidate, size_t candidate_length);
bool gomore_primitives_sleep_engine_open(
    void *state, size_t state_length,
    gomore_primitives_tensor_construct_binding_fn construct_tensor);
bool gomore_primitives_shift_negated_filter_history(
    void *state, size_t state_length,
    const float input[25], bool zero_fill,
    gomore_primitives_filter_apply_fn apply_filter);
bool gomore_primitives_log_u32(
    const gomore_primitives_log_config *configuration,
    uint32_t level, uint32_t category,
    const char *format, uint32_t value);
bool gomore_primitives_accelerometer_resample25(
    void *filter_states, size_t filter_state_length,
    const float *const sources[3], size_t source_count,
    int32_t sample_count,
    float *const destinations[3], size_t destination_count,
    uint8_t *failed, uint32_t *status,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger);
bool gomore_primitives_ppg_resample25(
    void *filter_states, size_t filter_state_length,
    const float *const *sources, size_t source_count,
    int32_t channel_count, int32_t sample_count,
    float output[25], uint8_t *failed, uint32_t *status,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger);

#endif
