#include "r1_gh3x2x_reconstructed_roots.h"

#include "r1_gh3x2x_primitive_adapter.h"
#include "model_data/r1_model_data.h"

#include <limits.h>

static uint32_t root_function_mask(uint8_t offset) {
    return (uint32_t)1u << offset;
}

static bool root_frame_matches(const r1_gh3x2x_algo_frame *frame,
                               uint8_t offset) {
    return frame != NULL && frame->function_offset == offset &&
        frame->function_mask == root_function_mask(offset) &&
        frame->sample_rate_hz != 0u;
}

static bool lifecycle_complete(
    const r1_gh3x2x_root_state_lifecycle *lifecycle) {
    return lifecycle != NULL && lifecycle->initialize != NULL &&
        lifecycle->deinitialize != NULL;
}

static int32_t signed_word(uint32_t word) {
    union {
        uint32_t unsigned_value;
        int32_t signed_value;
    } converted = {.unsigned_value = word};
    return converted.signed_value;
}

static bool root_initialize(void *owner, bool *initialized,
                            const r1_gh3x2x_root_state_lifecycle *lifecycle,
                            const r1_gh3x2x_algo_frame *frame,
                            uint8_t expected_offset) {
    if (owner == NULL || initialized == NULL || *initialized ||
        !lifecycle_complete(lifecycle) ||
        !root_frame_matches(frame, expected_offset) ||
        !lifecycle->initialize(lifecycle->context,
                               frame->sample_rate_hz)) {
        return false;
    }
    *initialized = true;
    return true;
}

static bool root_deinitialize(bool *initialized,
                              const r1_gh3x2x_root_state_lifecycle *lifecycle) {
    if (initialized == NULL || !*initialized ||
        !lifecycle_complete(lifecycle) ||
        !lifecycle->deinitialize(lifecycle->context)) {
        return false;
    }
    *initialized = false;
    return true;
}

static bool hba_initialize(void *opaque,
                           const r1_gh3x2x_algo_frame *frame) {
    r1_gh3x2x_hba_root_context *context = opaque;
    return context != NULL && root_initialize(
        context, &context->initialized, &context->lifecycle, frame,
        R1_GH3X2X_ALGO_FUNCTION_HR);
}

static bool hrv_initialize(void *opaque,
                           const r1_gh3x2x_algo_frame *frame) {
    r1_gh3x2x_hrv_root_context *context = opaque;
    return context != NULL && root_initialize(
        context, &context->initialized, &context->lifecycle, frame,
        R1_GH3X2X_ALGO_FUNCTION_HRV);
}

static bool spo2_initialize(void *opaque,
                            const r1_gh3x2x_algo_frame *frame) {
    r1_gh3x2x_spo2_root_context *context = opaque;
    return context != NULL && root_initialize(
        context, &context->initialized, &context->lifecycle, frame,
        R1_GH3X2X_ALGO_FUNCTION_SPO2);
}

r1_gh3x2x_root_status r1_gh3x2x_format_hba_root_output(
    uint32_t status, const goodix_primitives_hba_process_output *root,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]) {
    if (status != 0u || root == NULL || output == NULL) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    if (root->valid != 1u) {
        return R1_GH3X2X_ROOT_NO_UPDATE;
    }
    const int32_t diagnostic = signed_word(root->reserved);
    if (diagnostic > INT32_MAX / 100 ||
        diagnostic < INT32_MIN / 100) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    output[0] = signed_word(root->selected);
    output[1] = signed_word(root->scaled_score);
    output[2] = diagnostic * 100;
    output[3] = signed_word(root->score_at_least_70);
    output[4] = 0;
    output[5] = 0;
    return R1_GH3X2X_ROOT_UPDATE;
}

static r1_gh3x2x_root_status hba_process(
    void *opaque, const r1_gh3x2x_algo_input *input,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]) {
    r1_gh3x2x_hba_root_context *context = opaque;
    if (context == NULL || !context->initialized || input == NULL ||
        output == NULL) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    r1_gh3x2x_algo_input mutable_input = *input;
    goodix_primitives_hba_process_input primitive_input;
    if (!r1_gh3x2x_algo_bind_hr_primitive_input(
            &mutable_input, context->filter_code,
            context->filter_code_count, &primitive_input)) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    goodix_primitives_hba_process_output primitive_output = {0};
    const uint32_t status = context->runtime != NULL
        ? goodix_primitives_hba_runtime_process(
            context->runtime, &primitive_input, &primitive_output)
        : goodix_primitives_hba_process(
            context->configuration, &primitive_input, &primitive_output,
            context->plan, context->state, context->stream_workspace,
            context->workspace);
    return r1_gh3x2x_format_hba_root_output(
        status, &primitive_output, output);
}

static r1_gh3x2x_root_status hrv_process(
    void *opaque, const r1_gh3x2x_algo_input *input,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]) {
    r1_gh3x2x_hrv_root_context *context = opaque;
    if (context == NULL || !context->initialized || input == NULL ||
        output == NULL) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    r1_gh3x2x_algo_input mutable_input = *input;
    goodix_primitives_hrv_process_input primitive_input;
    return r1_gh3x2x_algo_bind_hrv_primitive_input(
               &mutable_input, &primitive_input) &&
            (context->runtime != NULL
                ? goodix_primitives_hrv_runtime_process(
                    context->runtime, &primitive_input, output)
                : goodix_primitives_hrv_process(
                    &primitive_input, context->plan, context->state,
                    context->workspace, output))
        ? R1_GH3X2X_ROOT_UPDATE : R1_GH3X2X_ROOT_ERROR;
}

static bool spo2_round(uint32_t raw, int32_t *rounded) {
    if (rounded == NULL) {
        return false;
    }
    const float value = (float)signed_word(raw) / 10000.0f;
    if (value >= -0.00001f && value <= 0.00001f) {
        *rounded = 0;
    } else if (value < -0.00001f) {
        *rounded = (int32_t)(value - 0.5f);
    } else {
        *rounded = (int32_t)(value + 0.5f);
    }
    return true;
}

r1_gh3x2x_root_status r1_gh3x2x_format_spo2_root_output(
    int32_t status,
    const uint32_t root_words[R1_GH3X2X_ALGO_RESULT_COUNT],
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]) {
    if ((status != 0 && status != 3 && status != 4) ||
        root_words == NULL || output == NULL) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    if (root_words[12] != 1u) {
        return R1_GH3X2X_ROOT_NO_UPDATE;
    }
    int32_t final_spo2 = 0;
    if (!spo2_round(root_words[0], &final_spo2)) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    output[0] = final_spo2;
    output[1] = signed_word(root_words[11]);
    output[2] = signed_word(root_words[2]);
    output[3] = signed_word(root_words[1]);
    output[4] = signed_word(root_words[4]);
    output[5] = signed_word(root_words[6]);
    return R1_GH3X2X_ROOT_UPDATE;
}

static r1_gh3x2x_root_status spo2_process(
    void *opaque, const r1_gh3x2x_algo_input *input,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]) {
    r1_gh3x2x_spo2_root_context *context = opaque;
    if (context == NULL || !context->initialized || input == NULL ||
        output == NULL) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    r1_gh3x2x_algo_input mutable_input = *input;
    goodix_primitives_spo2_calc_input primitive_input;
    if (!r1_gh3x2x_algo_bind_spo2_primitive_input(
            &mutable_input, &primitive_input)) {
        return R1_GH3X2X_ROOT_ERROR;
    }
    uint32_t primitive_output[R1_GH3X2X_ALGO_RESULT_COUNT] = {0};
    const int32_t status = context->runtime != NULL
        ? goodix_primitives_spo2_runtime_process(
            context->runtime, &primitive_input, primitive_output,
            R1_GH3X2X_ALGO_RESULT_COUNT)
        : goodix_primitives_spo2_calc(
            context->plan, &primitive_input, context->state,
            context->workspace, primitive_output,
            R1_GH3X2X_ALGO_RESULT_COUNT);
    return r1_gh3x2x_format_spo2_root_output(
        status, primitive_output, output);
}

static bool hba_deinitialize(void *opaque) {
    r1_gh3x2x_hba_root_context *context = opaque;
    return context != NULL && root_deinitialize(
        &context->initialized, &context->lifecycle);
}

static bool hrv_deinitialize(void *opaque) {
    r1_gh3x2x_hrv_root_context *context = opaque;
    return context != NULL && root_deinitialize(
        &context->initialized, &context->lifecycle);
}

static bool spo2_deinitialize(void *opaque) {
    r1_gh3x2x_spo2_root_context *context = opaque;
    return context != NULL && root_deinitialize(
        &context->initialized, &context->lifecycle);
}

static bool hba_version(void *opaque, char *destination,
                        size_t destination_size) {
    (void)opaque;
    return goodix_primitives_build_hr_version(
        destination, destination_size);
}

static bool hrv_version(void *opaque, char *destination,
                        size_t destination_size) {
    (void)opaque;
    return goodix_primitives_build_hrv_version(
        destination, destination_size);
}

static bool spo2_version(void *opaque, char *destination,
                         size_t destination_size) {
    const r1_gh3x2x_spo2_root_context *context = opaque;
    if (context == NULL || context->weights_version == NULL) {
        return false;
    }
    return goodix_primitives_build_spo2_version(
        destination, destination_size, context->weights_version);
}

bool r1_gh3x2x_make_hba_root_binding(
    r1_gh3x2x_hba_root_context *context,
    r1_gh3x2x_root_binding *binding) {
    if (context == NULL || binding == NULL || context->initialized ||
        context->configuration == NULL || context->plan == NULL ||
        context->state == NULL || context->stream_workspace == NULL ||
        context->workspace == NULL || context->filter_code == NULL ||
        context->filter_code_count == 0u ||
        !lifecycle_complete(&context->lifecycle)) {
        return false;
    }
    *binding = (r1_gh3x2x_root_binding){
        .context = context,
        .initialize = hba_initialize,
        .process = hba_process,
        .deinitialize = hba_deinitialize,
        .version = hba_version,
    };
    return true;
}

static float reconstructed_hba_float(uint32_t bits) {
    union {
        uint32_t bits;
        float value;
    } converted = {.bits = bits};
    return converted.value;
}

static uint32_t reconstructed_hba_target_base(
    const r1_model_data_view *view) {
#if UINTPTR_MAX <= UINT32_MAX
    return view != NULL ? (uint32_t)(uintptr_t)view->words : 0u;
#else
    return view != NULL ? view->stock_base_address : 0u;
#endif
}

static int32_t reconstructed_hba_primary_operation(
    void *record, uintptr_t first, uintptr_t second, uintptr_t third,
    uintptr_t fourth, uintptr_t fifth) {
    (void)first;
    (void)third;
    (void)fifth;
    quantized_runtime_gomore_executor_graph *graph = record;
    const goodix_primitives_graph_executor_input *input =
        (const goodix_primitives_graph_executor_input *)second;
    float **output_binding = (float **)fourth;
    const quantized_runtime_goodix_executor_plan *plan = graph != NULL
        ? (const quantized_runtime_goodix_executor_plan *)
              graph->operation_context
        : NULL;
    if (graph == NULL || input == NULL || output_binding == NULL ||
            *output_binding == NULL || plan == NULL ||
            input->workspace == NULL || input->tail_input == NULL ||
            input->tail_input_count < 4u ||
            input->workspace_count > SIZE_MAX / sizeof(float)) {
        return 1;
    }
    const quantized_runtime_goodix_executor_io io = {
        .workspace = (uint8_t *)input->workspace,
        .workspace_size = input->workspace_count * sizeof(float),
        .tail_input = (const uint8_t *)input->tail_input,
        .tail_input_size = input->tail_input_count * sizeof(uint32_t),
        .output = (uint8_t *)*output_binding,
        .output_capacity = sizeof(float),
    };
    size_t output_bytes = 0u;
    return quantized_runtime_goodix_executor_execute(
               plan, &io, &output_bytes) && output_bytes == sizeof(float)
        ? 0 : 1;
}

static int32_t reconstructed_hba_secondary_operation(
    void *record, uintptr_t first, uintptr_t second, uintptr_t third,
    uintptr_t fourth, uintptr_t fifth) {
    (void)first;
    (void)third;
    (void)fifth;
    quantized_runtime_goodix_second_graph *graph = record;
    r1_gh3x2x_hba_reconstructed_state *state = graph != NULL
        ? (r1_gh3x2x_hba_reconstructed_state *)graph->operation_context
        : NULL;
    if (state == NULL || second == (uintptr_t)0 || fourth != second) {
        return 1;
    }
    quantized_runtime_goodix_second_executor_io io = {
        .workspace = (uint8_t *)second,
        .workspace_size =
            QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_WORKSPACE_BYTES,
        .temporary = state->graph_6_temporary,
        .temporary_size = sizeof(state->graph_6_temporary),
        .output = (uint8_t *)fourth,
        .output_capacity =
            QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES,
    };
    size_t output_bytes = 0u;
    return quantized_runtime_goodix_second_executor_execute(
               &state->graph_plan_6, &io, &output_bytes) &&
            output_bytes ==
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES
        ? 0 : 1;
}

static uintptr_t reconstructed_hba_graph_0_build(
    void *opaque, const void *primary_binding, uintptr_t encoded_size,
    const void *secondary_binding) {
    r1_gh3x2x_hba_reconstructed_state *state = opaque;
    size_t consumed = 0u;
    uint32_t end = 0u;
    if (state == NULL || state->runtime_bindings == NULL ||
            state->runtime_bindings->quantized == NULL ||
            state->stage_resolver == NULL ||
            state->graph_selector_0_built ||
            primary_binding != r1_goodix_hba_family_0_graph.words ||
            secondary_binding != r1_goodix_hba_mode_0_descriptors.words ||
            encoded_size != UINT32_C(0x4BE4) ||
            !quantized_runtime_gomore_executor_graph_build(
                state->runtime_bindings->quantized,
                &state->graph_selector_0, 0u,
                r1_goodix_hba_family_0_graph.words,
                r1_goodix_hba_family_0_graph.word_count,
                reconstructed_hba_target_base(
                    &r1_goodix_hba_family_0_graph),
                r1_goodix_hba_mode_0_descriptors.words,
                r1_goodix_hba_mode_0_descriptors.word_count,
                reconstructed_hba_target_base(
                    &r1_goodix_hba_mode_0_descriptors),
                r1_goodix_hba_tail_schema,
                state->allocate, state->release, state->provider_context,
                &consumed, &end) ||
            consumed != r1_goodix_hba_family_0_graph.word_count ||
            end != reconstructed_hba_target_base(
                       &r1_goodix_hba_family_0_graph) +
                (uint32_t)(consumed * sizeof(uint32_t))) {
        return (uintptr_t)0;
    }
    if (!quantized_runtime_gomore_executor_plan_build(
            &state->graph_selector_0, &state->graph_plan_0,
            state->stage_resolver, state->stage_resolver_context)) {
        quantized_runtime_gomore_executor_graph_destroy(
            &state->graph_selector_0, state->release,
            state->provider_context);
        return (uintptr_t)0;
    }
    state->graph_selector_0.operation_context = &state->graph_plan_0;
    state->graph_selector_0_built = true;
    return (uintptr_t)state->graph_selector_0.bytes;
}

static uintptr_t reconstructed_hba_graph_1_build(
    void *opaque, const void *primary_binding, uintptr_t encoded_size,
    const void *secondary_binding) {
    r1_gh3x2x_hba_reconstructed_state *state = opaque;
    size_t consumed = 0u;
    uint32_t end = 0u;
    if (state == NULL || state->runtime_bindings == NULL ||
            state->runtime_bindings->quantized == NULL ||
            state->stage_resolver == NULL ||
            state->graph_selector_1_built || encoded_size != (uintptr_t)0 ||
            secondary_binding != NULL ||
            primary_binding != r1_goodix_hba_family_1_graph.words ||
            !quantized_runtime_gomore_executor_graph_build(
                state->runtime_bindings->quantized,
                &state->graph_selector_1, 1u,
                r1_goodix_hba_family_1_graph.words,
                r1_goodix_hba_family_1_graph.word_count,
                reconstructed_hba_target_base(
                    &r1_goodix_hba_family_1_graph),
                NULL, 0u, 0u,
                r1_goodix_hba_tail_schema +
                    R1_GOODIX_HBA_TAIL_SCHEMA_BYTES_PER_MODE,
                state->allocate, state->release, state->provider_context,
                &consumed, &end) ||
            consumed != r1_goodix_hba_family_1_graph.word_count ||
            end != reconstructed_hba_target_base(
                       &r1_goodix_hba_family_1_graph) +
                (uint32_t)(consumed * sizeof(uint32_t))) {
        return (uintptr_t)0;
    }
    if (!quantized_runtime_gomore_executor_plan_build(
            &state->graph_selector_1, &state->graph_plan_1,
            state->stage_resolver, state->stage_resolver_context)) {
        quantized_runtime_gomore_executor_graph_destroy(
            &state->graph_selector_1, state->release,
            state->provider_context);
        return (uintptr_t)0;
    }
    state->graph_selector_1.operation_context = &state->graph_plan_1;
    state->graph_selector_1_built = true;
    return (uintptr_t)state->graph_selector_1.bytes;
}

static uintptr_t reconstructed_hba_graph_6_build(
    void *opaque, const void *primary_binding, uintptr_t encoded_size,
    const void *secondary_binding) {
    r1_gh3x2x_hba_reconstructed_state *state = opaque;
    size_t consumed = 0u;
    uint32_t end = 0u;
    if (state == NULL || state->runtime_bindings == NULL ||
            state->runtime_bindings->quantized == NULL ||
            state->stage_resolver == NULL ||
            state->multi_stage_resolver == NULL ||
            state->graph_selector_6_built || encoded_size != (uintptr_t)0 ||
            secondary_binding != NULL ||
            primary_binding != r1_goodix_hba_second_graph.words ||
            !quantized_runtime_goodix_second_graph_build(
                state->runtime_bindings->quantized,
                &state->graph_selector_6,
                r1_goodix_hba_second_graph.words,
                r1_goodix_hba_second_graph.word_count,
                reconstructed_hba_target_base(
                    &r1_goodix_hba_second_graph),
                goodix_primitives_quantized_concatenate_vector(),
                &consumed, &end) ||
            consumed != r1_goodix_hba_second_graph.word_count ||
            end != reconstructed_hba_target_base(
                       &r1_goodix_hba_second_graph) +
                (uint32_t)(consumed * sizeof(uint32_t))) {
        return (uintptr_t)0;
    }
    if (!quantized_runtime_goodix_second_executor_plan_build(
            state->runtime_bindings->quantized,
            &state->graph_selector_6, &state->graph_plan_6,
            state->stage_resolver, state->stage_resolver_context,
            state->multi_stage_resolver,
            state->multi_stage_resolver_context)) {
        state->graph_selector_6 =
            (quantized_runtime_goodix_second_graph){0};
        return (uintptr_t)0;
    }
    state->graph_selector_6.operation_context = state;
    state->graph_selector_6_built = true;
    return (uintptr_t)&state->graph_selector_6;
}

static void reconstructed_hba_graph_release(
    void *opaque, uintptr_t graph) {
    r1_gh3x2x_hba_reconstructed_state *state = opaque;
    if (state == NULL || graph == (uintptr_t)0) {
        return;
    }
    if (graph == (uintptr_t)state->graph_selector_0.bytes) {
        quantized_runtime_gomore_executor_graph_destroy(
            &state->graph_selector_0, state->release,
            state->provider_context);
        state->graph_selector_0_built = false;
        state->graph_plan_0 = (quantized_runtime_goodix_executor_plan){0};
    } else if (graph == (uintptr_t)state->graph_selector_1.bytes) {
        quantized_runtime_gomore_executor_graph_destroy(
            &state->graph_selector_1, state->release,
            state->provider_context);
        state->graph_selector_1_built = false;
        state->graph_plan_1 = (quantized_runtime_goodix_executor_plan){0};
    } else if (graph == (uintptr_t)&state->graph_selector_6) {
        state->graph_selector_6 = (quantized_runtime_goodix_second_graph){0};
        state->graph_plan_6 =
            (quantized_runtime_goodix_second_executor_plan){0};
        state->graph_selector_6_built = false;
    }
}

static bool reconstructed_hba_initialize(void *opaque,
                                         uint16_t sample_rate_hz) {
    r1_gh3x2x_hba_reconstructed_state *state = opaque;
    if (state == NULL || state->configuration == NULL ||
            state->runtime_bindings == NULL || state->allocate == NULL ||
            state->release == NULL ||
            state->context_owner.primary != NULL ||
            state->context_owner.secondary != NULL || state->runtime.bound) {
        return false;
    }
    if (state->stage_resolver == NULL) {
        state->stage_resolver =
            quantized_runtime_source_stage_token_resolve;
        state->stage_resolver_context = NULL;
    }
    if (state->multi_stage_resolver == NULL) {
        state->multi_stage_resolver =
            quantized_runtime_source_multi_stage_token_resolve;
        state->multi_stage_resolver_context = NULL;
    }
    goodix_primitives_hr_configuration configuration =
        *state->configuration;
    configuration.sample_rate = sample_rate_hz;
    for (size_t index = 0u; index < 20u; ++index) {
        state->filter_coefficients[index] = reconstructed_hba_float(
            r1_goodix_hba_filter_coefficients.words[index]);
    }
    const goodix_primitives_tables tables = {
        .table_9d640 = r1_goodix_hba_family_1_graph.words,
        .table_a04cc = r1_goodix_hba_mode_0_descriptors.words,
        .table_a50b0 = r1_goodix_hba_second_graph.words,
        .table_a692c = r1_goodix_hba_family_0_graph.words,
    };
    state->graph_bindings = (goodix_primitives_hr_graph_bindings){
        .selector_0 = {
            reconstructed_hba_graph_0_build,
            reconstructed_hba_graph_release, state,
        },
        .selector_1 = {
            reconstructed_hba_graph_1_build,
            reconstructed_hba_graph_release, state,
        },
        .selector_6 = {
            reconstructed_hba_graph_6_build,
            reconstructed_hba_graph_release, state,
        },
    };
    if (goodix_primitives_hr_primary_context_create(
            &state->context_owner, &configuration, sizeof(configuration),
            "pv_v1.1.0", &tables, state->filter_coefficients,
            &state->graph_bindings, state->allocate, state->release,
            state->provider_context) != GOODIX_PRIMITIVES_HR_OK) {
        return false;
    }
    for (size_t index = 0u; index < GOODIX_PRIMITIVES_STATE_COUNT; ++index) {
        state->operations[index] = NULL;
    }
    state->operations[0] = reconstructed_hba_primary_operation;
    state->operations[1] = reconstructed_hba_primary_operation;
    state->operations[6] = reconstructed_hba_secondary_operation;
    const goodix_primitives_hba_runtime_bindings runtime_bindings = {
        .integrity_transform = state->runtime_bindings->integrity_transform,
        .quantized = state->runtime_bindings->quantized,
        .operations = state->operations,
        .elapsed_state = state->runtime_bindings->elapsed_state,
        .mode_buffers = state->runtime_bindings->mode_buffers,
        .exponential = state->runtime_bindings->exponential,
        .logarithm_base_10 = state->runtime_bindings->logarithm_base_10,
        .square_root = state->runtime_bindings->square_root,
    };
    if (!goodix_primitives_hba_runtime_bind(
            &state->context_owner, &runtime_bindings,
            &state->runtime)) {
        (void)goodix_primitives_hr_primary_context_release(
            &state->context_owner, state->release,
            state->provider_context);
        return false;
    }
    return true;
}

static bool reconstructed_hba_deinitialize(void *opaque) {
    r1_gh3x2x_hba_reconstructed_state *state = opaque;
    if (state == NULL || state->release == NULL ||
            state->context_owner.primary == NULL ||
            state->context_owner.secondary == NULL ||
            !state->runtime.bound ||
            !goodix_primitives_hba_runtime_unbind(&state->runtime)) {
        return false;
    }
    return goodix_primitives_hr_primary_context_release(
        &state->context_owner, state->release, state->provider_context);
}

bool r1_gh3x2x_make_reconstructed_hba_root_binding(
    r1_gh3x2x_hba_root_context *context,
    r1_gh3x2x_hba_reconstructed_state *state,
    r1_gh3x2x_root_binding *binding) {
    if (context == NULL || state == NULL || binding == NULL ||
            context->initialized || state->configuration == NULL ||
            state->runtime_bindings == NULL || state->allocate == NULL ||
            state->release == NULL ||
            state->context_owner.primary != NULL ||
            state->context_owner.secondary != NULL || state->runtime.bound) {
        return false;
    }
    context->configuration = &state->runtime.configuration;
    context->plan = &state->runtime.plan;
    context->state = &state->runtime.state;
    context->stream_workspace = &state->runtime.stream_workspace;
    context->workspace = &state->runtime.workspace;
    context->runtime = &state->runtime;
    context->lifecycle = (r1_gh3x2x_root_state_lifecycle){
        .context = state,
        .initialize = reconstructed_hba_initialize,
        .deinitialize = reconstructed_hba_deinitialize,
    };
    return r1_gh3x2x_make_hba_root_binding(context, binding);
}

bool r1_gh3x2x_make_hrv_root_binding(
    r1_gh3x2x_hrv_root_context *context,
    r1_gh3x2x_root_binding *binding) {
    if (context == NULL || binding == NULL || context->initialized ||
        context->plan == NULL || context->state == NULL ||
        context->workspace == NULL ||
        !lifecycle_complete(&context->lifecycle)) {
        return false;
    }
    *binding = (r1_gh3x2x_root_binding){
        .context = context,
        .initialize = hrv_initialize,
        .process = hrv_process,
        .deinitialize = hrv_deinitialize,
        .version = hrv_version,
    };
    return true;
}

static bool reconstructed_hrv_initialize(void *opaque,
                                         uint16_t sample_rate_hz) {
    r1_gh3x2x_hrv_reconstructed_state *state = opaque;
    if (state == NULL || state->configuration == NULL ||
            state->allocate == NULL || state->release == NULL ||
            state->square_root == NULL || state->context != NULL ||
            state->runtime.bound) {
        return false;
    }
    if (goodix_primitives_hrv_initialize_for_sample_count(
            &state->context, state->configuration, sample_rate_hz,
            state->allocate, state->release, state->provider_context) !=
            GOODIX_PRIMITIVES_HRV_OK) {
        return false;
    }
    if (!goodix_primitives_hrv_runtime_bind(
            state->context, state->square_root, &state->runtime)) {
        (void)goodix_primitives_hrv_context_destroy(
            &state->context, state->release, state->provider_context);
        return false;
    }
    return true;
}

static bool reconstructed_hrv_deinitialize(void *opaque) {
    r1_gh3x2x_hrv_reconstructed_state *state = opaque;
    if (state == NULL || state->release == NULL || state->context == NULL ||
            !state->runtime.bound ||
            !goodix_primitives_hrv_context_destroy(
                &state->context, state->release,
                state->provider_context)) {
        return false;
    }
    state->runtime = (goodix_primitives_hrv_runtime){0};
    return true;
}

bool r1_gh3x2x_make_reconstructed_hrv_root_binding(
    r1_gh3x2x_hrv_root_context *context,
    r1_gh3x2x_hrv_reconstructed_state *state,
    r1_gh3x2x_root_binding *binding) {
    if (context == NULL || state == NULL || binding == NULL ||
            context->initialized || state->configuration == NULL ||
            state->allocate == NULL || state->release == NULL ||
            state->square_root == NULL || state->context != NULL ||
            state->runtime.bound) {
        return false;
    }
    *context = (r1_gh3x2x_hrv_root_context){
        .plan = &state->runtime.plan,
        .state = &state->runtime.state,
        .workspace = &state->runtime.workspace,
        .runtime = &state->runtime,
        .lifecycle = {
            .context = state,
            .initialize = reconstructed_hrv_initialize,
            .deinitialize = reconstructed_hrv_deinitialize,
        },
    };
    return r1_gh3x2x_make_hrv_root_binding(context, binding);
}

bool r1_gh3x2x_make_spo2_root_binding(
    r1_gh3x2x_spo2_root_context *context,
    r1_gh3x2x_root_binding *binding) {
    if (context == NULL || binding == NULL || context->initialized ||
        context->plan == NULL || context->state == NULL ||
        context->workspace == NULL || context->weights_version == NULL ||
        !lifecycle_complete(&context->lifecycle)) {
        return false;
    }
    *binding = (r1_gh3x2x_root_binding){
        .context = context,
        .initialize = spo2_initialize,
        .process = spo2_process,
        .deinitialize = spo2_deinitialize,
        .version = spo2_version,
    };
    return true;
}

static bool reconstructed_spo2_initialize(void *opaque,
                                          uint16_t sample_rate_hz) {
    r1_gh3x2x_spo2_reconstructed_state *state = opaque;
    if (state == NULL || sample_rate_hz != UINT16_C(25) ||
        (state->bindings.execute == NULL &&
         (state->bindings.power == NULL ||
          state->bindings.square_root == NULL ||
          state->bindings.floor == NULL ||
          state->bindings.exponential == NULL ||
          state->bindings.arc_tangent == NULL ||
          state->bindings.double_exponential == NULL)) ||
            state->bindings.quantized == NULL ||
            state->bindings.allocate == NULL ||
            state->bindings.release == NULL || state->runtime.bound ||
            state->runtime.session != NULL) {
        return false;
    }
    return goodix_primitives_spo2_runtime_bind(
        &state->bindings, &state->runtime);
}

static bool reconstructed_spo2_deinitialize(void *opaque) {
    r1_gh3x2x_spo2_reconstructed_state *state = opaque;
    return state != NULL &&
        goodix_primitives_spo2_runtime_unbind(&state->runtime);
}

bool r1_gh3x2x_make_reconstructed_spo2_root_binding(
    r1_gh3x2x_spo2_root_context *context,
    r1_gh3x2x_spo2_reconstructed_state *state,
    r1_gh3x2x_root_binding *binding) {
    if (context == NULL || state == NULL || binding == NULL ||
            context->initialized ||
        (state->bindings.execute == NULL &&
         (state->bindings.power == NULL ||
          state->bindings.square_root == NULL ||
          state->bindings.floor == NULL ||
          state->bindings.exponential == NULL ||
          state->bindings.arc_tangent == NULL ||
          state->bindings.double_exponential == NULL)) ||
            state->bindings.quantized == NULL ||
            state->bindings.allocate == NULL ||
            state->bindings.release == NULL || state->weights_version == NULL ||
            state->runtime.bound || state->runtime.session != NULL) {
        return false;
    }
    *context = (r1_gh3x2x_spo2_root_context){
        .plan = &state->runtime.plan,
        .state = &state->runtime.state,
        .workspace = &state->runtime.workspace,
        .runtime = &state->runtime,
        .weights_version = state->weights_version,
        .lifecycle = {
            .context = state,
            .initialize = reconstructed_spo2_initialize,
            .deinitialize = reconstructed_spo2_deinitialize,
        },
    };
    return r1_gh3x2x_make_spo2_root_binding(context, binding);
}
