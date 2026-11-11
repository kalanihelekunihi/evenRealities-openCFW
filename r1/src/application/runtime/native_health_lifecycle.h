#ifndef R1_NATIVE_HEALTH_LIFECYCLE_H
#define R1_NATIVE_HEALTH_LIFECYCLE_H
#include <stdint.h>
/* Stock 0x4bd98 has no consumed return value. Mode 0 restores crash data;
 * mode 1 clears previous data before initialization; other words do neither. */
void r1_native_gomore_lifecycle_initialize(uint32_t mode);
void r1_gomore_force_reinitialize_native(void);
void r1_gomore_time_transition_adapter(uint32_t packet);
#endif
