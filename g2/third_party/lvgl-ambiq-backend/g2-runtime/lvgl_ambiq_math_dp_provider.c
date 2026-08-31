/* SPDX-License-Identifier: MIT */
/* Public exact-symbol wrappers around the pinned musl FPv5-D16 closure. */

#include "lvgl_ambiq_math_dp_provider.h"

#define OPEN_CFW_PUBLIC __attribute__((visibility("default"), used, noinline))
#define OPEN_CFW_HIDDEN __attribute__((visibility("hidden")))

extern OPEN_CFW_HIDDEN float open_cfw_musl_cosf(float);
extern OPEN_CFW_HIDDEN float open_cfw_musl_sinf(float);
extern OPEN_CFW_HIDDEN double open_cfw_musl_sqrt(double);
extern OPEN_CFW_HIDDEN float open_cfw_musl_tanf(float);

OPEN_CFW_PUBLIC float cosf(float value) { return open_cfw_musl_cosf(value); }
OPEN_CFW_PUBLIC float sinf(float value) { return open_cfw_musl_sinf(value); }
OPEN_CFW_PUBLIC double sqrt(double value) { return open_cfw_musl_sqrt(value); }
OPEN_CFW_PUBLIC float tanf(float value) { return open_cfw_musl_tanf(value); }
