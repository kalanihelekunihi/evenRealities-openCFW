/* Apollo type-5 pin control 0x4c420c. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_power_clear_4d39e4(void);
extern uint32_t display_driver_uled_pin_control_type2_4c3e9a(uint32_t);
extern uint32_t display_driver_uled_pin_control_type3_4c3d28(uint32_t);
extern uint32_t display_driver_uled_power_enable_4d3952(uint32_t);

uint32_t display_driver_uled_pin_control_type5_4c420c(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(5u,index)==0u)return 0u;
    uint32_t prior=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(5u,index,0u);
    if(display_driver_uled_pin_group_query_4c377a(5u)==0u) {
        if (*(volatile uint32_t *)(uintptr_t)0x20074254u!=0u) {
            *(volatile uint8_t *)(uintptr_t)0x20074f5au=0u;
            (void)display_driver_uled_power_clear_4d39e4();
            (void)display_driver_uled_pin_control_type2_4c3e9a(0x36u);
            (void)display_driver_uled_pin_control_type3_4c3d28(0x36u);
            *(volatile uint8_t *)(uintptr_t)0x20074f58u=0u;
            *(volatile uint32_t *)(uintptr_t)0x20074268u=0u;
        }
        (void)display_driver_uled_power_enable_4d3952(0u);
    }
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    return 0u;
}
