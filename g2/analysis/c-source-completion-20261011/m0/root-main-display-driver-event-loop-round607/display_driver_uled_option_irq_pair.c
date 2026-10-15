/* Apollo option-table interrupt callbacks 0x592658 and 0x5bbd48.
 * Lower interrupt status/clear source is pinned Ambiq HAL 5.1.0;
 * interrupt_service is a separate, currently incomplete provider gate.
 */
#include <stdbool.h>
#include <stdint.h>
extern uint32_t am_hal_mspi_interrupt_status_get(void *,uint32_t *,bool);
extern uint32_t am_hal_mspi_interrupt_clear(void *,uint32_t);
extern uint32_t am_hal_mspi_interrupt_service(void *,uint32_t);

static void service_cell(uintptr_t cell_address) {
    volatile uint32_t *cell=(volatile uint32_t *)cell_address;
    uint32_t handle=*cell;
    if(handle==0u)return;
    uint32_t status=0u;
    (void)am_hal_mspi_interrupt_status_get((void *)(uintptr_t)handle,&status,false);
    (void)am_hal_mspi_interrupt_clear((void *)(uintptr_t)*cell,status);
    (void)am_hal_mspi_interrupt_service((void *)(uintptr_t)*cell,status);
}

void display_driver_uled_option_type0_irq_592658(void) {
    service_cell((uintptr_t)0x20074524u);
}

void display_driver_uled_option_type1_irq_5bbd48(void) {
    service_cell((uintptr_t)0x20074510u);
}
