#include "native_hba_quantized_runtime.h"
#include <stdint.h>

extern float r1_native_fminf(float,float);
extern float r1_native_fmaxf(float,float);
extern float r1_native_floorf(float);
extern float r1_native_expf(float);
extern void r1_native_qsort(uint8_t *,uint32_t,uint32_t,
    int (*)(const void *,const void *));

static void hba_sort(void *base,size_t count,size_t width,
    quantized_runtime_compare_fn compare)
{
    /* Quantized arena compaction sorts at most twelve live descriptors.
     * Keep the adapter checked on wider host builds as well. */
    if (base==NULL || compare==NULL || count>UINT32_MAX ||
            width>UINT32_MAX) return;
    r1_native_qsort(base,(uint32_t)count,(uint32_t)width,compare);
}

void r1_goodix_hba_quantized_runtime_initialize(quantized_runtime *runtime)
{
    const quantized_runtime_providers providers={
        .fminf_fn=r1_native_fminf,
        .fmaxf_fn=r1_native_fmaxf,
        .floorf_fn=r1_native_floorf,
        .expf_fn=r1_native_expf,
        .qsort_fn=hba_sort,
    };
    quantized_runtime_initialize(runtime,&providers);
}
