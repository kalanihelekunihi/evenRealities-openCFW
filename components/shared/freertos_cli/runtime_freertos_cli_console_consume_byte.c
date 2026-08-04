/* SPDX-License-Identifier: GPL-3.0-only */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_consume_byte(
    struct open_cfw_freertos_cli_console_state *state,
    open_cfw_freertos_cli_console_u8 value
)
{
    if (value == 0x7FU) {
        value = 0x08U;
    }

    open_cfw_retained_freertos_cli_console_display_byte(value);

    if (value == 0x0AU || value == 0x0DU) {
        open_cfw_freertos_cli_console_process_command(state);
        return;
    }

    if (value == 0x08U) {
        if (state->length != 0U) {
            state->length--;
            state->input[state->length] = 0U;
            open_cfw_retained_freertos_cli_console_display_byte(0x20U);
            open_cfw_retained_freertos_cli_console_display_byte(0x08U);
        }
        return;
    }

    if (state->length < OPEN_CFW_FREERTOS_CLI_CONSOLE_PAYLOAD_BYTES) {
        state->input[state->length] = value;
        state->length++;
        state->input[state->length] = 0U;
    }
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
