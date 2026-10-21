/* SPDX-License-Identifier: MIT */
#ifndef G2_UART_STAGE2_COMMAND_H
#define G2_UART_STAGE2_COMMAND_H
#include <stdint.h>
#include <stddef.h>

struct gx8002_stage2_command {
    const char *name;
    uintptr_t words[4];
};
_Static_assert(sizeof(struct gx8002_stage2_command) == 20,
               "stage-2 command descriptor size");

const struct gx8002_stage2_command *gx8002_uart_stage2_find_command_5e74(
    const char *name, const struct gx8002_stage2_command *table,
    uint32_t count);
int32_t gx8002_uart_stage2_strcmp_6270(const char *a, const char *b);
uint32_t gx8002_uart_stage2_poll_interrupt_5a7c(void);
int32_t gx8002_uart_stage2_launch_61a4(const char *format, ...);
#endif
