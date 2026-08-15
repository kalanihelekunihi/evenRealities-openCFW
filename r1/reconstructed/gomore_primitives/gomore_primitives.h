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
typedef void (*gomore_primitives_stage_consumer_fn)(
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
typedef int32_t (*gomore_primitives_state_byte_fn)(void *state,
                                                   uint8_t value);
typedef int32_t (*gomore_primitives_state_call_fn)(void *state);
typedef int32_t (*gomore_primitives_record_step_fn)(void *state,
                                                    void *record);
typedef uint32_t (*gomore_primitives_tensor_construct_binding_fn)(
    void *pool, size_t pool_length, uint32_t rank,
    const uint16_t *dimensions, size_t dimension_count);
typedef uint32_t (*gomore_primitives_format_u32_fn)(
    char *destination, size_t capacity, const char *format, uint32_t value);
typedef void (*gomore_primitives_log_emit_fn)(const char *format,
                                              const char *message);

typedef struct {
    bool enabled;
    uint16_t category_mask;
    uint32_t level_mask;
    gomore_primitives_format_u32_fn format_u32;
    gomore_primitives_log_emit_fn emit;
} gomore_primitives_log_config;

typedef struct {
    float value;
    int32_t metadata;
} gomore_primitives_quality_sample;

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
int32_t gomore_primitives_filtered_u8_mean(const uint8_t *values,
                                          size_t count, int32_t center,
                                          int32_t tolerance);
bool gomore_primitives_complex_multiply(const float left[2],
                                        const float right[2],
                                        float output[2]);
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
float gomore_primitives_energy_core(const void *state, size_t length,
                                    float primary, float secondary);
float gomore_primitives_energy_scaled(const void *state, size_t length,
                                      float primary, float scale_input);
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

/* Initializer-chain, resample, compaction, and predicate closure. */
bool gomore_primitives_mode_state_configure(
    void *record, size_t length, uint32_t mode, uint32_t count,
    const float parameters[2],
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2);
bool gomore_primitives_large_filter_state_initialize(
    void *record, size_t length,
    gomore_primitives_mode2_init_fn initialize_mode2);
bool gomore_primitives_engine_state_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_large_init_fn initialize);
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
float gomore_primitives_thresholded_mean5(float threshold,
                                          const float values[5],
                                          const float comparisons[5]);
float gomore_primitives_magnitude_score10(float threshold,
                                         const float values[10]);
int32_t gomore_primitives_circular_count_predicate(
    const int16_t *values, size_t count, int32_t cursor,
    int32_t lookback, int32_t lower, int32_t upper,
    uint8_t comparison, int32_t required);
bool gomore_primitives_run_length_encode_2bit(
    const int8_t *values, size_t count,
    uint8_t *output, size_t capacity, size_t *written);
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
bool gomore_primitives_stage_32_and_consume(
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

#endif
