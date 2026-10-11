/* SPDX-License-Identifier: MIT
 * Stage-2 shell command dispatch at 0x10006018, from the authenticated
 * uart_stage2.bin native body. The six command descriptors at 0x1000900c
 * are a separate product-data ownership contract until their callbacks and
 * strings have been reconstructed as source relocations.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern const struct gx8002_stage2_command gx8002_stage2_product_commands[6];

typedef int32_t (*gx8002_stage2_command_handler)(
    const struct gx8002_stage2_command *, uint32_t, uint32_t, char **);

int32_t gx8002_uart_stage2_dispatch_6018(uint32_t mode, uint32_t argc,
                                          char **argv, uint32_t *status)
{
    const struct gx8002_stage2_command *entry =
        gx8002_uart_stage2_find_command_5e74(argv[0],
                                               gx8002_stage2_product_commands,
                                               6u);
    if (entry == 0) {
        gx8002_uart_stage2_launch_61a4(
            "Unknown command '%s' - try 'help'\n", argv[0]);
        return 1;
    }
    if (entry->words[0] < argc) {
        gx8002_uart_stage2_launch_61a4("%s - %s\n\n",
                                         entry->name,
                                         (const char *)entry->words[3]);
        return 1;
    }
    gx8002_stage2_command_handler handler =
        (gx8002_stage2_command_handler)entry->words[2];
    int32_t result = handler(entry, mode, argc, argv);
    gx8002_uart_stage2_launch_61a4(result == 0 ?
                                     "[Result]:SUCC\n" : "[Result]:FAIL\n");
    *status &= (uint32_t)entry->words[1];
    if (result == -1) {
        gx8002_uart_stage2_launch_61a4("%s - %s\n\n",
                                         entry->name,
                                         (const char *)entry->words[3]);
        return 1;
    }
    return result;
}
