#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "goodix_primitives/goodix_primitives.h"

static unsigned dispatch_calls;
static unsigned hook_calls;
static unsigned release_calls;
static unsigned tensor_pipeline_calls;
static goodix_primitives_tensor_descriptor tensor_pipeline_inputs[3];
static goodix_primitives_tensor_descriptor tensor_pipeline_outputs[3];
static uintptr_t tensor_pipeline_input_aux[3];
static uintptr_t tensor_pipeline_output_aux[3];
static size_t nadt_subgraph_calls;
static goodix_primitives_tensor_descriptor nadt_subgraph_inputs[19];
static goodix_primitives_tensor_descriptor nadt_subgraph_second_inputs[19];
static goodix_primitives_tensor_descriptor nadt_subgraph_outputs[19];
static uintptr_t nadt_subgraph_input_aux[19];
static uintptr_t nadt_subgraph_output_aux[19];

typedef struct {
    const char *format;
    int32_t values[3];
    size_t value_count;
} spo2_diagnostic_event;

typedef struct {
    spo2_diagnostic_event events[32];
    size_t count;
} spo2_diagnostic_trace;

typedef struct {
    uint32_t calls;
} spo2_memory_trace;

static void record_spo2_diagnostic(
    void *context, const char *format, const int32_t *values,
    size_t value_count) {
    spo2_diagnostic_trace *trace = context;
    assert(trace != NULL && format != NULL && value_count <= 3u &&
           trace->count < 32u &&
           (value_count == 0u || values != NULL));
    spo2_diagnostic_event *event = &trace->events[trace->count++];
    event->format = format;
    event->value_count = value_count;
    for (size_t index = 0u; index < value_count; ++index) {
        event->values[index] = values[index];
    }
}

static uint32_t next_spo2_available_memory(void *context) {
    spo2_memory_trace *trace = context;
    assert(trace != NULL);
    ++trace->calls;
    return UINT32_C(1000) + trace->calls;
}

typedef struct {
    float *workspace;
    float *recurrent_state;
    size_t subgraph_calls;
    size_t stage_calls;
    size_t fail_stage;
    bool expect_zero_state;
} nadt_generated_graph_fixture;

typedef struct {
    nadt_generated_graph_fixture *fixture;
    size_t index;
} nadt_generated_graph_callback_context;

static bool nadt_generated_subgraph(
    void *context, float *workspace, size_t workspace_count) {
    nadt_generated_graph_callback_context *callback_context = context;
    assert(callback_context != NULL && callback_context->fixture != NULL &&
           callback_context->index < 2u &&
           workspace == callback_context->fixture->workspace &&
           workspace_count > GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_BANK);
    if (callback_context->index == 1u) {
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES; ++index) {
            assert(workspace[index] == (float)(1000u + index));
        }
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_PRIMARY_VALUES; ++index) {
        workspace[index] = (float)(
            (callback_context->index == 0u ? 100u : 200u) + index);
    }
    ++callback_context->fixture->subgraph_calls;
    return true;
}

static bool nadt_generated_stage(
    void *context,
    const goodix_primitives_tensor_descriptor *const *inputs,
    size_t input_count,
    goodix_primitives_tensor_descriptor *const *outputs,
    size_t output_count) {
    nadt_generated_graph_callback_context *callback_context = context;
    assert(callback_context != NULL && callback_context->fixture != NULL &&
           callback_context->index < GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT &&
           inputs != NULL && outputs != NULL && output_count == 1u &&
           outputs[0] != NULL);
    nadt_generated_graph_fixture *fixture = callback_context->fixture;
    const size_t stage = callback_context->index;
    static const uint32_t expected_input_rows[] = {
        120u, 5u, 4u, 120u, 123u, 6u, 4u,
    };
    static const uint32_t expected_output_rows[] = {
        5u, 4u, 4u, 123u, 6u, 4u, 2u,
    };
    assert(input_count == (stage == 3u ? 2u : 1u));
    assert(inputs[0] != NULL &&
           inputs[0]->rows == expected_input_rows[stage] &&
           outputs[0]->rows == expected_output_rows[stage]);
    if (stage == 3u) {
        assert(inputs[1] != NULL && inputs[1]->rows == 3u &&
               ((const float *)inputs[1]->data)[0] == 30.0f &&
               ((const float *)inputs[1]->data)[1] == 31.0f &&
               ((const float *)inputs[1]->data)[2] == 32.0f);
    }
    if (stage == 4u) {
        for (size_t index = 0u; index < 6u; ++index) {
            assert(fixture->recurrent_state[index] ==
                   (fixture->expect_zero_state ? 0.0f : 9.0f));
        }
    }
    ++fixture->stage_calls;
    if (fixture->fail_stage == stage) {
        return false;
    }
    float *const destination = outputs[0]->data;
    for (size_t index = 0u; index < outputs[0]->rows; ++index) {
        destination[index] = (float)(10u * (stage + 1u) + index);
    }
    return true;
}

static void tensor_pipeline_stage(
    void *context, goodix_primitives_tensor_binding *input,
    goodix_primitives_tensor_binding *output) {
    const size_t stage = (size_t)(uintptr_t)context;
    assert(stage < 3u && input != NULL && output != NULL &&
           input->descriptor != NULL && output->descriptor != NULL);
    tensor_pipeline_inputs[stage] = *input->descriptor;
    tensor_pipeline_outputs[stage] = *output->descriptor;
    tensor_pipeline_input_aux[stage] = input->auxiliary;
    tensor_pipeline_output_aux[stage] = output->auxiliary;
    ++tensor_pipeline_calls;
}

static void nadt_subgraph_operator(
    void *context, goodix_primitives_tensor_binding *input,
    goodix_primitives_tensor_binding *output) {
    const size_t stage = (size_t)(uintptr_t)context;
    assert(stage < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT &&
           stage == nadt_subgraph_calls && input != NULL &&
           input[0].descriptor != NULL && output != NULL &&
           output->descriptor != NULL);
    nadt_subgraph_inputs[stage] = *input[0].descriptor;
    if (input[1].descriptor != NULL) {
        nadt_subgraph_second_inputs[stage] = *input[1].descriptor;
    } else {
        nadt_subgraph_second_inputs[stage] =
            (goodix_primitives_tensor_descriptor) {0};
    }
    nadt_subgraph_outputs[stage] = *output->descriptor;
    nadt_subgraph_input_aux[stage] = input[0].auxiliary;
    nadt_subgraph_output_aux[stage] = output->auxiliary;
    if (stage == 0u) {
        goodix_primitives_tensor_descriptor *const auxiliary =
            (goodix_primitives_tensor_descriptor *)output->auxiliary;
        assert(auxiliary != NULL && auxiliary->data != NULL);
        (void)goodix_primitives_tensor_descriptor_initialize(
            auxiliary, 1u, 1u, 2u, 4u, auxiliary->data);
    } else if (stage == 1u) {
        const goodix_primitives_tensor_descriptor *const auxiliary =
            (const goodix_primitives_tensor_descriptor *)input[0].auxiliary;
        assert(auxiliary != NULL && auxiliary->data != NULL &&
               input[1].descriptor != NULL &&
               *(const uint32_t *)input[1].descriptor->data == 2000u);
        const float *const range = auxiliary->data;
        assert(range[0] == -2.0f && range[1] == 3.0f);
    } else if (stage == 18u) {
        const goodix_primitives_tensor_descriptor *const branch =
            (const goodix_primitives_tensor_descriptor *)input[0].auxiliary;
        assert(branch != NULL && branch->rows == 8u &&
               branch->columns == 15u && branch->element_bytes == 4u);
        float *const values = output->descriptor->data;
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OUTPUT_VALUES;
                ++index) {
            values[index] = (float)(3000u + index);
        }
    }
    ++nadt_subgraph_calls;
}

typedef struct {
    int32_t command_result;
    int32_t status_result;
    uint32_t clock_value;
    uint32_t clock_step;
    uint32_t command;
    uint32_t status_reads;
} command_poll_fixture;

typedef struct {
    void *allocations[32];
    size_t count;
} release_order_fixture;

typedef struct {
    uint8_t selector;
    uint8_t payload[2];
    uint32_t payload_length;
    uint32_t first;
    uint32_t second;
    size_t calls;
} payload_send_fixture;

typedef struct {
    uint8_t events[2];
    uint16_t addresses[2];
    uint16_t values[2];
    uint8_t low_bit;
    uint8_t high_bit;
    size_t count;
} register_configuration_fixture;

static uintptr_t indexed_operation_arguments[6];
static int32_t indexed_operation_result = INT32_C(-17);
static int32_t score_operation_result;
static float score_operation_output;
static float score_exponential_argument;
static float *timed_dispatch_output_pointer;
static uintptr_t seven_word_arguments[7];
static uintptr_t five_word_arguments[5];
static int32_t inference_execute_result;
static float inference_execute_output;
static size_t float_transform_input_count;
static size_t float_transform_count;

#define NADT_FIXTURE_CAPACITY 32u

static goodix_primitives_decimated_float_window nadt_float_window(
    float *values) {
    const goodix_primitives_decimated_float_window window = {
        .values = values,
        .count = 0u,
        .capacity = NADT_FIXTURE_CAPACITY,
        .period = 1u,
        .phase = 0u,
        .cursor = 0u,
        .sum = 0.0f,
    };
    return window;
}

static void nadt_rolling_state_initialize(
    goodix_primitives_nadt_rolling_feature_state *state,
    float storage[5][NADT_FIXTURE_CAPACITY]) {
    state->input = nadt_float_window(storage[0]);
    state->smoothed = nadt_float_window(storage[1]);
    state->residual = nadt_float_window(storage[2]);
    state->residual_smoothed = nadt_float_window(storage[3]);
    state->feature_average = nadt_float_window(storage[4]);
}

static void nadt_pair_state_initialize(
    goodix_primitives_nadt_feature_pair_state *state,
    float feature_storage[5][NADT_FIXTURE_CAPACITY],
    float pair_storage[NADT_FIXTURE_CAPACITY]) {
    nadt_rolling_state_initialize(&state->feature, feature_storage);
    state->average_accumulator = 0.0f;
    state->pair_average = nadt_float_window(pair_storage);
}

static void nadt_channel_state_initialize(
    goodix_primitives_nadt_channel_state *state,
    float primary_storage[5][NADT_FIXTURE_CAPACITY],
    float primary_pair_storage[NADT_FIXTURE_CAPACITY],
    float secondary_storage[5][NADT_FIXTURE_CAPACITY],
    float secondary_pair_storage[NADT_FIXTURE_CAPACITY],
    float ratio_storage[3][NADT_FIXTURE_CAPACITY],
    int16_t half_storage[NADT_FIXTURE_CAPACITY]) {
    nadt_pair_state_initialize(
        &state->primary, primary_storage, primary_pair_storage);
    nadt_pair_state_initialize(
        &state->secondary, secondary_storage, secondary_pair_storage);
    state->combined_ratio = nadt_float_window(ratio_storage[0]);
    state->primary_ratio = nadt_float_window(ratio_storage[1]);
    state->secondary_ratio = nadt_float_window(ratio_storage[2]);
    state->half_primary_input =
        (goodix_primitives_decimated_i16_window) {
            .values = half_storage,
            .count = 0u,
            .capacity = NADT_FIXTURE_CAPACITY,
            .cursor = 0u,
            .phase = 0u,
            .period = 1u,
        };
}

static double round_double_away(double value) {
    return value < 0.0 ? (double)(int32_t)(value - 0.5)
                       : (double)(int32_t)(value + 0.5);
}

static int32_t poll_command(uint32_t command, void *context) {
    command_poll_fixture *fixture = context;
    fixture->command = command;
    return fixture->command_result;
}

static int32_t poll_register_read(uint32_t address, uint32_t count,
                                  void *context) {
    command_poll_fixture *fixture = context;
    assert(address == UINT32_C(0xAE) && count == 1u);
    ++fixture->status_reads;
    return fixture->status_result;
}

static uint32_t poll_clock(void *context) {
    command_poll_fixture *fixture = context;
    const uint32_t value = fixture->clock_value;
    fixture->clock_value += fixture->clock_step;
    return value;
}

static void release_in_order(void *context, void *allocation) {
    release_order_fixture *fixture = context;
    assert(allocation != NULL && fixture->count < 32u);
    fixture->allocations[fixture->count++] = allocation;
}

static int32_t indexed_operation(void *record, uintptr_t first,
                                 uintptr_t second, uintptr_t third,
                                 uintptr_t fourth, uintptr_t fifth) {
    indexed_operation_arguments[0] = (uintptr_t)((uint32_t *)record)[0];
    indexed_operation_arguments[1] = first;
    indexed_operation_arguments[2] = second;
    indexed_operation_arguments[3] = third;
    indexed_operation_arguments[4] = fourth;
    indexed_operation_arguments[5] = fifth;
    return indexed_operation_result;
}

static int32_t score_operation(void *record, uintptr_t first,
                               uintptr_t second, uintptr_t third,
                               uintptr_t fourth, uintptr_t fifth) {
    goodix_primitives_spo2_score_context *context =
        (goodix_primitives_spo2_score_context *)second;
    assert(record != NULL && ((uint32_t *)record)[0] == 0u &&
           first == UINT32_C(0x64) && third == UINT32_C(0x68) &&
           fourth != (uintptr_t)0 && fifth == (uintptr_t)0 &&
           context != NULL && context->recent_inputs[0] == UINT32_C(0x40F00000) &&
           context->recent_inputs[1] == UINT32_C(0x3F800000) &&
           context->recent_inputs[2] == UINT32_C(22) &&
           context->recent_inputs[3] == UINT32_C(33) &&
           context->workspace[99] == context->workspace[0] &&
           context->workspace[197] == context->workspace[98]);
    float **const output_binding = (float **)fourth;
    assert(*output_binding != NULL);
    **output_binding = score_operation_output;
    return score_operation_result;
}

static float score_exponential(float value) {
    score_exponential_argument = value;
    return 1.0f;
}

static int32_t timed_indexed_operation(void *record, uintptr_t first,
                                       uintptr_t second, uintptr_t third,
                                       uintptr_t fourth, uintptr_t fifth) {
    const int32_t result = indexed_operation(
        record, first, second, third, fourth, fifth);
    timed_dispatch_output_pointer = *(float **)fourth;
    return result;
}

static int32_t seven_word_operation(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth, uintptr_t sixth, uintptr_t seventh) {
    seven_word_arguments[0] = first;
    seven_word_arguments[1] = second;
    seven_word_arguments[2] = third;
    seven_word_arguments[3] = fourth;
    seven_word_arguments[4] = fifth;
    seven_word_arguments[5] = sixth;
    seven_word_arguments[6] = seventh;
    return INT32_C(-23);
}

static int32_t inference_execute(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth, uintptr_t sixth, uintptr_t seventh) {
    const uintptr_t *const workspace = (const uintptr_t *)third;
    const uintptr_t *const output_binding = (const uintptr_t *)fifth;
    assert(first == UINT32_C(0x1C) && second == UINT32_C(0x14) &&
           fourth == UINT32_C(0x18) && sixth == (uintptr_t)0 &&
           seventh == UINT32_C(7) && workspace != NULL &&
           output_binding != NULL && workspace[0] != (uintptr_t)0 &&
           workspace[1] != (uintptr_t)0 && workspace[2] == output_binding[0] &&
           workspace[3] == (uintptr_t)0 && output_binding[1] == (uintptr_t)0);
    const float *const primary = (const float *)workspace[0];
    const float *const normalized = (const float *)workspace[1];
    assert(primary[0] == 2.0f && primary[1] == 3.0f &&
           normalized[0] == 0.5f && normalized[1] == 1.0f &&
           normalized[2] == 1.0f);
    *(float *)output_binding[0] = inference_execute_output;
    return inference_execute_result;
}

static int32_t five_word_operation(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth) {
    five_word_arguments[0] = first;
    five_word_arguments[1] = second;
    five_word_arguments[2] = third;
    five_word_arguments[3] = fourth;
    five_word_arguments[4] = fifth;
    return INT32_C(-29);
}

static void float_transform_fixture(
    float *values, size_t input_count, size_t transform_count) {
    float_transform_input_count = input_count;
    float_transform_count = transform_count;
    for (size_t index = input_count; index < transform_count; ++index) {
        values[index] = 0.0f;
    }
    for (size_t index = 0u; index < transform_count; ++index) {
        values[index] += (float)(index + 1u);
    }
}

static void capture_payload_send(uint8_t selector, const uint8_t *payload,
                                 uint32_t payload_length, uint32_t first,
                                 uint32_t second, void *context) {
    payload_send_fixture *fixture = context;
    assert(payload != NULL && payload_length == 2u);
    fixture->selector = selector;
    fixture->payload[0] = payload[0];
    fixture->payload[1] = payload[1];
    fixture->payload_length = payload_length;
    fixture->first = first;
    fixture->second = second;
    ++fixture->calls;
}

static void capture_register_write(uint16_t address, uint16_t value,
                                   void *context) {
    register_configuration_fixture *fixture = context;
    assert(fixture->count < 2u);
    fixture->events[fixture->count] = 1u;
    fixture->addresses[fixture->count] = address;
    fixture->values[fixture->count] = value;
    ++fixture->count;
}

static void capture_bit_field_write(uint16_t address, uint8_t low_bit,
                                    uint8_t high_bit, uint16_t value,
                                    void *context) {
    register_configuration_fixture *fixture = context;
    assert(fixture->count < 2u);
    fixture->events[fixture->count] = 2u;
    fixture->addresses[fixture->count] = address;
    fixture->values[fixture->count] = value;
    fixture->low_bit = low_bit;
    fixture->high_bit = high_bit;
    ++fixture->count;
}

static void state_handler(void *record) {
    uint32_t *words = record;
    ++dispatch_calls;
    words[1] = UINT32_C(0xA55A);
}

static int32_t initialize_device(uint16_t device_id) {
    return device_id == UINT16_C(0x1234) ? 0 : 7;
}

static void hook(void) {
    ++hook_calls;
}

typedef union {
    max_align_t alignment;
    uint8_t bytes[16384];
} aligned_arena;

typedef struct {
    aligned_arena arena;
    size_t used;
    size_t calls;
    size_t fail_after;
} allocation_trace;

typedef struct {
    const void *expected_primary;
    uintptr_t expected_size;
    const void *expected_secondary;
    uintptr_t result;
    size_t build_calls;
    size_t release_calls;
} hr_graph_fixture;

static uintptr_t build_hr_graph(
    void *context, const void *primary_binding, uintptr_t encoded_size,
    const void *secondary_binding) {
    hr_graph_fixture *fixture = context;
    assert(fixture != NULL &&
           primary_binding == fixture->expected_primary &&
           encoded_size == fixture->expected_size &&
           secondary_binding == fixture->expected_secondary);
    ++fixture->build_calls;
    return fixture->result;
}

static void release_hr_graph(void *context, uintptr_t graph) {
    hr_graph_fixture *fixture = context;
    assert(fixture != NULL && graph == fixture->result);
    ++fixture->release_calls;
}

static void *allocate_from_trace(void *context, size_t bytes) {
    allocation_trace *trace = context;
    if (trace->fail_after != 0u && trace->calls >= trace->fail_after) {
        return NULL;
    }
    const size_t alignment = sizeof(max_align_t);
    const size_t start = (trace->used + alignment - 1u) / alignment * alignment;
    if (start > sizeof(trace->arena.bytes) ||
            bytes > sizeof(trace->arena.bytes) - start) {
        return NULL;
    }
    trace->used = start + bytes;
    ++trace->calls;
    return &trace->arena.bytes[start];
}

static void release_to_trace(void *context, void *allocation) {
    allocation_trace *trace = context;
    assert(allocation != NULL);
    ++release_calls;
    ++trace->calls;
}

static void assert_hrv_geometry(uint32_t sample_count,
                                uint32_t expected_mode,
                                uint32_t expected_divisor,
                                uint32_t expected_window_a,
                                uint32_t expected_window_b,
                                uint32_t expected_group_count) {
    allocation_trace trace = {0};
    const goodix_primitives_hrv_configuration configuration = {
        UINT32_C(0xA55A1234), sample_count,
        {10000, -20000, 2500, -5000},
    };
    goodix_primitives_hrv_context *context = NULL;
    assert(goodix_primitives_hrv_context_create(
               &context, &configuration, "pv_v1.1.0",
               allocate_from_trace, release_to_trace, &trace) ==
           GOODIX_PRIMITIVES_HRV_OK);
    assert(context != NULL && context->identity == UINT32_C(0xA55A1234));
    assert(context->sample_count == sample_count);
    assert(context->mode == expected_mode);
    assert(context->divisor == expected_divisor);
    assert(context->window_a == expected_window_a);
    assert(context->window_b == expected_window_b);
    assert(context->group_count == expected_group_count);
    assert(context->scaled_sample_bytes == sample_count * 4u);
    assert(context->sample_count_copy == sample_count);
    assert(context->calibration_e8 == 1.0f);
    assert(context->calibration_ec == -2.0f);
    assert(context->calibration_f4 == 0.25f);
    assert(context->calibration_f0 == -0.5f);
    assert(context->subobject_capacities[0] == 11u);
    assert(context->subobject_capacities[1] == 10u);
    assert(context->subobject_capacities[2] == 10u);
    assert(context->subobject_capacities[3] == 10u);
    assert(context->subobject_capacities[4] == expected_group_count);
    assert(context->subobject_capacities[5] == expected_divisor);
    assert(context->subobject_capacities[6] == expected_window_a);
    assert(context->subobject_capacities[7] == expected_window_b);
    assert(context->subobject_capacities[8] == 4u);
    assert(context->subobject_capacities[9] == 125u);
    assert(context->subobject_capacities[10] ==
           (sample_count % 25u == 0u ? sample_count / 25u : 5u));
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT; ++index) {
        assert(context->subobjects[index] != NULL);
    }
    assert(context->owned_6c != NULL && context->owned_6c->mode == 2u);
    assert(context->owned_70 != NULL);
    assert(context->owned_70->channels == 20u);
    assert(context->owned_70->factor == 7u);
    assert(context->owned_70->quarter_sample_count ==
           (int32_t)(sample_count / 4u));
    assert(context->owned_70->double_sample_count == sample_count * 2u);
    assert(context->owned_70->block_size == 16u);
    assert(context->owned_70->scale_a == 1.0f);
    assert(context->owned_70->scale_b == 1.0f);
    const unsigned releases_before = release_calls;
    assert(goodix_primitives_hrv_context_destroy(
        &context, release_to_trace, &trace));
    assert(context == NULL && release_calls == releases_before + 14u);
}

static float exp_fixture(float value) {
    (void)value;
    return 1.0f;
}

static size_t quality_exp_calls;

static float quality_exp_fixture(float value) {
    static const float results[3] = {0.0f, 1.0f, 3.0f};
    assert(value == value && quality_exp_calls < 3u);
    return results[quality_exp_calls++];
}

static float square_root_fixture(float value) {
    if (value <= 0.0f) {
        return 0.0f;
    }
    float estimate = value > 1.0f ? value : 1.0f;
    for (size_t index = 0u; index < 12u; ++index) {
        estimate = 0.5f * (estimate + value / estimate);
    }
    return estimate;
}

static size_t channel_power_calls;
static double channel_power_bases[2];
static double channel_power_exponents[2];

static double channel_power_fixture(double base, double exponent) {
    assert(channel_power_calls < 2u);
    channel_power_bases[channel_power_calls] = base;
    channel_power_exponents[channel_power_calls] = exponent;
    ++channel_power_calls;
    if (base == 10.0 && exponent == 3.0) {
        return 1000.0;
    }
    if (base == 10.0 && exponent == 9.0) {
        return 1000000000.0;
    }
    assert(base == 2.0 && exponent == 17.0);
    return 131072.0;
}

static float floor_positive_fixture(float value) {
    assert(value >= 0.0f && value <= (float)INT32_MAX);
    return (float)(int32_t)value;
}

typedef struct {
    int32_t expected_peaks[GOODIX_PRIMITIVES_NADT_SPECTRAL_PEAK_CAPACITY];
    size_t calls;
    bool accept;
} nadt_harmonic_fixture;

static bool select_nadt_harmonics_fixture(
    void *context, float bin_width, const int32_t *peak_indices,
    const float *peak_values, size_t peak_count,
    int32_t *candidate_indices, uint8_t *candidate_flags,
    size_t candidate_capacity) {
    nadt_harmonic_fixture *fixture = context;
    assert(fixture != NULL && bin_width == 0.09765625f &&
           peak_indices != NULL && peak_values != NULL &&
           peak_count == GOODIX_PRIMITIVES_NADT_SPECTRAL_PEAK_CAPACITY &&
           candidate_indices != NULL && candidate_flags != NULL &&
           candidate_capacity ==
               GOODIX_PRIMITIVES_NADT_SPECTRAL_OUTPUT_CAPACITY);
    for (size_t index = 0u; index < peak_count; ++index) {
        assert(peak_indices[index] == fixture->expected_peaks[index] &&
               peak_values[index] == 0.0f);
    }
    for (size_t index = 0u; index < candidate_capacity; ++index) {
        candidate_indices[index] = peak_indices[index];
        candidate_flags[index] = (uint8_t)(index + 1u);
    }
    ++fixture->calls;
    return fixture->accept;
}

static double gaussian_exp_arguments[8];
static size_t gaussian_exp_call_count;

static double gaussian_exp_fixture(double value) {
    assert(gaussian_exp_call_count <
           sizeof(gaussian_exp_arguments) / sizeof(gaussian_exp_arguments[0]));
    gaussian_exp_arguments[gaussian_exp_call_count] = value;
    ++gaussian_exp_call_count;
    return 1.0;
}

static double signal_confidence_exp_fixture(double value) {
    assert(value == value);
    return 1.0;
}

typedef struct {
    goodix_primitives_nadt_preprocess_stage calls[32];
    size_t call_count;
    int32_t statuses[GOODIX_PRIMITIVES_NADT_PREPROCESS_STAGE_COUNT];
    float summary_metric;
    float inference_value;
    const void *expected_source;
    uint32_t *expected_output;
} nadt_preprocess_fixture;

static int32_t nadt_preprocess_stage_fixture(
    void *context, goodix_primitives_nadt_preprocess_stage stage,
    goodix_primitives_nadt_preprocess_frame *frame) {
    nadt_preprocess_fixture *fixture = context;
    assert(fixture != NULL && frame != NULL &&
           fixture->call_count <
               sizeof(fixture->calls) / sizeof(fixture->calls[0]) &&
           (size_t)stage < GOODIX_PRIMITIVES_NADT_PREPROCESS_STAGE_COUNT &&
           frame->source == fixture->expected_source &&
           frame->output_words == fixture->expected_output &&
           frame->output_word_count == 16u && frame->state != NULL &&
           frame->workspace != NULL);
    fixture->calls[fixture->call_count++] = stage;
    if (stage == GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_DISPATCH) {
        frame->workspace->summary_metric = fixture->summary_metric;
    } else if (stage == GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE) {
        frame->workspace->inference_values[0] = fixture->inference_value;
    } else if (stage == GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_BUILD) {
        frame->output_words[12] = 1u;
    }
    return fixture->statuses[stage];
}

static float log10_argument;
static size_t log10_call_count;

static float log10_zero_fixture(float value) {
    log10_argument = value;
    ++log10_call_count;
    return 0.0f;
}

static float log10_half_fixture(float value) {
    log10_argument = value;
    ++log10_call_count;
    return 0.5f;
}

static double arc_tangent_fixture(double value) {
    return value;
}

static float round_fixture(float value) {
    return value >= 0.0f ? (float)(int32_t)(value + 0.5f)
                         : (float)(int32_t)(value - 0.5f);
}

static int32_t add_one(int32_t value) {
    return value + 1;
}

typedef struct {
    uint8_t channels[6];
    uint16_t groups[6];
    size_t call_count;
} channel_decode_fixture;

typedef struct {
    goodix_primitives_spo2_report_analysis result;
    size_t call_count;
} report_analyze_fixture;

static void analyze_report_fixture(
    void *context, goodix_primitives_spo2_report_analysis *analysis) {
    report_analyze_fixture *fixture = context;
    assert(fixture != NULL && analysis != NULL);
    *analysis = fixture->result;
    ++fixture->call_count;
}

static void decode_channel_fixture(
    void *context, uint8_t channel, uint16_t group, float destination[2]) {
    channel_decode_fixture *fixture = context;
    assert(fixture != NULL && destination != NULL && fixture->call_count < 6u);
    fixture->channels[fixture->call_count] = channel;
    fixture->groups[fixture->call_count] = group;
    ++fixture->call_count;
    destination[0] = (float)((uint16_t)channel * 10u + group);
    destination[1] = destination[0] + 0.5f;
}

static uint16_t low_half(uint32_t value) {
    return (uint16_t)value;
}

static int32_t initialize_ok(void) {
    return 0;
}

void test_reconstructed_goodix_primitives(void) {
    char version[32];
    memset(version, 'x', sizeof(version));
    assert(goodix_primitives_copy_preprocess_version(version,
                                                     sizeof(version)));
    assert(strcmp(version, "pre_pv_v1.1.0") == 0);
    memset(version, 'x', sizeof(version));
    assert(goodix_primitives_copy_preprocess_version(version, 5u));
    assert(memcmp(version, "pre_", 5u) == 0);
    assert(version[4] == '\0');
    assert(!goodix_primitives_copy_preprocess_version(version, 0u));
    assert(goodix_primitives_copy_process_version(version, sizeof(version)));
    assert(strcmp(version, "pv_v1.1.0") == 0);

    char dsp_version[23];
    assert(goodix_primitives_copy_dsp_version(
        dsp_version, sizeof(dsp_version)));
    assert(strcmp(dsp_version, "dsp_pv_v1.3.0_30234f22") == 0);
    char spo2_version[127];
    assert(goodix_primitives_build_spo2_version(
        spo2_version, sizeof(spo2_version), "gh3x2x-v2.23_7ecd2a"));
    static const char expected_spo2_version[] =
        "GH_SPO2_pre_pv_v2.1.10.0(gh3x2x-v2.23_7ecd2a)_nc_277e89de\n"
        "net_1f1cf98b\n"
        "dsp_pv_v1.3.0_30234f22\n"
        "dlCom_pre2exc_pv_v1.3.0_c00c91c9";
    assert(strcmp(spo2_version, expected_spo2_version) == 0);
    assert(!goodix_primitives_build_spo2_version(
        spo2_version, sizeof(spo2_version) - 1u,
        "gh3x2x-v2.23_7ecd2a"));
    assert(spo2_version[0] == '\0');

    char nadt_version[59];
    assert(goodix_primitives_build_nadt_version(
        nadt_version, sizeof(nadt_version)));
    assert(strcmp(nadt_version,
                  "GH_NADT_pre_pv_v1.0.2.0_nc_548d894d\n"
                  "dsp_pv_v1.3.0_30234f22") == 0);
    assert(!goodix_primitives_build_nadt_version(
        nadt_version, sizeof(nadt_version) - 1u));
    assert(nadt_version[0] == '\0');
    assert(!goodix_primitives_build_nadt_version(
        NULL, sizeof(nadt_version)));

    char hrv_version[32];
    assert(goodix_primitives_build_hrv_version(
        hrv_version, sizeof(hrv_version)));
    assert(strcmp(hrv_version,
                  "GH_HRV_pre_pv_v1.0.1.0_ed953ff3") == 0);
    assert(!goodix_primitives_build_hrv_version(
        hrv_version, sizeof(hrv_version) - 1u));
    assert(!goodix_primitives_build_hrv_version(NULL, sizeof(hrv_version)));

    const goodix_primitives_state_handler_fn handlers[7] = {
        state_handler, state_handler, state_handler, state_handler,
        state_handler, state_handler, state_handler,
    };
    uint32_t state[2] = {3u, 0u};
    assert(goodix_primitives_dispatch_state(state, handlers));
    assert(dispatch_calls == 1u && state[1] == UINT32_C(0xA55A));
    state[0] = 7u;
    assert(!goodix_primitives_dispatch_state(state, handlers));

    uint8_t record[GOODIX_PRIMITIVES_RECORD_BYTES];
    memset(record, UINT8_C(0x5A), sizeof(record));
    assert(goodix_primitives_record_initialize(record, sizeof(record)));
    assert(record[0] == 0u && record[1] == 0u &&
           record[2] == UINT8_C(0x5A));
    for (size_t index = 3u; index < sizeof(record); ++index) {
        assert(record[index] == UINT8_C(0xFF));
    }
    memset(record, UINT8_C(0xA5), sizeof(record));
    record[0] = 0u;
    assert(goodix_primitives_record_initialize_once(record, sizeof(record)));
    assert(record[1] == 1u && record[0x0B] == 1u && record[0x13] == 0u);
    record[0] = 2u;
    record[1] = 9u;
    assert(goodix_primitives_record_initialize_once(record, sizeof(record)));
    assert(record[1] == 9u);

    assert(goodix_primitives_initialize_device(UINT16_C(0x1234),
                                               initialize_device) == 0);
    assert(goodix_primitives_initialize_device(UINT16_C(1),
                                               initialize_device) == -1);
    assert(goodix_primitives_initialize_device(UINT16_C(1), NULL) == -1);

    uint32_t first = 0u;
    uint32_t second = 0u;
    goodix_primitives_select_fixed_pair(false, &first, &second);
    assert(first == UINT32_C(0x00ECCCCD));
    assert(second == UINT32_C(0x00A66666));
    goodix_primitives_select_fixed_pair(true, &first, &second);
    assert(first == UINT32_C(0x00F33333));
    assert(second == UINT32_C(0x00C00000));

    memset(record, UINT8_C(0xA5), sizeof(record));
    assert(goodix_primitives_reset_state_record(record, sizeof(record)));
    assert(record[0] == UINT8_C(0xFF) && record[1] == 0u);
    assert(record[0x0E] == 0u && record[0x0F] == 0u);
    for (size_t index = 0x14u; index < 0x18u; ++index) {
        assert(record[index] == 0u);
    }
    record[5] = 1u;
    record[6] = 2u;
    record[7] = 3u;
    assert(goodix_primitives_clear_state_flags(record, sizeof(record)));
    assert(record[5] == 0u && record[6] == 0u && record[7] == 0u);

    assert(!goodix_primitives_call_hook(NULL));
    assert(goodix_primitives_call_hook(hook));
    assert(hook_calls == 1u);
    assert(goodix_primitives_library_code() == UINT32_C(0x12F9));
    assert(goodix_primitives_constant_four() == 4u);
    assert(goodix_primitives_constant_one_a() == 1u);
    assert(goodix_primitives_constant_one_b() == 1u);

    static const uint32_t table_values[7] = {1u, 2u, 3u, 4u, 5u, 6u, 7u};
    const goodix_primitives_tables tables = {
        &table_values[0], &table_values[1], &table_values[2],
        &table_values[3], &table_values[4], &table_values[5],
        &table_values[6],
    };
    assert(goodix_primitives_table_9d640(&tables) == &table_values[0]);
    assert(goodix_primitives_table_a04cc(&tables) == &table_values[1]);
    assert(goodix_primitives_table_a50b0(&tables) == &table_values[2]);
    assert(goodix_primitives_table_a692c(&tables) == &table_values[3]);
    assert(goodix_primitives_table_ad1ac(&tables) == &table_values[4]);
    assert(goodix_primitives_table_ad13c(&tables) == &table_values[5]);
    assert(goodix_primitives_table_ad160(&tables) == &table_values[6]);
    assert(goodix_primitives_table_9d640(NULL) == NULL);

    allocation_trace allocation = {0};
    goodix_primitives_buffer_record *buffer_record = NULL;
    assert(goodix_primitives_buffer_record_create(
        &buffer_record, allocate_from_trace, &allocation));
    assert(buffer_record != NULL && buffer_record->buffer != NULL);
    assert(allocation.calls == 2u);
    for (size_t index = 0u; index < 0x40u; ++index) {
        assert(buffer_record->buffer[index] == 0u);
    }
    assert(buffer_record->flag_05 == 0u && buffer_record->flag_06 == 0u);

    const int32_t integers[5] = {-8, 7, 7, 4, 9};
    int32_t maximum = 0;
    size_t maximum_index = 0u;
    assert(goodix_primitives_integer_max_index(
        integers, 5u, &maximum, &maximum_index));
    assert(maximum == 9 && maximum_index == 4u);

    char dlcom_version[40];
    assert(goodix_primitives_copy_dlcom_version(
        dlcom_version, sizeof(dlcom_version)));
    assert(strcmp(dlcom_version,
                  "dlCom_pre2exc_pv_v1.3.0_c00c91c9") == 0);
    char hr_version[128];
    static const char expected_hr_version[] =
        "GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1\n"
        "dsp_pv_v1.3.0_30234f22\n"
        "dlCom_pre2exc_pv_v1.3.0_c00c91c9";
    assert(goodix_primitives_build_hr_version(
        hr_version, sizeof(hr_version)));
    assert(strcmp(hr_version, expected_hr_version) == 0);
    assert(!goodix_primitives_build_hr_version(
        hr_version, sizeof(expected_hr_version) - 1u));
    assert(hr_version[0] == '\0');

    uint32_t window_values[3] = {0u, 0u, 0u};
    goodix_primitives_word_window window = {window_values, 0u, 3u};
    assert(goodix_primitives_word_window_push(&window, 1u));
    assert(goodix_primitives_word_window_push(&window, 2u));
    assert(goodix_primitives_word_window_push(&window, 3u));
    assert(goodix_primitives_word_window_push(&window, 4u));
    assert(window.count == 3u && window_values[0] == 2u &&
           window_values[1] == 3u && window_values[2] == 4u);

    /* 0x2F260: UInt32 history plus wrapping lifetime push count. */
    uint32_t counted_values[3] = {0u, 0u, 0u};
    goodix_primitives_counted_word_history counted_history = {
        counted_values, 0u, 3u, UINT32_MAX,
    };
    assert(goodix_primitives_counted_word_history_push(
        &counted_history, 10u));
    assert(counted_history.push_count == 0u);
    assert(goodix_primitives_counted_word_history_push(
        &counted_history, 20u));
    assert(goodix_primitives_counted_word_history_push(
        &counted_history, 30u));
    assert(goodix_primitives_counted_word_history_push(
        &counted_history, 40u));
    assert(counted_history.count == 3u &&
           counted_history.push_count == 3u &&
           counted_values[0] == 20u && counted_values[1] == 30u &&
           counted_values[2] == 40u);
    counted_history.capacity = 0u;
    assert(!goodix_primitives_counted_word_history_push(
        &counted_history, 50u));

    uint32_t hr_raw_values[2] = {0u, 0u};
    uint32_t hr_periodic_values[2] = {0u, 0u};
    uint32_t hr_mean_values[2] = {0u, 0u};
    uint32_t hr_centered_values[2] = {0u, 0u};
    uint32_t hr_weighted_values[2] = {0u, 0u};
    const float hr_mode_zero_coefficients[2] = {3.0f, 4.0f};
    goodix_primitives_hr_weighted_feature_state hr_weighted_state = {
        .input_rate = 100,
        .mode = 0u,
        .midpoint_window = 3,
        .raw_history = {hr_raw_values, 0u, 2u, 0u},
        .periodic_history = {hr_periodic_values, 0u, 2u, 0u},
        .mean_history = {hr_mean_values, 0u, 2u, 0u},
        .centered_history = {hr_centered_values, 0u, 2u, 0u},
        .weighted_history = {hr_weighted_values, 0u, 2u, 0u},
        .mode_coefficients = {hr_mode_zero_coefficients, NULL, NULL, NULL},
        .mode_coefficient_counts = {2u, 0u, 0u, 0u},
    };
    bool hr_weighted_emitted = true;
    const float hr_periodic_samples[4] = {4.0f, 6.0f, 8.0f, 10.0f};
    for (size_t index = 0u; index < 4u; ++index) {
        assert(goodix_primitives_hr_weighted_feature_update(
            &hr_weighted_state, hr_periodic_samples[index],
            &hr_weighted_emitted));
        assert(hr_weighted_emitted == (index == 3u));
    }
    assert(hr_weighted_state.periodic_history.push_count == 4u &&
           hr_periodic_values[0] == UINT32_C(0x41000000) &&
           hr_periodic_values[1] == UINT32_C(0x41200000));
    assert(hr_weighted_state.mean_history.count == 2u &&
           hr_mean_values[0] == UINT32_C(0x40A00000) &&
           hr_mean_values[1] == UINT32_C(0x41100000));
    assert(hr_weighted_state.centered_history.count == 1u &&
           hr_centered_values[0] == UINT32_C(0x40000000));
    assert(hr_weighted_state.weighted_history.count == 1u &&
           hr_weighted_values[0] == UINT32_C(0x40C00000));

    hr_weighted_state.mode_coefficient_counts[0] = 1u;
    assert(!goodix_primitives_hr_weighted_feature_update(
        &hr_weighted_state, 11.0f, &hr_weighted_emitted));
    hr_weighted_state.mode_coefficient_counts[0] = 2u;

    uint32_t hr_resample_raw_values[5] = {
        UINT32_C(0x41200000), UINT32_C(0x41300000),
        UINT32_C(0x41400000), UINT32_C(0x41500000),
        UINT32_C(0x41600000),
    };
    uint32_t hr_resample_periodic_values[4] = {0u, 0u, 0u, 0u};
    goodix_primitives_hr_weighted_feature_state hr_resample_state = {
        .input_rate = 128,
        .raw_history = {hr_resample_raw_values, 5u, 5u, 5u},
        .periodic_history = {
            hr_resample_periodic_values, 0u, 4u, 0u,
        },
        .interpolation_count = 0,
        .interpolation_phase = 0,
        .previous_interpolation_sample = 8.0f,
    };
    bool hr_resampled = true;
    assert(goodix_primitives_hr_interpolate_periodic_sample(
        &hr_resample_state, &hr_resampled));
    assert(!hr_resampled && hr_resample_state.interpolation_count == 1 &&
           hr_resample_state.interpolation_phase == 26 &&
           hr_resample_state.periodic_history.count == 0u &&
           hr_resample_state.previous_interpolation_sample == 8.0f);
    hr_resample_state.raw_history.push_count = 10u;
    assert(goodix_primitives_hr_interpolate_periodic_sample(
        &hr_resample_state, &hr_resampled));
    assert(hr_resampled && hr_resample_state.interpolation_count == 2 &&
           hr_resample_state.interpolation_phase == 1 &&
           hr_resample_state.periodic_history.count == 1u &&
           hr_resample_periodic_values[0] == UINT32_C(0x413D70A4) &&
           hr_resample_state.previous_interpolation_sample == 12.0f);
    hr_resample_raw_values[4] = UINT32_C(0x41A00000);
    hr_resample_state.raw_history.push_count = 128u;
    const int32_t phase_before_boundary =
        hr_resample_state.interpolation_phase;
    assert(goodix_primitives_hr_interpolate_periodic_sample(
        &hr_resample_state, &hr_resampled));
    assert(hr_resampled && hr_resample_state.raw_history.push_count == 0u &&
           hr_resample_state.interpolation_count == 3 &&
           hr_resample_state.interpolation_phase == phase_before_boundary &&
           hr_resample_state.periodic_history.count == 2u &&
           hr_resample_periodic_values[1] == UINT32_C(0x41A00000) &&
           hr_resample_state.previous_interpolation_sample == 20.0f);
    hr_resample_state.input_rate = 24;
    assert(!goodix_primitives_hr_interpolate_periodic_sample(
        &hr_resample_state, &hr_resampled));

    int32_t nadt_direct_values[5] = {
        -129, 111, 222, 333, 444,
    };
    const int32_t nadt_calibration_values[5] = {
        1000000, 0, 1000, 0, -1000000,
    };
    uint8_t nadt_scale_codes[5] = {0u, 0u, 6u, 0u, 3u};
    goodix_primitives_nadt_sample_preparation_state nadt_prepare_state = {
        .previous_sequence = 0u,
        .previous_scale_code = UINT32_C(0xFF),
    };
    goodix_primitives_nadt_sample_preparation_input nadt_prepare_input = {
        .direct_values = nadt_direct_values,
        .direct_value_count = 5u,
        .calibration_values = nadt_calibration_values,
        .calibration_value_count = 5u,
        .scale_codes = nadt_scale_codes,
        .scale_code_count = 5u,
        .sequence = 10u,
        .lane_stride = 2u,
        .conversion_mode = 2u,
        .calibrated = false,
    };
    int32_t nadt_prepared[3] = {0, 0, 0};
    uint16_t nadt_configuration_changed = UINT16_MAX;
    assert(goodix_primitives_nadt_sample_prepare(
        &nadt_prepare_state, &nadt_prepare_input, nadt_prepared,
        &nadt_configuration_changed));
    assert(nadt_configuration_changed == 0u && nadt_prepared[0] == -2 &&
           nadt_prepared[1] == 222 && nadt_prepared[2] == 444);
    nadt_prepare_input.sequence = 11u;
    nadt_scale_codes[0] = 1u;
    assert(goodix_primitives_nadt_sample_prepare(
        &nadt_prepare_state, &nadt_prepare_input, nadt_prepared,
        &nadt_configuration_changed));
    assert(nadt_configuration_changed == 1u);
    nadt_prepare_input.calibrated = true;
    nadt_prepare_input.conversion_mode = 3u;
    nadt_scale_codes[0] = 0u;
    assert(goodix_primitives_nadt_sample_prepare(
        &nadt_prepare_state, &nadt_prepare_input, nadt_prepared,
        &nadt_configuration_changed));
    assert(nadt_prepared[0] == 66264 && nadt_prepared[1] == 8397929 &&
           nadt_prepared[2] == 7456540);
    nadt_scale_codes[4] = 7u;
    assert(!goodix_primitives_nadt_sample_prepare(
        &nadt_prepare_state, &nadt_prepare_input, nadt_prepared,
        &nadt_configuration_changed));
    assert(nadt_prepared[0] == 9000000 && nadt_prepared[1] == 9000000 &&
           nadt_prepared[2] == 9000000);
    nadt_scale_codes[4] = 3u;
    nadt_prepare_input.conversion_mode = 4u;
    assert(!goodix_primitives_nadt_sample_prepare(
        &nadt_prepare_state, &nadt_prepare_input, nadt_prepared,
        &nadt_configuration_changed));

    const goodix_primitives_hr_candidate_record hr_candidates[5] = {
        {.tag = 5u, .position = 50.0f, .value = 70.0f,
         .alternate_tag = 6u, .suppressed = 0u},
        {.tag = 1u, .position = 72.0f, .value = 60.0f,
         .alternate_tag = 9u, .suppressed = 0u},
        {.tag = 4u, .position = 73.0f, .value = 50.0f,
         .alternate_tag = 6u, .suppressed = 0u},
        {.tag = 3u, .position = 74.0f, .value = 10.0f,
         .alternate_tag = 6u, .suppressed = 0u},
        {.tag = 2u, .position = 75.0f, .value = 200.0f,
         .alternate_tag = 6u, .suppressed = 0u},
    };
    goodix_primitives_hr_candidate_selection_state hr_candidate_state = {
        .call_count = UINT32_MAX,
        .position_origin = 100,
        .position_step = 10,
    };
    goodix_primitives_hr_candidate_selection hr_selection;
    assert(goodix_primitives_hr_candidate_window_select(
        &hr_candidate_state, hr_candidates, 5u, 20, 120,
        5, 5, 50.0f, &hr_selection));
    assert(hr_candidate_state.call_count == 0u && hr_selection.count == 4u &&
           hr_selection.values[0] == 60.0f && hr_selection.tags[0] == 9u &&
           hr_selection.values[1] == 50.0f && hr_selection.tags[1] == 4u &&
           hr_selection.values[2] == 25.0f && hr_selection.tags[2] == 8u &&
           hr_selection.values[3] == 150.0f && hr_selection.tags[3] == 8u);
    assert(goodix_primitives_hr_candidate_window_select(
        &hr_candidate_state, hr_candidates, 1u, 20, 120,
        0, 5, 50.0f, &hr_selection));
    assert(hr_selection.count == 1u && hr_selection.values[0] == 70.0f &&
           hr_selection.tags[0] == 7u && hr_selection.values[1] == 0.0f &&
           hr_selection.tags[1] == 0u);
    goodix_primitives_hr_candidate_record suppressed_candidate = {
        .tag = 2u, .position = 75.0f, .value = 80.0f,
        .alternate_tag = 6u, .suppressed = 1u,
    };
    assert(goodix_primitives_hr_candidate_window_select(
        &hr_candidate_state, &suppressed_candidate, 1u, 20, 120,
        0, 5, 50.0f, &hr_selection));
    assert(hr_selection.count == 0u);

    /* 0x30090: three capped running means and explicit timestamp binding. */
    goodix_primitives_running_triplet running_triplet = {
        .count = 0,
        .capacity = 2,
        .mean = {0.0f, 0.0f, 0.0f},
        .timestamp = 0u,
    };
    assert(goodix_primitives_running_triplet_update(
        &running_triplet, 3.0f, 6.0f, 9.0f, 10u));
    assert(running_triplet.count == 1 &&
           running_triplet.mean[0] == 3.0f &&
           running_triplet.mean[1] == 6.0f &&
           running_triplet.mean[2] == 9.0f &&
           running_triplet.timestamp == 10u);
    assert(goodix_primitives_running_triplet_update(
        &running_triplet, 5.0f, 10.0f, 15.0f, 20u));
    assert(running_triplet.count == 2 &&
           running_triplet.mean[0] == 4.0f &&
           running_triplet.mean[1] == 8.0f &&
           running_triplet.mean[2] == 12.0f);
    assert(goodix_primitives_running_triplet_update(
        &running_triplet, 7.0f, 14.0f, 21.0f, 30u));
    assert(running_triplet.count == 2 &&
           running_triplet.mean[0] == 5.5f &&
           running_triplet.mean[1] == 11.0f &&
           running_triplet.mean[2] == 16.5f &&
           running_triplet.timestamp == 30u);
    running_triplet.count = 3;
    assert(!goodix_primitives_running_triplet_update(
        &running_triplet, 1.0f, 1.0f, 1.0f, 40u));

    /* 0x66470/0x66494/0x6652A/0x66560/0x665A0/0x66608:
     * the shared Goodix rolling-buffer family. */
    float rolling_float_values[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    goodix_primitives_decimated_float_window rolling_float = {
        .values = rolling_float_values,
        .count = 4u,
        .capacity = 4u,
        .period = 2u,
        .phase = 0u,
        .cursor = 0u,
        .sum = 10.0f,
    };
    float rolling_mean = 0.0f;
    assert(goodix_primitives_float_window_mean(
        &rolling_float, &rolling_mean));
    assert(rolling_mean == 2.5f);
    float removed = 0.0f;
    assert(goodix_primitives_float_window_remove(
        &rolling_float, 1u, &removed));
    assert(removed == 2.0f && rolling_float.count == 3u &&
           rolling_float.cursor == 3u && rolling_float.sum == 8.0f &&
           rolling_float_values[0] == 1.0f &&
           rolling_float_values[1] == 3.0f &&
           rolling_float_values[2] == 4.0f);
    assert(goodix_primitives_float_window_remove(
        &rolling_float, 0u, &removed));
    assert(removed == 1.0f && rolling_float.count == 2u &&
           rolling_float.cursor == 2u && rolling_float.sum == 7.0f);
    rolling_float.cursor = 0u;
    assert(!goodix_primitives_float_window_remove(
        &rolling_float, 0u, &removed));

    int16_t rolling_i16_values[3] = {0, 0, 0};
    goodix_primitives_i16_window rolling_i16 = {
        .values = rolling_i16_values, .count = 0u, .capacity = 3u,
    };
    assert(goodix_primitives_i16_window_push(&rolling_i16, 1));
    assert(goodix_primitives_i16_window_push(&rolling_i16, 2));
    assert(goodix_primitives_i16_window_push(&rolling_i16, 3));
    assert(goodix_primitives_i16_window_push(&rolling_i16, 4));
    assert(rolling_i16.count == 3u && rolling_i16_values[0] == 2 &&
           rolling_i16_values[1] == 3 && rolling_i16_values[2] == 4);

    uint8_t rolling_byte_values[3] = {0u, 0u, 0u};
    goodix_primitives_byte_window rolling_byte = {
        .values = rolling_byte_values,
        .count = 0u,
        .capacity = 3u,
        .cursor = 0u,
    };
    assert(goodix_primitives_byte_window_push(&rolling_byte, 1u));
    assert(goodix_primitives_byte_window_push(&rolling_byte, 2u));
    assert(goodix_primitives_byte_window_push(&rolling_byte, 3u));
    assert(rolling_byte.cursor == 0u);
    assert(goodix_primitives_byte_window_push(&rolling_byte, 4u));
    assert(rolling_byte.count == 3u && rolling_byte.cursor == 1u &&
           rolling_byte_values[0] == 2u && rolling_byte_values[1] == 3u &&
           rolling_byte_values[2] == 4u);

    int16_t decimated_i16_values[2] = {0, 0};
    goodix_primitives_decimated_i16_window decimated_i16 = {
        .values = decimated_i16_values,
        .count = 0u,
        .capacity = 2u,
        .cursor = 0u,
        .phase = 0u,
        .period = 2u,
    };
    assert(goodix_primitives_decimated_i16_window_push(
        &decimated_i16, 10));
    assert(goodix_primitives_decimated_i16_window_push(
        &decimated_i16, 11));
    assert(goodix_primitives_decimated_i16_window_push(
        &decimated_i16, 12));
    assert(decimated_i16.count == 2u && decimated_i16.cursor == 0u &&
           decimated_i16.phase == 1u && decimated_i16_values[0] == 10 &&
           decimated_i16_values[1] == 12);
    decimated_i16.period = 0u;
    assert(!goodix_primitives_decimated_i16_window_push(
        &decimated_i16, 13));

    float decimated_float_values[2] = {0.0f, 0.0f};
    goodix_primitives_decimated_float_window decimated_float = {
        .values = decimated_float_values,
        .count = 0u,
        .capacity = 2u,
        .period = 2u,
        .phase = 0u,
        .cursor = 0u,
        .sum = 0.0f,
    };
    assert(goodix_primitives_decimated_float_window_push(
        &decimated_float, 1.0f));
    assert(goodix_primitives_decimated_float_window_push(
        &decimated_float, 99.0f));
    assert(goodix_primitives_decimated_float_window_push(
        &decimated_float, 3.0f));
    assert(goodix_primitives_decimated_float_window_push(
        &decimated_float, 99.0f));
    assert(goodix_primitives_decimated_float_window_push(
        &decimated_float, 5.0f));
    assert(decimated_float.count == 2u && decimated_float.cursor == 1u &&
           decimated_float.phase == 1u && decimated_float.sum == 8.0f &&
           decimated_float_values[0] == 3.0f &&
           decimated_float_values[1] == 5.0f);

    /* Numerical post-processing leaves at 0x35F44, 0x36EB4, 0x37DB4,
     * 0x668A4, and 0x66C18. */
    float truncated = 0.0f;
    assert(goodix_primitives_truncate_decimal(1.234567f, 4u,
                                               &truncated));
    assert(truncated > 1.2344f && truncated < 1.2346f);
    assert(goodix_primitives_truncate_decimal(-1.234567f, 4u,
                                               &truncated));
    assert(truncated < -1.2344f && truncated > -1.2346f);
    assert(!goodix_primitives_truncate_decimal(1.0f, 10u, &truncated));
    assert(!goodix_primitives_truncate_decimal(
        2147483648.0f, 0u, &truncated));

    goodix_primitives_word_pair bit_pairs[8];
    for (uint32_t index = 0u; index < 8u; ++index) {
        bit_pairs[index].first = index;
        bit_pairs[index].second = 100u + index;
    }
    assert(goodix_primitives_bit_reverse_permute_pairs(
        bit_pairs, 8u, 3u));
    static const uint32_t bit_reverse_order[8] = {
        0u, 4u, 2u, 6u, 1u, 5u, 3u, 7u,
    };
    for (size_t index = 0u; index < 8u; ++index) {
        assert(bit_pairs[index].first == bit_reverse_order[index]);
        assert(bit_pairs[index].second ==
               100u + bit_reverse_order[index]);
    }
    assert(!goodix_primitives_bit_reverse_permute_pairs(
        bit_pairs, 7u, 3u));

    float complex_fft[GOODIX_PRIMITIVES_FFT_COMPLEX_VALUES];
    for (size_t index = 0u; index < 128u; ++index) {
        complex_fft[index * 2u] = 1.0f;
        complex_fft[index * 2u + 1u] = 0.0f;
    }
    assert(goodix_primitives_fft_complex_128_dif(
        complex_fft, GOODIX_PRIMITIVES_FFT_COMPLEX_VALUES));
    assert(complex_fft[0] == 128.0f && complex_fft[1] == 0.0f);
    for (size_t index = 2u;
            index < GOODIX_PRIMITIVES_FFT_COMPLEX_VALUES; ++index) {
        assert(complex_fft[index] == 0.0f);
    }
    assert(!goodix_primitives_fft_complex_128_dif(complex_fft, 255u));

    float real_fft[GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES] = {0.0f};
    real_fft[0] = 1.0f;
    assert(goodix_primitives_fft_real_magnitude_256(
        real_fft, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES, 1u,
        square_root_fixture));
    assert(real_fft[0] == 0.0f);
    for (size_t index = 1u;
            index < GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES; ++index) {
        assert(real_fft[index] == 1.0f);
    }

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_FFT_REAL_VALUES; ++index) {
        real_fft[index] = (index & 1u) == 0u ? 1.0f : -1.0f;
    }
    assert(goodix_primitives_fft_real_magnitude_256(
        real_fft, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES,
        GOODIX_PRIMITIVES_FFT_REAL_VALUES, square_root_fixture));
    for (size_t index = 0u; index < 128u; ++index) {
        assert(real_fft[index] == 0.0f);
    }
    assert(real_fft[128] == 256.0f);
    assert(!goodix_primitives_fft_real_magnitude_256(
        real_fft, 255u, 1u, square_root_fixture));

    goodix_primitives_warmup_average_state warmup = {
        .first = 9, .second = -1, .third = -1, .average = -1, .phase = 1u,
    };
    assert(goodix_primitives_finalize_warmup_average(&warmup));
    assert(warmup.second == 9 && warmup.third == 9 &&
           warmup.average == 9 && warmup.phase == 4u);
    warmup.first = 9;
    warmup.second = 6;
    warmup.third = -1;
    warmup.average = -1;
    warmup.phase = 2u;
    assert(goodix_primitives_finalize_warmup_average(&warmup));
    assert(warmup.third == 9 && warmup.average == 6 &&
           warmup.phase == 4u);
    warmup.first = 3;
    warmup.second = 6;
    warmup.third = 9;
    warmup.phase = 3u;
    assert(goodix_primitives_finalize_warmup_average(&warmup));
    assert(warmup.average == 6 && warmup.phase == 4u);
    warmup.first = INT32_MAX;
    warmup.second = INT32_MAX;
    warmup.third = INT32_MAX;
    warmup.phase = 3u;
    assert(goodix_primitives_finalize_warmup_average(&warmup));
    assert(warmup.average == INT32_C(715827881));

    float normalized_values[3] = {2.0f, -1.0f, 4.0f};
    assert(goodix_primitives_normalize_by_max(normalized_values, 3u));
    assert(normalized_values[0] == 0.5f &&
           normalized_values[1] == -0.25f &&
           normalized_values[2] == 1.0f);
    float tiny_values[2] = {0x1.0p-21f, -0x1.0p-22f};
    assert(goodix_primitives_normalize_by_max(tiny_values, 2u));
    assert(tiny_values[0] == 0x1.0p-21f &&
           tiny_values[1] == -0x1.0p-22f);
    assert(!goodix_primitives_normalize_by_max(NULL, 0u));

    const float clip_values[5] = {
        -0.04f, -0.01f, 0.0f, 0.01f, 0.04f,
    };
    float clip_output[5] = {0.0f};
    assert(goodix_primitives_nadt_clip_normalize(
        clip_values, 5u, clip_output, 5u));
    assert(clip_output[0] == -1.0f && clip_output[1] == -0.5f &&
           clip_output[2] == 0.0f && clip_output[3] == 0.5f &&
           clip_output[4] == 1.0f);
    const float small_clip_values[3] = {-0.01f, 0.005f, 0.0f};
    assert(goodix_primitives_nadt_clip_normalize(
        small_clip_values, 3u, clip_output, 5u));
    assert(clip_output[0] == -1.0f && clip_output[1] == 0.5f &&
           clip_output[2] == 0.0f);
    const float tiny_clip_values[2] = {0x1.0p-24f, -0x1.0p-25f};
    clip_output[0] = 9.0f;
    clip_output[1] = 9.0f;
    assert(goodix_primitives_nadt_clip_normalize(
        tiny_clip_values, 2u, clip_output, 5u));
    assert(clip_output[0] == 0.0f && clip_output[1] == 0.0f);
    union {
        uint32_t bits;
        float value;
    } clip_nan = {.bits = UINT32_C(0x7FC00000)};
    assert(goodix_primitives_nadt_clip_normalize(
        &clip_nan.value, 1u, clip_output, 5u));
    assert(clip_output[0] == 0.0f);
    const float clip_nan_values[2] = {0.01f, clip_nan.value};
    assert(goodix_primitives_nadt_clip_normalize(
        clip_nan_values, 2u, clip_output, 5u));
    assert(clip_output[0] == 1.0f && clip_output[1] == 1.0f);
    assert(!goodix_primitives_nadt_clip_normalize(
        clip_values, 5u, clip_output, 4u));

    const float inference_primary[3] = {1.0f, 2.0f, 3.0f};
    const float inference_secondary[4] = {0.0f, 0.01f, 0.02f, 0.04f};
    const goodix_primitives_nadt_inference_source inference_source = {
        .primary_values = inference_primary,
        .primary_count = 3u,
        .secondary_values = inference_secondary,
        .secondary_count = 4u,
    };
    const goodix_primitives_nadt_inference_configuration
        inference_configuration = {
            .primary_rows = 1u,
            .primary_columns = 2u,
            .secondary_rows = 1u,
            .secondary_columns = 3u,
            .field_14 = (uintptr_t)UINT32_C(0x14),
            .field_18 = (uintptr_t)UINT32_C(0x18),
            .field_1c = (uintptr_t)UINT32_C(0x1C),
        };
    float inference_primary_scratch[2] = {0.0f, 0.0f};
    float inference_workspace[
        GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS] = {0.0f};
    float inference_output = -9.0f;
    inference_execute_result = 0;
    inference_execute_output = -1.0f;
    assert(goodix_primitives_nadt_inference_bridge(
        &inference_source, &inference_configuration, 7u,
        inference_execute, inference_primary_scratch, 2u,
        inference_workspace,
        GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS,
        &inference_output) == 0);
    assert(inference_output == 0.0f);
    inference_execute_output = 3.0f;
    assert(goodix_primitives_nadt_inference_bridge(
        &inference_source, &inference_configuration, 7u,
        inference_execute, inference_primary_scratch, 2u,
        inference_workspace,
        GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS,
        &inference_output) == 0);
    assert(inference_output == 2.0f);
    inference_execute_result = -1;
    inference_execute_output = 1.0f;
    assert(goodix_primitives_nadt_inference_bridge(
        &inference_source, &inference_configuration, 7u,
        inference_execute, inference_primary_scratch, 2u,
        inference_workspace,
        GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS,
        &inference_output) == 5);
    assert(goodix_primitives_nadt_inference_bridge(
        &inference_source, &inference_configuration, 7u,
        inference_execute, inference_primary_scratch, 1u,
        inference_workspace,
        GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS,
        &inference_output) == 5);

    float phase_values[4] = {0.25f, 0.75f, -1.0f, -9.0f};
    uint16_t phase_indices[4] = {0u, 2u, 1u, UINT16_C(0xAAAA)};
    float phase_dispersion = -1.0f;
    float phase_quality = -1.0f;
    assert(goodix_primitives_nadt_peak_dispersion_quality(
        phase_values, 4u, phase_indices, 4u, 3u, 4u,
        square_root_fixture, &phase_dispersion, &phase_quality));
    assert(phase_values[3] == 1.0f && phase_indices[3] == 3u &&
           phase_dispersion == 0.0f && phase_quality == 100.0f);
    float deviating_phase_values[3] = {0.5f, 1.0f, -9.0f};
    uint16_t deviating_phase_indices[3] = {0u, 1u, UINT16_C(0xAAAA)};
    assert(goodix_primitives_nadt_peak_dispersion_quality(
        deviating_phase_values, 3u, deviating_phase_indices, 3u, 2u, 4u,
        square_root_fixture, &phase_dispersion, &phase_quality));
    assert(deviating_phase_values[2] == 1.0f &&
           deviating_phase_indices[2] == 3u &&
           phase_dispersion > 0.3227f && phase_dispersion < 0.3228f &&
           phase_quality == 50.0f);
    float clamped_phase_values[2] = {2.0f, -9.0f};
    uint16_t clamped_phase_indices[2] = {0u, UINT16_C(0xAAAA)};
    assert(goodix_primitives_nadt_peak_dispersion_quality(
        clamped_phase_values, 2u, clamped_phase_indices, 2u, 1u, 4u,
        square_root_fixture, &phase_dispersion, &phase_quality));
    assert(phase_dispersion > 1.237f && phase_dispersion < 1.238f &&
           phase_quality == 0.0f);
    float skipped_phase_values[3] = {-1.0f, clip_nan.value, -9.0f};
    uint16_t skipped_phase_indices[3] = {0u, 1u, UINT16_C(0xAAAA)};
    assert(goodix_primitives_nadt_peak_dispersion_quality(
        skipped_phase_values, 3u, skipped_phase_indices, 3u, 2u, 4u,
        square_root_fixture, &phase_dispersion, &phase_quality));
    assert(phase_dispersion == 0.0f && phase_quality == 100.0f);
    float rejected_phase_value = -9.0f;
    uint16_t rejected_phase_index = UINT16_C(0xAAAA);
    assert(!goodix_primitives_nadt_peak_dispersion_quality(
        &rejected_phase_value, 1u, &rejected_phase_index, 1u, 1u, 4u,
        square_root_fixture, &phase_dispersion, &phase_quality));
    assert(rejected_phase_value == -9.0f &&
           rejected_phase_index == UINT16_C(0xAAAA));
    assert(!goodix_primitives_nadt_peak_dispersion_quality(
        phase_values, 4u, phase_indices, 4u, 3u, 0u,
        square_root_fixture, &phase_dispersion, &phase_quality));

    gaussian_exp_call_count = 0u;
    float gaussian_probability = -1.0f;
    assert(goodix_primitives_nadt_gaussian_interval_probability(
        0.0f, 1.0f, 0.0f, 1.0f, 0.25f,
        square_root_fixture, gaussian_exp_fixture, &gaussian_probability));
    assert(gaussian_exp_call_count == 4u &&
           gaussian_exp_arguments[0] == -0.03125 &&
           gaussian_exp_arguments[1] == -0.125 &&
           gaussian_exp_arguments[2] == -0.28125 &&
           gaussian_exp_arguments[3] == -0.5 &&
           gaussian_probability > 0.3988f &&
           gaussian_probability < 0.3991f);
    gaussian_exp_call_count = 0u;
    assert(goodix_primitives_nadt_gaussian_interval_probability(
        0.0f, 0.2f, 0.0f, 1.0f, 0.25f,
        square_root_fixture, gaussian_exp_fixture, &gaussian_probability));
    assert(gaussian_exp_call_count == 0u && gaussian_probability == 0.0f);
    assert(goodix_primitives_nadt_gaussian_interval_probability(
        0.0f, 1.0f, 0.0f, 0.0f, 0.25f,
        square_root_fixture, gaussian_exp_fixture, &gaussian_probability));
    assert(gaussian_exp_call_count == 0u && gaussian_probability == 0.0f);
    gaussian_probability = -1.0f;
    assert(!goodix_primitives_nadt_gaussian_interval_probability(
        0.0f, 1.0f, 0.0f, 1.0f, 0.0f,
        square_root_fixture, gaussian_exp_fixture, &gaussian_probability));
    assert(gaussian_probability == -1.0f);

    const int32_t fir_input[4] = {10, 20, 30, 40};
    const float fir_coefficients[3] = {0.25f, 0.5f, 0.25f};
    int32_t fir_output[4] = {0};
    int32_t fir_scratch[6] = {0};
    assert(goodix_primitives_nadt_symmetric_fir_i32(
        fir_input, 4u, fir_coefficients, 3u,
        fir_output, 4u, fir_scratch, 6u));
    assert(fir_scratch[0] == 20 && fir_scratch[1] == 10 &&
           fir_scratch[2] == 20 && fir_scratch[3] == 30 &&
           fir_scratch[4] == 40 && fir_scratch[5] == 30);
    assert(fir_output[0] == 15 && fir_output[1] == 20 &&
           fir_output[2] == 30 && fir_output[3] == 35);
    const float fir_identity[3] = {0.0f, 1.0f, 0.0f};
    assert(goodix_primitives_nadt_symmetric_fir_i32(
        fir_input, 4u, fir_identity, 3u,
        fir_output, 4u, fir_scratch, 6u));
    for (size_t index = 0u; index < 4u; ++index) {
        assert(fir_output[index] == fir_input[index]);
    }
    const float fir_half[1] = {0.5f};
    const int32_t fir_small_input[2] = {1, -1};
    assert(goodix_primitives_nadt_symmetric_fir_i32(
        fir_small_input, 2u, fir_half, 1u,
        fir_output, 4u, fir_scratch, 6u));
    assert(fir_output[0] == 0 && fir_output[1] == 0);
    assert(!goodix_primitives_nadt_symmetric_fir_i32(
        fir_input, 4u, fir_coefficients, 2u,
        fir_output, 4u, fir_scratch, 6u));
    assert(!goodix_primitives_nadt_symmetric_fir_i32(
        fir_input, 4u, fir_coefficients, 3u,
        fir_output, 3u, fir_scratch, 6u));
    assert(!goodix_primitives_nadt_symmetric_fir_i32(
        fir_input, 4u, fir_coefficients, 3u,
        fir_output, 4u, fir_scratch, 5u));

    int32_t window_input[30];
    int32_t window_output[30];
    int32_t window_filtered[30] = {0};
    int32_t window_fir_scratch[52] = {0};
    float window_boundary_coefficients[11u * 23u] = {0.0f};
    for (size_t index = 0u; index < 30u; ++index) {
        window_input[index] = (int32_t)index + 1;
        window_output[index] = -999;
    }
    for (size_t row = 0u; row < 11u; ++row) {
        window_boundary_coefficients[row * 23u + row] = 1.0f;
    }
    assert(goodix_primitives_nadt_window_filter_i32(
        window_input, 30u, window_output, 30u, 3u,
        window_boundary_coefficients, 11u * 23u,
        window_filtered, 30u, window_fir_scratch, 52u));
    for (size_t row = 0u; row < 11u; ++row) {
        assert(window_output[row] == (int32_t)(23u - row));
        assert(window_output[19u + row] == (int32_t)(18u - row));
    }
    for (size_t index = 11u; index < 19u; ++index) {
        assert(window_output[index] == window_filtered[index]);
    }
    for (size_t index = 0u; index < 30u; ++index) {
        window_output[index] = -999;
    }
    assert(goodix_primitives_nadt_window_filter_i32(
        window_input, 30u, window_output, 30u, 0u,
        window_boundary_coefficients, 11u * 23u,
        window_filtered, 30u, window_fir_scratch, 52u));
    assert(window_output[0] == -999 && window_output[10] == -999 &&
           window_output[19] == -999 && window_output[29] == -999);
    assert(!goodix_primitives_nadt_window_filter_i32(
        window_input, 22u, window_output, 30u, 3u,
        window_boundary_coefficients, 11u * 23u,
        window_filtered, 30u, window_fir_scratch, 52u));

    const float rate_amplitudes[5] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    uint16_t rate_positions[5] = {0u, 10u, 20u, 30u, 40u};
    int32_t rate_selected[5] = {0};
    int32_t rate_differences[4] = {0};
    int32_t periodic_rate = -1;
    assert(goodix_primitives_nadt_periodic_peak_rate(
        rate_amplitudes, rate_positions, 5u,
        rate_selected, 5u, rate_differences, 4u, &periodic_rate));
    assert(periodic_rate == 150 &&
           rate_selected[0] == 0 && rate_selected[4] == 40 &&
           rate_differences[0] == 10 && rate_differences[3] == 10);
    const uint16_t slow_rate_positions[5] = {0u, 50u, 100u, 150u, 200u};
    assert(goodix_primitives_nadt_periodic_peak_rate(
        rate_amplitudes, slow_rate_positions, 5u,
        rate_selected, 5u, rate_differences, 4u, &periodic_rate));
    assert(periodic_rate == 40);
    const uint16_t fast_rate_positions[5] = {0u, 5u, 10u, 15u, 20u};
    assert(goodix_primitives_nadt_periodic_peak_rate(
        rate_amplitudes, fast_rate_positions, 5u,
        rate_selected, 5u, rate_differences, 4u, &periodic_rate));
    assert(periodic_rate == 200);
    const uint16_t irregular_positions[5] = {0u, 10u, 24u, 38u, 52u};
    assert(goodix_primitives_nadt_periodic_peak_rate(
        rate_amplitudes, irregular_positions, 5u,
        rate_selected, 5u, rate_differences, 4u, &periodic_rate));
    assert(periodic_rate == 0);
    assert(goodix_primitives_nadt_periodic_peak_rate(
        rate_amplitudes, rate_positions, 2u,
        rate_selected, 5u, rate_differences, 4u, &periodic_rate));
    assert(periodic_rate == 0);
    assert(!goodix_primitives_nadt_periodic_peak_rate(
        rate_amplitudes, rate_positions, 5u,
        rate_selected, 4u, rate_differences, 4u, &periodic_rate));

    float spectral_values[128] = {0.0f};
    spectral_values[40] = 10.0f;
    spectral_values[80] = 5.0f;
    float spectral_concentration = -1.0f;
    float spectral_peak = -1.0f;
    log10_call_count = 0u;
    assert(goodix_primitives_spo2_spectral_peak_concentration_db(
        spectral_values, 128u, 1u, log10_half_fixture,
        &spectral_concentration, &spectral_peak));
    assert(spectral_concentration == 5.0f && spectral_peak == 40.0f &&
           log10_call_count == 1u &&
           log10_argument > 20.83f && log10_argument < 20.84f);
    memset(spectral_values, 0, sizeof(spectral_values));
    assert(goodix_primitives_spo2_spectral_peak_concentration_db(
        spectral_values, 128u, 1u, log10_half_fixture,
        &spectral_concentration, &spectral_peak));
    assert(spectral_concentration == 0.0f && spectral_peak == 0.0f &&
           log10_call_count == 1u);
    assert(!goodix_primitives_spo2_spectral_peak_concentration_db(
        spectral_values, 256u, 1u, log10_half_fixture,
        &spectral_concentration, &spectral_peak));

    float report_primary_spectrum[349] = {0.0f};
    float report_secondary_spectrum[93] = {0.0f};
    report_primary_spectrum[25] = 10.0f;
    report_primary_spectrum[50] = 8.0f;
    report_primary_spectrum[75] = 7.0f;
    report_primary_spectrum[281] = 6.0f;
    report_secondary_spectrum[24] = 6.0f;
    uint8_t report_primary_candidates[3] = {0u};
    uint8_t report_reference_candidates[3] = {0u};
    float report_concentrations[3] = {0.0f};
    float report_metrics[3] = {0.0f};
    goodix_primitives_spo2_report_analyzer_state report_analysis_state = {
        .primary_candidates = {
            .values = report_primary_candidates, .capacity = 3u,
        },
        .concentrations = {
            .values = report_concentrations, .capacity = 3u, .period = 1u,
        },
        .reference_candidates = {
            .values = report_reference_candidates, .capacity = 3u,
        },
        .metric_history = {
            .values = report_metrics, .capacity = 3u, .period = 1u,
        },
        .reference_limit = 50u,
    };
    const goodix_primitives_spo2_report_analyzer_input report_analysis_input = {
        .primary_spectrum = report_primary_spectrum,
        .primary_spectrum_count = 349u,
        .secondary_spectrum = report_secondary_spectrum,
        .secondary_spectrum_count = 93u,
        .metrics = {1.0f, 2.0f, 3.0f, 3.0f},
        .reference_candidate = 48u,
    };
    goodix_primitives_spo2_report_analysis report_analysis = {0};
    log10_call_count = 0u;
    for (size_t iteration = 0u; iteration < 3u; ++iteration) {
        assert(goodix_primitives_spo2_report_analyze(
            &report_analysis_input, &report_analysis_state,
            square_root_fixture, log10_half_fixture, &report_analysis));
    }
    assert(log10_call_count == 3u &&
           report_analysis.primary_candidate == 48u &&
           report_analysis.first_harmonic_candidate == 95u &&
           report_analysis.second_harmonic_candidate == 144u &&
           report_analysis.spectral_candidate == 48u &&
           report_analysis.secondary_candidate == 46u &&
           report_analysis.spectral_concentration == 5.0f &&
           report_analysis.score == 0.0f &&
           report_analysis.concentration_deviation == 0.0f &&
           report_analysis.metric_mean == 3.0f &&
           report_analysis.primary_spectral_proximity == 1u &&
           report_analysis.harmonic_consistency == 1u &&
           report_analysis.phase_gate == 1u &&
           report_analysis.acceptance_gate == 0u &&
           report_analysis.paired_gate_a == 3u &&
           report_analysis.paired_gate_b == 3u &&
           report_analysis.activation_gate == 0u &&
           report_analysis.hold_gate == 3u &&
           report_analysis.metrics_below_four == 1u &&
           report_analysis.secondary_consistency == 1u &&
           report_analysis_state.primary_spectral_streak == 3u &&
           report_analysis_state.harmonic_streak == 3u &&
           report_analysis_state.stable_primary_streak == 2u &&
           report_analysis_state.previous_primary_candidate == 48u);
    goodix_primitives_spo2_report_analyzer_input short_report_analysis =
        report_analysis_input;
    short_report_analysis.primary_spectrum_count = 348u;
    const goodix_primitives_spo2_report_analysis saved_report_analysis =
        report_analysis;
    assert(!goodix_primitives_spo2_report_analyze(
        &short_report_analysis, &report_analysis_state,
        square_root_fixture, log10_half_fixture, &report_analysis));
    assert(memcmp(&report_analysis, &saved_report_analysis,
                  sizeof(report_analysis)) == 0);

    uint8_t report_history[532];
    for (size_t index = 0u; index < sizeof(report_history); ++index) {
        report_history[index] = (uint8_t)index;
    }
    goodix_primitives_spo2_report_state report_state = {
        .history_shift_a = true,
        .history_shift_b = true,
        .use_secondary_candidate = false,
        .accepted = false,
        .minimum_selected_value = 12u,
        .event = 7u,
        .phase = 0u,
        .event_seen = 0u,
        .history = report_history,
        .history_capacity = sizeof(report_history),
    };
    report_analyze_fixture report_analyzer = {
        .result = {
            .primary_candidate = 10u,
            .secondary_candidate = 52u,
            .score = 4.0f,
            .acceptance_gate = 3u,
        },
        .call_count = 0u,
    };
    goodix_primitives_spo2_report_output report_output = {0};
    assert(goodix_primitives_spo2_report_state_update(
        &report_state, 10u, 50, &report_output,
        analyze_report_fixture, &report_analyzer));
    assert(report_analyzer.call_count == 1u && report_state.accepted &&
           report_state.use_secondary_candidate && report_state.event == 0u &&
           report_output.selected_value == 12u &&
           report_history[0] == 20u && report_history[511] == 19u);

    report_state.history_shift_a = false;
    report_state.history_shift_b = false;
    report_state.accepted = false;
    report_state.phase = 0u;
    report_state.event = 0u;
    report_state.event_seen = 0u;
    report_analyzer.result.primary_candidate = 50u;
    report_analyzer.result.secondary_candidate = 0u;
    report_analyzer.result.score = 1.5f;
    report_analyzer.result.phase_gate = 1u;
    report_analyzer.result.acceptance_gate = 3u;
    report_analyzer.result.paired_gate_a = 0u;
    report_analyzer.result.paired_gate_b = 0u;
    report_analyzer.result.activation_gate = 3u;
    report_analyzer.result.hold_gate = 0u;
    assert(goodix_primitives_spo2_report_state_update(
        &report_state, 1u, 100, &report_output,
        analyze_report_fixture, &report_analyzer));
    assert(!report_state.accepted && report_state.phase == 1u &&
           report_state.event == 1u && report_state.event_seen == 1u);
    assert(goodix_primitives_spo2_report_state_update(
        &report_state, 1u, 100, &report_output,
        analyze_report_fixture, &report_analyzer));
    assert(report_state.phase == 1u && report_state.event == 1u);
    report_analyzer.result.hold_gate = 3u;
    report_analyzer.result.primary_candidate = 51u;
    report_analyzer.result.phase_gate = 2u;
    assert(goodix_primitives_spo2_report_state_update(
        &report_state, 1u, 100, &report_output,
        analyze_report_fixture, &report_analyzer));
    assert(report_state.phase == 2u && report_state.event == 0u);
    assert(goodix_primitives_spo2_report_state_update(
        &report_state, 1u, 100, &report_output,
        analyze_report_fixture, &report_analyzer));
    assert(report_state.phase == 0u && report_state.event == 0u);

    uint16_t packed_deviation_a[6] = {0};
    uint16_t packed_deviation_b[4] = {0};
    uint16_t packed_deviation_c[1] = {0};
    uint16_t packed_deviation_d[3] = {0};
    const float packed_deviation_a_values[6] = {
        1.0f, 9.0f, 9.0f, 3.0f, 9.0f, 9.0f,
    };
    const float packed_deviation_b_values[4] = {2.0f, 9.0f, 9.0f, 2.0f};
    const float packed_deviation_c_values[1] = {7.0f};
    const float packed_deviation_d_values[3] = {1.0f, 2.0f, 3.0f};
    for (size_t index = 0u; index < 6u; ++index) {
        uint32_t bits = 0u;
        memcpy(&bits, &packed_deviation_a_values[index], sizeof(bits));
        packed_deviation_a[index] =
            goodix_primitives_f32_bits_to_packed_6_9(bits);
    }
    for (size_t index = 0u; index < 4u; ++index) {
        uint32_t bits = 0u;
        memcpy(&bits, &packed_deviation_b_values[index], sizeof(bits));
        packed_deviation_b[index] =
            goodix_primitives_f32_bits_to_packed_6_9(bits);
    }
    {
        uint32_t bits = 0u;
        memcpy(&bits, &packed_deviation_c_values[0], sizeof(bits));
        packed_deviation_c[0] =
            goodix_primitives_f32_bits_to_packed_6_9(bits);
    }
    for (size_t index = 0u; index < 3u; ++index) {
        uint32_t bits = 0u;
        memcpy(&bits, &packed_deviation_d_values[index], sizeof(bits));
        packed_deviation_d[index] =
            goodix_primitives_f32_bits_to_packed_6_9(bits);
    }
    const goodix_primitives_packed_u16_span packed_deviation_channels[4] = {
        {packed_deviation_a, 6u},
        {packed_deviation_b, 4u},
        {packed_deviation_c, 1u},
        {packed_deviation_d, 3u},
    };
    float packed_deviation_output[4] = {0.0f};
    float packed_deviation_scratch[60] = {0.0f};
    assert(goodix_primitives_spo2_packed_channel_standard_deviations(
        packed_deviation_channels, packed_deviation_output,
        packed_deviation_scratch, 60u, square_root_fixture));
    assert(packed_deviation_output[0] == 1.0f &&
           packed_deviation_output[1] == 0.0f &&
           packed_deviation_output[2] == 0.0f &&
           packed_deviation_output[3] > 0.816f &&
           packed_deviation_output[3] < 0.817f);
    assert(!goodix_primitives_spo2_packed_channel_standard_deviations(
        packed_deviation_channels, packed_deviation_output,
        packed_deviation_scratch, 59u, square_root_fixture));

    int32_t channel_scaling_values[6] = {
        16384, 0, 0, 2000, 0, 0,
    };
    uint8_t channel_scaling_codes[6] = {0u, 0u, 0u, 0u, 0u, 0u};
    int16_t channel_scaling_divisors[6] = {2, 1, 1, 4, 1, 1};
    const int32_t channel_scale_mode_zero[1] = {5};
    const int32_t channel_scale_mode_one[1] = {1};
    const int32_t channel_scale_mode_two[1] = {2};
    const int32_t channel_scale_zero[1] = {0};
    goodix_primitives_spo2_channel_scaling channel_scaling = {
        .channel_count = 2u,
        .encoded_values = channel_scaling_values,
        .encoded_value_count = 6u,
        .scale_codes = channel_scaling_codes,
        .scale_code_count = 6u,
        .divisors = channel_scaling_divisors,
        .divisor_count = 6u,
        .bit_width = 17u,
        .scale_mode = 0u,
        .encoding_mode = 1u,
        .scale_tables = {
            channel_scale_mode_zero,
            channel_scale_mode_one,
            channel_scale_mode_two,
        },
        .scale_table_counts = {1u, 1u, 1u},
        .power = channel_power_fixture,
    };
    float channel_scaled_pair[2] = {-1.0f, -2.0f};
    channel_power_calls = 0u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 1u, 1u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == 2000.0f &&
           channel_scaled_pair[1] == 0.5f && channel_power_calls == 0u);
    channel_scaling_divisors[3] = -1;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 1u, 1u, channel_scaled_pair);
    assert(channel_scaled_pair[1] > 0.00003051f &&
           channel_scaled_pair[1] < 0.00003052f);
    channel_scaling_divisors[3] = 4;

    channel_scaling.encoding_mode = 0u;
    channel_power_calls = 0u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == 16384.0f &&
           channel_scaled_pair[1] == 20000000.0f &&
           channel_power_calls == 2u &&
           channel_power_bases[0] == 10.0 &&
           channel_power_exponents[0] == 3.0 &&
           channel_power_bases[1] == 2.0 &&
           channel_power_exponents[1] == 17.0);

    channel_scaling_values[0] = 65536;
    channel_scaling.scale_mode = 1u;
    channel_power_calls = 0u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == 65536.0f &&
           channel_scaled_pair[1] == 450000000.0f &&
           channel_power_calls == 2u &&
           channel_power_exponents[0] == 9.0 &&
           channel_power_exponents[1] == 17.0);
    channel_scaling.scale_mode = 2u;
    channel_power_calls = 0u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[1] == 225000000.0f &&
           channel_power_calls == 2u);

    channel_scaling_values[0] = INT32_C(0x00040008);
    channel_scaling.bit_width = 20u;
    channel_scaling.scale_mode = 3u;
    channel_power_calls = 0u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == 32769.0f &&
           channel_scaled_pair[1] == 0.0f && channel_power_calls == 0u);

    channel_scaling.bit_width = 17u;
    channel_scaling.scale_mode = 0u;
    channel_scaling_values[0] = 16384;
    channel_scaling.scale_tables[0] = channel_scale_zero;
    channel_power_calls = 0u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == 16384.0f &&
           channel_scaled_pair[1] == 0.0f && channel_power_calls == 0u);
    channel_scaling.scale_tables[0] = channel_scale_mode_zero;
    channel_scaling_divisors[0] = 0;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == 16384.0f &&
           channel_scaled_pair[1] == 0.0f && channel_power_calls == 0u);
    channel_scaling_divisors[0] = 2;
    channel_scaling.scale_table_counts[0] = 0u;
    channel_scaled_pair[0] = -11.0f;
    channel_scaled_pair[1] = -22.0f;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == -11.0f &&
           channel_scaled_pair[1] == -22.0f);
    channel_scaling.scale_table_counts[0] = 1u;
    channel_scaling.encoding_mode = 2u;
    goodix_primitives_spo2_channel_scale_decode(
        &channel_scaling, 0u, 0u, channel_scaled_pair);
    assert(channel_scaled_pair[0] == -11.0f &&
           channel_scaled_pair[1] == -22.0f);

    uint8_t channel_presence[6] = {0xECu, 1u, 1u, 1u, 1u, 1u};
    int32_t channel_encoded[6] = {1, 2, 3, 4, 5, 6};
    channel_decode_fixture channel_decoder = {0};
    goodix_primitives_spo2_channel_record assembled_channel_records[2] = {{{0}}};
    const goodix_primitives_spo2_channel_source assembled_channel_source = {
        .channel_count = 2u,
        .presence_bytes = channel_presence,
        .presence_byte_count = 6u,
        .encoded_values = channel_encoded,
        .encoded_value_count = 6u,
        .metadata = {11u, 12u, 13u},
        .decode_context = &channel_decoder,
    };
    goodix_primitives_spo2_channel_output assembled_channel_output = {
        .sequence = -1,
        .record_count = 0u,
        .records = assembled_channel_records,
        .record_capacity = 2u,
        .metadata = {0u, 0u, 0u},
    };
    bool channel_count_mismatch = true;
    assert(goodix_primitives_spo2_channel_records_assemble(
        &assembled_channel_source, 10, 2u, &assembled_channel_output, add_one,
        decode_channel_fixture, &channel_count_mismatch));
    assert(!channel_count_mismatch && assembled_channel_output.sequence == 9 &&
           assembled_channel_output.record_count == 2u &&
           assembled_channel_output.metadata[0] == 11u &&
           assembled_channel_output.metadata[1] == 12u &&
           assembled_channel_output.metadata[2] == 13u);
    assert(channel_decoder.call_count == 5u &&
           channel_decoder.channels[0] == 0u && channel_decoder.groups[0] == 0u &&
           channel_decoder.channels[1] == 0u && channel_decoder.groups[1] == 1u &&
           channel_decoder.channels[2] == 0u && channel_decoder.groups[2] == 2u &&
           channel_decoder.channels[3] == 1u && channel_decoder.groups[3] == 0u &&
           channel_decoder.channels[4] == 1u && channel_decoder.groups[4] == 2u);
    assert(assembled_channel_records[0].groups[0][0] == 0.0f &&
           assembled_channel_records[0].groups[1][0] == 1.0f &&
           assembled_channel_records[0].groups[2][0] == 2.0f &&
           assembled_channel_records[1].groups[0][0] == 10.0f &&
           assembled_channel_records[1].groups[2][1] == 12.5f);
    for (size_t index = 0u; index < 6u; ++index) {
        assert(channel_encoded[index] == INT32_C(0x00800000));
    }

    channel_decoder.call_count = 0u;
    assembled_channel_output.record_count = 4u;
    assembled_channel_output.record_capacity = 1u;
    channel_count_mismatch = false;
    assert(goodix_primitives_spo2_channel_records_assemble(
        &assembled_channel_source, INT32_MIN, 1u, &assembled_channel_output, add_one,
        decode_channel_fixture, &channel_count_mismatch));
    assert(channel_count_mismatch && assembled_channel_output.sequence == INT32_MAX &&
           assembled_channel_output.record_count == 6u &&
           channel_decoder.call_count == 3u);
    goodix_primitives_spo2_channel_source short_channel_source =
        assembled_channel_source;
    short_channel_source.presence_byte_count = 5u;
    assert(!goodix_primitives_spo2_channel_records_assemble(
        &short_channel_source, 1, 1u, &assembled_channel_output, add_one,
        decode_channel_fixture, &channel_count_mismatch));

    goodix_primitives_biquad_state biquad_state[2] = {{1.0f, 2.0f}, {0}};
    const goodix_primitives_biquad_coefficients biquad_coefficients[2] = {
        {0.5f, 0.25f, 0.125f, 0.1f, 0.2f},
        {1.0f, 0.0f, 0.0f, 0.0f, 0.0f},
    };
    goodix_primitives_biquad_cascade biquad = {
        .stage_count = 1u,
        .states = biquad_state,
        .state_count = 2u,
        .coefficients = biquad_coefficients,
        .coefficient_count = 2u,
        .previous_input = 9.0f,
    };
    float biquad_output = 0.0f;
    assert(goodix_primitives_spo2_biquad_cascade_process(
        &biquad, 4.0f, false, false, 0, false, &biquad_output));
    assert(biquad_output == 3.0f && biquad.previous_input == 9.0f &&
           biquad_state[0].first > 3.299f &&
           biquad_state[0].first < 3.301f &&
           biquad_state[0].second > 1.099f &&
           biquad_state[0].second < 1.101f);
    biquad.stage_count = 2u;
    biquad_state[0].first = 0.0f;
    biquad_state[0].second = 0.0f;
    biquad_state[1].first = 0.0f;
    biquad_state[1].second = 0.0f;
    assert(goodix_primitives_spo2_biquad_cascade_process(
        &biquad, 8.0f, false, false, 0, false, &biquad_output));
    assert(biquad_output == 4.0f);
    const goodix_primitives_biquad_coefficients correction_coefficients[1] = {
        {1.0f, 2.0f, 3.0f, 0.0f, 0.0f},
    };
    biquad.stage_count = 1u;
    biquad.coefficients = correction_coefficients;
    biquad.coefficient_count = 1u;
    biquad.previous_input = 10.0f;
    biquad_state[0].first = 0.0f;
    biquad_state[0].second = 0.0f;
    assert(goodix_primitives_spo2_biquad_cascade_process(
        &biquad, 12.0f, true, false, 0, true, &biquad_output));
    assert(biquad_output == 22.0f && biquad.previous_input == 12.0f &&
           biquad_state[0].first == 30.0f &&
           biquad_state[0].second == 36.0f);
    biquad.previous_input = 10.0f;
    biquad_state[0].first = 0.0f;
    biquad_state[0].second = 0.0f;
    assert(goodix_primitives_spo2_biquad_cascade_process(
        &biquad, 12.0f, true, true, 3, false, &biquad_output));
    assert(biquad_output == 12.0f && biquad.previous_input == 12.0f &&
           biquad_state[0].first == 24.0f &&
           biquad_state[0].second == 36.0f);
    biquad.stage_count = 0u;
    assert(!goodix_primitives_spo2_biquad_cascade_process(
        &biquad, 1.0f, false, false, 0, false, &biquad_output));
    biquad.stage_count = 2u;
    biquad.coefficient_count = 1u;
    assert(!goodix_primitives_spo2_biquad_cascade_process(
        &biquad, 1.0f, false, false, 0, false, &biquad_output));

    log10_call_count = 0u;
    float decimal_residual = -9.0f;
    assert(goodix_primitives_spo2_decimal_residual(
        1.2345678f, log10_zero_fixture, &decimal_residual));
    float residual_four = 0.0f;
    float residual_eight = 0.0f;
    assert(goodix_primitives_truncate_decimal(
        0.12345678f, 4u, &residual_four));
    assert(goodix_primitives_truncate_decimal(
        0.12345678f, 8u, &residual_eight));
    float expected_residual =
        (residual_four - residual_eight) * 10000.0f;
    if (expected_residual < 0.0f) {
        expected_residual = -expected_residual;
    }
    const int32_t residual_parity =
        (int32_t)(expected_residual * 10000.0f);
    if ((residual_parity & 1) != 0) {
        expected_residual = -expected_residual;
    }
    assert(log10_call_count == 1u && log10_argument == 1.2345678f &&
           decimal_residual == expected_residual);
    assert(goodix_primitives_spo2_decimal_residual(
        -1.2345678f, log10_zero_fixture, &decimal_residual));
    assert(log10_call_count == 2u && log10_argument == 1.2345678f);
    decimal_residual = 7.0f;
    assert(goodix_primitives_spo2_decimal_residual(
        0x1.0p-21f, log10_zero_fixture, &decimal_residual));
    assert(decimal_residual == 7.0f && log10_call_count == 2u);
    assert(!goodix_primitives_spo2_decimal_residual(
        1.0f, NULL, &decimal_residual));

    const float rolling_source[5] = {2.0f, 0.0f, 0.0f, 0.0f, 6.0f};
    float rolling_sorted[6] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 0.0f};
    size_t rolling_count = 5u;
    float rolling_anchor = 3.0f;
    float rolling_output = 0.0f;
    assert(goodix_primitives_spo2_rolling_percentile_select(
        rolling_source, 5u, rolling_sorted, &rolling_count, 6u,
        &rolling_anchor, 1, &rolling_output));
    assert(rolling_count == 5u && rolling_anchor == 2.0f &&
           rolling_sorted[0] == 1.0f && rolling_sorted[1] == 2.0f &&
           rolling_sorted[2] == 4.0f && rolling_sorted[3] == 5.0f &&
           rolling_sorted[4] == 6.0f && rolling_output == 6.0f);
    rolling_anchor = 4.0f;
    assert(goodix_primitives_spo2_rolling_percentile_select(
        rolling_source, 5u, rolling_sorted, &rolling_count, 6u,
        &rolling_anchor, 0, &rolling_output));
    assert(rolling_count == 5u && rolling_output == 5.0f);
    rolling_anchor = 99.0f;
    assert(goodix_primitives_spo2_rolling_percentile_select(
        rolling_source, 5u, rolling_sorted, &rolling_count, 6u,
        &rolling_anchor, 1, &rolling_output));
    assert(rolling_count == 6u);
    rolling_anchor = 99.0f;
    assert(!goodix_primitives_spo2_rolling_percentile_select(
        rolling_source, 5u, rolling_sorted, &rolling_count, 6u,
        &rolling_anchor, 1, &rolling_output));

    double smoothed_accumulator = 0.0;
    int32_t smoothed_result = -1;
    for (uint32_t sample_count = 1u; sample_count <= 59u;
            ++sample_count) {
        assert(goodix_primitives_spo2_smoothed_scale(
            sample_count, 2.0f, 10000u,
            &smoothed_accumulator, &smoothed_result));
        assert(smoothed_result == 0);
    }
    assert(smoothed_accumulator == 118.0);
    assert(goodix_primitives_spo2_smoothed_scale(
        60u, 2.0f, 10000u,
        &smoothed_accumulator, &smoothed_result));
    assert(smoothed_accumulator == 2.0 && smoothed_result == 0);
    assert(goodix_primitives_spo2_smoothed_scale(
        61u, 62.0f, 10000u,
        &smoothed_accumulator, &smoothed_result));
    assert(smoothed_accumulator == 3.0 && smoothed_result == 0);
    smoothed_accumulator = 1.0;
    assert(goodix_primitives_spo2_smoothed_scale(
        75u, 1.0f, 5000u,
        &smoothed_accumulator, &smoothed_result));
    assert(smoothed_accumulator == 1.0 && smoothed_result == 0);
    smoothed_accumulator = 3.0;
    assert(goodix_primitives_spo2_smoothed_scale(
        75u, 3.0f, 5000u,
        &smoothed_accumulator, &smoothed_result));
    assert(smoothed_accumulator == 3.0 && smoothed_result == 1);
    smoothed_accumulator = -1.0;
    assert(goodix_primitives_spo2_smoothed_scale(
        75u, -1.0f, 10000u,
        &smoothed_accumulator, &smoothed_result));
    assert(smoothed_result == 0);
    assert(!goodix_primitives_spo2_smoothed_scale(
        75u, 1.0f, 10000u, NULL, &smoothed_result));

    const float percentile_values[8] = {
        0.0f, 1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f,
    };
    float percentile = -1.0f;
    assert(goodix_primitives_percentile_lookup(
        percentile_values, 8u, 25u, &percentile));
    assert(percentile == 2.0f);
    assert(goodix_primitives_percentile_lookup(
        percentile_values, 8u, 50u, &percentile));
    assert(percentile == 4.0f);
    assert(goodix_primitives_percentile_lookup(
        percentile_values, 8u, 75u, &percentile));
    assert(percentile == 6.0f);
    assert(goodix_primitives_percentile_lookup(
        percentile_values, 8u, 99u, &percentile));
    assert(percentile == 7.0f);
    assert(!goodix_primitives_percentile_lookup(
        percentile_values, 8u, 100u, &percentile));

    /* NADT feature/statistics leaves at 0x5144C, 0x361D8, 0x3623C,
     * and 0x29AA0. */
    const int32_t mean_values[3] = {1, 2, 6};
    float i32_mean = 0.0f;
    assert(goodix_primitives_i32_mean(mean_values, 3u, &i32_mean));
    assert(i32_mean == 3.0f);
    assert(!goodix_primitives_i32_mean(mean_values, 0u, &i32_mean));
    uint32_t squared_deviation = 0u;
    assert(goodix_primitives_i32_squared_deviation_sum(
        mean_values, 3u, round_fixture, &squared_deviation));
    assert(squared_deviation == 14u);
    const int32_t saturating_values[2] = {INT32_MIN, INT32_MAX};
    assert(goodix_primitives_i32_squared_deviation_sum(
        saturating_values, 2u, round_fixture, &squared_deviation));
    assert(squared_deviation == UINT32_C(0x3FFFFFFF));
    assert(!goodix_primitives_i32_squared_deviation_sum(
        mean_values, 3u, NULL, &squared_deviation));

    const int16_t trimmed_values[5] = {10, 20, 30, 40, 50};
    const int16_t trimmed_indices[5] = {4, 0, 2, 1, 3};
    int16_t trimmed_mean = 0;
    assert(goodix_primitives_indexed_i16_trimmed_mean(
        trimmed_values, 5u, trimmed_indices, 5u, &trimmed_mean));
    assert(trimmed_mean == 30);
    assert(goodix_primitives_indexed_i16_trimmed_mean(
        trimmed_values, 5u, trimmed_indices, 2u, &trimmed_mean));
    assert(trimmed_mean == 60);
    const int16_t wrapping_values[2] = {30000, 30000};
    const int16_t wrapping_indices[2] = {0, 1};
    assert(goodix_primitives_indexed_i16_trimmed_mean(
        wrapping_values, 2u, wrapping_indices, 2u, &trimmed_mean));
    assert(trimmed_mean == -5536);
    const int16_t invalid_index[1] = {-1};
    assert(!goodix_primitives_indexed_i16_trimmed_mean(
        trimmed_values, 5u, invalid_index, 1u, &trimmed_mean));

    const uint8_t packed_mask[2] = {UINT8_C(0x02), UINT8_C(0x40)};
    uint8_t mask_columns[5] = {
        UINT8_C(0xAA), UINT8_C(0xAA), UINT8_C(0xAA),
        UINT8_C(0xAA), UINT8_C(0xAA),
    };
    assert(goodix_primitives_mask_columns_any(
        packed_mask, sizeof(packed_mask), 5u, 3u,
        mask_columns, 5u));
    assert(mask_columns[0] == UINT8_C(0xAA));
    assert(mask_columns[1] == 1u);
    assert(mask_columns[2] == UINT8_C(0xAA));
    assert(mask_columns[3] == UINT8_C(0xAA));
    assert(mask_columns[4] == 1u);
    assert(!goodix_primitives_mask_columns_any(
        packed_mask, 1u, 5u, 3u, mask_columns, 5u));

    /* Feature preparation/state leaves at 0x32744, 0x43860, 0x9775C,
     * and 0x97984. */
    const float channel_source[3] = {2.0f, 3.0f, 4.0f};
    const float channel_scales[3] = {0.5f, 2.0f, -1.0f};
    float channel_output[3] = {0.0f, 0.0f, 0.0f};
    float channel_factor = 0.0f;
    assert(goodix_primitives_channel_scale_copy(
        channel_source, 3u, 1u, channel_scales, 0.25f,
        channel_output, 3u, &channel_factor));
    assert(channel_factor == 0.25f && channel_output[0] == 1.0f &&
           channel_output[1] == 6.0f && channel_output[2] == -4.0f);
    assert(goodix_primitives_channel_scale_copy(
        channel_source, 3u, 2u, NULL, 9.0f,
        channel_output, 3u, &channel_factor));
    assert(channel_factor == 1.0f && channel_output[0] == 2.0f &&
           channel_output[1] == 3.0f && channel_output[2] == 4.0f);
    assert(!goodix_primitives_channel_scale_copy(
        channel_source, 3u, 1u, NULL, 0.25f,
        channel_output, 3u, &channel_factor));

    const float transform_input[3] = {10.0f, 20.0f, 30.0f};
    float transform_scratch[5] = {-1.0f, -1.0f, -1.0f, -1.0f, -1.0f};
    float prefix_transform_output[4] = {0.0f, 0.0f, 0.0f, 99.0f};
    assert(goodix_primitives_float_transform_prefix_copy(
        transform_input, 3u, 5u, transform_scratch, 5u,
        prefix_transform_output, 4u, 3u, float_transform_fixture));
    assert(float_transform_input_count == 3u && float_transform_count == 5u);
    assert(transform_scratch[0] == 11.0f &&
           transform_scratch[1] == 22.0f &&
           transform_scratch[2] == 33.0f &&
           transform_scratch[3] == 4.0f &&
           transform_scratch[4] == 5.0f);
    assert(prefix_transform_output[0] == 11.0f &&
           prefix_transform_output[1] == 22.0f &&
           prefix_transform_output[2] == 33.0f &&
           prefix_transform_output[3] == 99.0f);
    assert(!goodix_primitives_float_transform_prefix_copy(
        transform_input, 3u, 5u, transform_scratch, 4u,
        prefix_transform_output, 4u, 3u, float_transform_fixture));
    assert(!goodix_primitives_float_transform_prefix_copy(
        transform_input, 3u, 5u, transform_scratch, 5u,
        prefix_transform_output, 4u, 6u, float_transform_fixture));
    assert(!goodix_primitives_float_transform_prefix_copy(
        transform_input, 3u, 5u, transform_scratch, 5u,
        prefix_transform_output, 4u, 3u, NULL));

    float fft_input[GOODIX_PRIMITIVES_FFT_REAL_VALUES];
    uint16_t packed_fft_input[GOODIX_PRIMITIVES_FFT_REAL_VALUES];
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_FFT_REAL_VALUES; ++index) {
        const bool positive = (index & 1u) == 0u;
        fft_input[index] = positive ? 1.0f : -1.0f;
        packed_fft_input[index] = positive
            ? UINT16_C(0x3C00) : UINT16_C(0xBC00);
    }
    float fft_scratch[GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES] = {0.0f};
    float fft_output[GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES] = {0.0f};
    assert(goodix_primitives_fft_magnitude_prepare(
        fft_input, NULL, false, GOODIX_PRIMITIVES_FFT_REAL_VALUES, false,
        fft_scratch, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES,
        fft_output, GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES,
        GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES, square_root_fixture));
    assert(fft_output[0] == 0.0f && fft_output[127] == 0.0f &&
           fft_output[128] == 256.0f);
    assert(goodix_primitives_fft_magnitude_prepare(
        NULL, packed_fft_input, true, GOODIX_PRIMITIVES_FFT_REAL_VALUES,
        true, fft_scratch, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES,
        fft_output, GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES,
        GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES, square_root_fixture));
    assert(fft_output[0] == 0.0f && fft_output[127] == 0.0f &&
           fft_output[128] == 2.0f);
    assert(!goodix_primitives_fft_magnitude_prepare(
        fft_input, NULL, false, GOODIX_PRIMITIVES_FFT_REAL_VALUES, false,
        fft_scratch, GOODIX_PRIMITIVES_FFT_REAL_VALUES,
        fft_output, GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES,
        GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES, square_root_fixture));
    assert(!goodix_primitives_fft_magnitude_prepare(
        NULL, packed_fft_input, false,
        GOODIX_PRIMITIVES_FFT_REAL_VALUES, false,
        fft_scratch, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES,
        fft_output, GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES,
        GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES, square_root_fixture));

    float nadt_spectral_input[
        GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES] = {0.0f};
    float nadt_spectral_scales[
        GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES];
    nadt_spectral_input[0] = 100.0f;
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES; ++index) {
        nadt_spectral_scales[index] = 2.0f;
    }
    goodix_primitives_nadt_spectral_source nadt_spectral_source = {
        .spectrum_values = nadt_spectral_input,
        .spectrum_count = GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
        .outlier_multiplier_tenths = 0u,
        .mode_one_scales = nadt_spectral_scales,
        .scale_count = GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
        .mode_one_factor = 2.0f,
    };
    goodix_primitives_nadt_spectral_workspace nadt_spectral_workspace;
    goodix_primitives_nadt_spectral_result nadt_spectral_result;
    nadt_harmonic_fixture nadt_harmonics = {
        .expected_peaks = {5, 9, 13, 17, 49},
        .accept = true,
    };
    assert(goodix_primitives_nadt_spectral_peak_prepare(
        &nadt_spectral_source, select_nadt_harmonics_fixture,
        &nadt_harmonics, square_root_fixture, floor_positive_fixture,
        &nadt_spectral_workspace, &nadt_spectral_result));
    assert(nadt_harmonics.calls == 1u &&
           nadt_spectral_result.spectral_bin_count == 53u &&
           nadt_spectral_result.peak_begin == 5 &&
           nadt_spectral_result.peak_radius == 3 &&
           nadt_spectral_result.peak_count == 5u &&
           nadt_spectral_result.candidate_indices[0] == 5 &&
           nadt_spectral_result.candidate_indices[1] == 9 &&
           nadt_spectral_result.candidate_indices[2] == 13 &&
           nadt_spectral_result.candidate_flags[0] == 1u &&
           nadt_spectral_result.candidate_flags[1] == 2u &&
           nadt_spectral_result.candidate_flags[2] == 3u);
    assert(nadt_spectral_workspace.accumulated[0] == 100.0f &&
           nadt_spectral_workspace.outlier_mask[0] == 1 &&
           nadt_spectral_workspace.masked[0] == 0.0f &&
           nadt_spectral_workspace.scaled[0] == 0.0f);
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES; ++index) {
        assert(nadt_spectral_workspace.fft_bins[index] == 0.0f);
    }
    nadt_harmonics.accept = false;
    assert(!goodix_primitives_nadt_spectral_peak_prepare(
        &nadt_spectral_source, select_nadt_harmonics_fixture,
        &nadt_harmonics, square_root_fixture, floor_positive_fixture,
        &nadt_spectral_workspace, &nadt_spectral_result));
    assert(nadt_harmonics.calls == 2u);
    nadt_spectral_source.scale_count--;
    assert(!goodix_primitives_nadt_spectral_peak_prepare(
        &nadt_spectral_source, select_nadt_harmonics_fixture,
        &nadt_harmonics, square_root_fixture, floor_positive_fixture,
        &nadt_spectral_workspace, &nadt_spectral_result));

    const float quantile_values[8] = {
        -100.0f, 0.0f, 1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 100.0f,
    };
    float quantile_scratch[8] = {0.0f};
    float quantile = 0.0f;
    assert(goodix_primitives_float_quantile_interpolated(
        quantile_values, 8u, 0.25f, quantile_scratch, 8u, &quantile));
    assert(quantile == 0.5f);
    assert(goodix_primitives_float_quantile_interpolated(
        quantile_values, 8u, 0.75f, quantile_scratch, 8u, &quantile));
    assert(quantile == 4.5f);
    assert(goodix_primitives_float_quantile_interpolated(
        quantile_values, 8u, 0.0f, quantile_scratch, 8u, &quantile));
    assert(quantile == -100.0f);
    assert(goodix_primitives_float_quantile_interpolated(
        quantile_values, 8u, 1.0f, quantile_scratch, 8u, &quantile));
    assert(quantile == 100.0f);
    int8_t quartile_mask[8] = {0};
    assert(goodix_primitives_nadt_quartile_mask(
        quantile_values, 8u, 1.0f, quantile_scratch, 8u,
        quartile_mask, 8u));
    assert(quartile_mask[0] == -1 && quartile_mask[1] == 0 &&
           quartile_mask[6] == 0 && quartile_mask[7] == 1);
    int32_t nonuniform_count = -1;
    assert(goodix_primitives_nadt_nonuniform_mask_count(
        quantile_values, 8u, 10u, quantile_scratch, 8u,
        quartile_mask, 8u, &nonuniform_count));
    assert(nonuniform_count == 2);
    const float one_sided_values[8] = {
        0.0f, 1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 100.0f,
    };
    assert(goodix_primitives_nadt_nonuniform_mask_count(
        one_sided_values, 8u, 10u, quantile_scratch, 8u,
        quartile_mask, 8u, &nonuniform_count));
    assert(nonuniform_count == 0);

    const float difference_values[5] = {10.0f, 7.0f, 20.0f, 17.0f, 19.0f};
    const int32_t difference_first[2] = {0, 2};
    const int32_t difference_second[2] = {1, 2};
    goodix_primitives_nadt_difference_summary difference_summary = {
        .nonuniform_mask_count = -1,
        .reserved_04 = UINT32_C(0xAABBCCDD),
        .mean_difference = -1.0f,
        .relative_variance = -2.0f,
        .accepted_count = UINT8_C(0xEE),
        .sufficient_coverage = UINT8_C(0xDD),
        .reserved_12 = {UINT8_C(0xCC), UINT8_C(0xBB)},
    };
    assert(goodix_primitives_nadt_positive_difference_statistics(
        difference_values, 5u, difference_first, difference_second, 2u,
        &difference_summary));
    assert(difference_summary.mean_difference == 3.0f &&
           difference_summary.relative_variance == 0.0f &&
           difference_summary.accepted_count == 2u &&
           difference_summary.sufficient_coverage == 1u);
    assert(difference_summary.reserved_04 == UINT32_C(0xAABBCCDD) &&
           difference_summary.reserved_12[0] == UINT8_C(0xCC) &&
           difference_summary.reserved_12[1] == UINT8_C(0xBB));
    float difference_sort_scratch[5] = {0.0f};
    int8_t difference_mask_scratch[5] = {0};
    int32_t expected_difference_mask_count = -1;
    assert(goodix_primitives_nadt_nonuniform_mask_count(
        difference_values, 5u, 10u, difference_sort_scratch, 5u,
        difference_mask_scratch, 5u, &expected_difference_mask_count));
    int32_t difference_summary_status = -1;
    assert(goodix_primitives_nadt_difference_summary_execute(
        difference_values, 5u, difference_first, difference_second, 2u,
        10u, difference_sort_scratch, 5u, difference_mask_scratch, 5u,
        &difference_summary, &difference_summary_status));
    assert(difference_summary_status == 0 &&
           difference_summary.nonuniform_mask_count ==
               expected_difference_mask_count &&
           difference_summary.mean_difference == 3.0f &&
           difference_summary.accepted_count == 2u);
    const int32_t invalid_difference_first[2] = {0, 5};
    assert(!goodix_primitives_nadt_positive_difference_statistics(
        difference_values, 5u, invalid_difference_first,
        difference_second, 2u, &difference_summary));
    assert(!goodix_primitives_float_quantile_interpolated(
        quantile_values, 8u, 0.5f, quantile_scratch, 7u, &quantile));

    const goodix_primitives_nadt_cadence_configuration cadence_two = {
        .feature_average_period = 2u,
        .pair_average_period = 2u,
        .ratio_period = 2u,
        .geometry_period = 2u,
    };
    float cadence_feature_storage[5][NADT_FIXTURE_CAPACITY] = {{0.0f}};
    float cadence_pair_storage[NADT_FIXTURE_CAPACITY] = {0.0f};
    goodix_primitives_nadt_feature_pair_state cadence_pair_state = {0};
    nadt_pair_state_initialize(
        &cadence_pair_state, cadence_feature_storage,
        cadence_pair_storage);
    goodix_primitives_nadt_feature_pair cadence_pair = {
        .feature_value = 8.0f,
        .average_value = 6.0f,
    };
    assert(goodix_primitives_nadt_feature_pair_update(
        &cadence_pair, 0u, &cadence_two, &cadence_pair_state));
    assert(cadence_pair_state.average_accumulator == 6.0f &&
           cadence_pair_state.pair_average.count == 0u &&
           cadence_pair_state.feature.feature_average.count == 0u);
    cadence_pair.feature_value = 10.0f;
    cadence_pair.average_value = 10.0f;
    assert(goodix_primitives_nadt_feature_pair_update(
        &cadence_pair, 1u, &cadence_two, &cadence_pair_state));
    assert(cadence_pair_state.average_accumulator == 16.0f &&
           cadence_pair_state.pair_average.count == 1u &&
           cadence_pair_state.pair_average.values[0] == 8.0f &&
           cadence_pair_state.feature.feature_average.count == 1u);

    const goodix_primitives_nadt_cadence_configuration cadence_one = {
        .feature_average_period = 1u,
        .pair_average_period = 1u,
        .ratio_period = 1u,
        .geometry_period = 1u,
    };
    float channel_primary_storage[5][NADT_FIXTURE_CAPACITY] = {{0.0f}};
    float channel_primary_pair_storage[NADT_FIXTURE_CAPACITY] = {0.0f};
    float channel_secondary_storage[5][NADT_FIXTURE_CAPACITY] = {{0.0f}};
    float channel_secondary_pair_storage[NADT_FIXTURE_CAPACITY] = {0.0f};
    float channel_ratio_storage[3][NADT_FIXTURE_CAPACITY] = {{0.0f}};
    int16_t channel_half_storage[NADT_FIXTURE_CAPACITY] = {0};
    goodix_primitives_nadt_channel_state nadt_channel_state = {0};
    nadt_channel_state_initialize(
        &nadt_channel_state, channel_primary_storage,
        channel_primary_pair_storage, channel_secondary_storage,
        channel_secondary_pair_storage, channel_ratio_storage,
        channel_half_storage);
    const goodix_primitives_nadt_channel_input channel_input = {
        .primary = {.feature_value = 8.0f, .average_value = 6.0f},
        .secondary = {.feature_value = 4.0f, .average_value = 2.0f},
    };
    assert(goodix_primitives_nadt_channel_ratio_update(
        &channel_input, 0u, &cadence_one, &nadt_channel_state));
    assert(nadt_channel_state.primary.feature.input.count == 1u &&
           nadt_channel_state.primary.feature.smoothed.count == 1u &&
           nadt_channel_state.primary.feature.residual.count == 1u &&
           nadt_channel_state.primary.feature.residual_smoothed.count == 1u &&
           nadt_channel_state.primary.feature.feature_average.count == 1u &&
           nadt_channel_state.primary.pair_average.count == 1u &&
           nadt_channel_state.primary.pair_average.values[0] == 6.0f &&
           nadt_channel_state.secondary.pair_average.values[0] == 2.0f &&
           nadt_channel_state.primary_ratio.count == 1u &&
           nadt_channel_state.secondary_ratio.count == 1u &&
           nadt_channel_state.combined_ratio.count == 1u &&
           nadt_channel_state.half_primary_input.count == 1u &&
           nadt_channel_state.half_primary_input.values[0] == 4);

    int16_t magnitude_delta_storage[8] = {0};
    int16_t angle_average_storage[8] = {0};
    goodix_primitives_nadt_geometry_state geometry_state = {
        .magnitude = -1.0f,
        .magnitude_delta = {
            .values = magnitude_delta_storage, .count = 0u, .capacity = 8u,
        },
        .angle_accumulator = -1.0f,
        .angle_average = {
            .values = angle_average_storage, .count = 0u, .capacity = 8u,
        },
    };
    const int32_t vector_horizontal[3] = {3, 4, 0};
    assert(goodix_primitives_nadt_vector_geometry_update(
        vector_horizontal, 0u, &cadence_two, &geometry_state,
        square_root_fixture, arc_tangent_fixture));
    assert(geometry_state.magnitude == 5.0f &&
           geometry_state.magnitude_delta.count == 1u &&
           geometry_state.magnitude_delta.values[0] == 0 &&
           geometry_state.angle_accumulator == 90.0f &&
           geometry_state.angle_average.count == 0u);
    const int32_t vector_negative_z[3] = {0, 0, -1};
    assert(goodix_primitives_nadt_vector_geometry_update(
        vector_negative_z, 1u, &cadence_two, &geometry_state,
        square_root_fixture, arc_tangent_fixture));
    assert(geometry_state.magnitude == 1.0f &&
           geometry_state.magnitude_delta.values[1] == -4 &&
           geometry_state.angle_accumulator == 270.0f &&
           geometry_state.angle_average.count == 1u &&
           geometry_state.angle_average.values[0] == 135);

    int32_t accumulation_status = -1;
    assert(goodix_primitives_nadt_accumulation_execute(
        &channel_input, vector_horizontal, 24u, &cadence_one,
        &nadt_channel_state, &geometry_state, square_root_fixture,
        arc_tangent_fixture, &accumulation_status));
    assert(accumulation_status == 4);
    assert(goodix_primitives_nadt_accumulation_execute(
        &channel_input, vector_horizontal, 124u, &cadence_one,
        &nadt_channel_state, &geometry_state, square_root_fixture,
        arc_tangent_fixture, &accumulation_status));
    assert(accumulation_status == 0);
    goodix_primitives_nadt_cadence_configuration invalid_cadence = cadence_one;
    invalid_cadence.ratio_period = 0u;
    assert(!goodix_primitives_nadt_channel_ratio_update(
        &channel_input, 0u, &invalid_cadence, &nadt_channel_state));

    const goodix_primitives_nadt_batch_configuration batch_configuration = {
        .channel_count = 2u,
        .period = 2u,
    };
    goodix_primitives_nadt_channel_accumulator batch_channels[2] = {
        {.reserved = {0u, 0u}, .primary = {2.0f, 20.0f},
         .secondary = {6.0f, 60.0f}},
        {.reserved = {0u, 0u}, .primary = {4.0f, 40.0f},
         .secondary = {8.0f, 80.0f}},
    };
    goodix_primitives_nadt_channel_accumulator batch_accumulators[2] = {
        {.reserved = {1u, 1u}, .primary = {-1.0f, -1.0f},
         .secondary = {-1.0f, -1.0f}},
        {.reserved = {1u, 1u}, .primary = {-1.0f, -1.0f},
         .secondary = {-1.0f, -1.0f}},
    };
    goodix_primitives_nadt_batch_state batch_state = {
        .batch_index = UINT32_MAX,
        .selector = UINT8_MAX,
        .channels = batch_accumulators,
        .channel_capacity = 2u,
        .vector = {-1, -1, -1},
        .aggregate = {
            .reserved = {1u, 1u}, .primary = {-1.0f, -1.0f},
            .secondary = {-1.0f, -1.0f},
        },
    };
    goodix_primitives_nadt_batch_input batch_input = {
        .sample_index = 0u,
        .selector = UINT32_C(0x1234),
        .channels = batch_channels,
        .vector = {10, -10, INT32_MAX},
    };
    int32_t batch_status = -1;
    assert(goodix_primitives_nadt_batch_accumulate(
        &batch_input, &batch_configuration, &batch_state, &batch_status));
    assert(batch_status == 3 && batch_accumulators[0].primary[0] == 2.0f &&
           batch_state.vector[0] == 10 && batch_state.vector[1] == -10 &&
           batch_state.aggregate.primary[0] == 0.0f);
    batch_channels[0].primary[0] = 4.0f;
    batch_channels[0].primary[1] = 40.0f;
    batch_channels[0].secondary[0] = 10.0f;
    batch_channels[0].secondary[1] = 100.0f;
    batch_channels[1].primary[0] = 6.0f;
    batch_channels[1].primary[1] = 60.0f;
    batch_channels[1].secondary[0] = 12.0f;
    batch_channels[1].secondary[1] = 120.0f;
    batch_input.sample_index = 1u;
    batch_input.vector[0] = 14;
    batch_input.vector[1] = -14;
    batch_input.vector[2] = 1;
    assert(goodix_primitives_nadt_batch_accumulate(
        &batch_input, &batch_configuration, &batch_state, &batch_status));
    assert(batch_status == 0 && batch_state.batch_index == 0u &&
           batch_state.selector == UINT8_C(0x34) &&
           batch_accumulators[0].primary[0] == 3.0f &&
           batch_accumulators[0].primary[1] == 30.0f &&
           batch_accumulators[0].secondary[0] == 8.0f &&
           batch_accumulators[0].secondary[1] == 80.0f &&
           batch_accumulators[1].primary[0] == 5.0f &&
           batch_accumulators[1].secondary[0] == 10.0f &&
           batch_state.aggregate.primary[0] == 4.0f &&
           batch_state.aggregate.primary[1] == 0.0f &&
           batch_state.aggregate.secondary[0] == 9.0f &&
           batch_state.aggregate.secondary[1] == 0.0f &&
           batch_state.vector[0] == 12 && batch_state.vector[1] == -12 &&
           batch_state.vector[2] == INT32_MIN / 2);
    batch_input.sample_index = 2u;
    assert(goodix_primitives_nadt_batch_accumulate(
        &batch_input, &batch_configuration, &batch_state, &batch_status));
    assert(batch_status == 3 && batch_accumulators[0].primary[0] == 4.0f &&
           batch_state.vector[0] == 14);
    goodix_primitives_nadt_batch_state short_batch_state = batch_state;
    short_batch_state.channel_capacity = 1u;
    assert(!goodix_primitives_nadt_batch_accumulate(
        &batch_input, &batch_configuration, &short_batch_state,
        &batch_status));

    const goodix_primitives_nadt_output_record encoded_record = {
        .metric = 1.25f,
        .direction = -2,
        .category = 7u,
        .reference = 2.5f,
        .scaled_reference = 1.25f,
        .source_flags = 5u,
        .first_score = 0.125f,
        .second_score = 0.5f,
        .output_metric = 2.25f,
    };
    uint32_t encoded_words[16];
    for (size_t index = 0u; index < 16u; ++index) {
        encoded_words[index] = UINT32_MAX;
    }
    assert(goodix_primitives_nadt_record_encode(
        &encoded_record, encoded_words));
    assert(encoded_words[0] == 12500u &&
           encoded_words[1] == UINT32_C(0xFFFFFFFE) &&
           encoded_words[2] == 7u && encoded_words[3] == 0u &&
           encoded_words[4] == 3u && encoded_words[5] == 125u &&
           encoded_words[6] == 5u && encoded_words[7] == 12500u &&
           encoded_words[8] == 50000u && encoded_words[9] == 0u &&
           encoded_words[10] == 0u && encoded_words[11] == 22500u &&
           encoded_words[12] == 0u && encoded_words[13] == 0u &&
           encoded_words[14] == 0u && encoded_words[15] == 0u);
    goodix_primitives_nadt_output_record invalid_encoded_record =
        encoded_record;
    invalid_encoded_record.metric = -1.0f;
    assert(!goodix_primitives_nadt_record_encode(
        &invalid_encoded_record, encoded_words));

    const goodix_primitives_nadt_source_metrics source_metrics = {
        .second_score = 0.5f,
        .fourth_score = 0.75f,
        .first_score = 0.125f,
        .third_score = 0.25f,
        .source_flags = 3u,
        .category = 9u,
    };
    const goodix_primitives_nadt_reference_metrics reference_metrics = {
        .reference = 2.5f,
        .scaled_reference = 1.25f,
    };
    float preserved_history_values[1] = {42.0f};
    goodix_primitives_nadt_output_record built_record = {
        .primary_count = 11u,
        .history = {
            .values = preserved_history_values, .count = 1u, .capacity = 1u,
            .period = 1u, .phase = 0u, .cursor = 0u, .sum = 42.0f,
        },
        .quality_flags = 0xAAu,
        .secondary_count = 12u,
    };
    assert(goodix_primitives_nadt_output_record_build(
        true, 1.25f, -2, &source_metrics, &reference_metrics, 2.25f,
        &built_record, encoded_words));
    assert(built_record.primary_count == 11u &&
           built_record.history.values == preserved_history_values &&
           built_record.quality_flags == 0xAAu &&
           built_record.secondary_count == 12u &&
           built_record.metric == 1.25f && built_record.direction == -2 &&
           built_record.category == 9u && built_record.baseline == 0.0f &&
           built_record.reference == 2.5f &&
           built_record.scaled_reference == 1.25f &&
           built_record.source_flags == 3u &&
           built_record.first_score == 0.125f &&
           built_record.second_score == 0.5f &&
           built_record.third_score == 0.25f &&
           built_record.fourth_score == 0.75f &&
           built_record.output_metric == 2.25f &&
           encoded_words[12] == 1u);
    assert(goodix_primitives_nadt_output_record_build(
        false, 1.25f, -2, &source_metrics, NULL, 2.25f,
        &built_record, encoded_words));
    assert(built_record.reference == 0.0f &&
           built_record.scaled_reference == 0.0f &&
           encoded_words[4] == 0u && encoded_words[5] == 0u &&
           encoded_words[12] == 1u);

    const goodix_primitives_nadt_quality_configuration quality_configuration = {
        .rounded_value_threshold = 10u,
        .alternate_history_length = 2,
        .default_history_length = 3,
        .alternate_tolerance = 1u,
        .default_tolerance = 2u,
    };
    float quality_history_values[4] = {0.0f};
    goodix_primitives_nadt_output_record quality_record = {
        .primary_count = 0u,
        .history = {
            .values = quality_history_values, .count = 0u, .capacity = 4u,
            .period = 1u, .phase = 0u, .cursor = 0u, .sum = 0.0f,
        },
        .quality_flags = 0u,
        .secondary_count = 0u,
    };
    assert(goodix_primitives_nadt_output_record_quality_update(
        &quality_configuration, 0u, 1.0f, &quality_record));
    assert(quality_record.primary_count == 1u &&
           quality_record.secondary_count == 1u &&
           quality_record.quality_flags == UINT8_C(0x84));
    assert(goodix_primitives_nadt_output_record_quality_update(
        &quality_configuration, 0u, 2.0f, &quality_record));
    assert(quality_record.primary_count == 2u &&
           quality_record.quality_flags == UINT8_C(0x84));
    assert(goodix_primitives_nadt_output_record_quality_update(
        &quality_configuration, 0u, 3.0f, &quality_record));
    assert(quality_record.primary_count == 3u &&
           quality_record.secondary_count == 3u &&
           quality_record.quality_flags == 0u);
    assert(goodix_primitives_nadt_output_record_quality_update(
        &quality_configuration, 0u, 9.5f, &quality_record));
    assert(quality_record.primary_count == 4u &&
           quality_record.secondary_count == 4u &&
           quality_record.quality_flags == UINT8_C(0x80));
    assert(goodix_primitives_nadt_output_record_quality_update(
        &quality_configuration, 1u, 9.5f, &quality_record));
    assert(quality_record.primary_count == 0u &&
           quality_record.secondary_count == 0u &&
           quality_record.quality_flags == UINT8_C(0x04));
    quality_record.primary_count = UINT8_MAX;
    quality_record.secondary_count = UINT8_MAX;
    assert(goodix_primitives_nadt_output_record_quality_update(
        &quality_configuration, 0u, 9.5f, &quality_record));
    assert(quality_record.primary_count == UINT8_MAX &&
           quality_record.secondary_count == UINT8_MAX);

    float analysis_primary_values[125];
    float analysis_secondary_values[125];
    for (size_t index = 0u; index < 125u; ++index) {
        analysis_primary_values[index] = 0.0f;
        analysis_secondary_values[index] = 0.0f;
    }
    analysis_primary_values[124] = 1.0f;
    analysis_secondary_values[124] = 1.0f;
    float analysis_primary_average_values[2] = {2.0f, 4.0f};
    float analysis_secondary_average_values[2] = {6.0f, 8.0f};
    goodix_primitives_nadt_channel_state analysis_state = {0};
    analysis_state.primary_ratio =
        (goodix_primitives_decimated_float_window) {
            .values = analysis_primary_values, .count = 125u,
            .capacity = 125u, .period = 1u, .phase = 0u, .cursor = 0u,
            .sum = 0.0f,
        };
    analysis_state.secondary_ratio =
        (goodix_primitives_decimated_float_window) {
            .values = analysis_secondary_values, .count = 125u,
            .capacity = 125u, .period = 1u, .phase = 0u, .cursor = 0u,
            .sum = 0.0f,
        };
    analysis_state.primary.pair_average =
        (goodix_primitives_decimated_float_window) {
            .values = analysis_primary_average_values, .count = 2u,
            .capacity = 2u, .period = 1u, .phase = 0u, .cursor = 0u,
            .sum = 6.0f,
        };
    analysis_state.secondary.pair_average =
        (goodix_primitives_decimated_float_window) {
            .values = analysis_secondary_average_values, .count = 2u,
            .capacity = 2u, .period = 1u, .phase = 0u, .cursor = 0u,
            .sum = 14.0f,
        };
    const int32_t analysis_events[2] = {0, 1};
    const goodix_primitives_event_pair_source analysis_event_source = {
        .primary = analysis_events,
        .primary_count = 2u,
        .primary_start = 0u,
        .secondary = NULL,
        .secondary_count = 0u,
        .secondary_start = 0u,
    };
    int32_t analysis_primary_indices[2] = {-1, -1};
    int32_t analysis_secondary_indices[2] = {-1, -1};
    float analysis_sort_scratch[125] = {0.0f};
    int8_t analysis_mask_scratch[125] = {0};
    goodix_primitives_nadt_channel_analysis channel_analysis = {0};
    assert(goodix_primitives_nadt_channel_analysis_execute(
        &analysis_state, &analysis_event_source, 5, 10u,
        analysis_primary_indices, analysis_secondary_indices, 2u,
        analysis_sort_scratch, 125u, analysis_mask_scratch, 125u,
        square_root_fixture, &channel_analysis));
    assert(analysis_primary_indices[0] == 0 &&
           analysis_primary_indices[1] == 1);
    assert(analysis_secondary_indices[0] == 0 &&
           analysis_secondary_indices[1] == 1);
    assert(channel_analysis.primary_difference.nonuniform_mask_count == 0);
    assert(channel_analysis.primary_difference.mean_difference == 0.0f);
    assert(channel_analysis.primary_difference.relative_variance == -1.0f);
    assert(channel_analysis.primary_difference.accepted_count == 0u);
    assert(channel_analysis.secondary_difference.mean_difference == 0.0f);
    assert(channel_analysis.primary_average == 3.0f);
    assert(channel_analysis.secondary_average == 7.0f);
    assert(channel_analysis.cosine_percent == 100u);
    analysis_state.primary_ratio.count = 124u;
    assert(!goodix_primitives_nadt_channel_analysis_execute(
        &analysis_state, &analysis_event_source, 5, 10u,
        analysis_primary_indices, analysis_secondary_indices, 2u,
        analysis_sort_scratch, 125u, analysis_mask_scratch, 125u,
        square_root_fixture, &channel_analysis));

    int16_t descriptor_values[4] = {-4, 2, 8, 10};
    const goodix_primitives_buffer_descriptor i16_descriptor = {
        .data = descriptor_values, .count = 4u, .capacity = 4u,
    };
    int16_t descriptor_mean = 0;
    assert(goodix_primitives_i16_descriptor_mean(
        &i16_descriptor, &descriptor_mean));
    assert(descriptor_mean == 4);

    int16_t nadt_primary_values[4] = {-4, 0, 2, 6};
    int16_t nadt_secondary_values[2] = {2, 4};
    const goodix_primitives_buffer_descriptor nadt_primary = {
        .data = nadt_primary_values, .count = 4u, .capacity = 4u,
    };
    const goodix_primitives_buffer_descriptor nadt_secondary = {
        .data = nadt_secondary_values, .count = 2u, .capacity = 2u,
    };
    const goodix_primitives_nadt_threshold_configuration nadt_threshold = {
        .maximum_threshold = 4u,
        .minimum_threshold = 2u,
        .deviation_factor = 1u,
    };
    const goodix_primitives_nadt_summary_context nadt_summary_context = {
        .configuration = &nadt_threshold,
        .primary = &nadt_primary,
        .secondary = &nadt_secondary,
        .downstream_first = (uintptr_t)UINT32_C(0x11223344),
        .downstream_second = (uintptr_t)UINT32_C(0x55667788),
    };
    goodix_primitives_nadt_primary_summary nadt_primary_summary = {0};
    assert(goodix_primitives_nadt_sample_statistics(
        &nadt_threshold, &nadt_primary, square_root_fixture,
        &nadt_primary_summary));
    assert(nadt_primary_summary.mean == 1 &&
           nadt_primary_summary.threshold == 3u &&
           nadt_primary_summary.outlier_count == 2u);
    goodix_primitives_nadt_sample_summary nadt_summary = {0};
    int32_t nadt_summary_result = INT32_C(-1);
    assert(goodix_primitives_nadt_sample_summary_build(
        &nadt_summary_context, square_root_fixture, &nadt_summary,
        &nadt_summary_result));
    assert(nadt_summary_result == 0 && nadt_summary.mean == 1 &&
           nadt_summary.threshold == 3u &&
           nadt_summary.outlier_count == 2u &&
           nadt_summary.secondary_mean == 3);
    assert(goodix_primitives_nadt_summary_dispatch(
        (uintptr_t)UINT32_C(0xA1B2C3D4),
        (uintptr_t)UINT32_C(0x10203040), &nadt_summary,
        &nadt_summary_context, square_root_fixture, five_word_operation,
        &nadt_summary_result));
    assert(nadt_summary_result == INT32_C(-29));
    assert(five_word_arguments[0] == nadt_summary_context.downstream_first &&
           five_word_arguments[1] == nadt_summary_context.downstream_second &&
           five_word_arguments[2] == (uintptr_t)UINT32_C(0xA1B2C3D4) &&
           five_word_arguments[3] == (uintptr_t)UINT32_C(0x10203040) &&
           five_word_arguments[4] == (uintptr_t)&nadt_summary);
    assert(!goodix_primitives_nadt_sample_statistics(
        &nadt_threshold, NULL, square_root_fixture,
        &nadt_primary_summary));
    assert(!goodix_primitives_nadt_sample_summary_build(
        &nadt_summary_context, NULL, &nadt_summary, &nadt_summary_result));
    assert(!goodix_primitives_nadt_summary_dispatch(
        0u, 0u, &nadt_summary, &nadt_summary_context,
        square_root_fixture, NULL, &nadt_summary_result));

    const float weighted_coefficients[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    const float weighted_history[3] = {10.0f, 20.0f, 30.0f};
    float weighted_sum = 0.0f;
    assert(goodix_primitives_reverse_clamped_weighted_sum(
        weighted_coefficients, 4u, weighted_history, 3u, 3u,
        &weighted_sum));
    assert(weighted_sum == 140.0f);
    assert(goodix_primitives_reverse_clamped_weighted_sum(
        weighted_coefficients, 4u, NULL, 0u, 0u, &weighted_sum));
    assert(weighted_sum == 0.0f);
    assert(!goodix_primitives_reverse_clamped_weighted_sum(
        weighted_coefficients, 4u, weighted_history, 2u, 3u,
        &weighted_sum));

    goodix_primitives_extrema_history extrema = {0};
    int32_t extrema_transition = 0;
    assert(goodix_primitives_extrema_history_update(
        &extrema, 10, 3, &extrema_transition));
    assert(extrema_transition == 0 && extrema.extremum == 10 &&
           extrema.sample_count == 1 && extrema.descending == 0u);
    assert(goodix_primitives_extrema_history_update(
        &extrema, 12, 3, &extrema_transition));
    assert(extrema_transition == 0 && extrema.extremum == 12 &&
           extrema.extremum_count == 1 && extrema.sample_count == 2);
    assert(goodix_primitives_extrema_history_update(
        &extrema, 8, 3, &extrema_transition));
    assert(extrema_transition == 1 && extrema.descending == 1u &&
           extrema.emitted_count == 1 && extrema.extremum_count == 2 &&
           extrema.sample_count == 3);
    assert(goodix_primitives_extrema_history_update(
        &extrema, 5, 3, &extrema_transition));
    assert(extrema_transition == 0 && extrema.extremum == 5 &&
           extrema.extremum_count == 3 && extrema.sample_count == 4);
    assert(goodix_primitives_extrema_history_update(
        &extrema, 9, 3, &extrema_transition));
    assert(extrema_transition == -1 && extrema.descending == 0u &&
           extrema.emitted_count == 3 && extrema.extremum_count == 4 &&
           extrema.sample_count == 5);
    extrema.sample_count = INT32_MAX;
    assert(goodix_primitives_extrema_history_update(
        &extrema, 9, 3, &extrema_transition));
    assert(extrema.sample_count == INT32_MIN);

    /* Array transformation leaves at 0x29394, 0x4FDB8, and 0x66AB2. */
    float range_rows[6] = {1.0f, 3.0f, 5.0f, 2.0f, 2.0f, 2.0f};
    assert(goodix_primitives_normalize_rows_by_range(range_rows, 2u, 3u));
    assert(range_rows[0] == 0.25f && range_rows[1] == 0.75f &&
           range_rows[2] == 1.25f && range_rows[3] == 2.0f &&
           range_rows[4] == 2.0f && range_rows[5] == 2.0f);
    assert(!goodix_primitives_normalize_rows_by_range(range_rows, 2u, 0u));

    uint8_t record_storage[64] = {0};
    uint8_t record_a[32];
    uint8_t record_b[32];
    uint8_t record_c[32];
    memset(record_a, UINT8_C(0x11), sizeof(record_a));
    memset(record_b, UINT8_C(0x22), sizeof(record_b));
    memset(record_c, UINT8_C(0x33), sizeof(record_c));
    goodix_primitives_record32_history record_history = {
        .records = record_storage, .count = 0u, .capacity = 2u,
    };
    assert(goodix_primitives_record32_history_push(
        &record_history, record_a));
    assert(goodix_primitives_record32_history_push(
        &record_history, record_b));
    assert(goodix_primitives_record32_history_push(
        &record_history, record_c));
    assert(record_history.count == 2u);
    for (size_t byte = 0u; byte < 32u; ++byte) {
        assert(record_storage[byte] == UINT8_C(0x22));
        assert(record_storage[32u + byte] == UINT8_C(0x33));
    }

    uint8_t hr_record_storage[128] = {0};
    goodix_primitives_record32_history hr_record_history = {
        .records = hr_record_storage, .count = 2u, .capacity = 4u,
    };
    goodix_primitives_hr_event_record hr_first = {
        .prefix = {UINT8_C(0x11)}, .center = 8.0f, .eligible = 1,
        .suffix = {UINT8_C(0x12)},
    };
    goodix_primitives_hr_event_record hr_second = {
        .prefix = {UINT8_C(0x21)}, .center = 12.0f, .eligible = 7,
        .suffix = {UINT8_C(0x22)},
    };
    assert(goodix_primitives_hr_rebalance_record_pair(
        0.1f, 10.0f, 3, 2, &hr_record_history, &hr_first,
        &hr_second));
    assert(hr_record_history.count == 2u);
    assert(hr_first.center == 10.0f && hr_second.center == 10.0f);
    goodix_primitives_hr_event_record hr_stored_first;
    goodix_primitives_hr_event_record hr_stored_second;
    memcpy(&hr_stored_first, hr_record_storage, sizeof(hr_stored_first));
    memcpy(&hr_stored_second, hr_record_storage + 32u,
           sizeof(hr_stored_second));
    assert(hr_stored_first.center == 10.0f &&
           hr_stored_first.eligible == 1);
    assert(hr_stored_second.center == 10.0f &&
           hr_stored_second.eligible == 7);

    memset(hr_record_storage, UINT8_C(0x5A), sizeof(hr_record_storage));
    hr_record_history.count = 2u;
    hr_first.center = 8.0f;
    hr_second.center = 12.0f;
    assert(goodix_primitives_hr_rebalance_record_pair(
        0.1f, 10.0f, 1, 2, &hr_record_history, &hr_first,
        &hr_second));
    assert(hr_record_history.count == 2u && hr_first.center == 8.0f &&
           hr_second.center == 12.0f);
    memcpy(&hr_stored_second, hr_record_storage + 32u,
           sizeof(hr_stored_second));
    assert(hr_stored_second.center == 12.0f &&
           hr_stored_second.eligible == 7);

    union {
        uint32_t bits;
        float value;
    } hr_quiet_nan = {.bits = UINT32_C(0x7FC00000)};
    hr_record_history.count = 1u;
    hr_first.center = hr_quiet_nan.value;
    assert(goodix_primitives_hr_rebalance_record_pair(
        0.1f, 10.0f, 3, 2, &hr_record_history, &hr_first,
        &hr_second));
    assert(hr_record_history.count == 1u);
    assert(!goodix_primitives_hr_rebalance_record_pair(
        0.1f, 10.0f, 3, 2, NULL, &hr_first, &hr_second));

    const uint8_t row_mask[2] = {UINT8_C(0x30), UINT8_C(0x7D)};
    uint16_t selected_label = 0u;
    assert(goodix_primitives_select_mask_row(
        row_mask, sizeof(row_mask), 4u, 2u, 4u, &selected_label));
    assert(selected_label == 3u);
    assert(!goodix_primitives_select_mask_row(
        row_mask, 1u, 4u, 2u, 4u, &selected_label));
    assert(!goodix_primitives_select_mask_row(
        row_mask, sizeof(row_mask), 4u, 0u, 4u, &selected_label));

    float logistic = 0.0f;
    assert(goodix_primitives_logistic_score(
        5.0f, 4.0f, 2.0f, 3.0f, exp_fixture, &logistic));
    assert(logistic == 50.0f);

    const goodix_primitives_nadt_channel_quality_configuration
        channel_quality_configuration = {
        .primary_level_threshold = 10u,
        .secondary_level_threshold = 20u,
        .metric_limit_percent = 50u,
        .quality_threshold = 5u,
        .flag_mask = UINT8_C(0x3F),
    };
    goodix_primitives_nadt_channel_quality_summary channel_quality_summary = {
        .primary_level = 11u,
        .secondary_level = 21,
    };
    goodix_primitives_nadt_channel_quality_record channel_quality_record = {
        .primary_activity = 1,
        .secondary_activity = 0,
        .primary_metric = 0.25f,
        .secondary_metric = 0.4f,
        .primary_valid = false,
        .secondary_valid = true,
        .quality = 4,
        .flags = UINT8_C(0xFF),
        .score = UINT8_C(0xFF),
    };
    quality_exp_calls = 0u;
    assert(goodix_primitives_nadt_channel_quality_update(
        &channel_quality_configuration, &channel_quality_summary,
        &channel_quality_record,
        quality_exp_fixture));
    assert(quality_exp_calls == 3u &&
           channel_quality_record.flags == UINT8_C(0x2F) &&
           channel_quality_record.score == UINT8_C(65));

    goodix_primitives_nadt_channel_quality_configuration
        masked_channel_quality_configuration = channel_quality_configuration;
    masked_channel_quality_configuration.flag_mask = UINT8_C(0x15);
    channel_quality_summary.secondary_level = -1;
    channel_quality_record.primary_metric = -1.0f;
    quality_exp_calls = 0u;
    assert(goodix_primitives_nadt_channel_quality_update(
        &masked_channel_quality_configuration, &channel_quality_summary,
        &channel_quality_record,
        quality_exp_fixture));
    assert(channel_quality_record.flags == UINT8_C(0x15) &&
           channel_quality_record.score == UINT8_C(65));
    assert(!goodix_primitives_nadt_channel_quality_update(
        &channel_quality_configuration, &channel_quality_summary,
        &channel_quality_record, NULL));

    goodix_primitives_noop_a();
    goodix_primitives_noop_b();
    assert(goodix_primitives_zero_a() == 0);
    assert(goodix_primitives_zero_b() == 0);
    const uint32_t pair[2] = {7u, 19u};
    assert(goodix_primitives_second_word(pair) == 19u);
    assert(goodix_primitives_transformed_differs(4, add_one));
    static const struct {
        uint32_t input;
        uint32_t encoded;
    } integrity_cases[] = {
        {UINT32_C(0x00000000), UINT32_C(0x00000000)},
        {UINT32_C(0x00000001), UINT32_C(0x00000000)},
        {UINT32_C(0x00000002), UINT32_C(0x00000003)},
        {UINT32_C(0x00000003), UINT32_C(0x00000003)},
        {UINT32_C(0x00000004), UINT32_C(0x00000005)},
        {UINT32_C(0x00000005), UINT32_C(0x00000005)},
        {UINT32_C(0x00000006), UINT32_C(0x00000006)},
        {UINT32_C(0x00000007), UINT32_C(0x00000006)},
        {UINT32_C(0x00123456), UINT32_C(0x00123457)},
        {UINT32_C(0x00ABCDEF), UINT32_C(0x00ABCDEE)},
        {UINT32_C(0x80FFFFFF), UINT32_C(0x80FFFFFF)},
    };
    for (size_t index = 0u;
            index < sizeof(integrity_cases) / sizeof(integrity_cases[0]);
            ++index) {
        assert(goodix_primitives_integrity_encode(
                   integrity_cases[index].input) ==
               integrity_cases[index].encoded);
        assert(goodix_primitives_integrity_invalid(
                   integrity_cases[index].input) ==
               (integrity_cases[index].input !=
                integrity_cases[index].encoded));
    }
    static const struct {
        uint16_t input;
        uint32_t five_ten;
        uint32_t six_nine;
    } packed_cases[] = {
        {UINT16_C(0x0000), UINT32_C(0x00000000), UINT32_C(0x00000000)},
        {UINT16_C(0x8000), UINT32_C(0x80000000), UINT32_C(0x80000000)},
        {UINT16_C(0x0001), UINT32_C(0x33800000), UINT32_C(0x2C000000)},
        {UINT16_C(0x3C00), UINT32_C(0x3F800000), UINT32_C(0x3F000000)},
        {UINT16_C(0x4000), UINT32_C(0x40000000), UINT32_C(0x40000000)},
        {UINT16_C(0xFFFF), UINT32_C(0xC7FFE000), UINT32_C(0xCFFFC000)},
    };
    for (size_t index = 0u;
            index < sizeof(packed_cases) / sizeof(packed_cases[0]); ++index) {
        assert(goodix_primitives_packed_5_10_to_f32_bits(
                   packed_cases[index].input) == packed_cases[index].five_ten);
        assert(goodix_primitives_packed_6_9_to_f32_bits(
                   packed_cases[index].input) == packed_cases[index].six_nine);
    }
    static const struct {
        uint32_t input;
        uint16_t packed;
    } reverse_packed_cases[] = {
        {UINT32_C(0x00000000), UINT16_C(0x0000)},
        {UINT32_C(0x80000000), UINT16_C(0x8000)},
        {UINT32_C(0x2F800000), UINT16_C(0x0080)},
        {UINT32_C(0x3F000000), UINT16_C(0x3C00)},
        {UINT32_C(0x3F800000), UINT16_C(0x3E00)},
        {UINT32_C(0x40000000), UINT16_C(0x4000)},
        {UINT32_C(0x7F800000), UINT16_C(0x7E00)},
        {UINT32_C(0x7FC00000), UINT16_C(0x7F00)},
    };
    for (size_t index = 0u;
            index < sizeof(reverse_packed_cases) /
                        sizeof(reverse_packed_cases[0]);
            ++index) {
        assert(goodix_primitives_f32_bits_to_packed_6_9(
                   reverse_packed_cases[index].input) ==
               reverse_packed_cases[index].packed);
    }
    static const struct {
        uint32_t input;
        uint16_t packed;
    } reverse_half_cases[] = {
        {UINT32_C(0x00000000), UINT16_C(0x0000)},
        {UINT32_C(0x80000000), UINT16_C(0x8000)},
        {UINT32_C(0x33800000), UINT16_C(0x0001)},
        {UINT32_C(0x3F800000), UINT16_C(0x3C00)},
        {UINT32_C(0xC0000000), UINT16_C(0xC000)},
        {UINT32_C(0x477FE000), UINT16_C(0x7BFF)},
        {UINT32_C(0x7F800000), UINT16_C(0x7C00)},
        {UINT32_C(0x7FC00000), UINT16_C(0x7E00)},
    };
    for (size_t index = 0u;
            index < sizeof(reverse_half_cases) /
                        sizeof(reverse_half_cases[0]);
            ++index) {
        assert(goodix_primitives_f32_bits_to_packed_5_10(
                   reverse_half_cases[index].input) ==
               reverse_half_cases[index].packed);
    }
    uint16_t spo2_packed[GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES];
    float spo2_workspace[GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES];
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES; ++index) {
        spo2_packed[index] = (uint16_t)(index * 173u);
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES; ++index) {
        spo2_workspace[index] = -123.0f;
    }
    assert(goodix_primitives_spo2_expand_packed_triplicate(
        0u, 1u, spo2_packed,
        GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES, spo2_workspace,
        GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES));
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_SPO2_PACKED_PREFIX_VALUES; ++index) {
        assert(spo2_workspace[index] == -123.0f);
    }
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_COUNT; ++bank) {
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES; ++index) {
            union {
                float value;
                uint32_t bits;
            } observed = {
                .value = spo2_workspace[
                    GOODIX_PRIMITIVES_SPO2_PACKED_PREFIX_VALUES +
                    bank * GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES + index],
            };
            assert(observed.bits ==
                   goodix_primitives_packed_6_9_to_f32_bits(
                       spo2_packed[index]));
        }
    }
    spo2_workspace[GOODIX_PRIMITIVES_SPO2_PACKED_PREFIX_VALUES] = 77.0f;
    assert(goodix_primitives_spo2_expand_packed_triplicate(
        1u, 1u, NULL, 0u, NULL, 0u));
    assert(spo2_workspace[GOODIX_PRIMITIVES_SPO2_PACKED_PREFIX_VALUES] ==
           77.0f);
    assert(!goodix_primitives_spo2_expand_packed_triplicate(
        0u, 1u, spo2_packed,
        GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES, spo2_workspace,
        GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES - 1u));
    uint16_t spo2_packed_banks
        [GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT]
        [GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES];
    const uint16_t *spo2_bank_bindings
        [GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT];
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT; ++bank) {
        spo2_bank_bindings[bank] = spo2_packed_banks[bank];
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES; ++index) {
            spo2_packed_banks[bank][index] =
                (uint16_t)(bank * 1000u + index * 173u);
        }
    }
    assert(goodix_primitives_spo2_expand_packed_banks(
        spo2_bank_bindings, spo2_workspace,
        GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES));
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT; ++bank) {
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES; ++index) {
            union {
                float value;
                uint32_t bits;
            } observed = {
                .value = spo2_workspace[
                    bank * GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES + index],
            };
            assert(observed.bits ==
                   goodix_primitives_packed_6_9_to_f32_bits(
                       spo2_packed_banks[bank][index]));
        }
    }
    spo2_workspace[0] = 77.0f;
    spo2_bank_bindings[3] = NULL;
    assert(!goodix_primitives_spo2_expand_packed_banks(
        spo2_bank_bindings, spo2_workspace,
        GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES));
    assert(spo2_workspace[0] == 77.0f);
    spo2_bank_bindings[3] = spo2_packed_banks[3];
    assert(!goodix_primitives_spo2_expand_packed_banks(
        spo2_bank_bindings, spo2_workspace,
        GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES - 1u));

    float spo2_spectral_float_values[
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS *
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES] = {0.0f};
    uint16_t spo2_spectral_packed
        [GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS]
        [GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES] = {{0u}};
    goodix_primitives_spo2_spectral_source spo2_spectral_source = {
        .transformed_values = spo2_spectral_float_values,
        .transformed_value_count =
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS *
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES,
    };
    static const uint32_t spo2_spectral_impulse_bits[] = {
        UINT32_C(0x3F800000), UINT32_C(0x40000000),
        UINT32_C(0x40400000), UINT32_C(0x40800000),
    };
    for (size_t channel = 0u;
            channel < GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS;
            ++channel) {
        spo2_spectral_float_values[
            channel * GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES +
            (channel == 0u
                 ? GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES - 1u
                 : channel)] = channel == 0u ? 2.5f : (float)(channel + 1u);
        spo2_spectral_source.packed_channels[channel] =
            spo2_spectral_packed[channel];
        spo2_spectral_source.packed_channel_counts[channel] =
            GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES;
        spo2_spectral_packed[channel][1] = UINT16_C(0x7FFF);
        spo2_spectral_packed[channel][
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_VALUES - 1u] =
            goodix_primitives_f32_bits_to_packed_6_9(
                spo2_spectral_impulse_bits[channel]);
    }
    goodix_primitives_spo2_spectral_workspace spo2_spectral_workspace;
    goodix_primitives_spo2_spectral_result spo2_spectral_result;
    assert(goodix_primitives_spo2_normalized_spectra_prepare(
        &spo2_spectral_source, square_root_fixture,
        &spo2_spectral_workspace, &spo2_spectral_result));
    for (size_t channel = 0u;
            channel < GOODIX_PRIMITIVES_SPO2_SPECTRAL_CHANNELS; ++channel) {
        assert(spo2_spectral_result.channels[channel][0] == 0.0f);
        float spectral_maximum = 0.0f;
        for (size_t bin = 1u;
                bin < GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES; ++bin) {
            const float value = spo2_spectral_result.channels[channel][bin];
            assert(value == value && value >= 0.0f && value <= 1.000001f);
            if (spectral_maximum < value) {
                spectral_maximum = value;
            }
        }
        assert(spectral_maximum >= 0.999999f);
    }
    for (size_t bin = 0u;
            bin < GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES; ++bin) {
        assert(spo2_spectral_result.channels[4][bin] ==
               spo2_spectral_result.channels[0][bin]);
    }
    spo2_spectral_result.channels[0][0] = 77.0f;
    spo2_spectral_source.transformed_value_count -= 1u;
    assert(!goodix_primitives_spo2_normalized_spectra_prepare(
        &spo2_spectral_source, square_root_fixture,
        &spo2_spectral_workspace, &spo2_spectral_result));
    assert(spo2_spectral_result.channels[0][0] == 77.0f);
    spo2_spectral_source.transformed_value_count += 1u;
    spo2_spectral_source.packed_channel_counts[3] =
        GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_VALUES - 1u;
    assert(!goodix_primitives_spo2_normalized_spectra_prepare(
        &spo2_spectral_source, square_root_fixture,
        &spo2_spectral_workspace, &spo2_spectral_result));
    spo2_spectral_source.packed_channel_counts[3] =
        GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES;
    assert(!goodix_primitives_spo2_normalized_spectra_prepare(
        &spo2_spectral_source, NULL,
        &spo2_spectral_workspace, &spo2_spectral_result));
    const uint32_t transform_source[3] = {
        UINT32_C(0x12345678), UINT32_C(0xABCDEF01), UINT32_C(0x0000BEEF),
    };
    uint16_t transform_output[3] = {0u, 0u, 0u};
    assert(goodix_primitives_u32_to_u16_transform(
        transform_output, transform_source, 3u, low_half));
    assert(transform_output[0] == UINT16_C(0x5678));
    assert(transform_output[1] == UINT16_C(0xEF01));
    assert(transform_output[2] == UINT16_C(0xBEEF));
    assert(!goodix_primitives_u32_to_u16_transform(
        NULL, transform_source, 3u, low_half));
    int32_t transformed = 8;
    assert(goodix_primitives_transform_in_place(&transformed, add_one));
    assert(transformed == 9);
    assert(goodix_primitives_initialize_status(initialize_ok) == 0);
    assert(goodix_primitives_initialize_status(NULL) == -1);

    float float_values[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    goodix_primitives_float_buffer float_buffer = {
        float_values, 2u, 4u,
    };
    assert(goodix_primitives_is_evenly_divisible(12u, 4u));
    assert(!goodix_primitives_is_evenly_divisible(12u, 0u));
    assert(!goodix_primitives_float_buffer_full(&float_buffer));
    float_buffer.count = 4u;
    assert(goodix_primitives_float_buffer_full(&float_buffer));
    assert(goodix_primitives_float_buffer_get(&float_buffer, 2u, -1.0f) ==
           3.0f);
    assert(goodix_primitives_float_buffer_get(&float_buffer, 4u, -1.0f) ==
           -1.0f);
    float buffer_mean = -1.0f;
    assert(goodix_primitives_float_buffer_mean(&float_buffer, &buffer_mean));
    assert(buffer_mean == 2.5f);
    float_buffer.count = 0u;
    buffer_mean = 7.0f;
    assert(!goodix_primitives_float_buffer_mean(&float_buffer, &buffer_mean));
    assert(buffer_mean == 7.0f);
    assert(!goodix_primitives_float_buffer_mean(NULL, &buffer_mean));
    float variance = 0.0f;
    assert(goodix_primitives_sample_variance(float_values, 4u, &variance));
    assert(variance > 1.6666f && variance < 1.6667f);
    float standard_deviation = 0.0f;
    assert(goodix_primitives_sample_standard_deviation(
        float_values, 4u, square_root_fixture, &standard_deviation));
    assert(standard_deviation > 1.2909f && standard_deviation < 1.2911f);
    float hr_outlier_values[125] = {0.0f};
    hr_outlier_values[50] = 10.0f;
    hr_outlier_values[100] = -10.0f;
    hr_outlier_values[124] = 20.0f;
    const goodix_primitives_float_buffer hr_outlier_buffer = {
        hr_outlier_values, 125u, 125u,
    };
    uint32_t hr_outliers = UINT32_MAX;
    uint32_t hr_tail_outliers = UINT32_MAX;
    assert(goodix_primitives_hr_count_mean_outliers(
        &hr_outlier_buffer, 125u, 5.0f, 1.0f, 1.0f,
        square_root_fixture, &hr_outliers, &hr_tail_outliers));
    assert(hr_outliers == 3u && hr_tail_outliers == 2u);
    union {
        uint32_t bits;
        float value;
    } hr_threshold_nan = {.bits = UINT32_C(0x7FC00000)};
    assert(goodix_primitives_hr_count_mean_outliers(
        &hr_outlier_buffer, 125u, hr_threshold_nan.value, 1.0f, 1.0f,
        square_root_fixture, &hr_outliers, &hr_tail_outliers));
    assert(hr_outliers == 0u && hr_tail_outliers == 0u);
    assert(!goodix_primitives_hr_count_mean_outliers(
        &hr_outlier_buffer, 126u, 5.0f, 1.0f, 1.0f,
        square_root_fixture, &hr_outliers, &hr_tail_outliers));
    const int16_t i16_deviation_values[4] = {1, 2, 3, 4};
    assert(goodix_primitives_i16_sample_standard_deviation(
        i16_deviation_values, 4u, square_root_fixture,
        &standard_deviation));
    assert(standard_deviation > 1.2909f && standard_deviation < 1.2911f);
    const int16_t i16_constant_values[3] = {-7, -7, -7};
    assert(goodix_primitives_i16_sample_standard_deviation(
        i16_constant_values, 3u, square_root_fixture,
        &standard_deviation));
    assert(standard_deviation == 0.0f);
    standard_deviation = 9.0f;
    assert(goodix_primitives_i16_sample_standard_deviation(
        NULL, 1u, NULL, &standard_deviation));
    assert(standard_deviation == 0.0f);
    assert(!goodix_primitives_i16_sample_standard_deviation(
        i16_deviation_values, 4u, NULL, &standard_deviation));
    const uint8_t u8_deviation_values[4] = {0u, 2u, 4u, 6u};
    assert(goodix_primitives_u8_population_standard_deviation(
        u8_deviation_values, 4u, square_root_fixture,
        &standard_deviation));
    assert(standard_deviation > 2.2360f && standard_deviation < 2.2361f);
    standard_deviation = 7.0f;
    assert(!goodix_primitives_u8_population_standard_deviation(
        u8_deviation_values, 0u, square_root_fixture,
        &standard_deviation));
    assert(standard_deviation == 7.0f);

    const float cosine_left[2] = {1.0f, 2.0f};
    const float cosine_same[2] = {2.0f, 4.0f};
    const float cosine_opposite[2] = {-2.0f, -4.0f};
    float similarity = 0.0f;
    assert(goodix_primitives_positive_cosine_similarity(
        cosine_left, cosine_same, 2u, square_root_fixture, &similarity));
    assert(similarity > 0.9999f && similarity < 1.0001f);
    assert(goodix_primitives_positive_cosine_similarity(
        cosine_left, cosine_opposite, 2u, square_root_fixture,
        &similarity));
    assert(similarity == 0.0f);
    const float cosine_zero[2] = {0.0f, 0.0f};
    assert(goodix_primitives_positive_cosine_similarity(
        cosine_left, cosine_zero, 2u, square_root_fixture, &similarity));
    assert(similarity == 0.0f);
    assert(goodix_primitives_positive_cosine_similarity(
        NULL, NULL, 0u, square_root_fixture, &similarity));
    assert(similarity == 0.0f);
    const float strided_values[] = {
        1.0f, 99.0f, 2.0f, 99.0f, 3.0f, 99.0f, 4.0f,
    };
    assert(goodix_primitives_strided_sample_standard_deviation(
        strided_values, 7u, 2u, 4u, square_root_fixture,
        &standard_deviation));
    assert(standard_deviation > 1.2909f && standard_deviation < 1.2911f);
    assert(!goodix_primitives_strided_sample_standard_deviation(
        strided_values, 6u, 2u, 4u, square_root_fixture,
        &standard_deviation));
    assert(!goodix_primitives_strided_sample_standard_deviation(
        strided_values, 7u, 2u, 1u, square_root_fixture,
        &standard_deviation));
    float_buffer.count = 4u;
    assert(goodix_primitives_float_buffer_standard_deviation(
        &float_buffer, square_root_fixture, &standard_deviation));
    assert(goodix_primitives_float_buffer_incremental_standard_deviation(
        &float_buffer, square_root_fixture, &standard_deviation));
    assert(standard_deviation > 1.2909f && standard_deviation < 1.2911f);
    float_buffer.count = 1u;
    standard_deviation = 9.0f;
    assert(!goodix_primitives_float_buffer_standard_deviation(
        &float_buffer, square_root_fixture, &standard_deviation));
    assert(standard_deviation == 9.0f);
    assert(!goodix_primitives_sample_variance(float_values, 1u, &variance));
    assert(!goodix_primitives_sample_standard_deviation(
        float_values, 4u, NULL, &standard_deviation));
    assert(goodix_primitives_sample_variance_or_zero(
        float_values, 4u, &variance));
    assert(variance > 1.6666f && variance < 1.6667f);
    assert(goodix_primitives_population_variance_or_zero(
        float_values, 4u, &variance));
    assert(variance == 1.25f);
    assert(goodix_primitives_sample_variance_or_zero(NULL, 0u, &variance));
    assert(variance == 0.0f);
    assert(goodix_primitives_population_variance_or_zero(
        float_values, 1u, &variance));
    assert(variance == 0.0f);
    assert(goodix_primitives_sample_standard_deviation_or_zero(
        NULL, 0u, square_root_fixture, &standard_deviation));
    assert(standard_deviation == 0.0f);
    assert(goodix_primitives_population_standard_deviation_or_zero(
        float_values, 4u, square_root_fixture, &standard_deviation));
    assert(standard_deviation > 1.1180f && standard_deviation < 1.1181f);
    assert(!goodix_primitives_population_variance_or_zero(
        NULL, 2u, &variance));
    uint16_t nadt_result[30] = {0u};
    assert(goodix_primitives_nadt_result_binding(nadt_result) == nadt_result);
    assert(goodix_primitives_nadt_result_binding(NULL) == NULL);
    uint32_t hrv_configuration[6] = {0u};
    assert(goodix_primitives_hrv_configuration_binding(hrv_configuration) ==
           hrv_configuration);
    assert(goodix_primitives_hrv_configuration_binding(NULL) == NULL);
    float_buffer.count = 4u;
    assert(goodix_primitives_unsigned_power(2.0f, 5u) == 32.0f);
    assert(goodix_primitives_centered_i8(-1) == INT8_MIN);
    assert(goodix_primitives_centered_i8(128) == 0);
    assert(goodix_primitives_centered_i8(256) == INT8_MAX);
    assert(goodix_primitives_float_sum(float_values, 4u) == 10.0f);

    int32_t counter = 2;
    assert(goodix_primitives_decrement_counter(&counter) && counter == 1);
    goodix_primitives_tensor_descriptor descriptor;
    assert(goodix_primitives_tensor_descriptor_initialize(
               &descriptor, 1u, 2u, 3u, 4u, float_values) == float_values);
    assert(descriptor.element_bytes == 4u && descriptor.batches == 1u &&
           descriptor.rows == 2u && descriptor.columns == 3u);
    uint8_t tensor_pipeline_workspace[1100] = {0};
    goodix_primitives_tensor_descriptor tensor_pipeline_input_descriptor = {
        4u, 1u, 1u, 1u, float_values,
    };
    goodix_primitives_tensor_descriptor tensor_pipeline_state_descriptor = {
        1u, 1u, 1u, 1u, tensor_pipeline_workspace,
    };
    const goodix_primitives_tensor_binding tensor_pipeline_input = {
        &tensor_pipeline_input_descriptor, (uintptr_t)11u,
    };
    goodix_primitives_tensor_binding tensor_pipeline_state = {
        &tensor_pipeline_state_descriptor, (uintptr_t)22u,
    };
    const goodix_primitives_tensor_stage_fn tensor_pipeline_stages[3] = {
        tensor_pipeline_stage, tensor_pipeline_stage, tensor_pipeline_stage,
    };
    void *const tensor_pipeline_contexts[3] = {
        (void *)(uintptr_t)0u, (void *)(uintptr_t)1u,
        (void *)(uintptr_t)2u,
    };
    const uint8_t tensor_pipeline_dimensions[6] = {2u, 3u, 4u, 5u, 6u, 7u};
    tensor_pipeline_calls = 0u;
    assert(goodix_primitives_three_stage_u8_pipeline(
        tensor_pipeline_stages, tensor_pipeline_contexts,
        &tensor_pipeline_input, &tensor_pipeline_state,
        tensor_pipeline_dimensions, sizeof(tensor_pipeline_workspace)));
    assert(tensor_pipeline_calls == 3u);
    assert(tensor_pipeline_inputs[0].data == float_values &&
           tensor_pipeline_input_aux[0] == (uintptr_t)11u);
    assert(tensor_pipeline_outputs[0].rows == 2u &&
           tensor_pipeline_outputs[0].columns == 3u &&
           tensor_pipeline_outputs[0].data == tensor_pipeline_workspace);
    assert(tensor_pipeline_inputs[1].rows == 2u &&
           tensor_pipeline_outputs[1].rows == 4u &&
           tensor_pipeline_outputs[1].columns == 5u &&
           tensor_pipeline_outputs[1].data ==
               tensor_pipeline_workspace + 0x3E0u);
    assert(tensor_pipeline_inputs[2].data ==
               tensor_pipeline_workspace + 0x3E0u &&
           tensor_pipeline_outputs[2].rows == 6u &&
           tensor_pipeline_outputs[2].columns == 7u &&
           tensor_pipeline_outputs[2].data == tensor_pipeline_workspace);
    assert(tensor_pipeline_input_aux[1] == (uintptr_t)22u &&
           tensor_pipeline_input_aux[2] == (uintptr_t)22u &&
           tensor_pipeline_output_aux[0] == (uintptr_t)22u &&
           tensor_pipeline_output_aux[1] == (uintptr_t)22u &&
           tensor_pipeline_output_aux[2] == (uintptr_t)22u);
    assert(tensor_pipeline_state_descriptor.element_bytes == 1u &&
           tensor_pipeline_state_descriptor.batches == 1u &&
           tensor_pipeline_state_descriptor.rows == 6u &&
           tensor_pipeline_state_descriptor.columns == 7u &&
           tensor_pipeline_state_descriptor.data == tensor_pipeline_workspace);
    assert(!goodix_primitives_three_stage_u8_pipeline(
        tensor_pipeline_stages, tensor_pipeline_contexts,
        &tensor_pipeline_input, &tensor_pipeline_state,
        tensor_pipeline_dimensions, 1000u));

    float nadt_subgraph_workspace[
        GOODIX_PRIMITIVES_NADT_SUBGRAPH_WORKSPACE_FLOATS] = {0.0f};
    goodix_primitives_nadt_generated_subgraph nadt_subgraph = {
        .quantization_minimum = -2.0f,
        .quantization_maximum = 3.0f,
    };
    for (size_t stage = 0u;
            stage < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT; ++stage) {
        nadt_subgraph.operators[stage] = nadt_subgraph_operator;
        nadt_subgraph.operator_contexts[stage] = (void *)(uintptr_t)stage;
    }
    nadt_subgraph_calls = 0u;
    assert(goodix_primitives_nadt_generated_subgraph_execute(
        &nadt_subgraph, nadt_subgraph_workspace,
        GOODIX_PRIMITIVES_NADT_SUBGRAPH_WORKSPACE_FLOATS));
    assert(nadt_subgraph_calls ==
           GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT);
    static const uint32_t nadt_subgraph_expected_rows[19] = {
        1u, 16u, 16u, 4u, 4u, 16u, 16u, 16u, 4u, 4u,
        16u, 16u, 16u, 16u, 1u, 1u, 8u, 8u, 8u,
    };
    static const uint32_t nadt_subgraph_expected_columns[19] = {
        125u, 125u, 62u, 62u, 62u, 62u, 62u, 31u, 31u, 31u,
        31u, 31u, 15u, 15u, 15u, 15u, 15u, 15u, 15u,
    };
    static const uint32_t nadt_subgraph_expected_element_bytes[19] = {
        4u, 1u, 1u, 1u, 1u, 1u, 1u, 1u, 1u, 1u,
        1u, 1u, 1u, 4u, 4u, 4u, 4u, 4u, 4u,
    };
    static const size_t nadt_subgraph_expected_offsets[19] = {
        0u, 0u, 0u, 0u, 0x3E0u, 0u, 0u, 0u, 0u, 0x3E0u,
        0u, 0u, 0u, 0x3E0u, 0u, 0x1F0u, 0u, 0x1E0u, 0u,
    };
    for (size_t stage = 0u;
            stage < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT; ++stage) {
        assert(nadt_subgraph_outputs[stage].batches == 1u &&
               nadt_subgraph_outputs[stage].rows ==
                   nadt_subgraph_expected_rows[stage] &&
               nadt_subgraph_outputs[stage].columns ==
                   nadt_subgraph_expected_columns[stage] &&
               nadt_subgraph_outputs[stage].element_bytes ==
                   nadt_subgraph_expected_element_bytes[stage] &&
               (const uint8_t *)nadt_subgraph_outputs[stage].data ==
                   (const uint8_t *)nadt_subgraph_workspace +
                       nadt_subgraph_expected_offsets[stage]);
    }
    assert(nadt_subgraph_second_inputs[1].rows == 1u &&
           nadt_subgraph_second_inputs[1].columns == 1u &&
           nadt_subgraph_second_inputs[6].rows == 16u &&
           nadt_subgraph_second_inputs[6].columns == 62u &&
           nadt_subgraph_second_inputs[11].rows == 16u &&
           nadt_subgraph_second_inputs[11].columns == 31u &&
           nadt_subgraph_input_aux[0] == 0u &&
           nadt_subgraph_output_aux[0] != 0u &&
           nadt_subgraph_input_aux[13] != 0u &&
           nadt_subgraph_output_aux[13] != 0u &&
           nadt_subgraph_input_aux[14] == 0u &&
           nadt_subgraph_output_aux[17] == 0u &&
           nadt_subgraph_input_aux[18] != 0u);
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OUTPUT_VALUES; ++index) {
        assert(nadt_subgraph_workspace[index] == (float)(3000u + index));
    }
    nadt_subgraph_workspace[0] = -99.0f;
    nadt_subgraph_calls = 0u;
    nadt_subgraph.operators[7] = NULL;
    assert(!goodix_primitives_nadt_generated_subgraph_execute(
        &nadt_subgraph, nadt_subgraph_workspace,
        GOODIX_PRIMITIVES_NADT_SUBGRAPH_WORKSPACE_FLOATS));
    assert(nadt_subgraph_calls == 0u && nadt_subgraph_workspace[0] == -99.0f);
    nadt_subgraph.operators[7] = nadt_subgraph_operator;
    assert(!goodix_primitives_nadt_generated_subgraph_execute(
        &nadt_subgraph, nadt_subgraph_workspace,
        GOODIX_PRIMITIVES_NADT_SUBGRAPH_WORKSPACE_FLOATS - 1u));
    assert(nadt_subgraph_calls == 0u && nadt_subgraph_workspace[0] == -99.0f);

    float nadt_graph_input[GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES];
    float nadt_graph_workspace[600] = {0.0f};
    float nadt_graph_recurrent_state[6];
    float nadt_graph_output[2] = {-1.0f, -1.0f};
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES; ++index) {
        nadt_graph_input[index] = (float)(1000u + index);
    }
    for (size_t index = 0u; index < 6u; ++index) {
        nadt_graph_recurrent_state[index] = 9.0f;
    }
    nadt_generated_graph_fixture nadt_graph_fixture = {
        .workspace = nadt_graph_workspace,
        .recurrent_state = nadt_graph_recurrent_state,
        .fail_stage = SIZE_MAX,
        .expect_zero_state = true,
    };
    nadt_generated_graph_callback_context nadt_subgraph_contexts[2];
    nadt_generated_graph_callback_context nadt_stage_contexts[
        GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT];
    goodix_primitives_nadt_generated_graph nadt_graph = {
        .first_stage_values = 5u,
        .shared_stage_values = 4u,
        .recurrent_values = 6u,
        .recurrent_state = nadt_graph_recurrent_state,
        .recurrent_state_capacity = 6u,
        .penultimate_values = 4u,
        .output_values = 2u,
    };
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT; ++index) {
        nadt_subgraph_contexts[index].fixture = &nadt_graph_fixture;
        nadt_subgraph_contexts[index].index = index;
        nadt_graph.subgraphs[index] = nadt_generated_subgraph;
        nadt_graph.subgraph_contexts[index] = &nadt_subgraph_contexts[index];
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT; ++index) {
        nadt_stage_contexts[index].fixture = &nadt_graph_fixture;
        nadt_stage_contexts[index].index = index;
        nadt_graph.stages[index] = nadt_generated_stage;
        nadt_graph.stage_contexts[index] = &nadt_stage_contexts[index];
    }
    assert(goodix_primitives_nadt_generated_graph_execute(
        &nadt_graph, nadt_graph_input,
        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
        nadt_graph_workspace,
        sizeof(nadt_graph_workspace) / sizeof(nadt_graph_workspace[0]), true,
        nadt_graph_output,
        sizeof(nadt_graph_output) / sizeof(nadt_graph_output[0])));
    assert(nadt_graph_fixture.subgraph_calls == 2u &&
           nadt_graph_fixture.stage_calls == 7u &&
           nadt_graph_output[0] == 70.0f && nadt_graph_output[1] == 71.0f);
    for (size_t index = 0u; index < 6u; ++index) {
        assert(nadt_graph_recurrent_state[index] == 0.0f);
        nadt_graph_recurrent_state[index] = 9.0f;
    }

    nadt_graph_fixture.subgraph_calls = 0u;
    nadt_graph_fixture.stage_calls = 0u;
    nadt_graph_fixture.expect_zero_state = false;
    assert(goodix_primitives_nadt_generated_graph_execute(
        &nadt_graph, nadt_graph_input,
        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
        nadt_graph_workspace,
        sizeof(nadt_graph_workspace) / sizeof(nadt_graph_workspace[0]), false,
        nadt_graph_output,
        sizeof(nadt_graph_output) / sizeof(nadt_graph_output[0])));
    assert(nadt_graph_fixture.subgraph_calls == 2u &&
           nadt_graph_fixture.stage_calls == 7u);
    for (size_t index = 0u; index < 6u; ++index) {
        assert(nadt_graph_recurrent_state[index] == 9.0f);
    }

    nadt_graph_output[0] = 99.0f;
    assert(!goodix_primitives_nadt_generated_graph_execute(
        &nadt_graph, nadt_graph_input,
        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
        nadt_graph_workspace,
        GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_BANK + 3u, false,
        nadt_graph_output,
        sizeof(nadt_graph_output) / sizeof(nadt_graph_output[0])));
    assert(nadt_graph_output[0] == 99.0f);
    nadt_graph.shared_stage_values = 2u;
    assert(!goodix_primitives_nadt_generated_graph_execute(
        &nadt_graph, nadt_graph_input,
        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
        nadt_graph_workspace,
        sizeof(nadt_graph_workspace) / sizeof(nadt_graph_workspace[0]), false,
        nadt_graph_output,
        sizeof(nadt_graph_output) / sizeof(nadt_graph_output[0])));
    nadt_graph.shared_stage_values = 4u;
    nadt_graph_fixture.fail_stage = 3u;
    assert(!goodix_primitives_nadt_generated_graph_execute(
        &nadt_graph, nadt_graph_input,
        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
        nadt_graph_workspace,
        sizeof(nadt_graph_workspace) / sizeof(nadt_graph_workspace[0]), false,
        nadt_graph_output,
        sizeof(nadt_graph_output) / sizeof(nadt_graph_output[0])));
    nadt_graph_fixture.fail_stage = SIZE_MAX;
    assert(goodix_primitives_filter_code(5u) == 5u);
    assert(goodix_primitives_filter_code(2u) == 0u);

    union {
        float value;
        uint32_t word;
    } last_bits = {6.25f};
    uint32_t last_values[2] = {0u, last_bits.word};
    goodix_primitives_word_window last_window = {last_values, 2u, 2u};
    assert(goodix_primitives_word_window_last(&last_window, 0u) ==
           last_bits.word);
    assert(goodix_primitives_word_window_count(&last_window) == 2u);
    uint16_t bound = 0u;
    assert(goodix_primitives_store_version_qualifier(&bound));
    assert(bound == UINT16_C(0x636E));

    assert(goodix_primitives_copy_process_version_v1_1(
        version, sizeof(version)));
    assert(strcmp(version, "pv_v1.1.0") == 0);
    assert(goodix_primitives_copy_process_version_v1_0(
        version, sizeof(version)));
    assert(strcmp(version, "pv_v1.0.0") == 0);
    uint32_t reversed = 0u;
    assert(goodix_primitives_reverse_low_bits(UINT32_C(0x0D), 4u,
                                              &reversed));
    assert(reversed == UINT32_C(0x0B));
    float mean = 0.0f;
    assert(goodix_primitives_float_mean(float_values, 4u, &mean));
    assert(mean == 2.5f);
    assert(goodix_primitives_sum_squares(float_values, 4u) == 30.0f);
    const float other_values[4] = {2.0f, 3.0f, 4.0f, 5.0f};
    assert(goodix_primitives_dot_product(float_values, other_values, 4u) ==
           40.0f);

    uint8_t indexed_records[64];
    for (size_t index = 0u; index < sizeof(indexed_records); ++index) {
        indexed_records[index] = (uint8_t)index;
    }
    uint8_t indexed_copy[32] = {0};
    assert(goodix_primitives_copy_indexed_record(
               indexed_records, 2u, 1, indexed_copy) == 0);
    assert(memcmp(indexed_copy, &indexed_records[32], 32u) == 0);
    assert(goodix_primitives_copy_indexed_record(
               indexed_records, 2u, 2, indexed_copy) ==
           INT32_C(0x10000003));
    assert(goodix_primitives_round_nearest(2.5f) == 3);
    assert(goodix_primitives_round_nearest(-2.5f) == -3);

    uint8_t packed_records[8] = {0u, 0u, 0u, 1u, 0u, 0u, 0u, 2u};
    assert(goodix_primitives_transform_packed24_lsb(
        packed_records, sizeof(packed_records), add_one));
    assert(packed_records[3] == 2u && packed_records[7] == 3u);
    assert(goodix_primitives_visit_packed24(
        packed_records, sizeof(packed_records), add_one));
    uint8_t words[4] = {0x12u, 0x34u, 0xABu, 0xCDu};
    assert(goodix_primitives_swap_u16_bytes(words, sizeof(words)));
    assert(words[0] == 0x34u && words[1] == 0x12u &&
           words[2] == 0xCDu && words[3] == 0xABu);

    const int32_t ranged[4] = {3, -7, 11, 2};
    int32_t high = 0;
    int32_t low = 0;
    int32_t range = 0;
    assert(goodix_primitives_i32_range(
        ranged, 4u, &high, &low, &range));
    assert(high == 11 && low == -7 && range == 18);

    uint8_t processing_source[76] = {0};
    uint8_t processing_record[96] = {0};
    processing_source[4] = 100u;
    assert(goodix_primitives_processing_record_initialize(
        processing_record, sizeof(processing_record), processing_source,
        sizeof(processing_source)));
    assert(processing_record[76] == 4u);
    assert(processing_record[80] == 5u);
    assert(processing_record[84] == 25u);
    assert(processing_record[88] == 1u);
    assert(processing_record[92] == 25u);

    uint8_t transition[7] = {0};
    assert(goodix_primitives_update_transition(
        transition, sizeof(transition), 0u, 1u));
    assert(transition[4] == 0u && transition[5] == 1u);
    transition[6] = 3u;
    assert(goodix_primitives_update_transition(
        transition, sizeof(transition), 1u, 1u));
    assert(transition[5] == 0u && transition[6] == 4u);

    float sorted[6] = {4.0f, 1.0f, 3.0f, 2.0f, 0.0f, 0.0f};
    assert(goodix_primitives_sort_floats(sorted, 4u));
    assert(sorted[0] == 1.0f && sorted[1] == 2.0f &&
           sorted[2] == 3.0f && sorted[3] == 4.0f);
    float median_filtered[5] = {0.0f, 1.0f, 2.0f, 3.0f, 100.0f};
    float far_median_scratch[5] = {0.0f};
    assert(goodix_primitives_replace_far_from_median(
        median_filtered, 5u, 8, far_median_scratch, 5u));
    assert(median_filtered[0] == 0.0f && median_filtered[1] == 1.0f &&
           median_filtered[2] == 2.0f && median_filtered[3] == 3.0f &&
           median_filtered[4] == 2.0f);
    assert(far_median_scratch[0] == 0.0f &&
           far_median_scratch[1] == 1.0f &&
           far_median_scratch[2] == 2.0f &&
           far_median_scratch[3] == 3.0f &&
           far_median_scratch[4] == 100.0f);
    assert(!goodix_primitives_replace_far_from_median(
        median_filtered, 5u, 8, far_median_scratch, 4u));
    assert(!goodix_primitives_replace_far_from_median(
        median_filtered, 5u, 8, median_filtered, 5u));
    float insertion_sorted[6] = {4.0f, -1.0f, 4.0f, 2.0f, 0.0f, 3.0f};
    assert(goodix_primitives_insertion_sort_floats(
        insertion_sorted, 6u));
    assert(insertion_sorted[0] == -1.0f &&
           insertion_sorted[1] == 0.0f &&
           insertion_sorted[2] == 2.0f &&
           insertion_sorted[3] == 3.0f &&
           insertion_sorted[4] == 4.0f &&
           insertion_sorted[5] == 4.0f);
    assert(goodix_primitives_insertion_sort_floats(NULL, 0u));
    assert(!goodix_primitives_insertion_sort_floats(NULL, 1u));

    const float top_source[7] = {
        1.0f, 99.0f, 5.0f, 99.0f, 3.0f, 99.0f, 5.0f,
    };
    float top_values[3] = {0.0f, 0.0f, 0.0f};
    assert(goodix_primitives_top_descending_strided(
        top_values, 3u, top_source, 7u, 2u, 4u, 3u));
    assert(top_values[0] == 5.0f && top_values[1] == 5.0f &&
           top_values[2] == 3.0f);
    assert(!goodix_primitives_top_descending_strided(
        top_values, 2u, top_source, 7u, 2u, 4u, 3u));
    assert(!goodix_primitives_top_descending_strided(
        top_values, 3u, top_source, 6u, 2u, 4u, 3u));

    const int16_t extrema_values[7] = {0, 3, 1, -2, 4, 2, 0};
    int16_t maxima_indices[2] = {-1, -1};
    int16_t minima_indices[1] = {-1};
    uint8_t maxima_count = 0u;
    uint8_t minima_count = 0u;
    assert(goodix_primitives_i16_local_extrema_indices(
        extrema_values, 7u, maxima_indices, 2u, &maxima_count,
        minima_indices, 1u, &minima_count));
    assert(maxima_count == 2u && maxima_indices[0] == 1 &&
           maxima_indices[1] == 4);
    assert(minima_count == 1u && minima_indices[0] == 3);
    assert(!goodix_primitives_i16_local_extrema_indices(
        extrema_values, 7u, maxima_indices, 1u, &maxima_count,
        minima_indices, 1u, &minima_count));
    maxima_count = UINT8_C(0xFF);
    minima_count = UINT8_C(0xFF);
    assert(goodix_primitives_i16_local_extrema_indices(
        NULL, 0u, NULL, 0u, &maxima_count, NULL, 0u,
        &minima_count));
    assert(maxima_count == 0u && minima_count == 0u);

    const float grouped_coefficients[4] = {1.0f, 10.0f, 2.0f, 20.0f};
    const float grouped_values[6] = {1.0f, 2.0f, 3.0f,
                                     4.0f, 5.0f, 6.0f};
    float grouped_output[6] = {0.0f};
    assert(goodix_primitives_grouped_row_weighted_sums(
        grouped_coefficients, 4u, 2u, 2u,
        grouped_values, 6u, 3u, grouped_output, 6u));
    assert(grouped_output[0] == 41.0f && grouped_output[1] == 52.0f &&
           grouped_output[2] == 63.0f && grouped_output[3] == 82.0f &&
           grouped_output[4] == 104.0f && grouped_output[5] == 126.0f);
    assert(!goodix_primitives_grouped_row_weighted_sums(
        grouped_coefficients, 3u, 2u, 2u,
        grouped_values, 6u, 3u, grouped_output, 6u));
    assert(!goodix_primitives_grouped_row_weighted_sums(
        grouped_coefficients, 4u, 2u, 2u,
        grouped_values, 5u, 3u, grouped_output, 6u));

    const goodix_primitives_point2f spline_controls[4] = {
        {0.0f, 0.0f}, {1.0f, 2.0f}, {3.0f, 2.0f}, {4.0f, 0.0f},
    };
    goodix_primitives_point2f spline_point = {0.0f, 0.0f};
    assert(goodix_primitives_cardinal_spline_point(
        0.5f, spline_controls, 0, &spline_point));
    assert(spline_point.x == 2.0f && spline_point.y == 2.25f);
    assert(goodix_primitives_cardinal_spline_point(
        0.25f, spline_controls, 1, &spline_point));
    assert(spline_point.x == 1.3125f && spline_point.y == 2.0f);
    assert(!goodix_primitives_cardinal_spline_point(
        0.5f, NULL, 0, &spline_point));

    goodix_primitives_point2f spline_samples[3] = {{0.0f, 0.0f}};
    assert(goodix_primitives_sample_cardinal_spline(
        spline_controls, 0, 2u, spline_samples, 3u));
    assert(spline_samples[0].x == 1.0f && spline_samples[0].y == 2.0f);
    assert(spline_samples[1].x == 2.0f && spline_samples[1].y == 2.25f);
    assert(spline_samples[2].x == 3.0f && spline_samples[2].y == 2.0f);
    assert(!goodix_primitives_sample_cardinal_spline(
        spline_controls, 0, 2u, spline_samples, 2u));
    assert(goodix_primitives_sample_cardinal_spline(
        spline_controls, 0, 0u, spline_samples, 1u));
    assert(spline_samples[0].x == 1.0f && spline_samples[0].y == 2.0f);

    float hr_extrema_values[4] = {0.0f, 1.0f, 2.0f, 3.0f};
    goodix_primitives_float_buffer hr_extrema_history = {
        .values = hr_extrema_values,
        .count = 3u,
        .capacity = 4u,
    };
    goodix_primitives_hr_extrema_tracker hr_extrema = {
        .direction_state = 0,
        .sample_index = 12,
    };
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 100, 10, &hr_extrema,
        NULL, NULL, NULL));
    assert(hr_extrema.direction_state == 0 && hr_extrema.pair_ready == 0u);

    hr_extrema_history.count = 4u;
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 100, 10, &hr_extrema,
        NULL, NULL, NULL));
    assert(hr_extrema.direction_state == 1 &&
           hr_extrema.trough_position == 91.0f &&
           hr_extrema.trough_value == 2.0f &&
           hr_extrema.pair_ready == 1u);
    hr_extrema_values[2] = 3.0f;
    hr_extrema_values[3] = 2.0f;
    hr_extrema.sample_index = 13;
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 100, 10, &hr_extrema,
        NULL, NULL, NULL));
    assert(hr_extrema.direction_state == 0 &&
           hr_extrema.peak_position == 93.0f &&
           hr_extrema.peak_value == 3.0f &&
           hr_extrema.rise_amplitude == 1.0f &&
           hr_extrema.rise_span == 2.0f);

    hr_extrema_values[2] = 2.0f;
    hr_extrema_values[3] = 3.0f;
    hr_extrema.sample_index = 20;
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 100, 10, &hr_extrema,
        NULL, NULL, NULL));
    assert(hr_extrema.direction_state == 1 &&
           hr_extrema.peak_position == 83.0f &&
           hr_extrema.trough_position == 89.0f &&
           hr_extrema.fall_amplitude == 1.0f &&
           hr_extrema.fall_span == 6.0f &&
           hr_extrema.fall_complete == 1u);

    goodix_primitives_hr_extrema_tracker equality_extrema = {
        .direction_state = 2,
        .sample_index = 1,
    };
    hr_extrema_values[2] = 2.0f;
    hr_extrema_values[3] = 2.0f;
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 0, 10, &equality_extrema,
        NULL, NULL, NULL));
    assert(equality_extrema.direction_state == 2);
    hr_extrema_values[3] = 3.0f;
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 0, 10, &equality_extrema,
        NULL, NULL, NULL));
    assert(equality_extrema.direction_state == 1);
    equality_extrema.direction_state = 2;
    hr_extrema_values[3] = 1.0f;
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 0, 0u, 0, 10, &equality_extrema,
        NULL, NULL, NULL));
    assert(equality_extrema.direction_state == 0);

    const goodix_primitives_hr_extrema_curve hr_extrema_curve = {
        .x = {0.0f, 1.0f, 2.0f, 3.0f},
    };
    goodix_primitives_hr_extrema_workspace hr_extrema_workspace;
    goodix_primitives_point2f expected_extrema_samples[6];
    const goodix_primitives_point2f expected_trough_controls[4] = {
        {0.0f, 4.0f}, {1.0f, 1.0f},
        {2.0f, 2.0f}, {3.0f, 3.0f},
    };
    assert(goodix_primitives_sample_cardinal_spline(
        expected_trough_controls, 0, 5u, expected_extrema_samples, 6u));
    goodix_primitives_point2f expected_trough = expected_extrema_samples[0];
    for (size_t index = 1u; index < 6u; ++index) {
        if (expected_extrema_samples[index].y < expected_trough.y) {
            expected_trough = expected_extrema_samples[index];
        }
    }
    hr_extrema_values[0] = 4.0f;
    hr_extrema_values[1] = 1.0f;
    hr_extrema_values[2] = 2.0f;
    hr_extrema_values[3] = 3.0f;
    goodix_primitives_hr_extrema_tracker refined_trough = {
        .direction_state = 0,
        .pair_ready = 1u,
        .peak_position = 80.0f,
        .peak_value = 5.0f,
        .sample_index = 12,
    };
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 1, 3u, 100, 10, &refined_trough,
        &hr_extrema_curve, &hr_extrema_curve, &hr_extrema_workspace));
    assert(refined_trough.trough_position ==
               91.0f + expected_trough.x - 2.0f &&
           refined_trough.trough_value == expected_trough.y &&
           refined_trough.fall_amplitude ==
               5.0f - expected_trough.y &&
           refined_trough.fall_complete == 1u);

    const goodix_primitives_point2f expected_peak_controls[4] = {
        {0.0f, 1.0f}, {1.0f, 4.0f},
        {2.0f, 3.0f}, {3.0f, 2.0f},
    };
    assert(goodix_primitives_sample_cardinal_spline(
        expected_peak_controls, 0, 5u, expected_extrema_samples, 6u));
    goodix_primitives_point2f expected_peak = expected_extrema_samples[0];
    for (size_t index = 1u; index < 6u; ++index) {
        if (expected_extrema_samples[index].y > expected_peak.y) {
            expected_peak = expected_extrema_samples[index];
        }
    }
    hr_extrema_values[0] = 1.0f;
    hr_extrema_values[1] = 4.0f;
    hr_extrema_values[2] = 3.0f;
    hr_extrema_values[3] = 2.0f;
    goodix_primitives_hr_extrema_tracker refined_peak = {
        .direction_state = 1,
        .trough_position = 80.0f,
        .trough_value = 1.0f,
        .pair_ready = 1u,
        .sample_index = 13,
    };
    assert(goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 1, 3u, 100, 10, &refined_peak,
        &hr_extrema_curve, &hr_extrema_curve, &hr_extrema_workspace));
    assert(refined_peak.peak_position ==
               93.0f + expected_peak.x - 2.0f &&
           refined_peak.peak_value == expected_peak.y &&
           refined_peak.rise_amplitude == expected_peak.y - 1.0f &&
           refined_peak.rise_span == refined_peak.peak_position - 80.0f);

    const goodix_primitives_hr_extrema_tracker saved_refined_peak =
        refined_peak;
    assert(!goodix_primitives_hr_extrema_tracker_update(
        &hr_extrema_history, 1, 3u, 100, 0, &refined_peak,
        &hr_extrema_curve, &hr_extrema_curve, &hr_extrema_workspace));
    assert(memcmp(&refined_peak, &saved_refined_peak,
                  sizeof(refined_peak)) == 0);

    /* 0x0006CCC0: exact typed GH_SPO2/dlCom diagnostic stream. */
    const goodix_primitives_spo2_diagnostic_configuration
        spo2_diagnostic_configuration = {
            .sample_frequency = 100u,
            .timestamp = 0u,
            .mode = 2u,
            .latest_output_time = 5,
            .earliest_output_time = 4,
            .valid_channel_count = 3u,
            .sigma = 6,
            .delay_time = 8,
            .valid_score_scale = 9,
            .last_heart_rate = 10,
            .raw_ppg_scale = 7,
        };
    const int32_t spo2_ppg[3] = {11, 12, 13};
    const uint8_t spo2_enable_flags[2] = {1u, 0u};
    const goodix_primitives_spo2_diagnostic_input spo2_diagnostic_input = {
        .total_channel_count = 3u,
        .enable_flags = spo2_enable_flags,
        .enable_flag_count = 2u,
        .ppg = spo2_ppg,
        .ppg_count = 3u,
        .accelerometer = {20, 21, 22},
        .gyroscope = {30, 31, 32},
    };
    spo2_diagnostic_trace formatted_diagnostics = {0};
    spo2_diagnostic_trace direct_diagnostics = {0};
    spo2_memory_trace memory_diagnostics = {0};
    goodix_primitives_spo2_diagnostic_plan spo2_diagnostic_plan = {
        .formatted_emit = record_spo2_diagnostic,
        .formatted_context = &formatted_diagnostics,
        .direct_emit = record_spo2_diagnostic,
        .direct_context = &direct_diagnostics,
        .memory_available = next_spo2_available_memory,
        .memory_context = &memory_diagnostics,
    };

    assert(goodix_primitives_spo2_input_diagnostics_emit(
        &spo2_diagnostic_configuration, NULL, &spo2_diagnostic_plan));
    assert(formatted_diagnostics.count == 9u &&
           direct_diagnostics.count == 9u && memory_diagnostics.calls == 0u);
    static const char *const initial_diagnostic_formats[9] = {
        "alg:mode=%d\n",
        "alg:fs=%d\n",
        "alg:valid_ch_num=%d\n",
        "alg:earliest_output_time=%d\n",
        "alg:latest_output_time=%d\n",
        "alg:sigma=%d\n",
        "alg:raw_ppg_scale=%d\n",
        "alg:delay_time=%d\n",
        "alg:valid_score_scale=%d\n",
    };
    const int32_t initial_diagnostic_values[9] = {
        2, 100, 3, 4, 5, 6, 7, 8, 9,
    };
    for (size_t index = 0u; index < 9u; ++index) {
        assert(strcmp(formatted_diagnostics.events[index].format,
                      initial_diagnostic_formats[index]) == 0);
        assert(strcmp(direct_diagnostics.events[index].format,
                      initial_diagnostic_formats[index]) == 0);
        assert(formatted_diagnostics.events[index].value_count == 1u &&
               direct_diagnostics.events[index].value_count == 1u &&
               formatted_diagnostics.events[index].values[0] ==
                   initial_diagnostic_values[index] &&
               direct_diagnostics.events[index].values[0] ==
                   initial_diagnostic_values[index]);
    }

    formatted_diagnostics = (spo2_diagnostic_trace){0};
    direct_diagnostics = (spo2_diagnostic_trace){0};
    assert(goodix_primitives_spo2_input_diagnostics_emit(
        &spo2_diagnostic_configuration, &spo2_diagnostic_input,
        &spo2_diagnostic_plan));
    assert(formatted_diagnostics.count == 20u &&
           direct_diagnostics.count == 20u && memory_diagnostics.calls == 2u);
    assert(strcmp(formatted_diagnostics.events[9].format,
                  "alg:ts=%d\n") == 0 &&
           formatted_diagnostics.events[9].values[0] == 0);
    assert(strcmp(formatted_diagnostics.events[10].format,
                  "alg:mem=%d\n") == 0 &&
           formatted_diagnostics.events[10].values[0] == 1001);
    assert(direct_diagnostics.events[10].values[0] == 1002);
    assert(strcmp(formatted_diagnostics.events[11].format,
                  "alg:lhr=%d\n") == 0 &&
           formatted_diagnostics.events[11].values[0] == 10);
    assert(strcmp(formatted_diagnostics.events[12].format,
                  "alg:total_ch_num=%d\n") == 0 &&
           formatted_diagnostics.events[12].values[0] == 3);
    for (size_t index = 0u; index < 3u; ++index) {
        const spo2_diagnostic_event *event =
            &formatted_diagnostics.events[13u + index];
        assert(strcmp(event->format, "alg:%d ppg=%d\n") == 0 &&
               event->value_count == 2u &&
               event->values[0] == (int32_t)index &&
               event->values[1] == spo2_ppg[index]);
    }
    assert(strcmp(formatted_diagnostics.events[16].format,
                  "alg:en=%d\n") == 0 &&
           formatted_diagnostics.events[16].values[0] == 1);
    assert(strcmp(formatted_diagnostics.events[17].format,
                  "alg:en=%d\n") == 0 &&
           formatted_diagnostics.events[17].values[0] == 0);
    assert(strcmp(formatted_diagnostics.events[18].format,
                  "alg:c3Xm=%d,y=%d,z=%d\n") == 0 &&
           formatted_diagnostics.events[18].value_count == 3u &&
           formatted_diagnostics.events[18].values[0] == 20 &&
           formatted_diagnostics.events[18].values[1] == 21 &&
           formatted_diagnostics.events[18].values[2] == 22);
    assert(strcmp(formatted_diagnostics.events[19].format,
                  "alg:groy_x=%d,groy_y=%d,groy_z=%d\n\n") == 0 &&
           formatted_diagnostics.events[19].value_count == 3u &&
           formatted_diagnostics.events[19].values[0] == 30 &&
           formatted_diagnostics.events[19].values[1] == 31 &&
           formatted_diagnostics.events[19].values[2] == 32);

    goodix_primitives_spo2_diagnostic_configuration dynamic_only =
        spo2_diagnostic_configuration;
    dynamic_only.timestamp = 77u;
    formatted_diagnostics = (spo2_diagnostic_trace){0};
    spo2_diagnostic_plan.direct_emit = NULL;
    assert(goodix_primitives_spo2_input_diagnostics_emit(
        &dynamic_only, &spo2_diagnostic_input, &spo2_diagnostic_plan));
    assert(formatted_diagnostics.count == 11u &&
           strcmp(formatted_diagnostics.events[0].format,
                  "alg:ts=%d\n") == 0 &&
           formatted_diagnostics.events[0].values[0] == 77 &&
           memory_diagnostics.calls == 3u);

    goodix_primitives_spo2_diagnostic_input undersized_diagnostics =
        spo2_diagnostic_input;
    undersized_diagnostics.ppg_count = 2u;
    formatted_diagnostics = (spo2_diagnostic_trace){0};
    assert(!goodix_primitives_spo2_input_diagnostics_emit(
        &dynamic_only, &undersized_diagnostics, &spo2_diagnostic_plan));
    assert(formatted_diagnostics.count == 0u && memory_diagnostics.calls == 3u);
    undersized_diagnostics = spo2_diagnostic_input;
    undersized_diagnostics.enable_flag_count = 1u;
    assert(!goodix_primitives_spo2_input_diagnostics_emit(
        &dynamic_only, &undersized_diagnostics, &spo2_diagnostic_plan));
    const goodix_primitives_spo2_diagnostic_plan no_diagnostic_sinks = {0};
    assert(goodix_primitives_spo2_input_diagnostics_emit(
        &spo2_diagnostic_configuration, &spo2_diagnostic_input,
        &no_diagnostic_sinks));

    const int32_t primary_events[3] = {10, 20, 30};
    const int32_t secondary_events[4] = {5, 15, 25, 35};
    const goodix_primitives_event_pair_source event_source = {
        primary_events, 3u, 0u, secondary_events, 4u, 0u,
    };
    int32_t paired_primary[3] = {0, 0, 0};
    int32_t paired_secondary[3] = {0, 0, 0};
    size_t paired_count = 0u;
    assert(goodix_primitives_align_event_pairs(
        5, &event_source, paired_primary, paired_secondary, 3u,
        &paired_count));
    assert(paired_count == 3u && paired_primary[0] == 10 &&
           paired_primary[1] == 20 && paired_primary[2] == 30 &&
           paired_secondary[0] == 15 && paired_secondary[1] == 25 &&
           paired_secondary[2] == 35);
    assert(goodix_primitives_align_event_pairs(
        4, &event_source, paired_primary, paired_secondary, 3u,
        &paired_count));
    assert(paired_primary[0] == 35 && paired_primary[1] == 45 &&
           paired_primary[2] == 55 && paired_secondary[0] == 40 &&
           paired_secondary[1] == 50 && paired_secondary[2] == 60);
    const goodix_primitives_event_pair_source no_secondary_events = {
        primary_events, 3u, 1u, NULL, 0u, 0u,
    };
    assert(goodix_primitives_align_event_pairs(
        5, &no_secondary_events, paired_primary, paired_secondary, 2u,
        &paired_count));
    assert(paired_count == 2u && paired_primary[0] == 20 &&
           paired_secondary[0] == 20 && paired_primary[1] == 30 &&
           paired_secondary[1] == 30);
    assert(!goodix_primitives_align_event_pairs(
        5, &event_source, paired_primary, paired_secondary, 2u,
        &paired_count));

    /* 0x00036BFA / 0x0002F65C: mode-one three-buffer clear. */
    float clear_a[] = {1.0f, 2.0f};
    float clear_b[] = {-3.0f};
    float clear_c[] = {4.0f, 5.0f, 6.0f};
    goodix_primitives_float_span clear_buffers[3] = {
        {clear_a, 2u}, {clear_b, 1u}, {clear_c, 3u},
    };
    assert(goodix_primitives_clear_mode_buffers(clear_buffers, 0u));
    assert(clear_a[0] == 1.0f && clear_b[0] == -3.0f &&
           clear_c[2] == 6.0f);
    assert(goodix_primitives_clear_mode_buffers(clear_buffers, 1u));
    assert(clear_a[0] == 0.0f && clear_a[1] == 0.0f &&
           clear_b[0] == 0.0f && clear_c[0] == 0.0f &&
           clear_c[1] == 0.0f && clear_c[2] == 0.0f);
    clear_buffers[1].values = NULL;
    assert(!goodix_primitives_clear_mode_buffers(clear_buffers, 1u));
    assert(goodix_primitives_clear_mode_buffers(NULL, 2u));

    /* 0x00043B30 / 0x00099010: selected-slot elapsed accounting. */
    const uint32_t slot_timestamps[] = {11u, 130u, 0u};
    goodix_primitives_elapsed_state elapsed_state = {
        100u, 150u, 180u, slot_timestamps, 3u,
    };
    assert(goodix_primitives_update_elapsed_slot(&elapsed_state, 0u));
    assert(elapsed_state.baseline == 100u &&
           elapsed_state.elapsed_a == 150u &&
           elapsed_state.elapsed_b == 180u);
    assert(goodix_primitives_update_elapsed_slot(&elapsed_state, 1u));
    assert(elapsed_state.baseline == 130u &&
           elapsed_state.elapsed_a == 180u &&
           elapsed_state.elapsed_b == 210u);
    assert(!goodix_primitives_update_elapsed_slot(&elapsed_state, 2u));
    assert(!goodix_primitives_update_elapsed_slot(&elapsed_state, 3u));
    assert(!goodix_primitives_update_elapsed_slot(NULL, 0u));

    const int32_t extrema_samples[5] = {0, 5, 0, 5, 0};
    int16_t rising_extrema[2] = {-1, -1};
    int16_t falling_extrema[2] = {-1, -1};
    int16_t all_extrema[2] = {-1, -1};
    goodix_primitives_extrema_index_counts extrema_counts = {0};
    assert(goodix_primitives_collect_extrema_indices(
        extrema_samples, 5u, 2, rising_extrema, 2u,
        falling_extrema, 2u, all_extrema, 2u, &extrema_counts));
    assert(extrema_counts.rising_count == 2u &&
           extrema_counts.falling_count == 1u &&
           extrema_counts.transition_count == 2u);
    assert(rising_extrema[0] == 1 && rising_extrema[1] == 3 &&
           falling_extrema[0] == 2 &&
           all_extrema[0] == 1 && all_extrema[1] == 2);
    assert(!goodix_primitives_collect_extrema_indices(
        extrema_samples, 5u, 2, rising_extrema, 1u,
        falling_extrema, 2u, all_extrema, 2u, &extrema_counts));
    assert(goodix_primitives_collect_extrema_indices(
        extrema_samples, 5u, 2, NULL, 0u, NULL, 0u, NULL, 0u,
        &extrema_counts));
    assert(extrema_counts.rising_count == 2u &&
           extrema_counts.falling_count == 1u &&
           extrema_counts.transition_count == 0u);

    goodix_primitives_timed_triplet_destination triplet_destination = {
        {9.0f, 9.0f, 9.0f}, 100u,
    };
    goodix_primitives_timed_triplet_source triplet_source = {
        121u, 10.0f, {1.0f, 2.0f, 3.0f},
    };
    bool triplet_copied = false;
    assert(goodix_primitives_copy_fresh_gated_triplet(
        &triplet_destination, &triplet_source, &triplet_copied));
    assert(triplet_copied && triplet_destination.values[0] == 1.0f &&
           triplet_destination.values[1] == 2.0f &&
           triplet_destination.values[2] == 3.0f);
    triplet_source.timestamp = 120u;
    triplet_source.values[0] = 8.0f;
    assert(goodix_primitives_copy_fresh_gated_triplet(
        &triplet_destination, &triplet_source, &triplet_copied));
    assert(!triplet_copied && triplet_destination.values[0] == 1.0f);
    triplet_source.timestamp = 15u;
    triplet_source.gate = 29.0f;
    triplet_destination.last_timestamp = UINT32_MAX - UINT32_C(5);
    assert(goodix_primitives_copy_fresh_gated_triplet(
        &triplet_destination, &triplet_source, &triplet_copied));
    assert(triplet_copied && triplet_destination.values[0] == 8.0f);
    triplet_source.gate = 30.0f;
    assert(goodix_primitives_copy_fresh_gated_triplet(
        &triplet_destination, &triplet_source, &triplet_copied));
    assert(!triplet_copied);

    uint32_t crossing_values[3] = {10u, 0u, 0u};
    const int32_t crossing_samples[3] = {11, 5, 12};
    goodix_primitives_threshold_history crossing_history = {
        {crossing_values, 1u, 3u}, 0u, 99u,
    };
    assert(goodix_primitives_accumulate_threshold_crossings(
        crossing_samples, 3u, 5, &crossing_history));
    assert(crossing_history.window.count == 3u &&
           crossing_values[0] == 10u && crossing_values[1] == 11u &&
           crossing_values[2] == 12u && crossing_history.cursor == 0u &&
           crossing_history.emitted_count == 2u);
    uint32_t full_crossing_values[2] = {10u, 20u};
    const int32_t full_crossing_sample[1] = {30};
    goodix_primitives_threshold_history full_crossing_history = {
        {full_crossing_values, 2u, 2u}, 1u, 0u,
    };
    assert(goodix_primitives_accumulate_threshold_crossings(
        full_crossing_sample, 1u, 5, &full_crossing_history));
    assert(full_crossing_values[0] == 20u &&
           full_crossing_values[1] == 30u &&
           full_crossing_history.cursor == 0u &&
           full_crossing_history.emitted_count == 1u);
    uint32_t offset_crossing_values[3] = {10u, 0u, 0u};
    const int32_t offset_crossing_samples[2] = {-10, 0};
    goodix_primitives_threshold_history offset_crossing_history = {
        {offset_crossing_values, 1u, 3u}, 0u, 0u,
    };
    assert(goodix_primitives_accumulate_threshold_crossings(
        offset_crossing_samples, 2u, 6, &offset_crossing_history));
    assert(offset_crossing_values[1] == 15u &&
           offset_crossing_values[2] == 25u &&
           offset_crossing_history.cursor == 2u &&
           offset_crossing_history.emitted_count == 2u);
    crossing_history.window.count = 4u;
    assert(!goodix_primitives_accumulate_threshold_crossings(
        NULL, 0u, 5, &crossing_history));

    /* The 0x30178 -> 0x76B78 -> 0x47FA8 -> 0x3441C -> 0x30114
     * NADT peak-mask closure, including plateau suppression and the stock
     * newest-index retention rule. */
    const float plateau_peak_values[5] = {0.0f, 3.0f, 3.0f, 2.0f, 0.0f};
    uint8_t plateau_packed[2] = {UINT8_C(0xFF), UINT8_C(0xFF)};
    assert(goodix_primitives_nadt_extrema_neighborhood_mask(
        plateau_peak_values, 5u, 3u, 2u, 0,
        plateau_packed, sizeof(plateau_packed)));
    assert(plateau_packed[0] == UINT8_C(0x7B) &&
           plateau_packed[1] == UINT8_C(0x7F));
    assert(!goodix_primitives_nadt_extrema_neighborhood_mask(
        plateau_peak_values, 5u, 3u, 3u, 0,
        plateau_packed, sizeof(plateau_packed)));
    const union {
        uint32_t bits;
        float value;
    } peak_quiet_nan = {.bits = UINT32_C(0x7FC00000)};
    const float unordered_peak_values[3] = {
        0.0f, peak_quiet_nan.value, 0.0f,
    };
    uint8_t unordered_peak_packed[1] = {0u};
    assert(goodix_primitives_nadt_extrema_neighborhood_mask(
        unordered_peak_values, 3u, 1u, 0u, 0,
        unordered_peak_packed, sizeof(unordered_peak_packed)));
    assert(unordered_peak_packed[0] == UINT8_C(0x05));

    const float alternating_extrema[9] = {
        0.0f, 2.0f, 0.0f, 2.0f, 0.0f, 2.0f, 0.0f, 2.0f, 0.0f,
    };
    const goodix_primitives_nadt_peak_mask_configuration peak_configuration = {
        .row_count = 1u, .plateau_radius = 0u, .first_label = 1u,
    };
    uint8_t peak_packed[2] = {0u, 0u};
    uint8_t peak_columns[9] = {0u};
    assert(goodix_primitives_nadt_peak_mask_columns(
        alternating_extrema, 9u, &peak_configuration, 0,
        peak_packed, sizeof(peak_packed),
        peak_columns, sizeof(peak_columns)));
    for (size_t index = 0u; index < 9u; ++index) {
        assert(peak_columns[index] == (uint8_t)((index & 1u) == 0u));
    }
    /* Eight packed bits still require the stock allocator's extra byte. */
    assert(!goodix_primitives_nadt_peak_mask_columns(
        alternating_extrema, 8u, &peak_configuration, 0,
        peak_packed, 1u, peak_columns, sizeof(peak_columns)));

    int32_t retained_peak_indices[2] = {-1, -1};
    size_t retained_peak_count = 0u;
    assert(goodix_primitives_nadt_peak_index_collect(
        alternating_extrema, 9u, &peak_configuration, 0,
        peak_packed, sizeof(peak_packed), peak_columns, sizeof(peak_columns),
        retained_peak_indices, 2u, &retained_peak_count));
    assert(retained_peak_count == 2u && retained_peak_indices[0] == 5 &&
           retained_peak_indices[1] == 7);
    assert(goodix_primitives_nadt_peak_index_collect(
        alternating_extrema, 9u, &peak_configuration, 1,
        peak_packed, sizeof(peak_packed), peak_columns, sizeof(peak_columns),
        retained_peak_indices, 2u, &retained_peak_count));
    assert(retained_peak_count == 2u && retained_peak_indices[0] == 4 &&
           retained_peak_indices[1] == 6);

    uint32_t peak_history_values[2] = {0u, 0u};
    uint32_t trough_history_values[2] = {0u, 0u};
    goodix_primitives_threshold_history peak_histories[2] = {
        {{peak_history_values, 0u, 2u}, 0u, 0u},
        {{trough_history_values, 0u, 2u}, 0u, 0u},
    };
    assert(goodix_primitives_nadt_peak_histories_update(
        alternating_extrema, 9u, 5, &peak_configuration,
        peak_packed, sizeof(peak_packed), peak_columns, sizeof(peak_columns),
        retained_peak_indices, 2u, peak_histories));
    assert(peak_history_values[0] == 5u && peak_history_values[1] == 7u &&
           peak_histories[0].window.count == 2u &&
           peak_histories[0].emitted_count == 2u);
    assert(trough_history_values[0] == 4u &&
           trough_history_values[1] == 6u &&
           peak_histories[1].window.count == 2u &&
           peak_histories[1].emitted_count == 2u);

    float fixed_peak_values[125] = {0.0f};
    goodix_primitives_nadt_channel_state fixed_peak_state = {0};
    fixed_peak_state.primary_ratio =
        (goodix_primitives_decimated_float_window) {
            .values = fixed_peak_values, .count = 125u, .capacity = 125u,
            .period = 1u, .phase = 0u, .cursor = 0u, .sum = 0.0f,
        };
    uint8_t fixed_peak_packed[563] = {0u};
    uint8_t fixed_peak_columns[125] = {0u};
    int32_t fixed_peak_indices[20] = {0};
    uint32_t fixed_peak_history_values[2][2] = {{0u, 0u}, {0u, 0u}};
    goodix_primitives_threshold_history fixed_peak_histories[2] = {
        {{fixed_peak_history_values[0], 0u, 2u}, 0u, 9u},
        {{fixed_peak_history_values[1], 0u, 2u}, 0u, 9u},
    };
    assert(goodix_primitives_nadt_primary_ratio_peak_update(
        &fixed_peak_state, 5, fixed_peak_packed, sizeof(fixed_peak_packed),
        fixed_peak_columns, sizeof(fixed_peak_columns),
        fixed_peak_indices, 20u, fixed_peak_histories));
    assert(fixed_peak_histories[0].window.count == 0u &&
           fixed_peak_histories[0].emitted_count == 0u &&
           fixed_peak_histories[1].window.count == 0u &&
           fixed_peak_histories[1].emitted_count == 0u);
    fixed_peak_state.primary_ratio.count = 124u;
    assert(!goodix_primitives_nadt_primary_ratio_peak_update(
        &fixed_peak_state, 5, fixed_peak_packed, sizeof(fixed_peak_packed),
        fixed_peak_columns, sizeof(fixed_peak_columns),
        fixed_peak_indices, 20u, fixed_peak_histories));

    uint8_t local_maximum_packed[2] = {0u, 0u};
    int16_t local_maximum_row_scores[1] = {-1};
    int16_t local_maximum_columns[9] = {0};
    assert(goodix_primitives_nadt_local_maximum_prefix_counts(
        alternating_extrema, 9u, 1u,
        local_maximum_packed, sizeof(local_maximum_packed),
        local_maximum_row_scores, 1u,
        local_maximum_columns, 9u));
    assert(local_maximum_packed[0] == UINT8_C(0x55) &&
           local_maximum_packed[1] == UINT8_C(0x01) &&
           local_maximum_row_scores[0] == 5);
    for (size_t index = 0u; index < 9u; ++index) {
        assert(local_maximum_columns[index] ==
               (int16_t)((index & 1u) == 0u));
    }
    int16_t local_peak_indices[2] = {-1, -1};
    size_t local_peak_count = 0u;
    assert(goodix_primitives_nadt_local_peak_indices(
        alternating_extrema, 9u, 1u, 0u,
        local_maximum_packed, sizeof(local_maximum_packed),
        local_maximum_row_scores, 1u, local_maximum_columns, 9u,
        local_peak_indices, 2u, &local_peak_count));
    assert(local_peak_count == 2u && local_peak_indices[0] == 3 &&
           local_peak_indices[1] == 5);

    const float equal_plateau_values[4] = {0.0f, 3.0f, 3.0f, 0.0f};
    uint8_t equal_plateau_packed[1] = {0u};
    int16_t equal_plateau_score[1] = {0};
    int16_t equal_plateau_columns[4] = {0};
    int16_t equal_plateau_index[1] = {-1};
    assert(goodix_primitives_nadt_local_peak_indices(
        equal_plateau_values, 4u, 1u, 0u,
        equal_plateau_packed, sizeof(equal_plateau_packed),
        equal_plateau_score, 1u, equal_plateau_columns, 4u,
        equal_plateau_index, 1u, &local_peak_count));
    assert(local_peak_count == 1u && equal_plateau_index[0] == 2);
    assert(goodix_primitives_nadt_local_maximum_prefix_counts(
        unordered_peak_values, 3u, 1u,
        equal_plateau_packed, sizeof(equal_plateau_packed),
        equal_plateau_score, 1u, equal_plateau_columns, 4u));
    assert(equal_plateau_packed[0] == UINT8_C(0x05) &&
           equal_plateau_score[0] == 2 &&
           equal_plateau_columns[1] == 0);
    assert(goodix_primitives_nadt_local_peak_indices(
        alternating_extrema, 9u, 1u, 0u,
        local_maximum_packed, sizeof(local_maximum_packed),
        local_maximum_row_scores, 1u, local_maximum_columns, 9u,
        NULL, 0u, &local_peak_count));
    assert(local_peak_count == 0u);

    const float correlation_first[3] = {1.0f, 2.0f, 3.0f};
    const float correlation_second[2] = {4.0f, 5.0f};
    float centered_correlation[5] = {
        -99.0f, -99.0f, -99.0f, -99.0f, -99.0f,
    };
    assert(goodix_primitives_centered_cross_correlation(
        correlation_first, 3u, correlation_second, 2u,
        centered_correlation, 5u));
    assert(centered_correlation[0] == -99.0f &&
           centered_correlation[1] == 5.0f &&
           centered_correlation[2] == 14.0f &&
           centered_correlation[3] == 23.0f &&
           centered_correlation[4] == 12.0f);
    for (size_t index = 0u; index < 5u; ++index) {
        centered_correlation[index] = -77.0f;
    }
    assert(goodix_primitives_centered_cross_correlation(
        correlation_second, 2u, correlation_first, 3u,
        centered_correlation, 5u));
    assert(centered_correlation[0] == 12.0f &&
           centered_correlation[1] == 23.0f &&
           centered_correlation[2] == 14.0f &&
           centered_correlation[3] == 5.0f &&
           centered_correlation[4] == -77.0f);
    assert(!goodix_primitives_centered_cross_correlation(
        correlation_first, 3u, correlation_second, 2u,
        centered_correlation, 4u));

    float autocorrelation_scratch[5] = {0.0f};
    float normalized_autocorrelation[3] = {0.0f};
    assert(goodix_primitives_nadt_normalized_autocorrelation(
        correlation_first, 3u, normalized_autocorrelation, 3u,
        autocorrelation_scratch, 5u));
    assert(normalized_autocorrelation[0] > 0.2142f &&
           normalized_autocorrelation[0] < 0.2143f &&
           normalized_autocorrelation[1] > 0.5714f &&
           normalized_autocorrelation[1] < 0.5715f &&
           normalized_autocorrelation[2] == 1.0f);
    const float subthreshold_autocorrelation_input[1] = {0.0005f};
    float subthreshold_autocorrelation_output[1] = {0.0f};
    float subthreshold_autocorrelation_scratch[1] = {0.0f};
    assert(goodix_primitives_nadt_normalized_autocorrelation(
        subthreshold_autocorrelation_input, 1u,
        subthreshold_autocorrelation_output, 1u,
        subthreshold_autocorrelation_scratch, 1u));
    assert(subthreshold_autocorrelation_output[0] > 0.00000024f &&
           subthreshold_autocorrelation_output[0] < 0.00000026f);
    const float unordered_autocorrelation_input[1] = {
        peak_quiet_nan.value,
    };
    assert(goodix_primitives_nadt_normalized_autocorrelation(
        unordered_autocorrelation_input, 1u,
        subthreshold_autocorrelation_output, 1u,
        subthreshold_autocorrelation_scratch, 1u));
    assert(subthreshold_autocorrelation_output[0] !=
           subthreshold_autocorrelation_output[0]);
    assert(!goodix_primitives_nadt_normalized_autocorrelation(
        correlation_first, 3u, normalized_autocorrelation, 3u,
        autocorrelation_scratch, 4u));

    float dual_primary[127] = {10.0f, 20.0f};
    float dual_secondary[128] = {100.0f, -100.0f, 50.0f};
    for (size_t index = 2u; index < 127u; ++index) {
        dual_primary[index] = 1.0f;
    }
    for (size_t index = 3u; index < 128u; ++index) {
        dual_secondary[index] = 1.0f;
    }
    const goodix_primitives_nadt_dual_window_source dual_source = {
        .primary_values = dual_primary,
        .primary_count = 127u,
        .secondary_values = dual_secondary,
        .secondary_count = 128u,
    };
    goodix_primitives_nadt_dual_window_workspace dual_workspace;
    goodix_primitives_nadt_dual_window_result dual_result = {
        .primary_dispersion = -1.0f,
        .secondary_dispersion = -2.0f,
        .correlation = -3.0f,
        .primary_rate = 111,
        .secondary_rate = 222,
        .primary_quality = 11.0f,
        .secondary_quality = 22.0f,
    };
    assert(goodix_primitives_nadt_dual_window_features_extract(
        &dual_source, square_root_fixture, &dual_workspace, &dual_result));
    assert(dual_result.primary_dispersion == 0.5f &&
           dual_result.secondary_dispersion == 0.5f &&
           dual_result.primary_rate == 111 &&
           dual_result.secondary_rate == 222 &&
           dual_result.primary_quality == 11.0f &&
           dual_result.secondary_quality == 22.0f &&
           dual_result.correlation > 0.999f &&
           dual_result.correlation < 1.001f &&
           dual_workspace.primary_packed[
               GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES - 1u] ==
               UINT16_C(0x3C00));

    for (size_t index = 0u; index < 127u; ++index) {
        dual_primary[index] = 0.0f;
    }
    for (size_t index = 0u; index < 128u; ++index) {
        dual_secondary[index] = 0.0f;
    }
    dual_primary[126] = 1.0f;
    dual_secondary[127] = 1.0f;
    dual_result = (goodix_primitives_nadt_dual_window_result) {
        .primary_dispersion = -1.0f,
        .secondary_dispersion = -2.0f,
        .correlation = -3.0f,
        .primary_rate = 111,
        .secondary_rate = 222,
        .primary_quality = 11.0f,
        .secondary_quality = 22.0f,
    };
    assert(goodix_primitives_nadt_dual_window_features_extract(
        &dual_source, square_root_fixture, &dual_workspace, &dual_result));
    assert(dual_result.primary_dispersion == 0.0f &&
           dual_result.secondary_dispersion == 0.0f &&
           dual_result.correlation == 1.0f &&
           dual_result.primary_rate == 0 &&
           dual_result.secondary_rate == 0 &&
           dual_result.primary_quality == 100.0f &&
           dual_result.secondary_quality == 100.0f &&
           dual_workspace.primary_packed[0] == UINT16_C(0x0000) &&
           dual_workspace.primary_packed[
               GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES - 1u] ==
               UINT16_C(0x3C00));

    const goodix_primitives_nadt_dual_window_source short_dual_source = {
        .primary_values = dual_primary,
        .primary_count = 124u,
        .secondary_values = dual_secondary,
        .secondary_count = 128u,
    };
    dual_result.correlation = -77.0f;
    assert(!goodix_primitives_nadt_dual_window_features_extract(
        &short_dual_source, square_root_fixture,
        &dual_workspace, &dual_result));
    assert(dual_result.correlation == -77.0f);
    assert(!goodix_primitives_nadt_dual_window_features_extract(
        &dual_source, NULL, &dual_workspace, &dual_result));
    assert(dual_result.correlation == -77.0f);

    int16_t auxiliary_values[55];
    for (size_t index = 0u; index < 5u; ++index) {
        auxiliary_values[index] = INT16_C(1234);
    }
    for (size_t index = 5u; index < 55u; ++index) {
        auxiliary_values[index] = (index & 1u) != 0u ? 0 : 100;
    }
    const goodix_primitives_nadt_auxiliary_configuration
        auxiliary_configuration = {
            .enabled = true,
            .range_threshold = 50,
            .deviation_threshold = 50,
            .required_extrema_count = 24u,
            .required_consecutive_windows = 2u,
        };
    goodix_primitives_nadt_auxiliary_state auxiliary_state = {
        .current_result = 7u,
        .mode = 3u,
    };
    goodix_primitives_nadt_auxiliary_workspace auxiliary_workspace;
    goodix_primitives_nadt_auxiliary_diagnostics auxiliary_diagnostics = {
        .range = -1,
        .maximum_count = UINT8_C(0xFF),
    };
    uint32_t auxiliary_result = UINT32_MAX;
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        auxiliary_values, 55u, &auxiliary_configuration, true,
        &auxiliary_state, &auxiliary_workspace, &auxiliary_diagnostics,
        square_root_fixture, &auxiliary_result));
    assert(auxiliary_result == 7u && auxiliary_state.mode == 3u &&
           auxiliary_state.consecutive_matches == 1u &&
           auxiliary_diagnostics.range == 100 &&
           auxiliary_diagnostics.maximum_count == 24u);
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        auxiliary_values, 55u, &auxiliary_configuration, true,
        &auxiliary_state, &auxiliary_workspace, &auxiliary_diagnostics,
        square_root_fixture, &auxiliary_result));
    assert(auxiliary_result == 2u && auxiliary_state.mode == 5u &&
           auxiliary_state.consecutive_matches == 0u);

    goodix_primitives_nadt_auxiliary_state gated_auxiliary_state = {
        .current_result = 9u,
        .mode = 4u,
        .consecutive_matches = 1u,
    };
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        auxiliary_values, 55u, &auxiliary_configuration, false,
        &gated_auxiliary_state, &auxiliary_workspace, NULL,
        square_root_fixture, &auxiliary_result));
    assert(auxiliary_result == 9u && gated_auxiliary_state.mode == 4u &&
           gated_auxiliary_state.consecutive_matches == 2u);

    int16_t flat_auxiliary_values[50] = {0};
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        flat_auxiliary_values, 50u, &auxiliary_configuration, true,
        &gated_auxiliary_state, NULL, &auxiliary_diagnostics, NULL,
        &auxiliary_result));
    assert(auxiliary_result == 9u &&
           gated_auxiliary_state.consecutive_matches == 0u &&
           auxiliary_diagnostics.range == 0);

    int16_t duplicate_auxiliary_values[50];
    for (size_t index = 0u; index < 50u; ++index) {
        duplicate_auxiliary_values[index] =
            ((index / 2u) & 1u) != 0u ? 100 : 0;
    }
    goodix_primitives_nadt_auxiliary_configuration duplicate_auxiliary =
        auxiliary_configuration;
    duplicate_auxiliary.range_threshold = 10;
    duplicate_auxiliary.deviation_threshold = 0;
    duplicate_auxiliary.required_extrema_count = 11u;
    duplicate_auxiliary.required_consecutive_windows = UINT8_MAX;
    goodix_primitives_nadt_auxiliary_state duplicate_auxiliary_state = {
        .current_result = 4u,
    };
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        duplicate_auxiliary_values, 50u, &duplicate_auxiliary, true,
        &duplicate_auxiliary_state, &auxiliary_workspace, NULL,
        square_root_fixture, &auxiliary_result));
    for (size_t index = 0u; index < 25u; ++index) {
        assert(duplicate_auxiliary_values[index] ==
               ((index & 1u) != 0u ? 100 : 0));
    }
    gated_auxiliary_state.consecutive_matches = 6u;
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        NULL, 49u, &auxiliary_configuration, true,
        &gated_auxiliary_state, NULL, NULL, NULL, &auxiliary_result));
    assert(auxiliary_result == 9u &&
           gated_auxiliary_state.consecutive_matches == 6u);

    goodix_primitives_nadt_auxiliary_configuration disabled_auxiliary =
        auxiliary_configuration;
    disabled_auxiliary.enabled = false;
    gated_auxiliary_state.processing = true;
    assert(goodix_primitives_nadt_auxiliary_state_classify(
        NULL, 500u, &disabled_auxiliary, true, &gated_auxiliary_state,
        NULL, NULL, NULL, &auxiliary_result));
    assert(auxiliary_result == 9u &&
           gated_auxiliary_state.consecutive_matches == 6u);
    auxiliary_result = UINT32_C(0xDEADBEEF);
    assert(!goodix_primitives_nadt_auxiliary_state_classify(
        auxiliary_values, 55u, &auxiliary_configuration, true,
        &gated_auxiliary_state, &auxiliary_workspace, NULL,
        square_root_fixture, &auxiliary_result));
    assert(auxiliary_result == UINT32_C(0xDEADBEEF) &&
           gated_auxiliary_state.consecutive_matches == 6u);

    int16_t alternate_samples[GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT];
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT; ++index) {
        alternate_samples[index] = index % 12u < 6u ? 1000 : -1000;
    }
    const goodix_primitives_nadt_alternate_configuration
        alternate_configuration = {
            .enabled = true,
            .sample_gate_limit = 10u,
            .minimum_range = 100,
            .minimum_interval = 0u,
            .maximum_interval_spread = 0u,
            .minimum_quality = 0u,
            .required_consecutive_windows = 2u,
        };
    goodix_primitives_nadt_alternate_state alternate_state = {
        .current_result = 0,
        .sample_gate = 5u,
    };
    goodix_primitives_nadt_alternate_workspace alternate_workspace;
    goodix_primitives_nadt_alternate_diagnostics alternate_diagnostics = {0};
    int32_t alternate_result = -1;
    assert(goodix_primitives_nadt_alternate_state_classify(
        alternate_samples, GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT,
        &alternate_configuration, &alternate_state, &alternate_workspace,
        &alternate_diagnostics, &alternate_result));
    assert(alternate_result == 0 &&
           alternate_state.consecutive_matches == 1u &&
           alternate_diagnostics.range == 2000 &&
           alternate_diagnostics.maxima_count >= 2u &&
           alternate_diagnostics.minima_count >= 2u &&
           alternate_diagnostics.minimum_interval == 6 &&
           alternate_diagnostics.interval_range == 0 &&
           alternate_diagnostics.quality > 0u);
    assert(goodix_primitives_nadt_alternate_state_classify(
        alternate_samples, GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT,
        &alternate_configuration, &alternate_state, &alternate_workspace,
        NULL, &alternate_result));
    assert(alternate_result == 2 && alternate_state.current_result == 2 &&
           alternate_state.mode == 4u &&
           alternate_state.consecutive_matches == 0u);

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT; ++index) {
        alternate_samples[index] = (index & 1u) != 0u ? 1000 : -1000;
    }
    goodix_primitives_nadt_alternate_configuration imbalanced_alternate =
        alternate_configuration;
    imbalanced_alternate.required_consecutive_windows = 1u;
    goodix_primitives_nadt_alternate_state imbalanced_alternate_state = {
        .current_result = 0,
        .sample_gate = 5u,
    };
    alternate_diagnostics =
        (goodix_primitives_nadt_alternate_diagnostics){0};
    assert(goodix_primitives_nadt_alternate_state_classify(
        alternate_samples, GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT,
        &imbalanced_alternate, &imbalanced_alternate_state,
        &alternate_workspace, &alternate_diagnostics, &alternate_result));
    assert(alternate_result == 2 &&
           alternate_diagnostics.maxima_count ==
               (uint8_t)(alternate_diagnostics.minima_count + 1u) &&
           alternate_workspace.maxima[0] < alternate_workspace.minima[0] &&
           alternate_diagnostics.minimum_interval == 1 &&
           alternate_diagnostics.interval_range == 0);

    goodix_primitives_nadt_alternate_configuration disabled_alternate =
        alternate_configuration;
    disabled_alternate.enabled = false;
    alternate_state.processing = true;
    alternate_result = -1;
    assert(goodix_primitives_nadt_alternate_state_classify(
        NULL, 0u, &disabled_alternate, &alternate_state, NULL, NULL,
        &alternate_result));
    assert(alternate_result == 2);
    disabled_alternate.enabled = true;
    alternate_result = -1;
    assert(!goodix_primitives_nadt_alternate_state_classify(
        alternate_samples, GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT,
        &disabled_alternate, &alternate_state, &alternate_workspace, NULL,
        &alternate_result));
    assert(alternate_result == 2);
    alternate_state.processing = false;
    alternate_state.current_result = 1;
    alternate_state.consecutive_matches = 9u;
    assert(goodix_primitives_nadt_alternate_state_classify(
        NULL, GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT - 1u,
        &alternate_configuration, &alternate_state, NULL, NULL,
        &alternate_result));
    assert(alternate_result == 1 &&
           alternate_state.consecutive_matches == 0u);

    uint16_t signal_intervals[
        GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES];
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES;
            ++index) {
        signal_intervals[index] = (uint16_t)(index * 10u);
    }
    float signal_history_values[15] = {0.0f};
    goodix_primitives_nadt_signal_confidence_state signal_state = {
        .rate_history = {
            .values = signal_history_values,
            .capacity = 15u,
        },
        .mode = 2,
    };
    goodix_primitives_nadt_signal_confidence_workspace signal_workspace;
    goodix_primitives_nadt_signal_confidence_diagnostics signal_diagnostics = {
        .selected_rate = -1,
        .selected_quality = -1.0f,
        .interval_deviation = -1.0f,
        .rate_appended = true,
    };
    goodix_primitives_nadt_dual_window_result signal_features = {
        .primary_rate = 80,
        .secondary_rate = 84,
        .primary_quality = 55.0f,
        .secondary_quality = 65.0f,
    };
    assert(goodix_primitives_nadt_signal_confidence_update(
        &signal_features, NULL, 0u, false, &signal_state, NULL, NULL, NULL,
        &signal_diagnostics));
    assert(signal_diagnostics.selected_rate == 80 &&
           signal_diagnostics.selected_quality == 65.0f &&
           signal_diagnostics.interval_deviation == 0.0f &&
           !signal_diagnostics.rate_appended &&
           signal_state.rate_history.count == 0u &&
           signal_state.mode == 2);

    signal_features.primary_rate = 60;
    signal_features.secondary_rate = 0;
    signal_features.primary_quality = 75.0f;
    assert(goodix_primitives_nadt_signal_confidence_update(
        &signal_features, signal_intervals,
        GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES, true,
        &signal_state, &signal_workspace, square_root_fixture,
        signal_confidence_exp_fixture, &signal_diagnostics));
    assert(signal_diagnostics.selected_rate == 60 &&
           signal_diagnostics.selected_quality == 75.0f &&
           signal_diagnostics.interval_deviation == 0.0f &&
           signal_diagnostics.rate_appended &&
           signal_state.rate_history.count == 1u &&
           signal_history_values[0] == 60.0f &&
           signal_state.low_variation_windows == 0 &&
           signal_state.rolling_mean == 60.0f &&
           signal_state.probability == 0.0f);

    signal_features.primary_rate = 64;
    assert(goodix_primitives_nadt_signal_confidence_update(
        &signal_features, signal_intervals,
        GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES, true,
        &signal_state, &signal_workspace, square_root_fixture,
        signal_confidence_exp_fixture, &signal_diagnostics));
    assert(signal_diagnostics.rate_appended &&
           signal_state.rate_history.count == 2u &&
           signal_history_values[1] == 64.0f &&
           signal_state.rolling_mean == 62.0f &&
           signal_state.probability > 0.0f);

    signal_features.primary_rate = 60;
    signal_features.primary_quality = 90.0f;
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES;
            ++index) {
        signal_intervals[index] = (index & 1u) == 0u ? 0u : 300u;
    }
    signal_state.high_variation_windows = 0;
    signal_state.low_variation_windows = 9;
    signal_state.mode = 0;
    for (size_t call = 0u; call < 5u; ++call) {
        assert(goodix_primitives_nadt_signal_confidence_update(
            &signal_features, signal_intervals,
            GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES, true,
            &signal_state, &signal_workspace, square_root_fixture,
            signal_confidence_exp_fixture, &signal_diagnostics));
    }
    assert(signal_state.high_variation_windows == 5 &&
           signal_state.low_variation_windows == 0 &&
           signal_state.mode == 1 &&
           signal_diagnostics.interval_deviation > 100.0f);

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES;
            ++index) {
        signal_intervals[index] = (uint16_t)(index * 10u);
    }
    signal_state.high_variation_windows = 7;
    signal_state.low_variation_windows = 0;
    for (size_t call = 0u; call < 5u; ++call) {
        assert(goodix_primitives_nadt_signal_confidence_update(
            &signal_features, signal_intervals,
            GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES, true,
            &signal_state, &signal_workspace, square_root_fixture,
            signal_confidence_exp_fixture, NULL));
    }
    assert(signal_state.high_variation_windows == 0 &&
           signal_state.low_variation_windows == 5 &&
           signal_state.mode == 0);

    signal_state.rate_history.count = 1u;
    signal_history_values[0] = 100.0f;
    signal_state.hold_windows = 10u;
    signal_state.probability = 0.75f;
    signal_features.primary_rate = 60;
    signal_features.primary_quality = 45.0f;
    assert(goodix_primitives_nadt_signal_confidence_update(
        &signal_features, signal_intervals,
        GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES, true,
        &signal_state, &signal_workspace, square_root_fixture,
        signal_confidence_exp_fixture, &signal_diagnostics));
    assert(signal_diagnostics.rate_appended &&
           signal_state.hold_windows == 0u &&
           signal_state.rate_history.count == 2u &&
           signal_history_values[1] == 60.0f);

    signal_features.primary_rate = 0;
    signal_features.secondary_rate = 0;
    signal_state.hold_windows = UINT8_MAX;
    signal_state.probability = 0.75f;
    assert(goodix_primitives_nadt_signal_confidence_update(
        &signal_features, signal_intervals,
        GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES, true,
        &signal_state, &signal_workspace, square_root_fixture,
        signal_confidence_exp_fixture, &signal_diagnostics));
    assert(signal_state.hold_windows == 0u &&
           signal_state.probability == 0.75f &&
           !signal_diagnostics.rate_appended);

    const uint32_t signal_count_before = signal_state.rate_history.count;
    assert(!goodix_primitives_nadt_signal_confidence_update(
        &signal_features, signal_intervals,
        GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES - 1u, true,
        &signal_state, &signal_workspace, square_root_fixture,
        signal_confidence_exp_fixture, NULL));
    assert(signal_state.rate_history.count == signal_count_before);

    float output_selection_history[3] = {0.0f, 0.0f, 79.4f};
    const goodix_primitives_nadt_output_selection_configuration
        output_selection_configuration = {
            .rate_threshold = 80u,
            .initial_sample = 3u,
            .override_sample = 5u,
            .flags = 7u,
        };
    goodix_primitives_nadt_output_selection_state output_selection_state = {
        .rate_history = {
            .values = output_selection_history,
            .count = 3u,
            .capacity = 3u,
        },
        .retained_rate = 70u,
        .phase_value = 0.0001f,
    };
    float selected_output = -1.0f;
    uint8_t selected_kind = UINT8_MAX;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 2u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == -1.0f && selected_kind == UINT8_MAX &&
           output_selection_state.transition_state == 0u);
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 3u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 79.0f && selected_kind == 5u &&
           output_selection_state.transition_state == 2u &&
           output_selection_state.retained_rate == 79u);

    output_selection_history[2] = 79.5f;
    output_selection_state.signal_present = 1u;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 79.0f && selected_kind == 2u &&
           output_selection_state.transition_state == 21u);
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 79.0f && selected_kind == 2u &&
           output_selection_state.transition_state == 21u);

    output_selection_history[2] = 70.0f;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 70.0f && selected_kind == 5u &&
           output_selection_state.transition_state == 2u &&
           output_selection_state.retained_rate == 70u);

    output_selection_state.transition_state = 1u;
    output_selection_state.retained_rate = 74u;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 74.0f && selected_kind == 2u &&
           output_selection_state.transition_state == 12u);
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 74.0f && selected_kind == 2u &&
           output_selection_state.transition_state == 12u);
    output_selection_history[2] = 80.0f;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 80.0f && selected_kind == 5u &&
           output_selection_state.transition_state == 1u &&
           output_selection_state.retained_rate == 80u);

    output_selection_state.transition_state = 12u;
    output_selection_state.retained_rate = 65u;
    output_selection_state.phase_value = 0.0f;
    output_selection_history[2] = 66.5f;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 4u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 67.0f && selected_kind == 2u &&
           output_selection_state.transition_state == 12u &&
           output_selection_state.retained_rate == 65u);

    output_selection_state.transition_state = 0u;
    output_selection_state.signal_present = 1u;
    output_selection_state.persistence = 6u;
    output_selection_state.retained_rate = 88u;
    output_selection_history[2] = 82.5f;
    assert(goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 5u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == 100.0f && selected_kind == 1u &&
           output_selection_state.transition_state == 0u &&
           output_selection_state.retained_rate == 88u);

    output_selection_state.transition_state = 3u;
    selected_output = -5.0f;
    selected_kind = UINT8_MAX;
    assert(!goodix_primitives_nadt_output_state_select(
        &output_selection_configuration, 5u, &output_selection_state,
        &selected_output, &selected_kind));
    assert(selected_output == -5.0f && selected_kind == UINT8_MAX);

    int nadt_preprocess_source = 123;
    uint32_t nadt_preprocess_output[16] = {0u};
    uint8_t nadt_preprocess_records[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_RECORD_BYTES * 2u] = {0u};
    uint8_t nadt_preprocess_summaries[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_BYTES * 2u] = {0u};
    float nadt_preprocess_inference[1] = {0.0f};
    float nadt_preprocess_adjusted[1] = {0.0f};
    float nadt_preprocess_selected_rate[1] = {0.0f};
    uint8_t nadt_preprocess_selected_kind[1] = {0u};
    goodix_primitives_nadt_preprocess_workspace nadt_preprocess_workspace = {
        .assembled_records = nadt_preprocess_records,
        .assembled_record_bytes = sizeof(nadt_preprocess_records),
        .summaries = nadt_preprocess_summaries,
        .summary_bytes = sizeof(nadt_preprocess_summaries),
        .inference_values = nadt_preprocess_inference,
        .inference_capacity = 1u,
        .adjusted_values = nadt_preprocess_adjusted,
        .adjusted_capacity = 1u,
        .selected_rates = nadt_preprocess_selected_rate,
        .selected_rate_capacity = 1u,
        .selected_kinds = nadt_preprocess_selected_kind,
        .selected_kind_capacity = 1u,
    };
    goodix_primitives_nadt_preprocess_state nadt_preprocess_state = {
        .initialized = true,
        .frame_count = 24u,
        .lane_count = 2u,
        .adjustment_enabled = true,
        .summary_metric_threshold = 100u,
    };
    const int32_t nadt_preprocess_quartic[7] = {
        0, 0, 0, 0, 0, 0, 950000,
    };
    nadt_preprocess_fixture nadt_preprocess = {
        .summary_metric = 8.0f,
        .inference_value = 3.0f,
        .expected_source = &nadt_preprocess_source,
        .expected_output = nadt_preprocess_output,
    };
    nadt_preprocess.statuses[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_SPECTRAL_PREPARE] = 99;
    nadt_preprocess.statuses[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE] = 23;
    const goodix_primitives_nadt_preprocess_plan nadt_preprocess_plan = {
        .execute = nadt_preprocess_stage_fixture,
        .context = &nadt_preprocess,
        .quartic_coefficients = nadt_preprocess_quartic,
        .quartic_coefficient_count = 7u,
    };
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &nadt_preprocess_state, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 23);
    static const goodix_primitives_nadt_preprocess_stage
        expected_nadt_preprocess_calls[13] = {
            GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_BATCH_ACCUMULATE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_ACCUMULATE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_SPECTRAL_PREPARE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_PRIMARY_PEAK_UPDATE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_DISPATCH,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_QUALITY_UPDATE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_TRANSITION_UPDATE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_QUALITY,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_SELECT,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_SIGNAL_CONFIDENCE,
            GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_BUILD,
        };
    assert(nadt_preprocess.call_count == 13u);
    for (size_t index = 0u; index < 13u; ++index) {
        assert(nadt_preprocess.calls[index] ==
               expected_nadt_preprocess_calls[index]);
    }
    assert(nadt_preprocess_state.process_count == 1u &&
           nadt_preprocess_state.frame_count == 25u &&
           nadt_preprocess_state.batch_index == 1u &&
           nadt_preprocess_adjusted[0] == 97.0f &&
           nadt_preprocess_output[12] == 1u);

    nadt_preprocess.call_count = 0u;
    nadt_preprocess.summary_metric = 100.0f;
    nadt_preprocess.statuses[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE] = 0;
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &nadt_preprocess_state, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 0);
    assert(nadt_preprocess_adjusted[0] == 95.0f &&
           nadt_preprocess_state.frame_count == 26u &&
           nadt_preprocess_state.batch_index == 1u);

    goodix_primitives_nadt_preprocess_state nadt_preprocess_failure_state =
        nadt_preprocess_state;
    nadt_preprocess_failure_state.process_count = 0u;
    nadt_preprocess_failure_state.frame_count = 0u;
    nadt_preprocess.call_count = 0u;
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_PREPROCESS_STAGE_COUNT; ++index) {
        nadt_preprocess.statuses[index] = 0;
    }
    nadt_preprocess.statuses[GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE] = 9;
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &nadt_preprocess_failure_state, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 9);
    assert(nadt_preprocess.call_count == 2u &&
           nadt_preprocess.calls[0] ==
               GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE &&
           nadt_preprocess.calls[1] ==
               GOODIX_PRIMITIVES_NADT_PREPROCESS_FAILURE_ENCODE &&
           nadt_preprocess_failure_state.process_count == 1u &&
           nadt_preprocess_failure_state.frame_count == 0u);

    nadt_preprocess.call_count = 0u;
    nadt_preprocess.statuses[GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE] = 0;
    nadt_preprocess.statuses[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_BATCH_ACCUMULATE] = 3;
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &nadt_preprocess_failure_state, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 3);
    assert(nadt_preprocess.call_count == 3u &&
           nadt_preprocess.calls[2] ==
               GOODIX_PRIMITIVES_NADT_PREPROCESS_FAILURE_ENCODE &&
           nadt_preprocess_failure_state.frame_count == 0u);

    nadt_preprocess.call_count = 0u;
    nadt_preprocess.statuses[
        GOODIX_PRIMITIVES_NADT_PREPROCESS_BATCH_ACCUMULATE] = 0;
    nadt_preprocess.statuses[GOODIX_PRIMITIVES_NADT_PREPROCESS_ACCUMULATE] = 4;
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &nadt_preprocess_failure_state, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 4);
    assert(nadt_preprocess.call_count == 3u &&
           nadt_preprocess.calls[2] ==
               GOODIX_PRIMITIVES_NADT_PREPROCESS_ACCUMULATE &&
           nadt_preprocess_failure_state.frame_count == 1u);

    goodix_primitives_nadt_preprocess_state uninitialized_preprocess = {
        .lane_count = 2u,
    };
    nadt_preprocess.call_count = 0u;
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &uninitialized_preprocess, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 7 &&
           nadt_preprocess.call_count == 0u);
    const size_t saved_summary_bytes = nadt_preprocess_workspace.summary_bytes;
    nadt_preprocess_workspace.summary_bytes = saved_summary_bytes - 1u;
    const uint32_t process_before_rejection =
        nadt_preprocess_failure_state.process_count;
    assert(goodix_primitives_nadt_preprocess_execute(
        &nadt_preprocess_plan, &nadt_preprocess_source,
        &nadt_preprocess_failure_state, &nadt_preprocess_workspace,
        nadt_preprocess_output, 16u) == 5 &&
           nadt_preprocess_failure_state.process_count ==
               process_before_rejection &&
           nadt_preprocess.call_count == 0u);
    nadt_preprocess_workspace.summary_bytes = saved_summary_bytes;

    const float strict_peak_values[7] = {0.0f, 3.0f, 1.0f, 5.0f,
                                         5.0f, 4.0f, 0.0f};
    float selected_peak = -1.0f;
    uint32_t selected_peak_index = UINT32_MAX;
    assert(goodix_primitives_strict_local_peak_max(
        strict_peak_values, 7u, &selected_peak, &selected_peak_index));
    assert(selected_peak == 3.0f && selected_peak_index == 1u);
    const float negative_peak_values[3] = {-3.0f, -1.0f, -2.0f};
    assert(goodix_primitives_strict_local_peak_max(
        negative_peak_values, 3u, &selected_peak, &selected_peak_index));
    assert(selected_peak == 0.0f && selected_peak_index == 0u);
    assert(!goodix_primitives_strict_local_peak_max(
        strict_peak_values, (size_t)UINT8_MAX + 1u,
        &selected_peak, &selected_peak_index));

    const float merge_incoming[5] = {20.0f, 7.0f, 11.0f, 13.0f, 17.0f};
    float merge_continuation[6] = {10.0f, 1.0f, 5.0f,
                                    2.0f, 3.0f, 4.0f};
    assert(goodix_primitives_merge_six_float_state(
        merge_continuation, merge_incoming, false));
    assert(merge_continuation[0] == 10.0f &&
           merge_continuation[1] == 1.0f &&
           merge_continuation[2] == 11.0f &&
           merge_continuation[3] == 2.0f &&
           merge_continuation[4] == 33.0f &&
           merge_continuation[5] == 4.0f);
    float merge_advance[6] = {10.0f, 1.0f, 5.0f, 2.0f, 3.0f, 4.0f};
    assert(goodix_primitives_merge_six_float_state(
        merge_advance, merge_incoming, true));
    assert(merge_advance[0] == 20.0f && merge_advance[1] == 3.0f &&
           merge_advance[2] == 11.0f && merge_advance[3] == 18.0f &&
           merge_advance[4] == 17.0f && merge_advance[5] == 14.0f);
    float merge_clamped[6] = {10.0f, 1.0f, 9.0f, 2.0f, 3.0f, 4.0f};
    assert(goodix_primitives_merge_six_float_state(
        merge_clamped, merge_incoming, true));
    assert(merge_clamped[1] == 1.0f);
    assert(!goodix_primitives_merge_six_float_state(
        NULL, merge_incoming, false));

    const float sign_run_source[7] = {
        2.0f, 1.0f, -1.0f, -2.0f, 0.0f, 3.0f, 4.0f,
    };
    const uint8_t sign_run_markers[7] = {0u, 1u, 0u, 1u, 1u, 0u, 0u};
    float sign_run_output[7] = {
        9.0f, 9.0f, 9.0f, 9.0f, 9.0f, 9.0f, 9.0f,
    };
    assert(goodix_primitives_zero_masked_sign_runs(
        sign_run_source, sign_run_markers, 7u, sign_run_output));
    assert(sign_run_output[0] == 0.0f && sign_run_output[1] == 0.0f &&
           sign_run_output[2] == 0.0f && sign_run_output[3] == 0.0f &&
           sign_run_output[4] == 9.0f && sign_run_output[5] == 3.0f &&
           sign_run_output[6] == 4.0f);
    const uint8_t tail_run_markers[7] = {0u, 0u, 0u, 0u, 0u, 0u, 1u};
    assert(goodix_primitives_zero_masked_sign_runs(
        sign_run_source, tail_run_markers, 7u, sign_run_output));
    assert(sign_run_output[4] == 0.0f && sign_run_output[5] == 0.0f &&
           sign_run_output[6] == 0.0f);
    assert(goodix_primitives_zero_masked_sign_runs(NULL, NULL, 0u, NULL));

    goodix_primitives_running_i32_statistics running_statistics = {
        -1.0f, -1.0f, -1, -1,
    };
    assert(goodix_primitives_running_i32_statistics_update(
        &running_statistics, 5, 1u));
    assert(running_statistics.mean == 5.0f &&
           running_statistics.squared_deviation_sum == 0.0f &&
           running_statistics.maximum == 5 && running_statistics.minimum == 5);
    assert(goodix_primitives_running_i32_statistics_update(
        &running_statistics, 8, 2u));
    assert(running_statistics.mean == 6.0f &&
           running_statistics.squared_deviation_sum == 6.0f &&
           running_statistics.maximum == 8 && running_statistics.minimum == 5);
    assert(goodix_primitives_running_i32_statistics_update(
        &running_statistics, 2, 3u));
    assert(running_statistics.mean == 5.0f &&
           running_statistics.squared_deviation_sum == 18.0f &&
           running_statistics.maximum == 8 && running_statistics.minimum == 2);
    assert(!goodix_primitives_running_i32_statistics_update(
        &running_statistics, 9, 0u));
    assert(!goodix_primitives_running_i32_statistics_update(NULL, 9, 1u));

    const float difference_numerator[3] = {1.0f, 2.0f, 3.0f};
    float difference_denominator[3] = {1.0f, 0.5f, 0.25f};
    const float difference_input_history[2] = {4.0f, 5.0f};
    const float difference_output_history[2] = {6.0f, 8.0f};
    float difference_result = 0.0f;
    assert(goodix_primitives_second_order_difference_output(
        2.0f, difference_numerator, difference_denominator,
        difference_input_history, difference_output_history,
        NULL, &difference_result));
    assert(difference_result == 20.0f);
    difference_denominator[0] = 3.0f;
    assert(goodix_primitives_second_order_difference_output(
        2.0f, difference_numerator, difference_denominator,
        difference_input_history, difference_output_history,
        round_double_away, &difference_result));
    assert(difference_result == 7.0f);
    assert(!goodix_primitives_second_order_difference_output(
        2.0f, difference_numerator, difference_denominator,
        difference_input_history, difference_output_history,
        NULL, &difference_result));

    const float optical_numerators[6] = {
        1.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f,
    };
    const float optical_denominators[6] = {
        1.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f,
    };
    float optical_input_histories[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    float optical_output_histories[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    goodix_primitives_nadt_optical_transform optical_transform = {
        .numerators = optical_numerators,
        .numerator_count = 6u,
        .denominators = optical_denominators,
        .denominator_count = 6u,
        .input_histories = optical_input_histories,
        .input_history_count = 4u,
        .output_histories = optical_output_histories,
        .output_history_count = 4u,
        .correction_threshold = 10.0f,
    };
    float optical_output = 0.0f;
    assert(goodix_primitives_nadt_optical_sample_transform(
        &optical_transform, 3.4f, round_double_away, &optical_output));
    assert(optical_output == 3.0f &&
           optical_input_histories[0] == 3.4f &&
           optical_input_histories[1] == 0.0f &&
           optical_input_histories[2] == 3.4f &&
           optical_input_histories[3] == 0.0f &&
           optical_output_histories[0] == 3.4f &&
           optical_output_histories[1] == 0.0f &&
           optical_output_histories[2] == 3.4f &&
           optical_output_histories[3] == 0.0f);

    optical_input_histories[0] = 1.0f;
    optical_input_histories[1] = 2.0f;
    optical_input_histories[2] = 0.0f;
    optical_input_histories[3] = 0.0f;
    memset(optical_output_histories, 0, sizeof(optical_output_histories));
    optical_transform.correction_threshold = 1.0f;
    assert(goodix_primitives_nadt_optical_sample_transform(
        &optical_transform, 4.0f, round_double_away, &optical_output));
    assert(optical_output == 4.0f &&
           optical_input_histories[0] == 4.0f &&
           optical_input_histories[1] == 4.0f);

    optical_input_histories[0] = 1.0f;
    optical_input_histories[1] = 2.0f;
    optical_transform.correction_threshold = 4.0f;
    assert(goodix_primitives_nadt_optical_sample_transform(
        &optical_transform, 4.0f, round_double_away, &optical_output));
    assert(optical_input_histories[0] == 4.0f &&
           optical_input_histories[1] == 1.0f);
    assert(!goodix_primitives_nadt_optical_sample_transform(
        &optical_transform, 4.0f, NULL, &optical_output));
    optical_transform.numerator_count = 5u;
    assert(!goodix_primitives_nadt_optical_sample_transform(
        &optical_transform, 4.0f, round_double_away, &optical_output));
    optical_transform.numerator_count = 6u;

    command_poll_fixture command_fixture = {
        7, 1, UINT32_MAX - UINT32_C(10), 200u, 0u, 0u,
    };
    const goodix_primitives_command_poll_ops command_operations = {
        poll_command, poll_register_read, poll_clock, &command_fixture,
    };
    int32_t poll_result = 0;
    assert(goodix_primitives_command_status_poll(
        &command_operations, UINT32_C(0x2000), &poll_result));
    assert(poll_result == 7 && command_fixture.command == UINT32_C(0xA6) &&
           command_fixture.status_reads == 0u);
    command_fixture.command_result = 0;
    command_fixture.status_result = 0;
    command_fixture.clock_value = 100u;
    command_fixture.clock_step = 1u;
    assert(goodix_primitives_command_status_poll(
        &command_operations, 0u, &poll_result));
    assert(poll_result == 0 && command_fixture.command == UINT32_C(0xAE) &&
           command_fixture.status_reads == 1u);
    command_fixture.status_result = 1;
    command_fixture.clock_value = UINT32_MAX - UINT32_C(10);
    command_fixture.clock_step = 200u;
    command_fixture.status_reads = 0u;
    assert(goodix_primitives_command_status_poll(
        &command_operations, 0u, &poll_result));
    assert(poll_result == -3 && command_fixture.status_reads == 2u);
    assert(!goodix_primitives_command_status_poll(NULL, 0u, &poll_result));

    float median_scratch[6] = {0.0f};
    float median = -1.0f;
    const float median_odd_values[5] = {8.0f, -2.0f, 4.0f, 9.0f, 1.0f};
    assert(goodix_primitives_float_median(
        median_odd_values, 5u, median_scratch, 6u, &median));
    assert(median == 4.0f);
    const float median_even_values[6] = {
        8.0f, -2.0f, 4.0f, 10.0f, 1.0f, 6.0f,
    };
    assert(goodix_primitives_float_median(
        median_even_values, 6u, median_scratch, 6u, &median));
    assert(median == 5.0f);
    assert(goodix_primitives_float_median(
        NULL, 0u, NULL, 0u, &median));
    assert(median == 0.0f);
    assert(!goodix_primitives_float_median(
        median_even_values, 6u, median_scratch, 5u, &median));

    const float mad_values[5] = {1.0f, 2.0f, 3.0f, 4.0f, 100.0f};
    float mad_scratch[5] = {0.0f};
    uint8_t mad_mask[5] = {0u};
    assert(goodix_primitives_hr_mad_inlier_mask(
        mad_values, 5u, 1, mad_scratch, 5u, mad_mask, 5u));
    assert(mad_scratch[0] == 2.0f && mad_scratch[1] == 1.0f &&
           mad_scratch[2] == 0.0f && mad_scratch[3] == 1.0f &&
           mad_scratch[4] == 97.0f);
    assert(mad_mask[0] == 1u && mad_mask[1] == 1u &&
           mad_mask[2] == 1u && mad_mask[3] == 1u &&
           mad_mask[4] == 0u);
    const float zero_mad_values[3] = {5.0f, 5.0f, 5.0f};
    assert(goodix_primitives_hr_mad_inlier_mask(
        zero_mad_values, 3u, 1, mad_scratch, 5u, mad_mask, 5u));
    assert(mad_scratch[0] == 0.0f && mad_scratch[1] == 0.0f &&
           mad_scratch[2] == 0.0f && mad_mask[0] == 1u &&
           mad_mask[1] == 1u && mad_mask[2] == 1u);
    assert(goodix_primitives_hr_mad_inlier_mask(
        zero_mad_values, 3u, -1, mad_scratch, 5u, mad_mask, 5u));
    assert(mad_mask[0] == 1u && mad_mask[1] == 1u && mad_mask[2] == 1u);
    assert(goodix_primitives_hr_mad_inlier_mask(
        mad_values, 5u, -1, mad_scratch, 5u, mad_mask, 5u));
    assert(mad_mask[0] == 0u && mad_mask[1] == 0u &&
           mad_mask[2] == 0u && mad_mask[3] == 0u && mad_mask[4] == 0u);
    mad_mask[0] = UINT8_C(0xA5);
    assert(!goodix_primitives_hr_mad_inlier_mask(
        mad_values, 5u, 1, mad_scratch, 4u, mad_mask, 5u));
    assert(mad_mask[0] == UINT8_C(0xA5));
    assert(!goodix_primitives_hr_mad_inlier_mask(
        mad_values, 5u, 1, mad_scratch, 5u, mad_mask, 4u));

    uint8_t teardown_tokens[25] = {0};
    release_order_fixture teardown_order = {0};
    goodix_primitives_algorithm_context_ownership algorithm_ownership = {
        &teardown_tokens[0], &teardown_tokens[1], &teardown_tokens[2],
        &teardown_tokens[3],
    };
    assert(goodix_primitives_algorithm_context_destroy(
               &algorithm_ownership, release_in_order,
               &teardown_order) == 0);
    assert(teardown_order.count == 5u);
    assert(teardown_order.allocations[0] == &teardown_tokens[3]);
    assert(teardown_order.allocations[1] == &teardown_tokens[0]);
    assert(teardown_order.allocations[2] == &teardown_tokens[1]);
    assert(teardown_order.allocations[3] == &teardown_tokens[2]);
    assert(teardown_order.allocations[4] == &algorithm_ownership);
    assert(goodix_primitives_algorithm_context_destroy(
               NULL, release_in_order, &teardown_order) == -1);

    teardown_order = (release_order_fixture){0};
    goodix_primitives_record_family_ownership record_ownership = {0};
    for (size_t index = 0u; index < 9u; ++index) {
        record_ownership.descriptor_allocations[index] =
            &teardown_tokens[index];
        record_ownership.owned_slots[index] = &teardown_tokens[9u + index];
    }
    for (size_t index = 0u; index < 7u; ++index) {
        record_ownership.extended_owned_slots[index] =
            &teardown_tokens[18u + index];
    }
    assert(goodix_primitives_record_family_teardown(
               &record_ownership, release_in_order, &teardown_order) == 0);
    assert(teardown_order.count == 25u);
    for (size_t index = 0u; index < 7u; ++index) {
        assert(teardown_order.allocations[index] == &teardown_tokens[index]);
    }
    assert(teardown_order.allocations[7] == &teardown_tokens[8]);
    assert(teardown_order.allocations[8] == &teardown_tokens[7]);
    for (size_t index = 0u; index < 9u; ++index) {
        assert(teardown_order.allocations[9u + index] ==
               &teardown_tokens[9u + index]);
        assert(record_ownership.owned_slots[index] == NULL);
    }
    for (size_t index = 0u; index < 7u; ++index) {
        assert(teardown_order.allocations[18u + index] ==
               &teardown_tokens[18u + index]);
        assert(record_ownership.extended_owned_slots[index] == NULL);
    }
    assert(record_ownership.descriptor_allocations[0] ==
           &teardown_tokens[0]);
    assert(goodix_primitives_record_family_teardown(
               NULL, release_in_order, &teardown_order) == -1);

    goodix_primitives_indexed_operation_fn indexed_operations[
        GOODIX_PRIMITIVES_STATE_COUNT] = {0};
    indexed_operations[3] = indexed_operation;
    uint32_t indexed_record[2] = {3u, UINT32_C(0xA55A)};
    int32_t indexed_result = 0;
    assert(goodix_primitives_dispatch_indexed_operation(
        indexed_record, indexed_operations, 11u, 22u, 33u, 44u, 55u,
        &indexed_result));
    assert(indexed_result == -17);
    for (size_t index = 0u; index < 6u; ++index) {
        assert(indexed_operation_arguments[index] ==
               (uintptr_t)(index == 0u ? 3u : index * 11u));
    }
    assert(goodix_primitives_dispatch_indexed_operation(
        NULL, indexed_operations, 0u, 0u, 0u, 0u, 0u, &indexed_result));
    assert(indexed_result == 0);
    indexed_record[0] = GOODIX_PRIMITIVES_STATE_COUNT;
    assert(!goodix_primitives_dispatch_indexed_operation(
        indexed_record, indexed_operations, 0u, 0u, 0u, 0u, 0u,
        &indexed_result));

    int32_t seven_word_result = 0;
    assert(goodix_primitives_nadt_graph_execute_veneer(
        seven_word_operation, 11u, 22u, 33u, 44u, 55u, 66u, 77u,
        &seven_word_result));
    assert(seven_word_result == INT32_C(-23));
    for (size_t index = 0u; index < 7u; ++index) {
        assert(seven_word_arguments[index] == (uintptr_t)(index + 1u) * 11u);
    }
    assert(!goodix_primitives_nadt_graph_execute_veneer(
        NULL, 0u, 0u, 0u, 0u, 0u, 0u, 0u, &seven_word_result));
    assert(!goodix_primitives_nadt_graph_execute_veneer(
        seven_word_operation, 0u, 0u, 0u, 0u, 0u, 0u, 0u, NULL));

    indexed_record[0] = 3u;
    uint32_t copied_input = UINT32_C(0x89ABCDEF);
    uint32_t copied_output = 0u;
    const goodix_primitives_word_dispatch_context word_dispatch = {
        .dispatch_record = indexed_record,
        .field_64 = (uintptr_t)UINT32_C(0x11223344),
        .field_68 = (uintptr_t)UINT32_C(0x55667788),
    };
    assert(goodix_primitives_dispatch_word_copy(
        &copied_input, &copied_output, &word_dispatch, indexed_operations));
    assert(copied_output == copied_input);
    assert(indexed_operation_arguments[0] == 3u);
    assert(indexed_operation_arguments[1] == word_dispatch.field_64);
    assert(indexed_operation_arguments[2] == (uintptr_t)&copied_input);
    assert(indexed_operation_arguments[3] == word_dispatch.field_68);
    assert(indexed_operation_arguments[4] == (uintptr_t)&copied_output);
    assert(indexed_operation_arguments[5] == (uintptr_t)0);

    indexed_operation_result = 0;
    copied_output = 0u;
    assert(!goodix_primitives_dispatch_word_copy(
        &copied_input, &copied_output, &word_dispatch, indexed_operations));
    assert(copied_output == copied_input);
    indexed_operation_result = INT32_C(-17);
    assert(!goodix_primitives_dispatch_word_copy(
        NULL, &copied_output, &word_dispatch, indexed_operations));
    assert(!goodix_primitives_dispatch_word_copy(
        &copied_input, NULL, &word_dispatch, indexed_operations));
    assert(!goodix_primitives_dispatch_word_copy(
        &copied_input, &copied_output, NULL, indexed_operations));

    const goodix_primitives_word_dispatch_context null_word_dispatch = {
        .dispatch_record = NULL,
        .field_64 = 0u,
        .field_68 = 0u,
    };
    assert(!goodix_primitives_dispatch_word_copy(
        &copied_input, &copied_output, &null_word_dispatch,
        indexed_operations));

    float score_workspace[198] = {0.0f};
    for (size_t index = 0u; index < 99u; ++index) {
        score_workspace[index] = (float)index + 0.25f;
    }
    uint32_t score_history[4] = {
        UINT32_C(0x3F800000), UINT32_C(22), UINT32_C(33), UINT32_C(44),
    };
    uint32_t score_dispatch_record[1] = {0u};
    goodix_primitives_spo2_score_context score_context = {
        .workspace = score_workspace,
        .workspace_count = 198u,
        .recent_inputs = score_history,
        .recent_input_count = 4u,
        .dispatch = {
            .dispatch_record = score_dispatch_record,
            .field_64 = (uintptr_t)UINT32_C(0x64),
            .field_68 = (uintptr_t)UINT32_C(0x68),
        },
    };
    goodix_primitives_indexed_operation_fn score_operations[
        GOODIX_PRIMITIVES_STATE_COUNT] = {0};
    score_operations[0] = score_operation;
    uint32_t score_history_scratch[4] = {0u};
    float score_output = -1.0f;
    score_operation_result = 0;
    score_operation_output = 2.0f;
    assert(!goodix_primitives_spo2_dispatch_logistic_score(
        &score_context, 7.5f, &score_output, score_history_scratch,
        score_operations, score_exponential));
    assert(score_output == 50.0f && score_exponential_argument == -2.0f);
    assert(score_history[0] == UINT32_C(0x3F800000) &&
           score_history[1] == UINT32_C(22) &&
           score_history[2] == UINT32_C(33) &&
           score_history[3] == UINT32_C(44));
    for (size_t index = 0u; index < 99u; ++index) {
        assert(score_workspace[99u + index] == score_workspace[index]);
    }

    score_operation_result = -1;
    score_operation_output = -100.0f;
    assert(goodix_primitives_spo2_dispatch_logistic_score(
        &score_context, 7.5f, &score_output, score_history_scratch,
        score_operations, score_exponential));
    assert(score_exponential_argument == 88.0f && score_output == 0.0f);
    score_context.workspace_count = 197u;
    assert(!goodix_primitives_spo2_dispatch_logistic_score(
        &score_context, 7.5f, &score_output, score_history_scratch,
        score_operations, score_exponential));
    score_context.workspace_count = 198u;

    float timed_buffer_a[2] = {1.0f, 2.0f};
    float timed_buffer_b[1] = {3.0f};
    float timed_buffer_c[2] = {4.0f, 5.0f};
    const goodix_primitives_float_span timed_buffers[3] = {
        {.values = timed_buffer_a, .count = 2u},
        {.values = timed_buffer_b, .count = 1u},
        {.values = timed_buffer_c, .count = 2u},
    };
    uint32_t timed_timestamps[2] = {0u, 130u};
    goodix_primitives_elapsed_state timed_elapsed = {
        .baseline = 100u,
        .elapsed_a = 150u,
        .elapsed_b = 180u,
        .slot_timestamps = timed_timestamps,
        .slot_count = 2u,
    };
    const goodix_primitives_timed_dispatch_context timed_dispatch = {
        .elapsed_state = &timed_elapsed,
        .mode_buffers = timed_buffers,
        .mode = 1u,
        .dispatch_record = indexed_record,
        .field_64 = (uintptr_t)UINT32_C(0x10203040),
        .field_68 = (uintptr_t)UINT32_C(0x50607080),
    };
    goodix_primitives_indexed_operation_fn timed_operations[
        GOODIX_PRIMITIVES_STATE_COUNT] = {0};
    timed_operations[3] = timed_indexed_operation;
    float timed_output = 7.0f;
    timed_dispatch_output_pointer = NULL;
    memset(indexed_operation_arguments, 0,
           sizeof(indexed_operation_arguments));
    assert(goodix_primitives_timed_dispatch_scaled_output(
               (uintptr_t)UINT32_C(0xA1B2C3D4), 0u, &timed_output,
               &timed_dispatch, timed_operations) == 1u);
    assert(timed_output == 7.0f && timed_buffer_a[0] == 1.0f &&
           timed_dispatch_output_pointer == NULL &&
           indexed_operation_arguments[0] == 0u);

    indexed_operation_result = 0;
    assert(goodix_primitives_timed_dispatch_scaled_output(
               (uintptr_t)UINT32_C(0xA1B2C3D4), 1u, &timed_output,
               &timed_dispatch, timed_operations) == 0u);
    assert(timed_output == 42.96875f);
    assert(timed_elapsed.baseline == 130u &&
           timed_elapsed.elapsed_a == 180u &&
           timed_elapsed.elapsed_b == 210u);
    assert(timed_buffer_a[0] == 0.0f && timed_buffer_a[1] == 0.0f &&
           timed_buffer_b[0] == 0.0f && timed_buffer_c[0] == 0.0f &&
           timed_buffer_c[1] == 0.0f);
    assert(indexed_operation_arguments[0] == 3u);
    assert(indexed_operation_arguments[1] == timed_dispatch.field_64);
    assert(indexed_operation_arguments[2] ==
           (uintptr_t)UINT32_C(0xA1B2C3D4));
    assert(indexed_operation_arguments[3] == timed_dispatch.field_68);
    assert(indexed_operation_arguments[4] != (uintptr_t)&timed_output);
    assert(indexed_operation_arguments[5] == (uintptr_t)0);
    assert(timed_dispatch_output_pointer == &timed_output);

    goodix_primitives_timed_dispatch_context timed_no_clear = timed_dispatch;
    timed_no_clear.mode = 2u;
    timed_buffer_a[0] = 6.0f;
    timed_output = 1.0f;
    assert(goodix_primitives_timed_dispatch_scaled_output(
               0u, 1u, &timed_output, &timed_no_clear,
               timed_operations) == 0u);
    assert(timed_output == 31.25f && timed_buffer_a[0] == 6.0f);

    goodix_primitives_indexed_operation_fn missing_timed_operations[
        GOODIX_PRIMITIVES_STATE_COUNT] = {0};
    timed_output = 8.0f;
    assert(goodix_primitives_timed_dispatch_scaled_output(
               0u, 1u, &timed_output, &timed_no_clear,
               missing_timed_operations) == 1u);
    assert(timed_output == 8.0f);

    indexed_operation_result = INT32_C(-17);
    timed_output = 9.0f;
    assert(goodix_primitives_timed_dispatch_scaled_output(
               0u, 1u, &timed_output, &timed_dispatch,
               timed_operations) == 1u);
    assert(timed_output == 0.0f);
    assert(goodix_primitives_timed_dispatch_scaled_output(
               0u, 1u, NULL, &timed_dispatch,
               timed_operations) == 1u);
    assert(goodix_primitives_timed_dispatch_scaled_output(
               0u, 1u, &timed_output, NULL,
               timed_operations) == 1u);

    assert(goodix_primitives_round_float_half_away_from_zero(0.49f) == 0.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(0.5f) == 1.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(1.49f) == 1.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(1.5f) == 2.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(-0.49f) ==
           -0.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(-0.5f) ==
           -1.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(-1.49f) ==
           -1.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(-1.5f) ==
           -2.0f);
    assert(goodix_primitives_round_float_half_away_from_zero(8388607.5f) ==
           8388608.0f);
    union {
        float f;
        uint32_t u;
    } rounded_bits;
    rounded_bits.f = goodix_primitives_round_float_half_away_from_zero(0.0f);
    assert(rounded_bits.u == UINT32_C(0x80000000));
    rounded_bits.u = UINT32_C(0x7F800000);
    assert(goodix_primitives_round_float_half_away_from_zero(rounded_bits.f) ==
           rounded_bits.f);
    rounded_bits.u = UINT32_C(0x7FC12345);
    const float rounded_nan =
        goodix_primitives_round_float_half_away_from_zero(rounded_bits.f);
    assert(rounded_nan != rounded_nan);

    goodix_primitives_record_family_ownership processing_family = {0};
    uint8_t processing_tokens[29] = {0};
    for (size_t index = 0u; index < 9u; ++index) {
        processing_family.descriptor_allocations[index] =
            &processing_tokens[index];
        processing_family.owned_slots[index] =
            &processing_tokens[9u + index];
    }
    for (size_t index = 0u; index < 7u; ++index) {
        processing_family.extended_owned_slots[index] =
            &processing_tokens[18u + index];
    }
    uint32_t processing_states[3][2] = {
        {0u, 0u}, {1u, 0u}, {2u, 0u},
    };
    goodix_primitives_processing_context_ownership processing_context = {
        .state_6c = processing_states[0],
        .state_70 = processing_states[1],
        .state_84 = processing_states[2],
        .owned_b0 = &processing_tokens[25],
        .owned_bc = &processing_tokens[26],
        .owned_cc = &processing_tokens[27],
        .owned_d8 = &processing_tokens[28],
    };
    release_order_fixture processing_order = {0};
    const unsigned dispatches_before_processing = dispatch_calls;
    assert(goodix_primitives_processing_context_destroy(
               &processing_family, &processing_context, handlers,
               release_in_order, &processing_order) == 0);
    assert(dispatch_calls == dispatches_before_processing + 3u);
    for (size_t index = 0u; index < 3u; ++index) {
        assert(processing_states[index][1] == UINT32_C(0xA55A));
    }
    assert(processing_order.count == 31u);
    assert(processing_order.allocations[25] == &processing_family);
    for (size_t index = 0u; index < 4u; ++index) {
        assert(processing_order.allocations[26u + index] ==
               &processing_tokens[25u + index]);
    }
    assert(processing_order.allocations[30] == &processing_context);
    assert(processing_context.owned_b0 == NULL &&
           processing_context.owned_bc == NULL &&
           processing_context.owned_cc == NULL &&
           processing_context.owned_d8 == NULL);
    assert(goodix_primitives_processing_context_destroy(
               NULL, &processing_context, handlers,
               release_in_order, &processing_order) == -1);

    payload_send_fixture payload_send = {0};
    assert(goodix_primitives_send_fixed_aa_pair(
        UINT8_C(0x5C), UINT32_C(0x11223344), UINT32_C(0x55667788),
        capture_payload_send, &payload_send));
    assert(payload_send.calls == 1u &&
           payload_send.selector == UINT8_C(0x5C) &&
           payload_send.payload[0] == UINT8_C(0xAA) &&
           payload_send.payload[1] == UINT8_C(0xAA) &&
           payload_send.payload_length == 2u &&
           payload_send.first == UINT32_C(0x11223344) &&
           payload_send.second == UINT32_C(0x55667788));
    assert(!goodix_primitives_send_fixed_aa_pair(
        0u, 0u, 0u, NULL, &payload_send));

    const int16_t quality_samples[4] = {2, 4, 0, 8};
    int16_t quality_indices[4] = {0};
    uint8_t quality_count = 0u;
    uint8_t quality = UINT8_C(0xFF);
    assert(goodix_primitives_peak_quality_update(
        quality_samples, 4u, quality_indices, 4u, &quality_count,
        4, 8, &quality));
    assert(quality_count == 1u && quality_indices[0] == 3 && quality == 0u);
    quality_indices[0] = 0;
    quality_indices[1] = 1;
    quality_count = 2u;
    assert(goodix_primitives_peak_quality_update(
        quality_samples, 4u, quality_indices, 4u, &quality_count,
        4, 8, &quality));
    assert(quality_count == 3u && quality_indices[2] == 3 && quality == 100u);
    const int16_t mismatched_quality_samples[4] = {2, 0, 0, -8};
    quality_indices[0] = 0;
    quality_indices[1] = 1;
    quality_count = 2u;
    assert(goodix_primitives_peak_quality_update(
        mismatched_quality_samples, 4u, quality_indices, 4u,
        &quality_count, 4, 8, &quality));
    assert(quality == 50u);
    const int16_t zero_quality_samples[4] = {0, 0, 0, 0};
    quality_indices[0] = 0;
    quality_indices[1] = 1;
    quality_count = 2u;
    assert(goodix_primitives_peak_quality_update(
        zero_quality_samples, 4u, quality_indices, 4u, &quality_count,
        4, 8, &quality));
    assert(quality == 0u);
    assert(!goodix_primitives_peak_quality_update(
        quality_samples, 4u, quality_indices, 3u, &quality_count,
        4, 8, &quality));

    const int16_t autocorrelation_i16_samples[3] = {1, 2, 3};
    int16_t autocorrelation_output[3] = {0};
    goodix_primitives_autocorrelation_state autocorrelation_state = {
        -1, 0,
    };
    assert(goodix_primitives_i16_autocorrelation_transform(
        autocorrelation_i16_samples, autocorrelation_output, 3u,
        0, 100, &autocorrelation_state));
    assert(autocorrelation_output[0] == 21 &&
           autocorrelation_output[1] == 57 &&
           autocorrelation_output[2] == 100);
    assert(autocorrelation_state.previous_output == 21 &&
           autocorrelation_state.previous_correlation == 3);
    const int32_t autocorrelation_i32_samples[3] = {1, 2, 3};
    autocorrelation_state = (goodix_primitives_autocorrelation_state){-1, 0};
    assert(goodix_primitives_i32_autocorrelation_transform(
        autocorrelation_i32_samples, autocorrelation_output, 3u,
        0, 100, &autocorrelation_state));
    assert(autocorrelation_output[0] == 21 &&
           autocorrelation_output[1] == 57 &&
           autocorrelation_output[2] == 100);
    autocorrelation_state =
        (goodix_primitives_autocorrelation_state){100, 20};
    assert(goodix_primitives_i16_autocorrelation_transform(
        autocorrelation_i16_samples, autocorrelation_output, 3u,
        0, 100, &autocorrelation_state));
    assert(autocorrelation_output[2] == 99);
    autocorrelation_state =
        (goodix_primitives_autocorrelation_state){100, 10};
    assert(goodix_primitives_i16_autocorrelation_transform(
        autocorrelation_i16_samples, autocorrelation_output, 3u,
        0, 100, &autocorrelation_state));
    assert(autocorrelation_output[2] == 101);
    const int16_t autocorrelation_zero_samples[3] = {0, 0, 0};
    autocorrelation_state =
        (goodix_primitives_autocorrelation_state){0, 99};
    assert(goodix_primitives_i16_autocorrelation_transform(
        autocorrelation_zero_samples, autocorrelation_output, 3u,
        0, 100, &autocorrelation_state));
    assert(autocorrelation_output[0] == 0 &&
           autocorrelation_output[1] == 0 &&
           autocorrelation_output[2] == 0);
    assert(goodix_primitives_i16_autocorrelation_transform(
        NULL, NULL, 0u, 0, 0, NULL));
    assert(!goodix_primitives_i16_autocorrelation_transform(
        autocorrelation_i16_samples, autocorrelation_output, 3u,
        0, 0, &autocorrelation_state));

    register_configuration_fixture register_configuration = {0};
    const goodix_primitives_register_configuration_ops register_operations = {
        capture_register_write, capture_bit_field_write,
        &register_configuration,
    };
    assert(goodix_primitives_reset_register_fields(&register_operations));
    assert(register_configuration.count == 2u &&
           register_configuration.events[0] == 1u &&
           register_configuration.events[1] == 2u &&
           register_configuration.addresses[0] == UINT16_C(0x0502) &&
           register_configuration.values[0] == 0u &&
           register_configuration.addresses[1] == 0u &&
           register_configuration.values[1] == 0u &&
           register_configuration.low_bit == 10u &&
           register_configuration.high_bit == 10u);
    assert(!goodix_primitives_reset_register_fields(NULL));
    goodix_primitives_register_configuration_ops missing_register_operation =
        register_operations;
    missing_register_operation.write_bit_field = NULL;
    assert(!goodix_primitives_reset_register_fields(
        &missing_register_operation));

    size_t sorted_count = 4u;
    assert(goodix_primitives_sorted_insert(
        sorted, &sorted_count, 6u, 2.5f));
    assert(sorted_count == 5u && sorted[2] == 2.5f && sorted[3] == 3.0f);
    assert(goodix_primitives_float_mean_or_zero(float_values, 4u) == 2.5f);
    assert(goodix_primitives_float_mean_or_zero(NULL, 0u) == 0.0f);
    assert(goodix_primitives_word_window_full(&last_window));

    const int16_t signed_values[4] = {8, -2, 4, -6};
    int16_t signed_mean = 0;
    size_t signed_minimum_index = 0u;
    assert(goodix_primitives_i16_mean(
        signed_values, 4u, &signed_mean));
    assert(signed_mean == 1);
    assert(goodix_primitives_i16_min_index(
        signed_values, 4u, &signed_minimum_index));
    assert(signed_minimum_index == 3u);
    float extremum = 0.0f;
    size_t extremum_index = 0u;
    assert(goodix_primitives_float_min_index(
        float_values, 4u, &extremum, &extremum_index));
    assert(extremum == 1.0f && extremum_index == 0u);
    assert(goodix_primitives_float_max_index(
        float_values, 4u, &extremum, &extremum_index));
    assert(extremum == 4.0f && extremum_index == 3u);

    void *released = indexed_records;
    assert(goodix_primitives_release_and_clear(
        &released, release_to_trace, &allocation));
    assert(released == NULL && release_calls == 1u);
    assert(goodix_primitives_release_if_present(
               indexed_copy, release_to_trace, &allocation) == 0);
    assert(release_calls == 2u);

    /* 0x0006DAD0 / 0x0006DB58: complete 14-release HRV teardown. */
    uint8_t hrv_allocations[13] = {0};
    goodix_primitives_hrv_context hrv_storage = {0};
    for (size_t index = 0u; index < 11u; ++index) {
        hrv_storage.subobjects[index] = &hrv_allocations[index];
    }
    hrv_storage.owned_6c =
        (goodix_primitives_hrv_work_a *)&hrv_allocations[11];
    hrv_storage.owned_70 =
        (goodix_primitives_hrv_work_b *)&hrv_allocations[12];
    goodix_primitives_hrv_context *hrv_context = &hrv_storage;
    const unsigned releases_before_hrv = release_calls;
    assert(goodix_primitives_hrv_context_destroy(
        &hrv_context, release_to_trace, &allocation));
    assert(hrv_context == NULL &&
           release_calls == releases_before_hrv + 14u);
    assert(goodix_primitives_hrv_context_destroy(
        &hrv_context, release_to_trace, &allocation));
    assert(release_calls == releases_before_hrv + 14u);
    assert(!goodix_primitives_hrv_context_destroy(
        NULL, release_to_trace, &allocation));

    /* 0x0006DB5C: all four recovered sample geometry families and default. */
    assert_hrv_geometry(25u, 0u, 1u, 37u, 65u, 1u);
    assert_hrv_geometry(150u, 1u, 3u, 75u, 65u, 1u);
    assert_hrv_geometry(500u, 2u, 5u, 151u, 65u, 1u);
    assert_hrv_geometry(800u, 3u, 4u, 251u, 129u, 1u);
    assert_hrv_geometry(123u, 0u, 1u, 151u, 65u, 4u);

    const goodix_primitives_hrv_configuration hrv_create_configuration = {
        UINT32_C(0x01020304), 25u, {100, 200, 300, 400},
    };
    allocation_trace hrv_failure = {0};
    hrv_failure.fail_after = 5u;
    goodix_primitives_hrv_context *failed_hrv = NULL;
    const unsigned releases_before_hrv_failure = release_calls;
    assert(goodix_primitives_hrv_context_create(
               &failed_hrv, &hrv_create_configuration, "pv_v1.1.0",
               allocate_from_trace, release_to_trace, &hrv_failure) ==
           GOODIX_PRIMITIVES_HRV_ALLOCATION_FAILED);
    assert(failed_hrv == NULL &&
           release_calls == releases_before_hrv_failure + 5u);
    allocation_trace hrv_invalid = {0};
    assert(goodix_primitives_hrv_context_create(
               &failed_hrv, &hrv_create_configuration, "pv_v1.0.0",
               allocate_from_trace, release_to_trace, &hrv_invalid) ==
           GOODIX_PRIMITIVES_HRV_INVALID);
    assert(hrv_invalid.calls == 0u);

    allocation_trace hrv_wrapper = {0};
    assert(goodix_primitives_hrv_initialize_for_sample_count(
               &failed_hrv, &hrv_create_configuration, 50u,
               allocate_from_trace, release_to_trace, &hrv_wrapper) ==
           GOODIX_PRIMITIVES_HRV_OK);
    assert(failed_hrv != NULL && failed_hrv->sample_count == 50u &&
           failed_hrv->mode == 1u && failed_hrv->divisor == 1u);
    assert(goodix_primitives_hrv_initialize_for_sample_count(
               &failed_hrv, &hrv_create_configuration, 100u,
               allocate_from_trace, release_to_trace, &hrv_wrapper) ==
           GOODIX_PRIMITIVES_HRV_ALREADY_INITIALIZED);
    assert(goodix_primitives_hrv_context_destroy(
        &failed_hrv, release_to_trace, &hrv_wrapper));

    allocation_trace hrv_dispatch_trace = {0};
    uint16_t hrv_result_status = 0u;
    uint8_t hrv_provider_active = 1u;
    uint32_t hrv_owner_active = 1u;
    assert(goodix_primitives_hrv_initialize_dispatch(
               &failed_hrv, &hrv_create_configuration, 100u,
               &hrv_result_status, &hrv_provider_active, &hrv_owner_active,
               allocate_from_trace, release_to_trace,
               &hrv_dispatch_trace) == 0);
    assert(failed_hrv != NULL && failed_hrv->mode == 2u);
    assert(hrv_result_status == UINT16_C(0x007F));
    assert(hrv_provider_active == 0u && hrv_owner_active == 0u);
    assert(goodix_primitives_hrv_context_destroy(
        &failed_hrv, release_to_trace, &hrv_dispatch_trace));

    allocation_trace heap = {0};
    void *records_allocation = NULL;
    void *scratch_allocation = NULL;
    assert(goodix_primitives_allocate_record_pair(
        2u, &records_allocation, &scratch_allocation,
        allocate_from_trace, &heap));
    assert(records_allocation != NULL && scratch_allocation != NULL);
    assert(goodix_primitives_release_context_pair_vector() ==
           (uintptr_t)&goodix_primitives_release_context_pair);

    const int32_t quartic_record[] = {0, 0, 1, 2, 3, 4, 5};
    const float quartic_value =
        goodix_primitives_quartic_evaluate(2.0f, quartic_record);
    assert(quartic_value > 0.0056999f && quartic_value < 0.0057001f);
    assert(goodix_primitives_quartic_evaluate(2.0f, NULL) == 0.0f);

    const float peak_values[] = {0.0f, 1.0f, 3.0f, 1.0f, 0.0f,
                                 2.0f, 4.0f, 2.0f, 0.0f};
    int32_t peak_indices[2] = {-1, -1};
    float selected_peaks[2] = {-1.0f, -1.0f};
    int32_t peak_count = -1;
    assert(goodix_primitives_peak_select(
        0.5f, peak_values, 9, 1, 8, 1, 2, peak_indices,
        selected_peaks, &peak_count));
    assert(peak_count == 2);
    assert(peak_indices[0] == 6 && peak_indices[1] == 2);
    assert(selected_peaks[0] == 4.0f && selected_peaks[1] == 3.0f);
    assert(!goodix_primitives_peak_select(
        0.5f, peak_values, 9, 1, 10, 1, 2, peak_indices,
        selected_peaks, &peak_count));

    const unsigned releases_before_pair = release_calls;
    assert(goodix_primitives_release_context_pair(
               records_allocation, scratch_allocation,
               release_to_trace, &heap) == 0);
    assert(release_calls == releases_before_pair + 2u);

    allocation_trace descriptors = {0};
    goodix_primitives_buffer_descriptor buffer_descriptor;
    assert(goodix_primitives_buffer_descriptor_initialize(
        &buffer_descriptor, NULL, 4u, sizeof(uint32_t),
        allocate_from_trace, &descriptors));
    assert(buffer_descriptor.data != NULL &&
           buffer_descriptor.count == 0u &&
           buffer_descriptor.capacity == 4u);
    goodix_primitives_extended_descriptor extended_descriptor;
    assert(goodix_primitives_extended_descriptor_initialize(
        &extended_descriptor, NULL, 8u, sizeof(uint16_t), 7u,
        allocate_from_trace, &descriptors));
    assert(extended_descriptor.data != NULL &&
           extended_descriptor.count == 0u &&
           extended_descriptor.capacity == 8u &&
           extended_descriptor.auxiliary == 0u &&
           extended_descriptor.status == 0u &&
           extended_descriptor.flag == 7u);
    goodix_primitives_float_descriptor float_descriptor;
    assert(goodix_primitives_float_descriptor_initialize(
        &float_descriptor, float_values, 4u, 3u,
        allocate_from_trace, &descriptors));
    assert(float_descriptor.data == float_values &&
           float_descriptor.count == 4u &&
           float_descriptor.capacity == 4u &&
           float_descriptor.flag == 3u &&
           float_descriptor.status == 0u &&
           float_descriptor.auxiliary == 0u &&
           float_descriptor.reserved == 0u);

    void *release_first = indexed_records;
    void *release_second = indexed_copy;
    assert(goodix_primitives_release_two_and_clear(
        &release_first, &release_second, release_to_trace, &allocation));
    assert(release_first == NULL && release_second == NULL);
    assert(release_calls == releases_before_pair + 4u);
    assert(goodix_primitives_release_two(
        indexed_records, indexed_copy, release_to_trace, &allocation));
    assert(release_calls == releases_before_pair + 6u);
    uint8_t fill[7] = {0};
    assert(goodix_primitives_byte_fill(UINT8_C(0xA6), fill,
                                       sizeof(fill)));
    for (size_t index = 0u; index < sizeof(fill); ++index) {
        assert(fill[index] == UINT8_C(0xA6));
    }

    uint32_t primary[4] = {1u, 2u, 3u, 4u};
    uint32_t secondary[4] = {5u, 6u, 7u, 8u};
    goodix_primitives_dual_buffer_descriptor dual;
    assert(goodix_primitives_dual_buffer_descriptor_initialize(
        &dual, 11u, 12u, primary, 4u, secondary, 4u, 3u, 13u));
    assert(dual.field_00 == 11u && dual.field_04 == 12u &&
           dual.primary == primary && dual.secondary == secondary &&
           dual.count == 3u && dual.field_14 == 13u);
    for (size_t index = 0u; index < 4u; ++index) {
        assert(primary[index] == 0u && secondary[index] == 0u);
    }
    assert(!goodix_primitives_dual_buffer_descriptor_initialize(
        &dual, 11u, 12u, primary, 3u, secondary, 4u, 3u, 13u));

    uint8_t nadt_bank_400_a[400];
    uint8_t nadt_bank_400_b[400];
    uint8_t nadt_bank_600[600];
    uint8_t nadt_bank_68[68];
    uint32_t nadt_counters[16];
    uint32_t nadt_init_primary[4];
    uint32_t nadt_init_secondary[4];
    memset(nadt_bank_400_a, UINT8_C(0xA5), sizeof(nadt_bank_400_a));
    memset(nadt_bank_400_b, UINT8_C(0xA5), sizeof(nadt_bank_400_b));
    memset(nadt_bank_600, UINT8_C(0xA5), sizeof(nadt_bank_600));
    memset(nadt_bank_68, UINT8_C(0xA5), sizeof(nadt_bank_68));
    memset(nadt_counters, UINT8_C(0xA5), sizeof(nadt_counters));
    memset(nadt_init_primary, UINT8_C(0xA5), sizeof(nadt_init_primary));
    memset(nadt_init_secondary, UINT8_C(0xA5), sizeof(nadt_init_secondary));
    goodix_primitives_dual_buffer_descriptor nadt_descriptor;
    goodix_primitives_nadt_initializer_workspace nadt_workspace = {
        .bank_400_a = nadt_bank_400_a,
        .bank_400_a_bytes = sizeof(nadt_bank_400_a),
        .bank_400_b = nadt_bank_400_b,
        .bank_400_b_bytes = sizeof(nadt_bank_400_b),
        .bank_600 = nadt_bank_600,
        .bank_600_bytes = sizeof(nadt_bank_600),
        .bank_68 = nadt_bank_68,
        .bank_68_bytes = sizeof(nadt_bank_68),
        .counters = nadt_counters,
        .counter_count = sizeof(nadt_counters) / sizeof(nadt_counters[0]),
        .descriptor = &nadt_descriptor,
        .descriptor_primary = nadt_init_primary,
        .descriptor_primary_words =
            sizeof(nadt_init_primary) / sizeof(nadt_init_primary[0]),
        .descriptor_secondary = nadt_init_secondary,
        .descriptor_secondary_words =
            sizeof(nadt_init_secondary) / sizeof(nadt_init_secondary[0]),
        .descriptor_field_00 = UINT32_C(0x000B1534),
        .descriptor_field_04 = UINT32_C(0x000B151C),
        .descriptor_field_14 = UINT32_C(0x457A1000),
    };
    allocation_trace nadt_allocation = {0};
    goodix_primitives_nadt_initializer_state nadt_state;
    goodix_primitives_nadt_runtime_configuration nadt_runtime;
    memset(&nadt_state, UINT8_C(0xA5), sizeof(nadt_state));
    memset(&nadt_runtime, UINT8_C(0xA5), sizeof(nadt_runtime));
    uint8_t nadt_result_status = UINT8_C(0xA5);
    assert(goodix_primitives_nadt_default_initialize(
               100u, &nadt_result_status, &nadt_state, &nadt_runtime,
               &nadt_workspace, allocate_from_trace, &nadt_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_OK);
    assert(nadt_result_status == 0u && nadt_allocation.calls == 1u);
    goodix_primitives_nadt_initializer_state expected_nadt_state;
    memset(&expected_nadt_state, 0, sizeof(expected_nadt_state));
    expected_nadt_state.marker = UINT8_C(0xBF);
    expected_nadt_state.threshold_09 = UINT8_C(0x32);
    expected_nadt_state.limit_34 = UINT32_C(0xFF);
    expected_nadt_state.allocation_58 = nadt_state.allocation_58;
    assert(nadt_state.allocation_58 != NULL &&
           memcmp(&nadt_state, &expected_nadt_state,
                  sizeof(nadt_state)) == 0);
    goodix_primitives_nadt_runtime_configuration expected_nadt_runtime;
    memset(&expected_nadt_runtime, 0, sizeof(expected_nadt_runtime));
    expected_nadt_runtime.sample_rate = 100u;
    expected_nadt_runtime.mode = 3u;
    expected_nadt_runtime.field_04 = 1200u;
    expected_nadt_runtime.enabled_06 = 1u;
    expected_nadt_runtime.field_07 = 4u;
    expected_nadt_runtime.field_08 = 2u;
    expected_nadt_runtime.offset_0c = INT32_C(0x000890EC);
    expected_nadt_runtime.offset_10 = INT32_C(0x00062DF4);
    expected_nadt_runtime.field_14 = 25u;
    expected_nadt_runtime.enabled_18 = 1u;
    expected_nadt_runtime.minimum_1c = 0x1.47ae14p-7f;
    expected_nadt_runtime.maximum_20 = 0x1.47ae14p-6f;
    expected_nadt_runtime.field_24 = 1u;
    expected_nadt_runtime.constant_28 = 8u;
    expected_nadt_runtime.field_2c = 300u;
    expected_nadt_runtime.timing_30 = 2;
    expected_nadt_runtime.constant_34 = 60u;
    expected_nadt_runtime.constant_36 = 40u;
    expected_nadt_runtime.timing_38 = 6;
    expected_nadt_runtime.field_3c = 50u;
    expected_nadt_runtime.field_3e = 140u;
    expected_nadt_runtime.field_40 = 8u;
    expected_nadt_runtime.half_field_44 = 4;
    expected_nadt_runtime.field_48 = 50u;
    expected_nadt_runtime.timing_4a = 5u;
    expected_nadt_runtime.constant_4c = 900u;
    expected_nadt_runtime.timing_4e = 3u;
    expected_nadt_runtime.timing_50 = 7u;
    expected_nadt_runtime.field_52_enabled = 1u;
    expected_nadt_runtime.constant_54 = 10u;
    expected_nadt_runtime.field_56 = 30u;
    expected_nadt_runtime.doubled_field_58 = 30;
    expected_nadt_runtime.field_5c = 15;
    expected_nadt_runtime.timing_60 = 15u;
    expected_nadt_runtime.constant_62 = 900u;
    expected_nadt_runtime.timing_64 = 6u;
    expected_nadt_runtime.constant_66 = 5u;
    expected_nadt_runtime.field_67 = 1u;
    expected_nadt_runtime.field_68 = 100u;
    expected_nadt_runtime.field_6a = 100u;
    expected_nadt_runtime.field_6c = 12u;
    expected_nadt_runtime.field_6d = 1u;
    expected_nadt_runtime.field_6e = 10u;
    expected_nadt_runtime.field_70 = 10u;
    expected_nadt_runtime.field_72 = 5u;
    expected_nadt_runtime.constant_74 = 70u;
    assert(memcmp(&nadt_runtime, &expected_nadt_runtime,
                  sizeof(nadt_runtime)) == 0);
    for (size_t index = 0u; index < sizeof(nadt_bank_400_a); ++index) {
        assert(nadt_bank_400_a[index] == 0u);
        assert(nadt_bank_400_b[index] == 0u);
    }
    for (size_t index = 0u; index < sizeof(nadt_bank_600); ++index) {
        assert(nadt_bank_600[index] == 0u);
    }
    for (size_t index = 0u; index < sizeof(nadt_bank_68); ++index) {
        assert(nadt_bank_68[index] == 0u);
    }
    for (size_t index = 0u; index < 16u; ++index) {
        assert(nadt_counters[index] == 0u);
    }
    assert(nadt_descriptor.field_00 == UINT32_C(0x000B1534) &&
           nadt_descriptor.field_04 == UINT32_C(0x000B151C) &&
           nadt_descriptor.primary == nadt_init_primary &&
           nadt_descriptor.secondary == nadt_init_secondary &&
           nadt_descriptor.count == 3u &&
           nadt_descriptor.field_14 == UINT32_C(0x457A1000));
    for (size_t index = 0u; index < 4u; ++index) {
        assert(nadt_init_primary[index] == 0u &&
               nadt_init_secondary[index] == 0u);
    }

    allocation_trace nadt_bad_rate_allocation = {0};
    assert(goodix_primitives_nadt_default_initialize(
               75u, &nadt_result_status, &nadt_state, &nadt_runtime,
               &nadt_workspace, allocate_from_trace,
               &nadt_bad_rate_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(nadt_result_status == 0u && nadt_bad_rate_allocation.calls == 1u &&
           nadt_runtime.sample_rate == 25u && nadt_runtime.mode == 3u);
    goodix_primitives_nadt_initialize_configuration nadt_bad_mode = {
        .sample_rate = 50u,
        .mode = 4u,
        .timing_base = 1000,
    };
    allocation_trace nadt_bad_mode_allocation = {0};
    assert(goodix_primitives_nadt_context_initialize(
               &nadt_bad_mode, "pv_v1.0.0", &nadt_state, &nadt_runtime,
               &nadt_workspace, allocate_from_trace,
               &nadt_bad_mode_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(nadt_bad_mode_allocation.calls == 1u &&
           nadt_runtime.sample_rate == 50u && nadt_runtime.mode == 1u);
    allocation_trace nadt_rejected_allocation = {0};
    assert(goodix_primitives_nadt_context_initialize(
               &nadt_bad_mode, "pv_v1.0.1", &nadt_state, &nadt_runtime,
               &nadt_workspace, allocate_from_trace,
               &nadt_rejected_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(nadt_rejected_allocation.calls == 0u);
    goodix_primitives_nadt_initializer_workspace nadt_small_workspace =
        nadt_workspace;
    nadt_small_workspace.bank_600_bytes = 599u;
    assert(goodix_primitives_nadt_context_initialize(
               &nadt_bad_mode, "pv_v1.0.0", &nadt_state, &nadt_runtime,
               &nadt_small_workspace, allocate_from_trace,
               &nadt_rejected_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(nadt_rejected_allocation.calls == 0u);
    allocation_trace nadt_exhausted_allocation = {0};
    nadt_exhausted_allocation.used = sizeof(nadt_exhausted_allocation.arena.bytes);
    assert(goodix_primitives_nadt_context_initialize(
               &nadt_bad_mode, "pv_v1.0.0", &nadt_state, &nadt_runtime,
               &nadt_workspace, allocate_from_trace,
               &nadt_exhausted_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(nadt_exhausted_allocation.calls == 0u);
    assert(goodix_primitives_nadt_default_initialize(
               100u, NULL, &nadt_state, &nadt_runtime, &nadt_workspace,
               allocate_from_trace, &nadt_rejected_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);

    allocation_trace nadt_reset_allocation = {0};
    void *const nadt_reset_owned = allocate_from_trace(
        &nadt_reset_allocation, 0x34u);
    assert(nadt_reset_owned != NULL && nadt_reset_allocation.calls == 1u);
    goodix_primitives_nadt_initializer_state nadt_reset_state;
    memset(&nadt_reset_state, UINT8_C(0xA5), sizeof(nadt_reset_state));
    nadt_reset_state.allocation_58 = nadt_reset_owned;
    goodix_primitives_nadt_initializer_state expected_nadt_reset =
        nadt_reset_state;
    expected_nadt_reset.word_28 = 0u;
    expected_nadt_reset.word_2c = 0u;
    expected_nadt_reset.flag_01 = 0u;
    expected_nadt_reset.counter_20 = 0u;
    expected_nadt_reset.flag_0a = 0u;
    expected_nadt_reset.counter_22 = 0u;
    expected_nadt_reset.counter_1c = 0u;
    memset(expected_nadt_reset.flags_04_08, 0,
           sizeof(expected_nadt_reset.flags_04_08));
    expected_nadt_reset.counter_1e = 0u;
    expected_nadt_reset.threshold_09 = UINT8_C(0x32);
    memset(expected_nadt_reset.flags_0b_18, 0,
           sizeof(expected_nadt_reset.flags_0b_18));
    expected_nadt_reset.word_38 = 0u;
    expected_nadt_reset.word_3c = 0u;
    expected_nadt_reset.word_40 = 0u;
    expected_nadt_reset.word_44 = 0u;
    expected_nadt_reset.counter_24 = 0u;
    expected_nadt_reset.counter_26 = 0u;
    expected_nadt_reset.word_48 = 0u;
    expected_nadt_reset.word_4c = 0u;
    expected_nadt_reset.flag_03 = 0u;
    expected_nadt_reset.allocation_58 = NULL;
    expected_nadt_reset.marker = UINT8_C(0xBF);
    memset(nadt_bank_400_a, UINT8_C(0xA5), sizeof(nadt_bank_400_a));
    memset(nadt_bank_400_b, UINT8_C(0xA5), sizeof(nadt_bank_400_b));
    memset(nadt_bank_600, UINT8_C(0xA5), sizeof(nadt_bank_600));
    memset(nadt_bank_68, UINT8_C(0xA5), sizeof(nadt_bank_68));
    memset(nadt_counters, UINT8_C(0xA5), sizeof(nadt_counters));
    memset(nadt_init_primary, UINT8_C(0xA5), sizeof(nadt_init_primary));
    memset(nadt_init_secondary, UINT8_C(0xA5),
           sizeof(nadt_init_secondary));
    const unsigned releases_before_nadt_reset = release_calls;
    assert(goodix_primitives_nadt_context_reset(
               &nadt_reset_state, &nadt_workspace,
               release_to_trace, &nadt_reset_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_OK);
    assert(release_calls == releases_before_nadt_reset + 1u &&
           nadt_reset_allocation.calls == 2u &&
           memcmp(&nadt_reset_state, &expected_nadt_reset,
                  sizeof(nadt_reset_state)) == 0);
    for (size_t index = 0u; index < sizeof(nadt_bank_400_a); ++index) {
        assert(nadt_bank_400_a[index] == 0u);
        assert(nadt_bank_400_b[index] == 0u);
    }
    for (size_t index = 0u; index < sizeof(nadt_bank_600); ++index) {
        assert(nadt_bank_600[index] == 0u);
    }
    for (size_t index = 0u; index < sizeof(nadt_bank_68); ++index) {
        assert(nadt_bank_68[index] == 0u);
    }
    for (size_t index = 0u; index < 16u; ++index) {
        assert(nadt_counters[index] == 0u);
    }
    assert(nadt_descriptor.field_00 == UINT32_C(0x000B1534) &&
           nadt_descriptor.field_04 == UINT32_C(0x000B151C) &&
           nadt_descriptor.primary == nadt_init_primary &&
           nadt_descriptor.secondary == nadt_init_secondary &&
           nadt_descriptor.count == 3u &&
           nadt_descriptor.field_14 == UINT32_C(0x457A1000));
    for (size_t index = 0u; index < 4u; ++index) {
        assert(nadt_init_primary[index] == 0u &&
               nadt_init_secondary[index] == 0u);
    }
    assert(goodix_primitives_nadt_context_reset(
               &nadt_reset_state, &nadt_workspace,
               release_to_trace, &nadt_reset_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_OK);
    assert(release_calls == releases_before_nadt_reset + 1u &&
           nadt_reset_allocation.calls == 2u);
    assert(goodix_primitives_nadt_context_reset(
               NULL, &nadt_workspace, release_to_trace,
               &nadt_reset_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(goodix_primitives_nadt_context_reset(
               &nadt_reset_state, &nadt_small_workspace,
               release_to_trace, &nadt_reset_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);
    assert(goodix_primitives_nadt_context_reset(
               &nadt_reset_state, &nadt_workspace, NULL,
               &nadt_reset_allocation) ==
           GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID);

    float supplied_storage[3] = {1.0f, 2.0f, 3.0f};
    goodix_primitives_float_storage float_storage;
    assert(goodix_primitives_float_storage_initialize(
        &float_storage, supplied_storage, 3u, NULL, NULL));
    assert(float_storage.values == supplied_storage &&
           float_storage.count == 3u && float_storage.capacity == 3u &&
           float_storage.limit == 3u && supplied_storage[0] == 1.0f);
    assert(goodix_primitives_float_storage_initialize(
        &float_storage, NULL, 5u, allocate_from_trace, &descriptors));
    assert(float_storage.values != NULL && float_storage.count == 0u &&
           float_storage.capacity == 5u && float_storage.limit == 0u);
    for (size_t index = 0u; index < 5u; ++index) {
        assert(float_storage.values[index] == 0.0f);
    }

    const float pair_coefficients[5] = {
        0.25f, 0.0f, -0.25f, 1.0f, -0.5f,
    };
    goodix_primitives_pair_buffer pair_buffer;
    assert(goodix_primitives_pair_buffer_initialize(
        &pair_buffer, 6u, pair_coefficients,
        allocate_from_trace, &descriptors));
    assert(pair_buffer.count == 3u && pair_buffer.records != NULL &&
           pair_buffer.coefficient_record == pair_coefficients);
    const uint8_t *pair_bytes = (const uint8_t *)pair_buffer.records;
    for (size_t index = 0u; index < 24u; ++index) {
        assert(pair_bytes[index] == 0u);
    }

    allocation_trace hr_secondary_trace = {0};
    goodix_primitives_hr_secondary_context hr_secondary;
    assert(goodix_primitives_hr_secondary_context_initialize(
        &hr_secondary, pair_coefficients, allocate_from_trace,
        release_to_trace, &hr_secondary_trace));
    assert(hr_secondary_trace.calls == 25u);
    for (size_t index = 0u; index < 9u; ++index) {
        assert(hr_secondary.pair_buffers[index].count == 4u &&
               hr_secondary.pair_buffers[index].records != NULL &&
               hr_secondary.pair_buffers[index].coefficient_record ==
                   pair_coefficients);
        const uint8_t *records =
            (const uint8_t *)hr_secondary.pair_buffers[index].records;
        for (size_t byte = 0u; byte < 32u; ++byte) {
            assert(records[byte] == 0u);
        }
        const uint16_t expected_capacity = index == 7u
            ? UINT16_C(60) : UINT16_C(180);
        assert(hr_secondary.i16_buffers[index].data != NULL &&
               hr_secondary.i16_buffers[index].count == 0u &&
               hr_secondary.i16_buffers[index].capacity ==
                   expected_capacity);
        const uint8_t *i16_bytes =
            (const uint8_t *)hr_secondary.i16_buffers[index].data;
        for (size_t byte = 0u;
             byte < (size_t)expected_capacity * sizeof(uint16_t); ++byte) {
            assert(i16_bytes[byte] == 0u);
        }
    }
    for (size_t index = 0u; index < 7u; ++index) {
        assert(hr_secondary.float_histories[index].data != NULL &&
               hr_secondary.float_histories[index].count == 0u &&
               hr_secondary.float_histories[index].capacity == 20u &&
               hr_secondary.float_histories[index].flag == 1u);
        const float *values =
            (const float *)hr_secondary.float_histories[index].data;
        for (size_t value = 0u; value < 20u; ++value) {
            assert(values[value] == 0.0f);
        }
    }
    const unsigned releases_before_hr_secondary = release_calls;
    assert(goodix_primitives_hr_secondary_context_release(
        &hr_secondary, release_to_trace, &hr_secondary_trace));
    assert(release_calls == releases_before_hr_secondary + 25u &&
           hr_secondary.pair_buffers[0].records == NULL &&
           hr_secondary.i16_buffers[0].data == NULL &&
           hr_secondary.float_histories[0].data == NULL);

    allocation_trace failing_hr_secondary = {.fail_after = 10u};
    const unsigned releases_before_hr_secondary_failure = release_calls;
    assert(!goodix_primitives_hr_secondary_context_initialize(
        &hr_secondary, pair_coefficients, allocate_from_trace,
        release_to_trace, &failing_hr_secondary));
    assert(release_calls == releases_before_hr_secondary_failure + 10u &&
           hr_secondary.pair_buffers[0].records == NULL &&
           hr_secondary.i16_buffers[0].data == NULL &&
           hr_secondary.float_histories[0].data == NULL);

    uint32_t hr_table_9d640 = UINT32_C(0x9D640001);
    uint32_t hr_table_a04cc = UINT32_C(0xA04CC002);
    uint32_t hr_table_a50b0 = UINT32_C(0xA50B0003);
    uint32_t hr_table_a692c = UINT32_C(0xA692C004);
    const goodix_primitives_tables hr_tables = {
        .table_9d640 = &hr_table_9d640,
        .table_a04cc = &hr_table_a04cc,
        .table_a50b0 = &hr_table_a50b0,
        .table_a692c = &hr_table_a692c,
    };
    hr_graph_fixture hr_graph_0 = {
        .expected_primary = &hr_table_a692c,
        .expected_size = UINT32_C(0x4BE4),
        .expected_secondary = &hr_table_a04cc,
        .result = UINT32_C(0x1000),
    };
    hr_graph_fixture hr_graph_1 = {
        .expected_primary = &hr_table_9d640,
        .expected_size = 0u,
        .expected_secondary = NULL,
        .result = UINT32_C(0x2000),
    };
    hr_graph_fixture hr_graph_6 = {
        .expected_primary = &hr_table_a50b0,
        .expected_size = 0u,
        .expected_secondary = NULL,
        .result = UINT32_C(0x6000),
    };
    const goodix_primitives_hr_graph_bindings hr_graph_bindings = {
        .selector_0 = {build_hr_graph, release_hr_graph, &hr_graph_0},
        .selector_1 = {build_hr_graph, release_hr_graph, &hr_graph_1},
        .selector_6 = {build_hr_graph, release_hr_graph, &hr_graph_6},
    };
    const goodix_primitives_hr_configuration hr_configuration = {
        .algorithm_mode = 1u,
        .sample_rate = 128u,
        .minimum_batch = 0,
        .secondary_window_override = 0u,
        .primary_window_override = 0u,
        .feature_stride = 0,
        .terminal_default = 0,
        .candidate_limit = 25u,
        .owner_word = UINT32_C(0x12345678),
    };
    goodix_primitives_hr_context_owner hr_owner = {0};
    allocation_trace hr_primary_trace = {0};
    assert(goodix_primitives_hr_primary_context_create(
               &hr_owner, &hr_configuration, sizeof(hr_configuration),
               "pv_v1.1.0", &hr_tables, pair_coefficients,
               &hr_graph_bindings, allocate_from_trace, release_to_trace,
               &hr_primary_trace) == GOODIX_PRIMITIVES_HR_OK);
    assert(hr_primary_trace.calls == 31u && hr_owner.primary != NULL &&
           hr_owner.secondary != NULL);
    const goodix_primitives_hr_primary_context *hr_primary =
        hr_owner.primary;
    assert(hr_primary->sample_rate == 128u &&
           hr_primary->samples_per_25hz_phase == 5u &&
           hr_primary->configuration_selector == 1u &&
           hr_primary->primary_window == 15u &&
           hr_primary->secondary_window == 9u &&
           hr_primary->minimum_batch == 1u &&
           hr_primary->feature_stride == 1 &&
           hr_primary->candidate_limit == 20u &&
           hr_primary->owner_word == UINT32_C(0x12345678) &&
           hr_primary->terminal_default == 202 &&
           hr_primary->primary_window_low_byte == 15u &&
           hr_primary->graph_latch == 0u);
    const uint8_t expected_hr_graph_control[6] = {
        1u, 5u, UINT8_C(0x80), 1u, 4u, 1u,
    };
    assert(memcmp(hr_primary->graph_control, expected_hr_graph_control,
                  sizeof(expected_hr_graph_control)) == 0 &&
           hr_primary->graph_span == UINT32_C(0x164) &&
           hr_primary->graph_mode == 2u &&
           hr_primary->graph_enabled == 1u &&
           hr_primary->graph_selector_0 == UINT32_C(0x1000) &&
           hr_primary->graph_selector_1 == UINT32_C(0x2000) &&
           hr_primary->graph_selector_6 == UINT32_C(0x6000));
    assert(hr_graph_0.build_calls == 1u && hr_graph_1.build_calls == 1u &&
           hr_graph_6.build_calls == 1u);
    assert(hr_primary->short_history_a.count == 0u &&
           hr_primary->short_history_a.capacity == 3u &&
           hr_primary->float_history_a.count == 0u &&
           hr_primary->float_history_a.capacity == 3u &&
           hr_primary->float_history_a.flag == 1u &&
           hr_primary->short_history_b.count == 0u &&
           hr_primary->short_history_b.capacity == 3u &&
           hr_primary->float_history_b.count == 0u &&
           hr_primary->float_history_b.capacity == 3u &&
           hr_primary->float_history_b.flag == 1u);
    for (size_t index = 0u; index < 4u; ++index) {
        assert(hr_primary->initial_accumulators[index] == 262144.0f &&
               hr_primary->initial_baselines[index] == 0.0);
    }
    const unsigned releases_before_hr_primary = release_calls;
    assert(goodix_primitives_hr_primary_context_release(
        &hr_owner, release_to_trace, &hr_primary_trace));
    assert(hr_owner.primary == NULL && hr_owner.secondary == NULL &&
           release_calls == releases_before_hr_primary + 31u &&
           hr_graph_0.release_calls == 1u &&
           hr_graph_1.release_calls == 1u &&
           hr_graph_6.release_calls == 1u);

    allocation_trace rejected_hr_primary = {0};
    assert(goodix_primitives_hr_primary_context_create(
               &hr_owner, &hr_configuration, sizeof(hr_configuration) - 1u,
               "pv_v1.1.0", &hr_tables, pair_coefficients,
               &hr_graph_bindings, allocate_from_trace, release_to_trace,
               &rejected_hr_primary) == GOODIX_PRIMITIVES_HR_INVALID);
    assert(goodix_primitives_hr_primary_context_create(
               &hr_owner, &hr_configuration, sizeof(hr_configuration),
               "pv_v1.0.0", &hr_tables, pair_coefficients,
               &hr_graph_bindings, allocate_from_trace, release_to_trace,
               &rejected_hr_primary) == GOODIX_PRIMITIVES_HR_INVALID &&
           rejected_hr_primary.calls == 0u);

    hr_graph_0.build_calls = 0u;
    hr_graph_0.release_calls = 0u;
    hr_graph_1.build_calls = 0u;
    hr_graph_1.release_calls = 0u;
    hr_graph_6.build_calls = 0u;
    hr_graph_6.release_calls = 0u;
    allocation_trace failing_hr_primary = {.fail_after = 30u};
    const unsigned releases_before_hr_primary_failure = release_calls;
    assert(goodix_primitives_hr_primary_context_create(
               &hr_owner, &hr_configuration, sizeof(hr_configuration),
               "pv_v1.1.0", &hr_tables, pair_coefficients,
               &hr_graph_bindings, allocate_from_trace, release_to_trace,
               &failing_hr_primary) == GOODIX_PRIMITIVES_HR_INVALID);
    assert(hr_owner.primary == NULL && hr_owner.secondary == NULL &&
           release_calls == releases_before_hr_primary_failure + 30u &&
           hr_graph_0.release_calls == 1u &&
           hr_graph_1.release_calls == 1u &&
           hr_graph_6.release_calls == 1u);

    allocation_trace lifecycle = {0};
    goodix_primitives_channel_state channel_state;
    const unsigned releases_before_channel = release_calls;
    assert(goodix_primitives_channel_state_initialize(
        &channel_state, 5u, 25u, allocate_from_trace,
        release_to_trace, &lifecycle));
    assert(channel_state.history.capacity == 25u &&
           channel_state.window.capacity == 17u &&
           channel_state.filtered.capacity == 25u &&
           channel_state.scalar.capacity == 1u &&
           channel_state.primary_buckets.capacity == 25u &&
           channel_state.secondary_buckets.capacity == 5u);
    assert(goodix_primitives_channel_state_release(
        &channel_state, release_to_trace, &lifecycle));
    assert(release_calls == releases_before_channel + 6u &&
           channel_state.history.data == NULL &&
           channel_state.secondary_buckets.data == NULL);
    assert(!goodix_primitives_channel_state_initialize(
        &channel_state, 0u, 25u, allocate_from_trace,
        release_to_trace, &lifecycle));

    allocation_trace session_lifecycle = {0};
    goodix_primitives_session_state session_state;
    const unsigned releases_before_session = release_calls;
    assert(goodix_primitives_session_state_initialize(
        &session_state, 5u, 25u, allocate_from_trace,
        release_to_trace, &session_lifecycle));
    assert(session_state.primary.window.capacity == 17u &&
           session_state.secondary.secondary_buckets.capacity == 5u &&
           session_state.tail_a.capacity == 125u &&
           session_state.tail_d.capacity == 125u &&
           session_state.tail_d.flag == 1u);
    assert(goodix_primitives_session_state_release(
        &session_state, release_to_trace, &session_lifecycle));
    assert(release_calls == releases_before_session + 16u &&
           session_state.primary.history.data == NULL &&
           session_state.tail_d.data == NULL);

    allocation_trace failing_lifecycle = {0};
    failing_lifecycle.fail_after = 1u;
    const unsigned releases_before_failure = release_calls;
    assert(!goodix_primitives_channel_state_initialize(
        &channel_state, 5u, 25u, allocate_from_trace,
        release_to_trace, &failing_lifecycle));
    assert(release_calls == releases_before_failure + 1u &&
           channel_state.history.data == NULL);

    allocation_trace owned_record_lifecycle = {0};
    goodix_primitives_owned_float_record *owned_record = NULL;
    const unsigned releases_before_owned_record = release_calls;
    assert(goodix_primitives_owned_float_record_create(
        &owned_record, 4u, 7u, allocate_from_trace,
        release_to_trace, &owned_record_lifecycle));
    assert(owned_record != NULL && owned_record->samples.capacity == 7u &&
           owned_record->samples.count == 0u &&
           owned_record->samples.flag == 1u);
    assert(goodix_primitives_owned_float_record_destroy(
        &owned_record, release_to_trace, &owned_record_lifecycle));
    assert(owned_record == NULL &&
           release_calls == releases_before_owned_record + 2u);

    allocation_trace record_array_lifecycle = {0};
    goodix_primitives_channel_record *channel_records = NULL;
    const unsigned releases_before_record_array = release_calls;
    assert(goodix_primitives_channel_record_array_create(
        &channel_records, 3u, true, UINT8_C(0x5A), allocate_from_trace,
        release_to_trace, &record_array_lifecycle));
    for (size_t index = 0u; index < 3u; ++index) {
        assert(channel_records[index].status == 0u &&
               channel_records[index].lower == 0.0f &&
               channel_records[index].upper == 0.0f &&
               channel_records[index].samples.capacity == 15u &&
               channel_records[index].samples.flag == 1u &&
               channel_records[index].tag == UINT8_C(0x5A));
    }
    assert(goodix_primitives_channel_record_array_destroy(
        &channel_records, 3u, true, release_to_trace,
        &record_array_lifecycle));
    assert(channel_records == NULL &&
           release_calls == releases_before_record_array + 4u);

    allocation_trace failing_record_array = {0};
    failing_record_array.fail_after = 2u;
    const unsigned releases_before_record_failure = release_calls;
    assert(!goodix_primitives_channel_record_array_create(
        &channel_records, 3u, true, 1u, allocate_from_trace,
        release_to_trace, &failing_record_array));
    assert(channel_records == NULL &&
           release_calls == releases_before_record_failure + 2u);

    allocation_trace aggregate_lifecycle = {0};
    goodix_primitives_session_aggregate aggregate;
    const unsigned releases_before_aggregate = release_calls;
    assert(goodix_primitives_session_aggregate_create(
        &aggregate, 5u, 25u, 5u, allocate_from_trace,
        release_to_trace, &aggregate_lifecycle));
    assert(aggregate.session != NULL && aggregate.pair != NULL &&
           aggregate.auxiliary.marker == 0u &&
           aggregate.auxiliary.full_rate.capacity == 125u &&
           aggregate.auxiliary.reduced_rate.capacity == 25u &&
           aggregate.pair->first.capacity == 20u &&
           aggregate.pair->second.capacity == 20u);
    assert(goodix_primitives_session_aggregate_destroy(
        &aggregate, release_to_trace, &aggregate_lifecycle));
    assert(aggregate.session == NULL && aggregate.pair == NULL &&
           release_calls == releases_before_aggregate + 22u);

    allocation_trace failing_aggregate = {0};
    failing_aggregate.fail_after = 1u;
    const unsigned releases_before_aggregate_failure = release_calls;
    assert(!goodix_primitives_session_aggregate_create(
        &aggregate, 5u, 25u, 5u, allocate_from_trace,
        release_to_trace, &failing_aggregate));
    assert(aggregate.session == NULL &&
           release_calls == releases_before_aggregate_failure + 1u);

    const unsigned releases_before_buffer_record = release_calls;
    assert(goodix_primitives_buffer_record_destroy(
        &buffer_record, release_to_trace, &allocation));
    assert(buffer_record == NULL &&
           release_calls == releases_before_buffer_record + 2u);

    /* 0x0006EB94 / 0x0006EB30: complete outer session lifecycle. */
    uint8_t outer_source[76] = {0};
    outer_source[0] = 2u;   /* record count */
    outer_source[4] = 125u; /* recovered geometry source */
    outer_source[28] = 1u;  /* channel-record array enabled */
    outer_source[32] = UINT8_C(0x5A);
    outer_source[71] = 4u;
    outer_source[72] = 7u;
    uint32_t outer_model[
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS];
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS;
            ++index) {
        outer_model[index] = UINT32_C(0xC0000000) + (uint32_t)index;
    }
    quantized_runtime_providers outer_providers = {0};
    outer_providers.vector_36dcc = (uintptr_t)0x00036DCDu;
    outer_providers.run_76bdc = (uintptr_t)0x00076BDDu;
    outer_providers.vector_30534 = (uintptr_t)0x00030535u;
    quantized_runtime outer_runtime;
    quantized_runtime_initialize(&outer_runtime, &outer_providers);
    allocation_trace outer_trace = {0};
    goodix_primitives_outer_session *outer = NULL;
    const unsigned releases_before_outer = release_calls;
    assert(goodix_primitives_outer_session_create(
        &outer, outer_source, sizeof(outer_source), "pre_pv_v1.1.0",
        &outer_runtime, outer_model,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x10000u,
        allocate_from_trace, release_to_trace, &outer_trace));
    assert(outer != NULL);
    assert(outer->processing_record[0] == 2u);
    assert(outer->processing_record[4] == 125u);
    assert(outer->processing_record[76] == 5u);
    assert(outer->processing_record[80] == 5u);
    assert(outer->processing_record[84] == 25u);
    assert(outer->processing_record[88] == 1u);
    assert(outer->processing_record[92] == 25u);
    assert(outer->record_pair.records != NULL);
    assert(outer->record_pair.scratch != NULL);
    assert(outer->aggregate.session != NULL);
    assert(outer->aggregate.pair != NULL);
    assert(outer->owned_float != NULL);
    assert(outer->owned_float->samples.capacity == 7u);
    assert(outer->buffer_record != NULL);
    assert(outer->model.instance != NULL);
    assert(outer->channel_records != NULL);
    assert(outer->channel_records[0].tag == UINT8_C(0x5A));
    assert(outer->channel_records[1].tag == UINT8_C(0x5A));
    assert(goodix_primitives_outer_session_destroy(
        &outer, release_to_trace, &outer_trace));
    assert(outer == NULL);
    assert(release_calls == releases_before_outer + 34u);

    allocation_trace rejected_outer = {0};
    assert(!goodix_primitives_outer_session_create(
        &outer, outer_source, sizeof(outer_source), "pre_pv_v1.0.0",
        &outer_runtime, outer_model,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x10000u,
        allocate_from_trace, release_to_trace, &rejected_outer));
    assert(outer == NULL && rejected_outer.calls == 0u);

    allocation_trace failing_outer = {0};
    failing_outer.fail_after = 3u;
    const unsigned releases_before_outer_failure = release_calls;
    assert(!goodix_primitives_outer_session_create(
        &outer, outer_source, sizeof(outer_source), "pre_pv_v1.1.0",
        &outer_runtime, outer_model,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x10000u,
        allocate_from_trace, release_to_trace, &failing_outer));
    assert(outer == NULL);
    assert(release_calls == releases_before_outer_failure + 3u);
}
