/* Stock BLE event consumer0x45184. This unit owns no connection state. */
#include <stdint.h>
#include "native_ble_connection_control.h"
#include "cmsis_os2.h"
#include "peer_manager.h"
#include "../board/native_battery_memory.h"
#include "../board/native_connection_parameters.h"
extern void *volatile r1_ble_message_queue;
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_phone_connection_handle_get(void),r1_glasses_connection_handle_get(void);
extern void r1_advertising_stop_guard(void),r1_advertising_restart(uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_protocol_time_timeout_callback(uint32_t),r1_connection_control_role_sync_thread_flags(uint32_t);
extern void r1_connection_control_plan_adv_start(uint32_t);
extern uint32_t r1_kv_dev_info_bit2_set(uint32_t),r1_peer_is_target_glasses(uint32_t);
extern void r1_charge_state_cache_update(void),r1_touch_status_report(void),r1_glasses_tx_power_set(uint32_t);
extern void r1_ear_worn_state_notify(uint32_t);
extern uint32_t r1_peer_address_from_slots(uint32_t,void *);
extern void r1_peer_address_record_update(const volatile void *,const volatile void *);
extern int32_t r1_native_memcmp(const uint8_t *,const uint8_t *,uint32_t);
extern uint32_t r1_phone_cmd_send_op8(const void *,uint32_t,uint32_t);
/* The registered native target0x4e1e2 is exactly BX LR. */
void r1_legacy_pair_timeout_callback(uint32_t argument){(void)argument;}

static const char text_4554c[]="[RING]AUTH_DEVICE_PHONE: phone_conn_handle set to %d";
static const char text_45584[]="AUTH_DEVICE_PHONE: phone_conn_handle set to %d";
static const char text_455b4[]="[RING]Phone and glasses are both connected, stop advertising";
static const char text_455f4[]="Phone and glasses are both connected, stop advertising";
static const char text_45630[]="[RING]encrypted auth success, 100ms auth flag will notify";
static const char text_4566c[]="encrypted auth success, 100ms auth flag will notify";
static const char text_456a0[]="[RING]pm_conn_secure wait encrypted auth success";
static const char text_456d4[]="pm_conn_secure wait encrypted auth success";
static const char text_45700[]="[RING]pm_conn_secure failed, err_code = %d";
static const char text_4572c[]="pm_conn_secure failed, err_code = %d";
static const char text_45754[]="[RING]AUTH_DEVICE_GLASSES, conn_handle=%d";
static const char text_45780[]="AUTH_DEVICE_GLASSES, conn_handle=%d";
static const char text_457a8[]="glasses connect, start fast advertising, for phone connect";
static const char text_45b34[]="[RING]ADV_START: connected glasses mac match target leg mac";
static const char text_45b70[]="ADV_START: connected glasses mac match target leg mac";
static const char text_45bbc[]="[RING]ADV_START: start fast advertising";
static const char text_45be4[]="ADV_START: start fast advertising";
static const char text_bea70[]="[RING]THREAD_BLE_EVT_TARGET_GLASSES_MAC: glasses_mac_addr = %02X:%02X:%02X:";
static const char text_beabc[]="THREAD_BLE_EVT_TARGET_GLASSES_MAC: glasses_mac_addr = %02X:%02X:%02X:";
static const char text_beb04[]="[RING]THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: left mac[2-0] = %02X:%02X:%02X";
static const char text_beb50[]="THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: left mac[2-0] = %02X:%02X:%02X";
static const char text_beb98[]="[RING]THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: right mac[2-0] = %02X:%02X:%02X";
static const char text_bebe4[]="THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: right mac[2-0] = %02X:%02X:%02X";
static const char text_bec2c[]="[RING]THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: left mac[5-3] = %02X:%02X:%02X";
static const char text_bec78[]="THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: left mac[5-3] = %02X:%02X:%02X";
static const char text_becc0[]="[RING]THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: right mac[5-3] = %02X:%02X:%02X";
static const char text_bed0c[]="THREAD_BLE_EVT_FAST_ADV_WAIT_CONNECT: right mac[5-3] = %02X:%02X:%02X";
static const char text_bed54[]="[RING]THREAD_BLE_EVT_TARGET_GLASSES_MAC: glasses_mac_addr = %02X:%02X:%02X";
static const char text_beda0[]="THREAD_BLE_EVT_TARGET_GLASSES_MAC: glasses_mac_addr = %02X:%02X:%02X";
static const char text_bede8[]="[RING]--->non-target glasses connected, notify it to unbind ring. conn_handle: %d";
static const char text_bee3c[]="--->non-target glasses connected, notify it to unbind ring. conn_handle: %d";
static const char text_bee88[]="[RING]ADV_START: connected glasses mac mismatch both legs, notify unbind conn_handle=%d";
static const char text_beee0[]="ADV_START: connected glasses mac mismatch both legs, notify unbind conn_handle=%d";
static const char text_bf010[]="[RING]ADV_START: connected glasses peer mac unavailable, skip disconnect compare";
static const char text_bf064[]="ADV_START: connected glasses peer mac unavailable, skip disconnect compare";
static const char text_bf0b0[]="[RING]ADV_START: phone and glasses both connected with matching mac, stop advertising";
static const char text_bf108[]="ADV_START: phone and glasses both connected with matching mac, stop advertising";
static const char text_bf158[]="[RING]ADV_START: glasses mac mismatch, wait disconnect to trigger fast advertising";
static const char text_bf1ac[]="ADV_START: glasses mac mismatch, wait disconnect to trigger fast advertising";
static const char text_bf3e8[]="[RING]glasses connect, start fast advertising, for phone connect";
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log0(uint32_t marker,uint32_t severity,const char *ring,const char *sdk)
{
 if(ring_enabled())(void)r1_structured_log_format(marker,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(severity,sdk);
}
static void log1(uint32_t marker,uint32_t severity,const char *ring,const char *sdk,uint32_t value)
{
 if(ring_enabled())(void)r1_structured_log_format(marker,ring,ring,value);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(severity,sdk,value);
}
/* Re-read the message word after each logging-mode provider, as stock does. */
static void log_message(uint32_t marker,uint32_t severity,const char *ring,const char *sdk,const volatile uint8_t *message)
{
 if(ring_enabled())(void)r1_structured_log_format(marker,ring,ring,read32(message));
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(severity,sdk,read32(message));
}
static void log_address(const volatile uint8_t *address,uint32_t offset,const char *ring,const char *sdk)
{
 if(ring_enabled()){
  uint32_t low=address[offset],middle=address[offset+1],high=address[offset+2];
  (void)r1_structured_log_format(0x0cc00000,ring,ring,high,middle,low);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t low=address[offset],middle=address[offset+1],high=address[offset+2];
  nrf_log_frontend_std_3(0x001c0003,sdk,high,middle,low);
 }
}
static void stop_both_roles(void)
{
 log0(0x0c000000,0x001c0003,text_455b4,text_455f4);
 (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
 r1_advertising_stop_guard();
}
static void pair_auth(const volatile uint8_t *message)
{
 (void)r1_native_delayed_cancel(r1_legacy_pair_timeout_callback,0);
 (void)r1_native_delayed_cancel(r1_protocol_time_timeout_callback,0);
 r1_app_ble_set_slow_mode(read16(message),0);
 uint32_t role=message[12];
 if(role==1){
  log_message(0x0c400000,0x001c0003,text_4554c,text_45584,message);
  if(r1_phone_connection_handle_get()!=65535u && r1_glasses_connection_handle_get()!=65535u)stop_both_roles();
  if(r1_ble_control_flag_get()){
   log0(0x0c000000,0x001c0003,text_45630,text_4566c);
   r1_native_delayed_schedule(r1_protocol_time_timeout_callback,0,0x66);
   r1_native_delayed_schedule(r1_protocol_time_timeout_callback,0,0x800);
  }else{
   log0(0x0c000000,0x001c0003,text_456a0,text_456d4);
   uint32_t status=pm_conn_secure((uint16_t)read16(message),false);
   if(status && status!=17u)log1(0x08400000,0x001c0002,text_45700,text_4572c,status);
   r1_native_delayed_schedule(r1_protocol_time_timeout_callback,1,0x3c00);
  }
 }else if(role==2){
  log_message(0x0c400000,0x001c0003,text_45754,text_45780,message);
  (void)r1_kv_dev_info_bit2_set(1);
  if(r1_phone_connection_handle_get()==65535u){
   log0(0x0c000000,0x001c0003,text_bf3e8,text_457a8);
   (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
   r1_native_delayed_schedule(r1_connection_control_role_sync_thread_flags,0,0x1400);
  }
  if(r1_peer_is_target_glasses(read16(message))){
   r1_charge_state_cache_update();r1_touch_status_report();r1_glasses_tx_power_set(read16(message));
   if(r1_phone_connection_handle_get()!=65535u && r1_glasses_connection_handle_get()!=65535u)stop_both_roles();
  }else{
   log_message(0x04400000,0x001c0001,text_bede8,text_bee3c,message);
   r1_ear_worn_state_notify(read16(message));
   (void)r1_native_delayed_cancel(r1_connection_control_plan_adv_start,0);
   r1_native_delayed_schedule(r1_connection_control_plan_adv_start,read32(message),0x5000);
  }
 }
}
static void fast_advertising_targets(const volatile uint8_t *message)
{
 const volatile uint8_t *first=message+12,*second=message+18;
 log_address(first,3,text_becc0,text_bed0c);
 /* The native second diagnostic reads the second target despite its label. */
 log_address(second,0,text_beb98,text_bebe4);
 log_address(second,3,text_bec2c,text_bec78);
 log_address(second,0,text_beb04,text_beb50);
 uint32_t glasses=r1_glasses_connection_handle_get(),mismatch=0;
 if(glasses!=65535u && read32(message+8)>=12u){
  uint8_t address[8]={0};
  if(r1_peer_address_from_slots(glasses,address)){
   if(r1_native_memcmp(address,(const uint8_t *)(uintptr_t)first,6) &&
      r1_native_memcmp(address,(const uint8_t *)(uintptr_t)second,6)){
    log1(0x0c400000,0x001c0003,text_bee88,text_beee0,glasses);
    mismatch=1;r1_ear_worn_state_notify(glasses);
    (void)r1_native_delayed_cancel(r1_connection_control_plan_adv_start,0);
    r1_native_delayed_schedule(r1_connection_control_plan_adv_start,glasses,0x5000);
   }else log0(0x0c000000,0x001c0003,text_45b34,text_45b70);
  }else log0(0x08000000,0x001c0002,text_bf010,text_bf064);
 }
 r1_peer_address_record_update(first,second);
 (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
 if(mismatch)log0(0x0c000000,0x001c0003,text_bf158,text_bf1ac);
 else if(glasses==65535u || r1_phone_connection_handle_get()==65535u){
  log0(0x0c000000,0x001c0003,text_45bbc,text_45be4);r1_advertising_restart(3);
 }else{
  log0(0x0c000000,0x001c0003,text_bf0b0,text_bf108);r1_advertising_stop_guard();
 }
}
/* Queue ownership transfers only on osOK. Known routes require readable
 * native header/payload spans; a null successful dequeue ends this drain. */
void r1_ble_connection_control_event_consumer(void)
{
 void *item=0;
 while(osMessageQueueGet(r1_ble_message_queue,&item,0,0)==osOK){
  if(!item)return;
  const volatile uint8_t *message=item;
  switch(read32(message+4)){
   case 2:pair_auth(message);break;
   case 8:
    if(read32(message+8)){uint8_t byte=message[12];r1_phone_cmd_send_op8(&byte,1,0);}
    break;
   case 16:r1_connection_parameter_mode_adapter(read16(message),1);break;
   case 32:r1_connection_parameter_mode_adapter(read16(message),2);break;
   case 64:r1_connection_parameter_mode_adapter(read16(message),0);break;
   case 0x200:fast_advertising_targets(message);break;
   case 0x4000:
    log_address(message+12,3,text_bea70,text_beabc);
    log_address(message+12,0,text_bed54,text_beda0);
    r1_peer_address_record_update(message+12,message+12);break;
   default:break;
  }
  vPortFree(item);item=0;
 }
}
