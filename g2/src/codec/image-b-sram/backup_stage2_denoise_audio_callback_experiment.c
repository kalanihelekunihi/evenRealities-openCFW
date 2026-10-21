/* Stock image-B 0x1000bd54..0x1000bdab, corroborated by pinned
 * NationalChip lvp/lvp_mode_denoise.c _LvpAudioInRecordCallback. The frame
 * slot, mic-frame, cache-invalidate, and queue-write children are selected.
 * Queue storage at 0x2002d2d8 remains an explicit BSS placement contract.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_frame_slot_10009e8c(
    uint32_t index, uint32_t *address, uint32_t *size);
extern uint32_t gx8002_image_b_mic_frame_10009ec0(
    const uint32_t *frame_state, uint32_t channel, uint32_t sample);
extern void gx8002_image_b_dcache_invalidate_range_10004dd8(
    uint32_t address, int32_t length);
extern uint32_t gx8002_image_b_audio_ring_write_10015b64(
    volatile int32_t *ring, const uint8_t *source);
extern volatile int32_t gx8002_image_b_denoise_ring_2002d2d8[];

int32_t gx8002_image_b_denoise_audio_callback_1000bd54(uint32_t index,
                                                          void *priv)
{
    (void)priv;
    uint32_t context_address;
    uint32_t context_size;
    (void)gx8002_image_b_audio_frame_slot_10009e8c(
        index, &context_address, &context_size);
    (void)context_size;
    volatile uint32_t *const context =
        (volatile uint32_t *)(uintptr_t)context_address;
    volatile uint32_t *const header =
        (volatile uint32_t *)(uintptr_t)context[0];
    context[2] = index;

    uint32_t sample_count = header[0x1cu / 4u] * header[0x24u / 4u];
    sample_count = sample_count * header[0x20u / 4u] / 1000u;
    const uint32_t channels = header[0x8u / 4u];
    if (channels != 0u) {
        const uint32_t bytes = sample_count * 2u;
        for (uint32_t channel = 0; channel < channels; ++channel) {
            const uint32_t address = gx8002_image_b_mic_frame_10009ec0(
                (const uint32_t *)(uintptr_t)context_address, channel, 0u);
            gx8002_image_b_dcache_invalidate_range_10004dd8(
                address, (int32_t)bytes);
        }
    }
    (void)gx8002_image_b_audio_ring_write_10015b64(
        gx8002_image_b_denoise_ring_2002d2d8,
        (const uint8_t *)&context_address);
    return 0;
}
