#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "../board/native_battery_memory.h"
#include "../../include/r1_product_serial.h"
extern uint32_t r1_protocol_send_response(uint32_t,const void *,const void *,uint32_t);
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
/* Source-owned cold class bytes; only authenticated offsets are interpreted.
 * Preserve the observed erased regions and mixed configuration bytes. */
struct r1_serial_record_class {uint32_t link_00;char key[12];uint16_t tag_16;volatile uint16_t flags;volatile uint16_t payload_size;uint16_t reserved_22;uint8_t payload[124];};
#define FF4 255,255,255,255
#define FF8 FF4,FF4
#define FF16 FF8,FF8
#define FF32 FF16,FF16
#define FF64 FF32,FF32
struct r1_serial_record_class r1_serial_record_class __attribute__((section(".r1.serial.kv.class"),aligned(4)))={.key="nv_r1",.tag_16=1,.flags=2,.payload_size=124,.payload={FF64,FF8,255,255,0,0,FF32,FF4,90,0,0,0,0,0,0,0,0,0,0,0}};
#undef FF64
#undef FF32
#undef FF16
#undef FF8
#undef FF4
_Static_assert(sizeof(struct r1_serial_record_class)==148 && offsetof(struct r1_serial_record_class,flags)==18 && offsetof(struct r1_serial_record_class,payload_size)==20 && offsetof(struct r1_serial_record_class,payload)==24,"native124-byte KV class layout");
void *volatile r1_device_info_kv_handle __attribute__((section(".r1.serial.kv.handle"),aligned(4)))=&r1_serial_record_class;
/* Public header fields, without private saved-register/frame contracts. */
static uint32_t header_send(uint32_t handle,uint32_t command,uint32_t version,
 uint32_t flags,uint32_t sequence,const void *payload,uint32_t length,uint32_t force_ack)
{
 uint32_t header[2];
 header[0]=(uint8_t)((flags^1u)|force_ack)|((uint32_t)(uint8_t)version<<8)|((command&0xff00u)<<8)|((command&255u)<<24);
 header[1]=(uint16_t)sequence;
 return r1_protocol_send_response(handle,header,payload,length);
}
uint32_t r1_protocol_ack_header_send(uint32_t handle,uint32_t command,uint32_t version,
 uint32_t flags,uint32_t sequence,const void *payload,uint32_t length)
{return header_send(handle,command,version,flags,sequence,payload,length,2);}
uint32_t r1_protocol_send_flag_inv(uint32_t handle,uint32_t command,uint32_t version,
 uint32_t flags,uint32_t sequence,const void *payload,uint32_t length)
{return header_send(handle,command,version,flags,sequence,payload,length,0);}
uint32_t r1_protocol_send_checked(uint32_t handle,uint32_t command,uint32_t flags,
 uint32_t sequence,const void *payload,uint32_t length)
{
 if(handle==0xffffu)return 0;
 return r1_protocol_ack_header_send(handle,command,1,flags,sequence,payload,length)==0;
}
uint32_t r1_native_product_serial_read(void *destination,uint8_t *length)
{
 uint8_t record[124];(void)memset(record,255,sizeof(record));
 uint32_t error=r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
 uint32_t result;
 if(!error && record[61]!=255){
  result=(uintptr_t)r1_native_memory_move(destination,record+31,15);
  if(length){*length=15;result=15;}
 }else{
  (void)memset(destination,255,15);result=(uintptr_t)destination+15u;
  if(length){*length=0;result=0;}
 }
 return result;
}
extern __typeof__(r1_native_product_serial_read) r1_advertising_product_sn_read
 __attribute__((alias("r1_native_product_serial_read")));
uint32_t r1_device_serial_handler(uint32_t handle,const void *packet,
 uintptr_t scratch __attribute__((unused)),uint32_t seed __attribute__((unused)))
{
 uint8_t output[16]={0};
 (void)r1_native_product_serial_read(output,0);
 return r1_protocol_send_checked(handle,16,0,read16((const volatile uint8_t *)packet+3),output,15);
}
