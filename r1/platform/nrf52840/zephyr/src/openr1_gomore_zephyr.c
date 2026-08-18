#include "openr1_gomore_zephyr.h"

#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#include <zephyr/kernel.h>

#include "gomore_primitives/gomore_primitives.h"
#include "model_data/r1_model_data.h"
#include "openr1/r1_crc.h"
#include "openr1/r1_storage.h"
#include "openr1_clock_zephyr.h"
#include "openr1_databases_zephyr.h"
#include "openr1_sensor_stream_zephyr.h"
#include "openr1_storage_zephyr.h"

#define OPENR1_GOMORE_ENGINE_BYTES 0x39E0u
#define OPENR1_GOMORE_PREVIOUS_BYTES 0x2E0u
#define OPENR1_GOMORE_RETRY_MILLISECONDS 5000u
#define OPENR1_GOMORE_PKEY_OFFSET 0xA000u
#define OPENR1_GOMORE_PKEY_HEADER_BYTES 72u
#define OPENR1_GOMORE_SLEEP_MODE_TABLE_ADDRESS UINT32_C(0x000B1BDE)
#define OPENR1_GOMORE_SLEEP_MODE_TABLE_BYTES 77u
#define OPENR1_GOMORE_SLEEP_BELOW_DESCRIPTOR_ADDRESS UINT32_C(0x000B1C4C)
#define OPENR1_GOMORE_SLEEP_UPPER_DESCRIPTOR_ADDRESS UINT32_C(0x000B2048)
#define OPENR1_GOMORE_SLEEP_DESCRIPTOR_BYTES 20u

typedef struct {
    uint8_t *engine;
    uint8_t *previous;
    uint8_t time_configuration[10];
    r1_user_profile profile;
    bool profile_defaulted;
    bool profile_recorded;
    bool callback_failed;
    bool previous_available;
    bool previous_restored;
    uint32_t previous_writes;
    uint32_t previous_write_failures;
    uint32_t retry_at_uptime;
    int32_t status;
    gomore_primitives_output_orchestrator_providers output_providers;
    float activity_differences[249];
    gomore_primitives_optical_period_workspace optical_period_workspace;
    gomore_primitives_sleep_stage_classifier_model sleep_models[2];
    gomore_primitives_sleep_stage_classifier_context sleep_classifier;
    gomore_primitives_sensor_update_state sensor_update;
    float raw_optical_output[25];
    float accelerometer_outputs[3][25];
    uint8_t output_snapshot[GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_DESTINATION_BYTES];
    uint8_t *result_pointer;
    uint8_t sleep_result_status;
    uint8_t consecutive_update_failures;
    bool force_fresh_previous;
    bool reinitialize_requested;
    uint32_t updates;
    uint32_t update_failures;
    uint32_t activity_publication_failures;
    uint32_t sleep_publications;
    uint32_t sleep_publication_failures;
    uint32_t authorization_failures;
    uint32_t reinitializations;
    uint32_t reinitialization_failures;
} openr1_gomore_zephyr_state;

static openr1_gomore_zephyr_state gomore_state;

static void gomore_filter_initialize(
    void *record, uint32_t rows, uint32_t columns,
    const float parameters[2]);
static void gomore_large_filter_initialize(
    void *record, uint32_t count, const float parameters[2]);

static bool gomore_store_read(
    void *context, uint32_t offset, uint8_t *destination, size_t length) {
    return r1_flash_read((const r1_flash *)context, offset,
                         destination, length) == R1_OK;
}

static bool gomore_store_write(
    void *context, uint32_t offset, const uint8_t *source, size_t length) {
    return r1_flash_program((const r1_flash *)context, offset,
                            source, length) == R1_OK;
}

static bool gomore_store_erase(
    void *context, uint32_t offset, size_t length) {
    return r1_flash_erase((const r1_flash *)context, offset, length) == R1_OK;
}

static void gomore_store_u32(uint8_t destination[4], uint32_t value) {
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
    destination[2] = (uint8_t)(value >> 16u);
    destination[3] = (uint8_t)(value >> 24u);
}

static bool gomore_pkey_store_bind(gomore_primitives_pkey_store *store) {
    r1_flash *const flash = openr1_storage_zephyr_flash();
    if (store == NULL || flash == NULL || flash->size <
            OPENR1_GOMORE_PKEY_OFFSET +
            GOMORE_PRIMITIVES_PKEY_PARTITION_BYTES) {
        return false;
    }
    *store = (gomore_primitives_pkey_store){
        .initialized = true,
        .partition_offset = OPENR1_GOMORE_PKEY_OFFSET,
        .flash_context = flash,
        .read = gomore_store_read,
        .write = gomore_store_write,
        .erase = gomore_store_erase,
        .initialize = NULL,
    };
    return true;
}

static bool gomore_previous_state_prepare(uint8_t previous[0x2E0u]) {
    gomore_primitives_pkey_store store;
    if (!gomore_pkey_store_bind(&store)) {
        return false;
    }
    r1_flash *const flash = store.flash_context;
    uint8_t key[64] = {0};
    gomore_primitives_previous_state_result restore = {0};
    if (gomore_primitives_previous_state_restore(
            &store, key, previous, OPENR1_GOMORE_PREVIOUS_BYTES,
            &restore)) {
        gomore_state.previous_available = true;
        gomore_state.previous_restored = restore.found;
        return true;
    }
    if (restore.status == GOMORE_PRIMITIVES_PREVIOUS_STATE_NOT_FOUND) {
        gomore_state.previous_available = true;
        return true;
    }
    if (restore.status != GOMORE_PRIMITIVES_PREVIOUS_STATE_PKEY_INVALID) {
        return false;
    }

    uint8_t header[OPENR1_GOMORE_PKEY_HEADER_BYTES];
    if (!gomore_store_read(flash, OPENR1_GOMORE_PKEY_OFFSET,
                           header, sizeof(header))) {
        return false;
    }
    for (size_t index = 0u; index < sizeof(header); ++index) {
        if (header[index] != UINT8_MAX) {
            return false;
        }
    }

    /* A fresh openR1 installation has no retail authorization credential.
     * This explicit all-zero record is only the recovered pKey-page layout
     * anchor needed by the previous-state slots; engine authorization does
     * not read or depend on it. */
    memset(header, 0, sizeof(header));
    gomore_store_u32(&header[0], 64u);
    gomore_store_u32(&header[4],
        r1_crc32_castagnoli(&header[8], 64u));
    if (!gomore_store_write(flash, OPENR1_GOMORE_PKEY_OFFSET,
                            header, sizeof(header))) {
        return false;
    }
    gomore_state.previous_available = true;
    return true;
}

static void gomore_previous_state_persist(void) {
    if (!gomore_state.previous_available || gomore_state.previous == NULL ||
            gomore_state.status != 0) {
        return;
    }
    gomore_primitives_pkey_store store;
    if (!gomore_pkey_store_bind(&store)) {
        ++gomore_state.previous_write_failures;
        return;
    }
    uint8_t scratch[OPENR1_GOMORE_PKEY_HEADER_BYTES];
    gomore_primitives_previous_append_result result = {0};
    if (gomore_primitives_previous_state_append(
            &store, gomore_state.previous, OPENR1_GOMORE_PREVIOUS_BYTES,
            OPENR1_GOMORE_PREVIOUS_BYTES, scratch, sizeof(scratch),
            &result) != GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK) {
        ++gomore_state.previous_write_failures;
        return;
    }
    ++gomore_state.previous_writes;
}

static float gomore_cosine(float value) {
    return cosf(value);
}

static float gomore_sine(float value) {
    return sinf(value);
}

static float gomore_tangent(float value) {
    return tanf(value);
}

static float gomore_power(float value, float exponent) {
    return powf(value, exponent);
}

static uint16_t gomore_load_u16(const uint8_t source[2]) {
    return (uint16_t)source[0] | (uint16_t)((uint16_t)source[1] << 8u);
}

static uint32_t gomore_load_u32(const uint8_t source[4]) {
    return (uint32_t)source[0] | ((uint32_t)source[1] << 8u) |
        ((uint32_t)source[2] << 16u) | ((uint32_t)source[3] << 24u);
}

static float gomore_load_float(const uint8_t source[4]) {
    const uint32_t bits = gomore_load_u32(source);
    float value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static float gomore_float_from_bits(uint32_t bits) {
    float value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static const uint8_t *gomore_model_address(uint32_t stock_address,
                                            size_t length) {
    if (stock_address < R1_MODEL_DATA_STOCK_BASE) {
        return NULL;
    }
    const size_t offset = (size_t)(stock_address - R1_MODEL_DATA_STOCK_BASE);
    const size_t capacity = sizeof(r1_model_data_words);
    if (offset > capacity || length > capacity - offset) {
        return NULL;
    }
    return (const uint8_t *)(const void *)r1_model_data_words + offset;
}

typedef struct {
    uint32_t data_address;
    uint32_t element_count;
    uint32_t shape;
    uint32_t storage;
    uint32_t scale_bits;
} gomore_sleep_model_descriptor;

static bool gomore_sleep_descriptor_load(
    uint32_t table_address, size_t index,
    gomore_sleep_model_descriptor *descriptor) {
    if (descriptor == NULL || index >= 51u) {
        return false;
    }
    const uint8_t *const bytes = gomore_model_address(
        table_address + (uint32_t)(index * OPENR1_GOMORE_SLEEP_DESCRIPTOR_BYTES),
        OPENR1_GOMORE_SLEEP_DESCRIPTOR_BYTES);
    if (bytes == NULL) {
        return false;
    }
    *descriptor = (gomore_sleep_model_descriptor){
        .data_address = gomore_load_u32(&bytes[0]),
        .element_count = gomore_load_u32(&bytes[4]),
        .shape = gomore_load_u32(&bytes[8]),
        .storage = gomore_load_u32(&bytes[12]),
        .scale_bits = gomore_load_u32(&bytes[16]),
    };
    return true;
}

static bool gomore_sleep_half_binding(
    uint32_t table_address, size_t index, size_t expected_count,
    const uint16_t **values) {
    gomore_sleep_model_descriptor descriptor;
    if (values == NULL ||
            !gomore_sleep_descriptor_load(table_address, index, &descriptor) ||
            descriptor.element_count != expected_count ||
            ((descriptor.storage >> 16u) != 0x05u &&
             (descriptor.storage >> 16u) != 0x07u) ||
            descriptor.scale_bits != 0u) {
        return false;
    }
    const uint8_t *const bytes = gomore_model_address(
        descriptor.data_address, expected_count * sizeof(uint16_t));
    if (bytes == NULL || ((uintptr_t)bytes & 1u) != 0u) {
        return false;
    }
    *values = (const uint16_t *)(const void *)bytes;
    return true;
}

static bool gomore_sleep_affine_binding(
    uint32_t table_address, size_t weight_index, size_t bias_index,
    size_t rows, size_t columns,
    gomore_primitives_sleep_stage_affine_model *model) {
    gomore_sleep_model_descriptor weights;
    const uint16_t *bias = NULL;
    if (model == NULL || rows > SIZE_MAX / columns ||
            !gomore_sleep_descriptor_load(
                table_address, weight_index, &weights) ||
            weights.element_count != rows * columns ||
            (weights.storage >> 16u) != 0x0Eu ||
            !(gomore_float_from_bits(weights.scale_bits) > 0.0f) ||
            !gomore_sleep_half_binding(
                table_address, bias_index, rows, &bias)) {
        return false;
    }
    const uint8_t *const weight_bytes = gomore_model_address(
        weights.data_address, weights.element_count);
    if (weight_bytes == NULL) {
        return false;
    }
    *model = (gomore_primitives_sleep_stage_affine_model){
        .weights = (const int8_t *)(const void *)weight_bytes,
        .weight_count = weights.element_count,
        .rows = rows,
        .columns = columns,
        .weight_scale = gomore_float_from_bits(weights.scale_bits),
        .bias_half = (const int16_t *)(const void *)bias,
        .bias_count = rows,
    };
    return true;
}

static bool gomore_sleep_model_bind(
    uint32_t table_address,
    gomore_primitives_sleep_stage_classifier_model *model) {
    static const size_t convolution_weights[7] = {
        12u, 96u, 192u, 192u, 192u, 192u, 192u,
    };
    memset(model, 0, sizeof(*model));
    for (size_t block = 0u; block < 7u; ++block) {
        const size_t descriptor = block * 5u;
        const size_t parameters = block == 0u ? 4u : 8u;
        gomore_primitives_sleep_stage_conv_model *const convolution =
            &model->convolution[block];
        if (!gomore_sleep_half_binding(
                table_address, descriptor, convolution_weights[block],
                &convolution->weights_half) ||
                !gomore_sleep_half_binding(
                    table_address, descriptor + 1u, parameters,
                    &convolution->scale_half) ||
                !gomore_sleep_half_binding(
                    table_address, descriptor + 2u, parameters,
                    &convolution->offset_half) ||
                !gomore_sleep_half_binding(
                    table_address, descriptor + 3u, parameters,
                    &convolution->variance_half) ||
                !gomore_sleep_half_binding(
                    table_address, descriptor + 4u, parameters,
                    &convolution->mean_half)) {
            return false;
        }
        convolution->weight_count = convolution_weights[block];
        convolution->parameter_count = parameters;
    }
    return
        gomore_sleep_affine_binding(
            table_address, 35u, 36u, 32u, 120u, &model->projection[0]) &&
        gomore_sleep_affine_binding(
            table_address, 37u, 38u, 32u, 32u, &model->projection[1]) &&
        gomore_sleep_affine_binding(
            table_address, 39u, 43u, 96u, 32u,
            &model->recurrent[0].input) &&
        gomore_sleep_affine_binding(
            table_address, 40u, 44u, 96u, 32u,
            &model->recurrent[0].recurrent) &&
        gomore_sleep_affine_binding(
            table_address, 41u, 45u, 96u, 32u,
            &model->recurrent[1].input) &&
        gomore_sleep_affine_binding(
            table_address, 42u, 46u, 96u, 32u,
            &model->recurrent[1].recurrent) &&
        gomore_sleep_affine_binding(
            table_address, 47u, 48u, 32u, 32u,
            &model->post_recurrent) &&
        gomore_sleep_affine_binding(
            table_address, 49u, 50u, 4u, 32u, &model->output);
}

static float gomore_sleep_logistic(float value) {
    return gomore_primitives_logistic(value, expf);
}

static uint32_t gomore_sleep_tensor_construct(
    void *pool, size_t pool_length, uint32_t rank,
    const uint16_t *dimensions, size_t dimension_count) {
    if (pool == NULL || pool_length != 0x1B90u || rank != 2u ||
            dimensions == NULL || dimension_count != 2u ||
            dimensions[0] != 1u || dimensions[1] != 90u) {
        gomore_state.callback_failed = true;
        return 0u;
    }
    return (uint32_t)(uintptr_t)pool;
}

static const float *gomore_load_float_pointer(const uint8_t source[4]) {
    return (const float *)(uintptr_t)gomore_load_u32(source);
}

static void gomore_filter_apply(
    void *filter_state, float *values, size_t count) {
    if (!gomore_primitives_iir_filter_apply(
            filter_state, 0x50u, values, count)) {
        gomore_state.callback_failed = true;
    }
}

static void gomore_activity_statistics(
    const float *values, uint32_t count, uint32_t mode, float output[4]) {
    if (!gomore_primitives_peak_statistics(
            values, count, mode, output, powf, sqrtf)) {
        gomore_state.callback_failed = true;
    }
}

static float gomore_sps_state2_primary(const float *values) {
    const gomore_primitives_linear_model3 model = {
        .centers = {
            gomore_float_from_bits(UINT32_C(0x432DAD60)),
            gomore_float_from_bits(UINT32_C(0x432F2E7B)),
            gomore_float_from_bits(UINT32_C(0x44DF07BD)),
        },
        .divisors = {
            gomore_float_from_bits(UINT32_C(0x40B908FD)),
            gomore_float_from_bits(UINT32_C(0x41471339)),
            gomore_float_from_bits(UINT32_C(0x43982465)),
        },
        .weights = {
            gomore_float_from_bits(UINT32_C(0x3F5ABE4F)),
            gomore_float_from_bits(UINT32_C(0x3F8EE557)),
            gomore_float_from_bits(UINT32_C(0x3FC4413D)),
        },
        .bias = gomore_float_from_bits(UINT32_C(0x4131EECE)),
    };
    return gomore_primitives_linear_model3_evaluate(values, &model);
}

static float gomore_sps_state2_secondary(const float *values) {
    return gomore_primitives_sps_secondary_model(values, sqrt);
}

static float gomore_sps_state1_primary(const float *values) {
    const gomore_primitives_affine_reciprocal_model4 model = {
        .coefficients = {
            gomore_float_from_bits(UINT32_C(0x3BBE6E0E)),
            gomore_float_from_bits(UINT32_C(0xBE952A90)),
            gomore_float_from_bits(UINT32_C(0xC6002839)),
            gomore_float_from_bits(UINT32_C(0x39C6CDCD)),
            gomore_float_from_bits(UINT32_C(0x39997D65)),
            gomore_float_from_bits(UINT32_C(0x42C375D0)),
        },
    };
    return gomore_primitives_affine_reciprocal_model4_evaluate(
        values, &model);
}

static float gomore_sps_state1_secondary(const float *values) {
    const gomore_primitives_linear_model3 model = {
        .centers = {0.0f, 0.0f, 0.0f},
        .divisors = {1.0f, 1.0f, 1.0f},
        .weights = {
            gomore_float_from_bits(UINT32_C(0x3D666AB6)),
            gomore_float_from_bits(UINT32_C(0xBC5BA131)),
            gomore_float_from_bits(UINT32_C(0x3BB3BEDF)),
        },
        .bias = gomore_float_from_bits(UINT32_C(0xBF7535B8)),
    };
    return gomore_primitives_linear_model3_evaluate(values, &model);
}

static float gomore_sps_adjust(float primary, void *state) {
    const gomore_primitives_sps_model_state *const model = state;
    return gomore_primitives_linear_evaluate(
        primary, model->calibration_slope, model->calibration_intercept);
}

static void gomore_sps_commit(
    void *state, float primary, float secondary) {
    if (!gomore_primitives_accumulate_pair(
            state, sizeof(gomore_primitives_sps_model_state),
            primary, secondary)) {
        gomore_state.callback_failed = true;
    }
}

static void gomore_locomotion_classify(void *state, void *output) {
    const gomore_primitives_six_channel_linear_model ring_model = {
        .weights = {
            gomore_float_from_bits(UINT32_C(0xBA8E0D9F)),
            gomore_float_from_bits(UINT32_C(0x3C5D639E)),
            gomore_float_from_bits(UINT32_C(0xBA815EE5)),
            gomore_float_from_bits(UINT32_C(0xBCA9FB3C)),
            gomore_float_from_bits(UINT32_C(0xBC0BEFEE)),
            gomore_float_from_bits(UINT32_C(0x3C2C7C80)),
        },
        .bias = gomore_float_from_bits(UINT32_C(0x3F8F797D)),
        .scale = 1000.0f,
        .empty_window_value = 0.0f,
        .minimum_output = -32000,
    };
    static const uint32_t linear_bits[4] = {
        UINT32_C(0xBE445123), UINT32_C(0x3F697FE1),
        UINT32_C(0xBC00B405), UINT32_C(0x3F7237E0),
    };
    float linear_coefficients[4];
    for (size_t index = 0u; index < 4u; ++index) {
        linear_coefficients[index] =
            gomore_float_from_bits(linear_bits[index]);
    }
    const gomore_primitives_locomotion_classifier_configuration
        configuration = {
            .ring_score_model = &ring_model,
            .linear_sign_coefficients = linear_coefficients,
            .linear_sign_bias =
                gomore_float_from_bits(UINT32_C(0xBF4485EE)),
            .autocorrelation =
                gomore_primitives_locomotion_autocorrelation_analyze,
            .crossing_estimate =
                gomore_primitives_locomotion_crossing_period_estimate,
        };
    if (!gomore_primitives_locomotion_window_classify(
            state, 0x26Eu, output, 0x3Eu, &configuration)) {
        gomore_state.callback_failed = true;
    }
}

static int gomore_compare_float(const void *left, const void *right) {
    const float left_value = *(const float *)left;
    const float right_value = *(const float *)right;
    return left_value < right_value ? -1 : left_value > right_value ? 1 : 0;
}

static int32_t gomore_respiratory_estimate(
    void *state, uint32_t elapsed, const void *input, uint32_t status,
    float *rate, float *confidence) {
    const gomore_primitives_optical_period_providers providers = {
        .initialize_filter_state = gomore_large_filter_initialize,
        .apply_filter = gomore_filter_apply,
        .round_value = round,
        .feature_math = {
            .qsort_provider = qsort,
            .compare = gomore_compare_float,
            .power_f32 = powf,
            .square_root_f32 = sqrtf,
            .power_f64 = pow,
            .square_root_f64 = sqrt,
        },
    };
    int32_t result = -1;
    float output[2] = {0.0f, 0.0f};
    if (!gomore_primitives_optical_period_estimate(
            state, elapsed, input, status, &providers,
            &gomore_state.optical_period_workspace,
            output, &result)) {
        gomore_state.callback_failed = true;
        return -1;
    }
    *rate = output[0];
    *confidence = output[1];
    return result;
}

static void gomore_dormant_quadratic(
    float coefficient_a, float coefficient_b, float coefficient_c,
    void *state) {
    float roots[2] = {0.0f, 0.0f};
    if (!gomore_primitives_positive_quadratic_roots(
            coefficient_a, coefficient_b, coefficient_c, roots, powf)) {
        gomore_state.callback_failed = true;
        return;
    }
    memcpy((uint8_t *)state + 0x18u, roots, sizeof(roots));
    memset((uint8_t *)state + 0x20u, 0, sizeof(float));
}

static void gomore_dormant_cubic(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float coefficient_d, void *state) {
    if (!gomore_primitives_cubic_candidates(
            coefficient_a, coefficient_b, coefficient_c, coefficient_d,
            state, 0x2Cu, powf, atan2f, sqrtf, logf, expf, cosf, sinf)) {
        gomore_state.callback_failed = true;
    }
}

static float gomore_dormant_reduce(
    float primary, float secondary, float auxiliary,
    void *state, int32_t mode) {
    float output = 0.0f;
    if (!gomore_primitives_dormant_root_reduce(
            primary, secondary, auxiliary, state, 0x2Cu, mode,
            atanf, cosf, powf, &output)) {
        gomore_state.callback_failed = true;
    }
    return output;
}

static float gomore_dormant_finalize(
    float reduced, float auxiliary, void *state, int32_t mode) {
    float output = 0.0f;
    if (!gomore_primitives_dormant_root_resolve(
            reduced, auxiliary, state, 0x2Cu, mode, powf,
            gomore_dormant_quadratic, gomore_dormant_cubic, &output)) {
        gomore_state.callback_failed = true;
    }
    return output;
}

static void gomore_dormant_ratio_accumulate(
    void *state, const gomore_primitives_dormant_ratio_input *input) {
    if (!gomore_primitives_dormant_ratio_accumulator(
            (gomore_primitives_dormant_ratio_accumulator_state *)state,
            input, powf)) {
        gomore_state.callback_failed = true;
    }
}

static int32_t gomore_dormant_process_record(void *state, void *record) {
    gomore_primitives_dormant_estimator_record *const source = record;
    if (state == NULL || source == NULL || source->configuration == NULL) {
        gomore_state.callback_failed = true;
        return -1;
    }
    /* FUN_000721B4 reads configuration[2] for the mode-one smoother and
     * configuration[3] for the mode-zero angular projection. */
    gomore_primitives_dormant_cycle_auxiliary auxiliary = {
        .smoother_input = source->configuration[2],
        .mode0_first_input = source->configuration[3],
    };
    gomore_primitives_dormant_cycle_input input = {
        .sample_index = (int32_t)source->sample_index,
        .raw_heart_rate = source->selected_heart_rate,
        .selected_speed = source->selected_speed,
        .auxiliary_speed = source->current_auxiliary,
        .copied_auxiliary_1 = source->copied_auxiliary_1,
        .copied_auxiliary_2 = source->copied_auxiliary_2,
        .auxiliary = &auxiliary,
        .unused_heart_rate_feature = source->trailing_total_energy,
    };
    const gomore_primitives_dormant_cycle_providers providers = {
        .arctangent = atanf,
        .cosine = cosf,
        .sine = sinf,
        .power = powf,
        .reduce = gomore_dormant_reduce,
        .finalize = gomore_dormant_finalize,
        .filter_heart_rate =
            gomore_primitives_dormant_heart_rate_filter_update,
        .accumulate_ratio = gomore_dormant_ratio_accumulate,
    };
    int32_t result = -1;
    if (!gomore_primitives_dormant_estimator_cycle(
            state, GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES,
            &input, &providers, &result)) {
        gomore_state.callback_failed = true;
        return -1;
    }
    return result;
}

static void gomore_update_core(void *engine, uint32_t elapsed_seconds) {
    if (engine != gomore_state.engine + 0x140u ||
            !gomore_primitives_output_orchestrate(
                engine, 0x3894u, elapsed_seconds,
                &gomore_state.output_providers,
                &gomore_state.result_pointer)) {
        gomore_state.callback_failed = true;
    }
}

static void gomore_update_error(const void *context, int32_t status) {
    (void)context;
    (void)status;
}

static void gomore_request_reinitialize(void) {
    gomore_state.reinitialize_requested = true;
}

static int32_t gomore_update_apply(
    const void *context, const gomore_primitives_host_input *input,
    uint32_t normalized_timestamp) {
    (void)context;
    gomore_primitives_host_input normalized = *input;
    normalized.unix_seconds = normalized_timestamp;
    const gomore_primitives_host_input_bindings bindings = {
        .raw_optical_output_binding =
            (uint32_t)(uintptr_t)gomore_state.raw_optical_output,
        .accelerometer_output_bindings = {
            (uint32_t)(uintptr_t)gomore_state.accelerometer_outputs[0],
            (uint32_t)(uintptr_t)gomore_state.accelerometer_outputs[1],
            (uint32_t)(uintptr_t)gomore_state.accelerometer_outputs[2],
        },
    };
    gomore_state.callback_failed = false;
    if (!gomore_primitives_host_input_adapter_update(
            gomore_state.engine, OPENR1_GOMORE_ENGINE_BYTES,
            &normalized, gomore_state.sensor_update.previous_timestamp,
            gomore_state.raw_optical_output,
            gomore_state.accelerometer_outputs, &bindings,
            gomore_primitives_linear_resample, gomore_filter_apply,
            NULL, gomore_update_core) || gomore_state.callback_failed) {
        return -EIO;
    }
    return 0;
}

static void gomore_update_snapshot(const void *context) {
    (void)context;
    if (!gomore_primitives_copy_algorithm_output_snapshot(
            gomore_state.output_snapshot,
            sizeof(gomore_state.output_snapshot),
            &gomore_state.engine[0x140u], 0x3894u)) {
        gomore_state.callback_failed = true;
    }
}

static void gomore_lifecycle_noop(void *context) {
    (void)context;
}

static bool gomore_lifecycle_result_ready(void *context) {
    (void)context;
    return gomore_state.result_pointer != NULL &&
        !gomore_state.callback_failed;
}

static void gomore_lifecycle_activity(
    void *context, const uint32_t activity[2]) {
    (void)context;
    if (openr1_databases_zephyr_consume_activity_cumulative(
            activity, gomore_state.sleep_result_status) != R1_OK) {
        ++gomore_state.activity_publication_failures;
    }
}

static void gomore_lifecycle_sleep_status(void *context, uint8_t status) {
    (void)context;
    gomore_state.sleep_result_status = status;
}

static bool gomore_final_sleep_interval_select(
    gomore_primitives_sleep_interval_result *selected) {
    if (selected == NULL || gomore_state.engine == NULL) {
        return false;
    }
    uint8_t *const nested = &gomore_state.engine[0x140u];
    const gomore_primitives_sleep_cycle_state *const cycle =
        (const gomore_primitives_sleep_cycle_state *)(const void *)
            &nested[0xFF0u];
    *selected = cycle->previous_interval;
    if (cycle->last_decision.stage != 1u) {
        return true;
    }

    gomore_primitives_sleep_interval_source source =
        cycle->current.interval_source;
    const uint32_t current_time = gomore_load_u32(&nested[0x50u]);
    source.end = current_time;
    gomore_primitives_sleep_interval_result candidate;
    const uint8_t *const step = (const uint8_t *)(const void *)&cycle->step;
    if (!gomore_primitives_sleep_interval_compose(
            &candidate, cycle->step.minute_accumulator.minute_zero_fraction,
            cycle->step.local_time_window == 1u,
            gomore_load_u32(&step[0xA4u]),
            gomore_load_u32(&step[0xACu]), 1,
            cycle->previous_interval.end,
            (int16_t)gomore_load_u16(&nested[0x4Cu]), 0, 0u,
            &source, &cycle->policy, &cycle->previous_interval,
            cycle->previous_descriptor.totals[0],
            cycle->previous_descriptor.totals[3],
            (int16_t)cycle->policy.reserved)) {
        return false;
    }
    if ((candidate.flags & UINT8_C(0x10)) != 0u) {
        *selected = candidate;
    }
    return true;
}

static bool gomore_lifecycle_final_sleep(void *context) {
    (void)context;
    uint8_t *const stages = k_malloc(0xB40u);
    if (stages == NULL) {
        ++gomore_state.sleep_publication_failures;
        return false;
    }

    bool available = true;
    uint8_t *const nested = &gomore_state.engine[0x140u];
    const uint8_t *const stream = &nested[0x12B8u];
    const uint8_t mode = stream[0x20F5u];
    const uint8_t *const table = gomore_model_address(
        OPENR1_GOMORE_SLEEP_MODE_TABLE_ADDRESS,
        OPENR1_GOMORE_SLEEP_MODE_TABLE_BYTES);
    gomore_primitives_sleep_interval_result interval;
    if (table == NULL || mode >= 7u ||
            !gomore_final_sleep_interval_select(&interval)) {
        ++gomore_state.sleep_publication_failures;
        goto release;
    }

    gomore_primitives_final_sleep_build_output built = {
        .stages = (int8_t *)(void *)stages,
        .stage_capacity = 0xB40u,
    };
    int32_t status = -1;
    if (!gomore_primitives_final_sleep_build(
            (uint8_t *)(void *)stream, 0xB40u,
            gomore_load_u32(&nested[0x50u]),
            &table[(size_t)mode * 11u], &interval,
            gomore_primitives_sleep_stage_refine, tanh, powf,
            &built, &status) || status != 0) {
        ++gomore_state.sleep_publication_failures;
        goto release;
    }

    const gomore_primitives_final_sleep_record record = {
        .wire_type = built.wire_type,
        .start_timestamp = (int32_t)built.start_timestamp,
        .end_timestamp = (int32_t)built.end_timestamp,
        .stages = built.stages,
        .stage_count = built.stage_count,
        .efficiency = built.statistics.efficiency,
        .score = built.score,
        .rem_fraction = built.statistics.rem_fraction,
        .light_fraction = built.statistics.light_fraction,
        .deep_fraction = built.statistics.deep_fraction,
        .total_minutes = built.statistics.interval_minutes,
        .wake_minutes = built.statistics.awake_minutes,
        .rem_minutes = built.statistics.rem_minutes,
        .light_minutes = built.statistics.light_minutes,
        .deep_minutes = built.statistics.deep_minutes,
        .body_temperature = 0u,
    };
    uint8_t serialized[R1_SLEEP_STORED_MAX_BYTES];
    size_t serialized_length = 0u;
    if (!gomore_primitives_final_sleep_record_serialize(
            &record, serialized, sizeof(serialized),
            &serialized_length) ||
            openr1_databases_zephyr_consume_sleep_record(
                serialized, serialized_length) != R1_OK) {
        ++gomore_state.sleep_publication_failures;
        goto release;
    }
    ++gomore_state.sleep_publications;

release:
    k_free(stages);
    return available;
}

static void gomore_lifecycle_authorize(
    void *context, uint32_t slot, bool enabled) {
    (void)context;
    if (openr1_sensor_stream_zephyr_gomore_authorization_set(
            slot, enabled) != 0) {
        ++gomore_state.authorization_failures;
    }
}

static void gomore_lifecycle_dispatch(
    const gomore_primitives_topic_input_state *topic) {
    const uint8_t active_slot_mask =
        openr1_sensor_stream_zephyr_gomore_active_slot_mask();
    gomore_primitives_output_lifecycle_state lifecycle = {
        .active_slot_mask = active_slot_mask,
        .activity = {
            gomore_load_u32(&gomore_state.output_snapshot[0x78u]),
            gomore_load_u32(&gomore_state.output_snapshot[0x7Cu]),
        },
        .sleep_lifecycle_flags = gomore_state.output_snapshot[0x70u],
        .stage_ppg_request =
            (int8_t)gomore_state.output_snapshot[0x62u],
        .previous_stage_ppg_request =
            (active_slot_mask & UINT8_C(0x10)) != 0u,
        .accelerometer_pending = topic->accelerometer_sample_count != 0u,
        .optical_pending = topic->raw_optical_sample_count != 0u,
    };
    const gomore_primitives_output_lifecycle_providers providers = {
        .refresh_input = gomore_lifecycle_noop,
        .update_engine = gomore_lifecycle_noop,
        .result_ready = gomore_lifecycle_result_ready,
        .consume_activity = gomore_lifecycle_activity,
        .publish_sleep_status = gomore_lifecycle_sleep_status,
        .publish_final_sleep = gomore_lifecycle_final_sleep,
        .authorize = gomore_lifecycle_authorize,
    };
    if (!gomore_primitives_output_lifecycle_dispatch(
            &gomore_state, &lifecycle, &providers)) {
        gomore_state.callback_failed = true;
    }
}

static bool gomore_topic_consume(
    void *context, const gomore_primitives_topic_input_state *topic) {
    r1_runtime *const runtime = context;
    if (runtime == NULL || topic == NULL || gomore_state.engine == NULL) {
        return false;
    }
    uint32_t timestamp = runtime->device.unix_seconds;
    (void)openr1_clock_zephyr_epoch(&timestamp);
    if (timestamp == 0u) {
        timestamp = k_uptime_get_32() / 1000u;
    }
    int16_t utc_offset = (int16_t)runtime->device.timezone_minutes_raw;
    (void)openr1_clock_zephyr_utc_offset(&utc_offset);
    const gomore_primitives_host_input input = {
        .unix_seconds = timestamp,
        .timezone_offset_minutes = utc_offset,
        .accelerometer_axes = {
            topic->accelerometer_axes[0],
            topic->accelerometer_axes[1],
            topic->accelerometer_axes[2],
        },
        .accelerometer_sample_count = topic->accelerometer_sample_count,
        .raw_optical_samples = topic->raw_optical,
        .raw_optical_sample_count = topic->raw_optical_sample_count,
        .raw_optical_channel_count =
            topic->raw_optical_sample_count == 0u ? 0u : 1u,
        .hrv_auxiliary_samples = topic->hrv_auxiliary,
        .hrv_auxiliary_count = topic->hrv_auxiliary_count,
        .direct_heart_rate = topic->direct_heart_rate,
        .legacy_zero_word = 0u,
        .wear_state_is_unknown =
            runtime->device.wear == R1_WEAR_UNKNOWN ? 1u : 0u,
        .mode2_legacy_byte0 = 0u,
        .mode2_legacy_byte1 = 0u,
        .raw_optical_binding =
            (uint32_t)(uintptr_t)topic->raw_optical,
    };
    const gomore_primitives_sensor_update_configuration configuration = {
        .diagnostics_enabled = false,
        .validation_enabled = false,
        .configured_timestamp_limit = 0u,
        .runtime_present = true,
        .configured_version = 7,
        .runtime_version = 7,
    };
    const gomore_primitives_sensor_update_providers providers = {
        .diagnose = NULL,
        .log_error = gomore_update_error,
        .apply = gomore_update_apply,
        .snapshot = gomore_update_snapshot,
    };
    int32_t status = -EIO;
    if (!gomore_primitives_sensor_update_orchestrate(
            &gomore_state, &gomore_state.sensor_update, &input,
            &configuration, &providers, &status) || status != 0 ||
            gomore_state.callback_failed) {
        const uint32_t failure_status = status != 0
            ? (uint32_t)status : UINT32_C(1);
        (void)gomore_primitives_update_failure_counter(
            failure_status, timestamp,
            &gomore_state.consecutive_update_failures,
            NULL, gomore_request_reinitialize);
        gomore_state.status = status == 0 ? -EIO : status;
        ++gomore_state.update_failures;
        return false;
    }
    gomore_lifecycle_dispatch(topic);
    if (gomore_state.callback_failed) {
        gomore_state.status = -EIO;
        ++gomore_state.update_failures;
        return false;
    }
    (void)gomore_primitives_update_failure_counter(
        0u, timestamp, &gomore_state.consecutive_update_failures,
        NULL, gomore_request_reinitialize);
    gomore_state.status = 0;
    ++gomore_state.updates;
    return true;
}

static bool gomore_output_stage_execute(
    void *context, uint8_t *engine, size_t engine_length,
    uint32_t elapsed_updates,
    const gomore_primitives_output_stage_descriptor *descriptor,
    uint32_t *status) {
    (void)context;
    if (engine == NULL || engine_length < 0x3894u || descriptor == NULL ||
            status == NULL || descriptor->stage_state_offset >= engine_length) {
        return false;
    }
    *status = 0u;
    switch (descriptor->id) {
    case GOMORE_PRIMITIVES_OUTPUT_STAGE_RESPIRATORY_RATE: {
        const gomore_primitives_respiratory_rate_input input = {
            .estimator_input = (const void *)
                gomore_load_float_pointer(&engine[0x30u]),
            .input_unavailable = engine[0x34u] != 0u,
            .secondary_code = engine[0x41u],
            .primary_code = engine[0x42u],
        };
        const gomore_primitives_respiratory_rate_providers providers = {
            .estimate = gomore_respiratory_estimate,
            .square_root = sqrt,
        };
        if (!input.input_unavailable && input.estimator_input == NULL) {
            return false;
        }
        gomore_state.callback_failed = false;
        const bool result = gomore_primitives_respiratory_rate_update(
            (gomore_primitives_respiratory_rate_state *)(void *)
                &engine[descriptor->stage_state_offset],
            elapsed_updates, &input,
            (gomore_primitives_optical_interval_state *)(void *)
                &engine[0x228u],
            &providers, (float *)(void *)&engine[0x40u], status);
        return result && !gomore_state.callback_failed;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_LOCOMOTION_PREPROCESS: {
        const float *axes[3] = {
            gomore_load_float_pointer(&engine[0x88u]),
            gomore_load_float_pointer(&engine[0x8Cu]),
            gomore_load_float_pointer(&engine[0x90u]),
        };
        const bool unavailable = engine[0x94u] != 0u;
        if (!unavailable &&
                (axes[0] == NULL || axes[1] == NULL || axes[2] == NULL)) {
            return false;
        }
        gomore_state.callback_failed = false;
        const int32_t result = gomore_primitives_locomotion_window_preprocess(
            &engine[descriptor->stage_state_offset], 0x26Eu,
            elapsed_updates, axes, unavailable,
            &engine[0x98u], 0x3Eu, sqrtf, gomore_locomotion_classify);
        if (result < 0 || gomore_state.callback_failed) {
            return false;
        }
        *status = (uint32_t)result;
        return true;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_CLASSIFIER:
        return gomore_primitives_motion_classifier_update(
            &engine[descriptor->stage_state_offset],
            engine_length - descriptor->stage_state_offset,
            elapsed_updates, &engine[0x88u], engine_length - 0x88u,
            &engine[0x98u], 0x3Eu, &engine[0xD8u], 3u, NULL);

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_CANDIDATE: {
        const gomore_primitives_sps_candidate_providers providers = {
            .state2_primary = gomore_sps_state2_primary,
            .state2_secondary = gomore_sps_state2_secondary,
            .state1_primary = gomore_sps_state1_primary,
            .state1_secondary = gomore_sps_state1_secondary,
            .adjust = gomore_sps_adjust,
            .commit = gomore_sps_commit,
        };
        gomore_state.callback_failed = false;
        const bool result =
            gomore_primitives_sps_accelerometer_candidate_update(
                (gomore_primitives_sps_candidate_state *)(void *)
                    &engine[descriptor->stage_state_offset],
                elapsed_updates,
                (const gomore_primitives_sps_features *)(const void *)
                    &engine[0x98u],
                (const gomore_primitives_sps_motion *)(const void *)
                    &engine[0xD8u],
                gomore_load_float(&engine[0x74u]), &providers,
                (gomore_primitives_sps_candidate_output *)(void *)
                    &engine[0xDCu]);
        return result && !gomore_state.callback_failed;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_SELECT:
        *status = gomore_primitives_sps_select_available(
            gomore_load_float(&engine[0x10u]),
            gomore_load_float(&engine[0x6Cu]),
            gomore_load_float(&engine[0xDCu]), engine[0xE0u], NULL,
            (gomore_primitives_sps_selection *)(void *)&engine[0xE4u]);
        return true;

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_MOTION: {
        const float *axes[3] = {
            gomore_load_float_pointer(&engine[0x88u]),
            gomore_load_float_pointer(&engine[0x8Cu]),
            gomore_load_float_pointer(&engine[0x90u]),
        };
        if (engine[0x94u] == 0u &&
                (axes[0] == NULL || axes[1] == NULL || axes[2] == NULL)) {
            return false;
        }
        const int32_t result = gomore_primitives_sleep_motion_feature(
            (gomore_primitives_sleep_motion_state *)(void *)
                &engine[descriptor->stage_state_offset],
            elapsed_updates, axes, engine[0x94u] != 0u,
            (float *)(void *)&engine[0xF0u], floorf, sqrtf);
        if (result < 0) {
            return false;
        }
        *status = (uint32_t)result;
        return true;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_HEART_RATE_SELECT:
        return gomore_primitives_select_heart_rate(
            engine[descriptor->stage_state_offset],
            gomore_load_float(&engine[0x2Cu]),
            (const gomore_primitives_hr_candidate *)(const void *)
                &engine[0xF8u],
            (gomore_primitives_hr_selection *)(void *)&engine[0x104u]);

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_ENERGY:
        *status = gomore_primitives_energy_update(
            (gomore_primitives_energy_update_state *)(void *)
                &engine[descriptor->stage_state_offset],
            (int32_t)elapsed_updates,
            gomore_load_float(&engine[0x104u]),
            &engine[0x74u], sizeof(gomore_primitives_profile_output),
            gomore_load_float(&engine[0x28u]),
            gomore_load_float(&engine[0x110u]),
            (const float *)(const void *)&engine[0x20u],
            gomore_load_float(&engine[0xE4u]),
            gomore_load_float(&engine[0xF0u]),
            (int8_t)engine[0xD9u],
            gomore_load_float(&engine[0x18u]),
            expf, logf, log, &gomore_primitives_energy_table_defaults,
            (gomore_primitives_energy_update_output *)(void *)
                &engine[0x114u]);
        return true;

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_GATE: {
        /* Exact Float32 words behind stock DAT_0005F3D0 at 0x000BD2E4. */
        static const uint32_t weight_bits[18] = {
            UINT32_C(0xBC74E45F), UINT32_C(0xBC307364),
            UINT32_C(0xBC3AABE4), UINT32_C(0xBC425615),
            UINT32_C(0xBC36586D), UINT32_C(0xBC2E6D76),
            UINT32_C(0xBC2ABB77), UINT32_C(0xBC3C334A),
            UINT32_C(0xBC5C10B1), UINT32_C(0xBC43123B),
            UINT32_C(0xBC3D049D), UINT32_C(0xBC5251C5),
            UINT32_C(0xBC50B8CE), UINT32_C(0xBC795147),
            UINT32_C(0xBC92BF25), UINT32_C(0xBCD9F826),
            UINT32_C(0xBD120A28), UINT32_C(0xBD8D8A4A),
        };
        float weights[18];
        for (size_t index = 0u; index < 18u; ++index) {
            weights[index] = gomore_float_from_bits(weight_bits[index]);
        }
        return gomore_primitives_motion_gate_accumulate(
            (gomore_primitives_motion_gate_state *)(void *)
                &engine[descriptor->stage_state_offset],
            elapsed_updates, gomore_load_u32(&engine[0x50u]),
            gomore_load_float(&engine[0xF0u]), weights,
            (gomore_primitives_motion_gate_output *)(void *)
                &engine[0x1B8u]);
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_CYCLE: {
        /* The isolated 0x5C19C reduction made its stock state[-4] read an
         * explicit preceding-fraction argument. At this call boundary that
         * word is exactly engine+0x0FEC, immediately before the substate. */
        const gomore_primitives_sleep_cycle_input input = {
            .elapsed_seconds = elapsed_updates,
            .current_time = gomore_load_u32(&engine[0x50u]),
            .utc_offset_minutes =
                (int16_t)gomore_load_u16(&engine[0x4Cu]),
            .minute_sample = gomore_load_float(&engine[0xF4u]),
            .ring_sample = gomore_load_float(&engine[0x104u]),
            .input_active = engine[0x35u] != 0u,
            .upper_flag = engine[0x34u] == 1u,
            .lower_flag = engine[0x94u] == 1u,
            .quality_flag4 = engine[0x1BCu] != 0u,
            .quality_flag6 = engine[0x1BEu] != 0u,
            .preceding_fraction = gomore_load_float(&engine[0xFECu]),
        };
        return gomore_primitives_sleep_cycle_update(
            (gomore_primitives_sleep_cycle_state *)(void *)
                &engine[descriptor->stage_state_offset],
            &input,
            (gomore_primitives_sleep_interval_result *)(void *)
                &engine[0x184u]);
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_OPTICAL_PEAK: {
        const gomore_primitives_sleep_optical_input input = {
            .samples = gomore_load_float_pointer(&engine[0x30u]),
            .invalid = engine[0x34u] != 0u,
        };
        if (!input.invalid && input.samples == NULL) {
            return false;
        }
        gomore_state.callback_failed = false;
        const bool result = gomore_primitives_sleep_optical_peak_update(
            (gomore_primitives_sleep_optical_history *)(void *)
                &engine[descriptor->stage_state_offset],
            elapsed_updates, &input, &engine[0x1A4u],
            gomore_filter_initialize, gomore_primitives_linear_resample,
            gomore_filter_apply);
        return result && !gomore_state.callback_failed;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_WINDOW: {
        const bool alternate = engine[0x94u] != 0u;
        const gomore_primitives_activity_window_input input = {
            .samples = gomore_load_float_pointer(&engine[0x38u]),
            .sample_count = (int16_t)gomore_load_u16(&engine[0x3Cu]),
            .channel_count = engine[0x3Eu],
        };
        const gomore_primitives_activity_window_providers providers = {
            .axes = {
                gomore_load_float_pointer(&engine[0x88u]),
                gomore_load_float_pointer(&engine[0x8Cu]),
                gomore_load_float_pointer(&engine[0x90u]),
            },
            .alternate_conditioning = alternate,
            .square_root = sqrtf,
            .statistics = gomore_activity_statistics,
        };
        gomore_state.callback_failed = false;
        const bool result = gomore_primitives_activity_window_update(
            (gomore_primitives_activity_window_state *)(void *)
                &engine[descriptor->stage_state_offset],
            (float)elapsed_updates, &input, &providers,
            gomore_state.activity_differences,
            sizeof(gomore_state.activity_differences) /
                sizeof(gomore_state.activity_differences[0]),
            (gomore_primitives_activity_window_output *)(void *)
                &engine[0x1C0u]);
        return result && !gomore_state.callback_failed;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_DORMANT_ESTIMATOR: {
        gomore_state.callback_failed = false;
        const int32_t result = gomore_primitives_dormant_estimator_update(
            &engine[descriptor->stage_state_offset],
            GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES,
            elapsed_updates,
            (const uint32_t *)(const void *)&engine[0x50u],
            (const float *)(const void *)&engine[0x104u],
            (const float *)(const void *)&engine[0xE4u],
            (const float *)(const void *)&engine[0x54u],
            (const float *)(const void *)&engine[0x14u],
            (const float *)(const void *)&engine[0x114u],
            &engine[0x140u], GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_OUTPUT_BYTES,
            gomore_dormant_process_record);
        if (result < 0 || gomore_state.callback_failed) {
            return false;
        }
        *status = (uint32_t)result;
        return true;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_STREAM: {
        _Static_assert(
            sizeof(gomore_primitives_sleep_stage_stream_state) == 0x20F8u,
            "sleep-stage stream state must match the recovered ABI");
        const uint8_t *const mode_table = gomore_model_address(
            OPENR1_GOMORE_SLEEP_MODE_TABLE_ADDRESS,
            OPENR1_GOMORE_SLEEP_MODE_TABLE_BYTES);
        if (mode_table == NULL) {
            return false;
        }
        gomore_state.callback_failed = false;
        const bool result = gomore_primitives_sleep_stage_stream_update(
            (gomore_primitives_sleep_stage_stream_state *)(void *)
                &engine[descriptor->stage_state_offset],
            gomore_load_u32(&engine[0x50u]),
            (const gomore_primitives_sleep_stage_peak_input *)(const void *)
                &engine[0x1A4u],
            &engine[0x184u], 0x20u,
            (const gomore_primitives_sleep_stage_status *)(const void *)
                &engine[0x1B8u],
            &engine[0x1B5u], mode_table,
            OPENR1_GOMORE_SLEEP_MODE_TABLE_BYTES,
            gomore_sleep_tensor_construct,
            gomore_primitives_sleep_stage_classify,
            &gomore_state.sleep_classifier);
        return result && !gomore_state.callback_failed;
    }

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_STEP_ACCUMULATE:
        return gomore_primitives_step_accumulate(
            (gomore_primitives_step_accumulator *)(void *)
                &engine[descriptor->stage_state_offset],
            elapsed_updates, engine[0xDAu],
            (float *)(void *)&engine[0x1C4u]);

    case GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_ACCUMULATE: {
        gomore_primitives_activity_accumulator_state *const state =
            (gomore_primitives_activity_accumulator_state *)(uintptr_t)
                gomore_load_u32(&engine[descriptor->stage_state_offset]);
        if (state == NULL) {
            return false;
        }
        return gomore_primitives_activity_accumulate(
            state, gomore_load_u32(&engine[0x50u]),
            (int16_t)gomore_load_u16(&engine[0x4Cu]),
            gomore_load_float(&engine[0x1C4u]),
            (const gomore_primitives_energy_update_output *)(const void *)
                &engine[0x114u],
            gomore_load_float(&engine[0xE4u]),
            (gomore_primitives_activity_accumulator_output *)(void *)
                &engine[0x1C8u]);
    }

    default:
        /* The fixed schedule has no extension IDs. */
        return false;
    }
}

static void gomore_small_filter_initialize(
    void *record, uint32_t mode, uint32_t count, float parameter) {
    if (record == NULL ||
        !gomore_primitives_iir_low_high_coefficients(
            record, mode, count, parameter,
            gomore_cosine, gomore_sine, gomore_power)) {
        gomore_state.callback_failed = true;
    }
}

static void gomore_large_filter_initialize(
    void *record, uint32_t count, const float parameters[2]) {
    if (record == NULL ||
        !gomore_primitives_iir_bandpass_coefficients(
            record, count, parameters,
            gomore_cosine, gomore_sine, gomore_tangent)) {
        gomore_state.callback_failed = true;
    }
}

static void gomore_filter_initialize(
    void *record, uint32_t rows, uint32_t columns,
    const float parameters[2]) {
    if (record == NULL || rows != 2u || columns != 2u ||
        !gomore_primitives_iir_bandpass_coefficients(
            record, columns, parameters,
            gomore_cosine, gomore_sine, gomore_tangent)) {
        gomore_state.callback_failed = true;
        return;
    }
    /* This callback corresponds to stock 0x71D62's mode-two branch. The
     * designer writes coefficients at +4; the wrapper publishes order 4. */
    uint8_t *bytes = record;
    bytes[0] = 4u;
    bytes[1] = 0u;
    bytes[2] = 0u;
    bytes[3] = 0u;
}

static void gomore_finish_sps_initialize(void *context) {
    (void)context;
    /* Stock callback 0x5A442 is the recovered return-zero leaf. */
}

static bool profile_matches(
    const r1_user_profile *left, bool left_defaulted,
    const r1_user_profile *right, bool right_defaulted) {
    return left_defaulted == right_defaulted &&
        left->gender == right->gender &&
        left->age_years == right->age_years &&
        left->height_cm == right->height_cm &&
        left->weight_kg == right->weight_kg &&
        left->valid == right->valid;
}

static gomore_primitives_profile_input profile_convert(
    const r1_user_profile *profile, bool defaulted) {
    /* Exact 28-byte stock default at retail address 0x0009A5B4. */
    gomore_primitives_profile_input converted = {
        .age_years = 28.0f,
        .binary_sex = 1.0f,
        .height_centimeters = 175.0f,
        .weight_kilograms = 75.0f,
        .parameter_4 = -1.0f,
        .parameter_5 = -1.0f,
        .parameter_6 = -1.0f,
    };
    if (!defaulted) {
        converted.age_years = (float)profile->age_years;
        converted.binary_sex = profile->gender == 0u ? 0.0f : 1.0f;
        converted.height_centimeters = (float)profile->height_cm;
        converted.weight_kilograms = (float)profile->weight_kg;
    }
    return converted;
}

static void gomore_release(bool checkpoint_previous) {
    if (checkpoint_previous) {
        gomore_previous_state_persist();
    }
    k_free(gomore_state.previous);
    k_free(gomore_state.engine);
    gomore_state.engine = NULL;
    gomore_state.previous = NULL;
    memset(gomore_state.time_configuration, 0,
           sizeof(gomore_state.time_configuration));
}

static int gomore_initialize(
    uint32_t timestamp, const r1_user_profile *profile, bool defaulted,
    bool restore_previous) {
    uint8_t *engine = k_calloc(1u, OPENR1_GOMORE_ENGINE_BYTES);
    uint8_t *previous = k_calloc(1u, OPENR1_GOMORE_PREVIOUS_BYTES);
    if (engine == NULL || previous == NULL) {
        k_free(previous);
        k_free(engine);
        gomore_state.status = -ENOMEM;
        return -ENOMEM;
    }

    gomore_state.engine = engine;
    gomore_state.previous = previous;
    gomore_state.callback_failed = false;
    gomore_state.previous_available = false;
    gomore_state.previous_restored = false;
    gomore_state.result_pointer = NULL;
    gomore_state.sleep_result_status = 0u;
    gomore_state.sensor_update = (gomore_primitives_sensor_update_state){0};
    memset(gomore_state.raw_optical_output, 0,
           sizeof(gomore_state.raw_optical_output));
    memset(gomore_state.accelerometer_outputs, 0,
           sizeof(gomore_state.accelerometer_outputs));
    memset(gomore_state.output_snapshot, 0,
           sizeof(gomore_state.output_snapshot));
    memset(&gomore_state.optical_period_workspace, 0,
           sizeof(gomore_state.optical_period_workspace));
    if (!gomore_sleep_model_bind(
            OPENR1_GOMORE_SLEEP_BELOW_DESCRIPTOR_ADDRESS,
            &gomore_state.sleep_models[0]) ||
            !gomore_sleep_model_bind(
                OPENR1_GOMORE_SLEEP_UPPER_DESCRIPTOR_ADDRESS,
                &gomore_state.sleep_models[1])) {
        k_free(previous);
        k_free(engine);
        gomore_state.engine = NULL;
        gomore_state.previous = NULL;
        gomore_state.status = -EINVAL;
        return -EINVAL;
    }
    gomore_state.sleep_classifier =
        (gomore_primitives_sleep_stage_classifier_context){
            .mode_below_100 = &gomore_state.sleep_models[0],
            .mode_100_and_above = &gomore_state.sleep_models[1],
            .math = {
                .square_root = sqrtf,
                .exponential = expf,
                .logistic = gomore_sleep_logistic,
                .hyperbolic_tangent = tanhf,
            },
        };
    memset(gomore_state.time_configuration, 0,
           sizeof(gomore_state.time_configuration));
    gomore_state.output_providers.context = &gomore_state;
    for (size_t stage = 0u;
            stage < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++stage) {
        gomore_state.output_providers.stages[stage] =
            gomore_output_stage_execute;
    }

    (void)gomore_previous_state_prepare(gomore_state.previous);
    if (!restore_previous) {
        memset(gomore_state.previous, 0, OPENR1_GOMORE_PREVIOUS_BYTES);
        gomore_state.previous_restored = false;
    }

    const gomore_primitives_profile_input converted =
        profile_convert(profile, defaulted);
    const uint32_t previous_binding =
        (uint32_t)(uintptr_t)gomore_state.previous;
    const gomore_primitives_sleep_algorithm_configuration configuration = {
        .random_seed = timestamp,
        .version_validation_enabled = false,
        .configured_runtime_limit = 0u,
        .runtime_present = true,
        .configured_version = 7,
        .runtime_version = 7,
        .time_configuration = gomore_state.time_configuration,
        .time_configuration_length =
            sizeof(gomore_state.time_configuration),
        .seed_random = srand,
        .random_value = rand,
        .initialize_small_filter = gomore_small_filter_initialize,
        .initialize_large_filter = gomore_large_filter_initialize,
        .finish_sps_initialize = gomore_finish_sps_initialize,
        .initialize_filter = gomore_filter_initialize,
        .logger = NULL,
    };
    gomore_primitives_sleep_algorithm_outputs outputs = {0};
    gomore_state.status = gomore_primitives_sleep_algorithm_initialize(
        gomore_state.engine, OPENR1_GOMORE_ENGINE_BYTES,
        timestamp, &converted,
        gomore_state.previous, OPENR1_GOMORE_PREVIOUS_BYTES,
        previous_binding, &configuration, &outputs);
    if (gomore_state.status != 0 || gomore_state.callback_failed ||
        outputs.active_estimator_state == NULL ||
        outputs.result_pointer == NULL) {
        if (gomore_state.status == 0) {
            gomore_state.status = -EIO;
        }
        const int32_t status = gomore_state.status;
        gomore_release(false);
        return status;
    }
    return 0;
}

int openr1_gomore_zephyr_sync(r1_runtime *runtime) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    const bool enabled = runtime->device.health_settings[4] != 0u;
    if (!enabled) {
        openr1_sensor_stream_zephyr_health_policy_request(false);
        gomore_release(true);
        gomore_state.profile_recorded = false;
        gomore_state.force_fresh_previous = false;
        gomore_state.reinitialize_requested = false;
        gomore_state.consecutive_update_failures = 0u;
        gomore_state.retry_at_uptime = 0u;
        gomore_state.status = 0;
        return 0;
    }
    openr1_sensor_stream_zephyr_health_policy_request(true);

    const r1_user_profile *profile = &runtime->device.profile;
    const bool defaulted = !profile->valid;
    const bool same_profile = gomore_state.profile_recorded &&
        profile_matches(
            &gomore_state.profile, gomore_state.profile_defaulted,
            profile, defaulted);
    if (gomore_state.engine != NULL && same_profile) {
        return 0;
    }

    const uint32_t uptime = k_uptime_get_32();
    if (gomore_state.engine == NULL && same_profile &&
        gomore_state.retry_at_uptime != 0u &&
        (int32_t)(uptime - gomore_state.retry_at_uptime) < 0) {
        return gomore_state.status;
    }

    const bool profile_changed = gomore_state.profile_recorded && !same_profile;
    if (gomore_state.engine != NULL || !same_profile) {
        if (profile_changed) {
            gomore_state.force_fresh_previous = true;
        }
        gomore_release(!profile_changed);
        gomore_state.retry_at_uptime = 0u;
    }
    gomore_state.profile = *profile;
    gomore_state.profile_defaulted = defaulted;
    gomore_state.profile_recorded = true;

    uint32_t timestamp = runtime->device.unix_seconds;
    if (timestamp == 0u) {
        timestamp = uptime / 1000u;
    }
    const bool restore_previous = !gomore_state.force_fresh_previous;
    gomore_state.force_fresh_previous = false;
    const int status = gomore_initialize(
        timestamp, profile, defaulted, restore_previous);
    if (status != 0 && !restore_previous) {
        gomore_state.force_fresh_previous = true;
    }
    gomore_state.retry_at_uptime = status == 0 ? 0u :
        uptime + OPENR1_GOMORE_RETRY_MILLISECONDS;
    return status;
}

int openr1_gomore_zephyr_poll(r1_runtime *runtime) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    if (!openr1_gomore_zephyr_initialized()) {
        return gomore_state.status;
    }
    const int consumed = openr1_sensor_stream_zephyr_gomore_consume_ready(
        gomore_topic_consume, runtime);
    if (gomore_state.reinitialize_requested) {
        gomore_state.reinitialize_requested = false;
        (void)openr1_gomore_zephyr_reinitialize(runtime);
    }
    return consumed;
}

int openr1_gomore_zephyr_reinitialize(r1_runtime *runtime) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    if (gomore_state.engine == NULL ||
            runtime->device.health_settings[4] == 0u) {
        return 0;
    }

    if (openr1_sensor_stream_zephyr_gomore_authorization_set(4u, false) != 0) {
        ++gomore_state.authorization_failures;
    }
    gomore_release(false);
    gomore_state.profile_recorded = false;
    gomore_state.force_fresh_previous = true;
    gomore_state.retry_at_uptime = 0u;
    gomore_state.consecutive_update_failures = 0u;
    (void)openr1_sensor_stream_zephyr_gomore_health_stage_set(true);

    const int status = openr1_gomore_zephyr_sync(runtime);
    if (status == 0) {
        ++gomore_state.reinitializations;
    } else {
        ++gomore_state.reinitialization_failures;
    }
    return status;
}

bool openr1_gomore_zephyr_initialized(void) {
    /* A failed sample update does not invalidate the allocated engine. Stock
     * retries the next ready batch and reinitializes only on failure 60. */
    return gomore_state.engine != NULL;
}

int32_t openr1_gomore_zephyr_last_status(void) {
    return gomore_state.status;
}

size_t openr1_gomore_zephyr_allocated_bytes(void) {
    return gomore_state.engine == NULL ? 0u :
        OPENR1_GOMORE_ENGINE_BYTES + OPENR1_GOMORE_PREVIOUS_BYTES;
}

bool openr1_gomore_zephyr_previous_state_available(void) {
    return gomore_state.previous_available;
}

bool openr1_gomore_zephyr_previous_state_restored(void) {
    return gomore_state.previous_restored;
}

uint32_t openr1_gomore_zephyr_previous_state_writes(void) {
    return gomore_state.previous_writes;
}

uint32_t openr1_gomore_zephyr_previous_state_write_failures(void) {
    return gomore_state.previous_write_failures;
}

uint32_t openr1_gomore_zephyr_updates(void) {
    return gomore_state.updates;
}

uint32_t openr1_gomore_zephyr_update_failures(void) {
    return gomore_state.update_failures;
}

uint32_t openr1_gomore_zephyr_activity_publication_failures(void) {
    return gomore_state.activity_publication_failures;
}

uint32_t openr1_gomore_zephyr_sleep_publications(void) {
    return gomore_state.sleep_publications;
}

uint32_t openr1_gomore_zephyr_sleep_publication_failures(void) {
    return gomore_state.sleep_publication_failures;
}

uint32_t openr1_gomore_zephyr_authorization_failures(void) {
    return gomore_state.authorization_failures;
}

uint32_t openr1_gomore_zephyr_reinitializations(void) {
    return gomore_state.reinitializations;
}

uint32_t openr1_gomore_zephyr_reinitialization_failures(void) {
    return gomore_state.reinitialization_failures;
}
