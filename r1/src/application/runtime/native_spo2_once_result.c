#include <stdint.h>
#include "native_spo2_timing.h"
#include "../../vendor/gomore_primitives/gomore_primitives.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_6(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_health_mode_is_2(void),r1_event_publish(uint32_t,const void *,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);

static void raw_ring(const volatile uint8_t *packet)
{
    /* Preserve the native fault/read order, including signed byte 3. */
    uint32_t b2=packet[2];
    uint32_t b5=packet[5];
    uint32_t b4=packet[4];
    int32_t b3=(int8_t)packet[3];
    uint32_t b1=packet[1];
    uint32_t b0=packet[0];
    (void)r1_structured_log_format(0x0d800000,
        "[RING]algo spo2 once result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
        "[RING]algo spo2 once result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
        b0,b1,b2,b3,b4,b5);
}
static void raw_sdk(const volatile uint8_t *packet)
{
    uint32_t b2=packet[2];
    uint32_t b5=packet[5];
    uint32_t b4=packet[4];
    int32_t b3=(int8_t)packet[3];
    uint32_t b1=packet[1];
    uint32_t b0=packet[0];
    nrf_log_frontend_std_6(0x001c0003,
        "algo spo2 once result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
        b0,b1,b2,(uint32_t)b3,b4,b5);
}
__attribute__((section(".text.r1_spo2_once_result_plan")))
void r1_spo2_once_result_plan(uint32_t handle,const volatile void *data,uint32_t length)
{
    (void)length;
    const volatile uint8_t *packet=data;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) raw_ring(packet);
    if (r1_structured_log_mode_get()&2u) raw_sdk(packet);
    uint32_t valid=gomore_primitives_byte_in_70_100(packet[0]);
    if (valid && r1_health_mode_is_2()) {
        uint8_t record[8]={0};
        record[0]=gomore_primitives_piecewise_clamp_70_100(packet[0]);
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
            uint32_t converted=record[0];
            uint32_t raw=packet[0];
            (void)r1_structured_log_format(0x0c800000,
                "[RING]algo spo2 once calibrated: %d -> %d",
                "[RING]algo spo2 once calibrated: %d -> %d",raw,converted);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t converted=record[0];
            uint32_t raw=packet[0];
            nrf_log_frontend_std_2(0x001c0003,"algo spo2 once calibrated: %d -> %d",raw,converted);
        }
        (void)r1_event_publish(8,record,8);
    }
    r1_sensor_stream_unregister_by_name("spo2",handle);
    r1_spo2_streams[0]=0;
}
