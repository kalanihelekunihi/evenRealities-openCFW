/* SPDX-License-Identifier: MIT
 * Semantic source for the six 20-byte command descriptors at stock
 * 0x1000900c..0x10009083. Values and referenced strings were decoded
 * directly from uart_stage2.bin; callback symbols remain real imports.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern int32_t gx8002_uart_stage2_flash_552c(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, char **);
extern int32_t gx8002_uart_stage2_help_54f8(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, char **);
extern int32_t gx8002_uart_stage2_reboot_5a40(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, char **);
extern int32_t gx8002_uart_stage2_serialdown_5628(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, char **);
extern int32_t gx8002_uart_stage2_wdt_5978(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, char **);

const struct gx8002_stage2_command gx8002_stage2_product_commands[6] = {
    {"flash",      {5, 1, (uintptr_t)&gx8002_uart_stage2_flash_552c,
                    (uintptr_t)"flash command"}},
    {"help",       {16, 1, (uintptr_t)&gx8002_uart_stage2_help_54f8,
                    (uintptr_t)"print command description/usage"}},
    {"?",          {16, 1, (uintptr_t)&gx8002_uart_stage2_help_54f8,
                    (uintptr_t)"alias for 'help'"}},
    {"reboot",     {1, 0, (uintptr_t)&gx8002_uart_stage2_reboot_5a40,
                    (uintptr_t)"reset mcu through watchdog"}},
    {"serialdown", {5, 1, (uintptr_t)&gx8002_uart_stage2_serialdown_5628,
                    (uintptr_t)"burn flash from serial"}},
    {"wdt",        {3, 1, (uintptr_t)&gx8002_uart_stage2_wdt_5978,
                    (uintptr_t)"wdt test command"}},
};
