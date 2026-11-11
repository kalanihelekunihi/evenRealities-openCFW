#ifndef R1_NATIVE_HEALTH_TIME_STORAGE_H
#define R1_NATIVE_HEALTH_TIME_STORAGE_H
#include <stdint.h>
struct r1_health_time_transition {
    int16_t old_offset,new_offset;
    uint32_t old_timestamp,new_timestamp;
};
void r1_health_time_transition_storage_orchestrator(const volatile struct r1_health_time_transition *);
#endif
