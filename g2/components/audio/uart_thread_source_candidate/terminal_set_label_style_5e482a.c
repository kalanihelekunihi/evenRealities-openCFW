/* Stock Terminal output label style 0x5e482a. */
#include <stdint.h>

extern void audio_lv_object_call_441488(uint32_t, uint32_t, uint32_t);
extern void audio_lv_label_style_call_597ea6(uint32_t, const void *, uint32_t);
extern void audio_lv_label_style_call_597f10(uint32_t, uint32_t);
extern void audio_lv_label_style_call_597f52(uint32_t, uint32_t);
extern void audio_lv_label_style_call_597ee0(uint32_t);

uint32_t audio_terminal_set_label_style_5e482a(uint32_t object,
                                                const void *style,
                                                uint32_t count,
                                                uint32_t scale) {
    if (object != 0u && style != 0 && count != 0u && scale != 0u) {
        audio_lv_object_call_441488(object, 0xffu, 0u);
        audio_lv_label_style_call_597ea6(object, style, count);
        audio_lv_label_style_call_597f10(object, count * scale);
        audio_lv_label_style_call_597f52(object, 0xffffffffu);
        audio_lv_label_style_call_597ee0(object);
    }
    return scale;
}
