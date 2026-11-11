#include <stdint.h>

extern volatile uint8_t r1_wear_living_status;
extern volatile uint32_t r1_wear_living_timestamp,r1_wear_living_stream;
extern uint32_t osKernelGetTickCount(void),r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);

void r1_wear_living_topic_callback(uint32_t context,uint32_t payload,uint32_t length)
{
    (void)context;(void)length;
    r1_wear_living_status=*(const volatile uint8_t *)(uintptr_t)(payload+1u);
    uint32_t now=osKernelGetTickCount();
    r1_wear_living_timestamp=now;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t status=r1_wear_living_status;
        (void)r1_structured_log_format(0x0c400000,
            "[RING]algo wear vivo: %d","[RING]algo wear vivo: %d",status);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t status=r1_wear_living_status;
        nrf_log_frontend_std_1(0x001c0003,"algo wear vivo: %d",status);
    }
    uint32_t stream=r1_wear_living_stream;
    if (stream) {
        r1_sensor_stream_unregister_by_name("wear",stream);
        r1_wear_living_stream=0;
    }
}
