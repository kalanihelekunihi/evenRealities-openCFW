/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_SPECIAL_COMMANDS_H
#define OPENCFW_G2_KWS_SPECIAL_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_SPECIAL_COMMAND_COUNT = 3,
    G2_KWS_SPECIAL_COMMAND_BYTES = 44
};

/* Emit the reduce, activation-mode-4, or format-conversion record. */
int g2_kws_emit_special(unsigned ordinal, uint8_t *out, size_t capacity,
                         unsigned *program_index);

#endif
