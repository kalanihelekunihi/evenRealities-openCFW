/* Offline stock CMSIS/FreeRTOS wrapper reconstruction, not pristine-public attribution. */
#include "queue.h"
uint32_t audio_scheduler_state(void){
 if(!*(volatile uint32_t *)0x20074a3cu)return 1;
 return *(volatile uint32_t *)0x20074a58u?0:2;
}
uint32_t audio_cmsis_irq_context(void){
 uint32_t ipsr,primask,basepri;
 __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));if(ipsr)return 1;
 if(audio_scheduler_state()==1)return 0;
 __asm__ volatile("mrs %0, primask":"=r"(primask));if(primask)return 1;
 __asm__ volatile("mrs %0, basepri":"=r"(basepri));return basepri!=0;
}
int32_t audio_cmsis_queue_put(void *queue,const void *message,uint8_t priority,uint32_t timeout){
 (void)priority;
 if(audio_cmsis_irq_context()){
  if(!queue||!message||timeout)return -4;
  int32_t woke=0;if(xQueueGenericSendFromISR(queue,message,&woke,0)!=1)return -3;
  if(woke)*(volatile uint32_t *)0xe000ed04u=0x10000000;
  return 0;
 }
 if(!queue||!message)return -4;
 if(xQueueGenericSend(queue,message,timeout,0)!=1)return timeout?-2:-3;
 return 0;
}
/* Queue-buffer copy contract: valid nonoverlapping regions, no libc/original helper. */
void *audio_queue_copy_bytes(void *destination,const void *source,uint32_t size){
 uint8_t *d=destination;const uint8_t *s=source;
 for(uint32_t i=0;i<size;i++)d[i]=s[i];return destination;
}
