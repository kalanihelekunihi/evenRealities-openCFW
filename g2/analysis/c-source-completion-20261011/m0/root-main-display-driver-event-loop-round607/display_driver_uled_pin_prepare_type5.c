/* Apollo type-5 pin prepare 0x4c4086. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_check_4c37ca(uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_pin_prepare_type2_4c3d9e(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type3_4c3cd4(uint32_t);
extern uint32_t display_driver_uled_pin_control_type2_4c3e9a(uint32_t);
extern uint32_t display_driver_uled_pin_control_type3_4c3d28(uint32_t);
extern uint32_t display_driver_uled_power_enable_4d3952(uint32_t);
extern uint32_t display_driver_uled_power_config_4d3992(const volatile void *);
extern void display_driver_uled_pin_type5_finalize_4c4058(uint32_t *);

uint32_t display_driver_uled_pin_prepare_type5_4c4086(uint32_t pin) {
    uint32_t remaining=50u;
    uint32_t index=(uint8_t)pin;
    uint32_t status=0u;
    volatile uint8_t *active=(volatile uint8_t *)(uintptr_t)0x20074f58u;
    volatile uint32_t *remaining_cell=(volatile uint32_t *)(uintptr_t)0x20074268u;
    volatile uint8_t *powered=(volatile uint8_t *)(uintptr_t)0x20074f5au;
    volatile uint8_t *panel=(volatile uint8_t *)(uintptr_t)0x20004537u;
    volatile uint32_t *provider=(volatile uint32_t *)(uintptr_t)0x20074254u;
    volatile uint8_t *mode=(volatile uint8_t *)(uintptr_t)0x20073f3cu;

    if(display_driver_uled_pin_query_4c37a8(5u,index)!=0u) {
        uint32_t prior=display_driver_uled_irq_save_473940();
        if (*active!=0u)remaining=*(volatile uint32_t *)(uintptr_t)*remaining_cell;
        *remaining_cell=(uint32_t)(uintptr_t)&remaining;
        __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
        display_driver_uled_pin_type5_finalize_4c4058(&remaining);
        return 0u;
    }

    uint32_t prior=display_driver_uled_irq_save_473940();
    if((uint8_t)display_driver_uled_pin_group_check_4c37ca(5u)==0u)
        *powered=1u;
    (void)display_driver_uled_pin_apply_4c37fe(5u,index,1u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");

    if(*panel!=0u && *provider!=0u) {
        status=(*mode==0u) ?
            display_driver_uled_pin_prepare_type2_4c3d9e(0x36u) :
            display_driver_uled_pin_prepare_type3_4c3cd4(0x36u);
        if(status!=0u) {
            prior=display_driver_uled_irq_save_473940();
            (void)display_driver_uled_pin_apply_4c37fe(5u,index,0u);
            __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
        }
    }

    if(status==0u) {
        prior=display_driver_uled_irq_save_473940();
        if(*active!=0u)remaining=*(volatile uint32_t *)(uintptr_t)*remaining_cell;
        if(*panel==0u)status=1u;
        if(status==0u && *powered!=0u) {
            *powered=0u;
            (void)display_driver_uled_power_enable_4d3952(1u);
            if(*provider!=0u) {
                status=display_driver_uled_power_config_4d3992(mode);
                if(status==0u) {
                    if(*active==0u)*active=1u;
                } else (void)display_driver_uled_power_enable_4d3952(0u);
            }
        }
        if(status!=0u)(void)display_driver_uled_pin_apply_4c37fe(5u,index,0u);
        if(*active!=0u)*remaining_cell=(uint32_t)(uintptr_t)&remaining;
        __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    }
    if(status!=0u && *panel!=0u && *provider!=0u) {
        status=(*mode==0u) ?
            display_driver_uled_pin_control_type2_4c3e9a(0x36u) :
            display_driver_uled_pin_control_type3_4c3d28(0x36u);
    }
    display_driver_uled_pin_type5_finalize_4c4058(&remaining);
    return status;
}
