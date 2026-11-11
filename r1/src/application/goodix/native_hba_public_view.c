#include "native_hba_public_view.h"
#include <stddef.h>

_Static_assert(offsetof(goodix_hba_input_unique,scence)==0,
    "stock HBA selector is the first unique-input byte");
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(goodix_hba_input_rawdata)==56,
    "stock HBA public input geometry");
_Static_assert(sizeof(goodix_hba_result)==40,
    "stock HBA public result geometry");
_Static_assert(offsetof(goodix_hba_input_rawdata,data_type)==0x33,
    "stock HBA stream mode byte");
_Static_assert(offsetof(goodix_hba_input_rawdata,pst_module_unique)==0x34,
    "stock HBA module selector pointer");
#endif

bool r1_goodix_hba_public_input_view(
    const goodix_hba_input_rawdata *raw,
    goodix_primitives_hba_process_input *view)
{
    if (raw==NULL || view==NULL || raw->ppg_rawdata==NULL ||
            raw->enable_flg==NULL || raw->pst_module_unique==NULL) return false;
    const size_t channels=raw->total_ch_num;
    const size_t samples=channels*3u;
    const goodix_hba_input_unique *const unique=raw->pst_module_unique;
    *view=(goodix_primitives_hba_process_input){
        .channel_values=raw->ppg_rawdata,
        .channel_value_count=samples,
        .enable_flags=raw->enable_flg,
        .enable_flag_count=(samples+7u)/8u,
        .gain_codes=raw->ch_agc_gain,
        .gain_code_count=samples,
        .drive_currents=raw->ch_agc_drv,
        .drive_current_count=samples,
        .channel_count=raw->total_ch_num,
        .accelerometer={raw->acc_x,raw->acc_y,raw->acc_z},
        .mode=raw->data_type,
        .filter_code=&unique->scence,
        .filter_code_count=1u,
    };
    return true;
}

void r1_goodix_hba_public_result_load(
    const goodix_hba_result *result,
    goodix_primitives_hba_process_output *output)
{
    *output=(goodix_primitives_hba_process_output){
        .valid=result->hba_out_flag,
        .selected=result->hba_out,
        .score_at_least_70=result->valid_level,
        .scaled_score=result->valid_score,
    };
}

void r1_goodix_hba_public_result_store(
    const goodix_primitives_hba_process_output *output,
    goodix_hba_result *result)
{
    result->hba_out_flag=output->valid;
    result->hba_out=output->selected;
    result->valid_level=output->score_at_least_70;
    result->valid_score=output->scaled_score;
}
