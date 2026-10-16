/* Stock Terminal processing-label hide wrapper 0x5e4878. */
#include <stdint.h>

extern void audio_lv_object_call_450500(uint32_t object, uint32_t value);
extern void audio_lv_object_call_441488(uint32_t object, uint32_t x,
                                        uint32_t y);

void audio_terminal_processing_hide_5e4878(uint32_t object) {
    if (object == 0u)
        return;
    audio_lv_object_call_450500(object, 0u);
    audio_lv_object_call_441488(object, 0u, 0u);
}
