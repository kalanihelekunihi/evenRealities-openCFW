/* SPDX-License-Identifier: GPL-3.0-only */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_task(void *argument)
{
    struct open_cfw_freertos_cli_console_state state;
    open_cfw_freertos_cli_console_u8 *input;
    open_cfw_freertos_cli_console_u8 *output;

    (void)argument;
    open_cfw_freertos_cli_console_register_groups();

#if defined(__arm__) || defined(__thumb__)
    /* Keep each reviewed absolute MOVW/MOVT relocation pair adjacent. */
    __asm__ volatile(
        "movw %0, :lower16:open_cfw_retained_freertos_cli_console_input\n"
        "movt %0, :upper16:open_cfw_retained_freertos_cli_console_input"
        : "=r"(input)
    );
    __asm__ volatile(
        "movw %0, :lower16:open_cfw_retained_freertos_cli_console_output\n"
        "movt %0, :upper16:open_cfw_retained_freertos_cli_console_output"
        : "=r"(output)
    );
#else
    input = open_cfw_retained_freertos_cli_console_input;
    output = open_cfw_retained_freertos_cli_console_output;
#endif

    open_cfw_freertos_cli_console_state_initialize(
        &state,
        input,
        output
    );

    for (;;) {
        (void)open_cfw_freertos_cli_console_poll_once(&state);
    }
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
