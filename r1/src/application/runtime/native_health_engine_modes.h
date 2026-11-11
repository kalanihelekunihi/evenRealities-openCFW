#ifndef R1_NATIVE_HEALTH_ENGINE_MODES_H
#define R1_NATIVE_HEALTH_ENGINE_MODES_H
#include <stdint.h>
uint32_t r1_health_lifecycle_mode_native(uint32_t,uint32_t);
uint32_t r1_health_lifecycle_profile_apply_native(uint32_t,uint32_t,uint32_t);
uint32_t r1_gomore_mode_threshold_native(uint32_t,uint32_t);
uint32_t r1_gomore_mode_value_store_native(uint32_t,uint32_t);
uint32_t r1_gomore_mode_code_valid_native(uint32_t,uint32_t);
uint32_t r1_gomore_mode_code_set_native(uint32_t,uint32_t);
uint32_t r1_gomore_mode_checked_store_native(uint32_t,uint32_t);
uint32_t r1_gomore_profile_slot_native(uint32_t,uint32_t,uint32_t,uint32_t);
#endif
