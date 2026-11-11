/* Stock0x7b634/0x7bbe8/0x839b4: cached NV report, envelope and checked send. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "../board/native_battery_memory.h"
#include "../board/native_kv_class.h"
#include "../../include/r1_stock_checksums.h"
extern void *volatile r1_device_info_kv_handle,*volatile r1_batcfg_record_kv_handle,*volatile r1_r_size_kv_handle;
extern void *pvPortMalloc(uint32_t);extern void vPortFree(void *);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
#define INVALID(ring,sdk,value) do {RING(0x08400000,ring,value);if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0002,sdk,(uint32_t)(value));}while(0)
uint32_t r1_nv_recovery_report_builder(volatile uint8_t *out)
{
 if(!out){RING(0x04000000,"[RING][NV_RECOVER] nv_recover is NULL");if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0001,"[NV_RECOVER] nv_recover is NULL");return 0;}
 uint8_t serial[124]={0},battery[4]={0},ring_size=0;
 (void)memset((void *)(uintptr_t)out,0,116);
 (void)r1_kv_class_read(r1_device_info_kv_handle,serial,124);
 (void)memmove((void *)(uintptr_t)out,serial,30);out[30]=serial[30];
 (void)memmove((void *)(uintptr_t)(out+31),serial+31,30);out[61]=serial[61];
 write32(out+62,read32(serial+62));write16(out+66,read16(serial+66));write32(out+68,read32(serial+68));write16(out+72,read16(serial+72));
 (void)r1_kv_class_read(r1_batcfg_record_kv_handle,battery,4);
 out[92]=battery[0];write16(out+94,read16(battery+2));
 (void)r1_kv_class_read(r1_r_size_kv_handle,&ring_size,1);out[96]=ring_size;
 uint32_t valid=1;
 if((uint32_t)out[92]-1u>=4u){INVALID("[RING][NV_RECOVER] invalid battery_type: %d","[NV_RECOVER] invalid battery_type: %d",out[92]);valid=0;}
 int32_t adc=(int16_t)read16(out+94);
 if((uint32_t)(adc+500)>1000u || adc==-1){INVALID("[RING][NV_RECOVER] invalid voltage_compensation: %d","[NV_RECOVER] invalid voltage_compensation: %d",(int32_t)(int16_t)read16(out+94));valid=0;}
 if((uint32_t)out[96]-6u>=10u){INVALID("[RING][NV_RECOVER] invalid ring_size: %d","[NV_RECOVER] invalid ring_size: %d",out[96]);valid=0;}
 if(out[30]==255 || out[30]==0 || out[30]>30){INVALID("[RING][NV_RECOVER] invalid product_bsn_len: %d","[NV_RECOVER] invalid product_bsn_len: %d",out[30]);valid=0;}
 return valid;
}
uint32_t r1_nv_recovery_outbound_response(const volatile uint8_t *packet)
{
 if(!packet)return 0;
 uint32_t handle=r1_phone_connection_handle_get();uint32_t bytes=(uint16_t)(read16(packet+1)+5u);
 return r1_protocol_response_send_0x100(handle,17,1,0,(const void *)(uintptr_t)packet,bytes);
}
uint32_t r1_native_nv_recovery_report_boundary(void)
{
 uint8_t *packet=pvPortMalloc(121);
 if(!packet){
  RING(0x04000000,"[RING][NV_RECOVER] malloc proto_nv_recover failed");
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,"[NV_RECOVER] malloc proto_nv_recover failed");return 0;
 }
 if(r1_nv_recovery_report_builder(packet+5)){
  write16(packet+3,r1_stock_crc16_modbus(packet+5,116));write16(packet+1,116);packet[0]=2;
  (void)r1_nv_recovery_outbound_response(packet);
 }else{
  RING(0x08000000,"[RING][NV_RECOVER] local nv data invalid, skip report");
  if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0002,"[NV_RECOVER] local nv data invalid, skip report");
 }
 vPortFree(packet);
 /* vPortFree has no C result. Define the completed cleanup path as zero. */
 return 0;
}
