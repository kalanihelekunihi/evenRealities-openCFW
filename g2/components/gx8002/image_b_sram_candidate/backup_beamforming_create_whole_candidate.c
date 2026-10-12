/* Experimental composition of GSC create core 0x1000ce14..0x1000d176.
 * The actual entry remains a genuine import until native/C whole-body
 * effects, FPR ABI, product memory layout, and allocation failure branches
 * are qualified. This symbol is intentionally distinct from 0x1000ce14.
 */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_dsp_config_2002d7a4[4];
extern uint32_t *gx8002_image_b_create_prefix_verified_chunk(
    void *(*allocate)(uint32_t), int32_t sample_rate, int32_t mic_count,
    int32_t angle_count, int32_t linear, float elevation, float gain,
    float mic_distance, float mic_radius, int32_t circular,
    float short_alpha, float long_alpha, int32_t output_count);
extern void gx8002_image_b_create_allocations_verified_chunk(
    uint32_t *ctx, void *(*allocate)(uint32_t), uint32_t mic_count,
    uint32_t angle_count, uint32_t output_count);
extern void gx8002_image_b_create_angles_verified_chunk(
    uint32_t *ctx, int32_t linear, int32_t angle_count);
extern void gx8002_image_b_create_buffers_verified_chunk(
    uint32_t *ctx, uint32_t mic_count, uint32_t angle_count,
    uint32_t output_count, const uint32_t *output_indices);
extern void gx8002_image_b_create_window_verified_chunk(
    int32_t sample_count, int32_t *window);
extern void *gx8002_image_b_create_temp_verified_chunk(
    const uint32_t *ctx, void *(*allocate)(uint32_t));
extern void gx8002_image_b_create_overlap_verified_chunk(
    const int32_t *window, int32_t *inverse, int32_t stages,
    int32_t shift, int32_t frame, int32_t *temporary,
    void (*release)(void *));

void *gx8002_image_b_beamforming_core_whole_candidate(
    int sample_rate, int mic_count, int angle_count, int linear,
    float elevation, float gain, float mic_distance, float mic_radius,
    int circular, float short_alpha, float long_alpha, int reserved,
    int output_count, const int *output_indices)
{
    (void)reserved; /* the native entry loads no value from this stack slot */
    void *(*allocate)(uint32_t)=(void *(*)(uint32_t))
        (uintptr_t)gx8002_image_b_dsp_config_2002d7a4[0];
    void (*release)(void *)=(void (*)(void *))
        (uintptr_t)gx8002_image_b_dsp_config_2002d7a4[3];
    uint32_t *ctx=gx8002_image_b_create_prefix_verified_chunk(
        allocate,sample_rate,mic_count,angle_count,linear,elevation,gain,
        mic_distance,mic_radius,circular,short_alpha,long_alpha,output_count);
    gx8002_image_b_create_allocations_verified_chunk(
        ctx,allocate,(uint32_t)mic_count,(uint32_t)angle_count,
        (uint32_t)output_count);
    gx8002_image_b_create_angles_verified_chunk(ctx,linear,angle_count);
    gx8002_image_b_create_buffers_verified_chunk(
        ctx,(uint32_t)mic_count,(uint32_t)angle_count,
        (uint32_t)output_count,(const uint32_t *)output_indices);
    gx8002_image_b_create_window_verified_chunk(
        (int32_t)ctx[0x0c/4],
        (int32_t *)(uintptr_t)ctx[0x70/4]);
    int32_t *temporary=(int32_t *)
        gx8002_image_b_create_temp_verified_chunk(ctx,allocate);
    if (temporary==0) return ctx;
    gx8002_image_b_create_overlap_verified_chunk(
        (const int32_t *)(uintptr_t)ctx[0x70/4],
        (int32_t *)(uintptr_t)ctx[0x74/4],
        (int32_t)ctx[0x08/4],(int32_t)ctx[0x10/4],(int32_t)ctx[0x0c/4],
        temporary,release);
    return ctx;
}
