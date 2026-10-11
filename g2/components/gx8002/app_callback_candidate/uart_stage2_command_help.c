/* SPDX-License-Identifier: MIT
 * Stage-2 command help/lookup outer body at 0x10005ef0.
 * The three format strings are stock initialized literals reached by
 * pointer words at 0x1000600c, 0x10006010, and 0x10006014.
 */
#include "uart_stage2_command.h"

static const char unknown_command_format[] =
    "Unknown command '%s' - try 'help' without arguments for list of all known commands\n\n";
static const char one_command_format[] = "%s - %s\n\n";
static const char list_command_format[] = "%-*s- %s\n";

uint32_t gx8002_uart_stage2_command_help_5ef0(
    const struct gx8002_stage2_command *commands, uint32_t count,
    uint32_t unused0, uint32_t unused1, int32_t argc, const char *const *argv)
{
    (void)unused0;
    (void)unused1;
    if (argc != 1) {
        if (argc < 2) return 0;
        for (int32_t i = 1; i < argc; ++i) {
            const struct gx8002_stage2_command *match =
                gx8002_uart_stage2_find_command_5e74(argv[i], commands,
                                                        count);
            if (match != NULL)
                gx8002_uart_stage2_launch_61a4(one_command_format,
                    match->name, (const char *)match->words[3]);
            else
                gx8002_uart_stage2_launch_61a4(unknown_command_format,
                                                 argv[i]);
        }
        return 1;
    }
    if (count == 0) return 0;
    const struct gx8002_stage2_command *sorted[count];
    for (uint32_t i = 0; i < count; ++i) sorted[i] = &commands[i];
    for (uint32_t pass = count - 1; pass != 0; --pass) {
        uint32_t swaps = 0;
        for (uint32_t i = 0; i < pass; ++i) {
            if (gx8002_uart_stage2_strcmp_6270(sorted[i]->name,
                                                sorted[i + 1]->name) > 0) {
                const struct gx8002_stage2_command *tmp = sorted[i];
                sorted[i] = sorted[i + 1];
                sorted[i + 1] = tmp;
                ++swaps;
            }
        }
        if (swaps == 0) break;
    }
    for (uint32_t i = 0; i < count; ++i) {
        const struct gx8002_stage2_command *entry = sorted[i];
        if (gx8002_uart_stage2_poll_interrupt_5a7c() != 0) return 1;
        if (entry->words[3] != 0)
            gx8002_uart_stage2_launch_61a4(list_command_format, 8,
                        entry->name, (const char *)entry->words[3]);
    }
    return 0;
}
