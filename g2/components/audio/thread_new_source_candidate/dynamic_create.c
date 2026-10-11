/* Experimental FreeRTOS dynamic task constructor, stock 0x4548ba.
 * Heap calls are selected; TCB initialization/scheduling are typed lowers. */
#include <stdint.h>
#include <stddef.h>
typedef void (*thread_entry)(void *);
extern void *pvPortMalloc(uint32_t bytes);
extern void vPortFree(void *ptr);
extern void g2_thread_initialize_tcb(thread_entry,const char *,uint32_t,
                                       void *,uint32_t,void **,void *,uint32_t);
extern void g2_thread_schedule_tcb(void *);
int32_t g2_thread_create_dynamic(thread_entry entry,const char *name,
                                  uint16_t depth,void *argument,
                                  uint32_t priority,void **created) {
    void *stack=pvPortMalloc((uint32_t)depth*4u);
    if(!stack) return -1;
    uint8_t *tcb=(uint8_t *)pvPortMalloc(0x70u);
    if(!tcb) {vPortFree(stack);return -1;}
    for(uint32_t i=0;i<0x70u;i++) tcb[i]=0;
    *(void **)(void *)(tcb+0x30u)=stack;
    tcb[0x6du]=0;
    g2_thread_initialize_tcb(entry,name,depth,argument,priority,created,
                              tcb,0u);
    g2_thread_schedule_tcb(tcb);
    return 1;
}
