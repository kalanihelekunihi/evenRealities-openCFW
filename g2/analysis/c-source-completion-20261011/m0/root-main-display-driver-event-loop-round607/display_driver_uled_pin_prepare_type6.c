/* Apollo type-6 pin prepare 0x4c427e. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_query_4c37a8(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pin_group_check_4c37ca(uint32_t);
extern uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t display_driver_uled_pin_prepare_type2_4c3d9e(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type3_4c3cd4(uint32_t);
extern uint32_t display_driver_uled_pin_control_type2_4c3e9a(uint32_t);
extern uint32_t display_driver_uled_pin_control_type3_4c3d28(uint32_t);
extern uint32_t display_driver_uled_object_create_5398e0(uint32_t,uint32_t *);
extern uint32_t display_driver_uled_object_config_539a40(uint32_t,const volatile void *);
extern uint32_t display_driver_uled_object_start_539994(uint32_t);
extern uint32_t display_driver_uled_object_release_539944(uint32_t);
extern uint32_t display_driver_uled_object_wait_539b56(uint32_t);

uint32_t display_driver_uled_pin_prepare_type6_4c427e(uint32_t pin) {
    uint32_t index=(uint8_t)pin;
    uint32_t status=0u;
    uint32_t started=0u;
    volatile uint8_t *connected=(volatile uint8_t *)(uintptr_t)0x20074f55u;
    volatile uint8_t *mode=(volatile uint8_t *)(uintptr_t)0x20073f48u;
    volatile uint8_t *first=(volatile uint8_t *)(uintptr_t)0x20074f5bu;
    volatile uint32_t *object_cell=(volatile uint32_t *)(uintptr_t)0x2007425cu;
    if(display_driver_uled_pin_query_4c37a8(6u,index)!=0u)return 0u;

    uint32_t prior=display_driver_uled_irq_save_473940();
    if((uint8_t)display_driver_uled_pin_group_check_4c37ca(6u)==0u)*first=1u;
    (void)display_driver_uled_pin_apply_4c37fe(6u,index,1u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");

    if(*connected!=0u) {
        if(*mode==0u) {
            status=display_driver_uled_pin_prepare_type2_4c3d9e(0x35u);
            (void)display_driver_uled_pin_prepare_type3_4c3cd4(0x35u);
        } else {
            status=display_driver_uled_pin_prepare_type3_4c3cd4(0x35u);
            (void)display_driver_uled_pin_prepare_type2_4c3d9e(0x35u);
        }
    }

    prior=display_driver_uled_irq_save_473940();
    if(status==0u) {
        if(*connected==0u)status=1u;
        if(status==0u && *first!=0u) {
            *first=0u;
            if(*object_cell==0u)
                status=display_driver_uled_object_create_5398e0(0u,(uint32_t *)object_cell);
            if(status==0u)
                status=display_driver_uled_object_config_539a40(*object_cell,mode);
            if(status==0u)
                status=display_driver_uled_object_start_539994(*object_cell);
            if(status==0u)started=1u;
            else if(*object_cell!=0u) {
                (void)display_driver_uled_object_release_539944(*object_cell);
                *object_cell=0u;
            }
        }
        if(status!=0u)(void)display_driver_uled_pin_apply_4c37fe(6u,index,0u);
    } else (void)display_driver_uled_pin_apply_4c37fe(6u,index,0u);
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");

    if(*connected!=0u) {
        if(status==0u) {
            if(*mode==0u)(void)display_driver_uled_pin_control_type3_4c3d28(0x35u);
            else (void)display_driver_uled_pin_control_type2_4c3e9a(0x35u);
        } else {
            (void)display_driver_uled_pin_control_type2_4c3e9a(0x35u);
            (void)display_driver_uled_pin_control_type3_4c3d28(0x35u);
        }
    }
    if(started!=0u)status=display_driver_uled_object_wait_539b56(*object_cell);
    return status;
}
