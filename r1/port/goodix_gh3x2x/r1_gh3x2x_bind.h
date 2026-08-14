#ifndef R1_GH3X2X_BIND_H
#define R1_GH3X2X_BIND_H

/*
 * openR1 binding between the clean-room r1_goodix provider seam and the
 * Goodix GH3X2X democode kernel (Gh3x2xDemoInit / Gh3x2xDemoStartSampling /
 * Gh3x2xDemoStopSampling / Gh3x2xDemoArrayCfgSwitch).
 *
 * Compiled only where the pinned vendor tree is available (host
 * vendor-goodix-test and the Nordic SDK image); the implementation
 * includes vendor headers so the entry-point prototypes are checked.
 */

#include <stdint.h>

#include "openr1/r1_goodix.h"

/* Provider ops table with a NULL context; bind it to an r1_goodix_adapter
 * together with the board ops for the target platform. */
const r1_goodix_provider_ops *r1_gh3x2x_bind_provider_ops(void);

/* Individually callable operations (same behavior as the ops table). */
int32_t r1_gh3x2x_bind_initialize(void *context);
int32_t r1_gh3x2x_bind_switch_configuration(void *context,
                                            uint8_t configuration);
int32_t r1_gh3x2x_bind_start_sampling(void *context, uint32_t mask);
int32_t r1_gh3x2x_bind_stop_sampling(void *context, uint32_t mask);

#endif
