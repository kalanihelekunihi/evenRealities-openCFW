/* Native nrfx clock has calibration-state storage and no assertion branches. */
#include "sdk_common.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#include "nrfx.h"
#undef NRFX_CLOCK_CONFIG_LF_SRC
#define NRFX_CLOCK_CONFIG_LF_SRC 0
#undef NRFX_CLOCK_CONFIG_LF_CAL_ENABLED
#define NRFX_CLOCK_CONFIG_LF_CAL_ENABLED 1
_Static_assert(NRFX_CLOCK_CONFIG_LF_SRC==0,"native LF RC source");
_Static_assert(NRFX_CLOCK_CONFIG_IRQ_PRIORITY==6,"native CLOCK priority");
_Static_assert(NRFX_POWER_ENABLED==0,"native no shared power IRQ flag");
