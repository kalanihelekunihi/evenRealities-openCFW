/* Apollo type-6 pin control 0x4c43ec. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_object_stop_539a10(uint32_t);
extern uint32_t display_driver_uled_object_release_539944(uint32_t);
extern uint32_t display_driver_uled_pin_control_type2_4c3e9a(uint32_t);
extern uint32_t display_driver_uled_pin_control_type3_4c3d28(uint32_t);

uint32_t display_driver_uled_pin_control_type6_4c43ec(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    if(display_driver_uled_pin_query_4c37a8(6u,index)==0u)return 0u;
    uint32_t prior=display_driver_uled_irq_save_473940();
    (void)display_driver_uled_pin_apply_4c37fe(6u,index,0u);
    if(display_driver_uled_pin_group_query_4c377a(6u)==0u) {
        *(volatile uint8_t *)(uintptr_t)0x20074f5bu=0u;
        volatile uint32_t *object_cell=(volatile uint32_t *)(uintptr_t)0x2007425cu;
        (void)display_driver_uled_object_stop_539a10(*object_cell);
        (void)display_driver_uled_object_release_539944(*object_cell);
        *object_cell=0u;
        if (*(volatile uint8_t *)(uintptr_t)0x20073f48u==0u)
            (void)display_driver_uled_pin_control_type2_4c3e9a(0x35u);
        else (void)display_driver_uled_pin_control_type3_4c3d28(0x35u);
    }
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    return 0u;
}
