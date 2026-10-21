/* SPDX-License-Identifier: MIT
 * Native XIP 0x10206dc0..0x10206e57, source algorithm from pinned
 * NationalChip lvp/common/lvp_buffer.c and field schema lvp_context.h.
 * Five native literal words identify header/context/feature/mic storage
 * and LVP_CONTEXT_VERSION. Final placement of these SRAM objects is a
 * linker/startup obligation; this candidate retains native addresses.
 */
#include <stdint.h>
#include <stddef.h>

extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);

typedef struct {
    uint32_t version, fft_vad_en, mic_num, ref_num, fft_num;
    uint32_t logfbank_num, out_num, frame_length, sample_rate;
    uint32_t pcm_frame_num_per_context, pcm_frame_num_per_channel;
    uint32_t fft_frame_num_per_channel, logfbank_frame_num_per_channel;
    uint32_t out_frame_num_per_channel, ctx_buffer, ctx_num, ctx_size;
    uint32_t snpu_buffer_size, out_buffer, out_buffer_size;
    uint32_t mic_buffer, mic_buffer_size, ref_buffer, ref_buffer_size;
    uint32_t fft_dim_per_frame, fft_buffer, fft_buffer_size;
    uint32_t logfbank_dim_per_frame, logfbank_buffer, logfbank_buffer_size;
} gx8002_context_header;

_Static_assert(sizeof(gx8002_context_header) == 0x78u, "native header extent");
_Static_assert(offsetof(gx8002_context_header, mic_buffer) == 0x50u,
               "native mic buffer offset");
_Static_assert(offsetof(gx8002_context_header, logfbank_buffer) == 0x70u,
               "native feature buffer offset");

void gx8002_xip_buffer_initialize_10206dc0(void)
{
    gx8002_context_header *const header =
        (gx8002_context_header *)(uintptr_t)UINT32_C(0x20027b60);
    void *const contexts = (void *)(uintptr_t)UINT32_C(0x20027be0);
    void *const features = (void *)(uintptr_t)UINT32_C(0x20030000);
    gx8002_xip_memset_102099cc(header, 0u, 0x78u);
    gx8002_xip_memset_102099cc(contexts, 0u, 0x63c0u);
    gx8002_xip_memset_102099cc(features, 0u, 0x410u);
    header->logfbank_buffer = UINT32_C(0x20032210);
    header->logfbank_buffer_size = 0xf00u;
    header->logfbank_frame_num_per_channel = 0x30u;
    header->frame_length = 10u;
    header->sample_rate = 16000u;
    header->pcm_frame_num_per_context = 4u;
    header->pcm_frame_num_per_channel = 0xcu;
    header->logfbank_dim_per_frame = 0x28u;
    header->version = UINT32_C(0x20191222);
    header->mic_num = 2u;
    header->fft_dim_per_frame = 0x100u;
    header->mic_buffer = UINT32_C(0x20030410);
    header->snpu_buffer_size = 0x2120u;
    header->mic_buffer_size = 0x1e00u;
    header->ctx_size = 0x2140u;
    header->ref_num = 0u;
    header->ref_buffer = 0u;
    header->ref_buffer_size = 0u;
    header->fft_num = 0u;
    header->fft_buffer = 0u;
    header->fft_buffer_size = 0u;
    header->fft_frame_num_per_channel = 0u;
    header->logfbank_num = 1u;
    header->out_num = 0u;
    header->out_buffer = 0u;
    header->out_buffer_size = 0u;
    header->ctx_buffer = UINT32_C(0x20027be0);
    header->ctx_num = 3u;
    header->fft_vad_en = 1u;
}
