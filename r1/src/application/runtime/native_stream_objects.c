#include <stdint.h>
#include <stddef.h>
#include "../board/native_watchdog.h"
extern void *pvPortMalloc(size_t),*r1_native_list_append(struct r1_native_list *);
extern void __aeabi_memclr(void *,size_t);
extern void *memcpy(void *,const void *,size_t);
extern size_t strlen(const char *);
extern int strcmp(const char *,const char *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
struct r1_native_list r1_stream_object_registry __attribute__((section(".bss.r1.stream.object_registry"),aligned(4)));
#define TEXT(name,value) const char r1_stream_##name[] __attribute__((section(".r1.stream." #name)))=value
TEXT(object_ring,"[RING]obj malloc fail");TEXT(object_sdk,"obj malloc fail");
TEXT(insert_ring,"[RING]list insert fail");TEXT(insert_sdk,"list insert fail");
static void log_failure(const char *ring,const char *sdk)
{
 uint32_t mode=r1_structured_log_mode_get();
 if((mode&1) || (r1_structured_log_mode_get()&4))(void)r1_structured_log_format(0x04000000,ring,ring);
 if(r1_structured_log_mode_get()&2)nrf_log_frontend_std_0(0x001c0001,sdk);
}
static __attribute__((noreturn,noinline)) void bad_object(void)
{uint32_t mask=64;__asm__ volatile("msr BASEPRI,%0"::"r"(mask):"memory");*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;for(;;){}}
uint32_t r1_stream_object_insert(void *object)
{
 if(!r1_stream_object_registry.payload_bytes)r1_native_list_initialize(&r1_stream_object_registry,8);
 volatile uint32_t *node=r1_native_list_append(&r1_stream_object_registry);
 if(!node){log_failure(r1_stream_insert_ring,r1_stream_insert_sdk);return 0;}
 node[1]=(uint32_t)(uintptr_t)object;return 1;
}
void *r1_stream_object_lookup(const char *name)
{
 if(!r1_stream_object_registry.payload_bytes)return (void *)0;
 for(volatile uint32_t *node=r1_native_list_head(&r1_stream_object_registry);node;node=r1_native_list_next(&r1_stream_object_registry,(void *)(uintptr_t)node)){
  uint32_t object=node[1];
  if(!strcmp((const char *)(uintptr_t)object,name))return (void *)(uintptr_t)node[1];
 }
 return (void *)0;
}
void *r1_stream_object_create(const char *name,uint32_t sample_size,const void *provider,uint32_t context)
{
 if(!name || !provider || !sample_size)bad_object();
 volatile uint32_t *object=pvPortMalloc(56);
 if(!object){log_failure(r1_stream_object_ring,r1_stream_object_sdk);return (void *)0;}
 __aeabi_memclr((void *)(uintptr_t)object,56);
 volatile uint8_t *bytes=(volatile uint8_t *)object;bytes[40]&=(uint8_t)~6u;
 uint32_t length=(uint8_t)strlen(name);if(length>8)length=8;
 (void)memcpy((void *)(uintptr_t)object,name,length);
 r1_native_list_initialize((struct r1_native_list *)(uintptr_t)(bytes+44),24);
 if(context)object[9]=context;
 object[3]=(uint32_t)(uintptr_t)provider;*(volatile uint16_t *)(bytes+28)=(uint16_t)sample_size;
 (void)r1_stream_object_insert((void *)(uintptr_t)object);
 return (void *)(uintptr_t)object;
}
uint32_t r1_stream_object_flag_set(volatile uint8_t *object,uint32_t value)
{
 if(!object)return 0;
 object+=40;*object=(uint8_t)((*object&0xfeu)|(value&1u));return (uint32_t)(uintptr_t)object;
}
