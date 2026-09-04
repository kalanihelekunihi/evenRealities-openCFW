/*
 * SPDX-License-Identifier: MIT
 *
 * Public ABI for the clean-room G2 eAT core.
 */

#ifndef OPEN_CFW_G2_AT_CORE_H
#define OPEN_CFW_G2_AT_CORE_H

#include <stdarg.h>
#include <stdint.h>

typedef void (*open_cfw_at_core_output_callback)(
    const char *message,
    int length
);

typedef void (*open_cfw_at_core_command_handler)(
    const char *parameter_1,
    const char *parameter_2
);

struct open_cfw_at_core_command {
    uint32_t flags;
    const char *name;
    open_cfw_at_core_command_handler handler;
    uint32_t reserved;
};

struct open_cfw_at_core_state {
    uint32_t flags;
    uint32_t reserved;
    const struct open_cfw_at_core_command *commands;
    uint32_t command_count;
    uint32_t callback_mask;
    uint8_t output_mode;
    uint8_t padding[3];
    open_cfw_at_core_output_callback callbacks[3];
    char output[256];
};

void open_cfw_at_core_register_callback(
    uint8_t index,
    open_cfw_at_core_output_callback callback
);
void open_cfw_at_core_init(void);
void open_cfw_at_core_handler(const char *command);
void open_cfw_at_core_output(const char *format, ...);
void open_cfw_at_core_dispatch_command(
    const char *command,
    const char *parameter_1,
    const char *parameter_2
);

#endif
