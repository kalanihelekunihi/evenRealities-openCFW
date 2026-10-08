/* Locked IOM status42c672/clear42c6b6 and module4 IRQ wrapper430610.
 * Issued register accesses are reconstructed; physical W1C is not modeled. */
#include <stdint.h>
#include "context_events.h"
#define W(p,o) (*(volatile uint32_t *)((uintptr_t)(p)+(o)))
#define NI __attribute__((noinline))
NI uint32_t opencfw_boot_iom_interrupt_status(void *handle,uint32_t enabled,
                                           uint32_t *output) {
    if(!handle || (W(handle,0)&0x01ffffffu)!=0x01123456u) return 2;
    if(!output) return 6;
    uint32_t module=W(handle,4);uintptr_t iom=0x40050000u+(module<<12);
    uint32_t status=W(iom,0x204);
    if((uint8_t)enabled) status&=W(iom,0x200);
    *output=status;return 0;
}
NI uint32_t opencfw_boot_iom_interrupt_clear(void *handle,uint32_t status) {
    if(!handle || (W(handle,0)&0x01ffffffu)!=0x01123456u) return 2;
    uint32_t module=W(handle,4);uintptr_t iom=0x40050000u+(module<<12);
    W(iom,0x208)=status;(void)W(iom,0x204);return 0;
}
NI void opencfw_boot_iom4_irq_dispatch(void) {
    uint32_t status;
    if(opencfw_boot_iom_interrupt_status((void *)(uintptr_t)W(0x20000374u,0x44),1,&status)) return;
    if(!status) return;
    (void)opencfw_boot_iom_interrupt_clear((void *)(uintptr_t)W(0x20000374u,0x44),status);
    (void)opencfw_boot_iom_event_service((void *)(uintptr_t)W(0x20000374u,0x44),status);
}
