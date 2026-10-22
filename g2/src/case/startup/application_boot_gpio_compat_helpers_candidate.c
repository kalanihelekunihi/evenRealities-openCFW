/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ba44..0xbb2c GPIO wrappers absent as named bodies from
 * the reachable candidate call graph. Their effects use sourced GPIO lowers.
 */
#include <stdint.h>
extern void case_bus_gpio_config(uint32_t,volatile uint32_t *); /* 0x4d30 */
extern void case_control_write(uint32_t,uint32_t,uint32_t); /* 0x4e9e */
extern uint32_t case_init_pin_read(uint32_t,uint32_t); /* 0x4e94 */

/* Stock 0x0800A39C (case_read_mask4) */
uint32_t case_boot_gpio_a4_read(void) /* 0xa39c */
{return case_init_pin_read(0x50000400u,4u);}
/* Stock 0x0800A3AC (case_read_mask8) */
uint32_t case_boot_gpio_b8_read(void) /* 0xa3ac */
{return case_init_pin_read(0x50000000u,8u);}

static void configure_if_changed(uint32_t base,uint32_t address,uint32_t index,uint32_t target)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)address;
    if(state[index]!=target){state[index]=target;case_bus_gpio_config(base,state);}
}
/* Stock 0x0800BA44 (case_transition_word4) */
void case_boot_gpio_a4_input(void) /* 0xba44 */
{configure_if_changed(0x50000400u,0x20000014u,1u,0u);}
/* Stock 0x0800BA64 (case_transition_word4_alt) */
void case_boot_gpio_b8_input(void) /* 0xba64 */
{configure_if_changed(0x50000000u,0x200000a0u,1u,0u);}
/* Stock 0x0800BA84 (case_transition_word4) */
void case_boot_gpio_a4_output(void) /* 0xba84 */
{configure_if_changed(0x50000400u,0x20000014u,1u,1u);}
void case_boot_gpio_b8_output(void) /* 0xbaa4 */
{configure_if_changed(0x50000000u,0x200000a0u,1u,1u);}
/* Stock 0x0800BAC4 (case_write_mask4_set) */
void case_boot_gpio_a4_high(void) /* 0xbac4 */
{case_control_write(0x50000400u,4u,1u);}
void case_boot_gpio_b8_high(void) /* 0xbad8 */
{case_control_write(0x50000000u,8u,1u);}
/* Stock 0x0800BAE8 (case_write_mask4_clear) */
void case_boot_gpio_a4_low(void) /* 0xbae8 */
{case_control_write(0x50000400u,4u,0u);}
void case_boot_gpio_b8_low(void) /* 0xbafc */
{case_control_write(0x50000000u,8u,0u);}
/* Stock 0x0800BB0C (case_transition_word8) */
void case_boot_gpio_a4_alt(void) /* 0xbb0c */
{configure_if_changed(0x50000400u,0x20000014u,2u,1u);}
/* Stock 0x0800BB2C (case_transition_word8_alt) */
void case_boot_gpio_b8_alt(void) /* 0xbb2c */
{configure_if_changed(0x50000000u,0x200000a0u,2u,1u);}
