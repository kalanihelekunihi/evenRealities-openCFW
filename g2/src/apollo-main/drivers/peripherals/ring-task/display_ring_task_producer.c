/* Native Main thread_ring_queue_init/create/terminate
 * 0x4c4d66/0x4c4da4/0x4c4dd0.
 * ROM 0x75b8a4 authenticates the CMSIS thread attributes and RAM extents. */
#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
_Static_assert(sizeof(struct ring_thread_manager)==16u,"ring manager ABI");
struct thread_attrs {const char *name;uint32_t bits;void *cb;uint32_t cb_size;
                     void *stack;uint32_t stack_size;uint32_t priority;
                     uint32_t tz;uint32_t reserved;};
extern struct ring_thread_manager audio_uart_ring_thread_manager; /* RAM 0x20004120 */
extern uint8_t audio_uart_ring_thread_cb[112]; /* RAM 0x20072290 */
extern uint8_t audio_uart_ring_thread_stack[4096]; /* RAM 0x2036be40 */
extern void thread_ring_entry(void *);
extern void *audio_queue_new(uint32_t,uint32_t,const void *); /* selected 0x449a32 */
extern void *audio_thread_new(void (*)(void *),void *,const void *); /* selected 0x4490e2 */
extern int32_t audio_thread_terminate_peer(void *); /* selected 0x4491fe */
extern uint32_t audio_wsf_interrupt_mask_set(void); /* selected 0x5fa0a4 */
static const char task_name[]="ring";
static const struct thread_attrs task_attrs={task_name,0u,audio_uart_ring_thread_cb,112u,
    audio_uart_ring_thread_stack,4096u,46u,1u,0u};
static void native_allocation_failure(void) {
    (void)audio_wsf_interrupt_mask_set();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    for(;;){}
}
void thread_ring_queue_init(void) {
    audio_uart_ring_thread_manager.queue=audio_queue_new(3u,4u,0);
    if(audio_uart_ring_thread_manager.queue==0)native_allocation_failure();
}
void thread_ring_create(void) {
    audio_uart_ring_thread_manager.thread=audio_thread_new(thread_ring_entry,0,&task_attrs);
    if(audio_uart_ring_thread_manager.thread==0)native_allocation_failure();
}
void thread_ring_terminate(void) {
    if(audio_uart_ring_thread_manager.thread!=0) {
        (void)audio_thread_terminate_peer(audio_uart_ring_thread_manager.thread);
        audio_uart_ring_thread_manager.thread=0;
    }
}
