/*
 * openR1 binding between the r1_goodix provider seam and the Goodix GH3X2X
 * democode kernel.  Error mapping: the r1_goodix adapter contract is
 * 0 == success / nonzero == failure; the democode kernel uses
 * GH3X2X_RET_OK (0) with negative error codes, which maps directly.
 * Gh3x2xDemoStartSampling / Gh3x2xDemoStopSampling return void upstream;
 * driver-level failures (bus errors, chip mismatch) already surface
 * through Gh3x2xDemoInit / GH3X2X_CommunicateConfirm, so the start/stop
 * wrappers report success once the kernel accepted the request.
 */

#include "r1_gh3x2x_bind.h"

#include "gh_demo.h"

int32_t r1_gh3x2x_bind_initialize(void *context) {
    UNUSED_VAR(context);
    return Gh3x2xDemoInit();
}

int32_t r1_gh3x2x_bind_switch_configuration(void *context,
                                            uint8_t configuration) {
    UNUSED_VAR(context);
    return Gh3x2xDemoArrayCfgSwitch(configuration);
}

int32_t r1_gh3x2x_bind_start_sampling(void *context, uint32_t mask) {
    UNUSED_VAR(context);
    Gh3x2xDemoStartSampling(mask);
    return 0;
}

int32_t r1_gh3x2x_bind_stop_sampling(void *context, uint32_t mask) {
    UNUSED_VAR(context);
    Gh3x2xDemoStopSampling(mask);
    return 0;
}

const r1_goodix_provider_ops *r1_gh3x2x_bind_provider_ops(void) {
    static const r1_goodix_provider_ops ops = {
        .initialize = r1_gh3x2x_bind_initialize,
        .switch_configuration = r1_gh3x2x_bind_switch_configuration,
        .start_sampling = r1_gh3x2x_bind_start_sampling,
        .stop_sampling = r1_gh3x2x_bind_stop_sampling,
    };
    return &ops;
}
