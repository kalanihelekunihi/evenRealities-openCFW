/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_GENERAL_COMMANDS_H
#define OPENCFW_G2_KWS_GENERAL_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_GENERAL_COMMAND_COUNT = 152,
    G2_KWS_GENERAL_COMMAND_MAX_BYTES = 48
};

/* Emit one recovered copy or tensor arithmetic command. The ordinal is the
 * table position, while program_index identifies its position in the full
 * 212-command KWS graph. Returns zero on success. */
int g2_kws_emit_general_command(unsigned ordinal, uint8_t *out,
                                size_t capacity, unsigned *program_index,
                                size_t *written);

#endif
