/* Native uLED option callbacks +0x00: type1 0x5bbd48, type0 0x592658.
 * Two BSS handle cells are source-owned; exact SRAM placement remains gated.
 */
#include <stdint.h>
extern uint32_t display_driver_uled_mspi_child_4c2392(void *,uint32_t *,uint32_t);
extern uint32_t display_driver_uled_mspi_child_4c23de(void *,uint32_t);
extern uint32_t display_driver_uled_mspi_child_4c240e(void *,uint32_t);
void * volatile display_driver_uled_type1_handle;
void * volatile display_driver_uled_type0_handle;

static uint32_t shutdown_handle(void *handle,uint32_t saved_r2) {
    if(handle==0)return saved_r2;
    uint32_t value;
    (void)display_driver_uled_mspi_child_4c2392(handle,&value,0u);
    (void)display_driver_uled_mspi_child_4c23de(handle,value);
    (void)display_driver_uled_mspi_child_4c240e(handle,value);
    return value;
}
uint32_t display_driver_uled_type1_shutdown_5bbd48(uint32_t a,uint32_t b,uint32_t saved_r2) {
    (void)a;(void)b;
    return shutdown_handle(display_driver_uled_type1_handle,saved_r2);
}
uint32_t display_driver_uled_type0_shutdown_592658(uint32_t a,uint32_t b,uint32_t saved_r2) {
    (void)a;(void)b;
    return shutdown_handle(display_driver_uled_type0_handle,saved_r2);
}
