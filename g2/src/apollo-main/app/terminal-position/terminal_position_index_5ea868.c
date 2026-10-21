/* Stock Terminal position-to-item binary search at 0x5ea868. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);

uint32_t audio_terminal_position_index_5ea868(uint32_t position) {
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    if (count == 0u)
        return 0u;
    int32_t target = (int32_t)position;
    if (target < 0)
        target = 0;
    uint32_t low = 0u;
    uint32_t high = count;
    uint32_t result = 0u;
    while ((uint16_t)low < (uint16_t)high) {
        uint32_t middle = ((uint16_t)high + low) >> 1;
        int32_t offset = *(const int32_t *)(const void *)
            (audio_terminal_ui_state_base + 0xbcu + (uint16_t)middle * 4u);
        if (target >= offset) {
            result = middle;
            low = middle + 1u;
        } else {
            high = middle;
        }
    }
    return (uint16_t)result;
}
