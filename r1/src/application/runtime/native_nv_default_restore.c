/* Stock0x7c52c: restore cached ring/battery calibration by controller address. */
#include <stdint.h>
#include <stddef.h>
#include "ble_gap.h"
#include "../board/native_kv_class.h"
extern uint32_t r1_batcfg_byte0_get(void),r1_nv_modules_idle_check(void);
extern void *volatile r1_batcfg_record_kv_handle,*volatile r1_r_size_kv_handle;
extern int r1_native_sprintf(char *,const char *,...);
extern int r1_native_memcmp(const void *,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void nrf_log_frontend_std_6(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
struct restore_record {char mac[12];uint8_t packed;int8_t adc;};
_Static_assert(sizeof(struct restore_record)==14,"native calibration stride");
const struct restore_record r1_nv_restore_table[59]={
#include "native_nv_restore_table.inc"
};
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
uint32_t r1_nv_compiled_default_restore(uint32_t unused0 __attribute__((unused)),uint32_t unused1 __attribute__((unused)))
{
 uint32_t flag=r1_batcfg_byte0_get();if(flag!=0 && flag!=255)return UINT32_MAX;
 ble_gap_addr_t address={0};char mac[16]={0};
 if(sd_ble_gap_addr_get(&address)){
  RING(0x0c000000,"[RING][NV_RESTORE] get mac address failed");
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"[NV_RESTORE] get mac address failed");
  return UINT32_MAX-1u;
 }
 const uint8_t *a=address.addr;
 (void)r1_native_sprintf(mac,"%02X%02X%02X%02X%02X%02X",a[5],a[4],a[3],a[2],a[1],a[0]);
 RING(0x0d800000,"[RING][NV_RESTORE] mac=%X%X%X%X%X%X",a[5],a[4],a[3],a[2],a[1],a[0]);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_6(0x001c0003,"[NV_RESTORE] mac=%X%X%X%X%X%X",a[5],a[4],a[3],a[2],a[1],a[0]);
 uint32_t index;
 for(index=0;index<59;index++)if(!r1_native_memcmp(mac,r1_nv_restore_table[index].mac,12))break;
 if(index==59){
  RING(0x08000000,"[RING][NV_RESTORE] not found in restore table");
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0002,"[NV_RESTORE] not found in restore table");
  return UINT32_MAX-1u;
 }
 uint8_t ring=0,battery[4]={0};
 (void)r1_kv_class_read(r1_r_size_kv_handle,&ring,1);
 (void)r1_kv_class_read(r1_batcfg_record_kv_handle,battery,4);
 ring=r1_nv_restore_table[index].packed&15u;
 battery[0]=r1_nv_restore_table[index].packed>>4;
 int16_t adc=r1_nv_restore_table[index].adc;battery[2]=(uint8_t)adc;battery[3]=(uint8_t)((uint16_t)adc>>8);
 (void)r1_kv_class_write(r1_r_size_kv_handle,&ring,1);
 (void)r1_kv_class_write(r1_batcfg_record_kv_handle,battery,4);
 (void)r1_nv_modules_idle_check();
 RING(0x0d000000,"[RING][NV_RESTORE] index=%d, ring_size=%d, bat_type=%d, adc=%d",index,(uint32_t)(r1_nv_restore_table[index].packed&15u),(uint32_t)(r1_nv_restore_table[index].packed>>4),(int32_t)r1_nv_restore_table[index].adc);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_4(0x001c0003,"[NV_RESTORE] index=%d, ring_size=%d, bat_type=%d, adc=%d",index,(uint32_t)(r1_nv_restore_table[index].packed&15u),(uint32_t)(r1_nv_restore_table[index].packed>>4),(uint32_t)(int32_t)r1_nv_restore_table[index].adc);
 return 0;
}
extern __typeof__(r1_nv_compiled_default_restore) r1_event_service_0007c52c __attribute__((alias("r1_nv_compiled_default_restore")));
