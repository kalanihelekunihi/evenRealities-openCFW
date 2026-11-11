#ifndef R1_GOODIX_NATIVE_HBA_GRAPH_CALLBACKS_H
#define R1_GOODIX_NATIVE_HBA_GRAPH_CALLBACKS_H

#include "native_hba_graph_execute.h"

/* Bind only while the initializer-owned graph records and plan set live.
 * Unbind before the native HBA teardown releases those records. */
bool r1_goodix_hba_graph_callbacks_bind(
    r1_goodix_hba_plan_set *set,
    goodix_primitives_elapsed_state *elapsed);
void r1_goodix_hba_graph_callbacks_unbind(void);
extern const goodix_primitives_indexed_operation_fn
    r1_goodix_hba_graph_operations[GOODIX_PRIMITIVES_STATE_COUNT];

#endif
