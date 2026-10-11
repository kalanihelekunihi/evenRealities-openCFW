/* FreeRTOS task TCB setup, stock 0x454938. */
#include <stdint.h>
#include <stddef.h>
typedef void (*thread_entry)(void *);
extern void g2_log_stack_fill(char *destination,uint32_t count,uint8_t value);
extern void *g2_thread_initialize_stack(void *top,void *base,
                                         thread_entry entry,void *argument);
extern void g2_thread_assert_failure(void) __attribute__((noreturn));
void g2_thread_initialize_tcb(thread_entry entry,const char *name,
                              uint32_t depth,void *argument,
                              uint32_t priority,void **created,
                              void *control,uint32_t unused) {
    (void)unused;
    uint8_t *tcb=(uint8_t *)control;
    uint8_t *base=*(uint8_t **)(void *)(tcb+0x30u);
    g2_log_stack_fill((char *)base,depth*4u,0xa5u);
    uintptr_t top=((uintptr_t)base+depth*4u-4u)&~(uintptr_t)7u;
    if((top&7u)!=0u) g2_thread_assert_failure();
    *(uint32_t *)(void *)(tcb+0x54u)=depth;
    if(name) {
        uint32_t i=0;
        while(i<32u) {
            char c=name[i];tcb[0x34u+i]=(uint8_t)c;
            if(c==0) break;
            i++;
        }
        tcb[0x53u]=0;
    }
    if(priority>=56u) g2_thread_assert_failure();
    *(uint32_t *)(void *)(tcb+0x2cu)=priority;
    *(uint32_t *)(void *)(tcb+0x60u)=priority;
    *(uint32_t *)(void *)(tcb+0x14u)=0;
    *(uint32_t *)(void *)(tcb+0x28u)=0;
    *(void **)(void *)(tcb+0x10u)=tcb;
    *(uint32_t *)(void *)(tcb+0x18u)=56u-priority;
    *(void **)(void *)(tcb+0x24u)=tcb;
    *(void **)(void *)tcb=g2_thread_initialize_stack((void *)top,base,entry,argument);
    if(created) *created=tcb;
}
