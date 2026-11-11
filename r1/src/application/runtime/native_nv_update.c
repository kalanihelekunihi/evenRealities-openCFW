#include <stdint.h>
#include <string.h>
#include "../board/native_kv_class.h"
#include "../board/native_battery_memory.h"
extern void *volatile r1_device_info_record_kv_handle;
extern void *volatile r1_ble_mult_kv_handle, *volatile r1_health_settings_kv_handle;
extern void *volatile r1_health_record_kv_handle, *volatile r1_batcfg_record_kv_handle;
extern void *volatile r1_device_info_kv_handle, *volatile r1_r_size_kv_handle;
/* Stock 0x20007de8..0x20007e04: preserve class indices and reload each
 * live handle, including changes made by a persistence callback. */
void *volatile *const r1_nv_handle_owners[R1_NV_HANDLE_COUNT] = {
 &r1_device_info_record_kv_handle, &r1_ble_mult_kv_handle,
 &r1_health_settings_kv_handle, &r1_health_record_kv_handle,
 &r1_batcfg_record_kv_handle, &r1_device_info_kv_handle,
 &r1_r_size_kv_handle
};
/* Stock 0x73634: read a named slice from one of the seven live NV records. */
uint32_t r1_factory_read_lookup(const char *name,void *destination,
                                uint32_t offset,uint32_t length)
{
 if(!name)return 1u;
 for(uint32_t index=0;index<R1_NV_HANDLE_COUNT;++index){
  const volatile uint8_t *record=*r1_nv_handle_owners[index];
  if(strcmp((const char *)(record+4),name)!=0)continue;
  if(!record)return 1u;
  if(offset+length>(uint32_t)read16(record+20))return 1u;
  memcpy(destination,(const void *)(record+24+offset),length);
  return 0u;
 }
 return 1u;
}
extern uint32_t r1_store_class_record_write(void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_nv_sync_ring[] __attribute__((section(".r1.nv.sync.ring")))="[RING]sync store one class, name:%s,ret:%d";
const char r1_nv_sync_sdk[] __attribute__((section(".r1.nv.sync.sdk")))="sync store one class, name:%s,ret:%d";
uint32_t r1_native_nv_dirty_scan(void)
{
 unsigned index;
 for(index=0;index<R1_NV_HANDLE_COUNT;index++){void *node=*r1_nv_handle_owners[index];if(*(volatile uint8_t *)((uintptr_t)node+18)&1u)break;}
 if(index==R1_NV_HANDLE_COUNT)return 1;
 for(index=0;index<R1_NV_HANDLE_COUNT;index++){
  void *node=*r1_nv_handle_owners[index];uint32_t result=r1_store_class_record_write(node,index);
  if(result){
   if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
    (void)r1_structured_log_format(0x0c800000,r1_nv_sync_ring,r1_nv_sync_ring,(const char *)node+4,result);
   if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_2(0x001c0003,r1_nv_sync_sdk,(uintptr_t)node+4,result);
  }
 }
 uint32_t (*request)(uint32_t,uint32_t)=(void *)(uintptr_t)read32((const volatile uint8_t *)r1_kv_port+24);
 (void)request(1,0);return 1;
}
uint32_t r1_nv_modules_idle_check(void){return r1_native_nv_dirty_scan()^1u;}
uint32_t r1_kv_dev_info_bit2_set(uint32_t value)
{
 volatile uint8_t record[52]={0};
 (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)record,52);
 record[24]=(record[24]&0xfbu)|((value&1u)<<2);
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)record,52);
 return r1_nv_modules_idle_check();
}
uint32_t r1_peer_address_record_write(const void *first_address,const void *second_address)
{
 const volatile uint8_t *first=first_address,*second=second_address;
 volatile uint8_t record[52]={0};
 (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)record,52);
 if(first){write32(record+8,read32(first));write16(record+12,read16(first+4));}
 if(second){write32(record+14,read32(second));write16(record+18,read16(second+4));}
 write32(record+20,0x484d4143);
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)record,52);
 return r1_nv_modules_idle_check();
}
uint32_t r1_protocol_command_000844b0(uint32_t handle,const void *input,
                                   uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;
 const volatile uint8_t *packet=input;
 if(!r1_packet_field12_get(packet))return 0;
 (void)r1_protocol_send_flag_set_c(handle,130,1,read16(packet+3),0);
 (void)r1_kv_dev_info_bit2_set(0);
 uint8_t address[6];
 memset(address,255,sizeof(address));
 return r1_peer_address_record_write(address,address);
}
