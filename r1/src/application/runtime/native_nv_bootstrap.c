/* Stock 0x73220: restore registered cached classes from eight storage slots.
 * Header sizes must match the configured class before any record is copied. */
#include "../board/native_kv_class.h"
#include "../board/native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"
#include <string.h>
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log0(uint32_t marker,uint32_t header,const char *ring,const char *sdk)
{
 if(ring_enabled())(void)r1_structured_log_format(marker,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(header,sdk);
}
static void log1(uint32_t marker,uint32_t header,const char *ring,const char *sdk,const char *value)
{
 if(ring_enabled())(void)r1_structured_log_format(marker,ring,ring,value);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(header,sdk,(uint32_t)(uintptr_t)value);
}
uint32_t r1_nv_store_bootstrap_73220(void)
{
 log0(0x0c000000u,0x001c0003u,"[RING]KV core restore","KV core restore");
 uint32_t (*open)(const char *)=(void *)(uintptr_t)read32((const volatile uint8_t *)r1_kv_port+8);
 if(open("r")){
  log0(0x04000000u,0x001c0001u,"[RING]KV restore not file","KV restore not file");return 6;
 }
 uint8_t *record=pvPortMalloc(256);
 if(!record){
  log1(0x04400000u,0x001c0001u,"[RING]%s malloc err","%s malloc err","kv_core_restore");return 1;
 }
 for(uint32_t slot=0;slot<8;slot++){
  uint32_t (*read_record)(uint32_t,void *,uint32_t)=(void *)(uintptr_t)read32((const volatile uint8_t *)r1_kv_port+16);
  if(read_record(slot<<8,record,256))continue;
  volatile uint8_t *node=NULL;
  for(uint32_t i=0;i<R1_NV_HANDLE_COUNT;i++){
   volatile uint8_t *candidate=*r1_nv_handle_owners[i];
   if(read32(candidate)==read32(record) && strcmp((const char *)(uintptr_t)(candidate+4),(const char *)(record+4))==0){node=candidate;break;}
  }
  if(!node)continue;
  uint32_t size=read16(node+20);
  /* Payload CRC does not authenticate the stored size. Keep corrupt headers
   * from changing the cached class extent or causing later slot overreads. */
  if(size>231u || read16(record+20)!=size)continue;
  uint16_t crc=r1_stock_crc16_modbus(record+24,size);
  if(crc!=read16(record+22)){
   log1(0x04400000u,0x001c0001u,"[RING]crc check fail,%s","crc check fail,%s",(const char *)(uintptr_t)(node+4));continue;
  }
  (void)memmove((void *)(uintptr_t)node,record,size+24u);
  write16(node+18,(uint16_t)((read16(node+18)&3u)|((slot&0x3fffu)<<2)));
  if(ring_enabled()){
   uint32_t index=read16(node+18)>>2;
   (void)r1_structured_log_format(0x0c800000u,"[RING]restore class, name:%s, index:%d","[RING]restore class, name:%s, index:%d",(const char *)(uintptr_t)(node+4),index);
  }
  if(r1_structured_log_mode_get()&2u){
   uint32_t index=read16(node+18)>>2;
   nrf_log_frontend_std_2(0x001c0003u,"restore class, name:%s, index:%d",(uint32_t)(uintptr_t)(node+4),index);
  }
 }
 uint32_t (*close)(void)=(void *)(uintptr_t)read32((const volatile uint8_t *)r1_kv_port+12);
 (void)close();vPortFree(record);return 0;
}
