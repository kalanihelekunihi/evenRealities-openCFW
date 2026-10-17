/* Native pre-release route at 0x58c836. */
#include <stdint.h>

extern uint32_t audio_conversate_route_get_release_pair_597f82(uint32_t handle);
extern void audio_lv_object_call_450500(uint32_t first, uint32_t second);

void audio_conversate_route_before_release_58c836(uint32_t handle) {
    if (handle == 0u)
        return;
    const uint32_t pair = audio_conversate_route_get_release_pair_597f82(handle);
    if (pair != 0u) {
        const uint32_t first = *(const uint32_t *)(uintptr_t)pair;
        const uint32_t second = *(const uint32_t *)(uintptr_t)(pair + 4u);
        audio_lv_object_call_450500(first, second);
    }
}
