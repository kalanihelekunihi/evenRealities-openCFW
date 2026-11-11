/* Stock glasses wear/display policy and its deferred hardware callbacks.
 * State bytes0x20006c37/38 belong to the existing factory-state owner. */
#include <stdint.h>
#include "nrf_soc.h"
#include "native_connection_parameters.h"
#include "../runtime/native_factory_mode.h"
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_service_touch_open(uint32_t),r1_service_touch_close(uint32_t);
extern uint32_t r1_kv_dev_info_bit_get(void *),r1_glasses_connection_handle_get(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern void r1_connection_control_delayed_event_plan(uint32_t);
_Static_assert(SD_POWER_DCDC_MODE_SET==0x3f,"native DC/DC SVC");
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
#define SDK(n,text,...) do {if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_##n(0x001c0003,text,##__VA_ARGS__);}while(0)
static const char text_6a6a8[]="[RING]glasses_dcdc_deferred_enable_cb: enable dcdc";
static const char text_6a6e4[]="glasses_dcdc_deferred_enable_cb: enable dcdc";
static const char text_6aa1c[]="[RING]glasses_touch_close_deferred_cb: close touch";
static const char text_6aa50[]="glasses_touch_close_deferred_cb: close touch";
static const char text_c0424[]="[RING]glasses_touch_close_deferred_cb: skip close, wear_status=%d";
static const char text_6aa84[]="glasses_touch_close_deferred_cb: skip close, wear_status=%d";
static const char text_c03e0[]="[RING]glasses_status_cmd: glass_wear_status=%d, glass_lcd_status=%d";
static const char text_6a87c[]="glasses_status_cmd: glass_wear_status=%d, glass_lcd_status=%d";
static const char text_6a8c8[]="[RING]glasses_status_cmd: disable dcdc";
static const char text_6a8f0[]="glasses_status_cmd: disable dcdc";
static const char text_6a914[]="[RING]glasses_status_cmd: enable dcdc";
static const char text_6a93c[]="glasses_status_cmd: enable dcdc";
static const char text_4e0ec[]="[RING]touch_set_fast_mode conn_handle = %d\r\n";
static const char text_4e124[]="touch_set_fast_mode conn_handle = %d\r\n";

/* Native0x6a668. The scheduled argument is ignored. */
void r1_factory_status_timeout_6a668(uint32_t argument)
{
 (void)argument;
 RING(0x0c000000,text_6a6a8);SDK(0,text_6a6e4);
 (void)sd_power_dcdc_mode_set(1);
}
/* Native0x6a988. Decide before diagnostics; nonzero diagnostics reload signed. */
void r1_factory_status_timeout_6a988(uint32_t argument)
{
 (void)argument;
 if(r1_factory_mode_state.reserved[2]==0){
  RING(0x0c000000,text_6aa1c);SDK(0,text_6aa50);
  (void)r1_service_touch_close(0);
 }else{
  RING(0x0c400000,text_c0424,(int32_t)(int8_t)r1_factory_mode_state.reserved[2]);
  SDK(1,text_6aa84,(int32_t)(int8_t)r1_factory_mode_state.reserved[2]);
 }
}
/* Native0x4e070: use existing observer flag byte, preserve callback packing. */
void r1_touch_set_fast_mode(uint32_t connection)
{
 r1_connection_parameter_flags[1]=0;
 RING(0x0c400000,text_4e0ec,connection);SDK(1,text_4e124,connection);
 uint32_t packed=connection<<16;
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,packed);
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,packed+1u);
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,packed+2u);
 r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,packed+2u,0);
}
/* Native0x6a714: the original seven-byte record is also the reply buffer. */
uint32_t r1_glasses_status_plan_command(uint32_t connection,volatile uint8_t *packet)
{
 (void)connection;
 if(packet[3]==1){
  uint32_t bits=packet[4],wear=bits>>7,display=(bits>>6)&1u;
  packet[4]=1;
  RING(0x0c800000,text_c03e0,wear,display);SDK(2,text_6a87c,wear,display);
  if((int32_t)(int8_t)r1_factory_mode_state.reserved[2]!=(int32_t)wear){
   r1_factory_mode_state.reserved[2]=(uint8_t)wear;
   uint8_t setting=0;
   (void)r1_kv_dev_info_bit_get(&setting);
   if(wear){
    (void)r1_native_delayed_cancel(r1_factory_status_timeout_6a988,0);
    (void)r1_service_touch_open(0);
    if(!setting){
     (void)r1_native_delayed_cancel(r1_factory_status_timeout_6a668,0);
     RING(0x0c000000,text_6a8c8);SDK(0,text_6a8f0);
     (void)sd_power_dcdc_mode_set(0);
    }
   }else{
    (void)r1_native_delayed_cancel(r1_factory_status_timeout_6a988,0);
    r1_native_delayed_schedule(r1_factory_status_timeout_6a988,0,0x96000);
    if(!setting){
     (void)r1_native_delayed_cancel(r1_factory_status_timeout_6a668,0);
     RING(0x0c000000,text_6a914);SDK(0,text_6a93c);
     r1_native_delayed_schedule(r1_factory_status_timeout_6a668,0,0x7800);
    }
   }
  }
  if((int32_t)(int8_t)r1_factory_mode_state.reserved[3]!=(int32_t)display){
   r1_factory_mode_state.reserved[3]=(uint8_t)display;
   uint32_t handle=r1_glasses_connection_handle_get();
   if(display)r1_touch_set_fast_mode(handle);
   else r1_app_ble_set_slow_mode(handle,0);
  }
 }
 return r1_legacy_bounded_reply_send((const void *)(uintptr_t)packet,7);
}
