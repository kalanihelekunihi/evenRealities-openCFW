/* SPDX-License-Identifier: MIT
 * NationalChip gx_audio_in_v2.h output descriptors, each word at the
 * native board-control offsets. The original C API passes these by value.
 */
#ifndef OPENCFW_GX8002_AUDIO_OUTPUT_TYPES_H
#define OPENCFW_GX8002_AUDIO_OUTPUT_TYPES_H
#include <stdint.h>

typedef struct {
    uint32_t left_buffer, right_buffer, size, frame_num, endian, source;
} gx8002_pcm_output;

typedef struct {
    uint32_t buffer, size, frame_num, endian, source;
} gx8002_logfbank_output;

typedef gx8002_logfbank_output gx8002_spectrum_output;

typedef struct {
    uint32_t word[7];
} gx8002_i2s_output;

#endif
