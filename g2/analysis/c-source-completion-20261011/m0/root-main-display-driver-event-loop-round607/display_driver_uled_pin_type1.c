/* Apollo type-1 pin prepare/control 0x4c3c60 and 0x4c3ca2. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_pin_prepare_type1_4c3c60(uint32_t pin) {
    if (*(volatile uint32_t *)(uintptr_t)0x200001d8u == 0u) return 7u;
    uint32_t index=(uint8_t)pin;
    if (display_driver_uled_pin_query_4c37a8(1u,index)!=0u)return 0u;
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(1u,index,1u);
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return 0u;
}

uint32_t display_driver_uled_pin_control_type1_4c3ca2(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if (display_driver_uled_pin_query_4c37a8(1u,index)==0u)return 0u;
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(1u,index,0u);
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return 0u;
}
