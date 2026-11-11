#include <stdint.h>
#include "native_algorithm_state.h"
extern GS8 GH3x2xAdtAlgoDeinit(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xHrAlgoDeinit(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xHrvAlgoDeinit(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xSpo2AlgoDeinit(const STGh3x2xFrameInfo *const);
extern GS8 GH3x2xSoftAdtAlgoDeinit(const STGh3x2xFrameInfo *const);
volatile uint32_t r1_goodix_algorithm_started
    __attribute__((section(".r1.goodix.algorithm.started"),aligned(4)));
volatile uint8_t r1_goodix_algorithm_initialized[20]
    __attribute__((section(".r1.goodix.algorithm.initialized"),aligned(1)));
GS8 GH3X2X_AlgoDeinit(GU32 functions)
{
    typedef GS8 (*deinit_fn)(const STGh3x2xFrameInfo *const);
    static const deinit_fn deinit[20]={
        [0]=GH3x2xAdtAlgoDeinit,
        [1]=GH3x2xHrAlgoDeinit,
        [2]=GH3x2xHrvAlgoDeinit,
        [6]=GH3x2xSpo2AlgoDeinit,
        [9]=GH3x2xSoftAdtAlgoDeinit,
        [15]=GH3x2xSoftAdtAlgoDeinit
    };
    if (!r1_goodix_algorithm_frame_table) return 0;
    r1_goodix_algorithm_started&=~functions;
    GS8 result=0;
    for (uint32_t i=0;i<20;i++) {
        if (functions&(UINT32_C(1)<<i)) {
            /* Stock reads the live frame before inspecting the init byte. */
            uintptr_t frames=(uintptr_t)r1_goodix_algorithm_frame_table;
            const STGh3x2xFrameInfo *frame=*(const STGh3x2xFrameInfo *const volatile *)
                (frames+i*sizeof(void *));
            if (r1_goodix_algorithm_initialized[i] && deinit[i]) {
                result=deinit[i](frame);
                if (result) break;
                r1_goodix_algorithm_initialized[i]=0;
            }
        }
    }
    return result;
}
