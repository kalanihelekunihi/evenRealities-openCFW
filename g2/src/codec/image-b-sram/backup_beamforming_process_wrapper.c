/* Native 0x1000dea0..0x1000deb3: forward four register words and the
 * fifth stack word to 0x1000d46c. The rooted caller at 0x1000bb58
 * overwrites R0 before using it, so its source-level result is void.
 */
#include <stdint.h>

extern void gx8002_image_b_beamforming_process_core_1000d46c(
    uint32_t context, uint32_t input, uint32_t output,
    uint32_t frame_count, uint32_t flags);

void gx8002_image_b_beamforming_process_entry_1000dea0(
    uint32_t context, uint32_t input, uint32_t output,
    uint32_t frame_count, uint32_t flags)
{
    gx8002_image_b_beamforming_process_core_1000d46c(
        context, input, output, frame_count, flags);
}
