/* Apollo type-3 pin prepare/control 0x4c3cd4 and 0x4c3d28. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_pin_register_write_480f0c(uint32_t,uint32_t);

uint32_t display_driver_uled_pin_prepare_type3_4c3cd4(uint32_t pin) {
    uint32_t config=(*(volatile uint32_t *)(uintptr_t)0x0078ee34u & ~15u)|10u;
    if (*(volatile uint32_t *)(uintptr_t)0x200001dcu==0u)return 7u;
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(3u,index)!=0u)return 0u;
    uint32_t prior=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_register_write_480f0c(15u,config);
    (void)display_driver_uled_pin_apply_4c37fe(3u,index,1u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    return 0u;
}

uint32_t display_driver_uled_pin_control_type3_4c3d28(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(3u,index)==0u)return 0u;
    uint32_t prior=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(3u,index,0u);
    if(display_driver_uled_pin_group_query_4c377a(3u)==0u)
        (void)display_driver_uled_pin_register_write_480f0c(
            15u,*(volatile uint32_t *)(uintptr_t)0x0078ee38u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    return 0u;
}
