#include <stdint.h>

extern volatile uint8_t r1_health_mode_byte;
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t r1_phone_cmd_send_op3(const void *,uint32_t,uint32_t);
extern uint32_t r1_glasses_connection_handle_get(void);
extern int32_t r1_ble_tx_queue_dispatch_type0(uint32_t,const void *,uint32_t);

/* Retain the recovered entry name; this packet reports hardware wear state. */
void r1_touch_status_report(void)
{
    uint8_t packet[12]={0,9,0x8c,0,0,0,0,0,0,0,0,0};
    packet[4]=r1_health_mode_byte!=0;
    if (r1_glasses_connection_handle_get()!=UINT16_MAX) {
        uint32_t handle=r1_glasses_connection_handle_get();
        (void)r1_ble_tx_queue_dispatch_type0(handle,packet,5);
    }
}

void r1_native_health_module_group4_callback(const volatile void *event)
{
    (void)event;
    uint32_t status=r1_health_mode_byte?2:1;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,
            "[RING]proto system status change, wear status: %d",
            "[RING]proto system status change, wear status: %d",status);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"proto system status change, wear status: %d",status);
    (void)r1_phone_cmd_send_op3(&status,1,0);
    r1_touch_status_report();
}
