/* Recovered native backend policy. The already compiled SDK SVCI state is
 * shared; backend and canonical service contexts deliberately remain distinct. */
#include <stdint.h>
#include <stddef.h>
#define SVCALL_AS_NORMAL_FUNCTION
#include "ble.h"
#include "ble_dfu.h"
#include "nrf_soc.h"
#include "nrf_pwr_mgmt.h"
#include "nrf_dfu_ble_svci_bond_sharing.h"
extern volatile ble_dfu_buttonless_t r1_ble_dfu_context;
extern nrf_dfu_set_adv_name_svci_async_t nrf_dfu_set_adv_name_svci_async_def;
volatile ble_dfu_buttonless_t *volatile r1_dfu_backend_context __attribute__((section(".r1.dfu.backend_context"),aligned(4)))=0;
nrf_dfu_adv_name_t r1_dfu_adv_name __attribute__((section(".r1.dfu.adv_name"),aligned(4)))={0};
_Static_assert(sizeof(nrf_dfu_adv_name_t)==28 && offsetof(nrf_dfu_adv_name_t,name)==4 && offsetof(nrf_dfu_adv_name_t,len)==24,"native adv name");
_Static_assert(sizeof(nrf_dfu_set_adv_name_svci_async_t)==12 && offsetof(nrf_dfu_set_adv_name_svci_async_t,state)==8,"shared native SVCI state");
_Static_assert(SD_BLE_GATTS_HVX==174 && SD_POWER_GPREGRET_CLR==61 && SD_POWER_GPREGRET_SET==60 && NRF_PWR_MGMT_SHUTDOWN_GOTO_DFU==2,"native SDK operations");
extern void *memcpy(void *,const void *,size_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
const char r1_dfu_protected_ring[] __attribute__((section(".r1.dfu.protected_ring")))="[RING]The bootloader has write protected its settings page. This prohibits setting the advertising name. The bootloader must be compiled with NRF_BL_SETTINGS_PAGE_PROTECT=0 to allow setting the advertising name.";
const char r1_dfu_protected_sdk[] __attribute__((section(".r1.dfu.protected_sdk")))="The bootloader has write protected its settings page. This prohibits setting the advertising name. The bootloader must be compiled with NRF_BL_SETTINGS_PAGE_PROTECT=0 to allow setting the advertising name.";
static volatile uint8_t *backend_bytes(void){return (volatile uint8_t *)r1_dfu_backend_context;}
static uint32_t backend_event(uint32_t event){return ((uint32_t (*)(uint32_t))(uintptr_t)r1_dfu_backend_context->evt_handler)(event);}
__attribute__((naked,noinline)) uint32_t r1_dfu_hvx(uint32_t c __attribute__((unused)),const void *p __attribute__((unused))){__asm__ volatile("svc %0\nbx lr"::"I"(SD_BLE_GATTS_HVX):"r0","memory");}
__attribute__((naked,noinline)) uint32_t r1_dfu_gpregret_clear(uint32_t i __attribute__((unused)),uint32_t m __attribute__((unused))){__asm__ volatile("svc %0\nbx lr"::"I"(SD_POWER_GPREGRET_CLR):"r0","memory");}
__attribute__((naked,noinline)) uint32_t r1_dfu_gpregret_set(uint32_t i __attribute__((unused)),uint32_t m __attribute__((unused))){__asm__ volatile("svc %0\nbx lr"::"I"(SD_POWER_GPREGRET_SET):"r0","memory");}
__attribute__((used,noinline)) static uint32_t response_kernel(uint32_t opcode,uint32_t response,volatile uint32_t *frame){
 volatile uint8_t *bytes=(volatile uint8_t *)frame;
 bytes[0]=3;bytes[1]=0; /* high halfword and byte23 retain caller history */
 bytes[20]=0x20;bytes[21]=(uint8_t)opcode;frame[1]=0;frame[2]=0;bytes[22]=(uint8_t)response;
 uint32_t handle=r1_ble_dfu_context.control_point_char.value_handle;
 bytes[4]=(uint8_t)handle;bytes[5]=(uint8_t)(handle>>8);bytes[6]=2;
 frame[4]=(uintptr_t)(bytes+20);frame[3]=(uintptr_t)frame;
 uint32_t result=r1_dfu_hvx(r1_ble_dfu_context.conn_handle,(const void *)(uintptr_t)(bytes+4));
 if(!result && (bytes[0]|((uint32_t)bytes[1]<<8))!=3)return 12;
 return result;
}
__attribute__((naked,noinline)) uint32_t r1_native_dfu_response(uint32_t o __attribute__((unused)),uint32_t r __attribute__((unused))){__asm__ volatile("sub sp,sp,#24\nmov r2,sp\npush {r4,lr}\nbl response_kernel\npop {r4,lr}\nadd sp,sp,#24\nbx lr");}
uint32_t r1_native_dfu_finalize(void){
 uint32_t result=r1_dfu_gpregret_clear(0,0xffffffff);if(result)return result;
 result=r1_dfu_gpregret_set(0,0xb1);if(result)return result;
 (void)((uint32_t (*)(uint32_t))(uintptr_t)r1_ble_dfu_context.evt_handler)(1);
 nrf_pwr_mgmt_shutdown(NRF_PWR_MGMT_SHUTDOWN_GOTO_DFU);return 0;
}
uint32_t r1_dfu_bootloader_prepare_boundary(void){(void)backend_event(0);return r1_native_dfu_finalize();}
uint32_t r1_native_dfu_set_adv_name(nrf_dfu_adv_name_t *name){
 if(backend_bytes()[25])return 6;
 volatile nrf_dfu_set_adv_name_svci_async_t *state=&nrf_dfu_set_adv_name_svci_async_def;
 uint32_t result=state->async_func(name,(nrf_dfu_set_adv_name_state_t *)&state->state);
 if(!result)backend_bytes()[25]=1;
 else if(result==15){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))(void)r1_structured_log_format(0x04000000,r1_dfu_protected_ring,r1_dfu_protected_ring);
  if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0001,r1_dfu_protected_sdk);
 }
 return result;
}
__attribute__((used,noinline)) static uint32_t control_kernel(const volatile uint8_t *write,volatile uint32_t *frame){
 uint32_t opcode=write[12],response=4,result;
 if(opcode==1){
  if(backend_bytes()[25]){
   result=response_kernel(1,6,frame);if(result)return backend_event(3);return 0;
  }
  backend_bytes()[24]=1;result=response_kernel(1,1,frame);if(!result)return 0;
  backend_bytes()[24]=0;if(result==17)response=6;
 }else if(opcode==2){
  uint32_t length=write[13];
  if(!length || length>20)response=5;
  else {
   (void)memcpy(r1_dfu_adv_name.name,(const void *)(uintptr_t)(write+14),length);
   r1_dfu_adv_name.len=write[13];result=r1_native_dfu_set_adv_name(&r1_dfu_adv_name);if(!result)return 0;
  }
 }else response=2;
 result=response_kernel(write[12],response,frame);if(result)(void)backend_event(3);
 return backend_event(2);
}
__attribute__((naked,noinline)) uint32_t r1_dfu_control_point_write_boundary(const void *write __attribute__((unused))){__asm__ volatile("push {r4,r5,r6,r7,r8,lr}\nmov r4,r0\nsub sp,sp,#24\nmov r1,sp\nbl control_kernel\nadd sp,sp,#24\npop {r4,r5,r6,r7,r8,pc}");}
__attribute__((used,noinline)) static uint32_t sys_kernel(uint32_t event,volatile uint32_t *frame){
 volatile nrf_dfu_set_adv_name_svci_async_t *state=&nrf_dfu_set_adv_name_svci_async_def;
 if(!state->async_func)return event;
 nrf_dfu_set_adv_name_event_fn_t handler=state->sys_evt_handler;if(!handler)return event;
 uint32_t result=handler(event,(nrf_dfu_set_adv_name_state_t *)&state->state);if(result==8)return result;
 backend_bytes()[25]=0;
 if(result){uint32_t sent=response_kernel(2,6,frame);if(sent)(void)backend_event(3);return backend_event(2);}
 result=response_kernel(2,1,frame);if(result)return backend_event(3);return 0;
}
__attribute__((naked,noinline)) uint32_t r1_native_dfu_on_sys_evt(uint32_t event __attribute__((unused)),uintptr_t ignored __attribute__((unused))){__asm__ volatile("push {r4,r5,r6,lr}\nsub sp,sp,#24\nmov r1,sp\nbl sys_kernel\nadd sp,sp,#24\npop {r4,r5,r6,pc}");}
