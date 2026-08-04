/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 FreeRTOS+CLI console task.  This
 * candidate is deliberately absent from every production overlay/manifest.
 */

#include "runtime_freertos_cli_console_task_candidate.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

static OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_fill(
    open_cfw_freertos_cli_console_u8 *destination,
    open_cfw_freertos_cli_console_u32 count,
    open_cfw_freertos_cli_console_u8 value
)
{
    while (count != 0U) {
        *destination = value;
        destination++;
        count--;
    }
}

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
    open_cfw_freertos_cli_console_fill(
        input,
        OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES,
        0U
    );
    open_cfw_freertos_cli_console_fill(
        output,
        OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES,
        0U
    );
}

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_register_groups_candidate(void)
{
    open_cfw_retained_freertos_cli_register_group_57e626();
    open_cfw_retained_freertos_cli_register_group_57e810();
    open_cfw_retained_freertos_cli_register_group_57ff40();
    open_cfw_retained_freertos_cli_register_group_580392();
    open_cfw_retained_freertos_cli_register_group_5807c0();
    open_cfw_retained_freertos_cli_register_group_580c04();
    open_cfw_retained_freertos_cli_register_group_580fec();
    open_cfw_retained_freertos_cli_register_group_5810d8();
    open_cfw_retained_freertos_cli_register_group_581136();
    open_cfw_retained_freertos_cli_register_group_581644();
    open_cfw_retained_freertos_cli_register_group_58183a();
    open_cfw_retained_freertos_cli_register_group_581960();
    open_cfw_retained_freertos_cli_register_group_581d60();
    open_cfw_retained_freertos_cli_register_group_5827d0();
    open_cfw_retained_freertos_cli_register_group_5836b8();
    open_cfw_retained_freertos_cli_register_group_583cec();
    open_cfw_retained_freertos_cli_register_group_583f74();
    open_cfw_retained_freertos_cli_register_group_5840f4();
    open_cfw_retained_freertos_cli_register_group_5841ee();
    open_cfw_retained_freertos_cli_register_group_584320();
    open_cfw_retained_freertos_cli_register_group_584430();
    open_cfw_retained_freertos_cli_register_group_584702();
}

static OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
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
        open_cfw_freertos_cli_console_fill(
            state->output,
            OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES,
            0U
        );
    } while (more_output != 0);

    state->length = 0U;
    open_cfw_freertos_cli_console_fill(
        state->input,
        OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES,
        0U
    );
}

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_consume_byte_candidate(
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

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
open_cfw_freertos_cli_console_u32
open_cfw_freertos_cli_console_poll_once_candidate(
    struct open_cfw_freertos_cli_console_state *state
)
{
    open_cfw_freertos_cli_console_u8 received = 0U;
    open_cfw_freertos_cli_console_u32 count;

    count = open_cfw_retained_freertos_cli_console_receive(
        open_cfw_retained_freertos_cli_console_receive_handle,
        &received,
        1U,
        OPEN_CFW_FREERTOS_CLI_CONSOLE_RECEIVE_FOREVER
    );
    if (count != 1U) {
        return 0U;
    }

    open_cfw_freertos_cli_console_consume_byte_candidate(state, received);
    return 1U;
}

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_task_candidate(void *argument)
{
    struct open_cfw_freertos_cli_console_state state;

    (void)argument;
    open_cfw_freertos_cli_console_register_groups_candidate();
    open_cfw_freertos_cli_console_state_initialize(
        &state,
        open_cfw_retained_freertos_cli_console_input,
        open_cfw_retained_freertos_cli_console_output
    );

    for (;;) {
        (void)open_cfw_freertos_cli_console_poll_once_candidate(&state);
    }
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
