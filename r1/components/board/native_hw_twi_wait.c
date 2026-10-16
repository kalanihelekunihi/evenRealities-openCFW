/* Native0x70820/0x7088c product wait policy. CMSIS and the Nordic subtract-three
 * primitive stay existing upstream providers; no local kernel/semaphore clone. */
#include <stdint.h>
#include "../registry/stock_registry.h"
typedef void (*r1_hw_metadata_fn)(void);
typedef struct {uint8_t state_00,state_01,state_02,padding;void *semaphore;uint32_t reserved_08;} r1_hw_twi_control;
typedef struct {
 const char *name;uint8_t opened,padding[3];uint32_t pin_08,pin_0c,instance_id;
 uintptr_t peripheral;uint32_t driver_index,use_dma;r1_hw_metadata_fn irq;
 generic_device_registry_device device;r1_hw_metadata_fn ops[9];
} r1_hw_twi_record;
typedef struct {r1_hw_twi_control control;r1_hw_twi_record record;} r1_hw_twi_cluster;
extern r1_hw_twi_cluster r1_hw_twi0,r1_hw_twi1;
extern int32_t osKernelGetState(void),osSemaphoreAcquire(void *,uint32_t);
extern uint32_t osKernelGetTickFreq(void);
extern void r1_rtt_delay_cycles(uint32_t);
_Static_assert(sizeof(r1_hw_twi_cluster)==108 && offsetof(r1_hw_twi_cluster,record)==12,"native cluster");
static uint32_t wait_for(volatile r1_hw_twi_control *control,uint32_t readyoff,uint32_t milliseconds) {
 if(((volatile uint8_t *)control)[readyoff] && control->semaphore){
  int32_t state=osKernelGetState();
  if(state==2 || state==3){
   uint32_t ticks=(osKernelGetTickFreq()*milliseconds)/1000u;
   if(!ticks)ticks=1;
   if(osSemaphoreAcquire(control->semaphore,ticks))return 13;
   return control->reserved_08;
  }
 }
 uint32_t limit=milliseconds*1000u,counter=0;
 while(!control->state_00){
  uint32_t before=counter++;
  if(before>=limit)return 13;
  r1_rtt_delay_cycles(64);
 }
 return control->reserved_08;
}
uint32_t r1_twi_primary_wait_adapter(uint32_t milliseconds) {return wait_for(&r1_hw_twi0.control,2,milliseconds);}
uint32_t r1_twi_secondary_wait_adapter(uint32_t milliseconds) {return wait_for(&r1_hw_twi1.control,1,milliseconds);}
