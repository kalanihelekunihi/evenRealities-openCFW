/* SPDX-License-Identifier: MIT */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
open_cfw_freertos_cli_console_u32
open_cfw_freertos_cli_console_poll_once(
    struct open_cfw_freertos_cli_console_state *state
)
{
    open_cfw_freertos_cli_console_u8 received = 0U;
    open_cfw_freertos_cli_console_u32 count;
    void *volatile *receive_handle_slot;

#if defined(__arm__) || defined(__thumb__)
    /* Keep the reviewed absolute MOVW/MOVT relocation pair adjacent. */
    __asm__ volatile(
        "movw %0, :lower16:open_cfw_retained_freertos_cli_console_receive_handle\n"
        "movt %0, :upper16:open_cfw_retained_freertos_cli_console_receive_handle"
        : "=r"(receive_handle_slot)
    );
#else
    receive_handle_slot =
        &open_cfw_retained_freertos_cli_console_receive_handle;
#endif

    count = open_cfw_retained_freertos_cli_console_receive(
        *receive_handle_slot,
        &received,
        1U,
        OPEN_CFW_FREERTOS_CLI_CONSOLE_RECEIVE_FOREVER
    );
    if (count != 1U) {
        return 0U;
    }

    open_cfw_freertos_cli_console_consume_byte(state, received);
    return 1U;
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
