#include <stdint.h>
#define SVCALL_AS_NORMAL_FUNCTION
#include "nrf_soc.h"
#include "../board/native_battery_memory.h"
extern void *volatile r1_device_info_record_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t),r1_kv_class_write(void *,const void *,uint32_t);
extern uint32_t r1_nv_modules_idle_check(void);
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_checked(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
_Static_assert(SD_POWER_DCDC_MODE_SET==63,"authenticated native regulator SVC");
__attribute__((naked,noinline)) uint32_t r1_system_settings_dcdc_request(uint32_t mode __attribute__((unused)))
{__asm__ volatile("svc %0\nbx lr"::"I"(SD_POWER_DCDC_MODE_SET):"r0","memory");}
const char r1_settings_get_ring[] __attribute__((section(".r1.settings.get_ring")))="[RING]proto settings get: sw dcdc:%d";
const char r1_settings_get_sdk[] __attribute__((section(".r1.settings.get_sdk")))="proto settings get: sw dcdc:%d";
const char r1_settings_set_ring[] __attribute__((section(".r1.settings.set_ring")))="[RING]proto settings set: sw type:%d, sw status:%d";
const char r1_settings_set_sdk[] __attribute__((section(".r1.settings.set_sdk")))="proto settings set: sw type:%d, sw status:%d";
__attribute__((used,noinline)) static uint32_t bit_get_kernel(volatile uint8_t *destination,volatile uint8_t *record)
{
 uint32_t result=r1_kv_class_read(r1_device_info_record_kv_handle,(void *)(uintptr_t)record,52);
 if(destination){result=(record[24]>>1)&1u;*destination=(uint8_t)result;}
 return result;
}
__attribute__((naked,noinline)) uint32_t r1_kv_dev_info_bit_get(void *destination __attribute__((unused)))
{__asm__ volatile("push {r4,lr}\nsub sp,sp,#56\nmov r1,sp\nbl bit_get_kernel\nadd sp,sp,#56\npop {r4,pc}");}
__attribute__((used,noinline)) static uint32_t bit1_set_kernel(uint32_t value,volatile uint8_t *record)
{
 (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)(uintptr_t)record,52);
 record[24]=(record[24]&0xfdu)|((value&1u)<<1);
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)(uintptr_t)record,52);
 return r1_nv_modules_idle_check();
}
__attribute__((naked,noinline)) uint32_t r1_kv_dev_info_bit1_set(uint32_t value __attribute__((unused)))
{__asm__ volatile("push {r4,r5,lr}\nsub sp,sp,#52\nmov r1,sp\nbl bit1_set_kernel\nadd sp,sp,#52\npop {r4,r5,pc}");}
__attribute__((used,noinline)) static uint32_t settings_kernel(uint32_t handle,const volatile uint8_t *packet,volatile uint8_t *frame)
{
 if(!(packet[5]&2u)){
  (void)r1_kv_dev_info_bit_get((void *)(uintptr_t)(frame+8));
  write32(frame+16,0);uint32_t saved=frame[8];write32(frame+12,0);write32(frame+20,0);
  frame[17]=(uint8_t)saved;write32(frame+18,0);write16(frame+22,0);
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x0c400000,r1_settings_get_ring,r1_settings_get_ring,frame[8]);
  if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_settings_get_sdk,frame[8]);
  return r1_protocol_send_checked(handle,15,0,read16(packet+3),(const void *)(uintptr_t)(frame+12),12);
 }
 (void)r1_protocol_send_flag_set_c(handle,15,1,read16(packet+3),0);
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);
 if(!payload)return 0;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint32_t status=payload[5],type=payload[4];
  (void)r1_structured_log_format(0x0c800000,r1_settings_set_ring,r1_settings_set_ring,type,status);
 }
 if(r1_structured_log_mode_get()&2u){uint32_t status=payload[5],type=payload[4];(void)nrf_log_frontend_std_2(0x001c0003,r1_settings_set_sdk,type,status);}
 uint32_t type=payload[4];if(type)return type;
 (void)r1_kv_dev_info_bit_get((void *)(uintptr_t)(frame+8));
 uint32_t requested=payload[5];if(requested==frame[8])return requested;
 (void)r1_kv_dev_info_bit1_set(requested!=0);
 return r1_system_settings_dcdc_request(payload[5]!=0);
}
/* Research-native interface; bounded portable planner and admission are separate. */
__attribute__((naked,noinline)) uint32_t r1_native_system_settings_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)))
{__asm__ volatile("push {r4,r5,r6,r7,lr}\nsub sp,sp,#28\nmov r2,sp\nbl settings_kernel\nadd sp,sp,#28\npop {r4,r5,r6,r7,pc}");}
