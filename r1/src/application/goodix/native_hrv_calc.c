#include <stddef.h>
#include <stdint.h>
#include "goodix_hrv.h"
#include "native_hrv_calc.h"
#include "../../vendor/goodix_primitives/goodix_primitives.h"

extern void *volatile r1_goodix_native_hrv_context;
extern float r1_native_sqrtf(float);

static goodix_primitives_hrv_context context;
static goodix_primitives_hrv_runtime runtime;
static bool bound;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(goodix_primitives_hrv_work_a)==48u,
    "native HRV extrema allocation");
_Static_assert(sizeof(goodix_primitives_hrv_work_b)==696u,
    "native HRV decision allocation");
#endif

static uint32_t word(const uint8_t *base,size_t offset)
{
    return *(const volatile uint32_t *)(const void *)(base+offset);
}

static float number(const uint8_t *base,size_t offset)
{
    return *(const volatile float *)(const void *)(base+offset);
}

static void put_word(uint8_t *base,size_t offset,uint32_t value)
{
    *(volatile uint32_t *)(void *)(base+offset)=value;
}

void r1_goodix_hrv_calculation_unbind(void)
{
    runtime=(goodix_primitives_hrv_runtime){0};
    context=(goodix_primitives_hrv_context){0};
    bound=false;
}

static bool bind(void)
{
    if (bound) return true;
    const uint8_t *const native=r1_goodix_native_hrv_context;
    if (native==NULL) return false;
    context=(goodix_primitives_hrv_context){0};
    context.identity=word(native,0u);
    context.sample_count=word(native,8u);
    context.mode=word(native,0x14u);
    context.divisor=word(native,0x18u);
    context.window_a=word(native,0x124u);
    context.window_b=word(native,0x128u);
    context.group_count=word(native,0x12cu);
    context.scaled_sample_bytes=word(native,0x104u);
    context.sample_count_copy=word(native,0x108u);
    context.process_count=word(native,4u);
    context.window_index=word(native,0x130u);
    context.calibration_e8=number(native,0xe8u);
    context.calibration_ec=number(native,0xecu);
    context.calibration_f0=number(native,0xf0u);
    context.calibration_f4=number(native,0xf4u);
    static const uint8_t offsets[GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT]={
        0x94u,0xa8u,0xb8u,0xc8u,0x1cu,0x2cu,0x3cu,
        0x4cu,0x5cu,0x74u,0x84u};
    for (size_t i=0;i<GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT;i++) {
        context.subobjects[i]=(void *)(uintptr_t)word(native,offsets[i]);
        context.subobject_capacities[i]=word(native,offsets[i]+8u);
    }
    context.owned_6c=(goodix_primitives_hrv_work_a *)(uintptr_t)
        word(native,0x6cu);
    context.owned_70=(goodix_primitives_hrv_work_b *)(uintptr_t)
        word(native,0x70u);
    if (!goodix_primitives_hrv_runtime_bind(
            &context,r1_native_sqrtf,&runtime)) {
        r1_goodix_hrv_calculation_unbind();
        return false;
    }
    bound=true;
    return true;
}

goodix_hrv_ret goodix_hrv_calc(goodix_hrv_input_rawdata *raw,
    goodix_hrv_result *result)
{
    if (raw==NULL || result==NULL || raw->ppg_rawdata==NULL ||
            raw->enable_flg==NULL || raw->pst_module_unique==NULL ||
            !bind()) return GX_HRV_ALGO_NULL_PTR;
    const goodix_primitives_hrv_process_input input={
        .channel_values=raw->ppg_rawdata,
        .channel_value_count=(size_t)raw->total_ch_num*3u,
        .presence_bytes=raw->enable_flg,
        .presence_byte_count=((size_t)raw->total_ch_num*3u+7u)/8u,
        .gain_codes=raw->ch_agc_gain,
        .gain_code_count=(size_t)raw->total_ch_num*3u,
        .drive_currents=raw->ch_agc_drv,
        .drive_current_count=(size_t)raw->total_ch_num*3u,
        .channel_count=raw->total_ch_num,
        .last_hr=*(const uint8_t *)raw->pst_module_unique,
        .axis_x=raw->acc_x,.axis_y=raw->acc_y,.axis_z=raw->acc_z,
    };
    int32_t output[6]={0};
    if (!goodix_primitives_hrv_runtime_process(&runtime,&input,output))
        return GX_HRV_ALGO_FAILED;
    uint8_t *const native=r1_goodix_native_hrv_context;
    put_word(native,4u,context.process_count);
    put_word(native,0x130u,context.window_index);
    if (context.process_count/context.sample_count<=5u ||
            context.process_count%context.sample_count!=0u)
        return GX_HRV_ALGO_OK;
    for (size_t i=0;i<4u;i++) result->rri[i]=output[i];
    result->rri_confidence=output[4];
    result->rri_valid_num=output[5];
    return GX_HRV_ALGO_UPDATE;
}
