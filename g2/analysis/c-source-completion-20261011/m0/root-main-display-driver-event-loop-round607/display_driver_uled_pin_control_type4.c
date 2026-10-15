/* Apollo type-4 pin-control provider 0x4c4016. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t);
extern uint32_t display_driver_uled_power_set_4d391e(uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_pin_control_type4_4c4016(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(4u,index)==0u)return 0u;
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(4u,index,0u);
    if(display_driver_uled_pin_group_query_4c377a(4u)==0u)
        (void)display_driver_uled_power_set_4d391e(0u);
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return 0u;
}
