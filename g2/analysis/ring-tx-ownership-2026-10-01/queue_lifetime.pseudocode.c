/* Manual behavioral pseudocode; NOT original source or a firmware patch.
 * Addresses refer to the authenticated s200_v2.2.6.10 application payload.
 * Native structs are conceptual; stock pointers are 32 bits.
 * Logging, timer dispatch details and unrelated message handling are omitted.
 */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
typedef struct Message {
 uint16_t connection;uint8_t event,status;
 const uint8_t *borrowed_payload;uint16_t length,unused;
} Message; /* stock size 12, not sizeof(Message) on a 64-bit host */
typedef struct {uint16_t write,notify,cccd;} Handles;
extern uint8_t ring_connection,ring_handler;
extern uint16_t ring_epoch;
extern Handles *ring_handles;
extern void *WsfBufAlloc(unsigned);
extern void WsfBufFree(void *);
extern void WsfQueueEnq(void *,void *),*WsfQueueDeq(void *);
extern void WsfCsEnter(void),WsfCsExit(void),WsfSetOsSpecificEvent(void);
extern uint8_t wsf_ready;
extern void *wsf_queue;
extern void (*handlers[10])(unsigned,void *);
extern void AttcWriteCmd(uint8_t,uint16_t,uint16_t,const void *);
extern void tx_wait(void),tx_complete(void);

/* 0x004BF99E: WSF private prefix occupies eight bytes before public message. */
void *message_alloc(uint16_t length) {
 uint8_t *base=WsfBufAlloc((unsigned)length+8);
 return base?base+8:NULL;
}
/* 0x004BF9B0: no nested pointer traversal or payload destructor. */
void message_free(void *msg) {WsfBufFree((uint8_t *)msg-8);}
/* 0x004BF9DE and 0x004BF9BA. Queue is intrusive; no enqueue allocation,
 * capacity result, or rollback status occurs in these bodies. */
void message_send(uint8_t handler,void *msg) {
 ((uint8_t *)msg)[-4]=handler;
 WsfQueueEnq(wsf_queue,(uint8_t *)msg-8);
 WsfCsEnter();wsf_ready|=1;WsfCsExit();WsfSetOsSpecificEvent();
}
/* 0x004BF9EC */
void *message_dequeue(uint8_t *handler) {
 uint8_t *base=WsfQueueDeq(wsf_queue);
 if(!base)return NULL;
 *handler=base[4];return base+8;
}
/* 0x0052B9D0 queued-message branch. Stock repeats while ready bits are set;
 * timer callbacks and handler-only events are separate, not auto-freed here. */
void dispatch_queued_messages_excerpt(void) {
 uint8_t handler;void *msg;
 while((msg=message_dequeue(&handler))!=NULL) {
  handlers[handler](0,msg); /* ring handler wrapper: 0x004A19C0 */
  message_free(msg); /* stock BL at 0x0052BA08, after indirect call returns */
 }
}
/* Existing producer at 0x004C4B7E. Gate occurs before wait; the connection
 * field is read again afterward. No epoch is copied to the message. */
unsigned ring_send(const uint8_t *data,uint16_t length) {
 if(ring_connection && ring_handles && ring_handles->write) {
  tx_wait();
  Message *m=message_alloc(12);
  if(!m)tx_complete();
  else {
   m->event=0xac;m->connection=ring_connection;
   m->borrowed_payload=data;m->length=length;
   message_send(ring_handler,m);
  }
 }
 return 0;
}
/* 0x004C4910, event 0xAC only. No epoch comparison or payload free. */
void ring_queued_tx(const Message *m) {
 uint8_t conn=(uint8_t)m->connection;
 uint16_t handle=ring_handles?ring_handles->write:0;
 if(!conn || conn!=ring_connection || !handle)tx_complete();
 else AttcWriteCmd(conn,handle,m->length,m->borrowed_payload);
 /* Return to WSF dispatcher: it frees only the message allocation. */
}
/* 0x00476ACE: cancellation of delayed callbacks, separate from WSF queue.
 * Mutex error diagnostics do not abort the stock table scan. */
extern uintptr_t delayed_callbacks[64];
extern bool delayed_initialized;
extern void delayed_lock(void),delayed_unlock(void),stop_delay_timer(void);
extern uint32_t kernel_ticks(void),delay_epoch;
extern void reschedule_delays(uint32_t); /* 0x004767A8, external test boundary */
bool remove_delayed(uintptr_t callback) {
 if(!delayed_initialized)return false;
 bool found=false;delayed_lock();
 for(unsigned i=0;i<64;i++)if(delayed_callbacks[i]==callback) {
  delayed_callbacks[i]=0;found=true;
 }
 delayed_unlock();
 if(found){uint32_t now=kernel_ticks();stop_delay_timer();reschedule_delays((now-delay_epoch)|0xff000000);}
 return found;
}
/* Close branch, 0x004C4910. Central-role guard is omitted from this excerpt.
 * Original instructions only alter connection/handles, cancel delayed CCCD,
 * and post ring event 8. They do not scan the WSF message queue. */
extern uintptr_t cccd_callback;
extern void ring_event(unsigned);
void ring_close_excerpt(void) {
 ring_connection=0;++ring_epoch;
 if(ring_handles)ring_handles->write=ring_handles->notify=ring_handles->cccd=0;
 remove_delayed(cccd_callback);ring_event(8);
}
/* 0x004C4DD0 / 0x004D0B1C. The BLE callback-manager deinit is an explicit
 * external boundary. These local wrappers have no WSF queue drain. */
extern void terminate_thread(void *),callback_manager_deinit(void);
void ring_terminate(void **thread) {if(*thread){terminate_thread(*thread);*thread=NULL;}}
void ble_wsf_terminate(void **thread) {callback_manager_deinit();ring_terminate(thread);}
/* Static task attributes, consumed by original osThreadNew at 0x004490E2:
 * ring:    0x0075B8A4, entry 0x004C4CED, priority 46, stack 4096 bytes.
 * ble_wsf: 0x0075B838, entry 0x004D0A4D, priority 49, stack 16384 bytes.
 * Runtime scheduler/preemption is not reconstructed by this excerpt.
 */
