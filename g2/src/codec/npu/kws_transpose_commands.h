/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_TRANSPOSE_COMMANDS_H
#define OPENCFW_G2_KWS_TRANSPOSE_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_TRANSPOSE_COMMAND_COUNT = 14,
    G2_KWS_TRANSPOSE_COMMAND_BYTES = 24
};

/* Emit one decoded transpose record from the locked KWS graph. */
int g2_kws_emit_transpose(unsigned ordinal, uint8_t *out, size_t capacity,
                          unsigned *program_index);

#endif
