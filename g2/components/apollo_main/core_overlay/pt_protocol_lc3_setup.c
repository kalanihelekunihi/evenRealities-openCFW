/******************************************************************************
 *
 *  Copyright 2022 Google LLC
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at:
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 ******************************************************************************/

/* SPDX-License-Identifier: Apache-2.0 */

/*
 * Adapted for the G2 ABI from Google/liblc3
 * third_party/liblc3/src/lc3.c at the authenticated v1.1.3 baseline, commit
 * 96a3af0beb5487aca3b98a4b992a539a1f6d80d1.
 * The complete upstream license is retained at
 * ../../../third_party/liblc3/LICENSE.  This attribution describes the
 * adapted encoder-setup implementation only; G2 protocol wiring remains in
 * the separately licensed OpenCFW board-leaf source.
 */

#include "pt_protocol_board_leaf_candidates.h"

#include <stddef.h>
#include <stdint.h>


size_t open_cfw_pt_lc3_encoder_size(int duration_us,
                                    int pcm_sample_rate_hz)
{
    uint32_t duration_index;
    uint32_t pcm_samples_2m5;
    uint32_t pcm_samples_4m;
    uint32_t frame_samples;
    uint32_t temporal_samples;
    uint32_t delayed_samples;
    uint32_t sample_buffer_count;

    switch (duration_us) {
    case 2500: duration_index = 0U; break;
    case 5000: duration_index = 1U; break;
    case 7500: duration_index = 2U; break;
    case 10000: duration_index = 3U; break;
    default: return 0U;
    }

    switch (pcm_sample_rate_hz) {
    case 8000:
        pcm_samples_2m5 = 20U; pcm_samples_4m = 32U; break;
    case 16000:
        pcm_samples_2m5 = 40U; pcm_samples_4m = 64U; break;
    case 24000:
        pcm_samples_2m5 = 60U; pcm_samples_4m = 96U; break;
    case 32000:
        pcm_samples_2m5 = 80U; pcm_samples_4m = 128U; break;
    case 48000:
        pcm_samples_2m5 = 120U; pcm_samples_4m = 192U; break;
    default: return 0U;
    }

    temporal_samples = pcm_samples_2m5 >> 1U;
    frame_samples = pcm_samples_2m5 * (duration_index + 1U);
    delayed_samples = (frame_samples +
        (duration_index == 2U ? pcm_samples_4m : pcm_samples_2m5)) >> 1U;
    sample_buffer_count = ((frame_samples + temporal_samples) >> 1U) +
        frame_samples + delayed_samples;
    return 0x4ACU + sample_buffer_count * sizeof(uint32_t);
}


void *open_cfw_pt_lc3_setup_encoder(int duration_us,
                                    int codec_sample_rate_hz,
                                    int pcm_sample_rate_hz,
                                    void *storage)
{
    uint32_t duration_index;
    uint32_t codec_rate_index;
    uint32_t pcm_rate_index;
    uint32_t pcm_samples_2m5;
    uint32_t pcm_samples_4m;
    uint32_t frame_samples;
    uint32_t temporal_samples;
    uint32_t delayed_samples;
    uint32_t sample_buffer_count;
    uint8_t *bytes;
    uint32_t *words;
    uint32_t index;

    switch (duration_us) {
    case 2500U: duration_index = 0U; break;
    case 5000U: duration_index = 1U; break;
    case 7500U: duration_index = 2U; break;
    case 10000U: duration_index = 3U; break;
    default: return NULL;
    }

    switch (codec_sample_rate_hz) {
    case 8000U: codec_rate_index = 0U; break;
    case 16000U: codec_rate_index = 1U; break;
    case 24000U: codec_rate_index = 2U; break;
    case 32000U: codec_rate_index = 3U; break;
    case 48000U: codec_rate_index = 4U; break;
    default: return NULL;
    }

    if (pcm_sample_rate_hz <= 0)
        pcm_sample_rate_hz = codec_sample_rate_hz;
    switch (pcm_sample_rate_hz) {
    case 8000U:
        pcm_rate_index = 0U; pcm_samples_2m5 = 20U;
        pcm_samples_4m = 32U; break;
    case 16000U:
        pcm_rate_index = 1U; pcm_samples_2m5 = 40U;
        pcm_samples_4m = 64U; break;
    case 24000U:
        pcm_rate_index = 2U; pcm_samples_2m5 = 60U;
        pcm_samples_4m = 96U; break;
    case 32000U:
        pcm_rate_index = 3U; pcm_samples_2m5 = 80U;
        pcm_samples_4m = 128U; break;
    case 48000U:
        pcm_rate_index = 4U; pcm_samples_2m5 = 120U;
        pcm_samples_4m = 192U; break;
    default: return NULL;
    }
    if (codec_rate_index > pcm_rate_index || storage == NULL ||
            ((uintptr_t)storage & (sizeof(uint32_t) - 1U)) != 0U)
        return NULL;

    temporal_samples = pcm_samples_2m5 >> 1U;
    frame_samples = pcm_samples_2m5 * (duration_index + 1U);
    delayed_samples = (frame_samples +
        (duration_index == 2U ? pcm_samples_4m : pcm_samples_2m5)) >> 1U;
    sample_buffer_count = ((frame_samples + temporal_samples) >> 1U) +
        frame_samples + delayed_samples;

    bytes = (uint8_t *)storage;
    words = (uint32_t *)storage;
    for (index = 0U; index < (0x4ACU / sizeof(uint32_t)) +
            sample_buffer_count; ++index)
        words[index] = 0U;

    bytes[0] = (uint8_t)duration_index;
    bytes[1] = (uint8_t)codec_rate_index;
    bytes[2] = (uint8_t)pcm_rate_index;
    words[0x4A0U / sizeof(uint32_t)] = temporal_samples;
    words[0x4A4U / sizeof(uint32_t)] =
        (temporal_samples + frame_samples) >> 1U;
    words[0x4A8U / sizeof(uint32_t)] =
        words[0x4A4U / sizeof(uint32_t)] + frame_samples;
    return storage;
}


void *open_cfw_pt_lc3_setup_encoder_bounded(int duration_us,
                                            int codec_sample_rate_hz,
                                            int pcm_sample_rate_hz,
                                            void *storage,
                                            size_t storage_capacity)
{
    int effective_pcm_sample_rate_hz = pcm_sample_rate_hz;
    size_t required;

    if (effective_pcm_sample_rate_hz <= 0)
        effective_pcm_sample_rate_hz = codec_sample_rate_hz;
    required = open_cfw_pt_lc3_encoder_size(
        duration_us, effective_pcm_sample_rate_hz);
    if (required == 0U || required > storage_capacity)
        return NULL;
    return open_cfw_pt_lc3_setup_encoder(
        duration_us, codec_sample_rate_hz, pcm_sample_rate_hz, storage);
}
