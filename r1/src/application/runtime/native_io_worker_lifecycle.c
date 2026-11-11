/* Stock BLE lifecycle 0x44f20/0x44ec0 and touch 0x46e7c/0x46e64. */
#include <stdint.h>
#include "cmsis_os2.h"
#include "../board/native_task_contexts.h"
extern void *volatile r1_protocol_service_thread,*volatile r1_touch_task_thread_handle;
extern _Noreturn void r1_ble_io_worker(void *),r1_touch_io_worker(void *);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
uint8_t r1_ble_io_tcb[112] __attribute__((section(".bss.r1.ble.io.tcb"),aligned(8)));
uint8_t r1_ble_io_stack[4096] __attribute__((section(".bss.r1.ble.io.stack"),aligned(8)));
uint8_t r1_touch_io_tcb[112] __attribute__((section(".bss.r1.touch.io.tcb"),aligned(8)));
uint8_t r1_touch_io_stack[4096] __attribute__((section(".bss.r1.touch.io.stack"),aligned(8)));
const osThreadAttr_t r1_ble_io_attributes={.name="ble",.cb_mem=r1_ble_io_tcb,.cb_size=112,
 .stack_mem=r1_ble_io_stack,.stack_size=4096,.priority=(osPriority_t)52,.tz_module=1};
const osThreadAttr_t r1_touch_io_attributes={.name="touch",.cb_mem=r1_touch_io_tcb,.cb_size=112,
 .stack_mem=r1_touch_io_stack,.stack_size=4096,.priority=(osPriority_t)49,.tz_module=1};
void r1_thread_create_c(void)
{
 osThreadId_t thread=osThreadNew(r1_ble_io_worker,NULL,&r1_ble_io_attributes);
 r1_protocol_service_thread=thread;
 if (!thread) r1_bae8_rx_allocation_fault();
}
void r1_task_stop_6568(void)
{
 osThreadId_t thread=r1_protocol_service_thread;
 if (thread) {(void)osThreadTerminate(thread);r1_protocol_service_thread=NULL;}
}
void r1_touch_io_create(void)
{
 osThreadId_t thread=osThreadNew(r1_touch_io_worker,NULL,&r1_touch_io_attributes);
 r1_touch_task_thread_handle=thread;
 if (!thread) r1_bae8_rx_allocation_fault();
}
void r1_touch_io_stop(void)
{
 osThreadId_t thread=r1_touch_task_thread_handle;
 if (thread) {(void)osThreadTerminate(thread);r1_touch_task_thread_handle=NULL;}
}
struct r1_task_lifecycle r1_ble_io_lifecycle
 __attribute__((section(".r1.ble.io.lifecycle"),aligned(4)))={r1_thread_create_c,r1_task_stop_6568};
struct r1_task_lifecycle r1_touch_io_lifecycle
 __attribute__((section(".r1.touch.io.lifecycle"),aligned(4)))={r1_touch_io_create,r1_touch_io_stop};
