/* SPDX-License-Identifier: MIT
 * Stage-2 `reboot` command callback at stock 0x10005a40, native 10-byte
 * body: invoke the watchdog reset lower at 0x10004508, then return zero.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern void gx8002_uart_stage2_watchdog_reset_4508(void);

int32_t gx8002_uart_stage2_reboot_5a40(
    const struct gx8002_stage2_command *entry, uint32_t mode,
    uint32_t argc, char **argv)
{
    (void)entry;
    (void)mode;
    (void)argc;
    (void)argv;
    gx8002_uart_stage2_watchdog_reset_4508();
    return 0;
}
