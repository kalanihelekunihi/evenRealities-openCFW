/* Stock 0x45e64 launch, 0x45e90 transient thread and 0x45e4c stop.
 * The manager worker is a separate, explicit source dependency. */
#include <stddef.h>
#include "cmsis_os2.h"
#include "native_application_launch.h"
#include "native_application_manager.h"
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
_Static_assert(sizeof(osThreadAttr_t)==36 && offsetof(osThreadAttr_t,stack_size)==20 &&
               offsetof(osThreadAttr_t,priority)==24,"native CMSIS attributes");
_Static_assert(sizeof(struct r1_application_lifecycle)==12 &&
               offsetof(struct r1_application_lifecycle,thread)==8,"native lifecycle");
uint8_t r1_application_manager_tcb[112]
 __attribute__((section(".bss.r1.application.manager.tcb"),aligned(8)));
uint8_t r1_application_manager_stack[2048]
 __attribute__((section(".bss.r1.application.manager.stack"),aligned(8)));
const char r1_application_manager_name[]="manager";
const osThreadAttr_t r1_application_manager_attributes
 __attribute__((section(".r1.application.manager.attributes"),aligned(4)))={
 .name=r1_application_manager_name,.cb_mem=r1_application_manager_tcb,.cb_size=112,
 .stack_mem=r1_application_manager_stack,.stack_size=2048,
 .priority=(osPriority_t)53,.tz_module=1
};
struct r1_application_lifecycle r1_application_lifecycle
 __attribute__((section(".r1.application.lifecycle"),aligned(4)))={
 r1_application_launch,r1_application_manager_stop,NULL
};
void r1_application_launch(void)
{
 (void)osKernelInitialize();
 if(!osThreadNew(r1_application_startup_thread,NULL,NULL))
  r1_bae8_rx_allocation_fault();
 (void)osKernelStart();
}
void r1_application_startup_thread(void *argument)
{
 (void)argument;
 osThreadId_t thread=osThreadNew(r1_application_manager_thread,NULL,
                               &r1_application_manager_attributes);
 r1_application_lifecycle.thread=thread;
 if(!thread)r1_bae8_rx_allocation_fault();
 (void)osThreadTerminate(osThreadGetId());
}
void r1_application_manager_stop(void)
{
 osThreadId_t thread=r1_application_lifecycle.thread;
 if(thread){
  (void)osThreadTerminate(thread);
  r1_application_lifecycle.thread=NULL;
 }
}
