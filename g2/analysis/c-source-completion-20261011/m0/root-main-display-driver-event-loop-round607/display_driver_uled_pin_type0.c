/* Apollo type-0 pin prepare/control 0x4c3bfc and 0x4c3c2e. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_pin_prepare_type0_4c3bfc(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(0u,index)!=0u)return 0u;
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(0u,index,1u);
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return 0u;
}

uint32_t display_driver_uled_pin_control_type0_4c3c2e(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(0u,index)==0u)return 0u;
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(0u,index,0u);
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return 0u;
}
