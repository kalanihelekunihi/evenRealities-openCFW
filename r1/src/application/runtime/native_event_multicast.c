#include <stddef.h>
#include <stdint.h>
#include "native_subscriber.h"
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void *r1_native_memory_move(void *,const void *,size_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} multicast_word;
typedef struct __attribute__((packed,may_alias)) {uint16_t value;} multicast_half;
static uint32_t word(const volatile uint8_t *p)
{return ((const volatile multicast_word *)p)->value;}
static void put(volatile uint8_t *p,uint32_t value)
{((volatile multicast_word *)p)->value=value;}
/* The opaque native callback receives payload, thread-cell address and its
 * own target in R0/R1/R2. The required tail call preserves the caller's LR. */
typedef void (*r1_multicast_callback_fn)(uint32_t,uint32_t,uint32_t);
__attribute__((noinline,used)) void r1_subscriber_multicast_invoke(
 uint32_t payload,uint32_t reference,uint32_t callback)
{
 __attribute__((musttail)) return
  ((r1_multicast_callback_fn)(uintptr_t)callback)(payload,reference,callback);
}
static volatile uint8_t *root_at(uint32_t kind)
{
 uint32_t address=(uint32_t)(uintptr_t)r1_subscriber_roots+kind*4u;
 return (volatile uint8_t *)(uintptr_t)word((const volatile uint8_t *)(uintptr_t)address);
}
/* Stock 0x8b028: cached short payload, synchronous current-thread callbacks,
 * and one queued copy per known destination thread-cell address. */
uint32_t r1_event_service_0008b028(uint32_t kind,const void *payload,uint32_t length)
{
 if(!root_at(kind))return 0;
 (void)r1_subscriber_lock();
 if(length<=4){
  put(root_at(kind)+8,0);
  r1_native_memory_move((void *)(uintptr_t)(root_at(kind)+8),payload,length);
 }
 uint32_t thread=(uint32_t)(uintptr_t)osThreadGetId();
 uint32_t node=word(root_at(kind));
 uint32_t sent=0,size=(uint16_t)(length+8u);
 if(!node){(void)r1_subscriber_unlock();return 1;}
 volatile uint8_t *record=pvPortMalloc(size);
 if(record){
  put(record,node);
  ((volatile multicast_half *)(record+4))->value=(uint16_t)length;
  r1_native_memory_move((void *)(uintptr_t)(record+6),payload,length);
 }
 do{
  const volatile uint8_t *entry=(const volatile uint8_t *)(uintptr_t)node;
  uint32_t callback=word(entry);
  if(callback){
   uint32_t reference=word(entry+4);
   if(word((const volatile uint8_t *)(uintptr_t)reference)==thread)
    r1_subscriber_multicast_invoke((uint32_t)(uintptr_t)payload,reference,callback);
   else for(uint32_t route=0;route<2;++route){
    const volatile uint8_t *row=(const volatile uint8_t *)&r1_subscriber_routes[route];
    if(word(row)!=reference)continue;
    uint32_t bit=1u<<route;
    if(!(sent&bit)){
     if(record){
      uint32_t id=((const volatile multicast_half *)(row+4))->value;
      (void)r1_event_publish(id,(const void *)(uintptr_t)record,size);
     }
     sent|=bit;
    }
    break;
   }
  }
  node=word(entry+8);
 }while(node);
 if(record)vPortFree((void *)(uintptr_t)record);
 (void)r1_subscriber_unlock();return 1;
}
