/* Native callbacks0x70778/0x707cc. Completion/error/ready bytes intentionally
 * differ between buses. Unknown event codes retain the previous result word. */
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
extern int32_t osKernelGetState(void),osSemaphoreRelease(void *);
_Static_assert(sizeof(r1_hw_twi_cluster)==108 && offsetof(r1_hw_twi_cluster,record)==12,"native cluster");
static uint32_t completion(volatile r1_hw_twi_control *control,const volatile uint8_t *event,uint32_t primary) {
 uint32_t code=event[0];control->state_00=1;
 if(primary && code!=0)control->state_01=1;
 if(code==0)control->reserved_08=0;
 else if(code==1)control->reserved_08=5;
 else if(code==2)control->reserved_08=7;
 uint32_t ready=primary?control->state_02:control->state_01;
 if(!ready)return 0;
 if(!control->semaphore)return 0;
 int32_t state=osKernelGetState();
 if(state==2 || state==3)return (uint32_t)osSemaphoreRelease(control->semaphore);
 return (uint32_t)state;
}
uint32_t r1_hw_twi0_irq(const volatile uint8_t *event) {return completion(&r1_hw_twi0.control,event,1);}
uint32_t r1_hw_twi1_irq(const volatile uint8_t *event) {return completion(&r1_hw_twi1.control,event,0);}
