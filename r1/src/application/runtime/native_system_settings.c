#include <stdint.h>
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
__attribute__((noinline)) uint32_t r1_system_settings_dcdc_request(uint32_t mode)
{return sd_power_dcdc_mode_set((uint8_t)mode);}
const char r1_settings_get_ring[] __attribute__((section(".r1.settings.get_ring")))="[RING]proto settings get: sw dcdc:%d";
const char r1_settings_get_sdk[] __attribute__((section(".r1.settings.get_sdk")))="proto settings get: sw dcdc:%d";
const char r1_settings_set_ring[] __attribute__((section(".r1.settings.set_ring")))="[RING]proto settings set: sw type:%d, sw status:%d";
const char r1_settings_set_sdk[] __attribute__((section(".r1.settings.set_sdk")))="proto settings set: sw type:%d, sw status:%d";
uint32_t r1_kv_dev_info_bit_get(void *destination)
{
 uint8_t record[52]={0};
 uint32_t result=r1_kv_class_read(r1_device_info_record_kv_handle,record,52);
 if(destination){uint8_t value=result?0:(record[24]>>1)&1u;*(uint8_t *)destination=value;return value;}
 return result;
}
uint32_t r1_kv_dev_info_bit1_set(uint32_t value)
{
 uint8_t record[52]={0};
 uint32_t result=r1_kv_class_read(r1_device_info_record_kv_handle,record,52);
 if(result)return result;
 record[24]=(uint8_t)((record[24]&0xfdu)|((value&1u)<<1));
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,record,52);
 return r1_nv_modules_idle_check();
}
uint32_t r1_system_settings_plan_command(uint32_t handle,const void *input,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;
 const volatile uint8_t *packet=input;
 if(!(packet[5]&2u)){
  uint8_t setting=0,response[12]={0};
  (void)r1_kv_dev_info_bit_get(&setting);response[5]=setting;
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x0c400000,r1_settings_get_ring,r1_settings_get_ring,setting);
  if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_settings_get_sdk,setting);
  return r1_protocol_send_checked(handle,15,0,read16(packet+3),response,12);
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
 uint8_t setting=0;
 (void)r1_kv_dev_info_bit_get(&setting);
 uint32_t requested=payload[5];if(requested==setting)return requested;
 (void)r1_kv_dev_info_bit1_set(requested!=0);
 return r1_system_settings_dcdc_request(payload[5]!=0);
}
extern __typeof__(r1_system_settings_plan_command) r1_native_system_settings_handler
 __attribute__((alias("r1_system_settings_plan_command")));
