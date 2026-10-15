/* Apollo type-4 pin prepare 0x4c3f2a. Candidate. */
#include <stdint.h>

extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_pin_group_check_4c37ca(uint32_t);
extern uint32_t display_driver_uled_power_set_4d391e(uint32_t);
extern uint32_t display_driver_uled_power_apply_4d3938(uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern void display_driver_uled_pin_prepare_finalize_4c3ef4(uint32_t *);

uint32_t display_driver_uled_pin_prepare_type4_4c3f2a(uint32_t pin) {
    uint32_t local_count = 1000u;
    uint32_t index = (uint8_t)pin;
    uint32_t queried = display_driver_uled_pin_query_4c37a8(4u,index);
    uint32_t prior_mask = display_driver_uled_irq_save_473940();
    volatile uint8_t *flag = (volatile uint8_t *)(uintptr_t)0x20074f57u;
    volatile uint32_t *pointer_cell = (volatile uint32_t *)(uintptr_t)0x20074264u;
    if (*flag != 0u) local_count = *(volatile uint32_t *)(uintptr_t)*pointer_cell;
    if (queried != 0u) {
        *pointer_cell = (uint32_t)(uintptr_t)&local_count;
        __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
        display_driver_uled_pin_prepare_finalize_4c3ef4(&local_count);
        return 0u;
    }
    uint32_t status = (*(volatile uint8_t *)(uintptr_t)0x20004536u == 0u);
    if (status == 0u) {
        if ((uint8_t)display_driver_uled_pin_group_check_4c37ca(4u) == 0u) {
            (void)display_driver_uled_power_set_4d391e(1u);
            if (*(volatile uint32_t *)(uintptr_t)0x20074250u != 0u) {
                uint32_t power_arg = *(volatile uint32_t *)(uintptr_t)0x20073f30u;
                status = display_driver_uled_power_apply_4d3938(power_arg);
                if (status == 0u) {
                    if (*flag == 0u && *(volatile uint8_t *)(uintptr_t)0x20074f59u == 0u)
                        *flag = 1u;
                } else {
                    (void)display_driver_uled_power_set_4d391e(0u);
                }
            }
        }
        if (status == 0u) (void)display_driver_uled_pin_apply_4c37fe(4u,index,1u);
        if (*flag != 0u) *pointer_cell = (uint32_t)(uintptr_t)&local_count;
    }
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    display_driver_uled_pin_prepare_finalize_4c3ef4(&local_count);
    return status;
}
