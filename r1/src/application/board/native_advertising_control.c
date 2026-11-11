/* Stock 0x4c81c restart and 0x4c8f8 stop guard. Existing Nordic storage
 * and S140 supervisor-call definitions own the controller interface. */
#include <stdint.h>
#include "ble_advertising.h"
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern ble_advertising_t r1_ble_advertising_context_a;
extern uint32_t r1_gap_adv_addr_get(uint8_t);
extern void r1_adc_error(uint32_t),r1_advertising_status_publish(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_advertising_start_result_ring[]="[RING]app_ble_advertising_start = %d";
const char r1_advertising_start_result_sdk[]="app_ble_advertising_start = %d";
static void stop_existing(volatile uint8_t *handle)
{
    uint32_t status=sd_ble_gap_adv_stop(*handle);
    if (status!=0 && status!=8) r1_adc_error(status);
}
void r1_advertising_restart(uint32_t mode)
{
    if (r1_connection_field8!=UINT16_MAX && r1_connection_field10!=UINT16_MAX)
        return;
    volatile uint8_t *handle=&r1_ble_advertising_context_a.adv_handle;
    if (r1_gap_adv_addr_get(*handle)) stop_existing(handle);
    uint32_t status=ble_advertising_start(&r1_ble_advertising_context_a,(ble_adv_mode_t)mode);
    if (status) r1_adc_error(status);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c400000,r1_advertising_start_result_ring,
                               r1_advertising_start_result_ring,status);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_advertising_start_result_sdk,status);
}
void r1_advertising_stop_guard(void)
{
    volatile uint8_t *handle=&r1_ble_advertising_context_a.adv_handle;
    if (!r1_gap_adv_addr_get(*handle)) return;
    stop_existing(handle);
    r1_advertising_status_publish(0,0);
}
