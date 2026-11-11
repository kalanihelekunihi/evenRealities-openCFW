/* Stock 0x45d7c: hardware/task startup and persistent manager loop.
 * Lower unimplemented services remain explicit dependencies. */
#include "native_application_manager.h"
#include "native_task_suspend.h"
#include "../board/native_clock_bootstrap.h"
extern uint32_t r1_structured_log_typed(uint32_t,const char *,...);
extern uint32_t r1_native_watchdog_hw_feed(void);
extern void r1_nordic_softdevice_resource_bootstrap_configuration(void);
extern void r1_eat_core_init(void),r1_storage_manager_initialize_731a0(void);
extern void r1_ep_plan_initialization(void),r1_task_startup(void);
extern void r1_task_suspend_barrier(void);
extern uint32_t r1_native_watchdog_register(const char *,uint32_t);
extern void r1_manager_logging_start_91504(void);
extern void r1_manager_event_dispatch_46004(uint32_t);
extern void r1_rtt_console_poll(void),r1_native_watchdog_feed(uint32_t);
extern void r1_native_watchdog_check(void);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
volatile uint8_t r1_application_manager_ready
 __attribute__((section(".r1.application.manager.ready")))=0;
const char r1_application_manager_start_message[]="[thread_manager]thread manager start";
void r1_application_manager_thread(void *argument)
{
 (void)argument;
 (void)r1_structured_log_typed(0x10000000u,r1_application_manager_start_message);
 (void)r1_native_watchdog_hw_feed();
 r1_nordic_softdevice_resource_bootstrap_configuration();
 (void)r1_clock_initialize(NULL,NULL);
 r1_eat_core_init();
 r1_storage_manager_initialize_731a0();
 r1_ep_plan_initialization();
 r1_task_startup();
 (void)r1_native_watchdog_hw_feed();
 osEventFlagsId_t flags=osEventFlagsNew(NULL);
 r1_native_sync_event_flags=flags;
 if(!flags)r1_bae8_rx_allocation_fault();
 (void)r1_native_watchdog_hw_feed();
 r1_task_suspend_barrier();
 (void)r1_native_watchdog_hw_feed();
 uint32_t watchdog=r1_native_watchdog_register("manager",10000);
 r1_application_manager_ready=1;
 r1_manager_logging_start_91504();
 for(;;){
  uint32_t events=osThreadFlagsWait(0x00ffffffu,osFlagsWaitAny,500);
  if((uint32_t)(events-1u)<0x7fffffffu)
   r1_manager_event_dispatch_46004(events);
  r1_rtt_console_poll();
  r1_native_watchdog_feed(watchdog);
  r1_native_watchdog_check();
 }
}
