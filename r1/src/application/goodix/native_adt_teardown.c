#include <stdint.h>
#include "gh3x2x_demo_algo_call.h"
#include "goodix_nadt.h"
#include "native_nadt_state.h"
volatile uint8_t r1_goodix_native_adt_flags[3]
    __attribute__((section(".r1.goodix.native.adt.flags"),aligned(1)));
volatile uint32_t r1_goodix_native_soft_adt_timeout
    __attribute__((section(".r1.goodix.native.soft_adt.timeout"),aligned(4)));
GS8 GH3x2xAdtAlgoDeinit(const STGh3x2xFrameInfo *const frame)
{
    (void)frame;
    r1_goodix_native_adt_flags[2]=0;
    r1_goodix_native_adt_flags[0]=0;
    return 0;
}
GS8 GH3x2xSoftAdtAlgoDeinit(const STGh3x2xFrameInfo *const frame)
{
    (void)frame;
    goodix_nadt_ret status=goodix_nadt_deinit();
    r1_goodix_native_soft_adt_timeout=0;
    return status==GX_ALGO_NADT_SUCCESS ? 0 : -1;
}
