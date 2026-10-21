#include <stdint.h>
#include "../board/native_battery_memory.h"
extern void *volatile r1_device_info_record_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t),r1_kv_class_write(void *,const void *,uint32_t),r1_nv_modules_idle_check(void);
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_checked(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_health_settings_get_ring[] __attribute__((section(".r1.health.settings.get_ring")))="[RING]proto settings get: health_enable:%d, settings_time:%d";
const char r1_health_settings_get_sdk[] __attribute__((section(".r1.health.settings.get_sdk")))="proto settings get: health_enable:%d, settings_time:%d";
const char r1_health_settings_set_ring[] __attribute__((section(".r1.health.settings.set_ring")))="[RING]proto settings:%d, sw_health: %d, kv:%d,%d";
const char r1_health_settings_set_sdk[] __attribute__((section(".r1.health.settings.set_sdk")))="proto settings:%d, sw_health: %d, kv:%d,%d";
__attribute__((used,noinline)) static uint32_t flag_word_get_kernel(volatile uint8_t *flag,volatile uint8_t *word,volatile uint8_t *record)
{
 uint32_t result=r1_kv_class_read(r1_device_info_record_kv_handle,(void *)(uintptr_t)record,52);
 if(flag){result=record[24]&1u;*flag=(uint8_t)result;}
 if(word){result=read32(record+32);write32(word,result);}
 return result;
}
__attribute__((naked,noinline)) uint32_t r1_kv_dev_info_flag_word_get(void *flag __attribute__((unused)),void *word __attribute__((unused)))
{__asm__ volatile("push {r4,r5,lr}\nsub sp,sp,#52\nmov r2,sp\nbl flag_word_get_kernel\nadd sp,sp,#52\npop {r4,r5,pc}");}
__attribute__((used,noinline)) static uint32_t flag0_word_set_kernel(uint32_t value,uint32_t word,volatile uint8_t *record)
{
 (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)(uintptr_t)record,52);
 uint32_t old=record[24];if((old&1u)==value)return old;
 record[24]=(old&0xfeu)|(value&1u);write32(record+32,word);
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)(uintptr_t)record,52);
 return r1_nv_modules_idle_check();
}
__attribute__((naked,noinline)) uint32_t r1_kv_dev_info_flag0_word_set(uint32_t value __attribute__((unused)),uint32_t word __attribute__((unused)))
{__asm__ volatile("push {r4,r5,r6,lr}\nsub sp,sp,#56\nmov r2,sp\nbl flag0_word_set_kernel\nadd sp,sp,#56\npop {r4,r5,r6,pc}");}
__attribute__((used,noinline)) static uint32_t health_settings_kernel(uint32_t handle,const volatile uint8_t *packet,volatile uint8_t *frame)
{
 if(!(packet[5]&2u)){
  write32(frame+24,0);write32(frame+28,0);write32(frame+32,0);
  (void)r1_kv_dev_info_flag_word_get((void *)(uintptr_t)(frame+8),(void *)(uintptr_t)(frame+20));
  write32(frame+24,read32(frame+20));frame[28]=frame[8];write32(frame+29,0);write16(frame+33,0);frame[35]=0;
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
   uint32_t word=read32(frame+20),flag=frame[8];
   (void)r1_structured_log_format(0x0c800000,r1_health_settings_get_ring,r1_health_settings_get_ring,flag,word);
  }
  if(r1_structured_log_mode_get()&2u){uint32_t flag=frame[8],word=read32(frame+20);(void)nrf_log_frontend_std_2(0x001c0003,r1_health_settings_get_sdk,flag,word);}
  return r1_protocol_send_checked(handle,14,0,read16(packet+3),(const void *)(uintptr_t)(frame+24),12);
 }
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);if(!payload)return 0;
 (void)r1_protocol_send_flag_set_c(handle,14,1,read16(packet+3),0);
 (void)r1_kv_dev_info_flag_word_get((void *)(uintptr_t)(frame+12),(void *)(uintptr_t)(frame+16));
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint32_t requested=payload[4],flag=frame[12],old_word=read32(frame+16),new_word=read32(payload);
  (void)r1_structured_log_format(0x0d000000,r1_health_settings_set_ring,r1_health_settings_set_ring,new_word,requested,flag,old_word);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t old_word=read32(frame+16),flag=frame[12],requested=payload[4],new_word=read32(payload);
  (void)nrf_log_frontend_std_4(0x001c0003,r1_health_settings_set_sdk,new_word,requested,flag,old_word);
 }
 uint32_t requested=payload[4];if(requested==frame[12])return requested;
 uint32_t word=read32(payload);(void)r1_kv_dev_info_flag0_word_set(requested!=0,word);
 return r1_event_publish(0x100d,(const void *)(uintptr_t)(payload+4),1);
}
/* Research-native body; portable planner/backing/admission remain separate. */
__attribute__((naked,noinline)) uint32_t r1_native_health_settings_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)))
{__asm__ volatile("push {r4,r5,r6,r7,r8,lr}\nsub sp,sp,#40\nmov r2,sp\nbl health_settings_kernel\nadd sp,sp,#40\npop {r4,r5,r6,r7,r8,pc}");}
