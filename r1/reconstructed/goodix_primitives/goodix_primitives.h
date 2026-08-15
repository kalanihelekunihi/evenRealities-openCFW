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

typedef void (*goodix_primitives_state_handler_fn)(void *record);
typedef int32_t (*goodix_primitives_device_initialize_fn)(uint16_t device_id);
typedef void (*goodix_primitives_hook_fn)(void);
typedef void *(*goodix_primitives_allocate_fn)(void *context, size_t bytes);
typedef void (*goodix_primitives_release_fn)(void *context, void *allocation);
typedef float (*goodix_primitives_float_unary_fn)(float value);
typedef int32_t (*goodix_primitives_i32_unary_fn)(int32_t value);
typedef uint16_t (*goodix_primitives_u32_to_u16_fn)(uint32_t value);
typedef int32_t (*goodix_primitives_status_fn)(void);

typedef struct {
    float *values;
    uint32_t count;
    uint32_t capacity;
} goodix_primitives_float_buffer;

typedef struct {
    uint32_t element_bytes;
    uint32_t batches;
    uint32_t rows;
    uint32_t columns;
    void *data;
} goodix_primitives_tensor_descriptor;

typedef struct {
    void *data;
    uint16_t count;
    uint16_t capacity;
} goodix_primitives_buffer_descriptor;

typedef struct {
    uint32_t field_00;
    uint32_t field_04;
    uint32_t *primary;
    uint32_t *secondary;
    uint32_t count;
    uint32_t field_14;
} goodix_primitives_dual_buffer_descriptor;

typedef struct {
    float *values;
    uint32_t count;
    uint32_t capacity;
    uint32_t limit;
} goodix_primitives_float_storage;

typedef struct {
    uint8_t count;
    void *records;
    uint32_t metadata;
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
bool goodix_primitives_word_window_push(goodix_primitives_word_window *window,
                                        uint32_t value);
bool goodix_primitives_logistic_score(float value, float threshold,
                                      float lower_scale, float upper_scale,
                                      goodix_primitives_float_unary_fn exp_provider,
                                      float *result);

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
int8_t goodix_primitives_centered_i8(int32_t value);
float goodix_primitives_float_sum(const float *values, size_t count);
bool goodix_primitives_decrement_counter(int32_t *counter);
void *goodix_primitives_tensor_descriptor_initialize(
    goodix_primitives_tensor_descriptor *descriptor, uint32_t batches,
    uint32_t rows, uint32_t columns, uint32_t element_bytes, void *data);
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
bool goodix_primitives_update_transition(uint8_t *record, size_t length,
                                         uint8_t state,
                                         uint8_t source_flag);
bool goodix_primitives_sort_floats(float *values, size_t count);
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
    uint32_t metadata, goodix_primitives_allocate_fn allocate,
    void *allocate_context);
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
