/* SPDX-License-Identifier: MIT
 * Native CASE 0x502c, 0x38a0, 0x2b40 and 0x35f0 init completion paths.
 */
#include <stdint.h>
extern uint32_t case_init_pmic_write(uint32_t reg,uint32_t value);
extern uint32_t case_init_pmic_reset(uint32_t reg,uint32_t value);
extern void case_init_wait(uint32_t ticks);
extern void case_policy_led_left_clear(uint32_t value); /* 0x6b80 */
extern void case_policy_led_right_clear(uint32_t value); /* 0x6b98 */
__attribute__((noreturn)) void case_init_display_reset(void)
{
    __asm__ volatile("dsb sy" ::: "memory");
    *(volatile uint32_t *)(uintptr_t)0xe000ed0cu=0x05fa0004u;
    __asm__ volatile("dsb sy" ::: "memory");
    for(;;)__asm__ volatile("nop");
}
/* Stock 0x080038A0 (case_toggle_lines_three) */
void case_init_led_show(void)
{
    for(uint8_t i=0u;i<3u;i=(uint8_t)(i+1u)){
        case_policy_led_left_clear(1u);
        case_policy_led_right_clear(0u);
        case_init_wait(200u);
        case_policy_led_left_clear(0u);
        case_policy_led_right_clear(1u);
        case_init_wait(200u);
    }
    case_policy_led_left_clear(0u);
    case_policy_led_right_clear(0u);
}
/* Stock 0x08002B40 (case_command_a2_clear) */
void case_init_usb_reset(void)
{(void)case_init_pmic_write(0xa2u,0u);}
/* Stock 0x080035F0 (case_configure_register_sequence) */
void case_init_sensor_finish(void)
{
    static const uint8_t registers[7]={19u,22u,25u,23u,24u,26u,27u};
    static const uint8_t values[7]={0x90u,0u,2u,0x28u,1u,0u,1u};
    for(uint32_t i=0u;i<7u;++i){
        (void)case_init_pmic_reset(registers[i],values[i]);
        case_init_wait(2u);
    }
}
