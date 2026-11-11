#ifndef R1_GOODIX_NATIVE_HBA_GRAPH_EXECUTE_H
#define R1_GOODIX_NATIVE_HBA_GRAPH_EXECUTE_H

#include "native_hba_graph_view.h"
#include "../../vendor/goodix_primitives/goodix_primitives.h"

/* Execute a bound graph with caller-owned scratch. Mode one needs a full
 * graph arena because its public input is only the 396-float model vector. */
bool r1_goodix_hba_mode01_execute(
    const r1_goodix_hba_plan_set *set, uint32_t mode,
    const goodix_primitives_graph_executor_input *input,
    float *output, void *scratch, size_t scratch_capacity);

/* Selector six transforms the 1,935-float HBA workspace in place. */
bool r1_goodix_hba_mode6_execute(
    const r1_goodix_hba_plan_set *set, float *workspace,
    size_t workspace_count, void *temporary, size_t temporary_capacity);

#endif
