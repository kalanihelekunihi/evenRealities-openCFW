/* SPDX-License-Identifier: MIT
 * Native four-register/two-stack-argument adapter at stock 0x100054f8.
 * It binds the product command table to the shared help body 0x10005ef0.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern const struct gx8002_stage2_command gx8002_stage2_product_commands[6];
extern uint32_t gx8002_uart_stage2_command_help_5ef0(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, uint32_t,
    int32_t, const char *const *);

int32_t gx8002_uart_stage2_help_54f8(
    const struct gx8002_stage2_command *entry, uint32_t mode,
    uint32_t argc, char **argv)
{
    return (int32_t)gx8002_uart_stage2_command_help_5ef0(
        gx8002_stage2_product_commands, 6u, (uint32_t)(uintptr_t)entry,
        mode, (int32_t)argc, (const char *const *)argv);
}
