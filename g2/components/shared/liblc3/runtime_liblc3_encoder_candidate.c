/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-excluded, bounded G2 adapter for the authenticated Google
 * liblc3 v1.1.3 encoder source snapshot.  The upstream sources are compiled
 * separately and remain unmodified.
 */

#include "runtime_liblc3_encoder_candidate.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#include <lc3_private.h>

/*
 * Stock G2 and IAR use one-byte enums in the private encoder object.  Without
 * -fshort-enums, Clang/GCC silently move sr and sr_pcm away from stock offsets
 * 1 and 2.  Make that build-profile requirement fail closed.
 */
_Static_assert(sizeof(enum lc3_dt) == 1U,
    "G2 liblc3 requires -fshort-enums");
_Static_assert(sizeof(enum lc3_srate) == 1U,
    "G2 liblc3 requires -fshort-enums");
_Static_assert(offsetof(struct lc3_encoder, dt) == 0U,
    "G2 liblc3 encoder dt offset changed");
_Static_assert(offsetof(struct lc3_encoder, sr) == 1U,
    "G2 liblc3 encoder sr offset changed");
_Static_assert(offsetof(struct lc3_encoder, sr_pcm) == 2U,
    "G2 liblc3 encoder sr_pcm offset changed");
_Static_assert(offsetof(struct lc3_encoder, attdet) == 0x004U,
    "G2 liblc3 encoder attack detector offset changed");
_Static_assert(offsetof(struct lc3_encoder, ltpf) == 0x010U,
    "G2 liblc3 encoder LTPF offset changed");
_Static_assert(offsetof(struct lc3_encoder, spec) == 0x498U,
    "G2 liblc3 encoder spectrum state offset changed");
_Static_assert(offsetof(struct lc3_encoder, xt_off) == 0x4A0U,
    "G2 liblc3 encoder xt offset field changed");
_Static_assert(offsetof(struct lc3_encoder, xs_off) == 0x4A4U,
    "G2 liblc3 encoder xs offset field changed");
_Static_assert(offsetof(struct lc3_encoder, xd_off) == 0x4A8U,
    "G2 liblc3 encoder xd offset field changed");
_Static_assert(offsetof(struct lc3_encoder, x) == 0x4ACU,
    "G2 liblc3 encoder sample buffer offset changed");
_Static_assert(sizeof(struct lc3_encoder) == 0x4B0U,
    "G2 liblc3 encoder fixed state size changed");
_Static_assert(sizeof(float) == 4U, "G2 liblc3 requires binary32 float");
_Static_assert(LC3_PCM_FORMAT_S16 == 0 && LC3_PCM_FORMAT_S24 == 1 &&
    LC3_PCM_FORMAT_S24_3LE == 2 && LC3_PCM_FORMAT_FLOAT == 3,
    "liblc3 PCM format ABI changed");
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_config) == 24U,
    "liblc3 candidate config ABI changed");
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_plan) == 16U,
    "liblc3 candidate plan ABI changed");

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_candidate) == 44U,
    "G2 liblc3 candidate state ABI changed");
#endif

static int open_cfw_liblc3_u32_to_int(uint32_t value, int *result)
{
    if (value > (uint32_t)INT_MAX) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }
    *result = (int)value;
    return OPEN_CFW_LIBLC3_OK;
}

int open_cfw_liblc3_encoder_plan(
    const struct open_cfw_liblc3_encoder_config *config,
    struct open_cfw_liblc3_encoder_plan *plan
)
{
    int frame_us;
    int sample_rate_hz;
    int pcm_sample_rate_hz;
    int bitrate_bps;
    int encoded_samples;
    int pcm_samples;
    int frame_bytes;
    unsigned encoder_bytes;

    if (config == NULL || plan == NULL || config->pcm_stride == 0U ||
        config->pcm_stride > (uint32_t)INT_MAX ||
        config->pcm_format > (uint32_t)LC3_PCM_FORMAT_FLOAT ||
        open_cfw_liblc3_u32_to_int(config->frame_us, &frame_us) != 0 ||
        open_cfw_liblc3_u32_to_int(
            config->sample_rate_hz, &sample_rate_hz) != 0 ||
        open_cfw_liblc3_u32_to_int(config->bitrate_bps, &bitrate_bps) != 0) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }

    if (config->pcm_sample_rate_hz == 0U) {
        pcm_sample_rate_hz = sample_rate_hz;
    } else if (open_cfw_liblc3_u32_to_int(
        config->pcm_sample_rate_hz, &pcm_sample_rate_hz) != 0) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }

    encoded_samples = lc3_frame_samples(frame_us, sample_rate_hz);
    pcm_samples = lc3_frame_samples(frame_us, pcm_sample_rate_hz);
    frame_bytes = lc3_frame_bytes(frame_us, bitrate_bps);
    encoder_bytes = lc3_encoder_size(frame_us, pcm_sample_rate_hz);

    if (encoded_samples <= 0 || pcm_samples <= 0 || frame_bytes <= 0 ||
        encoder_bytes == 0U || pcm_sample_rate_hz < sample_rate_hz) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }

    plan->encoded_samples_per_frame = (uint32_t)encoded_samples;
    plan->pcm_samples_per_frame = (uint32_t)pcm_samples;
    plan->frame_bytes = (uint32_t)frame_bytes;
    plan->encoder_bytes = (uint32_t)encoder_bytes;
    return OPEN_CFW_LIBLC3_OK;
}

int open_cfw_liblc3_encoder_setup(
    struct open_cfw_liblc3_encoder_candidate *candidate,
    const struct open_cfw_liblc3_encoder_config *config,
    void *storage,
    size_t storage_size
)
{
    struct open_cfw_liblc3_encoder_plan plan;
    int status;

    if (candidate == NULL) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }
    candidate->encoder = NULL;
    if (storage == NULL ||
        ((uintptr_t)storage % _Alignof(void *)) != 0U) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }

    status = open_cfw_liblc3_encoder_plan(config, &plan);
    if (status != OPEN_CFW_LIBLC3_OK) {
        return status;
    }
    if (storage_size < (size_t)plan.encoder_bytes) {
        return OPEN_CFW_LIBLC3_STORAGE_TOO_SMALL;
    }

    candidate->encoder = lc3_setup_encoder(
        (int)config->frame_us,
        (int)config->sample_rate_hz,
        (int)config->pcm_sample_rate_hz,
        storage
    );
    if (candidate->encoder == NULL) {
        return OPEN_CFW_LIBLC3_CODEC_ERROR;
    }

    candidate->config = *config;
    candidate->plan = plan;
    return OPEN_CFW_LIBLC3_OK;
}

int open_cfw_liblc3_encoder_encode(
    struct open_cfw_liblc3_encoder_candidate *candidate,
    const void *pcm,
    size_t pcm_scalar_count,
    void *output,
    size_t output_size
)
{
    size_t required_pcm_scalars;
    size_t sample_gaps;
    int result;

    if (candidate == NULL || candidate->encoder == NULL || pcm == NULL ||
        output == NULL) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }
    if (output_size < (size_t)candidate->plan.frame_bytes) {
        return OPEN_CFW_LIBLC3_OUTPUT_TOO_SMALL;
    }

    sample_gaps = (size_t)candidate->plan.pcm_samples_per_frame - 1U;
    if (sample_gaps > (SIZE_MAX - 1U) / candidate->config.pcm_stride) {
        return OPEN_CFW_LIBLC3_INVALID_ARGUMENT;
    }
    required_pcm_scalars =
        sample_gaps * candidate->config.pcm_stride + 1U;
    if (pcm_scalar_count < required_pcm_scalars) {
        return OPEN_CFW_LIBLC3_PCM_TOO_SHORT;
    }

    result = lc3_encode(
        candidate->encoder,
        (enum lc3_pcm_format)candidate->config.pcm_format,
        pcm,
        (int)candidate->config.pcm_stride,
        (int)candidate->plan.frame_bytes,
        output
    );
    return result == 0 ? OPEN_CFW_LIBLC3_OK : OPEN_CFW_LIBLC3_CODEC_ERROR;
}
