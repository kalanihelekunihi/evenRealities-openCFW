#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_health_storage_hour_index(uint32_t),r1_health_storage_average(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern const char r1_health_storage_stress_text[];
/* Symbolic native sample storage; bounded cold-zero prefixes are not full contexts. */
uint8_t r1_health_storage_hr_prefix[80] __attribute__((aligned(1),section(".r1.health.storage.hr")))={0};
/* Stock 0x5ad90. HR sample storage uses the shared cache owner. */
void r1_hr_event_storage(const volatile uint8_t *sample)
{
 if(!sample)return;
 uint32_t timestamp=read32(sample+1);
 uint32_t hour=r1_health_storage_hour_index(timestamp);
 timestamp=read32(sample+1);uint32_t value=sample[0];
 uint32_t average=r1_health_storage_average(0,value,timestamp);
 volatile uint8_t *base=r1_health_storage_hr_prefix;
 volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)base+hour*3u);
 value=sample[0];uint32_t maximum=entry[1];
 if(value>maximum)entry[1]=(uint8_t)value;
 value=sample[0];uint32_t minimum=entry[2];
 if(value<minimum || !minimum)entry[2]=(uint8_t)value;
 entry[0]=(uint8_t)average;
 write32(base+75,read32(sample));base[79]=sample[4];
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  timestamp=read32(sample+1);value=sample[0];
  (void)r1_structured_log_format(0x0c800000,"[RING]last_hr: %d, timestamp: %d","[RING]last_hr: %d, timestamp: %d",value,timestamp);
 }
 if(r1_structured_log_mode_get()&2u){
  timestamp=read32(sample+1);value=sample[0];
  nrf_log_frontend_std_2(0x001c0003,"last_hr: %d, timestamp: %d",value,timestamp);
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  (void)r1_structured_log_format(0x0d000000,"[RING]hr: %d, avg_hr: %d, max_hr: %d, min_hr: %d","[RING]hr: %d, avg_hr: %d, max_hr: %d, min_hr: %d",value,average,maximum,minimum);
 }
 if(r1_structured_log_mode_get()&2u){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  nrf_log_frontend_std_4(0x001c0003,"hr: %d, avg_hr: %d, max_hr: %d, min_hr: %d",value,average,maximum,minimum);
 }
}
uint8_t r1_health_storage_hrv_prefix[153] __attribute__((aligned(1),section(".r1.health.storage.hrv")))={0};
/* Stock 0x5af60: halfword rows and six-byte latest sample. */
void r1_hrv_event_storage(const volatile uint8_t *sample)
{
 if(!sample)return;
 uint32_t timestamp=read32(sample+2);
 uint32_t hour=r1_health_storage_hour_index(timestamp);
 timestamp=read32(sample+2);uint32_t value=read16(sample);
 uint32_t average=r1_health_storage_average(5,value,timestamp);
 volatile uint8_t *base=r1_health_storage_hrv_prefix;
 volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)base+hour*6u);
 value=read16(sample);uint32_t maximum=read16(entry+2);
 if(value>maximum)write16(entry+2,value);
 value=read16(sample);uint32_t minimum=read16(entry+4);
 if(value<minimum || !minimum)write16(entry+4,value);
 write16(entry,average);
 write32(base+147,read32(sample));write16(base+151,read16(sample+4));
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  timestamp=read32(sample+2);value=read16(sample);
  (void)r1_structured_log_format(0x0c800000,"[RING]last_hrv: %d, timestamp: %d","[RING]last_hrv: %d, timestamp: %d",value,timestamp);
 }
 if(r1_structured_log_mode_get()&2u){
  timestamp=read32(sample+2);value=read16(sample);
  nrf_log_frontend_std_2(0x001c0003,"last_hrv: %d, timestamp: %d",value,timestamp);
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  minimum=read16(entry+4);maximum=read16(entry+2);value=read16(sample);
  (void)r1_structured_log_format(0x0d000000,"[RING]hrv: %d, avg_hrv: %d, max_hrv: %d, min_hrv: %d","[RING]hrv: %d, avg_hrv: %d, max_hrv: %d, min_hrv: %d",value,average,maximum,minimum);
 }
 if(r1_structured_log_mode_get()&2u){
  minimum=read16(entry+4);maximum=read16(entry+2);value=read16(sample);
  nrf_log_frontend_std_4(0x001c0003,"hrv: %d, avg_hrv: %d, max_hrv: %d, min_hrv: %d",value,average,maximum,minimum);
 }
}
uint8_t r1_health_storage_spo2_prefix[80] __attribute__((aligned(1),section(".r1.health.storage.spo2")))={0};
/* Stock 0x5bb2c. Preserve live SpO2 sample/cache accesses. */
void r1_spo2_event_storage(const volatile uint8_t *sample)
{
 if(!sample)return;
 uint32_t timestamp=read32(sample+1);
 uint32_t hour=r1_health_storage_hour_index(timestamp);
 timestamp=read32(sample+1);uint32_t value=sample[0];
 uint32_t average=r1_health_storage_average(1,value,timestamp);
 volatile uint8_t *base=r1_health_storage_spo2_prefix;
 volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)base+hour*3u);
 value=sample[0];uint32_t maximum=entry[1];
 if(value>maximum)entry[1]=(uint8_t)value;
 value=sample[0];uint32_t minimum=entry[2];
 if(value<minimum || !minimum)entry[2]=(uint8_t)value;
 entry[0]=(uint8_t)average;
 write32(base+75,read32(sample));base[79]=sample[4];
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  timestamp=read32(sample+1);value=sample[0];
  (void)r1_structured_log_format(0x0c800000,"[RING]last_spo2: %d, timestamp: %d","[RING]last_spo2: %d, timestamp: %d",value,timestamp);
 }
 if(r1_structured_log_mode_get()&2u){
  timestamp=read32(sample+1);value=sample[0];
  nrf_log_frontend_std_2(0x001c0003,"last_spo2: %d, timestamp: %d",value,timestamp);
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  (void)r1_structured_log_format(0x0d000000,"[RING]spo2: %d, avg_spo2: %d, max_spo2: %d, min_spo2: %d","[RING]spo2: %d, avg_spo2: %d, max_spo2: %d, min_spo2: %d",value,average,maximum,minimum);
 }
 if(r1_structured_log_mode_get()&2u){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  nrf_log_frontend_std_4(0x001c0003,"spo2: %d, avg_spo2: %d, max_spo2: %d, min_spo2: %d",value,average,maximum,minimum);
 }
}
#include "native_hourly_state.h"
/* Stock 0x5bcec. Preserve live sample/cache reads across all providers. */
void r1_stress_event_storage(const volatile uint8_t *sample)
{
 if(!sample)return;
 uint32_t timestamp=read32(sample+1);
 uint32_t hour=r1_health_storage_hour_index(timestamp);
 timestamp=read32(sample+1);uint32_t value=sample[0];
 uint32_t average=r1_health_storage_average(3,value,timestamp);
 volatile uint8_t *base=r1_health_storage_stress_prefix;
 volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)base+hour*3u);
 value=sample[0];uint32_t maximum=entry[1];
 if(value>maximum)entry[1]=(uint8_t)value;
 value=sample[0];uint32_t minimum=entry[2];
 if(value<minimum || !minimum)entry[2]=(uint8_t)value;
 entry[0]=(uint8_t)average;
 write32(base+75,read32(sample));base[79]=sample[4];
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  timestamp=read32(sample+1);value=sample[0];
  (void)r1_structured_log_format(0x0c800000,"[RING]last_stress: %d, timestamp: %d","[RING]last_stress: %d, timestamp: %d",value,timestamp);
 }
 if(r1_structured_log_mode_get()&2u){
  timestamp=read32(sample+1);value=sample[0];
  nrf_log_frontend_std_2(0x001c0003,"last_stress: %d, timestamp: %d",value,timestamp);
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  (void)r1_structured_log_format(0x0d000000,r1_health_storage_stress_text,r1_health_storage_stress_text,value,average,maximum,minimum);
 }
 if(r1_structured_log_mode_get()&2u){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  nrf_log_frontend_std_4(0x001c0003,"stress: %d, avg_stress: %d, max_stress: %d, min_stress: %d",value,average,maximum,minimum);
 }
}
uint8_t r1_health_storage_temperature_prefix[80] __attribute__((aligned(1),section(".r1.health.storage.temperature")))={0};
/* Stock 0x5be7c: diagnostics add250; stored sample/average remain bytes. */
void r1_temperature_event_storage(const volatile uint8_t *sample)
{
 if(!sample)return;
 uint32_t timestamp=read32(sample+1);
 uint32_t hour=r1_health_storage_hour_index(timestamp);
 timestamp=read32(sample+1);uint32_t value=sample[0];
 uint32_t average=r1_health_storage_average(2,value,timestamp);
 volatile uint8_t *base=r1_health_storage_temperature_prefix;
 volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)base+hour*3u);
 value=sample[0];uint32_t maximum=entry[1];
 if(value>maximum)entry[1]=(uint8_t)value;
 value=sample[0];uint32_t minimum=entry[2];
 if(value<minimum || !minimum)entry[2]=(uint8_t)value;
 entry[0]=(uint8_t)average;
 write32(base+75,read32(sample));base[79]=sample[4];
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  timestamp=read32(sample+1);value=sample[0];
  (void)r1_structured_log_format(0x0c800000,"[RING]last_temp: %d, timestamp: %d","[RING]last_temp: %d, timestamp: %d",value+250u,timestamp);
 }
 if(r1_structured_log_mode_get()&2u){
  timestamp=read32(sample+1);value=sample[0];
  nrf_log_frontend_std_2(0x001c0003,"last_temp: %d, timestamp: %d",value+250u,timestamp);
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  (void)r1_structured_log_format(0x0d000000,"[RING]temp: %d, avg_temp: %d, max_temp: %d, min_temp: %d","[RING]temp: %d, avg_temp: %d, max_temp: %d, min_temp: %d",value+250u,average+250u,maximum+250u,minimum+250u);
 }
 if(r1_structured_log_mode_get()&2u){
  minimum=entry[2];maximum=entry[1];value=sample[0];
  nrf_log_frontend_std_4(0x001c0003,"temp: %d, avg_temp: %d, max_temp: %d, min_temp: %d",value+250u,average+250u,maximum+250u,minimum+250u);
 }
}
const char r1_health_storage_stress_text[] __attribute__((aligned(1),section(".r1.health.storage.stress_text")))="[RING]stress: %d, avg_stress: %d, max_stress: %d, min_stress: %d";
