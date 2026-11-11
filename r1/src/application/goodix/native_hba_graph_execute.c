#include "native_hba_graph_execute.h"
#include <stdint.h>
#include <string.h>

#define HBA_GRAPH_ARENA_BYTES 7740u

static bool overlaps(const void *first,size_t first_size,
    const void *second,size_t second_size)
{
    const uintptr_t a=(uintptr_t)first,b=(uintptr_t)second;
    if (first_size==0u || second_size==0u) return false;
    if (a<=b) return b-a<first_size;
    return a-b<second_size;
}

bool r1_goodix_hba_mode01_execute(
    const r1_goodix_hba_plan_set *set,uint32_t mode,
    const goodix_primitives_graph_executor_input *input,
    float *output,void *scratch,size_t scratch_capacity)
{
    if (set==NULL || !set->bound || mode>1u || input==NULL ||
            input->workspace==NULL || input->tail_input==NULL ||
            input->workspace_count>SIZE_MAX/sizeof(float) ||
            input->tail_input_count>SIZE_MAX/sizeof(uint32_t) ||
            input->tail_input_count<4u || output==NULL) return false;
    uint8_t *arena=(uint8_t *)input->workspace;
    size_t arena_bytes=input->workspace_count*sizeof(float);
    if (mode==1u) {
        if (scratch==NULL || scratch_capacity<HBA_GRAPH_ARENA_BYTES ||
                arena_bytes>HBA_GRAPH_ARENA_BYTES ||
                overlaps(input->workspace,arena_bytes,scratch,
                    HBA_GRAPH_ARENA_BYTES) ||
                overlaps(input->tail_input,input->tail_input_count*
                    sizeof(uint32_t),scratch,HBA_GRAPH_ARENA_BYTES) ||
                overlaps(output,sizeof(*output),scratch,
                    HBA_GRAPH_ARENA_BYTES)) return false;
        memset(scratch,0,HBA_GRAPH_ARENA_BYTES);
        memcpy(scratch,input->workspace,arena_bytes);
        arena=scratch;
        arena_bytes=HBA_GRAPH_ARENA_BYTES;
    }
    const quantized_runtime_goodix_executor_io io={
        .workspace=arena,
        .workspace_size=arena_bytes,
        .tail_input=input->tail_input,
        .tail_input_size=input->tail_input_count*sizeof(uint32_t),
        .output=(uint8_t *)output,
        .output_capacity=sizeof(*output),
    };
    size_t written=0u;
    return quantized_runtime_goodix_executor_execute(
        &set->plans[mode],&io,&written) && written==sizeof(*output);
}

bool r1_goodix_hba_mode6_execute(
    const r1_goodix_hba_plan_set *set,float *workspace,
    size_t workspace_count,void *temporary,size_t temporary_capacity)
{
    if (set==NULL || !set->bound || workspace==NULL || temporary==NULL ||
            workspace_count>SIZE_MAX/sizeof(float) ||
            workspace_count*sizeof(float)<
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_WORKSPACE_BYTES ||
            temporary_capacity<
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_TEMPORARY_BYTES ||
            overlaps(workspace,workspace_count*sizeof(float),temporary,
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_TEMPORARY_BYTES))
        return false;
    const quantized_runtime_goodix_second_executor_io io={
        .workspace=(uint8_t *)workspace,
        .workspace_size=workspace_count*sizeof(float),
        .temporary=temporary,
        .temporary_size=temporary_capacity,
        .output=(uint8_t *)workspace,
        .output_capacity=workspace_count*sizeof(float),
    };
    size_t written=0u;
    return quantized_runtime_goodix_second_executor_execute(
        &set->mode6_plan,&io,&written) && written==
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES;
}
