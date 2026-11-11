#include "native_hourly_state.h"
/* One source owner for the native overlapping hourly/stress state. */
struct r1_hourly_stress_storage r1_health_hourly_stress_storage
    __attribute__((section(".r1.health.hourly_stress"),aligned(4)))={0};
