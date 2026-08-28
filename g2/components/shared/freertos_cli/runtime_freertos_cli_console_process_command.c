/* SPDX-License-Identifier: MIT */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_process_command(
    struct open_cfw_freertos_cli_console_state *state
)
{
    open_cfw_freertos_cli_console_s32 more_output;

    open_cfw_retained_freertos_cli_console_display_string("\n#");
    do {
        more_output = open_cfw_retained_freertos_cli_process_command(
            (const char *)state->input,
            (char *)state->output,
            OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES
        );
        open_cfw_retained_freertos_cli_console_display_string(
            (const char *)state->output
        );
        open_cfw_freertos_cli_console_fill(state->output);
    } while (more_output != 0);

    state->length = 0U;
    open_cfw_freertos_cli_console_fill(state->input);
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
