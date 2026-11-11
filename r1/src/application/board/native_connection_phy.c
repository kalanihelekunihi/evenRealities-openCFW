/* Stock 0x4d2f4. Ordinary C policy around the pinned S140 PHY gateway.
 * Full-word diagnostics precede the SDK's uint16/uint8 argument narrowing. */
#include <stdint.h>
#include "ble_conn_state.h"
#include "ble_gap.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
static const char invalid_ring[]="[RING]Invalid connection handle or not connected: %d";
static const char invalid_sdk[]="Invalid connection handle or not connected: %d";
static const char request_ring[]="[RING]Requesting PHY update: conn_handle=%d, tx_phys=0x%02X, rx_phys=0x%02X";
static const char request_sdk[]="Requesting PHY update: conn_handle=%d, tx_phys=0x%02X, rx_phys=0x%02X";
static const char error_ring[]="[RING]PHY update request failed: err_code=0x%08X";
static const char error_sdk[]="PHY update request failed: err_code=0x%08X";
uint32_t r1_connection_phy_update_plan(uint32_t connection,uint32_t tx,uint32_t rx)
{
 if(connection==UINT16_MAX || ble_conn_state_status((uint16_t)connection)!=BLE_CONN_STATUS_CONNECTED){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x08400000,invalid_ring,invalid_ring,connection);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0002,invalid_sdk,connection);
  return 8;
 }
 ble_gap_phys_t phys={.tx_phys=(uint8_t)tx,.rx_phys=(uint8_t)rx};
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0cc00000,request_ring,request_ring,connection,tx,rx);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,request_sdk,connection,tx,rx);
 uint32_t status=sd_ble_gap_phy_update((uint16_t)connection,&phys);
 if(status){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x04400000,error_ring,error_ring,status);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001,error_sdk,status);
 }
 return status;
}
