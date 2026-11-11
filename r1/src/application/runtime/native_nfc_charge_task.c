/* Stock 0x924f4 worker and 0x45fbc/0x45fd4 lifecycle, named by the
 * authenticated nfc_charge thread attributes. Hardware children stay explicit. */
#include <stddef.h>
#include <stdint.h>
#include "cmsis_os2.h"
#include "../board/native_task_contexts.h"
extern void *volatile r1_battery_thread_handle;
extern void r1_native_sync_wait(uint32_t),r1_native_sync_signal(uint32_t);
extern uint32_t r1_native_watchdog_register(const char *,uint32_t);
extern void r1_native_watchdog_arm(uint32_t),r1_native_watchdog_disarm(uint32_t);
extern void r1_native_watchdog_feed(uint32_t);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
extern void r1_battery_initialize_000912a8(void);
extern void r1_battery_periodic_schedule_00091174(void);
extern void r1_pmic_late_init_plan_build(void);
extern void r1_nfc_charge_task_plan_build(uint32_t);
osMessageQueueId_t volatile r1_nfc_charge_task_queue
 __attribute__((section(".r1.nfc.charge.queue"),aligned(4)))=0;
uint32_t volatile r1_nfc_charge_task_watchdog
 __attribute__((section(".r1.nfc.charge.watchdog"),aligned(4)))=0;
uint8_t r1_nfc_charge_task_tcb[112]
 __attribute__((section(".bss.r1.nfc.charge.tcb"),aligned(8)));
uint8_t r1_nfc_charge_task_stack[4096]
 __attribute__((section(".bss.r1.nfc.charge.stack"),aligned(8)));
const char r1_nfc_charge_task_name[]="nfc_charge";
_Static_assert(sizeof(osThreadAttr_t)==36 && offsetof(osThreadAttr_t,priority)==24,
               "stock CMSIS attributes");
const osThreadAttr_t r1_nfc_charge_task_attributes={
 .name=r1_nfc_charge_task_name,.cb_mem=r1_nfc_charge_task_tcb,.cb_size=112,
 .stack_mem=r1_nfc_charge_task_stack,.stack_size=4096,
 .priority=(osPriority_t)28,.tz_module=1
};
_Noreturn void r1_system_task_plan_startup(void *argument)
{
 (void)argument;
 r1_native_sync_wait(1);
 osMessageQueueId_t queue=osMessageQueueNew(50,44,NULL);
 r1_nfc_charge_task_queue=queue;
 if(!queue)r1_bae8_rx_allocation_fault();
 r1_battery_initialize_000912a8();
 r1_battery_periodic_schedule_00091174();
 r1_pmic_late_init_plan_build();
 r1_native_sync_signal(1);
 r1_nfc_charge_task_watchdog=r1_native_watchdog_register(r1_nfc_charge_task_name,10000);
 for(;;){
  r1_native_watchdog_arm(r1_nfc_charge_task_watchdog);
  uint32_t flags=osThreadFlagsWait(0x00ffffff,0,UINT32_MAX);
  r1_native_watchdog_disarm(r1_nfc_charge_task_watchdog);
  if(flags-1u<UINT32_C(0x7fffffff))r1_nfc_charge_task_plan_build(flags);
  r1_native_watchdog_feed(r1_nfc_charge_task_watchdog);
 }
}
void r1_system_task_create(void)
{
 osThreadId_t thread=osThreadNew(r1_system_task_plan_startup,NULL,
                               &r1_nfc_charge_task_attributes);
 r1_battery_thread_handle=thread;
 if(!thread)r1_bae8_rx_allocation_fault();
}
void r1_system_task_stop(void)
{
 osThreadId_t thread=r1_battery_thread_handle;
 if(thread){(void)osThreadTerminate(thread);r1_battery_thread_handle=NULL;}
}
struct r1_nfc_charge_lifecycle r1_nfc_charge_lifecycle
 __attribute__((section(".r1.nfc.charge.lifecycle"),aligned(4)))={
 r1_system_task_create,r1_system_task_stop
};
