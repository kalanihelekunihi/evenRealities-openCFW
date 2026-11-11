#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_sleep_sync_status_backend(const void *,uint32_t);
void r1_health_publish_spo2_state(uint32_t);
void r1_health_publish_temperature_state(uint32_t);

__attribute__((section(".text.r1_event_service_0008e154"))) void r1_event_service_0008e154(uint32_t status)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,"[RING]service sleep status: %d","[RING]service sleep status: %d",status);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"service sleep status: %d",status);
}

__attribute__((section(".text.r1_event_service_0008e1e0"))) void r1_event_service_0008e1e0(const void *buffer,uint32_t length)
{
    if (buffer && length) {
        r1_sleep_sync_status_backend(buffer,length);
        return;
    }
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,"[RING]sync status buffer is null","[RING]sync status buffer is null");
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0001,"sync status buffer is null");
}

__attribute__((section(".text.r1_event_service_0008e274"))) void r1_event_service_0008e274(void) { r1_health_publish_spo2_state(1); }
__attribute__((section(".text.r1_event_service_0008e552"))) void r1_event_service_0008e552(void) { r1_health_publish_temperature_state(0); }
__attribute__((section(".text.r1_event_service_0008e55c"))) void r1_event_service_0008e55c(void) { }

