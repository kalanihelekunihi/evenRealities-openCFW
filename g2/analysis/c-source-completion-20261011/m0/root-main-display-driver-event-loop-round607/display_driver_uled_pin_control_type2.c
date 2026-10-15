/* Apollo type-2 pin-control provider 0x4c3e9a. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_pin_bus_command_4809c4(uint32_t,uint8_t *);

uint32_t display_driver_uled_pin_control_type2_4c3e9a(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(2u,index)==0u)return 0u;
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(2u,index,0u);
    if(display_driver_uled_pin_group_query_4c377a(2u)==0u) {
        uint8_t value=1u;
        (void)display_driver_uled_pin_bus_command_4809c4(4u,&value);
        *(volatile uint8_t *)(uintptr_t)0x20074f56u=0u;
        *(volatile uint32_t *)(uintptr_t)0x20074260u=0u;
    }
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return 0u;
}
