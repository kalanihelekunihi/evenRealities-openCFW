/* Stock 0x60dc4: bind the source-owned sleep model to the typed C stage. */
#include <stdint.h>
#include <stddef.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"
#include "../../vendor/model_data/r1_model_data.h"
#include "../../vendor/quantized_runtime/quantized_runtime.h"

extern float r1_native_sqrtf(float);
extern float r1_native_expf(float);
extern float r1_native_tanhf(float);

#define MODEL_PTR(type, address) \
    ((const type *)(const void *)((const uint8_t *)r1_model_data_words + \
                                 ((address) - R1_MODEL_DATA_STOCK_BASE)))
#include "native_gomore_sleep_stage_model.inc"
#undef MODEL_PTR

_Static_assert(sizeof(quantized_runtime_pool) == 0x1B90u,
               "stock sleep tensor pool layout");
_Static_assert(R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_OFFSET +
               R1_GOMORE_SLEEP_100_AND_ABOVE_WORD_COUNT ==
               R1_MODEL_DATA_WORD_COUNT, "complete sleep model data");

static uint32_t construct_tensor(void *pool, size_t pool_length,
                                 uint32_t rank, const uint16_t *dimensions,
                                 size_t dimension_count)
{
    if (pool_length < sizeof(quantized_runtime_pool) ||
        rank > dimension_count || rank > 3u)
        return 0u;
    return (uint32_t)(uintptr_t)quantized_runtime_tensor_construct(
        (quantized_runtime_pool *)pool, (int32_t)rank, dimensions);
}

static float logistic(float value)
{
    return gomore_primitives_logistic(value, r1_native_expf);
}

static const gomore_primitives_sleep_stage_classifier_context classifier = {
    .mode_below_100 = &sleep_models[0],
    .mode_100_and_above = &sleep_models[1],
    .math = {
        .square_root = r1_native_sqrtf,
        .exponential = r1_native_expf,
        .logistic = logistic,
        .hyperbolic_tangent = r1_native_tanhf,
    },
};

uint32_t r1_gomore_stage_60dc4_native(uint32_t state_address,
    uint32_t elapsed, uint32_t peaks_address, uint32_t activity_address,
    uint32_t timestamp_address, uint32_t status_address,
    uint32_t output_address)
{
    (void)elapsed; /* Stock stage reads the live timestamp word instead. */
    const size_t table_offset = UINT32_C(0x000B1BDE) -
                                R1_MODEL_DATA_STOCK_BASE;
    const uint8_t *table = (const uint8_t *)r1_model_data_words +
                           table_offset;
    const bool updated = gomore_primitives_sleep_stage_stream_update(
        (gomore_primitives_sleep_stage_stream_state *)(uintptr_t)state_address,
        *(const volatile uint32_t *)(uintptr_t)timestamp_address,
        (const gomore_primitives_sleep_stage_peak_input *)(uintptr_t)peaks_address,
        (const uint8_t *)(uintptr_t)activity_address, 27u,
        (const gomore_primitives_sleep_stage_status *)(uintptr_t)status_address,
        (uint8_t *)(uintptr_t)output_address,
        table, sizeof(r1_model_data_words) - table_offset,
        construct_tensor, gomore_primitives_sleep_stage_classify,
        (void *)(const void *)&classifier);
    return updated ? 0u : UINT32_MAX;
}
