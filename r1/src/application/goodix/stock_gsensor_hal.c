/* Typed SDK entry for the checked stock 6f920 consumer. */
#include "kernel/gh_demo_config.h"
#include "gh_demo_inner.h"
#include "stock_gsensor_callbacks.h"
#include <stddef.h>
_Static_assert(sizeof(STGsensorRawdata) == 6, "native three-axis sample");
_Static_assert(offsetof(STGsensorRawdata, sXAxisVal) == 0 &&
               offsetof(STGsensorRawdata, sYAxisVal) == 2 &&
               offsetof(STGsensorRawdata, sZAxisVal) == 4,
               "native signed halfword axis offsets");
_Static_assert(sizeof(GS16) == 2 && (GS16)-1 < 0 && sizeof(GU16) == 2,
               "native axis and count words");
void hal_gsensor_drv_get_fifo_data(STGsensorRawdata samples[], GU16 *count)
{
    return r1_goodix_gsensor_sample((int16_t *)samples,
                                                            count);
}
