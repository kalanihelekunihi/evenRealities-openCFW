/* SPDX-License-Identifier: GPL-3.0-only */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_state_initialize(
    struct open_cfw_freertos_cli_console_state *state,
    open_cfw_freertos_cli_console_u8 *input,
    open_cfw_freertos_cli_console_u8 *output
)
{
    state->input = input;
    state->output = output;
    state->length = 0U;
    open_cfw_freertos_cli_console_fill(input);
    open_cfw_freertos_cli_console_fill(output);
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
