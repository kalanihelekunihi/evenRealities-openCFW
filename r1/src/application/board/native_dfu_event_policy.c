/* Stock buttonless DFU policy0x5232c and disconnect callback0x5c58c.
 * SDK owns bootloader entry; prepare only changes instance B's disconnect
 * advertising policy and requests disconnects through the typed S140 API. */
#include <stdint.h>
#include <stddef.h>
#include "ble_dfu.h"
#include "ble_advertising.h"
#include "ble_conn_state.h"
extern ble_advertising_t r1_ble_advertising_context_b;
extern void r1_advertising_params_init(ble_adv_modes_config_t *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
_Static_assert(sizeof(ble_adv_modes_config_t)==44 && offsetof(ble_adv_modes_config_t,ble_adv_on_disconnect_disabled)==0,"native advertising configuration");
_Static_assert(offsetof(ble_advertising_t,adv_modes_config)==4,"native advertising instance configuration");
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
#define SDK0(severity,text) do {if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(severity,text);}while(0)
static const char text_524a0[]="[RING]Device is preparing to enter bootloader mode.";
static const char text_524d4[]="Device is preparing to enter bootloader mode.";
static const char text_5250c[]="[RING]Disconnected %d links.";
static const char text_5252c[]="Disconnected %d links.";
static const char text_52544[]="[RING]Device will enter bootloader mode.";
static const char text_52570[]="Device will enter bootloader mode.";
static const char text_52594[]="[RING]Request to enter bootloader mode failed asynchroneously.";
static const char text_525d4[]="Request to enter bootloader mode failed asynchroneously.";
static const char text_52610[]="[RING]Request to send a response to client failed.";
static const char text_52644[]="Request to send a response to client failed.";
static const char text_52674[]="[RING]Unknown event from ble_dfu_buttonless.";
static const char text_526a4[]="Unknown event from ble_dfu_buttonless.";
static const char text_be334[]="[RING]Failed to disconnect connection. Connection handle: %d Error: %d";
static const char text_be37c[]="Failed to disconnect connection. Connection handle: %d Error: %d";

void r1_ble_disconnect_attempt(uint16_t connection,void *context)
{
 (void)context;
 uint32_t status=sd_ble_gap_disconnect(connection,BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
 if(!status)return;
 RING(0x08800000,text_be334,connection,status);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0002,text_be37c,connection,status);
}
void r1_buttonless_dfu_event_policy(ble_dfu_buttonless_evt_type_t event)
{
 switch(event){
 case BLE_DFU_EVT_BOOTLOADER_ENTER_PREPARE:{
  RING(0x0c000000,text_524a0);SDK0(0x001c0003,text_524d4);
  ble_adv_modes_config_t configuration;
  r1_advertising_params_init(&configuration);
  configuration.ble_adv_on_disconnect_disabled=true;
  ble_advertising_modes_config_set(&r1_ble_advertising_context_b,&configuration);
  uint32_t count=ble_conn_state_for_each_connected(r1_ble_disconnect_attempt,NULL);
  RING(0x0c400000,text_5250c,count);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,text_5252c,count);
  return;
 }
 case BLE_DFU_EVT_BOOTLOADER_ENTER:RING(0x0c000000,text_52544);SDK0(0x001c0003,text_52570);return;
 case BLE_DFU_EVT_BOOTLOADER_ENTER_FAILED:RING(0x04000000,text_52594);SDK0(0x001c0001,text_525d4);return;
 case BLE_DFU_EVT_RESPONSE_SEND_ERROR:RING(0x04000000,text_52610);SDK0(0x001c0001,text_52644);return;
 default:RING(0x04000000,text_52674);SDK0(0x001c0001,text_526a4);return;
 }
}
