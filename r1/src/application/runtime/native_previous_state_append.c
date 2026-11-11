/* Stock 0x6bbb0: two-argument native binding over the shared append core.
 * FAL errors abort further operations; corrupt arithmetic is rejected. */
#include "native_health_storage.h"
#include "../board/native_battery_memory.h"
#include "gomore_primitives/gomore_primitives.h"
_Static_assert(sizeof(gomore_primitives_previous_append_stage)==4 &&
 sizeof(gomore_primitives_previous_append_result)==24,"native/core enum/result ABI");
_Static_assert(sizeof(gomore_primitives_previous_append_hooks)==24 &&
 sizeof(gomore_primitives_pkey_store)==28,"native/core store/hooks ABI");
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log0(uint32_t marker,uint32_t sdk_header,const char *ring,const char *sdk)
{
 if(enabled())(void)r1_structured_log_format(marker,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(sdk_header,sdk);
}
static void log1(const char *ring,const char *sdk,uint32_t value)
{
 if(enabled())(void)r1_structured_log_format(0x0c400000u,ring,ring,value);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003u,sdk,value);
}
static void log2(const char *ring,const char *sdk,uint32_t first,uint32_t second)
{
 if(enabled())(void)r1_structured_log_format(0x0c800000u,ring,ring,first,second);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003u,sdk,first,second);
}
static uint32_t offset(void *context)
{
 (void)context;
 return read32((const volatile uint8_t *)(uintptr_t)r1_health_pkey_storage.partition+52);
}
static bool read_flash(void *context,uint32_t at,uint8_t *out,size_t size)
{
 (void)context;
 int (*read)(long,uint8_t *,size_t)=(void *)(uintptr_t)read32((const volatile uint8_t *)(uintptr_t)r1_health_pkey_storage.device+40);
 return read((long)at,out,size)>=0;
}
static bool write_flash(void *context,uint32_t at,const uint8_t *in,size_t size)
{
 (void)context;
 int (*write)(long,const uint8_t *,size_t)=(void *)(uintptr_t)read32((const volatile uint8_t *)(uintptr_t)r1_health_pkey_storage.device+44);
 return write((long)at,in,size)>=0;
}
static bool erase_flash(void *context,uint32_t at,size_t size)
{
 (void)context;
 int (*erase)(long,size_t)=(void *)(uintptr_t)read32((const volatile uint8_t *)(uintptr_t)r1_health_pkey_storage.device+48);
 return erase((long)at,size)>=0;
}
static void *allocate(void *context,size_t size)
{(void)context;return pvPortMalloc(size);}
static void release(void *context,void *memory)
{(void)context;vPortFree(memory);}
static void observe(void *context,gomore_primitives_previous_append_stage stage,
                    uint32_t first,uint32_t second,const uint8_t *header)
{
 (void)context;
 switch(stage){
 case GOMORE_PREVIOUS_APPEND_LENGTHS:
  log2("[RING]gomore store data len:%d,pkey len:%d","gomore store data len:%d,pkey len:%d",first,second);break;
 case GOMORE_PREVIOUS_APPEND_TRIGGER:
  if(enabled())(void)r1_structured_log_format(0x0c800000u,"[RING]gomore store start:%d, end:%d","[RING]gomore store start:%d, end:%d",offset(NULL),first);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003u,"gomore store start:%d, end:%d",offset(NULL),first);
  break;
 case GOMORE_PREVIOUS_APPEND_ERASED:
  log0(0x0c000000u,0x001c0003u,"[RING]gomore store erase","gomore store erase");break;
 case GOMORE_PREVIOUS_APPEND_SLOT_READ:
  if(enabled())(void)r1_structured_log_format(0x0c800000u,"[RING]gomore store read_offset:%d, pKey_head.len:%d","[RING]gomore store read_offset:%d, pKey_head.len:%d",first,read32(header));
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003u,"gomore store read_offset:%d, pKey_head.len:%d",first,read32(header));
  break;
 case GOMORE_PREVIOUS_APPEND_SELECTED:
  log1("[RING]gomore store write_pos:%d","gomore store write_pos:%d",first);break;
 case GOMORE_PREVIOUS_APPEND_WRITTEN:
  log1("[RING]gomore store write_offset:%d","gomore store write_offset:%d",first);break;
 case GOMORE_PREVIOUS_APPEND_TOO_LARGE:
  log0(0x04000000u,0x001c0001u,"[RING]gomore store previousData is too long","gomore store previousData is too long");break;
 case GOMORE_PREVIOUS_APPEND_SCRATCH_ERROR:
  log0(0x04000000u,0x001c0001u,"[RING]gomore store malloc failed","gomore store malloc failed");break;
 case GOMORE_PREVIOUS_APPEND_READ_ERROR:
  log0(0x04000000u,0x001c0001u,"[RING]gomore store flash read failed","gomore store flash read failed");break;
 case GOMORE_PREVIOUS_APPEND_ERASE_ERROR:
  log0(0x04000000u,0x001c0001u,"[RING]gomore store flash erase failed","gomore store flash erase failed");break;
 case GOMORE_PREVIOUS_APPEND_WRITE_ERROR:
  log0(0x04000000u,0x001c0001u,"[RING]gomore store flash write failed","gomore store flash write failed");break;
 }
}
void r1_previous_state_append_native(const void *state,uint32_t length)
{
 if(!r1_health_pkey_storage.initialized)r1_pkey_fal_bind();
 if(!r1_health_pkey_storage.partition || !r1_health_pkey_storage.device){
  log0(0x04000000u,0x001c0001u,"[RING]gomore store flash not init","gomore store flash not init");return;
 }
 if(!state || !length){
  log0(0x04000000u,0x001c0001u,"[RING]gomore store previousData is null","gomore store previousData is null");return;
 }
 if(length>UINT32_MAX-3u){
  observe(NULL,GOMORE_PREVIOUS_APPEND_TOO_LARGE,0,0,NULL);return;
 }
 gomore_primitives_pkey_store store={.initialized=true,.partition_offset=0,
  .read=read_flash,.write=write_flash,.erase=erase_flash};
 gomore_primitives_previous_append_hooks hooks={.current_offset=offset,
  .observe=observe,.allocate=allocate,.release=release,.fallback_slot_zero=true};
 gomore_primitives_previous_append_result result;
 (void)gomore_primitives_previous_state_append_with_hooks(&store,state,length,
  (length+3u)&~3u,NULL,0,&result,&hooks);
}
