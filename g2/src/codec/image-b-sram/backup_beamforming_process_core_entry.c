/* Native process core 0x1000d46c, rooted call at 0x1000bb58.
 * The fifth stack word is forwarded by 0x1000dea0 but not read by the
 * complete native core. The rooted caller ignores the incidental R0.
 * These two RAM words are outside the CRT-cleared range and must be placed
 * and initialized by the final loaded-image integration. */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_process_energy_first_use_2002d79c;
extern volatile uint32_t gx8002_image_b_process_ring_counter_2002d7a0;
extern void gx8002_image_b_process_whole_experimental(
    const uint32_t *ctx, uint8_t *caller_output,
    uint32_t unused_r2, uint32_t output_frame_index,
    volatile uint32_t *observed_ring_counter,
    volatile uint32_t *energy_first_use_word);

void gx8002_image_b_beamforming_process_core_1000d46c(
    uint32_t context, uint32_t output, uint32_t unused_r2,
    uint32_t frame_index, uint32_t forwarded_stack_word)
{
    (void)forwarded_stack_word;
    gx8002_image_b_process_whole_experimental(
        (const uint32_t *)(uintptr_t)context,
        (uint8_t *)(uintptr_t)output, unused_r2, frame_index,
        &gx8002_image_b_process_ring_counter_2002d7a0,
        &gx8002_image_b_process_energy_first_use_2002d79c);
}
