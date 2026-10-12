/* Complete source control-flow candidate for image-B IMCRA
 * 0x10015d34..0x100167ce.  The pieces preserve the original cold-state,
 * adaptive, period-boundary and spectral order.  Native numerical/FP ABI
 * equality and physical runtime behavior are separate qualification gates.
 */
#include <stdint.h>

typedef struct { int32_t shift; float energy_scale; } prefix_result;
extern prefix_result gx8002_image_b_imcra_process_prefix_chunk(
    uint8_t *, const int16_t *);
extern void gx8002_image_b_imcra_cold_initialize_chunk(uint8_t *);
extern void gx8002_image_b_imcra_adaptive_prefix_chunk(uint8_t *);
extern void gx8002_image_b_imcra_minimum_smoothing_chunk(uint8_t *);
extern void gx8002_image_b_imcra_minimum_flags_chunk(uint8_t *);
extern void gx8002_image_b_imcra_flagged_smoothing_chunk(uint8_t *);
extern void gx8002_image_b_imcra_gain_table_chunk(uint8_t *);
extern int gx8002_image_b_imcra_noise_update_chunk(uint8_t *);
extern void gx8002_image_b_imcra_history_rotate_chunk(uint8_t *);
extern void gx8002_image_b_imcra_spectral_output_chunk(
    uint8_t *, int16_t *, int32_t);

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_process_10015d34(
    uint8_t *state, const int16_t *input, int16_t *output)
{
    prefix_result prefix =
        gx8002_image_b_imcra_process_prefix_chunk(state, input);
    int32_t bins = (int32_t)word(state, 0x1cu);
    if (word(state, 0x20u) == 0u)
        gx8002_image_b_imcra_cold_initialize_chunk(state);
    if (bins > 0)
        gx8002_image_b_imcra_adaptive_prefix_chunk(state);
    gx8002_image_b_imcra_minimum_smoothing_chunk(state);
    gx8002_image_b_imcra_minimum_flags_chunk(state);
    gx8002_image_b_imcra_flagged_smoothing_chunk(state);
    if (bins > 0) {
        gx8002_image_b_imcra_gain_table_chunk(state);
        (void)gx8002_image_b_imcra_noise_update_chunk(state);
    }
    int32_t period = (int32_t)word(state, 0x70u);
    int32_t next_frame = (int32_t)word(state, 0x20u) + 1;
    if (next_frame % period == 0)
        gx8002_image_b_imcra_history_rotate_chunk(state);
    gx8002_image_b_imcra_spectral_output_chunk(
        state, output, prefix.shift);
}
