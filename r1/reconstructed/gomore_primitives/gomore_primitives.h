#ifndef OPENR1_RECONSTRUCTED_GOMORE_PRIMITIVES_H
#define OPENR1_RECONSTRUCTED_GOMORE_PRIMITIVES_H

/*
 * Owner-authorized clean-room reconstruction of 19 small GoMore-candidate
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

#endif
