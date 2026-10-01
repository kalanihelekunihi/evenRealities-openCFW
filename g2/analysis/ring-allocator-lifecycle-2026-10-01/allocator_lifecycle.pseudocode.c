/* Manual behavioral recovery. Not original source, a full RTOS model, or patch.
 * Native structs are conceptual: stock Pool is 12 bytes with 32-bit pointers.
 * See validation.json for individual body hashes and exercised paths. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
typedef struct Block {struct Block *next;uint32_t marker;} Block;
typedef struct {uint16_t size;uint8_t count,pad;Block *start,*free;} Pool;
extern Pool *pools;extern uint8_t pool_count;
extern void enter_critical(void),exit_critical(void);
/* Stock compressed initializer produces config at 0x200003B0:
 * {16,8},{32,4},{64,10},{480,20}. WsfBufInit 0x00530364 rounds sizes up
 * to >=8 and multiples of 8, places 4*12 descriptor bytes then free lists.
 * Arena 0x2004FA98, supplied length 0x2940, actual consumed 0x2930.
 */
/* 0x00530446: first fitting nonempty pool, spills into larger pools. */
Block *stock_alloc(uint16_t size) {
 for(unsigned i=0;i<pool_count;i++)if(size<=pools[i].size) {
  enter_critical();Block *p=pools[i].free;
  if(p){pools[i].free=p->next;p->marker=0;exit_critical();return p;}
  exit_critical();
 }
 return NULL;
}
/* 0x005304D4: assumes valid allocated pointer; it does not validate upper
 * bounds, alignment or double-free. Do not use this as a safe host allocator. */
extern uint32_t free_marker;
void stock_free(Block *p) {
 for(unsigned i=pool_count;i>0;i--)if((uintptr_t)p>=(uintptr_t)pools[i-1].start) {
  enter_critical();p->marker=free_marker;p->next=pools[i-1].free;
  pools[i-1].free=p;exit_critical();return;
 }
}
/* 0x004BF99E: u16 allocator argument truncates sum. Oversized callers must
 * be rejected before this API: length 65528 causes allocator request zero. */
void *stock_message_alloc(uint16_t length) {
 uint8_t *p=(uint8_t *)stock_alloc((uint16_t)(length+8));return p?p+8:NULL;
}
void stock_message_free(void *message) {stock_free((Block *)((uint8_t *)message-8));}

/* 0x004C96B6: exits requested by thread flags, not direct deinit callbacks.
 * Indices correspond to the manager's readiness/exit bit assignments. */
extern void *task[13];
extern void set_thread_flags(void *,uint32_t);
uint32_t request_exit(uint32_t mode_flags) {
 set_thread_flags(task[1],0x800000);set_thread_flags(task[6],0x800000);
 set_thread_flags(task[11],0x800000);
 uint32_t mask=0x842;
 if(!(mode_flags&0x20)) {
  set_thread_flags(task[7],0x800000);set_thread_flags(task[8],0x800000);
  set_thread_flags(task[9],0x800000);mask=0xbc2;
 }
 set_thread_flags(task[3],0x800000);set_thread_flags(task[4],0x800000);
 set_thread_flags(task[5],0x800000);set_thread_flags(task[12],0x800000);
 return mask|0x1038;
}
/* 0x004C9778: timeout does not block subsequent return or retry automatically. */
extern uint32_t wait_exit_flags(uint32_t,unsigned,unsigned);
extern void log_exit_mismatch(uint32_t,uint32_t);
void wait_requested_exit(uint32_t mode) {
 uint32_t expected=request_exit(mode);
 uint32_t observed=wait_exit_flags(expected,1,5000); /* kernel ticks */
 if(observed!=expected)log_exit_mismatch(observed,expected);
}
/* 0x004C995E: retained diagnostic labels establish mode names. */
static bool ota_already_requested;
void manager_mode_events(uint32_t flags) {
 if((flags&0x20)&&!ota_already_requested){ota_already_requested=true;wait_requested_exit(flags);}
 if(flags&1)wait_requested_exit(flags); /* poweroff */
 if(flags&2)wait_requested_exit(flags); /* reboot */
 if(flags&4)wait_requested_exit(flags); /* ship mode */
 if(flags&8)wait_requested_exit(flags); /* low power */
 if(flags&16)wait_requested_exit(flags); /* temperature abnormal */
}
/* 0x004C507E excerpt: queue bit processed before exit bit if both present. */
extern void drain_ring_input_queue(void),publish_exit_ack(unsigned);
extern void *ring_input_queue;
extern void delete_queue(void *),delay_ticks(uint32_t);
void ring_flags_excerpt(uint32_t flags) {
 if(flags&0x400000)drain_ring_input_queue();
 /* Other functional flag branches omitted; they precede exit as well. */
 if(flags&0x800000) {
  /* 0x004C53A6 -> 0x004C9C3C: ack bit6 is set BEFORE deleting input queue. */
  publish_exit_ack(6);
  if(ring_input_queue){delete_queue(ring_input_queue);ring_input_queue=NULL;}
  for(;;)delay_ticks(UINT32_MAX);
 }
}
/* Ring input queue != global WSF queue. This exit has no WSF queue barrier.
 * It stops the ring task at delay, but does not prove AT/other producers stopped.
 * Stored deinit callbacks were recovered from initialized SRAM; no call to them
 * is present in these manager event paths. Final reset/poweroff lies outside
 * this bounded reconstruction. */
