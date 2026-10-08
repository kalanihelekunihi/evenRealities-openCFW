/* Independent selected nonblocking/negative-callback reconstruction.
 * Original scheduler query/critical providers and callback bodies remain peers. */
#include "consumer.h"
extern int32_t case_scheduler_state(void);
extern void case_enter_critical(void),case_exit_critical(void),case_yield_request(void);
extern int32_t case_remove_waiter(case_list *);
int32_t case_receive_nowait(case_queue *q,void *out){
 (void)case_scheduler_state();case_enter_critical();
 if(q->messages){case_copy_from_queue(q,out);q->messages--;
  if(q->send_wait.count && case_remove_waiter(&q->send_wait))case_yield_request();
  case_exit_critical();return 1;
 }
 case_exit_critical();return 0;
}
void case_drain_negative_callbacks(void){
 case_deferred_message m;case_queue *q=*(case_queue **)0x20000164u;
 while(case_receive_nowait(q,&m)){
  if(m.command>=0)return; /* Outside this helper's declared contract, not timer semantics. */
  ((void(*)(uint32_t,uint32_t))(uintptr_t)m.callback)(m.arg1,m.arg2);
 }
}
