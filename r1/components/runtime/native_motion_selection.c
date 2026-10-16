#include <stdint.h>
#include "../registry/stock_registry.h"
extern generic_device_registry_device *volatile r1_motion_bus_device;
extern volatile uint32_t r1_motion_selected_provider;
extern uint32_t r1_lis2dw12_identity_probe(void),r1_bma456w_identity_probe(void),r1_qma6100_chip_id(void);
extern uint32_t r1_lis2dw12_configure_boundary(uint32_t),r1_bma456w_configure_boundary(uint32_t),r1_qma6100_configure_boundary(uint32_t);
extern uint32_t r1_qma6100_irq_boundary(void);
extern int32_t r1_lis2dw12_fifo_normalized(uint8_t *,uint32_t),r1_bma456w_fifo_normalized(uint8_t *,uint32_t),r1_qma6100_fifo_normalized(uint8_t *,uint32_t);
/* Auxiliary entries are pointer contracts only until their call ABI is reduced. */
extern void r1_lis2dw12_aux16_boundary(void),r1_lis2dw12_aux20_boundary(void);
__attribute__((noinline)) uint32_t r1_motion_bus_acquire(void){return r1_stock_dispatch_08(r1_motion_bus_device);}
__attribute__((noinline)) uint32_t r1_motion_bus_release(void){return r1_stock_dispatch_0c(r1_motion_bus_device);}
/* Native wrappers are ABI glue: exact saved-ID and tail-release behavior. */
#define PROBE(name,provider) __attribute__((naked)) uint32_t name(void){__asm__ volatile("push {r4,lr}\nbl r1_motion_bus_acquire\nbl " #provider "\nmov r4,r0\nbl r1_motion_bus_release\nmov r0,r4\npop {r4,pc}\n");}
PROBE(r1_lis2dw12_probe_wrapper,r1_lis2dw12_identity_probe)
PROBE(r1_bma456w_probe_wrapper,r1_bma456w_identity_probe)
PROBE(r1_qma6100_probe_wrapper,r1_qma6100_chip_id)
#define CONFIG(name,provider) __attribute__((naked)) uint32_t name(void){__asm__ volatile("push {r4,lr}\nbl r1_motion_bus_acquire\nmovs r0,#25\nbl " #provider "\ncbz r0,1f\nbl r1_motion_bus_release\nmovs r0,#1\npop {r4,pc}\n1: bl r1_motion_bus_release\nmovs r0,#0\npop {r4,pc}\n");}
CONFIG(r1_lis2dw12_configuration_wrapper,r1_lis2dw12_configure_boundary)
CONFIG(r1_bma456w_configuration_wrapper,r1_bma456w_configure_boundary)
CONFIG(r1_qma6100_configuration_wrapper,r1_qma6100_configure_boundary)
void r1_lis2dw12_interrupt_noop(void){}
void r1_bma456w_interrupt_noop(void){}
__attribute__((naked)) uint32_t r1_qma6100_interrupt_wrapper(void){__asm__ volatile("push {r4,lr}\nbl r1_motion_bus_acquire\nbl r1_qma6100_irq_boundary\npop {r4,lr}\nb r1_motion_bus_release\n");}
typedef void (*r1_motion_slot)(void);
typedef struct {r1_motion_slot slot[6];} r1_motion_table;
_Static_assert(sizeof(r1_motion_table)==24,"native motion operation table");
const r1_motion_table r1_motion_qma_table __attribute__((section(".r1.motion.qma.table"),aligned(4)))={{(r1_motion_slot)r1_qma6100_configuration_wrapper,(r1_motion_slot)r1_qma6100_probe_wrapper,(r1_motion_slot)r1_qma6100_fifo_normalized,(r1_motion_slot)r1_qma6100_interrupt_wrapper,0,0}};
const r1_motion_table r1_motion_lis_table __attribute__((section(".r1.motion.lis.table"),aligned(4)))={{(r1_motion_slot)r1_lis2dw12_configuration_wrapper,(r1_motion_slot)r1_lis2dw12_probe_wrapper,(r1_motion_slot)r1_lis2dw12_fifo_normalized,r1_lis2dw12_interrupt_noop,r1_lis2dw12_aux16_boundary,r1_lis2dw12_aux20_boundary}};
const r1_motion_table r1_motion_bma_table __attribute__((section(".r1.motion.bma.table"),aligned(4)))={{(r1_motion_slot)r1_bma456w_configuration_wrapper,(r1_motion_slot)r1_bma456w_probe_wrapper,(r1_motion_slot)r1_bma456w_fifo_normalized,r1_bma456w_interrupt_noop,0,0}};
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
__attribute__((naked)) uint32_t r1_motion_refresh_selection(void)
{
 __asm__ volatile("ldr r0,=r1_motion_selected_provider\nldr r0,[r0]\ncbz r0,1f\nldr r0,[r0,#4]\ncbz r0,1f\nbx r0\n1: b r1_motion_probe_and_select_provider\n");
}
