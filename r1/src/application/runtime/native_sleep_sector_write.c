/* Stock R1 0x8fe98: payload first, then the 20-byte slot header. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"
extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_sleep_sector_finalize(uint32_t);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
const char r1_sleep_write_success_text[] __attribute__((section(".r1.sleep.write.success"),aligned(1)))="[RING]sleep storage write data to sector success:%d, size:%d, cnt:%d";
static uint32_t ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void failure(const char *ring,const char *sdk,uint32_t status)
{
 if(ring_enabled())(void)r1_structured_log_format(0x04400000u,ring,ring,status);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001u,sdk,status);
}
static const volatile uint8_t *partition(void)
{return (const volatile uint8_t *)(uintptr_t)((volatile uint32_t *)r1_sleep_sync_context_prefix)[1];}
static const volatile uint8_t *device(void)
{return (const volatile uint8_t *)(uintptr_t)((volatile uint32_t *)r1_sleep_sync_context_prefix)[2];}
uint32_t r1_sleep_sector_write(uint32_t sector,const volatile uint8_t *data,uint32_t length)
{
 uint32_t headers=read32(partition()+52)+(sector<<12)+16;
 /* Stock rounds and masks to 16 bits, including zero on boundary wrap. */
 uint32_t aligned=(length+3u)&UINT32_C(0xfffc);
 uint32_t payload=headers+192;
 uint8_t header[24];__aeabi_memclr(header,sizeof(header));
 uint32_t slot;
 for(slot=0;slot<8;slot++){
  int (*read)(long,void *,size_t)=(void *)(uintptr_t)read32(device()+40);
  (void)read((long)(headers+slot*24),header,sizeof(header));
  if(read32(header+8)==UINT32_MAX && read32(header+12)==UINT32_MAX)break;
  payload=read32(partition()+52)+(sector<<12)+read16(header)+read16(header+2);
 }
 if(slot==8)return 0;
 uint32_t end=read32(partition()+52)+(sector<<12)+4096;
 if(end<payload+aligned){
  const char *ring="[RING]slp storage is full:%d, %d";
  if(ring_enabled())(void)r1_structured_log_format(0x04800000u,ring,ring,payload,aligned);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001u,"slp storage is full:%d, %d",payload,aligned);
  (void)r1_sleep_sector_finalize(sector);return 0;
 }
 int (*write)(long,const void *,size_t)=(void *)(uintptr_t)read32(device()+44);
 uint32_t status=(uint32_t)write((long)payload,(const void *)(uintptr_t)data,aligned);
 if(status){
  failure("[RING]sleep storage write data to sector fail:%d","sleep storage write data to sector fail:%d",status);return 0;
 }
 write16(header,aligned);
 write16(header+2,payload-(read16(partition()+52)+(sector<<12)));
 write16(header+6,read16(data+10));write32(header+8,read32(data+12));write32(header+12,read32(data+16));
 write16(header+18,r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)data,aligned));
 write=(void *)(uintptr_t)read32(device()+44);
 status=(uint32_t)write((long)(headers+slot*24),header,20);
 if(status){
  failure("[RING]sleep storage write head to sector fail:%d","sleep storage write head to sector fail:%d",status);return 0;
 }
 if(ring_enabled())(void)r1_structured_log_format(0x0cc00000u,r1_sleep_write_success_text,r1_sleep_write_success_text,payload,length,slot+1);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003u,"sleep storage write data to sector success:%d, size:%d, cnt:%d",payload,length,slot+1);
 return slot==7?r1_sleep_sector_finalize(sector):1;
}
