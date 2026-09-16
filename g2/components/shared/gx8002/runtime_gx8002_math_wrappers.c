/* SPDX-License-Identifier: MIT */
/* Recovered backup ABI wrappers: stock forwards directly, without errno logic. */
extern float __ieee754_powf(float, float);
extern float __ieee754_logf(float);
extern float __ieee754_expf(float);
 #ifndef OPEN_CFW_LOG_EXP_ONLY
float open_cfw_gx8002_powf(float x, float y) { return __ieee754_powf(x, y); }
#endif
#ifndef OPEN_CFW_POWER_ONLY
float open_cfw_gx8002_logf(float x) { return __ieee754_logf(x); }
float open_cfw_gx8002_expf(float x) { return __ieee754_expf(x); }

#endif
