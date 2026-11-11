#ifndef R1_NATIVE_GOMORE_AUTHORIZATION_H
#define R1_NATIVE_GOMORE_AUTHORIZATION_H
#include <stdint.h>
#include <stddef.h>
struct r1_gomore_authorization_entry {
    uint8_t flags,padding[3];
    uint32_t enable_callback,disable_callback,context;
};
struct r1_gomore_authorization_state {
    uint8_t ready,padding0[3],device_id_cached_valid,padding1[3];
    uint32_t streams[4],idle_timer,hrv_count,hrv_total;
    struct r1_gomore_authorization_entry entries[7];
};
struct r1_gomore_authorization_samples {
    uint8_t hrv_active,padding[3];
    uint32_t hr_value;
};
_Static_assert(sizeof(struct r1_gomore_authorization_state)==148,"authorization state size");
_Static_assert(offsetof(struct r1_gomore_authorization_state,entries)==36,"authorization table offset");
_Static_assert(sizeof(struct r1_gomore_authorization_entry)==16,"authorization entry size");
_Static_assert(sizeof(struct r1_gomore_authorization_samples)==8,"authorization samples size");
extern volatile struct r1_gomore_authorization_state r1_gomore_authorization_state;
struct r1_gomore_sensor_state {
    uint32_t timestamp;
    uint16_t utc_offset,padding0;
    uint32_t acc_y,acc_x,acc_z;
    uint8_t acc_count,padding1[3];
    uint32_t raw_hr;
    uint8_t raw_hr_count,time_valid,padding2[2];
    uint32_t reserved;
    struct r1_gomore_authorization_samples authorization_samples;
    uint32_t reserved2;
    uint8_t inactive,padding3[3];
    /* Observed output prefix; retains gaps between native copied fields. */
    uint8_t output_snapshot[120];
};
_Static_assert(sizeof(struct r1_gomore_sensor_state)==172,"sensor workspace size");
_Static_assert(offsetof(struct r1_gomore_sensor_state,authorization_samples)==36,"shared sample offset");
_Static_assert(offsetof(struct r1_gomore_sensor_state,inactive)==48,"activity offset");
extern volatile struct r1_gomore_sensor_state r1_gomore_sensor_state;
#define r1_gomore_authorization_samples (r1_gomore_sensor_state.authorization_samples)
#define r1_device_id_once_status (r1_gomore_authorization_state.ready)
#define r1_gomore_wake_authorization_flags (r1_gomore_authorization_state.entries[4].flags)
#endif
