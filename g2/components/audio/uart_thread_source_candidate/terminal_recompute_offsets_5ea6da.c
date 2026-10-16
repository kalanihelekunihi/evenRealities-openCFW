/* Stock Terminal layout-offset recomputation at 0x5ea6da. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);
extern void audio_lv_object_size_call_43f4c0(uint32_t, uint32_t, uint32_t);

void audio_terminal_recompute_offsets_5ea6da(uint32_t first) {
    uint8_t *state = audio_terminal_ui_state_base;
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    uint16_t index = (uint16_t)first;
    if (count < index)
        index = count;
    uint32_t total = index == 0u ? 0u
        : *(const uint32_t *)(const void *)(state + 0xbcu + (uint32_t)index * 4u);
    for (; index < count; ++index) {
        *(uint32_t *)(void *)(state + 0xbcu + (uint32_t)index * 4u) = total;
        total += *(const uint16_t *)(const void *)(state + 0x3cu + (uint32_t)index * 2u);
    }
    *(uint32_t *)(void *)(state + 0xbcu + (uint32_t)count * 4u) = total;
    *(uint32_t *)(void *)(state + 0x1c8u) = total;
    uint32_t child = *(const uint32_t *)(const void *)(state + 8u);
    if (child != 0u)
        audio_lv_object_size_call_43f4c0(child, 0x240u, total);
}
