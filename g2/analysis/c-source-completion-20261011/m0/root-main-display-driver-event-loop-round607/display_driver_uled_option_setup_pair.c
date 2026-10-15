/* Apollo uLED option setup callbacks 0x592680 and 0x5bbd70. Candidate.
 * Child configuration/enable providers remain independent source gates.
 */
#include <stdint.h>
extern uint32_t display_driver_uled_option_config_59cf1a(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_option_type0_enable_5926b4(uint32_t);
extern uint32_t display_driver_uled_option_type1_enable_5bbda4(uint32_t);

uint32_t display_driver_uled_option_type0_setup_592680(uint32_t handle,
                                                         uint32_t argument,
                                                         uint32_t callback) {
    if(handle==0u)return UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)0x2007452cu=handle;
    *(volatile uint32_t *)(uintptr_t)0x20074528u=argument;
    (void)display_driver_uled_option_config_59cf1a(
        0x20074524u,callback,0x20000788u,0x200007a0u);
    return display_driver_uled_option_type0_enable_5926b4(1u);
}

uint32_t display_driver_uled_option_type1_setup_5bbd70(uint32_t handle,
                                                         uint32_t argument,
                                                         uint32_t callback) {
    if(handle==0u)return UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)0x20074518u=handle;
    *(volatile uint32_t *)(uintptr_t)0x20074514u=argument;
    (void)display_driver_uled_option_config_59cf1a(
        0x20074510u,callback,0x20000758u,0x20000770u);
    return display_driver_uled_option_type1_enable_5bbda4(1u);
}
