/* Stock peer-manager event policy0x7f2b0 and bond diagnostic0x8216c.
 * Shared BLE flags/handles retain their existing owners. */
#include <stdint.h>
#include <stddef.h>
#include "peer_manager.h"
#include "peer_manager_handler.h"
#include "native_battery_memory.h"
extern volatile uint8_t r1_ble_control_flag;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_5(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void nrf_log_frontend_hexdump(uint32_t,const void *,uint16_t);
extern uint32_t ble_conn_state_peripheral_conn_count(void),r1_glasses_connection_handle_get(void),r1_phone_connection_handle_get(void),r1_peer_record_flag_get(void);
extern void r1_advertising_restart(uint32_t),r1_advertising_stop_guard(void),r1_app_ble_set_slow_mode_again(uint32_t);
extern void r1_protocol_time_timeout_callback(uint32_t),r1_legacy_pair_timeout_callback(uint32_t),r1_connection_control_role_sync_thread_flags(uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
_Static_assert(offsetof(pm_evt_t,conn_handle)==2 && offsetof(pm_evt_t,peer_id)==4 && offsetof(pm_evt_t,params)==8,"native short-enum event ABI");
_Static_assert(sizeof(pm_peer_data_bonding_t)==80 && offsetof(pm_peer_data_bonding_t,own_ltk)==52,"native bonding layout");
_Static_assert(sizeof(pm_conn_sec_config_t)==1 && PM_EVT_CONN_SEC_SUCCEEDED==3 && PM_EVT_PEERS_DELETE_SUCCEEDED==13 && PM_EVT_FLASH_GARBAGE_COLLECTED==20,"native event/config ABI");
volatile pm_peer_id_t r1_ble_last_secured_peer_id __attribute__((section(".r1.ble.last_secured_peer_id"),aligned(2)))=0;
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
#define SDK(n,severity,text,...) do {if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_##n(severity,text,##__VA_ARGS__);}while(0)
static const char text_7f6c0[]="[RING]phone connect:PM_EVT_CONN_SEC_SUCCEEDED";
static const char text_7f6f0[]="phone connect:PM_EVT_CONN_SEC_SUCCEEDED";
static const char text_be5f0[]="[RING]glasses connect ring flag is %d, start fast advertising, for glasses connect";
static const char text_be644[]="glasses connect ring flag is %d, start fast advertising, for glasses connect";
static const char text_7f724[]="[RING]Phone and glasses are both connected, stop advertising";
static const char text_7f764[]="Phone and glasses are both connected, stop advertising";
static const char text_7f79c[]="[RING]This is a reconnection device! Stored LTK exist\n";
static const char text_7f7d4[]="This is a reconnection device! Stored LTK exist\n";
static const char text_7f808[]="[RING]This is a new device connecting for the first time\n";
static const char text_7f844[]="This is a new device connecting for the first time\n";
static const char text_7f878[]="[RING]encrypted get sec auth flag will notify";
static const char text_7f8a8[]="encrypted get sec auth flag will notify";
static const char text_7f8d0[]="[RING]encrypted not get sec auth flag will wait";
static const char text_7f900[]="encrypted not get sec auth flag will wait";
static const char text_7f92c[]="REMOTE";
static const char text_be51c[]="[RING]Connection security failed: conn_handle: 0x%x, peer_id: %d, procedure: %d, error: 0x%x, error_src: %s";
static const char text_be588[]="Connection security failed: conn_handle: 0x%x, peer_id: %d, procedure: %d, error: 0x%x, error_src: %s";
static const char text_7f93c[]="LOCAL";
static const char text_be468[]="[RING]SMP timeout detected, connection will be terminated. Reconnect required for pairing.";
static const char text_be4c4[]="SMP timeout detected, connection will be terminated. Reconnect required for pairing.";
static const char text_7f94c[]="[RING]New Bond, add the peer to the whitelist if possible";
static const char text_7f988[]="New Bond, add the peer to the whitelist if possible";
static const char text_be3c0[]="[RING]PM_EVT_CONN_SEC_CONFIG_REQ: peer_id=%d, accept to fix bonding, conn_handle=%d\r\n";
static const char text_be418[]="PM_EVT_CONN_SEC_CONFIG_REQ: peer_id=%d, accept to fix bonding, conn_handle=%d\r\n";
static const char text_7f9c8[]="[RING]GC completed";
static const char text_7f9dc[]="GC completed";
static const char text_7fa10[]="[RING]PM_EVT_STORAGE_FULL occurred";
static const char text_7fa34[]="PM_EVT_STORAGE_FULL occurred";
static const char text_822d4[]="[RING]Error: Invalid Peer ID\n";
static const char text_822f4[]="Error: Invalid Peer ID\n";
static const char text_8230c[]="[RING]LTK[0]:[15]";
static const char text_82320[]="LTK[0]:[15]";
static const char text_8232c[]="[RING]%02x:%02x:%02x:%02x:%02x:%02x:%02x:%02x";
static const char text_8235c[]="[RING]Failed to load bonding data for Peer ID %d (Error: 0x%X)\n";
static const char text_8239c[]="Failed to load bonding data for Peer ID %d (Error: 0x%X)\n";

void r1_peer_bond_diagnostic_plan(uint32_t peer)
{
 if(peer==UINT16_MAX){RING(0x04000000,text_822d4);SDK(0,0x001c0001,text_822f4);return;}
 pm_peer_data_bonding_t bonding;
 uint32_t status=pm_peer_data_bonding_load((pm_peer_id_t)peer,&bonding);
 if(status){RING(0x08800000,text_8235c,peer,status);SDK(2,0x001c0002,text_8239c,peer,status);return;}
 volatile uint8_t *data=(volatile void *)&bonding;
 nrf_log_frontend_hexdump(0x001c0003,(const void *)(uintptr_t)(data+18),6);
 nrf_log_frontend_hexdump(0x001c0003,(const void *)(uintptr_t)(data+1),16);
 RING(0x0c000000,text_8230c);SDK(0,0x001c0003,text_82320);
 nrf_log_frontend_hexdump(0x001c0003,(const void *)(uintptr_t)(data+52),16);
 if(r1_structured_log_mode_get()==2)return;
 (void)r1_structured_log_format(0x0e000000,text_8232c,text_8232c,data[52],data[53],data[54],data[55],data[56],data[57],data[58],data[59]);
 (void)r1_structured_log_format(0x0e000000,text_8232c,text_8232c,data[60],data[61],data[62],data[63],data[64],data[65],data[66],data[67]);
}
static void time_notifications(uint32_t argument)
{
 (void)r1_native_delayed_cancel(r1_protocol_time_timeout_callback,0);
 r1_native_delayed_schedule(r1_protocol_time_timeout_callback,argument,0x66);
 r1_native_delayed_schedule(r1_protocol_time_timeout_callback,argument,0x400);
 r1_native_delayed_schedule(r1_protocol_time_timeout_callback,argument,0x800);
}
void r1_peer_manager_event_policy(pm_evt_t const *event)
{
 pm_handler_on_pm_evt(event);
 pm_handler_flash_clean(event);
 const volatile uint8_t *e=(const volatile void *)event;
 switch(e[0]){
 case 3:{
  r1_ble_last_secured_peer_id=read16(e+4);
  uint32_t count=(uint8_t)ble_conn_state_peripheral_conn_count();
  (void)r1_native_delayed_cancel(r1_legacy_pair_timeout_callback,0);
  time_notifications(0);
  if(count<3 && r1_glasses_connection_handle_get()==UINT16_MAX){
   RING(0x0c000000,text_7f6c0);SDK(0,0x001c0003,text_7f6f0);
   RING(0x0c400000,text_be5f0,r1_peer_record_flag_get());SDK(1,0x001c0003,text_be644,r1_peer_record_flag_get());
   (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
   r1_native_delayed_schedule(r1_connection_control_role_sync_thread_flags,0,0x2800);
  }
  if(r1_phone_connection_handle_get()!=UINT16_MAX && r1_glasses_connection_handle_get()!=UINT16_MAX){
   RING(0x0c000000,text_7f724);SDK(0,0x001c0003,text_7f764);
   (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);r1_advertising_stop_guard();
  }
  pm_peer_data_bonding_t bonding;
  uint32_t status=pm_peer_data_bonding_load(r1_ble_last_secured_peer_id,&bonding);
  r1_app_ble_set_slow_mode_again(r1_phone_connection_handle_get());
  if(!status){RING(0x0c000000,text_7f79c);SDK(0,0x001c0003,text_7f7d4);r1_peer_bond_diagnostic_plan(r1_ble_last_secured_peer_id);}
  else{RING(0x0c000000,text_7f808);SDK(0,0x001c0003,text_7f844);}
  if(r1_ble_control_flag){time_notifications(0);RING(0x0c000000,text_7f878);SDK(0,0x001c0003,text_7f8a8);}
  else{r1_ble_control_flag=1;RING(0x0c000000,text_7f8d0);SDK(0,0x001c0003,text_7f900);}
  return;
 }
 case 4:{
  uint32_t error=read16(e+10),source=e[12],procedure=e[8];
  const char *origin=source?text_7f92c:text_7f93c;
  RING(0x05400000,text_be51c,read16(e+2),read16(e+4),procedure,error,origin);
  SDK(5,0x001c0001,text_be588,read16(e+2),read16(e+4),procedure,error,(uintptr_t)origin);
  (void)r1_native_delayed_cancel(r1_protocol_time_timeout_callback,0);
  r1_native_delayed_schedule(r1_protocol_time_timeout_callback,1,0x800);
  if(error==0x1101){RING(0x08000000,text_be468);SDK(0,0x001c0002,text_be4c4);}
  return;
 }
 case 5:{
  RING(0x0c800000,text_be3c0,read16(e+4),read16(e+2));SDK(2,0x001c0003,text_be418,read16(e+4),read16(e+2));
  struct {pm_conn_sec_config_t value;uint8_t padding[3];} configuration={.value={.allow_repairing=true}};
  pm_conn_sec_config_reply(read16(e+2),&configuration.value);return;
 }
 case 7:RING(0x08000000,text_7fa10);SDK(0,0x001c0002,text_7fa34);return;
 case 9:
  if((e[16]&1u) && e[8]==7){RING(0x0c000000,text_7f94c);SDK(0,0x001c0003,text_7f988);r1_peer_bond_diagnostic_plan(r1_ble_last_secured_peer_id);}return;
 case 13:r1_advertising_restart(3);return;
 case 20:RING(0x0c000000,text_7f9c8);SDK(0,0x001c0003,text_7f9dc);return;
 default:return;
 }
}
