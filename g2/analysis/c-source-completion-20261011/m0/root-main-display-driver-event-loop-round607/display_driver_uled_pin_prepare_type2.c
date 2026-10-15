/* Apollo type-2 pin prepare 0x4c3d9e. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_pin_bus_status_480c56(uint8_t *);
extern uint32_t display_driver_uled_pin_bus_command_4809c4(uint32_t,uint8_t *);
extern void display_driver_uled_pin_prepare_type2_finalize_4c3d70(uint32_t *);

uint32_t display_driver_uled_pin_prepare_type2_4c3d9e(uint32_t pin) {
    uint32_t count=150u;
    volatile uint8_t *waiting=(volatile uint8_t *)(uintptr_t)0x20074f56u;
    volatile uint32_t *pointer_cell=(volatile uint32_t *)(uintptr_t)0x20074260u;
    volatile uint8_t *mode=(volatile uint8_t *)(uintptr_t)0x200001ccu;
    if (*(volatile uint32_t *)(uintptr_t)0x200001d0u == 0u) return 7u;
    uint32_t index=(uint8_t)pin;
    if (display_driver_uled_pin_query_4c37a8(2u,index)!=0u) {
        uint32_t prior_mask=display_driver_uled_irq_save_473940();
        if (*waiting != 0u)count=*(volatile uint32_t *)(uintptr_t)*pointer_cell;
        *pointer_cell=(uint32_t)(uintptr_t)&count;
        __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
        display_driver_uled_pin_prepare_type2_finalize_4c3d70(&count);
        return 0u;
    }
    uint32_t prior_mask=display_driver_uled_irq_save_473940();
    uint8_t bus_status=0u;
    (void)display_driver_uled_pin_bus_status_480c56(&bus_status);
    if (*waiting != 0u)count=*(volatile uint32_t *)(uintptr_t)*pointer_cell;
    uint32_t result=0u;
    if (bus_status==0u) {
        if (*mode==1u) {
            uint8_t command=1u;
            (void)display_driver_uled_pin_bus_command_4809c4(3u,&command);
        } else {
            (void)display_driver_uled_pin_bus_command_4809c4(2u,0);
            if (*waiting==0u)*waiting=1u;
        }
    } else if ((bus_status==2u && *mode==0u) ||
               (bus_status==1u && *mode==1u)) {
        result=3u;
    }
    if (result==0u)(void)display_driver_uled_pin_apply_4c37fe(2u,index,1u);
    if (*waiting!=0u)*pointer_cell=(uint32_t)(uintptr_t)&count;
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    display_driver_uled_pin_prepare_type2_finalize_4c3d70(&count);
    return result;
}
