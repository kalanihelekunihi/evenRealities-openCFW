#include <stdint.h>
#include "native_motion_operations.h"
#include "../registry/stock_registry.h"
extern generic_device_registry_device *volatile r1_motion_bus_device;
extern volatile uint32_t r1_motion_selected_provider;
extern uint32_t r1_lis2dw12_identity_probe(void),r1_bma456w_identity_probe(void),r1_qma6100_chip_id(void);
extern uint32_t r1_lis2dw12_configure_boundary(uint32_t),r1_bma456w_configure_boundary(uint32_t),r1_qma6100_configure_boundary(uint32_t);
extern uint32_t r1_qma6100_irq_boundary(void);
extern int32_t r1_lis2dw12_fifo_normalized(uint8_t *,uint32_t),r1_bma456w_fifo_normalized(uint8_t *,uint32_t),r1_qma6100_fifo_normalized(uint8_t *,uint32_t);
__attribute__((noinline)) uint32_t r1_motion_bus_acquire(void){return r1_stock_dispatch_08(r1_motion_bus_device);}
__attribute__((noinline)) uint32_t r1_motion_bus_release(void){return r1_stock_dispatch_0c(r1_motion_bus_device);}
/* Preserve provider results across bus release; acquisition errors are ignored
 * by stock, and do not suppress the provider call or final release. */
#define PROBE(name,provider) uint32_t name(void) { \
 (void)r1_motion_bus_acquire(); \
 uint32_t id = provider(); \
 (void)r1_motion_bus_release(); \
 return id; \
}
PROBE(r1_lis2dw12_probe_wrapper,r1_lis2dw12_identity_probe)
PROBE(r1_bma456w_probe_wrapper,r1_bma456w_identity_probe)
PROBE(r1_qma6100_probe_wrapper,r1_qma6100_chip_id)
#define CONFIG(name,provider) uint32_t name(void) { \
 (void)r1_motion_bus_acquire(); \
 uint32_t success = provider(25) != 0; \
 (void)r1_motion_bus_release(); \
 return success; \
}
CONFIG(r1_lis2dw12_configuration_wrapper,r1_lis2dw12_configure_boundary)
CONFIG(r1_bma456w_configuration_wrapper,r1_bma456w_configure_boundary)
CONFIG(r1_qma6100_configuration_wrapper,r1_qma6100_configure_boundary)
void r1_lis2dw12_interrupt_noop(void){}
void r1_bma456w_interrupt_noop(void){}
void r1_qma6100_interrupt_wrapper(void)
{
 (void)r1_motion_bus_acquire();
 (void)r1_qma6100_irq_boundary();
 (void)r1_motion_bus_release();
}
const r1_motion_table r1_motion_qma_table __attribute__((section(".r1.motion.qma.table"),aligned(4)))={
 .configure=r1_qma6100_configuration_wrapper, .probe=r1_qma6100_probe_wrapper,
 .fifo=r1_qma6100_fifo_normalized, .interrupt.notify=r1_qma6100_interrupt_wrapper};
const r1_motion_table r1_motion_lis_table __attribute__((section(".r1.motion.lis.table"),aligned(4)))={
 .configure=r1_lis2dw12_configuration_wrapper, .probe=r1_lis2dw12_probe_wrapper,
 .fifo=r1_lis2dw12_fifo_normalized, .interrupt.notify=r1_lis2dw12_interrupt_noop,
 .aux16=r1_lis2dw12_aux16_boundary, .aux20=r1_lis2dw12_aux20_boundary};
const r1_motion_table r1_motion_bma_table __attribute__((section(".r1.motion.bma.table"),aligned(4)))={
 .configure=r1_bma456w_configuration_wrapper, .probe=r1_bma456w_probe_wrapper,
 .fifo=r1_bma456w_fifo_normalized, .interrupt.notify=r1_bma456w_interrupt_noop};
uint32_t r1_motion_probe_and_select_provider(void)
{
 (void)r1_motion_bus_acquire();
 uint32_t id=r1_lis2dw12_identity_probe();const r1_motion_table *selected=0;
 if(id==0x44)selected=&r1_motion_lis_table;
 else {id=r1_bma456w_identity_probe();if(id==0x16)selected=&r1_motion_bma_table;
  else {id=r1_qma6100_chip_id();if(id==0x90)selected=&r1_motion_qma_table;}}
 r1_motion_selected_provider=(uint32_t)(uintptr_t)selected;
 (void)r1_motion_bus_release();return selected?id:0;
}
uint32_t r1_motion_refresh_selection(void)
{
 const volatile r1_motion_table *selected =
  (const volatile r1_motion_table *)(uintptr_t)r1_motion_selected_provider;
 if (selected != 0) {
  uint32_t (*probe)(void) = selected->probe;
  if (probe != 0)
   return probe();
 }
 return r1_motion_probe_and_select_provider();
}
