/* Stock 0x7ba40 with an explicit capacity API and bounded malformed records. */
#include <stdint.h>
#include <stddef.h>
extern void *memcpy(void *,const void *,size_t);
extern void *memset(void *,int,size_t);
#include "native_product_bsn.h"
#include "native_kv_class.h"
extern void *volatile r1_device_info_kv_handle;
uint32_t r1_product_bsn_read(void *destination,uint32_t capacity)
{
 if(!destination || !capacity)return 0;
 uint8_t record[124];
 (void)memset(record,255,sizeof record);
 (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof record);
 uint32_t length=record[30];
 uint32_t erased=length>30u;
 if(erased)length=21;
 if(length>capacity)length=capacity;
 if(erased)(void)memset(destination,255,length);
 else (void)memcpy(destination,record,length);
 return length;
}
void r1_product_bsn_get(void *destination)
{(void)r1_product_bsn_read(destination,30);}
