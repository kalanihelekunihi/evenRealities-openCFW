/* Apollo option-table interrupt callbacks 0x592658 and 0x5bbd48.
 * Keep each native handle-cell load: the status/clear helpers may change
 * the shared cell before the next call. This candidate covers the normal
 * invariant that a nonzero handle makes status_get write the status word.
 * Stock otherwise inherits the saved entry r2 value; that malformed-handle
 * machine-state dependency is not modeled by this void C interface.
 */
#include <stdbool.h>
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_a6ng_mspi_handle[] __asm__("g2_a6ng_mspi_handle");
extern unsigned char g2ref_g2_jbd4010_mspi_handle[] __asm__("g2_jbd4010_mspi_handle");
extern uint32_t am_hal_mspi_interrupt_status_get(void *,uint32_t *,bool);
extern uint32_t am_hal_mspi_interrupt_clear(void *,uint32_t);
extern uint32_t am_hal_mspi_interrupt_service(void *,uint32_t);

static void service_cell(uintptr_t cell_address) {
    volatile uint32_t *cell=(volatile uint32_t *)cell_address;
    if(*cell==0u)return;
    uint32_t status=0u;
    (void)am_hal_mspi_interrupt_status_get((void *)(uintptr_t)*cell,&status,false);
    (void)am_hal_mspi_interrupt_clear((void *)(uintptr_t)*cell,status);
    (void)am_hal_mspi_interrupt_service((void *)(uintptr_t)*cell,status);
}

void display_driver_uled_option_type0_irq_592658(void) {
    service_cell((uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_mspi_handle));
}

void display_driver_uled_option_type1_irq_5bbd48(void) {
    service_cell((uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_mspi_handle));
}
