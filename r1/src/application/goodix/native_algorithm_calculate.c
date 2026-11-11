#include <stdint.h>
#include "native_algorithm_state.h"
#include "gh3x2x_demo_algorithm_calc.h"
extern GS8 GH3x2xAdtAlgoExe(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xHrAlgoExe(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xHrvAlgoExe(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xSpo2AlgoExe(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xSoftAdtAlgoExe(const STGh3x2xFrameInfo *const);
static uint32_t frame_word(const STGh3x2xFrameInfo *frame,uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)frame+offset);
}
/* Stock0x29e8c. The native result is reset by every unselected slot, even
 * after an earlier executor error. Unsupported selected slots do not reset it.
 * Engine bodies remain explicit providers; this is the shared frame policy. */
GS8 GH3X2X_AlgoCalculate(GU32 functions)
{
    typedef GS8 (*calculate_fn)(const STGh3x2xFrameInfo *const);
    static const calculate_fn calculate[20]={
        [0]=GH3x2xAdtAlgoExe,[1]=GH3x2xHrAlgoExe,[2]=GH3x2xHrvAlgoExe,
        [6]=GH3x2xSpo2AlgoExe,[9]=GH3x2xSoftAdtAlgoExe,[15]=GH3x2xSoftAdtAlgoExe
    };
    if (!r1_goodix_algorithm_started) return 0;
    GS8 result=-1;
    for (uint32_t i=0;i<20;++i) {
        if (!(functions&(UINT32_C(1)<<i))) { result=0; continue; }
        if (functions&~r1_goodix_algorithm_started) continue;
        uintptr_t frames=(uintptr_t)r1_goodix_algorithm_frame_table;
        const STGh3x2xFrameInfo *frame=*(const STGh3x2xFrameInfo *const volatile *)
            (frames+i*sizeof(void *));
        if (GH3x2xSleepFlagGet()) {
            volatile uint32_t *flags=(volatile uint32_t *)(uintptr_t)frame_word(frame,0x28);
            flags[2]|=8u;
        }
        if (!r1_goodix_algorithm_initialized[i] || !calculate[i]) continue;
        result=calculate[i](frame);
        if (!*(const volatile uint32_t *)(uintptr_t)frame_word(frame,0x38) &&
                !*(const volatile uint8_t *)(uintptr_t)frame_word(frame,0x3c)) {
            GH3X2X_Memset((void *)(uintptr_t)frame_word(frame,0x3c),0,68);
            *(volatile uint8_t *)(uintptr_t)frame_word(frame,0x3c)=1;
            *(volatile uint16_t *)((uintptr_t)frame_word(frame,0x3c)+2)=255;
            uint8_t count=GH3x2x_BitCount(255);
            *(volatile uint8_t *)((uintptr_t)frame_word(frame,0x3c)+1)=count;
        }
        uintptr_t output=frame_word(frame,0x3c);
        if (*(const volatile uint8_t *)output==1)
            GH3X2X_Memcpy((void *)(uintptr_t)frame_word(frame,0x40),(const void *)output,68);
    }
    return result;
}
