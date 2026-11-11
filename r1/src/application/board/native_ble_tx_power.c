/* R1 radio power policy, stock 0x4e150; advertising availability 0x41800.
 * The S140 supervisor-call boundary is provided by the pinned Nordic headers. */
#include <stdint.h>
#include "ble_advertising.h"
#include "ble_conn_state.h"
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern ble_advertising_t r1_ble_advertising_context_a;
extern void r1_adc_error(uint32_t);

uint32_t r1_gap_adv_addr_get(uint8_t handle)
{
    ble_gap_addr_t address={0};
    return sd_ble_gap_adv_addr_get(handle,&address)==0;
}

void r1_tx_power_plan(uint32_t enabled)
{
    uint32_t status;
    if (r1_connection_field8!=UINT16_MAX &&
        ble_conn_state_status(r1_connection_field8)==BLE_CONN_STATUS_CONNECTED) {
        status=sd_ble_gap_tx_power_set(BLE_GAP_TX_POWER_ROLE_CONN,
                    r1_connection_field8,enabled ? 0:-8);
        if (status) r1_adc_error(status);
    }
    if (r1_connection_field10!=UINT16_MAX &&
        ble_conn_state_status(r1_connection_field10)==BLE_CONN_STATUS_CONNECTED) {
        status=sd_ble_gap_tx_power_set(BLE_GAP_TX_POWER_ROLE_CONN,
                    r1_connection_field10,enabled ? 6:-8);
        if (status) r1_adc_error(status);
    }
    volatile uint8_t *handle=&r1_ble_advertising_context_a.adv_handle;
    if (r1_gap_adv_addr_get(*handle)) {
        status=sd_ble_gap_tx_power_set(BLE_GAP_TX_POWER_ROLE_ADV,
                    *handle,enabled ? 0:-8);
        if (status) r1_adc_error(status);
    }
}

extern uint32_t r1_structured_log_mode_get(void);
/* Native0x4cc60: preserve full handle diagnostics, typed S140 key is uint16. */
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static const char r1_glasses_power_ring[]="[RING]glasses_tx_power_set success, conn_handle: %d, tx_power_level: %d";
static const char r1_glasses_power_sdk[]="glasses_tx_power_set success, conn_handle: %d, tx_power_level: %d";
void r1_glasses_tx_power_set(uint32_t connection)
{
 uint32_t status=sd_ble_gap_tx_power_set(BLE_GAP_TX_POWER_ROLE_CONN,(uint16_t)connection,6);
 if(status)r1_adc_error(status);
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c800000,r1_glasses_power_ring,r1_glasses_power_ring,connection,6u);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,r1_glasses_power_sdk,connection,6);
}
