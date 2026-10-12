extern uint32_t opencfw_em9305_scan_available_307b9c(void);
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
/* Native30b9f4..30ba84: product mirror before gate, genuine16x16 DSP products. */
uint32_t opencfw_em9305_command_scan_params_30b9f4(uint32_t first,uint32_t second,uint32_t interval,uint32_t duration)
{
 uintptr_t root=0x805a70u;
 uint32_t prior=*(volatile uint8_t *)(root+12u);
 *(volatile uint8_t *)(root+14u)=0u;
 *(volatile uint8_t *)(root+13u)=(uint8_t)prior;
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)goto gate_error;
 if(first==1u){
  if(second>=3u)goto argument_error;
  if(second==2u&&(interval==0u||duration==0u))goto argument_error;
 }
 uint32_t interval_ticks,duration_ticks;
 __asm__ volatile("mpyuw %0,%1,10":"=r"(interval_ticks):"r"(interval));
 __asm__ volatile("mpyuw %0,%1,1280":"=r"(duration_ticks):"r"(duration));
 if(interval!=0u&&first==1u&&duration!=0u&&interval_ticks>=duration_ticks)goto argument_error;
 if(opencfw_em9305_scan_available_307b9c()==0u)goto argument_error;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(16u);
 if(message==0u)return 0u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint32_t *)(message+12u)=duration_ticks;
 *(volatile uint32_t *)(message+8u)=interval_ticks;
 *(volatile uint8_t *)(message+4u)=(uint8_t)second;
 *(volatile uint8_t *)(message+3u)=(uint8_t)((first==0u)+1u);
 *(volatile uint8_t *)(message+2u)=7u;
 return opencfw_em9305_wsf_task_message_send(handler,message);
 gate_error:
 *(volatile uint8_t *)(root+13u)=1u;return opencfw_em9305_scan_error_30e7f8(12u);
 argument_error:
 *(volatile uint8_t *)(root+13u)=1u;return opencfw_em9305_scan_error_30e7f8(18u);
}
