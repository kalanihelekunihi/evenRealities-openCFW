/* Native image-B 0x1000b800, corroborated by pinned NationalChip
 * lvp/lvp_mode_denoise.c _beamformingInit. Stock-specific beam angles,
 * gain, distance, frame length and frame shift come from 0xb800..0xb8e6.
 */
#include <stdint.h>

extern void *gx8002_image_b_heap_alloc_alias_10009f2c(uint32_t bytes);
extern void *gx8002_image_b_heap_calloc_10009c0c(uint32_t count,
                                                   uint32_t size);
extern void *gx8002_image_b_heap_realloc_10009ca4(void *memory,
                                                    uint32_t bytes);
extern void gx8002_image_b_heap_free_10009c2c(void *memory);
extern uint32_t gx8002_image_b_dsp_config_copy_1000deb4(const uint32_t *ops);
extern void *gx8002_image_b_beamforming_create_1000de40(
    int mic_count, int angle_count, int sample_rate, float gain,
    float subtraction_ratio, int subtraction_enabled, int linear,
    float mic_distance, int circular, float mic_radius, float elevation,
    float short_alpha, float long_alpha, int reserved, int output_count,
    const int *output_indices);
extern int gx8002_image_b_beamforming_angles_1000c6e8(
    void *state, int count, const int16_t *angles);
extern uint32_t gx8002_image_b_imcra_allocation_size_1000c6a4(
    uint32_t channels, uint32_t stages, uint32_t bins, uint32_t history);
extern void gx8002_image_b_imcra_layout_1000d1fc(uint32_t *ctx,
                                                   uint32_t base);
extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

_Static_assert(sizeof(void *) == 4, "image-B native pointer ABI");

int32_t gx8002_image_b_denoise_beamforming_init_1000b800(void)
{
    const int16_t angles[3] = {35, 45, 55};
    const int output_indices[1] = {1};
    const uint32_t operations[4] = {
        (uint32_t)(uintptr_t)&gx8002_image_b_heap_alloc_alias_10009f2c,
        (uint32_t)(uintptr_t)&gx8002_image_b_heap_calloc_10009c0c,
        (uint32_t)(uintptr_t)&gx8002_image_b_heap_realloc_10009ca4,
        (uint32_t)(uintptr_t)&gx8002_image_b_heap_free_10009c2c,
    };
    volatile uint32_t *state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d2bc);
    (void)gx8002_image_b_dsp_config_copy_1000deb4(operations);

    void *beamforming = gx8002_image_b_beamforming_create_1000de40(
        2, 3, 16000, 2.0f, 0.6f, 0, 1, 0.035f, 0, 1.0f, 0.0f,
        0.2f, 0.01f, 0, 1, output_indices);
    state[0] = (uint32_t)(uintptr_t)beamforming;
    if (beamforming == 0) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]Init Beamforming Failed\n");
        return -1;
    }

    gx8002_image_b_beamforming_angles_1000c6e8(beamforming, 3, angles);
    void *mic_buffer = gx8002_image_b_heap_alloc_alias_10009f2c(2048u);
    state[1] = (uint32_t)(uintptr_t)mic_buffer;
    if (mic_buffer == 0) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]BF malloc g_bf_mictmp failed\n");
        return -1;
    }

    uint32_t bytes = gx8002_image_b_imcra_allocation_size_1000c6a4(
        2u, 3u, 512u, 256u);
    (void)gx8002_image_b_heap_log_10009934("bf_size = %d\n", bytes);
    void *temp_buffer = gx8002_image_b_heap_alloc_alias_10009f2c(bytes);
    if (temp_buffer == 0) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]BF malloc g_bf_temp_buf failed\n");
        return -1;
    }
    gx8002_image_b_imcra_layout_1000d1fc(
        (uint32_t *)beamforming, (uint32_t)(uintptr_t)temp_buffer);
    return 0;
}
