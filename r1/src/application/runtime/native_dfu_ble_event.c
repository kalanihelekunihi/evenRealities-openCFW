/* Native observer differs from SDK ble_dfu.c in disconnect selection and
 * connection stores before authorization/HVC handling. SDK type/helper reused;
 * initialization and backend control-point/boot preparation stay real gates. */
#include <stdint.h>
#include <stddef.h>
#include "ble.h"
#include "ble_dfu.h"
#include "ble_srv_common.h"
volatile ble_dfu_buttonless_t r1_ble_dfu_context __attribute__((section(".r1.dfu.context"),aligned(4)))={0};
const uint32_t r1_dfu_value_seed __attribute__((section(".r1.dfu.value_seed")))=2;
_Static_assert(sizeof(ble_dfu_buttonless_t)==28 && offsetof(ble_dfu_buttonless_t,conn_handle)==4 && offsetof(ble_dfu_buttonless_t,control_point_char)==6 && offsetof(ble_dfu_buttonless_t,evt_handler)==20 && offsetof(ble_dfu_buttonless_t,is_waiting_for_reset)==24,"native DFU context");
_Static_assert(SD_BLE_GATTS_VALUE_GET==173 && SD_BLE_GATTS_RW_AUTHORIZE_REPLY==176,"native GATTS SVC IDs");
extern uint32_t r1_glasses_connection_handle_get(void);
extern uint32_t r1_dfu_bootloader_prepare_boundary(void),r1_dfu_control_point_write_boundary(const void *);
/* Pinned SDK C declarations own the GATTS supervisor-call ABI. */
__attribute__((noinline)) uint32_t r1_dfu_value_get(uint32_t connection,uint32_t handle,void *value)
{return sd_ble_gatts_value_get((uint16_t)connection,(uint16_t)handle,(ble_gatts_value_t *)value);}
__attribute__((noinline)) uint32_t r1_dfu_authorize_reply(uint32_t connection,const void *reply)
{return sd_ble_gatts_rw_authorize_reply((uint16_t)connection,(const ble_gatts_rw_authorize_reply_params_t *)reply);}
_Static_assert(sizeof(ble_gatts_value_t)==8 && offsetof(ble_gatts_value_t,len)==0 &&
 offsetof(ble_gatts_value_t,offset)==2 && offsetof(ble_gatts_value_t,p_value)==4,"native GATTS value frame");
_Static_assert(sizeof(ble_gatts_rw_authorize_reply_params_t)==16 &&
 offsetof(ble_gatts_rw_authorize_reply_params_t,params)==4 &&
 offsetof(ble_dfu_buttonless_t,control_point_char.cccd_handle)==10,"native authorization frame");
static uint32_t read16(const volatile uint8_t *p){return p[0]|((uint32_t)p[1]<<8);}
__attribute__((used,noinline)) static uint32_t authorize_kernel(const void *write,volatile uint32_t *frame){
 frame[0]=2;frame[1]=0;frame[2]=0;frame[3]=0;
 frame[4]=r1_dfu_value_seed;frame[5]=(uintptr_t)((volatile uint8_t *)frame+28);
 uint32_t result=r1_dfu_value_get(r1_ble_dfu_context.conn_handle,r1_ble_dfu_context.control_point_char.cccd_handle,(void *)(uintptr_t)(frame+4));
 volatile uint8_t *bytes=(volatile uint8_t *)frame;
 if(!result && ble_srv_is_indication_enabled((const uint8_t *)(uintptr_t)(bytes+28))){bytes[6]=1;bytes[4]=0;bytes[5]=0;}
 else {bytes[4]=0xfd;bytes[5]=1;}
 do {result=r1_dfu_authorize_reply(r1_ble_dfu_context.conn_handle,(const void *)(uintptr_t)frame);}while(result==17);
 uint32_t status=read16(bytes+4);
 if(status)return status;
 return r1_dfu_control_point_write_boundary(write);
}
__attribute__((noinline)) uint32_t r1_native_dfu_ctrlpt_authorize(const void *write){
 /* Match the native frame's address relative to entry SP. Clang saves two
  * registers here; the remaining ten words keep the frame at entry SP-48. */
 volatile uint32_t frame[10];
 return authorize_kernel(write,frame);
}
uint32_t r1_native_dfu_ble_event(const volatile uint8_t *event,uintptr_t ignored){
 (void)ignored;if(!event)return 0;
 uint32_t id=read16(event);
 if(id==16){uint32_t conn=read16(event+4);r1_ble_dfu_context.conn_handle=(uint16_t)conn;return conn;}
 if(id==17){uint32_t conn=r1_glasses_connection_handle_get();if(conn==r1_ble_dfu_context.conn_handle)return conn;r1_ble_dfu_context.conn_handle=0xffff;return 0xffff;}
 uint32_t value=r1_ble_dfu_context.control_point_char.value_handle;
 if(id==83){
  if(read16(event+6)!=value)return (uintptr_t)event;
  r1_ble_dfu_context.conn_handle=(uint16_t)read16(event+4);
  uint32_t waiting=((const volatile uint8_t *)&r1_ble_dfu_context)[24];
  if(!waiting)return 0;
  uint32_t result=r1_dfu_bootloader_prepare_boundary();if(!result)return 0;
  return ((uint32_t (*)(uint32_t))(uintptr_t)r1_ble_dfu_context.evt_handler)(2);
 }
 if(id==81){
  r1_ble_dfu_context.conn_handle=(uint16_t)read16(event+4);
  const volatile uint8_t *auth=event+6;
  if(auth[0]!=2 || read16(auth+2)!=value)return (uintptr_t)auth;
  uint32_t op=auth[8];if(op==4 || op==5 || op==6)return (uintptr_t)auth;
  return r1_native_dfu_ctrlpt_authorize((const void *)(uintptr_t)(auth+2));
 }
 return (uintptr_t)event;
}
