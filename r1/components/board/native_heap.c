/* R1 heap4-family native extensions. Authenticated application contract:
 * init 0x84f98, insert 0x851a4, malloc 0x855a0, free 0x95d48.
 * FreeRTOS-Kernel 10.5.1 heap_4.c establishes lineage (MIT, see upstream
 * portable/MemMang/heap_4.c); this adapter preserves the observed R1 layout,
 * request rounding, caller tracking and fatal failure policy. */
#include <stdint.h>
#include <stddef.h>
typedef struct block { struct block *next; uint32_t size,caller; } block;
_Static_assert(sizeof(block)==12,"native sentinel; allocated header reserves 16 bytes");
typedef struct {block *end;uint32_t free_bytes,minimum,allocations,frees;} heap_state;
_Static_assert(sizeof(heap_state)==20,"native heap state");
__attribute__((section(".r1.heap.storage"),aligned(8))) uint8_t r1_heap_storage[51200];
__attribute__((section(".r1.heap.start"),aligned(8))) block r1_heap_start;
__attribute__((section(".r1.heap.state"),aligned(4))) heap_state r1_heap_state;
extern void vTaskSuspendAll(void);
extern int32_t xTaskResumeAll(void);
__attribute__((noreturn)) void r1_malloc_failed_hook(void){
 __asm volatile("msr basepri, %0"::"r"(64):"memory");
 *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
 for(;;){}
}
#define REQUIRE(x) do { if(!(x))r1_malloc_failed_hook(); } while(0)
void r1_heap_initialize(void){
 uintptr_t first=((uintptr_t)r1_heap_storage+7u)&~(uintptr_t)7u;
 block *end=(block *)(((uintptr_t)r1_heap_storage+sizeof(r1_heap_storage)-16u)&~(uintptr_t)7u);
 r1_heap_start.next=(block *)first;r1_heap_start.size=0;r1_heap_start.caller=0;
 r1_heap_state.end=end;end->size=0;end->next=0;end->caller=0;
 block *initial=(block *)first;initial->caller=0;initial->next=end;
 initial->size=(uint32_t)((uintptr_t)end-first);
 r1_heap_state.minimum=initial->size;r1_heap_state.free_bytes=initial->size;
}
void r1_heap_insert(block *value){
 block *previous=&r1_heap_start;
 while((uintptr_t)previous->next<(uintptr_t)value)previous=previous->next;
 block *next=previous->next;
 if((uintptr_t)previous+previous->size==(uintptr_t)value){previous->size+=value->size;value=previous;}
 if((uintptr_t)value+value->size==(uintptr_t)next){
  if(next!=r1_heap_state.end){value->size+=next->size;next=previous->next->next;}
  else next=r1_heap_state.end;
 }
 value->next=next;
 if(previous!=value)previous->next=value;
}
__attribute__((noinline)) void *pvPortMalloc(uint32_t requested){
 uint32_t caller=(uint32_t)(uintptr_t)__builtin_return_address(0);void *result=0;
 vTaskSuspendAll();
 if(!r1_heap_state.end)r1_heap_initialize();
 if(requested){
  uint32_t addition=24u-(requested&7u);
  if(requested>UINT32_MAX-addition || (int32_t)(requested+addition)<=0){(void)xTaskResumeAll();r1_malloc_failed_hook();}
  uint32_t wanted=requested+addition;
  if(wanted>r1_heap_state.free_bytes){(void)xTaskResumeAll();r1_malloc_failed_hook();}
  block *previous=&r1_heap_start,*value=previous->next;
  while(value->size<wanted && value->next){previous=value;value=value->next;}
  if(value==r1_heap_state.end){(void)xTaskResumeAll();r1_malloc_failed_hook();}
  result=(uint8_t *)previous->next+16;previous->next=value->next;
  uint32_t remainder=value->size-wanted;
  if(remainder>32){block *split=(block *)((uint8_t *)value+wanted);REQUIRE(!((uintptr_t)split&7u));split->size=remainder;split->caller=0;value->size=wanted;r1_heap_insert(split);}
  r1_heap_state.free_bytes-=value->size;
  if(r1_heap_state.free_bytes<r1_heap_state.minimum)r1_heap_state.minimum=r1_heap_state.free_bytes;
  value->caller=caller;value->next=0;value->size|=0x80000000u;r1_heap_state.allocations++;
 }
 (void)xTaskResumeAll();if(!result)r1_malloc_failed_hook();
 REQUIRE(!((uintptr_t)result&7u));return result;
}
void vPortFree(void *pointer){
 if(!pointer)return;
 block *value=(block *)((uint8_t *)pointer-16);
 REQUIRE(value->size&0x80000000u);REQUIRE(value->next==0);
 value->size&=0x7fffffffu;value->caller=0;
 vTaskSuspendAll();r1_heap_state.free_bytes+=value->size;r1_heap_insert(value);r1_heap_state.frees++;(void)xTaskResumeAll();
}
