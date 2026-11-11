/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_ACTIVATION_COMMANDS_H
#define OPENCFW_G2_KWS_ACTIVATION_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_ACTIVATION_COUNT = 12,
    G2_KWS_ACTIVATION_COMMAND_BYTES = 44
};

/* Emit one of the twelve semantically recovered ReLU/sigmoid commands.
 * ordinal selects the table entry; program_index identifies its position
 * among all 212 commands in the locked KWS graph. Returns zero on success.
 */
int g2_kws_emit_activation(unsigned ordinal, uint8_t *out, size_t capacity,
                           unsigned *program_index);

#endif
