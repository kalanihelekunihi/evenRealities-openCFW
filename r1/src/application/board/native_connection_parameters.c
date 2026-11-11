/* Product-specific connection policy and packed delayed dispatch from stock.
 * Own only the observed four flag bytes; downstream providers remain separate.
 * See r1/docs/reference/connection-parameters-c-review.md. */
#include <stdint.h>
#include "ble_conn_state.h"
#include "native_battery_memory.h"
#include "native_connection_parameters.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_glasses_connection_handle_get(void),r1_phone_connection_handle_get(void);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_connection_control_delayed_event_plan(uint32_t);
volatile uint8_t r1_connection_parameter_flags[2]
 __attribute__((section(".r1.connection.parameter.flags")))={0,0};
volatile uint8_t r1_connection_parameter_fast
 __attribute__((section(".r1.connection.parameter.fast")))=0;
#define TEXT(name,text) const char r1_cp_##name[] __attribute__((section(".r1.connection.parameter.text." #name)))=text
TEXT(fast,"fast");TEXT(slow,"slow");
TEXT(connect_ring,"[RING]connect parame %d,%d is %s\r\n");
TEXT(connect_sdk,"connect parame %d,%d is %s\r\n");
TEXT(fail_ring,"[RING]conn_params update %s fail xxxxxxxxxxx\r\n");
TEXT(fail_sdk,"conn_params update %s fail xxxxxxxxxxx\r\n");
TEXT(glasses_ring,"[RING]glasses conn_params update %s ok *********\r\n");
TEXT(glasses_sdk,"glasses conn_params update %s ok *********\r\n");
TEXT(phone_ring,"[RING]phone conn_params update %s ok *********\r\n");
TEXT(phone_sdk,"phone conn_params update %s ok *********\r\n");
#undef TEXT
uint32_t r1_connection_parameters_are_fast(const volatile void *params)
{
 return read16((const volatile uint8_t *)params+2)<50;
}
static const char *speed(void)
{
 return r1_connection_parameter_fast ? r1_cp_fast:r1_cp_slow;
}
static void state_log(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,ring,ring,speed());
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(0x001c0003,sdk,(uintptr_t)speed());
}
void r1_connection_parameter_ble_observer(const ble_evt_t *event,void *context)
{
 (void)context;
 const volatile uint8_t *e=(const volatile void *)event;
 uint32_t role=ble_conn_state_role(read16(e+4));
 uint32_t id=read16(e);
 if(id==16){
  if(role!=1)return;
  r1_connection_parameter_fast=(uint8_t)r1_connection_parameters_are_fast(e+16);
  r1_connection_parameter_flags[1]=1;
  r1_connection_parameter_flags[0]=1;
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
   const char *s=speed();uint32_t maximum=read16(e+18),minimum=read16(e+16);
   (void)r1_structured_log_format(0x0cc00000,r1_cp_connect_ring,r1_cp_connect_ring,minimum,maximum,s);
  }
  if(r1_structured_log_mode_get()&2u){
   const char *s=speed();uint32_t maximum=read16(e+18),minimum=read16(e+16);
   nrf_log_frontend_std_3(0x001c0003,r1_cp_connect_sdk,minimum,maximum,(uintptr_t)s);
  }
  uint32_t minimum=read16(e+16);
  if(minimum==39){if(read16(e+18)!=39)return;}
  else if(minimum==36){if(read16(e+18)!=36)return;}
  else return;
  if(r1_connection_parameter_profile==255)r1_connection_parameter_profile=1;
  return;
 }
 if(id==17){(void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,0);return;}
 if(id!=18)return;
 volatile uint32_t copy[2];copy[0]=read32(e+8);copy[1]=read32(e+12);
 uint32_t fast=r1_connection_parameters_are_fast(copy);
 if(fast!=r1_connection_parameter_fast){
  state_log(r1_cp_fail_ring,r1_cp_fail_sdk);
  r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,
                            r1_connection_parameter_fast,fast ? 2000u:4u);
  return;
 }
 uint32_t handle=r1_glasses_connection_handle_get();
 if(handle==read16(e+4)){
  r1_connection_parameter_flags[1]=r1_connection_parameter_fast;
  state_log(r1_cp_glasses_ring,r1_cp_glasses_sdk);
 }else {
  handle=r1_phone_connection_handle_get();
  if(handle!=read16(e+4))return;
  r1_connection_parameter_flags[0]=r1_connection_parameter_fast;
  state_log(r1_cp_phone_ring,r1_cp_phone_sdk);
 }
}
extern uint32_t r1_ble_thread_message_encode(uint32_t,uint32_t,uint32_t,const void *);
extern void r1_adc_error(uint32_t);
void r1_connection_control_delayed_event_plan(uint32_t packed)
{
 uint32_t handle=packed>>16,opcode=(uint8_t)packed;
 if(handle==65535)return;
 if(opcode>2){r1_adc_error(opcode);return;}
 uint32_t command=opcode==0 ? 64u:opcode==1 ? 16u:32u;
 (void)r1_ble_thread_message_encode(handle,command,0,0);
}

/* Stock0x4dd78/0x4de44 diagnostics retain the literal backslashes. */
static const char slow_ring[]="[RING]app_ble_set_slow_mode conn_handle = %d\r\n";
static const char slow_sdk[]="app_ble_set_slow_mode conn_handle = %d\r\n";
static const char again_ring[]="[RING]app_ble_set_slow_mode_again conn_handle = %d\r\n";
static const char again_sdk[]="app_ble_set_slow_mode_again conn_handle = %d\r\n";
static const char fast_ring[]="[RING]app_ble_set_fast_mode conn_handle = %d\r\n";
static const char fast_sdk[]="app_ble_set_fast_mode conn_handle = %d\r\n";
/* Stock 0x4ca08: replace both pending parameter changes, request fast mode
 * now, then schedule the slow-mode return after 61,440 milliseconds. */
void r1_app_ble_set_fast_mode(uint32_t connection)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,fast_ring,fast_ring,connection);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(0x001c0003,fast_sdk,connection);
 uint32_t fast=1u+(connection<<16),slow=connection<<16;
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,fast);
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,slow);
 r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,fast,0u);
 r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,slow,61440u);
}
/* Stock 0x4d590: queue an immediate fast-parameter update for the connection. */
void r1_app_ble_set_fast_mode_delayed(uint32_t connection)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,fast_ring,fast_ring,connection);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,fast_sdk,connection);
 uint32_t packed=1u+(connection<<16);
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,packed);
 r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,packed,0u);
}
void r1_app_ble_set_slow_mode(uint32_t connection,uint32_t immediate)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,slow_ring,slow_ring,connection);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,slow_sdk,connection);
 uint32_t packed=connection<<16;
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,packed);
 r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,packed,immediate?0u:0x2800u);
}
void r1_app_ble_set_slow_mode_again(uint32_t connection)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,again_ring,again_ring,connection);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,again_sdk,connection);
 uint32_t packed=connection<<16;
 (void)r1_native_delayed_cancel(r1_connection_control_delayed_event_plan,packed);
 r1_native_delayed_schedule(r1_connection_control_delayed_event_plan,packed,0x2c00u);
}
/* Stock0x9917a/0x99192. The middle two records already belong to the GAP
 * preferred-parameter array at0x99182 and are reused rather than copied. */
const ble_gap_conn_params_t r1_connection_slow_parameters={72,84,4,600};
const ble_gap_conn_params_t r1_connection_glasses_parameters={16,16,2,600};
_Static_assert(sizeof(ble_gap_conn_params_t)==8,"native four-halfword parameters");
/* Stock0x4d4ac. SDK declarations retain the S140 supervisor-call gateway.
 * Error logging returns; only the nativeffff setup status aborts this path. */
void r1_connection_parameter_mode_adapter(uint32_t connection,uint32_t mode)
{
 if(connection==65535u)return;
 if(r1_phone_connection_handle_get()==connection && r1_connection_parameter_flags[0]==mode)return;
 uint32_t status;
 if(mode==2u){
  if(r1_glasses_connection_handle_get()==connection && r1_connection_parameter_flags[1]==1u)return;
  status=sd_ble_gap_ppcp_set(&r1_connection_glasses_parameters);
  if(status){r1_adc_error(status);if(status==65535u)return;}
  r1_connection_parameter_fast=1;
  status=sd_ble_gap_conn_param_update((uint16_t)connection,&r1_connection_glasses_parameters);
  if(status && status!=17u)r1_adc_error(status);
 }else if(mode==1u){
  const ble_gap_conn_params_t *parameters=&r1_gap_preferred_parameter_profiles[r1_connection_parameter_profile!=0];
  status=sd_ble_gap_ppcp_set(parameters);
  if(status && status!=17u){r1_adc_error(status);if(status==65535u)return;}
  r1_connection_parameter_fast=1;
  parameters=&r1_gap_preferred_parameter_profiles[r1_connection_parameter_profile!=0];
  status=sd_ble_gap_conn_param_update((uint16_t)connection,parameters);
  if(status && status!=17u)r1_adc_error(status);
 }else{
  status=sd_ble_gap_ppcp_set(&r1_connection_slow_parameters);
  if(status){r1_adc_error(status);if(status==65535u)return;}
  r1_connection_parameter_fast=0;
  status=sd_ble_gap_conn_param_update((uint16_t)connection,&r1_connection_slow_parameters);
  if(status)r1_adc_error(status);
 }
}
/* The single flag at0x200064f8 is shared by the native getter/setter. */
volatile uint8_t r1_ble_control_flag __attribute__((section(".r1.ble.control_flag")))=0;
uint32_t r1_ble_control_flag_get(void){return r1_ble_control_flag;}
uint32_t r1_ble_control_flag_set(uint32_t value){r1_ble_control_flag=(uint8_t)value;return value;}
