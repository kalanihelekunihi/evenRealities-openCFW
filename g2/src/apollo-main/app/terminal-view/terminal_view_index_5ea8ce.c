/* Stock Terminal viewport start-index calculation at 0x5ea8ce. */
#include <stdint.h>

extern uint32_t audio_terminal_resource_597324(void);
extern uint32_t audio_terminal_position_index_5ea868(uint32_t position);

uint32_t audio_terminal_view_index_5ea8ce(uint32_t position) {
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    if (count == 0u)
        return 0u;
    uint32_t index = audio_terminal_position_index_5ea868(position);
    uint32_t first = (uint16_t)index >= 3u ? index - 2u : 0u;
    uint32_t max_first = count >= 13u ? (uint32_t)count - 12u : 0u;
    if ((uint16_t)max_first < (uint16_t)first)
        first = max_first;
    return (uint16_t)first;
}
