#include "native_subscriber.h"
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} subscriber_word;
static uint32_t word(const volatile uint8_t *p)
{return ((const volatile subscriber_word *)p)->value;}
static void put(volatile uint8_t *p,uint32_t value)
{((volatile subscriber_word *)p)->value=value;}
/* The native callback receives its payload in R0 and its own target in R1.
 * A required tail call preserves the caller's link register. */
typedef void (*r1_subscriber_callback_fn)(uint32_t,uint32_t);
__attribute__((noinline,used)) void r1_subscriber_invoke(
 uint32_t payload,uint32_t callback)
{__attribute__((musttail)) return
 ((r1_subscriber_callback_fn)(uintptr_t)callback)(payload,callback);}
/* Native 0x8b0fc reloads the event head after every callback, before loading
 * next. A callback clearing that head still causes the native read at +8. */
osStatus_t r1_event_service_0008b0fc(volatile uint8_t *event)
{
 if(!event)return osOK;
 uint32_t thread=(uint32_t)(uintptr_t)osThreadGetId();
 (void)r1_subscriber_lock();
 uint32_t node=word(event);
 while(node){
  const volatile uint8_t *entry=(const volatile uint8_t *)(uintptr_t)node;
  uint32_t callback=word(entry);
  if(callback){
   uint32_t owner=word(entry+4);
   if(word((const volatile uint8_t *)(uintptr_t)owner)==thread)
    r1_subscriber_invoke((uint32_t)(uintptr_t)event+6u,callback);
  }
  node=word(event);
  node=word((const volatile uint8_t *)(uintptr_t)(node+8u));
  put(event,node);
 }
 return r1_subscriber_unlock();
}
