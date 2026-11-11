#include "native_hba_graph_view.h"
#include <stddef.h>

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(quantized_runtime_recurrent_descriptor)==24,
    "target recurrent record is six words");
_Static_assert(offsetof(quantized_runtime_recurrent_descriptor,state)==4,
    "target recurrent state pointer offset");
#endif

static uint32_t word(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1]<<8) |
           ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
}

bool r1_goodix_hba_graph_view_bind(
    const void *record, const quantized_runtime *runtime,
    r1_goodix_hba_graph_view *view)
{
    if (record==NULL || runtime==NULL || view==NULL) return false;
    const uint8_t *const bytes=record;
    const uint32_t mode=word(bytes);
    if (mode>1u) return false;
    static const uint16_t offsets[3]={0x1bcu,0x1d8u,0x1f0u};
    for (size_t i=0;i<3u;i++) {
        const uint8_t *const p=bytes+offsets[i];
        view->recurrent[i]=(quantized_runtime_recurrent_descriptor){
            .units=word(p),
            .state=(float *)(uintptr_t)word(p+4),
            .input_weights_offset=word(p+8),
            .recurrent_weights_offset=word(p+12),
            .bias_offset=word(p+16),
            .execute=(uintptr_t)word(p+20),
        };
    }
    view->graph=(quantized_runtime_gomore_executor_graph_view){
        .bytes=bytes,
        .byte_count=mode==0u
            ? QUANTIZED_RUNTIME_GOMORE_EXECUTOR_GRAPH_MODE0_BYTES
            : QUANTIZED_RUNTIME_GOMORE_EXECUTOR_GRAPH_MODE1_BYTES,
        .mode=mode,
        .recurrent=view->recurrent,
        .runtime=runtime,
        .rewrite=r1_goodix_hba_stage_token_rewrite,
    };
    return true;
}

bool r1_goodix_hba_mode6_graph_view_bind(
    const void *record,
    quantized_runtime_goodix_second_graph_view *view)
{
    if (record==NULL || view==NULL) return false;
    const uint8_t *const bytes=record;
    if (word(bytes)!=6u) return false;
    *view=(quantized_runtime_goodix_second_graph_view){
        .bytes=bytes,
        .byte_count=QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_BYTES,
        .rewrite=r1_goodix_hba_stage_token_rewrite,
    };
    return true;
}

bool r1_goodix_hba_plan_set_bind(
    const void *mode0_record, const void *mode1_record,
    const void *mode6_record, const quantized_runtime *runtime,
    r1_goodix_hba_plan_set *set,
    quantized_runtime_stage_token_resolver_fn resolve,
    void *resolve_context,
    quantized_runtime_multi_stage_token_resolver_fn resolve_multi,
    void *resolve_multi_context)
{
    if (set==NULL) return false;
    *set=(r1_goodix_hba_plan_set){0};
    if (runtime==NULL || mode0_record==NULL ||
            mode1_record==NULL || mode6_record==NULL ||
            resolve==NULL || resolve_multi==NULL) return false;
    if (!r1_goodix_hba_graph_view_bind(mode0_record,runtime,&set->views[0]) ||
            set->views[0].graph.mode!=0u ||
            !r1_goodix_hba_graph_view_bind(mode1_record,runtime,&set->views[1]) ||
            set->views[1].graph.mode!=1u ||
            !r1_goodix_hba_mode6_graph_view_bind(
                mode6_record,&set->mode6_view) ||
            !quantized_runtime_gomore_executor_plan_build_view(
                &set->views[0].graph,&set->plans[0],
                resolve,resolve_context) ||
            !quantized_runtime_gomore_executor_plan_build_view(
                &set->views[1].graph,&set->plans[1],
                resolve,resolve_context) ||
            !quantized_runtime_goodix_second_executor_plan_build_view(
                runtime,&set->mode6_view,&set->mode6_plan,
                resolve,resolve_context,resolve_multi,
                resolve_multi_context)) {
        *set=(r1_goodix_hba_plan_set){0};
        return false;
    }
    set->bound=true;
    return true;
}

bool r1_goodix_hba_plan_set_bind_source(
    const void *mode0_record, const void *mode1_record,
    const void *mode6_record, const quantized_runtime *runtime,
    r1_goodix_hba_plan_set *set)
{
    return r1_goodix_hba_plan_set_bind(
        mode0_record,mode1_record,mode6_record,runtime,set,
        quantized_runtime_source_stage_token_resolve,NULL,
        quantized_runtime_source_multi_stage_token_resolve,NULL);
}

static void put_word(uint8_t *p,uint32_t value)
{
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}

bool r1_goodix_hba_elapsed_bind(
    const r1_goodix_hba_plan_set *set,
    goodix_primitives_elapsed_state *state)
{
    if (set==NULL || !set->bound || state==NULL ||
            set->views[0].graph.bytes==NULL) return false;
    const uint8_t *const record=set->views[0].graph.bytes;
    if (word(record)!=0u ||
            ((uintptr_t)(record+0x238u)&(sizeof(uint32_t)-1u))!=0u)
        return false;
    *state=(goodix_primitives_elapsed_state){
        .baseline=word(record+0x1e0u),
        .elapsed_a=word(record+0x1e4u),
        .elapsed_b=word(record+0x1e8u),
        .slot_timestamps=(const uint32_t *)(const void *)(record+0x238u),
        .slot_count=6u,
    };
    return true;
}

bool r1_goodix_hba_elapsed_commit(
    r1_goodix_hba_plan_set *set,
    const goodix_primitives_elapsed_state *state)
{
    if (set==NULL || !set->bound || state==NULL ||
            set->views[0].graph.bytes==NULL ||
            state->slot_timestamps!=(const uint32_t *)(const void *)(
                set->views[0].graph.bytes+0x238u) ||
            state->slot_count!=6u) return false;
    uint8_t *const record=(uint8_t *)(uintptr_t)set->views[0].graph.bytes;
    put_word(record+0x1e0u,state->baseline);
    put_word(record+0x1e4u,state->elapsed_a);
    put_word(record+0x1e8u,state->elapsed_b);
    quantized_runtime_recurrent_descriptor *const recurrent=
        &set->views[0].recurrent[1];
    recurrent->input_weights_offset=state->baseline;
    recurrent->recurrent_weights_offset=state->elapsed_a;
    recurrent->bias_offset=state->elapsed_b;
    return true;
}

bool r1_goodix_hba_mode_buffers_bind(
    const r1_goodix_hba_plan_set *set,
    goodix_primitives_float_span buffers[3])
{
    if (set==NULL || !set->bound || buffers==NULL ||
            set->views[0].graph.bytes==NULL ||
            word(set->views[0].graph.bytes)!=0u) return false;
    for (size_t i=0;i<3u;i++) {
        const quantized_runtime_recurrent_descriptor *const recurrent=
            &set->views[0].recurrent[i];
        if (recurrent->units!=0u && recurrent->state==NULL) return false;
        buffers[i]=(goodix_primitives_float_span){
            .values=recurrent->state,.count=recurrent->units};
    }
    return true;
}
