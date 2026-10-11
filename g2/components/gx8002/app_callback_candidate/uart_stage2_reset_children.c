/* SPDX-License-Identifier: MIT
 * Direct UART stage-2 reset children at 0x100052b0 and 0x100054e0.
 * Their callees retain separate source obligations by native address.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_runtime_boot_2a3c(void);
extern uint32_t gx8002_uart_stage2_set_ldo_analog_voltage_4408(uint32_t mode);
extern uint32_t gx8002_uart_stage2_set_ldo_request_4428(uint32_t mode);
extern void gx8002_uart_stage2_application_setup_547c(void);
extern void gx8002_uart_stage2_application_main_5a4c(void);

uint32_t gx8002_uart_stage2_application_run_54ec(void)
{
    gx8002_uart_stage2_application_main_5a4c();
    return 0;
}

void gx8002_uart_stage2_init_runtime(void)
{
    gx8002_uart_stage2_runtime_boot_2a3c();
    (void)gx8002_uart_stage2_set_ldo_analog_voltage_4408(0);
    (void)gx8002_uart_stage2_set_ldo_request_4428(0);
}

__attribute__((noreturn)) void gx8002_uart_stage2_enter_application(void)
{
    gx8002_uart_stage2_application_setup_547c();
    (void)gx8002_uart_stage2_application_run_54ec();
    for (;;) __asm__ volatile("br ." ::: "memory");
}
