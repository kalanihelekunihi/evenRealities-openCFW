#include "native_hba_calc.h"
#include "native_hba_graph_callbacks.h"
#include "native_hba_public_view.h"
#include "native_hba_quantized_runtime.h"
#include "native_processing_teardown.h"

extern float r1_native_expf(float);
extern float r1_native_log10f(float);
extern float r1_native_sqrtf(float);

static goodix_primitives_hr_context_owner owner;
static goodix_primitives_hba_runtime runtime;
static r1_goodix_hba_plan_set plans;
static quantized_runtime quantized;
static goodix_primitives_elapsed_state elapsed;
static goodix_primitives_float_span mode_buffers[3];
static bool bound;

static int32_t integrity(int32_t value)
{
    return (int32_t)goodix_primitives_integrity_encode((uint32_t)value);
}

void r1_goodix_hba_calculation_unbind(void)
{
    r1_goodix_hba_graph_callbacks_unbind();
    if (runtime.bound) (void)goodix_primitives_hba_runtime_unbind(&runtime);
    plans=(r1_goodix_hba_plan_set){0};
    owner=(goodix_primitives_hr_context_owner){0};
    elapsed=(goodix_primitives_elapsed_state){0};
    bound=false;
}

static bool bind(void)
{
    if (bound) return true;
    if (!r1_goodix_native_hba_context_owner_view(&owner)) return false;
    const goodix_primitives_hr_primary_context *const primary=owner.primary;
    r1_goodix_hba_quantized_runtime_initialize(&quantized);
    if (!r1_goodix_hba_plan_set_bind_source(
            (const void *)primary->graph_selector_0,
            (const void *)primary->graph_selector_1,
            (const void *)primary->graph_selector_6,
            &quantized,&plans) ||
            !r1_goodix_hba_elapsed_bind(&plans,&elapsed) ||
            !r1_goodix_hba_mode_buffers_bind(&plans,mode_buffers)) {
        r1_goodix_hba_calculation_unbind();
        return false;
    }
    const goodix_primitives_hba_runtime_bindings bindings={
        .integrity_transform=integrity,
        .quantized=&quantized,
        .operations=r1_goodix_hba_graph_operations,
        .elapsed_state=&elapsed,
        .mode_buffers=mode_buffers,
        .exponential=r1_native_expf,
        .logarithm_base_10=r1_native_log10f,
        .square_root=r1_native_sqrtf,
    };
    if (!goodix_primitives_hba_runtime_bind(&owner,&bindings,&runtime) ||
            !r1_goodix_hba_graph_callbacks_bind(&plans,&elapsed)) {
        r1_goodix_hba_calculation_unbind();
        return false;
    }
    bound=true;
    return true;
}

goodix_hba_ret goodix_hba_calc(goodix_hba_input_rawdata *raw,
    goodix_hba_result *result)
{
    goodix_primitives_hba_process_input input;
    if (result==NULL || !r1_goodix_hba_public_input_view(raw,&input) ||
            !bind()) return (goodix_hba_ret)1;
    goodix_primitives_hba_process_output output;
    r1_goodix_hba_public_result_load(result,&output);
    const uint32_t status=goodix_primitives_hba_runtime_process(
        &runtime,&input,&output);
    r1_goodix_hba_public_result_store(&output,result);
    return (goodix_hba_ret)status;
}
