/* Native UI action route wrappers 0x5b34a0 and 0x5b34b4. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern void audio_conversate_route_scroll_5b22fa(uint32_t);
extern uint32_t audio_conversate_route_release_58c84e(uint32_t);

uint32_t audio_conversate_ui_route_5b34a0(uint32_t state, uint32_t value) {
    (void)state;
    (void)value;
    const uint32_t handle = *(const uint32_t *)(const void *)(
        audio_conversate_ui_settings_extension_20071369 + 0x13u);
    audio_conversate_route_scroll_5b22fa(handle);
    return 0u;
}

uint32_t audio_conversate_ui_route_5b34b4(uint32_t state, uint32_t value) {
    (void)state;
    (void)value;
    const uint32_t handle = *(const uint32_t *)(const void *)(
        audio_conversate_ui_settings_extension_20071369 + 0x17u);
    if (handle != 0u)
        (void)audio_conversate_route_release_58c84e(handle);
    return 0u;
}
