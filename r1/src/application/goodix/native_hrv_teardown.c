#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include "goodix_hrv.h"
#include "native_hrv_calc.h"
#include "gh3x2x_demo_algo_call.h"
/* Canonical native HRV context cell. Initialization must share this owner. */
void *volatile r1_goodix_native_hrv_context
    __attribute__((section(".r1.goodix.native.hrv.context"),aligned(4)));
uint32_t r1_goodix_native_release_cell(volatile uint32_t *cell)
{
    uint32_t allocation=*cell;
    if (allocation) {
        goodix_mem_free((void *)(uintptr_t)allocation);
        *cell=0;
    }
    return 0;
}
goodix_hrv_ret goodix_hrv_deinit(void)
{
    r1_goodix_hrv_calculation_unbind();
    static const uint8_t offsets[]={0x94,0xa8,0xb8,0xc8,0x1c,0x2c,0x3c,0x4c,0x5c,0x74,0x84};
    /* Stock assumes a valid initial context and reloads the owner before
     * every release. Do not replace this with an early null return. */
    for (uint32_t i=0;i<sizeof(offsets);i++)
        (void)r1_goodix_native_release_cell((volatile uint32_t *)
            ((uintptr_t)r1_goodix_native_hrv_context+offsets[i]));
    uintptr_t context=(uintptr_t)r1_goodix_native_hrv_context;
    goodix_mem_free((void *)(uintptr_t)*(const volatile uint32_t *)(context+0x6c));
    context=(uintptr_t)r1_goodix_native_hrv_context;
    goodix_mem_free((void *)(uintptr_t)*(const volatile uint32_t *)(context+0x70));
    void *last=r1_goodix_native_hrv_context;
    if (last) {
        goodix_mem_free(last);
        r1_goodix_native_hrv_context=0;
        return GX_HRV_ALGO_OK;
    }
    return GX_HRV_ALGO_DEINIT_ABORT;
}
extern __typeof__(goodix_hrv_deinit) goodix_hrv_deinit_func
    __attribute__((alias("goodix_hrv_deinit")));
GS8 GH3x2xHrvAlgoDeinit(const STGh3x2xFrameInfo *const frame)
{
    (void)frame;
    return goodix_hrv_deinit()==GX_HRV_ALGO_OK ? 0 : -1;
}
