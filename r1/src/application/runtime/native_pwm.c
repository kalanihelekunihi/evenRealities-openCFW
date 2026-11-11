/* Stock PWM0/1/2 configuration. Keep the pinned Nordic C implementation
 * unchanged and scope recovered configuration to this translation unit.
 * Layout, IRQ behavior and remaining gates: pwm-c-review.md. */
#include <nrfx.h>
#undef NRFX_PWM_ENABLED
#define NRFX_PWM_ENABLED 1
#undef NRFX_PWM0_ENABLED
#define NRFX_PWM0_ENABLED 1
#undef NRFX_PWM1_ENABLED
#define NRFX_PWM1_ENABLED 1
#undef NRFX_PWM2_ENABLED
#define NRFX_PWM2_ENABLED 1
#undef NRFX_PWM3_ENABLED
#define NRFX_PWM3_ENABLED 0
#undef NRFX_PWM_NRF52_ANOMALY_109_WORKAROUND_ENABLED
#define NRFX_PWM_NRF52_ANOMALY_109_WORKAROUND_ENABLED 0
#undef NRFX_PWM_CONFIG_LOG_ENABLED
#define NRFX_PWM_CONFIG_LOG_ENABLED 0
#include "nrfx_pwm.c"
