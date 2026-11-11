/* Stock0x7bd68: fill missing cached NV fields, preserving valid local data. */
#include <stdint.h>
#include <string.h>
#include "../board/native_battery_memory.h"
#include "../board/native_kv_class.h"
#include "../../include/r1_stock_checksums.h"
extern void *volatile r1_device_info_kv_handle,*volatile r1_batcfg_record_kv_handle,*volatile r1_r_size_kv_handle;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t),nrf_log_frontend_std_6(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
#define INFO1(ring,sdk,value) do {RING(0x0c400000,ring,value);if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,sdk,(uint32_t)(value));}while(0)
#define INFO3(ring,sdk,a,b,c) do {RING(0x0cc00000,ring,a,b,c);if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,sdk,(uint32_t)(a),(uint32_t)(b),(uint32_t)(c));}while(0)
static uint32_t adc_valid(int32_t value)
{return (uint32_t)(value+500)<=1000u && value!=-1 && value!=0;}
uint32_t r1_native_nv_recovery_merge_boundary(const void *body,uint32_t length,uint32_t expected_crc)
{
 const volatile uint8_t *in=body;
 if(!in){RING(0x04000000,"[RING][NV_RECOVER] nv_recover is NULL");if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,"[NV_RECOVER] nv_recover is NULL");return 0;}
 /* The only native command admission is the fixed116-byte recovery record. */
 if(length!=116)return 0;
 uint32_t computed=r1_stock_crc16_modbus(body,length);
 if(computed!=expected_crc){
  RING(0x04800000,"[RING][NV_RECOVER] crc mismatch, expected: %d, calc: %d",expected_crc,computed);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001,"[NV_RECOVER] crc mismatch, expected: %d, calc: %d",expected_crc,computed);
  return 0;
 }
 uint8_t serial[124]={0},battery[4]={0},ring_size=0;
 uint32_t sr=r1_kv_class_read(r1_device_info_kv_handle,serial,124);
 uint32_t br=r1_kv_class_read(r1_batcfg_record_kv_handle,battery,4);
 uint32_t rr=r1_kv_class_read(r1_r_size_kv_handle,&ring_size,1);
 /* Do not construct writes from unavailable local records. */
 if(sr || br || rr)return 0;
 uint32_t serial_changed=0,battery_changed=0,ring_changed=0;
 if((uint32_t)battery[0]-1u>=4u && (uint32_t)in[92]-1u<4u){
  battery[0]=in[92];battery_changed=1;
  INFO1("[RING][NV_RECOVER] set battery type: %d","[NV_RECOVER] set battery type: %d",battery[0]);
 }
 if(!adc_valid((int16_t)read16(battery+2)) && adc_valid((int16_t)read16(in+94))){
  write16(battery+2,read16(in+94));battery_changed=1;
  INFO1("[RING][NV_RECOVER] set voltage compensation: %d","[NV_RECOVER] set voltage compensation: %d",(int32_t)(int16_t)read16(battery+2));
 }
 if((uint32_t)ring_size-6u>=10u && (uint32_t)in[96]-6u<10u){
  ring_size=in[96];ring_changed=1;
  INFO1("[RING][NV_RECOVER] set ring size: %d","[NV_RECOVER] set ring size: %d",ring_size);
 }
 if(serial[30]==255){
  uint32_t count=in[30];
  if(count>0 && count<=30){
  (void)memmove(serial,(const void *)(uintptr_t)in,count);serial[30]=in[30];serial_changed=1;
  INFO3("[RING][NV_RECOVER] set product bsn: %d %d %d","[NV_RECOVER] set product bsn: %d %d %d",serial[0],serial[1],serial[2]);
  }
 }
 if(serial[61]==255){
  uint32_t count=in[61];
  if(count>0 && count<=30){
  (void)memmove(serial+31,(const void *)(uintptr_t)(in+31),count);serial[61]=in[61];serial_changed=1;
  INFO3("[RING][NV_RECOVER] set product sn: %d %d %d","[NV_RECOVER] set product sn: %d %d %d",serial[31],serial[32],serial[33]);
  }
 }
 if(serial[62]==255 && in[62]!=255){
  write32(serial+62,read32(in+62));write16(serial+66,read16(in+66));serial_changed=1;
  RING(0x0d800000,"[RING][NV_RECOVER] set temp cal: %d %d %d %d %d %d",serial[62],serial[63],serial[64],serial[65],serial[66],serial[67]);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_6(0x001c0003,"[NV_RECOVER] set temp cal: %d %d %d %d %d %d",serial[62],serial[63],serial[64],serial[65],serial[66],serial[67]);
 }
 if((int16_t)read16(serial+68)==-1 && (int16_t)read16(in+68)!=-1){
  write32(serial+68,read32(in+68));write16(serial+72,read16(in+72));
  /* Native reaches the serial write unconditionally after this copy. */
  serial_changed=1;
  INFO3("[RING][NV_RECOVER] set acc cal: %d %d %d","[NV_RECOVER] set acc cal: %d %d %d",(int32_t)(int16_t)read16(serial+68),(int32_t)(int16_t)read16(serial+70),(int32_t)(int16_t)read16(serial+72));
 }
 if(serial_changed)(void)r1_kv_class_write(r1_device_info_kv_handle,serial,124);
 if(battery_changed)(void)r1_kv_class_write(r1_batcfg_record_kv_handle,battery,4);
 if(ring_changed)(void)r1_kv_class_write(r1_r_size_kv_handle,&ring_size,1);
 /* Native R0 was an incidental logger/cache return. Define C completion. */
 return 0;
}
