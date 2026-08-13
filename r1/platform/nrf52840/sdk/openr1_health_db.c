#include "openr1/r1_health_db.h"

typedef struct {
    void *(*provider_handle)(void *);
    r1_error (*startup)(
        const uint8_t *, const r1_health_db_startup_ops *,
        r1_health_crash_record *, r1_activity_history *,
        r1_health_u8_history *, r1_health_u8_accumulator *,
        r1_health_u8_history *, r1_health_u16_history *,
        r1_health_db_startup_result *);
} openr1_health_db_api;

__attribute__((used, section(".openr1_health_db_api")))
static const openr1_health_db_api retained_health_db_api = {
    r1_health_db_provider_handle,
    r1_health_db_startup,
};
