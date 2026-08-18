#ifndef R1_GH3X2X_RECONSTRUCTED_ROOTS_H
#define R1_GH3X2X_RECONSTRUCTED_ROOTS_H

/*
 * Direct, transparent executors for the recovered retail Goodix roots.
 *
 * These records deliberately do not hide plan or workspace construction.
 * Every persistent object remains caller-owned, and initialization is an
 * explicit callback that must establish the complete state for the supplied
 * sample rate before a root can run.  This lets target composition fail
 * closed while the remaining initializer/global bindings are recovered.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "goodix_primitives/goodix_primitives.h"
#include "r1_gh3x2x_provider_composer.h"

typedef bool (*r1_gh3x2x_root_state_initialize_fn)(
    void *context, uint16_t sample_rate_hz);
typedef bool (*r1_gh3x2x_root_state_deinitialize_fn)(void *context);

typedef struct {
    void *context;
    r1_gh3x2x_root_state_initialize_fn initialize;
    r1_gh3x2x_root_state_deinitialize_fn deinitialize;
} r1_gh3x2x_root_state_lifecycle;

typedef struct {
    const goodix_primitives_hba_process_configuration *configuration;
    const goodix_primitives_hba_process_plan *plan;
    goodix_primitives_hba_process_state *state;
    goodix_primitives_hba_stream_workspace *stream_workspace;
    goodix_primitives_hba_process_workspace *workspace;
    goodix_primitives_hba_runtime *runtime;
    const uint8_t *filter_code;
    size_t filter_code_count;
    r1_gh3x2x_root_state_lifecycle lifecycle;
    bool initialized;
} r1_gh3x2x_hba_root_context;

typedef struct {
    const goodix_primitives_hr_configuration *configuration;
    const goodix_primitives_hba_runtime_bindings *runtime_bindings;
    goodix_primitives_allocate_fn allocate;
    goodix_primitives_release_fn release;
    void *provider_context;
    goodix_primitives_hr_context_owner context_owner;
    goodix_primitives_hr_graph_bindings graph_bindings;
    quantized_runtime_gomore_executor_graph graph_selector_0;
    quantized_runtime_gomore_executor_graph graph_selector_1;
    quantized_runtime_goodix_second_graph graph_selector_6;
    quantized_runtime_goodix_executor_plan graph_plan_0;
    quantized_runtime_goodix_executor_plan graph_plan_1;
    quantized_runtime_goodix_second_executor_plan graph_plan_6;
    quantized_runtime_stage_token_resolver_fn stage_resolver;
    void *stage_resolver_context;
    quantized_runtime_multi_stage_token_resolver_fn multi_stage_resolver;
    void *multi_stage_resolver_context;
    uint8_t graph_6_temporary[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_TEMPORARY_BYTES];
    goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT];
    bool graph_selector_0_built;
    bool graph_selector_1_built;
    bool graph_selector_6_built;
    float filter_coefficients[20];
    goodix_primitives_hba_runtime runtime;
} r1_gh3x2x_hba_reconstructed_state;

typedef struct {
    const goodix_primitives_hrv_process_plan *plan;
    goodix_primitives_hrv_process_state *state;
    goodix_primitives_hrv_process_workspace *workspace;
    goodix_primitives_hrv_runtime *runtime;
    r1_gh3x2x_root_state_lifecycle lifecycle;
    bool initialized;
} r1_gh3x2x_hrv_root_context;

typedef struct {
    const goodix_primitives_hrv_configuration *configuration;
    goodix_primitives_allocate_fn allocate;
    goodix_primitives_release_fn release;
    void *provider_context;
    goodix_primitives_float_unary_fn square_root;
    goodix_primitives_hrv_context *context;
    goodix_primitives_hrv_runtime runtime;
} r1_gh3x2x_hrv_reconstructed_state;

typedef struct {
    const goodix_primitives_nadt_preprocess_plan *plan;
    goodix_primitives_nadt_preprocess_state *state;
    goodix_primitives_nadt_preprocess_workspace *workspace;
    goodix_primitives_spo2_runtime *runtime;
    const char *weights_version;
    r1_gh3x2x_root_state_lifecycle lifecycle;
    bool initialized;
} r1_gh3x2x_spo2_root_context;

typedef struct {
    goodix_primitives_spo2_runtime_bindings bindings;
    const char *weights_version;
    goodix_primitives_spo2_runtime runtime;
} r1_gh3x2x_spo2_reconstructed_state;

/* Construct complete composer bindings around the recovered roots.  The
 * caller must retain both context and all referenced storage for the entire
 * binding lifetime.  Rebuilding an initialized context is rejected. */
bool r1_gh3x2x_make_hba_root_binding(
    r1_gh3x2x_hba_root_context *context,
    r1_gh3x2x_root_binding *binding);
/* Compose HBA directly from the recovered 0x6D204/0x72C48 initializers and
 * SHA-pinned graph/filter data. The three target-ABI graph records are built
 * and owned by state; their typed executable operations remain explicit
 * source-level bindings in state->runtime_bindings. */
bool r1_gh3x2x_make_reconstructed_hba_root_binding(
    r1_gh3x2x_hba_root_context *context,
    r1_gh3x2x_hba_reconstructed_state *state,
    r1_gh3x2x_root_binding *binding);
bool r1_gh3x2x_make_hrv_root_binding(
    r1_gh3x2x_hrv_root_context *context,
    r1_gh3x2x_root_binding *binding);
/* Compose the HRV root directly from the recovered 0x6DB5C initializer.
 * The state owns every former global/workspace binding; allocation and math
 * providers remain explicit ordinary C callbacks. */
bool r1_gh3x2x_make_reconstructed_hrv_root_binding(
    r1_gh3x2x_hrv_root_context *context,
    r1_gh3x2x_hrv_reconstructed_state *state,
    r1_gh3x2x_root_binding *binding);
bool r1_gh3x2x_make_spo2_root_binding(
    r1_gh3x2x_spo2_root_context *context,
    r1_gh3x2x_root_binding *binding);
/* Compose the exact 0x6EB94 outer session and 0x6E838 root from the
 * SHA-pinned configuration/model data and a typed source stage executor. */
bool r1_gh3x2x_make_reconstructed_spo2_root_binding(
    r1_gh3x2x_spo2_root_context *context,
    r1_gh3x2x_spo2_reconstructed_state *state,
    r1_gh3x2x_root_binding *binding);

/* Exact outer-wrapper result transformations, exposed for evidence-pinned
 * tests and for callers that replay captured root outputs. */
r1_gh3x2x_root_status r1_gh3x2x_format_hba_root_output(
    uint32_t status, const goodix_primitives_hba_process_output *root,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]);
r1_gh3x2x_root_status r1_gh3x2x_format_spo2_root_output(
    int32_t status,
    const uint32_t root_words[R1_GH3X2X_ALGO_RESULT_COUNT],
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]);

#endif
