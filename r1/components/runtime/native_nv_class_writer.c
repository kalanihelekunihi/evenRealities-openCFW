#include <stdint.h>
#include "../board/native_kv_class.h"
#include "../board/native_battery_memory.h"
#include "../../source/include/r1_stock_checksums.h"
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_nv_class_write_ring[] __attribute__((section(".r1.nv.class_writer.ring")))="[RING]store class fail, write fail, calss name:%s";
const char r1_nv_class_write_sdk[] __attribute__((section(".r1.nv.class_writer.sdk")))="store class fail, write fail, calss name:%s";
uint32_t r1_store_class_record_write(void *node,uint32_t index)
{
 volatile uint8_t *p=node;
 uint16_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)(p+24),read16(p+20));
 write16(p+22,crc);
 uint16_t flags=(uint16_t)((read16(p+18)&2u)|((index&0x3fffu)<<2));
 write16(p+18,flags);
 uintptr_t callback=read32((const volatile uint8_t *)r1_kv_port+20);
 uint32_t (*write_record)(uint32_t,const void *,uint32_t,uintptr_t)=(void *)callback;
 uint32_t result=write_record((uint32_t)(flags>>2)<<8,node,(uint32_t)read16(p+20)+24u,callback);
 if(!result)return 1;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x04400000,r1_nv_class_write_ring,r1_nv_class_write_ring,(const char *)node+4);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0001,r1_nv_class_write_sdk,(uintptr_t)node+4);
 return 0;
}
