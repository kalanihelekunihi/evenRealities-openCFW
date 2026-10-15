/* Apollo semantic_terminal_reset_output_tracking, native 0x5e8178. */
#include <stdint.h>

/* Native RAM 0x2006e364 through 0x2006e36b. Final placement is open. */
struct audio_terminal_output_tracking {
    uint8_t active;
    uint8_t reserved[3];
    uint32_t count;
};
struct audio_terminal_output_tracking audio_terminal_output_tracking;

void audio_terminal_reset_output_tracking(void) {
    audio_terminal_output_tracking.active=0;
    audio_terminal_output_tracking.count=0;
}
