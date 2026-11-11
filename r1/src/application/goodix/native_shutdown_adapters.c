#include <stdint.h>
#include "gh3x2x_demo_algo_call.h"
#include "goodix_spo2.h"
#include "native_processing_teardown.h"
GS8 GH3x2xHrAlgoDeinit(const STGh3x2xFrameInfo *const frame)
{
    (void)frame;
    return r1_goodix_native_processing_destroy()==0 ? 0 : -1;
}
GS8 GH3x2xSpo2AlgoDeinit(const STGh3x2xFrameInfo *const frame)
{
    (void)frame;
    return goodix_spo2_deinit()==GX_ALGO_SPO2_SUCCESS ? 0 : -1;
}
