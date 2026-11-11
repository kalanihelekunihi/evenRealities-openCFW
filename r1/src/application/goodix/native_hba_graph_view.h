#ifndef R1_GOODIX_NATIVE_HBA_GRAPH_VIEW_H
#define R1_GOODIX_NATIVE_HBA_GRAPH_VIEW_H

#include <stdbool.h>
#include <stdint.h>
#include "../../vendor/quantized_runtime/quantized_runtime.h"
#include "../../vendor/goodix_primitives/goodix_primitives.h"

typedef struct {
    quantized_runtime_recurrent_descriptor recurrent[3];
    quantized_runtime_gomore_executor_graph_view graph;
} r1_goodix_hba_graph_view;

/* Plans retain pointers into their views and the initializer-owned records.
 * Bind in the final storage location; do not copy or move a bound set. */
typedef struct {
    r1_goodix_hba_graph_view views[2];
    quantized_runtime_goodix_second_graph_view mode6_view;
    quantized_runtime_goodix_executor_plan plans[2];
    quantized_runtime_goodix_second_executor_plan mode6_plan;
    bool bound;
} r1_goodix_hba_plan_set;

/* The initializer retains ownership of record. The view and record must
 * outlive any executor plan built from view.graph. Selectors 0/1 only. */
bool r1_goodix_hba_graph_view_bind(
    const void *record, const quantized_runtime *runtime,
    r1_goodix_hba_graph_view *view);
bool r1_goodix_hba_mode6_graph_view_bind(
    const void *record,
    quantized_runtime_goodix_second_graph_view *view);
uint32_t r1_goodix_hba_stage_token_rewrite(void *context,uint32_t token);
bool r1_goodix_hba_plan_set_bind(
    const void *mode0_record, const void *mode1_record,
    const void *mode6_record, const quantized_runtime *runtime,
    r1_goodix_hba_plan_set *set,
    quantized_runtime_stage_token_resolver_fn resolve,
    void *resolve_context,
    quantized_runtime_multi_stage_token_resolver_fn resolve_multi,
    void *resolve_multi_context);
bool r1_goodix_hba_plan_set_bind_source(
    const void *mode0_record, const void *mode1_record,
    const void *mode6_record, const quantized_runtime *runtime,
    r1_goodix_hba_plan_set *set);
/* Stock 0x43B30 shifts mode-0 recurrent weight words +0x1E0..+0x1E8
 * using the remap table at +0x238. Load before the timed dispatch; commit
 * after its update and before executing the mode-0 graph. */
bool r1_goodix_hba_elapsed_bind(
    const r1_goodix_hba_plan_set *set,
    goodix_primitives_elapsed_state *state);
bool r1_goodix_hba_elapsed_commit(
    r1_goodix_hba_plan_set *set,
    const goodix_primitives_elapsed_state *state);
/* Stock 0x36BFA clears the three mode-0 recurrent state buffers when mode=1.
 * The count and pointer pairs are the first two words of these records. */
bool r1_goodix_hba_mode_buffers_bind(
    const r1_goodix_hba_plan_set *set,
    goodix_primitives_float_span buffers[3]);

#endif
