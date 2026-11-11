/* Stock 0x52b9c GAP observer. Existing SDK contexts and recovered state owners
 * are shared with the connection consumer; no shadow connection database. */
#include <stdint.h>
#include <stddef.h>
#include "ble.h"
#include "ble_advertising.h"
#include "ble_conn_state.h"
#include "nrf_ble_qwr.h"
#include "native_battery_memory.h"
#include "native_peer_address.h"
#include "native_connection_parameters.h"
#include "../runtime/native_factory_mode.h"
#include "../runtime/native_ack_registry.h"
extern volatile uint16_t r1_connection_field6,r1_connection_field8,r1_connection_field10;
extern nrf_ble_qwr_t r1_ble_qwr_context_a,r1_ble_qwr_context_b,r1_ble_qwr_context_c;
extern ble_advertising_t r1_ble_advertising_context_a;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_ble_flag_2000_callback(uint32_t),r1_legacy_pair_timeout_callback(uint32_t);
extern void r1_connection_control_role_sync_thread_flags(uint32_t),r1_connection_control_plan_adv_start(uint32_t);
extern void r1_bae8_rx_timeout_noop(uint32_t);
extern void r1_factory_status_timeout_6a988(uint32_t),r1_factory_status_timeout_6a668(uint32_t);
extern uint32_t r1_advertising_configuration_byte_get(void),r1_gap_adv_addr_get(uint8_t);
extern uint32_t r1_connection_phy_update_plan(uint32_t,uint32_t,uint32_t);
extern void r1_status_record_ring_publish(uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_service_touch_close(uint32_t),r1_adc_error(uint32_t);
_Static_assert(offsetof(ble_evt_t,evt.gap_evt.conn_handle)==4,"native event key");
_Static_assert(offsetof(ble_advertising_t,adv_handle)==84,"native advertising key");
_Static_assert(sizeof(nrf_ble_qwr_t)==12 && offsetof(nrf_ble_qwr_t,conn_handle)==2,"native QWR layout");
volatile uint8_t r1_ble_connection_latch __attribute__((section(".r1.ble.connection.latch")))=0;
/* Native0x4e1e0 is distinct from the adjacent0x4e1e2 callback. */
void r1_legacy_pair_hook_nop(uint32_t argument){(void)argument;}
/* Native0x6a95c: factory state already owns bytes0x20006c37/38. */
void r1_factory_status_reset(void)
{
 (void)r1_native_delayed_cancel(r1_factory_status_timeout_6a988,0);
 (void)r1_native_delayed_cancel(r1_factory_status_timeout_6a668,0);
 r1_factory_mode_state.reserved[2]=255;
 r1_factory_mode_state.reserved[3]=255;
}
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
#define SDK(n,severity,text,...) do {if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_##n(severity,text,##__VA_ARGS__);}while(0)
static const char text_52fb4[]="[RING]Connected";
static const char text_52fc4[]="Connected";
static const char text_52fd0[]="[RING]Connected MAC: %02X:%02X:%02X:";
static const char text_52ff8[]="Connected MAC: %02X:%02X:%02X:";
static const char text_53018[]="[RING]%02X:%02X:%02X, addr_type: %d";
static const char text_5303c[]="%02X:%02X:%02X, addr_type: %d";
static const char text_53064[]="[RING]Phone connected, wait glasses auth.";
static const char text_53090[]="Phone connected, wait glasses auth.";
static const char text_530b4[]="[RING]Connection err_code: 0x%x .";
static const char text_530d8[]="Connection err_code: 0x%x .";
static const char text_530f4[]="[RING]Disconnected, conn_handle: %d, reason: 0x%x";
static const char text_53128[]="Disconnected, conn_handle: %d, reason: 0x%x";
static const char text_bdedc[]="[RING]Disconnected, phone_conn_handle: %d, glasses_conn_handle: %d";
static const char text_53158[]="Disconnected, phone_conn_handle: %d, glasses_conn_handle: %d";
static const char text_5319c[]="[RING]periph_link_cnt: %d";
static const char text_531b8[]="periph_link_cnt: %d";
static const char text_531cc[]="[RING]glasses disconnected, conn_handle: %d";
static const char text_531f8[]="glasses disconnected, conn_handle: %d";
static const char text_53220[]="[RING]phone disconnected, conn_handle: %d";
static const char text_5324c[]="phone disconnected, conn_handle: %d";
static const char text_be284[]="[RING]ble_advertising_start failed: 0x%x, periph_link_cnt: %d, will retry via event loop";
static const char text_be2e0[]="ble_advertising_start failed: 0x%x, periph_link_cnt: %d, will retry via event loop";
static const char text_53548[]="[RING]request PHY update: tx_phys=0x%02X, rx_phys=0x%02X";
static const char text_53584[]="request PHY update: tx_phys=0x%02X, rx_phys=0x%02X";
static const char text_535b8[]="[RING]phone_conn_handle: %d, glasses_conn_handle: %d";
static const char text_535f0[]="phone_conn_handle: %d, glasses_conn_handle: %d";
static const char text_53620[]="[RING]Glasses PHY update request. conn_handle: %d";
static const char text_53654[]="Glasses PHY update request. conn_handle: %d";
static const char text_53680[]="[RING]Using local preferred PHY: tx=1M, rx=coded";
static const char text_536b4[]="Using local preferred PHY: tx=1M, rx=coded";
static const char text_536e0[]="[RING]APP PHY update request conn_handle: %d";
static const char text_53710[]="APP PHY update request conn_handle: %d";
static const char text_bdc90[]="[RING]PHY update completed: tx_phy=0x%02X, rx_phy=0x%02X, status=0x%02X";
static const char text_bdcd8[]="PHY update completed: tx_phy=0x%02X, rx_phy=0x%02X, status=0x%02X";
static const char text_bddb0[]="[RING]Successfully switched to Coded PHY! tx_phy=0x%02X, rx_phy=0x%02X";
static const char text_bddf8[]="Successfully switched to Coded PHY! tx_phy=0x%02X, rx_phy=0x%02X";
static const char text_bde3c[]="[RING]PHY update succeeded but not using Coded PHY. tx_phy=0x%02X, rx_phy=0x%02X";
static const char text_bde90[]="PHY update succeeded but not using Coded PHY. tx_phy=0x%02X, rx_phy=0x%02X";
static const char text_53750[]="[RING]PHY update failed with status: 0x%02X";
static const char text_5377c[]="PHY update failed with status: 0x%02X";
static const char text_537a4[]="[RING]GATT Client Timeout.";
static const char text_537c0[]="GATT Client Timeout.";
static const char text_537d8[]="[RING]GATT Server Timeout.";
static const char text_537f4[]="GATT Server Timeout.";

void r1_gap_event_plan_build(ble_evt_t const *event,void *context)
{
 (void)context;
 const volatile uint8_t *e=(const volatile void *)event;
 nrf_ble_qwr_t *const qwr[3]={&r1_ble_qwr_context_a,&r1_ble_qwr_context_b,&r1_ble_qwr_context_c};
 switch(read16(e)){
 case 16:{
  (void)r1_native_delayed_cancel(r1_ble_flag_2000_callback,0);
  r1_native_delayed_schedule(r1_ble_flag_2000_callback,0,0xf000);
  RING(0x0c000000,text_52fb4);SDK(0,0x001c0003,text_52fc4);
  RING(0x0cc00000,text_52fd0,e[14],e[13],e[12]);SDK(3,0x001c0003,text_52ff8,e[14],e[13],e[12]);
  RING(0x0d000000,text_53018,e[11],e[10],e[9],e[8]>>1);SDK(4,0x001c0003,text_5303c,e[11],e[10],e[9],e[8]>>1);
  uint32_t connection=read16(e+4);
  if(connection<3){volatile uint8_t *slot=r1_ble_peer_address_slots[connection];write32(slot,read32(e+8));write16(slot+4,read16(e+12));slot[6]=e[14];}
  (void)r1_native_delayed_cancel(r1_legacy_pair_timeout_callback,0);
  (void)r1_native_delayed_cancel(r1_legacy_pair_hook_nop,0);
  if(r1_advertising_configuration_byte_get()==0x5a){
   r1_native_delayed_schedule(r1_legacy_pair_timeout_callback,read16(e+4),0x7800);
   if(r1_connection_field8!=UINT16_MAX){
    RING(0x08000000,text_53064);SDK(0,0x001c0002,text_53090);
    r1_native_delayed_schedule(r1_legacy_pair_hook_nop,read16(e+4),0x7800);
   }else (void)r1_ble_control_flag_set(0);
  }
  r1_connection_field6=read16(e+4);
  for(uint32_t i=0;i<3;i++)if(*(volatile uint16_t *)&qwr[i]->conn_handle==UINT16_MAX){
   uint32_t status=nrf_ble_qwr_conn_handle_assign(qwr[i],read16(e+4));
   RING(0x0c400000,text_530b4,status);SDK(1,0x001c0003,text_530d8,status);
   if(status)r1_adc_error(status);
   break;
  }
  return;
 }
 case 17:{
  RING(0x0c800000,text_530f4,read16(e+4),e[8]);SDK(2,0x001c0003,text_53128,read16(e+4),e[8]);
  RING(0x0c800000,text_bdedc,r1_connection_field8,r1_connection_field10);SDK(2,0x001c0003,text_53158,r1_connection_field8,r1_connection_field10);
  (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
  (void)r1_native_delayed_cancel(r1_legacy_pair_timeout_callback,0);
  (void)r1_native_delayed_cancel(r1_legacy_pair_hook_nop,0);
  uint32_t remaining=ble_conn_state_peripheral_conn_count();
  RING(0x0c400000,text_5319c,remaining);SDK(1,0x001c0003,text_531b8,remaining);
  r1_ble_connection_latch=0;
  uint32_t connection=read16(e+4);
  for(uint32_t i=0;i<3;i++)if(*(volatile uint16_t *)&qwr[i]->conn_handle==connection){*(volatile uint16_t *)&qwr[i]->conn_handle=UINT16_MAX;break;}
  connection=read16(e+4);
  if(connection<3){volatile uint8_t *slot=r1_ble_peer_address_slots[connection];write32(slot,0);write16(slot+4,0);slot[6]=0;}
  connection=read16(e+4);
  if(r1_connection_field10==connection){
   RING(0x0c400000,text_531cc,read16(e+4));SDK(1,0x001c0003,text_531f8,read16(e+4));
   r1_status_record_ring_publish(1,3,e[8],2);
   (void)r1_native_delayed_cancel(r1_connection_control_plan_adv_start,0);
   r1_connection_field10=UINT16_MAX;
   r1_service_touch_close(0);r1_factory_status_reset();
  }else if(r1_connection_field8==connection){
   RING(0x0c400000,text_53220,read16(e+4));SDK(1,0x001c0003,text_5324c,read16(e+4));
   r1_status_record_ring_publish(1,3,e[8],1);
   (void)r1_ble_control_flag_set(0);r1_connection_field8=UINT16_MAX;
   (void)r1_native_delayed_cancel(r1_bae8_rx_timeout_noop,0);(void)r1_ack_table_clear();
  }else r1_status_record_ring_publish(1,3,e[8],0);
  volatile uint8_t *handle=&r1_ble_advertising_context_a.adv_handle;
  if(r1_gap_adv_addr_get(*handle)){uint32_t status=sd_ble_gap_adv_stop(*handle);if(status && status!=8)r1_adc_error(status);}
  uint32_t status=ble_advertising_start(&r1_ble_advertising_context_a,3);
  if(status){
   RING(0x08800000,text_be284,status,remaining);SDK(2,0x001c0002,text_be2e0,status,remaining);
   r1_native_delayed_schedule(r1_connection_control_role_sync_thread_flags,0,0x66);
  }
  r1_connection_field6=UINT16_MAX;return;
 }
 case 33:{
  uint32_t rx=e[8],tx=e[9];
  RING(0x0c800000,text_53548,rx,tx);SDK(2,0x001c0003,text_53584,rx,tx);
  RING(0x0c800000,text_535b8,r1_connection_field8,r1_connection_field10);SDK(2,0x001c0003,text_535f0,r1_connection_field8,r1_connection_field10);
  if(r1_connection_field10==read16(e+4)){
   RING(0x0c400000,text_53620,read16(e+4));SDK(1,0x001c0003,text_53654,read16(e+4));
   RING(0x0c000000,text_53680);SDK(0,0x001c0003,text_536b4);
   (void)r1_connection_phy_update_plan(read16(e+4),tx,rx);
  }else{
   RING(0x0c400000,text_536e0,read16(e+4));SDK(1,0x001c0003,text_53710,read16(e+4));
   (void)r1_connection_phy_update_plan(read16(e+4),1,1);
  }
  return;
 }
 case 34:{
  uint32_t tx=e[9],rx=e[10],status=e[8];
  RING(0x0cc00000,text_bdc90,tx,rx,status);SDK(3,0x001c0003,text_bdcd8,tx,rx,status);
  if(status){RING(0x04400000,text_53750,status);SDK(1,0x001c0001,text_5377c,status);}
  else if(tx==4 || rx==4){RING(0x0c800000,text_bddb0,tx,rx);SDK(2,0x001c0003,text_bddf8,tx,rx);}
  else {RING(0x08800000,text_bde3c,tx,rx);SDK(2,0x001c0002,text_bde90,tx,rx);}
  return;
 }
 case 59:RING(0x08000000,text_537a4);SDK(0,0x001c0002,text_537c0);return;
 case 86:RING(0x08000000,text_537d8);SDK(0,0x001c0002,text_537f4);return;
 default:return;
 }
}
