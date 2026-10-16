#include <stdint.h>
#include <string.h>
#include "../board/native_kv_class.h"
#include "../board/native_battery_memory.h"
extern void *volatile r1_device_info_record_kv_handle;
extern uint8_t r1_nv_handles_begin[],r1_nv_handles_end[];
extern uint32_t r1_store_class_record_write(void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_nv_sync_ring[] __attribute__((section(".r1.nv.sync.ring")))="[RING]sync store one class, name:%s,ret:%d";
const char r1_nv_sync_sdk[] __attribute__((section(".r1.nv.sync.sdk")))="sync store one class, name:%s,ret:%d";
uint32_t r1_native_nv_dirty_scan(void)
{
 uintptr_t end=(uintptr_t)r1_nv_handles_end,p=(uintptr_t)r1_nv_handles_begin;
 for(;p<end;p+=4){void *node=*(void *volatile *)p;if(*(volatile uint8_t *)((uintptr_t)node+18)&1u)break;}
 if(p==end)return 1;
 uint16_t index=0;
 for(p=(uintptr_t)r1_nv_handles_begin;p<end;p+=4,index++){
  void *node=*(void *volatile *)p;uint32_t result=r1_store_class_record_write(node,index);
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
__attribute__((used,noinline)) static uint32_t bit2_body(uint32_t value,volatile uint8_t *record)
{
 (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)record,52);
 record[24]=(record[24]&0xfbu)|((value&1u)<<2);
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)record,52);
 return r1_nv_modules_idle_check();
}
__attribute__((naked,noinline)) uint32_t r1_kv_dev_info_bit2_set(uint32_t value __attribute__((unused)))
{__asm__ volatile("push {r4,r5,lr}\nsub sp,sp,#52\nmov r1,sp\nbl bit2_body\nadd sp,sp,#52\npop {r4,r5,pc}");}
__attribute__((used,noinline)) static uint32_t peer_body(const volatile uint8_t *first,const volatile uint8_t *second,volatile uint8_t *record)
{
 (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)record,52);
 if(first){write32(record+8,read32(first));write16(record+12,read16(first+4));}
 if(second){write32(record+14,read32(second));write16(record+18,read16(second+4));}
 write32(record+20,0x484d4143);
 (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)record,52);
 return r1_nv_modules_idle_check();
}
__attribute__((naked,noinline)) uint32_t r1_peer_address_record_write(const void *first __attribute__((unused)),const void *second __attribute__((unused)))
{__asm__ volatile("push {r4,r5,r6,lr}\nsub sp,sp,#56\nmov r2,sp\nbl peer_body\nadd sp,sp,#56\npop {r4,r5,r6,pc}");}
__attribute__((used,noinline)) static uint32_t clear_peer_body(uint32_t handle,const volatile uint8_t *packet,volatile uint8_t *frame)
{
 if(!r1_packet_field12_get(packet))return 0;
 write32(frame,0);
 (void)r1_protocol_send_flag_set_c(handle,130,1,read16(packet+3),0);
 (void)r1_kv_dev_info_bit2_set(0);
 memset((void *)(frame+4),255,6);
 return r1_peer_address_record_write((const void *)(frame+4),(const void *)(frame+4));
}
__attribute__((naked,noinline)) uint32_t r1_protocol_command_000844b0(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)),uintptr_t scratch __attribute__((unused)),uint32_t seed __attribute__((unused)))
{__asm__ volatile("push {r1,r2,r3,r4,r5,lr}\nmov r2,sp\nbl clear_peer_body\npop {r1,r2,r3,r4,r5,pc}");}
