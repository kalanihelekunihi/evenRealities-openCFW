/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_BATCH_NORM_COMMANDS_H
#define OPENCFW_G2_KWS_BATCH_NORM_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_BATCH_NORM_COMMAND_COUNT = 18,
    G2_KWS_BATCH_NORM_COMMAND_BYTES = 44
};

/* Encode one decoded batch-normalization command from the locked KWS graph. */
int g2_kws_emit_batch_norm(unsigned ordinal, uint8_t *out, size_t capacity,
                           unsigned *program_index);

#endif
