/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_FC_COMMANDS_H
#define OPENCFW_G2_KWS_FC_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_FC_COMMAND_COUNT = 4,
    G2_KWS_FC_COMMAND_BYTES = 48
};

/* Encode one field-level opcode-0x40 fully connected record. */
int g2_kws_emit_fc(unsigned ordinal, uint8_t *out, size_t capacity,
                   unsigned *program_index);

#endif
