/* Native observer differs from SDK ble_dfu.c in disconnect selection and
 * connection stores before authorization/HVC handling. SDK type/helper reused;
 * initialization and backend control-point/boot preparation stay real gates. */
#include <stdint.h>
#include <stddef.h>
#define SVCALL_AS_NORMAL_FUNCTION
#include "ble.h"
#include "ble_dfu.h"
#include "ble_srv_common.h"
volatile ble_dfu_buttonless_t r1_ble_dfu_context __attribute__((section(".r1.dfu.context"),aligned(4)))={0};
const uint32_t r1_dfu_value_seed __attribute__((section(".r1.dfu.value_seed")))=2;
_Static_assert(sizeof(ble_dfu_buttonless_t)==28 && offsetof(ble_dfu_buttonless_t,conn_handle)==4 && offsetof(ble_dfu_buttonless_t,control_point_char)==6 && offsetof(ble_dfu_buttonless_t,evt_handler)==20 && offsetof(ble_dfu_buttonless_t,is_waiting_for_reset)==24,"native DFU context");
_Static_assert(SD_BLE_GATTS_VALUE_GET==173 && SD_BLE_GATTS_RW_AUTHORIZE_REPLY==176,"native GATTS SVC IDs");
extern uint32_t r1_glasses_connection_handle_get(void);
extern uint32_t r1_dfu_bootloader_prepare_boundary(void),r1_dfu_control_point_write_boundary(const void *);
__attribute__((naked,noinline)) uint32_t r1_dfu_value_get(uint32_t c __attribute__((unused)),uint32_t h __attribute__((unused)),void *v __attribute__((unused))) {__asm__ volatile("svc %0\nbx lr"::"I"(SD_BLE_GATTS_VALUE_GET):"r0","memory");}
__attribute__((naked,noinline)) uint32_t r1_dfu_authorize_reply(uint32_t c __attribute__((unused)),const void *r __attribute__((unused))) {__asm__ volatile("svc %0\nbx lr"::"I"(SD_BLE_GATTS_RW_AUTHORIZE_REPLY):"r0","memory");}
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
__attribute__((naked,noinline)) uint32_t r1_native_dfu_ctrlpt_authorize(const void *write __attribute__((unused))){__asm__ volatile("push {r4,r5,r6,lr}\nsub sp,sp,#32\nmov r1,sp\nbl authorize_kernel\nadd sp,sp,#32\npop {r4,r5,r6,pc}");}
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
