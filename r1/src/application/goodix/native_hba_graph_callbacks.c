#include "native_hba_graph_callbacks.h"
#include <stdint.h>
#include "goodix_mem.h"

static r1_goodix_hba_plan_set *bound_set;
static goodix_primitives_elapsed_state *bound_elapsed;

bool r1_goodix_hba_graph_callbacks_bind(
    r1_goodix_hba_plan_set *set,goodix_primitives_elapsed_state *elapsed)
{
    bound_set=NULL;
    bound_elapsed=NULL;
    if (set==NULL || !set->bound || elapsed==NULL) return false;
    bound_set=set;
    bound_elapsed=elapsed;
    return true;
}

void r1_goodix_hba_graph_callbacks_unbind(void)
{
    bound_set=NULL;
    bound_elapsed=NULL;
}

static int32_t mode01(void *record,uintptr_t first,uintptr_t second,
    uintptr_t third,uintptr_t fourth,uintptr_t fifth)
{
    (void)first;(void)third;(void)fifth;
    r1_goodix_hba_plan_set *const set=bound_set;
    if (set==NULL || !set->bound || record==NULL || second==0u ||
            fourth==0u) return 1;
    const uint32_t mode=*(const uint32_t *)record;
    if (mode>1u || record!=set->views[mode].graph.bytes) return 1;
    if (mode==0u && !r1_goodix_hba_elapsed_commit(
            set,bound_elapsed)) return 1;
    const goodix_primitives_graph_executor_input *const input=
        (const goodix_primitives_graph_executor_input *)second;
    float *const output=*(float *const *)fourth;
    void *scratch=NULL;
    if (mode==1u) {
        scratch=goodix_mem_malloc(7740);
        if (scratch==NULL) return 1;
    }
    const bool success=r1_goodix_hba_mode01_execute(
        set,mode,input,output,scratch,mode==1u?7740u:0u);
    if (scratch!=NULL) goodix_mem_free(scratch);
    return success?0:1;
}

static int32_t mode6(void *record,uintptr_t first,uintptr_t second,
    uintptr_t third,uintptr_t fourth,uintptr_t fifth)
{
    (void)first;(void)third;(void)fifth;
    const r1_goodix_hba_plan_set *const set=bound_set;
    if (set==NULL || !set->bound || record==NULL ||
            record!=set->mode6_view.bytes || second==0u ||
            fourth!=second) return 1;
    void *const temporary=goodix_mem_malloc(4320);
    if (temporary==NULL) return 1;
    const bool success=r1_goodix_hba_mode6_execute(
        set,(float *)second,GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES,
        temporary,4320u);
    goodix_mem_free(temporary);
    return success?0:1;
}

const goodix_primitives_indexed_operation_fn
r1_goodix_hba_graph_operations[GOODIX_PRIMITIVES_STATE_COUNT]={
    mode01,mode01,NULL,NULL,NULL,NULL,mode6
};
