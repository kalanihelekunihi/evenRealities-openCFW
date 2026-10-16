#include <stdint.h>
#include <string.h>
#include "../board/native_battery_memory.h"
extern void __aeabi_memclr(void *,uint32_t);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
/* Native6ab88 has cached-pointer/length and SVC109/FICR/formatter branches.
 * The bounded frozen GoMore helper is not the same raw ABI. */
extern void r1_native_device_id_read_boundary(void *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
/* One authenticated byte only: eventual owner of20006da0 must alias this field. */
volatile uint8_t r1_device_id_once_status __attribute__((section(".r1.device.id.status")))=0;
const uint8_t r1_device_id_default[28] __attribute__((section(".r1.device.id.default")))={1};
const char r1_device_id_ring[] __attribute__((section(".r1.device.id.ring")))="[RING]sta:%d, devid:%s";
const char r1_device_id_sdk[] __attribute__((section(".r1.device.id.sdk")))="sta:%d, devid:%s";
__attribute__((noinline)) uint32_t r1_device_id_status_get(void){return r1_device_id_once_status;}
__attribute__((used,noinline)) static uint32_t status_clear_kernel(void){r1_device_id_once_status=0;return 0;}
/* Native setter changes neither r2 nor r3. Retain those words across the C
 * store even when this compiler uses r2 to materialize zero. */
__attribute__((naked,noinline)) uint32_t r1_device_id_status_clear(void)
{__asm__ volatile("push {r2,r3,r4,lr}\nbl status_clear_kernel\npop {r2,r3,r4,pc}");}
__attribute__((used,noinline)) static uint32_t op11_kernel(const void *payload,uint32_t first,uint32_t second,volatile uint32_t *frame)
{
 if(!payload)return 0;
 uint32_t handle=r1_phone_connection_handle_get();frame[0]=(uintptr_t)payload;frame[1]=25;
 return r1_protocol_response_send_0x100(handle,11,first,second,payload,25);
}
__attribute__((naked,noinline)) uint32_t r1_phone_cmd_send_op11(const void *payload __attribute__((unused)),uint32_t first __attribute__((unused)),uint32_t second __attribute__((unused)))
{__asm__ volatile("push {r2,r3,r4,r5,r6,lr}\nmov r3,sp\nbl op11_kernel\npop {r2,r3,r4,r5,r6,pc}");}
__attribute__((used,noinline)) static uint32_t device_id_kernel(const volatile uint8_t *packet,volatile uint8_t *frame)
{
 volatile uint8_t *response=frame+4,*id=frame+32;
 (void)memcpy((void *)(uintptr_t)response,r1_device_id_default,28);
 if(r1_device_id_status_get()==1){response[0]=1;(void)r1_device_id_status_clear();}else response[0]=0;
 __aeabi_memclr((void *)(uintptr_t)id,28);
 r1_native_device_id_read_boundary((void *)(uintptr_t)id);
 (void)memcpy((void *)(uintptr_t)(response+1),(const void *)(uintptr_t)id,24);
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c800000,r1_device_id_ring,r1_device_id_ring,response[0],(const void *)(uintptr_t)id);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_2(0x001c0003,r1_device_id_sdk,response[0],(uintptr_t)id);
 return r1_phone_cmd_send_op11((const void *)(uintptr_t)response,0,read16(packet+3));
}
__attribute__((naked,noinline)) uint32_t r1_protocol_command_00083e50(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)),uintptr_t scratch __attribute__((unused)),uint32_t seed __attribute__((unused)))
{__asm__ volatile("push {r4,lr}\nsub sp,sp,#64\nmov r0,r1\nmov r1,sp\nbl device_id_kernel\nadd sp,sp,#64\npop {r4,pc}");}
