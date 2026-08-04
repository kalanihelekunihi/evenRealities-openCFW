/* SPDX-License-Identifier: GPL-3.0-only */

#include "runtime_freertos_cli_console.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
#endif

OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
void open_cfw_freertos_cli_console_fill(
    open_cfw_freertos_cli_console_u8 *destination
)
{
    open_cfw_freertos_cli_console_u32 count =
        OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES;

    while (count != 0U) {
        *destination = 0U;
        destination++;
        count--;
    }
}

#undef OPEN_CFW_FREERTOS_CLI_CONSOLE_NOINLINE
