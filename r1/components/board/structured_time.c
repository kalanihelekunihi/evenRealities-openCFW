/* Native timestamp consumers: RTC adapter 0x514BC, backend thunk 0x8ADA4,
 * local timestamp 0x8AD40. Contextual calendar code remains separate. */
#include <stddef.h>
#include <stdint.h>
#include "../registry/stock_registry.h"
#include "time_calendar/time_calendar.h"
generic_device_registry_device *r1_structured_rtc_device __attribute__((section(".r1.time.rtc"),aligned(4)));
time_calendar_registration r1_time_registration __attribute__((section(".r1.time.registration"),aligned(4)));
time_calendar_state r1_time_state __attribute__((section(".r1.time.state"),aligned(4)));
_Static_assert(offsetof(generic_device_registry_time_block,epoch_seconds)==44,"stock epoch field");
_Static_assert(sizeof(generic_device_registry_time_block)==64,"stock request extent");
_Static_assert(offsetof(time_calendar_registration,backend)==8,"stock backend slot");
_Static_assert(offsetof(time_calendar_state,utc_offset_minutes)==8,"stock signed timezone");
uint32_t r1_structured_log_timestamp_adapter(void) {
    generic_device_registry_time_block request={0};
    (void)r1_stock_dispatch_10(r1_structured_rtc_device,0,(uintptr_t)&request,0);
    return request.epoch_seconds;
}
uint32_t r1_time_backend_timestamp(void) {
    /* Native stock faults on an unbound backend/getter; do not add guards. */
    return r1_time_registration.backend->get(NULL);
}
uint32_t r1_structured_log_local_timestamp(void) {
    uint32_t epoch=r1_time_backend_timestamp();
    return epoch+(uint32_t)((int32_t)r1_time_state.utc_offset_minutes*60);
}
