/* Native hardware-TWI registration contracts at0x54f90/0x54fc4.
 * Operation/IRQ symbols below are metadata bindings, not admitted bodies/ABIs. */
#include <stdint.h>
#include "../registry/stock_registry.h"
typedef void (*r1_hw_metadata_fn)(void);
extern void r1_hw_twi0_open(void),r1_hw_twi0_close(void),r1_hw_twi0_read(void),r1_hw_twi0_write(void),r1_hw_twi0_irq(void);
extern void r1_hw_twi1_open(void),r1_hw_twi1_close(void),r1_hw_twi1_read(void),r1_hw_twi1_write(void),r1_hw_twi1_irq(void);
extern void *osSemaphoreNew(uint32_t,uint32_t,const void *);
typedef struct {uint8_t state_00,state_01,state_02,padding;void *semaphore;uint32_t reserved_08;} r1_hw_twi_control;
typedef struct {
 const char *name;uint8_t opened,padding[3];uint32_t pin_08,pin_0c,instance_id;
 uintptr_t peripheral;uint32_t driver_index,use_dma;r1_hw_metadata_fn irq;
 generic_device_registry_device device;r1_hw_metadata_fn ops[9];
} r1_hw_twi_record;
typedef struct {r1_hw_twi_control control;r1_hw_twi_record record;} r1_hw_twi_cluster;
_Static_assert(sizeof(r1_hw_twi_record)==96 && sizeof(r1_hw_twi_cluster)==108,"native TWI extents");
_Static_assert(offsetof(r1_hw_twi_record,device)==36 && offsetof(r1_hw_twi_record,ops)==60,"native device/ops slots");
const char r1_hw_twi0_name[] __attribute__((section(".r1.hw_twi.name0")))="i2c_0";
const char r1_hw_twi1_name[] __attribute__((section(".r1.hw_twi.name1")))="i2c_1";
r1_hw_twi_cluster r1_hw_twi0 __attribute__((section(".r1.hw_twi.primary")))={.record={
 .name=r1_hw_twi0_name,.pin_08=12,.pin_0c=1,.instance_id=0,.peripheral=0x40003000,.driver_index=0,.use_dma=1,.irq=r1_hw_twi0_irq,
 .ops={[2]=r1_hw_twi0_open,[3]=r1_hw_twi0_close,[4]=r1_hw_twi0_read,[5]=r1_hw_twi0_write}}};
r1_hw_twi_cluster r1_hw_twi1 __attribute__((section(".r1.hw_twi.secondary")))={.record={
 .name=r1_hw_twi1_name,.pin_08=11,.pin_0c=14,.instance_id=1,.peripheral=0x40004000,.driver_index=1,.use_dma=1,.irq=r1_hw_twi1_irq,
 .ops={[2]=r1_hw_twi1_open,[3]=r1_hw_twi1_close,[4]=r1_hw_twi1_read,[5]=r1_hw_twi1_write}}};
static uint32_t initialize(r1_hw_twi_cluster *cluster,uint8_t *flag) {
 cluster->record.device.name=cluster->record.name;
 cluster->record.device.ops=(const void *)cluster->record.ops;
 (void)r1_stock_registry_register(&cluster->record.device);
 void *semaphore=osSemaphoreNew(1,0,0);
 cluster->control.semaphore=semaphore;
 if (semaphore) {*flag=1;return 1;}
 return 0; /* Native leaves a previously set ready flag intact on failure. */
}
uint32_t r1_twi_primary_device_binding_configuration(void) {return initialize(&r1_hw_twi0,&r1_hw_twi0.control.state_02);}
uint32_t r1_twi_secondary_device_binding_configuration(void) {return initialize(&r1_hw_twi1,&r1_hw_twi1.control.state_01);}
