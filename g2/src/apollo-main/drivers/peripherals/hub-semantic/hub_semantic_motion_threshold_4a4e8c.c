/* Stock semantic_set_motion_threshold, 0x4a4e8c..0x4a4ec0. */
#include <stdint.h>

uint32_t audio_hub_motion_threshold_cell; /* stock RAM 0x20000e64 */
float audio_hub_motion_threshold_sine_cell; /* stock RAM 0x200731a8 */

extern __attribute__((pcs("aapcs-vfp"))) float
audio_uart_float_trig_mode1_50968c(float angle);

uint32_t audio_hub_semantic_motion_threshold_4a4e8c(uint32_t threshold)
{
    audio_hub_motion_threshold_cell = threshold;
    double radians = ((double)(int32_t)threshold *
                      0x1.921fb54442eeap+1) / 180.0;
    float angle = (float)radians;
    audio_hub_motion_threshold_sine_cell =
        audio_uart_float_trig_mode1_50968c(angle);
    return 0u;
}
