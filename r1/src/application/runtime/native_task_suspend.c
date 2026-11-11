/* Stock 0x46a74: signal the worker and wait for its acknowledgement bit. */
#include "native_task_suspend.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
const char r1_task_suspend_ring[]="[thread_manager]thread sync failed:0x%x, task:%d";
const char r1_task_suspend_sdk[]="thread sync failed:0x%x, task:%d";
void r1_task_suspend_handshake(osThreadId_t worker,uint32_t ordinal)
{
 /* ARM register shifts use the low byte and produce zero for counts >=32. */
 uint32_t shift=ordinal&255u;
 uint32_t bit=shift<32u ? UINT32_C(1)<<shift : 0;
 (void)osThreadFlagsSet(worker,UINT32_C(1)<<23);
 uint32_t result=osEventFlagsWait(r1_native_sync_event_flags,bit,
                                 osFlagsWaitAll,0x5000);
 if(bit&~result){
  if((r1_structured_log_mode_get()&1u) ||
     (r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x04800000,r1_task_suspend_ring,
                                r1_task_suspend_ring,result,ordinal);
  if(r1_structured_log_mode_get()&2u)
   nrf_log_frontend_std_2(0x001c0001,r1_task_suspend_sdk,result,ordinal);
 }
}
