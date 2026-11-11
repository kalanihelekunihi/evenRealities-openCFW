#include <stddef.h>
#include "native_subscriber.h"
#include <stdint.h>
void *volatile r1_subscriber_roots[5] __attribute__((section(".r1.subscriber.roots"),aligned(4)))={0};
struct r1_event_context { void (*create)(void), (*stop)(void); void *thread, *queue; };
extern struct r1_event_context r1_event_sensor,r1_event_system;
_Static_assert(sizeof(struct r1_subscriber_route)==8,"native routing stride");
const struct r1_subscriber_route r1_subscriber_routes[2] __attribute__((section(".r1.subscriber.routes"),aligned(4)))={{&r1_event_sensor.thread,2,0},{&r1_event_system.thread,0x1000,0}};
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} subscriber_word;
static uint32_t word(const volatile uint8_t *p)
{return ((const volatile subscriber_word *)p)->value;}
static void put(volatile uint8_t *p,uint32_t value)
{((volatile subscriber_word *)p)->value=value;}
extern void *pvPortMalloc(size_t);
/* Native allocation failures keep the lock, mask interrupts and fault. */
static __attribute__((noreturn,noinline)) void subscriber_allocation_failure(void)
{
 uint32_t mask=64;
 __builtin_arm_wsr("basepri",mask);
 *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
 for(;;){}
}
/* Stock 0x8af8c: callback-only uniqueness and late head/tail reads matter
 * when allocator/lock callbacks change shared state. */
uint32_t r1_subscriber_register(uint32_t kind,uint32_t callback,uint32_t thread_reference)
{
 if(kind>=5)return 0;
 (void)r1_subscriber_lock();
 volatile uint8_t *root=r1_subscriber_roots[kind];
 if(!root){
  root=pvPortMalloc(12);
  if(!root)subscriber_allocation_failure();
  put(root,0);put(root+4,0);put(root+8,0);
  r1_subscriber_roots[kind]=(void *)(uintptr_t)root;
 }
 uint32_t node=word(root);
 while(node){
  const volatile uint8_t *entry=(const volatile uint8_t *)(uintptr_t)node;
  if(word(entry)==callback){(void)r1_subscriber_unlock();return 0;}
  node=word(entry+8);
 }
 volatile uint8_t *entry=pvPortMalloc(12);
 if(!entry)subscriber_allocation_failure();
 put(entry,callback);put(entry+8,0);
 if(!thread_reference)thread_reference=(uint32_t)(uintptr_t)&r1_event_sensor.thread;
 put(entry+4,thread_reference);
 if(word(root)){
  uint32_t tail=word(root+4);
  put((volatile uint8_t *)(uintptr_t)(tail+8u),(uint32_t)(uintptr_t)entry);
 }else put(root,(uint32_t)(uintptr_t)entry);
 put(root+4,(uint32_t)(uintptr_t)entry);
 (void)r1_subscriber_unlock();return 1;
}
