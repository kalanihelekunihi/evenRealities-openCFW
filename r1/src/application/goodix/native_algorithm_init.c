#include <stdint.h>
#include "native_algorithm_state.h"
#include "native_nadt_state.h"
/* These algorithm engine initializers remain explicit native boundaries. */
extern int32_t r1_goodix_hr_engine_init(uint32_t);
extern int32_t r1_goodix_hrv_engine_init(uint32_t);
extern int32_t r1_goodix_spo2_engine_init(uint32_t);
extern void r1_goodix_soft_adt_engine_init(const STGh3x2xFrameInfo *);
volatile uint32_t r1_goodix_hrv_initialization_count
    __attribute__((section(".r1.goodix.hrv.initialization.count"),aligned(4)));
volatile uint8_t r1_goodix_soft_adt_initialization_flags[2]
    __attribute__((section(".r1.goodix.soft.adt.initialization.flags"),aligned(1)));
static uint32_t frame_word(const STGh3x2xFrameInfo *frame,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)frame+offset);
}
static void clear_frame_result(const STGh3x2xFrameInfo *frame)
{
    *(volatile uint8_t *)(uintptr_t)frame_word(frame,0x40)=0;
}
static uint32_t sample_rate(const STGh3x2xFrameInfo *frame)
{
    return *(const volatile uint16_t *)(uintptr_t)frame_word(frame,4);
}
GU8 GH3X2X_GetAlgoMemStatus(void)
{
    return r1_goodix_algorithm_memory.initialized;
}
void Gh3x2xOutputValueStrategyInit(GU32 functions)
{
    (void)functions; /* Stock0x2e950 is BX LR: strategy disabled in this build. */
}
GS8 GH3x2xAdtAlgoInit(const STGh3x2xFrameInfo *const frame)
{
    (void)frame;
    r1_goodix_native_adt_flags[2]=0;
    r1_goodix_native_adt_flags[0]=0;
    r1_goodix_native_adt_flags[1]=0;
    return 0;
}
GS8 GH3x2xHrAlgoInit(const STGh3x2xFrameInfo *const frame)
{
    int32_t status=r1_goodix_hr_engine_init(sample_rate(frame));
    clear_frame_result(frame);
    *(volatile uint32_t *)((uintptr_t)frame_word(frame,0x40)+4)=0;
    return status==0 ? 0 : -1;
}
GS8 GH3x2xHrvAlgoInit(const STGh3x2xFrameInfo *const frame)
{
    int32_t status=r1_goodix_hrv_engine_init(sample_rate(frame));
    if (!status) *(volatile uint16_t *)((uintptr_t)frame_word(frame,0x3c)+2)=127;
    uintptr_t frames=(uintptr_t)r1_goodix_algorithm_frame_table;
    const STGh3x2xFrameInfo *hr_frame=*(const STGh3x2xFrameInfo *const volatile *)(frames+4);
    clear_frame_result(hr_frame);
    r1_goodix_hrv_initialization_count=0;
    return status==0 ? 0 : -1;
}
GS8 GH3x2xSpo2AlgoInit(const STGh3x2xFrameInfo *const frame)
{
    return r1_goodix_spo2_engine_init(sample_rate(frame))==0 ? 0 : -1;
}
GS8 GH3x2xSoftAdtAlgoInit(const STGh3x2xFrameInfo *const frame)
{
    if (frame) {
        r1_goodix_soft_adt_initialization_flags[0]=0;
        r1_goodix_soft_adt_initialization_flags[1]=frame_word(frame,0)==0x8000;
        r1_goodix_soft_adt_engine_init(frame);
    }
    return 0;
}
GS8 GH3X2X_AlgoInit(GU32 functions)
{
    typedef GS8 (*init_fn)(const STGh3x2xFrameInfo *const);
    static const init_fn init[20]={
        [0]=GH3x2xAdtAlgoInit,[1]=GH3x2xHrAlgoInit,[2]=GH3x2xHrvAlgoInit,
        [6]=GH3x2xSpo2AlgoInit,[9]=GH3x2xSoftAdtAlgoInit,[15]=GH3x2xSoftAdtAlgoInit
    };
    if (!r1_goodix_algorithm_frame_table) return 0;
    r1_goodix_algorithm_started|=functions;
    if (GH3X2X_GetAlgoMemStatus()!=1) return -1;
    uint8_t result=0;
    for (uint32_t i=0;i<20;++i) {
        if (functions&(UINT32_C(1)<<i)) {
            uintptr_t frames=(uintptr_t)r1_goodix_algorithm_frame_table;
            uint8_t initialized=r1_goodix_algorithm_initialized[i];
            const STGh3x2xFrameInfo *frame=*(const STGh3x2xFrameInfo *const volatile *)(frames+i*sizeof(void *));
            if (initialized!=1) {
                if (init[i]) {
                    result=(uint8_t)init[i](frame);
                    if (!result) r1_goodix_algorithm_initialized[i]=1;
                }
                Gh3x2xOutputValueStrategyInit(functions);
                if (result) break;
            }
        }
    }
    return (GS8)result;
}
