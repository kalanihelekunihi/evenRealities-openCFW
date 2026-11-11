/* Stock R1 0x45054; native CMSIS attributes at 0x99240. */
#include <stdint.h>
#include <stddef.h>
struct r1_bae8_thread_attr {
    const char *name;uint32_t attr_bits;void *cb_mem;uint32_t cb_size;
    void *stack_mem;uint32_t stack_size;int32_t priority;uint32_t tz_module,reserved;
};
_Static_assert(sizeof(struct r1_bae8_thread_attr)==36,"native CMSIS thread attributes");
extern void *osThreadNew(void (*)(void *),void *,const struct r1_bae8_thread_attr *);
extern void *volatile r1_bae8_rx_thread;
extern _Noreturn void r1_bae8_input_task_plan_startup(void *);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
uint8_t r1_bae8_rx_tcb[112] __attribute__((section(".bss.r1.bae8.rx.tcb"),aligned(8)));
uint8_t r1_bae8_rx_stack[5120] __attribute__((section(".bss.r1.bae8.rx.stack"),aligned(8)));
const char r1_bae8_rx_thread_name[] __attribute__((section(".r1.bae8.rx.name")))="ble_msgrx";
const struct r1_bae8_thread_attr r1_bae8_rx_thread_attributes
 __attribute__((section(".r1.bae8.rx.attributes"),aligned(4)))={
    r1_bae8_rx_thread_name,0,r1_bae8_rx_tcb,112,r1_bae8_rx_stack,5120,51,1,0
};
void r1_thread_create_d(void)
{
    void *thread=osThreadNew(r1_bae8_input_task_plan_startup,0,&r1_bae8_rx_thread_attributes);
    r1_bae8_rx_thread=thread;
    if (!thread) r1_bae8_rx_allocation_fault();
}

/* Native RW prefix at 0x20006590; adjacent handles retain their existing owners. */
void r1_thread_create_d(void);
extern void r1_task_stop_6590(void);
#include "../board/native_task_contexts.h"
_Static_assert(sizeof(struct r1_bae8_rx_lifecycle)==8,"native lifecycle prefix");
struct r1_bae8_rx_lifecycle r1_bae8_rx_lifecycle
 __attribute__((section(".r1.bae8.rx.lifecycle"),aligned(4)))={r1_thread_create_d,r1_task_stop_6590};
