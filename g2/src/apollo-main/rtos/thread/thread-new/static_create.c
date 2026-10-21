/* Experimental static task constructor, stock 0x454820. The caller supplies
 * the 0x70-byte TCB and stack; allocator/product object remain caller-owned. */
#include <stdint.h>
typedef void (*thread_entry)(void *);
extern void g2_thread_assert_failure(void) __attribute__((noreturn));
extern void g2_thread_initialize_tcb(thread_entry,const char *,uint32_t,
                                       void *,uint32_t,void **,void *,uint32_t);
extern void g2_thread_schedule_tcb(void *);
void *audio_daemon_create_static(thread_entry entry,const char *name,
                                  uint32_t depth,void *argument,
                                  uint32_t priority,void *stack,void *control) {
    if(!stack || !control) g2_thread_assert_failure();
    uint8_t *tcb=(uint8_t *)control;
    for(uint32_t i=0;i<0x70u;i++) tcb[i]=0;
    *(void **)(void *)(tcb+0x30u)=stack;
    tcb[0x6du]=2u;
    void *created=0;
    g2_thread_initialize_tcb(entry,name,depth,argument,priority,
                              &created,tcb,0u);
    g2_thread_schedule_tcb(tcb);
    return created;
}
