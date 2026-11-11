/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_G2_KWS_CONV_COMMANDS_H
#define OPENCFW_G2_KWS_CONV_COMMANDS_H

#include <stddef.h>
#include <stdint.h>

enum {
    G2_KWS_CONV_COMMAND_COUNT = 5,
    G2_KWS_CONV_COMMAND_BYTES = 60,
    G2_KWS_DEPTHWISE_COMMAND_COUNT = 4,
    G2_KWS_DEPTHWISE_COMMAND_BYTES = 48
};

int g2_kws_emit_conv(unsigned ordinal, uint8_t *out, size_t capacity,
                      unsigned *program_index);
int g2_kws_emit_depthwise(unsigned ordinal, uint8_t *out, size_t capacity,
                           unsigned *program_index);

#endif
